"""Local crown dispatch and curved palm fronds for poke_o."""
import math
from profiles import build as profile_build
from leaves import build as leaf_build
from voxlib import components

def build(kind,n,h,cartoon,decor):
 if kind=='leafy':return leaf_build('droop',n,h,cartoon,None)
 if kind!='palm':return profile_build(kind,n,h,cartoon,None)
 c=(n-1)/2;v={};g={}
 def put(x,y,z,col,group):
  if 0<=x<n and 0<=y<n and 0<=z<h:v[x,y,z]=col;g[x,y,z]=group
 # Solid trunk with ringed bark and modest root flare.
 for z in range(int(h*.90)):
  cx=c if cartoon else c+math.sin(z/h*2)*.7
  rad=n*.065+(n*.05*(1-z/5) if z<5 else 0)
  for x in range(n):
   for y in range(n):
    if (x-cx)**2+(y-c)**2<=rad*rad:put(x,y,z,7 if z%5==0 else 8,'wood')
 # Eight balanced arching blades in Cartoon; seven varied blades in Base.
 count=8 if cartoon else 7
 for j in range(count):
  a=j*math.tau/count+(0 if cartoon else .05*math.sin(j*3));co=math.cos(a);si=math.sin(a)
  length=n*.47*(1 if cartoon else .94+.06*math.cos(j*2))
  for step in range(81):
   t=step/80;r=t*length
   zc=h-h*.1+h*.05*math.sin(math.pi*t)-h*.275*t*t
   width=.65+n*.1*math.sin(math.pi*t)**.8
   # Repeated shallow edge notches imply compound leaves without floating pieces.
   width*=.82 if .15<t<.9 and int(t*14)%2==0 else 1
   cx=c+r*co;cy=c+r*si
   for x in range(max(0,int(cx-width-2)),min(n,int(cx+width+3))):
    for y in range(max(0,int(cy-width-2)),min(n,int(cy+width+3))):
     tangent=-(x-cx)*si+(y-cy)*co;along=(x-cx)*co+(y-cy)*si
     if abs(along)>.8 or abs(tangent)>width:continue
     for z in range(max(0,int(zc)-1),min(h,int(zc)+2)):
      if abs(z-zc)<=1:
       col=5 if abs(tangent)<.8 else (3 if t>.65 else 4)
       put(x,y,z,col,'foliage')
 # Upright central unfurling leaves join all fronds and define occupied height.
 for z in range(int(h*.86),h):
  radius=2.2 if z<h-2 else 1
  for x in range(n):
   for y in range(n):
    if (x-c)**2+(y-c)**2<=radius*radius:put(x,y,z,6,'foliage')
 if cartoon:
  canonical={p:(v[p],g[p]) for p in v if p[0]>=n//2 and p[1]>=n//2};v={};g={}
  for (x,y,z),(col,group) in canonical.items():
   for xx,yy in [(x,y),(n-1-y,x),(n-1-x,n-1-y),(y,n-1-x)]:put(xx,yy,z,col,group)
 assert len(components(v))==1,(kind,cartoon,components(v))
 return v,g
