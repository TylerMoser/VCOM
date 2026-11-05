"""Create complete source-relative rock families. Never writes to VoxelXCOM."""
from pathlib import Path
import json,hashlib,struct
from PIL import Image,ImageDraw
from catalogue import FAMILIES,COLORS,EXCLUSIONS
from sculpt import make
from voxlib import read,write,components
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
CRATE=json.loads((ROOT/'knowledge/palettes/crate-palette.json').read_text())
def shade(rgb,delta):return tuple(max(0,min(255,v+delta)) for v in rgb)+(255,)
def label_group(label):return 'stone' if label.startswith(('stone','dry')) else label.rstrip('0123456789')
def paint(f,m,style):
 flat='TwoColor' in style;crate='CratePalette' in style
 base=COLORS[f['color']];rgb={'stone':base,'dry':(163,130,116),'moss':(100,145,66),'crystal':(206,71,80)}
 palette=[tuple(c) for c in CRATE['rgba']] if crate else [base+(255,)]*256
 keys={};mapping={};groups={}
 for label in sorted(set(m.v.values())):
  group=label_group(label);family=label.rstrip('0123456789');value=base if flat and group=='stone' else rgb[family]
  color=shade(value,0 if flat else [-28,-10,10,29][int(label[-1])])
  key=(group,color)
  if key not in keys:
   if crate:
    allowed=[185,186,187,193,194,195,196,201,202,203,204,205,206]
    if f['color'] in ('brown','sand','tan') and group=='stone':allowed=[185,225,226,227,228,229,230,233,234,235,236,237,238]
    if f['color']=='purple' and group=='stone':allowed=[185,193,194,209,210,211]
    if group=='moss':allowed=list(range(241,247))
    if group=='crystal':allowed=[218,219,220,221,222]
    allowed=[i for i in allowed if str(i) not in groups or groups[str(i)]==group]
    idx=min(allowed,key=lambda i:sum((palette[i-1][k]-color[k])**2 for k in range(3)))
   else:idx=len(keys)+1;palette[idx-1]=color
   keys[key]=idx;groups[str(idx)]=group
  mapping[label]=keys[key]
 return {p:mapping[label] for p,label in m.v.items()},palette,groups
def main():
 manifest={'date':'2026-10-28','scope':'Discrete rock props, not continuous cliff terrain or buildings.','families':FAMILIES,'models':[]}
 for f in FAMILIES:
  stem=Path(f['source']).stem;dest=ROOT/'output'/stem;support=dest/'rocks';support.mkdir(parents=True,exist_ok=True)
  crop=Image.open(ROOT/f['source']).convert('RGB').crop(f['crop']);scale=min(6,360/crop.width,360/crop.height)
  crop.resize((int(crop.width*scale),int(crop.height*scale)),Image.Resampling.NEAREST).save(support/(f['name']+'_source.png'))
  models={False:make(f),True:make(f,True)}
  for cartoon,model in models.items():
   c=components(model.v)
   assert c==[len(model.v)],(f['name'],cartoon,c)
  assert set(models[False].v)!=set(models[True].v),(f['name'],'Cartoon needs distinct geometry')
  for style in STYLES:
   m=models['Cartoon' in style];v,pal,groups=paint(f,m,style)
   filename=f['name']+('' if style=='Base' else '_'+style)+'.vox';path=dest/filename
   write(path,m.size,v,pal);assert read(path)==(m.size,v,pal)
   row={'file':path.relative_to(ROOT).as_posix(),'family':f['name'],'style':style,'canvas':m.size,'voxels':len(v),'colors':len(set(v.values())),
    'groups':groups,'occupied_min':[min(p[k] for p in v) for k in range(3)],'occupied_max':[max(p[k] for p in v) for k in range(3)],
    'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'palette_sha256':hashlib.sha256(b''.join(bytes(c) for c in pal)).hexdigest(),
    'material':'opaque diffuse','symmetry':'bilateral X' if f['shape'] in ('geode','stack','crystals') else 'bilateral X and Y'}
   assert row['occupied_min'][2]==0 and 255 not in v.values()
   if 'CratePalette' in style:assert row['palette_sha256']==CRATE['palette_sha256']
   if 'TwoColor' in style:
    for group in set(groups.values()):assert len({i for i in v.values() if groups[str(i)]==group})==1
   manifest['models'].append(row)
  print(f['name'],len(models[False].v),'voxels')
 for source in sorted(set(f['source'] for f in FAMILIES)):
  dest=ROOT/'output'/Path(source).stem/'rocks'
  (dest/'manifest.json').write_text(json.dumps({'source':source,'families':[f for f in FAMILIES if f['source']==source],'models':[r for r in manifest['models'] if r['file'].split('/')[1]==Path(source).stem]},indent=2))
 coverage=json.loads((HERE/'source-inventory.json').read_text())
 for s in coverage:
  s['families']=[f['name'] for f in FAMILIES if f['source']==s['source']]
  assert s['families'] or s['source'] in EXCLUSIONS,s
  s['assessment']=EXCLUSIONS.get(s['source'],'Discrete rocks modeled; repeated placements within image represented once. Buildings, continuous cliff walls, water foam, loose items, creatures and shells are excluded.')
 (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2));(HERE/'catalogue.json').write_text(json.dumps({'sources':coverage,'families':FAMILIES},indent=2))
 for page in range((len(FAMILIES)+14)//15):
  sheet=Image.new('RGB',(1200,750),'#dedfd7');d=ImageDraw.Draw(sheet)
  for i,f in enumerate(FAMILIES[page*15:page*15+15]):
   im=Image.open(ROOT/f['source']).crop(f['crop']).convert('RGB');s=min(230/im.width,200/im.height);im=im.resize((int(im.width*s),int(im.height*s)),Image.Resampling.NEAREST)
   x=i%5*240;y=i//5*250;sheet.paste(im,(x,y+40));d.text((x+4,y+4),str(page*15+i)+' '+f['name'],fill='black')
  sheet.save(HERE/'reference'/f'catalogue_{page+1}.png')
 print('GENERATED',len(manifest['models']),'models')
if __name__=='__main__':main()
