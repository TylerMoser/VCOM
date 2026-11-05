"""Pastel tree families and pale-trunk ornamental trees for poke_s."""
import math
from voxlib import components
from profiles import build as profile_build
from leaves import build as leaf_build
from crowns import build as crown_build

def build(kind,n,h,cartoon,decor):
 if kind=='tiered':return leaf_build('layered',n,h,cartoon,None)
 if kind=='tall':return leaf_build('droop',n,h,cartoon,None)
 if kind in ('cluster','flat'):return crown_build(kind,n,h,cartoon,None)
 if kind in ('sapling','shrub'):return profile_build('column' if kind=='sapling' else 'compact',n,h,cartoon,None)
 c=(n-1)/2;v={};g={}
 def put(x,y,z,col,group):
  if 0<=x<n and 0<=y<n and 0<=z<h:v[x,y,z]=col;g[x,y,z]=group
 def ball(cx,cy,cz,rad,col,group):
  for x in range(max(0,int(cx-rad)),min(n,int(cx+rad)+2)):
   for y in range(max(0,int(cy-rad)),min(n,int(cy+rad)+2)):
    for z in range(max(0,int(cz-rad)),min(h,int(cz+rad)+2)):
     if (x-cx)**2+(y-cy)**2+(z-cz)**2<=rad*rad:put(x,y,z,col,group)
 def branch(a,b,rad):
  steps=max(1,int(math.dist(a,b)*2))
  for i in range(steps+1):
   t=i/steps;ball(*[a[k]+(b[k]-a[k])*t for k in range(3)],rad,8,'wood')
 # Pale, lightly ringed central trunk and narrow ascending forks.
 for z in range(h-6):
  ball(c,c,z,1.65,7 if z%9==0 else (9 if z%9>5 else 8),'wood')
 ball(c,c,0,2.4,8,'wood')
 def leaf(cx,cy,cz,rx,ry,rz,col):
  for x in range(max(0,int(cx-rx)),min(n,int(cx+rx)+2)):
   for y in range(max(0,int(cy-ry)),min(n,int(cy+ry)+2)):
    for z in range(max(0,int(cz-rz)),min(h,int(cz+rz)+2)):
     q=abs((x-cx)/rx)+abs((y-cy)/ry)+abs((z-cz)/rz)
     if q<=1:put(x,y,z,max(1,min(6,col+(1 if q<.5 else 0))),'foliage')
 for tier,(level,spread) in enumerate([(.40,.30),(.60,.35),(.78,.23)]):
  count=4 if cartoon else 3
  for j in range(count):
   a=j*math.tau/count+(0 if cartoon else tier*.8)
   cx=c+math.cos(a)*n*spread;cy=c+math.sin(a)*n*spread;cz=h*level
   branch((c,c,cz-h*.12),(cx,cy,cz),1.15)
   leaf(cx,cy,cz+2,n*.16,n*.16,h*.12,3+tier)
 # Tall central diamond-shaped tip, joined to the trunk.
 leaf(c,c,h*.89,n*.17,n*.17,h*.11,5)
 if cartoon:
  canonical={p:(v[p],g[p]) for p in v if p[0]>=n//2 and p[1]>=n//2};v={};g={}
  for (x,y,z),(col,group) in canonical.items():
   for xx,yy in [(x,y),(n-1-y,x),(n-1-x,n-1-y),(y,n-1-x)]:put(xx,yy,z,col,group)
 assert len(components(v))==1,(kind,cartoon,components(v))
 return v,g
