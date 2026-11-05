"""Deterministic deadwood sculpture. X is width, Y log length, Z up."""
from types import SimpleNamespace
import math

def make(f,cartoon=False):
 W,L,H=f['size'];v={};cx=(W-1)/2;cy=(L-1)/2
 def add(x,y,z,group,shade=1):
  if 0<=x<W and 0<=y<L and 0<=z<H:v[x,y,z]=group+str(max(0,min(2,shade)))
 def shade(x,y,z,t=0):
  if cartoon:x=min(x,W-1-x);y=min(y,L-1-y)
  return 0 if (x//2+y//4+t)%7==0 else (2 if (x//3+y//5+z//5+t)%6==0 else 1)
 if f['kind'] in ('stump','broken'):
  # Flared buttress roots narrow smoothly into an upright cut trunk.
  for x in range(W):
   for y in range(L):
    dx=(x-cx)/(W/2);dy=(y-cy)/(L/2);r=math.hypot(dx,dy);a=math.atan2(dy,dx)
    roots=(abs(math.cos(2*a))**7 if cartoon else max(0,math.cos(5*a+.35))**5)
    for z in range(H):
     t=z/max(1,H-1);radius=.62+.30*roots*max(0,1-t*2.4)+.05*(1-t)
     if not cartoon:radius+=.035*math.sin(a*7+.7)+.025*math.sin(a*3+z*.15)
     top=H-1
     if f['kind']=='broken':
      # Separate tall splinters around the edge, with exposed sloping wood inside.
      top=int((H-1)*(.45+.55*max(0,math.cos((4 if cartoon else 5)*a))**3))
      if r<.38:top=int(H*.35)
     if r<=radius and z<=top:
      cut=z==top
      sh=shade(x,y,z)
      if cut:sh=0 if int(r*W/2)%4==0 else (2 if int(r*W/2)%4==2 else 1)
      add(x,y,z,'wood' if cut else 'bark',sh)
 else:
  # Bark cylinder with filled end grain; length stays on Y for VCOM's X mask.
  radx=W*.46;radz=H*.46;cz=radz-.5
  if f['kind']=='drift':radx=W*.20;radz=H*.23;cz=radz-.5
  for y in range(L):
   shift=0 if cartoon else .6*math.sin(y*.19)
   rscale=1 if cartoon else 1+.035*math.sin(y*.7)
   for x in range(W):
    for z in range(H):
     q=((x-cx-shift)/radx)**2+((z-cz)/radz)**2
     if q<=rscale:
      angle=math.atan2(z-cz,x-cx)
      stripe=int((angle+math.pi)*radx)
      sh=0 if (stripe+y//15)%9==0 else (2 if stripe%8==3 else 1)
      wood=y in (0,L-1) and q<.78
      if wood:sh=0 if int(math.sqrt(q)*radx)%3==0 else 1
      add(x,y,z,'wood' if wood else 'bark',sh)
  # Recognizable lateral branch on driftwood and the Pixelwood fallen trunk.
  if f['kind']=='drift' or f['name']=='PixelwoodA_FallenLog':
   ys=[L//2] if cartoon else [L//3]
   for yy in ys:
    signs=(-1,1) if cartoon or f['kind']=='drift' else (1,)
    for sign in signs:
     for step in range(int(W*.43)):
      bx=round(cx+sign*step);by=yy+int(step*.45);bz=int(cz+step*(.95 if f['name']=='PixelwoodA_FallenLog' else .45))
      for x in range(bx-1,bx+2):
       for y in range(by-1,by+2):
        for z in range(bz-1,bz+2):add(x,y,z,'wood' if step==int(W*.43)-1 else 'bark',1)
   if cartoon:
    # Reflect the full branch geometry and paint to retain main-direction symmetry.
    for (x,y,z),c in list(v.items()):
     for xx,yy in [(W-1-x,y),(x,L-1-y),(W-1-x,L-1-y)]:v[xx,yy,z]=c
 # Normalize Cartoon paint using mirrored coordinates without changing semantic regions.
 if cartoon:
  for x,y,z in list(v):
   group=v[x,y,z][:-1]
   if group=='bark':v[x,y,z]=group+str(shade(x,y,z))
 if cartoon:
  original=dict(v)
  for x,y,z in v:v[x,y,z]=original[min(x,W-1-x),min(y,L-1-y),z]
 return SimpleNamespace(size=tuple(f['size']),v=v)
