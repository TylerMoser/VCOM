"""Checks serialized outputs, variants, source preservation and actual runtime report."""
import json,hashlib,importlib.util,struct
from generate import ROOT,HERE,FAMILIES,STYLES,paint,make,read,label_group
from voxlib import components
spec=importlib.util.spec_from_file_location('rock_vox_auditor',ROOT/'tools/inspect_vox.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
def matl(path):
 data=path.read_bytes();pos=20;materials=[]
 while pos<len(data):
  cid,n,c=struct.unpack_from('<4sii',data,pos)
  if cid==b'MATL':materials.append(data[pos+12:pos+12+n])
  pos+=12+n+c
 assert materials and all(b'_diffuse' in m and b'_emit' not in m and b'_glass' not in m for m in materials)
manifest=json.loads((HERE/'manifest.json').read_text());runtime=json.loads((HERE/'godot-validation.json').read_text());checks=[]
structural=[audit.inspect(ROOT/row['file']) for row in manifest['models']]
assert not any(r.get('error') or r.get('warnings') for r in structural)
(HERE/'structural-audit.json').write_text(json.dumps(structural,indent=2))
for f in FAMILIES:
 source_models={False:make(f),True:make(f,True)}
 actual={}
 for style in STYLES:
  row=next(r for r in manifest['models'] if r['family']==f['name'] and r['style']==style)
  path=ROOT/row['file'];size,vox,pal=read(path);m=source_models['Cartoon' in style]
  v_expected,p_expected,groups=paint(f,m,style)
  assert (vox,pal)==(v_expected,p_expected)
  assert components(vox)==[len(vox)];assert 0 not in vox.values() and 255 not in vox.values()
  matl(path)
  if 'Cartoon' in style:
   assert {(size[0]-1-x,y,z):c for (x,y,z),c in vox.items()}==vox,(path,'X symmetry')
   if 'and Y' in row['symmetry']:assert {(x,size[1]-1-y,z):c for (x,y,z),c in vox.items()}==vox,(path,'Y symmetry')
  if 'TwoColor' in style:
   for group in set(map(label_group,m.v.values())):
    assert len({vox[p] for p,label in m.v.items() if label_group(label)==group})==1
  actual[style]=set(vox)
  digest=hashlib.sha256(path.read_bytes()).hexdigest();r=runtime[row['file']]
  assert r['sha256']==digest==row['sha256'];assert r['voxels']==len(vox) and r['grounded'] and r['dimensions_match']
  checks.append({'file':row['file'],'geometry_materials_palette':'pass','connectivity':'pass','runtime_hash_match':'pass'})
 for style in STYLES:assert actual[style]==actual['Cartoon' if 'Cartoon' in style else 'Base']
baseline=json.loads((HERE/'preservation-baseline.json').read_text())
for file,digest in baseline.items():assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest,file
sources=json.loads((HERE/'source-inventory.json').read_text())
for row in sources:assert hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest()==row['sha256']
summary={'models':len(checks),'families':len(FAMILIES),'sources_reviewed':len(sources),'preserved_previous_models':len(baseline),'checks':checks,'runtime_report':'godot-validation.json','level_integration':'not performed','visual_review':'visual-review.json'}
(HERE/'validation-summary.json').write_text(json.dumps(summary,indent=2))
print('ROCKS_VALIDATED',len(checks),'models;',len(baseline),'previous models preserved')
