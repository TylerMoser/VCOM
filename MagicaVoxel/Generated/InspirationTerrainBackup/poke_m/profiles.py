"""poke_m crowns adapted from the established poke_b geometry, with new profiles."""
import math
from voxlib import components

def noise(x,y,z):
 n=(int(x)*374761393+int(y)*668265263+int(z)*2147483647+1274126177)&0xffffffff
 n=((n^(n>>13))*1274126177)&0xffffffff
 return ((n^(n>>16))&65535)/65535

def lerp(t,profile):
 for (a,r),(b,s) in zip(profile,profile[1:]):
  if a<=t<=b:return r+(s-r)*(t-a)/(b-a)
 return 0

def build(kind,n,h,cartoon,decor):
 c=(n-1)/2;R=n/2-.5;v={};groups={}
 def put(p,col,group):
  if all(0<=p[a]<(n,n,h)[a] for a in range(3)):v[p]=col;groups[p]=group
 def woodball(cx,cy,cz,r):
  for x in range(max(0,int(cx-r)),min(n,int(cx+r)+2)):
   for y in range(max(0,int(cy-r)),min(n,int(cy+r)+2)):
    for z in range(max(0,int(cz-r)),min(h,int(cz+r)+2)):
     if (x-cx)**2+(y-cy)**2+(z-cz)**2<=r*r:put((x,y,z),8 if cartoon else 7+int(noise(x//2,y//2,z//4)*3),'wood')
 # Continuous structural stem, roots and branch forks; complete solid interior.
 trunk= max(.8,n*(.11 if kind in ('spread','giant') else .075))
 for z in range(int(h*.79)):
  rad=max(.8,trunk*(1-z/h*.8))
  for x in range(n):
   for y in range(n):
    dx=abs(x-c);dy=abs(y-c)
    root=z<max(2,int(h*.05)) and min(dx,dy)<max(.7,trunk*.55) and max(dx,dy)<trunk*2
    if dx*dx+dy*dy<=rad*rad or root:put((x,y,z),8 if cartoon else 7+int(noise(x//2,y//2,z//4)*3),'wood')
 if kind in ('spread','giant'):
  for j in range(4 if cartoon else 5):
   angle=j*math.tau/(4 if cartoon else 5)+(.15 if not cartoon else 0)
   for step in range(int(n*.35)):
    woodball(c+math.cos(angle)*step,c+math.sin(angle)*step,h*.22+step*.65,max(1,trunk*.56-step*.055))
 profiles={
 'ball':[(.12,.20),(.22,.66),(.38,.98),(.55,1),(.70,.87),(.84,.63),(.94,.36),(1,.06)],
 'domed':[(.10,.22),(.18,.56),(.30,.86),(.47,1),(.63,.94),(.76,.75),(.87,.48),(1,.045)],
 'compact':[(.09,.19),(.20,.58),(.38,.94),(.52,1),(.70,.86),(.85,.55),(1,.075)],
 'tufted':[(.13,.20),(.20,.58),(.33,.92),(.44,1),(.60,.91),(.74,.72),(.88,.38),(1,.045)],
 'olive':[(.12,.18),(.20,.62),(.37,.98),(.48,1),(.61,.90),(.77,.67),(.89,.33),(1,.045)],
 'stemmed':[(.28,.20),(.37,.70),(.52,1),(.70,.85),(.84,.53),(1,.13)],
 'column':[(.07,.18),(.13,.55),(.23,.90),(.36,1),(.47,.93),(.51,.79),(.55,.88),(.70,.72),(.77,.51),(.80,.58),(.90,.37),(1,.045)],
 'broad':[(.13,.20),(.20,.58),(.33,.90),(.42,1),(.56,.91),(.61,.80),(.65,.84),(.79,.60),(.89,.34),(1,.045)],
 'sapling':[(.10,.17),(.18,.55),(.35,1),(.60,.82),(.73,.70),(.88,.40),(1,.13)]}
 for z in range(h):
  t=z/(h-1)
  for x in range(n):
   for y in range(n):
    dx=x-c;dy=y-c;r=math.hypot(dx,dy);a=math.atan2(dy,dx)
    # Fourfold terms ensure that the Cartoon geometry AND paint are exact.
    cs4=(dx**4-6*dx*dx*dy*dy+dy**4)/(r**4) if r else 1
    edge=1+(.025*cs4 if cartoon else .035*math.sin(5*a+z*.18)+.022*math.cos(9*a-z*.31))
    if kind=='domed':edge=1+.065*(2*cs4*cs4-1)+(0 if cartoon else .02*math.sin(5*a+z*.1))
    inside=False;local=t
    if kind in profiles:
     rad=max(.76,R*lerp(t,profiles[kind])) if t>=profiles[kind][0][0] else 0
     inside=r<=rad*edge
     if kind=='tufted':
      # A fuller, multi-tip shoulder differentiates the similarly colored pointed tree.
      for j in range(4 if cartoon else 3):
       ang=j*math.tau/(4 if cartoon else 3)
       tx=c+math.cos(ang)*R*.22;ty=c+math.sin(ang)*R*.22
       if ((x-tx)/(R*.29))**2+((y-ty)/(R*.29))**2+((t-.84)/.145)**2<=1:inside=True
    elif kind in ('conifer','smallpine'):
     # Three overlapping pointed whorls, long lower tips, a small top leader.
     for bottom,top,wide in ([(.34,.73,1),(.52,.86,.79),(.70,1,.53)] if kind=='smallpine' else [(.13,.65,1),(.37,.83,.79),(.61,1,.53)]):
      if bottom<=t<=top:
       q=(t-bottom)/(top-bottom)
       rad=R*wide*(1-q)**.78
       rad*=.80+.20*cs4 if cartoon else .83+.13*math.cos(5*a)+.04*math.cos(9*a+z*.12)
       if r<=max(.76,rad):inside=True;local=q*.60+.22+t*.18
    elif kind=='spread':
     # Broad low crown ring, open cleft under an offset upper leaf cap.
     ring=((r-R*.61)/(R*.39))**2+((t-.43)/.13)**2<=1
     capx=c if cartoon else c-R*.08;capy=c if cartoon else c+R*.04
     cap=((x-capx)/(R*.60))**2+((y-capy)/(R*.60))**2+((t-.835)/.17)**2<=1
     # Wood forks join the two leaf masses; the exposed cleft is intentional.
     inside=ring or cap
     local=(t-.25)/.75
    elif kind=='giant':
     lobes=[(0,0,.75,.66,.255)]
     for j in range(4 if cartoon else 5):
      ang=j*math.tau/(4 if cartoon else 5)+(.16 if not cartoon else 0)
      lobes.append((math.cos(ang)*.48,math.sin(ang)*.48,.55+(0 if cartoon else .035*math.sin(j*2)),.52,.25))
     for lx,ly,lz,rr,rz in lobes:
      if ((dx/R-lx)/rr)**2+((dy/R-ly)/rr)**2+((t-lz)/rz)**2<=1:
       inside=True;local=max(local,(t-(lz-rz))/(2*rz))
    if inside:
     if cartoon:shade=2 if local<.42 else (4 if local<.73 else 5)
     else:
      patch=noise((x+z//7)//3,(y-z//9)//3,z//3)
      shade=max(0,min(5,int(local*4.6+(patch-.5)*1.35+.3*math.sin(a*5+z*.28))))
     if kind=='domed':
      # Broad radial leaf folds rather than unrelated fine surface speckles.
      shade=max(0,min(5,int(t*4.5+.65*(2*cs4*cs4-1))))
     put((x,y,z),1+shade,'foliage')
 # Retain hidden trunk inside the canopy without creating surface wood speckles.
 for p in list(v):
  x,y,z=p
  if z<h*.70 and (x-c)**2+(y-c)**2<(trunk*.56)**2:put(p,8 if cartoon else 7+int(noise(x//2,y//2,z//4)*3),'wood')
 if decor:
  # Attached surface fruit/flowers, never ground litter or floating ornaments.
  locations=[(.30,.25),(.54,1.10),(.69,2.25),(.41,3.10),(.59,4.35),(.34,5.40)]
  if kind=='sapling':locations=[(.33,.2),(.58,2.3),(.74,4.5)]
  if kind=='spread':locations=[(.43,.2),(.55,2.3),(.41,4.4)]
  if cartoon:locations=[(.43,j*math.pi/2) for j in range(4)]
  # Paint and relief are created on a canonical sector then rotated for Cartoon.
  for level,ang in locations:
   z=int(level*h);direction=(math.cos(ang),math.sin(ang))
   candidates=[p for p,g in groups.items() if g=='foliage' and abs(p[2]-z)<=1 and abs((p[0]-c)*direction[1]-(p[1]-c)*direction[0])<1.5]
   if not candidates:continue
   anchor=max(candidates,key=lambda p:(p[0]-c)*direction[0]+(p[1]-c)*direction[1])
   rad=1.2 if n<=12 else (2.1 if decor=='flower' else 1.8)
   # Voxel relief with a lighter center; flower corners create a four-petal motif.
   for xx in range(-3,4):
    for yy in range(-3,4):
     for zz in range(-3,4):
      if xx*xx+yy*yy+zz*zz>rad*rad:continue
      q=(anchor[0]+xx,anchor[1]+yy,anchor[2]+zz)
      color=11 if abs(xx)+abs(yy)+abs(zz)<=1 else 10
      put(q,color,'foliage')
  if cartoon:
   # Use one quadrant's final material assignment as authority for exact C4.
   for p in list(v):
    x,y,z=p
    if x>=n//2 and y>=n//2:
     orbit=[(x,y,z),(n-1-y,x,z),(n-1-x,n-1-y,z),(y,n-1-x,z)]
     for q in orbit:put(q,v[p],groups[p])
   # Geometry before ornament was symmetric; copy emptiness as well at relief edges.
   canonical={p:(v[p],groups[p]) for p in v if p[0]>=n//2 and p[1]>=n//2}
   v={};groups={}
   for (x,y,z),(col,g) in canonical.items():
    for q in [(x,y,z),(n-1-y,x,z),(n-1-x,n-1-y,z),(y,n-1-x,z)]:put(q,col,g)
 # Cap any sub-voxel ellipsoid tip with a connected 2x2 leader, preserving
 # the requested occupied height without resampling the model.
 top=max(p[2] for p in v)
 for z in range(top+1,h):
  for x in (n//2-1,n//2):
   for y in (n//2-1,n//2):put((x,y,z),6,'foliage')
 assert len(components(v))==1,(kind,cartoon,components(v))
 if cartoon:assert {(n-1-y,x,z):col for (x,y,z),col in v.items()}==v,(kind,'symmetry')
 return v,groups

