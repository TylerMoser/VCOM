from pathlib import Path
from PIL import Image,ImageDraw
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
m=json.loads((HERE/'manifest.json').read_text());families=m['families']
styles=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
labels=['Base','Cartoon','Crate palette','Minimal flat','Cartoon + flat','Crate + flat','Cartoon + crate + flat']
def image(path,size):
 im=Image.open(path).convert('RGB');im.thumbnail(size);return im
def folder(f):return ROOT/'output'/Path(f['source']).stem/'lights'
def stem(f,s):return f['name']+('' if s=='Base' else '_'+s)
for f in families:
 support=folder(f);sheet=Image.new('RGB',(1540,630),'#eceee7');d=ImageDraw.Draw(sheet)
 d.text((12,10),f['name']+' | day / night | '+str(f['size'])+' voxels',fill='black')
 for i,s in enumerate(styles):
  d.text((i*220+5,35),labels[i],fill='black')
  for j,suffix in enumerate(['','_night']):sheet.paste(image(support/'previews'/(stem(f,s)+suffix+'.png'),(216,280)),(i*220,j*285+55))
 sheet.save(support/'variations.png')
 geo=Image.new('RGB',(960,620),'#eceee7');d=ImageDraw.Draw(geo)
 for j,s in enumerate(['Base','Cartoon']):
  for i,a in enumerate([0,90,180,270]):
   d.text((i*240+5,j*310+5),s+' '+str(a)+' degrees',fill='black')
   geo.paste(image(support/'previews'/(stem(f,s)+'_view'+str(a)+'.png'),(236,280)),(i*240,j*310+25))
 geo.save(support/'geometry.png')
for part in range(2):
 batch=families[part*6:part*6+6]
 sheet=Image.new('RGB',(1120,len(batch)*245),'#eceee7');d=ImageDraw.Draw(sheet)
 geo=Image.new('RGB',(1280,len(batch)*290),'#eceee7');dg=ImageDraw.Draw(geo)
 for j,f in enumerate(batch):
  d.text((5,j*245+3),f['name'],fill='black');dg.text((5,j*290+3),f['name'],fill='black')
  for i,s in enumerate(styles):
   d.text((i*160+3,j*245+20),labels[i],fill='black');sheet.paste(image(folder(f)/'previews'/(stem(f,s)+'.png'),(158,205)),(i*160,j*245+40))
  for k,s in enumerate(['Base','Cartoon']):
   for i,a in enumerate([0,90,180,270]):
    x=(k*4+i)*160;dg.text((x+3,j*290+20),s+' '+str(a),fill='black');geo.paste(image(folder(f)/'previews'/(stem(f,s)+'_view'+str(a)+'.png'),(158,250)),(x,j*290+40))
 sheet.save(HERE/f'variations_{part+1}.png');geo.save(HERE/f'geometry_{part+1}.png')
overview=Image.new('RGB',(1320,720),'#eceee7');d=ImageDraw.Draw(overview)
for i,f in enumerate(families):
 x=(i%6)*220;y=(i//6)*360;d.text((x+3,y+5),f['name'].replace('Street',''),fill='black')
 overview.paste(image(folder(f)/'previews'/(f['name']+'_night.png'),(216,320)),(x,y+30))
overview.save(HERE/'overview-night.png')
print('Contact sheets composed')
