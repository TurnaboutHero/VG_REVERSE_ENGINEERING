"""Tests for the desktop_auto step parser (pure logic only; no input injection)."""

import unittest

from vg.tools.desktop_auto import parse_step


class ParseStepTests(unittest.TestCase):
    def test_click_parses_coordinates(self):
        self.assertEqual(parse_step("click:2730,1668"), ("click", ["2730", "1668"]))

    def test_pointer_ops_parse_coordinates(self):
        self.assertEqual(parse_step("dblclick:10,20"), ("dblclick", ["10", "20"]))
        self.assertEqual(parse_step("rclick:10,20"), ("rclick", ["10", "20"]))
        self.assertEqual(parse_step("move:0,0"), ("move", ["0", "0"]))

    def test_click_requires_two_integer_coordinates(self):
        with self.assertRaises(ValueError):
            parse_step("click:100")
        with self.assertRaises(ValueError):
            parse_step("click:a,b")

    def test_sleep_parses_seconds(self):
        self.assertEqual(parse_step("sleep:1.5"), ("sleep", ["1.5"]))

    def test_sleep_rejects_missing_or_non_numeric(self):
        with self.assertRaises(ValueError):
            parse_step("sleep:")
        with self.assertRaises(ValueError):
            parse_step("sleep:abc")

    def test_shot_keeps_full_path_including_drive_colon_and_commas(self):
        self.assertEqual(
            parse_step("shot:D:/tmp/a,b.png"),
            ("shot", ["D:/tmp/a,b.png"]),
        )

    def test_shot_requires_path(self):
        with self.assertRaises(ValueError):
            parse_step("shot:")

    def test_key_allows_known_names_only(self):
        self.assertEqual(parse_step("key:esc"), ("key", ["esc"]))
        with self.assertRaises(ValueError):
            parse_step("key:f13")

    def test_info_takes_no_args(self):
        self.assertEqual(parse_step("info"), ("info", []))

    def test_unknown_step_rejected(self):
        with self.assertRaises(ValueError):
            parse_step("drag:1,2")


if __name__ == "__main__":
    unittest.main()
