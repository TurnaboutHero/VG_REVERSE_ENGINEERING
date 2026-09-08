"""
Legacy KDA candidate extraction from strictly framed Vainglory replay records.

The candidate labels and counting rules in this module are historical heuristics;
they are not validated native event names. In particular, opcode 0x041D is a
generic resource/counter update whose index and mode are preserved below.
"""
import math
import struct
from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set

from vg.core.vgr_records import VGRRecord, iter_records


KILL_HEADER = bytes([0x18, 0x04, 0x1C])
DEATH_HEADER = bytes([0x08, 0x04, 0x31])
CREDIT_HEADER = bytes([0x10, 0x04, 0x1D])


@dataclass
class CreditRecord:
    """A framed 0x041D update retained by the legacy assist heuristic."""
    eid: int
    value: float
    offset: int = 0
    action: int = 0
    mode: int = 0
    timestamp: Optional[float] = None
    raw_payload_hex: str = ""


@dataclass
class KillEvent:
    """A record matching the legacy kill-candidate predicate."""
    killer_eid: int
    timestamp: Optional[float] = None
    frame_idx: int = 0
    file_offset: int = 0
    credits: List[CreditRecord] = field(default_factory=list)


@dataclass
class DeathEvent:
    """A record matching the legacy death-candidate predicate."""
    victim_eid: int
    timestamp: float = 0.0
    frame_idx: int = 0
    file_offset: int = 0


@dataclass
class KDAResult:
    """Per-player KDA counts."""
    kills: int = 0
    deaths: int = 0
    assists: int = 0
    minion_kills: int = 0
    kill_events: List[KillEvent] = field(default_factory=list)
    death_events: List[DeathEvent] = field(default_factory=list)


def _matches_kill_structure(record: VGRRecord) -> bool:
    """Return whether a framed record matches the legacy kill structure."""
    if record.opcode != 0x041C or record.content_length != 24:
        return False
    return (
        struct.unpack_from(">I", record.payload, 4)[0] == 0xFFFFFFFF
        and struct.unpack_from(">I", record.payload, 8)[0] == 0x3F800000
        and record.payload[12] == 0x29
    )


class KDADetector:
    """
    Extract legacy KDA candidates from strictly framed VGR replay data.

    Usage:
        detector = KDADetector(valid_entity_ids={0x05DC, 0x05DD, ...})
        for frame_idx, frame_data in frames:
            detector.process_frame(frame_idx, frame_data)
        results = detector.get_results()  # dict of eid -> KDAResult
        # Or with post-game filter:
        results = detector.get_results(game_duration=1028)
    """

    def __init__(self, valid_entity_ids: Set[int]):
        """
        Args:
            valid_entity_ids: Set of valid player entity IDs (Big Endian).
        """
        self.valid_eids = valid_entity_ids
        self._kill_events: List[KillEvent] = []
        self._death_events: List[DeathEvent] = []
        self._minion_kills: Dict[int, int] = defaultdict(int)  # eid -> count

    def process_frame(self, frame_idx: int, data: bytes) -> None:
        """Parse one complete frame and extract only framed candidates.

        Malformed framing raises ``VGRRecordError`` from ``iter_records`` before
        this detector mutates its accumulated results.
        """
        records = list(iter_records(data))

        for record_index, record in enumerate(records):
            if _matches_kill_structure(record):
                eid = struct.unpack_from(">I", record.payload, 0)[0]
                if eid in self.valid_eids:
                    self._kill_events.append(KillEvent(
                        killer_eid=eid,
                        timestamp=record.timestamp,
                        frame_idx=frame_idx,
                        file_offset=record.offset + 7,
                        credits=self._collect_credits(records, record_index),
                    ))
                continue

            if record.opcode == 0x0431 and record.content_length == 8:
                eid = struct.unpack_from(">I", record.payload, 0)[0]
                if eid in self.valid_eids and record.payload[4:] == b"\x00\x00":
                    self._death_events.append(DeathEvent(
                        victim_eid=eid,
                        timestamp=record.timestamp,
                        frame_idx=frame_idx,
                        file_offset=record.offset + 7,
                    ))
                continue

            if record.opcode == 0x041D and record.content_length == 16:
                eid = struct.unpack_from(">I", record.payload, 0)[0]
                value = struct.unpack_from(">f", record.payload, 4)[0]
                index = record.payload[8]
                if (
                    eid in self.valid_eids
                    and abs(value - 1.0) < 0.01
                    and index == 0x0E
                ):
                    self._minion_kills[eid] += 1

    def _collect_credits(
        self, records: List[VGRRecord], kill_index: int
    ) -> List[CreditRecord]:
        """Apply the legacy framed-record neighborhood used for assists."""
        kill_signature_offset = records[kill_index].offset + 7
        limit = kill_signature_offset + 16 + 500
        credits: List[CreditRecord] = []

        for record in records[kill_index + 1:]:
            signature_offset = record.offset + 7
            if signature_offset >= limit:
                break
            if _matches_kill_structure(record):
                break
            if record.opcode != 0x041D or record.content_length != 16:
                continue

            eid = struct.unpack_from(">I", record.payload, 0)[0]
            value = struct.unpack_from(">f", record.payload, 4)[0]
            if (
                eid in self.valid_eids
                and math.isfinite(value)
                and 0 <= value <= 10000
            ):
                credits.append(CreditRecord(
                    eid=eid,
                    value=round(value, 2),
                    offset=signature_offset,
                    action=record.payload[8],
                    mode=record.payload[9],
                    timestamp=record.timestamp,
                    raw_payload_hex=record.payload.hex(),
                ))

        return credits

    def get_results(self, game_duration: Optional[float] = None,
                    death_buffer: float = 3.0,
                    kill_buffer: float = 20.0,
                    team_map: Optional[Dict[int, str]] = None) -> Dict[int, KDAResult]:
        """
        Get per-player KDA results.

        Args:
            game_duration: If provided, events after game end are filtered.
            death_buffer: Buffer seconds for death filtering (default 3s).
                         Current tournament fixtures still contain a short
                         end-of-match death tail; tighter values undercount.
                         Very-late deaths can still be rescued if they align
                         tightly with an opposing late kill event.
            kill_buffer: Buffer seconds for kill filtering (default 20s).
                        Current truth-covered fixtures show several real
                        scoreboard-counted kills landing well after nominal
                        duration. A wider default materially improves K/D/A
                        agreement on complete matches.
            team_map: Dict mapping entity ID (BE) -> team name ("left"/"right").
                     Required for assist detection. If None, assists remain 0.

        Returns:
            Dict mapping entity ID (BE) to KDAResult.
        """
        results: Dict[int, KDAResult] = {}
        for eid in self.valid_eids:
            results[eid] = KDAResult()

        # Count kills with a wider post-game buffer; current truth fixtures
        # still score several late-tail kills on the final board.
        max_kill_ts = (game_duration + kill_buffer) if game_duration else 9999
        for kev in self._kill_events:
            if kev.killer_eid in results:
                if kev.timestamp is not None and kev.timestamp > max_kill_ts:
                    continue  # Post-game ceremony kill
                results[kev.killer_eid].kills += 1
                results[kev.killer_eid].kill_events.append(kev)

        # Count deaths with a short post-game tail. A narrow rescue path keeps
        # some scoreboard-counted late deaths when they align with a nearby
        # opposing late kill, while still excluding most ceremony noise.
        max_death_ts = (game_duration + death_buffer) if game_duration else 9999
        late_kill_events = [
            kev for kev in self._kill_events
            if kev.timestamp is not None and game_duration is not None and kev.timestamp > game_duration
        ]
        for dev in self._death_events:
            keep_death = dev.timestamp <= max_death_ts
            if (
                not keep_death
                and game_duration is not None
                and team_map
                and dev.timestamp <= game_duration + 25.0
            ):
                victim_team = team_map.get(dev.victim_eid)
                if victim_team:
                    keep_death = any(
                        team_map.get(kev.killer_eid) != victim_team
                        and abs((kev.timestamp or 0.0) - dev.timestamp) <= 2.0
                        for kev in late_kill_events
                    )

            if dev.victim_eid in results and keep_death:
                results[dev.victim_eid].deaths += 1
                results[dev.victim_eid].death_events.append(dev)

        # Count minion kills
        for eid, count in self._minion_kills.items():
            if eid in results:
                results[eid].minion_kills = count

        # Count assists (requires team_map, uses kill_buffer since assists derive from kills)
        if team_map:
            self._count_assists(results, team_map, game_duration, kill_buffer)

        return results

    def _count_assists(self, results: Dict[int, KDAResult],
                       team_map: Dict[int, str],
                       game_duration: Optional[float] = None,
                       death_buffer: float = 10.0) -> None:
        """Count assists from credit records after each kill.

        An assist = non-killer, same-team player with:
          - value==1.0 participation flag
          - at least one OTHER credit record (gold share)
        A lone 1.0 without gold credit is a false positive
        (e.g., Blackfeather passive triggering credit records).
        """
        max_ts = (game_duration + death_buffer) if game_duration else 9999
        for kev in self._kill_events:
            # Skip post-game kills for assist counting
            if kev.timestamp is not None and kev.timestamp > max_ts:
                continue

            killer_eid = kev.killer_eid
            killer_team = team_map.get(killer_eid)
            if not killer_team:
                continue

            # Group credits by entity ID
            credits_by_eid: Dict[int, List[float]] = defaultdict(list)
            for cr in kev.credits:
                credits_by_eid[cr.eid].append(cr.value)

            for eid, values in credits_by_eid.items():
                if eid == killer_eid:
                    continue
                # Must have 1.0 participation flag
                if not any(abs(v - 1.0) < 0.01 for v in values):
                    continue
                # Must have at least 2 credit records (1.0 flag + gold share).
                # A lone [1.0] is a false positive from hero passives.
                if len(values) < 2:
                    continue
                # Must be same team as killer
                if team_map.get(eid) != killer_team:
                    continue
                if eid in results:
                    results[eid].assists += 1

    @property
    def kill_events(self) -> List[KillEvent]:
        return list(self._kill_events)

    @property
    def death_events(self) -> List[DeathEvent]:
        return list(self._death_events)

    def get_kill_death_pairs(self, team_map: Dict[int, str],
                             game_duration: Optional[float] = None,
                             death_buffer: float = 10.0,
                             max_dt: float = 5.0) -> List[dict]:
        """
        Match kills to deaths by timestamp (killer's team != victim's team).

        Args:
            team_map: Dict mapping entity ID (BE) -> team name ("left"/"right").
            game_duration: Optional game duration for death filtering.
            death_buffer: Buffer for death filtering.
            max_dt: Maximum time difference for kill-death matching.

        Returns:
            List of matched events with killer, victim, timestamp, etc.
        """
        max_death_ts = (game_duration + death_buffer) if game_duration else 9999

        # Filter deaths
        valid_deaths = [d for d in self._death_events if d.timestamp <= max_death_ts]
        valid_deaths.sort(key=lambda d: d.timestamp)

        # Sort kills by timestamp
        kills_with_ts = [k for k in self._kill_events if k.timestamp is not None]
        kills_with_ts.sort(key=lambda k: k.timestamp)

        # Greedy 1:1 matching
        used_deaths = set()
        pairs = []

        for kev in kills_with_ts:
            killer_team = team_map.get(kev.killer_eid)
            best_death = None
            best_dt = max_dt
            best_idx = -1

            for di, dev in enumerate(valid_deaths):
                if di in used_deaths:
                    continue
                victim_team = team_map.get(dev.victim_eid)
                if victim_team and victim_team != killer_team:
                    dt = abs(kev.timestamp - dev.timestamp)
                    if dt < best_dt:
                        best_dt = dt
                        best_death = dev
                        best_idx = di

            pairs.append({
                "killer_eid": kev.killer_eid,
                "victim_eid": best_death.victim_eid if best_death else None,
                "kill_ts": kev.timestamp,
                "death_ts": best_death.timestamp if best_death else None,
                "dt": best_dt if best_death else None,
                "frame": kev.frame_idx,
            })
            if best_idx >= 0:
                used_deaths.add(best_idx)

        return pairs
