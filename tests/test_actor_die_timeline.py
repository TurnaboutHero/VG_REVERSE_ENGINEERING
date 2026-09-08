import contextlib
import io
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

from vg.analysis.event_timeline import iter_timeline, main


def packet(timestamp, opcode, payload):
    return struct.pack('>fIH', timestamp, len(payload) + 2, opcode) + payload


def death(victim=1500, source=2007):
    return struct.pack('>II', victim, source) + bytes.fromhex('0011aabbccff')


class ActorDieTimelineTests(unittest.TestCase):
    def test_native_fields_raw_source_and_sentinel_are_lossless(self):
        for source in (2007, 1501, 0, 0xFFFFFFFF):
            with self.subTest(source=source), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'match.0.vgr'
                payload = death(source=source)
                path.write_bytes(packet(978.115417, 0x0430, payload))
                rows = list(iter_timeline(path))
                self.assertEqual(len(rows), 1)
                row = rows[0]
                self.assertEqual(row['native_label'], 'ActionActorDie')
                self.assertEqual(row['native_class'], 'Nuo::Kindred::ActionActorDie')
                self.assertEqual(row['native_type'], 'actor_die_action')
                self.assertEqual(row['native_victim_id'], 1500)
                self.assertEqual(row['native_source_raw'], source)
                self.assertEqual(row['native_source_is_sentinel'], source == 0xFFFFFFFF)
                self.assertEqual((row['ref0'], row['ref1']), (1500, source))
                self.assertEqual(row['native_evidence'], 'windows-659f9eed')
                self.assertEqual(row['native_evidence_sha256'], '659f9eed557a426db57554d2a768efe34ba9fe02ba1085d77db64390b0d92642')
                self.assertEqual(row['remaining_hex'], '0011aabbccff')
                self.assertEqual(row['payload_hex'], payload.hex())
                self.assertEqual(row['content_length'], 16)
                self.assertEqual(row['timestamp'], struct.unpack('>f', struct.pack('>f', 978.115417))[0])
                for forbidden in ('credited_killer', 'native_stat', 'game_timestamp', 'match_completed'):
                    self.assertNotIn(forbidden, row)
                for entity in (1500, source):
                    self.assertEqual(list(iter_timeline(path, entity_ids=[entity])), rows)
                self.assertEqual(list(iter_timeline(path, entity_ids=[9999])), [])

    def test_short_and_long_payloads_remain_uninterpreted(self):
        for size in (0, 7, 8, 13, 15, 16, 30):
            with self.subTest(size=size), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'match.0.vgr'
                payload = bytes(range(size))
                path.write_bytes(packet(1, 0x0430, payload))
                row, = iter_timeline(path)
                self.assertEqual(row['decoding_status'], 'unexpected_content_length')
                self.assertEqual(row['expected_content_length'], 16)
                self.assertEqual(row['payload_hex'], payload.hex())
                self.assertFalse(any(key.startswith('native_') for key in row))
                self.assertNotIn('ref0', row)
                self.assertNotIn('ref1', row)

    def test_framing_numeric_sections_and_separate_state_counter_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake = packet(1, 0x9999, packet(70, 0x0430, death(9999)))
            counter = struct.pack('>IIfBB', 1500, 0xFFFFFFFF, 1, 42, 0) + bytes(8)
            (root / 'match.10.vgr').write_bytes(packet(90, 0x0430, death(1501)))
            path = root / 'match.2.vgr'
            path.write_bytes(fake + packet(100, 0x0430, death()) + packet(100, 0x041c, counter)
                             + packet(101, 0x0431, struct.pack('>I', 1500) + bytes(2)))
            rows = list(iter_timeline(path))
            self.assertEqual([row['opcode'] for row in rows], [0x0430, 0x041c, 0x0431, 0x0430])
            self.assertEqual([row['timestamp'] for row in rows], [100, 100, 101, 90])
            self.assertEqual([row['frame_idx'] for row in rows], [2, 2, 2, 10])
            self.assertEqual([row['record_index'] for row in rows], [1, 2, 3, 0])
            self.assertEqual(rows[0]['record_offset'], len(fake))
            self.assertEqual(rows[1]['native_stat'], 'deaths')
            self.assertEqual(rows[2]['native_type'], 'actor_state_transition')
            self.assertEqual(list(iter_timeline(path, entity_ids=[9999])), [])

    def test_cli_help_source_filter_and_truncated_input(self):
        result = subprocess.run([sys.executable, '-m', 'vg.analysis.event_timeline', '--help'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('ActionActorDie', result.stdout)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'match.0.vgr'
            framed = packet(100, 0x0430, death())
            path.write_bytes(framed)
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                status = main([str(path), '--entity', '2007'])
            self.assertEqual(status, 0)
            self.assertEqual(json.loads(stdout.getvalue())['native_source_raw'], 2007)
            path.write_bytes(framed[:-1])
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                self.assertEqual(main([str(path)]), 2)
            self.assertIn('error:', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
