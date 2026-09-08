import hashlib,json,subprocess
from pathlib import Path
p=Path('.superpowers/sdd/2026-09-07-mismatch/probe.json')
checked=0
for m in json.loads(p.read_text()):
 source=Path(m['replay']);prefix=source.stem.rsplit('.',1)[0]
 for f in m['files']:
  actual=source.parent/f'{prefix}.{f["frame"]}.vgr'
  assert hashlib.sha256(actual.read_bytes()).hexdigest()==f['sha256'],str(actual)
  checked+=1
print(json.dumps({'status':'PASS','replay_files_unchanged':checked,'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}))
