"""Replay completeness and signal extraction for decoder_v2."""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

from vg.core.kda_detector import KDADetector
from vg.core.native_stats import inspect_native_clock
from vg.core.unified_decoder import _DEATH_HEADER, _ITEM_ACQUIRE_HEADER, _le_to_be
from vg.core.vgr_parser import VGRParser

from .models import CompletenessAssessment, CompletenessStatus, ReplaySignalSummary


def load_frames(replay_file: str) -> List[Tuple[int, bytes]]:
    """Load replay frames as `(frame_index, bytes)` tuples."""
    replay_path = Path(replay_file)
    frame_dir = replay_path.parent
    replay_name = replay_path.stem.rsplit(".", 1)[0]
    return [
        (int(frame.stem.split(".")[-1]), frame.read_bytes())
        for frame in sorted(frame_dir.glob(f"{replay_name}.*.vgr"), key=lambda p: int(p.stem.split(".")[-1]))
    ]


def _scan_max_timestamp_in_bytes(
    data: bytes,
    header: bytes,
    timestamp_offset: int,
    guards: Sequence[Tuple[int, bytes]] = (),
) -> Optional[float]:
    values = []
    pos = 0
    while True:
        idx = data.find(header, pos)
        if idx == -1:
            break
        pos = idx + 1
        if idx + timestamp_offset + 4 > len(data):
            continue
        if any(data[idx + rel:idx + rel + len(expected)] != expected for rel, expected in guards):
            continue
        try:
            ts = struct.unpack_from(">f", data, idx + timestamp_offset)[0]
        except struct.error:
            continue
        if 0 < ts < 5000:
            values.append(ts)
    return max(values) if values else None


def _scan_max_timestamp(
    frames: Sequence[Tuple[int, bytes]],
    header: bytes,
    timestamp_offset: int,
    guards: Sequence[Tuple[int, bytes]] = (),
) -> Optional[float]:
    """Scan the largest valid float timestamp for a header family frame-by-frame."""
    values = []
    for _, data in frames:
        value = _scan_max_timestamp_in_bytes(data, header, timestamp_offset, guards)
        if value is not None:
            values.append(value)
    return max(values) if values else None


def extract_replay_signals(replay_file: str) -> ReplaySignalSummary:
    """Extract timing/completeness signals from a replay."""
    parser = VGRParser(replay_file, auto_truth=False)
    parsed = parser.parse()
    frames = load_frames(replay_file)

    valid_eids = {
        _le_to_be(player["entity_id"])
        for team in ("left", "right")
        for player in parsed["teams"][team]
        if player.get("entity_id")
    }

    detector = KDADetector(valid_eids)
    for frame_idx, data in frames:
        detector.process_frame(frame_idx, data)

    max_kill_ts = max((event.timestamp for event in detector.kill_events if event.timestamp is not None), default=None)
    max_player_death_ts = max((event.timestamp for event in detector.death_events), default=None)
    max_death_header_ts = _scan_max_timestamp(
        frames,
        _DEATH_HEADER,
        9,
        guards=((3, b"\x00\x00"), (7, b"\x00\x00")),
    )
    max_item_ts = _scan_max_timestamp(
        frames,
        _ITEM_ACQUIRE_HEADER,
        17,
        guards=((3, b"\x00\x00"),),
    )

    crystal_ts = None
    if frames:
        crystal_events = []
        for _, data in frames:
            pos = 0
            while True:
                idx = data.find(_DEATH_HEADER, pos)
                if idx == -1:
                    break
                pos = idx + 1
                if idx + 13 > len(data):
                    continue
                if (
                    data[idx + 3:idx + 5] != b"\x00\x00"
                    or data[idx + 7:idx + 9] != b"\x00\x00"
                ):
                    continue
                eid = struct.unpack_from(">H", data, idx + 5)[0]
                ts = struct.unpack_from(">f", data, idx + 9)[0]
                if 2000 <= eid <= 2005 and 60 < ts < 2400:
                    crystal_events.append(ts)
        if crystal_events:
            crystal_ts = max(crystal_events)

    clock = inspect_native_clock(frames)
    return ReplaySignalSummary(
        replay_name=parsed["replay_name"],
        replay_file=parsed["replay_file"],
        frame_count=len(frames),
        max_frame_index=frames[-1][0] if frames else 0,
        crystal_ts=crystal_ts,
        max_kill_ts=max_kill_ts,
        max_player_death_ts=max_player_death_ts,
        max_death_header_ts=max_death_header_ts,
        max_item_ts=max_item_ts,
        native_clock_valid=clock.valid,
        native_clock_status=clock.status,
        native_clock_reason=clock.reason,
        first_game_time=clock.first_game_time,
        last_game_time=clock.last_game_time,
    )


def assess_completeness(signals: ReplaySignalSummary) -> CompletenessAssessment:
    """Apply a conservative completeness heuristic."""
    if signals.native_clock_valid is False:
        return CompletenessAssessment(
            status=CompletenessStatus.COMPLETENESS_UNKNOWN,
            reason=f"Native clock integrity failed ({signals.native_clock_status}): {signals.native_clock_reason}",
            signals=signals,
        )

    crystal_ts = signals.crystal_ts
    max_death_ts = signals.max_player_death_ts
    max_death_header_ts = signals.max_death_header_ts
    max_item_ts = signals.max_item_ts

    if signals.frame_count < 20:
        return CompletenessAssessment(
            status=CompletenessStatus.INCOMPLETE_CONFIRMED,
            reason="Tiny replay snippet lacks enough signal to represent a full match.",
            signals=signals,
        )

    if (
        crystal_ts is not None
        and max_death_ts is not None
        and abs(crystal_ts - max_death_ts) <= 30
    ):
        return CompletenessAssessment(
            status=CompletenessStatus.COMPLETE_CONFIRMED,
            reason="Crystal death agrees with player-death tail within 30s.",
            signals=signals,
        )

    if (
        crystal_ts is not None
        and max_death_header_ts is not None
        and max_item_ts is not None
        and signals.frame_count >= 180
        and crystal_ts >= 1800
        and abs(max_death_header_ts - crystal_ts) <= 30
        and abs(max_item_ts - crystal_ts) <= 60
        and (max_death_ts is None or (crystal_ts - max_death_ts) >= 100)
    ):
        return CompletenessAssessment(
            status=CompletenessStatus.COMPLETE_CONFIRMED,
            reason="Late crystal, generic death-header, and item tails agree even though player-death tail appears stale.",
            signals=signals,
        )

    if (
        crystal_ts is None
        and max_death_ts is not None
        and max_death_header_ts is not None
        and max_death_ts < 600
        and (max_death_header_ts - max_death_ts) > 300
        and signals.frame_count < 90
    ):
        return CompletenessAssessment(
            status=CompletenessStatus.INCOMPLETE_CONFIRMED,
            reason="No crystal death, short frame count, and large gap between player-death tail and generic death-header tail.",
            signals=signals,
        )

    return CompletenessAssessment(
        status=CompletenessStatus.COMPLETENESS_UNKNOWN,
        reason="No corroborated terminal crystal evidence; aligned activity tails do not confirm match completion.",
        signals=signals,
    )
