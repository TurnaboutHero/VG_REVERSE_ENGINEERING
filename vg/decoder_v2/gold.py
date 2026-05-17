"""Completeness-gated gold extraction for decoder_v2."""

from __future__ import annotations

import math
import struct
from collections import defaultdict
from typing import Dict, Optional

from vg.core.unified_decoder import _CREDIT_HEADER, _le_to_be
from vg.core.vgr_parser import VGRParser

from .completeness import assess_completeness, extract_replay_signals, load_frames
from .models import CompletenessAssessment, CompletenessStatus, GoldExtractionResult, GoldPlayerSummary


def _status_for_assessment(assessment: CompletenessAssessment) -> str:
    if assessment.status == CompletenessStatus.COMPLETE_CONFIRMED:
        return "accepted"
    if assessment.status == CompletenessStatus.INCOMPLETE_CONFIRMED:
        return "partial_incomplete_replay"
    return "partial_completeness_unknown"


def decode_gold_from_replay(
    replay_file: str,
    assessment: Optional[CompletenessAssessment] = None,
) -> GoldExtractionResult:
    """Decode per-player gold from `[10 04 1D]` action `0x06` credit records.

    Formula validated on complete local truth fixtures:
    `600 + sum(action 0x06 positive values where sell_flag != 0x01)`.
    """
    if assessment is None:
        assessment = assess_completeness(extract_replay_signals(replay_file))

    parsed = VGRParser(replay_file, auto_truth=False).parse()
    players_by_be = {
        _le_to_be(int(player["entity_id"])): player
        for team in ("left", "right")
        for player in parsed.get("teams", {}).get(team, [])
        if player.get("entity_id")
    }

    income: Dict[int, float] = defaultdict(float)
    sellback_refund: Dict[int, float] = defaultdict(float)
    spent: Dict[int, float] = defaultdict(float)

    for _, data in load_frames(replay_file):
        pos = 0
        while True:
            pos = data.find(_CREDIT_HEADER, pos)
            if pos == -1:
                break
            if pos + 13 > len(data):
                pos += 1
                continue
            if data[pos + 3:pos + 5] != b"\x00\x00":
                pos += 1
                continue

            entity_id_be = struct.unpack_from(">H", data, pos + 5)[0]
            if entity_id_be not in players_by_be:
                pos += 3
                continue

            value = struct.unpack_from(">f", data, pos + 7)[0]
            action = data[pos + 11]
            sell_flag = data[pos + 12]
            if action != 0x06 or not math.isfinite(value):
                pos += 3
                continue

            if value > 0 and sell_flag != 0x01:
                income[entity_id_be] += value
            elif value > 0:
                sellback_refund[entity_id_be] += value
            elif value < 0:
                spent[entity_id_be] += abs(value)

            pos += 3

    gold_status = _status_for_assessment(assessment)
    players = []
    for team_label in ("left", "right"):
        for player in parsed.get("teams", {}).get(team_label, []):
            entity_id = player.get("entity_id")
            if not entity_id:
                continue
            entity_id_be = _le_to_be(int(entity_id))
            action_income = income.get(entity_id_be, 0.0)
            players.append(
                GoldPlayerSummary(
                    player_name=str(player.get("name")),
                    team=str(player.get("team") or team_label),
                    hero_name=str(player.get("hero_name") or "Unknown"),
                    gold=600 + round(action_income),
                    gold_status=gold_status,
                    action_06_income=round(action_income, 4),
                    action_06_sellback_refund=round(sellback_refund.get(entity_id_be, 0.0), 4),
                    action_06_spent=round(spent.get(entity_id_be, 0.0), 4),
                )
            )

    accepted = assessment.status == CompletenessStatus.COMPLETE_CONFIRMED
    if accepted:
        reason = "Accepted: action 0x06 no-sell gold formula is validated on complete fixtures."
    elif assessment.status == CompletenessStatus.INCOMPLETE_CONFIRMED:
        reason = "Withheld from index: incomplete replay can undercount late gold."
    else:
        reason = "Withheld from index: replay completeness is not confirmed."

    return GoldExtractionResult(
        accepted=accepted,
        reason=reason,
        assessment=assessment,
        players=tuple(players),
    )
