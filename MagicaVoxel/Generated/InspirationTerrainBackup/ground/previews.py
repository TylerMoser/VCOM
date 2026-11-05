"""Exact stored-voxel top views and 3x3 repetition checks; optional Godot sheets."""
from pathlib import Path
from PIL import Image,ImageDraw
import json
from voxlib import read
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
m=json.loads((HERE/'manifest.json').read_text());rows=m['models'];fam=m['families'];labels=['Base','Cartoon','Crate palette','Flat','Cartoon + flat','Crate + flat','All three']
def top(row):
 _,v,p=read(ROOT/row['file']);im=Image.new('RGB',(16,16))
 heights={}
 for (x,y,z),c in v.items():
  if z>heights.get((x,y),-1):heights[x,y]=z;im.putpixel((x,y),p[c-1][:3])
 return im
# Read only serialized VOX; top paint is unlit, so flat-color behavior is visible.
images={r['file']:top(r) for r in rows}
for f in fam:
 subset=[r for r in rows if r['family']==f['name']];dest=ROOT/'output'/Path(f['source']).stem/'ground'
 sheet=Image.new('RGB',(1120,370),'#e4e5dc');d=ImageDraw.Draw(sheet);d.text((4,4),f['name']+' | 16 x 16 x 16 canvas | unlit top / 3 x 3 repeat',fill='black')
 for i,r in enumerate(subset):
  d.text((i*160+4,25),labels[i],fill='black');im=images[r['file']];sheet.paste(im.resize((128,128),Image.Resampling.NEAREST),(i*160+12,45))
  repeat=Image.new('RGB',(48,48))
  for x in range(3):
   for y in range(3):repeat.paste(im,(x*16,y*16))
  sheet.paste(repeat.resize((144,144),Image.Resampling.NEAREST),(i*160+4,196))
 sheet.save(dest/(f['name']+'_top_and_repeat.png'))
for typ in ['surface','transition']:
 fs=[f for f in fam if f['role']==typ]
 for page in range((len(fs)+11)//12):
  batch=fs[page*12:(page+1)*12];sheet=Image.new('RGB',(1050,len(batch)*130),'#e4e5dc');d=ImageDraw.Draw(sheet)
  for j,f in enumerate(batch):
   d.text((3,j*130+2),f['name'],fill='black')
   for i,r in enumerate(r for r in rows if r['family']==f['name']):
    d.text((i*150+3,j*130+18),labels[i],fill='black');im=images[r['file']];repeat=Image.new('RGB',(48,48))
    for x in range(3):
     for y in range(3):repeat.paste(im,(x*16,y*16))
    sheet.paste(repeat.resize((96,96),Image.Resampling.NEAREST),(i*150+20,j*130+33))
  sheet.save(HERE/f'{typ}_styles_{page+1:02}.png')
# Assemble real edge/corner arrangements around a central patch (A outside, B inside).
rowmap={(r['family'],r['style']):r for r in rows}
styles=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
for f in fam:
 if f['role']!='transition' or f['contour']!='Edge':continue
 prefix=f['name'][:-4];dest=ROOT/'output'/Path(f['source']).stem/'ground';sheet=Image.new('RGB',(1260,215),'#e4e5dc');d=ImageDraw.Draw(sheet)
 d.text((4,4),prefix+' | 5 x 5 assembled tiles; A outside, B inside',fill='black')
 for k,style in enumerate(styles):
  tile=Image.new('RGB',(80,80))
  for gx in range(5):
   for gy in range(5):
    name=f['materials'][0];rotation=0
    if (gx,gy)==(2,2):name=f['materials'][1]
    elif (gx,gy) in [(1,1),(3,1),(3,3),(1,3)]:
     name=prefix+'InnerCorner';rotation={(1,1):0,(3,1):270,(3,3):180,(1,3):90}[gx,gy]
    elif (gx,gy) in [(2,1),(3,2),(2,3),(1,2)]:
     name=f['name'];rotation={(2,1):270,(3,2):180,(2,3):90,(1,2):0}[gx,gy]
    im=images[rowmap[name,style]['file']].rotate(rotation);tile.paste(im,(gx*16,gy*16))
  sheet.paste(tile.resize((160,160),Image.Resampling.NEAREST),(k*180+8,44));d.text((k*180+3,25),labels[k],fill='black')
 sheet.save(dest/(prefix+'_assembled.png'))

# Actual runtime camera/lighting is identical for all styles.
if all((ROOT/Path(r['file']).parent/'ground/previews'/(Path(r['file']).stem+'.png')).exists() for r in rows):
 for f in fam:
  dest=ROOT/'output'/Path(f['source']).stem/'ground';sheet=Image.new('RGB',(1400,240),'#e4e5dc');d=ImageDraw.Draw(sheet);d.text((4,4),f['name']+' | VCOM renderer | 16 voxels per cell',fill='black')
  for i,r in enumerate(r for r in rows if r['family']==f['name']):
   d.text((i*200+3,23),labels[i],fill='black');im=Image.open(dest/'previews'/(Path(r['file']).stem+'.png'));im.thumbnail((196,196));sheet.paste(im,(i*200,42))
  sheet.save(dest/(f['name']+'_variations.png'))
 for page in range((len(fam)+47)//48):
  sheet=Image.new('RGB',(1200,1280),'#e4e5dc');d=ImageDraw.Draw(sheet)
  for j,f in enumerate(fam[page*48:(page+1)*48]):
   x=j%6*200;y=j//6*160;d.text((x+2,y+2),f['name'].replace('_Ground_','\n'),fill='black');im=Image.open(ROOT/'output'/Path(f['source']).stem/'ground/previews'/(f['name']+'.png'));im.thumbnail((130,125));sheet.paste(im,(x+32,y+32))
  sheet.save(HERE/f'runtime_overview_{page+1:02}.png')
print('Top/repeat previews ready for',len(fam),'families')
