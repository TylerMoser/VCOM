"""Deterministic poke_s tree families. Run from any directory.
Writes only the 147 named outputs and manifest.json. Refuses changed existing VOX
unless --replace-generated is passed; use that flag only for deliberate revisions.
Resized reference: roughly 10 image pixels per tile; 16 voxels per tile. Depth inferred.
"""
from pathlib import Path
import math, json, hashlib, argparse
from voxlib import write, read, components
ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent.parent
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
# Six foliage shades, three bark shades, then decoration shades.
GREENS={
 'mint':[(34,92,59),(49,119,73),(68,145,89),(95,170,108),(130,193,133),(169,213,163)],
 'teal':[(26,86,86),(36,112,111),(54,139,136),(77,165,159),(112,187,178),(154,208,198)],
 'pink':[(125,53,65),(158,72,84),(188,96,107),(216,123,134),(238,156,163),(252,193,197)],
 'gold':[(139,110,24),(170,138,30),(198,165,38),(223,190,51),(241,215,81),(252,233,127)],
 'green':[(32,84,44),(44,111,56),(64,139,71),(91,165,88),(124,188,112),(165,211,146)]}
FAMILIES=[]
for color in ['mint','teal','pink','gold']:FAMILIES.append(('Tiered'+color.title(),'tiered',32,48,color,None))
for color in ['mint','teal','pink']:FAMILIES.append(('Tall'+color.title(),'tall',48,80,color,None))
for color in ['teal','gold']:FAMILIES.append(('Cluster'+color.title(),'cluster',48,64,color,None))
FAMILIES.append(('FlatTierGreen','flat',48,48,'green',None))
for color in ['mint','teal','pink','gold']:FAMILIES.append(('Ornamental'+color.title(),'ornamental',32,64,color,None))
for color in ['mint','teal','pink','gold']:FAMILIES.append(('Sapling'+color.title(),'sapling',12,28,color,None))
for color in ['mint','teal','pink']:FAMILIES.append(('Shrub'+color.title(),'shrub',24,28,color,None))


from sculpt import build

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--replace-generated',action='store_true');args=parser.parse_args()
 crate=json.loads((WORK/'knowledge/palettes/crate-palette.json').read_text());cp=[tuple(c) for c in crate['rgba']]
 regions=json.loads((ROOT/'reference/regions.json').read_text())
 records=[];families=[]
 old=json.loads((ROOT/'manifest.json').read_text()) if (ROOT/'manifest.json').exists() else {'models':[]}
 hashes={r['file']:r['sha256'] for r in old['models']}
 for fi,(label,kind,n,h,scheme,decor) in enumerate(FAMILIES):
  base='PokeS_'+label;palette=[(*rgb,255) for rgb in GREENS[scheme]]+[(72,46,24,255),(109,74,36,255),(148,107,55,255)]
  if kind=='ornamental':palette[6:9]=[(160,164,139,255),(215,219,191,255),(245,245,222,255)]
  palette+=([(134,75,196,255),(207,163,241,255)] if decor=='flower' else [(231,87,39,255),(255,170,61,255)])
  if decor=='bud':palette[9:11]=[(196,221,181,255),(236,247,211,255)]
  palette+=[palette[0]]*(256-len(palette))
  original,og=build(kind,n,h,False,decor);cartoon,cg=build(kind,n,h,True,decor)
  representative=[palette[3],palette[7]]
  # Warm crowns use the entire established warm range rather than being forced green.
  allowed=range(241,247) if scheme in ('mint','green') else range(1,255)
  wood_allowed=range(193,197) if kind=='ornamental' else (178,179,180)
  mapping={i:min(allowed if i<=6 else (wood_allowed if i<=9 else range(1,255)),key=lambda j:sum((palette[i-1][a]-cp[j-1][a])**2 for a in range(3))) for i in range(1,12)}
  two_game=[min(allowed,key=lambda j:sum((representative[0][a]-cp[j-1][a])**2 for a in range(3))),min(wood_allowed,key=lambda j:sum((representative[1][a]-cp[j-1][a])**2 for a in range(3)))]
  if cp[two_game[0]-1]==cp[two_game[1]-1]:two_game[0]=min((j for j in allowed if cp[j-1]!=cp[two_game[1]-1]),key=lambda j:sum((representative[0][a]-cp[j-1][a])**2 for a in range(3)))
  assert cp[two_game[0]-1]!=cp[two_game[1]-1]
  family={'asset_id':base,'source_image':'poke_s.jpg','source_region_xyxy_exclusive':regions[fi][1],'shape':kind,'appearance':scheme,'decoration':decor,'canvas_xyz':[n,n,h],'approximate_tiles_xyz':[n/16,n/16,h/16],'symmetry':'Cartoon: exact quarter turn and paint around Z, center ((width-1)/2,(depth-1)/2). Base: intentional natural asymmetry.','semantic_groups':{'foliage':'All leaves, fronds, hanging leafy vines and hidden foliage core.','wood':'Trunk, roots, hidden core, branches.'},'group_assignment':'Explicit per-coordinate dictionaries returned by sculpt.build(); original indices 1-6 and 10-11 foliage, 7-9 wood.','two_color_rgba':representative,'two_color_crate_indices':two_game,'crate_mapping':mapping,'models':[]}
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
 manifest={'source_image':'poke_s.jpg','source_sha256':hashlib.sha256((WORK/'poke_s.jpg').read_bytes()).hexdigest(),'specification_version':'1.0','generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'sculpt_sha256':hashlib.sha256((ROOT/'sculpt.py').read_bytes()).hexdigest(),'geometry_dependencies':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['profiles.py','leaves.py','crowns.py','palm.py']},'command':'python output/poke_s/generate.py','seed':'fixed deterministic integer hash, no random state','scale':.0625,'scene_translation':'0 0 floor(canvas height/2)','delivery':'Complete models only, no per-cell files','palette_snapshot':'knowledge/palettes/crate-palette.json','palette_sha256':crate['palette_sha256'],'families':families,'models':records}
 (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 print('Generated and validated',len(records),'complete VOX files in',len(families),'families.')
if __name__=='__main__':main()
