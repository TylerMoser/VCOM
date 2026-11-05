"""Complete source-specific bridges. Fixed formulas, no random seeds, protected outputs."""
from pathlib import Path
import json,hashlib,math,struct
from PIL import Image
from voxlib import write,read,components
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
CPDATA=json.loads((ROOT/'knowledge/palettes/crate-palette.json').read_text());CP=[tuple(c) for c in CPDATA['rgba']]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def family(src,name,kind,size,crop,deck,tile=16,**kw):return dict(source=src,name=name,kind=kind,size=size,crop=crop,deck=deck,tile_pixels=tile,**kw)
F=[
 family('poke_a.jpg','PokeA_CompletePicketBridge','wood',(112,64,64),(215,263,295,324),32,10.5,rail='picket',wood=(180,137,83),note='Seven-tile timber span with close pickets, caps, deck, beams and four inferred bank piles.'),
 family('poke_c.png','PokeC_DownstreamStoneBridge','stone',(208,48,80),(317,608,530,680),48,bays=[0,28,76,124,172,208],rail='woodsolid',stone=(75,83,90),paving=(163,163,128),wood=(102,66,48),note='Downstream uncovered bridge: dark masonry, three principal arch bays and small end openings, pale slab paving, solid brown timber guards.'),
 family('poke_d.png','PokeD_FourArchBridge','stone',(320,80,96),(142,217,465,357),64,bays=[0,80,160,240,320],rail='stone',stone=(150,149,128),paving=(163,162,143),note='Four long arches, broad cobbled carriageway, pale solid parapets and rounded pier noses; complete 20-tile scene in one file with two internal halves.'),
 family('poke_d.png','PokeD_SingleArchBridge','stone',(80,64,80),(262,699,360,802),48,bays=[0,80],rail='stone',stone=(150,149,128),paving=(163,162,143),note='Southern short river bridge; single arch, cobbles and matching parapets.'),
 family('poke_d.png','PokeD_StoneOverpass','stone',(80,64,72),(542,374,625,466),40,bays=[0,80],rail='stone',stone=(150,149,128),paving=(163,162,143),note='Eastern short arched road overpass. Terrain approaches, side stair and nearby lower terrace remain separate.'),
 family('poke_f.png','PokeF_PondSlatCrossing','wood',(32,48,32),(268,398,323,434),16,rail='none',slats=8,gap=2,wood=(182,168,110),bolts=True,nopiles=True,note='Four broad planks across the pond neck, with visible gaps and end fasteners; underside stringers inferred.'),
 family('poke_h.png','PokeH_FarmPicketBridge','wood',(160,64,64),(430,433,560,501),32,rail='picket',wood=(151,106,60),note='Image clips the far end. Visible 128-pixel span is completed to a symmetric ten-tile bridge; full unseen length is an explicit estimate.'),
 family('poke_i.jpg','PokeI_ArchedTimberBridge','wood',(80,64,64),(253,314,310,357),24,9.5,rail='picket',hump=8,wood=(150,143,98),note='Upper west river crossing: shallow bowed timber deck with pale close-spaced rails. Uses later building calibration of 9.5 displayed pixels/tile.'),
 family('poke_i.jpg','PokeI_FlatTimberBridge','wood',(64,56,56),(266,394,311,430),24,9.5,rail='picket',wood=(150,143,98),note='Lower west crossing; shorter and flat, with paired pale timber rails.'),
 family('poke_i.jpg','PokeI_NarrowPlankBridge','wood',(64,40,40),(333,350,365,394),24,9.5,rail='none',wood=(150,143,98),note='North-south central crossing with broad transverse plank joints and low edge beams. Rotate this X-running model 90 degrees.'),
 family('poke_m.png','PokeM_DiagonalDeckBridge','wood',(80,48,40),(350,686,435,742),24,rail='none',diagonal=True,bolts=True,wood=(191,149,64),note='Gold diagonal-board deck, timber border and four light metal L-corner plates. Hidden beams/short bank supports inferred; no rail added.'),
 family('poke_p.png','PokeP_GullyPlankBridge','wood',(144,64,64),(646,394,794,495),40,rail='posts',approach=24,wood=(205,175,125),note='Repeated east-west gully crossings: six-tile deck plus bank-anchor margin, three independent-looking posts at each corner; no connecting rails.'),
 family('poke_p.png','PokeP_ShortGullyBridge','wood',(128,64,64),(532,895,635,1045),40,rail='posts',approach=24,wood=(205,175,125),note='Shorter north-south five-tile crossing, same construction; rotate 90 degrees. Adjacent gray diagonal ramp is terrain stairs, not part of this bridge.'),
 family('poke_s.jpg','PokeS_IvyStoneBridge','stone',(112,48,80),(580,335,657,385),48,10,rail='stone',bays=[0,112],stone=(190,194,173),paving=(190,194,173),ivy=True,note='Eastern pale garden bridge over water: slab paving, single open arch, solid coping and ivy. Other pale linear details are garden walls/edging, already covered.'),
 family('poke_t.png','PokeT_TubularRailBridge','wood',(128,48,64),(541,268,677,322),32,rail='metal',wood=(158,116,65),note='Eight-tile timber crossing with rounded metal hoop rails. Northern/southern horizontal copies and the two vertical views reuse this model with rotations.'),
 family('poke_u.jpg','PokeU_ShortIslandBridge','wood',(64,32,40),(126,46,161,113),24,rail='none',slats=16,gap=1,sag=2,wood=(160,145,111),note='Upper floating-island crossing, four broad plank sections; low underside ties and bank anchors inferred, no handrail.'),
 family('poke_u.jpg','PokeU_LongIslandBridge','wood',(96,32,40),(272,238,304,339),24,rail='none',slats=16,gap=1,sag=3,wood=(160,145,111),note='Lower crossing is six plank sections long. Shallow sag and hidden ties inferred; same source palette as upper span.')]
# Palette slots: 1-4 timber, 5-8 masonry/coping, 9-12 paving,
# 13-15 metal, 16-18 ivy. Flat colors merge masonry and paving.
GROUP={i:(1 if i<=4 else 5 if i<=12 else 13 if i<=15 else 16) for i in range(1,19)}
ALLOWED={1:list(range(177,181))+list(range(225,231))+list(range(233,239)),5:list(range(193,197))+list(range(201,207)),13:list(range(193,197)),16:list(range(241,247))}
def palette(f):
 def shades(rgb):return [tuple(max(0,min(255,round(v*k))) for v in rgb)+(255,) for k in [1,.77,1.15,.90]]
 p=shades(f.get('wood',(150,109,65)))+shades(f.get('stone',(150,151,133)))+shades(f.get('paving',f.get('stone',(150,151,133))))
 if f['source']=='poke_d.png':
  rgb=f['paving'];p[8:12]=[tuple(round(v*k) for v in rgb)+(255,) for k in [1,.88,1.06,.96]]
 p += [(167,178,180,255),(112,129,134,255),(205,215,210,255),(102,148,82,255),(131,171,103,255),(75,114,65,255)]
 return p+[(0,0,0,255)]*(256-len(p))
def nearest(p,i):return min(ALLOWED[GROUP[i]],key=lambda k:sum((p[i-1][j]-CP[k-1][j])**2 for j in range(3)))
class Sculpt:
 def __init__(self,f,cartoon):self.f=f;self.size=f['size'];self.v={};self.c=cartoon
 def box(self,a,b,c):
  for x in range(max(0,a[0]),min(b[0],self.size[0])):
   for y in range(max(0,a[1]),min(b[1],self.size[1])):
    for z in range(max(0,a[2]),min(b[2],self.size[2])):self.v[x,y,z]=c
 def height(self,x):
  L=self.size[0];t=min(x,L-1-x)/(max(1,(L-1)/2));curve=2*t-t*t
  if self.c:curve=round(curve*4)/4
  return self.f['deck']+round(self.f.get('hump',0)*curve)-round(self.f.get('sag',0)*curve)
 def rail(self,kind,start,end):
  L,D,H=self.size;thick=3 if self.c else 2
  if kind=='none':return
  for side in [3,D-4]:
   if kind in ('picket','metal'):
    for x in range(start,end):
     h=self.height(x);self.box((x,side-1,h-2),(x+1,side+2,h+2),13 if kind=='metal' else 2)
    xs=set(range(start+2,end-2,8 if kind=='picket' else 16));xs|={L-1-x for x in xs}
    for x in sorted(xs):
     h=self.height(x);self.box((x-1,side-1,h-3),(x+thick,side+thick,h+16),13 if kind=='metal' else 1)
    for x in range(start,end):
     h=self.height(x);self.box((x,side-1,h+11),(x+1,side+thick,h+14+(1 if self.c else 0)),13 if kind=='metal' else 3)
    if kind=='metal':
     # Rounded shoulders in each repeated hoop, not a featureless bar.
     for x in range(start+2,end-2,16):
      h=self.height(x)
      for dx in [0,1,13,14]:self.box((x+dx,side-1,h+9),(x+dx+1,side+2,h+12),13)
   elif kind=='posts':
    for x in [4,12,20,L-21,L-13,L-5]:
     h=self.height(x);self.box((x-1,side-1,0),(x+2,side+2,h+12),1)
     self.box((x-1,side-1,h+12),(x+2,side+2,h+14),3)
   else:
    idx=1 if kind=='woodsolid' else 5
    for x in range(L):
     h=self.height(x);self.box((x,side-1,h),(x+1,side+3,h+12),idx)
     self.box((x,max(0,side-2),h+12),(x+1,min(D,side+4),h+15+(1 if self.c else 0)),3 if idx==1 else 7)
    for x in sorted(set([2,L-3]+self.f.get('bays',[])[1:-1])):
     h=self.height(max(0,min(L-1,x)));self.box((x-3,side-3,h),(x+4,side+4,h+19),idx)
     self.box((x-3,side-3,h+19),(x+4,side+4,h+21),3 if idx==1 else 7)
 def wood(self):
  f=self.f;L,D,H=self.size;a=f.get('approach',0);pitch=f.get('slats',8);gap=f.get('gap',0);decklo=8;deckhi=D-8
  # Longitudinal beams remain connected across plank seams and curved decks.
  for x in range(a,L-a):
   h=self.height(x)
   for y in [decklo,deckhi-4]:self.box((x,y,h-8-(1 if self.c else 0)),(x+1,y+4,h-2),2)
   if (x-a)%pitch>=pitch-gap:continue
   self.box((x,decklo,h-4),(x+1,deckhi,h),1)
   for y in range(decklo,deckhi):
    xx=min(x,L-1-x) if self.c else x;yy=min(y,D-1-y) if self.c else y
    value=1 if self.c else [1,3,1,4][(x//pitch)%4]
    if f.get('diagonal'):value=2 if (xx+yy)%(12 if self.c else 8)==0 else 1
    elif xx%pitch==0:value=2
    elif not self.c and yy%11==0 and x%pitch>2:value=4
    self.v[x,y,h-1]=value
  if not f.get('nopiles'):
   for x in [a,L-a-8]:
    h=self.height(x);self.box((x,2,0),(x+8,D-2,4),2)
    for y in [4,D-10]:self.box((x,y,0),(x+6+(1 if self.c else 0),y+6,h-3),2)
    self.box((x,2,h-5),(x+8,D-2,h-2),1)
  else:
   for x in [a,L-a-4]:self.box((x,decklo,0),(x+4,deckhi,self.height(x)-3),2)
  if a:
   # Concealed bank anchors connect the sparse posts; no rail across the road.
   for x in [0,L-24]:self.box((x,1,0),(x+24,D-1,3),2)
  if f.get('diagonal'):
   for y in [decklo,deckhi-3]:self.box((0,y,f['deck']-3),(L,y+3,f['deck']+1+(1 if self.c else 0)),3)
   for x in [0,L-3]:self.box((x,decklo,f['deck']-3),(x+3,deckhi,f['deck']+1),3)
  if f.get('bolts'):
   for x in ([2,L-3] if f.get('diagonal') else list(range(3,L,8))):
    h=self.height(x)
    for y in [decklo+1,deckhi-2]:
     self.box((x-1,y-1,h-1),(x+1,y+1,h),13)
     if f.get('diagonal'):
      self.box((max(0,x-2),y-1,h),(min(L,x+3),y+1,h+2),13)
      self.box((x-1,max(decklo,y-3),h),(x+1,min(deckhi,y+4),h+2),13)
  self.rail(f['rail'],a,L-a)
 def stone(self):
  f=self.f;L,D,H=self.size;h=f['deck'];bays=f['bays'];course=8 if self.c else 5
  # Arches are cut through the entire depth; no black paint pretending to be air.
  for x in range(L):
   k=next(i for i in range(len(bays)-1) if bays[i]<=x<bays[i+1]);left,right=bays[k:k+2];cx=(left+right-1)/2;r=(right-left)/2-(8 if L>=200 else 10)
   spring=max(4,h-int(r)-10);rise=min(r,h-10-spring)
   arch_top=spring+rise*math.sqrt(max(0,1-((x-cx)/r)**2)) if abs(x-cx)<r else -1
   for y in range(4,D-4):
    for z in range(h):
     if abs(x-cx)<r and z<arch_top:continue
     # Soften the noses of long-bridge piers below their arch spring.
     if L==320 and z<spring:
      pc=min(bays,key=lambda b:abs(x-b));dx=abs(x-pc)
      if y<10 and dx*dx+(10-y)**2>13**2 or y>=D-10 and dx*dx+(y-(D-11))**2>13**2:continue
     c=6 if z%course==0 or (x+(z//course%2)*6)%12==0 else 5
     if arch_top>=0 and arch_top<=z<arch_top+3+(1 if self.c else 0):c=7
     if z==h-1:
      if f['source']=='poke_d.png':
       px,py=(8,6) if self.c else (6,5)
       xx=(x+(y//py%2)*(px//2))%px;yy=y%py
       rounded=((xx-(px-1)/2)/(px/2))**2+((yy-(py-1)/2)/(py/2))**2
       c=10 if rounded>1.05 else [9,9,11,12,9][(x//px*7+y//py*3)%5]
      else:c=10 if y%8==0 or (x+(y//8%2)*8)%16==0 else 9
     self.v[x,y,z]=c
  if self.c:
   # A proud, thick cornice makes Cartoon geometry distinct even on a short arch.
   self.box((0,2,h-4),(L,6,h-1),7);self.box((0,D-6,h-4),(L,D-2,h-1),7)
  self.rail(f['rail'],0,L)
  if f.get('ivy'):
   for (x,y,z),c in list(self.v.items()):
    if c not in (5,6,7) or z<6 or z>h+10:continue
    if y in (4,D-5,1,D-3) and (min(x,L-1-x)+z//8)%21<3:self.v[x,y,z]=16 if self.c else 16+(z//5)%3
 def finish(self):
  (self.stone if self.f['kind']=='stone' else self.wood)()
  if self.c:
   # Preserve directional ramps, but regularize both banks and both guards.
   # Every bridge is bilateral across its longitudinal center plane, paint too.
   L,D,H=self.size
   for p,c in list(self.v.items()):
    x,y,z=p
    if y<D//2:self.v[x,D-1-y,z]=c
   for p in list(self.v):
    x,y,z=p
    if y>=D//2 and (x,D-1-y,z) not in self.v:del self.v[p]
  # Tiny railing overhangs are allowed; every occupied coordinate stays in canvas.
  assert all(all(0<=p[i]<self.size[i] for i in range(3)) for p in self.v)
  return self.v
def run():
 old=json.loads((HERE/'manifest.json').read_text()) if (HERE/'manifest.json').exists() else {'models':[]};known={r['file']:r['sha256'] for r in old['models']}
 baseline=HERE/'preserved-hashes.json'
 if not baseline.exists():baseline.write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'output').glob('*/*.vox') if p.relative_to(ROOT).as_posix() not in known},indent=2))
 rows=[];families=[]
 for f in F:
  folder=ROOT/'output'/Path(f['source']).stem;support=folder/'bridges';(support/'reference').mkdir(parents=True,exist_ok=True)
  Image.open(ROOT/f['source']).crop(f['crop']).resize(((f['crop'][2]-f['crop'][0])*3,(f['crop'][3]-f['crop'][1])*3),Image.Resampling.NEAREST).save(support/'reference'/(f['name']+'.png'))
  p=palette(f);mapping={i:nearest(p,i) for i in range(1,19)};geo={False:Sculpt(f,False).finish(),True:Sculpt(f,True).finish()}
  for g in geo.values():assert len(components(g))==1,(f['name'],'disconnected',components(g)[:8])
  assert set(geo[False])!=set(geo[True]),(f['name'],'cartoon geometry unchanged')
  fam={**f,'source_sha256':sha(ROOT/f['source']),'crate_mapping':mapping,'palette_rgb':[list(c) for c in p[:18]]};families.append(fam)
  for style in STYLES:
   g=geo['Cartoon' in style];flat='TwoColor' in style;crate='CratePalette' in style
   v={point:(mapping[GROUP[c] if flat else c] if crate else GROUP[c] if flat else c) for point,c in g.items()}
   path=folder/(f['name']+('' if style=='Base' else '_'+style)+'.vox');rel=path.relative_to(ROOT).as_posix()
   if path.exists() and sha(path)!=known.get(rel):raise RuntimeError('Protecting modified/unowned file '+rel)
   pal=CP if crate else p;write(path,f['size'],v,pal);size,actual,ap,nmodels=read(path);assert size==tuple(f['size']) and actual==v and ap==pal
   rows.append({'family':f['name'],'file':rel,'source':f['source'],'style':style,'canvas':f['size'],'scene_models':nmodels,'voxels':len(v),'colors':len(set(v.values())),'occupied_min':[min(q[i] for q in v) for i in range(3)],'occupied_max':[max(q[i] for q in v) for i in range(3)],'sha256':sha(path),'geometry_source':f['name']+('_Cartoon' if 'Cartoon' in style else ''),'geometry_sha256':hashlib.sha256(b''.join(struct.pack('<HHH',*q) for q in sorted(v))).hexdigest()})
  print(f['name'],len(geo[False]),flush=True)
 assert all(sha(ROOT/p)==h for p,h in json.loads(baseline.read_text()).items())
 (HERE/'manifest.json').write_text(json.dumps({'date':'2026-11-03','palette_sha256':CPDATA['palette_sha256'],'families':families,'models':rows},indent=2))
 (HERE/'catalogue.json').write_text(json.dumps(F,indent=2))
 print('PASS',len(rows),'models')
if __name__=='__main__':run()
