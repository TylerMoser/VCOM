from pathlib import Path
import struct,json,hashlib,math
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];GAME=ROOT.parent/'VoxelXCOM'
DEST=GAME/'MagicaVoxel/Items'
PIN=json.loads((ROOT/'knowledge/palettes/crate-palette.json').read_text())
CRATE=[tuple(c) for c in PIN['rgba']]
def sha(b):return hashlib.sha256(b).hexdigest()
def i(*v):return struct.pack('<'+'i'*len(v),*v)
def s(v):
 b=str(v).encode();return i(len(b))+b
def d(v):return i(len(v))+b''.join(s(k)+s(val) for k,val in v.items())
def chunk(cid,b=b'',kids=b''):return cid.encode()+i(len(b),len(kids))+b+kids
def chunks(data,start=20,end=None):
 end=end or len(data)
 while start<end:
  cid,n,m=struct.unpack_from('<4sii',data,start)
  yield cid.decode(),data[start+12:start+12+n],data[start+12+n:start+12+n+m]
  start+=12+n+m
def read(path):
 data=Path(path).read_bytes();v={};pal=[];mats={};size=None
 for cid,b,k in chunks(data):
  if cid=='SIZE':size=struct.unpack('<iii',b)
  elif cid=='XYZI':v.update({tuple(q[:3]):q[3] for q in struct.iter_unpack('BBBB',b[4:])})
  elif cid=='RGBA':pal=list(struct.iter_unpack('BBBB',b))
  elif cid=='MATL':
   pos=4;n=struct.unpack_from('<i',b,pos)[0];pos+=4;props={}
   for _ in range(n):
    pair=[]
    for __ in range(2):
     count=struct.unpack_from('<i',b,pos)[0];pos+=4;pair.append(b[pos:pos+count].decode());pos+=count
    props[pair[0]]=pair[1]
   mats[struct.unpack_from('<i',b)[0]]=props
 return size,v,pal,mats
GLASS={'_type':'_glass','_trans':'.65','_rough':'.08','_ior':'.5','_ri':'1.5'}
EMIT={'_type':'_emit','_emit':'.65','_flux':'0','_ldr':'0'}
def writebytes(size,v,pal,mats):
 pal=list(pal)+[(0,0,0,255)]*(256-len(pal))
 b=chunk('SIZE',i(*size))+chunk('XYZI',i(len(v))+b''.join(bytes((*p,c)) for p,c in sorted(v.items())))
 b+=chunk('nTRN',i(0)+d({})+i(1,-1,-1,1)+d({}))+chunk('nGRP',i(1)+d({})+i(1,2))
 b+=chunk('nTRN',i(2)+d({})+i(3,-1,0,1)+d({'_t':f'0 0 {size[2]//2}'}))
 b+=chunk('nSHP',i(3)+d({})+i(1,0)+d({}))+chunk('LAYR',i(0)+d({})+i(-1))
 b+=chunk('RGBA',b''.join(bytes(c) for c in pal))
 b+=b''.join(chunk('MATL',i(c)+d(m)) for c,m in sorted(mats.items()) if c in set(v.values()))
 return b'VOX '+i(200)+chunk('MAIN',kids=b)
def remap(v,pal,mats):
 mapping={};outm={};reserved={}
 # Different material dictionaries may never collapse onto one palette index.
 for c in sorted(set(v.values()),key=lambda c:(mats.get(c,{}).get('_type','_diffuse')=='_diffuse',c)):
  mat=mats.get(c,{'_type':'_diffuse'}); signature=json.dumps(mat,sort_keys=True)
  rgb=pal[c-1][:3]
  candidates=[k for k in range(1,255) if k not in reserved or reserved[k]==signature]
  k=min(candidates,key=lambda k:sum((rgb[a]-CRATE[k-1][a])**2 for a in range(3)))
  mapping[c]=k;reserved[k]=signature;outm[k]=mat
 return {p:mapping[c] for p,c in v.items()},outm,mapping
def recolor_original(path):
 data=Path(path).read_bytes();size,v,pal,mats=read(path);_,newm,mapping=remap(v,pal,mats)
 out=b''
 for cid,b,kids in chunks(data):
  if cid=='RGBA':b=b''.join(bytes(c) for c in CRATE)
  elif cid=='XYZI':b=b[:4]+b''.join(bytes((*q[:3],mapping[q[3]])) for q in struct.iter_unpack('BBBB',b[4:]))
  elif cid in ('MATL','MATT','IMAP'):continue
  out+=chunk(cid,b,kids)
 out+=b''.join(chunk('MATL',i(c)+d(m)) for c,m in sorted(newm.items()))
 return data[:8]+chunk('MAIN',kids=out),mapping
class Model:
 def __init__(self):self.v={}
 def put(self,x,y,z,c):self.v[round(x),round(y),round(z)]=c
 def box(self,x0,x1,y0,y1,z0,z1,c):
  for x in range(round(x0),round(x1)+1):
   for y in range(round(y0),round(y1)+1):
    for z in range(round(z0),round(z1)+1):self.put(x,y,z,c)
 def line(self,a,b,c,r=0):
  n=max(abs(b[k]-a[k]) for k in range(3))*3+1;last=None
  for j in range(int(n)+1):
   p=tuple(round(a[k]+(b[k]-a[k])*j/n) for k in range(3))
   if last:
    cur=list(last)
    for ax in range(3):
     while cur[ax]!=p[ax]:
      cur[ax]+=1 if p[ax]>cur[ax] else -1;self.box(cur[0]-r,cur[0]+r,cur[1]-r,cur[1]+r,cur[2]-r,cur[2]+r,c)
   self.box(p[0]-r,p[0]+r,p[1]-r,p[1]+r,p[2]-r,p[2]+r,c);last=p
 def ellipsoid(self,cx,cy,cz,rx,ry,rz,c,shell=False):
  for x in range(math.floor(cx-rx),math.ceil(cx+rx)+1):
   for y in range(math.floor(cy-ry),math.ceil(cy+ry)+1):
    for z in range(math.floor(cz-rz),math.ceil(cz+rz)+1):
     t=((x-cx)/max(rx,.5))**2+((y-cy)/max(ry,.5))**2+((z-cz)/max(rz,.5))**2
     if t<=1.05 and (not shell or t>=.55):self.put(x,y,z,c)
 def cylinder(self,x,y,z0,z1,r,c):
  for z in range(z0,z1+1):
   for dx in range(-math.ceil(r),math.ceil(r)+1):
    for dy in range(-math.ceil(r),math.ceil(r)+1):
     if dx*dx+dy*dy<=r*r+.01:self.put(x+dx,y+dy,z,c)
 def ring(self,cx,cy,cz,rx,rz,c):
  pts=[(round(cx+rx*math.cos(j*math.pi/16)),cy,round(cz+rz*math.sin(j*math.pi/16))) for j in range(33)]
  for a,b in zip(pts,pts[1:]):self.line(a,b,c)
 def normalize(self):
  low=[min(p[a] for p in self.v) for a in range(3)];high=[max(p[a] for p in self.v) for a in range(3)]
  return tuple(high[a]-low[a]+1 for a in range(3)),{tuple(p[a]-low[a] for a in range(3)):c for p,c in self.v.items()},low

# Shared semantic slots: steel, dark iron, timber, leather, brass, cloth, accent,
# glass, luminous accent, pale material, dark material, food flesh, foliage, body.
BASE=[(157,175,186),(49,60,68),(125,79,43),(78,47,31),(190,143,63),(111,119,83),(171,57,56),(182,217,227),(241,157,54),(220,207,170),(31,36,40),(186,97,54),(74,132,71),(117,128,139)]
ELEMENTS={'Fire':(231,87,38),'Incendiary':(235,101,36),'Frost':(132,211,232),'Ice':(152,216,235),'Water':(49,137,202),'Flood':(45,124,178),'Air':(193,218,220),'Wind':(187,215,201),'Earth':(155,116,68),'Quake':(169,120,57),'Lightning':(241,211,75),'Shock':(235,202,66),'Poison':(113,173,60),'Acid':(170,204,48),'Nature':(64,150,83),'Blight':(131,72,137),'Shadow':(111,65,154),'Light':(240,218,137),'Arcane':(179,95,224),'Sand':(207,178,107),'Mud':(119,90,55),'Steam':(203,218,217),'Vacuum':(99,128,154),'Gravity':(118,95,201),'Ash':(132,134,137),'Spores':(181,137,183),'Oil':(82,86,110),'Mana':(69,126,218),'Healing':(205,57,66),'Smoke':(148,161,169),'Gas':(182,182,90),'Glue':(213,189,105)}
def palette(name,variant):
 p=BASE.copy();accent=next((v for k,v in ELEMENTS.items() if k in name),[(173,65,59),(64,116,139),(179,144,69),(133,82,176)][variant])
 p[6]=accent;p[8]=accent
 if variant==1:p[2]=(87,61,40);p[5]=(87,103,87)
 if variant==2:p[2]=(112,59,37);p[5]=(64,80,109)
 if variant==3:p[5]=(84,60,111)
 return [(*c,255) for c in p]+[(0,0,0,255)]*(256-len(p))
def materials(v):
 result={c:{'_type':'_diffuse','_rough':'.65'} for c in set(v.values())}
 if 8 in result:result[8]=dict(GLASS)
 if 9 in result:result[9]=dict(EMIT)
 return result
