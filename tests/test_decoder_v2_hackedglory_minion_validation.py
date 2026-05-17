import unittest
from unittest.mock import patch

from vg.decoder_v2.hackedglory_minion_validation import build_hackedglory_minion_validation


class TestHackedGloryMinionValidation(unittest.TestCase):
    def test_build_report_marks_nonfinals_policy_safe_and_experimental_context_only(self) -> None:
        nonfinals = {
            "policy": "nonfinals-baseline-0e",
            "player_rows": 4,
            "accepted_rows": 2,
            "accepted_exact": 2,
            "accepted_error": 0,
            "precision": 1.0,
            "coverage": 0.5,
            "rows": [
                {"accepted": True, "error": 0},
                {"accepted": True, "error": 0},
            ],
        }
        experimental = {
            "policy": "nonfinals-or-low-mixed-ratio-experimental",
            "player_rows": 4,
            "accepted_rows": 3,
            "accepted_exact": 2,
            "accepted_error": 1,
            "precision": 2 / 3,
            "coverage": 0.75,
            "rows": [
                {
                    "accepted": True,
                    "error": 1,
                    "player_name": "p1",
                    "baseline_0e": 7,
                    "truth_minion_kills": 6,
                }
            ],
        }
        cross_validation = {
            "row_count": 4,
            "series_count": 2,
            "replay_count": 2,
            "fixed_policy_reference": [{"policy": "accept_nonfinals_only"}],
            "leave_one_series_out": {"summary": {"failed_folds": 1}},
            "leave_one_replay_out": {"summary": {"failed_folds": 0}},
        }
        window_report = {
            "complete_fixture_matches": 2,
            "global_positive_target_samples": 10,
            "global_nonpositive_target_samples": 30,
            "global_enriched_headers": [{"header_hex": "28043f"}],
            "global_enriched_credit_patterns": [{"pattern": "0x02@14.34"}],
            "per_match": [
                {
                    "fixture_directory_name": "2",
                    "positive_residual_players": 1,
                    "positive_target_samples": 10,
                },
                {
                    "fixture_directory_name": "1",
                    "positive_residual_players": 0,
                    "positive_target_samples": 0,
                },
            ],
        }

        with patch(
            "vg.decoder_v2.hackedglory_minion_validation.validate_minion_policy",
            side_effect=[nonfinals, experimental],
        ), patch(
            "vg.decoder_v2.hackedglory_minion_validation.build_minion_policy_cross_validation",
            return_value=cross_validation,
        ), patch(
            "vg.decoder_v2.hackedglory_minion_validation.build_minion_window_fixture_report",
            return_value=window_report,
        ):
            report = build_hackedglory_minion_validation("truth.json")

        self.assertEqual(report["schema_version"], "decoder_v2.hackedglory_minion_validation.v1")
        self.assertEqual(report["assessment"]["product_safe_policy"], "nonfinals-baseline-0e")
        self.assertEqual(report["assessment"]["default_policy_should_remain"], "none")
        self.assertFalse(report["assessment"]["experimental_policy_safe_for_default"])
        self.assertEqual(report["assessment"]["source_target_reward_status"], "context_only")
        self.assertIn("failed folds", report["assessment"]["reasons"][2])
        self.assertEqual(
            report["source_target_reward_window"]["positive_residual_match_count"],
            1,
        )
        self.assertEqual(
            len(
                report["policy_validation"]["nonfinals-or-low-mixed-ratio-experimental"][
                    "accepted_error_rows"
                ]
            ),
            1,
        )


if __name__ == "__main__":
    unittest.main()
