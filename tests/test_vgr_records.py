import math
import struct
import unittest

from vg.core.vgr_records import VGRRecordError, iter_records


def packet(timestamp, opcode, payload=b""):
    body = struct.pack(">H", opcode) + payload
    return struct.pack(">fI", timestamp, len(body)) + body


class VGRRecordTests(unittest.TestCase):
    def test_reads_exact_boundaries_and_owning_timestamps(self):
        data = packet(2001.0, 0x0431, bytes.fromhex("000005dc0000")) + packet(
            2002.0, 0x041D, b"\x08\x04\x31"
        )

        records = list(iter_records(data))

        self.assertEqual([record.timestamp for record in records], [2001.0, 2002.0])
        self.assertEqual([record.offset for record in records], [0, 16])
        self.assertEqual([record.content_length for record in records], [8, 5])
        self.assertEqual([record.opcode for record in records], [0x0431, 0x041D])
        self.assertEqual(bytes(records[1].payload), b"\x08\x04\x31")
        self.assertIsInstance(records[0].payload, memoryview)

    def test_accepts_unknown_opcode_and_large_payload(self):
        record = next(iter_records(packet(3601.25, 0xFFFF, b"x" * 300)))
        self.assertEqual(record.opcode, 0xFFFF)
        self.assertEqual(record.content_length, 302)
        self.assertEqual(len(record.payload), 300)

    def test_empty_input_has_no_records(self):
        self.assertEqual(list(iter_records(b"")), [])

    def test_rejects_each_partial_header_length(self):
        for length in range(1, 8):
            with self.subTest(length=length):
                with self.assertRaisesRegex(VGRRecordError, "header") as caught:
                    list(iter_records(b"\0" * length))
                self.assertEqual(caught.exception.offset, 0)

    def test_rejects_truncated_body(self):
        data = struct.pack(">fI", 1.0, 4) + b"\x04\x31\xff"
        with self.assertRaisesRegex(VGRRecordError, "body") as caught:
            list(iter_records(data))
        self.assertEqual(caught.exception.offset, 0)

    def test_rejects_content_lengths_smaller_than_opcode(self):
        for length in (0, 1):
            with self.subTest(length=length):
                data = struct.pack(">fI", 1.0, length) + b"\0" * length
                with self.assertRaisesRegex(VGRRecordError, "content length") as caught:
                    list(iter_records(data))
                self.assertEqual(caught.exception.offset, 0)

    def test_rejects_non_finite_timestamps(self):
        for timestamp in (math.nan, math.inf, -math.inf):
            with self.subTest(timestamp=timestamp):
                with self.assertRaisesRegex(VGRRecordError, "timestamp") as caught:
                    list(iter_records(packet(timestamp, 1)))
                self.assertEqual(caught.exception.offset, 0)

    def test_error_offset_is_start_of_malformed_record(self):
        valid = packet(3.0, 1, b"abc")
        with self.assertRaises(VGRRecordError) as caught:
            list(iter_records(valid + b"\0"))
        self.assertEqual(caught.exception.offset, len(valid))


if __name__ == "__main__":
    unittest.main()
