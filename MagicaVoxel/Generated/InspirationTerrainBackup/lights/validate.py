"""Validate delivered files, actual MATL dictionaries, preservation and variants."""
import json,struct,hashlib,sys,subprocess
from pathlib import Path
from generate import ROOT,HERE,FAMILIES,STYLES,paint,build,read
def materials(path):
 data=path.read_bytes();pos=20;out={}
 while pos<len(data):
  tag,n,children=struct.unpack_from('<4sii',data,pos);p=pos+12
  if tag==b'MATL':
   idx,count=struct.unpack_from('<ii',data,p);p+=8;props={}
   for _ in range(count):
    pair=[]
    for j in range(2):
     size=struct.unpack_from('<i',data,p)[0];p+=4;pair.append(data[p:p+size].decode());p+=size
    props[pair[0]]=pair[1]
   out[idx]=props
  pos+=12+n+children
 return out
manifest=json.loads((HERE/'manifest.json').read_text());reports=[]
for f in FAMILIES:
 models={False:build(f),True:build(f,True)}
 for style in STYLES:
  row=next(r for r in manifest['models'] if r['family']==f['name'] and r['style']==style)
  path=ROOT/row['file'];size,vox,pal=read(path);m=models['Cartoon' in style]
  expected,palette,mats,groups=paint(f,m,style)
  assert vox==expected and pal==palette and set(vox)==set(m.v)
  assert materials(path)==mats
  actualemit={p for p,i in vox.items() if mats[i]['_type']=='_emit'}
  assert actualemit=={p for p,label in m.v.items() if label in ('light','flame','flameLight')}
  if 'Cartoon' in style:
   w,d,h=size
   transform=(lambda p:(p[0],d-1-p[1],p[2])) if f['shape']=='crook' else ((lambda p:(w-1-p[0],p[1],p[2])) if f['shape']=='twin' else (lambda p:(w-1-p[1],p[0],p[2])))
   assert {transform(p):c for p,c in vox.items()}==vox,(path,'paint/geometry symmetry')
  reports.append({'file':row['file'],'serialized_geometry_and_materials':'pass','emitter_mask':'pass','cartoon_symmetry':'pass' if 'Cartoon' in style else 'not applicable'})
baseline=json.loads((HERE/'preservation-baseline.json').read_text())
for file,digest in baseline.items():assert hashlib.sha256((ROOT/file).read_bytes()).hexdigest()==digest,file
sources=json.loads((HERE/'source-inventory.json').read_text())
for row in sources:assert hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest()==row['sha256']
subprocess.run([sys.executable,str(ROOT/'tools/inspect_vox.py'),*[str(ROOT/r['file']) for r in manifest['models']],'--output',str(HERE/'structural-audit.json')],check=True)
godot=json.loads((HERE/'godot-validation.json').read_text());assert len(godot)==len(reports)
for row in manifest['models']:
 g=godot[row['file']];assert g['voxels']==row['voxels'] and g['emit_voxels']==row['emission_voxels'] and g['grounded']
summary={'models':len(reports),'source_images_reviewed':len(sources),'source_appearances':len(FAMILIES),'distinct_designs':len(FAMILIES)-1,'preserved_existing_vox_files':len(baseline),'preserved_original_images':len(sources),'checks':reports,'runtime_report':'godot-validation.json','game_level_integration':'not performed; no cell files','visual_review':'See day/night variation sheets and four cardinal Base/Cartoon views.'}
(HERE/'validation-summary.json').write_text(json.dumps(summary,indent=2));print('LIGHT COLLECTION VALIDATED',len(reports),'models;',len(baseline),'previous VOX files preserved')
