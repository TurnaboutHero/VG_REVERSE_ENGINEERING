from contextlib import ExitStack, redirect_stderr, redirect_stdout
from dataclasses import asdict, replace
import io
import json
import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from tests.test_event_timeline import packet
from vg.analysis.event_timeline import iter_timeline, main
from vg.core.definition_catalog import BuildProfile, CatalogError, Definition, DefinitionCatalog
from vg.core.entity_definition import EntityKindEvidence


class TimelineEntityResourceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.path = self.root / 'match.0.vgr'
        self.asset = self.root / 'crystal.cff'
        self.manifest = self.root / 'manifest.cff'
        self.executable = self.root / 'game.exe'
        for path in (self.asset, self.manifest, self.executable):
            path.write_bytes(b'owned input')
        self.catalog = DefinitionCatalog(BuildProfile('a' * 64, 'b' * 64, 0, 1, 1),
                                         (Definition(0, 'Crystal', serialized_name='*Crystal*'),))
        self.evidence = EntityKindEvidence('a' * 64, 'c' * 64, '*Crystal*', 0x2419fb6c, 0, 2, 'structure')
        self.enriched = replace(self.catalog, definitions=(
            replace(self.catalog.lookup(0), kind='structure', kind_evidence=self.evidence),))
        self.spawn = packet(1, 0x03f2, struct.pack('>III', 0, 3, 2007) + bytes(110))
        self.death = packet(2, 0x0430, struct.pack('>II', 1500, 2007) + bytes(6))
        self.path.write_bytes(self.spawn + self.death)
        self.flags = ['--manifest', str(self.manifest), '--executable', str(self.executable),
                      '--build-sha256', 'a' * 64, '--manifest-sha256', 'b' * 64]
        self.resource = ['--entity-resource', '0', str(self.asset), 'c' * 64]

    def mocks(self, stack, **enrich_options):
        stack.enter_context(patch('vg.analysis.event_timeline.supported_build_profile'))
        stack.enter_context(patch('vg.analysis.event_timeline.load_catalog', return_value=self.catalog))
        return stack.enter_context(patch('vg.analysis.event_timeline.enrich_definition', **enrich_options))

    def test_resource_evidence_reaches_filtered_death_rows(self):
        output = io.StringIO()
        with ExitStack() as stack:
            enrich = self.mocks(stack, return_value=self.enriched)
            with redirect_stdout(output):
                result = main([str(self.path), '--opcode', '0x0430', '--entity', '2007',
                               *self.flags, *self.resource])
        self.assertEqual(result, 0)
        enrich.assert_called_once_with(self.catalog, 0, b'owned input', b'owned input', 'c' * 64)
        identity = json.loads(output.getvalue())['ref1_identity']
        self.assertEqual(identity['kind'], 'structure')
        self.assertEqual(identity['kind_evidence'], asdict(self.evidence))
        self.assertIsNone(identity['credited_player_id'])

    def test_invalid_catalog_resource_arguments_preserve_existing_output(self):
        output = self.root / 'keep.jsonl'
        invalid_index = ['--entity-resource', 'no-index', str(self.asset), 'c' * 64]
        cases = [self.resource, [*self.flags, *invalid_index],
                 [*self.flags, *self.resource, *self.resource]]
        for flags in cases:
            with self.subTest(flags=flags), ExitStack() as stack:
                output.write_text('keep')
                self.mocks(stack, return_value=self.enriched)
                with redirect_stderr(io.StringIO()):
                    self.assertEqual(main([str(self.path), '-o', str(output), *flags]), 2)
                self.assertEqual(output.read_text(), 'keep')

    def test_output_cannot_overwrite_actor_resource_or_hardlink(self):
        alias = self.root / 'alias.jsonl'
        os.link(self.asset, alias)
        for output in (self.asset, alias):
            with self.subTest(output=output), ExitStack() as stack:
                self.mocks(stack, return_value=self.enriched)
                with redirect_stderr(io.StringIO()):
                    self.assertEqual(main([str(self.path), '-o', str(output), *self.flags, *self.resource]), 2)
                self.assertEqual(self.asset.read_bytes(), b'owned input')

    def test_invalid_resource_is_rejected_before_output_is_opened(self):
        output = self.root / 'keep.jsonl'
        output.write_text('keep')
        with ExitStack() as stack:
            self.mocks(stack, side_effect=CatalogError('SYMB name mismatch'))
            with redirect_stderr(io.StringIO()):
                self.assertEqual(main([str(self.path), '-o', str(output), *self.flags, *self.resource]), 2)
        self.assertEqual(output.read_text(), 'keep')

    def test_kind_evidence_survives_destroy_and_recording_isolation(self):
        destroy = packet(3, 0x040b, struct.pack('>I', 2007) + bytes(2))
        self.path.write_bytes(self.spawn + destroy + self.death)
        row = next(iter_timeline(self.path, catalog=self.enriched, build_sha256='a' * 64))
        identity = row['ref1_identity']
        self.assertEqual(identity['kind_evidence'], asdict(self.evidence))
        self.assertEqual(identity['lifecycle']['status'], 'destroy_action_observed')
        other = self.root / 'other.0.vgr'
        other.write_bytes(self.death)
        other_row = next(iter_timeline(other, catalog=self.enriched, build_sha256='a' * 64))
        self.assertEqual(other_row['ref1_identity']['kind'], 'unknown')
        self.assertEqual(other_row['ref1_identity']['status'], 'unobserved')


if __name__ == '__main__':
    unittest.main()
