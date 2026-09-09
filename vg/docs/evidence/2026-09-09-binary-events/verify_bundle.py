"""Check publication consistency without the private executable or replay corpus."""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import sys

STEM = 'vg-binary-event-candidates-2026-09-09'
PREFIX = 'evidence/2026-09-09-binary-events/'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(docs):
    evidence = docs / PREFIX
    def read(path):
        return json.loads(path.read_text(encoding='utf-8'))
    manifest = read(evidence / 'manifest.json')
    for name, expected in manifest['distributed_sha256'].items():
        path = (docs / name).resolve()
        require(path.is_relative_to(docs.resolve()), 'manifest path leaves docs: ' + name)
        require(sha(path) == expected, 'distributed hash mismatch: ' + name)
    catalog = read(docs / (STEM + '.json'))
    source = read(evidence / 'source-branches.json')
    census = read(evidence / 'corpus/opcode-summary.json')
    provenance = read(evidence / 'corpus/provenance.json')
    emitters = read(evidence / 'native/packet-emitters.json')
    native = read(evidence / 'native/native-inventory.json')
    coverage = catalog['coverage']
    candidates = {r['opcode']: r for r in catalog['candidates']}
    require(len(candidates) == len(catalog['candidates']) == 161, 'candidate IDs/count')
    receiver = {'0x' + r['opcode'] for r in source['rows']}
    machine = {'0x' + r['opcode'] for r in coverage['jump_table'] if not r['default_target']}
    machine.update('0x' + r['opcode'] for r in coverage['low_branch_handlers'])
    emitted = {'0x' + r['opcode'] for r in emitters['rows']}
    require(receiver == machine and len(receiver) == 123, 'receiver coverage')
    require(not coverage['case_machine_symmetric_difference'], 'source/machine mismatch')
    require(len(emitted) == len(emitters['rows']) == 111, 'formatter coverage')
    require(set(candidates) == receiver | emitted | set(census), 'candidate union')
    require(len(census) == 85 and len(set(census) - receiver) == 12, 'observed coverage')
    require(len(receiver - set(census)) == 50, 'unobserved receiver coverage')
    require(len(catalog['native_candidates']) == len(native['vtables']) == 147, 'native count')
    require(len(catalog['unclassified_conversion_references']) == 22, 'unclassified count')
    require(sum(r['record_count'] for r in census.values()) == 30729156, 'record total')
    require(len(provenance['rows']) == 56, 'recording count')
    require(sum(r['section_count'] for r in provenance['rows']) == 7870, 'section total')
    require(sum(r['record_count'] for r in provenance['rows']) == 30729156, 'provenance record total')
    for opcode, observed in census.items():
        require(candidates[opcode]['observed'] == observed, 'candidate observation: ' + opcode)
        require(sum(observed['payload_length_histogram'].values()) == observed['record_count'], 'length histogram: ' + opcode)
        require(sum(observed['recording_counts'].values()) == observed['record_count'], 'recording counts: ' + opcode)
    for row in source['rows']:
        require(sha(evidence / row['snippet']) == row['body_sha256'], 'branch body: ' + row['opcode'])
        candidate = candidates['0x' + row['opcode']]
        require(candidate['branch_evidence'] == {**row, 'snippet': PREFIX + row['snippet']}, 'branch metadata: ' + row['opcode'])
    for name, expected in catalog['source_hashes'].items():
        require(sha(docs / name) == expected, 'source hash: ' + name)
    for row in candidates.values():
        require(row['validation_plan_id'] in catalog['validation_plans'], 'validation plan: ' + row['opcode'])
        for field in ('unresolved', 'offline_next', 'runtime_scenario', 'negative_control', 'pass_criterion'):
            require(bool(row[field]), 'missing ' + field + ': ' + row['opcode'])
    with (docs / (STEM + '.csv')).open(encoding='utf-8-sig', newline='') as handle:
        csv_rows = list(csv.DictReader(handle))
    require(len(csv_rows) == 161 and {r['opcode'] for r in csv_rows} == set(candidates), 'CSV opcode coverage')
    for row in csv_rows:
        candidate = candidates[row['opcode']]
        require(row['candidate'] == candidate['candidate'], 'CSV name: ' + row['opcode'])
        require(int(row['record_count']) == (candidate['observed'] or {}).get('record_count', 0), 'CSV record count: ' + row['opcode'])
        for field in ('unresolved', 'offline_next', 'runtime_scenario', 'negative_control', 'pass_criterion'):
            require(row[field] == candidate[field], 'CSV ' + field + ': ' + row['opcode'])
    with (docs / (STEM + '-native.csv')).open(encoding='utf-8-sig', newline='') as handle:
        native_rows = list(csv.DictReader(handle))
    require(len(native_rows) == 147, 'native CSV count')
    require({r['vtable'] for r in native_rows} == {r['vtable'] for r in catalog['native_candidates']}, 'native CSV coverage')
    return {'verdict': 'PASS', 'distributed_files': len(manifest['distributed_sha256']), 'candidate_opcodes': len(candidates), 'native_candidates': len(native_rows), 'branch_hashes': len(source['rows']), 'records': 30729156, 'scope': 'Publication consistency only; native and gameplay experiments were not rerun.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--docs', type=Path, default=Path(__file__).resolve().parents[2], help='vg/docs directory containing the published snapshot')
    args = parser.parse_args()
    try:
        result = verify(args.docs)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print('verification failed: ' + str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
