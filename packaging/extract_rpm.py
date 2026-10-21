#!/usr/bin/env python3
"""Extract only usr/lib/chatgpt from a checked RPM, using the Python stdlib."""
from __future__ import annotations

import gzip
import io
import lzma
import os
from pathlib import Path, PurePosixPath
import stat
import struct


def read_exact(stream, size):
    data = stream.read(size)
    if len(data) != size:
        raise ValueError("Truncated package")
    return data


def consume(stream, size, output=None):
    while size:
        data = read_exact(stream, min(size, 1024 * 1024))
        if output is not None:
            output.write(data)
        size -= len(data)


def payload_offset(stream):
    if read_exact(stream, 4) != b"\xed\xab\xee\xdb":
        raise ValueError("Not an RPM")
    stream.seek(96)
    for index in range(2):
        header = read_exact(stream, 16)
        if header[:4] != b"\x8e\xad\xe8\x01":
            raise ValueError("Invalid RPM header")
        entries, length = struct.unpack(">II", header[8:])
        stream.seek(entries * 16 + length, io.SEEK_CUR)
        if index == 0:
            stream.seek((-stream.tell()) % 8, io.SEEK_CUR)
    return stream.tell()


def extract_cpio(stream, destination):
    root = Path(destination).resolve()
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise ValueError("Extraction destination must be empty")
    links, pending = {}, {}
    extracted = 0
    while True:
        header = read_exact(stream, 110)
        # newc only: CRC archives must not be accepted without verifying CRCs.
        if header[:6] != b"070701":
            raise ValueError("Unsupported CPIO format")
        fields = [int(header[i:i + 8], 16) for i in range(6, 110, 8)]
        inode, mode, _, _, nlink, _, size, major, minor, _, _, namesize, _ = fields
        if not 1 <= namesize <= 65536:
            raise ValueError("Invalid CPIO path length")
        name_bytes = read_exact(stream, namesize)
        if not name_bytes.endswith(b"\0"):
            raise ValueError("Invalid CPIO path")
        name = name_bytes[:-1].decode("utf-8", "surrogateescape")
        consume(stream, (-(110 + namesize)) % 4)
        if name == "TRAILER!!!":
            if pending:
                raise ValueError("Unresolved hard links")
            return extracted
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError("Unsafe archive path")
        parts = path.parts
        if parts[:3] != ("usr", "lib", "chatgpt") or len(parts) == 3:
            consume(stream, size)
        else:
            relative = parts[3:]
            parent = root
            for part in relative[:-1]:
                parent /= part
                if parent.is_symlink():
                    raise ValueError("Archive traverses a symbolic link")
                parent.mkdir(exist_ok=True)
            target = parent / relative[-1]
            if target.is_symlink() or target.exists():
                if not (stat.S_ISDIR(mode) and target.is_dir()):
                    raise ValueError("Duplicate archive entry")
            key = (inode, major, minor)
            if stat.S_ISDIR(mode):
                if size:
                    raise ValueError("Directory contains data")
                target.mkdir(exist_ok=True)
            elif stat.S_ISREG(mode):
                if nlink > 1 and size == 0:
                    if key in links:
                        os.link(links[key], target)
                    else:
                        pending.setdefault(key, []).append(target)
                else:
                    with target.open("xb") as output:
                        consume(stream, size, output)
                    os.chmod(target, stat.S_IMODE(mode) & 0o777)
                    if nlink > 1:
                        links[key] = target
                        for other in pending.pop(key, []):
                            os.link(target, other)
            elif stat.S_ISLNK(mode):
                link = read_exact(stream, size).decode("utf-8", "surrogateescape")
                if PurePosixPath(link).is_absolute():
                    raise ValueError("Absolute symlink in application payload")
                if not (target.parent / link).resolve().is_relative_to(root):
                    raise ValueError("Symlink escapes application payload")
                target.symlink_to(link)
            else:
                raise ValueError("Unsupported archive entry type")
            extracted += 1
        consume(stream, (-size) % 4)


def extract_rpm(source, destination):
    with Path(source).open("rb") as rpm:
        start = payload_offset(rpm)
        magic = rpm.read(6)
        rpm.seek(start)
        if magic.startswith(b"\xfd7zXZ\0"):
            stream = lzma.LZMAFile(rpm)
        elif magic.startswith(b"\x1f\x8b"):
            stream = gzip.GzipFile(fileobj=rpm)
        elif magic == b"070701":
            stream = rpm
        else:
            raise ValueError("Unsupported RPM compression")
        return extract_cpio(stream, destination)


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        raise SystemExit("usage: extract_rpm.py PACKAGE.rpm OUTPUT-DIRECTORY")
    print(f"Extracted {extract_rpm(sys.argv[1], sys.argv[2])} application entries")
