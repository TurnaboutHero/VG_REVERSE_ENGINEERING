"""Probe level/XP-like signals without promoting them to decoder output."""

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

from .completeness import load_frames
from .credit_events import iter_credit_events
from .minion_research import _load_truth_matches


HEARTBEAT_HEADER = bytes.fromhex("18043e")
HEARTBEAT_RECORD_SIZE = 32
STRUCTURAL_OFFSETS = set(range(0, 11))


def _player_maps(parsed: Dict[str, Any]) -> Tuple[Dict[int, Dict[str, Any]], Dict[int, Dict[str, Any]]]:
    by_be: Dict[int, Dict[str, Any]] = {}
    by_le: Dict[int, Dict[str, Any]] = {}
    for team in ("left", "right"):
        for player in parsed.get("teams", {}).get(team, []):
            entity_id = player.get("entity_id")
            if not entity_id:
                continue
            by_le[int(entity_id)] = player
            by_be[_le_to_be(int(entity_id))] = player
    return by_be, by_le


def _iter_heartbeat_records(replay_file: str, players_by_be: Dict[int, Dict[str, Any]]) -> Iterable[Tuple[int, int, bytes]]:
    for frame_idx, data in load_frames(replay_file):
        pos = 0
        while True:
            pos = data.find(HEARTBEAT_HEADER, pos)
            if pos == -1:
                break
            if pos + HEARTBEAT_RECORD_SIZE <= len(data) and data[pos + 3:pos + 5] == b"\x00\x00":
                entity_id_be = struct.unpack_from(">H", data, pos + 5)[0]
                duplicate_entity_id_be = struct.unpack_from(">H", data, pos + 9)[0]
                if entity_id_be in players_by_be and duplicate_entity_id_be == entity_id_be:
                    yield frame_idx, entity_id_be, data[pos:pos + HEARTBEAT_RECORD_SIZE]
            pos += 1


def _distinct(values: List[float]) -> List[float]:
    output = []
    previous = None
    for value in values:
        rounded = round(value, 4)
        if previous is None or rounded != previous:
            output.append(value)
            previous = rounded
    return output


def _monotonic_ratio(values: List[float]) -> Optional[float]:
    if len(values) < 2:
        return None
    steps = [b - a for a, b in zip(values, values[1:])]
    return round(sum(1 for step in steps if step >= 0) / len(steps), 4)


def _decode_numeric(record: bytes, kind: str, offset: int) -> Optional[float]:
    try:
        if kind == "u8":
            return float(record[offset])
        if kind == "u16be" and offset + 2 <= len(record):
            return float(struct.unpack_from(">H", record, offset)[0])
        if kind == "f32be" and offset + 4 <= len(record):
            value = struct.unpack_from(">f", record, offset)[0]
            return float(value) if math.isfinite(value) else None
    except (IndexError, struct.error):
        return None
    return None


def _score_level_candidate(records_by_player: Dict[int, List[bytes]], kind: str, offset: int) -> Optional[Dict[str, Any]]:
    player_rows = []
    for records in records_by_player.values():
        values = []
        for record in records:
            value = _decode_numeric(record, kind, offset)
            if value is not None:
                values.append(value)
        if len(values) < 5:
            continue
        distinct = _distinct(values)
        if not distinct:
            continue
        level_like = [
            value
            for value in distinct
            if 1 <= value <= 12 and abs(value - round(value)) < 0.001
        ]
        plus12_like = [
            value
            for value in distinct
            if 13 <= value <= 24 and abs(value - round(value)) < 0.001
        ]
        player_rows.append(
            {
                "level_like_rate": len(level_like) / len(distinct),
                "plus12_level_like_rate": len(plus12_like) / len(distinct),
                "monotonic_ratio": _monotonic_ratio(distinct),
                "distinct_count": len(distinct),
                "first_value": distinct[0],
                "final_value": distinct[-1],
                "min_value": min(distinct),
                "max_value": max(distinct),
            }
        )
    if not player_rows:
        return None
    return {
        "kind": kind,
        "offset": offset,
        "players_covered": len(player_rows),
        "avg_level_like_rate": round(mean(row["level_like_rate"] for row in player_rows), 4),
        "avg_plus12_level_like_rate": round(mean(row["plus12_level_like_rate"] for row in player_rows), 4),
        "avg_monotonic_ratio": round(mean(row["monotonic_ratio"] or 0 for row in player_rows), 4),
        "avg_distinct_count": round(mean(row["distinct_count"] for row in player_rows), 4),
        "avg_final_value": round(mean(float(row["final_value"]) for row in player_rows), 4),
        "avg_max_value": round(mean(float(row["max_value"]) for row in player_rows), 4),
    }


def _candidate_verdict(candidate: Dict[str, Any]) -> str:
    if candidate["offset"] in STRUCTURAL_OFFSETS:
        return "reject_structural_header_or_entity"
    if candidate["avg_distinct_count"] < 2:
        return "reject_constant"
    if candidate["avg_level_like_rate"] >= 0.9 and candidate["avg_monotonic_ratio"] >= 0.8 and candidate["avg_max_value"] <= 12:
        return "plausible_level"
    if (
        candidate["avg_plus12_level_like_rate"] >= 0.9
        and candidate["avg_monotonic_ratio"] >= 0.8
        and candidate["avg_max_value"] <= 24
    ):
        return "plausible_level_plus_12"
    return "reject_not_level_like"


def _summarize_credit_action_03(replay_file: str, players_by_be: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    player_counts = Counter()
    value_counts: Dict[str, Counter] = defaultdict(Counter)
    nonplayer_count = 0
    for event in iter_credit_events(replay_file):
        if event.action != 0x03:
            continue
        player = players_by_be.get(event.entity_id_be)
        if not player:
            nonplayer_count += 1
            continue
        player_name = str(player.get("name"))
        player_counts[player_name] += 1
        if event.value is not None:
            value_counts[player_name][round(event.value, 2)] += 1

    return {
        "total_player_records": sum(player_counts.values()),
        "nonplayer_records": nonplayer_count,
        "players_with_records": len(player_counts),
        "player_counts": dict(player_counts.most_common()),
        "top_values_by_player": {
            player_name: [
                {"value": value, "count": count}
                for value, count in counter.most_common(10)
            ]
            for player_name, counter in value_counts.items()
        },
        "interpretation": (
            "Action 0x03 is not treated as a universal level signal when it appears on only a subset "
            "of players or has hero/passive-like value distributions."
        ),
    }


def build_level_signal_probe(replay_file: str) -> Dict[str, Any]:
    parsed = VGRParser(replay_file, auto_truth=False).parse()
    players_by_be, _ = _player_maps(parsed)
    records_by_player: Dict[int, List[bytes]] = defaultdict(list)
    frame_ranges: Dict[int, List[int]] = defaultdict(list)
    for frame_idx, entity_id_be, record in _iter_heartbeat_records(replay_file, players_by_be):
        records_by_player[entity_id_be].append(record)
        frame_ranges[entity_id_be].append(frame_idx)

    candidate_rows = []
    for kind, max_offset in (("u8", 31), ("u16be", 30), ("f32be", 28)):
        for offset in range(max_offset + 1):
            scored = _score_level_candidate(records_by_player, kind, offset)
            if scored is None:
                continue
            if max(scored["avg_level_like_rate"], scored["avg_plus12_level_like_rate"]) < 0.5:
                continue
            scored["verdict"] = _candidate_verdict(scored)
            candidate_rows.append(scored)
    candidate_rows.sort(
        key=lambda row: (
            row["verdict"].startswith("plausible"),
            max(row["avg_level_like_rate"], row["avg_plus12_level_like_rate"]),
            row["avg_monotonic_ratio"],
        ),
        reverse=True,
    )

    byte15_rows = []
    timestamp_rows = []
    for entity_id_be, records in records_by_player.items():
        player = players_by_be[entity_id_be]
        byte15_values = _distinct([float(record[15]) for record in records])
        timestamp_values = []
        for record in records:
            value = _decode_numeric(record, "f32be", 25)
            if value is not None and 0 <= value <= 10_000:
                timestamp_values.append(value)
        timestamp_distinct = _distinct(timestamp_values)
        frames = frame_ranges[entity_id_be]
        byte15_rows.append(
            {
                "player_name": player.get("name"),
                "record_count": len(records),
                "byte15_first": byte15_values[0] if byte15_values else None,
                "byte15_final": byte15_values[-1] if byte15_values else None,
                "byte15_max": max(byte15_values) if byte15_values else None,
                "byte15_monotonic_ratio": _monotonic_ratio(byte15_values),
                "byte15_inferred_level_max": (max(byte15_values) - 12) if byte15_values else None,
                "first_frame": frames[0] if frames else None,
                "last_frame": frames[-1] if frames else None,
            }
        )
        timestamp_rows.append(
            {
                "player_name": player.get("name"),
                "timestamp_first": round(timestamp_distinct[0], 4) if timestamp_distinct else None,
                "timestamp_final": round(timestamp_distinct[-1], 4) if timestamp_distinct else None,
                "timestamp_monotonic_ratio": _monotonic_ratio(timestamp_distinct),
                "timestamp_distinct_count": len(timestamp_distinct),
            }
        )

    viable_candidates = [row for row in candidate_rows if str(row["verdict"]).startswith("plausible")]
    credit_action_03_audit = _summarize_credit_action_03(replay_file, players_by_be)
    return {
        "schema_version": "decoder_v2.level_signal_probe.v1",
        "replay_name": parsed.get("replay_name"),
        "replay_file": str(Path(replay_file).resolve()),
        "heartbeat_header": HEARTBEAT_HEADER.hex(),
        "summary": {
            "players_with_heartbeat": len(records_by_player),
            "heartbeat_records": sum(len(records) for records in records_by_player.values()),
            "candidate_offsets": len(candidate_rows),
            "viable_level_candidates": len(viable_candidates),
            "byte15_level_plus_12_hypothesis": (
                "rejected"
                if any((row["byte15_max"] or 0) > 24 for row in byte15_rows)
                else "unresolved"
            ),
            "credit_action_03_players_with_records": credit_action_03_audit["players_with_records"],
        },
        "byte15_level_plus_12_audit": byte15_rows,
        "timestamp_offset25_audit": timestamp_rows,
        "candidate_offsets": candidate_rows[:40],
        "credit_action_03_audit": credit_action_03_audit,
        "interpretation": (
            "No level field is promoted. The historical byte15=level+12 hypothesis is rejected "
            "when full frame streams are considered; byte15 behaves like a counter/sequence field."
        ),
    }


def build_level_signal_batch(truth_path: str, limit: Optional[int] = None) -> Dict[str, Any]:
    matches = []
    for match in _load_truth_matches(truth_path):
        replay_file = match.get("replay_file")
        if not replay_file or not Path(str(replay_file)).exists():
            continue
        matches.append(build_level_signal_probe(str(replay_file)))
        if limit is not None and len(matches) >= limit:
            break

    return {
        "schema_version": "decoder_v2.level_signal_batch.v1",
        "truth_path": str(Path(truth_path).resolve()),
        "matches_processed": len(matches),
        "summary": {
            "matches_with_viable_level_candidates": sum(
                1 for match in matches if match["summary"]["viable_level_candidates"] > 0
            ),
            "byte15_rejected_matches": sum(
                1
                for match in matches
                if match["summary"]["byte15_level_plus_12_hypothesis"] == "rejected"
            ),
            "heartbeat_records": sum(match["summary"]["heartbeat_records"] for match in matches),
        },
        "matches": matches,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Probe level/XP-like local replay signals.")
    parser.add_argument("replay_file", nargs="?", help="Path to one replay .0.vgr")
    parser.add_argument("--truth", help="Optional truth JSON for batch mode")
    parser.add_argument("--limit", type=int, help="Optional batch replay limit")
    parser.add_argument("-o", "--output", help="Optional output JSON path")
    args = parser.parse_args(argv)

    if args.truth:
        payload_obj = build_level_signal_batch(args.truth, limit=args.limit)
    elif args.replay_file:
        payload_obj = build_level_signal_probe(args.replay_file)
    else:
        parser.error("provide replay_file or --truth")

    payload = json.dumps(payload_obj, indent=2, ensure_ascii=False)
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(payload, encoding="utf-8")
        print(f"Level signal probe saved to {output_path}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
