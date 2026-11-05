"""Complete environmental model VOX scenes; oversized spans use two internal architectural halves.
No separate cell files. Parser flattens the actual graph for independent QA.
"""
import struct,sys
from pathlib import Path
from legacy_voxlib import chunk,dictionary,components
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'))
from inspect_vox import Reader
def write(path,size,vox,palette,materials=None):
 parts=[(0,size[0])] if size[0]<=256 else [(0,size[0]//2),(size[0]//2,size[0])]
 body=chunk('PACK',struct.pack('<i',len(parts))) if len(parts)>1 else b''
 for start,end in parts:
  data=[(x-start,y,z,c) for (x,y,z),c in sorted(vox.items()) if start<=x<end]
  body+=chunk('SIZE',struct.pack('<iii',end-start,size[1],size[2]))+chunk('XYZI',struct.pack('<i',len(data))+b''.join(bytes(p) for p in data))
 body+=chunk('nTRN',struct.pack('<i',0)+dictionary({'_name':path.stem,'_canvas':' '.join(map(str,size))})+struct.pack('<iiii',1,-1,-1,1)+dictionary({}))
 body+=chunk('nGRP',struct.pack('<i',1)+dictionary({})+struct.pack('<i',len(parts))+b''.join(struct.pack('<i',2+i*2) for i in range(len(parts))))
 for i,(start,end) in enumerate(parts):
  offset=start+(end-start)//2-size[0]//2
  body+=chunk('nTRN',struct.pack('<i',2+i*2)+dictionary({'_name':'Whole model' if len(parts)==1 else f'Half {i+1}'})+struct.pack('<iiii',3+i*2,-1,0,1)+dictionary({'_t':f'{offset} 0 {size[2]//2}'}))
  body+=chunk('nSHP',struct.pack('<i',3+i*2)+dictionary({})+struct.pack('<ii',1,i)+dictionary({}))
 body+=chunk('LAYR',struct.pack('<i',0)+dictionary({'_name':'Complete environmental model'})+struct.pack('<i',-1))
 body+=chunk('RGBA',b''.join(bytes(c) for c in palette))
 for c in sorted(set(vox.values())):body+=chunk('MATL',struct.pack('<i',c)+dictionary((materials or {}).get(c,{'_type':'_diffuse','_rough':'1'})))
 path.write_bytes(b'VOX '+struct.pack('<i',200)+chunk('MAIN',children=body))
def read(path):
 data=path.read_bytes();pos=20;models=[];nodes={};palette=None
 while pos<len(data):
  cid,n,m=struct.unpack_from('<4sii',data,pos);payload=data[pos+12:pos+12+n];r=Reader(payload)
  if cid==b'SIZE':models.append({'size':tuple(r.integer() for _ in range(3))})
  if cid==b'XYZI':
   count=r.integer();records=list(struct.iter_unpack('BBBB',r.take(count*4)));assert len(set(v[:3] for v in records))==count
   models[-1]['vox']={p[:3]:p[3] for p in records}
  if cid in (b'nTRN',b'nGRP',b'nSHP'):
   idx=r.integer();attrs=r.dictionary();node={'type':cid,'attrs':attrs};nodes[idx]=node
   if cid==b'nTRN':
    node['child']=r.integer();r.integer();r.integer();assert r.integer()==1;node['frame']=r.dictionary()
   if cid==b'nGRP':node['children']=[r.integer() for _ in range(r.integer())]
   if cid==b'nSHP':
    assert r.integer()==1;node['model']=r.integer();r.dictionary()
  if cid==b'RGBA':palette=[tuple(p) for p in struct.iter_unpack('BBBB',payload)]
  pos+=12+n+m
 canvas=tuple(map(int,nodes[0]['attrs']['_canvas'].split()));out={}
 def walk(idx,t=(0,0,0),seen=frozenset()):
  assert idx not in seen;node=nodes[idx];seen=seen|{idx}
  if node['type']==b'nTRN':
   assert '_r' not in node['frame'];dt=tuple(map(int,node['frame'].get('_t','0 0 0').split()));walk(node['child'],tuple(t[i]+dt[i] for i in range(3)),seen)
  elif node['type']==b'nGRP':
   for child in node['children']:walk(child,t,seen)
  else:
   model=models[node['model']]
   for p,c in model['vox'].items():
    q=tuple(p[i]-model['size'][i]//2+t[i]+(canvas[i]//2 if i<2 else 0) for i in range(3));assert q not in out
    out[q]=c
 walk(0);return canvas,out,palette,len(models)
