import struct
import unittest
from unittest.mock import patch

from vg.decoder_v2.gold import decode_gold_from_replay
from vg.decoder_v2.models import CompletenessStatus

from tests.test_decoder_v2_decode_match import make_assessment


def _credit(entity_id_be: int, value: float, action: int, sell_flag: int = 0) -> bytes:
    return (
        bytes.fromhex("10041d0000")
        + entity_id_be.to_bytes(2, "big")
        + struct.pack(">f", value)
        + bytes([action, sell_flag])
    )


class TestDecoderV2Gold(unittest.TestCase):
    def test_decode_gold_accepts_complete_no_sell_action_06_income(self) -> None:
        parsed = {
            "teams": {
                "left": [{"name": "p1", "team": "left", "entity_id": 0x3412, "hero_name": "Alpha"}],
                "right": [{"name": "p2", "team": "right", "entity_id": 0x7856, "hero_name": "Beta"}],
            },
        }
        data = b"".join(
            [
                _credit(0x1234, 5000.0, 0x06),
                _credit(0x1234, 1000.0, 0x06, sell_flag=0x01),
                _credit(0x1234, -300.0, 0x06),
                _credit(0x5678, 6100.0, 0x06),
                _credit(0x5678, 999.0, 0x0D),
            ]
        )

        with patch("vg.decoder_v2.gold.VGRParser") as parser_cls, patch(
            "vg.decoder_v2.gold.load_frames",
            return_value=[(0, data)],
        ):
            parser_cls.return_value.parse.return_value = parsed
            result = decode_gold_from_replay(
                "sample.0.vgr",
                assessment=make_assessment(CompletenessStatus.COMPLETE_CONFIRMED),
            )

        by_name = {player.player_name: player for player in result.players}
        self.assertTrue(result.accepted)
        self.assertEqual(by_name["p1"].gold, 5600)
        self.assertEqual(by_name["p1"].gold_status, "accepted")
        self.assertEqual(by_name["p1"].action_06_sellback_refund, 1000.0)
        self.assertEqual(by_name["p1"].action_06_spent, 300.0)
        self.assertEqual(by_name["p2"].gold, 6700)

    def test_decode_gold_marks_incomplete_as_partial(self) -> None:
        parsed = {
            "teams": {
                "left": [{"name": "p1", "team": "left", "entity_id": 0x3412, "hero_name": "Alpha"}],
                "right": [],
            },
        }
        with patch("vg.decoder_v2.gold.VGRParser") as parser_cls, patch(
            "vg.decoder_v2.gold.load_frames",
            return_value=[(0, _credit(0x1234, 5000.0, 0x06))],
        ):
            parser_cls.return_value.parse.return_value = parsed
            result = decode_gold_from_replay(
                "sample.0.vgr",
                assessment=make_assessment(CompletenessStatus.INCOMPLETE_CONFIRMED),
            )

        self.assertFalse(result.accepted)
        self.assertEqual(result.players[0].gold, 5600)
        self.assertEqual(result.players[0].gold_status, "partial_incomplete_replay")


if __name__ == "__main__":
    unittest.main()
