"""Procedural, source-specific prop sculpture; coordinates are MagicaVoxel Z-up."""
from types import SimpleNamespace
import math

def make(f,cartoon=False):
 W,D,H=f['size'];v={};kind=f['kind'];cx=(W-1)/2;cy=(D-1)/2
 def put(x,y,z,g='body',shade=None):
  if 0<=x<W and 0<=y<D and 0<=z<H:
   if shade is None:shade=1 if cartoon else (2 if z%7==6 else (0 if (x//3+y//3)%9==0 else 1))
   v[x,y,z]=g+str(shade)
 def box(x0,y0,z0,x1,y1,z1,g='body',shade=None):
  for x in range(max(0,int(x0)),min(W,int(x1))):
   for y in range(max(0,int(y0)),min(D,int(y1))):
    for z in range(max(0,int(z0)),min(H,int(z1))):put(x,y,z,g,shade)
 def ell(xc,yc,zc,rx,ry,rz,g='body',shade=None):
  for x in range(max(0,int(xc-rx)),min(W,int(xc+rx)+2)):
   for y in range(max(0,int(yc-ry)),min(D,int(yc+ry)+2)):
    for z in range(max(0,int(zc-rz)),min(H,int(zc+rz)+2)):
     if ((x-xc)/rx)**2+((y-yc)/ry)**2+((z-zc)/rz)**2<=1:put(x,y,z,g,shade)
 def cyl(xc,yc,z0,z1,r,g='body',shade=None):
  for x in range(W):
   for y in range(D):
    if (x-xc)**2+(y-yc)**2<=r*r:
     for z in range(max(0,int(z0)),min(H,int(z1))):put(x,y,z,g,shade)
 def line(a,b,r=1,g='body',shade=None):
  n=max(abs(b[i]-a[i]) for i in range(3))*2+1
  for j in range(int(n)+1):
   t=j/max(1,n);x,y,z=[round(a[i]*(1-t)+b[i]*t) for i in range(3)]
   box(x-r,y-r,z-r,x+r+1,y+r+1,z+r+1,g,shade)
 def panel_marks(z0,z1,y=1):
  for z in range(int(z0),int(z1),3):
   for x in range(5,W-5):
    if x%7 not in [0,1]:put(x,y,z,'ink',1)
 if kind in ['sign','board','plaque','direction']:
  thick=4 if cartoon else 3
  if kind=='board':
   for x in [3,W-6]:box(x,D//2-2,0,x+3,D//2+2,H-1,'frame')
   box(2,1,H*.35,W-2,D-1,H-2,'frame');box(5,0,H*.45,W-5,2,H-5,'face');panel_marks(H*.5,H-6,0)
  elif kind=='direction':
   box(W//2-2,D//2-2,0,W//2+2,D//2+2,H,'frame')
   levels=[H-9,H-20] if 'Pixelwood' in f['name'] else [H-9]
   for j,z in enumerate(levels):
    for x in range(1,W-1):
     t=x if j%2 else W-1-x;trim=max(0,4-t)
     box(x,1,z+trim,x+1,1+thick,z+8-trim,'frame')
    panel_marks(z+2,z+7,0)
  else:
   box(W//2-2,D//2-2,0,W//2+2,D//2+2,H*.6,'frame')
   box(1,1,H*.35,W-1,D-1,H-1,'frame');box(3,0,H*.43,W-3,2,H-3,'face')
   if kind=='plaque':
    # Rounded cap and sparse emblem strokes, not invented readable text.
    box(3,1,H-1,W-3,D-1,H,'frame')
   panel_marks(H*.5,H-4,0)
  if cartoon:
   box(0,1,H-4,W,D-1,H-2,'frame') if kind!='direction' else box(W//2-3,D//2-2,0,W//2+3,D//2+2,3,'frame')
 elif kind=='kiosk':
  box(2,2,0,W-2,D-1,H-1,'frame');box(4,1,H*.25,W-4,3,H*.75,'face')
  panel_marks(H*.3,H*.7,1)
  box(1 if cartoon else 2,1,H-5,W-(1 if cartoon else 2),D-1,H-2,'mark')
 elif kind=='question':
  margin=1 if cartoon else 0
  box(0,0,0,W,D,H,'body')
  if cartoon:
   for x in [0,W-1]:
    for y in [0,D-1]:
     for z in range(H):v.pop((x,y,z),None)
  glyph=['01110','11011','00011','00110','00100','00000','00100']
  for j,row in enumerate(glyph):
   for i,c in enumerate(row):
    if c=='1':box(3+i*2,0,H-3-j*2,5+i*2,1,H-1-j*2,'mark',1)
  for x in [1,W-2]:
   for z in [1,H-2]:put(x,0,z,'rim',1)
 elif kind=='mushroom':
  cyl(cx,cy,0,H*.6,2 if not cartoon else 3,'stem')
  ell(cx,cy,H*.56,W*.45,D*.45,H*.38,'cap')
  for p in list(v):
   x,y,z=p
   if v[p].startswith('cap') and (x-W*.32)**2+(y-D*.35)**2<3:v[p]='spot1'
  if 'Pixelwood' in f['name']:
   for p in list(v):
    x,y,z=p
    if v[p].startswith('cap') and (x-W*.7)**2+(y-D*.6)**2<3:v[p]='spot1'
 elif kind=='chest':
  box(1,1,0,W-1,D-1,H*.55,'wood')
  for y in range(1,D-1):
   top=int(H*.55+H*(.44 if cartoon else .4)*math.sqrt(max(0,1-((y-cy)/(D*.48))**2)))
   box(1,y,H*.5,W-1,y+1,top,'wood')
  for x in [2,W//2-1,W-5]:
   for y in range(1,D-1):
    top=max(z for xx,yy,z in v if xx==x and yy==y)
    box(x,y,0,x+(3 if cartoon else 2),y+1,top+1,'trim')
  box(1,0,H*.4,W-1,2,H*.5,'trim');box(W//2-2,0,H*.3,W//2+2,2,H*.6,'trim')
  box(W//2-1,0,H*.4,W//2+1,1,H*.47,'ink',1)
 elif kind=='bench':
  for x in [3,W-6]:
   for y in [3,D-6]:box(x,y,0,x+3,y+3,H*.48,'metal')
   box(x,D-5,0,x+3,D-2,H-1,'metal')
  for y in range(2,D-3,4):box(1,y,H*.38,W-1,y+3,H*.48,'wood')
  for z in range(int(H*.55),H-2,4):box(1,D-5,z,W-1,D-2,z+3,'wood')
  for x in [2,W-4]:box(x,2,H*.6,x+2,D-2,H*.68,'metal');box(x,2,H*.4,x+2,4,H*.68,'metal')
  if cartoon:box(0,D-6,H-4,W,D-1,H-1,'wood')
 elif kind=='mailbox':
  box(W//2-1,D//2-1,0,W//2+1,D//2+1,H*.55,'metal')
  box(2,2,H*.4,W-2,D-2,H-4,'body');ell(cx,cy,H-5,W*.34,D*.34,4 if cartoon else 3,'body')
  box(3,1,H*.52,W-3,2,H*.61,'ink',1);box(3,1,H*.75,W-3,2,H*.8,'metal')
 elif kind=='terminal':
  for x in [4,W-7]:box(x,3,0,x+3,D-3,H*.5,'metal')
  box(2,2,H*.3,W-2,D-2,H*.65,'body');ell(cx,cy,H*.64,W*.39,D*.3,H*.3,'body')
  box(5,1,H*.55,W-5,3,H*.78,'ink',1)
  for x in [4,9,14]:box(x,1,H*.37,x+2,2,H*.45,'button',1)
  if cartoon:box(1,1,H*.3,W-1,D-1,H*.4,'body')
 elif kind=='ball':
  ell(cx,cy,(H-1)/2,W/2,D/2,H/2,'white')
  for p in list(v):
   x,y,z=p;v[p]=('red' if z>=H//2+1 else ('ink' if z==H//2 else 'white'))+'1'
  box(W//2-1,0,H//2-1,W//2+1,2,H//2+2,'white',1)
  if cartoon:
   for x in [0,W-1]:
    for y in [0,D-1]:
     for z in range(H):v.pop((x,y,z),None)
   # Flatten the pedestal-free base just enough to make a distinct stable Cartoon form.
   box(W//2-3,D//2-2,0,W//2+3,D//2+2,2,'white',1)
 elif kind in ['bale','balestack']:
  def bale(x,y,z,w,d,h):
   box(x,y,z,x+w,y+d,z+h,'straw')
   for xx in [x+w//3,x+w*2//3]:box(xx,y,z,xx+(2 if cartoon else 1),y+d,z+h,'rope')
  if kind=='bale':bale(1,1,0,W-2,D-2,H-1)
  else:
   bale(1,1,0,14,20,14);bale(17,1,0,14,20,14);bale(9,2,14,14,18,14)
 elif kind=='hay':
  for z in range(H-2):cyl(cx,cy,z,z+1,max(2,W*.48*(1-(z/(H-1))**1.4)),'straw')
  if cartoon:cyl(cx,cy,H-5,H,3,'straw')
 elif kind=='fork':
  box(W//2-1,D//2-1,0,W//2+1,D//2+1,H*.72,'wood')
  box(2,D//2-1,H*.65,W-2,D//2+1,H*.74,'metal')
  for x in [2,W//2-1,W-4]:box(x,D//2-1,H*.7,x+2,D//2+1,H-1,'metal')
  if cartoon:box(W//2-2,D//2-2,0,W//2+2,D//2+2,3,'wood')
 elif kind=='planter':
  box(1,1,0,W-1,D-1,H*.35,'wood');box(0,0,H*.3,W,D,H*.45,'wood');box(2,2,H*.4,W-2,D-2,H*.5,'soil')
  for y in [7,16,25]:
   for x in [6,13]:
    box(x-1,y-1,H*.45,x+1,y+1,H*.75,'leaf')
    ell(x,y,H*.65,4,4,3,'leaf');ell(x,y,H*.85,3 if cartoon else 2.5,3,2,'petal')
 elif kind=='parasol':
  cyl(cx,cy,0,H-2,1.5,'wood');cyl(cx,cy,0,2,4,'metal')
  for x in range(W):
   for y in range(D):
    r=math.hypot(x-cx,y-cy)
    if r<W*.48:
     z=int(H-2-r*.45);sector=int((math.atan2(y-cy,x-cx)+math.pi)/(math.pi/4))
     box(x,y,z-(2 if cartoon else 1),x+1,y+1,z+1,'cloth',0 if sector%2 else 1)
 elif kind=='lounger':
  for x in [2,W-4]:
   for y in [4,D-7]:box(x,y,0,x+2,y+2,6,'metal')
   for y in range(2,D-2):
    z=6+max(0,y-D*.55)*.65
    box(x,y,z,x+2,y+1,z+2,'metal')
  for y in range(2,D-2):
   z=6+max(0,y-D*.55)*(.7 if cartoon else .65)
   box(4,y,z,W-4,y+1,z+2,'cloth')
 elif kind=='sandcastle':
  box(1,1,0,W-1,D-1,2,'sand')
  for x in [6,W-7]:
   for y in [6,D-7]:
    cyl(x,y,0,H-5,5,'sand')
    for z in range(H-5,H):cyl(x,y,z,z+1,max(1,5-(z-(H-5))),'sand')
  box(6,5,0,W-6,8,H*.5,'sand');box(6,D-9,0,W-6,D-6,H*.5,'sand')
  box(5,6,0,8,D-6,H*.5,'sand');box(W-9,6,0,W-6,D-6,H*.5,'sand')
  for x in range(8,W-8,5):
   for y in [5,D-9]:box(x,y,H*.5,x+3,y+3,H*.6+(1 if cartoon else 0),'sand')
  for x in range(W//2-2,W//2+2):
   for y in range(4,9):
    for z in range(1,7):v.pop((x,y,z),None)
 elif kind=='scooter':
  # Wheels face the sides; frame and body remain genuinely volumetric.
  for x in [6,W-7]:
   for xx in range(W):
    for z in range(0,12):
     q=((xx-x)/5)**2+((z-5)/5)**2
     if q<=1:box(xx,3,z,xx+1,D-3,z+1,'rubber')
   box(x-1,2,4,x+2,D-2,7,'metal')
  box(5,4,6,W-5,D-4,10,'metal');box(8,2,8,W-7,D-2,14,'body')
  box(14,2,14,W-7,D-2,17,'seat');box(5,2,10,11,D-2,H-4,'body')
  line((8,D//2,12),(11,D//2,H-2),1,'metal');box(10,0,H-3,13,D,H-1,'metal')
  if cartoon:box(5,1,11,12,D-1,17,'body')
 elif kind=='timberpile':
  for row in range(2):
   for xc in ([4,12,20,28] if row==0 else [8,16,24]):
    zc=3.5+row*6
    for x in range(W):
     for z in range(H):
      q=(x-xc)**2+(z-zc)**2
      if q<=(4 if cartoon else 3.8)**2:
       box(x,1,z,x+1,D-1,z+1,'wood')
       if q<7:box(x,0,z,x+1,2,z+1,'cut')
 elif kind=='barrel':
  for z in range(H):
   r=W*.38+W*(.1 if cartoon else .08)*math.sin(math.pi*z/(H-1));cyl(cx,cy,z,z+1,r,'wood')
  for z in [4,H-7]:
   for zz in range(z,z+(3 if cartoon else 2)):
    r=W*.38+W*(.1 if cartoon else .08)*math.sin(math.pi*zz/(H-1))
    for x in range(W):
     for y in range(D):
      if (r-1.6)**2<=(x-cx)**2+(y-cy)**2<=r*r:put(x,y,zz,'metal')
 elif kind=='fountain':
  cyl(cx,cy,0,3,W*.47,'stone');cyl(cx,cy,3,6,W*.42,'stone')
  for x in range(W):
   for y in range(D):
    rr=math.hypot(x-cx,y-cy)
    if rr<W*.34:box(x,y,5,x+1,y+1,7,'water')
    elif rr<W*.42:box(x,y,5,x+1,y+1,10,'stone')
  cyl(cx,cy,6,H-3,4 if cartoon else 3,'stone')
  cyl(cx,cy,H*.5,H*.5+3,W*.22,'stone');cyl(cx,cy,H*.5+3,H*.5+4,W*.18,'water')
  ell(cx,cy,H-4,4,4,3,'stone')
 elif kind in ['statue','antler']:
  box(2,2,0,W-2,D-2,4,'stone');box(4,4,4,W-4,D-4,8,'stone')
  if kind=='antler':
   box(W//2-4,D//2-3,8,W//2+4,D//2+3,H*.5,'stone');ell(cx,cy,H*.55,5,4,6,'stone')
   for sign in [-1,1]:
    line((cx+sign*3,cy,H*.6),(cx+sign*8,cy,H*.8),1,'stone')
    line((cx+sign*8,cy,H*.8),(cx+sign*7,cy,H-2),1 if not cartoon else 2,'stone')
    line((cx+sign*6,cy,H*.75),(cx+sign*3,cy,H*.9),1,'stone')
  else:
   for x in [W//2-4,W//2+1]:box(x,D//2-2,8,x+3,D//2+2,H*.45,'stone')
   ell(cx,cy,H*.52,4 if cartoon else 3.5,3,H*.18,'stone');ell(cx,cy,H*.81,3.5,3,4,'stone')
   line((cx-2,cy,H*.65),(3,cy,H*.87),1,'stone');line((cx+2,cy,H*.65),(W-4,cy,H*.87),1,'stone')
   line((3,cy,H*.87),(2,cy,H-2),1 if not cartoon else 2,'stone');line((W-4,cy,H*.87),(W-3,cy,H-2),1 if not cartoon else 2,'stone')
 else:raise ValueError(kind)
 if f['name']=='PokeB_BluePlaque':
  box(4,0,8,W-4,1,10,'red',1);box(4,0,11,W-4,1,13,'ink',1)
 if f['source']=='poke_u.jpg':
  for x in range(2,W-2):
   z=H-3-int(2*abs((x-cx)/max(cx,1)))
   box(x,0,z,x+1,2,z+1,'mark',1)
 if cartoon and kind in ['bale','balestack']:
  for x in [1,W-2]:
   for y in [1,D-2]:
    for z in range(H):v.pop((x,y,z),None)
 if cartoon:
  axes=[] if kind in ['direction','question','scooter'] else [0]
  if kind in ['mushroom','ball','barrel','hay','fountain']:axes=[0,1]
  for axis in axes:
   for p,c in list(v.items()):
    q=list(p);q[axis]=[W,D,H][axis]-1-q[axis];v[tuple(q)]=c
  old=dict(v)
  for p in v:
   q=list(p)
   for axis in axes:q[axis]=min(q[axis],[W,D,H][axis]-1-q[axis])
   v[p]=old[tuple(q)]
 if cartoon and kind=='mushroom':
  for (x,y,z),s in list(v.items()):
   if s.startswith('cap') and z>=H*.65 and any((x-(cx+dx))**2+(y-(cy+dy))**2<=2 for dx in [-W*.22,W*.22] for dy in [-D*.2,D*.2]):v[x,y,z]='spot1'
 return SimpleNamespace(size=tuple(f['size']),v=v)
