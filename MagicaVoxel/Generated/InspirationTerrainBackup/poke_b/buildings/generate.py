"""Six poke_b buildings, seven treatments each. Does not own tree files."""
from pathlib import Path
import json,hashlib,argparse
from voxlib import write,read,components
from sculpt import build
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent;WORK=ROOT.parent.parent
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
def palette(kind):
 body=[(69,56,43),(113,89,64),(158,125,88),(194,167,129),(220,202,174),(241,232,213)]
 roof=[(92,51,39),(139,65,45),(176,78,51),(205,101,68),(226,130,92),(241,160,117)]
 if kind=='DomeLab':roof=[(134,65,56),(177,87,73),(206,107,87),(225,128,106),(239,148,128),(249,170,151)]
 if kind=='RedClinic':
  body=[(40,69,57),(65,98,80),(96,132,111),(139,170,145),(194,205,176),(231,233,204)]
  roof=[(115,50,30),(162,64,33),(199,77,39),(219,107,75),(228,118,86),(241,146,110)]
 if kind in ('GrayEntryHouse','GrayWindowHouse'):roof=[(65,66,63),(103,105,100),(132,134,129),(155,156,148),(181,182,175),(207,209,201)]
 if kind=='CyanEntryHouse':roof=[(45,91,96),(66,123,130),(85,148,155),(111,177,183),(144,201,204),(179,223,222)]
 extra=[(100,127,144),(94,159,201),(167,212,236),(234,185,63),(36,45,46),(67,133,48),(232,105,132)]
 p=[(*c,255) for c in body+roof+extra];return p+[p[0]]*(256-len(p))
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--replace-generated',action='store_true');args=parser.parse_args();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
 crate=json.loads((WORK/'knowledge/palettes/crate-palette.json').read_text());cp=[tuple(c) for c in crate['rgba']]
 regions=json.loads((HERE/'reference/regions.json').read_text())
 old=json.loads((HERE/'manifest.json').read_text()) if (HERE/'manifest.json').exists() else {'models':[]}
 hashes={r['file']:r['sha256'] for r in old['models']};rows=[];families=[]
 for kind,region,size in regions:
  name='PokeB_'+kind;pal=palette(kind);reps=[pal[4],pal[9]]
  mapping={i:min(range(1,255),key=lambda j:sum((pal[i-1][a]-cp[j-1][a])**2 for a in range(3))) for i in range(1,20)}
  two=[mapping[5],mapping[10]];assert cp[two[0]-1]!=cp[two[1]-1]
  original,og=build(kind,size,False);cartoon,cg=build(kind,size,True)
  for style in STYLES:
   src,groups=(cartoon,cg) if 'Cartoon' in style else (original,og);v=dict(src);p=pal
   if 'TwoColor' in style:
    ids=two if 'CratePalette' in style else [1,2];v={q:ids[0] if groups[q]=='body' else ids[1] for q in src};p=cp if 'CratePalette' in style else reps+[reps[0]]*254
   elif 'CratePalette' in style:v={q:mapping[c] for q,c in src.items()};p=cp
   filename=name+('' if style=='Base' else '_'+style)+'.vox';dest=ROOT/filename
   if dest.exists() and not args.replace_generated:assert sha(dest)==hashes.get(filename),'Preserve edited file: '+filename
   write(dest,size,v,p);ss,saved,sp=read(dest)
   assert saved==v and tuple(size)==ss and saved.keys()==src.keys() and len(components(saved))==1
   assert 255 not in saved.values()
   if 'TwoColor' in style:assert len(set(saved.values()))==len({sp[c-1] for c in saved.values()})==2
   ph=hashlib.sha256(b''.join(bytes(c) for c in sp)).hexdigest()
   if 'CratePalette' in style:assert ph==crate['palette_sha256']
   rows.append({'file':filename,'family':name,'style':style,'canvas':size,'occupied_min':[min(q[a] for q in saved) for a in range(3)],'occupied_max':[max(q[a] for q in saved) for a in range(3)],'voxels':len(saved),'sha256':sha(dest),'palette_sha256':ph,'used_indices':sorted(set(saved.values())),'used_rgba':[sp[c-1] for c in sorted(set(saved.values()))],'geometry_source':name+('_Cartoon' if 'Cartoon' in style else '')+'.vox'})
  families.append({'asset_id':name,'kind':kind,'canvas_xyz':size,'source_region_xyxy_exclusive':region,'symmetry':'Cartoon regularizes repeated architectural details and paint; retain source-specific asymmetric doors, roof fixtures, signs and annex. No full-model rotational symmetry claim.','semantic_groups':{'body':'Primary structure, columns, floors, trim, cream dome; indices 1-6.','accent':'Roof, glazing, secondary fixtures, colored signs and plants; indices 7-19.'},'two_color_rgba':reps,'two_color_crate_indices':two,'crate_mapping':mapping})
 byname={r['file']:r for r in rows}
 for r in rows:r['geometry_source_sha256']=byname[r['geometry_source']]['sha256']
 manifest={'source_image':'poke_b.png','source_sha256':sha(WORK/'poke_b.png'),'generator_sha256':sha(Path(__file__)),'dependencies':{f:sha(HERE/f) for f in ['sculpt.py','voxlib.py','reference/regions.json']},'families':families,'models':rows,'scale':.0625,'front':'local -Y / Godot +Z','scene_translation':'0 0 floor(canvas height/2)','palette_sha256':crate['palette_sha256'],'delivery':'Complete buildings only, no cell files.','command':'python output/poke_b/buildings/generate.py'}
 (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Generated and checked',len(rows),'building files.')
if __name__=='__main__':main()
