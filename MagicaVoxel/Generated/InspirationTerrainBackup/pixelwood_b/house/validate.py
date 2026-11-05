"""Serialized cabin invariants; runtime evidence is import/render only."""
from generate import HERE,ROOT,WORK,read,components,SIZE
from pathlib import Path
import hashlib,json
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((HERE/'manifest.json').read_text());a=json.loads((HERE/'structural-audit.json').read_text());g=json.loads((HERE/'godot-validation.json').read_text())
assert len(m['models'])==len(a)==len(g)==7
assert h(HERE/'generate.py')==m['generator_sha256'] and h(WORK/m['source_image'])==m['source_sha256']
for p,sha in m['dependencies'].items():assert h(HERE/p)==sha
assert not any(r.get('errors') or r.get('warnings') for r in a)
audit={Path(r['path']).name:r for r in a}
for r in m['models']:
 p=ROOT/r['file'];size,v,pal=read(p);ss,src,_=read(ROOT/r['geometry_source'])
 assert h(p)==r['sha256']==audit[p.name]['sha256']
 assert size==ss==SIZE and v.keys()==src.keys() and len(components(v))==1
 assert len(v)==r['voxels']==g[p.name]['voxels'] and g[p.name]['grounded']
 assert (HERE/'previews'/p.with_suffix('.png').name).exists()
 assert 255 not in v.values() and min(q[2] for q in v)==0 and max(q[2] for q in v)==79
 assert (40,40,20) not in v and (40,40,5) in v # hollow room and floor
 assert (23,12,15) in v # closed offset door
 assert (50,12,19) in v and (36,10,47) in v # glazing
 assert all((x,y,z) not in v for x in range(17,22) for y in range(52,57) for z in range(73,80))
 if r['style']=='Cartoon':
  # Roof alone is symmetric away from the intentional left chimney.
  assert all(v.get((79-x,y,z))==col for (x,y,z),col in v.items() if 7<=col<=12 and y<40)
 if 'TwoColor' in r['style']:
  assert len(set(v.values()))==len({pal[c-1] for c in v.values()})==2
  wood={v[q] for q,c in src.items() if c<=6};acc={v[q] for q,c in src.items() if c>=7}
  assert len(wood)==len(acc)==1 and wood!=acc
 if 'CratePalette' in r['style']:assert hashlib.sha256(b''.join(bytes(c) for c in pal)).hexdigest()==m['palette_sha256']
for name,sha in json.loads((HERE/'preserved-tree-hashes.json').read_text()).items():assert h(ROOT/name)==sha
print('PASS: seven house files, palettes, semantic recolors, hollow room, door/windows, open flue, roof balance, render counts and 28 preserved tree models.')
