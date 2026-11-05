"""Source-specific complete fence sections, with deliberate joining interfaces."""
from types import SimpleNamespace
import math

def make(f,cartoon=False):
 W,D,H=f['size'];v={};k=f['kind'];name=f['name']
 def box(a,b,g='wood'):
  for x in range(max(0,a[0]),min(W,b[0])):
   for y in range(max(0,a[1]),min(D,b[1])):
    for z in range(max(0,a[2]),min(H,b[2])):
     xx=min(x,W-1-x) if cartoon else x
     shade=1 if cartoon else (0 if (xx//2+z//6)%9==0 else (2 if y==2 or z%8==7 else 1))
     v[x,y,z]=g+str(shade)
 def post(x,top,width=4,g='wood'):
  box((x-width//2,2,0),(x+width//2,6,top),g)
  if cartoon:box((x-width//2-1,1,top-3),(x+width//2+1,7,top-1),g)
 def rail(z,t=2,g='wood'):box((4,3,z),(36,5,z+t),g)
 if k=='skull':
  box((3,3,0),(13,9,19));box((2,2,0),(14,10,3));box((1,2,16),(15,10,19))
  # Crossbones on the front of a timber plinth.
  for i in range(8):
   for z in [5+i,12-i]:box((4+i,1,z),(6+i,3,z+2),'bone')
  # Rounded, filled cranium with actual recessed eye/nose sockets.
  rx=6 if cartoon else 6.5;rz=7
  for x in range(16):
   for y in range(12):
    for z in range(18,H):
     if ((x-7.5)/rx)**2+((y-5.5)/4.5)**2+((z-25)/rz)**2<=1:box((x,y,z),(x+1,y+1,z+1),'bone')
  box((5,2,18),(11,8,22),'bone')
  for x in [4,9]:
   for xx in range(x,x+3):
    for y in range(0,7):
     for z in range(23,26):v.pop((xx,y,z),None)
  for y in range(6):v.pop((7,y,21),None);v.pop((8,y,21),None)
  # Dark timber backing is visible through the sockets, matching the source sign.
  for x in [4,9]:box((x,7,23),(x+3,8,26),'wood')
  box((7,6,21),(9,7,23),'wood')
 elif k=='chain':
  for x in [4,36]:
   post(x,H-2,4);box((x-4,0,H-5),(x+4,8,H-1))
  # Interlocking squared links follow a gentle catenary; every link shares face contacts.
  for x in range(7,34):
   z=H-9-round(5*math.sin(math.pi*(x-7)/26))
   if x%4 in (0,3):box((x,3,z-1),(x+1,5,z+3),'metal')
   else:
    box((x,3,z-1),(x+1,5,z),'metal');box((x,3,z+2),(x+1,5,z+3),'metal')
  # Thin contiguous chain spine ensures strong links at stair-stepped sag changes.
  for x in range(6,34):
   z=H-9-round((4 if cartoon else 5)*math.sin(math.pi*(x-6)/28));box((x,3,z),(x+2,5,z+1),'metal')
 elif k in ['hoop','tube']:
  # Two metal arches, either round garden hoops or flat-topped bridge handrails.
  thick=3 if cartoon else 2
  for left in [4,20]:
   for x in range(left,left+17):
    u=(x-left)/16
    top=round(3+(H-4)*math.sin(math.pi*u)) if k=='hoop' else min(H-2,5+min(x-left,left+16-x)*3)
    prev=round(3+(H-4)*math.sin(math.pi*max(0,x-left-1)/16)) if k=='hoop' else min(H-2,5+min(max(0,x-left-1),left+17-x)*3)
    box((x,3,max(0,min(top-thick,prev-thick))),(x+1,5,max(top,prev)+1))
   for x in [left,left+16]:box((x,3,0),(x+2,5,6))
  if k=='tube':rail(2)
 elif k=='balustrade':
  box((2,1,0),(38,7,3));box((2,1,H-4),(38,7,H-1))
  for x in [4,12,20,28,36]:
   post(x,H-3,4 if cartoon else 2)
   box((x-2,2,5),(x+2,6,8));box((x-2,2,H-8),(x+2,6,H-5))
 else:
  if k not in ['picket','bamboo']:
   for x in [4,36]:post(x,H,4 if not cartoon else 6)
  if k=='rail':
   rail(4,3);rail(H-6,3)
  elif k=='iron':
   rail(4);rail(10);rail(H-5)
   for x in [12,20,28]:box((x-1,3,0),(x+1,5,H-2 if cartoon else H-3))
  else:
   if name!='PokeP_RusticFence':rail(4);rail(H-7)
   if k=='capped':rail(H-5,3)
   if name in ['PokeA_BridgePicket','PokeI_BridgeRailing']:rail(H-3,2)
   for j,x in enumerate([4,12,20,28,36]):
    w=6 if cartoon else (6 if name=='PokeN_WhitePicket' else 4)
    top=H-2 if cartoon else H-2-(j%2 if name in ['PokeE_WhitePicket','PokeQ_BambooFence'] else 0)
    if k=='capped' and x in [4,36]:continue
    box((x-w//2,2,0),(x+w//2,6,top))
    if (cartoon and name=='PokeN_WhitePicket') or name in ['PokeB_RosePicket','PokeH_FarmPicket','PokeP_RusticFence','PokeR_WhitePicket']:
     box((x-w//2+1,2,top),(x+w//2-1,6,top+1))
    if k=='bamboo':
     for z in [4,10,16]:box((x-w//2,1,z),(x+w//2,7,z+1))
 # Cartoon has a broader deliberate outline and exact X symmetry; all ordinary fences also mirror depth.
 if cartoon:
  for (x,y,z),c in list(v.items()):v[W-1-x,y,z]=c
  if k!='skull':
   for (x,y,z),c in list(v.items()):v[x,D-1-y,z]=c
  old=dict(v)
  for x,y,z in v:v[x,y,z]=old[min(x,W-1-x),min(y,D-1-y) if k!='skull' else y,z][:-1]+'1'
 primary='wood' if k in ('chain','skull') else f['material']
 v={p:(primary+s[4:] if s.startswith('wood') else s) for p,s in v.items()}
 return SimpleNamespace(size=tuple(f['size']),v=v)
