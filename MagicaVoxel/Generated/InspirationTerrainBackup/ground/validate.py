"""Validate serialized tiles, reference preservation, styles, repetition and VCOM reports."""
import json,hashlib,importlib.util,sys
from generate import *
spec=importlib.util.spec_from_file_location('ground_auditor',ROOT/'tools/inspect_vox.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
m=json.loads((HERE/'manifest.json').read_text());runtime=json.loads((HERE/'godot-validation.json').read_text()) if '--binary' not in sys.argv else None
records=[];struct=[];by={r['family']+'|'+r['style']:r for r in m['models']}
for f in CAT:
 
 if f['role']=='transition':assert f['materials'][0]!=f['materials'][1]
 shapes={};raws={c:model(f,c) for c in [False,True]}
 if f['role']=='surface':
  for cartoon in [False,True]:
   for x in range(16):
    for y in range(16):
     assert surface(f,x,y,cartoon)==surface(f,x+16,y,cartoon)==surface(f,x,y+16,cartoon)
 elif f['contour']=='Edge':
  for c in [False,True]:
   assert [contour_a(f,x,0,c) for x in range(16)]==[contour_a(f,x,15,c) for x in range(16)]
 for style in STYLES:
  row=by[f['name']+'|'+style];path=ROOT/row['file'];size,v,pal=read(path);raw,refs=raws['Cartoon' in style];expected,epal,groups=paint(raw,refs,style)
  assert size==(16,16,16) and v==expected and pal==epal
  assert len(v)==row['voxels'] and len(set(v.values()))==row['colors']
  assert not ({0,255}&set(v.values())) and all(0<=q<16 for p in v for q in p)
  cols={}
  for x,y,z in v:cols.setdefault((x,y),[]).append(z)
  assert len(cols)==256 and all(sorted(zs)==list(range(max(zs)+1)) for zs in cols.values())
  assert len(components(v))==1
  if 'Cartoon' in style and f['role']=='surface' and f['kind'] not in ['planks','diagonalplanks','herringbone','brick','flagstone','furrows']:
   assert {(15-x,y,z):c for (x,y,z),c in v.items()}==v,(path,'mirror X')
   assert {(x,15-y,z):c for (x,y,z),c in v.items()}==v,(path,'mirror Y')
  if 'TwoColor' in style:assert all(len(indices)==1 for indices in groups.values()),path
  if 'CratePalette' in style:assert hashlib.sha256(b''.join(bytes(c) for c in pal)).hexdigest()==CRATE['palette_sha256']
  ar=audit.inspect(path);assert not ar.get('error') and not ar['warnings'];struct.append({'file':row['file'],'chunks':ar['chunks'],'models':len(ar['models']),'warnings':ar['warnings'],'sha256':sha(path)})
  assert sha(path)==row['sha256']
  if runtime:
   rr=runtime[row['file']];assert rr['sha256']==row['sha256'] and rr['voxels']==len(v) and rr['cell_reader'].startswith('pass') and rr['runtime_VoxelModel_shader']=='rendered'
  shapes[style]=set(v);records.append({'file':row['file'],'sha256':row['sha256'],'checks':'structure, geometry, palette, flat groups, filled columns, grounded, connected, scene graph','runtime':'pass' if runtime else 'pending'})
 for style in STYLES:assert shapes[style]==shapes['Cartoon' if 'Cartoon' in style else 'Base']
baseline=json.loads((HERE/'preservation-baseline.json').read_text())
for file,digest in baseline.items():assert sha(ROOT/file)==digest,file
sources=[{'source':p.name,'sha256':sha(p),'size':list(Image.open(p).size)} for p in ROOT.iterdir() if p.suffix.lower() in ['.png','.jpg','.gif']]
if (HERE/'source-inventory.json').exists():assert json.loads((HERE/'source-inventory.json').read_text())==sources
(HERE/'source-inventory.json').write_text(json.dumps(sources,indent=2))
(HERE/'structural-audit.json').write_text(json.dumps(struct,indent=2))
summary={'models':len(records),'families':len(CAT),'surface_families':sum(f['role']=='surface' for f in CAT),'transition_families':sum(f['role']=='transition' for f in CAT),'sources_reviewed':len(sources),'preserved_previous_models':len(baseline),'runtime_validated':bool(runtime),'level_integration':'not performed','checks':records}
(HERE/'validation-summary.json').write_text(json.dumps(summary,indent=2))
print('GROUND_VALIDATED',len(records),'models;',len(baseline),'previous models preserved; runtime',bool(runtime))
