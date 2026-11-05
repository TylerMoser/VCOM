"""Nine independent complete-tree variants; never overwrites the three originals.
Cartoon: symmetric sculpt and color. CratePalette: recolor only. TwoColor: recolor only.
Run with Python from any directory. Palette snapshot is local for reproducibility.
"""
from pathlib import Path
import json, struct, math, hashlib
from generate_trees import chunk,dictionary,components
ROOT=Path(__file__).resolve().parent
BASES=['PokeA_ForestTree_Large','PokeA_ForestTree','PokeA_Sapling']

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
 body+=chunk('LAYR',struct.pack('<i',0)+dictionary({'_name':'Tree'})+struct.pack('<i',-1))
 body+=chunk('RGBA',b''.join(bytes(c) for c in palette))
 for c in sorted(set(vox.values())):body+=chunk('MATL',struct.pack('<i',c)+dictionary({'_type':'_diffuse','_rough':'1'}))
 path.write_bytes(b'VOX '+struct.pack('<i',200)+chunk('MAIN',children=body))

def cartoon(size,original):
 n=size[0];h=max(p[2] for p in original)+1
 width=max(max(p[0] for p in original)-min(p[0] for p in original)+1,max(p[1] for p in original)-min(p[1] for p in original)+1)
 c=(n-1)/2;R=width/2-.25;v={}
 # Rounded, intentional three-tier silhouette; no random edge noise or stippling.
 profile=[(.10,.10),(.15,.52),(.27,.94),(.36,1),(.49,.87),(.53,.73),(.57,.84),(.68,.72),(.75,.52),(.78,.60),(.88,.43),(1,.045)]
 for z in range(h):
  t=z/(h-1)
  rad=0
  for (a,ra),(b,rb) in zip(profile,profile[1:]):
   if a<=t<=b:
    q=(t-a)/(b-a);q=q*q*(3-2*q)
    rad=R*(ra+(rb-ra)*q);break
  if t>.97:rad=max(.75,rad)
  for x in range(n):
   for y in range(n):
    dx,dy=abs(x-c),abs(y-c);r2=dx*dx+dy*dy
    trunk=max(.75,width*.095-t*width*.035)
    root=z<max(1,round(h*.06)) and ((dx<width*.06 and dy<width*.21) or (dy<width*.06 and dx<width*.21))
    if (t<.75 and r2<=trunk*trunk) or root:v[x,y,z]=13
    # Algebraic cos(4theta) is exactly invariant under swaps/sign changes.
    lobes=(dx**4-6*dx*dx*dy*dy+dy**4)/(r2*r2) if r2 else 1
    if t>=.10 and math.sqrt(r2)<=rad*(1+.018*lobes):
     v[x,y,z]=4 if t<.53 else (6 if t<.78 else 8)
 # Consistent hidden wood core also obeys quarter-turn symmetry.
 for p in list(v):
  x,y,z=p
  if z<h*.7 and (x-c)**2+(y-c)**2<=(width*.07)**2:v[p]=13
 assert {(n-1-y,x,z):col for (x,y,z),col in v.items()}==v
 assert {(n-1-x,y,z):col for (x,y,z),col in v.items()}==v
 return v

def main():
 crate=json.loads((ROOT/'crate-palette.json').read_text(encoding='utf-8'))
 crate_palette=[tuple(c) for c in crate['rgba']]
 records=[]
 for base in BASES:
  path=ROOT/(base+'.vox');source_hash=hashlib.sha256(path.read_bytes()).hexdigest()
  size,original,palette=read(path)
  variants={}
  variants['Cartoon']=(cartoon(size,original),palette)
  # Restrict to established Apollo greens and the actual brown slots used by the crate.
  mapping={}
  for c in set(original.values()):
   allowed=range(241,247) if c<=10 else (178,179,180)
   mapping[c]=min(allowed,key=lambda i:sum((palette[c-1][a]-crate_palette[i-1][a])**2 for a in range(3)))
  variants['CratePalette']=({p:mapping[c] for p,c in original.items()},crate_palette)
  green=(61,123,75,255);brown=(116,80,45,255)
  variants['TwoColor']=({p:1 if c<=10 else 2 for p,c in original.items()},[green,brown]+[green]*254)
  for style,(vox,pal) in variants.items():
   assert len(components(vox))==1,(base,style)
   assert all(0<=p[a]<size[a] for p in vox for a in range(3))
   assert all(1<=c<=254 for c in vox.values())
   if style!='Cartoon':assert vox.keys()==original.keys()
   if style=='TwoColor':assert set(vox.values())=={1,2} and len({pal[c-1] for c in vox.values()})==2
   name=f'{base}_{style}.vox';dest=ROOT/name;write(dest,size,vox,pal)
   r=dict(file=name,source=path.name,source_sha256=source_hash,style=style,canvas=size,occupied_min=[min(p[a] for p in vox) for a in range(3)],occupied_max=[max(p[a] for p in vox) for a in range(3)],voxels=len(vox),used_indices=sorted(set(vox.values())),used_rgba=[pal[c-1] for c in sorted(set(vox.values()))],sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),checks={'single_connected_component':True,'geometry_preserved':style!='Cartoon','quarter_turn_geometry_and_color_symmetry':style=='Cartoon','exactly_two_colors':style=='TwoColor'})
   if style=='CratePalette':
    r['palette_sha256']=hashlib.sha256(b''.join(bytes(c) for c in pal)).hexdigest();assert r['palette_sha256']==crate['palette_sha256'];r['index_mapping']=mapping
   records.append(r)
  assert hashlib.sha256(path.read_bytes()).hexdigest()==source_hash
 (ROOT/'variations-manifest.json').write_text(json.dumps({'models':records,'interpretation':'Three independent styles of each of the three existing complete trees, not cumulative combinations.','crate_palette_source':crate['source'],'crate_palette_sha256':crate['palette_sha256']},indent=2)+'\n',encoding='utf-8')
 for r in records:print(r['file'],r['voxels'],'voxels;',len(r['used_indices']),'colors')
if __name__=='__main__':main()
