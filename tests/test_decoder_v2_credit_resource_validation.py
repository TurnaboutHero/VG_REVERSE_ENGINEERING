import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vg.decoder_v2.credit_resource_validation import (
    build_credit_resource_validation,
    build_match_credit_resource_report,
)


def _credit(entity_id_be: int, value: float, action: int, sell_flag: int = 0) -> bytes:
    return (
        bytes.fromhex("10041d0000")
        + entity_id_be.to_bytes(2, "big")
        + struct.pack(">f", value)
        + bytes([action, sell_flag])
    )


class TestCreditResourceValidation(unittest.TestCase):
    def test_match_report_uses_action_06_no_sell_gold_formula(self) -> None:
        parsed = {
            "replay_name": "sample",
            "teams": {
                "left": [{"name": "p1", "entity_id": 0x3412}],
                "right": [{"name": "p2", "entity_id": 0x7856}],
            },
        }
        match = {
            "replay_name": "sample",
            "replay_file": "sample.0.vgr",
            "players": {
                "p1": {"gold": 5600},
                "p2": {"gold": 6600},
            },
        }
        data = b"".join(
            [
                _credit(0x1234, 5000.0, 0x06),
                _credit(0x1234, 100.0, 0x06, sell_flag=0x01),
                _credit(0x1234, 1000.0, 0x0D),
                _credit(0x5678, 6000.0, 0x06),
            ]
        )

        with patch("vg.decoder_v2.credit_resource_validation.VGRParser") as parser_cls, patch(
            "vg.decoder_v2.credit_resource_validation.load_frames",
            return_value=[(0, data)],
        ):
            parser_cls.return_value.parse.return_value = parsed
            report = build_match_credit_resource_report(match)

        current = next(
            row for row in report["formulas"] if row["formula"] == "base600_plus_0x06_no_sell"
        )
        with_jungle = next(
            row for row in report["formulas"] if row["formula"] == "base600_plus_0x06_0x0d"
        )

        self.assertEqual(current["accuracy_5pct"], 1.0)
        self.assertEqual(current["within_5pct"], 2)
        self.assertEqual(current["worst_errors"][0]["replay_name"], "sample")
        self.assertEqual(with_jungle["within_5pct"], 1)
        self.assertEqual(report["sell_flag_counts"], {"0x06:0x01": 1})

    def test_build_credit_resource_validation_batches_matches(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            replay_path = Path(temp_dir) / "sample.0.vgr"
            replay_path.write_bytes(b"sample")
            truth_path = Path(temp_dir) / "truth.json"
            truth_path.write_text("{}", encoding="utf-8")
            match = {
                "replay_name": "sample",
                "replay_file": str(replay_path),
                "players": {"p1": {"gold": 5600}},
            }

            with patch(
                "vg.decoder_v2.credit_resource_validation._load_truth_matches",
                return_value=[match],
            ), patch(
                "vg.decoder_v2.credit_resource_validation.build_match_credit_resource_report",
                return_value={
                    "replay_name": "sample",
                    "formulas": [
                        {
                            "formula": "base600_plus_0x06_no_sell",
                            "actions": ["0x06"],
                            "worst_errors": [
                                {
                                    "player_name": "p1",
                                    "truth_gold": 5600,
                                    "estimated_gold": 5600,
                                    "error": 0,
                                    "error_pct": 0.0,
                                }
                            ],
                        }
                    ],
                },
            ):
                report = build_credit_resource_validation(str(truth_path))

        self.assertEqual(report["schema_version"], "decoder_v2.credit_resource_validation.v1")
        self.assertEqual(report["matches_processed"], 1)
        self.assertEqual(report["complete_fixture_matches"], 1)
        self.assertEqual(report["summary"]["best_formula_by_10pct"]["formula"], "base600_plus_0x06_no_sell")
        self.assertEqual(
            report["summary"]["best_complete_fixture_formula_by_10pct"]["formula"],
            "base600_plus_0x06_no_sell",
        )


if __name__ == "__main__":
    unittest.main()
