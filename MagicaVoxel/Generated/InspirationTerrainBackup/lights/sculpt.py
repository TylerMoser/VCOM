"""Source-specific complete lighting props. Coordinates are MagicaVoxel Z-up.
Voxels store semantic labels, independent of palette/material treatment.
"""
import math

class Model:
 def __init__(self,size,cartoon=False):self.size=size;self.v={};self.cartoon=cartoon
 def put(self,x,y,z,label):
  p=(int(x),int(y),int(z))
  if all(0<=p[i]<self.size[i] for i in range(3)):self.v[p]=label
 def box(self,x0,x1,y0,y1,z0,z1,label):
  for x in range(x0,x1):
   for y in range(y0,y1):
    for z in range(z0,z1):self.put(x,y,z,label)
 def disc(self,cx,cy,z,r,label):
  for x in range(math.floor(cx-r),math.ceil(cx+r)+1):
   for y in range(math.floor(cy-r),math.ceil(cy+r)+1):
    if (x-cx)**2+(y-cy)**2<=r*r:self.put(x,y,z,label)
 def cylinder(self,cx,cy,z0,z1,r,label):
  for z in range(z0,z1):self.disc(cx,cy,z,r,label)
 def ball(self,cx,cy,cz,rx,ry,rz,label):
  for z in range(math.floor(cz-rz),math.ceil(cz+rz)+1):
   for x in range(math.floor(cx-rx),math.ceil(cx+rx)+1):
    for y in range(math.floor(cy-ry),math.ceil(cy+ry)+1):
     if ((x-cx)/rx)**2+((y-cy)/ry)**2+((z-cz)/rz)**2<=1:self.put(x,y,z,label)

def post(m,cx,cy,h,r=1.5,stone=False):
 label='stone' if stone else 'metal'
 m.cylinder(cx,cy,0,2,4.5,label+'Dark')
 m.cylinder(cx,cy,2,5,3.8,label)
 m.cylinder(cx,cy,5,7,3,label+'Light')
 m.cylinder(cx,cy,7,h,r,label)
 m.cylinder(cx,cy,h-2,h,2.5,label+'Light')

def lantern(m,cx,cy,z,w,h,kind='cap'):
 # Opaque opal diffuser: the visible pale chamber itself emits; no buried bulb.
 r=w/2
 if kind=='cap':
  for k in range(3):m.disc(cx,cy,z+k,r-1+k*.45,'metalDark')
  for k in range(h-7):m.disc(cx,cy,z+3+k,r-1+(k/max(1,h-8))*.5,'light')
  m.cylinder(cx,cy,z+h-4,z+h-2,r,'metalDark')
  for k in range(3):m.disc(cx,cy,z+h-2+k,max(1,r-1-k*1.5),'metalLight' if k==1 else 'metal')
 elif kind=='drum':
  m.cylinder(cx,cy,z,z+2,r-1,'metalDark')
  m.cylinder(cx,cy,z+2,z+5,r-.5,'light')
  m.cylinder(cx,cy,z+5,z+7,r,'metal')
  m.disc(cx,cy,z+7,r-1,'metalLight')
 elif kind=='hood':
  m.cylinder(cx,cy,z,z+2,r-1,'metalDark')
  m.cylinder(cx,cy,z+2,z+h-5,r-1,'light')
  for k in range(4):m.disc(cx,cy,z+h-5+k,max(1,r-k),'metal')
  m.disc(cx,cy,z+h-1,1,'metalLight')

def build(family,cartoon=False):
 m=Model(tuple(family['size']),cartoon);w,d,h=m.size;cx=(w-1)/2;cy=(d-1)/2
 kind=family['shape']
 if kind in ('cap','drum','hood'):
  head=(10 if w==10 else 14) if kind in ('cap','hood') else 8
  post(m,cx,cy,h-head,2 if cartoon else 1.5)
  lantern(m,cx,cy,h-head,(14 if kind in ('drum','hood') else 10) if w>=12 else 7,head,kind)
  if cartoon:
   # Broader balanced chamber and a deliberate double collar.
   m.cylinder(cx,cy,h-head-4,h-head-2,3,'metalLight')
   if kind=='drum':m.cylinder(cx,cy,h-6,h-3,7,'light')
 elif kind=='pixelwood':
  m.box(3,13,3,13,0,4,'metalDark');m.box(4,12,4,12,4,6,'metal')
  m.box(6,10,6,10,6,19,'metal')
  m.box(3,13,3,13,19,21,'metalDark')
  m.box(3,13,3,13,21,31,'light')
  # Dark corner mullions remain apart from the load-bearing post for shadows.
  for x in (2,12):
   for y in (2,12):m.box(x,x+2,y,y+2,21,31,'frame')
  m.box(2,14,2,14,31,33,'metalDark')
  for z in range(33,39):
   inset=(z-33)//2 if cartoon else (z-32)//2
   m.box(2+inset,14-inset,2+inset,14-inset,z,z+1,'metal')
  m.box(6,10,6,10,39,40,'metalLight')
  if cartoon:m.box(5,11,5,11,17,19,'metalLight')
 elif kind=='twin':
  post(m,cx,cy,30,2 if cartoon else 1.5)
  # Two branches rise outward; each step overlaps its neighbor.
  for sign in (-1,1):
   for k in range(10):
    x=cx+sign*k
    m.box(int(x),int(x)+2,int(cy)-1,int(cy)+2,28+k//2,31+k//2,'metal')
   bx=cx+sign*9
   m.cylinder(bx,cy,32,40,1.5,'metal')
   lantern(m,bx,cy,40,11 if cartoon else 10,8,'drum')
  if cartoon:m.cylinder(cx,cy,26,29,3,'metalLight')
 elif kind=='stone':
  for x in (3,10):
   for y in (3,10):m.box(x,x+3,y,y+3,0,3,'stoneDark')
  m.cylinder(cx,cy,2,3,6.5,'stoneDark');m.cylinder(cx,cy,3,5,7,'stone')
  m.cylinder(cx,cy,5,7,5.5,'stoneLight')
  # Four open windows reveal a small warm emitter, even in minimal-colour forms.
  m.box(6,10,6,10,7,12,'light')
  for x in (4,10):
   for y in (4,10):m.box(x,x+2,y,y+2,7,12,'stone')
  m.cylinder(cx,cy,12,14,7.5,'stoneDark')
  for z in range(14,18):m.disc(cx,cy,z,7-(z-14)*(1 if cartoon else 1.3),'stone')
  m.cylinder(cx,cy,18,20,2 if cartoon else 1.5,'stoneLight')
 elif kind=='crook':
  # Ivory fluted upright and a scroll arm carrying a down-hanging lantern.
  px=7.5
  post(m,px,cy,47,2 if cartoon else 1.5)
  for z in (11,15,32,36,44):m.cylinder(px,cy,z,z+2,2.5,'metalLight')
  path=[(8,46),(8,49),(9,51),(11,52),(14,52),(17,51),(18,49),(18,47)]
  if cartoon:path=[(8,46),(8,50),(10,52),(14,52),(17,50),(18,47)]
  for a,b in zip(path,path[1:]):
   steps=max(abs(a[0]-b[0]),abs(a[1]-b[1]))
   for i in range(steps+1):
    x=round(a[0]+(b[0]-a[0])*i/steps);z=round(a[1]+(b[1]-a[1])*i/steps)
    m.box(x,x+2,6,10,z,z+2,'metal')
  lantern(m,18.5,cy,34,8,14,'hood')
  m.cylinder(px,cy,48,56,1,'metalLight')
 elif kind=='fire':
  # A single connected rock ring, crossed charred logs, sculpted flame tongues.
  for x in range(w):
   for y in range(d):
    r=math.hypot(x-cx,y-cy)
    if 8<=r<=11.5:
     sector=int((math.atan2(y-cy,x-cx)+math.pi)*4/math.pi)%8
     for z in range(0,3+(sector%2 if not cartoon else 1)):
      m.put(x,y,z,'stoneLight' if z==2 and sector%2==0 and not cartoon else 'stone')
  m.box(4,20,9,15,1,4,'wood');m.box(9,15,4,20,2,5,'woodDark')
  # Cross sections taper and wander; cartoon has cardinally matched tongues.
  for z in range(4,h):
   t=(z-4)/(h-5)
   radius=max(.8,7*(1-t)**.75)
   ox=0 if cartoon else 2*math.sin(t*7)*t
   oy=0 if cartoon else math.sin(t*9)*1.5*t
   m.disc(cx+ox,cy+oy,z,radius,'flame')
  for dx,dy,top in ([(5,0,20),(-5,0,20),(0,5,20),(0,-5,20)] if cartoon else [(4,1,24),(-4,0,19),(0,-3,21)]):
   for z in range(5,top):m.disc(cx+dx,cy+dy,z,max(.8,3*(1-(z-5)/(top-5))),'flame')
  # Bright core painted on all exposed cardinal surfaces, with no separate islands.
  for p in list(m.v):
   x,y,z=p
   if m.v[p]=='flame' and z<16 and abs(x-cx)+abs(y-cy)<12-(z-4)*.5:m.v[p]='flameLight'
  for (x,y,z),label in sorted(list(m.v.items()),key=lambda item:-item[0][2]):
   if label.startswith('flame') and z>5 and (x,y,z-1) not in m.v:m.put(x,y,z-1,label)
 else:raise ValueError(kind)
 # Broad directional source-style highlights. Cartoon keeps paint symmetric.
 if not cartoon:
  for p,label in list(m.v.items()):
   x,y,z=p
   if label in ('metal','stone') and x<cx-1 and (x-1,y,z) not in m.v:m.v[p]=label+'Light'
 if cartoon:
  # Enforce the declared symmetry on both geometry and labels, resolving overlaps
  # deterministically. Directional fixtures retain their meaningful front/axis.
  symmetry='depth' if kind=='crook' else ('bilateral' if kind=='twin' else 'C4')
  original=dict(m.v);m.v={}
  for (x,y,z),label in sorted(original.items()):
   points=[(x,y,z)]
   if symmetry=='C4':points += [(w-1-y,x,z),(w-1-x,d-1-y,z),(y,d-1-x,z)]
   elif symmetry=='bilateral':points += [(w-1-x,y,z),(x,d-1-y,z),(w-1-x,d-1-y,z)]
   else:points += [(x,d-1-y,z)]
   for p in points:
    if p not in m.v or label>m.v[p]:m.v[p]=label
 return m
