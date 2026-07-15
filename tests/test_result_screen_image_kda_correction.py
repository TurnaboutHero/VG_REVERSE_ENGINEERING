import unittest

from vg.tools.result_screen_image_kda_correction import link_kda_rows_from_ocr_tokens


class TestResultScreenImageKdaCorrection(unittest.TestCase):
    def test_link_kda_rows_from_ocr_tokens_links_same_row_left_name(self) -> None:
        tokens = [
            ([[10, 100], [210, 100], [210, 140], [10, 140]], "2599_Ritoramu", 0.9),
            ([[900, 104], [990, 104], [990, 136], [900, 136]], "4/0/4", 0.99),
            ([[1600, 100], [1800, 100], [1800, 140], [1600, 140]], "2600_IcyBang", 0.9),
            ([[10, 220], [180, 220], [180, 260], [10, 260]], "2599_tsuki", 0.8),
            ([[900, 224], [990, 224], [990, 256], [900, 256]], "4/0/5", 0.98),
        ]
        expected = [
            {"name": "2599_Ritoramu", "team": "left", "kills": 0, "deaths": 0, "assists": 0},
            {"name": "2599_tsuki", "team": "left", "kills": 0, "deaths": 0, "assists": 0},
            {"name": "2600_IcyBang", "team": "right", "kills": 0, "deaths": 0, "assists": 0},
        ]

        report = link_kda_rows_from_ocr_tokens(tokens, expected)

        rows = {row["name"]: row for row in report["player_rows"]}
        self.assertEqual(report["applicable_rows"], 2)
        self.assertEqual(rows["2599_Ritoramu"]["corrected_kda"], "4/0/4")
        self.assertEqual(rows["2599_tsuki"]["corrected_kda"], "4/0/5")
        self.assertIsNone(rows["2600_IcyBang"]["corrected_kda"])

    def test_link_kda_rows_from_ocr_tokens_tolerates_minor_name_ocr_noise(self) -> None:
        tokens = [
            ([[10, 100], [210, 100], [210, 140], [10, 140]], "2600_Ghostl", 0.7),
            ([[900, 104], [990, 104], [990, 136], [900, 136]], "0/3/1", 0.99),
        ]
        expected = [
            {"name": "2600_Ghost", "team": "right", "kills": 0, "deaths": 0, "assists": 0},
        ]

        report = link_kda_rows_from_ocr_tokens(tokens, expected)

        self.assertEqual(report["player_rows"][0]["corrected_kda"], "0/3/1")


if __name__ == "__main__":
    unittest.main()
