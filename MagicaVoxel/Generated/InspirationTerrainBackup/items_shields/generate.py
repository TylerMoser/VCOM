"""32 original shield designs from Brainstorming/Items.txt; deterministic, protected exports."""
from pathlib import Path
import struct,json,hashlib
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
DEST=ROOT.parent/'VoxelXCOM/MagicaVoxel/Items/Shields'
def i(*values):return struct.pack('<'+'i'*len(values),*values)
def s(value):
 b=str(value).encode();return i(len(b))+b
def d(values):return i(len(values))+b''.join(s(k)+s(v) for k,v in values.items())
def chunk(name,body=b'',children=b''):return name.encode()+i(len(body),len(children))+body+children

# type, design, width, height, outline, finish, decoration
DESIGNS=[
('Buckler','IronBoss',7,7,'round','iron','boss'),
('Buckler','BronzeSun',9,9,'round','bronze','sun'),
('Buckler','DuelingSpike',7,9,'oval','iron','spike'),
('Buckler','FlutedGuard',9,9,'octagon','blue','ribs'),
('Wooden','OakPlanks',11,15,'clipped','oak','bands'),
('Wooden','PaintedKite',11,17,'kite','red','chevron'),
('Wooden','ReinforcedPalisade',13,15,'arch','darkwood','bands'),
('Wooden','ForestWard',11,13,'oval','green','tree'),
('Hide','RawhideOval',11,15,'oval','hide','lacing'),
('Hide','TribalSun',13,13,'round','hide','sun'),
('Hide','BoneWard',11,17,'waist','darkhide','bones'),
('Hide','HunterChevron',11,15,'clipped','darkhide','chevron'),
('Steel','KnightHeater',13,17,'heater','blue','cross'),
('Steel','RivetedKite',11,19,'kite','iron','ridge'),
('Steel','RoyalGuard',13,17,'heater','red','diamond'),
('Steel','BlackenedPlate',13,15,'octagon','black','ribs'),
('Tower','LegionScutum',13,23,'arch','red','wings'),
('Tower','OakPavise',15,25,'arch','oak','ridge'),
('Tower','AzureBastion',13,25,'clipped','blue','cross'),
('Tower','IronRampart',15,23,'clipped','black','bands'),
('Fortress','CastleGate',19,29,'battlement','iron','gate'),
('Fortress','DwarvenBulwark',19,27,'octagon','bronze','ribs'),
('Fortress','RoyalWall',19,29,'arch','blue','cross'),
('Fortress','SiegeMantlet',21,27,'clipped','darkwood','bands'),
('Round','VikingQuartered',15,15,'round','red','quarters'),
('Round','BronzeSunburst',15,15,'round','bronze','sun'),
('Round','ForestSpiral',13,13,'round','green','spiral'),
('Round','IronRings',15,15,'round','iron','rings'),
('Ballistic','Patrol',13,21,'clipped','black','viewport'),
('Ballistic','Breacher',15,23,'notched','black','viewport'),
('Ballistic','Riot',13,23,'arch','navy','stripe'),
('Ballistic','HeavyAssault',17,25,'clipped','olive','viewport'),
]
# slots: panel, alternate panel, metal rim, hardware, emblem, grip, glass
FINISH={
'iron':[(104,121,137),(82,99,115),(53,66,80),(189,204,211),(208,173,86)],
'bronze':[(159,108,49),(125,78,37),(78,56,39),(233,184,87),(245,215,135)],
'blue':[(40,83,137),(32,61,103),(74,88,105),(184,200,216),(225,211,151)],
'red':[(146,43,45),(103,34,39),(61,67,79),(184,194,200),(234,196,105)],
'oak':[(151,103,57),(116,74,40),(66,74,84),(175,185,195),(226,198,133)],
'darkwood':[(94,65,42),(66,45,32),(57,65,73),(163,175,184),(211,170,97)],
'green':[(53,99,65),(39,73,48),(89,67,42),(185,153,81),(224,210,142)],
'hide':[(177,132,78),(142,98,58),(86,58,37),(228,203,150),(104,48,35)],
'darkhide':[(113,72,48),(85,49,36),(59,40,31),(225,207,164),(204,154,83)],
'black':[(47,56,65),(34,40,48),(23,29,36),(132,150,162),(220,177,65)],
'navy':[(39,62,80),(29,47,61),(22,29,37),(142,159,171),(199,218,222)],
'olive':[(87,98,65),(62,73,49),(35,43,34),(151,163,142),(216,191,114)],
}
def sha(b):return hashlib.sha256(b).hexdigest()
def footprint(w,h,shape):
 c=w//2
 pts=set()
 for x in range(w):
  for z in range(h):
   u=abs(x-c); t=z/(h-1); a=u/c; b=abs(z-(h-1)/2)/((h-1)/2)
   yes=True
   if shape in ('round','oval'):yes=a*a+b*b<=1.08
   if shape=='octagon':yes=u+abs(z-(h-1)/2)<=c+(h-1)/2-min(w,h)*.23
   if shape in ('clipped','notched'):yes=not(u>c-2 and (z<2 or z>h-3))
   if shape=='notched' and x>w-4 and h*.48<z<h*.65:yes=False
   if shape=='arch':yes=z<h-4 or u<=c-(z-(h-4))
   if shape=='heater':yes=u<=min(c,round(t*c*2.4))
   if shape=='kite':yes=u<=min(c,round(t*c*1.5),round((1-t)*c*6))
   if shape=='waist':yes=u<=round(c-2*(1-b))
   if shape=='battlement' and z>=h-3:yes=(x//3)%2==0
   if yes:pts.add((x,z))
 return pts
def build(row):
 kind,name,w,h,shape,finish,deco=row;c=w//2;mid=h//2
 mask=footprint(w,h,shape);v={};faces={}
 for x,z in sorted(mask):
  edge=any(p not in mask for p in [(x-1,z),(x+1,z),(x,z-1),(x,z+1)])
  # Convex front and two-voxel structural panel, true thickness through edges.
  y=1+(1 if abs(x-c)>w*.28 else 0)
  faces[x,z]=y
  col=3 if edge else (2 if kind in ('Wooden','Round','Tower','Fortress') and (x//3)%2 else 1)
  if kind=='Hide' and not edge:col=1 if (x-c)**2+(z-mid)**2 < (w*.35)**2 else 2
  v[x,y,z]=col;v[x,y+1,z]=2 if not edge else 3
  if edge and z%4==1 and x%2==0:v[x,y,z]=4
 for (x,z),y in faces.items():
  if v[x,y,z]==3:continue
  dx=x-c;dz=z-mid; ax=abs(dx);az=abs(dz);r=(dx*dx+dz*dz)**.5
  mark=False;raised=False;col=5
  if deco in ('boss','spike'):mark=r<=1.5;col=4;raised=True
  if deco=='sun':mark=(ax==0 or az==0 or ax==az) and r<w*.38;raised=r<1.6;col=4 if raised else 5
  if deco=='ribs':mark=(x%4==c%4 or dz==0);col=4;raised=True
  if deco=='bands':mark=z in (h//4,3*h//4);col=3;raised=True
  if deco=='chevron':mark=abs(dz-(ax-2))<=0 or abs(dz-(ax+2))<=0
  if deco=='tree':mark=(dx==0 and az<h*.3) or (dz in (0,3) and ax<=3-dz//2)
  if deco=='lacing':mark=(ax>=c-2 and z%3==1);col=4
  if deco=='bones':mark=ax==az and ax<w*.35;col=4;raised=True
  if deco=='cross':mark=ax==0 or z==int(h*.65)
  if deco=='ridge':mark=dx==0;col=4;raised=True
  if deco=='diamond':mark=ax+az in (3,4);raised=True
  if deco=='wings':mark=(az==ax//2 and ax<w*.4) or (ax==0 and az<h*.3);raised=ax==0
  if deco=='gate':mark=(x in (c-4,c,c+4) and z<h-4) or z==h//3;raised=True;col=4
  if deco=='quarters':mark=(dx>=0)!=(dz>=0);col=5
  if deco=='spiral':mark=(dz==3 and -3<=dx<=3) or (dx==3 and -3<=dz<=3) or (dz==-3 and -3<=dx<=3) or (dx==-3 and -3<=dz<=1) or (dz==1 and -3<=dx<=1) or (dx==1 and -1<=dz<=1)
  if deco=='rings':mark=abs(r-w*.27)<.6 or r<1.5;col=4;raised=True
  if deco=='stripe':mark=z in (4,5,int(h*.72));col=5
  if mark:
   v[x,y,z]=col
   if raised:v[x,y-1,z]=col
 # Central boss on large round shields, independent of paint motif.
 if kind in ('Buckler','Round'):
  for dx in range(-1,2):
   for dz in range(-1,2):
    if abs(dx)+abs(dz)<=1:
     y=faces[c+dx,mid+dz];v[c+dx,y-1,mid+dz]=4
 if deco=='spike':
  # One extra projecting voxel; final normalization keeps coordinates nonnegative.
  v[c,-1,mid]=4
 if deco=='viewport':
  # Actual opening through both layers, filled with one glass layer, metal perimeter.
  z0=int(h*.76)
  for x in range(c-3,c+4):
   for z in range(z0-1,z0+3):
    if (x,z) not in faces:continue
    y=faces[x,z]
    if x in (c-3,c+3) or z in (z0-1,z0+2):v[x,y,z]=4
    else:
     for yy in range(-1,5):v.pop((x,yy,z),None)
     v[x,y,z]=7
 # Back grip: two lugs, two-voxel hand clearance, vertical leather grip.
 # Additional arm strap for the broad shields.
 grips=[c] if w<17 else [c-3,c+3]
 for gx in grips:
  for z in (mid-2,mid+2):
   if (gx,z) not in faces:raise ValueError('Grip outside panel')
   for y in range(faces[gx,z]+2,7):v[gx,y,z]=4 if y<5 else 6
  for z in range(mid-2,mid+3):v[gx,6,z]=6
 miny=min(p[1] for p in v)
 v={(x,y-miny,z):k for (x,y,z),k in v.items()}
 canvas=(w,max(p[1] for p in v)+1,h)
 return canvas,v
def encode(canvas,v,finish):
 colors=FINISH[finish]+[(79,48,33),(169,210,222)]
 palette=[(*c,255) for c in colors]+[(0,0,0,255)]*(256-len(colors))
 body=chunk('SIZE',i(*canvas))+chunk('XYZI',i(len(v))+b''.join(bytes((*p,k)) for p,k in sorted(v.items())))
 body+=chunk('nTRN',i(0)+d({})+i(1,-1,-1,1)+d({}))+chunk('nGRP',i(1)+d({})+i(1,2))
 body+=chunk('nTRN',i(2)+d({'_name':'Shield'})+i(3,-1,0,1)+d({'_t':f'0 0 {canvas[2]//2}'}))
 body+=chunk('nSHP',i(3)+d({})+i(1,0)+d({}))+chunk('LAYR',i(0)+d({'_name':'Shield'})+i(-1))
 body+=chunk('RGBA',b''.join(bytes(c) for c in palette))
 for k in sorted(set(v.values())):
  mat={'_type':'_diffuse','_rough':'.65'}
  if k==7:mat={'_type':'_glass','_trans':'.65','_rough':'.08','_ior':'.5','_ri':'1.5'}
  body+=chunk('MATL',i(k)+d(mat))
 return b'VOX '+i(200)+chunk('MAIN',children=body)
def main():
 DEST.mkdir(parents=True,exist_ok=True)
 previous=json.loads((HERE/'manifest.json').read_text()) if (HERE/'manifest.json').exists() else []
 hashes={r['name']:r['sha256'] for r in previous};pending=[];rows=[]
 for spec in DESIGNS:
  kind,name,w,h,shape,finish,deco=spec;canvas,v=build(spec)
  filename=f'Shield_{kind}_{name}.vox';data=encode(canvas,v,finish);path=DEST/filename
  if path.exists() and sha(path.read_bytes()) not in (hashes.get(filename),sha(data)):raise RuntimeError('Preserving edited file: '+str(path))
  pending.append((path,data));rows.append(dict(name=filename,path=str(path),kind=kind,design=name,canvas=canvas,outline=shape,finish=finish,decoration=deco,voxels=len(v),sha256=sha(data),glass_voxels=sum(k==7 for k in v.values())))
 for path,data in pending:path.write_bytes(data)
 (HERE/'manifest.json').write_text(json.dumps(rows,indent=2))
 print('Wrote',len(rows),'complete shields to',DEST)
if __name__=='__main__':main()
