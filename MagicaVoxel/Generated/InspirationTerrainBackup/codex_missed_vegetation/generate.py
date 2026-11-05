from pathlib import Path
import math,json,hashlib
from PIL import Image
from voxlib import write,read,components
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
CPDATA=json.loads((ROOT/'knowledge/palettes/crate-palette.json').read_text());CP=[tuple(c) for c in CPDATA['rgba']]
F=[]
for label,crop,top,side in [('RedOrange',[109,207,159,256],[207,76,40],[222,108,38]),('GoldOrange',[62,200,111,247],[221,176,79],[217,117,40]),('GreenGold',[118,235,169,286],[125,151,40],[206,161,62])]:
 F.append(dict(source='poke_f.png',name='PokeF_Codex_Layered'+label,kind='tree',size=[48,48,48],crop=crop,top=top,side=side,note='Broad layered crown with contrasting side lobes, dark exposed fork and short trunk. Same source silhouette across three distinct foliage appearances; hidden back/depth inferred.'))
F.append(dict(source='poke_d.png',name='PokeD_Codex_SpottedMushroomClump',kind='mushroom',size=[16,16,16],crop=[529,367,547,385],top=[226,106,101],side=[245,232,176],note='Two unequal coral-red spotted mushrooms, repeated near riverbanks. Pale cap spots and stems share one semantic color; separate grounded stems are intentional.'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def palette(f):
 p=[]
 for rgb in [f['top'],f['side'],[91,72,42] if f['kind']=='tree' else f['side']]:
  p.extend(tuple(min(255,round(c*k)) for c in rgb)+(255,) for k in [1,.8,1.12])
 return p+[(0,0,0,255)]*247
def group(c,kind):return (1 if c<=6 else 7) if kind=='tree' else (1 if c<=3 else 4)
def sculpt(f,cartoon):
 W,D,H=f['size'];v={}
 def ell(cx,cy,cz,rx,ry,rz,c):
  for x in range(max(0,math.floor(cx-rx)),min(W,math.ceil(cx+rx)+1)):
   for y in range(max(0,math.floor(cy-ry)),min(D,math.ceil(cy+ry)+1)):
    for z in range(max(0,math.floor(cz-rz)),min(H,math.ceil(cz+rz)+1)):
     if ((x-cx)/rx)**2+((y-cy)/ry)**2+((z-cz)/rz)**2<=1:v[x,y,z]=c
 def branch(a,b,r):
  n=math.ceil(math.dist(a,b)*2)
  for j in range(n+1):ell(*(a[i]+(b[i]-a[i])*j/n for i in range(3)),r,r,r,7)
 if f['kind']=='tree':
  cx=cy=23.5
  branch((cx,cy,2),(cx,cy,34),3.7)
  for j in range(4):
   a=j*math.pi/2
   branch((cx,cy,4),(cx+7*math.cos(a),cy+7*math.sin(a),1.5),2)
   branch((cx,cy,20),(cx+12*math.cos(a),cy+12*math.sin(a),33),2.5)
  # A broad lower whorl and four contrasting side umbrellas frame the exposed fork.
  ell(cx,cy,18,17,17,6,2)
  for j in range(8):
   a=j*math.pi/4;offset=0 if cartoon else (j%3-1)
   ell(cx+13*math.cos(a),cy+13*math.sin(a),19+offset,8,8,5,1 if j%2==0 else 2)
  for j in range(4):
   a=j*math.pi/2+math.pi/4;ox=16*math.cos(a);oy=16*math.sin(a)
   ell(cx+ox,cy+oy,29+(0 if cartoon else j%2),7,7,5,4)
   for k in [-1,0,1]:
    ell(cx+ox+3*math.sin(a)*k,cy+oy+3*math.cos(a)*k,31,5,5,3,6 if k==0 else 4)
  ell(cx,cy,36,12,12,7,1)
  for j in range(8):
   a=j*math.pi/4
   ell(cx+8*math.cos(a),cy+8*math.sin(a),36+(0 if cartoon else j%3-1),5.5,5.5,4.5,1 if j%2 else 3)
  ell(cx,cy,40,7,7,4,3)
 else:
  # Two independently grounded mushrooms; no artificial connecting soil slab.
  for cx,cy,r,h in ([(7.5,4.5,4.5,7),(7.5,12.5,2.5,4)] if cartoon else [(5.5,5,5,7),(11,11,3.5,4)]):
   for z in range(h+1):ell(cx,cy,z,1.4,1.4,1,4)
   for x in range(W):
    for y in range(D):
     d=((x-cx)/r)**2+((y-cy)/r)**2
     if d<=1:
      top=h+1+int(3*math.sqrt(1-d))
      for z in range(h,top+1):v[x,y,z]=2 if z==h else 1
      if any((x-(cx+dx))**2+(y-(cy+dy))**2<=rr**2 for dx,dy,rr in [(-2,-1,1.1),(2,-1,1.1),(0,2,1.2)]):v[x,y,top]=4
 if cartoon:
  if f['kind']=='tree':
   old=v;v={}
   for (x,y,z),c in old.items():
    if x<24 and y<24:
     for xx,yy in [(x,y),(47-y,x),(47-x,47-y),(y,47-x)]:v[xx,yy,z]=c
  else:
   for (x,y,z),c in list(v.items()):
    if x<8:v[15-x,y,z]=c
   for x,y,z in list(v):
    if x>=8 and (15-x,y,z) not in v:del v[x,y,z]
 return v
def run():
 old=json.loads((HERE/'manifest.json').read_text()) if (HERE/'manifest.json').exists() else {'models':[]};known={r['file']:r['sha256'] for r in old['models']}
 if not (HERE/'prior-hashes.json').exists():(HERE/'prior-hashes.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'output').glob('*/*.vox')},indent=2))
 rows=[];fs=[]
 for f in F:
  support=ROOT/'output'/Path(f['source']).stem/'codex_missed_vegetation';(support/'reference').mkdir(parents=True,exist_ok=True)
  im=Image.open(ROOT/f['source']).crop(f['crop']);im.resize((im.width*5,im.height*5),Image.Resampling.NEAREST).save(support/'reference'/(f['name']+'.png'))
  p=palette(f);mapping={i:min(range(1,255),key=lambda k:sum((p[i-1][j]-CP[k-1][j])**2 for j in range(3))) for i in range(1,10)}
  fs.append({**f,'source_sha256':sha(ROOT/f['source']),'crate_mapping':mapping,'tile_pixels':16})
  for style in STYLES:
   g=sculpt(f,'Cartoon' in style);flat='TwoColor' in style;crate='CratePalette' in style
   v={q:(mapping[group(c,f['kind']) if flat else c] if crate else group(c,f['kind']) if flat else c) for q,c in g.items()}
   path=support.parent/(f['name']+('' if style=='Base' else '_'+style)+'.vox');rel=path.relative_to(ROOT).as_posix()
   if path.exists() and sha(path)!=known.get(rel):raise RuntimeError('Protecting modified/unowned '+rel)
   write(path,f['size'],v,CP if crate else p);sz,actual,pal,n=read(path);assert v==actual
   rows.append(dict(family=f['name'],source=f['source'],style=style,file=rel,sha256=sha(path),canvas=f['size'],voxels=len(v),colors=len(set(v.values())),scene_models=n,components=components(v),occupied_min=[min(q[i] for q in v) for i in range(3)],occupied_max=[max(q[i] for q in v) for i in range(3)]))
 (HERE/'manifest.json').write_text(json.dumps(dict(date='2026-11-04',families=fs,models=rows,palette_sha256=CPDATA['palette_sha256']),indent=2));print('Generated',len(rows))
if __name__=='__main__':run()
