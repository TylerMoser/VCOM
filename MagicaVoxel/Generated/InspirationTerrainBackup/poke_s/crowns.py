"""Tropical crown volumes, connected branches, vines and palm seedling."""
import math
from profiles import build as profile_build
from leaves import build as leaf_build
from palm import build as palm_build
from voxlib import components

def build(kind,n,h,cartoon,decor):
 if kind=='palm':return palm_build('palm',n,h,cartoon,None)
 if kind=='leafconifer':return leaf_build('droop',n,h,cartoon,None)
 if kind in ('pointed','pear','smallcone'):
  return profile_build({'pointed':'broad','pear':'sapling','smallcone':'column'}[kind],n,h,cartoon,None)
 c=(n-1)/2;R=(n-1)/2;v={};g={}
 def put(x,y,z,col,group):
  if 0<=x<n and 0<=y<n and 0<=z<h:v[x,y,z]=col;g[x,y,z]=group
 def ell(cx,cy,cz,rx,ry,rz,col,group):
  for x in range(max(0,int(cx-rx)),min(n,int(cx+rx)+2)):
   for y in range(max(0,int(cy-ry)),min(n,int(cy+ry)+2)):
    for z in range(max(0,int(cz-rz)),min(h,int(cz+rz)+2)):
     q=((x-cx)/rx)**2+((y-cy)/ry)**2+((z-cz)/rz)**2
     if q<=1:
      shade=col
      if group=='foliage':shade=max(1,min(6,col+(1 if z>cz+rz*.25 else 0)-(1 if z<cz-rz*.45 else 0)))
      put(x,y,z,shade,group)
 def tube(a,b,rad,col,group):
  steps=max(1,int(math.dist(a,b)*2))
  for i in range(steps+1):
   t=i/steps;ell(*[a[k]+(b[k]-a[k])*t for k in range(3)],rad,rad,rad,col,group)
 if kind=='seedling':
  tube((c,c,0),(c,c,8),1.4,8,'wood')
  for j in range(8 if cartoon else 7):
   a=j*math.tau/(8 if cartoon else 7)
   for k in range(41):
    t=k/40;rr=R*.95*t;z=5+14*math.sin(math.pi*t)-2*t
    cx=c+math.cos(a)*rr;cy=c+math.sin(a)*rr
    width=.8+1.5*math.sin(math.pi*t)
    ell(cx,cy,z,width,width,1.1,4 if j%2==0 else 3,'foliage')
  tube((c,c,6),(c,c,h-1),.8,5,'foliage')
  ell(c,c,h*.65,2,2,h*.23,4,'foliage')
 else:
  trunk=n*(.085 if kind=='banyan' else .095)
  tube((c,c,0),(c,c,h*.82),trunk,8,'wood')
  for j in range(4):
   a=j*math.pi/2;tube((c,c,4),(c+math.cos(a)*trunk*2,c+math.sin(a)*trunk*2,0),trunk*.6,7,'wood')
  if kind=='ring':
   # A low circular canopy and upper cap leave a deliberate trunk cleft.
   for j in range(12):
    a=j*math.tau/12;cx=c+math.cos(a)*R*.60;cy=c+math.sin(a)*R*.60
    tube((c,c,h*.30),(cx,cy,h*.43),trunk*.48,8,'wood')
    ell(cx,cy,h*.43,R*.40,R*.40,h*.16,3,'foliage')
   ell(c,c,h*.84,R*.57,R*.57,h*.16,4,'foliage')
  elif kind=='flat':
   # Broad thin shelf with four wing-like pads and a separate flattened top.
   ell(c,c,h*.43,R*.88,R*.88,h*.085,3,'foliage')
   for j in range(4 if cartoon else 5):
    a=j*math.tau/(4 if cartoon else 5)
    cx=c+math.cos(a)*R*.60;cy=c+math.sin(a)*R*.60
    tube((c,c,h*.28),(cx,cy,h*.39),trunk*.4,8,'wood')
    ell(cx,cy,h*.39,R*.37,R*.37,h*.10,3,'foliage')
   ell(c if cartoon else c-R*.06,c,h*.90,R*.58,R*.58,h*.10,5,'foliage')
  elif kind=='cluster':
   # Three/four separate lower crowns and one upper crown on branching wood.
   for j in range(4 if cartoon else 3):
    a=j*math.tau/(4 if cartoon else 3)+(.12 if not cartoon else 0)
    cx=c+math.cos(a)*R*.48;cy=c+math.sin(a)*R*.48;cz=h*(.49 if cartoon else .47+.05*math.sin(j))
    tube((c,c,h*.2),(cx,cy,cz),trunk*.60,8,'wood')
    ell(cx,cy,cz,R*.51,R*.51,h*.17,3,'foliage')
   ell(c,c,h*.84,R*.59,R*.59,h*.16,4,'foliage')
  elif kind=='banyan':
   # Broad connected crown, satellite leaf pads and hanging aerial greenery.
   ell(c,c,h*.82,R*.92,R*.92,h*.10,3,'foliage')
   count=8 if cartoon else 7
   for j in range(count):
    a=j*math.tau/count;cx=c+math.cos(a)*R*.49;cy=c+math.sin(a)*R*.49
    tube((c,c,h*.45),(cx,cy,h*.83),trunk*.5,8,'wood')
    ell(cx,cy,h*.88,R*.48,R*.48,h*.12,4,'foliage')
   for j in range(4 if cartoon else 3):
    a=j*math.tau/(4 if cartoon else 3)+(.3 if not cartoon else 0)
    cx=c+math.cos(a)*R*.50;cy=c+math.sin(a)*R*.50;z=h*(.42 if cartoon else .37+.06*j)
    tube((c,c,z*.8),(cx,cy,z),trunk*.32,8,'wood')
    ell(cx,cy,z,R*.24,R*.24,h*.065,3,'foliage')
   for j in range(24 if cartoon else 27):
    a=j*math.tau/(24 if cartoon else 27);rr=R*(.67 if cartoon else .64+.06*math.sin(j*2))
    cx=c+math.cos(a)*rr;cy=c+math.sin(a)*rr
    end=h*(.24 if cartoon else .20+.19*(.5+.5*math.sin(j*1.7)))
    tube((cx,cy,h*.83),(cx,cy,end),.8,2,'foliage')
 if cartoon:
  canonical={p:(v[p],g[p]) for p in v if p[0]>=n//2 and p[1]>=n//2};v={};g={}
  for (x,y,z),(col,group) in canonical.items():
   for xx,yy in [(x,y),(n-1-y,x),(n-1-x,n-1-y),(y,n-1-x)]:put(xx,yy,z,col,group)
 assert len(components(v))==1,(kind,cartoon,components(v))
 return v,g
