import hashlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "packaging" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rpm = load("extract_rpm")
asar = load("patch_asar")


def cpio_entry(name, data=b"", mode=stat.S_IFREG | 0o644, inode=1, nlink=1):
    name = name.encode() + b"\0"
    fields = [inode, mode, 0, 0, nlink, 0, len(data), 0, 0, 0, 0, len(name), 0]
    header = b"070701" + b"".join(f"{v:08x}".encode() for v in fields)
    return header + name + b"\0" * ((-110 - len(name)) % 4) + data + b"\0" * ((-len(data)) % 4)


class ExtractTests(unittest.TestCase):
    def test_extracts_only_application_and_resolves_hardlinks(self):
        data = (cpio_entry("etc/secret", b"not an app") +
                cpio_entry("usr/lib/chatgpt/alias", b"", inode=42, nlink=2) +
                cpio_entry("usr/lib/chatgpt/program", b"executable", inode=42, nlink=2) +
                cpio_entry("TRAILER!!!"))
        with tempfile.TemporaryDirectory() as temp:
            rpm.extract_cpio(io.BytesIO(data), temp)
            self.assertEqual((Path(temp) / "alias").read_bytes(), b"executable")
            self.assertFalse((Path(temp) / "etc").exists())
            self.assertEqual((Path(temp) / "alias").stat().st_ino,
                             (Path(temp) / "program").stat().st_ino)

    def test_rejects_path_traversal(self):
        for name in ["usr/lib/chatgpt/../../escaped", "/usr/lib/chatgpt/escaped"]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                with self.assertRaises(ValueError):
                    rpm.extract_cpio(io.BytesIO(cpio_entry(name, b"x")), temp)

    def test_rejects_symlink_escape_and_truncated_data(self):
        for data in [cpio_entry("usr/lib/chatgpt/link", b"../../escape", stat.S_IFLNK | 0o777),
                     cpio_entry("usr/lib/chatgpt/file", b"long data")[:-8]]:
            with self.subTest(data=data[:20]), tempfile.TemporaryDirectory() as temp:
                with self.assertRaises(ValueError):
                    rpm.extract_cpio(io.BytesIO(data), temp)


class AsarTests(unittest.TestCase):
    def make_archive(self, path, main):
        other = b"unmodified binary\0data"
        tree = {"files": {".vite": {"files": {"build": {"files": {
            "main-test.js": {"size": len(main), "offset": "0", "integrity": asar.integrity(main, {})}
        }}}}, "other.bin": {"size": len(other), "offset": str(len(main))},
            "native.node": {"size": 7, "unpacked": True}}}
        encoded = json.dumps(tree).encode()
        body = struct.pack("<I", len(encoded)) + encoded
        body += b"\0" * ((-len(body)) % 4)
        pickled = struct.pack("<I", len(body)) + body
        path.write_bytes(struct.pack("<II", 4, len(pickled)) + pickled + main + other)
        return other

    def test_corrects_flag_preserves_entries_and_integrity(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "app.asar"
            main = b"const flags=[" + asar.MARKER + b"`other`];"
            other = self.make_archive(path, main)
            asar.patch(path)
            with path.open("rb") as stream:
                tree, start = asar.read_header(stream)
                entries = dict(asar.nodes(tree))
                entry = entries[".vite/build/main-test.js"]
                stream.seek(start + int(entry["offset"]))
                changed = stream.read(entry["size"])
                self.assertEqual(changed, main.replace(asar.MARKER, b""))
                self.assertEqual(entry["integrity"]["hash"], hashlib.sha256(changed).hexdigest())
                entry = entries["other.bin"]
                stream.seek(start + int(entry["offset"]))
                self.assertEqual(stream.read(entry["size"]), other)
                self.assertTrue(entries["native.node"]["unpacked"])

    def test_unexpected_package_fails_without_altering_original(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "app.asar"
            self.make_archive(path, b"different version")
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                asar.patch(path)
            self.assertEqual(before, path.read_bytes())


if __name__ == "__main__":
    unittest.main()
