"""Read saved art independently; check open caves, connected falling sheets and variants."""
from pathlib import Path
import json,hashlib,sys
from voxlib import read,components
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from inspect_vox import inspect
GROUP={i:(1 if i<=7 else 8 if i<=11 else 12) for i in range(1,16)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((HERE/'manifest.json').read_text());audits=[];checks=[]
for f in m['families']:
 rows=[r for r in m['models'] if r['family']==f['name']];assert len(rows)==7
 geometries={};groups={}
 for style in ['Base','Cartoon']:
  row=next(r for r in rows if r['style']==style);size,v,p,n=read(ROOT/row['file']);W,D,H=size
  assert len(components(v))==1
  geometries[style]=set(v);groups[style]={q:GROUP[c] for q,c in v.items()}
  if style=='Cartoon':assert all(v.get((W-1-x,y,z))==c for (x,y,z),c in v.items())
  if f['kind']=='cave':
   # An actual traversing air corridor, not a black painted facade or sealed alcove.
   for x in range(W//2-8,W//2+8):
    for y in range(D):
     assert (x,y,1) in v
     assert all((x,y,z) not in v for z in range(2,min(24,f['opening'][1]-8)))
   assert any(z>f['opening'][1] for x,y,z in v if x==W//2)
  else:
   # Each central column has a continuous sheet over the full declared drop.
   for x in range(8,W-8):
    for z in range(4,f['drop']+4):assert any((x,y,z) in v for y in range(D))
   assert {1}==set(GROUP[c] for c in v.values())
 assert geometries['Base']!=geometries['Cartoon']
 for row in rows:
  path=ROOT/row['file'];assert sha(path)==row['sha256'];size,v,p,n=read(path);a=inspect(path)
  assert not a['warnings'] and n==1 and all(0<s<=256 for s in size)
  assert all(all(0<=q[i]<size[i] for i in range(3)) for q in v)
  assert min(q[2] for q in v)==0 and not ({0,255}&set(v.values()))
  source='Cartoon' if 'Cartoon' in row['style'] else 'Base';assert set(v)==geometries[source]
  if 'CratePalette' in row['style']:assert a['palette_sha256']==m['palette_sha256']
  if 'TwoColor' in row['style']:
   bygroup={}
   for q,c in v.items():bygroup.setdefault(groups[source][q],set()).add(c)
   assert all(len(cs)==1 for cs in bygroup.values())
  audits.append(a)
 checks.append(dict(family=f['name'],seven_styles=True,connected=True,color_only_geometry_exact=True,cartoon_bilateral_geometry_and_paint=True,open_air_tunnel=f['kind']=='cave',continuous_water_sheet=f['kind']=='waterfall'))
 print('Validated',f['name'],flush=True)
baseline=json.loads((HERE/'prior-hashes.json').read_text());changes=[]
for name,h in baseline.items():
 p=ROOT/name
 if not p.exists() or sha(p)!=h:changes.append(name)
# Another authorized author may change their own files. Report that; never restore them.
(HERE/'structural-audit.json').write_text(json.dumps(audits,indent=2))
(HERE/'validation-summary.json').write_text(json.dumps(dict(models=len(audits),errors=0,warnings=0,prior_vox=len(baseline),prior_vox_unchanged=len(baseline)-len(changes),concurrent_external_changes=changes,families=checks),indent=2))
print('PASS',len(audits),'prior unchanged',len(baseline)-len(changes),'external changes',len(changes))
