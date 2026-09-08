import struct
import unittest
from vg.core.definition_catalog import BuildProfile, Definition, DefinitionCatalog, CatalogError
from vg.core.entity_identity import EntityResolver
from vg.core.vgr_records import VGRRecord


def record(offset, index=0, entity=2007, opcode=0x03f2, payload=None):
    size = 746 if opcode == 0x03f3 else 122
    data = (struct.pack('>III', index, 0xc10b41da, entity) + bytes(size - 12)) if payload is None else payload
    return VGRRecord(offset, 1.0, len(data)+2, opcode, memoryview(data))


class EntityTests(unittest.TestCase):
    def setUp(self):
        self.catalog = DefinitionCatalog(BuildProfile('a'*64, 'b'*64, 0, 1, 2), (Definition(0, 'Crystal'), Definition(1, 'Turret')))

    def resolver(self, name='recording-a'):
        return EntityResolver(name, self.catalog, 'a'*64)

    def test_both_spawn_opcodes_raw_fields(self):
        resolver = self.resolver()
        for offset, opcode in enumerate((0x03f2, 0x03f3)):
            result = resolver.observe(record(offset, opcode=opcode))
            self.assertEqual(result.definition_name, 'Crystal')
            self.assertEqual(result.skin_hash, 0xc10b41da)
            self.assertEqual(result.kind, 'unknown')
            self.assertIsNone(result.owner_entity_id)
            self.assertIsNone(result.credited_player_id)
            self.assertEqual(bytes.fromhex(result.raw_payload_hex), bytes(record(offset, opcode=opcode).payload))

    def test_same_id_recording_isolation_and_reassignment(self):
        a, b = self.resolver(), self.resolver('recording-b')
        self.assertIsNone(a.latest_observed(2007))
        first = a.observe(record(0))
        second = b.observe(record(0, index=1))
        self.assertNotEqual(first.recording_id, second.recording_id)
        self.assertEqual(a.latest_observed(2007).definition_name, 'Crystal')
        self.assertEqual(b.latest_observed(2007).definition_name, 'Turret')
        repeated = a.observe(record(0), section=1)
        self.assertEqual(repeated.transition, 'repeated_spawn_lifetime_unknown')
        self.assertEqual(repeated.previous_observation, first.observation)
        changed = a.observe(record(1, index=1), section=1)
        self.assertEqual(changed.transition, 'definition_changed')

    def test_unknown_missing_definition_and_nonspawn(self):
        resolver = self.resolver()
        self.assertIsNone(resolver.observe(record(0, opcode=0x0430)))
        value = resolver.observe(record(1, index=999))
        self.assertIsNone(value.definition_name)
        self.assertEqual(value.status, 'definition_index_out_of_range')

    def test_truncation_build_mismatch_and_order(self):
        with self.assertRaises(CatalogError):
            EntityResolver('a', self.catalog, 'c'*64)
        for length in (0, 11, 12, 121, 123, 125, 127, 745, 746):
            with self.assertRaises(ValueError):
                self.resolver().observe(record(0, payload=bytes(length)))
        resolver = self.resolver()
        resolver.observe(record(1))
        with self.assertRaises(ValueError):
            resolver.observe(record(0))
        with self.assertRaises(ValueError):
            resolver.observe(record(1))
        # All observed layouts preserve trailing fields without guessed meanings.
        for opcode, lengths in ((0x03f2, (122, 126)), (0x03f3, (746, 750))):
            for length in lengths:
                result = self.resolver().observe(record(0, opcode=opcode, payload=bytes(length)))
                self.assertEqual(len(bytes.fromhex(result.raw_payload_hex)), length)
        for length in (12, 122, 745, 747, 749, 751):
            with self.assertRaises(ValueError):
                self.resolver().observe(record(0, opcode=0x03f3, payload=bytes(length)))


if __name__ == '__main__':
    unittest.main()
