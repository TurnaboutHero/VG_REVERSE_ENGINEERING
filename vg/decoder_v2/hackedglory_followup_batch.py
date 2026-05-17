"""Batch HackedGlory-inspired follow-up probes across truth-covered replays."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .endgame_burst_probe import build_endgame_burst_report
from .hackedglory_semantic_probe import probe_replay
from .minion_research import _load_truth_matches
from .minion_window_research import build_minion_window_report
from .resource_counter_probe import build_resource_counter_report


def _truth_totals(match: Dict[str, Any]) -> Dict[str, int]:
    players = match.get("players", {})
    if not isinstance(players, dict):
        return {}

    totals = Counter()
    for row in players.values():
        if not isinstance(row, dict):
            continue
        for field in ("kills", "deaths", "assists", "gold", "minion_kills"):
            value = row.get(field)
            if isinstance(value, int):
                totals[field] += value
    return dict(totals)


def _truth_metric_map(match: Dict[str, Any], field: str) -> Dict[str, float]:
    players = match.get("players", {})
    if not isinstance(players, dict):
        return {}
    values = {}
    for player_name, row in players.items():
        if not isinstance(row, dict):
            continue
        value = row.get(field)
        if isinstance(value, (int, float)):
            values[str(player_name)] = float(value)
    return values


def _pearson(pairs: List[tuple[float, float]]) -> Optional[float]:
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
    corr = cov / math.sqrt(x_var * y_var)
    return round(corr, 4)


def _attach_truth_correlations(candidate: Dict[str, Any], match: Dict[str, Any]) -> Dict[str, Any]:
    players = candidate.get("players", [])
    if not isinstance(players, list):
        return candidate

    enriched = dict(candidate)
    correlations = {}
    for field in ("gold", "minion_kills", "kills", "deaths", "assists"):
        truth_values = _truth_metric_map(match, field)
        pairs = []
        for player in players:
            if not isinstance(player, dict):
                continue
            player_name = player.get("player_name")
            final_value = player.get("final_value")
            if player_name in truth_values and isinstance(final_value, (int, float)):
                pairs.append((float(final_value), truth_values[str(player_name)]))
        corr = _pearson(pairs)
        if corr is not None:
            correlations[field] = corr
    enriched["truth_metric_correlation"] = correlations
    return enriched


def _semantic_summary(report: Dict[str, Any]) -> Dict[str, Any]:
    targets = report.get("targets", [])
    missing = []
    partial = []
    for target in targets if isinstance(targets, list) else []:
        if not isinstance(target, dict):
            continue
        status = target.get("status")
        name = target.get("target")
        if status == "missing":
            missing.append(name)
        elif status == "partial":
            partial.append(name)

    return {
        "target_status_counts": report.get("summary", {}).get("target_status_counts", {}),
        "local_semantic_ready_players": report.get("summary", {}).get("local_semantic_ready_players"),
        "strict_hackedglory_replay_ready_players": report.get("summary", {}).get(
            "strict_hackedglory_replay_ready_players"
        ),
        "scoreboard_readiness": report.get("summary", {}).get("scoreboard_readiness", {}),
        "missing_targets": missing,
        "partial_targets": partial,
    }


def _resource_summary(report: Dict[str, Any], match: Dict[str, Any], top: int) -> Dict[str, Any]:
    families = report.get("family_counter_candidates", [])
    credits = report.get("credit_delta_summary", [])
    if isinstance(families, list):
        family_rows = [_attach_truth_correlations(item, match) for item in families[:top] if isinstance(item, dict)]
    else:
        family_rows = []
    return {
        "summary": report.get("summary", {}),
        "top_family_counter_candidates": family_rows,
        "top_credit_delta_rows": credits[:top] if isinstance(credits, list) else [],
    }


def _focus_key(row: Dict[str, Any]) -> str:
    name = row.get("player_name") or "unknown"
    team = row.get("team") or "unknown"
    return f"{team}:{name}"


def _focus_score(row: Dict[str, Any]) -> int:
    return int(row.get("known_header_total") or 0) + int(row.get("player_event_total") or 0)


def _focus_result(row: Optional[Dict[str, Any]], truth_winner: Optional[str]) -> str:
    if not row:
        return "no_candidate"
    team = row.get("team")
    if truth_winner in ("left", "right"):
        if team == truth_winner:
            return "winner_side"
        if team in ("left", "right"):
            return "loser_side"
    if team in ("left", "right"):
        return "truth_unknown"
    return "unknown_team"


def _with_truth_winner(row: Dict[str, Any], truth_winner: Optional[str]) -> Dict[str, Any]:
    enriched = dict(row)
    enriched["focus_score"] = _focus_score(row)
    enriched["winner_side"] = row.get("team") == truth_winner if truth_winner in ("left", "right") else None
    return enriched


def _endgame_summary(report: Dict[str, Any], match: Dict[str, Any], top: int) -> Dict[str, Any]:
    focus = report.get("focus_candidates", [])
    generic = report.get("tail_generic_header_summary", [])
    truth_winner = match.get("match_info", {}).get("winner")
    top_focus = focus[0] if isinstance(focus, list) and focus and isinstance(focus[0], dict) else None
    return {
        "summary": report.get("summary", {}),
        "truth_winner": truth_winner,
        "top_focus_result": _focus_result(top_focus, truth_winner),
        "top_focus_candidates": [
            _with_truth_winner(item, truth_winner)
            for item in (focus[:top] if isinstance(focus, list) else [])
            if isinstance(item, dict)
        ],
        "top_tail_generic_headers": generic[:top] if isinstance(generic, list) else [],
        "tail_known_header_summary": report.get("tail_known_header_summary", {}),
    }


def _minion_summary(report: Dict[str, Any], top: int) -> Dict[str, Any]:
    aggregate = report.get("aggregate", {})
    if not isinstance(aggregate, dict):
        return {}
    positive_headers = [
        row
        for row in aggregate.get("positive_enriched_headers", [])
        if isinstance(row, dict) and (row.get("delta_per_target_event") or 0) > 0
    ]
    positive_patterns = [
        row
        for row in aggregate.get("positive_enriched_credit_patterns", [])
        if isinstance(row, dict) and (row.get("delta_per_target_event") or 0) > 0
    ]
    return {
        "players": aggregate.get("players"),
        "positive_residual_players": aggregate.get("positive_residual_players"),
        "nonpositive_or_unknown_players": aggregate.get("nonpositive_or_unknown_players"),
        "positive_target_samples": aggregate.get("positive_target_samples"),
        "nonpositive_target_samples": aggregate.get("nonpositive_target_samples"),
        "top_enriched_headers": positive_headers[:top],
        "top_enriched_credit_patterns": positive_patterns[:top],
    }


def _iter_matches(truth_path: str, limit: Optional[int]) -> Iterable[Dict[str, Any]]:
    count = 0
    for match in _load_truth_matches(truth_path):
        replay_file = match.get("replay_file")
        if not replay_file or not Path(str(replay_file)).exists():
            continue
        yield match
        count += 1
        if limit is not None and count >= limit:
            break


def _global_summary(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    semantic_counts = Counter()
    missing_targets = Counter()
    partial_targets = Counter()
    resource_families = Counter()
    resource_correlations: Dict[str, Dict[str, List[float]]] = {}
    scoreboard_totals = Counter()
    scoreboard_blockers = Counter()
    focus_candidates = Counter()
    endgame_focus_results = Counter()
    minion_headers = Counter()
    minion_patterns = Counter()

    for row in matches:
        semantic = row.get("semantic", {})
        counts = semantic.get("target_status_counts", {}) if isinstance(semantic, dict) else {}
        if isinstance(counts, dict):
            semantic_counts.update({str(key): int(value) for key, value in counts.items()})
        for target in semantic.get("missing_targets", []) if isinstance(semantic, dict) else []:
            missing_targets[str(target)] += 1
        for target in semantic.get("partial_targets", []) if isinstance(semantic, dict) else []:
            partial_targets[str(target)] += 1
        readiness = semantic.get("scoreboard_readiness", {}) if isinstance(semantic, dict) else {}
        if isinstance(readiness, dict):
            for key in (
                "player_count",
                "identity_players",
                "kda_players",
                "gold_players",
                "xp_players",
                "level_players",
                "local_export_ready_players",
                "strict_hackedglory_replay_ready_players",
            ):
                value = readiness.get(key)
                if isinstance(value, int):
                    scoreboard_totals[key] += value
            for blocker in readiness.get("blocking_fields", []):
                scoreboard_blockers[str(blocker)] += 1

        resource = row.get("resource_counter", {})
        for family in resource.get("top_family_counter_candidates", []) if isinstance(resource, dict) else []:
            if not isinstance(family, dict):
                continue
            key = f"{family.get('action')}:{family.get('encoding')}@{family.get('payload_offset')}"
            resource_families[key] += 1
            metric_values = family.get("truth_metric_correlation", {})
            if isinstance(metric_values, dict):
                bucket = resource_correlations.setdefault(key, {})
                for metric, value in metric_values.items():
                    if isinstance(value, (int, float)):
                        bucket.setdefault(str(metric), []).append(float(value))

        endgame = row.get("endgame_burst", {})
        top_result = endgame.get("top_focus_result") if isinstance(endgame, dict) else None
        if top_result:
            endgame_focus_results[str(top_result)] += 1
        for focus in endgame.get("top_focus_candidates", []) if isinstance(endgame, dict) else []:
            if isinstance(focus, dict):
                focus_candidates[_focus_key(focus)] += 1

        minion = row.get("minion_window", {})
        for item in minion.get("top_enriched_headers", []) if isinstance(minion, dict) else []:
            if isinstance(item, dict):
                minion_headers[str(item.get("header_hex"))] += 1
        for item in minion.get("top_enriched_credit_patterns", []) if isinstance(minion, dict) else []:
            if isinstance(item, dict):
                minion_patterns[str(item.get("pattern"))] += 1

    return {
        "matches_processed": len(matches),
        "semantic_target_status_totals": dict(sorted(semantic_counts.items())),
        "semantic_missing_target_frequency": dict(missing_targets.most_common()),
        "semantic_partial_target_frequency": dict(partial_targets.most_common()),
        "scoreboard_readiness_totals": dict(scoreboard_totals),
        "scoreboard_blocking_field_frequency": dict(scoreboard_blockers.most_common()),
        "repeated_resource_family_candidates": dict(resource_families.most_common(20)),
        "repeated_resource_family_truth_correlations": {
            key: {
                "seen": resource_families[key],
                "avg_correlation": {
                    metric: round(sum(values) / len(values), 4)
                    for metric, values in sorted(metrics.items())
                    if values
                },
            }
            for key, metrics in sorted(
                resource_correlations.items(),
                key=lambda item: (-resource_families[item[0]], item[0]),
            )[:20]
        },
        "endgame_top_focus_result_counts": dict(endgame_focus_results.most_common()),
        "endgame_top_focus_winner_side_rate": (
            round(
                endgame_focus_results.get("winner_side", 0)
                / (endgame_focus_results.get("winner_side", 0) + endgame_focus_results.get("loser_side", 0)),
                4,
            )
            if (endgame_focus_results.get("winner_side", 0) + endgame_focus_results.get("loser_side", 0))
            else None
        ),
        "repeated_endgame_focus_candidates": dict(focus_candidates.most_common(20)),
        "repeated_minion_enriched_headers": dict(minion_headers.most_common(20)),
        "repeated_minion_enriched_credit_patterns": dict(minion_patterns.most_common(20)),
    }


def build_hackedglory_followup_batch(
    truth_path: str,
    *,
    limit: Optional[int] = None,
    top: int = 5,
    tail_frames: int = 12,
    include_resource: bool = True,
    include_endgame: bool = True,
    include_minion: bool = True,
) -> Dict[str, Any]:
    """Run compact HackedGlory follow-up summaries for truth-covered replay files."""
    per_match = []
    for match in _iter_matches(truth_path, limit):
        replay_file = str(match["replay_file"])
        row: Dict[str, Any] = {
            "replay_name": match.get("replay_name"),
            "replay_file": replay_file,
            "fixture_directory": str(Path(replay_file).parent.resolve()),
            "truth_totals": _truth_totals(match),
        }

        semantic = probe_replay(replay_file)
        row["semantic"] = _semantic_summary(semantic)

        if include_resource:
            resource = build_resource_counter_report(replay_file, top_n=max(top, 1))
            row["resource_counter"] = _resource_summary(resource, match, top)

        if include_endgame:
            endgame = build_endgame_burst_report(replay_file, tail_frames=tail_frames)
            row["endgame_burst"] = _endgame_summary(endgame, match, top)

        if include_minion:
            minion = build_minion_window_report(replay_file, truth_path=truth_path)
            row["minion_window"] = _minion_summary(minion, top)

        per_match.append(row)

    return {
        "schema_version": "decoder_v2.hackedglory_followup_batch.v1",
        "truth_path": str(Path(truth_path).resolve()),
        "options": {
            "limit": limit,
            "top": top,
            "tail_frames": tail_frames,
            "include_resource": include_resource,
            "include_endgame": include_endgame,
            "include_minion": include_minion,
        },
        "summary": _global_summary(per_match),
        "matches": per_match,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Batch HackedGlory-inspired semantic/resource/endgame/minion probes over truth replays."
    )
    parser.add_argument("--truth", default="vg/output/tournament_truth.json", help="Truth JSON path")
    parser.add_argument("--limit", type=int, help="Optional maximum replay count")
    parser.add_argument("--top", type=int, default=5, help="Rows retained per per-match section")
    parser.add_argument("--tail-frames", type=int, default=12, help="Ending frames inspected by endgame probe")
    parser.add_argument("--skip-resource", action="store_true", help="Skip resource counter probe")
    parser.add_argument("--skip-endgame", action="store_true", help="Skip endgame burst probe")
    parser.add_argument("--skip-minion", action="store_true", help="Skip minion window probe")
    parser.add_argument("-o", "--output", help="Optional output JSON path")
    args = parser.parse_args(argv)

    report = build_hackedglory_followup_batch(
        truth_path=args.truth,
        limit=args.limit,
        top=args.top,
        tail_frames=args.tail_frames,
        include_resource=not args.skip_resource,
        include_endgame=not args.skip_endgame,
        include_minion=not args.skip_minion,
    )
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(payload, encoding="utf-8")
        print(f"HackedGlory follow-up batch saved to {output_path}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
