"""Local VOX I/O helpers inherited from the verified poke_a generators."""
import struct

def chunk(cid,payload=b'',children=b''):
 return cid.encode()+struct.pack('<ii',len(payload),len(children))+payload+children

def string(s):
 b=str(s).encode();return struct.pack('<i',len(b))+b

def dictionary(d):return struct.pack('<i',len(d))+b''.join(string(k)+string(v) for k,v in d.items())

def components(v):
 left=set(v);sizes=[]
 while left:
  todo=[left.pop()];size=0
  while todo:
   x,y,z=todo.pop();size+=1
   for p in [(x+1,y,z),(x-1,y,z),(x,y+1,z),(x,y-1,z),(x,y,z+1),(x,y,z-1)]:
    if p in left:left.remove(p);todo.append(p)
  sizes.append(size)
 return sorted(sizes,reverse=True)

def read(path):
 data=path.read_bytes();pos=20;size=None;vox=None;palette=None
 while pos<len(data):
  cid,n,m=struct.unpack_from('<4sii',data,pos);p=data[pos+12:pos+12+n]
  if cid==b'SIZE':size=struct.unpack('<iii',p)
  if cid==b'XYZI':vox={tuple(r[:3]):r[3] for r in struct.iter_unpack('BBBB',p[4:])}
  if cid==b'RGBA':palette=[tuple(c) for c in struct.iter_unpack('BBBB',p)]
  pos+=12+n+m
 assert size and vox and len(palette)==256
 return size,vox,palette

def write(path,size,vox,palette):
 assert len(palette)==256
 graph=chunk('nTRN',struct.pack('<i',0)+dictionary({})+struct.pack('<iiii',1,-1,-1,1)+dictionary({}))
 graph+=chunk('nGRP',struct.pack('<i',1)+dictionary({})+struct.pack('<ii',1,2))
 graph+=chunk('nTRN',struct.pack('<i',2)+dictionary({'_name':path.stem})+struct.pack('<iiii',3,-1,0,1)+dictionary({'_t':f'0 0 {size[2]//2}'}))
 graph+=chunk('nSHP',struct.pack('<i',3)+dictionary({})+struct.pack('<ii',1,0)+dictionary({}))
 body=chunk('SIZE',struct.pack('<iii',*size))+chunk('XYZI',struct.pack('<i',len(vox))+b''.join(bytes((*p,c)) for p,c in sorted(vox.items())))+graph
 body+=chunk('LAYR',struct.pack('<i',0)+dictionary({'_name':'Deadwood'})+struct.pack('<i',-1))
 body+=chunk('RGBA',b''.join(bytes(c) for c in palette))
 for c in sorted(set(vox.values())):body+=chunk('MATL',struct.pack('<i',c)+dictionary({'_type':'_diffuse','_rough':'1'}))
 path.write_bytes(b'VOX '+struct.pack('<i',200)+chunk('MAIN',children=body))
