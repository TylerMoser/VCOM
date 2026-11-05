"""Deterministic poke_q tree families. Run from any directory.
Writes only the 70 named outputs and manifest.json. Refuses changed existing VOX
unless --replace-generated is passed; use that flag only for deliberate revisions.
One sprite pixel approximates one voxel; inferred crown depth equals crown width.
"""
from pathlib import Path
import math, json, hashlib, argparse
from voxlib import write, read, components
ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent.parent
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
# Six foliage shades, three bark shades, then decoration shades.
GREENS={
 'jungle':[(25,63,26),(32,84,31),(43,108,37),(58,134,43),(82,158,53),(115,183,71)],
 'olive':[(40,67,31),(52,88,38),(69,110,45),(88,135,54),(114,159,68),(146,184,87)],
 'lime':[(33,65,22),(46,89,28),(63,116,34),(85,145,42),(117,176,58),(159,203,82)],
 'palm':[(22,64,24),(29,88,31),(41,116,38),(60,143,44),(88,172,54),(127,197,76)]}
FAMILIES=[('VineCanopyTree','banyan',80,112,'jungle',None),('ClusterCrownTree','cluster',48,64,'olive',None),('RingCrownTree','ring',48,40,'jungle',None),('FlatTierTree','flat',48,48,'jungle',None),('LeafyConifer','leafconifer',56,72,'lime',None),('PointedTree','pointed',32,48,'jungle',None),('PearSapling','pear',16,32,'olive',None),('ConicalSapling','smallcone',16,28,'jungle',None),('BeachPalm','palm',64,72,'palm',None),('PalmSeedling','seedling',32,32,'palm',None)]


from sculpt import build

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--replace-generated',action='store_true');args=parser.parse_args()
 crate=json.loads((WORK/'knowledge/palettes/crate-palette.json').read_text());cp=[tuple(c) for c in crate['rgba']]
 regions=json.loads((ROOT/'reference/regions.json').read_text())
 records=[];families=[]
 old=json.loads((ROOT/'manifest.json').read_text()) if (ROOT/'manifest.json').exists() else {'models':[]}
 hashes={r['file']:r['sha256'] for r in old['models']}
 for fi,(label,kind,n,h,scheme,decor) in enumerate(FAMILIES):
  base='PokeQ_'+label;palette=[(*rgb,255) for rgb in GREENS[scheme]]+[(72,46,24,255),(109,74,36,255),(148,107,55,255)]
  palette+=([(134,75,196,255),(207,163,241,255)] if decor=='flower' else [(231,87,39,255),(255,170,61,255)])
  if decor=='bud':palette[9:11]=[(196,221,181,255),(236,247,211,255)]
  palette+=[palette[0]]*(256-len(palette))
  original,og=build(kind,n,h,False,decor);cartoon,cg=build(kind,n,h,True,decor)
  representative=[palette[3],palette[7]]
  # Warm crowns use the entire established warm range rather than being forced green.
  allowed=range(241,247) if scheme not in ('gold','orange','red') else range(217,239)
  mapping={i:min(allowed if i<=6 else ((178,179,180) if i<=9 else range(1,255)),key=lambda j:sum((palette[i-1][a]-cp[j-1][a])**2 for a in range(3))) for i in range(1,12)}
  two_game=[min(allowed,key=lambda j:sum((representative[0][a]-cp[j-1][a])**2 for a in range(3))),min((178,179,180),key=lambda j:sum((representative[1][a]-cp[j-1][a])**2 for a in range(3)))]
  assert cp[two_game[0]-1]!=cp[two_game[1]-1]
  family={'asset_id':base,'source_image':'poke_q.png','source_region_xyxy_exclusive':regions[fi][1],'shape':kind,'appearance':scheme,'decoration':decor,'canvas_xyz':[n,n,h],'approximate_tiles_xyz':[n/16,n/16,h/16],'symmetry':'Cartoon: exact quarter turn and paint around Z, center ((width-1)/2,(depth-1)/2). Base: intentional natural asymmetry.','semantic_groups':{'foliage':'All leaves, fronds, hanging leafy vines and hidden foliage core.','wood':'Trunk, roots, hidden core, branches.'},'group_assignment':'Explicit per-coordinate dictionaries returned by sculpt.build(); original indices 1-6 and 10-11 foliage, 7-9 wood.','two_color_rgba':representative,'two_color_crate_indices':two_game,'crate_mapping':mapping,'models':[]}
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
 manifest={'source_image':'poke_q.png','source_sha256':hashlib.sha256((WORK/'poke_q.png').read_bytes()).hexdigest(),'specification_version':'1.0','generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'sculpt_sha256':hashlib.sha256((ROOT/'sculpt.py').read_bytes()).hexdigest(),'geometry_dependencies':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['profiles.py','leaves.py','palm.py']},'command':'python output/poke_q/generate.py','seed':'fixed deterministic integer hash, no random state','scale':.0625,'scene_translation':'0 0 floor(canvas height/2)','delivery':'Complete models only, no per-cell files','palette_snapshot':'knowledge/palettes/crate-palette.json','palette_sha256':crate['palette_sha256'],'families':families,'models':records}
 (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 print('Generated and validated',len(records),'complete VOX files in',len(families),'families.')
if __name__=='__main__':main()
