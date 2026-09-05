import math
import struct
import unittest

from vg.core.kda_detector import KDADetector
from vg.core.vgr_records import VGRRecordError


def packet(timestamp: float, opcode: int, payload: bytes = b"") -> bytes:
    body = struct.pack(">H", opcode) + payload
    return struct.pack(">fI", timestamp, len(body)) + body


def kill_payload(entity_id: int, *, code: int = 0x29) -> bytes:
    return struct.pack(">IIIB", entity_id, 0xFFFFFFFF, 0x3F800000, code) + b"k" * 9


def death_payload(entity_id: int, *, tail: bytes = b"\x00\x00") -> bytes:
    return struct.pack(">I", entity_id) + tail


def credit_payload(
    entity_id: int,
    value: float,
    *,
    index: int = 0,
    mode: int = 0,
    flags: bytes = b"\x01\x00",
    trailer: bytes = b"\xaa\xbb",
) -> bytes:
    return struct.pack(">IfBB", entity_id, value, index, mode) + flags + trailer


class KDARecordFramingTests(unittest.TestCase):
    def test_uses_each_record_own_timestamp_without_raw_extraction_caps(self) -> None:
        killer = 0x123405DC
        victim = 0x89AB05DD
        data = (
            packet(2001.0, 0x041C, kill_payload(killer))
            + packet(345.0, 0x9999, b"next")
            + packet(0.0, 0x0431, death_payload(victim))
        )
        detector = KDADetector({killer, victim})

        detector.process_frame(7, data)

        self.assertEqual(len(detector.kill_events), 1)
        self.assertEqual(detector.kill_events[0].timestamp, 2001.0)
        self.assertEqual(detector.kill_events[0].file_offset, 7)
        self.assertEqual(len(detector.death_events), 1)
        self.assertEqual(detector.death_events[0].timestamp, 0.0)
        self.assertEqual(
            detector.death_events[0].file_offset,
            len(packet(2001.0, 0x041C, kill_payload(killer)))
            + len(packet(345.0, 0x9999, b"next"))
            + 7,
        )

    def test_final_0431_record_is_read_without_a_following_record(self) -> None:
        victim = 0x10203040
        detector = KDADetector({victim})

        detector.process_frame(3, packet(18.25, 0x0431, death_payload(victim)))

        self.assertEqual(
            [(event.victim_eid, event.timestamp, event.file_offset)
             for event in detector.death_events],
            [(victim, 18.25, 7)],
        )

    def test_death_uses_own_timestamp_instead_of_the_next_record_timestamp(self) -> None:
        victim = 0x000005DD
        death = packet(12.5, 0x0431, death_payload(victim))
        detector = KDADetector({victim})

        detector.process_frame(4, death + packet(777.0, 0x9999, b"next"))

        self.assertEqual(detector.death_events[0].timestamp, 12.5)

    def test_reads_full_32_bit_entity_reference_without_aliasing_low_bits(self) -> None:
        valid = 0x123405DC
        alias = 0xFFFF05DC
        detector = KDADetector({valid})
        data = (
            packet(1.0, 0x041C, kill_payload(alias))
            + packet(2.0, 0x041C, kill_payload(valid))
            + packet(3.0, 0x0431, death_payload(alias))
            + packet(4.0, 0x0431, death_payload(valid))
            + packet(5.0, 0x041D, credit_payload(alias, 1.0, index=0x0E))
            + packet(6.0, 0x041D, credit_payload(valid, 1.0, index=0x0E))
        )

        detector.process_frame(1, data)

        self.assertEqual([event.killer_eid for event in detector.kill_events], [valid])
        self.assertEqual([event.victim_eid for event in detector.death_events], [valid])
        self.assertEqual(detector.get_results()[valid].minion_kills, 1)

    def test_ignores_candidate_signatures_embedded_in_another_payload(self) -> None:
        player = 0x000005DC
        fake_kill = packet(11.0, 0x041C, kill_payload(player))
        fake_death = packet(12.0, 0x0431, death_payload(player)) + struct.pack(">f", 12.0)
        fake_credit = packet(
            13.0, 0x041D, credit_payload(player, 1.0, index=0x0E)
        )
        detector = KDADetector({player})

        detector.process_frame(
            1, packet(1.0, 0x9999, fake_kill + fake_death + fake_credit)
        )

        self.assertEqual(detector.kill_events, [])
        self.assertEqual(detector.death_events, [])
        self.assertEqual(detector.get_results()[player].minion_kills, 0)

    def test_requires_exact_content_lengths_and_existing_marker_predicates(self) -> None:
        player = 0x000005DC
        wrong_length_kill = packet(1.0, 0x041C, kill_payload(player) + b"x")
        wrong_marker_kill = packet(2.0, 0x041C, kill_payload(player, code=0x2A))
        wrong_length_death = packet(3.0, 0x0431, death_payload(player) + b"x")
        wrong_tail_death = packet(4.0, 0x0431, death_payload(player, tail=b"\x00\x01"))
        wrong_length_credit = packet(
            5.0, 0x041D, credit_payload(player, 1.0, index=0x0E) + b"x"
        )
        detector = KDADetector({player})

        detector.process_frame(
            1,
            wrong_length_kill
            + wrong_marker_kill
            + wrong_length_death
            + wrong_tail_death
            + wrong_length_credit,
        )

        self.assertEqual(detector.kill_events, [])
        self.assertEqual(detector.death_events, [])
        self.assertEqual(detector.get_results()[player].minion_kills, 0)

    def test_malformed_framing_raises_without_partial_state_or_fallback(self) -> None:
        player = 0x000005DC
        detector = KDADetector({player})
        malformed = packet(1.0, 0x041C, kill_payload(player)) + b"\x00"

        with self.assertRaises(VGRRecordError):
            detector.process_frame(1, malformed)

        self.assertEqual(detector.kill_events, [])
        self.assertEqual(detector.death_events, [])
        self.assertEqual(detector.get_results()[player].minion_kills, 0)

    def test_preserves_credit_index_mode_timestamp_and_complete_payload(self) -> None:
        killer = 0x000005DC
        assister = 0x000005DD
        payload = credit_payload(
            assister,
            37.125,
            index=9,
            mode=1,
            flags=b"\x00\x01",
            trailer=b"\x7e\x7f",
        )
        kill = packet(10.0, 0x041C, kill_payload(killer))
        detector = KDADetector({killer, assister})

        detector.process_frame(2, kill + packet(10.5, 0x041D, payload))

        credit = detector.kill_events[0].credits[0]
        self.assertEqual(credit.eid, assister)
        self.assertEqual(credit.value, 37.12)
        self.assertEqual(credit.offset, len(kill) + 7)
        self.assertEqual(credit.action, 9)
        self.assertEqual(credit.mode, 1)
        self.assertEqual(credit.timestamp, 10.5)
        self.assertEqual(credit.raw_payload_hex, payload.hex())
        self.assertTrue(math.isfinite(credit.value))

    def test_assist_window_and_next_structural_kill_stop_match_legacy_policy(self) -> None:
        killer = 0x000005DC
        assister = 0x000005DD
        non_player = 0x00000999
        kill = packet(10.0, 0x041C, kill_payload(killer))
        included_gold = packet(10.1, 0x041D, credit_payload(assister, 27.5, index=9))
        included_flag = packet(10.2, 0x041D, credit_payload(assister, 1.0, index=9))
        stop = packet(10.3, 0x041C, kill_payload(non_player))
        ignored_after_stop = packet(
            10.4, 0x041D, credit_payload(assister, 99.0, index=9)
        )
        detector = KDADetector({killer, assister})

        detector.process_frame(
            1, kill + included_gold + included_flag + stop + ignored_after_stop
        )

        self.assertEqual(
            [(credit.eid, credit.value) for credit in detector.kill_events[0].credits],
            [(assister, 27.5), (assister, 1.0)],
        )
        results = detector.get_results(
            team_map={killer: "left", assister: "left"}
        )
        self.assertEqual(results[assister].assists, 1)

    def test_credit_signature_at_or_beyond_legacy_window_is_excluded(self) -> None:
        killer = 0x000005DC
        assister = 0x000005DD
        kill = packet(1.0, 0x041C, kill_payload(killer))
        # kill signature is 7; a 483-byte record puts the next signature at 522,
        # the last included offset before the strict 7 + 16 + 500 boundary.
        filler_to_522 = packet(1.1, 0x9999, b"x" * 473)
        included = packet(1.2, 0x041D, credit_payload(assister, 1.0))
        detector = KDADetector({killer, assister})

        detector.process_frame(1, kill + filler_to_522 + included)

        self.assertEqual(
            [credit.offset for credit in detector.kill_events[0].credits], [522]
        )

        # One extra filler byte moves the same candidate to the excluded boundary.
        detector = KDADetector({killer, assister})
        filler_to_523 = packet(1.1, 0x9999, b"x" * 474)
        detector.process_frame(1, kill + filler_to_523 + included)
        self.assertEqual(detector.kill_events[0].credits, [])


if __name__ == "__main__":
    unittest.main()
