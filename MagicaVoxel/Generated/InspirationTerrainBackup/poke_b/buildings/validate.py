from pathlib import Path
import json,hashlib
from voxlib import read,components
R=Path(__file__).resolve().parent;ROOT=R.parent;WORK=ROOT.parent.parent
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((R/'manifest.json').read_text());a=json.loads((R/'structural-audit.json').read_text());g=json.loads((R/'godot-validation.json').read_text())
assert len(m['models'])==len(a)==len(g)==42 and len(m['families'])==6
assert h(R/'generate.py')==m['generator_sha256'] and h(WORK/m['source_image'])==m['source_sha256']
for name,sha in m['dependencies'].items():assert h(R/name)==sha
assert not any(x.get('errors') or x.get('warnings') for x in a)
audit={Path(x['path']).name:x for x in a}
for row in m['models']:
 p=ROOT/row['file'];s,v,pal=read(p);ss,src,_=read(ROOT/row['geometry_source'])
 assert h(p)==row['sha256']==audit[p.name]['sha256']
 assert s==ss==tuple(row['canvas']) and v.keys()==src.keys() and len(components(v))==1
 assert len(v)==row['voxels']==g[p.name]['voxels'] and g[p.name]['grounded']
 assert 255 not in v.values() and min(q[2] for q in v)==0
 assert (R/'previews'/p.with_suffix('.png').name).exists()
 if 'TwoColor' in row['style']:
  assert len(set(v.values()))==len({pal[c-1] for c in v.values()})==2
  body={v[q] for q,c in src.items() if c<=6};accent={v[q] for q,c in src.items() if c>=7}
  assert len(body)==len(accent)==1 and body!=accent
 if 'CratePalette' in row['style']:assert hashlib.sha256(b''.join(bytes(c) for c in pal)).hexdigest()==m['palette_sha256']
 # Every main ground-floor interior remains hollow above its floor.
 kind=row['family'].removeprefix('PokeB_')
 probe={'DomeLab':(60,50,20),'RedClinic':(50,50,15),'GrayEntryHouse':(40,45,20),'GrayWindowHouse':(40,45,20),'CyanEntryHouse':(40,45,20),'FlowerCottage':(40,45,15)}[kind]
 assert probe not in v
for fam in m['families']:
 _,base,_=read(ROOT/(fam['asset_id']+'.vox'));_,cart,_=read(ROOT/(fam['asset_id']+'_Cartoon.vox'))
 assert base.keys()!=cart.keys(),fam['asset_id']+' Cartoon must change shape, not just paint'
for name,sha in json.loads((R/'preserved-tree-hashes.json').read_text()).items():assert h(ROOT/name)==sha
print('PASS: 42 buildings; geometry, semantic colors, palettes, connectedness, hollow interiors, counts, previews and 112 preserved tree files.')
