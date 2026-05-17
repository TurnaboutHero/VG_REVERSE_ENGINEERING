import unittest
from unittest.mock import patch

from vg.decoder_v2.hackedglory_xp_level_validation import build_hackedglory_xp_level_validation


class TestHackedGloryXpLevelValidation(unittest.TestCase):
    def test_build_report_keeps_reward_pulses_separate_from_total_xp(self) -> None:
        action02 = {
            "rows": [
                {
                    "value": 20.0,
                    "match_count": 2,
                    "event_count": 10,
                    "shared_cluster_rate": 0.1,
                    "subfamily_label": "shared_reward_candidate",
                },
                {
                    "value": -50.0,
                    "match_count": 2,
                    "event_count": 8,
                    "shared_cluster_rate": 0.0,
                    "subfamily_label": "solo_reward_candidate",
                },
                {
                    "value": 3.14,
                    "match_count": 1,
                    "event_count": 1,
                    "shared_cluster_rate": 0.0,
                    "subfamily_label": "unclassified",
                },
            ]
        }
        level = {
            "matches_processed": 2,
            "summary": {
                "matches_with_viable_level_candidates": 0,
                "byte15_rejected_matches": 2,
                "heartbeat_records": 100,
            },
            "matches": [
                {"replay_name": "a", "summary": {"credit_action_03_players_with_records": 1}},
                {"replay_name": "b", "summary": {"credit_action_03_players_with_records": 0}},
            ],
        }

        with patch(
            "vg.decoder_v2.hackedglory_xp_level_validation.build_action02_subfamily_summary",
            return_value=action02,
        ), patch(
            "vg.decoder_v2.hackedglory_xp_level_validation.build_level_signal_batch",
            return_value=level,
        ):
            report = build_hackedglory_xp_level_validation("truth.json")

        self.assertEqual(report["schema_version"], "decoder_v2.hackedglory_xp_level_validation.v1")
        self.assertEqual(report["assessment"]["action02_status"], "reward_pulse_context")
        self.assertEqual(report["assessment"]["xp_total_export_status"], "not_safe")
        self.assertEqual(report["assessment"]["level_export_status"], "not_safe")
        self.assertEqual(report["assessment"]["blocking_fields"], ["xp_total", "level"])
        self.assertEqual(report["action02_reward_context"]["reward_candidate_bucket_count"], 2)
        self.assertEqual(report["level_signal_probe"]["matches_with_viable_level_candidates"], 0)


if __name__ == "__main__":
    unittest.main()
