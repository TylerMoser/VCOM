"""Verify delivered files against saved audit/render evidence; does not perform visual review."""
from pathlib import Path
import json,hashlib,re
from voxlib import read,components
R=Path(__file__).resolve().parent
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((R/'manifest.json').read_text());g=json.loads((R/'godot-validation.json').read_text());a=json.loads((R/'structural-audit.json').read_text())
assert len(m['models'])==len(g)==len(a)==14 and len(m['families'])==2
assert h(R.parent.parent/m['source_image'])==m['source_sha256']
for f,k in [('generate.py','generator_sha256'),('sculpt.py','sculpt_sha256')]:assert h(R/f)==m[k]
for f,sha in m['geometry_dependencies'].items():assert h(R/f)==sha
assert not any(t.get('errors') or t.get('warnings') for t in a)
audit={Path(t['path']).name:t for t in a}
for t in m['models']:
 p=R/t['file'];assert h(p)==t['sha256']==audit[p.name]['sha256']
 assert (R/'previews'/p.with_suffix('.png').name).exists()
 size,v,pal=read(p);ss,src,sp=read(R/t['geometry_source'])
 assert size==ss and v.keys()==src.keys() and len(v)==t['voxels']==g[p.name]['voxels']
 assert len(components(v))==1 and g[p.name]['grounded'] and g[p.name]['reader_import']=='pass'
 assert 255 not in v.values() and min(q[2] for q in v)==0
 if 'TwoColor' in t['style']:
  assert len(set(v.values()))==len({pal[c-1] for c in v.values()})==2
  leaves={v[pos] for pos,c in src.items() if c<=6 or c>=10};wood={v[pos] for pos,c in src.items() if 7<=c<=9}
  assert len(leaves)==len(wood)==1 and leaves!=wood
 if 'Cartoon' in t['style']:assert all(v.get((size[0]-1-y,x,z))==c for (x,y,z),c in v.items())
 if 'CratePalette' in t['style']:assert hashlib.sha256(b''.join(bytes(c) for c in pal)).hexdigest()==m['palette_sha256']
for p in [R/'README.md',R/'FILES.md']:
 for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
  if '://' not in link and not link.startswith('#'):assert (p.parent/link.split('#')[0]).exists(),link
print('PASS: 14 serialized models, hashes, audit evidence, palette, geometry, connectivity, C4 symmetry, semantic two-color checks, render counts, previews and catalogue links.')
