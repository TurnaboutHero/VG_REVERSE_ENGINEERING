"""Compare local VGR decoder output against HackedGlory semantic anchors."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from vg.core.vgr_parser import VGRParser

from .decode_match import decode_match_debug


Target = Dict[str, object]


def _players_from_parsed(parsed: Dict[str, Any]) -> List[Dict[str, Any]]:
    players = parsed.get("players")
    if isinstance(players, list) and players and all(isinstance(item, dict) for item in players):
        return players

    teams = parsed.get("teams", {})
    result: List[Dict[str, Any]] = []
    for side in ("left", "right"):
        side_players = teams.get(side, []) if isinstance(teams, dict) else []
        if isinstance(side_players, list):
            result.extend(item for item in side_players if isinstance(item, dict))
    return result


def _kda_players(debug_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    kda = debug_payload.get("kda_debug", {})
    players = kda.get("players", []) if isinstance(kda, dict) else []
    return [item for item in players if isinstance(item, dict)]


def _safe_players(debug_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    safe = debug_payload.get("safe_output", {})
    players = safe.get("players", []) if isinstance(safe, dict) else []
    return [item for item in players if isinstance(item, dict)]


def _status(ok: bool, partial: bool = False) -> str:
    if ok:
        return "covered"
    if partial:
        return "partial"
    return "missing"


def _target(
    name: str,
    status: str,
    hackedglory_signal: str,
    local_evidence: str,
    next_use: str,
) -> Target:
    return {
        "target": name,
        "status": status,
        "hackedglory_signal": hackedglory_signal,
        "local_evidence": local_evidence,
        "next_use": next_use,
    }


def _accepted(debug_payload: Dict[str, Any], field: str) -> bool:
    safe = debug_payload.get("safe_output", {})
    accepted_fields = safe.get("accepted_fields", {}) if isinstance(safe, dict) else {}
    value = accepted_fields.get(field) if isinstance(accepted_fields, dict) else None
    if isinstance(value, dict):
        return bool(value.get("accepted_for_index") or value.get("value") == "accepted")
    return value is not None


def _scoreboard_readiness(
    players: List[Dict[str, Any]],
    safe_players: List[Dict[str, Any]],
    *,
    kda_accepted: bool,
    gold_accepted: bool,
) -> Dict[str, Any]:
    identity_players = sum(
        1
        for player in players
        if player.get("name")
        and player.get("team")
        and player.get("entity_id") is not None
        and player.get("hero_name")
        and player.get("hero_name") != "Unknown"
    )
    gold_players = sum(
        1
        for player in safe_players
        if gold_accepted and isinstance(player.get("gold"), int) and player.get("gold_status") == "accepted"
    )
    kda_players = sum(
        1
        for player in safe_players
        if kda_accepted
        and isinstance(player.get("kills"), int)
        and isinstance(player.get("deaths"), int)
        and isinstance(player.get("assists"), int)
    )
    local_export_ready_players = sum(
        1
        for player in safe_players
        if player.get("name")
        and player.get("team")
        and player.get("entity_id") is not None
        and player.get("hero_name")
        and player.get("hero_name") != "Unknown"
        and isinstance(player.get("kills"), int)
        and isinstance(player.get("deaths"), int)
        and isinstance(player.get("assists"), int)
        and isinstance(player.get("gold"), int)
        and player.get("gold_status") == "accepted"
    )
    xp_players = 0
    level_players = 0
    strict_hackedglory_replay_ready_players = min(gold_players, xp_players, kda_players)
    blocking_fields = []
    if xp_players < len(players):
        blocking_fields.append("xp_total")
    if level_players < len(players):
        blocking_fields.append("level")
    return {
        "player_count": len(players),
        "identity_players": identity_players,
        "kda_players": kda_players,
        "gold_players": gold_players,
        "xp_players": xp_players,
        "level_players": level_players,
        "local_export_ready_players": local_export_ready_players,
        "strict_hackedglory_replay_ready_players": strict_hackedglory_replay_ready_players,
        "blocking_fields": blocking_fields,
    }


def build_semantic_probe(parsed: Dict[str, Any], debug_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Build a HackedGlory semantic comparison report from local decoder outputs."""
    players = _players_from_parsed(parsed)
    kda_players = _kda_players(debug_payload)
    safe_players = _safe_players(debug_payload)
    winner_debug = debug_payload.get("winner_debug", {})
    duration = debug_payload.get("duration", {})
    completeness = debug_payload.get("completeness", {})
    signals = completeness.get("signals", {}) if isinstance(completeness, dict) else {}
    minion_candidates = debug_payload.get("minion_candidates", [])

    player_count = len(players)
    uuid_count = sum(1 for player in players if player.get("uuid"))
    entity_count = sum(1 for player in players if player.get("entity_id") is not None)
    hero_count = sum(
        1
        for player in players
        if player.get("hero_name") and player.get("hero_name") != "Unknown"
    )
    team_values = {player.get("team") for player in players if player.get("team")}
    total_kills = sum(int(player.get("kills") or 0) for player in kda_players)
    total_deaths = sum(int(player.get("deaths") or 0) for player in kda_players)
    total_assists = sum(int(player.get("assists") or 0) for player in kda_players)

    kda_accepted = bool(debug_payload.get("kda_debug", {}).get("accepted"))
    gold_accepted = _accepted(debug_payload, "gold")
    winner_accepted = bool(isinstance(winner_debug, dict) and winner_debug.get("accepted"))
    duration_estimate = duration.get("estimate_seconds") if isinstance(duration, dict) else None
    max_item_ts = signals.get("max_item_ts") if isinstance(signals, dict) else None
    max_death_header_ts = signals.get("max_death_header_ts") if isinstance(signals, dict) else None

    targets = [
        _target(
            "roster_identity",
            _status(player_count > 0),
            "1005/1006/1113/1114 player handle records",
            f"{player_count} parsed local players",
            "Use roster as the first same-match join key.",
        ),
        _target(
            "uuid_identity",
            _status(uuid_count > 0),
            "1000/1006/1113/1114 UUID strings",
            f"{uuid_count}/{player_count} local players have UUIDs",
            "Use name+UUID pairs to confirm same-match alignment.",
        ),
        _target(
            "team_mapping",
            _status(len(team_values) >= 2),
            "1114 team byte and 1011 team field",
            f"local teams={sorted(str(item) for item in team_values)}",
            "Compare sides semantically; do not copy packet byte values.",
        ),
        _target(
            "hero_assignment",
            _status(hero_count == player_count and player_count > 0, hero_count > 0),
            "1107 hero catalog plus weak 1011 hero_type_id candidate",
            f"{hero_count}/{player_count} local heroes decoded from player block +0xA9",
            "Keep local hero id primary; use HackedGlory catalog only as a naming cross-check.",
        ),
        _target(
            "entity_mapping",
            _status(entity_count == player_count and player_count > 0, entity_count > 0),
            "1006 and 1114 player-to-entity mapping",
            f"{entity_count}/{player_count} local players have event entity ids",
            "Use mapping shape, not HackedGlory packet entity ranges.",
        ),
        _target(
            "death_timeline",
            _status(kda_accepted and total_deaths > 0, max_death_header_ts is not None),
            "1067 state index 0 value 3 death transition",
            f"local deaths={total_deaths}, max_death_header_ts={max_death_header_ts}",
            "Compare death ordering and dedupe windows.",
        ),
        _target(
            "kill_attribution",
            _status(kda_accepted and total_kills > 0),
            "1087 pre-death interaction, then opponent-only 1086 reward fallback",
            f"local kills={total_kills}, accepted={kda_accepted}",
            "Use HackedGlory's opponent-only guard to audit local attribution.",
        ),
        _target(
            "assist_credit",
            _status(kda_accepted and total_assists > 0),
            "1087 attackers and reward-window participants",
            f"local assists={total_assists}, accepted={kda_accepted}",
            "Cross-check same-team non-killer credit semantics.",
        ),
        _target(
            "winner_signal",
            _status(winner_accepted),
            "1077 seven-message end burst targeting winning-side focus player",
            f"local winner={winner_debug.get('winner') if isinstance(winner_debug, dict) else None}, accepted={winner_accepted}",
            "Search for an independent .vgr end-burst equivalent.",
        ),
        _target(
            "duration_timeline",
            _status(False, duration_estimate is not None),
            "packet elapsed time from capture start/end and event timestamps",
            f"local duration_estimate={duration_estimate}",
            "Compare normalized elapsed time only; timestamp formats differ.",
        ),
        _target(
            "gold_xp_total",
            _status(False, gold_accepted),
            "1086 type 0x4d total gold and 0x3e total XP monotonic counters",
            "local decoder_v2 exports accepted complete-fixture gold from [10 04 1D] action 0x06; XP is not exported",
            "Keep gold as credit-derived estimate; search separately for XP/level counters.",
        ),
        _target(
            "level_skill",
            "missing",
            "1086 0x3e/0x42 plus nearby 1053 stat changes",
            "local [18 04 3E] byte15=level+12 hypothesis is rejected; no level/XP total is exported",
            "Search for a different XP/level signal; do not promote heartbeat byte15.",
        ),
        _target(
            "items",
            _status(False, max_item_ts is not None),
            "weak 1087 self-target/loadout-like item signal",
            f"local max_item_ts={max_item_ts}; item ids are parsed by separate local logic",
            "Keep local item parser primary; use this as timing context.",
        ),
        _target(
            "creep_score_minions",
            _status(False, isinstance(minion_candidates, list) and len(minion_candidates) > 0),
            "1087 source-target minion interactions plus 1086 reward pulses",
            f"local minion candidate rows={len(minion_candidates) if isinstance(minion_candidates, list) else 0}",
            "Re-test minion counts with source-target-reward windows.",
        ),
    ]

    counts = {
        "covered": sum(1 for item in targets if item["status"] == "covered"),
        "partial": sum(1 for item in targets if item["status"] == "partial"),
        "missing": sum(1 for item in targets if item["status"] == "missing"),
    }

    local_semantic_ready_players = len(kda_players) if kda_accepted else 0
    scoreboard_readiness = _scoreboard_readiness(
        players,
        safe_players,
        kda_accepted=kda_accepted,
        gold_accepted=gold_accepted,
    )
    strict_replay_ready_players = scoreboard_readiness["strict_hackedglory_replay_ready_players"]

    return {
        "schema_version": "hackedglory_semantic_probe.v1",
        "source": "HackedGlory match_decryption semantic anchors",
        "replay_name": parsed.get("replay_name"),
        "replay_file": parsed.get("replay_file"),
        "game_mode": parsed.get("match_info", {}).get("mode"),
        "summary": {
            "player_count": player_count,
            "team_count": len(team_values),
            "completeness_status": completeness.get("status") if isinstance(completeness, dict) else None,
            "target_status_counts": counts,
            "strict_hackedglory_replay_ready_players": strict_replay_ready_players,
            "local_semantic_ready_players": local_semantic_ready_players,
            "scoreboard_readiness": scoreboard_readiness,
        },
        "targets": targets,
        "next_research": [
            "Find a .vgr endgame burst equivalent to HackedGlory opcode 1077.",
            "Search local credit payloads for monotonic total gold and XP counters shaped like HackedGlory 1086.",
            "Re-run minion research using source-target-reward windows instead of isolated action counts.",
        ],
    }


def probe_replay(replay_file: str) -> Dict[str, Any]:
    parsed = VGRParser(replay_file, auto_truth=False).parse()
    debug_payload = decode_match_debug(replay_file)
    return build_semantic_probe(parsed, debug_payload)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score a local .vgr replay against HackedGlory semantic anchors."
    )
    parser.add_argument("replay_file", help="Path to a .0.vgr replay file")
    parser.add_argument("-o", "--output", help="Optional output JSON path")
    args = parser.parse_args(argv)

    payload = probe_replay(args.replay_file)
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"HackedGlory semantic probe saved to {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
