"""Catalog enrichment must not change raw timeline or infer future identities."""
from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from tests.test_event_timeline import packet, record
from vg.analysis.event_timeline import TimelineInputError, decode_fields, iter_timeline, main
from vg.analysis.native_event_fields import decode_fields as native_decode
from vg.core.definition_catalog import BuildProfile, CatalogError, Definition, DefinitionCatalog


class TimelineIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / 'match.0.vgr'
        self.catalog = DefinitionCatalog(BuildProfile('a'*64, 'b'*64, 0, 1, 2),
                                         (Definition(0, 'Crystal'), Definition(1, 'Turret')))

    def spawn(self, index=0, entity=2007):
        return packet(1, 0x03f2, struct.pack('>III', index, 3, entity) + bytes(110))

    def death(self, source=2007):
        return packet(2, 0x0430, struct.pack('>II', 1500, source) + bytes(6))

    def destroy(self, entity=2007):
        return packet(3, 0x040b, struct.pack('>I', entity) + b'\xaa\x55')

    def rows(self, path=None, **kwargs):
        return list(iter_timeline(path or self.path, catalog=self.catalog, build_sha256='a'*64, **kwargs))

    def test_decoder_reexport_and_lossless_legacy_equivalence(self):
        self.assertIs(decode_fields, native_decode)
        self.path.write_bytes(self.spawn() + self.death())
        legacy = list(iter_timeline(self.path))
        enriched = self.rows()
        for row in enriched:
            row.pop('ref0_identity')
            row.pop('ref1_identity')
        self.assertEqual(json.dumps(legacy, sort_keys=True), json.dumps(enriched, sort_keys=True))
        self.assertEqual(decode_fields(record(0x0430, bytes(14))), native_decode(record(0x0430, bytes(14))))

    def test_filters_still_observe_spawns_and_no_future_resolution(self):
        self.path.write_bytes(self.death() + self.spawn() + self.death())
        rows = self.rows(opcodes=[0x0430], entity_ids=[2007])
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]['ref1_identity']['status'], 'unobserved')
        identity = rows[1]['ref1_identity']
        self.assertEqual(identity['definition_name'], 'Crystal')
        self.assertEqual(identity['evidence_scope'], 'prior_spawn_observation')
        self.assertEqual(identity['kind'], 'unknown')
        self.assertIsNone(identity['owner_entity_id'])
        self.assertIsNone(identity['credited_player_id'])
        self.assertLess(identity['record_offset'], rows[1]['record_offset'])

    def test_sections_reobservations_and_recording_isolation(self):
        self.path.write_bytes(self.spawn())
        (self.root / 'match.2.vgr').write_bytes(self.spawn(1) + self.death())
        (self.root / 'match.10.vgr').write_bytes(self.death())
        rows = self.rows()
        self.assertEqual([r['frame_idx'] for r in rows], [2, 10])
        self.assertEqual(rows[1]['ref1_identity']['section'], 2)
        self.assertEqual(rows[1]['ref1_identity']['transition'], 'definition_changed')
        other = self.root / 'other.0.vgr'
        other.write_bytes(self.death() + self.spawn(0) + self.death())
        second = self.rows(other)
        self.assertEqual(second[0]['ref1_identity']['status'], 'unobserved')
        self.assertEqual(second[1]['ref1_identity']['definition_name'], 'Crystal')
        self.assertNotEqual(rows[0]['ref1_identity']['recording_id'], second[1]['ref1_identity']['recording_id'])

    def test_out_of_range_and_sentinel_do_not_fabricate(self):
        self.path.write_bytes(self.spawn(99) + self.death() + self.spawn(0, 0xffffffff) + self.death(0xffffffff))
        rows = self.rows()
        self.assertEqual(rows[0]['ref1_identity']['status'], 'definition_index_out_of_range')
        self.assertIsNone(rows[0]['ref1_identity']['definition_name'])
        self.assertEqual(rows[1]['ref1_identity']['status'], 'sentinel')
        self.assertIsNone(rows[1]['ref1_identity']['definition_name'])
        self.assertEqual(rows[1]['ref1_identity']['lifecycle']['status'], 'unobserved')

    def test_unsupported_spawn_is_rejected_even_when_filtered(self):
        self.path.write_bytes(packet(1, 0x03f2, bytes(12)) + self.death())
        self.assertEqual(len(list(iter_timeline(self.path))), 1)
        with self.assertRaisesRegex(ValueError, 'unsupported'):
            self.rows(opcodes=[0x0430], entity_ids=[1500])

    def test_filtered_destroy_enriches_future_rows_without_rewriting_past_rows(self):
        self.path.write_bytes(self.spawn() + self.death() + self.destroy() + self.death())
        rows = self.rows(opcodes=[0x0430], entity_ids=[2007])
        self.assertEqual(len(rows), 2)
        before, after = (row['ref1_identity'] for row in rows)
        self.assertEqual(before['lifecycle']['status'], 'spawn_observed')
        self.assertIsNone(before['lifecycle']['latest_destroy_observation'])
        self.assertEqual(after['definition_name'], 'Crystal')
        self.assertEqual(after['observation'], before['observation'])
        self.assertEqual(after['lifecycle']['status'], 'destroy_action_observed')
        destroy = after['lifecycle']['latest_destroy_observation']
        self.assertEqual(destroy['previous_spawn_observation'], before['observation'])
        self.assertEqual(destroy['raw_payload_hex'], '000007d7aa55')
        self.assertEqual(destroy['timestamp'], 3.0)
        self.assertEqual(destroy['section'], 0)
        self.assertEqual(destroy['build_sha256'], 'a'*64)
        self.assertGreater(destroy['record_offset'], rows[0]['record_offset'])
        self.assertLess(destroy['record_offset'], rows[1]['record_offset'])
        legacy = list(iter_timeline(self.path))
        for row in rows:
            row.pop('ref0_identity')
            row.pop('ref1_identity')
        self.assertEqual(rows, legacy)

    def test_destroy_without_spawn_is_visible_and_does_not_leak_recordings(self):
        self.path.write_bytes(self.destroy() + self.death())
        identity = self.rows()[0]['ref1_identity']
        self.assertEqual(identity['status'], 'unobserved')
        self.assertIsNone(identity['definition_name'])
        evidence = identity['lifecycle']
        self.assertEqual(evidence['status'], 'destroy_action_observed')
        self.assertIsNone(evidence['latest_spawn_observation'])
        self.assertIsNone(evidence['latest_destroy_observation']['previous_spawn_observation'])
        other = self.root / 'other.0.vgr'
        other.write_bytes(self.death())
        other_evidence = self.rows(other)[0]['ref1_identity']['lifecycle']
        self.assertEqual(other_evidence['status'], 'unobserved')
        self.assertIsNone(other_evidence['latest_destroy_observation'])

    def test_sections_preserve_destroy_and_spawn_links_without_closing_on_death(self):
        self.path.write_bytes(self.spawn() + self.destroy())
        (self.root / 'match.2.vgr').write_bytes(self.spawn() + self.death())
        (self.root / 'match.10.vgr').write_bytes(
            packet(4, 0x0431, struct.pack('>I', 2007) + bytes(2)) + self.death())
        rows = self.rows(opcodes=[0x0430, 0x0431])
        self.assertEqual([row['frame_idx'] for row in rows], [2, 10, 10])
        for row, ref in ((rows[0], 'ref1'), (rows[1], 'ref0'), (rows[2], 'ref1')):
            identity = row[ref + '_identity']
            self.assertEqual(identity['transition'], 'spawn_after_destroy_observation')
            self.assertEqual(identity['lifecycle']['status'], 'spawn_observed')
            destroy = identity['lifecycle']['latest_destroy_observation']
            self.assertEqual(destroy['section'], 0)
            self.assertEqual(identity['previous_destroy_observation'], destroy['observation'])
            self.assertEqual(destroy['previous_spawn_observation'], identity['previous_observation'])

    def test_malformed_destroy_rejected_in_catalog_mode_even_when_filtered(self):
        for length in (0, 4, 5, 7, 8):
            with self.subTest(length=length):
                self.path.write_bytes(packet(1, 0x040b, bytes(length)) + self.death())
                self.assertEqual(len(list(iter_timeline(self.path))), 1)
                with self.assertRaisesRegex(TimelineInputError, 'destroy-action layout'):
                    self.rows(opcodes=[0x0430], entity_ids=[1500])

    def test_library_requires_matching_build(self):
        self.path.write_bytes(self.death())
        for kwargs in ({'catalog': self.catalog}, {'build_sha256': 'a'*64},
                       {'catalog': self.catalog, 'build_sha256': 'c'*64}):
            with self.assertRaises(CatalogError):
                list(iter_timeline(self.path, **kwargs))

    def test_cli_rejects_partial_wrong_build_missing_assets_before_output(self):
        self.path.write_bytes(self.death())
        output = self.root / 'output.jsonl'
        output.write_text('keep')
        for extra in (['--manifest', 'missing'],
                      ['--manifest', 'missing', '--executable', 'missing', '--build-sha256', 'a'*64, '--manifest-sha256', 'b'*64],
                      ['--manifest', 'missing', '--executable', 'missing', '--build-sha256',
                       '659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642', '--manifest-sha256', 'b'*64]):
            with redirect_stderr(io.StringIO()):
                self.assertEqual(main([str(self.path), '-o', str(output), *extra]), 2)
            self.assertEqual(output.read_text(), 'keep')

    def test_cli_cannot_overwrite_source_asset(self):
        self.path.write_bytes(self.death())
        asset = self.root / 'manifest'
        asset.write_bytes(b'owned')
        with patch('vg.analysis.event_timeline.supported_build_profile'), patch(
                'vg.analysis.event_timeline.load_catalog', return_value=self.catalog), redirect_stderr(io.StringIO()):
            result = main([str(self.path), '--manifest', str(asset), '--executable', str(asset),
                           '--build-sha256', 'a'*64, '--manifest-sha256', 'b'*64, '-o', str(asset)])
        self.assertEqual(result, 2)
        self.assertEqual(asset.read_bytes(), b'owned')


if __name__ == '__main__':
    unittest.main()
