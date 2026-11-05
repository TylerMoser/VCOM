from voxlib import *
from build import component_sizes
from collections import Counter,defaultdict
import wearables,catalog,sys
sys.path.insert(0,str(ROOT/'tools'))
from inspect_vox import inspect
rows=json.loads((HERE/'manifest.json').read_text());layouts=json.loads((HERE/'layouts.json').read_text());old=json.loads((HERE/'preserved-originals.json').read_text())
report=[];designs=defaultdict(set);geometries=defaultdict(set);fitted=defaultdict(dict)
for rel,h in old.items():assert sha((DEST/rel).read_bytes())==h,rel
for row in rows:
 p=Path(row['path']);size,v,pal,mats=read(p);a=inspect(p)
 assert not a['warnings'] and len(a['models'])==1,row['file']
 assert sha(p.read_bytes())==row['sha256'];assert len(v)==row['voxels'];assert 255 not in v.values()
 if row['style']=='CratePalette':
  assert pal==CRATE,row['file']
  _,src,sp,sm=read(DEST/row['source']);assert set(src)==set(v),row['file']
  for pos in v:
   assert sm.get(src[pos],{'_type':'_diffuse'})==mats.get(v[pos],{'_type':'_diffuse'}),(row['file'],pos)
 else:
  designs[row['category'],row['item'],row['form']].add(row['design'])
  geometries[row['category'],row['item'],row['form']].add(row['geometry_sha256'])
  expected=2 if row['family']=='boots' else 1
  assert len(component_sizes(v))==expected,(row['file'],component_sizes(v))
 if row['form']=='Fitted':
  layout=layouts[row['file']];assigned={}
  for bone,lo,hi in layout['regions']:
   for x in range(lo[0],hi[0]+1):assigned[x,lo[1],lo[2]]=bone
  assert set(assigned)==set(v)
  assert all(assigned[p]==wearables.bone(p,row['family']) for p in v)
  if row['family'] in ('armor','wearable'):
   for p in v:
    if 17<=p[2]<=19 and p[0]<=13:assert assigned[p].startswith('Right') and 'Arm' in assigned[p]
    if 17<=p[2]<=19 and p[0]>=19:assert assigned[p].startswith('Left') and 'Arm' in assigned[p]
  assert all(0<=p[0]<32 and 0<=p[1]<32 and 0<=p[2]<size[2] for p in v)
  fitted[row['category'],row['item'],row['design'],row['style']]['fitted']=v
 elif row['form']=='Standalone' and row['family'] in catalog.WEARABLE:
  off=row['original_offset'];restored={tuple(p[a]+off[a] for a in range(3)):c for p,c in v.items()}
  fitted[row['category'],row['item'],row['design'],row['style']]['standalone']=restored
 report.append({'file':row['file'],'sha256':row['sha256'],'structure':True,'palette_geometry_materials':True})
assert all(len(s)==4 for s in designs.values())
assert all(len(s)==4 for s in geometries.values()),{str(k):len(v) for k,v in geometries.items() if len(v)!=4}
assert len({(r['category'],r['item']) for r in rows if r['style']=='Base' and r['form']=='Standalone'})==len(catalog.CATALOG)
for key,pair in fitted.items():assert pair['fitted']==pair['standalone'],key
(HERE/'validation.json').write_text(json.dumps({'files':len(report),'originals_preserved':len(old),'types':len(catalog.CATALOG),'fitted_pairs':len(fitted),'results':report},indent=2))
print('PASS',len(report),'files;',len(old),'preserved originals;',len(catalog.CATALOG),'types;',len(fitted),'fitted-to-standalone exact pairs')
