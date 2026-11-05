from pathlib import Path
import json,hashlib,sys
from PIL import Image
from catalogue import F
from sculpt import Sculpt
from voxlib import write,read,components
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
CPDATA=json.loads((ROOT/'knowledge/palettes/crate-palette.json').read_text());CP=[tuple(c) for c in CPDATA['rgba']]
GROUPS=['leaf','wood','cut','stone','roof','metal','petal','center','glass','sand','grass','cloth','dark','lightgrass']
ALLOWED={'leaf':list(range(241,247)),'wood':[177,178,179,180],'cut':list(range(225,239)),'stone':list(range(193,207)),'roof':list(range(225,239))+list(range(193,197)),'metal':list(range(193,207)),'glass':[253],'grass':list(range(241,247)),'sand':list(range(233,239)),'cloth':[194,195,196,237,238],'dark':[201,202,240]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def palettes(f):
 colors=dict(leaf=f.get('leaf',(48,146,57)),wood=f.get('wood',(121,91,53)),cut=(178,151,99),stone=(133,149,163),roof=(145,126,81),metal=(139,159,170),petal=f.get('petal',(244,221,75)),center=(244,189,46),glass=(38,49,48),sand=(222,204,151),grass=f.get('leaf',(92,188,126)),cloth=(228,223,193),dark=(34,31,24))
 if f['kind']=='house':colors['wood']=(110,55,45);colors['cut']=(178,113,73)
 colors['lightgrass']=(121,200,134)
 if f['source']=='new_2.jpg':colors['leaf']=tuple(round(c*f.get('shade',1)) for c in colors['leaf'])
 p=[]
 for g in GROUPS:
  p += [tuple(min(255,round(c*k)) for c in colors[g])+(255,) for k in [.77,1,1.15]]
 p += [(0,0,0,255)]*(256-len(p));mapping={}
 for gi,g in enumerate(GROUPS):
  allowed=list(range(241,247)) if g=='lightgrass' else ALLOWED.get(g,list(range(217,239))+list(range(249,255)))
  if g=='leaf' and f['source']=='new_1.jpg' and f['kind']=='cone':allowed=[229,230,241,242,243]
  for s in range(3):
   i=gi*3+s+1;mapping[i]=min(allowed,key=lambda c:sum((p[i-1][j]-CP[c-1][j])**2 for j in range(3)))
 return p,mapping
def ground_components(v):
 left=set(v);result=[]
 while left:
  todo=[left.pop()];part=[]
  while todo:
   q=todo.pop();part.append(q);x,y,z=q
   for p in [(x+1,y,z),(x-1,y,z),(x,y+1,z),(x,y-1,z),(x,y,z+1),(x,y,z-1)]:
    if p in left:left.remove(p);todo.append(p)
  result.append(part)
 return result
def anchor(v,f):
 # Repair only detached sculpted foliage using a real stem to its nearest support.
 # Separate rooted grass blades / flowers / floating pads stay separate.
 added=0
 for part in sorted(ground_components(v),key=len,reverse=True):
  if any(p[2]==0 for p in part):continue
  # Avoid full pairwise search: search down/up in an occupied vertical column.
  best=None
  for x,y,z in part:
   for d in range(1,min(f['size'][2],16)):
    if (x,y,z-d) in v and (x,y,z-d) not in part:
     cand=(d,x,y,z,z-d)
     if best is None or cand<best:best=cand
     break
   if best and best[0]==1:break
  if best:
   d,x,y,z,bottom=best;g='leaf' if v[x,y,z][0]=='leaf' else v[x,y,z][0]
   for zz in range(bottom+1,z):v[x,y,zz]=(g,1);added+=1
 return added
def run():
 old=json.loads((HERE/'manifest.json').read_text()) if (HERE/'manifest.json').exists() else {'models':[]};known={r['file']:r['sha256'] for r in old['models']}
 if not (HERE/'prior-hashes.json').exists():(HERE/'prior-hashes.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'output').glob('*/*.vox')},indent=2))
 selected=[f for f in F if not sys.argv[1:] or any(token in f['name'] for token in sys.argv[1:])]
 selected_names={f['name'] for f in selected}
 rows=[r for r in old.get('models',[]) if r['family'] not in selected_names];families=[f for f in old.get('families',[]) if f['name'] not in selected_names]
 for f in F:
  if f['name'] not in selected_names:continue
  folder=ROOT/'output'/Path(f['source']).stem;support=folder/'codex';(support/'reference').mkdir(parents=True,exist_ok=True)
  im=Image.open(ROOT/f['source']).crop(f['crop']);im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(support/'reference'/(f['name']+'.png'))
  p,mapping=palettes(f);geo={False:Sculpt(f,False).finish(),True:Sculpt(f,True).finish()}
  repairs={}
  # Geometry is constructed coherently; detached component diagnostics are saved for review.
  for cartoon,g in geo.items():repairs[str(cartoon)]=0
  families.append({**f,'source_sha256':sha(ROOT/f['source']),'crate_mapping':mapping,'groups':GROUPS,'repairs':repairs})
  for style in STYLES:
   g=geo['Cartoon' in style];flat='TwoColor' in style;crate='CratePalette' in style;v={}
   for q,(material,s) in g.items():
    if flat and material=='cut':material='wood'
    idx=GROUPS.index(material)*3+(1 if flat else s)+1;v[q]=mapping[idx] if crate else idx
   path=folder/(f['name']+('' if style=='Base' else '_'+style)+'.vox');rel=path.relative_to(ROOT).as_posix()
   if path.exists() and sha(path)!=known.get(rel):raise RuntimeError('Protecting modified/unowned '+rel)
   glass={v[q] for q,c in g.items() if c[0]=='glass'};mats={c:{'_type':'_glass','_trans':'.7','_rough':'.15'} for c in glass}
   write(path,f['size'],v,CP if crate else p,mats);sz,actual,pal,n=read(path);assert actual==v
   parts=ground_components(v) if style in ['Base','Cartoon'] else None
   rows.append(dict(family=f['name'],source=f['source'],style=style,file=rel,sha256=sha(path),canvas=f['size'],voxels=len(v),colors=len(set(v.values())),scene_models=n,component_sizes=[len(a) for a in parts] if parts else None,ungrounded_components=[len(a) for a in parts if min(q[2] for q in a)>0] if parts else None,glass_indices=sorted(glass),occupied_min=[min(q[i] for q in v) for i in range(3)],occupied_max=[max(q[i] for q in v) for i in range(3)]))
  print(f['name'],len(geo[False]),flush=True)
 order={f['name']:i for i,f in enumerate(F)};families.sort(key=lambda f:order[f['name']]);rows.sort(key=lambda r:(order[r['family']],STYLES.index(r['style'])))
 (HERE/'manifest.json').write_text(json.dumps(dict(date='2026-11-04',families=families,models=rows,palette_sha256=CPDATA['palette_sha256']),indent=2));print('Generated',len(rows),'models in',len(F),'families',flush=True)
if __name__=='__main__':run()
