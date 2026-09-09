"""Read-only observations of player death actions without nearby counter adds."""

import argparse
from collections import Counter, defaultdict
from collections.abc import Collection, Sequence
from dataclasses import asdict
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

from vg.analysis.event_timeline import _discover_sections
from vg.analysis.native_event_fields import decode_fields
from vg.core.native_stats import inspect_native_clock
from vg.core.vgr_records import iter_records


def _unknown(reason):
    return {'value': None, 'status': reason, 'last_observation': None}


def _is_count(value, signed=False):
    return (value is not None and math.isfinite(value) and value.is_integer()
            and (signed or value >= 0))


def _operation_counts(rows):
    counts = Counter((row['opcode'], row['native_index'], row.get('native_layer'),
                      row['native_operation']) for row in rows)
    return [{'opcode': opcode, 'index': index, 'layer': layer, 'operation': operation,
             'count': count}
            for (opcode, index, layer, operation), count in sorted(
                counts.items(), key=lambda item: (item[0][0], item[0][1],
                                                  -1 if item[0][2] is None else item[0][2], item[0][3]))]


def _pair(actions, increments, method, window_seconds):
    action_edges = defaultdict(list)
    increment_edges = defaultdict(list)
    by_victim = defaultdict(list)
    for increment in increments:
        by_victim[increment['ref0']].append(increment)
    for action in actions:
        for increment in by_victim[action['native_victim_id']]:
            delta = increment['timestamp'] - action['timestamp']
            eligible = (delta == 0 if method == 'exact_timestamp' else
                        increment['seq'] > action['seq'] and 0 < delta <= window_seconds)
            if eligible:
                action_edges[action['seq']].append(increment)
                increment_edges[increment['seq']].append(action)
    pairs = []
    ambiguous_actions = {}
    ambiguous_increments = {}
    for action in actions:
        edges = action_edges[action['seq']]
        if len(edges) == 1 and len(increment_edges[edges[0]['seq']]) == 1:
            increment = edges[0]
            pairs.append({'method': method, 'action': action, 'increment': increment,
                          'record_time_delta': increment['timestamp'] - action['timestamp']})
        elif edges:
            ambiguous_actions[action['seq']] = action
            for increment in edges:
                ambiguous_increments[increment['seq']] = increment
    ambiguity = []
    if ambiguous_actions:
        ambiguity.append({
            'method': method,
            'actions': list(ambiguous_actions.values()),
            'increments': sorted(ambiguous_increments.values(), key=lambda row: row['seq']),
            'edges': [{'action_seq': action_seq, 'increment_seq': increment['seq']}
                      for action_seq in ambiguous_actions
                      for increment in action_edges[action_seq]],
        })
    return (pairs, ambiguity,
            [row for row in actions if not action_edges[row['seq']]],
            [row for row in increments if not increment_edges[row['seq']]])


def audit_counter_gaps(frames: Sequence[tuple[int, bytes]], player_ids: Collection[int],
                       window_seconds: float = 0.1) -> dict:
    """Audit caller-asserted player IDs without asserting completion or final scores.

    Exact timestamp matches are order-independent. The second pass considers only
    subsequent records with a positive record-time delta within the stated window.
    Only isolated one-to-one edges pair; ambiguity is retained instead of guessed.
    Layer-zero arithmetic is an observation of one array, never final scoreboard state.
    """
    if not isinstance(window_seconds, (int, float)) or not math.isfinite(window_seconds) or window_seconds < 0:
        raise ValueError('window_seconds must be finite and nonnegative')
    ids = sorted(set(player_ids))
    if not ids or any(type(entity) is not int or not 0 <= entity < 0xffffffff for entity in ids):
        raise ValueError('player_ids must contain non-sentinel unsigned 32-bit entity IDs')
    numbers = [number for number, _ in frames]
    if any(type(number) is not int or number < 0 for number in numbers) or numbers != sorted(set(numbers)):
        raise ValueError('frames must have unique nonnegative numbers in numeric order')
    wanted = set(ids)
    clock = asdict(inspect_native_clock(frames))
    actions = []
    increments = []
    operations = []
    victim_operations = defaultdict(list)
    snapshots = defaultdict(list)
    transitions = defaultdict(list)
    boundaries = []
    endings = []
    unsupported = []
    sections = []
    states = {entity: _unknown('missing_baseline') for entity in ids}
    before_action = {}
    last_snapshot = None
    eof = None
    seq = 0

    def issue(row, reason, entity=None):
        unsupported.append({**row, 'reason': reason, 'entity_id': entity})

    def invalidate(entity, reason):
        for target in ids if entity is None else (entity,):
            states[target] = _unknown(reason)

    for number, data in frames:
        record_count = 0
        for record in iter_records(data):
            row = {'seq': seq, 'frame': number, 'offset': record.offset,
                   'timestamp': record.timestamp, 'opcode': record.opcode}
            seq += 1
            record_count += 1
            eof = row
            payload = record.payload
            if record.opcode == 0x048d:
                boundaries.append({**row, 'payload_length': len(payload)})
                continue
            if record.opcode == 0x03f3:
                entity = struct.unpack_from('>I', payload, 8)[0] if len(payload) >= 12 else None
                if entity is not None and entity not in wanted:
                    continue
                if len(payload) not in (746, 750):
                    issue(row, 'unsupported_snapshot_length', entity)
                    invalidate(entity, 'unsupported_snapshot')
                    continue
                deaths = struct.unpack_from('>f', payload, 302)[0]
                layer = struct.unpack_from('>I', payload, 326)[0]
                snapshot = {**row, 'entity_id': entity, 'layer': layer,
                            'deaths': deaths if math.isfinite(deaths) else None,
                            'deaths_bits': struct.unpack_from('>I', payload, 302)[0],
                            'payload_length': len(payload)}
                snapshots[entity].append(snapshot)
                last_snapshot = snapshot
                if not _is_count(deaths):
                    issue(row, 'unsupported_snapshot_death_value', entity)
                if layer == 0:
                    states[entity] = ({'value': int(deaths), 'status': 'observed_layer0_only',
                                       'last_observation': row} if _is_count(deaths) else
                                      _unknown('unsupported_snapshot_death_value'))
                continue
            if record.opcode not in (0x041c, 0x041d, 0x0430, 0x03f1, 0x0431):
                continue
            fields = decode_fields(record)
            entity = struct.unpack_from('>I', payload, 0)[0] if len(payload) >= 4 else None
            if fields['decoding_status'] != 'decoded':
                if record.opcode == 0x03f1 or entity is None or entity in wanted:
                    issue({**row, 'content_length': record.content_length},
                          fields['decoding_status'], entity)
                    if record.opcode == 0x041c:
                        invalidate(entity, 'unsupported_stat_operation')
                continue
            row = {**row, **fields}
            if record.opcode == 0x03f1:
                endings.append(row)
                continue
            if entity not in wanted:
                continue
            if record.opcode == 0x0430:
                actions.append(row)
                before_action[row['seq']] = dict(states[entity])
            elif record.opcode == 0x0431:
                transitions[entity].append(row)
            else:
                victim_operations[entity].append(row)
                index = row['native_index']
                relevant = index in ((41, 42) if record.opcode == 0x041c else (11, 14))
                if relevant:
                    operations.append(row)
                if row['value'] is None or (relevant and not _is_count(row['value'], signed=True)):
                    issue(row, 'unsupported_stat_value', entity)
                if record.opcode == 0x041c and relevant and row['native_layer'] != 0:
                    issue(row, 'nonzero_attribute_layer_not_scoreboard_interpreted', entity)
                if record.opcode == 0x041c and index == 42 and row['native_layer'] == 0:
                    if row['native_operation'] == 'add' and row['value'] == 1:
                        increments.append(row)
                    previous = states[entity]['value']
                    value = row['value']
                    if not _is_count(value, signed=True):
                        states[entity] = _unknown('unsupported_stat_value')
                    elif row['native_operation'] == 'add' and previous is None:
                        states[entity] = _unknown('missing_or_invalid_baseline')
                    else:
                        updated = int(value) + previous if row['native_operation'] == 'add' else int(value)
                        states[entity] = ({'value': updated, 'status': 'observed_layer0_only',
                                           'last_observation': row} if updated >= 0 else
                                          _unknown('negative_value_requires_unproved_clamp'))
        sections.append({'number': number, 'sha256': hashlib.sha256(data).hexdigest(),
                         'bytes': len(data), 'record_count': record_count})

    exact, exact_ambiguity, remaining_actions, remaining_increments = _pair(
        actions, increments, 'exact_timestamp', window_seconds)
    delayed, delayed_ambiguity, missing, unmatched = _pair(
        remaining_actions, remaining_increments, 'forward_record_time_window', window_seconds)
    ambiguities = exact_ambiguity + delayed_ambiguity
    cases = []
    for action in missing:
        entity = action['native_victim_id']
        position = action['seq']
        prior = next((row for row in reversed(operations) if row['seq'] < position), None)
        later_ops = [row for row in operations if row['seq'] > position]
        later_victim_ops = [row for row in victim_operations[entity] if row['seq'] > position]
        cases.append({
            'action': action,
            'latest_prior_player_kda_cs_operation': prior,
            'later_player_kda_cs_operation_count': len(later_ops),
            'later_player_kda_cs_operation_counts': _operation_counts(later_ops),
            'later_victim_snapshots': [row for row in snapshots[entity] if row['seq'] > position],
            'later_victim_stat_operation_counts': _operation_counts(later_victim_ops),
            'later_0431': [row for row in transitions[entity] if row['seq'] > position],
            'next_048d': next((row for row in boundaries if row['seq'] > position), None),
            'next_03f1': next((row for row in endings if row['seq'] > position), None),
            'eof': eof,
            'pre_layer0_deaths': before_action[position],
            'eof_layer0_deaths': states[entity],
            'later_unsupported_semantic_count': sum(row['seq'] > position for row in unsupported),
        })
    return {
        'schema_version': 1,
        'scope': 'recorded_counter_gap_observations',
        'interpretation': ('Caller asserts player identities. Window matches are a heuristic, not causal proof. '
                           'Record order and record timestamps are reported separately; clock validity is unchanged. '
                           'Layer-zero death values describe observed assignments and arithmetic only; '
                           'other layers, native final scores and match completion are not established. '
                           '0x048d is an opaque positional anchor.'),
        'players': ids, 'window_seconds': window_seconds, 'clock': clock,
        'sections': sections, 'record_count': seq,
        'counts': {'player_actor_die': len(actions), 'death_add_one': len(increments),
                   'exact_pairs': len(exact), 'window_pairs': len(delayed),
                   'unmatched_actions': len(missing), 'unmatched_increments': len(unmatched),
                   'ambiguous_actions': sum(len(group['actions']) for group in ambiguities),
                   'ambiguous_increments': sum(len(group['increments']) for group in ambiguities),
                   'unsupported_semantics': len(unsupported)},
        'pairs': exact + delayed, 'cases': cases,
        'unmatched_increments': unmatched, 'ambiguities': ambiguities,
        'unsupported_semantics': unsupported,
        'boundaries_048d': boundaries, 'end_match_actions': endings,
        'last_player_kda_cs_operation': operations[-1] if operations else None,
        'last_player_snapshot': last_snapshot, 'eof': eof,
    }


def _player(value):
    try:
        result = int(value, 0)
    except ValueError as error:
        raise argparse.ArgumentTypeError('player must be an integer entity ID') from error
    if not 0 <= result < 0xffffffff:
        raise argparse.ArgumentTypeError('player must be a non-sentinel unsigned 32-bit entity ID')
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Audit recorded player death counter gaps; no final-score inference.')
    parser.add_argument('path', type=Path, help='numbered .vgr section; reads all matching sections in numeric order')
    parser.add_argument('--player', required=True, action='append', type=_player,
                        help='caller-asserted player entity ID; repeat for every player')
    parser.add_argument('--window-seconds', type=float, default=0.1,
                        help='nonnegative finite forward record-time matching window (default: 0.1)')
    args = parser.parse_args(argv)
    try:
        frames = [(number, path.read_bytes()) for number, path in _discover_sections(args.path)]
        report = audit_counter_gaps(frames, args.player, args.window_seconds)
        result = json.dumps(report, ensure_ascii=False, allow_nan=False)
    except (OSError, ValueError) as error:
        print(f'terminal-counter-audit: {error}', file=sys.stderr)
        return 2
    print(result)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
