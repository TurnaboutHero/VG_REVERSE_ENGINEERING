import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from vg.decoder_v2.models import PlayerEventRecord
from vg.decoder_v2.resource_candidate_validation import (
    build_resource_candidate_validation,
    evaluate_candidate_family,
)


def _payload(target_id: int, timestamp: float) -> bytes:
    payload = bytearray(32)
    payload[1:5] = target_id.to_bytes(4, "big")
    import struct

    struct.pack_into(">f", payload, 7, timestamp)
    payload[14:17] = bytes.fromhex("10043d")
    return bytes(payload)


class TestResourceCandidateValidation(unittest.TestCase):
    def test_evaluate_candidate_rejects_target_entity_like_family(self) -> None:
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
                "p1": {"gold": 6000, "minion_kills": 40, "kills": 1, "deaths": 0, "assists": 2},
                "p2": {"gold": 7000, "minion_kills": 50, "kills": 2, "deaths": 1, "assists": 3},
            },
        }
        events = []
        for frame, target_id in enumerate([2000, 2001, 2002], start=1):
            events.append(PlayerEventRecord(frame, 0x3412, 0x01, _payload(target_id, frame * 10.0).hex()))
            events.append(PlayerEventRecord(frame, 0x7856, 0x01, _payload(target_id, frame * 10.0).hex()))

        with patch("vg.decoder_v2.resource_candidate_validation.VGRParser") as parser_cls, patch(
            "vg.decoder_v2.resource_candidate_validation.iter_player_events",
            return_value=events,
        ):
            parser_cls.return_value.parse.return_value = parsed
            report = evaluate_candidate_family("sample.0.vgr", match, (0x01, "u32be", 1))

        self.assertEqual(report["verdict"], "reject_target_entity_id_like")
        self.assertEqual(report["aggregate"]["target_id_context_rate"], 1.0)
        self.assertEqual(report["aggregate"]["known_header_context_rate"], 1.0)

    def test_build_validation_batches_truth_replays(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            replay_path = Path(temp_dir) / "sample.0.vgr"
            replay_path.write_bytes(b"sample")
            truth_path = Path(temp_dir) / "truth.json"
            truth_path.write_text("{}", encoding="utf-8")
            match = {
                "replay_name": "sample",
                "replay_file": str(replay_path),
                "players": {
                    "p1": {"gold": 6000},
                },
            }

            with patch(
                "vg.decoder_v2.resource_candidate_validation._load_truth_matches",
                return_value=[match],
            ), patch(
                "vg.decoder_v2.resource_candidate_validation.evaluate_candidate_family",
                return_value={
                    "family": "0x01:u32be@1",
                    "verdict": "reject_target_entity_id_like",
                    "aggregate": {"truth_correlations": {"gold": 0.5}},
                },
            ):
                report = build_resource_candidate_validation(
                    str(truth_path),
                    families=["0x01:u32be@1"],
                )

        self.assertEqual(report["schema_version"], "decoder_v2.resource_candidate_validation.v1")
        self.assertEqual(report["summary"]["matches_processed"], 1)
        self.assertEqual(report["summary"]["verdict_counts"], {"reject_target_entity_id_like": 1})


if __name__ == "__main__":
    unittest.main()
