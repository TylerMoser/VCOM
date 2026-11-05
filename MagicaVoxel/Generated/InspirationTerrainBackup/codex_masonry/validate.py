import json
from generate import HERE,ROOT,sha,CP,group
from voxlib import read,components
m=json.loads((HERE/'manifest.json').read_text());results=[]
for f in m['families']:
 rows=[r for r in m['models'] if r['family']==f['name']];data={r['style']:read(ROOT/r['file']) for r in rows}
 for r in rows:
  size,v,p,n=data[r['style']];assert sha(ROOT/r['file'])==r['sha256'];assert size==tuple(f['size']) and n==1
  assert len(v)==r['voxels'] and len(components(v))==1
  assert all(0<=q[i]<size[i] for q in v for i in range(3));assert 0 not in v.values() and 255 not in v.values()
  cartoon='Cartoon' in r['style'];base=data['Cartoon' if cartoon else 'Base'][1];assert set(v)==set(base)
  if 'CratePalette' in r['style']:assert p==CP
  if 'TwoColor' in r['style']:
   assert len(set(v.values()))==(2 if f['kind']=='drain' else 1)
   for g in set(map(group,base.values())):assert len({v[q] for q,c in base.items() if group(c)==g})==1
  if cartoon:
   W,D,H=size
   for (x,y,z),c in v.items():
    q=(y,x,z) if f['kind']=='corner' else (W-1-y,x,z) if f['kind']=='pedestal' else (W-1-x,y,z)
    assert v.get(q)==c,(f['name'],q)
  if f['kind']=='drain':
   assert all((9,y,7) not in v for y in range(size[1])), 'Drain gap blocked'
   assert v[7,6,7] is not None
  results.append({'file':r['file'],'pass':True})
 assert data['Base'][1]!=data['Cartoon'][1]
baseline=json.loads((HERE/'prior-hashes.json').read_text());changed=[n for n,h in baseline.items() if not (ROOT/n).exists() or sha(ROOT/n)!=h]
(HERE/'validation-summary.json').write_text(json.dumps(dict(models=len(results),errors=0,warnings=0,checks=results,prior_vox=len(baseline),prior_vox_unchanged=len(baseline)-len(changed),concurrent_external_changes=changed),indent=2))
print('PASS',len(results),'models;',len(baseline)-len(changed),'prior files unchanged;',len(changed),'external changes')
