from pathlib import Path
import struct
import tempfile
import unittest

from vg.analysis.event_timeline import decode_fields, iter_timeline
from vg.core.vgr_records import VGRRecord, iter_records


EVIDENCE = "gamekindred-c23b2e9e"


def packet(timestamp: float, opcode: int, payload: bytes) -> bytes:
    body = struct.pack(">H", opcode) + payload
    return struct.pack(">fI", timestamp, len(body)) + body


def record(opcode: int, payload: bytes) -> VGRRecord:
    return next(iter_records(packet(1.0, opcode, payload)))


class EventNativeSemanticsTests(unittest.TestCase):
    def test_attribute_updates_label_stat_layer_operation_and_keep_raw_provenance(self):
        kills_payload = (
            struct.pack(">IIfBBB", 0x12345678, 0x90ABCDEF, 2.5, 0x29, 3, 2)
            + b"killraw"
        )
        deaths_payload = (
            struct.pack(">IIfBBB", 0x10203040, 0x50607080, -1.5, 0x2A, 1, 0)
            + b"deathrw"
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "match.7.vgr"
            first = packet(10.0, 0x041C, kills_payload)
            path.write_bytes(first + packet(11.0, 0x041C, deaths_payload))

            rows = list(iter_timeline(path))

        self.assertEqual(rows[0]["native_evidence"], EVIDENCE)
        self.assertEqual(rows[0]["native_type"], "attribute_update")
        self.assertEqual(rows[0]["native_index"], 0x29)
        self.assertEqual(rows[0]["native_layer"], 3)
        self.assertEqual(rows[0]["native_operation"], "set")
        self.assertEqual(rows[0]["native_stat"], "kills")
        self.assertEqual(rows[1]["native_index"], 0x2A)
        self.assertEqual(rows[1]["native_layer"], 1)
        self.assertEqual(rows[1]["native_operation"], "add")
        self.assertEqual(rows[1]["native_stat"], "deaths")
        self.assertEqual(rows[0]["ref0"], 0x12345678)
        self.assertEqual(rows[0]["ref1"], 0x90ABCDEF)
        self.assertEqual(rows[0]["value_bits"], 0x40200000)
        self.assertEqual(rows[0]["payload_hex"], kills_payload.hex())
        self.assertEqual(rows[0]["frame_idx"], 7)
        self.assertEqual(rows[0]["record_index"], 0)
        self.assertEqual(rows[1]["record_offset"], len(first))

    def test_resource_assists_is_distinct_from_unlabeled_resources_9_and_10(self):
        assists = struct.pack(">IfBBBB", 1500, 4.0, 0x0B, 2, 0xA1, 0xB2) + b"xy"
        resource_9 = struct.pack(">IfBBBB", 1500, 5.0, 0x09, 0, 0xC3, 0xD4) + b"xy"
        resource_10 = struct.pack(">IfBBBB", 1500, 6.0, 0x0A, 2, 0xE5, 0xF6) + b"xy"

        decoded = [
            decode_fields(record(0x041D, assists)),
            decode_fields(record(0x041D, resource_9)),
            decode_fields(record(0x041D, resource_10)),
        ]

        self.assertEqual(decoded[0]["native_evidence"], EVIDENCE)
        self.assertEqual(decoded[0]["native_type"], "resource_update")
        self.assertEqual(decoded[0]["native_index"], 0x0B)
        self.assertEqual(decoded[0]["native_operation"], "set")
        self.assertEqual(decoded[0]["native_flags"], [0xA1, 0xB2])
        self.assertEqual(decoded[0]["native_stat"], "assists")
        self.assertEqual(decoded[1]["native_operation"], "add")
        self.assertIsNone(decoded[1]["native_stat"])
        self.assertIsNone(decoded[2]["native_stat"])

    def test_indexed_state_bits_exposes_distinct_bytes_and_keeps_raw_tail(self):
        payload = struct.pack(">IBBBB", 2000, 5, 0x12, 0x34, 0x56) + b"rawbit"

        fields = decode_fields(record(0x042B, payload))

        self.assertEqual(fields["native_evidence"], EVIDENCE)
        self.assertEqual(fields["native_type"], "indexed_state_bits")
        self.assertEqual(fields["native_index"], 5)
        self.assertEqual(fields["native_state_bits"], 0x12)
        self.assertEqual(fields["native_mask_a"], 0x34)
        self.assertEqual(fields["native_mask_b"], 0x56)
        self.assertEqual(fields["uninterpreted_bytes"], list(payload[4:]))

    def test_actor_state_transition_is_conditional_without_death_label(self):
        payload = struct.pack(">I", 3000) + b"\xaa\xbb"

        fields = decode_fields(record(0x0431, payload))

        self.assertEqual(fields["native_evidence"], EVIDENCE)
        self.assertEqual(fields["native_type"], "actor_state_transition")
        self.assertEqual(fields["native_state_from"], 3)
        self.assertEqual(fields["native_state_to"], 4)
        self.assertIs(fields["native_conditional"], True)
        self.assertIsNone(fields["native_stat"])
        self.assertEqual(fields["remaining_hex"], "aabb")

    def test_unknown_and_unexpected_layouts_decline_native_interpretation(self):
        unknown = decode_fields(record(0x9999, b"unknown"))
        unexpected = decode_fields(record(0x041C, b"\xff" * 21))

        self.assertEqual(unknown["decoding_status"], "unknown_opcode")
        self.assertEqual(unexpected["decoding_status"], "unexpected_content_length")
        self.assertFalse(any(key.startswith("native_") for key in unknown))
        self.assertFalse(any(key.startswith("native_") for key in unexpected))


if __name__ == "__main__":
    unittest.main()
