import json,os,zipfile,hashlib
from pathlib import Path
m=json.loads(Path('vg/output/tournament_truth.json').read_text())['matches'][8]
p=Path(m['replay_file']);root=p.parents[3];needle='f7dc84e0-071a-4126-a0da-319ca51a6796'
out={'root':str(root),'needle':needle,'scanned_zips':[],'matching_archives':[],'errors':[]}
for d,ds,fs in os.walk(root):
 for fn in fs:
  if not fn.lower().endswith('.zip'):continue
  ap=Path(d,fn);out['scanned_zips'].append(str(ap.relative_to(root)))
  try:
   with zipfile.ZipFile(ap) as z:
    hits=[n for n in z.namelist() if needle in n]
    if hits:
     archive={'path':str(ap),'members':[]}
     for n in hits:
      dest=p.parent/Path(n).name
      row={'member':n,'current_path':str(dest),'archive_sha256':hashlib.sha256(z.read(n)).hexdigest(),'current_sha256':hashlib.sha256(dest.read_bytes()).hexdigest() if dest.exists() else None}
      row['identical']=row['archive_sha256']==row['current_sha256'];archive['members'].append(row)
     out['matching_archives'].append(archive)
  except Exception as e:out['errors'].append({'path':str(ap),'error':str(e)})
out['summary']={'zips_scanned':len(out['scanned_zips']),'matching_archives':len(out['matching_archives']),'members_compared':sum(len(x['members']) for x in out['matching_archives']),'identical':sum(r['identical'] for x in out['matching_archives'] for r in x['members'])}
print(json.dumps(out,ensure_ascii=True,indent=2))
