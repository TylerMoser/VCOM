"""Deterministic house authoring; owns seven PixelwoodB_House*.vox files only."""
from pathlib import Path
import sys,math,json,hashlib,argparse
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
WORK=ROOT.parent.parent
sys.path.append(str(ROOT))
from voxlib import write,read,components
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
SIZE=(80,80,80)
from sculpt import build
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--replace-generated',action='store_true');args=parser.parse_args()
 sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 crate=json.loads((WORK/'knowledge/palettes/crate-palette.json').read_text());cp=[tuple(c) for c in crate['rgba']]
 pal=[(57,28,25,255),(96,46,35,255),(129,65,40,255),(161,85,48,255),(186,112,69,255),(205,137,86,255),(10,32,28,255),(24,62,40,255),(37,82,43,255),(54,107,46,255),(77,133,52,255),(107,157,66,255),(38,42,50,255),(77,82,94,255),(115,122,134,255),(150,157,164,255),(17,17,14,255)]
 pal+=[pal[0]]*(256-len(pal))
 reps=[pal[3],pal[9]]
 mapping={i:min(range(1,255),key=lambda j:sum((pal[i-1][a]-cp[j-1][a])**2 for a in range(3))) for i in range(1,18)}
 two=[mapping[4],mapping[10]];assert cp[two[0]-1]!=cp[two[1]-1]
 original,og=build(False);cartoon,cg=build(True)
 old=json.loads((HERE/'manifest.json').read_text()) if (HERE/'manifest.json').exists() else {'models':[]}
 hashes={r['file']:r['sha256'] for r in old['models']};rows=[]
 for style in STYLES:
  src,groups=(cartoon,cg) if 'Cartoon' in style else (original,og);v=dict(src);p=pal
  if 'TwoColor' in style:
   ids=two if 'CratePalette' in style else [1,2]
   v={q:ids[0] if groups[q]=='wood' else ids[1] for q in src};p=cp if 'CratePalette' in style else reps+[reps[0]]*254
  elif 'CratePalette' in style:v={q:mapping[c] for q,c in src.items()};p=cp
  name='PixelwoodB_House'+('' if style=='Base' else '_'+style)+'.vox';dest=ROOT/name
  if dest.exists() and not args.replace_generated:assert sha(dest)==hashes.get(name),'Preserve edited file: '+name
  write(dest,SIZE,v,p);size,saved,sp=read(dest)
  assert saved==v and size==SIZE and saved.keys()==src.keys() and len(components(saved))==1
  assert 255 not in saved.values()
  if 'Cartoon' in style:assert all(saved.get((79-x,y,z))==c for (x,y,z),c in saved.items() if 7<=c<=12 and y<40) if 'CratePalette' not in style and 'TwoColor' not in style else True
  if 'TwoColor' in style:assert len(set(saved.values()))==len({sp[c-1] for c in saved.values()})==2
  ph=hashlib.sha256(b''.join(bytes(c) for c in sp)).hexdigest()
  if 'CratePalette' in style:assert ph==crate['palette_sha256']
  rows.append({'file':name,'family':'PixelwoodB_House','style':style,'canvas':SIZE,'occupied_min':[min(q[a] for q in saved) for a in range(3)],'occupied_max':[max(q[a] for q in saved) for a in range(3)],'voxels':len(saved),'sha256':sha(dest),'palette_sha256':ph,'used_indices':sorted(set(saved.values())),'used_rgba':[sp[c-1] for c in sorted(set(saved.values()))],'geometry_source':'PixelwoodB_House'+('_Cartoon' if 'Cartoon' in style else '')+'.vox'})
 byname={r['file']:r for r in rows}
 for r in rows:r['geometry_source_sha256']=byname[r['geometry_source']]['sha256']
 fam={'asset_id':'PixelwoodB_House','canvas_xyz':SIZE,'source_region_xyxy_exclusive':[404,300,830,800],'symmetry':'Cartoon: balanced roof and structural shell; intentional exceptions: left chimney, left front door, right front window and their trim. No full-model reflection claim.','semantic_groups':{'wood':'Timber structure, door, window frames, floor and steps; indices 1-6.','accent':'Roof, chimney masonry and recessed opaque dark glazing; indices 7-17.'},'two_color_rgba':reps,'two_color_crate_indices':two,'crate_mapping':mapping}
 manifest={'source_image':'pixelwood_b.gif','source_sha256':sha(WORK/'pixelwood_b.gif'),'generator_sha256':sha(Path(__file__)),'dependencies':{'../voxlib.py':sha(ROOT/'voxlib.py'),'sculpt.py':sha(HERE/'sculpt.py')},'families':[fam],'models':rows,'scale':.0625,'front':'local -Y / Godot +Z','scene_translation':'0 0 40','palette_sha256':crate['palette_sha256'],'delivery':'Complete hollow models; no cell files.','command':'python output/pixelwood_b/house/generate.py'}
 (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print('Generated and serialized-checked seven house models.')
if __name__=='__main__':main()
