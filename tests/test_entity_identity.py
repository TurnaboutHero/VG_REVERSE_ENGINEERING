import struct
import unittest
from dataclasses import FrozenInstanceError
from vg.core.definition_catalog import BuildProfile, Definition, DefinitionCatalog, CatalogError
from vg.core.entity_identity import DestroyObservation, EntityResolver
from vg.core.vgr_records import VGRRecord


def record(offset, index=0, entity=2007, opcode=0x03f2, payload=None):
    size = 746 if opcode == 0x03f3 else 122
    data = (struct.pack('>III', index, 0xc10b41da, entity) + bytes(size - 12)) if payload is None else payload
    return VGRRecord(offset, 1.0, len(data)+2, opcode, memoryview(data))


def destroy_record(offset, entity=2007, payload=None):
    data = struct.pack('>I', entity) + b'\xaa\x55' if payload is None else payload
    return VGRRecord(offset, 2.5, len(data)+2, 0x040b, memoryview(data))


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

    def test_destroy_preserves_historical_spawn_and_immutable_evidence(self):
        resolver = self.resolver()
        spawn = resolver.observe(record(12))
        before = resolver.lifecycle_evidence(2007)
        destroy = resolver.observe(destroy_record(0), section=1)
        self.assertIsInstance(destroy, DestroyObservation)
        self.assertIs(resolver.latest_observed(2007), spawn)
        self.assertEqual(destroy.previous_spawn_observation, spawn.observation)
        self.assertEqual((destroy.section, destroy.record_offset, destroy.timestamp), (1, 0, 2.5))
        self.assertEqual(destroy.raw_payload_hex, '000007d7aa55')
        self.assertEqual(destroy.build_sha256, 'a'*64)
        self.assertEqual(destroy.manifest_sha256, 'b'*64)
        self.assertEqual(before.status, 'spawn_observed')
        self.assertIsNone(before.latest_destroy_observation)
        evidence = resolver.lifecycle_evidence(2007)
        self.assertEqual(evidence.status, 'destroy_action_observed')
        self.assertEqual(evidence.latest_spawn_observation, spawn.observation)
        self.assertIs(evidence.latest_destroy_observation, destroy)
        with self.assertRaises(FrozenInstanceError):
            destroy.entity_id = 1
        with self.assertRaises(FrozenInstanceError):
            evidence.status = 'alive'

    def test_destroy_without_spawn_then_spawn_links_action_only(self):
        resolver = self.resolver()
        self.assertEqual(resolver.lifecycle_evidence(2007).status, 'unobserved')
        destroy = resolver.observe(destroy_record(0))
        self.assertIsNone(destroy.previous_spawn_observation)
        self.assertIsNone(resolver.latest_observed(2007))
        self.assertIsNone(resolver.lifecycle_evidence(2007).latest_spawn_observation)
        spawn = resolver.observe(record(1))
        self.assertEqual(spawn.transition, 'spawn_after_destroy_observation')
        self.assertIsNone(spawn.previous_observation)
        self.assertEqual(spawn.previous_destroy_observation, destroy.observation)
        self.assertEqual(resolver.lifecycle_evidence(2007).status, 'spawn_observed')

    def test_spawn_after_destroy_and_repeated_spawn_keep_observation_boundaries(self):
        resolver = self.resolver()
        first = resolver.observe(record(0))
        resolver.observe(destroy_record(1))
        latest_destroy = resolver.observe(destroy_record(2))
        spawn = resolver.observe(record(3, index=1))
        self.assertEqual(spawn.transition, 'spawn_after_destroy_observation')
        self.assertEqual(spawn.previous_observation, first.observation)
        self.assertEqual(spawn.previous_destroy_observation, latest_destroy.observation)
        repeated = resolver.observe(record(4, index=1))
        self.assertEqual(repeated.transition, 'repeated_spawn_lifetime_unknown')
        self.assertIsNone(repeated.previous_destroy_observation)
        self.assertIs(resolver.lifecycle_evidence(2007).latest_destroy_observation, latest_destroy)
        changed = resolver.observe(record(5, index=0))
        self.assertEqual(changed.transition, 'definition_changed')

    def test_death_and_state_transition_do_not_close_spawn_evidence(self):
        resolver = self.resolver()
        spawn = resolver.observe(record(0))
        for offset, opcode in enumerate((0x0430, 0x0431), start=1):
            self.assertIsNone(resolver.observe(record(offset, opcode=opcode)))
            self.assertIs(resolver.latest_observed(2007), spawn)
            self.assertEqual(resolver.lifecycle_evidence(2007).status, 'spawn_observed')
            self.assertIsNone(resolver.lifecycle_evidence(2007).latest_destroy_observation)

    def test_destroy_layout_rejects_unobserved_lengths_and_length_mismatch(self):
        for length in (0, 3, 4, 5, 7, 8, 10):
            with self.subTest(length=length), self.assertRaisesRegex(ValueError, 'destroy-action layout'):
                self.resolver().observe(destroy_record(0, payload=bytes(length)))
        valid = destroy_record(0)
        mismatch = VGRRecord(0, valid.timestamp, 7, valid.opcode, valid.payload)
        with self.assertRaisesRegex(ValueError, 'destroy-action layout'):
            self.resolver().observe(mismatch)

    def test_destroy_is_recording_scoped_and_sentinel_never_resolves(self):
        a, b = self.resolver(), self.resolver('recording-b')
        a.observe(destroy_record(0))
        self.assertEqual(a.lifecycle_evidence(2007).status, 'destroy_action_observed')
        self.assertEqual(b.lifecycle_evidence(2007).status, 'unobserved')
        for observed in (record(1, entity=0xFFFFFFFF), destroy_record(2, entity=0xFFFFFFFF)):
            self.assertIsNone(a.observe(observed))
        self.assertIsNone(a.latest_observed(0xFFFFFFFF))
        sentinel = a.lifecycle_evidence(0xFFFFFFFF)
        self.assertEqual(sentinel.status, 'unobserved')
        self.assertIsNone(sentinel.latest_spawn_observation)
        self.assertIsNone(sentinel.latest_destroy_observation)


if __name__ == '__main__':
    unittest.main()
