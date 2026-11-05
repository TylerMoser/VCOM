"""Serialized tent geometry/material checks and evidence verification."""
from generate import HERE,ROOT,WORK,read,components,build,SIZE
import json,hashlib
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((HERE/'manifest.json').read_text());a=json.loads((HERE/'structural-audit.json').read_text());g=json.loads((HERE/'godot-validation.json').read_text())
assert len(m['models'])==len(a)==len(g)==7
assert h(HERE/'generate.py')==m['generator_sha256'] and h(WORK/m['source_image'])==m['source_sha256']
assert not any(r.get('errors') or r.get('warnings') for r in a)
audit={__import__('pathlib').Path(r['path']).name:r for r in a}
for r in m['models']:
 p=ROOT/r['file'];size,v,pal=read(p);ss,src,_=read(ROOT/r['geometry_source'])
 assert h(p)==r['sha256']==audit[p.name]['sha256']
 assert size==ss==SIZE and v.keys()==src.keys() and len(components(v))==1
 assert len(v)==g[p.name]['voxels']==r['voxels'] and g[p.name]['grounded']
 assert (HERE/'previews'/p.with_suffix('.png').name).exists()
 assert 255 not in v.values() and min(q[2] for q in v)==0 and max(q[2] for q in v)==31
 # Open doorway and usable hollow room above the floor; closed rear wall.
 assert all((x,y,1) not in v for x in range(25,39) for y in range(4,57))
 assert all((31,y,10) not in v for y in range(4,57))
 assert (31,58,10) in v and (31,30,0) in v
 # Side vents remain actual holes through their sloping canvas panels.
 assert all((x,y,round(29*(1-abs(x-31.5)/27.5))) not in v for x in [17,46] for y in range(26,35))
 if 'Cartoon' in r['style']:assert all(v.get((63-x,y,z))==col for (x,y,z),col in v.items())
 if 'TwoColor' in r['style']:
  assert len(set(v.values()))==len({pal[c-1] for c in v.values()})==2
  groups=[{v[q] for q,c in src.items() if c<=6},{v[q] for q,c in src.items() if c>=7}]
  assert all(len(s)==1 for s in groups) and groups[0]!=groups[1]
 if 'CratePalette' in r['style']:assert hashlib.sha256(b''.join(bytes(c) for c in pal)).hexdigest()==m['palette_sha256']
for name,sha in json.loads((HERE/'preserved-tree-hashes.json').read_text()).items():assert h(ROOT/name)==sha
print('PASS: seven tent files; geometry, materials, symmetry, doorway, room, vents, import evidence, palettes and all 28 original tree files.')
