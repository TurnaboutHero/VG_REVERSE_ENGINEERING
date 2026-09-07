import json,struct,math
from pathlib import Path
from collections import defaultdict
from vg.core.vgr_records import iter_records
ms=json.loads(Path('vg/output/tournament_truth.json').read_text(encoding='utf-8'))['matches'];out=[]
for mi in range(1,len(ms)+1):
 p=Path(ms[mi-1]['replay_file']);samples=defaultdict(list);markers=[];files=[]
 for f in sorted(p.parent.glob(p.stem.rsplit('.',1)[0]+'.*.vgr'),key=lambda f:int(f.stem.rsplit('.',1)[1])):
  frame=int(f.stem.rsplit('.',1)[1]);seen=defaultdict(int);files.append(dict(frame=frame,mtime=f.stat().st_mtime,size=f.stat().st_size))
  for r in iter_records(f.read_bytes()):
   if r.opcode in (0x046f,0x0470,0x0471,0x03f3):markers.append(dict(frame=frame,offset=r.offset,time=r.timestamp,op=f'{r.opcode:04x}',hex=r.payload.hex()))
   key=(r.opcode,len(r.payload));seen[key]+=1
   if len(r.payload)<=80 and seen[key]<=2:samples[key].append((r.timestamp,bytes(r.payload)))
 candidates=[]
 for (op,n),ss in samples.items():
  if len(ss)<20 or ss[-1][0]-ss[0][0]<30:continue
  for off in range(n-3):
   vs=[struct.unpack_from('>f',b,off)[0] for t,b in ss]
   if not all(math.isfinite(v) and -100<=v<=10000 for v in vs):continue
   ds=[v-t for v,(t,b) in zip(vs,ss)]
   if max(ds)-min(ds)<3:candidates.append(dict(op=f'{op:04x}',length=n,offset=off,min_delta=min(ds),max_delta=max(ds),samples=[dict(record_time=t,value=v,delta=v-t) for (t,b),v in zip(ss,vs)]))
 out.append(dict(match=mi,markers=markers,files=files,candidates=candidates))
Path('.superpowers/sdd/2026-09-07-mismatch/clocks.json').write_text(json.dumps(out,indent=2))
print([(m['match'],[(c['op'],c['offset'],c['min_delta'],c['max_delta']) for c in m['candidates']]) for m in out])
