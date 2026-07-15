"""Boundary event file-order probe.

For each truth match, locate the crystal death record's physical position
(frame_idx, byte offset) and list every kill event within +/-BOUNDARY_WINDOW
seconds of the crystal timestamp, annotated with whether it physically
precedes or follows the crystal record in the byte stream.

Hypothesis: scoreboard-counted boundary kills precede the crystal record;
post-game ceremony kills follow it, even when timestamps tie exactly.

Task 5 extension: the same file-order comparison is applied to 0x0E minion
last-hit credit records (KDADetector._scan_minion_kills has no timestamp
to filter on, so file position is the only implementable signal). For each
match we report which valid-player 0x0E records fall physically after the
crystal record, plus a per-player count of records before/at it.
"""
import json
import struct
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from vg.core.unified_decoder import UnifiedDecoder

DEATH_HEADER = bytes([0x08, 0x04, 0x31])
MINION_CREDIT = bytes([0x10, 0x04, 0x1D])
BOUNDARY_WINDOW = 5.0
TRUTH_PATH = Path(__file__).resolve().parent.parent / "output" / "tournament_truth.json"
OUT_PATH = Path(__file__).resolve().parent.parent / "output" / "boundary_file_order_report.json"


def find_minion_kill_records(frames, valid_eids, eid_map):
    """Scan ALL frames for valid-player 0x0E minion last-hit credit records.

    Mirrors KDADetector._scan_minion_kills branch-for-branch (same bounds
    check, same zero-field check, same eid validity check, same value/action
    validation, same pos-advance behavior) so every record counted here is
    exactly one the real detector would also count in player.minion_kills.

    Returns a list of dicts: {player, eid, frame_idx, offset}, one per
    validated 0x0E record, in scan order.
    """
    hits = []
    for frame_idx, data in frames:
        pos = 0
        while True:
            pos = data.find(MINION_CREDIT, pos)
            if pos == -1:
                break
            if pos + 12 > len(data):
                pos += 1
                continue

            if data[pos+3:pos+5] != b"\x00\x00":
                pos += 1
                continue

            eid = struct.unpack_from(">H", data, pos + 5)[0]
            if eid not in valid_eids:
                pos += 1
                continue

            value = struct.unpack_from(">f", data, pos + 7)[0]
            action = data[pos + 11]

            if abs(value - 1.0) < 0.01 and action == 0x0E:
                player = eid_map.get(eid)
                hits.append({
                    "player": getattr(player, "name", None),
                    "eid": eid,
                    "frame_idx": frame_idx,
                    "offset": pos,
                })

            pos += 3  # Skip past header, same as KDADetector._scan_minion_kills

    return hits


def find_crystal_records(frames):
    """Scan death headers for eid 2000-2005; return [(ts, eid, frame_idx, offset)]."""
    hits = []
    for frame_idx, data in frames:
        pos = 0
        while True:
            pos = data.find(DEATH_HEADER, pos)
            if pos == -1:
                break
            if pos + 13 > len(data) or data[pos+3:pos+5] != b"\x00\x00" or data[pos+7:pos+9] != b"\x00\x00":
                pos += 1
                continue
            eid = struct.unpack_from(">H", data, pos + 5)[0]
            ts = struct.unpack_from(">f", data, pos + 9)[0]
            if 2000 <= eid <= 2005 and 60 < ts < 2400:
                hits.append({"ts": round(ts, 2), "eid": eid, "frame_idx": frame_idx, "offset": pos})
            pos += 1
    return hits


def probe_match(replay_file):
    decoder = UnifiedDecoder(replay_file)
    match = decoder.decode()

    replay_path = Path(replay_file)
    frame_dir = replay_path.parent
    frame_name = replay_path.stem.rsplit(".", 1)[0]
    frames = decoder._load_frames(frame_dir, frame_name)

    all_players = match.all_players
    detector, eid_map, team_map, duration_est = decoder._scan_kda_events(frames, all_players)
    if detector is None:
        return {"replay": str(replay_file), "error": "no valid entity ids"}

    crystals = find_crystal_records(frames)
    crystal_ts = match.crystal_death_ts
    # pick the scanned record matching the decoder's chosen crystal ts
    crystal = None
    if crystal_ts is not None:
        for rec in crystals:
            if abs(rec["ts"] - crystal_ts) < 1.0:
                crystal = rec
                break
    if crystal is None and crystals:
        crystal = max(crystals, key=lambda r: r["ts"])

    # Mirror UnifiedDecoder step 7's own crystal-vs-turret FP check
    # (unified_decoder.py:401-407): a scanned crystal record only counts as
    # a validated anchor if it is at/after (duration_est - 30). Matches where
    # this is false (M4, M6) have a scanned "crystal" that is actually a
    # turret false positive and cannot anchor a position comparison.
    anchor_valid = (
        crystal is not None
        and duration_est is not None
        and crystal["ts"] >= duration_est - 30
    )

    def position(ev):
        return (ev.frame_idx, ev.file_offset)

    def after_crystal(ev):
        if crystal is None:
            return None
        return position(ev) > (crystal["frame_idx"], crystal["offset"])

    boundary_kills = []
    ref_ts = crystal["ts"] if crystal else (match.duration_seconds or 0)
    for kev in detector.kill_events:
        if kev.timestamp is None:
            continue
        if abs(kev.timestamp - ref_ts) <= BOUNDARY_WINDOW or kev.timestamp > ref_ts:
            player = eid_map.get(kev.killer_eid)
            boundary_kills.append({
                "player": getattr(player, "name", None),
                "killer_eid": kev.killer_eid,
                "ts": round(kev.timestamp, 2),
                "frame_idx": kev.frame_idx,
                "offset": kev.file_offset,
                "after_crystal": after_crystal(kev),
            })

    # --- Task 5: minion (0x0E) file-order probe ---
    minion_hits = find_minion_kill_records(frames, detector.valid_eids, eid_map)

    def minion_position(rec):
        return (rec["frame_idx"], rec["offset"])

    minion_after_crystal = []
    minion_after_count_by_player = defaultdict(int)
    minion_before_count_by_player = defaultdict(int)
    for rec in minion_hits:
        if crystal is not None and minion_position(rec) > (crystal["frame_idx"], crystal["offset"]):
            minion_after_crystal.append(rec)
            minion_after_count_by_player[rec["player"]] += 1
        else:
            minion_before_count_by_player[rec["player"]] += 1

    return {
        "replay": str(replay_file),
        "crystal": crystal,
        "crystal_candidates": len(crystals),
        "duration": match.duration_seconds,
        "duration_est": duration_est,
        "anchor_valid": anchor_valid,
        "boundary_kills": sorted(boundary_kills, key=lambda k: (k["frame_idx"], k["offset"])),
        "minion_after_crystal": sorted(minion_after_crystal, key=lambda r: (r["frame_idx"], r["offset"])),
        "minion_after_crystal_count_by_player": dict(minion_after_count_by_player),
        "minion_before_crystal_count_by_player": dict(minion_before_count_by_player),
    }


def main():
    truth = json.loads(TRUTH_PATH.read_text(encoding="utf-8"))
    report = []
    for truth_match in truth["matches"]:
        replay_file = truth_match["replay_file"]
        print(f"probing {replay_file} ...")
        try:
            report.append(probe_match(replay_file))
        except Exception as exc:
            report.append({"replay": replay_file, "error": repr(exc)})
    OUT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {OUT_PATH} ({len(report)} matches)")


if __name__ == "__main__":
    main()
