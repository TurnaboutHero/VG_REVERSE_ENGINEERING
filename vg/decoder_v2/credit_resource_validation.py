"""Validate credit-action resource formulas against truth gold."""

from __future__ import annotations

import argparse
import json
import math
import struct
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Tuple

from vg.core.unified_decoder import _CREDIT_HEADER, _le_to_be
from vg.core.vgr_parser import VGRParser

from .completeness import load_frames
from .minion_research import _load_truth_matches


Formula = Tuple[str, Tuple[int, ...]]


DEFAULT_FORMULAS: Tuple[Formula, ...] = (
    ("base600_plus_0x06_no_sell", (0x06,)),
    ("base600_plus_0x06_0x0d", (0x06, 0x0D)),
    ("base600_plus_0x06_0x0f", (0x06, 0x0F)),
    ("base600_plus_0x06_0x0d_0x0f", (0x06, 0x0D, 0x0F)),
    ("base600_plus_0x06_0x08", (0x06, 0x08)),
    ("base600_plus_0x06_0x08_0x0d_0x0f", (0x06, 0x08, 0x0D, 0x0F)),
)


def _player_maps(parsed: Dict[str, Any]) -> Tuple[Dict[int, str], Dict[str, int]]:
    by_eid_be: Dict[int, str] = {}
    by_name: Dict[str, int] = {}
    for team in ("left", "right"):
        for player in parsed.get("teams", {}).get(team, []):
            entity_id_le = player.get("entity_id")
            player_name = player.get("name")
            if not entity_id_le or not player_name:
                continue
            entity_id_be = _le_to_be(int(entity_id_le))
            by_eid_be[entity_id_be] = str(player_name)
            by_name[str(player_name)] = entity_id_be
    return by_eid_be, by_name


def _resolve_truth_name(player_name: str, truth_players: Dict[str, Any]) -> Optional[str]:
    if player_name in truth_players:
        return player_name
    lower = {key.lower(): key for key in truth_players}
    if player_name.lower() in lower:
        return lower[player_name.lower()]
    return next((key for key in truth_players if key.endswith(player_name)), None)


def _scan_credit_action_sums(replay_file: str, valid_eids: Iterable[int]) -> Dict[int, Dict[str, Any]]:
    valid = set(valid_eids)
    rows: Dict[int, Dict[str, Any]] = defaultdict(
        lambda: {
            "positive_no_sell_by_action": defaultdict(float),
            "positive_all_by_action": defaultdict(float),
            "negative_by_action": defaultdict(float),
            "count_by_action": Counter(),
            "sell_flag_count_by_action": Counter(),
        }
    )

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
            if entity_id_be not in valid:
                pos += 3
                continue
            value = struct.unpack_from(">f", data, pos + 7)[0]
            action = data[pos + 11]
            sell_flag = data[pos + 12]
            if not math.isfinite(value):
                pos += 3
                continue

            row = rows[entity_id_be]
            row["count_by_action"][action] += 1
            if sell_flag:
                row["sell_flag_count_by_action"][(action, sell_flag)] += 1
            if value > 0:
                row["positive_all_by_action"][action] += value
                if sell_flag != 0x01:
                    row["positive_no_sell_by_action"][action] += value
            elif value < 0:
                row["negative_by_action"][action] += abs(value)
            pos += 3

    return rows


def _estimate_formula(row: Dict[str, Any], actions: Tuple[int, ...]) -> float:
    positive_no_sell = row["positive_no_sell_by_action"]
    return 600.0 + sum(float(positive_no_sell.get(action, 0.0)) for action in actions)


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


def _summarize_formula(name: str, actions: Tuple[int, ...], player_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    evaluated = []
    for row in player_rows:
        if row.get("truth_gold") is None:
            continue
        estimate = _estimate_formula(row["credit"], actions)
        truth_gold = float(row["truth_gold"])
        error = estimate - truth_gold
        error_pct = abs(error) / truth_gold if truth_gold else 0.0
        evaluated.append(
            {
                "replay_name": row.get("replay_name"),
                "player_name": row["player_name"],
                "truth_gold": int(truth_gold),
                "estimated_gold": round(estimate),
                "error": round(error),
                "error_pct": round(error_pct, 4),
            }
        )

    if not evaluated:
        return {
            "formula": name,
            "actions": [f"0x{action:02x}" for action in actions],
            "total_players": 0,
        }

    pairs = [(float(row["estimated_gold"]), float(row["truth_gold"])) for row in evaluated]
    within_5 = sum(1 for row in evaluated if row["error_pct"] <= 0.05)
    within_10 = sum(1 for row in evaluated if row["error_pct"] <= 0.10)
    return {
        "formula": name,
        "actions": [f"0x{action:02x}" for action in actions],
        "total_players": len(evaluated),
        "within_5pct": within_5,
        "within_10pct": within_10,
        "accuracy_5pct": round(within_5 / len(evaluated), 4),
        "accuracy_10pct": round(within_10 / len(evaluated), 4),
        "avg_abs_error": round(mean(abs(row["error"]) for row in evaluated), 2),
        "avg_abs_error_pct": round(mean(row["error_pct"] for row in evaluated), 4),
        "avg_signed_error": round(mean(row["error"] for row in evaluated), 2),
        "truth_correlation": _pearson(pairs),
        "worst_errors": sorted(evaluated, key=lambda row: row["error_pct"], reverse=True)[:12],
    }


def _json_action_map(values: Dict[int, float]) -> Dict[str, float]:
    return {f"0x{action:02x}": round(value, 4) for action, value in sorted(values.items())}


def _json_count_map(values: Dict[int, int]) -> Dict[str, int]:
    return {f"0x{action:02x}": int(value) for action, value in sorted(values.items())}


def _json_sell_flag_map(values: Dict[Tuple[int, int], int]) -> Dict[str, int]:
    return {
        f"0x{action:02x}:0x{flag:02x}": int(value)
        for (action, flag), value in sorted(values.items())
    }


def build_match_credit_resource_report(
    match: Dict[str, Any],
    formulas: Tuple[Formula, ...] = DEFAULT_FORMULAS,
) -> Dict[str, Any]:
    replay_file = str(match["replay_file"])
    fixture_dir = Path(replay_file).parent
    parsed = VGRParser(replay_file, auto_truth=False).parse()
    players_by_eid_be, players_by_name = _player_maps(parsed)
    credit_rows = _scan_credit_action_sums(replay_file, players_by_eid_be.keys())
    truth_players = match.get("players", {})

    player_rows = []
    for player_name, entity_id_be in sorted(players_by_name.items()):
        truth_name = _resolve_truth_name(player_name, truth_players) if isinstance(truth_players, dict) else None
        credit = credit_rows.get(entity_id_be)
        if not credit:
            continue
        row = {
            "replay_name": match.get("replay_name") or parsed.get("replay_name"),
            "player_name": player_name,
            "entity_id_be": entity_id_be,
            "truth_name": truth_name,
            "truth_gold": truth_players.get(truth_name, {}).get("gold") if truth_name else None,
            "credit": credit,
        }
        player_rows.append(row)

    formula_reports = [
        _summarize_formula(name, actions, player_rows)
        for name, actions in formulas
    ]
    action_totals = Counter()
    action_counts = Counter()
    sell_flag_counts = Counter()
    for row in player_rows:
        action_totals.update(row["credit"]["positive_no_sell_by_action"])
        action_counts.update(row["credit"]["count_by_action"])
        sell_flag_counts.update(row["credit"]["sell_flag_count_by_action"])

    return {
        "replay_name": match.get("replay_name") or parsed.get("replay_name"),
        "replay_file": replay_file,
        "fixture_directory": str(fixture_dir.resolve()),
        "fixture_directory_name": fixture_dir.name,
        "is_incomplete_fixture": "incomplete" in fixture_dir.name.lower(),
        "player_count": len(player_rows),
        "action_totals_positive_no_sell": _json_action_map(action_totals),
        "action_counts": _json_count_map(action_counts),
        "sell_flag_counts": _json_sell_flag_map(sell_flag_counts),
        "formulas": formula_reports,
        "players": [
            {
                "player_name": row["player_name"],
                "truth_name": row["truth_name"],
                "truth_gold": row["truth_gold"],
                "positive_no_sell_by_action": _json_action_map(row["credit"]["positive_no_sell_by_action"]),
                "positive_all_by_action": _json_action_map(row["credit"]["positive_all_by_action"]),
                "negative_by_action": _json_action_map(row["credit"]["negative_by_action"]),
                "count_by_action": _json_count_map(row["credit"]["count_by_action"]),
            }
            for row in player_rows
        ],
    }


def _combine_formula_results(matches: List[Dict[str, Any]], *, include_incomplete: bool = True) -> List[Dict[str, Any]]:
    grouped: Dict[str, Dict[str, Any]] = {}
    for match in matches:
        if not include_incomplete and match.get("is_incomplete_fixture"):
            continue
        for formula in match.get("formulas", []):
            name = str(formula.get("formula"))
            bucket = grouped.setdefault(
                name,
                {
                    "formula": name,
                    "actions": formula.get("actions", []),
                    "rows": [],
                },
            )
            bucket["rows"].extend(formula.get("worst_errors", []))

    results = []
    for bucket in grouped.values():
        rows = bucket["rows"]
        if not rows:
            continue
        within_5 = sum(1 for row in rows if row["error_pct"] <= 0.05)
        within_10 = sum(1 for row in rows if row["error_pct"] <= 0.10)
        pairs = [(float(row["estimated_gold"]), float(row["truth_gold"])) for row in rows]
        results.append(
            {
                "formula": bucket["formula"],
                "actions": bucket["actions"],
                "total_players": len(rows),
                "within_5pct": within_5,
                "within_10pct": within_10,
                "accuracy_5pct": round(within_5 / len(rows), 4),
                "accuracy_10pct": round(within_10 / len(rows), 4),
                "avg_abs_error": round(mean(abs(row["error"]) for row in rows), 2),
                "avg_abs_error_pct": round(mean(row["error_pct"] for row in rows), 4),
                "avg_signed_error": round(mean(row["error"] for row in rows), 2),
                "truth_correlation": _pearson(pairs),
                "worst_errors": sorted(rows, key=lambda row: row["error_pct"], reverse=True)[:20],
            }
        )
    results.sort(key=lambda row: (row["accuracy_10pct"], row["accuracy_5pct"], -row["avg_abs_error_pct"]), reverse=True)
    return results


def build_credit_resource_validation(
    truth_path: str,
    *,
    limit: Optional[int] = None,
    formulas: Tuple[Formula, ...] = DEFAULT_FORMULAS,
) -> Dict[str, Any]:
    matches = []
    processed = 0
    for match in _load_truth_matches(truth_path):
        replay_file = match.get("replay_file")
        if not replay_file or not Path(str(replay_file)).exists():
            continue
        matches.append(build_match_credit_resource_report(match, formulas=formulas))
        processed += 1
        if limit is not None and processed >= limit:
            break

    combined = _combine_formula_results(matches)
    complete_combined = _combine_formula_results(matches, include_incomplete=False)
    return {
        "schema_version": "decoder_v2.credit_resource_validation.v1",
        "truth_path": str(Path(truth_path).resolve()),
        "matches_processed": len(matches),
        "complete_fixture_matches": sum(1 for match in matches if not match.get("is_incomplete_fixture")),
        "incomplete_fixture_matches": sum(1 for match in matches if match.get("is_incomplete_fixture")),
        "summary": {
            "best_formula_by_10pct": combined[0] if combined else None,
            "formulas": combined,
            "best_complete_fixture_formula_by_10pct": complete_combined[0] if complete_combined else None,
            "complete_fixture_formulas": complete_combined,
            "note": "All formulas are raw credit-action estimates. Truth data has gold only, not XP.",
        },
        "matches": matches,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate credit-action gold formulas against truth fixtures.")
    parser.add_argument("--truth", default="vg/output/tournament_truth.json", help="Truth JSON path")
    parser.add_argument("--limit", type=int, help="Optional maximum replay count")
    parser.add_argument("-o", "--output", help="Optional output JSON path")
    args = parser.parse_args(argv)

    report = build_credit_resource_validation(args.truth, limit=args.limit)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(payload, encoding="utf-8")
        print(f"Credit resource validation saved to {output_path}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
