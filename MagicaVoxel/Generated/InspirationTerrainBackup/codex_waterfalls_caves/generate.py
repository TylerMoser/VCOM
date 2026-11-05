"""Codex versions of waterfalls and cave mouths; isolated from concurrent authors."""
from pathlib import Path
import json,hashlib,math
from PIL import Image
from voxlib import write,read,components
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
CPDATA=json.loads((ROOT/'knowledge/palettes/crate-palette.json').read_text());CP=[tuple(c) for c in CPDATA['rgba']]
F=[]
def fall(src,name,width,drop,crop,**kw):
 f=dict(source=src,name=name,kind='waterfall',width=width,drop=drop,crop=crop,tile_pixels=16,water=(63,153,198),foam=(205,242,230),tiers=1,free=False,pattern='streaks');f.update(kw)
 f['size']=[width+16,max(40,24+f['tiers']*8),math.ceil((drop+12)/16)*16];F.append(f)
fall('pixelwood_c.jpg','PixelwoodC_Codex_CurtainWaterfall',64,32,(254,127,477,269),tile_pixels=48,water=(77,145,179),foam=(153,202,193),pattern='broad',note='Broad blue curtain with a lighter central ribbon and comb-shaped lip/foot foam. 48 displayed pixels per tile; no standing stone or chest included.')
fall('poke_a.jpg','PokeA_Codex_TerraceWaterfall',48,32,(35,209,90,259),tile_pixels=10.5,water=(79,163,205),foam=(214,240,225),note='Repeated short bright-blue terrace falls; western and bridge-adjacent examples share this size. Small white shoreline corners are not separate falls.')
fall('poke_c.png','PokeC_Codex_FiveTierCascade',112,80,(333,154,468,245),tiers=5,water=(31,169,224),foam=(218,245,220),note='Wide upper five-band cascade interpreted as five shallow descending sheets linked by shelves.')
fall('poke_c.png','PokeC_Codex_ThreeTierCascade',96,48,(332,474,438,533),tiers=3,water=(31,169,224),foam=(218,245,220),note='Lower three-band cascade, narrower and shorter than the northern waterfall.')
fall('poke_d.png','PokeD_Codex_UpperWaterfall',80,48,(324,0,423,72),water=(66,130,116),foam=(213,240,210),note='Northern green-water fall with irregular pale crest and a curling foam foot. Inlet is clipped by the image; a short inlet tab is inferred.')
fall('poke_d.png','PokeD_Codex_WideSpillway',112,24,(274,388,397,433),water=(66,130,116),foam=(213,240,210),note='Wide shallow central spillway between rock banks; stretched lip and brief falling curtain.')
fall('poke_d.png','PokeD_Codex_NarrowWaterfall',64,48,(156,428,238,486),water=(66,130,116),foam=(213,240,210),note='Narrower southwest curtain; the adjacent boulders are existing rock assets.')
fall('poke_m.png','PokeM_Codex_FoamySpillway',48,16,(301,452,367,487),water=(81,165,148),foam=(221,248,225),note='Low foamy river lip repeated at about (411,608) and (420,834). Reeds and shore outlines are excluded.')
fall('poke_s.jpg','PokeS_Codex_TallGardenWaterfall',48,112,(103,99,147,189),tile_pixels=10,note='Tall northwestern bounded fall; repeated foam ribs are surface flow bands, not separate solid terraces.')
fall('poke_s.jpg','PokeS_Codex_MediumGardenWaterfall',48,80,(601,86,641,157),tile_pixels=10,note='Northeastern bounded waterfall; rounded foam foot below several flow bands.')
fall('poke_s.jpg','PokeS_Codex_LowGardenWaterfall',48,32,(581,213,622,252),tile_pixels=10,note='Low central-east terrace fall, distinct from the longer northern curtain.')
fall('poke_s.jpg','PokeS_Codex_NarrowGardenWaterfall',32,48,(166,337,211,384),tile_pixels=10,note='Narrow western garden drop; short top-edge and west-central copies reuse this appearance.')
fall('poke_s.jpg','PokeS_Codex_WideGardenWaterfall',48,48,(605,400,644,441),tile_pixels=10,note='Wider short drop below the eastern bridge; matching western drops reuse this family.')
fall('poke_s.jpg','PokeS_Codex_LongIslandWaterfall',48,160,(594,539,638,649),tile_pixels=10,free=True,note='Long central floating-island fall, extended down toward lower water. Foot mist is inferred; no invented rocky bottom basin.')
fall('poke_s.jpg','PokeS_Codex_IslandWaterfall',48,112,(706,536,750,636),tile_pixels=10,free=True,note='Other long island-edge curtains, including the west (about 118,530), use this shorter length. Depth and hidden termination are inferred.')
fall('poke_s.jpg','PokeS_Codex_NarrowIslandWaterfall',32,80,(123,680,161,735),tile_pixels=10,free=True,note='Slender lower-west island drop, partly obscured near the lower end; completed with modest attached mist.')
fall('poke_s.jpg','PokeS_Codex_SoutheastWaterfall',32,96,(838,728,878,800),tile_pixels=10,note='Southeastern narrow curtain terminating into the visible lower stream; differs from the long unbounded curtains.')
fall('poke_u.jpg','PokeU_Codex_UpperRibbonFall',16,64,(180,0,215,48),water=(68,142,170),foam=(177,216,221),free=True,note='Thin blue falling-water ribbon behind the northern house; inlet and lower end are occluded/cropped. 64-voxel completed length is an explicit estimate.')
fall('poke_u.jpg','PokeU_Codex_LowerRibbonFall',16,48,(158,302,216,361),water=(68,142,170),foam=(177,216,221),free=True,note='Lower island notch ribbon with a pale mist foot. Blue atmospheric gaps without a visible water ribbon are excluded.')
def cave(src,name,size,crop,opening,rock,**kw):
 f=dict(source=src,name=name,kind='cave',size=size,crop=crop,opening=opening,rock=rock,tile_pixels=16);f.update(kw);F.append(f)
cave('poke_p.png','PokeP_Codex_RockCaveEntrance',(48,40,48),(269,88,321,132),(20,32),(134,112,88),note='Small pointed pale-rock surround in the upper gully, with a real open tunnel and a recessed earthy floor. Unseen depth is inferred.')
cave('poke_t.png','PokeT_Codex_AmberCaveEntrance',(48,40,48),(912,414,962,463),(24,32),(151,111,70),note='Eastern warm brown rounded cave mouth near the sign; real arch opening, faceted rock brow and short through-tunnel.')
cave('poke_t.png','PokeT_Codex_DeepCavernEntrance',(80,56,80),(470,887,528,956),(36,56),(151,111,70),note='Large irregular southern dark recess reconstructed as a deep cavern mouth. The source black void beyond the entrance is background, not exported geometry; hidden roof/rear tunnel are inferred.')
GROUP={i:(1 if i<=7 else 8 if i<=11 else 12) for i in range(1,16)}
ALLOWED={1:list(range(249,255))+[193,205,206],5:[194,195,196,248,254],8:list(range(177,181))+list(range(225,239))+list(range(201,207)),12:list(range(177,181))+list(range(225,239))}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def palette(f):
 def shade(rgb,ks):return [tuple(min(255,round(v*k)) for v in rgb)+(255,) for k in ks]
 p=shade(f.get('water',(60,150,190)),[1,.81,1.13,.94])+shade(f.get('foam',(220,240,227)),[1,.91,1.04])+shade(f.get('rock',(135,112,86)),[1,.76,1.18,.92])+shade((113,89,61),[1,.8,1.12,.94])
 return p+[(0,0,0,255)]*(256-len(p))
class Sculpt:
 def __init__(self,f,c):self.f=f;self.c=c;self.size=f['size'];self.v={}
 def box(self,a,b,c):
  for x in range(max(0,a[0]),min(self.size[0],b[0])):
   for y in range(max(0,a[1]),min(self.size[1],b[1])):
    for z in range(max(0,a[2]),min(self.size[2],b[2])):self.v[x,y,z]=c
 def waterfall(self):
  f=self.f;W,D,H=self.size;w=f['width'];drop=f['drop'];tiers=f['tiers'];mid=(W-1)/2
  low=4;step=drop//tiers;front=12
  for k in range(tiers):
   z0=low+k*step;z1=low+(k+1)*step;y0=front+8*k
   for x in range(8,W-8):
    xx=min(x,W-1-x) if self.c else x
    for z in range(z0,z1):
     # A curved toe projects forward; thin coherent ribbons add real relief.
     bend=max(0,3-(z-z0)//3);ribbon=1 if xx%9<2 else 0
     y=y0-bend-ribbon;thick=4 if self.c else 3
     for yy in range(y,y0+thick):
      color=1
      if f['pattern']=='broad':color=3 if abs(x-mid)<w*.12 else 1
      elif (xx//3+z//11)%5==0:color=2
      elif xx%7<2:color=3
      if f['source']=='poke_s.jpg' and (z-z0)%16<2:color=3
      elif f['pattern']!='broad' and xx%11<2 and (z+xx//3)%17<5:color=6
      self.v[x,yy,z]=color
    # Rounded-over lip, with irregular connected foam teeth.
    self.box((x,y0,z1-2),(x+1,min(D-1,y0+11),z1+1),1)
    tooth=2 if self.c else 1+(xx*7%4)
    self.box((x,y0-1,z1-tooth),(x+1,y0+3,z1+2),5 if xx%7<5 else 6)
   # Link shelves to the next tier; no disconnected stacked waterfalls.
   if k<tiers-1:self.box((8,y0+3,z1-2),(W-8,y0+12,z1+1),1)
  # A shallow receiving pool or a small water/mist toe for free island falls.
  ry=6 if f['free'] else 12;cy=9 if f['free'] else 11
  for x in range(4,W-4):
   for y in range(max(0,cy-ry),min(D,cy+ry+1)):
    ellipse=((x-mid)/(w/2+3))**2+((y-cy)/ry)**2
    if ellipse>1:continue
    self.box((x,y,0),(x+1,y+1,5),1)
    xx=min(x,W-1-x) if self.c else x
    # Attached foam crescent at the impact, plus low lobes, never floating pixels.
    if .68<ellipse<1 or abs(y-9)<2 and xx%8<5:
     self.box((x,y,3),(x+1,y+1,6+(1 if self.c else xx%3)),5)
  if f['free']:
   # Minimal toe, not a rocky basin; all mist connects to the water sheet.
   for x in range(8,W-8,8):self.box((x,8,4),(x+4,12,9),5)
 def cave(self):
  f=self.f;W,D,H=self.size;ow,oh=f['opening'];cx=(W-1)/2
  for x in range(W):
   dx=abs(x-cx)
   for y in range(D):
    # Broad faceted outer rock mass, tapering behind the sculpted front brow.
    front=max(0,8-y)/8;outer_r=W/2-1-(0 if self.c else (y//7%3))
    if dx>outer_r:continue
    roof=H-5-round((dx/outer_r)**2*(H*.23))
    if not self.c:roof-=((x//7*3+y//8*5)%5)
    if self.c:roof=roof//3*3
    radius=ow/2+(2 if y>8 else 0)
    inner=oh-ow/2+math.sqrt(max(0,radius*radius-dx*dx)) if dx<radius else 0
    for z in range(2,roof):
     if dx<radius and z<inner:continue
     block=(int((x+(z//8%2)*4)//8)*7+(y//7)*3+(z//8)*11)%9
     color=9 if block==0 else 10 if block in [3,7] else 8
     if y<3 and inner and inner<=z<inner+4:color=10
     self.v[x,y,z]=color
  # Real floor and passage, open at both ends. No black plane behind the arch.
  self.box((1,0,0),(W-1,D,2),12)
  for x in range(2,W-2):
   for y in range(D):
    if not self.c and (x//5+y//7)%7==0:self.v[x,y,1]=15
  # Front boulder feet / buttresses stay outside the doorway.
  for x0 in [2,W-9]:
   self.box((x0,0,2),(x0+7,7,9+(2 if self.c else 0)),8)
 def finish(self):
  (self.waterfall if self.f['kind']=='waterfall' else self.cave)()
  if self.c:
   W,D,H=self.size
   for (x,y,z),c in list(self.v.items()):
    if x<W//2:self.v[W-1-x,y,z]=c
   for x,y,z in list(self.v):
    if x>=W//2 and (W-1-x,y,z) not in self.v:del self.v[x,y,z]
  return self.v
def run():
 old=json.loads((HERE/'manifest.json').read_text()) if (HERE/'manifest.json').exists() else {'models':[]};known={r['file']:r['sha256'] for r in old['models']}
 baseline=HERE/'prior-hashes.json'
 if not baseline.exists():baseline.write_text(json.dumps({p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/'output').glob('*/*.vox') if p.relative_to(ROOT).as_posix() not in known},indent=2))
 rows=[];families=[]
 for f in F:
  folder=ROOT/'output'/Path(f['source']).stem;support=folder/'codex_waterfalls_caves';(support/'reference').mkdir(parents=True,exist_ok=True)
  im=Image.open(ROOT/f['source']).crop(f['crop']);im.resize((im.width*3,im.height*3),Image.Resampling.NEAREST).save(support/'reference'/(f['name']+'.png'))
  p=palette(f);mapping={i:min(ALLOWED[5 if 5<=i<=7 else GROUP[i]],key=lambda k:sum((p[i-1][j]-CP[k-1][j])**2 for j in range(3))) for i in range(1,16)}
  geo={False:Sculpt(f,False).finish(),True:Sculpt(f,True).finish()}
  for g in geo.values():assert len(components(g))==1,(f['name'],components(g)[:5])
  assert set(geo[False])!=set(geo[True]),f['name']
  families.append({**f,'source_sha256':sha(ROOT/f['source']),'crate_mapping':mapping})
  for style in STYLES:
   g=geo['Cartoon' in style];flat='TwoColor' in style;crate='CratePalette' in style
   v={q:(mapping[GROUP[c] if flat else c] if crate else GROUP[c] if flat else c) for q,c in g.items()}
   path=folder/(f['name']+('' if style=='Base' else '_'+style)+'.vox');rel=path.relative_to(ROOT).as_posix()
   if path.exists() and sha(path)!=known.get(rel):raise RuntimeError('Protecting modified/unowned file '+rel)
   pal=CP if crate else p;write(path,f['size'],v,pal);sz,actual,ap,n=read(path);assert sz==tuple(f['size']) and actual==v and ap==pal
   rows.append(dict(family=f['name'],file=rel,source=f['source'],style=style,canvas=f['size'],scene_models=n,voxels=len(v),colors=len(set(v.values())),occupied_min=[min(q[i] for q in v) for i in range(3)],occupied_max=[max(q[i] for q in v) for i in range(3)],sha256=sha(path)))
  print(f['name'],len(geo[False]),flush=True)
 (HERE/'manifest.json').write_text(json.dumps(dict(date='2026-11-03',author='Codex',palette_sha256=CPDATA['palette_sha256'],families=families,models=rows),indent=2))
 print('PASS',len(rows),'models')
if __name__=='__main__':run()
