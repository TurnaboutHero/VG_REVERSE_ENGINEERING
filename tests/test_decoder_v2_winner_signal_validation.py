import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vg.decoder_v2.winner_signal_validation import build_winner_signal_validation


class TestWinnerSignalValidation(unittest.TestCase):
    def test_build_validation_rejects_mixed_top_focus_results(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            left_replay = Path(temp_dir) / "left.0.vgr"
            right_replay = Path(temp_dir) / "right.0.vgr"
            left_replay.write_bytes(b"sample")
            right_replay.write_bytes(b"sample")

            matches = [
                {
                    "replay_name": "left",
                    "replay_file": str(left_replay),
                    "match_info": {"winner": "left"},
                },
                {
                    "replay_name": "right",
                    "replay_file": str(right_replay),
                    "match_info": {"winner": "right"},
                },
            ]
            reports = [
                {
                    "summary": {"focus_candidates": 2},
                    "focus_candidates": [
                        {
                            "player_name": "left-carry",
                            "team": "left",
                            "known_header_total": 7,
                            "known_headers": {"credit": 7},
                        },
                        {
                            "player_name": "right-carry",
                            "team": "right",
                            "player_event_total": 4,
                            "player_event_actions": {"0x44": 4},
                        },
                    ],
                    "tail_generic_header_summary": [
                        {"header_hex": "080402", "tail_count": 5, "all_count": 5, "tail_fraction": 1.0}
                    ],
                },
                {
                    "summary": {"focus_candidates": 1},
                    "focus_candidates": [
                        {
                            "player_name": "left-carry",
                            "team": "left",
                            "player_event_total": 9,
                            "player_event_actions": {"0x05": 9},
                        }
                    ],
                    "tail_generic_header_summary": [],
                },
            ]

            with patch(
                "vg.decoder_v2.winner_signal_validation._load_truth_matches",
                return_value=matches,
            ), patch(
                "vg.decoder_v2.winner_signal_validation.build_endgame_burst_report",
                side_effect=reports,
            ):
                report = build_winner_signal_validation(str(Path(temp_dir) / "truth.json"), top=2)

        self.assertEqual(report["schema_version"], "decoder_v2.winner_signal_validation.v1")
        self.assertEqual(report["summary"]["matches_processed"], 2)
        self.assertEqual(report["summary"]["top_focus_winner_side"], 1)
        self.assertEqual(report["summary"]["top_focus_loser_side"], 1)
        self.assertEqual(report["summary"]["top_focus_winner_side_rate"], 0.5)
        self.assertEqual(report["summary"]["assessment"]["status"], "rejected")
        self.assertEqual(report["summary"]["repeated_tail_concentrated_generic_headers"], {"080402": 1})
        self.assertEqual(report["matches"][0]["top_focus_candidates"][0]["candidate_family"], "known:credit")

    def test_build_validation_promotes_consistent_winner_side_focus(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            matches = []
            reports = []
            for idx in range(3):
                replay = Path(temp_dir) / f"match{idx}.0.vgr"
                replay.write_bytes(b"sample")
                matches.append(
                    {
                        "replay_name": f"match{idx}",
                        "replay_file": str(replay),
                        "match_info": {"winner": "right"},
                    }
                )
                reports.append(
                    {
                        "summary": {"focus_candidates": 1},
                        "focus_candidates": [
                            {
                                "player_name": f"right-{idx}",
                                "team": "right",
                                "known_header_total": 7,
                                "known_headers": {"credit": 7},
                            }
                        ],
                        "tail_generic_header_summary": [],
                    }
                )

            with patch(
                "vg.decoder_v2.winner_signal_validation._load_truth_matches",
                return_value=matches,
            ), patch(
                "vg.decoder_v2.winner_signal_validation.build_endgame_burst_report",
                side_effect=reports,
            ):
                report = build_winner_signal_validation(str(Path(temp_dir) / "truth.json"))

        self.assertEqual(report["summary"]["top_focus_winner_side"], 3)
        self.assertEqual(report["summary"]["top_focus_loser_side"], 0)
        self.assertEqual(report["summary"]["assessment"]["status"], "candidate")


if __name__ == "__main__":
    unittest.main()
