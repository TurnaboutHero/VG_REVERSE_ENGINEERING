"""Verify published postgame derivatives, not the private replay corpus or gameplay."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compare(value, marker):
    delta = value - marker
    return 'before' if delta < 0 else 'after' if delta > 0 else 'same'


def verify(base):
    def load(name):
        return json.loads((base / name).read_text(encoding='utf-8'))

    corpus = load('corpus-summary.json')
    locators = load('record-locators.json')
    native = load('native-evidence.json')
    provenance = load('provenance.json')
    rows = corpus['rows']
    by_corpus = {r['corpus']: r for r in rows}
    require(list(by_corpus) == [f'C{i:02}' for i in range(1, 57)], '56 ordered unique corpus rows')
    require(sum(r['sections'] for r in rows) == 7870, 'section count')
    require(sum(r['records'] for r in rows) == 30729156, 'record count')
    require(Counter(r['clock']['status'] for r in rows) == {'accepted': 53, 'unsupported_clock': 2, 'mixed_segments': 1}, 'clock policies preserved')
    markers = {r['corpus']: [m for m in r['markers'] if m['opcode'] == 0x0452] for r in rows}
    require(all(len(m) <= 1 for m in markers.values()), 'no repeated 0452')
    absent = [cid for cid, m in markers.items() if not m]
    require(absent == ['C09', 'C10', 'C33', 'C34', 'C38', 'C41'], 'marker absence set')
    require(all(m['payload_length'] == 6 and m['payload_all_zero'] for group in markers.values() for m in group), 'observed marker payload property')
    all_markers = Counter(m['opcode'] for r in rows for m in r['markers'])
    require(all_markers == {0x03ef: 51, 0x0452: 50}, 'all marker opcode counts')
    totals, relations, matched = Counter(), Counter(), Counter()
    no_marker_score_count = 0
    for r in rows:
        row_score_count = 0
        for c in r['selected_operation_counts']:
            totals[(c['opcode'], c['index'], c['layer'], c['operation'])] += c['count']
            row_score_count += c['count']
        relation_count = sum(c['count'] for c in r['selected_score_relations'])
        if markers[r['corpus']]:
            require(relation_count == row_score_count, 'all score operations classified for marker recording')
        else:
            require(relation_count == 0, 'no relation assigned without marker')
            no_marker_score_count += row_score_count
        for c in r['selected_score_relations']:
            relations[(c['seq_relation'], c['timestamp_relation'])] += c['count']
        for c in r['matched_death_relations_to_0452']:
            matched[(c['seq_relation'], c['timestamp_relation'])] += c['count']
        require(r['unsupported_selected_player_stat_layout_count'] == 0, 'unsupported selected stat layout')
    require(totals == {(0x041c, 41, 0, 'add'): 2192, (0x041c, 42, 0, 'add'): 2182,
                       (0x041d, 11, None, 'add'): 3633, (0x041d, 14, None, 'add'): 46163}, 'score operation totals')
    require(relations == {('before', 'before'): 49748, ('after', 'same'): 14}, 'score relation totals')
    require(no_marker_score_count == 4408, 'score operations without marker')
    require(matched == {('before', 'before'): 2025, ('after', 'same'): 1}, 'matched death relations')
    require(sum(r['unmatched_death_count_after_0452'] for r in rows) == 39, 'unmatched totals')
    unmatched = locators['unmatched_deaths']
    require(len(unmatched) == 39, 'all 39 unmatched locators retained')
    require(len({(c['corpus'], c['action']['seq']) for c in unmatched}) == 39, 'unique unmatched locators')
    for c in unmatched:
        marker = markers[c['corpus']][0]
        require(marker == c['marker'], 'unmatched marker agrees with aggregate')
        action, relation = c['action'], c['relation']
        require(action['seq'] > marker['seq'] and action['timestamp'] > marker['timestamp'], 'unmatched action strictly later in both axes')
        require(action['timestamp'] - marker['timestamp'] == relation['record_time_delta'], 'unmatched time delta')
        require(action['seq'] - marker['seq'] == relation['record_position_delta'], 'unmatched sequence delta')
    same_time = locators['same_timestamp_score_operations_after_marker']
    require(len(same_time) == 14, '14 same-timestamp score locators')
    require(Counter(c['corpus'] for c in same_time) == {'C02': 4, 'C16': 3, 'C28': 3, 'C30': 1, 'C31': 3}, 'same-timestamp case distribution')
    for c in same_time:
        marker = markers[c['corpus']][0]
        require(c['seq'] > marker['seq'] and c['timestamp'] == marker['timestamp'], 'retained counterexample relation')
    boundary_deltas = [c['record_time_delta'] for c in locators['marker_to_048d_relations']]
    require(len(boundary_deltas) == 50, '50 boundary relations')
    require(min(boundary_deltas) == 5.9873046875 and max(boundary_deltas) == 6.1324462890625, 'boundary delta range')
    c16 = {c['seq']: c for c in locators['controls']['C16']['selected_rows']}
    require(all(c16[s]['timestamp'] == c16[717170]['timestamp'] for s in [717171, 717175, 717181, 717185, 717189]), 'C16 same-timestamp batch counterexample')
    require(c16[713091]['snapshot_deaths'] == c16[718184]['snapshot_deaths'] == 7, 'C16 unchanged death snapshot')
    require(locators['controls']['C02']['window_player_deaths'] == 0, 'C02 is not a player-death control')
    key_hash = 0x811c9dc5
    for byte in native['callback_key'].encode('ascii'):
        key_hash = ((key_hash ^ byte) * 0x01000193) & 0xffffffff
    require(f'{key_hash:08x}' == native['callback_key_hash'], 'FNV-1a32 key hash')
    require(native['build_sha256'] == provenance['binary_sha256'], 'native build provenance')
    require(len(provenance['published_files']) == 6, 'all six derivatives have hashes; provenance excludes itself')
    for name, metadata in provenance['published_files'].items():
        path = (base / name).resolve()
        require(path.is_file(), f'missing published file {name}')
        blob = path.read_bytes()
        require(len(blob) == metadata['bytes'], f'file size mismatch: {name}')
        require(hashlib.sha256(blob).hexdigest() == metadata['sha256'], f'file hash mismatch: {name}')
    report = base.parent.parent / 'POSTGAME_OFFLINE_2026-09-09.md'
    for target in re.findall(r'\]\(([^)]+)\)', report.read_text(encoding='utf-8')):
        require(not target.startswith(('/', 'file:', 'http:')), 'portable report links only')
        require((report.parent / target.split('#', 1)[0]).is_file(), f'missing report link {target}')
    return {'status': 'PASS', 'scope': 'published derivative consistency only; no replay rescan or gameplay validation',
            'recordings': len(rows), 'unmatched_locators': len(unmatched), 'same_timestamp_score_locators': len(same_time),
            'selected_score_operations': sum(totals.values()), 'hashed_files': len(provenance['published_files'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-dir', type=Path, default=Path(__file__).resolve().parent,
                        help='Directory containing the published postgame evidence files')
    args = parser.parse_args()
    try:
        print(json.dumps(verify(args.evidence_dir.resolve()), sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'verification failed: {error}\n')


if __name__ == '__main__':
    main()
