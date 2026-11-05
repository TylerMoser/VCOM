"""Audit saved assets, palette/geometry invariants, runtime reports and preservation."""
import json,hashlib,importlib.util
from generate import *
spec=importlib.util.spec_from_file_location('deadwood_auditor',ROOT/'tools/inspect_vox.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
manifest=json.loads((HERE/'manifest.json').read_text());runtime=json.loads((HERE/'godot-validation.json').read_text());checks=[];structural=[]
for f in FAMILIES:
 actual={}
 for style in STYLES:
  row=next(r for r in manifest['models'] if r['family']==f['name'] and r['style']==style)
  path=ROOT/row['file'];size,v,pal=read(path);m=make(f,'Cartoon' in style);expected,epal,groups=paint(f,m,style)
  assert (v,pal)==(expected,epal)
  r=audit.inspect(path);assert not r.get('error') and not r.get('warnings'),r;structural.append(r)
  assert len(components(v))==1 and min(p[2] for p in v)==0
  assert 0 not in v.values() and 255 not in v.values()
  if 'Cartoon' in style:
   assert {(size[0]-1-x,y,z):c for (x,y,z),c in v.items()}==v,(path,'X symmetry')
   assert {(x,size[1]-1-y,z):c for (x,y,z),c in v.items()}==v,(path,'Y symmetry')
  if 'TwoColor' in style:
   assert len(set(v.values()))==2
   for group in ['bark','wood']:assert len({v[p] for p,s in m.v.items() if s[:-1]==group})==1
  if 'CratePalette' in style:assert hashlib.sha256(b''.join(bytes(c) for c in pal)).hexdigest()==CRATE['palette_sha256']
  digest=hashlib.sha256(path.read_bytes()).hexdigest();r=runtime[row['file']]
  assert r['sha256']==digest==row['sha256'];assert r['voxels']==len(v) and r['grounded'] and r['dimensions_match']
  oversized=max(b-a+1 for a,b in zip(row['occupied_min'],row['occupied_max']))>62
  assert (r['runtime_VoxelModel_shader']=='rendered')!=oversized
  actual[style]=set(v);checks.append({'file':row['file'],'structure_geometry_palette_grounding':'pass','runtime_hash_match':'pass','VoxelModel_supported':not oversized})
 for style in STYLES:assert actual[style]==actual['Cartoon' if 'Cartoon' in style else 'Base']
baseline=json.loads((HERE/'preservation-baseline.json').read_text())
for file,digest in baseline.items():assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest,file
sources=json.loads((HERE/'source-inventory.json').read_text())
for row in sources:assert hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest()==row['sha256']
reuse=[]
for style in STYLES:
 path=ROOT/'output/pixelwood_a'/('PixelwoodA_Stump'+('' if style=='Base' else '_'+style)+'.vox');assert path.exists()
 reuse.append({'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(HERE/'reuse.json').write_text(json.dumps(reuse,indent=2))
(HERE/'structural-audit.json').write_text(json.dumps(structural,indent=2))
summary={'models':len(checks),'families':len(FAMILIES),'sources_reviewed':len(sources),'preserved_previous_models':len(baseline),'checks':checks,'runtime_supported_models':sum(c['VoxelModel_supported'] for c in checks),'oversized_imported_mesh_models':sum(not c['VoxelModel_supported'] for c in checks),'level_integration':'not performed'}
(HERE/'validation-summary.json').write_text(json.dumps(summary,indent=2))
print('DEADWOOD_VALIDATED',len(checks),'models;',len(baseline),'previous models preserved')
