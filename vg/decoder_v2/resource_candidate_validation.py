"""Validate HackedGlory-style resource counter candidates against local truth."""

from __future__ import annotations

import argparse
import json
import math
import struct
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Tuple

from vg.core.vgr_parser import VGRParser

from .minion_research import _load_truth_matches
from .player_events import iter_player_events


DEFAULT_FAMILIES = (
    "0x01:u32le@3",
    "0x01:u32be@1",
    "0x01:f32be@7",
    "0x01:u32be@5",
    "0x01:f32le@4",
)

KNOWN_CONTEXT_HEADERS = {
    "10041d": "credit",
    "10043d": "item_acquire",
    "18041c": "kill",
    "080431": "death",
}

Family = Tuple[int, str, int]


def _parse_family(text: str) -> Family:
    try:
        action_text, rest = text.split(":", 1)
        encoding, offset_text = rest.split("@", 1)
    except ValueError as exc:
        raise ValueError(f"Invalid family format {text!r}; expected 0x01:u32be@1") from exc
    return int(action_text, 16), encoding, int(offset_text)


def _format_family(family: Family) -> str:
    action, encoding, offset = family
    return f"0x{action:02x}:{encoding}@{offset}"


def _decode(payload: bytes, encoding: str, offset: int) -> Optional[float]:
    if offset < 0:
        return None
    try:
        if encoding == "u16le" and offset + 2 <= len(payload):
            return float(struct.unpack_from("<H", payload, offset)[0])
        if encoding == "u16be" and offset + 2 <= len(payload):
            return float(struct.unpack_from(">H", payload, offset)[0])
        if encoding == "u32le" and offset + 4 <= len(payload):
            return float(struct.unpack_from("<I", payload, offset)[0])
        if encoding == "u32be" and offset + 4 <= len(payload):
            return float(struct.unpack_from(">I", payload, offset)[0])
        if encoding == "f32le" and offset + 4 <= len(payload):
            value = struct.unpack_from("<f", payload, offset)[0]
            return float(value) if math.isfinite(value) else None
        if encoding == "f32be" and offset + 4 <= len(payload):
            value = struct.unpack_from(">f", payload, offset)[0]
            return float(value) if math.isfinite(value) else None
    except struct.error:
        return None
    return None


def _pearson(pairs: List[Tuple[float, float]]) -> Optional[float]:
    if len(pairs) < 3:
        return None
    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    x_var = sum((value - x_mean) ** 2 for value in xs)
    y_var = sum((value - y_mean) ** 2 for value in ys)
    if x_var <= 0 or y_var <= 0:
        return None
    cov = sum((x - x_mean) * (y - y_mean) for x, y in pairs)
    return round(cov / math.sqrt(x_var * y_var), 4)


def _distinct_values(values: List[Tuple[int, float]]) -> List[Tuple[int, float]]:
    result: List[Tuple[int, float]] = []
    previous = None
    for frame_idx, value in values:
        rounded = round(value, 4)
        if previous is None or rounded != previous:
            result.append((frame_idx, value))
            previous = rounded
    return result


def _monotonic_ratio(values: List[float]) -> Optional[float]:
    if len(values) < 2:
        return None
    steps = [b - a for a, b in zip(values, values[1:])]
    return round(sum(1 for step in steps if step >= 0) / len(steps), 4)


def _player_maps(parsed: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
    return {
        player["entity_id"]: player
        for team in ("left", "right")
        for player in parsed.get("teams", {}).get(team, [])
        if player.get("entity_id")
    }


def _truth_values(match: Dict[str, Any], field: str) -> Dict[str, float]:
    players = match.get("players", {})
    if not isinstance(players, dict):
        return {}
    values = {}
    for player_name, row in players.items():
        if isinstance(row, dict) and isinstance(row.get(field), (int, float)):
            values[str(player_name)] = float(row[field])
    return values


def _context_header_hits(payload: bytes) -> Counter:
    payload_hex = payload.hex()
    hits = Counter()
    for header_hex, label in KNOWN_CONTEXT_HEADERS.items():
        count = payload_hex.count(header_hex)
        if count:
            hits[label] += count
    return hits


def _classify_family(family: Family, aggregate: Dict[str, Any]) -> str:
    action, encoding, offset = family
    target_rate = aggregate.get("target_id_context_rate") or 0
    timestamp_rate = aggregate.get("timestamp_context_rate") or 0
    header_rate = aggregate.get("known_header_context_rate") or 0
    raw_gold_mape = aggregate.get("raw_gold_mape")
    gold_corr = aggregate.get("truth_correlations", {}).get("gold")

    if encoding.startswith("f32") and timestamp_rate >= 0.65:
        return "reject_timestamp_like"
    if action == 0x01 and encoding == "u32be" and offset == 1 and target_rate >= 0.65:
        return "reject_target_entity_id_like"
    if action == 0x01 and encoding == "u32le" and offset == 3 and target_rate >= 0.65:
        return "reject_endian_alias_of_target_entity"
    if action == 0x01 and header_rate >= 0.5 and target_rate >= 0.5:
        return "reject_embedded_event_context"
    if isinstance(raw_gold_mape, (int, float)) and raw_gold_mape <= 0.10 and isinstance(gold_corr, (int, float)) and gold_corr >= 0.90:
        return "plausible_gold_total"
    if isinstance(gold_corr, (int, float)) and gold_corr >= 0.70 and target_rate >= 0.50:
        return "reject_correlated_progression_not_gold_total"
    return "unresolved_resource_candidate"


def evaluate_candidate_family(replay_file: str, match: Dict[str, Any], family: Family) -> Dict[str, Any]:
    """Evaluate one candidate family in one replay against truth and context signals."""
    action, encoding, offset = family
    parsed = VGRParser(replay_file, auto_truth=False).parse()
    players_by_le = _player_maps(parsed)
    truth_gold = _truth_values(match, "gold")
    truth_minions = _truth_values(match, "minion_kills")
    truth_kills = _truth_values(match, "kills")
    truth_deaths = _truth_values(match, "deaths")
    truth_assists = _truth_values(match, "assists")

    grouped: Dict[str, List[Tuple[int, float]]] = defaultdict(list)
    context_totals = Counter()
    context_header_counts = Counter()
    considered_events = 0

    for event in iter_player_events(replay_file):
        if event.action != action or event.entity_id_le not in players_by_le:
            continue
        payload = bytes.fromhex(event.payload_hex)
        value = _decode(payload, encoding, offset)
        if value is None or not 0 <= value <= 100_000:
            continue

        considered_events += 1
        player_name = str(players_by_le[event.entity_id_le].get("name"))
        grouped[player_name].append((event.frame_idx, value))

        target_value = _decode(payload, "u32be", 1)
        if target_value is not None and 1000 <= target_value <= 3000:
            context_totals["target_id_context"] += 1
        timestamp_value = _decode(payload, "f32be", 7)
        if timestamp_value is not None and 0 <= timestamp_value <= 5000:
            context_totals["timestamp_context"] += 1
        header_hits = _context_header_hits(payload)
        if header_hits:
            context_totals["known_header_context"] += 1
            context_header_counts.update(header_hits)

    player_rows = []
    correlation_pairs: Dict[str, List[Tuple[float, float]]] = {
        "gold": [],
        "minion_kills": [],
        "kills": [],
        "deaths": [],
        "assists": [],
        "frame_index": [],
    }
    raw_gold_errors = []
    monotonic_ratios = []

    for player_name, values in grouped.items():
        distinct = _distinct_values(values)
        if len(distinct) < 3:
            continue
        frames = [float(frame_idx) for frame_idx, _ in distinct]
        decoded_values = [value for _, value in distinct]
        final_value = decoded_values[-1]
        mono = _monotonic_ratio(decoded_values)
        if mono is not None:
            monotonic_ratios.append(mono)

        row = {
            "player_name": player_name,
            "event_count": len(values),
            "distinct_count": len(distinct),
            "first_frame": distinct[0][0],
            "last_frame": distinct[-1][0],
            "first_value": round(decoded_values[0], 4),
            "final_value": round(final_value, 4),
            "monotonic_ratio": mono,
            "frame_value_correlation": _pearson(list(zip(frames, decoded_values))),
            "sample_values": [round(value, 4) for value in decoded_values[:8]],
            "tail_values": [round(value, 4) for value in decoded_values[-6:]],
        }

        if player_name in truth_gold:
            gold = truth_gold[player_name]
            row["truth_gold"] = gold
            row["raw_gold_error"] = round(final_value - gold, 4)
            row["raw_gold_error_pct"] = round(abs(final_value - gold) / gold, 4) if gold else None
            raw_gold_errors.append(abs(final_value - gold) / gold if gold else 0)
            correlation_pairs["gold"].append((final_value, gold))
        if player_name in truth_minions:
            row["truth_minion_kills"] = truth_minions[player_name]
            correlation_pairs["minion_kills"].append((final_value, truth_minions[player_name]))
        if player_name in truth_kills:
            correlation_pairs["kills"].append((final_value, truth_kills[player_name]))
        if player_name in truth_deaths:
            correlation_pairs["deaths"].append((final_value, truth_deaths[player_name]))
        if player_name in truth_assists:
            correlation_pairs["assists"].append((final_value, truth_assists[player_name]))
        correlation_pairs["frame_index"].extend(zip(decoded_values, frames))

        player_rows.append(row)

    truth_correlations = {
        metric: corr
        for metric, pairs in correlation_pairs.items()
        if (corr := _pearson(pairs)) is not None
    }

    aggregate = {
        "players_covered": len(player_rows),
        "considered_events": considered_events,
        "avg_monotonic_ratio": round(mean(monotonic_ratios), 4) if monotonic_ratios else None,
        "avg_final_value": round(mean(row["final_value"] for row in player_rows), 4) if player_rows else None,
        "raw_gold_mape": round(mean(raw_gold_errors), 4) if raw_gold_errors else None,
        "truth_correlations": truth_correlations,
        "target_id_context_rate": round(context_totals["target_id_context"] / considered_events, 4) if considered_events else 0,
        "timestamp_context_rate": round(context_totals["timestamp_context"] / considered_events, 4) if considered_events else 0,
        "known_header_context_rate": round(context_totals["known_header_context"] / considered_events, 4) if considered_events else 0,
        "known_header_context_counts": dict(context_header_counts.most_common()),
    }

    return {
        "family": _format_family(family),
        "replay_name": match.get("replay_name") or parsed.get("replay_name"),
        "replay_file": replay_file,
        "verdict": _classify_family(family, aggregate),
        "aggregate": aggregate,
        "players": sorted(player_rows, key=lambda row: row["player_name"]),
    }


def _global_summary(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    verdicts = Counter()
    by_family: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for match in matches:
        for row in match.get("families", []):
            if not isinstance(row, dict):
                continue
            verdicts[str(row.get("verdict"))] += 1
            by_family[str(row.get("family"))].append(row)

    family_rows = []
    for family, rows in by_family.items():
        verdict_counts = Counter(str(row.get("verdict")) for row in rows)
        aggregates = [row.get("aggregate", {}) for row in rows if isinstance(row.get("aggregate"), dict)]
        correlations: Dict[str, List[float]] = defaultdict(list)
        for aggregate in aggregates:
            for metric, value in aggregate.get("truth_correlations", {}).items():
                if isinstance(value, (int, float)):
                    correlations[str(metric)].append(float(value))
        family_rows.append(
            {
                "family": family,
                "matches_seen": len(rows),
                "verdict_counts": dict(verdict_counts.most_common()),
                "avg_raw_gold_mape": round(
                    mean(value for aggregate in aggregates if isinstance((value := aggregate.get("raw_gold_mape")), (int, float))),
                    4,
                )
                if any(isinstance(aggregate.get("raw_gold_mape"), (int, float)) for aggregate in aggregates)
                else None,
                "avg_target_id_context_rate": round(mean(float(aggregate.get("target_id_context_rate") or 0) for aggregate in aggregates), 4)
                if aggregates
                else None,
                "avg_timestamp_context_rate": round(mean(float(aggregate.get("timestamp_context_rate") or 0) for aggregate in aggregates), 4)
                if aggregates
                else None,
                "avg_known_header_context_rate": round(mean(float(aggregate.get("known_header_context_rate") or 0) for aggregate in aggregates), 4)
                if aggregates
                else None,
                "avg_truth_correlations": {
                    metric: round(mean(values), 4)
                    for metric, values in sorted(correlations.items())
                    if values
                },
            }
        )
    family_rows.sort(key=lambda row: (row["matches_seen"], row["family"]), reverse=True)
    return {
        "matches_processed": len(matches),
        "verdict_counts": dict(verdicts.most_common()),
        "families": family_rows,
    }


def build_resource_candidate_validation(
    truth_path: str,
    families: Iterable[str] = DEFAULT_FAMILIES,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    parsed_families = [_parse_family(family) for family in families]
    matches = []
    processed = 0
    for match in _load_truth_matches(truth_path):
        replay_file = match.get("replay_file")
        if not replay_file or not Path(str(replay_file)).exists():
            continue
        row = {
            "replay_name": match.get("replay_name"),
            "replay_file": str(replay_file),
            "families": [
                evaluate_candidate_family(str(replay_file), match, family)
                for family in parsed_families
            ],
        }
        matches.append(row)
        processed += 1
        if limit is not None and processed >= limit:
            break

    return {
        "schema_version": "decoder_v2.resource_candidate_validation.v1",
        "truth_path": str(Path(truth_path).resolve()),
        "families_requested": [_format_family(family) for family in parsed_families],
        "summary": _global_summary(matches),
        "matches": matches,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate monotonic resource candidates against truth gold and context signals."
    )
    parser.add_argument("--truth", default="vg/output/tournament_truth.json", help="Truth JSON path")
    parser.add_argument(
        "--family",
        action="append",
        dest="families",
        help="Candidate family in 0x01:u32be@1 format. Repeatable; defaults to top HackedGlory follow-up families.",
    )
    parser.add_argument("--limit", type=int, help="Optional maximum replay count")
    parser.add_argument("-o", "--output", help="Optional output JSON path")
    args = parser.parse_args(argv)

    report = build_resource_candidate_validation(
        truth_path=args.truth,
        families=args.families or DEFAULT_FAMILIES,
        limit=args.limit,
    )
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(payload, encoding="utf-8")
        print(f"Resource candidate validation saved to {output_path}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
