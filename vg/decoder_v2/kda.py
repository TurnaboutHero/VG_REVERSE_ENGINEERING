"""Native statistic decoding with distinct final and capture scopes."""

from __future__ import annotations

import math
from typing import Optional

from vg.core.native_stats import GameTime, RecordTime, read_native_stats
from vg.core.vgr_parser import VGRParser
from vg.core.unified_decoder import _le_to_be

from .completeness import extract_replay_signals, load_frames
from .duration import estimate_duration_from_signals
from .models import CompletenessStatus, KDAExtractionResult, KDAPlayerSummary


def decode_kda_from_replay(replay_file: str, *, at_game_time: Optional[float] = None) -> KDAExtractionResult:
    """Export final statistics only for complete replays, or an explicit capture."""
    signals = extract_replay_signals(replay_file)
    duration_estimate = estimate_duration_from_signals(signals)
    assessment = duration_estimate.assessment
    scope = 'capture' if at_game_time is not None else 'final'

    def reject(reason):
        return KDAExtractionResult(False, reason, assessment, duration_estimate,
                                   scope=scope, at_game_time=at_game_time)

    if at_game_time is not None and (not math.isfinite(at_game_time) or at_game_time < 0):
        return reject('Invalid game time: use a finite non-negative number of seconds.')
    if signals.native_clock_valid is False:
        return reject(assessment.reason)
    if scope == 'final' and assessment.status != CompletenessStatus.COMPLETE_CONFIRMED:
        return reject('Replay completeness is not confirmed; K/D/A export is withheld.')

    parser = VGRParser(replay_file, auto_truth=False)
    parsed = parser.parse()
    ordered_players = []
    for team_label in ('left', 'right'):
        for player in parsed['teams'][team_label]:
            if not player.get('entity_id'):
                return reject('Missing player entity ID; native statistics are withheld.')
            ordered_players.append((_le_to_be(player['entity_id']), team_label, player))
    if not ordered_players:
        return reject('No player identities; native statistics are withheld.')
    cutoff = (GameTime(at_game_time) if at_game_time is not None else
              RecordTime(duration_estimate.estimate_seconds) if duration_estimate.estimate_seconds is not None else None)
    result = read_native_stats(load_frames(replay_file), {eid for eid, _, _ in ordered_players}, cutoff=cutoff)
    if not result.valid:
        return reject(f'Native statistics withheld ({result.status}): {result.reason}')
    by_id = {player.entity_id: player for player in result.players}
    if any(eid not in by_id for eid, _, _ in ordered_players):
        return reject('Native statistics do not cover every player.')
    players = tuple(KDAPlayerSummary(
        player['name'], player.get('team', team), player.get('hero_name', 'Unknown'),
        by_id[eid].kills, by_id[eid].deaths, by_id[eid].assists, by_id[eid].minion_kills,
    ) for eid, team, player in ordered_players)
    return KDAExtractionResult(
        True, 'Native statistics exported for the requested capture.' if scope == 'capture' else
        'Native statistics exported on a completeness-confirmed replay.',
        assessment, duration_estimate, players, scope, at_game_time, result.as_of_game_time,
    )
