from pathlib import Path
import struct
import tempfile
import unittest

from tests.test_event_timeline import packet, record
from vg.analysis.event_timeline import decode_fields, iter_timeline
from vg.analysis.native_event_fields import DEFAULT_OPCODES


class EntityDestroyTimelineTests(unittest.TestCase):
    def test_exact_layout_preserves_entity_and_opaque_tail(self):
        for entity in (2007, 0xFFFFFFFF):
            with self.subTest(entity=entity):
                result = decode_fields(record(0x040B, struct.pack('>I', entity) + b'\x81\x7f'))
                self.assertEqual(result['native_label'], 'ActionEntityDestroy')
                self.assertEqual(result['ref0'], entity)
                self.assertEqual(result['remaining_hex'], '817f')
                self.assertNotIn('native_stat', result)

    def test_unsupported_lengths_are_not_decoded(self):
        for length in (0, 3, 4, 5, 7, 8):
            with self.subTest(length=length):
                result = decode_fields(record(0x040B, bytes(length)))
                self.assertEqual(result['decoding_status'], 'unexpected_content_length')
                self.assertNotIn('ref0', result)

    def test_explicit_opcode_and_entity_filter_without_default_change(self):
        self.assertNotIn(0x040B, DEFAULT_OPCODES)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'match.0.vgr'
            payload = struct.pack('>I', 2007) + b'\x00\x00'
            path.write_bytes(packet(1.0, 0x040B, payload))
            self.assertEqual(list(iter_timeline(path)), [])
            self.assertEqual(list(iter_timeline(path, opcodes=[0x040B], entity_ids=[1500])), [])
            rows = list(iter_timeline(path, opcodes=[0x040B], entity_ids=[2007]))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['payload_hex'], payload.hex())
            self.assertEqual(rows[0]['native_type'], 'entity_destroy_action')


if __name__ == '__main__':
    unittest.main()
