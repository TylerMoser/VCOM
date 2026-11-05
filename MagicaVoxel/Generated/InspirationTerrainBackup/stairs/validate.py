"""Independent on-disk geometry, color and staircase route checks."""
import json,sys,hashlib
from pathlib import Path
from voxlib import read,components
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from inspect_vox import inspect
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((HERE/'manifest.json').read_text());audits=[];results=[]
for f in m['families']:
 rows=[r for r in m['models'] if r['family']==f['name']];assert len(rows)==7
 geometry={};groupmap={};g={int(k):v for k,v in f['semantic_groups'].items()}
 for style in ['Base','Cartoon']:
  row=next(r for r in rows if r['style']==style);size,v,p,n=read(ROOT/row['file']);L,W,H=size
  assert len(components(v))==1
  geometry[style]=set(v);groupmap[style]={q:g[c] for q,c in v.items()}
  if style=='Cartoon':assert all(v.get((x,W-1-y,z))==c for (x,y,z),c in v.items())
  # Highest occupied surface through the middle is an unbroken stair profile.
  heights=[max(z for z in range(H) if (x,W//2,z) in v)+1 for x in range(L)]
  if f.get('kind')=='platform':
   assert all(h==32 for h in heights[5:80])
   assert all(0<=heights[x]-heights[x+1]<=5 for x in range(79,L-1))
  else:
   assert all(0<=b-a<=6 for a,b in zip(heights,heights[1:]))
   assert heights[-1]==f['rise'] and len(set(heights))==f['steps']
   assert all(h==f['rise'] for h in heights[-f['landing']:])
   if f.get('midlanding'):assert all(h==f['rise']//2 for h in heights[f['run']//2:f['run']//2+f['midlanding']])
   # A clear central corridor; curbs cannot encroach on its walking surface.
   for x,h in enumerate(heights):
    for y in range(W//2-8,W//2+8):
     assert (x,y,h-1) in v and all((x,y,z) not in v for z in range(h,H))
 assert geometry['Base']!=geometry['Cartoon']
 for row in rows:
  path=ROOT/row['file'];assert sha(path)==row['sha256'];size,v,p,n=read(path)
  a=inspect(path);assert not a['warnings'];assert n==1 and max(size)<=256
  assert min(q[2] for q in v)==0 and not {0,255}&set(v.values())
  authority='Cartoon' if 'Cartoon' in row['style'] else 'Base';assert set(v)==geometry[authority]
  assert all(all(0<=q[i]<size[i] for i in range(3)) for q in v)
  if 'CratePalette' in row['style']:assert a['palette_sha256']==m['palette_sha256']
  if 'TwoColor' in row['style']:
   used={}
   for q,c in v.items():used.setdefault(groupmap[authority][q],set()).add(c)
   assert all(len(indices)==1 for indices in used.values())
  audits.append(a)
 results.append(dict(family=f['name'],connected=True,seven_styles=True,geometry_inheritance=True,cartoon_bilateral_geometry_and_paint=True,stair_profile=True,flat_semantic_groups=True))
 print('Validated',f['name'],flush=True)
baseline=json.loads((HERE/'preserved-hashes.json').read_text());assert all(sha(ROOT/p)==h for p,h in baseline.items())
(HERE/'structural-audit.json').write_text(json.dumps(audits,indent=2))
(HERE/'validation-summary.json').write_text(json.dumps(dict(models=len(audits),errors=0,warnings=0,preserved_prior_vox=len(baseline),families=results),indent=2))
print('PASS',len(audits),'preserved',len(baseline))
