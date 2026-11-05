import json
from generate import HERE,ROOT,sha,CP,group
from voxlib import read,components
m=json.loads((HERE/'manifest.json').read_text());results=[]
for f in m['families']:
 rows=[r for r in m['models'] if r['family']==f['name']];data={r['style']:read(ROOT/r['file']) for r in rows}
 for r in rows:
  size,v,p,n=data[r['style']];assert sha(ROOT/r['file'])==r['sha256'];assert size==tuple(f['size']) and n==1
  assert len(v)==r['voxels'];assert len(components(v))==(1 if f['kind']=='tree' else 2)
  assert all(0<=q[i]<size[i] for q in v for i in range(3));assert all(1<=c<=254 for c in v.values())
  # Every connected component must touch the placement plane.
  left=set(v)
  while left:
   todo=[left.pop()];grounded=False
   while todo:
    x,y,z=todo.pop();grounded|=z==0
    for q in [(x+1,y,z),(x-1,y,z),(x,y+1,z),(x,y-1,z),(x,y,z+1),(x,y,z-1)]:
     if q in left:left.remove(q);todo.append(q)
   assert grounded
  cartoon='Cartoon' in r['style'];base=data['Cartoon' if cartoon else 'Base'][1];assert set(v)==set(base)
  if 'CratePalette' in r['style']:assert p==CP
  if 'TwoColor' in r['style']:
   assert len(set(v.values()))==2
   for g in set(group(c,f['kind']) for c in base.values()):assert len({v[q] for q,c in base.items() if group(c,f['kind'])==g})==1
  if cartoon:
   W,D,H=size
   for (x,y,z),c in v.items():assert v.get((W-1-y,x,z) if f['kind']=='tree' else (W-1-x,y,z))==c
  results.append({'file':r['file'],'pass':True})
 assert set(data['Base'][1])!=set(data['Cartoon'][1])
baseline=json.loads((HERE/'prior-hashes.json').read_text());changed=[n for n,h in baseline.items() if not (ROOT/n).exists() or sha(ROOT/n)!=h]
(HERE/'validation-summary.json').write_text(json.dumps(dict(models=len(results),errors=0,warnings=0,checks=results,prior_vox=len(baseline),prior_vox_unchanged=len(baseline)-len(changed),concurrent_external_changes=changed),indent=2))
print('PASS',len(results),'models;',len(baseline)-len(changed),'prior files unchanged;',len(changed),'external changes')
