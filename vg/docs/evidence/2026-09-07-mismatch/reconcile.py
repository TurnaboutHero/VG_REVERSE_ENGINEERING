"""Reconcile captured raw evidence without changing replay or truth files.

Input exports come from probe.py and clock_probe.py, which use iter_records.
Clock interpolation is measured from per-frame 046f anchors, not fitted to scores.
Resource14 is compared to the supplied CS label; its native display name is not proved.
"""
import argparse
import json
import struct
from collections import Counter
from pathlib import Path

OFFSETS = {'kills': 298, 'deaths': 302, 'assists': 306, 'minion_kills': 310}


def reconcile(probes, clock_exports):
    assert len(probes) == len(clock_exports)
    out = []
    for match, exported in zip(probes, clock_exports):
        assert match['match'] == exported['match']
        anchors = {}
        snapshots = []
        for row in exported['markers']:
            payload = bytes.fromhex(row['hex'])
            if row['op'] == '046f':
                assert len(payload) == 69
                assert row['frame'] not in anchors
                anchors[row['frame']] = dict(frame=row['frame'], offset=row['offset'], record_time=row['time'], clock_value=struct.unpack_from('>f', payload, 64)[0])
            elif row['op'] == '03f3':
                assert len(payload) in (746, 750)
                ref = struct.unpack_from('>I', payload, 8)[0]
                flag = struct.unpack_from('>I', payload, 326)[0]
                if str(ref) in match['actors'] and flag == 0:
                    snapshots.append(dict(frame=row['frame'], offset=row['offset'], time=row['time'], ref=ref, values={stat:struct.unpack_from('>f', payload, offset)[0] for stat,offset in OFFSETS.items()}))
        assert set(anchors) == {f['frame'] for f in match['files']}
        changes = []
        ordered = sorted(anchors.values(), key=lambda a:a['frame'])
        for before,after in zip(ordered,ordered[1:]):
            clock_delta = after['clock_value'] - before['clock_value']
            record_delta = after['record_time'] - before['record_time']
            if clock_delta < -1 or clock_delta - record_delta > 5:
                changes.append(dict(before=before,after=after,clock_delta=clock_delta,record_delta=record_delta))
        def game_time(row):
            anchor = anchors[row['frame']]
            return anchor['clock_value'] + row['time'] - anchor['record_time']
        def position(row):
            return row['frame'], row['offset']
        def value_at(ref,stat,target,use_initial=True,use_clock=True,latest=False):
            time_of = game_time if use_clock else lambda e:e['time']
            eligible = [s for s in snapshots if s['ref']==ref and time_of(s)<=target]
            baseline = (max if latest else min)(eligible,key=position) if use_initial and eligible else None
            if use_initial and baseline is None:
                return None
            value = baseline['values'][stat] if baseline else 0
            for event in match['events']:
                if event['ref']!=ref or event['stat']!=stat or time_of(event)>target:
                    continue
                if baseline and position(event)<=position(baseline):
                    continue
                assert event['mode']==0 and (event['layer'] in (0,None))
                value += event['value']
            return value
        rows = []
        target = match['info']['duration_seconds']
        for original in match['rows']:
            ref,stat = original['ref'],original['stat']
            initial = min((s for s in snapshots if s['ref']==ref),key=position)['values'][stat]
            row = dict(ref=ref,stat=stat,truth=original['truth'],raw_add_all=original['raw'],initial=initial,
                       initial_plus_all=value_at(ref,stat,float('inf')),
                       clock_only_at_capture=value_at(ref,stat,target,use_initial=False),
                       initial_only_at_record_capture=value_at(ref,stat,target,use_clock=False))
            if changes:
                row.update(status='not_scorable_mixed_clock_epochs',corrected=None)
            else:
                lower=value_at(ref,stat,target)
                upper=value_at(ref,stat,target+0.999999)
                checkpoint_lower=value_at(ref,stat,target,latest=True)
                checkpoint_upper=value_at(ref,stat,target+0.999999,latest=True)
                row.update(corrected=lower,capture_second_end=upper,checkpoint_corrected=checkpoint_lower,
                           checkpoint_second_end=checkpoint_upper,
                           status='stable_match' if lower==upper==checkpoint_lower==checkpoint_upper==original['truth'] else 'inspect')
            rows.append(row)
        initial_states = [{k:s[k] for k in ('ref','frame','offset','values')} for ref in match['actors']
                          for s in [min((s for s in snapshots if s['ref']==int(ref)),key=position)]]
        count=Counter(r['status'] for r in rows)
        out.append(dict(match=match['match'],capture_seconds=target,first_anchor=ordered[0],last_anchor=ordered[-1],
                        clock_discontinuities=changes,initial_states=initial_states,rows=rows,counts=dict(count)))
    summary = Counter()
    for m in out:
        for r in m['rows']:
            group = 'resource14_vs_cs' if r['stat']=='minion_kills' else 'kda'
            summary[f'{group}/{r["status"]}']+=1
            summary[f'{group}/raw_match']+=r['raw_add_all']==r['truth']
            summary[f'{group}/raw_total']+=1
    return dict(summary=dict(summary),matches=out,
                caveat='Observed supplied rows only. In-game screenshots are capture-time targets, not final results. Clock interpolation is an estimate. Mixed-clock inputs are not scored or repaired.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('probe',type=Path)
    parser.add_argument('clocks',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=reconcile(json.loads(args.probe.read_text(encoding='utf-8')),json.loads(args.clocks.read_text(encoding='utf-8')))
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps(result['summary'],indent=2))
    for match in result['matches']:
        print(f"M{match['match']}: {match['counts']}")
        for row in match['rows']:
            if row['status']=='inspect':print(row)

if __name__=='__main__':
    main()
