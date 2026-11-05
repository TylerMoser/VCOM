"""Volumetric leaves, blades, stems and flowers. All dimensions in voxels."""
import math,random
class Model:
 def __init__(self,size):self.size=tuple(size);self.v={}
 def put(self,p,label):
  p=tuple(round(t) for t in p)
  if all(0<=p[k]<self.size[k] for k in range(3)):self.v[p]=label
 def ball(self,c,r,label):
  if isinstance(r,(int,float)):r=(r,r,r)
  for x in range(math.floor(c[0]-r[0]),math.ceil(c[0]+r[0])+1):
   for y in range(math.floor(c[1]-r[1]),math.ceil(c[1]+r[1])+1):
    for z in range(math.floor(c[2]-r[2]),math.ceil(c[2]+r[2])+1):
     if sum(((p-q)/max(.6,s))**2 for p,q,s in zip((x,y,z),c,r))<=1.15:self.put((x,y,z),label)
 def line(self,a,b,r,label):
  steps=max(2,int(sum(abs(b[k]-a[k]) for k in range(3))*3))
  last=None
  for i in range(steps+1):
   p=tuple(round(a[k]+(b[k]-a[k])*i/steps) for k in range(3))
   if last is not None:
    bridge=list(last)
    for k in range(3):
     bridge[k]=p[k];self.ball(bridge,r,label)
   self.ball(p,r,label);last=p

def make(f,cartoon=False):
 m=Model(f['size']);w,d,h=m.size;cx=(w-1)/2;cy=(d-1)/2;rng=random.Random(f['seed']);kind=f['shape']
 def leaf(a,angle,length,height,width=1.5):
  vx,vy=math.cos(angle),math.sin(angle);prev=a
  for i in range(1,17):
   t=i/16;p=(a[0]+vx*length*t,a[1]+vy*length*t,a[2]+height*math.sin(t*math.pi*.46))
   rad=max(.5,width*math.sin(math.pi*t)**.6)
   m.line(prev,p,(rad,rad,.7),'leaf');prev=p
 def tuft(x,y,zheight,radius,count=7):
  m.ball((x,y,.5),(1.4,1.4,1),'leaf')
  for j in range(count):
   angle=j*math.tau/count+(0 if cartoon else .13)
   height=zheight*(1 if j%2==0 else .72) if cartoon else zheight*(.55+rng.random()*.45)
   leaf((x,y,0),angle,radius*(.9 if cartoon else .65+rng.random()*.35),height,1.25 if cartoon else 1)
 def blossom(x,y,z,r,petals=5,vertical=False,core='seed'):
  m.line((x,y,0),(x,y,z),.65,'leaf')
  leaf((x,y,max(0,z*.2)),0,r*.9,max(1,z*.15),1)
  leaf((x,y,max(0,z*.35)),math.pi,r*.8,max(1,z*.12),1)
  for j in range(petals):
   a=j*math.tau/petals
   if vertical:c=(x+math.cos(a)*r*.62,y,z+math.sin(a)*r*.62);rad=(r*.48,.9,r*.48)
   else:c=(x+math.cos(a)*r*.62,y+math.sin(a)*r*.62,z);rad=(r*.48,r*.48,1)
   m.ball(c,rad,'petal')
   m.line((x,y,z),c,.65,'petal')
  m.ball((x,y-.5 if vertical else y,z if vertical else z+.6),(max(1,r*.27),.8 if vertical else max(1,r*.27),max(1,r*.27) if vertical else .8),core)
 if kind in ('grass','grass_tile','turf','wheat','seedlings'):
  if kind=='grass':centers=[(cx,cy)];height=h-2;radius=min(w,d)*.42
  elif kind=='turf':centers=[(4,4),(11,4),(4,11),(11,11)];height=2;radius=2
  elif kind=='seedlings':centers=[(4,4),(11,4),(4,11),(11,11)];height=h-2;radius=3
  else:centers=[(4,4),(11,4),(4,11),(11,11)];height=h-3;radius=4
  for x,y in centers:
   if not cartoon:x+=rng.choice([-1,0,1]);y+=rng.choice([-1,0,1])
   if kind=='wheat':
    for a in [0,math.pi/2,math.pi,math.pi*1.5]:
     x1=x+math.cos(a)*1.8;y1=y+math.sin(a)*1.8;top=h-5-(0 if cartoon else rng.randrange(4))
     m.line((x,y,0),(x1,y1,top),.55,'leaf')
     for level in range(4):m.ball((x1+(level%2-.5)*1.4,y1,top-5+level*2),(1.2,1.1,1.2),'leaf')
     leaf((x,y,4),a,3,8,.8)
   else:tuft(x,y,height,radius,4 if cartoon else 6)
 elif kind in ('flowers','single','star','giant','sunflower'):
  if kind in ('single','giant','sunflower'):centers=[(cx,cy)];r=min(w,d)*.43
  else:
   lo=(w-1)*.25;hi=(w-1)*.75;ly=(d-1)*.25;hy=(d-1)*.75
   centers=[(round(lo),round(ly)),(round(hi),round((d-1)*.4)),(round((w-1)*.4),round(hy))] if not cartoon else [(round(lo),round(ly)),(round(hi),round(ly)),(round(lo),round(hy)),(round(hi),round(hy))]
   r=min(w,d)*(.16 if kind!='star' else .19)
  for j,(x,y) in enumerate(centers):
   vertical=kind=='sunflower';z=(h-1-r) if vertical else h-3-(0 if cartoon else j%3)
   blossom(x,y,z,r,4 if cartoon else (8 if kind in ('sunflower','star') else 5),vertical,core='darkseed' if kind in ('sunflower','giant') else 'seed')
 elif kind in ('spike','bell','bud','cattail'):
  if kind=='spike':centers=[(cx,cy)] if w<16 else ([(5,5),(10,10)] if not cartoon else [(4,4),(11,4),(4,11),(11,11)])
  else:centers=[(cx,cy)]
  for j,(x,y) in enumerate(centers):
   top=h-2-(j%2*3 if not cartoon else 0)
   m.line((x,y,0),(x,y,top),.8,'leaf')
   for a in range(4):leaf((x,y,0),a*math.pi/2,min(w,d)*.27,5,1.4)
   if kind=='cattail':
    for z in range(h//2,top):m.ball((x,y,z),(2,2,1),'petal')
   elif kind=='bud':
    # Open purple spathe around an exposed yellow spadix; not a closed bud.
    for a in range(4 if cartoon else 5):
     angle=a*math.tau/(4 if cartoon else 5)
     leaf((x,y,1),angle,w*.35,h*.48,3)
    for p in list(m.v):
     if p[2]<h*.65 and p[2]>2:m.v[p]='petal'
    m.line((x,y,2),(x,y,h-2),2.2,'seed')
    m.ball((x,y,h-3),(2,2,2),'seed')
   else:
    for z in range(max(5,h//3),top,4):
     rad=2.8*(1-.6*max(0,(z-h/3)/(h*2/3))) if kind=='spike' else 3.2
     for a in range(4 if cartoon else 3):
      angle=a*math.tau/(4 if cartoon else 3);p=(x+math.cos(angle)*rad*.7,y+math.sin(angle)*rad*.7,z)
      m.ball(p,(rad*.7,rad*.7,1.6),'petal');m.line((x,y,z),p,.6,'petal')
    m.ball((x,y,top-1),(1.1,1.1,1.4),'petal')
 elif kind in ('pad','pads','lily'):
  centers=[(cx,cy,min(w,d)*.45)] if kind!='pads' else ([(3,3,2.5),(12,3,2.5),(3,12,2.5),(12,12,2.5)] if cartoon else [(4,4,3),(11,5,3),(7,11,3.4)])
  for x,y,r in centers:
   m.ball((x,y,.4),(r,r,.8),'leaf')
   for p in list(m.v):
    if p[0]>x and abs(p[1]-y)<(p[0]-x)*.3:m.v.pop(p,None)
  if kind=='lily':blossom(cx,cy,2,min(w,d)*.25,4 if cartoon else 5)
 elif kind=='fern':
  m.ball((cx,cy,0),1.3,'leaf')
  for j in range(4 if cartoon else 5):
   a=j*math.tau/(4 if cartoon else 5);vx,vy=math.cos(a),math.sin(a)
   for k in range(1,8):
    t=k/8;p=(cx+vx*w*.38*t,cy+vy*d*.38*t,h*.8*t)
    m.line((cx,cy,0),p,.6,'leaf')
    for side in [-1,1]:m.line(p,(p[0]-vy*side*2.8*(1-t),p[1]+vx*side*2.8*(1-t),p[2]+1),.6,'leaf')
 elif kind=='twoleaf':
  m.ball((cx,cy,0),1.2,'leaf')
  for a in [math.pi*.25,math.pi*1.25]:
   leaf((cx,cy,0),a,min(w,d)*.38,h*.6,2)
 elif kind=='rosette':
  m.ball((cx,cy,0),1.2,'leaf')
  for i in range(4 if cartoon else 5):leaf((cx,cy,0),i*math.tau/(4 if cartoon else 5),min(w,d)*.4,h*.85,max(1,min(w,d)*.1))
  if f['petal']=='red':
   for p in list(m.v):
    if p[2]>h*.55:m.v[p]='petal'
 elif kind=='leafmat':
  for x in [3,8,12]:
   for y in [3,8,12]:
    top=h*.55 if cartoon else h*(.42+rng.random()*.18)
    m.ball((x,y,top*.45),(3.5,3.5,top*.65),'leaf')
    m.line((x,y,0),(x,y,top),1,'leaf')
    m.ball((x-1,y,top),(2,2,1.4),'leaf')
 elif kind=='hedge':
  m.ball((cx,cy,h*.32),(w*.46,d*.46,h*.55),'leaf')
  for i in range(7 if not cartoon else 8):
   a=i*math.tau/(7 if not cartoon else 8)
   x=cx+math.cos(a)*w*.34;y=cy+math.sin(a)*d*.34
   m.ball((x,y,h*.52),(w*.16,d*.16,h*.32),'leaf')
   m.line((x,y,h*.5),(x,y,h-1-(i%3 if not cartoon else 0)),1,'leaf')
 else:raise ValueError(kind)
 # Match the bottom plane, with no modeled soil pedestal.
 low=min(p[2] for p in m.v);m.v={(x,y,z-low):label for (x,y,z),label in m.v.items()}
 if cartoon:
  rank={'leaf':0,'petal':1,'seed':2,'darkseed':2};sym={}
  for (x,y,z),label in m.v.items():
   orbit=[(x,y,z),(w-1-x,y,z),(x,d-1-y,z),(w-1-x,d-1-y,z)]
   for q in orbit:
    if q not in sym or rank[label]>rank[sym[q]]:sym[q]=label
  m.v=sym
 # Broad coherent shade regions, symmetrically assigned for Cartoon.
 m.v={p:label+str(min(2,int(p[2]*3/max(1,h)))) for p,label in m.v.items()}
 return m
