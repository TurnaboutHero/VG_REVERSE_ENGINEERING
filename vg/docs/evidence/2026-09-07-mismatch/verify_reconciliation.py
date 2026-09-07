import hashlib
import json
from pathlib import Path
from reconcile import reconcile
root=Path(__file__).resolve().parent
probes=json.loads((root/'probe.json').read_text())
clocks=json.loads((root/'clocks.json').read_text())
first=reconcile(probes,clocks)
second=reconcile(probes,clocks)
assert first==second
assert first==json.loads((root/'reconciled.json').read_text())
assert first['summary']['kda/stable_match']==294
assert first['summary']['resource14_vs_cs/stable_match']==78
assert first['summary']['kda/not_scorable_mixed_clock_epochs']==27
assert first['summary']['resource14_vs_cs/not_scorable_mixed_clock_epochs']==9
m5,m6,m9=(first['matches'][i-1] for i in (5,6,9))
def mismatches(m,key):return sum(r[key]!=r['truth'] for r in m['rows'])
assert mismatches(m5,'raw_add_all')==4
assert mismatches(m5,'clock_only_at_capture')==0
assert mismatches(m6,'raw_add_all')==11
assert mismatches(m6,'initial_plus_all')==4
assert mismatches(m6,'clock_only_at_capture')==7
assert mismatches(m6,'corrected')==0
assert len(m9['clock_discontinuities'])==3
assert [(c['before']['frame'],c['after']['frame']) for c in m9['clock_discontinuities']]==[(6,7),(9,10),(32,33)]
assert all(r['corrected'] is None for r in m9['rows'])
assert all(r['status']=='stable_match' for m in first['matches'] if m['match']!=9 for r in m['rows'])
result=dict(status='PASS',repeated_reconciliation_identical=True,
    m5_toggle=dict(raw_mismatches=4,clock_aligned_mismatches=0),
    m6_toggle=dict(raw_mismatches=11,initial_state_only_mismatches=4,clock_only_mismatches=7,both_mismatches=0),
    m9_guard=dict(discontinuities=3,numeric_corrected_scores_emitted=0),
    independent_latest_checkpoint_agreement=True,
    files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'probe.json',root/'clocks.json',root/'reconcile.py',root/'reconciled.json')})
(root/'verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
