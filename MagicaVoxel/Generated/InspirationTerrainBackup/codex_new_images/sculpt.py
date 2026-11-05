"""Volumetric source interpretations. No sprite extrusion or shadow geometry."""
import math
class Sculpt:
 def __init__(self,f,cartoon):
  self.f=f;self.cartoon=cartoon;self.W,self.D,self.H=f['size'];self.cx=(self.W-1)/2;self.cy=(self.D-1)/2;self.v={}
 def put(self,x,y,z,g='leaf',s=1):
  x,y,z=round(x),round(y),round(z)
  if 0<=x<self.W and 0<=y<self.D and 0<=z<self.H:self.v[x,y,z]=(g,s)
 def box(self,a,b,g='wood',s=1):
  for x in range(max(0,int(a[0])),min(self.W,int(b[0]))):
   for y in range(max(0,int(a[1])),min(self.D,int(b[1]))):
    for z in range(max(0,int(a[2])),min(self.H,int(b[2]))):self.put(x,y,z,g,s)
 def ell(self,x,y,z,rx,ry,rz,g='leaf',s=1):
  if self.cartoon and g=='leaf':rx*=1.04;ry*=1.04;rz*=.96
  if min(rx,ry,rz)<=0:return
  for xx in range(max(0,math.floor(x-rx)),min(self.W,math.ceil(x+rx)+1)):
   for yy in range(max(0,math.floor(y-ry)),min(self.D,math.ceil(y+ry)+1)):
    for zz in range(max(0,math.floor(z-rz)),min(self.H,math.ceil(z+rz)+1)):
     if ((xx-x)/rx)**2+((yy-y)/ry)**2+((zz-z)/rz)**2<=1:self.put(xx,yy,zz,g,s)
 def line(self,a,b,r=1,g='wood',s=1):
  n=max(1,math.ceil(math.dist(a,b)*2))
  for i in range(n+1):
   p=[a[j]+(b[j]-a[j])*i/n for j in range(3)];self.ell(*p,r,r,r,g,s)
 def cylinder(self,x,y,r,z0,z1,g='wood',s=1):
  if self.cartoon:r+=.25
  for xx in range(max(0,math.floor(x-r)),min(self.W,math.ceil(x+r)+1)):
   for yy in range(max(0,math.floor(y-r)),min(self.D,math.ceil(y+r)+1)):
    if (xx-x)**2+(yy-y)**2<=r*r:
     for zz in range(max(0,int(z0)),min(self.H,int(z1))):self.put(xx,yy,zz,g,s)
 def cone(self,x,y,z,r,h,g='leaf',s=1,skirt=0):
  if self.cartoon:r*=1.04;h*=.96;skirt*=.5
  for zz in range(max(0,int(z)),min(self.H,math.ceil(z+h))):
   rr=max(.9,r*(1-(zz-z)/h))
   for xx in range(max(0,math.floor(x-rr)),min(self.W,math.ceil(x+rr)+1)):
    for yy in range(max(0,math.floor(y-rr)),min(self.D,math.ceil(y+rr)+1)):
     angle=math.atan2(yy-y,xx-x);edge=rr*(1+skirt*math.cos(angle*8))
     if (xx-x)**2+(yy-y)**2<=edge**2:self.put(xx,yy,zz,g,s)
 def trunk(self,h,r=None):
  r=r or max(1.3,self.W*.08);self.cylinder(self.cx,self.cy,r,0,h)
  for j in range(4):
   a=j*math.pi/2;self.line((self.cx,self.cy,min(h*.3,r*2)),(self.cx+math.cos(a)*r*2,self.cy+math.sin(a)*r*2,0),max(1,r*.55))
 def leaf(self,a,b,width,g='leaf',s=1):
  # Tapered, curved fleshy leaf, with a visible raised central vein.
  for i in range(17):
   t=i/16;p=[a[j]+(b[j]-a[j])*t for j in range(3)];p[2]+=math.sin(math.pi*t)*width*.6
   r=max(.75,width*math.sin(math.pi*t));self.ell(*p,r,r,max(.8,r*.35),g,s)
  self.line(a,b,.8,g,2)
 def tree(self):
  f=self.f;k=f['kind'];W,D,H=self.W,self.D,self.H;cx,cy=self.cx,self.cy;R=min(W,D)*.43
  self.trunk(H*(.35 if k=='bushpatch' else .65))
  if k=='column':
   self.ell(cx,cy,H*.52,R*.8,R*.8,H*.41)
   for j in range(4):
    zz=H*(.24+j*.18);rr=R*(.77 if j<3 else .55)
    self.ell(cx,cy,zz,rr,rr,H*.15,s=1 if j<3 else 2)
  elif k=='cone' and 'OliveConeTree' in f['name']:
   for j in range(3):
    self.cone(cx,cy,H*(.08+j*.095),R*(1-j*.065),H*.28,s=0 if j==0 else 1,skirt=.11)
   self.cone(cx,cy,H*.29,R*.85,H*.68,s=1,skirt=.025)
  elif k in ['cone','fir']:
   if any(name in f['name'] for name in ['UprightLeaf','PointedScale','PointedSapling','NarrowPoint','SmallPoint','JaggedLeaf']):
    self.ell(cx,cy,H*.46,R*.95,R*.95,H*.35)
   tiers=f.get('tiers',4 if k!='column' else 3)
   for j in range(tiers):
    t=j/max(1,tiers-1);z=H*(.12+.58*t);r=R*(1-.64*t);h=H*(.36 if k=='fir' else .31)
    self.cone(cx,cy,z,r,h,s=0 if j==0 else 1,skirt=.16 if k=='fir' else .07)
    if k!='column':
     for a in range(8):
      ang=a*math.pi/4;self.cone(cx+r*.65*math.cos(ang),cy+r*.65*math.sin(ang),z-1,r*.28,h*.65,s=1+(a%3==0),skirt=.07)
  elif k in ['bush','rooted','bushpatch','scallop']:
   profile=f.get('profile','round');r=R;z=H*.47;rz=H*.43
   if k=='rooted':z=H*.6;rz=H*.29
   if k=='bushpatch':z=H*.35;rz=H*.3
   if k=='bushpatch' and profile=='sparse':r*=.65;rz*=.7
   if k=='bushpatch' and profile=='dense':rz*=1.25
   self.ell(cx,cy,z,r,r,rz)
   if profile in ['point','pear','bell','tiers']:
    count=4 if profile=='tiers' else 2 if profile=='pear' else 3
    for j in range(count):self.cone(cx,cy,H*(.1+j*.55/count),r*(1-j*.7/count),H*(.5 if profile=='point' else .39),s=1)
   else:
    rings=4 if k=='scallop' else 2 if profile=='lobed' else 3
    for j in range(rings):
     zz=z+rz*(-.45+j*.4);rr=r*math.sqrt(max(.1,1-((zz-z)/rz)**2))*.75
     n=8 if self.cartoon else 9
     for a in range(n):
      ang=a*2*math.pi/n+(j%2)*.3;self.ell(cx+rr*math.cos(ang),cy+rr*math.sin(ang),zz,r*.32,r*.32,rz*.3,s=2 if j==rings-1 else 1)
   if k=='rooted':
    for a in range(8):
     ang=a*math.pi/4;self.line((cx,cy,H*.35),(cx+R*.65*math.cos(ang),cy+R*.65*math.sin(ang),0),1.5)
  elif k in ['cluster','cluster_tree','flat_tree','round_tree','droop']:
   bottom=H*.35 if k not in ['cluster','droop'] else H*.15
   if k=='round_tree':self.ell(cx,cy,H*.69,R,R,H*.28)
   elif k=='droop':
    self.ell(cx,cy,H*.6,R*.8,R*.8,H*.3)
    for j in range(8):
     a=j*math.pi/4;self.ell(cx+R*.65*math.cos(a),cy+R*.65*math.sin(a),H*.43,R*.35,R*.35,H*.27,s=j%2)
   else:
    self.ell(cx,cy,bottom+H*.22,R*.7,R*.7,H*.22)
    for j in range(4):
     a=j*math.pi/2;xx=cx+R*.52*math.cos(a);yy=cy+R*.52*math.sin(a)
     self.line((cx,cy,bottom),(xx,yy,bottom+H*.2),max(1,W*.045))
     self.ell(xx,yy,bottom+H*.22,R*.52,R*.52,H*(.16 if k=='flat_tree' else .2),s=1+j%2)
    self.ell(cx,cy,bottom+H*.37,R*.52,R*.52,H*.17,s=2)
  elif k in ['lollipop','fork']:
   if k=='lollipop':self.ell(cx,cy,H*.7,R*.65,R*.65,H*.27)
   else:
    for sign in [-1,1]:
     self.line((cx,cy,H*.35),(cx+sign*W*.28,cy,H*.67),1.3)
     self.ell(cx+sign*W*.25,cy,H*.72,W*.2,D*.27,H*.18)
  elif k=='giant':
   self.v={};self.trunk(H*.79,W*.09)
   for j,(a,z,reach) in enumerate([(0,.42,.32),(math.pi,.55,.28),(math.pi/2,.75,.27),(-math.pi/2,.82,.26)]):
    p=(cx+W*reach*math.cos(a),cy+W*reach*math.sin(a),H*z)
    self.line((cx,cy,H*(z-.13)),p,W*.045)
    self.ell(*p,W*.19,D*.19,H*.08,s=1)
   for dx,dy,dz in [(-.18,-.15,.82),(.18,-.1,.85),(-.14,.15,.88),(.16,.16,.82),(0,0,.91)]:
    self.ell(cx+W*dx,cy+D*dy,H*dz,W*.26,D*.26,H*.075,s=1 if dz<.9 else 2)
   if f.get('vines'):
    for j in range(16):
     a=j*math.pi/8;x=cx+W*.34*math.cos(a);y=cy+D*.34*math.sin(a)
     self.line((x,y,H*.81),(x,y,H*(.38+(j%4)*.07)),.85,'leaf',0)
     self.line((x,y,H*.81),(cx,cy,H*.85),.9,'leaf',0)
  self.leaf_texture()
 def leaf_texture(self):
  if self.cartoon:return
  for (x,y,z),(g,s) in list(self.v.items()):
   if g=='leaf' and (x//3*13+y//3*7+z//3*11)%19 in [0,1]:self.v[x,y,z]=(g,max(0,s-1))
 def palm(self,cx=None,cy=None,scale=1):
  cx=self.cx if cx is None else cx;cy=self.cy if cy is None else cy;H=self.H*scale;R=min(self.W,self.D)*.43*scale
  self.cylinder(cx,cy,max(2,R*.18),0,H*.66)
  for z in range(2,int(H*.62),4):self.cylinder(cx,cy,max(2,R*.21),z,z+1,'wood',0)
  n=self.f.get('fronds',8);n=8 if self.cartoon else n
  for j in range(n):
   a=j*2*math.pi/n
   self.leaf((cx,cy,H*.68),(cx+R*math.cos(a),cy+R*math.sin(a),H*.47),R*.2,s=1)
   self.leaf((cx,cy,H*.68),(cx+R*.63*math.cos(a+.2),cy+R*.63*math.sin(a+.2),H*.88),R*.17,s=2)
 def small(self):
  f=self.f;k=f['kind'];W,D,H=self.W,self.D,self.H;cx,cy=self.cx,self.cy
  if k in ['rosette','sprout']:
   self.cylinder(cx,cy,1,0,H*.35,'leaf')
   n=f.get('petals',2 if k=='sprout' else 6);n=4 if self.cartoon and k!='sprout' else n
   for j in range(n):
    a=2*math.pi*j/n;reach=.39 if k=='rosette' else .32;self.leaf((cx,cy,H*.25),(cx+W*reach*math.cos(a),cy+D*reach*math.sin(a),H*.6),min(W,D)*(.11 if k=='rosette' else .16))
  elif k=='grass':
   spacing=7 if f.get('count')==4 else 5 if W>20 else 4
   for x in range(2,W-2,spacing):
    for y in range(2,D-2,spacing):
     h=H*(.55+((x*3+y*7)%5)*.08)
     for sign in [-1,1]:self.leaf((x,y,0),(min(W-1,max(0,x+sign*3)),min(D-1,y+2),h),1.1)
  elif k in ['flower','flowers']:
   centers=[(cx,cy,H*.5)] if k=='flower' else [(cx,cy,H*.68),(cx-W*.25,cy,H*.43),(cx+W*.25,cy,H*.5),(cx,cy-D*.25,H*.52),(cx,cy+D*.25,H*.4)]
   for x,y,z in centers:
    self.line((x,y,0),(x,y,z),1,'leaf')
    for sign in [-1,1]:self.leaf((x,y,z*.25),(x+sign*W*.18,y,z*.48),W*.09)
    r=W*(.18 if k=='flower' else .1);n=f.get('petals',5);n=4 if self.cartoon else n
    for j in range(n):
     a=j*2*math.pi/n;self.ell(x+r*math.cos(a),y+r*math.sin(a),z,r*.8,r*.8,max(1,r*.45),'petal')
    self.ell(x,y,z+1,r*.5,r*.5,1.5,'center')
  elif k in ['lily','lily_pair']:
   centers=[(cx,cy,min(W,D)*.42)] if k=='lily' else [(W*.25,cy,W*.22),(W*.7,cy,W*.22)]
   if f.get('pads')==3:centers=[(W*.3,D*.65,min(W,D)*.26),(W*.38,D*.3,min(W,D)*.25),(W*.7,D*.38,min(W,D)*.28)]
   for x,y,r in centers:
    self.cylinder(x,y,r,0,2,'leaf')
    for q in list(self.v):
     if q[1]<y and abs(q[0]-x)<(y-q[1])*.35:del self.v[q]
    if f.get('petal'):
     for j in range(5):
      a=j*2*math.pi/5;self.ell(x+r*.25*math.cos(a),y+r*.25*math.sin(a),3,r*.22,r*.22,2,'petal')
     self.ell(x,y,4,1.1,1.1,1,'center')
  elif k in ['hedge','hedge_corner']:
   self.box((1,1,0),(W-1,D-1,H*.75),'leaf')
   for x in range(3,W,6):
    for y in range(3,D,6):self.ell(x,y,H*.72,4,4,H*.2)
   if k=='hedge_corner':
    for x,y,z in list(self.v):
     if x>W//2 and y<D//2:del self.v[x,y,z]
   self.leaf_texture()
  elif k=='cactus':
   for x,y,h,r in [(cx,cy,H*.92,W*.12),(cx-W*.25,cy,H*.7,W*.11),(cx+W*.25,cy,H*.72,W*.11)]:
    self.cylinder(x,y,r,0,h,'leaf');self.ell(x,y,h,r,r,r,'leaf',2)
    for z in range(3,int(h),5):self.put(x-r,y,z,'leaf',2);self.put(x+r,y,z,'leaf',2)
   self.box((cx-W*.3,cy-2,2),(cx+W*.3,cy+2,7),'leaf')
 def wood(self):
  k=self.f['kind'];W,D,H=self.W,self.D,self.H;cx,cy=self.cx,self.cy
  if k in ['stump','axe_stump']:
   height=H*.53 if k=='axe_stump' else H*.7;r=min(W,D)*.36
   self.cylinder(cx,cy,r,0,height)
   for j in range(6):
    a=j*math.pi/3;self.line((cx,cy,height*.4),(cx+r*1.15*math.cos(a),cy+r*1.15*math.sin(a),1),r*.23)
   for x,y,z in list(self.v):
    if z>=int(height)-1:self.v[x,y,z]=('cut',0 if int(math.hypot(x-cx,y-cy))%4==0 else 1)
   # A visible split cut down one side.
   for z in range(int(height*.4),int(height)):
    for x in range(round(cx),round(cx)+1):self.v.pop((x,round(cy-r)+1,z),None)
   if k=='axe_stump':
    self.line((cx+2,cy,height-3),(cx-13,cy,H-2),1.7)
    self.box((cx-6,cy-2,height+2),(cx+4,cy+2,height+9),'metal')
  elif k=='log':
   for x in range(1,W-1):
    for y in range(D):
     for z in range(H):
      if (y-cy)**2+(z-H*.42)**2<(D*(.42 if self.cartoon else .4))**2:self.put(x,y,z,'cut' if x<3 or x>=W-3 else 'wood',0 if x<3 and int(math.hypot(y-cy,z-H*.42))%3==0 else 1)
  elif k=='woodpile':
   # Three logs lie along depth, round sawn ends facing the viewer.
   radius=W*.15
   for xc in [W*.19,W*.5,W*.81]:
    for x in range(W):
     for z in range(min(H,math.ceil(radius*2)+1)):
      distance=math.hypot(x-xc,z-radius)
      if distance<=radius:
       for y in range(1,D-1):self.put(x,y,z,'cut' if y<3 or y>D-4 else 'wood',0 if y<3 and int(distance)%3==0 else 1)
   for y in [D*.28,D*.72]:self.box((1,y,radius*1.8),(W-1,y+3,radius*1.8+2),'cut')
 def ground(self):
  f=self.f;k=f['kind'];W,D,H=self.W,self.D,self.H
  for x in range(W):
   for y in range(D):
    sand=k=='path' or k=='edge' and y<8 or k=='outer' and x<8 and y<8 or k=='inner' and (x<8 or y<8)
    for z in range(H):
     g=('lightgrass' if f.get('light_patch') else 'sand') if sand else 'grass';s=1 if self.cartoon else 2 if (x//2*7+y//2*3)%8==0 else 1
     self.put(x,y,z,g,s if z>=H-2 else 0)
 def hammock(self):
  W,D,H=self.W,self.D,self.H
  for x in [20,W-21]:self.palm(x,self.cy,.8)
  for x in range(24,W-24):
   t=(x-24)/(W-49);z=H*.4-9*math.sin(math.pi*t)
   for y in range(D//2-8,D//2+9):
    if y in [D//2-8,D//2+8] or (x+y)%6==0 or (x-y)%6==0:self.box((x,y,z),(x+2,y+2,z+2),'cloth')
  for x in [20,W-21]:
   target=24 if x==20 else W-25
   for y in [D//2-8,D//2+8]:self.line((x,self.cy,H*.42),(target,y,H*.4),1,'cloth')
 def house(self):
  W,D,H=self.W,self.D,self.H
  # Boundary grid 8+16i; buried foundation level, three-course walls.
  self.box((8,8,0),(136,104,16),'stone')
  self.box((10,10,15),(134,102,16),'wood')
  for a,b in [((7,7,16),(137,9,64)),((7,103,16),(137,105,64)),((7,9,16),(9,103,64)),((135,9,16),(137,103,64))]:self.box(a,b,'wood')
  for x in [8,56,88,136]:self.box((x-3,5,16),(x+3,11,64),'stone')
  # Front windows occupy complete single slots, panes in middle course only.
  for x in [24,40,104,120]:
   self.box((x,6,32),(x+16,10,48),'glass')
   self.box((x,4,30),(x+16,7,33),'cut')
  # Two 16-wide closed leaves, inset under the source's broad arched timber hood.
  self.box((56,5,16),(88,10,48),'wood',0)
  for x in range(52,92):
   dx=abs(x-71.5);top=44+int(math.sqrt(max(0,20**2-dx**2)))
   self.box((x,3,16),(x+1,6,top),'wood')
   if 56<=x<88:self.box((x,2,16),(x+1,4,top-3),'wood',0 if x%8==0 else 1)
  self.box((48,0,14),(96,8,16),'stone')
  # Flat roof slab and segmented parapet; roof is accessible only by separate game design.
  self.box((4,4,64),(140,108,69),'roof')
  thick=7 if self.cartoon else 5
  for a,b in [((4,4,69),(140,4+thick,80)),((4,108-thick,69),(140,108,80)),((4,4,69),(4+thick,108,80)),((140-thick,4,69),(140,108,80))]:self.box(a,b,'roof',2)
  for x in range(8,138,16):
   for y in [4,107]:self.box((x,y,70),(x+1,y+1,79),'roof',0)
  # Open square flue at rear left, with no fictitious glow.
  self.box((12,83,69),(36,103,89),'roof')
  self.box((10,81,86),(38,105,90),'roof',2)
  for x in range(16,32):
   for y in range(87,99):
    for z in range(73,90):self.v.pop((x,y,z),None)
  self.box((16,87,72),(32,99,73),'dark')
  # Moss on left roof and planter foliage; copied source motifs in complete cottage.
  for x in range(9,23):
   for y in range(24,81):
    if self.cartoon or (x//3+y//4)%4:self.put(x,y,69,'leaf')
  self.box((17,2,24),(40,7,30),'cut')
  for x in [22,33]:
   self.line((x,4,29),(x,4,36),1,'leaf')
   for dx in [-3,0,3]:self.ell(x+dx,4,34,3,2,2,'leaf')
  for x,y in [(13,17),(19,16),(16,23),(23,22)]:
   self.line((x,y,69),(x,y,75),1,'leaf');self.ell(x,y,75,3,3,1,'petal');self.put(x,y,77,'center')
  # Broad, coherent cracks and masonry coursing without noisy random chips.
  if not self.cartoon:
   for x in range(74,109):
    y=40+(x//7)%3;self.put(x,y,68,'roof',0)
  for q,(g,s) in list(self.v.items()):
   x,y,z=q
   if g=='stone' and (z%8==7 or (x+(z//8%2)*4)%16==0):self.v[q]=(g,0)
 def finish(self):
  k=self.f['kind']
  if k in ['cone','fir','column','bush','rooted','bushpatch','scallop','cluster','cluster_tree','flat_tree','round_tree','droop','lollipop','fork','giant']:self.tree()
  elif k=='palm':self.palm()
  elif k=='hammock':self.hammock()
  elif k in ['stump','axe_stump','log','woodpile']:self.wood()
  elif k in ['ground','path','edge','outer','inner']:self.ground()
  elif k=='house':self.house()
  else:self.small()
  if self.cartoon:
   sym=self.f.get('symmetry');W,D=self.W,self.D
   if sym=='C4' and W==D:
    old=self.v;self.v={}
    for (x,y,z),c in old.items():
     if x<W//2 and y<D//2:
      for xx,yy in [(x,y),(W-1-y,x),(W-1-x,D-1-y),(y,D-1-x)]:self.v[xx,yy,z]=c
   elif sym=='bilateral':
    for (x,y,z),c in list(self.v.items()):
     if x<W//2:self.v[W-1-x,y,z]=c
    for x,y,z in list(self.v):
     if x>=W//2 and (W-1-x,y,z) not in self.v:del self.v[x,y,z]
   elif sym=='diagonal' and W==D:
    for (x,y,z),c in list(self.v.items()):
     if x+y<=W-1:self.v[W-1-y,W-1-x,z]=c
    for x,y,z in list(self.v):
     if x+y>W-1 and (W-1-y,W-1-x,z) not in self.v:del self.v[x,y,z]
   # Directional objects preserve openings and intentional asymmetry.
  if self.v:
   low=min(q[2] for q in self.v)
   if low:self.v={(x,y,z-low):c for (x,y,z),c in self.v.items()}
  # Thin leaf tips clipped by a symmetry plane can leave isolated voxel crumbs.
  # Trim those tiny detached leaf fragments, preserving every rooted clump.
  left=set(self.v)
  while left:
   todo=[left.pop()];part=[]
   while todo:
    q=todo.pop();part.append(q);x,y,z=q
    for p in [(x+1,y,z),(x-1,y,z),(x,y+1,z),(x,y-1,z),(x,y,z+1),(x,y,z-1)]:
     if p in left:left.remove(p);todo.append(p)
   if len(part)<=12 and all(q[2]>0 and self.v[q][0]=='leaf' for q in part):
    for q in part:del self.v[q]
  return self.v
