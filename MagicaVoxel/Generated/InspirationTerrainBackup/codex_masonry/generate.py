"""Whole masonry details, deterministic and guarded against overwriting hand edits."""
from pathlib import Path
import math,json,hashlib
from PIL import Image
from voxlib import write,read,components
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
CPDATA=json.loads((ROOT/'knowledge/palettes/crate-palette.json').read_text()); CP=[tuple(c) for c in CPDATA['rgba']]
F=[dict(source='poke_d.png',name='PokeD_Codex_BarredDrain',kind='drain',size=[32,16,32],crop=[482,477,526,508],stone=[150,149,128],note='Small half-round riverbank outlet. Five recessed bars, open gaps and through bore; hidden depth inferred. Source approximately two tiles wide.'),
 dict(source='poke_d.png',name='PokeD_Codex_RetainingWall',kind='wall',size=[64,16,48],crop=[574,559,602,644],stone=[155,153,133],note='Reusable four-tile straight section extracted from the masonry vocabulary of the lower terrace; inferred repeat length and hidden back. Not a separate new structure in the image.'),
 dict(source='poke_d.png',name='PokeD_Codex_RetainingCorner',kind='corner',size=[48,48,48],crop=[576,559,661,639],stone=[155,153,133],note='L-shaped outside corner matching the terrace masonry and pale coping. Repeatable assembly component; hidden return inferred.'),
 dict(source='pixelwood_c.jpg',name='PixelwoodC_Codex_ChestPedestal',kind='pedestal',size=[32,32,16],crop=[315,315,424,420],stone=[100,103,115],note='Square slate plinth under existing treasure chest; bevelled base, inset top and raised border. 48 displayed pixels per tile. Chest excluded; center it above z=10.')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def palette(f):
 rgb=f['stone']; p=[tuple(round(v*k) for v in rgb)+(255,) for k in [1,.78,1.17,.91]]
 return p+[(65,65,55,255),(91,91,74,255)]+[(0,0,0,255)]*250
def group(c):return 1 if c<=4 else 5
def sculpt(f,cartoon):
 W,D,H=f['size'];v={}
 def box(x0,x1,y0,y1,z0,z1,c):
  for x in range(x0,x1):
   for y in range(y0,y1):
    for z in range(z0,z1):v[x,y,z]=c
 if f['kind'] in ['wall','corner']:
  box(0,W,2,14,0,36,1)
  if f['kind']=='corner':box(2,14,0,D,0,36,1)
  # Recessed mortar remains physical relief after flat recoloring.
  for x,y,z in list(v):
   surface=y in [2,13] or f['kind']=='corner' and x in [2,13]
   along=x if y in [2,13] else y
   seam=z%7==6 or (along+(z//7%2)*6)%12==11
   if surface and seam:del v[x,y,z]
   elif surface:v[x,y,z]=[1,4,3,1][(along//12+z//7*3)%4]
  box(0,W,0,16,35,40 if cartoon else 39,3)
  if f['kind']=='corner':box(0,16,0,D,35,40 if cartoon else 39,3)
  # Cap joints, shallow cuts with uninterrupted supporting course below.
  for x,y,z in list(v):
   if z>=37 and ((y<16 and x%8==7) or (f['kind']=='corner' and x<16 and y%8==7)):
    if y in [0,15] or x in [0,15]:del v[x,y,z]
 elif f['kind']=='drain':
  cx=(W-1)/2; spring=5; inner=11;outer=15
  for x in range(W):
   for z in range(22):
    dx=x-cx;r=math.hypot(dx,max(0,z-spring))
    if r>outer or (abs(dx)<inner and z<spring+math.sqrt(max(0,inner**2-dx**2))):continue
    for y in range(2,14):
     a=math.atan2(max(0,z-spring),dx)
     c=3 if y<5 else 1
     if y<4 and int(a/math.pi*9)%2==0:c=4
     if y==2 and abs((a/math.pi*9)%1-.5)<.08:continue
     v[x,y,z]=c
  box(1,31,1,15,0,2,3)
  for x0 in [7,11,15,19,23]:
   roof=spring+math.sqrt(inner**2-(x0-cx)**2)
   box(x0,x0+2,6,8,2,math.ceil(roof)+1,5)
  if cartoon:box(13,19,0,5,17,22,3)
 else:
  # Compact chamfered square base, continuous support, upper seating recess.
  for z in range(10):
   inset=1 if z<2 else 0 if z<5 else 2
   for x in range(inset,W-inset):
    for y in range(inset,D-inset):
     if min(x,W-1-x)+min(y,D-1-y)<inset+2:continue
     v[x,y,z]=2 if z<2 else 1 if z<5 else 3 if z==9 else 4
  box(3,29,3,29,10,12 if cartoon else 11,3)
  box(4,28,4,28,10,11,1)
  # Inset seating surface at z=10, slightly raised rim around it.
  for x in range(4,28):
   for y in range(4,28):
    for z in range(10,12):v.pop((x,y,z),None)
  if not cartoon:
   for x in [8,9,10]:v[x,2,5]=2
   for y in [19,20,21]:v[29,y,6]=2
 if cartoon:
  if f['kind']=='corner':
   for (x,y,z),c in list(v.items()):
    if x<=y:v[y,x,z]=c
  elif f['kind']=='pedestal':
   original=dict(v);v={}
   for (x,y,z),c in original.items():
    if x<16 and y<16:
     for xx,yy in [(x,y),(31-y,x),(31-x,31-y),(y,31-x)]:v[xx,yy,z]=c
  else:
   for (x,y,z),c in list(v.items()):
    if x<W//2:v[W-1-x,y,z]=c
   for x,y,z in list(v):
    if x>=W//2 and (W-1-x,y,z) not in v:del v[x,y,z]
 return v
def run():
 old=json.loads((HERE/'manifest.json').read_text()) if (HERE/'manifest.json').exists() else {'models':[]};known={r['file']:r['sha256'] for r in old['models']}
 if not (HERE/'prior-hashes.json').exists():(HERE/'prior-hashes.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'output').glob('*/*.vox')},indent=2))
 rows=[];fs=[]
 for f in F:
  support=ROOT/'output'/Path(f['source']).stem/'codex_masonry';(support/'reference').mkdir(parents=True,exist_ok=True)
  im=Image.open(ROOT/f['source']).crop(f['crop']);im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(support/'reference'/(f['name']+'.png'))
  p=palette(f);mapping={i:min(range(1,255),key=lambda k:sum((p[i-1][j]-CP[k-1][j])**2 for j in range(3))) for i in range(1,7)}
  fs.append({**f,'source_sha256':sha(ROOT/f['source']),'crate_mapping':mapping,'tile_pixels':48 if f['kind']=='pedestal' else 16})
  for style in STYLES:
   g=sculpt(f,'Cartoon' in style);assert len(components(g))==1,(f['name'],components(g))
   flat='TwoColor' in style;crate='CratePalette' in style
   v={q:(mapping[group(c) if flat else c] if crate else group(c) if flat else c) for q,c in g.items()}
   path=support.parent/(f['name']+('' if style=='Base' else '_'+style)+'.vox');rel=path.relative_to(ROOT).as_posix()
   if path.exists() and sha(path)!=known.get(rel):raise RuntimeError('Protecting modified/unowned file '+rel)
   write(path,f['size'],v,CP if crate else p);sz,actual,pal,n=read(path);assert actual==v
   rows.append(dict(family=f['name'],source=f['source'],style=style,file=rel,sha256=sha(path),canvas=f['size'],voxels=len(v),colors=len(set(v.values())),scene_models=n,occupied_min=[min(q[i] for q in v) for i in range(3)],occupied_max=[max(q[i] for q in v) for i in range(3)]))
 (HERE/'manifest.json').write_text(json.dumps(dict(date='2026-11-04',families=fs,models=rows,palette_sha256=CPDATA['palette_sha256']),indent=2));print('Generated',len(rows))
if __name__=='__main__':run()
