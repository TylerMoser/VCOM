from pathlib import Path
import json,collections,sys
from voxlib import *
import catalog,weapons,objects,wearables

BUILDERS={k:getattr(weapons,k) for k in ('sword','axe','hammer','melee','gun','attachment','bow','thrown')}
BUILDERS.update({k:getattr(objects,k) for k in ('stim','medical','potion','ammo','grenade','scroll','torch','food','focus','relic')})
MANIFEST=HERE/'manifest.json'
def component_sizes(v):
 remaining=set(v);sizes=[]
 while remaining:
  p=remaining.pop();q=[p];n=0
  while q:
   p=q.pop();n+=1
   for ax in range(3):
    for delta in (-1,1):
     a=list(p);a[ax]+=delta;a=tuple(a)
     if a in remaining:remaining.remove(a);q.append(a)
  sizes.append(n)
 return sorted(sizes,reverse=True)
def record(path,spec,label,form,style,size,v,data,source=None,mapping=None,**extras):
 low=[min(p[a] for p in v) for a in range(3)];high=[max(p[a] for p in v) for a in range(3)]
 return dict(file=str(path.relative_to(DEST)),path=str(path),category=spec['category'],item=spec['name'],family=spec['family'],
  design=label,form=form,style=style,canvas=list(size),occupied_min=low,occupied_max=high,voxels=len(v),sha256=sha(data),
  geometry_sha256=sha(b''.join(bytes(p) for p in sorted(v))),source=source,palette_mapping=mapping,components=component_sizes(v),**extras)
def main():
 HERE.mkdir(exist_ok=True);DEST.mkdir(exist_ok=True)
 if not (HERE/'preserved-originals.json').exists():
  originals={str(p.relative_to(DEST)):sha(p.read_bytes()) for p in DEST.rglob('*.vox')}
  (HERE/'preserved-originals.json').write_text(json.dumps(originals,indent=2))
 originals=json.loads((HERE/'preserved-originals.json').read_text())
 for rel,h in originals.items():assert sha((DEST/rel).read_bytes())==h,'Original changed since collection began: '+rel
 previous=json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []
 owned={r['file']:r['sha256'] for r in previous};pending=[];rows=[];layouts={};issues=[]
 def stage(path,data):
  if path.exists() and sha(path.read_bytes()) not in (owned.get(str(path.relative_to(DEST))),sha(data)):
   raise RuntimeError('Preserving unowned/edited file: '+str(path))
  pending.append((path,data))
 for spec in catalog.CATALOG:
  for variant in range(4):
   label=catalog.LABELS.get(spec['family'],catalog.VARIANTS)[variant]
   fitted=spec['family'] in catalog.WEARABLE
   if fitted:m,bones=wearables.build(spec,variant)
   else:m=BUILDERS[spec['family']](spec['name'],variant)
   size,v,origin=m.normalize();forms=[('Standalone',size,v,origin)]
   if fitted:forms.append(('Fitted',(32,32,40 if max(p[2] for p in m.v)>=32 else 32),m.v,(0,0,0)))
   for form,size,v,origin in forms:
    pal=palette(spec['name'],variant);mats=materials(v)
    if spec['family']=='helmet' and spec['name'] in ('Brodie','Stahlhelm','Adrian','Pickelhaube','Pith','Miner'):
     pal[0]=[(102,110,78,255),(81,93,85,255),(94,110,125,255),(106,91,117,255)][variant]
    # The two first bottle designs use translucent liquid, two use opaque liquid.
    if spec['family']=='potion' and variant<2:mats[7]={**GLASS,'_trans':'.5','_ri':'1.33','_ior':'.33'}
    filename=f"{spec['name']}_{label}"+('_Fitted' if form=='Fitted' else '')
    folder=DEST/spec['category']/('Fitted' if form=='Fitted' else '')
    path=folder/(filename+'.vox');data=writebytes(size,v,pal,mats);stage(path,data)
    row=record(path,spec,label,form,'Base',size,v,data,original_offset=origin)
    if form=='Fitted':
     # Compress exact bone ownership into contiguous X runs per Y/Z, no broad regions swallowing adjacent limbs.
     regions=[]
     for bone_name in sorted(set(bones.values())):
      yz=collections.defaultdict(list)
      for (x,y,z),bone_id in bones.items():
       if bone_id==bone_name:yz[y,z].append(x)
      for (y,z),xs in sorted(yz.items()):
       xs.sort();a=last=xs[0]
       for x in xs[1:]+[999]:
        if x!=last+1:regions.append([bone_name,[a,y,z],[last,y,z]]);a=x
        last=x
     layouts[str(path.relative_to(DEST))]={'regions':regions,'base_character':'Character_Bigger','body_center':[16.5,16.0], 'equipment_only':True,'body_overlap':len(set(v)&set(wearables.BODY))}
    rows.append(row)
    cv,cm,mapping=remap(v,pal,mats);cp=folder/(filename+'_CratePalette.vox');cd=writebytes(size,cv,CRATE,cm);stage(cp,cd)
    rows.append(record(cp,spec,label,form,'CratePalette',size,cv,cd,source=row['file'],mapping=mapping,original_offset=origin))
    if form=='Fitted':layouts[str(cp.relative_to(DEST))]=layouts[str(path.relative_to(DEST))]
    if len(row['components'])>1 and form=='Standalone':issues.append((row['file'],row['components']))
 # Existing bottles/shields and hand-authored source equipment get non-destructive counterparts.
 for rel,h in originals.items():
  src=DEST/rel
  if '_CratePalette' in src.stem:continue
  category=src.parent.name if src.parent!=DEST else ('Swords' if 'sword' in src.stem.lower() else 'Guns' if 'Rifle' in src.stem else 'HealingSupplies' if 'Medkit' in src.stem else 'GrenadesBombs')
  path=(src.parent if src.parent!=DEST else DEST/category)/(src.stem+'_CratePalette.vox')
  data,mapping=recolor_original(src);stage(path,data);size,v,pal,mats=read(src);cv,_,_=remap(v,pal,mats)
  spec=dict(category=category,name=src.stem,family='preserved')
  rows.append(record(path,spec,'Existing','PreservedCounterpart','CratePalette',size,cv,data,source=rel,mapping=mapping,source_sha256=h))
 for path,data in pending:path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
 MANIFEST.write_text(json.dumps(rows,indent=2));(HERE/'layouts.json').write_text(json.dumps(layouts,indent=2))
 (HERE/'component-review.json').write_text(json.dumps(issues,indent=2))
 (HERE/'catalog.json').write_text(json.dumps(catalog.CATALOG,indent=2))
 print('Wrote',len(rows),'complete files;',len(catalog.CATALOG),'types;',len(layouts),'fitted files;',len(issues),'multi-component standalone designs to review')
if __name__=='__main__':main()
