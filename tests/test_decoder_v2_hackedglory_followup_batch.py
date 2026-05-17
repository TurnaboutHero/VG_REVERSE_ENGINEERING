import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vg.decoder_v2.hackedglory_followup_batch import build_hackedglory_followup_batch


class TestHackedGloryFollowupBatch(unittest.TestCase):
    def test_build_batch_aggregates_probe_summaries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            replay_path = Path(temp_dir) / "sample.0.vgr"
            replay_path.write_bytes(b"sample")
            truth_path = Path(temp_dir) / "truth.json"
            truth_path.write_text("{}", encoding="utf-8")

            match = {
                "replay_name": "sample",
                "replay_file": str(replay_path),
                "match_info": {"winner": "left"},
                "players": {
                    "p1": {"kills": 1, "deaths": 0, "assists": 2, "gold": 5000, "minion_kills": 20}
                },
            }
            semantic_report = {
                "summary": {
                    "target_status_counts": {"covered": 9, "partial": 4, "missing": 1},
                    "local_semantic_ready_players": 10,
                    "strict_hackedglory_replay_ready_players": 0,
                    "scoreboard_readiness": {
                        "player_count": 1,
                        "identity_players": 1,
                        "kda_players": 1,
                        "gold_players": 1,
                        "xp_players": 0,
                        "level_players": 0,
                        "local_export_ready_players": 1,
                        "strict_hackedglory_replay_ready_players": 0,
                        "blocking_fields": ["xp_total", "level"],
                    },
                },
                "targets": [
                    {"target": "gold_xp_total", "status": "missing"},
                    {"target": "winner_signal", "status": "covered"},
                    {"target": "level_skill", "status": "partial"},
                ],
            }
            resource_report = {
                "summary": {"family_counter_candidates": 2},
                "family_counter_candidates": [
                    {"action": "0x01", "encoding": "f32be", "payload_offset": 7}
                ],
                "credit_delta_summary": [{"action": "0x02", "count": 10}],
            }
            endgame_report = {
                "summary": {"focus_candidates": 1},
                "focus_candidates": [{"player_name": "p1", "team": "left"}],
                "tail_generic_header_summary": [{"header_hex": "10041d"}],
                "tail_known_header_summary": {"credit": 4},
            }
            minion_report = {
                "aggregate": {
                    "players": 1,
                    "positive_residual_players": 1,
                    "nonpositive_or_unknown_players": 0,
                    "positive_target_samples": 10,
                    "nonpositive_target_samples": 5,
                    "positive_enriched_headers": [
                        {"header_hex": "28043f", "delta_per_target_event": 0.5}
                    ],
                    "positive_enriched_credit_patterns": [
                        {"pattern": "0x02@14.34", "delta_per_target_event": 0.5}
                    ],
                }
            }

            with patch(
                "vg.decoder_v2.hackedglory_followup_batch._load_truth_matches",
                return_value=[match],
            ), patch(
                "vg.decoder_v2.hackedglory_followup_batch.probe_replay",
                return_value=semantic_report,
            ), patch(
                "vg.decoder_v2.hackedglory_followup_batch.build_resource_counter_report",
                return_value=resource_report,
            ), patch(
                "vg.decoder_v2.hackedglory_followup_batch.build_endgame_burst_report",
                return_value=endgame_report,
            ), patch(
                "vg.decoder_v2.hackedglory_followup_batch.build_minion_window_report",
                return_value=minion_report,
            ):
                report = build_hackedglory_followup_batch(str(truth_path), top=1)

        self.assertEqual(report["schema_version"], "decoder_v2.hackedglory_followup_batch.v1")
        self.assertEqual(report["summary"]["matches_processed"], 1)
        self.assertEqual(report["summary"]["semantic_missing_target_frequency"], {"gold_xp_total": 1})
        self.assertEqual(report["summary"]["scoreboard_readiness_totals"]["local_export_ready_players"], 1)
        self.assertEqual(report["summary"]["scoreboard_blocking_field_frequency"], {"xp_total": 1, "level": 1})
        self.assertEqual(report["summary"]["repeated_resource_family_candidates"], {"0x01:f32be@7": 1})
        self.assertEqual(report["summary"]["endgame_top_focus_result_counts"], {"winner_side": 1})
        self.assertEqual(report["summary"]["endgame_top_focus_winner_side_rate"], 1.0)
        self.assertEqual(report["summary"]["repeated_endgame_focus_candidates"], {"left:p1": 1})
        self.assertEqual(report["summary"]["repeated_minion_enriched_headers"], {"28043f": 1})
        self.assertEqual(report["matches"][0]["truth_totals"]["gold"], 5000)
        self.assertTrue(report["matches"][0]["endgame_burst"]["top_focus_candidates"][0]["winner_side"])


if __name__ == "__main__":
    unittest.main()
