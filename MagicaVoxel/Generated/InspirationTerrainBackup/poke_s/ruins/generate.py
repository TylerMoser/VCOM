"""Source-inspired sky-garden architecture. Run from any directory; protects hand edits."""
from pathlib import Path
import json, math, hashlib, sys
from PIL import Image
from voxlib import write, read, components
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]; OUT=HERE.parent
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
CRATE=json.loads((ROOT/'knowledge/palettes/crate-palette.json').read_text())
CP=[tuple(c) for c in CRATE['rgba']]
# Carefully chosen limestone, recessed mortar, creeping ivy, and inset blue stone.
RGB=[(190,194,173),(218,222,199),(155,164,148),(130,143,128),(105,157,91),(133,180,107),(77,126,75),(140,174,184)]
PAL=[(*c,255) for c in RGB]+[(190,194,173,255)]*248
GROUP={1:1,2:1,3:1,4:1,5:5,6:5,7:5,8:8}
ALLOWED={1:list(range(193,197)),5:list(range(241,247)),8:list(range(249,255))}
def nearest(c,group):return min(ALLOWED[group],key=lambda i:sum((CP[i-1][k]-c[k])**2 for k in range(3)))
MAPPING={i:nearest(PAL[i-1],GROUP[i]) for i in range(1,9)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class Sculpt:
 def __init__(self,size,cartoon):self.size=size;self.v={};self.cartoon=cartoon
 def put(self,x,y,z,c=1):
  if 0<=x<self.size[0] and 0<=y<self.size[1] and 0<=z<self.size[2]:self.v[x,y,z]=c
 def box(self,a,b,c=1):
  for x in range(a[0],b[0]):
   for y in range(a[1],b[1]):
    for z in range(a[2],b[2]):self.put(x,y,z,c)
 def masonry(self,x,y,z):
  course=8 if self.cartoon else 5
  if z%course==0 or (x+y+(z//course%2)*6)%12==0:return 3
  return 1 if self.cartoon else (2 if ((x//9)*7+(y//9)*3+z//course)%7==0 else 1)
 def rounded(self,x0,y0,w,d,h,z0=0,inner=False):
  r=min(w,d)//3 if self.cartoon else min(w,d)//4
  def inside(x,y,pad=0):
   xx=max(x0+r-x,0,x-(x0+w-r-1));yy=max(y0+r-y,0,y-(y0+d-r-1))
   return x0+pad<=x<x0+w-pad and y0+pad<=y<y0+d-pad and xx*xx+yy*yy<=(r-pad)**2
  for x in range(x0,x0+w):
   for y in range(y0,y0+d):
    if not inside(x,y):continue
    for z in range(z0,z0+h):
     if inner and inside(x,y,5):continue
     top=z>=z0+h-3
     self.put(x,y,z,2 if top else self.masonry(x,y,z))
 def arch(self,cx,y0,width,spring,depth,z0=0,seal=False):
  r=width/2
  for x in range(int(cx-r-3),int(cx+r+4)):
   for z in range(z0,z0+spring+int(r)+4):
    dx=x-cx; dz=z-z0-spring
    opening=abs(dx)<r and (dz<=0 or dx*dx+dz*dz<r*r)
    ring=abs(dx)<r+3 and (dz<=0 or dx*dx+dz*dz<(r+3)**2)
    for y in range(y0,y0+depth):
     if opening:
      self.v.pop((x,y,z),None)
      if seal and y==y0+depth-1:self.put(x,y,z,4 if (z%6 and (x+z//6*4)%10) else 3)
     elif ring:self.put(x,y,z,2)
 def column(self,cx,cy,z0=0,height=64,r=11):
  for z in range(z0,z0+height):
   rr=r+2 if z-z0<4 or z>=z0+height-4 else r
   if self.cartoon and 4<=z-z0<height-4:rr=r+1
   for x in range(cx-rr,cx+rr+1):
    for y in range(cy-rr,cy+rr+1):
     q=(x-cx)**2+(y-cy)**2
     if q<=rr*rr:
      c=2 if z>=z0+height-3 else self.masonry(x,y,z)
      if q>(rr-2)**2 and 7<z-z0<height-7 and (abs(x-cx)//3+abs(y-cy)//3)%3==0:c=5
      self.put(x,y,z,c)
 def ivy(self):
  # Surface-only vines. Cartoon uses mirrored broader strips; no disconnected leaves.
  for (x,y,z),c in list(self.v.items()):
   if c not in (1,3) or z<5:continue
   if all((x+dx,y+dy,z) in self.v for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]):continue
   xx=min(x,self.size[0]-1-x) if self.cartoon else x
   vine=(xx+round(2*math.sin(z/7)))%19
   if vine<3 and z%37<30:self.v[x,y,z]=5 if self.cartoon else [5,6,7][(xx//3+z//4)%3]
 def stairs(self,x,y,width,run,rise,z0=0):
  # Cut the flight out of existing terrace mass before adding the stepped fill.
  for p in list(self.v):
   if x<=p[0]<x+width and y<=p[1]<y+run and p[2]>=z0:del self.v[p]
  for t in range(run):
   h=max(2,((t//4+1)*rise)//(run//4))
   self.box((x,y+t,z0),(x+width,y+t+1,z0+h),2 if t%4==0 else 1)
   self.box((x-3,y+t,z0),(x,y+t+1,z0+h+3),2)
   self.box((x+width,y+t,z0),(x+width+3,y+t+1,z0+h+3),2)
def make(kind,size,cartoon):
 s=Sculpt(size,cartoon);w,d,h=size
 if kind=='Column':s.column(w//2,d//2,0,h-1,11)
 elif kind in ('GardenRotunda','RecessedRotunda'):
  s.rounded(2,2,w-4,d-4,40);s.rounded(2,2,w-4,d-4,7,40,True)
  s.arch((w-1)/2,2,18,20,12,0,kind=='RecessedRotunda')
  # Open arcade is a real tunnel across the base, top terrace remains supported.
  if kind=='GardenRotunda':s.arch((w-1)/2,2,18,20,d-4)
 elif kind=='TempleWing':
  s.rounded(0,0,w,d,48);s.rounded(0,0,w,d,7,48,True)
  s.arch((w-1)/2,0,22,23,12,0,True)
  s.arch(15,0,8,13,4,8,True)
 elif kind=='TempleCore':
  s.rounded(0,64,w,d-64,48)
  s.rounded(0,64,w,d-64,7,48,True)
  s.stairs(w//2-24,0,48,64,48)
  # Remove front parapet across the arrival landing.
  for p in list(s.v):
   if w//2-24<=p[0]<w//2+24 and 64<=p[1]<71 and p[2]>=48:del s.v[p]
  for cx in (24,w-25):
   for cy in (96,d-25):s.column(cx,cy,48,72,12)
  for cx in (36,w-37):
   s.arch(cx,64,16,8,3,16,True)
   for p in list(s.v):
    if abs(p[0]-cx)<7 and p[1]==66 and 16<=p[2]<31:s.v[p]=8
 elif kind=='TerraceGateway':
  s.rounded(0,0,w,d,60);s.arch((w-1)/2,0,32,24,d)
  s.rounded(0,0,w,d,4,60,True)
 elif kind=='SteppedSanctuary':
  s.rounded(0,0,w,d,40);s.rounded(5,48,w-10,d-53,36,40)
  s.stairs(w//2-12,0,24,48,40);s.stairs(w//2-12,48,24,40,36,40)
  for cx in (12,w-13):s.column(cx,d-17,76,30,5)
 elif kind=='CliffSanctuary':
  s.rounded(0,0,w,d,56);s.arch((w-1)/2,0,24,24,18,0,True)
  s.rounded(0,0,w,d,10,56,True)
  for cx in (10,w-11):s.column(cx,10,0,24,4)
 elif kind=='ArcadeWall':
  s.box((0,4,0),(w,d-4,56))
  for p in s.v:s.v[p]=s.masonry(*p)
  for cx in (24,72):s.arch(cx,4,24,23,d-8)
  s.box((0,2,56),(w,d-2,60),2)
  if cartoon:s.box((0,1,54),(w,d-1,58),2)
 elif kind=='TerraceWall':
  s.box((0,3,0),(w,d-3,44))
  for p in s.v:s.v[p]=s.masonry(*p)
  s.box((0,0,44),(w,d,48),2)
  if cartoon:s.box((0,1,42),(w,d-1,44),2)
 elif kind=='TerraceCorner':
  for x in range(w):
   for y in range(d):
    r=18 if cartoon else 14
    if x<r and y<r and (x-r)**2+(y-r)**2>r*r:continue
    for z in range(48):
     cap=z>=44
     if x<(16 if cap else 13) or y<(16 if cap else 13):
      if cap or x>=3 and y>=3:s.put(x,y,z,2 if cap else s.masonry(x,y,z))
 s.ivy()
 # Horizontal terrace floors: staggered pale paving, with grass pockets only
 # on the garden rotundas/wings. Coping and stair treads remain clear.
 floors={'GardenRotunda':[39],'RecessedRotunda':[39],'TempleWing':[47],
         'TempleCore':[47],'TerraceGateway':[59],'SteppedSanctuary':[39,75],
         'CliffSanctuary':[55]}.get(kind,[])
 for p,c in list(s.v.items()):
  x,y,z=p
  if z not in floors or (x,y,z+1) in s.v:continue
  pitch=12 if cartoon else 8
  s.v[p]=3 if y%pitch==0 or (x+(y//pitch%2)*pitch)% (pitch*2)==0 else 1
  if kind in ('GardenRotunda','RecessedRotunda','TempleWing','CliffSanctuary') and x>10 and y>d//2 and (x//10+y//13)%4<2:s.v[p]=5
 return s.v
FAMILIES=[
 ('Column',(32,32,72),(382,11,406,64),'Freestanding ivy-covered round column; cap and foot rings.'),
 ('GardenRotunda',(64,64,48),(241,175,288,233),'Roofless rounded garden terrace with open arched underpass.'),
 ('RecessedRotunda',(64,64,48),(205,239,250,300),'Same terrace form with dark recessed masonry arch, as drawn.'),
 ('TempleWing',(96,112,64),(314,52,379,147),'Rounded elevated garden flank with recessed arched facade; reuse mirrored for opposite side.'),
 ('TempleCore',(192,240,128),(375,10,497,200),'Main raised court, four columns, broad stair, parapet and blue arched inset panels; statue reused separately.'),
 ('TerraceGateway',(96,32,64),(380,239,458,289),'Broad arched facade below the main court, real opening and paved upper ledge.'),
 ('SteppedSanctuary',(80,128,112),(184,651,241,729),'Two stepped rounded terraces, central stair flights and paired upright remnants; cloud-obscured back inferred.'),
 ('CliffSanctuary',(64,64,80),(452,650,497,723),'Small recessed-arch shrine beneath a cliff overhang; roofless garden rim, paired front posts.'),
 ('ArcadeWall',(96,16,64),(655,57,716,131),'Reusable two-bay arched wall derived from eastern raised garden facade; rear inferred.'),
 ('TerraceWall',(64,16,48),(348,308,389,339),'Straight solid masonry garden retaining section with white coping and ivy.'),
 ('TerraceCorner',(32,32,48),(318,97,350,148),'Rounded retaining corner, compatible 48-voxel wall height; place with quarter turns.')]
def run():
 old=json.loads((HERE/'manifest.json').read_text()) if (HERE/'manifest.json').exists() else {'models':[]}
 hashes={r['file']:r['sha256'] for r in old['models']}
 before={str(p.relative_to(ROOT)):sha(p) for p in OUT.glob('*.vox') if str(p.relative_to(ROOT)).replace('\\','/') not in hashes}
 rows=[];families=[];img=Image.open(ROOT/'poke_s.jpg');(HERE/'reference').mkdir(exist_ok=True)
 for kind,size,crop,note in FAMILIES:
  name='PokeS_Ruins'+kind;geos={False:make(kind,size,False),True:make(kind,size,True)}
  img.crop(crop).resize(((crop[2]-crop[0])*4,(crop[3]-crop[1])*4),Image.Resampling.NEAREST).save(HERE/'reference'/f'{name}.png')
  # All architecture is connected; bare surfaces have no detached decoration.
  for g in geos.values():assert len(components(g))==1,(kind,'disconnected')
  families.append({'name':name,'canvas':size,'crop':crop,'interpretation':note,'cartoon':'Broader round corners and columns, regular courses and bilateral vine pattern; functional openings retained.'})
  for style in STYLES:
   geo=geos['Cartoon' in style];flat='TwoColor' in style;crate='CratePalette' in style
   painted={p:(MAPPING[GROUP[c] if flat else c] if crate else GROUP[c] if flat else c) for p,c in geo.items()}
   palette=CP if crate else PAL;path=OUT/(name+('' if style=='Base' else '_'+style)+'.vox');rel=path.relative_to(ROOT).as_posix()
   if path.exists() and hashes.get(rel)!=sha(path):raise RuntimeError('Refusing overwrite: '+str(path))
   write(path,size,painted,palette);rs,rv,rp=read(path);assert rs==size and rv==painted and rp==palette
   assert 255 not in rv.values() and set(rv)==set(geo)
   lo=[min(p[i] for p in rv) for i in range(3)];hi=[max(p[i] for p in rv) for i in range(3)]
   rows.append({'family':name,'file':rel,'style':style,'canvas':size,'voxels':len(rv),'colors':len(set(rv.values())),'occupied_min':lo,'occupied_max':hi,'sha256':sha(path),'geometry_source':name+('_Cartoon' if 'Cartoon' in style else ''),'geometry_sha256':hashlib.sha256(b''.join(bytes(p) for p in sorted(rv))).hexdigest()})
  print(name, len(geos[False]),flush=True)
 assert all(sha(ROOT/p)==v for p,v in before.items())
 (HERE/'preserved-hashes.json').write_text(json.dumps(before,indent=2))
 (HERE/'manifest.json').write_text(json.dumps({'date':'2026-11-03','source':'poke_s.jpg','source_sha256':sha(ROOT/'poke_s.jpg'),'palette_sha256':CRATE['palette_sha256'],'mapping':MAPPING,'semantic_groups':{'stone':[1,2,3,4],'ivy':[5,6,7],'blue_inset':[8]},'families':families,'models':rows},indent=2))
 print('PASS',len(rows),'models; preserved',len(before))
if __name__=='__main__':run()
