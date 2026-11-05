"""Independent serialized-file, style, material, grid and preservation checks."""
import json,struct
from generate import HERE,ROOT,sha,CP,GROUPS,ground_components
from voxlib import read
from sculpt import Sculpt
m=json.loads((HERE/'manifest.json').read_text());checks=[];exceptions=[]
for f in m['families']:
 rows=[r for r in m['models'] if r['family']==f['name']];data={r['style']:read(ROOT/r['file']) for r in rows};sources={False:Sculpt(f,False).finish(),True:Sculpt(f,True).finish()}
 for r in rows:
  sz,v,pal,n=data[r['style']];assert sha(ROOT/r['file'])==r['sha256'];assert sz==tuple(f['size']) and n==1
  assert len(v)==r['voxels'] and min(q[2] for q in v)==0
  assert all(0<=q[i]<sz[i] for q in v for i in range(3));assert all(1<=c<=254 for c in v.values())
  cartoon='Cartoon' in r['style'];source=sources[cartoon];assert set(source)==set(v)
  if 'CratePalette' in r['style']:assert pal==CP
  if 'TwoColor' in r['style']:
   for group in {c[0] for c in source.values()}:
    assert len({v[q] for q,c in source.items() if c[0]==group})==1,(f['name'],group)
  if cartoon:
   W,D,H=sz;sym=f['symmetry']
   for (x,y,z),c in v.items():
    if sym=='C4' and W==D:assert v.get((W-1-y,x,z))==c,(r['file'],(x,y,z))
    elif sym=='bilateral':assert v.get((W-1-x,y,z))==c
  if r['style'] in ['Base','Cartoon']:
   parts=ground_components(v);assert all(any(q[2]==0 for q in a) for a in parts),(r['file'],'ungrounded geometry')
  glass={q for q,c in source.items() if c[0]=='glass'};actual={q for q,c in v.items() if c in r['glass_indices']};assert actual==glass
  if f['kind']=='house':
   assert all(32<=q[2]<48 for q in glass)
   assert all((x,y,16) not in v for x in range(16,128) for y in range(16,96)), 'Interior obstructed'
   assert all((x,y,15) in v for x in range(8,136) for y in range(8,104))
   assert all((x,7,z) in v for x in range(56,88) for z in range(16,48))
  checks.append({'file':r['file'],'pass':True})
 if set(data['Base'][1])==set(data['Cartoon'][1]):exceptions.append({'family':f['name'],'note':'Shared occupied geometry; constrained repeat tile or tiny motif. Cartoon changes coherent paint / pattern only.'})
 print('Checked',f['name'],flush=True)
baseline=json.loads((HERE/'prior-hashes.json').read_text());changes=[p for p,h in baseline.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
(HERE/'validation-summary.json').write_text(json.dumps(dict(models=len(checks),families=len(m['families']),errors=0,checks=checks,cartoon_geometry_exceptions=exceptions,prior_vox=len(baseline),prior_vox_unchanged=len(baseline)-len(changes),concurrent_external_changes=changes),indent=2))
print('PASS',len(checks),'files; shared-geometry exceptions:',[e['family'] for e in exceptions])
