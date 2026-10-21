#!/usr/bin/env python3
"""Reproduce the one feature-flag correction in the working Mint installation.

No OpenAI application code is included in this script. The exact marker must
occur once in the pinned package; unexpected input fails rather than guessing.
"""
import hashlib
import json
from pathlib import Path
import shutil
import struct

MARKER = b"`apps_mcp_path_override`,"


def nodes(tree, prefix=""):
    for name, entry in tree.get("files", {}).items():
        path = prefix + name
        if "files" in entry:
            yield from nodes(entry, path + "/")
        else:
            yield path, entry


def read_header(stream):
    prefix = stream.read(16)
    if len(prefix) != 16:
        raise ValueError("Invalid ASAR header")
    header_size = struct.unpack_from("<I", prefix, 4)[0]
    json_size = struct.unpack_from("<I", prefix, 12)[0]
    if not 0 < json_size <= header_size <= 64 * 1024 * 1024:
        raise ValueError("Invalid ASAR header lengths")
    header = json.loads(stream.read(json_size))
    return header, 8 + header_size


def integrity(data, previous):
    block = previous.get("blockSize", 4 * 1024 * 1024)
    return {"algorithm": "SHA256", "hash": hashlib.sha256(data).hexdigest(),
            "blockSize": block, "blocks": [hashlib.sha256(data[i:i + block]).hexdigest()
                                           for i in range(0, len(data), block)]}


def patch(source):
    source = Path(source)
    temporary = source.with_suffix(source.suffix + ".tmp")
    try:
        with source.open("rb") as original:
            header, data_start = read_header(original)
            files = list(nodes(header))
            replacements = {}
            count = 0
            for name, entry in files:
                if name.startswith(".vite/build/main-") and name.endswith(".js") and "offset" in entry:
                    original.seek(data_start + int(entry["offset"]))
                    data = original.read(entry["size"])
                    count += data.count(MARKER)
                    if MARKER in data:
                        replacements[name] = data.replace(MARKER, b"")
            if count != 1:
                raise ValueError(f"Expected one obsolete flag, found {count}")
            ordered = sorted(((n, e) for n, e in files if "offset" in e),
                             key=lambda item: int(item[1]["offset"]))
            old = {n: (int(e["offset"]), e["size"]) for n, e in ordered}
            offset = 0
            for name, entry in ordered:
                entry["offset"] = str(offset)
                if name in replacements:
                    entry["size"] = len(replacements[name])
                    if "integrity" in entry:
                        entry["integrity"] = integrity(replacements[name], entry["integrity"])
                offset += entry["size"]
            encoded = json.dumps(header, ensure_ascii=False, separators=(",", ":")).encode()
            body = struct.pack("<I", len(encoded)) + encoded
            body += b"\0" * ((-len(body)) % 4)
            pickle_data = struct.pack("<I", len(body)) + body
            with temporary.open("xb") as output:
                output.write(struct.pack("<II", 4, len(pickle_data)))
                output.write(pickle_data)
                for name, _ in ordered:
                    if name in replacements:
                        output.write(replacements[name])
                    else:
                        start, size = old[name]
                        original.seek(data_start + start)
                        while size:
                            data = original.read(min(size, 1024 * 1024))
                            if not data:
                                raise ValueError("Truncated ASAR entry")
                            output.write(data)
                            size -= len(data)
        shutil.copymode(source, temporary)
        temporary.replace(source)
    finally:
        temporary.unlink(missing_ok=True)
    return list(replacements)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        raise SystemExit("usage: patch_asar.py APP.asar")
    print("Applied Mint compatibility correction to", ", ".join(patch(sys.argv[1])))
