"""Source-measured outdoor stairs; complete files only, guarded regeneration."""
from pathlib import Path
import json, hashlib, struct, math
from PIL import Image
from voxlib import write, read, components
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
CPDATA=json.loads((ROOT/'knowledge/palettes/crate-palette.json').read_text()); CP=[tuple(c) for c in CPDATA['rgba']]
CAND={r['key']:r for r in json.loads((HERE/'reference/candidates.json').read_text())}
def family(key,name,width,run,rise,steps,**kw):
 r=CAND[key]; return dict(source=r['source'],name=name,crop=r['crop'],width=width,run=run,rise=rise,steps=steps,landing=8,tile_pixels=16,stone=(171,173,175),edge=(139,94,62),rail='wood',**kw)
# Coordinates are uphill +X, transverse Y, height Z; landings are included.
F=[]
def add(key,name,w,run,rise,steps,**changes):
 f=family(key,name,w,run,rise,steps);f.update(changes);F.append(f)
add('b1','PokeB_LongTerraceStairs',48,48,32,12,note='Twelve narrow gray treads; brown stringers. Upper plaza flight.')
add('b2','PokeB_SideTerraceStairs',48,32,24,8,note='Eight treads in the oblique east-facing flight; rotate the uphill axis to match.')
add('c1','PokeC_VillageStairs',48,32,24,6,stone=(172,166,127),edge=(149,99,66),note='Six olive stone treads between brown edging at the western village center.')
add('c2','PokeC_WideVillageStairs',64,32,24,6,stone=(172,166,127),edge=(149,99,66),note='Wider six-step western terrace flight.')
add('c3','PokeC_LongVillageStairs',48,48,40,10,stone=(172,166,127),edge=(149,99,66),note='Ten-step southern descent, preserving its longer run.')
add('c4','PokeC_UpperVillageStairs',48,24,16,4,stone=(172,166,127),edge=(149,99,66),note='Short eastern flight below the large house; terrain staircase, separate from its doorway.')
add('d1','PokeD_RoughStoneStairs',64,40,32,6,rail='rock',stone=(155,153,133),edge=(125,126,108),note='Six broad rounded stone treads nested between rough rock shoulders.')
add('d2','PokeD_StairLanding',80,32,32,6,kind='platform',rail='stone',stone=(155,153,133),edge=(177,177,151),note='Complete lower eastern cobbled terrace with masonry support, parapets and a side flight; hidden underside and rear are inferred.')
add('f1','PokeF_TallTerraceStairs',64,32,32,8,edge=(154,75,51),note='Eight silver-gray treads with red-brown stringers; northern clipped copy reuses this family.')
add('f2','PokeF_LowTerraceStairs',64,16,16,4,edge=(154,75,51),note='Four-step terrace west of the clinic, not its entrance.')
add('g1','PokeG_TerraceStairs',48,32,24,6,stone=(168,177,167),edge=(139,110,59),note='Six pale treads and golden timber edging at the town upper terrace.')
add('g2','PokeG_SideTerraceStairs',48,40,32,8,stone=(168,177,167),edge=(139,110,59),note='Longer side-on staircase beside the upper house; paired timber stringers.')
add('h1','PokeH_FieldStairs',48,16,16,4,note='Four-step field terrace flight; side-facing field copies reuse this geometry rotated.')
add('i1','PokeI_FarmStairs',48,16,16,4,tile_pixels=9.5,stone=(180,185,177),edge=(149,112,71),note='Repeated short flights; uses the newer building calibration of 9.5 displayed pixels per tile.')
add('j1','PokeJ_ForestStairs',64,32,32,8,tile_pixels=12.25,note='Both forest flights share eight gray treads. Scale follows the building calibration.')
add('k1','PokeK_LakesideStairs',64,32,32,8,tile_pixels=14.72,note='Three repeated flights. Tree repeats are two tiles across: 29.4 displayed pixels = two tiles, correcting the older tree note for this collection.')
add('m2','PokeM_StoneStairs',48,32,24,6,rail='stone',stone=(150,141,119),edge=(190,182,157),note='Six warm gray treads, pale stone curbs and end piers.')
add('m1','PokeM_DoubleStoneStairs',48,64,48,12,midlanding=8,rail='stone',stone=(150,141,119),edge=(190,182,157),note='Two six-step flights separated by a short landing, complete as one model.')
add('n1','PokeN_TwoStepStairs',32,16,8,2,stone=(161,153,106),edge=(123,88,48),note='Two broad olive treads and short timber edging on the upper house path.')
add('p1','PokeP_GullyStairs',48,32,32,8,edge=(172,83,41),note='Gray side-on terrain stair with orange-brown stringers beside the lower plank bridge. Distinct from the bridge.')
add('q1','PokeQ_SummitBambooStairs',48,32,16,4,rail='bamboo',stone=(193,158,96),edge=(80,115,68),woodsteps=True,note='Four broad timber treads with green segmented bamboo edging below the summit.')
add('q2','PokeQ_LongBambooStairs',48,64,48,10,rail='bamboo',stone=(193,158,96),edge=(80,115,68),woodsteps=True,note='Ten-step lower island flight, with continuous paired bamboo stringers.')
add('r1','PokeR_GardenStairs',48,16,12,3,stone=(163,178,164),edge=(151,84,54),note='Three shallow pale treads; northern path and commercial garden reuse this family.')
add('s1','PokeS_MossyTerrainStairs',48,32,32,6,tile_pixels=10,rail='rock',stone=(164,162,143),edge=(118,127,103),moss=True,note='Repeated six-step outdoor rock cuts, outside the already authored sanctuaries. Low rough shoulders with restrained moss.')
add('s5','PokeS_ShortTerrainStairs',48,16,16,3,tile_pixels=10,rail='rock',stone=(164,162,143),edge=(118,127,103),moss=True,note='Short eastern three-step descent; not a separate temple entrance.')
add('t1','PokeT_CaveStairs',48,32,24,6,rail='stone',stone=(150,141,119),edge=(190,182,157),note='Six warm stone treads with pale curbs; repeated cave-bank side views reuse rotations. No cave wall or mouth included.')

GROUP={i:(1 if i<=4 else 5 if i<=8 else 9 if i<=12 else 13) for i in range(1,17)}
ALLOWED={1:list(range(193,197))+list(range(201,207))+list(range(233,239)),5:list(range(177,181))+list(range(225,231))+list(range(233,239)),9:list(range(241,247)),13:list(range(241,247))}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def palette(f):
 def shades(rgb):return [tuple(round(v*k) for v in rgb)+(255,) for k in [1,.80,1.10,.94]]
 return shades(f['stone'])+shades(f['edge'])+shades((94,129,73))+shades((80,115,68))+[(0,0,0,255)]*240
def groups(f):
 g=dict(GROUP)
 if f['rail'] in ['stone','rock']:
  for i in range(5,9):g[i]=1
 if f['rail']=='bamboo':
  for i in range(1,5):g[i]=5
  for i in range(5,9):g[i]=13
 return g
def size_of(f):
 if f.get('kind')=='platform':return (112,80,64)
 return (f['run']+f.get('midlanding',0)+f['landing'],f['width'],math.ceil((f['rise']+16)/16)*16)
def height_at(f,x):
 if f.get('kind')=='platform':return 32 if x<80 else max(1,32-math.floor((x-80)*6/32)*5-2)
 run=f['run'];mid=f.get('midlanding',0)
 if x>=run+mid:return f['rise']
 if mid and x>=run//2:
  if x<run//2+mid:return f['rise']//2
  x-=mid
 return math.ceil((min(f['steps']-1,x*f['steps']//run)+1)*f['rise']/f['steps'])
class Sculpt:
 def __init__(self,f,c):self.f=f;self.c=c;self.size=size_of(f);self.v={}
 def box(self,a,b,c):
  for x in range(max(0,a[0]),min(self.size[0],b[0])):
   for y in range(max(0,a[1]),min(self.size[1],b[1])):
    for z in range(max(0,a[2]),min(self.size[2],b[2])):self.v[x,y,z]=c
 def finish(self):
  f=self.f;L,W,H=self.size;curb=5 if self.c else 3
  if f.get('kind')=='platform':
   self.box((0,0,0),(80,80,32),1)
   for x in range(80):
    for y in range(80):
     xx=(x+(y//5%2)*3)%6;yy=y%5
     c=2 if ((xx-2.5)/3)**2+((yy-2)/2.5)**2>1.05 else [1,1,4,3,1][(x//6+y//5*3)%5]
     self.v[x,y,31]=c
   self.box((0,0,32),(80,4,44),1);self.box((0,76,32),(80,80,44),1);self.box((0,0,32),(4,80,44),1)
   for a,b in [(0,16),(64,80)]:self.box((76,a,32),(80,b,44),1)
   for y in [0,75]:self.box((0,y,44),(80,y+5,47+(1 if self.c else 0)),7)
   self.box((0,0,44),(5,80,47+(1 if self.c else 0)),7)
   for x,y,z in list(self.v):
    if z<44 and (x in (0,79) or y in (0,79)) and (z%6==0 or (x+y+(z//6%2)*6)%12==0):self.v[x,y,z]=2
   for x in range(80,L):
    h=height_at(f,x);self.box((x,16,0),(x+1,64,h),1)
    for y in [16,64-curb]:self.box((x,y,0),(x+1,y+curb,h+5),7)
    for y in range(16+curb,64-curb):self.v[x,y,h-1]=3
  else:
   for x in range(L):
    h=height_at(f,x);self.box((x,4,0),(x+1,W-4,h),1)
    # Subtle riser and tread colors; no baked shadows beyond material shading.
    for y in range(4,W-4):
     yy=min(y,W-1-y);c=1
     if x==0 or height_at(f,x-1)<h:c=3
     elif not self.c and (yy+3*(x//8))%23==0:c=4
     self.v[x,y,h-1]=c
    for y in [1,W-1-curb]:
     if f['rail']=='rock':
      width=curb+2;start=0 if y<W//2 else W-width
      top=h+2+(0 if self.c else (x//5)%3)
      self.box((x,start,0),(x+1,start+width,top),6 if x%8==0 else 5)
      if f.get('moss') and x%11<4:self.box((x,start,top-1),(x+1,start+width,top),9)
     else:
      # Solid side stringer/curb, rising continuously beside the treads.
      mid=f.get('midlanding',0);progress=x
      if mid and x>=f['run']//2:progress=max(f['run']//2,x-mid)
      railtop=min(f['rise'],math.floor(progress*f['rise']/f['run']))+math.ceil(f['rise']/f['steps'])+3
      self.box((x,y,max(0,h-6)),(x+1,y+curb,railtop),5)
      self.box((x,y,railtop-1),(x+1,y+curb,railtop),7)
      if x in (0,L-1):self.box((x,y,0),(x+1,y+curb,railtop+4),5)
      if f['rail']=='bamboo' and x%8<2:self.box((x,max(0,y-1),h-4),(x+1,min(W,y+curb+1),railtop+1),7)
    # Join side curbs to the solid core below every tread.
    self.box((x,1,max(0,h-4)),(x+1,W-1,h-2),2)
  # Cartoon keeps uphill direction, but makes transverse geometry and paint exact.
  if self.c:
   for (x,y,z),c in list(self.v.items()):
    if y<W//2:self.v[x,W-1-y,z]=c
   for x,y,z in list(self.v):
    if y>=W//2 and (x,W-1-y,z) not in self.v:del self.v[x,y,z]
  return self.v
def run():
 old=json.loads((HERE/'manifest.json').read_text()) if (HERE/'manifest.json').exists() else {'models':[]};known={r['file']:r['sha256'] for r in old['models']}
 baseline=HERE/'preserved-hashes.json'
 if not baseline.exists():baseline.write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'output').glob('*/*.vox') if p.relative_to(ROOT).as_posix() not in known},indent=2))
 rows=[];families=[]
 for f in F:
  folder=ROOT/'output'/Path(f['source']).stem;support=folder/'stairs';(support/'reference').mkdir(parents=True,exist_ok=True)
  im=Image.open(ROOT/f['source']).crop(f['crop']);im.resize((im.width*4,im.height*4),Image.Resampling.NEAREST).save(support/'reference'/(f['name']+'.png'))
  p=palette(f);group=groups(f);mapping={i:min(ALLOWED[group[i]],key=lambda k:sum((p[i-1][j]-CP[k-1][j])**2 for j in range(3))) for i in range(1,17)}
  # Flat representative for bamboo timber must come from the tread, not green edging.
  representatives={g:next(i for i in range(1,17) if group[i]==g) for g in set(group.values())}
  geo={False:Sculpt(f,False).finish(),True:Sculpt(f,True).finish()}
  for g in geo.values():assert len(components(g))==1,(f['name'],components(g)[:5])
  assert set(geo[False])!=set(geo[True]),f['name']
  size=size_of(f);families.append({**f,'size':size,'source_sha256':sha(ROOT/f['source']),'crate_mapping':mapping,'semantic_groups':group,'flat_representatives':representatives})
  for style in STYLES:
   g=geo['Cartoon' in style];flat='TwoColor' in style;crate='CratePalette' in style
   v={q:(mapping[representatives[group[c]] if flat else c] if crate else representatives[group[c]] if flat else c) for q,c in g.items()}
   path=folder/(f['name']+('' if style=='Base' else '_'+style)+'.vox');rel=path.relative_to(ROOT).as_posix()
   if path.exists() and sha(path)!=known.get(rel):raise RuntimeError('Protecting modified/unowned file '+rel)
   pal=CP if crate else p;write(path,size,v,pal);sz,actual,ap,n=read(path);assert sz==size and actual==v and ap==pal
   rows.append(dict(family=f['name'],file=rel,source=f['source'],style=style,canvas=size,scene_models=n,voxels=len(v),colors=len(set(v.values())),occupied_min=[min(q[i] for q in v) for i in range(3)],occupied_max=[max(q[i] for q in v) for i in range(3)],sha256=sha(path)))
  print(f['name'],len(geo[False]),flush=True)
 assert all(sha(ROOT/p)==h for p,h in json.loads(baseline.read_text()).items())
 (HERE/'manifest.json').write_text(json.dumps(dict(date='2026-11-03',palette_sha256=CPDATA['palette_sha256'],families=families,models=rows),indent=2))
 print('PASS',len(rows),'models')
if __name__=='__main__':run()
