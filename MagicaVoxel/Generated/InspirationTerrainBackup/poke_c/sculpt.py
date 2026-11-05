"""poke_c-specific crown profiles and leaf-pad construction; no random state."""
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
 c=(n-1)/2;R=n/2-.5;vox={};groups={}
 def put(x,y,z,col,group):
  if 0<=x<n and 0<=y<n and 0<=z<h:
   vox[x,y,z]=col;groups[x,y,z]=group
 def ball(cx,cy,cz,rx,ry,rz,group):
  for x in range(max(0,int(cx-rx)),min(n,int(cx+rx)+2)):
   for y in range(max(0,int(cy-ry)),min(n,int(cy+ry)+2)):
    for z in range(max(0,int(cz-rz)),min(h,int(cz+rz)+2)):
     q=((x-cx)/rx)**2+((y-cy)/ry)**2+((z-cz)/rz)**2
     if q>1:continue
     if group=='wood':col=8 if cartoon else 7+int(noise(x//2,y//2,z//4)*3)
     else:
      local=(z-(cz-rz))/(2*rz)
      if cartoon:col=3 if local<.35 else (5 if local<.72 else 6)
      else:col=1+max(0,min(5,int(local*4.4+(noise(x//3,y//3,z//3)-.5)*.9)))
     put(x,y,z,col,group)
 trunk=max(.8,n*(.085 if kind in ('spread','cluster') else .07))
 for z in range(int(h*.82)):
  for x in range(n):
   for y in range(n):
    dx=abs(x-c);dy=abs(y-c)
    roots=z<2 and min(dx,dy)<max(.7,trunk*.5) and max(dx,dy)<trunk*1.8
    if dx*dx+dy*dy<max(.8,trunk*(1-z/h*.6))**2 or roots:
     put(x,y,z,8 if cartoon else 7+int(noise(x//2,y//2,z//4)*3),'wood')
 if kind in ('spread','cluster'):
  for j in range(4 if cartoon else 5):
   ang=j*math.tau/(4 if cartoon else 5)+(.12 if not cartoon else 0)
   for step in range(int(R*.75)):
    ball(c+math.cos(ang)*step,c+math.sin(ang)*step,h*.20+step*.8,max(.85,trunk*.6-step*.035),max(.85,trunk*.6-step*.035),1.3,'wood')
 if kind=='cluster':
  # Five visually distinct overlapping pads, a squat crown unlike the forest tree.
  # Reorder leaves low-to-high to retain coherent surface shades at intersections.
  pads=[]
  count=4 if cartoon else 5
  for j in range(count):
   a=j*math.tau/count+(.17 if not cartoon else 0)
   height=.54 if cartoon else .51+.09*math.sin(j*2.1)
   pads.append((c+R*.56*math.cos(a),c+R*.56*math.sin(a),h*height,R*.42,R*.42,h*.215))
  pads.append((c if cartoon else c-R*.07,c if cartoon else c+R*.06,h*.81,R*.47,R*.47,h*.19))
  # C4-equivalent pads have different overlap order, so paint via final coordinate
  # geometry below instead of relying on sphere painter order for Cartoon.
  for p in sorted(pads,key=lambda p:p[2]):ball(*p,'foliage')
 elif kind=='spread':
  for z in range(h):
   t=z/(h-1)
   for x in range(n):
    for y in range(n):
     dx=x-c;dy=y-c;r=math.hypot(dx,dy);a=math.atan2(dy,dx)
     edge=1 if cartoon else 1+.025*math.cos(5*a+z*.12)
     ring=((r-R*.61)/(R*.39*edge))**2+((t-.44)/.145)**2<=1
     capx=c if cartoon else c-R*.09;capy=c if cartoon else c+R*.03
     cap=((x-capx)/(R*.59))**2+((y-capy)/(R*.59))**2+((t-.835)/.17)**2<=1
     if ring or cap:
      local=(t-.25)/.75
      col=(3 if t<.62 else 5) if cartoon else 1+max(0,min(5,int(local*5+(noise(x//3,y//3,z//3)-.5))))
      put(x,y,z,col,'foliage')
 else:
  profiles={
   'forest':[(.06,.18),(.14,.65),(.25,.98),(.32,.87),(.36,1),(.48,.79),(.52,.87),(.65,.63),(.69,.72),(.81,.45),(.85,.49),(.94,.25),(1,.045)],
   'broad':[(.12,.18),(.19,.53),(.31,.88),(.43,1),(.56,.91),(.67,.76),(.72,.79),(.84,.50),(.93,.24),(1,.045)],
   'oval':[(.12,.14),(.20,.63),(.35,.96),(.52,1),(.72,.87),(.88,.51),(1,.13)],
   'topiary':[(.30,.30),(.35,.83),(.46,1),(.59,.74),(.64,.85),(.76,.54),(.81,.64),(.91,.32),(1,.14)]}
  for z in range(h):
   t=z/(h-1);radius=R*interp(t,profiles[kind])
   if t>=profiles[kind][0][0]:radius=max(.76,radius)
   for x in range(n):
    for y in range(n):
     dx=x-c;dy=y-c;r=math.hypot(dx,dy);a=math.atan2(dy,dx)
     c4=(dx**4-6*dx*dx*dy*dy+dy**4)/r**4 if r else 1
     edge=1+.025*c4 if cartoon else 1+.045*math.cos(5*a+z*.15)+.018*math.sin(9*a-z*.25)
     if radius and r<=radius*edge:
      if cartoon:col=3 if t<.45 else (5 if t<.78 else 6)
      else:
       shade=t*4.7+(noise((x+z//6)//3,y//3,z//3)-.5)*.85
       # Leaf skirts carry grouped shade, without salt-and-pepper pixels.
       shade+=.25*math.cos(a*5+z*.37)
       col=1+max(0,min(5,int(shade)))
      put(x,y,z,col,'foliage')
 # Interior trunk remains wood. No hollow shell or disconnected leaf islands.
 for x,y,z in list(vox):
  if z<h*.72 and (x-c)**2+(y-c)**2<(trunk*.52)**2:put(x,y,z,8,'wood')
 if cartoon:
  # Apply the canonical quadrant to pad overlaps as well as painted regions.
  quarter={p:(vox[p],groups[p]) for p in vox if p[0]>=n//2 and p[1]>=n//2}
  vox={};groups={}
  for (x,y,z),(col,group) in quarter.items():
   for xx,yy in [(x,y),(n-1-y,x),(n-1-x,n-1-y),(y,n-1-x)]:put(xx,yy,z,col,group)
 top=max(p[2] for p in vox)
 for z in range(top+1,h):
  for x in [n//2-1,n//2]:
   for y in [n//2-1,n//2]:put(x,y,z,6,'foliage')
 assert len(components(vox))==1,(kind,cartoon,components(vox))
 if cartoon:assert {(n-1-y,x,z):col for (x,y,z),col in vox.items()}==vox
 return vox,groups
