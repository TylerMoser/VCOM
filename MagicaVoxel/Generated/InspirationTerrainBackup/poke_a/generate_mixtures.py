"""Create three two-color mixtures for each complete tree; preserve all existing files."""
from pathlib import Path
import json,hashlib
from generate_variations import read,write,BASES,components
ROOT=Path(__file__).resolve().parent
STYLES=['Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
def main():
 existing={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.vox') if not any(p.stem.endswith('_'+s) for s in STYLES)}
 crate=json.loads((ROOT/'crate-palette.json').read_text(encoding='utf-8'))
 crate_palette=[tuple(c) for c in crate['rgba']]
 green=(61,123,75,255);brown=(116,80,45,255)
 green_index=min(range(241,247),key=lambda i:sum((green[a]-crate_palette[i-1][a])**2 for a in range(3)))
 brown_index=min((178,179,180),key=lambda i:sum((brown[a]-crate_palette[i-1][a])**2 for a in range(3)))
 records=[]
 for base in BASES:
  for style in STYLES:
   is_cartoon='Cartoon' in style;is_crate='CratePalette' in style
   source=ROOT/(base+('_Cartoon' if is_cartoon else '')+'.vox')
   size,vox,_=read(source)
   gi,bi=(green_index,brown_index) if is_crate else (1,2)
   palette=crate_palette if is_crate else [green,brown]+[green]*254
   mixed={p:gi if c<=10 else bi for p,c in vox.items()}
   assert set(mixed.values())=={gi,bi}
   assert len({palette[c-1] for c in mixed.values()})==2
   assert mixed.keys()==vox.keys() and len(components(mixed))==1
   if is_cartoon:assert {(size[0]-1-y,x,z):c for (x,y,z),c in mixed.items()}==mixed
   path=ROOT/(base+'_'+style+'.vox');write(path,size,mixed,palette)
   records.append(dict(file=path.name,source_geometry=source.name,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),style=style,canvas=size,voxels=len(mixed),green_index=gi,brown_index=bi,green_rgba=palette[gi-1],brown_rgba=palette[bi-1],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),palette_sha256=hashlib.sha256(b''.join(bytes(c) for c in palette)).hexdigest(),checks={'exactly_two_used_colors':True,'source_geometry_preserved':True,'single_connected_component':True,'quarter_turn_symmetry':is_cartoon,'crate_palette':is_crate}))
 for name,sha in existing.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha
 (ROOT/'mixtures-manifest.json').write_text(json.dumps({'models':records,'preserved_existing_sha256':existing,'crate_palette_sha256':crate['palette_sha256']},indent=2)+'\n',encoding='utf-8')
 for r in records:print(r['file'],r['voxels'],r['green_index'],r['brown_index'])
if __name__=='__main__':main()
