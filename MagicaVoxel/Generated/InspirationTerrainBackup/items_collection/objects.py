from voxlib import Model
import math,hashlib

def glyph(m,name,x,y,z,c=7):
 bits=int(hashlib.sha256(name.encode()).hexdigest()[:4],16)
 for a in range(3):
  for b in range(3):
   if bits & (1<<(a*3+b)):m.put(x+a,y,z+b,c)
def stim(name,v):
 m=Model();h=8+v
 if v in (0,1):
  m.cylinder(0,0,3,h,1 if v==0 else 2,8);m.cylinder(0,0,4,h-1,0,7)
  m.box(0,0,0,0,0,2,1);m.box(-2,2,0,0,h+1,h+1,1);m.box(0,0,0,0,h+2,h+3,1);m.box(-1,1,-1,1,h+4,h+4,5)
 else:
  m.box(-1,1,-1,1,2,h,6);m.box(-1,1,-1,-1,4,7,7);m.box(-1,1,-1,1,0,1,1);m.box(-1,1,-1,1,h+1,h+2,2)
  if v==3:m.box(-3,-2,-2,2,1,h+1,3);m.box(-2,2,1,2,1,h+1,3)
 return m
def potion(name,v):
 m=Model();r=[2,2,1,3][v];h=[6,7,9,8][v]
 # Hollow real glass vessels, liquids separated by index and headspace.
 for z in range(h):
  radius=(1 if z>=h-2 else r)
  for x in range(-radius,radius+1):
   for y in range(-radius,radius+1):
    if v!=1 and x*x+y*y>radius*radius+1:continue
    wall=z==0 or (z==h-3 and (x!=0 or y!=0)) or abs(x)==radius or abs(y)==radius or (v!=1 and x*x+y*y>(radius-1)**2)
    if wall:m.put(x,y,z,8)
    elif z<h-3:m.put(x,y,z,7)
 m.box(0,0,0,0,h-1,h,4)
 if v==2:m.box(-1,1,-1,1,3,3,5)
 if v==3:m.box(-1,1,-3,-3,2,4,5);glyph(m,name,-1,-4,2,7)
 return m
def ammo(name,v):
 m=Model()
 def bullet(x,y,z,h,r=1):
  m.cylinder(x,y,z,z+h-3,r,5);m.cylinder(x,y,z,z,r+.5,2)
  m.cylinder(x,y,z+h-2,z+h-1,r,1);m.put(x,y,z+h,7)
  if name=='Tracer':m.cylinder(x,y,z+1,z+1,r,7)
 if v==0:bullet(0,0,0,8)
 elif v==1:
  m.cylinder(0,0,0,6,2,7);m.cylinder(0,0,0,1,2,5);m.cylinder(0,0,7,7,2,10)
 elif v==2:
  m.box(-1,9,-1,1,0,1,2)
  for x in (0,4,8):bullet(x,0,1,7)
 else:
  m.box(-4,4,-2,2,0,4,6);m.box(-4,4,-2,2,5,5,2);m.box(-2,2,-3,-3,1,3,10);glyph(m,name,-1,-4,1,7)
  m.box(-2,2,0,0,6,6,4);m.box(-2,-2,0,0,5,6,4);m.box(2,2,0,0,5,6,4)
 return m
def grenade(name,v):
 m=Model()
 if v==0:
  m.ellipsoid(0,0,3,2.5,2.5,3,6)
  for z in (2,4):m.cylinder(0,0,z,z,2.6,2)
  m.box(-1,1,-1,1,6,6,1);m.line((0,0,7),(3,0,4),1)
 elif v==1:
  m.box(0,0,0,0,0,5,3);m.cylinder(0,0,5,9,2,6);m.cylinder(0,0,7,7,2,7)
 elif v==2:
  m.cylinder(0,0,0,7,2,6);m.cylinder(0,0,0,0,2,1);m.cylinder(0,0,7,7,2,1)
  m.box(-1,1,-2,-2,2,5,7);m.box(0,0,0,0,8,9,1)
 else:
  m.ellipsoid(0,0,6,2,2,5,6);m.box(-3,3,0,0,0,3,2);m.box(0,0,-3,3,0,3,2);m.box(0,0,0,0,10,12,7)
 # Effect stripe and compact geometric code are tied to the type, not a random seed.
 surface=min(y for x,y,z in m.v)
 for p,c in list(m.v.items()):
  if p[1]==surface and p[2] in (3,4) and c==6:m.v[p]=7
 if name in ('Fire','Incendiary','Lightning','Shock','Arcane'):m.put(0,0,max(p[2] for p in m.v)+1,9)
 return m
def medical(name,v):
 m=Model();n=4+v
 if 'Bandage' in name or name=='GauzeRoll':
  m.cylinder(0,0,0,2+v%2,2+v//2,10);m.box(0,3+v,-1,1,0,0,10);m.put(0,0,3+v%2,2)
 elif name in ('Splint','Tourniquet'):
  m.box(-1,1,0,1,0,10+v,3 if name=='Splint' else 4)
  for z in (2,7):m.box(-2,2,-1,2,z,z+1,10 if name=='Splint' else 2)
 elif 'Bottle' in name or 'Vial' in name:
  return potion(name,v)
 elif 'Pack' in name or 'Dressing' in name or name=='HerbalPoultice':
  m.ellipsoid(0,0,2,n,2,2,10 if 'Dressing' in name else 6);m.box(-1,1,-2,-2,1,3,7)
  if v%2:m.box(-n,n,0,0,3,3,4)
 elif name=='SalveTin':
  m.cylinder(0,0,0,2,n,5);m.cylinder(0,0,3,3,n,10);m.box(-1,1,-1,1,4,4,7)
 else:
  m.box(-n,n,-2,2,0,5+v%2,6);m.box(-n,n,-2,2,5+v%2,5+v%2,4)
  m.box(-1,1,-3,-3,1,4,10);m.box(-2,2,-3,-3,2,3,10)
  m.line((-2,0,6+v%2),(-2,0,8+v%2),4);m.line((-2,0,8+v%2),(2,0,8+v%2),4);m.line((2,0,8+v%2),(2,0,6+v%2),4)
  if v==3:m.box(n,n+2,-1,1,1,4,5)
 return m
def scroll(name,v):
 m=Model();w=4+v;h=10+v
 if v==0:
  m.box(-w,w,0,0,1,h-1,10)
  for z in (0,h):m.box(-w-1,w+1,-1,1,z,z,3)
  glyph(m,name,-1,-1,h//2,7)
 elif v==1:
  m.cylinder(0,0,0,h,2,10);m.cylinder(0,0,h//2,h//2,2,7);m.box(-2,2,-1,1,0,0,3);m.box(-2,2,-1,1,h,h,3)
 elif v==2:
  m.box(-w,w,0,0,1,h-1,10)
  for x in (-w,w):m.cylinder(x,0,0,h,1,10)
  glyph(m,name,-2,-1,4,7);m.box(-w,w,0,0,0,0,3)
 else:
  m.cylinder(0,0,0,h,2,4);m.cylinder(0,0,0,1,2.5,5);m.cylinder(0,0,h-1,h,2.5,5);m.box(-1,1,-2,-2,4,7,7)
  m.line((2,0,2),(4,0,h-2),4);m.line((4,0,h-2),(2,0,h-1),4)
 return m
def torch(name,v):
 m=Model();h=12+v*2;lamp=any(s in name for s in ('Lantern','Lamp'))
 if lamp:
  m.box(-3,3,-2,2,0,1,2);m.box(-3,3,-2,2,7+v,8+v,2)
  for x in (-3,3):
   for y in (-2,2):m.box(x,x,y,y,1,7+v,5)
  m.box(-2,2,-2,-2,2,6+v,8);m.box(-2,2,2,2,2,6+v,8)
  m.box(-3,-3,-1,1,2,6+v,8);m.box(3,3,-1,1,2,6+v,8)
  m.cylinder(0,0,2,5+v,1,9);m.ring(0,0,10+v,2,2,4)
  if 'Signal' in name:m.box(-2,2,-3,-3,3,5,7)
 else:
  m.box(0,0,0,1,0,h-4,3 if 'Bone' not in name else 10)
  m.cylinder(0,0,h-5,h-2,1+v%2,4)
  m.ellipsoid(0,0,h,1.8+v%2,1.5,3,9);m.put(0,0,h+4,9);m.put(0,0,h+3,9)
  if 'Cage' in name or 'Brazier' in name:
   for x in (-2,2):m.box(x,x,0,0,h-3,h+2,2);m.line((x,0,h-3),(0,0,h-4),2)
  if v==2:m.box(-1,1,-1,1,h-6,h-6,5)
 return m
def food(name,v):
 m=Model();size=3+v*.5
 if name in ('Apple','Pear'):
  m.ellipsoid(0,0,3,size,size,3 if name=='Apple' else 4,7 if name=='Apple' else 13)
  m.box(0,0,0,0,6 if name=='Apple' else 7,7 if name=='Apple' else 8,3);m.line((0,0,7),(2,0,7),13)
 elif name=='Carrot':
  for z in range(7+v):m.cylinder(0,0,z,z,1 if z<3 else 2,12)
  m.line((0,0,7+v),(-2,0,10+v),13);m.line((0,0,7+v),(2,0,10+v),13)
 elif name=='Mushroom':
  m.cylinder(0,0,0,4+v,1,10);m.ellipsoid(0,0,5+v,3,3,2,12);m.put(-1,-2,6+v,10);m.put(1,1,7+v,10)
 elif name in ('Fish','SmokedFish'):
  m.ellipsoid(0,0,2,6+v,1.5,2,1 if name=='Fish' else 12);m.box(5+v,7+v,0,0,0,4,12);m.put(-4-v,-1,3,11)
 elif name in ('RoastMeat','Drumstick','Sausage'):
  m.ellipsoid(0,0,2,4+v,2,2,12);m.box(3+v,6+v,0,0,1,2,10 if name!='Sausage' else 4)
  if v==2:m.box(-2,2,-2,-2,2,2,2)
 elif name in ('CheeseWheel','CheeseWedge'):
  m.cylinder(0,0,0,3+v//2,4+v*.5,5)
  if name=='CheeseWedge':m.v={p:c for p,c in m.v.items() if p[0]>=0 and p[1]<=p[0]}
  for x,y in ((1,-1),(2,0)):m.put(x,y,3,12)
 elif name in ('BreadRoll','BreadLoaf','Baguette','Hardtack','MeatPie'):
  rx={'BreadRoll':3,'BreadLoaf':5,'Baguette':8,'Hardtack':3,'MeatPie':4}[name]+v
  if name=='Hardtack':m.box(-rx,rx,-2,2,0,1,10)
  else:m.ellipsoid(0,0,2,rx,2.5,2,12)
  for x in range(-rx+2,rx,3):m.put(x,0,4 if name!='Hardtack' else 1,10)
 elif name in ('StewBowl','BerryBowl'):
  m.cylinder(0,0,0,2,4+v*.5,3);m.cylinder(0,0,3,3,3+v*.5,12 if name=='StewBowl' else 7)
  for x in (-1,1):m.put(x,0,4,13 if name=='StewBowl' else 7)
 elif name in ('HoneyJar','JamJar'):
  m.cylinder(0,0,0,5+v,2,8);m.cylinder(0,0,1,4+v,1,5 if name=='HoneyJar' else 7);m.cylinder(0,0,6+v,6+v,2,4)
 elif name=='WaterCanteen':
  m.ellipsoid(0,0,4,3+v%2,1.5,4,6);m.box(-1,1,-1,1,8,9+v,2)
  m.line((-3,0,3),(-4,0,8),4);m.line((-4,0,8),(0,0,8),4)
 else:
  m.cylinder(0,0,0,4+v,3,1);m.cylinder(0,0,2,3+v,3,7);m.cylinder(0,0,5+v,5+v,3,2)
 if v==3 and name not in ('Carrot','Baguette','WaterCanteen'):
  # Serving tray joins the food's base rather than floating beneath it.
  low=min(p[2] for p in m.v);m.box(-5,5,-3,3,low-1,low-1,3)
 return m

def focus(name,v):
 m=Model();h=10+v*2
 if name=='Wand':h=14+v*2
 if name=='StaffHead':h=5+v
 if any(k in name for k in ('Wand','Scepter','StaffHead','DiviningRod','TuningFork','RitualDagger')):
  m.box(0,0,0,1,0,h,3);m.box(-1,1,-1,1,1,2,5)
  if 'Fork' in name or 'Rod' in name:
   for x in (-2,2):m.line((0,0,h-3),(x,0,h),5);m.box(x,x,0,0,h,h+4,5)
  elif 'Dagger' in name:
   m.box(-2,2,0,1,h//2,h//2,5);m.line((0,0,h//2),(0,0,h+4),1);m.box(-1,1,0,0,h//2+1,h,1)
  else:
   m.ellipsoid(0,0,h,1 if name=='Wand' else 2,1 if name=='Wand' else 2,2 if name=='Wand' else 3,9);m.box(-2,2,0,0,h-3,h-3,5)
   if name=='Scepter':
    for x in (-3,3):m.line((0,0,h-3),(x,0,h),5);m.box(x,x,0,0,h,h+2,5)
   if name=='StaffHead':m.cylinder(0,0,0,2,2,5)
 elif any(k in name for k in ('Grimoire','Spellbook','Tablet','RuneStone')):
  m.box(-4,4,0,2,0,h,4 if 'book' in name.lower() or name=='Grimoire' else 1)
  m.box(-3,3,0,2,1,h-1,10);m.box(-4,4,-1,-1,0,h,6);glyph(m,name,-1,-2,h//2,9)
  if v>0:m.box(4,5,-1,2,h//2,h//2+1,5)
 elif any(k in name for k in ('Orb','Crystal','Hourglass','Astrolabe','Mirror','SunDisk','Bell','Chalice','Censer','Lantern')):
  m.cylinder(0,0,0,1,3,5);m.cylinder(0,0,2,4,1,5)
  if 'Mirror' in name or 'Astrolabe' in name or 'SunDisk' in name:
   m.ring(0,0,9,4+v,5,5)
   if 'Astrolabe' in name:m.line((-4-v,0,9),(4+v,0,9),5);m.line((0,0,4),(0,0,14),5)
   else:m.ellipsoid(0,0,9,3+v,.5,4,8 if 'Mirror' in name else 9)
  elif 'Hourglass' in name:
   for z in range(4,12+v):m.cylinder(0,0,z,z,1+abs(z-(8+v//2))//2,8)
   m.cylinder(0,0,12+v,12+v,3,5)
   for x in (-3,3):m.box(x,x,0,0,1,12+v,5)
  elif 'Chalice' in name:
   # An actual open cup with a rim, stem and foot.
   for z in range(4,10):
    r=1+(z-4)//2+v*.3
    for x in range(-6,7):
     for y in range(-6,7):
      if max(0,r-1.8)**2<x*x+y*y<=r*r+1 or z==4 and x*x+y*y<=r*r+1:m.put(x,y,z,5)
   m.put(0,-2,7,9)
  elif 'Bell' in name:
   m=Model();m.cylinder(0,0,0,1,4+v*.5,5)
   for z in range(2,7):m.cylinder(0,0,z,z,max(1,4-z//2)+v*.2,5)
   m.cylinder(0,0,7,10+v,1,3);m.box(-1,1,-1,1,11+v,11+v,5)
  elif 'Censer' in name:
   m=Model();m.ellipsoid(0,0,3,3+v*.4,3,3,5)
   for x in (-2,2):m.line((x,0,5),(0,0,12+v),1)
   m.ring(0,0,13+v,1,1,5)
   for x in (-1,1):m.put(x,-2,4,9)
  elif 'Lantern' in name:return torch('CandleLantern',v)
  else:m.ellipsoid(0,0,8,3+v,3,4 if 'Crystal' in name else 3,9)
 elif 'Skull' in name:
  m.ellipsoid(0,0,5,3,2,4,10);m.box(-2,2,-2,0,0,2,10)
  for x in (-1,1):m.put(x,-2,6,11)
  m.put(0,-2,4,11)
  if v==1:m.box(-2,2,-3,-3,1,2,10)
  if v==2:m.line((-2,0,7),(-4,0,10),10);m.line((2,0,7),(4,0,10),10)
  if v==3:m.box(-2,2,0,0,9,10,5);m.put(0,0,11,9)
 elif 'Antler' in name:
  m.box(0,0,0,0,0,6,10)
  for side in (-1,1):
   m.line((0,0,5),(side*(4+v),0,12),10)
   for z in (7,9):m.line((side*(z-5)//2,0,z),(side*(z-4),0,z+3),10)
 elif 'Shell' in name:
  m.ellipsoid(0,0,4,4+v,1.5,4,10)
  for x in (-2,0,2):m.line((0,-2,0),(x,-2,6),5)
 elif 'Feather' in name:
  m.box(0,0,0,0,0,5,3)
  for x in range(-3,4):m.line((0,0,4),(x*2,0,11+v-abs(x)),13 if v%2 else 7)
 elif 'Beads' in name:
  m.ring(0,0,6+v,4+v,5+v,4)
  for x,z in ((0,1),(-4-v,6+v),(4+v,6+v),(0,11+2*v)):m.ellipsoid(x,0,z,1,1,1,7)
 else:
  m.box(-2,2,-1,1,0,h,3);m.box(-3,3,-2,2,h-4,h-2,10);glyph(m,name,-1,-2,3,9)
 if v==3 and m.v:m.put(0,0,min(p[2] for p in m.v),5)
 return m
def relic(name,v):
 if name in ('Spellbook','RuneStone','MagicMirror','CrystalBall','Hourglass'):return focus({'CrystalBall':'Orb','MagicMirror':'MirrorFocus','Hourglass':'HourglassFocus'}.get(name,name),v)
 m=Model()
 if 'Ring' in name or name in ('Bracelet','Circlet','Crown','Belt'):
  radius=2+v//2 if 'Ring' in name else 4+v
  # Horizontal band, hollow inside.
  for z in range(2+(name=='Crown')*2):
   for x in range(-radius,radius+1):
    for y in range(-radius,radius+1):
     if (radius-1.5)**2<x*x+y*y<=radius*radius+1:m.put(x,y,z,5 if name!='Belt' else 4)
  m.box(-1,1,-radius-1,-radius,0,2+v,7 if 'Ring' in name else 5)
  if name=='SignetRing':m.box(-2,2,-radius-2,-radius-1,1,2+v,5)
  if name=='GemRing':m.ellipsoid(0,-radius-2,2+v,1,1,2,9)
  if name=='Bracelet':m.box(-radius,radius,-1,1,1,1,5)
  if name=='Belt':m.box(-2,2,-radius-2,-radius-1,0,2,1)
  if name=='Crown':
   for x,y in ((-radius,0),(0,-radius),(radius,0),(0,radius)):m.box(x,x,y,y,3,5+v,5)
 elif name in ('Amulet','Locket','Pendant','Talisman','Brooch'):
  m.ring(0,0,7,3,5,5);m.ellipsoid(0,-1,2,2+v,1,2,7);m.put(0,-2,2,9)
  if name=='Locket':m.box(-2,2,-2,-1,0,3,5);m.put(0,-3,2,7)
  if name=='Pendant':m.line((0,-1,0),(0,-1,-3-v),9)
  if name=='Talisman':m.box(-2,2,-2,-1,0,4+v,10);glyph(m,name,-1,-3,1,9)
  if name=='Brooch':m.line((-4,-1,2),(4,-1,2),5);m.box(-3,3,-2,-2,1,1,5)
 elif name in ('Compass','PocketWatch'):
  m.ellipsoid(0,0,4,3+v,1,3,5);m.ellipsoid(0,-1,4,2,0.5,2,10);m.line((0,-2,3),(1,-2,5),2);m.ring(0,0,8,1,1,5)
 elif name=='EnchantedKey':
  m.ring(0,0,10+v,2,2,5);m.box(0,0,0,0,0,8+v,5);m.box(0,3,0,0,0,1,5);m.box(0,2,0,0,3,3,5)
 elif name=='FlyingCarpet':
  m.box(-5-v,5+v,-8,8,0,0,6)
  for x in (-5-v,5+v):m.box(x,x,-8,8,0,0,5)
  for y in (-8,8):
   for x in range(-5-v,6+v,2):m.put(x,y+(1 if y>0 else -1),0,5)
  for x in range(-2,3):m.box(x,x,-2,2,0,0,7 if abs(x)==2 else 6)
 elif name=='Gauntlet':
  m.box(-2,2,0,2,0,5,1);m.box(-3,-2,0,1,2,4,1)
  for x in range(-2,3):m.box(x,x,0,1,6,7+x%2+v,1)
  m.box(-2,2,-1,-1,0,1,5)
 else:
  m.box(-3-v%2,3+v%2,-2,2,0,5+v,3 if name=='MusicBox' else 4)
  m.box(-3,3,-2,2,5+v,6+v,5);m.box(-1,1,-3,-3,2,4,7)
  if name=='MusicBox':m.box(4,5,0,0,3,3,5);m.box(5,5,0,0,3,5,5)
  else:m.line((-3,0,6+v),(0,0,10+v),4);m.line((0,0,10+v),(3,0,6+v),4)
 return m
