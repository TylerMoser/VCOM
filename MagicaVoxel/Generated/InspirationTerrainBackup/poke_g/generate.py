"""Deterministic poke_g tree families. Run from any directory.
Writes only the 21 named outputs and manifest.json. Refuses changed existing VOX
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
 'dark':[(49,66,39),(64,82,46),(78,101,55),(98,124,63),(123,147,75),(164,180,94)],
 'bright':[(54,73,40),(71,92,46),(91,116,54),(119,146,65),(151,174,81),(187,199,110)],
 'sapling':[(45,65,34),(61,82,40),(78,103,46),(102,127,56),(130,152,70),(166,182,95)]}
FAMILIES=[('BroadCrown','broad',32,40,'dark',None),('TieredCrown','tiered',32,36,'bright',None),('Sapling','sapling',12,28,'sapling',None)]

from sculpt import build

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--replace-generated',action='store_true');args=parser.parse_args()
 crate=json.loads((WORK/'knowledge/palettes/crate-palette.json').read_text());cp=[tuple(c) for c in crate['rgba']]
 regions=json.loads((ROOT/'reference/regions.json').read_text())
 records=[];families=[]
 old=json.loads((ROOT/'manifest.json').read_text()) if (ROOT/'manifest.json').exists() else {'models':[]}
 hashes={r['file']:r['sha256'] for r in old['models']}
 for fi,(label,kind,n,h,scheme,decor) in enumerate(FAMILIES):
  base='PokeG_'+label;palette=[(*rgb,255) for rgb in GREENS[scheme]]+[(57,47,29,255),(86,72,43,255),(118,102,64,255)]
  wood_allowed=(178,179,180)
  palette+=([(134,75,196,255),(207,163,241,255)] if decor=='flower' else [(231,87,39,255),(255,170,61,255)])
  palette+=[palette[0]]*(256-len(palette))
  original,og=build(kind,n,h,False,decor);cartoon,cg=build(kind,n,h,True,decor)
  representative=[palette[3],palette[7]]
  # Warm crowns use the entire established warm range rather than being forced green.
  allowed=range(241,247) if scheme not in ('gold','orange','red') else range(217,239)
  mapping={i:min(allowed if i<=6 else (wood_allowed if i<=9 else range(1,255)),key=lambda j:sum((palette[i-1][a]-cp[j-1][a])**2 for a in range(3))) for i in range(1,12)}
  two_game=[min(allowed,key=lambda j:sum((representative[0][a]-cp[j-1][a])**2 for a in range(3))),min(wood_allowed,key=lambda j:sum((representative[1][a]-cp[j-1][a])**2 for a in range(3)))]
  assert cp[two_game[0]-1]!=cp[two_game[1]-1]
  family={'asset_id':base,'source_image':'poke_g.png','source_region_xyxy_exclusive':regions[fi][1],'shape':kind,'appearance':scheme,'decoration':decor,'canvas_xyz':[n,n,h],'approximate_tiles_xyz':[n/16,n/16,h/16],'symmetry':'Cartoon: exact quarter turn and paint around Z, center ((width-1)/2,(depth-1)/2). Base: intentional natural asymmetry.','semantic_groups':{'foliage':'All canopy leaves, including hidden foliage. No fruit or flower ornaments in this image.','wood':'Trunk, roots, hidden core, branches.'},'group_assignment':'Explicit per-coordinate dictionaries returned by sculpt.build(); indices 1-6 foliage, 7-9 wood.','two_color_rgba':representative,'two_color_crate_indices':two_game,'crate_mapping':mapping,'models':[]}
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
 manifest={'source_image':'poke_g.png','source_sha256':hashlib.sha256((WORK/'poke_g.png').read_bytes()).hexdigest(),'specification_version':'1.0','generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'sculpt_sha256':hashlib.sha256((ROOT/'sculpt.py').read_bytes()).hexdigest(),'command':'python output/poke_g/generate.py','seed':'fixed deterministic integer hash, no random state','scale':.0625,'scene_translation':'0 0 floor(canvas height/2)','delivery':'Complete models only, no per-cell files','palette_snapshot':'knowledge/palettes/crate-palette.json','palette_sha256':crate['palette_sha256'],'families':families,'models':records}
 (ROOT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
 print('Generated and validated',len(records),'complete VOX files in',len(families),'families.')
if __name__=='__main__':main()
