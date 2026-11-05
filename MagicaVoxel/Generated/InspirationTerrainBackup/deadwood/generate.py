"""Build seven complete VOX assets per source deadwood family; never split into cells."""
from pathlib import Path
import json,hashlib,math
from PIL import Image,ImageDraw
from sculpt import make
from voxlib import read,write,components
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
FAMILIES=json.loads((HERE/'catalogue.json').read_text())
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
CRATE=json.loads((ROOT/'knowledge/palettes/crate-palette.json').read_text())
def paint(f,m,style):
 flat='TwoColor' in style;crate='CratePalette' in style
 palette=[tuple(c) for c in CRATE['rgba']] if crate else [(0,0,0,255)]*256
 groups={};keys={};mapping={}
 for label in sorted(set(m.v.values())):
  group=label[:-1];delta=0 if flat else [-20,0,17][int(label[-1])]
  color=tuple(max(0,min(255,v+delta)) for v in f[group])+(255,);key=(group,color)
  if key not in keys:
   if crate:
    swatches=[179,180,234,235] if group=='bark' else [228,229,236,237]
    allowed=[i for i in swatches if str(i) not in groups or groups[str(i)]==group]
    idx=min(allowed,key=lambda i:sum((palette[i-1][k]-color[k])**2 for k in range(3)))
   else:idx=len(keys)+1;palette[idx-1]=color
   keys[key]=idx;groups[str(idx)]=group
  mapping[label]=keys[key]
 return {p:mapping[s] for p,s in m.v.items()},palette,groups

def main():
 manifest={'date':'2026-10-29','families':FAMILIES,'models':[],'reuse':{'pixelwood_a.jpg':['PixelwoodA_Stump (all seven existing styles)'],'pixelwood_b.gif':['pixelwood_a/PixelwoodA_Stump','pixelwood_a/PixelwoodA_FallenLog'],'pixelwood_c.jpg':['pixelwood_a/PixelwoodA_Stump']}}
 for f in FAMILIES:
  dest=ROOT/'output'/Path(f['source']).stem;support=dest/'deadwood';support.mkdir(parents=True,exist_ok=True)
  crop=Image.open(ROOT/f['source']).convert('RGB').crop(f['crop']);scale=min(8,600/crop.width,400/crop.height)
  crop.resize((int(crop.width*scale),int(crop.height*scale)),Image.Resampling.NEAREST).save(support/(f['name']+'_source.png'))
  models={False:make(f),True:make(f,True)}
  assert set(models[False].v)!=set(models[True].v),f['name']
  for m in models.values():assert len(components(m.v))==1,(f['name'],components(m.v))
  for style in STYLES:
   m=models['Cartoon' in style];v,pal,groups=paint(f,m,style)
   path=dest/(f['name']+('' if style=='Base' else '_'+style)+'.vox')
   # Existing outputs may only be rewritten by this generator if unchanged since its last run.
   if path.exists():
    previous=json.loads((HERE/'manifest.json').read_text())
    old=next(r for r in previous['models'] if r['file']==path.relative_to(ROOT).as_posix())
    assert hashlib.sha256(path.read_bytes()).hexdigest()==old['sha256'],'Hand edit: '+str(path)
   write(path,m.size,v,pal);assert read(path)==(m.size,v,pal)
   row={'file':path.relative_to(ROOT).as_posix(),'family':f['name'],'style':style,'canvas':m.size,'voxels':len(v),'colors':len(set(v.values())),'groups':groups,'components':components(v),'occupied_min':[min(p[k] for p in v) for k in range(3)],'occupied_max':[max(p[k] for p in v) for k in range(3)],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'palette_sha256':hashlib.sha256(b''.join(bytes(c) for c in pal)).hexdigest(),'material':'opaque diffuse'}
   if 'CratePalette' in style:assert row['palette_sha256']==CRATE['palette_sha256']
   if 'TwoColor' in style:assert row['colors']==2
   manifest['models'].append(row)
  print(f['name'])
 (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2))
 for source in json.loads((HERE/'source-inventory.json').read_text()):
  src=source['source'];support=ROOT/'output'/Path(src).stem/'deadwood';support.mkdir(parents=True,exist_ok=True)
  (support/'manifest.json').write_text(json.dumps({'source':source,'families':[f for f in FAMILIES if f['source']==src],'models':[r for r in manifest['models'] if r['file'].split('/')[1]==Path(src).stem],'reuse':manifest['reuse'].get(src,[])},indent=2))
 print('GENERATED',len(manifest['models']))
if __name__=='__main__':main()
