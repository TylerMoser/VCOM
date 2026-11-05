"""Deterministic pixelwood_a tree families. Run from any directory.
Writes only the 28 named outputs and manifest.json. Refuses changed existing VOX
unless --replace-generated is passed; use that flag only for deliberate revisions.
Approximate source scale: one original art pixel per voxel; source enlargement approximately 3x; 16 voxels per tile.
"""
from pathlib import Path
import math, json, hashlib, argparse
from voxlib import write, read, components
ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent.parent
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
# Six foliage shades, three bark shades, then decoration shades.
GREENS={'lime': [(15, 34, 27), (29, 66, 39), (49, 92, 41), (76, 127, 47), (120, 164, 55), (166, 198, 87)], 'olive': [(14, 31, 25), (28, 57, 36), (44, 77, 38), (64, 96, 42), (83, 117, 47), (117, 143, 63)], 'pine': [(10, 29, 24), (25, 58, 32), (39, 82, 34), (61, 115, 39), (91, 145, 44), (135, 174, 64)], 'cut': [(112, 58, 33), (130, 69, 38), (149, 82, 44), (172, 104, 59), (191, 124, 76), (203, 143, 91)]}
FAMILIES=[('RoundLime', 'round', 48, 48, 'lime', None), ('RoundOlive', 'round', 48, 48, 'olive', None), ('SquareShrub', 'shrub', 16, 16, 'lime', None), ('Stump', 'stump', 20, 16, 'cut', None)]


from sculpt import build

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--replace-generated',action='store_true');args=parser.parse_args()
 crate=json.loads((WORK/'knowledge/palettes/crate-palette.json').read_text());cp=[tuple(c) for c in crate['rgba']]
 regions=json.loads((ROOT/'reference/regions.json').read_text())
 records=[];families=[]
 old=json.loads((ROOT/'manifest.json').read_text()) if (ROOT/'manifest.json').exists() else {'models':[]}
 hashes={r['file']:r['sha256'] for r in old['models']}
 for fi,(label,kind,n,h,scheme,decor) in enumerate(FAMILIES):
  base='PixelwoodA_'+label;palette=[(*rgb,255) for rgb in GREENS[scheme]]+[(72,46,24,255),(109,74,36,255),(148,107,55,255)]
  if kind=='birch':palette[6:9]=[(48,55,57,255),(158,166,161,255),(232,238,222,255)]
  palette+=([(134,75,196,255),(207,163,241,255)] if decor=='flower' else [(231,87,39,255),(255,170,61,255)])
  palette+=[palette[0]]*(256-len(palette))
  original,og=build(kind,n,h,False,decor);cartoon,cg=build(kind,n,h,True,decor)
  representative=[palette[3],palette[8] if kind=='birch' else palette[7]]
  # Golden foliage maps to existing warm palette entries; greens use the green ramp.
  allowed=range(178,184) if kind=='stump' else range(241,247)
  wood_allowed=(193,194,195,196,248) if kind=='birch' else (178,179,180)
  mapping={i:min(allowed if i<=6 else (wood_allowed if i<=9 else range(1,255)),key=lambda j:sum((palette[i-1][a]-cp[j-1][a])**2 for a in range(3))) for i in range(1,12)}
  two_game=[min(allowed,key=lambda j:sum((representative[0][a]-cp[j-1][a])**2 for a in range(3))),min(wood_allowed,key=lambda j:sum((representative[1][a]-cp[j-1][a])**2 for a in range(3)))]
  if cp[two_game[0]-1]==cp[two_game[1]-1]:two_game[0]=min([j for j in allowed if cp[j-1]!=cp[two_game[1]-1]],key=lambda j:sum((representative[0][a]-cp[j-1][a])**2 for a in range(3)))
  assert cp[two_game[0]-1]!=cp[two_game[1]-1]
  family={'asset_id':base,'source_image':'pixelwood_a.jpg','source_region_xyxy_exclusive':regions[fi][1],'shape':kind,'appearance':scheme,'decoration':decor,'canvas_xyz':[n,n,h],'approximate_tiles_xyz':[n/16,n/16,h/16],'symmetry':'Cartoon: exact quarter turn and paint around Z, center ((width-1)/2,(depth-1)/2). Base: intentional natural asymmetry.','semantic_groups':{'foliage':('Exposed cut end grain, including rings.' if kind=='stump' else 'All leaves and hidden crown core.'),'wood':('Outer bark, roots and internal wood.' if kind=='stump' else 'Trunk, roots, hidden stem and branches; pale bark included.')},'group_assignment':'Explicit per-coordinate dictionaries returned by sculpt.build(); original indices 1-6 and 10-11 foliage, 7-9 wood.','two_color_rgba':representative,'two_color_crate_indices':two_game,'crate_mapping':mapping,'models':[]}
  for style in STYLES:
   source,groups=(cartoon,cg) if 'Cartoon' in style else (original,og)
   vox=dict(source);pal=palette
   if 'TwoColor' in style:
    ids=two_game if 'CratePalette' in style else [1,2]
    vox={p:ids[0] if groups[p]=='foliage' else ids[1] for p in source}
    pal=cp if 'CratePalette' in style else representative+[representative[0]]*254
   elif 'CratePalette' in style:vox={p:mapping[c] for p,c in source.items()};pal=cp
   filename=base+('' if style=='Base' else '_'+style)+'.vox';dest=ROOT/filename
   if dest.exists() and not args.replace_generated:assert hashlib.sha256(dest.read_bytes()).hexdigest()==hashes.get(filename),'Existing untracked/edited file: '+filename
   write(dest,(n,n,h),vox,pal)
   size,saved,sp=read(dest)
   assert saved==vox and tuple(size)==(n,n,h)
   assert set(saved)==set(source) and len(components(saved))==1
   assert all(0<=p[a]<size[a] for p in saved for a in range(3))
   assert all(1<=i<=254 for i in saved.values())
   if 'Cartoon' in style:assert {(n-1-y,x,z):col for (x,y,z),col in saved.items()}==saved
   if 'TwoColor' in style:assert len(set(saved.values()))==len({sp[i-1] for i in saved.values()})==2
   phash=hashlib.sha256(b''.join(bytes(c) for c in sp)).hexdigest()
   if 'CratePalette' in style:assert phash==crate['palette_sha256']
   row={'file':filename,'family':base,'style':style,'canvas':size,'occupied_min':[min(p[a] for p in saved) for a in range(3)],'occupied_max':[max(p[a] for p in saved) for a in range(3)],'voxels':len(saved),'used_indices':sorted(set(saved.values())),'used_rgba':[sp[i-1] for i in sorted(set(saved.values()))],'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'palette_sha256':phash,'geometry_source':base+('_Cartoon' if 'Cartoon' in style else '')+'.vox','checks':{'serialization_round_trip':'pass','geometry_source_equality':'pass','connected':'pass','symmetry':'pass' if 'Cartoon' in style else 'not_applicable','two_colors':'pass' if 'TwoColor' in style else 'not_applicable','crate_palette':'pass' if 'CratePalette' in style else 'not_applicable','gameplay':'not_run'}}
   records.append(row);family['models'].append(filename)
  families.append(family)
 byname={r['file']:r for r in records}
 for r in records:r['geometry_source_sha256']=byname[r['geometry_source']]['sha256']
 manifest={'source_image':'pixelwood_a.jpg','source_sha256':hashlib.sha256((WORK/'pixelwood_a.jpg').read_bytes()).hexdigest(),'specification_version':'1.0','generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'sculpt_sha256':hashlib.sha256((ROOT/'sculpt.py').read_bytes()).hexdigest(),'command':'python output/pixelwood_a/generate.py','seed':'fixed deterministic integer hash, no random state','scale':.0625,'scene_translation':'0 0 floor(canvas height/2)','delivery':'Complete models only, no per-cell files','palette_snapshot':'knowledge/palettes/crate-palette.json','palette_sha256':crate['palette_sha256'],'families':families,'models':records}
 (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 print('Generated and validated',len(records),'complete VOX files in',len(families),'families.')
if __name__=='__main__':main()
