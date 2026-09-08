import struct
import unittest
from unittest.mock import patch

from vg.decoder_v2.completeness import extract_replay_signals, assess_completeness
from vg.decoder_v2.models import CompletenessStatus, ReplaySignalSummary


def record(timestamp: float, opcode: int, payload: bytes) -> bytes:
    return struct.pack('>fIH', timestamp, len(payload) + 2, opcode) + payload


def death(timestamp: float, entity: int = 2000) -> bytes:
    return record(timestamp, 0x0431, struct.pack('>IH', entity, 0))


def item(timestamp: float) -> bytes:
    return record(timestamp, 0x043d, struct.pack('>I', 2000) + bytes(10))


class TestCompletenessRecordFraming(unittest.TestCase):
    def signals(self, frames: list[tuple[int, bytes]]) -> ReplaySignalSummary:
        with patch('vg.decoder_v2.completeness.VGRParser') as parser, patch(
            'vg.decoder_v2.completeness.load_frames', return_value=frames
        ):
            parser.return_value.parse.return_value = {
                'teams': {'left': [], 'right': []},
                'replay_name': 'match', 'replay_file': 'match.0.vgr',
            }
            return extract_replay_signals('match.0.vgr')

    def test_owning_timestamp_when_followed_by_later_record(self) -> None:
        # Given: valid records with distinct neighboring timestamps.
        data = death(100) + item(200) + record(300, 0x9999, b'')
        # When: extracting the real framed signal path.
        signals = self.signals([(0, data)])
        # Then: each candidate owns its prefix timestamp.
        self.assertEqual((signals.crystal_ts, signals.max_death_header_ts, signals.max_item_ts), (100, 100, 200))

    def test_final_record_needs_no_following_bytes(self) -> None:
        for data, field in ((death(100), 'max_death_header_ts'), (item(200), 'max_item_ts')):
            with self.subTest(field=field):
                signals = self.signals([(0, data)])
                self.assertEqual(getattr(signals, field), 100 if field == 'max_death_header_ts' else 200)

    def test_embedded_fake_signatures_are_ignored(self) -> None:
        fake = death(100) + item(200) + record(300, 0x9999, b'')
        signals = self.signals([(0, record(50, 0x9999, fake))])
        self.assertEqual((signals.crystal_ts, signals.max_death_header_ts, signals.max_item_ts), (None, None, None))

    def test_full_reference_does_not_alias_candidate(self) -> None:
        signals = self.signals([(0, death(100, 0x10007d0) + record(200, 0x9999, b''))])
        self.assertIsNone(signals.crystal_ts)
        self.assertIsNone(signals.max_death_header_ts)

    def test_malformed_tail_withholds_candidates(self) -> None:
        signals = self.signals([(0, death(100) + b'\x00')])
        self.assertEqual((signals.crystal_ts, signals.max_death_header_ts, signals.max_item_ts), (None, None, None))
        self.assertFalse(signals.native_clock_valid)
        self.assertEqual(signals.native_clock_status, 'malformed_records')
        self.assertEqual(assess_completeness(signals).status, CompletenessStatus.COMPLETENESS_UNKNOWN)

    def test_candidate_time_bounds_are_preserved(self) -> None:
        for timestamp in (0, 60, 2400, 5000):
            with self.subTest(timestamp=timestamp):
                signals = self.signals([(0, death(timestamp) + item(timestamp))])
                self.assertIsNone(signals.crystal_ts)
                expected = timestamp if 0 < timestamp < 5000 else None
                self.assertEqual((signals.max_death_header_ts, signals.max_item_ts), (expected, expected))

    def test_exact_lengths_and_candidate_guards_are_required(self) -> None:
        # Given: framed near-matches violating each legacy guard.
        cases = (
            record(100, 0x0431, struct.pack('>IH', 2000, 1)),
            record(100, 0x0431, struct.pack('>IH', 2000, 0) + b'\x00'),
            record(100, 0x043d, struct.pack('>I', 0x10007d0) + bytes(10)),
            record(100, 0x043d, struct.pack('>I', 2000) + bytes(11)),
        )
        for data in cases:
            with self.subTest(data=data.hex()):
                signals = self.signals([(0, data)])
                self.assertEqual((signals.crystal_ts, signals.max_death_header_ts, signals.max_item_ts), (None, None, None))

    def test_later_malformed_frame_discards_earlier_candidates(self) -> None:
        # Given: a complete candidate frame before a truncated next frame.
        signals = self.signals([(0, death(100) + item(200)), (1, b'\x00')])
        self.assertEqual((signals.crystal_ts, signals.max_death_header_ts, signals.max_item_ts), (None, None, None))
        self.assertFalse(signals.native_clock_valid)
