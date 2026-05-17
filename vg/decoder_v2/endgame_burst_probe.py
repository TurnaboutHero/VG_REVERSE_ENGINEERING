"""Search for HackedGlory-1077-like endgame burst candidates in VGR data."""

from __future__ import annotations

import argparse
import json
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from vg.core.unified_decoder import (
    _CREDIT_HEADER,
    _DEATH_HEADER,
    _ITEM_ACQUIRE_HEADER,
    _KILL_HEADER,
    _le_to_be,
)
from vg.core.vgr_parser import VGRParser

from .completeness import load_frames
from .player_events import iter_player_events


KNOWN_HEADERS = {
    _CREDIT_HEADER: "credit",
    _DEATH_HEADER: "death",
    _ITEM_ACQUIRE_HEADER: "item_acquire",
    _KILL_HEADER: "kill",
}


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


def _scan_known_headers(frames: List[Tuple[int, bytes]], players_by_be: Dict[int, Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for frame_idx, data in frames:
        for header, name in KNOWN_HEADERS.items():
            pos = 0
            while True:
                idx = data.find(header, pos)
                if idx == -1:
                    break
                pos = idx + 1
                if idx + 7 > len(data):
                    continue
                entity_id = struct.unpack_from(">H", data, idx + 5)[0]
                player = players_by_be.get(entity_id)
                rows.append(
                    {
                        "frame_idx": frame_idx,
                        "offset": idx,
                        "header": name,
                        "header_hex": header.hex(),
                        "entity_id_be": entity_id,
                        "player_name": player.get("name") if player else None,
                        "team": player.get("team") if player else None,
                    }
                )
    return rows


def _scan_generic_headers(frames: List[Tuple[int, bytes]]) -> Counter:
    counter: Counter[str] = Counter()
    for _, data in frames:
        for idx in range(0, len(data) - 2):
            if data[idx + 1] == 0x04 and data[idx] in (0x08, 0x10, 0x18, 0x28):
                counter[data[idx:idx + 3].hex()] += 1
    return counter


def build_endgame_burst_report(replay_file: str, tail_frames: int = 12) -> Dict[str, Any]:
    parser = VGRParser(replay_file, auto_truth=False)
    parsed = parser.parse()
    players_by_le, players_by_be = _player_maps(parsed)
    frames = load_frames(replay_file)
    tail = frames[-tail_frames:] if tail_frames > 0 else frames

    all_known = _scan_known_headers(frames, players_by_be)
    tail_known = _scan_known_headers(tail, players_by_be)
    all_generic = _scan_generic_headers(frames)
    tail_generic = _scan_generic_headers(tail)

    tail_player_events = [
        event
        for event in iter_player_events(replay_file)
        if tail and event.frame_idx >= tail[0][0]
    ]

    known_by_entity: Dict[int, Counter] = defaultdict(Counter)
    for row in tail_known:
        known_by_entity[row["entity_id_be"]][row["header"]] += 1

    player_event_by_entity: Dict[int, Counter] = defaultdict(Counter)
    for event in tail_player_events:
        player_event_by_entity[event.entity_id_le][f"0x{event.action:02x}"] += 1

    focus_candidates = []
    for entity_id, counter in known_by_entity.items():
        player = players_by_be.get(entity_id)
        total = sum(counter.values())
        if total < 3:
            continue
        focus_candidates.append(
            {
                "entity_id_be": entity_id,
                "player_name": player.get("name") if player else None,
                "team": player.get("team") if player else None,
                "known_header_total": total,
                "known_headers": dict(counter.most_common()),
            }
        )

    for entity_id_le, counter in player_event_by_entity.items():
        player = players_by_le.get(entity_id_le)
        total = sum(counter.values())
        if total < 3:
            continue
        focus_candidates.append(
            {
                "entity_id_le": entity_id_le,
                "entity_id_be": _le_to_be(entity_id_le),
                "player_name": player.get("name") if player else None,
                "team": player.get("team") if player else None,
                "player_event_total": total,
                "player_event_actions": dict(counter.most_common(12)),
            }
        )

    focus_candidates.sort(
        key=lambda item: item.get("known_header_total", 0) + item.get("player_event_total", 0),
        reverse=True,
    )

    generic_rows = []
    for header_hex, tail_count in tail_generic.most_common(30):
        all_count = all_generic.get(header_hex, 0)
        generic_rows.append(
            {
                "header_hex": header_hex,
                "tail_count": tail_count,
                "all_count": all_count,
                "tail_fraction": round(tail_count / all_count, 4) if all_count else None,
            }
        )

    return {
        "schema_version": "decoder_v2.endgame_burst_probe.v1",
        "replay_name": parsed["replay_name"],
        "replay_file": parsed["replay_file"],
        "game_mode": parsed["match_info"]["mode"],
        "tail_frames": tail_frames,
        "frame_count": len(frames),
        "tail_frame_range": [tail[0][0], tail[-1][0]] if tail else None,
        "interpretation": (
            "HackedGlory 1077 appears as a late multi-message burst focused on a winning-side player. "
            "This report searches the VGR tail for repeated known headers, generic xx04yy headers, "
            "and player-scoped action bursts."
        ),
        "summary": {
            "tail_known_header_events": len(tail_known),
            "tail_player_events": len(tail_player_events),
            "focus_candidates": len(focus_candidates),
            "tail_generic_header_types": len(tail_generic),
        },
        "focus_candidates": focus_candidates[:20],
        "tail_known_header_summary": dict(Counter(row["header"] for row in tail_known).most_common()),
        "tail_generic_header_summary": generic_rows,
        "tail_known_header_events_sample": tail_known[:80],
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Search local .vgr tail data for HackedGlory-1077-like bursts.")
    parser.add_argument("replay_file", help="Path to a .0.vgr replay file")
    parser.add_argument("--tail-frames", type=int, default=12, help="Number of ending frames to inspect")
    parser.add_argument("-o", "--output", help="Optional output JSON path")
    args = parser.parse_args(argv)

    report = build_endgame_burst_report(args.replay_file, tail_frames=args.tail_frames)
    payload = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(payload, encoding="utf-8")
        print(f"Endgame burst probe saved to {args.output}")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
