"""Validate delivered binaries, dependency invariants, runtime hashes and preservation."""
import json,hashlib,importlib.util
from generate import ROOT,HERE,FAMILIES,STYLES,paint,make,read,label_group,rooted_components,CRATE
from catalogue import REUSE
spec=importlib.util.spec_from_file_location('plant_vox_auditor',ROOT/'tools/inspect_vox.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
manifest=json.loads((HERE/'manifest.json').read_text());runtime=json.loads((HERE/'godot-validation.json').read_text());checks=[]
structural=[audit.inspect(ROOT/row['file']) for row in manifest['models']]
assert not any(r.get('error') or r.get('warnings') for r in structural)
(HERE/'structural-audit.json').write_text(json.dumps(structural,indent=2))
for f in FAMILIES:
 source={False:make(f),True:make(f,True)};actual={}
 for style in STYLES:
  row=next(r for r in manifest['models'] if r['family']==f['name'] and r['style']==style)
  path=ROOT/row['file'];size,v,pal=read(path);m=source['Cartoon' in style]
  expected,expected_pal,groups=paint(f,m,style);assert (v,pal)==(expected,expected_pal)
  assert all(c['minimum_z']==0 for c in rooted_components(v)),path
  assert 0 not in v.values() and 255 not in v.values()
  if 'Cartoon' in style:
   assert {(size[0]-1-x,y,z):c for (x,y,z),c in v.items()}==v,(path,'X symmetry')
   assert {(x,size[1]-1-y,z):c for (x,y,z),c in v.items()}==v,(path,'Y symmetry')
  if 'TwoColor' in style:
   for group in set(map(label_group,m.v.values())):assert len({v[p] for p,s in m.v.items() if label_group(s)==group})==1
  if 'CratePalette' in style:assert hashlib.sha256(b''.join(bytes(c) for c in pal)).hexdigest()==CRATE['palette_sha256']
  digest=hashlib.sha256(path.read_bytes()).hexdigest();r=runtime[row['file']]
  assert r['sha256']==digest==row['sha256'];assert r['voxels']==len(v) and r['grounded'] and r['dimensions_match']
  actual[style]=set(v);checks.append({'file':row['file'],'geometry_palette_groups':'pass','all_components_rooted':'pass','runtime_hash_match':'pass'})
 for style in STYLES:assert actual[style]==actual['Cartoon' if 'Cartoon' in style else 'Base']
baseline=json.loads((HERE/'preservation-baseline.json').read_text())
for file,digest in baseline.items():assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest,file
sources=json.loads((HERE/'source-inventory.json').read_text())
for row in sources:assert hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest()==row['sha256']
reuse=[]
for src,files in REUSE.items():
 for base in files:
  for style in STYLES:
   path=ROOT/(base[:-4]+('' if style=='Base' else '_'+style)+'.vox');assert path.is_file(),path
   reuse.append({'source':src,'file':path.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(HERE/'reuse.json').write_text(json.dumps(reuse,indent=2))
summary={'models':len(checks),'families':len(FAMILIES),'sources_reviewed':len(sources),'preserved_previous_models':len(baseline),'checks':checks,'runtime_report':'godot-validation.json','level_integration':'not performed','visual_review':'visual-review.json','reuse':'reuse.json'}
(HERE/'validation-summary.json').write_text(json.dumps(summary,indent=2))
print('VEGETATION_VALIDATED',len(checks),'models;',len(baseline),'previous models preserved')
