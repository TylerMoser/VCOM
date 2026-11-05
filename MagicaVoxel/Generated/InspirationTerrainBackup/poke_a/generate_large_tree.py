"""Build the 32x32x64 mature tree as one complete VOX file.
Preserves the earlier tree files. Uses the shared palette and VOX writer.
"""
from pathlib import Path
import math,json,hashlib
from generate_trees import write_vox,noise,interp,components,COLORS
ROOT=Path(__file__).resolve().parent
NAME='PokeA_ForestTree_Large'

def build():
 v={};c=15.5
 profile=[(3,1.9),(4,4.6),(6,6.5),(9,7.3),(12,6.7),(13,6.1),(14,6.6),(17,5.8),(19,4.6),(20,5.1),(22,4.2),(24,3.1),(26,1.4),(27,0.75)]
 for z in range(64):
  t=z*27/63
  radius=interp(t,profile)*2.15
  for x in range(32):
   for y in range(32):
    dx,dy=x-c,y-c;theta=math.atan2(dy,dx)
    trunk_radius=max(1,3.1-t*.07)
    root=z<4 and ((abs(dx)<1.6 and abs(dy)<6) or (abs(dy)<1.6 and abs(dx)<6))
    if (t<22 and dx*dx+dy*dy<=trunk_radius**2) or root:
     v[x,y,z]=12+int(noise(x//3,y//3,z//6,31)*3)
    lobe=1+.065*math.cos(5*theta+t*.13)+.035*math.sin(9*theta-t*.34)
    if t<3 or math.hypot(dx,dy)>radius*lobe:continue
    cluster=noise((x+int(t)//5)//3,(y-int(t)//6)//3,z//5,19)
    upper=z/63
    shade=.1+upper*5.7+(cluster-.5)*1.1
    shade+=.6*math.sin(theta*3+t*.8)+.45*math.cos(theta*5-t*.3)
    if upper>.74:shade+=1.5
    if any(abs(t-k)<.35 for k in (4,13,19)):shade-=.65
    shade+=(-dx-dy)*.0175
    v[x,y,z]=1+max(0,min(9,round(shade)))
 # Internal wooden column follows the trunk into the crown.
 for z in range(7,47):
  for x in range(14,18):
   for y in range(14,18):
    if (x,y,z) in v:v[x,y,z]=12+int(noise(x//2,y//2,z//6,31)*3)
 return v

def main():
 v=build()
 bounds=([min(p[a] for p in v) for a in range(3)],[max(p[a] for p in v) for a in range(3)])
 assert bounds==([0,0,0],[31,31,63]),bounds
 assert len(components(v))==1
 full=ROOT/(NAME+'.vox');write_vox(full,v,(32,32,64))
 manifest=dict(source='poke_a.jpg',file=full.name,size=[32,32,64],occupied_bounds=bounds,voxels=len(v),sha256=hashlib.sha256(full.read_bytes()).hexdigest(),palette=COLORS,scale=.0625,game_dimensions=[2,4,2],delivery='complete model only; no per-cell files',checks={'six_connected':True},note='Complete asset exceeds the current VoxelModel 62-side mesh limit. Integration is separate; do not auto-split.')
 (ROOT/'large-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('Complete:',len(v),'voxels, bounds',bounds)
if __name__=='__main__':main()
