"""Deterministic voxel reconstructions of the two tree silhouettes in poke_a.jpg.
Run from any directory. Rewrites only this generator's named outputs.
"""
from pathlib import Path
import math, struct, json, hashlib
ROOT=Path(__file__).resolve().parent
# Small shared palette, matched to the reference's teal -> yellow-green foliage.
COLORS=[(23,49,45),(29,62,54),(34,76,61),(40,91,67),(48,106,70),
        (61,123,75),(78,140,80),(98,156,85),(123,174,93),(150,189,105),
        (47,35,27),(67,47,31),(91,63,37),(116,80,45),(140,102,57)]
def chunk(cid,payload=b'',children=b''):
 return cid.encode()+struct.pack('<ii',len(payload),len(children))+payload+children
def string(s):
 b=str(s).encode();return struct.pack('<i',len(b))+b
def dictionary(d):return struct.pack('<i',len(d))+b''.join(string(k)+string(v) for k,v in d.items())
def write_vox(path,vox,size):
 assert all(0<=p[a]<size[a] for p in vox for a in range(3))
 assert all(1<=c<=254 for c in vox.values())
 graph=chunk('nTRN',struct.pack('<i',0)+dictionary({})+struct.pack('<iiii',1,-1,-1,1)+dictionary({}))
 graph+=chunk('nGRP',struct.pack('<i',1)+dictionary({})+struct.pack('<ii',1,2))
 graph+=chunk('nTRN',struct.pack('<i',2)+dictionary({'_name':path.stem})+struct.pack('<iiii',3,-1,0,1)+dictionary({'_t':f'0 0 {size[2]//2}'}))
 graph+=chunk('nSHP',struct.pack('<i',3)+dictionary({})+struct.pack('<ii',1,0)+dictionary({}))
 palette=b''.join(bytes((*c,255)) for c in COLORS)+bytes((0,0,0,255))*(256-len(COLORS))
 body=chunk('SIZE',struct.pack('<iii',*size))+chunk('XYZI',struct.pack('<i',len(vox))+b''.join(bytes((*p,c)) for p,c in sorted(vox.items(),key=lambda v:(v[0][2],v[0][1],v[0][0]))))
 body+=graph+chunk('LAYR',struct.pack('<i',0)+dictionary({'_name':'Tree'})+struct.pack('<i',-1))+chunk('RGBA',palette)
 for i in range(1,len(COLORS)+1):body+=chunk('MATL',struct.pack('<i',i)+dictionary({'_type':'_diffuse','_rough':'1'}))
 path.write_bytes(b'VOX '+struct.pack('<i',200)+chunk('MAIN',children=body))
def noise(x,y,z,seed=7):
 h=(x*374761393+y*668265263+z*2147483647+seed*1274126177)&0xffffffff
 h=((h^(h>>13))*1274126177)&0xffffffff
 return ((h^(h>>16))&65535)/65535

def interp(z,points):
 for (a,ra),(b,rb) in zip(points,points[1:]):
  if a<=z<=b:return ra+(rb-ra)*(z-a)/(b-a)
 return 0

def tree(small=False):
 # Mature: compact, tall pear-shaped crown with overlapping scalloped leaf skirts.
 # Sapling: same visual family but narrower, with two distinct leaf tiers.
 v={};h=16 if small else 28;c=7.5
 profile=([(2,1.1),(3,2.5),(5,3.7),(7,3.4),(8,2.7),(9,3.0),(11,2.4),(13,1.5),(15,0.65)] if small else
 [(3,1.9),(4,4.6),(6,6.5),(9,7.3),(12,6.7),(13,6.1),(14,6.6),(17,5.8),(19,4.6),(20,5.1),(22,4.2),(24,3.1),(26,1.4),(27,0.75)])
 # Bark: solid, narrow stem and low buttress roots. No separate floating foliage.
 for z in range(10 if small else 22):
  radius=(0.9 if small else 1.55) - z*(0.025 if small else 0.035)
  for x in range(16):
   for y in range(16):
    dx,dy=x-c,y-c
    root=(z<2 and ((abs(dx)<0.8 and abs(dy)<(2 if small else 3)) or (abs(dy)<0.8 and abs(dx)<(2 if small else 3))))
    if dx*dx+dy*dy<=radius*radius or root:
     v[x,y,z]=12+int(noise(x//2,y//2,z//4,31)*3)
 for z in range(profile[0][0],h):
  radius=interp(z,profile)
  for x in range(16):
   for y in range(16):
    dx,dy=x-c,y-c;theta=math.atan2(dy,dx)
    # Softly lobed perimeter, four major lobes plus finer leafy scallops.
    lobe=1+0.065*math.cos(5*theta+z*0.13)+0.035*math.sin(9*theta-z*.34)
    radial=math.hypot(dx,dy/0.94)
    if radial>radius*lobe:continue
    # Broad, coherent color clusters instead of uncorrelated speckled noise.
    cluster=noise((x+z//5)//2,(y-z//6)//2,z//3,19)
    upper=z/(h-1)
    shade=0.1+upper*5.7+(cluster-.5)*1.1
    # Highlight leaf tips/upper shoulders, avoiding a hard horizontal paint stripe.
    shade+=0.6*math.sin(theta*3+z*.8)+0.45*math.cos(theta*5-z*.3)
    if upper>.74:shade+=1.5
    if z in ([3,8] if small else [4,13,19]):shade-=.65
    # A subtle directional cue, less than a palette step so rotation still works.
    shade+=(-dx-dy)*.035
    col=1+max(0,min(9,round(shade)))
    v[x,y,z]=col
 # Restore the hidden central structural trunk so erosion reveals wood.
 for z in range(3,8 if small else 20):
  for x in ([7,8] if not small else [7]):
   for y in ([7,8] if not small else [7]):
    if (x,y,z) in v:v[x,y,z]=12+int(noise(x,y,z//3,31)*3)
 return v

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

def main():
 models={'PokeA_ForestTree':(tree(),(16,16,32)), 'PokeA_Sapling':(tree(True),(16,16,16))}
 records=[]
 for name,(vox,size) in models.items():
  assert len(components(vox))==1
  path=ROOT/(name+'.vox');write_vox(path,vox,size)
  records.append(dict(file=path.name,size=size,voxels=len(vox),occupied_min=[min(p[a] for p in vox) for a in range(3)],occupied_max=[max(p[a] for p in vox) for a in range(3)],components=components(vox),role='complete model',sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
 (ROOT/'manifest.json').write_text(json.dumps(dict(source='poke_a.jpg',palette=COLORS,models=records,scale=.0625,delivery='complete models only; no per-cell files',checks={'six_connected':True}),indent=2)+'\n')
 for r in records:print(r['file'],r['voxels'])
if __name__=='__main__':main()
