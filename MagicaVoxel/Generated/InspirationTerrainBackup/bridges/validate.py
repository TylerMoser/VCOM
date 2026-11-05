"""Validate final bridge files independently, including complete multi-model scenes."""
from pathlib import Path
import json,hashlib,sys
from voxlib import read,components
from generate import Sculpt,GROUP,ROOT,HERE
sys.path.insert(0,str(ROOT/'tools'))
from inspect_vox import inspect
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((HERE/'manifest.json').read_text());audits=[];families=[]
(HERE/'qa/expected').mkdir(parents=True,exist_ok=True)
for f in m['families']:
 rows=[r for r in m['models'] if r['family']==f['name']];assert len(rows)==7
 geometry={};groupmap={}
 for style in ['Base','Cartoon']:
  row=next(r for r in rows if r['style']==style);size,v,p,n=read(ROOT/row['file']);assert len(components(v))==1
  geometry[style]=set(v);groupmap[style]={q:GROUP[c] for q,c in v.items()};L,D,H=size
  if style=='Cartoon':assert all(v.get((x,D-1-y,z))==c for (x,y,z),c in v.items()),f['name']
  # Deck is actually present across the full intended crossing, except explicit plank gaps.
  a=f.get('approach',0);s=Sculpt(f,style=='Cartoon')
  for x in range(a,L-a):
   if f['kind']=='wood' and (x-a)%f.get('slats',8)>=f.get('slats',8)-f.get('gap',0):continue
   assert (x,D//2,s.height(x)-1) in v,(f['name'],'deck gap',x)
  if f['kind']=='stone':
   for l,r in zip(f['bays'],f['bays'][1:]):
    cx=(l+r)//2
    assert all((cx,y,1) not in v for y in range(4,D-4)),(f['name'],'blocked arch')
 assert geometry['Base']!=geometry['Cartoon']
 for row in rows:
  path=ROOT/row['file'];assert sha(path)==row['sha256'];size,v,p,n=read(path)
  a=inspect(path);assert not a['warnings'];assert len(a['models'])==n==row['scene_models']
  assert all(max(model['size'])<=256 for model in a['models'])
  assert min(z for x,y,z in v)==0 and 255 not in v.values() and 0 not in v.values()
  authority='Cartoon' if 'Cartoon' in row['style'] else 'Base';assert set(v)==geometry[authority]
  if 'CratePalette' in row['style']:assert a['palette_sha256']==m['palette_sha256']
  if 'TwoColor' in row['style']:
   used={}
   for q,c in v.items():used.setdefault(groupmap[authority][q],set()).add(c)
   assert all(len(indices)==1 for indices in used.values())
  if n>1:
   # Current Godot reader checks every global coordinate and color, not just bounds.
   L,D,H=size;expected=bytearray(L*D*H)
   for (x,y,z),c in v.items():expected[(x*D+y)*H+z]=c
   (HERE/'qa/expected'/(path.stem+'.bin')).write_bytes(expected)
  audits.append(a)
 families.append({'family':f['name'],'seven_variants':True,'connected':True,'clear_arches':True if f['kind']=='stone' else None,'deck_continuity':'intentional plank gaps' if f.get('gap') else 'pass','cartoon_bilateral_geometry_and_paint':True,'color_only_geometry_exact':True})
 print('Validated',f['name'],flush=True)
baseline=json.loads((HERE/'preserved-hashes.json').read_text());assert all(sha(ROOT/p)==h for p,h in baseline.items())
(HERE/'structural-audit.json').write_text(json.dumps(audits,indent=2))
(HERE/'validation-summary.json').write_text(json.dumps({'models':len(audits),'errors':0,'warnings':0,'preserved_prior_vox':len(baseline),'families':families},indent=2))
print('PASS',len(audits),'preserved',len(baseline))
