import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vg.tools.result_screen_kda_correction_bundle import build_result_screen_kda_correction_bundle, main


def _build_kda_dump() -> bytes:
    import struct
    from vg.tools.minidump_parser import MINIDUMP_SIGNATURE

    blob = (
        "12/1/4".encode("utf-16-le")
        + b"\x00" * 16
        + "2/5/2".encode("utf-16-le")
        + b"\x00" * 16
        + "2/5/2".encode("utf-16-le")
    )
    header = struct.pack("<IIIIIIQ", MINIDUMP_SIGNATURE, 0x0000A793, 1, 32, 0, 0, 0)
    stream = struct.pack("<III", 9, 32, 44)
    memory64 = struct.pack("<QQQQ", 1, 76, 0x4000, len(blob))
    return header + stream + memory64 + blob


class TestResultScreenKdaCorrectionBundle(unittest.TestCase):
    def test_bundle_builds_report_apply_and_merge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dump = Path(tmp) / "sample.dmp"
            dump.write_bytes(_build_kda_dump())
            decoded = {
                "safe_output": {
                    "replay_name": "sample",
                    "replay_file": "sample.0.vgr",
                    "players": [
                        {"name": "a", "team": "left", "kills": 12, "deaths": 1, "assists": 4},
                        {"name": "b", "team": "right", "kills": 2, "deaths": 5, "assists": 2},
                        {"name": "c", "team": "right", "kills": 2, "deaths": 5, "assists": 2},
                    ],
                }
            }

            bundle = build_result_screen_kda_correction_bundle(decoded, str(dump))

        self.assertEqual(bundle["report"]["group_confirmable_rows"], 3)
        self.assertEqual(bundle["apply"]["applicable_rows"], 3)
        self.assertEqual(bundle["merge"]["corrected_rows"], 3)

    def test_bundle_falls_back_to_image_ocr_when_dump_has_no_kda_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dump = Path(tmp) / "sample.dmp"
            dump.write_bytes(_build_kda_dump().replace("12/1/4".encode("utf-16-le"), b""))
            image = Path(tmp) / "result_screen.png"
            image.write_bytes(b"png")
            decoded = {
                "safe_output": {
                    "replay_name": "sample",
                    "replay_file": "sample.0.vgr",
                    "players": [
                        {"name": "a", "team": "left", "kills": 1, "deaths": 1, "assists": 1},
                    ],
                }
            }
            image_apply = {
                "image_path": str(image),
                "applicable_rows": 1,
                "total_rows": 1,
                "player_rows": [
                    {
                        "name": "a",
                        "team": "left",
                        "hero_name": None,
                        "parser_kda": "1/1/1",
                        "corrected_kda": "9/0/9",
                        "correction_status": "image_ocr_row_linked",
                    }
                ],
            }

            with patch(
                "vg.tools.result_screen_kda_correction_bundle.build_result_screen_image_kda_correction_apply",
                return_value=image_apply,
            ):
                bundle = build_result_screen_kda_correction_bundle(decoded, str(dump), image_path=str(image))

        self.assertEqual(bundle["apply"]["applicable_rows"], 1)
        self.assertEqual(bundle["merge"]["players"][0]["kills"], 9)
        self.assertEqual(bundle["merge"]["players"][0]["kda_correction_status"], "image_ocr_row_linked")

    def test_main_writes_image_apply_artifact_when_image_fallback_used(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dump = tmp_path / "sample.dmp"
            dump.write_bytes(_build_kda_dump().replace("12/1/4".encode("utf-16-le"), b""))
            image = tmp_path / "result_screen.png"
            image.write_bytes(b"png")
            decoded_path = tmp_path / "decoded.json"
            decoded_path.write_text(
                json.dumps(
                    {
                        "safe_output": {
                            "replay_name": "sample",
                            "replay_file": "sample.0.vgr",
                            "players": [
                                {"name": "a", "team": "left", "kills": 1, "deaths": 1, "assists": 1},
                            ],
                        }
                    }
                ),
                encoding="utf-8",
            )
            output_dir = tmp_path / "out"

            image_apply = {
                "image_path": str(image),
                "applicable_rows": 1,
                "total_rows": 1,
                "player_rows": [
                    {
                        "name": "a",
                        "team": "left",
                        "hero_name": None,
                        "parser_kda": "1/1/1",
                        "corrected_kda": "9/0/9",
                        "correction_status": "image_ocr_row_linked",
                    }
                ],
            }

            argv = [
                "result_screen_kda_correction_bundle.py",
                "--decoded",
                str(decoded_path),
                "--dump",
                str(dump),
                "--image",
                str(image),
                "--output-dir",
                str(output_dir),
            ]
            with patch(
                "vg.tools.result_screen_kda_correction_bundle.build_result_screen_image_kda_correction_apply",
                return_value=image_apply,
            ), patch.object(sys, "argv", argv):
                exit_code = main()

            self.assertEqual(exit_code, 0)
            image_apply_path = output_dir / "result_screen_kda_correction_image_apply.json"
            self.assertTrue(image_apply_path.exists())
            written = json.loads(image_apply_path.read_text(encoding="utf-8"))
            self.assertEqual(written, image_apply)

    def test_main_skips_image_apply_artifact_when_no_image_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            dump = tmp_path / "sample.dmp"
            dump.write_bytes(_build_kda_dump())
            decoded_path = tmp_path / "decoded.json"
            decoded_path.write_text(
                json.dumps(
                    {
                        "safe_output": {
                            "replay_name": "sample",
                            "replay_file": "sample.0.vgr",
                            "players": [
                                {"name": "a", "team": "left", "kills": 12, "deaths": 1, "assists": 4},
                                {"name": "b", "team": "right", "kills": 2, "deaths": 5, "assists": 2},
                                {"name": "c", "team": "right", "kills": 2, "deaths": 5, "assists": 2},
                            ],
                        }
                    }
                ),
                encoding="utf-8",
            )
            output_dir = tmp_path / "out"

            argv = [
                "result_screen_kda_correction_bundle.py",
                "--decoded",
                str(decoded_path),
                "--dump",
                str(dump),
                "--output-dir",
                str(output_dir),
            ]
            with patch.object(sys, "argv", argv):
                exit_code = main()

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / "result_screen_kda_correction_merge.json").exists())
            self.assertFalse((output_dir / "result_screen_kda_correction_image_apply.json").exists())


if __name__ == "__main__":
    unittest.main()
