import json
import math
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

from vg.analysis.event_timeline import decode_fields, iter_timeline, main
from vg.core.vgr_records import VGRRecord, VGRRecordError, iter_records


APPLE_DOUBLE_MAGIC = b"\x00\x05\x16\x07"


def packet(timestamp: float, opcode: int, payload: bytes = b"") -> bytes:
    body = struct.pack(">H", opcode) + payload
    return struct.pack(">fI", timestamp, len(body)) + body


def record(opcode: int, payload: bytes) -> VGRRecord:
    return next(iter_records(packet(1.0, opcode, payload)))


class EventTimelineTests(unittest.TestCase):
    def test_decodes_only_confirmed_structural_layouts(self):
        payload_1c = struct.pack(">IIfB", 0x12345678, 0xFEDCBA98, 1.5, 0xA7) + bytes(range(9))
        payload_1d = struct.pack(">IfB", 0x89ABCDEF, -2.25, 0x44) + b"abcde"
        payload_2b = struct.pack(">I", 0x80010002) + bytes(range(10, 20))
        payload_31 = struct.pack(">I", 0xFFFFFFFF) + b"\xaa\x55"

        decoded = [
            decode_fields(record(0x041C, payload_1c)),
            decode_fields(record(0x041D, payload_1d)),
            decode_fields(record(0x042B, payload_2b)),
            decode_fields(record(0x0431, payload_31)),
        ]

        self.assertEqual(
            decoded,
            [
                {
                    "decoding_status": "decoded",
                    "ref0": 0x12345678,
                    "ref1": 0xFEDCBA98,
                    "value": 1.5,
                    "value_bits": 0x3FC00000,
                    "code": 0xA7,
                    "remaining_hex": bytes(range(9)).hex(),
                },
                {
                    "decoding_status": "decoded",
                    "ref0": 0x89ABCDEF,
                    "value": -2.25,
                    "value_bits": 0xC0100000,
                    "code": 0x44,
                    "remaining_hex": b"abcde".hex(),
                },
                {
                    "decoding_status": "decoded",
                    "ref0": 0x80010002,
                    "uninterpreted_bytes": list(range(10, 20)),
                },
                {
                    "decoding_status": "decoded",
                    "ref0": 0xFFFFFFFF,
                    "remaining_hex": "aa55",
                },
            ],
        )

    def test_preserves_nonfinite_float_bits_as_strict_json_value(self):
        payload = struct.pack(">IIB", 1500, 0x7FC12345, 9) + b"\0" * 5

        fields = decode_fields(record(0x041D, payload))

        self.assertIsNone(fields["value"])
        self.assertEqual(fields["value_bits"], 0x7FC12345)
        json.dumps(fields, allow_nan=False)

    def test_declines_unexpected_length_and_unknown_opcode(self):
        wrong_length = decode_fields(record(0x041C, b"\xff" * 21))
        unknown = decode_fields(record(0x9999, b"\x01\x02"))

        self.assertEqual(
            wrong_length,
            {"decoding_status": "unexpected_content_length", "expected_content_length": 24},
        )
        self.assertEqual(unknown, {"decoding_status": "unknown_opcode"})

    def test_discovers_numeric_siblings_and_preserves_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skipped = packet(9.0, 0x9999, b"skip")
            frame_2 = (
                skipped
                + packet(20.0, 0x0431, struct.pack(">I", 1500) + b"xy")
                + packet(21.0, 0x9998, b"next")
            )
            frame_10 = packet(100.0, 0x0431, struct.pack(">I", 2000) + b"zz")
            (root / "match.10.vgr").write_bytes(frame_10)
            (root / "match.2.vgr").write_bytes(frame_2)
            (root / "match.3.vgr").write_bytes(APPLE_DOUBLE_MAGIC + b"metadata")

            rows = list(iter_timeline(root / "match.10.vgr"))

        self.assertEqual([row["frame_idx"] for row in rows], [2, 10])
        self.assertEqual([row["record_index"] for row in rows], [1, 0])
        self.assertEqual([row["record_offset"] for row in rows], [len(skipped), 0])
        self.assertEqual([row["timestamp"] for row in rows], [20.0, 100.0])
        self.assertEqual(rows[0]["payload_hex"], (struct.pack(">I", 1500) + b"xy").hex())
        self.assertEqual(rows[0]["content_length"], 8)

    def test_fake_marker_inside_payload_never_creates_a_row(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "match.1.vgr"
            fake = packet(77.0, 0x0431, struct.pack(">I", 9999) + b"aa")
            real = packet(88.0, 0x0431, struct.pack(">I", 1234) + b"bb")
            path.write_bytes(packet(1.0, 0x9999, fake) + real)

            rows = list(iter_timeline(path))

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["ref0"], 1234)
        self.assertEqual(rows[0]["timestamp"], 88.0)

    def test_entity_filter_matches_ref0_or_ref1(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "match.4.vgr"
            first = struct.pack(">IIfB", 11, 22, 1.0, 1) + b"a" * 9
            second = struct.pack(">IfB", 33, 2.0, 2) + b"b" * 5
            path.write_bytes(packet(1.0, 0x041C, first) + packet(2.0, 0x041D, second))

            by_ref1 = list(iter_timeline(path, entity_ids={22}))
            by_ref0 = list(iter_timeline(path, entity_ids={33}))

        self.assertEqual([row["opcode"] for row in by_ref1], [0x041C])
        self.assertEqual([row["opcode"] for row in by_ref0], [0x041D])

    def test_explicit_unknown_opcode_retains_complete_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "match.5.vgr"
            payload = bytes(range(32))
            path.write_bytes(packet(1.0, 0x9999, payload))

            rows = list(iter_timeline(path, opcodes={0x9999}))

        self.assertEqual(rows[0]["payload_hex"], payload.hex())
        self.assertEqual(rows[0]["decoding_status"], "unknown_opcode")

    def test_unexpected_length_row_preserves_complete_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "match.6.vgr"
            payload = bytes(range(21))
            path.write_bytes(packet(1.0, 0x041C, payload))

            rows = list(iter_timeline(path))

        self.assertEqual(rows[0]["payload_hex"], payload.hex())
        self.assertEqual(rows[0]["decoding_status"], "unexpected_content_length")
        self.assertNotIn("ref0", rows[0])

    def test_bad_inputs_and_malformed_framing_fail_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            malformed = root / "match.1.vgr"
            malformed.write_bytes(packet(1.0, 0x0431, b"123456") + b"\0")
            metadata = root / "meta.0.vgr"
            metadata.write_bytes(APPLE_DOUBLE_MAGIC + b"metadata")
            invalid_name = root / "not-numbered.vgr"
            invalid_name.write_bytes(packet(1.0, 0x0431, b"123456"))

            with self.assertRaises(VGRRecordError):
                list(iter_timeline(malformed))
            self.assertNotEqual(main([str(malformed)]), 0)
            self.assertNotEqual(main([str(metadata)]), 0)
            self.assertNotEqual(main([str(root / "missing.0.vgr")]), 0)
            self.assertNotEqual(main([str(invalid_name)]), 0)

    def test_cli_help_bad_path_and_output_protection(self):
        help_result = subprocess.run(
            [sys.executable, "-m", "vg.analysis.event_timeline", "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        bad_result = subprocess.run(
            [sys.executable, "-m", "vg.analysis.event_timeline", "missing.0.vgr"],
            capture_output=True,
            text=True,
            check=False,
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "match.1.vgr"
            original = packet(1.0, 0x0431, struct.pack(">I", 10) + b"zz")
            path.write_bytes(original)
            same_output = main([str(path), "-o", str(path)])
            preserved = path.read_bytes()

        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("--opcode", help_result.stdout)
        self.assertNotEqual(bad_result.returncode, 0)
        self.assertIn("error:", bad_result.stderr.lower())
        self.assertNotEqual(same_output, 0)
        self.assertEqual(original, preserved)


if __name__ == "__main__":
    unittest.main()
