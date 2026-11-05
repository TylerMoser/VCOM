"""Layered teardrop leaves reconstructed from poke_d's scalloped sprites."""
import math
from voxlib import components

def noise(x,y,z):
 n=(int(x)*374761393+int(y)*668265263+int(z)*2147483647+1274126177)&0xffffffff
 n=((n^(n>>13))*1274126177)&0xffffffff
 return ((n^(n>>16))&65535)/65535

def interp(t,points):
 for (a,r),(b,s) in zip(points,points[1:]):
  if a<=t<=b:return r+(s-r)*(t-a)/(b-a)
 return 0

def build(kind,n,h,cartoon,decor=None):
 c=(n-1)/2;R=n/2-.5;v={};groups={}
 def put(x,y,z,color,group='foliage'):
  if 0<=x<n and 0<=y<n and 0<=z<h:v[x,y,z]=color;groups[x,y,z]=group
 profiles={
 'tall':[(.08,.22),(.19,.65),(.34,.95),(.48,.87),(.65,.70),(.81,.50),(1,.04)],
 'round':[(.10,.22),(.21,.68),(.39,.96),(.56,.89),(.73,.71),(.87,.42),(1,.04)],
 'compact':[(.10,.25),(.22,.72),(.43,.96),(.63,.85),(.80,.61),(.92,.32),(1,.05)],
 'sapling':[(.10,.20),(.23,.70),(.46,.96),(.69,.77),(.85,.44),(1,.13)],
 'blossom':[(.10,.22),(.20,.64),(.38,.96),(.55,.87),(.71,.66),(.86,.43),(1,.05)]}
 profile=profiles[kind]
 # Filled interior underneath the overlapping leaf volumes.
 for z in range(h):
  t=z/(h-1);rad=R*interp(t,profile)*.83
  if t>=profile[0][0]:rad=max(.76,rad)
  for x in range(n):
   for y in range(n):
    if math.hypot(x-c,y-c)<=rad and rad>0:put(x,y,z,1+min(5,int(t*5)))
 def leaf(cx,cy,cz,angle,width,depth,height,shade,red=False):
  ca=math.cos(angle);sa=math.sin(angle)
  for z in range(max(0,int(cz-height)),min(h,int(cz+height)+2)):
   q=(z-cz)/height
   # Broad rounded shoulder and slightly tapered lower tip, like the source scales.
   taper=1 if q>=-.35 else 1+(q+.35)*.35
   for x in range(max(0,int(cx-width-depth)),min(n,int(cx+width+depth)+2)):
    for y in range(max(0,int(cy-width-depth)),min(n,int(cy+width+depth)+2)):
     dx=x-cx;dy=y-cy;u=-dx*sa+dy*ca;rr=dx*ca+dy*sa
     metric=(u/(width*taper))**2+(rr/depth)**2+q*q
     if metric>1:continue
     # Paint follows each leaf mass, not uncorrelated individual voxels.
     step=(0 if q<-.45 else (1 if q<.35 else 2))
     color=max(1,min(6,shade+step))
     put(x,y,z,color+9 if red else color)
 # A few large imbricated leaves are crucial to this reference's visual identity.
 levels=[.25,.43,.61,.78,.91] if kind=='tall' else ([.29,.52,.74,.91] if kind in ('round','blossom') else [.30,.56,.80,.94])
 if kind=='sapling':levels=[.27,.49,.70,.88]
 for row,t in enumerate(levels):
  radius=R*interp(t,profile)
  count=8 if cartoon else (7 if row%2==0 else 9)
  if kind=='sapling':count=4 if cartoon else 5
  if kind=='blossom' and .70<t<.85:count=4 if cartoon else 5
  width=max(1.05,R*(.32 if kind!='sapling' else .47))
  depth=max(.95,R*.24)
  height=h*(.14 if kind=='tall' else .155)
  if kind=='sapling':height=h*.145
  if t>.85:width*=.83;depth*=.85;height*=.80
  if kind=='blossom' and .70<t<.85:
   radius=R*.91;width=R*.36;depth=R*.28;height=h*.14
  ring=max(0,radius-depth*.83)
  for j in range(count):
   angle=j*math.tau/count+(row%2)*math.pi/count
   if not cartoon:angle+=.04*math.sin(row*3+j)
   cz=t*(h-1)+(0 if cartoon else math.sin(j*2.3+row)*.45)
   shade=2 if cartoon else max(1,min(4,1+int(t*3)+int(noise(j,row,7)>.7)))
   leaf(c+ring*math.cos(angle),c+ring*math.sin(angle),cz,angle,width,depth,height,shade,kind=='blossom' and t>=.74)
 # Top rosette and blossom's red petal cap, with the same green/wood semantics.
 leaf(c,c,h*.92,0,max(1.1,R*.34),max(1.1,R*.34),h*.08,4,kind=='blossom')
 # Structural trunk and roots; restore the central hidden wood after foliage.
 trunk=max(.8,n*.075)
 for z in range(int(h*.72)):
  radius=max(.78,trunk*(1-z/h*.75))
  for x in range(n):
   for y in range(n):
    dx=abs(x-c);dy=abs(y-c)
    roots=z<2 and min(dx,dy)<max(.7,trunk*.45) and max(dx,dy)<trunk*1.8
    if dx*dx+dy*dy<=radius*radius or roots:
     put(x,y,z,8 if cartoon else 7+int(noise(x//2,y//2,z//4)*3),'wood')
 # Enforce exact C4 including overlap paint and sub-voxel raster rounding.
 if cartoon:
  quarter={p:(v[p],groups[p]) for p in v if p[0]>=n//2 and p[1]>=n//2};v={};groups={}
  for (x,y,z),(col,group) in quarter.items():
   for xx,yy in [(x,y),(n-1-y,x),(n-1-x,n-1-y),(y,n-1-x)]:put(xx,yy,z,col,group)
 top=max(p[2] for p in v)
 for z in range(top+1,h):
  for x in [n//2-1,n//2]:
   for y in [n//2-1,n//2]:put(x,y,z,15 if kind=='blossom' else 6)
 assert len(components(v))==1,(kind,cartoon,components(v))
 if cartoon:assert {(n-1-y,x,z):col for (x,y,z),col in v.items()}==v
 return v,groups
