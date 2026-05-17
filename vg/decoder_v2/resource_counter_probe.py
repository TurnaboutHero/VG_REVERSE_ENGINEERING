"""Search for HackedGlory-1086-like resource counter candidates in VGR data."""

from __future__ import annotations

import argparse
import json
import math
import struct
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Tuple

from vg.core.unified_decoder import _le_to_be
from vg.core.vgr_parser import VGRParser

from .credit_events import iter_credit_events
from .player_events import iter_player_events


CandidateKey = Tuple[str, int, str, int]


def _decode_values(payload: bytes) -> Iterable[Tuple[str, int, float]]:
    for offset in range(0, len(payload) - 1):
        if offset + 2 <= len(payload):
            yield "u16le", offset, float(struct.unpack_from("<H", payload, offset)[0])
            yield "u16be", offset, float(struct.unpack_from(">H", payload, offset)[0])
        if offset + 4 <= len(payload):
            yield "u32le", offset, float(struct.unpack_from("<I", payload, offset)[0])
            yield "u32be", offset, float(struct.unpack_from(">I", payload, offset)[0])
            for kind, fmt in (("f32le", "<f"), ("f32be", ">f")):
                value = struct.unpack_from(fmt, payload, offset)[0]
                if math.isfinite(value):
                    yield kind, offset, float(value)


def _player_maps(parsed: Dict[str, Any]) -> Tuple[Dict[int, Dict[str, Any]], Dict[int, Dict[str, Any]]]:
    by_le: Dict[int, Dict[str, Any]] = {}
    by_be: Dict[int, Dict[str, Any]] = {}
    for team in ("left", "right"):
        for player in parsed.get("teams", {}).get(team, []):
            entity_id = player.get("entity_id")
            if not entity_id:
                continue
            by_le[entity_id] = player
            by_be[_le_to_be(entity_id)] = player
    return by_le, by_be


def _score_sequence(values: List[Tuple[int, float]]) -> Optional[Dict[str, Any]]:
    if len(values) < 5:
        return None

    filtered = [(frame, value) for frame, value in values if 0 <= value <= 100_000]
    if len(filtered) < 5:
        return None

    distinct_values = []
    previous = None
    for _, value in filtered:
        rounded = round(value, 4)
        if previous is None or rounded != previous:
            distinct_values.append(value)
            previous = rounded

    if len(distinct_values) < 3:
        return None

    steps = [b - a for a, b in zip(distinct_values, distinct_values[1:])]
    if not steps:
        return None

    nonnegative = sum(1 for step in steps if step >= 0)
    negative = len(steps) - nonnegative
    positive = sum(1 for step in steps if step > 0)
    monotonic_ratio = nonnegative / len(steps)
    max_drop = min(steps)
    max_step = max(steps)
    first_value = distinct_values[0]
    final_value = distinct_values[-1]

    if final_value < 10 or positive < 2:
        return None

    score = (
        monotonic_ratio * 100.0
        + min(len(distinct_values), 40)
        + min(final_value / 1000.0, 30)
        - max(0, negative - 1) * 10
    )

    return {
        "event_count": len(filtered),
        "distinct_count": len(distinct_values),
        "first_value": round(first_value, 4),
        "final_value": round(final_value, 4),
        "positive_steps": positive,
        "negative_steps": negative,
        "monotonic_ratio": round(monotonic_ratio, 4),
        "max_drop": round(max_drop, 4),
        "max_step": round(max_step, 4),
        "score": round(score, 4),
        "sample_values": [round(value, 4) for value in distinct_values[:12]],
        "tail_values": [round(value, 4) for value in distinct_values[-8:]],
    }


def _summarize_credit_deltas(replay_file: str, players_by_be: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[int, int], List[float]] = defaultdict(list)
    for event in iter_credit_events(replay_file):
        if event.entity_id_be not in players_by_be or event.value is None:
            continue
        grouped[(event.entity_id_be, event.action)].append(event.value)

    rows = []
    for (entity_id, action), values in grouped.items():
        positives = [value for value in values if value > 0]
        negatives = [value for value in values if value < 0]
        rounded_counts = Counter(round(value, 2) for value in values)
        player = players_by_be[entity_id]
        rows.append(
            {
                "player_name": player.get("name"),
                "team": player.get("team"),
                "entity_id_be": entity_id,
                "action": f"0x{action:02x}",
                "count": len(values),
                "positive_count": len(positives),
                "negative_count": len(negatives),
                "sum_positive": round(sum(positives), 4),
                "sum_negative": round(sum(negatives), 4),
                "max_value": round(max(values), 4),
                "min_value": round(min(values), 4),
                "top_values": [
                    {"value": value, "count": count}
                    for value, count in rounded_counts.most_common(8)
                ],
            }
        )
    rows.sort(key=lambda item: (item["count"], abs(item["sum_positive"]) + abs(item["sum_negative"])), reverse=True)
    return rows[:80]


def build_resource_counter_report(replay_file: str, top_n: int = 40) -> Dict[str, Any]:
    """Build a report of possible monotonic resource counters in player event payloads."""
    parser = VGRParser(replay_file, auto_truth=False)
    parsed = parser.parse()
    players_by_le, players_by_be = _player_maps(parsed)

    grouped: Dict[CandidateKey, List[Tuple[int, float]]] = defaultdict(list)
    for event in iter_player_events(replay_file):
        player = players_by_le.get(event.entity_id_le)
        if not player:
            continue
        payload = bytes.fromhex(event.payload_hex)
        player_name = str(player.get("name"))
        for kind, offset, value in _decode_values(payload):
            grouped[(player_name, event.action, kind, offset)].append((event.frame_idx, value))

    player_candidates = []
    family_accumulator: Dict[Tuple[int, str, int], List[Dict[str, Any]]] = defaultdict(list)
    for (player_name, action, kind, offset), values in grouped.items():
        scored = _score_sequence(values)
        if scored is None:
            continue
        player = next((item for item in players_by_le.values() if item.get("name") == player_name), {})
        row = {
            "player_name": player_name,
            "team": player.get("team"),
            "hero_name": player.get("hero_name"),
            "action": f"0x{action:02x}",
            "encoding": kind,
            "payload_offset": offset,
            **scored,
        }
        player_candidates.append(row)
        family_accumulator[(action, kind, offset)].append(row)

    player_candidates.sort(key=lambda item: item["score"], reverse=True)

    family_candidates = []
    for (action, kind, offset), rows in family_accumulator.items():
        if len(rows) < 2:
            continue
        family_candidates.append(
            {
                "action": f"0x{action:02x}",
                "encoding": kind,
                "payload_offset": offset,
                "players_covered": len(rows),
                "avg_score": round(mean(row["score"] for row in rows), 4),
                "avg_monotonic_ratio": round(mean(row["monotonic_ratio"] for row in rows), 4),
                "avg_final_value": round(mean(row["final_value"] for row in rows), 4),
                "avg_distinct_count": round(mean(row["distinct_count"] for row in rows), 4),
                "players": [
                    {
                        "player_name": row["player_name"],
                        "team": row["team"],
                        "final_value": row["final_value"],
                        "distinct_count": row["distinct_count"],
                        "monotonic_ratio": row["monotonic_ratio"],
                    }
                    for row in sorted(rows, key=lambda item: item["score"], reverse=True)[:12]
                ],
            }
        )
    family_candidates.sort(
        key=lambda item: (
            item["players_covered"],
            item["avg_monotonic_ratio"],
            item["avg_distinct_count"],
            item["avg_score"],
        ),
        reverse=True,
    )

    credit_delta_rows = _summarize_credit_deltas(replay_file, players_by_be)
    action_summary = Counter(row["action"] for row in credit_delta_rows)

    return {
        "schema_version": "decoder_v2.resource_counter_probe.v1",
        "replay_name": parsed["replay_name"],
        "replay_file": parsed["replay_file"],
        "game_mode": parsed["match_info"]["mode"],
        "player_count": len(players_by_le),
        "interpretation": (
            "HackedGlory 1086 exposes monotonic total-resource candidates. "
            "This report searches local player-event payloads for similarly monotonic fields, "
            "and separately summarizes credit-event deltas."
        ),
        "summary": {
            "player_counter_candidates": len(player_candidates),
            "family_counter_candidates": len(family_candidates),
            "credit_delta_player_action_rows": len(credit_delta_rows),
            "credit_actions_seen": dict(sorted(action_summary.items())),
        },
        "family_counter_candidates": family_candidates[:top_n],
        "player_counter_candidates": player_candidates[:top_n],
        "credit_delta_summary": credit_delta_rows[:top_n],
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Search local .vgr data for HackedGlory-1086-like resource counters.")
    parser.add_argument("replay_file", help="Path to a .0.vgr replay file")
    parser.add_argument("--top", type=int, default=40, help="Maximum rows per section")
    parser.add_argument("-o", "--output", help="Optional output JSON path")
    args = parser.parse_args(argv)

    report = build_resource_counter_report(args.replay_file, top_n=args.top)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
        print(f"Resource counter probe saved to {args.output}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
