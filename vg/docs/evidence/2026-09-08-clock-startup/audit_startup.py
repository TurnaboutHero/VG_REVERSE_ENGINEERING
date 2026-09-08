"""Audit recorded startup clocks and native checkpoint continuity, read-only.

Run from the repository root with PYTHONPATH=. This emits diagnostic evidence;
it never changes whole-replay acceptance or repairs a timestamp.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

from vg.core.native_stats import read_native_stats
from vg.core.unified_decoder import _le_to_be
from vg.core.vgr_parser import VGRParser
from vg.core.vgr_records import iter_records


def audit(root: Path, sections: int) -> dict:
    rows = []
    metadata_skipped = 0
    comparisons = 0
    differences = 0
    sync_messages = 0
    for start in sorted(root.rglob('*.0.vgr')):
        first_bytes = start.read_bytes()
        if first_bytes[:4] == bytes.fromhex('00051607'):
            metadata_skipped += 1
            continue
        parsed = VGRParser(str(start), auto_truth=False).parse()
        ids = {_le_to_be(p['entity_id']) for team in ('left', 'right')
               for p in parsed['teams'][team] if p.get('entity_id')}
        prefix = start.stem.rsplit('.', 1)[0]
        frames = []
        previous_stats = {}
        previous_anchor = None
        for index in range(sections):
            path = start.with_name(f'{prefix}.{index}.vgr')
            if not path.exists():
                break
            data = first_bytes if index == 0 else path.read_bytes()
            records = list(iter_records(data))
            anchors = [r for r in records if r.opcode == 0x046f]
            if len(anchors) != 1 or len(anchors[0].payload) != 69:
                raise ValueError(f'{path.name}: unsupported clock anchor layout')
            anchor = anchors[0]
            game = struct.unpack_from('>f', anchor.payload, 64)[0]
            initial = {}
            for rec in records:
                if rec.timestamp != records[0].timestamp:
                    break
                if rec.opcode == 0x03f3 and len(rec.payload) in (746, 750):
                    actor = struct.unpack_from('>I', rec.payload, 8)[0]
                    flag = struct.unpack_from('>I', rec.payload, 326)[0]
                    if actor in ids and flag == 0:
                        initial[actor] = tuple(struct.unpack_from('>f', rec.payload, off)[0]
                                               for off in (298, 302, 306, 310))
            state = read_native_stats([(index, data)], ids)
            end = {p.entity_id: (p.kills, p.deaths, p.assists, p.minion_kills)
                   for p in state.players}
            compared = sorted(previous_stats.keys() & initial.keys())
            changed = [actor for actor in compared if previous_stats[actor] != initial[actor]]
            comparisons += len(compared)
            differences += len(changed)
            sync_count = sum(r.opcode == 0x0451 for r in records)
            sync_messages += sync_count
            times = sorted({r.timestamp for r in records})
            frame = {
                'index': index, 'sha256': hashlib.sha256(data).hexdigest(),
                'record_count': len(records), 'record_first': records[0].timestamp,
                'record_last': records[-1].timestamp, 'anchor_record_time': anchor.timestamp,
                'anchor_game_time': game, 'sync_0451_records': sync_count,
                'first_nonzero_record_time': next((t for t in times if t > 0), None),
                'largest_record_gap': max((b-a for a,b in zip(times, times[1:])), default=0),
                'single_section_state_status': state.status,
                'compared_checkpoint_actors': len(compared),
                'changed_checkpoint_actors': changed,
            }
            if previous_anchor is not None:
                old_record, old_game = previous_anchor
                frame['game_delta'] = game - old_game
                frame['record_delta'] = anchor.timestamp - old_record
                frame['clock_residual'] = frame['game_delta'] - frame['record_delta']
            frames.append(frame)
            previous_anchor = (anchor.timestamp, game)
            previous_stats = end
        rows.append({'replay_start': start.name, 'sections': frames})
    return {
        'schema_version': 'clock_startup_audit.v1',
        'scope': 'diagnostic_startup_only', 'requested_sections': sections,
        'replays': len(rows), 'metadata_skipped': metadata_skipped,
        'sections_checked': sum(len(r['sections']) for r in rows),
        'single_section_state_counts': dict(Counter(f['single_section_state_status']
                                                   for r in rows for f in r['sections'])),
        'compared_checkpoint_actors': comparisons,
        'changed_checkpoint_actors': differences, 'sync_0451_records': sync_messages,
        'note': 'Checkpoint equality is internal consistency, not scoreboard truth or proof of clock correctness.',
        'rows': rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('replay_root', type=Path)
    parser.add_argument('--sections', type=int, default=3,
                        help='Number of initial sections per replay (default: 3)')
    args = parser.parse_args()
    if not args.replay_root.is_dir():
        parser.error('replay_root must be an existing directory')
    if args.sections < 2:
        parser.error('--sections must be at least 2 for a checkpoint comparison')
    result = audit(args.replay_root, args.sections)
    if result['replays'] == 0:
        parser.error('no real replay starts found')
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
