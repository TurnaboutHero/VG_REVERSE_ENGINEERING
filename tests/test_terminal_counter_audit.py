from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest

from vg.analysis.terminal_counter_audit import audit_counter_gaps, main
from vg.core.vgr_records import VGRRecordError


def packet(time, opcode, payload):
    return struct.pack('>fIH', time, len(payload) + 2, opcode) + payload


def anchor(time=0):
    payload = bytearray(69)
    struct.pack_into('>f', payload, 64, time)
    return packet(time, 0x046f, payload)


def die(time, victim=10):
    return packet(time, 0x0430, struct.pack('>II', victim, 20) + bytes(6))


def attribute(time, value=1, index=42, layer=0, mode=0, entity=10):
    return packet(time, 0x041c, struct.pack('>IIfBBB', entity, 0, value, index, layer, mode) + bytes(7))


def resource(time, value=1, index=11, mode=0, entity=10):
    return packet(time, 0x041d, struct.pack('>IfBB', entity, value, index, mode) + bytes(4))


def snapshot(time, deaths=3, layer=0, entity=10, length=746):
    payload = bytearray(length)
    struct.pack_into('>I', payload, 8, entity)
    struct.pack_into('>f', payload, 302, deaths)
    struct.pack_into('>I', payload, 326, layer)
    return packet(time, 0x03f3, payload)


class TerminalCounterAuditTests(unittest.TestCase):
    def audit(self, *records, **kwargs):
        return audit_counter_gaps([(0, anchor() + b''.join(records))], [10, 20], **kwargs)

    def test_exact_then_unique_delayed_and_unmatched_increment(self):
        report = self.audit(attribute(1), die(1), die(2), attribute(2.05), attribute(4))
        self.assertEqual(report['counts']['exact_pairs'], 1)
        self.assertEqual(report['counts']['window_pairs'], 1)
        self.assertEqual(report['counts']['unmatched_increments'], 1)
        self.assertEqual(report['counts']['unmatched_actions'], 0)
        self.assertLess(report['pairs'][0]['increment']['seq'], report['pairs'][0]['action']['seq'])
        self.assertTrue(report['clock']['valid'])

    def test_exact_priority_does_not_consume_one_increment_twice(self):
        report = self.audit(die(1), die(1.05), attribute(1.05))
        self.assertEqual(report['counts']['exact_pairs'], 1)
        self.assertEqual(report['counts']['window_pairs'], 0)
        self.assertEqual(report['counts']['unmatched_actions'], 1)
        self.assertEqual(report['cases'][0]['action']['timestamp'], 1)

    def test_many_to_many_and_forward_ambiguity_are_retained(self):
        for records, method in [((die(1), die(1), attribute(1), attribute(1)), 'exact_timestamp'),
                                ((die(1), die(1.01), attribute(1.05)), 'forward_record_time_window')]:
            with self.subTest(method=method):
                report = self.audit(*records)
                self.assertEqual(report['pairs'], [])
                self.assertEqual(report['cases'], [])
                self.assertEqual(report['counts']['ambiguous_actions'], 2)
                self.assertEqual(report['ambiguities'][0]['method'], method)
                self.assertEqual(report['counts']['unmatched_increments'], 0)

    def test_terminal_case_keeps_same_time_set_snapshot_and_end_order(self):
        report = self.audit(
            snapshot(1), resource(1.5, index=14), die(2),
            attribute(2, value=7, mode=1), attribute(2, index=41, layer=3, mode=1),
            resource(2, index=14, mode=1, entity=20), resource(2, index=9),
            snapshot(2, deaths=8, length=750),
            packet(2, 0x0431, struct.pack('>I', 10) + bytes(2)),
            packet(2, 0x048d, b'opaque'), packet(2, 0x03f1, struct.pack('>IBB', 1, 1, 0)))
        case = report['cases'][0]
        self.assertEqual(case['pre_layer0_deaths']['value'], 3)
        self.assertEqual(case['eof_layer0_deaths']['value'], 8)
        self.assertEqual(case['latest_prior_player_kda_cs_operation']['opcode'], 0x041d)
        self.assertEqual(case['later_player_kda_cs_operation_count'], 3)
        self.assertEqual(case['later_victim_snapshots'][0]['deaths'], 8)
        self.assertEqual(len(case['later_0431']), 1)
        self.assertEqual(sum(row['count'] for row in case['later_victim_stat_operation_counts']), 3)
        self.assertEqual(case['next_048d']['seq'] + 1, case['next_03f1']['seq'])
        self.assertEqual(case['next_03f1']['timestamp'], case['action']['timestamp'])
        self.assertEqual(case['next_048d']['payload_length'], 6)
        self.assertNotIn('native_stat', case['next_048d'])
        self.assertEqual(report['last_player_snapshot']['seq'], case['later_victim_snapshots'][0]['seq'])
        self.assertEqual(report['last_player_kda_cs_operation']['ref0'], 20)
        self.assertEqual(report['counts']['unsupported_semantics'], 1)

    def test_no_baseline_is_never_assumed_zero_and_set_establishes_only_deaths(self):
        report = self.audit(attribute(1), die(2), attribute(3, value=4, mode=1), die(4))
        first, last = report['cases']
        self.assertIsNone(first['pre_layer0_deaths']['value'])
        self.assertEqual(first['eof_layer0_deaths']['value'], 4)
        self.assertEqual(last['pre_layer0_deaths']['value'], 4)
        self.assertEqual(last['pre_layer0_deaths']['status'], 'observed_layer0_only')

    def test_nonfinite_and_fractional_counts_are_explicit_and_json_safe(self):
        report = self.audit(snapshot(1), die(2), attribute(3, value=float('nan')),
                            resource(4, value=1.5), snapshot(5, deaths=float('inf')))
        self.assertEqual(report['counts']['unsupported_semantics'], 3)
        self.assertIsNone(report['cases'][0]['eof_layer0_deaths']['value'])
        self.assertIsNone(report['cases'][0]['later_victim_snapshots'][0]['deaths'])
        json.dumps(report, allow_nan=False)

    def test_malformed_known_payload_is_not_silently_counted_as_zero(self):
        report = self.audit(snapshot(1), die(2), packet(3, 0x041c, struct.pack('>I', 10)),
                            packet(4, 0x03f3, b''), packet(5, 0x0430, b''))
        self.assertEqual(report['counts']['unsupported_semantics'], 3)
        self.assertEqual(report['cases'][0]['later_unsupported_semantic_count'], 3)
        self.assertIsNone(report['cases'][0]['eof_layer0_deaths']['value'])
        self.assertEqual(report['counts']['player_actor_die'], 1)

    def test_strict_framing_rejects_truncation_and_nonfinite_timestamp(self):
        for data in (anchor() + b'cut', die(1)[:-1], die(float('nan'))):
            with self.subTest(data=data), self.assertRaises(VGRRecordError):
                audit_counter_gaps([(0, data)], [10])

    def test_clock_failure_is_preserved_and_record_order_not_time_sorted(self):
        report = audit_counter_gaps([(0, anchor(2) + die(3)),
                                     (2, anchor(1) + attribute(3.05))], [10])
        self.assertFalse(report['clock']['valid'])
        self.assertEqual(report['clock']['status'], 'mixed_segments')
        self.assertEqual(report['counts']['window_pairs'], 1)
        self.assertEqual(report['pairs'][0]['increment']['frame'], 2)
        missing_clock = audit_counter_gaps([(0, die(1))], [10])
        self.assertEqual(missing_clock['clock']['status'], 'unsupported_clock')

    def test_delayed_pair_requires_later_record_and_positive_delta(self):
        report = self.audit(attribute(2.05), die(2), window_seconds=0.1)
        self.assertEqual(report['counts']['window_pairs'], 0)
        self.assertEqual(report['counts']['unmatched_actions'], 1)
        report = self.audit(die(1), attribute(1.05), window_seconds=0)
        self.assertEqual(report['counts']['unmatched_actions'], 1)

    def test_arguments_require_explicit_players_order_and_finite_window(self):
        for ids in ([], [-1], [0xffffffff], [True]):
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                audit_counter_gaps([(0, anchor())], ids)
        for frames in ([(1, anchor()), (0, anchor())], [(0, anchor()), (0, anchor())]):
            with self.subTest(frames=frames), self.assertRaises(ValueError):
                audit_counter_gaps(frames, [10])
        for value in (-1, float('nan'), float('inf')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.audit(die(1), window_seconds=value)

    def test_cli_stdout_help_errors_and_section_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'match.0.vgr'
            original = anchor() + snapshot(1) + die(2)
            path.write_bytes(original)
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main([str(path), '--player', '0xa']), 0)
            report = json.loads(output.getvalue())
            self.assertEqual(report['players'], [10])
            self.assertEqual(len(report['sections'][0]['sha256']), 64)
            self.assertNotIn(directory, output.getvalue())
            self.assertEqual(path.read_bytes(), original)
            with redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as result:
                main(['--help'])
            self.assertEqual(result.exception.code, 0)
            for args in ([str(path)], [str(path), '--player', '-1']):
                with self.subTest(args=args), redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as result:
                    main(args)
                self.assertEqual(result.exception.code, 2)
            for args in ([str(path), '--player', '10', '--window-seconds', 'nan'],
                         [str(path.with_name('missing.0.vgr')), '--player', '10']):
                with self.subTest(args=args), redirect_stderr(io.StringIO()), redirect_stdout(io.StringIO()):
                    self.assertEqual(main(args), 2)


if __name__ == '__main__':
    unittest.main()
