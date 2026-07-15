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

    def test_link_kda_rows_from_ocr_tokens_does_not_cross_link_missing_right_name(self) -> None:
        # Replicates the two-column result-screen geometry from the first test above,
        # but the right team's name tokens are missing (simulated OCR miss). Each
        # right-column KDA token is only ever "left of" nothing on its own side, so
        # the left column's same-row name is its sole same-row candidate. A right-side
        # KDA token is given higher OCR confidence than the left player's own KDA so
        # that a confidence-only dedupe tie-break (the pre-fix behavior) would steal it.
        tokens = [
            ([[10, 100], [210, 100], [210, 140], [10, 140]], "2599_Ritoramu", 0.9),
            ([[900, 104], [990, 104], [990, 136], [900, 136]], "4/0/4", 0.90),
            # Right-column KDA, same row as Ritoramu, no right-column name token was OCR'd.
            ([[1900, 104], [1990, 104], [1990, 136], [1900, 136]], "7/2/9", 0.99),
            ([[10, 220], [180, 220], [180, 260], [10, 260]], "2599_tsuki", 0.8),
            ([[900, 224], [990, 224], [990, 256], [900, 256]], "4/0/5", 0.80),
            # Right-column KDA, same row as tsuki, no right-column name token was OCR'd.
            ([[1900, 224], [1990, 224], [1990, 256], [1900, 256]], "1/3/2", 0.97),
        ]
        expected = [
            {"name": "2599_Ritoramu", "team": "left", "kills": 0, "deaths": 0, "assists": 0},
            {"name": "2599_tsuki", "team": "left", "kills": 0, "deaths": 0, "assists": 0},
            {"name": "2600_IcyBang", "team": "right", "kills": 0, "deaths": 0, "assists": 0},
        ]

        report = link_kda_rows_from_ocr_tokens(tokens, expected)

        rows = {row["name"]: row for row in report["player_rows"]}
        # Left players must keep their own KDA, never the right column's.
        self.assertEqual(rows["2599_Ritoramu"]["corrected_kda"], "4/0/4")
        self.assertEqual(rows["2599_tsuki"]["corrected_kda"], "4/0/5")
        # The orphaned right-column KDAs must stay unlinked, not silently misassigned.
        self.assertIsNone(rows["2600_IcyBang"]["corrected_kda"])
        self.assertEqual(rows["2600_IcyBang"]["correction_status"], "unresolved")
        self.assertEqual(report["applicable_rows"], 2)


if __name__ == "__main__":
    unittest.main()
