"""Pixelwood solid sculptor: broad crowns, shrub, stump, conifer and pale birch.
Indices 1-6 are foliage (cut end grain for stump), 7-9 are wood/bark.
Deterministic; no dependencies on other image folders.
"""
import math
from voxlib import components

def build(kind,n,h,cartoon,decor=None):
 c=(n-1)/2;R=(n-1)/2;v={};g={}
 def put(x,y,z,col,group):
  if 0<=x<n and 0<=y<n and 0<=z<h:v[x,y,z]=col;g[x,y,z]=group
 def ell(cx,cy,cz,rx,ry,rz,col,group,power=2):
  for x in range(max(0,int(cx-rx)),min(n,int(cx+rx)+2)):
   for y in range(max(0,int(cy-ry)),min(n,int(cy+ry)+2)):
    for z in range(max(0,int(cz-rz)),min(h,int(cz+rz)+2)):
     if abs((x-cx)/rx)**power+abs((y-cy)/ry)**power+abs((z-cz)/rz)**power<=1:
      shade=col
      if group=='foliage':shade=max(1,min(6,col+(z>cz+rz*.35)-(z<cz-rz*.35)))
      put(x,y,z,shade,group)
 def tube(a,b,rad,col=8):
  steps=max(1,int(math.dist(a,b)*2))
  for i in range(steps+1):
   t=i/steps;ell(*[a[k]+(b[k]-a[k])*t for k in range(3)],rad,rad,rad,col,'wood')
 trunk=max(1,n*(.13 if kind=='round' else .09))
 if kind=='stump':
  for z in range(h):
   for x in range(n):
    for y in range(n):
     dx=x-c;dy=y-c;rr=math.hypot(dx,dy);a=math.atan2(dy,dx)
     rad=R*(.75+.22*(1-z/(h-1))**3)
     rad*=1+.035*math.cos(4*a)+(0 if cartoon else .035*math.sin(a*7))
     if rr<=rad:
      if z>=h-2 and rr<rad-1.2:
       shade=4 if cartoon else (3 if int(rr*1.6)%4==0 else 5)
       put(x,y,z,shade,'foliage')
      else:put(x,y,z,8 if cartoon else (7 if int(a*9)%4==0 else 8+int(z>h*.6)),'wood')
 elif kind=='shrub':
  tube((c,c,0),(c,c,h*.45),1.5)
  ell(c,c,h*.38,R*.88,R*.88,h*.32,3,'foliage',3)
  for j in range(4):
   a=math.pi/4+j*math.pi/2
   ell(c+math.cos(a)*R*.65,c+math.sin(a)*R*.65,h*(.72 if cartoon else .72+.018*math.sin(j*2)),R*.43,R*.43,h*.30,5,'foliage',2.5)
 elif kind=='round':
  tube((c,c,0),(c,c,h*.72),trunk)
  for j in range(4):
   a=j*math.pi/2;tube((c,c,5),(c+math.cos(a)*trunk*1.7,c+math.sin(a)*trunk*1.7,0),trunk*.6,7)
  # Low, broad, almost flat-topped mass, with hanging scalloped leaf panels.
  ell(c,c,h*.57,R*.86,R*.86,h*.40,3,'foliage',2.8)
  for tier,(level,ring,width,tall) in enumerate([(.25,.68,.27,.15),(.43,.76,.25,.18),(.63,.68,.26,.18),(.80,.51,.27,.16)]):
   count=8 if cartoon else 12
   for j in range(count):
    a=j*math.tau/count+(tier%2)*math.pi/count
    if not cartoon:a+=.04*math.sin(j*2+tier)
    ell(c+math.cos(a)*R*ring,c+math.sin(a)*R*ring,h*level,R*width,R*width,h*tall,2+tier,'foliage',2.5)
  ell(c,c,h*.86,R*.53,R*.53,h*.14,5,'foliage',3)
 elif kind=='conifer':
  tube((c,c,0),(c,c,h*.60),trunk,8)
  for j in range(4):
   a=j*math.pi/2;tube((c,c,3),(c+math.cos(a)*trunk*1.8,c+math.sin(a)*trunk*1.8,0),trunk*.55,7)
  # Three strongly separated triangular whorls, each with long drooping tips.
  for z in range(h):
   t=z/(h-1)
   for x in range(n):
    for y in range(n):
     dx=x-c;dy=y-c;r=math.hypot(dx,dy);a=math.atan2(dy,dx)
     for k,(lo,hi,wide) in enumerate([(.19,.67,1),(.43,.86,.76),(.65,1,.50)]):
      if lo<=t<=hi:
       q=(t-lo)/(hi-lo);edge=.86+.14*math.cos(a*4)
       if not cartoon:edge+=.035*math.sin(7*a+z*.1)
       rad=R*wide*(1-q)**.92*edge
       if r<=max(.76,rad):
        shade=max(1,min(6,1+k+int(q*3)))
        if not cartoon and (int(a*11)+z//3)%7==0:shade=max(1,shade-1)
        put(x,y,z,shade,'foliage')
 elif kind=='birch':
  # Exposed white trunk with short charcoal birch markings.
  for z in range(int(h*.94)):
   for x in range(n):
    for y in range(n):
     if (x-c)**2+(y-c)**2<=(trunk*.8)**2:
      col=7 if z%9 in (3,4) and ((x>c) if z%18<9 else (y>c)) else 9
      put(x,y,z,col,'wood')
  for j in range(4):
   a=j*math.pi/2;tube((c,c,3),(c+math.cos(a)*trunk*1.6,c+math.sin(a)*trunk*1.6,0),trunk*.42,9)
  for tier,(level,width,tall) in enumerate([(.40,.98,.19),(.65,.76,.17),(.86,.48,.14)]):
   ell(c,c,h*level,R*width,R*width,h*tall,3+tier,'foliage',2.6)
   # Leaf skirts in broad vertical folds.
   for j in range(8 if cartoon else 10):
    a=j*math.tau/(8 if cartoon else 10)
    ell(c+math.cos(a)*R*width*.78,c+math.sin(a)*R*width*.78,h*(level-.06),R*width*.20,R*width*.20,h*tall*.7,2+tier,'foliage',2.5)
   if tier<2:
    # Pale exposed branch ends appear as rectangular knots in the reference.
    for j in range(4 if cartoon else 3):
     a=j*math.tau/(4 if cartoon else 3)
     end=(c+math.cos(a)*R*width*.97,c+math.sin(a)*R*width*.97,h*level)
     tube((c,c,h*(level-.10)),end,1.5,7)
     ell(*end,1.35,1.35,1.6,8,'wood',4)
 else:raise ValueError(kind)
 # Reinstall hidden structural core without altering the crown surface.
 if kind not in ('stump','shrub'):
  for p in list(v):
   x,y,z=p
   if z<h*.65 and (x-c)**2+(y-c)**2<(trunk*.48)**2:put(x,y,z,9 if kind=='birch' else 8,'wood')
 if cartoon:
  quarter={p:(v[p],g[p]) for p in v if p[0]>=n//2 and p[1]>=n//2};v={};g={}
  for (x,y,z),(col,group) in quarter.items():
   for xx,yy in [(x,y),(n-1-y,x),(n-1-x,n-1-y),(y,n-1-x)]:put(xx,yy,z,col,group)
 top=max(p[2] for p in v)
 for z in range(top+1,h):
  for x in (n//2-1,n//2):
   for y in (n//2-1,n//2):put(x,y,z,6,'foliage')
 assert len(components(v))==1,(kind,cartoon,components(v))
 return v,g
