"""Solid overlapping leaf-cluster trees for poke_q. No sprite shadows included."""
import math
from voxlib import components

def build(kind,n,h,cartoon,decor):
 c=(n-1)/2;v={};groups={}
 def put(x,y,z,col,g):
  if 0<=x<n and 0<=y<n and 0<=z<h:v[x,y,z]=col;groups[x,y,z]=g
 def radius(t):
  points=[(.12,.15),(.24,.65),(.40,1),(.56,.85),(.73,.63),(.88,.32),(1,.04)]
  if kind=='droop':points=[(.12,.15),(.25,.62),(.43,1),(.60,.80),(.77,.52),(.9,.27),(1,.04)]
  if kind=='rounded':points=[(.12,.18),(.24,.70),(.42,1),(.59,.94),(.76,.73),(.9,.38),(1,.05)]
  if kind=='sapling':points=[(.20,.15),(.32,.6),(.48,1),(.65,.85),(.82,.53),(1,.07)]
  for (a,r),(b,s) in zip(points,points[1:]):
   if a<=t<=b:return r+(s-r)*(t-a)/(b-a)
  return 0
 # Connected crown core, darker than the overlapping exterior leaves.
 for z in range(h):
  rad=radius(z/(h-1))*n*.35
  for x in range(n):
   for y in range(n):
    if (x-c)**2+(y-c)**2<=rad*rad:put(x,y,z,max(1,min(5,1+int(z/h*4))),'foliage')
 # Broad elliptical leaves layered from the lower skirt to the crown tip.
 levels=([.28,.45,.62,.79,.94] if kind=='droop' else [.28,.43,.58,.72,.85,.95]) if kind!='sapling' else [.35,.53,.70,.86,.96]
 for tier,t in enumerate(levels):
  count=(8 if cartoon else 12) if n>20 else (4 if cartoon else 8)
  ring=radius(t)*n*.32
  leafwidth=max(1.3,n*(.175 if cartoon else .14)*max(.45,radius(t)))
  leafdepth=max(1.3,n*.165*max(.4,radius(t)))
  leafheight=h*(.17 if kind=='droop' else (.115 if kind!='sapling' else .13))
  if kind=='droop':leafwidth*=.78
  for j in range(count):
   angle=j*math.tau/count+(tier%2)*math.pi/count
   if not cartoon:angle+=.035*math.sin(j*2+tier)
   co=math.cos(angle);si=math.sin(angle)
   cx=c+co*ring;cy=c+si*ring;cz=t*(h-1)
   for z in range(max(0,int(cz-leafheight)),min(h,int(cz+leafheight)+2)):
    for x in range(max(0,int(cx-leafwidth-leafdepth)),min(n,int(cx+leafwidth+leafdepth)+2)):
     for y in range(max(0,int(cy-leafwidth-leafdepth)),min(n,int(cy+leafwidth+leafdepth)+2)):
      dx=x-cx;dy=y-cy;radial=dx*co+dy*si;tangent=-dx*si+dy*co;vertical=(z-cz)/leafheight
      q=(radial/leafdepth)**2+(tangent/leafwidth)**2+vertical**2
      if q<=1:
       # Coherent upper leaf centers with dark lower rims, not random paint noise.
       col=max(1,min(6,2+int(t*4)+(1 if vertical>.2 and abs(tangent)<leafwidth*.55 else 0)-(1 if vertical<-.4 else 0)))
       put(x,y,z,col,'foliage')
 # Woody trunk and roots continue into the solid crown.
 trunk=max(1,n*.075)
 for z in range(int(h*.64)):
  rad=trunk*(1-.35*z/h)
  for x in range(n):
   for y in range(n):
    dx=abs(x-c);dy=abs(y-c)
    root=z<2 and min(dx,dy)<trunk*.65 and max(dx,dy)<trunk*1.7
    if dx*dx+dy*dy<=rad*rad or root:
     put(x,y,z,8 if cartoon else 7+((x//2+y//2+z//5)%3),'wood')
 # Exact cardinal symmetry, including colors, from a canonical quarter.
 if cartoon:
  canonical={p:(v[p],groups[p]) for p in v if p[0]>=n//2 and p[1]>=n//2}
  v={};groups={}
  for (x,y,z),(col,g) in canonical.items():
   for xx,yy in [(x,y),(n-1-y,x),(n-1-x,n-1-y),(y,n-1-x)]:put(xx,yy,z,col,g)
 assert len(components(v))==1,(kind,cartoon,components(v))
 assert max(p[2] for p in v)==h-1
 return v,groups
