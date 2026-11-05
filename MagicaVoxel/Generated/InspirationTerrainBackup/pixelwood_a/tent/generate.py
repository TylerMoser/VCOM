"""Deterministic tent authoring; owns seven PixelwoodA_Tent*.vox files only."""
from pathlib import Path
import sys,math,json,hashlib,argparse
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
WORK=ROOT.parent.parent
sys.path.insert(0,str(ROOT))
from voxlib import write,read,components
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
SIZE=(64,64,32)
def build(cartoon):
 v={};g={}
 def put(x,y,z,col,group='canvas'):
  if 0<=x<64 and 0<=y<64 and 0<=z<32:v[x,y,z]=col;g[x,y,z]=group
 def roof(x):return round(29*(1-abs(x-31.5)/27.5))
 # Two-voxel cloth thickness makes diagonal stair steps face-connected.
 for x in range(4,60):
  z=roof(x)
  for y in range(4,60):
   vent=(15<=x<=19 or 44<=x<=48) and 24<=y<=36
   if vent:continue
   shade=5 if cartoon else (5 if x<32 else 3)
   if abs(x-31.5)<1.6:shade=6
   if y in (4,5,58,59):shade=4 if cartoon else 3
   if not cartoon and y in (13,14,46) and abs(x-31.5)>18:shade-=1
   for zz in range(max(0,z-1),z+1):put(x,y,zz,shade)
 # Front (-Y) canvas wall with an open triangular door; rear is closed.
 for x in range(4,60):
  for z in range(roof(x)+1):
   opening=z<=17 and abs(x-31.5)<(18-z)*.60
   if not opening:
    col=3 if cartoon else (3 if x<32 else 2)
    # Bound doorway by lighter folded fabric, classified as cloth.
    if z<=19 and abs(abs(x-31.5)-(18-z)*.60)<2:col=4
    for y in (4,5):put(x,y,z,col)
   for y in (58,59):put(x,y,z,4 if cartoon else 3)
 # Inferred fabric groundsheet: interior surface, not a solid filled volume.
 for x in range(5,59):
  for y in range(6,59):put(x,y,0,1)
 # Raised vent flaps along the outward edges; these do not fill the opening.
 for x in (14,49):
  for y in range(23,38):
   for dx in (-1,0,1):
    xx=x+dx
    if xx in range(15,20) or xx in range(44,49):continue
    for z in range(roof(xx),roof(xx)+3):put(xx,y,z,6 if cartoon or xx<32 else 4)
 # Long stitched ridge and simplified broad side folds.
 for y in range(5,59):
  for x in (31,32):put(x,y,29,6)
 for y in ([16,46] if cartoon else [15,44,47]):
  for x in list(range(5,12))+list(range(52,59)):
   put(x,y,roof(x)+1,4 if cartoon else (5 if x<32 else 3))
 # Short wooden corner stakes touch canvas at the low eaves.
 for x0 in (2,59):
  for y0 in (3,58):
   for x in range(x0,x0+3):
    for y in range(y0,y0+3):
     for z in range(7):put(x,y,z,8 if cartoon else (9 if z==6 else 7+(x+y)%2),'wood')
 # Interior ridge beam, rear upright, and small exposed end caps.
 for x in (31,32):
  for y in range(2,62):
   for z in (27,28):put(x,y,z,8,'wood')
  for y in (58,59):
   for z in range(32):put(x,y,z,8 if cartoon else 7+(z//5)%3,'wood')
  for y in (2,3):
   for z in (29,30,31):put(x,y,z,8,'wood')
 if cartoon:
  half={p:(v[p],g[p]) for p in v if p[0]<32};v={};g={}
  for (x,y,z),(col,group) in half.items():
   put(x,y,z,col,group);put(63-x,y,z,col,group)
 assert len(components(v))==1,components(v)
 assert all((x,y,1) not in v for x in range(25,39) for y in range(4,57))
 assert (31,30,10) not in v and (31,58,10) in v
 return v,g
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--replace-generated',action='store_true');args=parser.parse_args()
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 crate=json.loads((WORK/'knowledge/palettes/crate-palette.json').read_text());cp=[tuple(c) for c in crate['rgba']]
 pal=[(53,42,30,255),(182,139,102,255),(202,164,127,255),(219,190,150,255),(232,212,173,255),(244,228,192,255),(68,42,28,255),(111,66,38,255),(155,94,52,255)]
 pal+=[pal[0]]*(256-len(pal))
 reps=[pal[4],pal[7]]
 mapping={i:min(range(1,255),key=lambda j:sum((pal[i-1][a]-cp[j-1][a])**2 for a in range(3))) for i in range(1,10)}
 two=[mapping[5],mapping[8]];assert cp[two[0]-1]!=cp[two[1]-1]
 original,og=build(False);cartoon,cg=build(True)
 old=json.loads((HERE/'manifest.json').read_text()) if (HERE/'manifest.json').exists() else {'models':[]}
 hashes={r['file']:r['sha256'] for r in old['models']};rows=[]
 for style in STYLES:
  src,groups=(cartoon,cg) if 'Cartoon' in style else (original,og);v=dict(src);p=pal
  if 'TwoColor' in style:
   ids=two if 'CratePalette' in style else [1,2]
   v={q:ids[0] if groups[q]=='canvas' else ids[1] for q in src};p=cp if 'CratePalette' in style else reps+[reps[0]]*254
  elif 'CratePalette' in style:v={q:mapping[c] for q,c in src.items()};p=cp
  name='PixelwoodA_Tent'+('' if style=='Base' else '_'+style)+'.vox';dest=ROOT/name
  if dest.exists() and not args.replace_generated:assert sha(dest)==hashes.get(name),'Preserve edited file: '+name
  write(dest,SIZE,v,p);size,saved,sp=read(dest)
  assert saved==v and size==SIZE and saved.keys()==src.keys() and len(components(saved))==1
  assert 255 not in saved.values()
  if 'Cartoon' in style:assert all(saved.get((63-x,y,z))==c for (x,y,z),c in saved.items())
  if 'TwoColor' in style:assert len(set(saved.values()))==len({sp[c-1] for c in saved.values()})==2
  ph=hashlib.sha256(b''.join(bytes(c) for c in sp)).hexdigest()
  if 'CratePalette' in style:assert ph==crate['palette_sha256']
  rows.append({'file':name,'family':'PixelwoodA_Tent','style':style,'canvas':SIZE,'occupied_min':[min(q[a] for q in saved) for a in range(3)],'occupied_max':[max(q[a] for q in saved) for a in range(3)],'voxels':len(saved),'sha256':sha(dest),'palette_sha256':ph,'used_indices':sorted(set(saved.values())),'used_rgba':[sp[c-1] for c in sorted(set(saved.values()))],'geometry_source':'PixelwoodA_Tent'+('_Cartoon' if 'Cartoon' in style else '')+'.vox'})
 byname={r['file']:r for r in rows}
 for r in rows:r['geometry_source_sha256']=byname[r['geometry_source']]['sha256']
 fam={'asset_id':'PixelwoodA_Tent','canvas_xyz':SIZE,'source_region_xyxy_exclusive':[210,180,395,390],'symmetry':'Cartoon: bilateral X reflection x -> 63-x, geometry and paint; front and rear intentionally distinct.','semantic_groups':{'canvas':'All fabric panels, hems, ridge seam and vent flaps; source indices 1-6.','wood':'Stakes, rear upright, internal ridge beam and end caps; source indices 7-9.'},'two_color_rgba':reps,'two_color_crate_indices':two,'crate_mapping':mapping}
 manifest={'source_image':'pixelwood_a.jpg','source_sha256':sha(WORK/'pixelwood_a.jpg'),'generator_sha256':sha(Path(__file__)),'dependencies':{'../voxlib.py':sha(ROOT/'voxlib.py')},'families':[fam],'models':rows,'scale':.0625,'front':'local -Y / Godot +Z','scene_translation':'0 0 16','palette_sha256':crate['palette_sha256'],'delivery':'Complete hollow models; no cell files.','command':'python output/pixelwood_a/tent/generate.py'}
 (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('Generated and serialized-checked seven tent models.')
if __name__=='__main__':main()
