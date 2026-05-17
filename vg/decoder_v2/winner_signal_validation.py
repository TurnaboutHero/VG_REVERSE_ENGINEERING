"""Validate HackedGlory-1077-like endgame candidates against truth winners."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from .endgame_burst_probe import build_endgame_burst_report
from .minion_research import _load_truth_matches


VALID_WINNERS = {"left", "right"}


def _candidate_score(candidate: Dict[str, Any]) -> int:
    return int(candidate.get("known_header_total") or 0) + int(candidate.get("player_event_total") or 0)


def _candidate_family(candidate: Dict[str, Any]) -> str:
    if candidate.get("known_headers"):
        headers = ",".join(str(key) for key in candidate.get("known_headers", {}).keys())
        return f"known:{headers}"
    if candidate.get("player_event_actions"):
        actions = ",".join(str(key) for key in list(candidate.get("player_event_actions", {}).keys())[:4])
        return f"player_event:{actions}"
    return "unknown"


def _iter_truth_matches(truth_path: str, limit: Optional[int]) -> Iterable[Dict[str, Any]]:
    yielded = 0
    for match in _load_truth_matches(truth_path):
        replay_file = match.get("replay_file")
        winner = match.get("match_info", {}).get("winner")
        if winner not in VALID_WINNERS:
            continue
        if not replay_file or not Path(str(replay_file)).exists():
            continue
        yield match
        yielded += 1
        if limit is not None and yielded >= limit:
            break


def _enrich_candidate(candidate: Dict[str, Any], winner: str) -> Dict[str, Any]:
    score = _candidate_score(candidate)
    team = candidate.get("team")
    return {
        "player_name": candidate.get("player_name"),
        "team": team,
        "winner_side": team == winner,
        "score": score,
        "known_header_total": candidate.get("known_header_total"),
        "known_headers": candidate.get("known_headers"),
        "player_event_total": candidate.get("player_event_total"),
        "player_event_actions": candidate.get("player_event_actions"),
        "entity_id_be": candidate.get("entity_id_be"),
        "entity_id_le": candidate.get("entity_id_le"),
        "candidate_family": _candidate_family(candidate),
    }


def _top_result(top_candidate: Optional[Dict[str, Any]], winner: str) -> str:
    if not top_candidate:
        return "no_candidate"
    team = top_candidate.get("team")
    if team == winner:
        return "winner_side"
    if team in VALID_WINNERS:
        return "loser_side"
    return "unknown_team"


def _summarize_tail_generic_headers(
    report: Dict[str, Any],
    *,
    min_tail_fraction: float,
    min_tail_count: int,
) -> List[Dict[str, Any]]:
    rows = []
    for row in report.get("tail_generic_header_summary", []):
        if not isinstance(row, dict):
            continue
        tail_fraction = row.get("tail_fraction")
        tail_count = row.get("tail_count")
        if not isinstance(tail_fraction, (int, float)) or not isinstance(tail_count, int):
            continue
        if tail_fraction < min_tail_fraction or tail_count < min_tail_count:
            continue
        rows.append(
            {
                "header_hex": row.get("header_hex"),
                "tail_count": tail_count,
                "all_count": row.get("all_count"),
                "tail_fraction": tail_fraction,
            }
        )
    return rows


def _match_summary(
    match: Dict[str, Any],
    report: Dict[str, Any],
    *,
    top: int,
    min_tail_fraction: float,
    min_tail_count: int,
) -> Dict[str, Any]:
    winner = str(match.get("match_info", {}).get("winner"))
    focus_candidates = [
        candidate for candidate in report.get("focus_candidates", []) if isinstance(candidate, dict)
    ]
    enriched = [_enrich_candidate(candidate, winner) for candidate in focus_candidates[:top]]
    top_candidate = enriched[0] if enriched else None
    second_score = enriched[1]["score"] if len(enriched) > 1 else None
    top_score = top_candidate["score"] if top_candidate else None
    return {
        "replay_name": match.get("replay_name"),
        "replay_file": str(match.get("replay_file")),
        "fixture_directory": str(Path(str(match.get("replay_file"))).parent.resolve()),
        "truth_winner": winner,
        "probe_summary": report.get("summary", {}),
        "top_result": _top_result(top_candidate, winner),
        "top_score": top_score,
        "second_score": second_score,
        "top_score_margin": (top_score - second_score) if top_score is not None and second_score is not None else None,
        "top_focus_candidates": enriched,
        "winner_side_candidate_count": sum(1 for candidate in focus_candidates if candidate.get("team") == winner),
        "loser_side_candidate_count": sum(
            1 for candidate in focus_candidates if candidate.get("team") in VALID_WINNERS and candidate.get("team") != winner
        ),
        "tail_concentrated_generic_headers": _summarize_tail_generic_headers(
            report,
            min_tail_fraction=min_tail_fraction,
            min_tail_count=min_tail_count,
        ),
    }


def _assessment(summary: Dict[str, Any]) -> Dict[str, Any]:
    with_candidate = int(summary.get("matches_with_focus_candidate") or 0)
    winner_side = int(summary.get("top_focus_winner_side") or 0)
    loser_side = int(summary.get("top_focus_loser_side") or 0)
    if with_candidate == 0:
        return {
            "status": "no_candidate",
            "reason": "No endgame focus candidates were found in truth-covered replays.",
        }
    accuracy = winner_side / with_candidate
    if accuracy >= 0.8 and loser_side == 0 and winner_side >= 3:
        return {
            "status": "candidate",
            "reason": "Top endgame focus candidates consistently point to the truth winner side.",
        }
    return {
        "status": "rejected",
        "reason": (
            "Current tail focus candidates are not a safe independent winner signal; "
            f"top focus matched the truth winner in {winner_side}/{with_candidate} matches."
        ),
    }


def _global_summary(matches: List[Dict[str, Any]]) -> Dict[str, Any]:
    top_results = Counter(str(row.get("top_result")) for row in matches)
    candidate_families = Counter()
    repeated_tail_headers = Counter()
    for row in matches:
        top_focus = row.get("top_focus_candidates", [])
        if top_focus and isinstance(top_focus[0], dict):
            candidate_families[str(top_focus[0].get("candidate_family"))] += 1
        for header in row.get("tail_concentrated_generic_headers", []):
            if isinstance(header, dict):
                repeated_tail_headers[str(header.get("header_hex"))] += 1

    summary = {
        "matches_processed": len(matches),
        "matches_with_focus_candidate": sum(
            1 for row in matches if row.get("top_result") != "no_candidate"
        ),
        "top_focus_winner_side": top_results.get("winner_side", 0),
        "top_focus_loser_side": top_results.get("loser_side", 0),
        "top_focus_unknown_team": top_results.get("unknown_team", 0),
        "top_focus_no_candidate": top_results.get("no_candidate", 0),
        "top_result_counts": dict(top_results.most_common()),
        "top_candidate_family_frequency": dict(candidate_families.most_common(20)),
        "repeated_tail_concentrated_generic_headers": dict(repeated_tail_headers.most_common(20)),
    }
    summary["top_focus_winner_side_rate"] = (
        round(summary["top_focus_winner_side"] / summary["matches_with_focus_candidate"], 4)
        if summary["matches_with_focus_candidate"]
        else None
    )
    summary["assessment"] = _assessment(summary)
    return summary


def build_winner_signal_validation(
    truth_path: str,
    *,
    limit: Optional[int] = None,
    top: int = 5,
    tail_frames: int = 12,
    min_tail_fraction: float = 0.5,
    min_tail_count: int = 3,
) -> Dict[str, Any]:
    """Compare local endgame burst/focus candidates to truth winner labels."""
    per_match = []
    for match in _iter_truth_matches(truth_path, limit):
        replay_file = str(match["replay_file"])
        report = build_endgame_burst_report(replay_file, tail_frames=tail_frames)
        per_match.append(
            _match_summary(
                match,
                report,
                top=top,
                min_tail_fraction=min_tail_fraction,
                min_tail_count=min_tail_count,
            )
        )

    return {
        "schema_version": "decoder_v2.winner_signal_validation.v1",
        "truth_path": str(Path(truth_path).resolve()),
        "options": {
            "limit": limit,
            "top": top,
            "tail_frames": tail_frames,
            "min_tail_fraction": min_tail_fraction,
            "min_tail_count": min_tail_count,
        },
        "summary": _global_summary(per_match),
        "matches": per_match,
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate HackedGlory-1077-like local winner burst candidates against truth winners."
    )
    parser.add_argument("--truth", default="vg/output/tournament_truth.json", help="Truth JSON path")
    parser.add_argument("--limit", type=int, help="Optional maximum replay count")
    parser.add_argument("--top", type=int, default=5, help="Top focus candidates retained per match")
    parser.add_argument("--tail-frames", type=int, default=12, help="Ending frames inspected by endgame probe")
    parser.add_argument(
        "--min-tail-fraction",
        type=float,
        default=0.5,
        help="Minimum tail/all fraction for concentrated generic header reporting",
    )
    parser.add_argument(
        "--min-tail-count",
        type=int,
        default=3,
        help="Minimum tail count for concentrated generic header reporting",
    )
    parser.add_argument("-o", "--output", help="Optional output JSON path")
    args = parser.parse_args(argv)

    report = build_winner_signal_validation(
        truth_path=args.truth,
        limit=args.limit,
        top=args.top,
        tail_frames=args.tail_frames,
        min_tail_fraction=args.min_tail_fraction,
        min_tail_count=args.min_tail_count,
    )
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(payload, encoding="utf-8")
        print(f"Winner signal validation saved to {output_path}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
