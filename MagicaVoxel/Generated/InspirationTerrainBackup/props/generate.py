"""Build seven complete VOX assets per source props family; never split into cells."""
from pathlib import Path
import json,hashlib,math
from PIL import Image,ImageDraw
from sculpt import make
from voxlib import read,write,components
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
FAMILIES=json.loads((HERE/'catalogue.json').read_text())
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
CRATE=json.loads((ROOT/'knowledge/palettes/crate-palette.json').read_text())
TONES={'white':(215,221,210),'gold':(231,169,46),'brown':(116,72,43),'wood':(158,133,83),'blue':(74,126,161),'red':(181,65,57),'slate':(99,117,119),'gray':(166,151,143),'straw':(172,154,49),'olive':(147,128,85),'orange':(224,135,91),'sand':(219,201,147),'green':(93,157,112)}
def colors(f):
 tone=TONES[f['tone']]
 c={'body':tone,'frame':(143,116,74),'face':tone,'ink':(61,66,61),'mark':(240,239,211),'rim':(171,110,38),'stem':(225,216,180),'cap':tone,'spot':(239,230,207),'cut':(180,144,87),'wood':(142,98,58),'trim':(221,169,70),'metal':(86,104,111),'button':(177,73,54),'white':(223,225,216),'red':(178,62,51),'straw':(177,158,56),'rope':(125,108,46),'soil':(68,51,37),'leaf':(68,119,59),'petal':(213,115,159),'cloth':tone,'sand':TONES['sand'],'rubber':(43,48,51),'seat':(135,53,53),'stone':tone,'water':(129,181,180)}
 if f['kind']=='bench':c['wood']=tone
 if f['kind']=='chest':c['wood']=tone
 if f['tone']=='white':c['frame']=(162,173,163)
 if f['kind']=='board' and f['tone']=='white':c['face']=(94,117,94)
 if f['name']=='PokeB_BluePlaque':c.update(frame=(109,120,140),face=(168,178,194),ink=(49,107,157))
 if f['name']=='PokeO_BluePlaque':c.update(frame=(165,175,192),face=(70,102,150),ink=(170,193,210))
 if f['source']=='poke_u.jpg':c.update(frame=(166,177,119),ink=(219,230,197))
 if f['name']=='PokeF_GardenNoticeboard':c.update(frame=(81,88,69),face=(136,142,112))
 return c

def paint(f,m,style):
 flat='TwoColor' in style;crate='CratePalette' in style;c=colors(f)
 palette=[tuple(a) for a in CRATE['rgba']] if crate else [(0,0,0,255)]*256
 keys={};groups={};mapping={}
 for label in sorted(set(m.v.values())):
  raw=label[:-1];group='stem' if raw=='spot' else raw
  if flat and f['kind'] in ['sign','board','direction'] and f['tone'] in ['wood','brown'] and raw in ['frame','face']:group='wood'
  if flat and f['kind']=='question' and raw=='rim':group='body'
  color=c[group] if flat else c[raw]
  delta=0 if flat else [-18,0,15][int(label[-1])]
  if raw=='cloth' and f['kind']=='parasol' and not flat and label[-1]=='0':color=(237,232,204);delta=0
  color=tuple(max(0,min(255,v+delta)) for v in color)+(255,);key=(group,color)
  if key not in keys:
   if crate:
    allowed=[i for i in range(1,255) if str(i) not in groups or groups[str(i)]==group]
    if group=='metal':
     neutral=[i for i in allowed if max(palette[i-1][:3])-min(palette[i-1][:3])<45]
     if neutral:allowed=neutral
    if group=='sand':
     earthy=[i for i in allowed if palette[i-1][0]>=palette[i-1][1] and palette[i-1][1]>palette[i-1][2]]
     if earthy:allowed=earthy
    idx=min(allowed,key=lambda i:sum((palette[i-1][k]-color[k])**2 for k in range(3)))
   else:idx=len(keys)+1;palette[idx-1]=color
   keys[key]=idx;groups[str(idx)]=group
  mapping[label]=keys[key]
 return {p:mapping[s] for p,s in m.v.items()},palette,groups

def rooted(v):
 left=set(v);result=[]
 while left:
  todo=[left.pop()];part=[]
  while todo:
   p=todo.pop();part.append(p);x,y,z=p
   for q in [(x-1,y,z),(x+1,y,z),(x,y-1,z),(x,y+1,z),(x,y,z-1),(x,y,z+1)]:
    if q in left:left.remove(q);todo.append(q)
  result.append({'voxels':len(part),'minimum_z':min(p[2] for p in part)})
 return result

def main():
 manifest={'date':'2026-10-29','families':FAMILIES,'models':[],'reuse':{}}
 for f in FAMILIES:
  dest=ROOT/'output'/Path(f['source']).stem;support=dest/'props';support.mkdir(parents=True,exist_ok=True)
  crop=Image.open(ROOT/f['source']).convert('RGB').crop(f['crop']);scale=min(8,600/crop.width,400/crop.height)
  crop.resize((int(crop.width*scale),int(crop.height*scale)),Image.Resampling.NEAREST).save(support/(f['name']+'_source.png'))
  models={False:make(f),True:make(f,True)}
  assert set(models[False].v)!=set(models[True].v),f['name']
  for m in models.values():assert all(c['minimum_z']==0 for c in rooted(m.v)),(f['name'],rooted(m.v))
  for style in STYLES:
   m=models['Cartoon' in style];v,pal,groups=paint(f,m,style)
   path=dest/(f['name']+('' if style=='Base' else '_'+style)+'.vox')
   # Existing outputs may only be rewritten by this generator if unchanged since its last run.
   if path.exists():
    previous=json.loads((HERE/'manifest.json').read_text()) if (HERE/'manifest.json').exists() else {'models':[]}
    old=next((r for r in previous['models'] if r['file']==path.relative_to(ROOT).as_posix()),None)
    if old:assert hashlib.sha256(path.read_bytes()).hexdigest()==old['sha256'],'Hand edit: '+str(path)
    else:assert read(path)==(m.size,v,pal),'Untracked different asset: '+str(path)
   write(path,m.size,v,pal);assert read(path)==(m.size,v,pal)
   row={'file':path.relative_to(ROOT).as_posix(),'family':f['name'],'style':style,'canvas':m.size,'voxels':len(v),'colors':len(set(v.values())),'groups':groups,'components':components(v),'occupied_min':[min(p[k] for p in v) for k in range(3)],'occupied_max':[max(p[k] for p in v) for k in range(3)],'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'palette_sha256':hashlib.sha256(b''.join(bytes(c) for c in pal)).hexdigest(),'material':'opaque diffuse'}
   if 'CratePalette' in style:assert row['palette_sha256']==CRATE['palette_sha256']
   if 'TwoColor' in style:assert row['colors']==len(set(groups.values()))
   manifest['models'].append(row)
  print(f['name'])
 (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2))
 for source in json.loads((HERE/'source-inventory.json').read_text()):
  src=source['source'];support=ROOT/'output'/Path(src).stem/'props';support.mkdir(parents=True,exist_ok=True)
  (support/'manifest.json').write_text(json.dumps({'source':source,'families':[f for f in FAMILIES if f['source']==src],'models':[r for r in manifest['models'] if r['file'].split('/')[1]==Path(src).stem],'reuse':manifest['reuse'].get(src,[])},indent=2))
 print('GENERATED',len(manifest['models']))
if __name__=='__main__':main()
