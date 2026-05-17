import unittest
from unittest.mock import patch

from vg.decoder_v2.endgame_burst_probe import build_endgame_burst_report
from vg.decoder_v2.models import PlayerEventRecord


class TestEndgameBurstProbe(unittest.TestCase):
    def test_build_endgame_burst_report_finds_tail_focus_candidate(self) -> None:
        parsed = {
            "replay_name": "sample",
            "replay_file": "sample.0.vgr",
            "match_info": {"mode": "GameMode_5v5_Ranked"},
            "teams": {
                "left": [{"name": "p1", "team": "left", "entity_id": 0x3412}],
                "right": [],
            },
        }
        # BE entity for LE 0x3412 is 0x1234.
        credit = b"\x10\x04\x1d\x00\x00\x12\x34\x3f\x80\x00\x00\x0e"
        frames = [(0, b"\x00" * 8), (10, credit * 4)]
        player_events = [
            PlayerEventRecord(10, 0x3412, 0x44, "00" * 32),
            PlayerEventRecord(10, 0x3412, 0x44, "00" * 32),
            PlayerEventRecord(10, 0x3412, 0x45, "00" * 32),
        ]

        with patch("vg.decoder_v2.endgame_burst_probe.VGRParser") as parser_cls, patch(
            "vg.decoder_v2.endgame_burst_probe.load_frames",
            return_value=frames,
        ), patch(
            "vg.decoder_v2.endgame_burst_probe.iter_player_events",
            return_value=player_events,
        ):
            parser_cls.return_value.parse.return_value = parsed
            report = build_endgame_burst_report("sample.0.vgr", tail_frames=1)

        self.assertGreaterEqual(report["summary"]["focus_candidates"], 1)
        self.assertEqual(report["focus_candidates"][0]["player_name"], "p1")
        self.assertIn("credit", report["tail_known_header_summary"])


if __name__ == "__main__":
    unittest.main()
