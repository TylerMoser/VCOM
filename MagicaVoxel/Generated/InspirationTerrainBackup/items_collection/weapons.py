from voxlib import Model
import math

def sword(name,v):
 m=Model();length={'Dagger':10,'Shortsword':13,'Greatsword':27,'Rapier':23,'Katana':23}.get(name,20)+v
 m.box(-1,1,0,1,0,1,5);m.box(0,0,0,1,2,5,4)
 guard=3 if name not in ('Katana','Dagger') else 2
 m.box(-guard,guard,-1,1,6,6,5)
 if v==1 or name in ('Cutlass','Sabre'):
  m.line((guard,0,6),(guard,0,2),5);m.line((guard,0,2),(0,0,1),5)
 previous=None
 for z in range(7,length+1):
  t=(z-7)/max(1,length-7)
  curve=round(t*t*(4 if name=='Scimitar' else 2)) if name in ('Scimitar','Sabre','Cutlass','Katana') else 0
  width=0 if name in ('Rapier','Dagger') else (2 if name=='Greatsword' else 1)
  if z>length-2:width=max(0,width-1)
  m.box(curve-width,curve+width,0,0 if name=='Rapier' else 1,z,z,1)
  if previous is not None:m.line((previous,0,z-1),(curve,0,z),1)
  previous=curve
  if name!='Rapier' and width:m.put(curve-width,0,z,10)
  if v==2 and z%3==0:m.put(curve,0,z,9)
 if v==3:m.box(-1,1,-1,-1,3,4,7);m.box(-guard-1,-guard,0,1,6,7,5);m.box(guard,guard+1,0,1,6,7,5)
 return m
def axe(name,v):
 m=Model();h={'Handaxe':12,'Battleaxe':19,'GreatAxe':26}.get(name,19)+v
 m.box(0,0,0,1,0,h,3);m.box(0,0,0,1,1,4+v,4)
 for z in range(h-6,h+1):
  radius=4+(v==1)*2-abs(z-(h-3))//2
  for x in range(1,radius+1):
   if v==0 and z<h-3 and x<2:continue
   m.box(x,x,-1,1,z,z,1 if x<radius else 10)
   if v==2 or name=='GreatAxe':m.box(-x,-x,-1,1,z,z,1 if x<radius else 10)
 m.box(-1,1,-1,1,h-3,h-1,5)
 if v==3:m.box(2,3,-2,-2,h-4,h-2,9)
 return m
def hammer(name,v):
 m=Model();h={'LightHammer':11,'Warhammer':18,'GreatHammer':25,'Maul':24}.get(name,18)+v
 m.box(0,0,0,1,0,h-1,3);m.box(0,0,0,1,0,4,4)
 width=3+(name in ('GreatHammer','Maul'))*2
 m.box(-width,width,-1,2,h-4,h,1);m.box(-width,-width,-1,2,h-4,h,5)
 if v==1:m.line((width,0,h-2),(width+3,0,h),1)
 if v==2:
  m.box(-width-1,-width,-2,3,h-3,h-1,1);m.box(width,width+1,-2,3,h-3,h-1,1)
 if v==3:m.box(-1,1,-2,-2,h-3,h-1,9);m.box(-width,width,-1,2,h,h+1,5)
 return m
def melee(name,v):
 if name=='Dagger':return sword(name,v)
 if name=='Maul':return hammer(name,v)
 m=Model();h={'Club':14,'Mace':16,'Staff':29,'Sickle':12,'Spear':30,'Flail':16,'Glaive':30,'Halberd':31,'Lance':34,'Pike':38}[name]+v
 m.box(0,0,0,1,0,h-5,3);m.box(0,0,0,1,1,4+v,4)
 if name=='Club':
  m.ellipsoid(0,.5,h-5,2+v%2,1.6,5,3)
  if v>0:
   for z in (h-7,h-3):m.box(-2,2,-1,2,z,z,2)
  if v==3:m.box(-3,3,0,1,h-4,h-4,1)
 elif name=='Mace':
  m.cylinder(0,0,h-7,h-2,2,1)
  for a in (-3,3):m.box(a,a,0,0,h-6,h-3,5);m.box(0,0,a,a,h-6,h-3,5)
  if v>1:m.box(0,0,0,0,h-1,h+v-1,1)
 elif name=='Staff':
  m.box(0,0,0,1,h-5,h-1,3)
  if v==0:m.ellipsoid(0,0,h,2,2,3,7)
  elif v==1:m.ring(0,0,h,3,3,5)
  elif v==2:m.box(-2,2,-1,1,h-2,h+1,9)
  else:m.line((0,0,h-2),(-3,0,h+2),3);m.line((0,0,h-2),(3,0,h+2),3);m.put(0,0,h-1,9)
 elif name=='Flail':
  m.box(0,0,0,1,h-5,h,3)
  m.line((0,0,h),(4+v,0,h+3),1);m.line((4+v,0,h+3),(6+v,0,h),1)
  m.ellipsoid(6+v,0,h-2,2+v%2,2,2,2);m.box(6+v,6+v,0,0,h-5,h+1,1)
 elif name=='Sickle':
  m.box(0,0,0,1,h-5,h-1,3)
  pts=[(0,0,h-1),(2,0,h+1),(5+v,0,h),(6+v,0,h-3),(4+v,0,h-5)]
  for a,b in zip(pts,pts[1:]):m.line(a,b,1)
 else:
  m.box(0,0,0,1,h-5,h,1)
  for z in range(h-7,h+1):
   w=max(0,2-(z-(h-7))//3)
   m.box(-w,w,0,1,z,z,1)
  if name in ('Glaive','Halberd'):
   for z in range(h-9,h-2):m.box(1,3+(z%3==0),0,1,z,z,1)
  if name=='Halberd':m.line((-4,0,h-6),(0,0,h-5),1)
  if name=='Lance':m.box(-2,2,-1,2,h//3,h//3+1,5)
  if v in (1,3):m.box(-2,2,-1,1,h-9,h-8,5)
  if v==2:m.box(0,0,-1,-1,h-4,h-2,9)
 return m
def gun(name,v):
 m=Model();pistol=name=='Pistol';length=(13 if pistol else 29)+v*2
 if name=='Blunderbuss':length=22+v*2
 if name=='HeavyMachineGun':length=35+v*2
 # Side profile along X, barrel at z=8, stock to left, muzzle right.
 m.box(0,6 if not pistol else 2,-1,1,5,8,3)
 m.box(5 if not pistol else 1,12 if not pistol else 7,-1,1,7,10,2)
 m.box(7 if not pistol else 2,9 if not pistol else 4,-1,1,2,6,4)
 if pistol:
  m.line((4,0,3),(7,0,3),1);m.line((7,0,3),(7,0,7),1)
 else:
  m.line((9,0,3),(13,0,4),1);m.line((13,0,4),(13,0,7),1)
 m.box(12 if not pistol else 6,length,0,1,8,9,1)
 m.box(length,length+1,-1,2,7,10,2)
 m.put(length+1,0,8,11);m.put(length+1,1,9,11)
 m.box(length-2,length-2,0,0,10,11,1)
 if name in ('Shotgun','Blunderbuss'):
  m.box(13,length-2,-1,2,6,7,3)
  if v in (0,2):m.box(12,length,-2,-1,8,9,1)
  if name=='Blunderbuss':
   for x in range(length-5,length+1):
    r=1+(x-(length-5))//2;m.box(x,x,-r,r,8-r,8+r,5)
   m.box(length,length,-2,2,6,10,11)
  if v==1:m.box(16,20,-2,2,5,7,4)
 elif name in ('LightMachineGun','HeavyMachineGun'):
  m.box(13,length-4,-2,2,6,11,2)
  for x in range(15,length-4,3):m.box(x,x,-2,2,6,11,1)
  if v%2:m.box(8,13,-1,1,10,15,2)
  else:m.ellipsoid(10,0,4,4,2,3,2)
  for y in (-4,4):m.line((length-7,0,7),(length-4,y,0),2)
  if name=='HeavyMachineGun':m.line((12,0,6),(5,0,0),2);m.box(13,length-5,-2,2,7,10,1)
 elif name=='Flamethrower':
  m.box(11,length-3,-1,2,5,7,5);m.box(length-2,length,-1,2,6,10,2)
  m.cylinder(5,4,2,12,2,6);m.cylinder(10,4,2,12,2,6)
  m.line((5,2,4),(5,0,4),4);m.line((10,2,4),(10,0,6),4)
  m.box(length, length+1,0,1,5,5,9)
 elif name=='GrenadeLauncher':
  m.box(12,length,-2,2,6,11,2);m.box(length,length,-1,1,7,10,11)
  if v>1:m.ellipsoid(11,0,6,4,3,4,2)
 elif name=='Pistol':
  if v==0 or v==2:m.ellipsoid(6,0,8,2,2,2,1)
  if v==3:m.box(1,5,-1,1,0,3,3)
 if name=='SniperRifle' or v==2:
  m.box(8,9,0,0,11,12,5);m.box(16,17,0,0,11,12,5)
  m.box(7,19,-1,1,13,14,2);m.box(19,19,-1,1,13,14,8)
 if v==1:m.box(3,6,-2,2,5,7,3)
 if v==3:m.box(10,12,-1,0,8,9,5);m.box(10,12,-2,-2,8,9,9);m.box(0,2,-2,2,4,9,5)
 return m
def attachment(name,v):
 m=Model();n=8+v*2
 if name=='Scope':
  m.box(0,n,-1,1,4,6,2);m.box(0,0,-2,2,3,7,5);m.box(n,n,-2,2,3,7,5);m.box(n+1,n+1,-1,1,4,6,8)
  for x in (2,n-2):m.box(x,x,0,0,0,3,1)
  m.box(4,5,-1,1,7,8+v,1)
 elif name=='Stock':
  m.box(0,2,-1,1,0,7+v,3);m.box(3,n,-1,1,3,6,3);m.box(n,n+1,-1,1,4,5,1)
  if v>0:m.box(0,0,-2,2,0,7+v,4)
 elif name=='HairTrigger':
  m.box(0,5+v,0,1,5,6,2);m.line((1,0,5),(3,0,2),1);m.line((0,0,5),(0,0,0),5);m.line((0,0,0),(6+v,0,0),5);m.line((6+v,0,0),(6+v,0,5),5)
 elif name=='ExtendedMagazine':
  for z in range(10+v*2):m.box(z//6,z//6+3,-1,1,z,z,2)
  m.box(0,3,-2,2,0,1,1)
  if v==3:m.ellipsoid(2,0,6,5,2,5,2)
 else:
  m.box(0,n,-1,1,1,4,2);m.box(0,1,-2,2,0,5,1)
  m.box(n-1,n,-2,2,0,5,1);m.line((2,0,5),(n-2,0,5),5)
  for x in range(3,n-1,2):m.box(x,x,-2,-2,2,3,5)
  if name=='AutoLoader':m.box(3,6,-1,1,5,8+v,2)
  else:m.box(n//2,n//2+1,1,3+v,4,4,3)
 return m
def bow(name,v):
 m=Model();cross='Crossbow' in name
 if cross:
  l={'HandCrossbow':10,'LightCrossbow':15,'Crossbow':19,'HeavyCrossbow':24}[name]+v
  m.box(0,1,0,l,5,6,3);m.box(0,1,1,3,0,5,4);m.box(-1,2,l-2,l,4,7,2)
  span=4+v+(name=='HeavyCrossbow')*3
  for side in (-1,1):
   m.line((0,l-3,6),(side*span,l-5,6),3)
   m.line((side*span,l-5,6),(0,l-9,6),10)
  m.box(0,0,4,l,7,7,1);m.box(-1,1,l,l+1,6,8,1)
 else:
  h=(30 if name=='Longbow' else 21)+v
  pts=[(0,0,0),(-3,0,h//5),(-5-v//2,0,h//2),(-3,0,h*4//5),(0,0,h)]
  for a,b in zip(pts,pts[1:]):m.line(a,b,3,0)
  m.line((0,0,0),(0,0,h),10);m.box(-5-v//2,-4-v//2,-1,1,h//2-2,h//2+2,4)
  if name=='CompoundBow':
   m.ring(0,0,2,2,2,2);m.ring(0,0,h-2,2,2,2)
  if v==3:m.box(-5-v//2,-5-v//2,-2,-2,h//2-1,h//2+1,9)
 return m
def thrown(name,v):
 m=Model()
 if name=='Dart':
  m.box(0,0,0,0,0,10+v*2,3);m.box(-1,1,0,0,1,3,7);m.box(0,0,-1,1,1,3,7)
  m.box(-1,1,0,0,9+v*2,10+v*2,1);m.put(0,0,11+v*2,1)
 else:
  m.ellipsoid(0,0,4,2,1,2,4)
  m.line((-1,0,4),(-4-v,0,12+v),4);m.line((1,0,4),(4+v,0,12+v),4)
  m.ring(-4-v,0,13+v,1,1,4)
  if v%2:m.ellipsoid(0,-1,4,1,1,1,1)
 return m
