import json,struct,hashlib
from pathlib import Path
from collections import Counter,defaultdict
from vg.core.vgr_records import iter_records
from vg.core.vgr_parser import VGRParser
from vg.core.unified_decoder import _le_to_be
truth=json.loads(Path('vg/output/tournament_truth.json').read_text(encoding='utf-8'))['matches']
out=[]
for mi,m in enumerate(truth,1):
 p=Path(m['replay_file']); parsed=VGRParser(str(p),auto_truth=False).parse()
 actors={_le_to_be(a['entity_id']):{'name':a['name'],'team':t,'truth':m['players'].get(a['name'],{})} for t in ('left','right') for a in parsed['teams'][t] if a.get('entity_id')}
 fs=sorted(p.parent.glob(p.stem.rsplit('.',1)[0]+'.*.vgr'),key=lambda f:int(f.stem.rsplit('.',1)[1])); files=[];events=[];last=[];bins=Counter();opcodes=Counter()
 for f in fs:
  data=f.read_bytes(); ts=[];n=0; frame=int(f.stem.rsplit('.',1)[1])
  for r in iter_records(data):
   ts.append(r.timestamp);n+=1;bins[int(r.timestamp//60)]+=1;opcodes[f'{r.opcode:04x}']+=1;b=r.payload;stat=None;layer=None
   if r.opcode==0x041c and r.content_length==24 and b[12] in (41,42):
    stat='kills' if b[12]==41 else 'deaths';v=struct.unpack_from('>f',b,8)[0];layer=b[13];mode=b[14]
   elif r.opcode==0x041d and r.content_length==16 and b[8] in (11,14):
    stat='assists' if b[8]==11 else 'minion_kills';v=struct.unpack_from('>f',b,4)[0];mode=b[9]
   if stat:
    eid=struct.unpack_from('>I',b)[0]
    if eid in actors:events.append(dict(frame=frame,offset=r.offset,time=r.timestamp,ref=eid,stat=stat,value=v,mode=mode,layer=layer,hex=b.hex()))
  files.append(dict(frame=frame,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),records=n,first=ts[0] if ts else None,last=ts[-1] if ts else None,min=min(ts) if ts else None,max=max(ts) if ts else None))
 rows=[];duration=m.get('match_info',{}).get('duration_seconds')
 for ref,a in actors.items():
  for stat in ('kills','deaths','assists','minion_kills'):
   expected=a['truth'].get(stat)
   if expected is None:continue
   es=[e for e in events if e['ref']==ref and e['stat']==stat];s=sum(e['value'] for e in es if e['mode']==0);before=sum(e['value'] for e in es if e['mode']==0 and e['time']<=duration)
   rows.append(dict(ref=ref,name=a['name'],stat=stat,truth=expected,raw=s,before_duration=before,delta=s-expected,after=[e for e in es if e['time']>duration]))
 out.append(dict(match=mi,replay=str(p),image=m['result_image'],info=m.get('match_info'),actors=actors,files=files,minute_records=dict(bins),opcodes=dict(opcodes),rows=rows,events=events))
 print(f'M{mi}: '+str([(r['ref'],r['stat'],r['truth'],r['raw'],r['before_duration']) for r in rows if r['delta']]),flush=True)
Path('.superpowers/sdd/2026-09-07-mismatch/probe.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
