"""Compose image-specific comparison/geometry sheets and collection review sheets."""
from PIL import Image,ImageDraw
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
m=json.loads((HERE/'manifest.json').read_text());families=m['families']
styles=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
labels=['Base','Cartoon','Crate palette','Flat colors','Cartoon + flat','Crate + flat','All three']
def folder(f):return ROOT/'output'/Path(f['source']).stem/'props'
def stem(f,s):return f['name']+('' if s=='Base' else '_'+s)
def thumb(path,size):
 im=Image.open(path).convert('RGB');im.thumbnail(size);return im
for f in families:
 dest=folder(f);sheet=Image.new('RGB',(1540,300),'#e8eadf');d=ImageDraw.Draw(sheet)
 d.text((5,5),f['name']+' | '+str(f['size'])+' voxels | independently framed per family',fill='black')
 for i,s in enumerate(styles):
  d.text((i*220+4,28),labels[i],fill='black');sheet.paste(thumb(dest/'previews'/(stem(f,s)+'.png'),(216,240)),(i*220,50))
 sheet.save(dest/(f['name']+'_variations.png'))
 geo=Image.new('RGB',(960,550),'#e8eadf');d=ImageDraw.Draw(geo)
 for j,s in enumerate(['Base','Cartoon']):
  for i,a in enumerate([0,90,180,270]):
   d.text((i*240+3,j*275+3),s+' '+str(a)+' degrees',fill='black');geo.paste(thumb(dest/'previews'/(stem(f,s)+'_view'+str(a)+'.png'),(236,245)),(i*240,j*275+25))
 geo.save(dest/(f['name']+'_geometry.png'))
for page in range((len(families)+5)//6):
 batch=families[page*6:page*6+6];sheet=Image.new('RGB',(1120,len(batch)*190),'#e8eadf');d=ImageDraw.Draw(sheet)
 geo=Image.new('RGB',(1120,len(batch)*170),'#e8eadf');dg=ImageDraw.Draw(geo)
 for j,f in enumerate(batch):
  d.text((4,j*190+3),f['name'],fill='black');dg.text((4,j*170+3),f['name']+' | Base: 0,90,180,270 | Cartoon: 0,90,180,270',fill='black')
  for i,s in enumerate(styles):
   d.text((i*160+3,j*190+18),labels[i],fill='black');sheet.paste(thumb(folder(f)/'previews'/(stem(f,s)+'.png'),(158,155)),(i*160,j*190+35))
  for k,s in enumerate(['Base','Cartoon']):
   for i,a in enumerate([0,90,180,270]):geo.paste(thumb(folder(f)/'previews'/(stem(f,s)+'_view'+str(a)+'.png'),(138,140)),((k*4+i)*140,j*170+25))
 sheet.save(HERE/f'variations_{page+1:02}.png');geo.save(HERE/f'geometry_{page+1:02}.png')
overview=Image.new('RGB',(1540,((len(families)+10)//11)*180),'#e8eadf');d=ImageDraw.Draw(overview)
for i,f in enumerate(families):
 x=i%11*140;y=i//11*180;d.text((x+3,y+4),f['name'].split('_')[0],fill='black')
 d.text((x+3,y+18),f['name'].split('_')[1][:22],fill='black')
 overview.paste(thumb(folder(f)/'previews'/(f['name']+'.png'),(138,140)),(x,y+37))
overview.save(HERE/'overview.png')
print('Composed',len(families),'family sheets')
