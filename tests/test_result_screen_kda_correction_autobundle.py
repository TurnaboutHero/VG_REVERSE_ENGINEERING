import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vg.tools.result_screen_kda_correction_autobundle import (
    build_result_screen_kda_correction_autobundle,
    main,
)


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


class TestResultScreenKdaCorrectionAutobundle(unittest.TestCase):
    def test_autobundle_uses_manifest_replay_name_to_find_decoded_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = root / "memory_sessions" / "probe"
            dumps = session / "dumps"
            dumps.mkdir(parents=True)
            (dumps / "result_screen_full.dmp").write_bytes(_build_kda_dump())
            (session / "manifest.json").write_text(
                json.dumps({"replay_name": "sample-replay"}),
                encoding="utf-8",
            )

            decoded = root / "target_replay_decoder_v2_debug.json"
            decoded.write_text(
                json.dumps(
                    {
                        "safe_output": {
                            "replay_name": "sample-replay",
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

            bundle = build_result_screen_kda_correction_autobundle(str(session), str(root))

        self.assertEqual(bundle["meta"]["replay_name"], "sample-replay")
        self.assertTrue(bundle["meta"]["decoded_path"].endswith("target_replay_decoder_v2_debug.json"))
        self.assertEqual(bundle["merge"]["corrected_rows"], 3)

    def test_autobundle_prefers_safe_output_payload_over_existing_merge(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = root / "memory_sessions" / "probe"
            dumps = session / "dumps"
            dumps.mkdir(parents=True)
            (dumps / "result_screen_full.dmp").write_bytes(_build_kda_dump())
            (session / "manifest.json").write_text(
                json.dumps({"replay_name": "sample-replay"}),
                encoding="utf-8",
            )
            bundle_dir = session / "bundle"
            bundle_dir.mkdir()
            (bundle_dir / "result_screen_kda_correction_merge.json").write_text(
                json.dumps(
                    {
                        "replay_name": "sample-replay",
                        "players": [
                            {"name": "old", "kills": 0, "deaths": 0, "assists": 0},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            decoded = root / "target_replay_decoder_v2_debug.json"
            decoded.write_text(
                json.dumps(
                    {
                        "safe_output": {
                            "replay_name": "sample-replay",
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

            bundle = build_result_screen_kda_correction_autobundle(str(session), str(root))

        self.assertTrue(bundle["meta"]["decoded_path"].endswith("target_replay_decoder_v2_debug.json"))

    def test_main_writes_image_apply_artifact_when_image_fallback_used(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            session = root / "memory_sessions" / "probe"
            dumps = session / "dumps"
            dumps.mkdir(parents=True)
            # Dump KDA rows (12/1/4, 2/5/2) do not match the expected player's
            # 1/1/1, so dump-based apply yields 0 rows and the image fallback runs.
            (dumps / "result_screen_full.dmp").write_bytes(_build_kda_dump())
            image = session / "result_screen.png"
            image.write_bytes(b"png")
            (session / "manifest.json").write_text(
                json.dumps({"replay_name": "sample-replay"}),
                encoding="utf-8",
            )

            decoded = root / "target_replay_decoder_v2_debug.json"
            decoded.write_text(
                json.dumps(
                    {
                        "safe_output": {
                            "replay_name": "sample-replay",
                            "replay_file": "sample.0.vgr",
                            "players": [
                                {"name": "a", "team": "left", "kills": 1, "deaths": 1, "assists": 1},
                            ],
                        }
                    }
                ),
                encoding="utf-8",
            )

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

            output_dir = session / "bundle"
            argv = [
                "result_screen_kda_correction_autobundle.py",
                "--session-dir",
                str(session),
                "--output-root",
                str(root),
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
            root = Path(tmp)
            session = root / "memory_sessions" / "probe"
            dumps = session / "dumps"
            dumps.mkdir(parents=True)
            # No result_screen image in the session dir, so no fallback can run.
            (dumps / "result_screen_full.dmp").write_bytes(_build_kda_dump())
            (session / "manifest.json").write_text(
                json.dumps({"replay_name": "sample-replay"}),
                encoding="utf-8",
            )

            decoded = root / "target_replay_decoder_v2_debug.json"
            decoded.write_text(
                json.dumps(
                    {
                        "safe_output": {
                            "replay_name": "sample-replay",
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

            output_dir = session / "bundle"
            argv = [
                "result_screen_kda_correction_autobundle.py",
                "--session-dir",
                str(session),
                "--output-root",
                str(root),
            ]
            with patch.object(sys, "argv", argv):
                exit_code = main()

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / "result_screen_kda_correction_merge.json").exists())
            self.assertTrue((output_dir / "result_screen_kda_correction_meta.json").exists())
            self.assertFalse((output_dir / "result_screen_kda_correction_image_apply.json").exists())


if __name__ == "__main__":
    unittest.main()
