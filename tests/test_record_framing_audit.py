import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

from vg.analysis.record_framing_audit import audit_path, main


def packet(timestamp, opcode, payload=b""):
    body = struct.pack(">H", opcode) + payload
    return struct.pack(">fI", timestamp, len(body)) + body


class RecordFramingAuditTests(unittest.TestCase):
    def make_fixture_tree(self, root):
        first = packet(1.0, 0x0431, b"abc") + packet(2.0, 0x041D)
        second = packet(3.0, 0x0431, b"z")
        malformed_prefix = packet(4.0, 0x9999)
        (root / "match.0.vgr").write_bytes(first)
        (root / "nested").mkdir()
        (root / "nested" / "match.1.vgr").write_bytes(second)
        (root / "nested" / "._match.0.vgr").write_bytes(b"\x00\x05\x16\x07metadata")
        (root / "broken.vgr").write_bytes(malformed_prefix + b"\0")
        return first, second, malformed_prefix

    def test_audits_valid_metadata_and_malformed_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second, malformed_prefix = self.make_fixture_tree(root)

            summary = audit_path(root)

        self.assertEqual(summary["files_seen"], 4)
        self.assertEqual(summary["replay_files"], 3)
        self.assertEqual(summary["replay_starts"], 1)
        self.assertEqual(summary["apple_double_files"], 1)
        self.assertEqual(summary["files_fully_consumed"], 2)
        self.assertEqual(summary["records"], 4)
        self.assertEqual(summary["bytes"], len(first) + len(second) + len(malformed_prefix) + 1)
        self.assertEqual(summary["consumed_bytes"], len(first) + len(second) + len(malformed_prefix))
        self.assertEqual(summary["opcode_counts"], {"0x041d": 1, "0x0431": 2, "0x9999": 1})
        self.assertEqual(summary["content_lengths"], {"2": 2, "3": 1, "5": 1})
        self.assertEqual(len(summary["errors"]), 1)
        self.assertEqual(summary["errors"][0]["path"], "broken.vgr")
        self.assertEqual(summary["errors"][0]["offset"], len(malformed_prefix))
        self.assertNotIn("payload", json.dumps(summary))

    def test_single_file_is_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "single.0.vgr"
            path.write_bytes(packet(7.0, 0xABCD))
            summary = audit_path(path)
        self.assertEqual(summary["files_seen"], 1)
        self.assertEqual(summary["replay_starts"], 1)
        self.assertEqual(summary["records"], 1)
        self.assertEqual(summary["errors"], [])

    def test_missing_path_and_directory_without_vgr_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                audit_path(root / "missing")
            (root / "note.txt").write_text("none", encoding="utf-8")
            with self.assertRaises(ValueError):
                audit_path(root)

    def test_metadata_only_input_fails_cli(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "._match.0.vgr"
            path.write_bytes(b"\x00\x05\x16\x07metadata")
            self.assertNotEqual(main([str(path)]), 0)

    def test_malformed_input_fails_cli_and_output_is_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_fixture_tree(root)
            output = root / "audit.json"
            self.assertNotEqual(main([str(root), "-o", str(output)]), 0)
            parsed = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(len(parsed["errors"]), 1)

    def test_help_returns_zero(self):
        result = subprocess.run(
            [sys.executable, "-m", "vg.analysis.record_framing_audit", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()
