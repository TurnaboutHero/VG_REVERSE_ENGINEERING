import unittest
from unittest.mock import patch

from vg.decoder_v2.models import CreditEventRecord, PlayerEventRecord
from vg.decoder_v2.resource_counter_probe import build_resource_counter_report


class TestResourceCounterProbe(unittest.TestCase):
    def test_build_resource_counter_report_finds_monotonic_payload_family(self) -> None:
        parsed = {
            "replay_name": "sample",
            "replay_file": "sample.0.vgr",
            "match_info": {"mode": "GameMode_5v5_Ranked"},
            "teams": {
                "left": [{"name": "p1", "team": "left", "entity_id": 0x3412, "hero_name": "Kestrel"}],
                "right": [{"name": "p2", "team": "right", "entity_id": 0x7856, "hero_name": "Celeste"}],
            },
        }

        events = []
        for frame, value in enumerate([100, 150, 200, 260, 330, 410], start=1):
            payload = value.to_bytes(2, "little") + b"\x00" * 30
            events.append(PlayerEventRecord(frame, 0x3412, 0x44, payload.hex()))
            events.append(PlayerEventRecord(frame, 0x7856, 0x44, payload.hex()))

        credits = [
            CreditEventRecord(1, 0x1234, 0x06, 50.0, 0, "", True, True),
            CreditEventRecord(2, 0x1234, 0x06, -300.0, 12, "", True, True),
        ]

        with patch("vg.decoder_v2.resource_counter_probe.VGRParser") as parser_cls, patch(
            "vg.decoder_v2.resource_counter_probe.iter_player_events",
            return_value=events,
        ), patch(
            "vg.decoder_v2.resource_counter_probe.iter_credit_events",
            return_value=credits,
        ):
            parser_cls.return_value.parse.return_value = parsed
            report = build_resource_counter_report("sample.0.vgr")

        self.assertGreaterEqual(report["summary"]["family_counter_candidates"], 1)
        top = report["family_counter_candidates"][0]
        self.assertEqual(top["action"], "0x44")
        self.assertEqual(top["encoding"], "u16le")
        self.assertEqual(top["payload_offset"], 0)


if __name__ == "__main__":
    unittest.main()
