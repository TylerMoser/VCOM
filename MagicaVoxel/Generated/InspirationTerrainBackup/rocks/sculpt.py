"""Solid faceted rocks, composed from clipped polygonal volumes, not sprite extrusions."""
import math,random

class Model:
 def __init__(self,size):self.size=tuple(size);self.v={}
 def put(self,x,y,z,label):
  p=(int(x),int(y),int(z))
  if all(0<=p[k]<self.size[k] for k in range(3)):self.v[p]=label
 def poly(self,cx,cy,rx,ry,height,z0=0,seed=1,cartoon=False,kind='boulder',group='stone'):
  rng=random.Random(seed)
  sides=8
  radii=[1]*sides if cartoon else [rng.uniform(.88,1.08) for _ in range(sides)]
  offset=(0,0) if cartoon else (rng.uniform(-.15,.15),rng.uniform(-.1,.1))
  for z in range(z0,z0+height):
   t=(z-z0+.5)/height
   if kind in ('shard','crystal','crag'):
    shoulder=.22 if kind=='shard' else (.68 if kind=='crystal' else .35)
    radius=(.75+t if t<.2 else (1 if t<shoulder else max(.1,(1-t)/(1-shoulder))))
   elif kind=='pillar':radius=.88 if t<.86 else 1.0-(t-.86)*1.6
   elif kind=='pebble':radius=min(.82+t*1.1,1.12-t*.65)
   else:
    # Broad shoulder and short crown facets; avoid making every boulder a cone.
    radius=(.80+1.2*t if t<.18 else (1.03-.2*t if t<.68 else .894-1.45*(t-.68)))
   for x in range(max(0,math.floor(cx-rx-2)),min(self.size[0],math.ceil(cx+rx+3))):
    for y in range(max(0,math.floor(cy-ry-2)),min(self.size[1],math.ceil(cy+ry+3))):
     nx=(x-cx)/rx-offset[0]*t;ny=(y-cy)/ry-offset[1]*t
     vals=[(nx*math.cos(k*math.pi/4)+ny*math.sin(k*math.pi/4))/radii[k] for k in range(sides)]
     if max(vals)>radius:continue
     # A clipped tilted crown makes a broad plane rather than a spherical dome.
     crown=t+(.08*abs(nx)+.08*abs(ny) if cartoon else .12*nx-.075*ny)
     if crown>1:continue
     facet=max(range(sides),key=lambda k:vals[k])
     if cartoon:shade=2 if t>.66 else (1 if t>.2 else 0)
     else:shade=([2,1,0,1,2,3,3,2][facet] if t<.73 else 3)
     self.put(x,y,z,group+str(shade))

def make(f,cartoon=False):
 w,d,h=f['size'];m=Model((w,d,h));cx=(w-1)/2;cy=(d-1)/2;s=f['seed'];kind=f['shape']
 def rock(x,y,rx,ry,height,z0=0,k='boulder',g='stone',seed=s):m.poly(x,y,rx,ry,height,z0,seed,cartoon,k,g)
 if kind in ('boulder','pebble','shard','crag','tipped'):
  rock(cx,cy,w*.49,d*.49,h,k='shard' if kind=='tipped' else kind)
  if kind=='tipped':
   for p in m.v:
    if p[2]>h*.68:m.v[p]='dry'+m.v[p][-1]
  if f['name'].endswith('_FracturedStone'):
   for p in list(m.v):
    x,y,z=p
    if y<d*.28 and z==int(h*.4+x*.13):del m.v[p]
 elif kind in ('pillar','moss_pillar'):
  rock(cx,cy,w*.49,d*.49,h,k='pillar')
  # Broken horizontal joints cut only the outer surface, leaving a strong core.
  for p in list(m.v):
   x,y,z=p
   joint=(z==h//3 or z==h*2//3)
   if joint and (y<d*.18 or (x>w*.82 and z==h//3)):del m.v[p]
  if not cartoon:
   for p in list(m.v):
    x,y,z=p
    if z>h-4 and x<w*.25 and y<d*.35:del m.v[p]
  if kind=='moss_pillar':
   for p in list(m.v):
    x,y,z=p
    if z>=h-3 or (z>h-7 and (x<w*.3 or y>d*.67)):m.v[p]='moss'+('1' if z>h-3 else '0')
 elif kind in ('cluster','pair','gravel'):
  if kind=='pair':
   rock(w*.37,d*.58,w*.32,d*.38,h,k='crag')
   rock(w*.65,d*.28,w*.33,d*.31,int(h*.58),seed=s+1)
  elif kind=='gravel':
   rock(w*.45,d*.58,w*.31,d*.36,h,seed=s)
   rock(w*.23,d*.28,w*.25,d*.29,max(3,int(h*.65)),seed=s+1)
   rock(w*.74,d*.31,w*.23,d*.3,max(3,int(h*.6)),seed=s+2)
  else:
   rock(w*.43,d*.56,w*.37,d*.4,h,seed=s)
   rock(w*.68,d*.29,w*.3,d*.29,int(h*.6),seed=s+1)
   rock(w*.2,d*.24,w*.22,d*.25,int(h*.45),seed=s+2)
 elif kind=='pile':
  rock(cx,cy,w*.49,d*.49,max(3,int(h*.28)),k='pebble')
  rock(cx-w*.08,cy+d*.06,w*.4,d*.38,int(h*.43),int(h*.15),seed=s+1)
  rock(cx+w*.07,cy,w*.28,d*.3,int(h*.57),int(h*.43),seed=s+2)
  rock(w*.82,d*.26,w*.16,d*.21,int(h*.25),seed=s+3)
 elif kind=='stack':
  n=2 if h>40 else 3
  for level in range(n):
   z0=level*h//n
   rock(cx+(0 if cartoon else (-1 if level%2 else 1)),cy,w*.48,d*.48,h//n+1,z0,k='pillar',seed=s+level)
  # Actual shallow pits persist when palette is flattened.
  for z0 in [h//n*i+h//n//2 for i in range(n)]:
   for ex in [int(w*.3),int(w*.65)]:
    for x in range(ex,ex+2):
     for z in range(z0,z0+2):
      ys=[y for xx,y,zz in m.v if xx==x and zz==z]
      if ys:m.v.pop((x,min(ys),z),None)
 elif kind=='ring':
  # Individual large stone facets on a continuous one-voxel contact ring.
  for i in range(8):
   a=i*math.pi/4
   rock(cx+8*math.cos(a),cy+8*math.sin(a),3.8,3.8,h if i%2==0 else h-1,seed=s+i)
  for x in range(w):
   for y in range(d):
    if 7.4<=math.hypot(x-cx,y-cy)<=10:m.put(x,y,0,'stone1')
 elif kind=='geode':
  rock(cx,cy,w*.49,d*.49,h,k='crag')
  # Open-front pocket with thick back wall and roof; not a black painted spot.
  for p in list(m.v):
   x,y,z=p
   if y<d*.62 and abs(x-cx)<w*.28 and h*.15<z<h*.72:del m.v[p]
  rock(cx,cy-d*.20,w*.125,d*.20,int(h*.65),int(h*.12),k='crystal',g='crystal',seed=s+1)
  rock(cx-w*.18,cy-d*.18,w*.10,d*.15,int(h*.43),int(h*.12),k='crystal',g='crystal',seed=s+2)
  rock(cx+w*.18,cy-d*.18,w*.10,d*.15,int(h*.43),int(h*.12),k='crystal',g='crystal',seed=s+3)
 elif kind=='crystals':
  rock(cx,cy,w*.49,d*.48,max(3,h//6),k='pebble',g='crystal')
  rock(cx,cy+d*.15,w*.16,d*.23,h,k='crystal',g='crystal')
  rock(cx-w*.26,cy-d*.13,w*.15,d*.21,int(h*.62),k='crystal',g='crystal',seed=s+1)
  rock(cx+w*.26,cy-d*.13,w*.15,d*.21,int(h*.48),k='crystal',g='crystal',seed=s+2)
 else:raise ValueError(kind)
 if cartoon:
  # Bilateral front balance for directional slabs/crystal openings. Natural rock
  # clusters retain lobes but gain deliberate X/Y balance in their cartoon form.
  depth=kind not in ('geode','stack','crystals')
  old=m.v;m.v={}
  for (x,y,z),label in sorted(old.items()):
   points=[(x,y,z),(w-1-x,y,z)]
   if depth:points.extend([(x,d-1-y,z),(w-1-x,d-1-y,z)])
   for p in points:
    if p not in m.v or label>m.v[p]:m.v[p]=label
  # Paint the finished union in broad, symmetric regions, not overlapping part
  # highlights, which would leave incidental stippling on a cartoon cluster.
  for p,label in list(m.v.items()):
   if label.startswith('stone'):m.v[p]='stone'+str(2 if p[2]>h*.65 else (1 if p[2]>h*.18 else 0))
 return m
