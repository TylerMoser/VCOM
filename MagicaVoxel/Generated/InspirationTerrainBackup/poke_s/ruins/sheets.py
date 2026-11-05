from PIL import Image,ImageDraw
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;m=json.loads((HERE/'manifest.json').read_text())
styles=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
labels=['Base','Cartoon','Crate palette','Flat colors','Cartoon + flat','Crate + flat','All three']
def thumb(path,size):
 im=Image.open(path).convert('RGB');im.thumbnail(size);return im
overview=Image.new('RGB',(1200,4*320),'#d9dfd4');od=ImageDraw.Draw(overview)
for j,f in enumerate(m['families']):
 name=f['name'];sheet=Image.new('RGB',(1680,290),'#d9dfd4');d=ImageDraw.Draw(sheet)
 for i,s in enumerate(styles):
  stem=name+('' if s=='Base' else '_'+s)
  d.text((i*240+5,5),labels[i],fill='black');sheet.paste(thumb(HERE/'previews'/f'{stem}.png',(240,240)),(i*240,28))
 sheet.save(HERE/f'{name}_variations.png')
 geo=Image.new('RGB',(1200,560),'#d9dfd4');gd=ImageDraw.Draw(geo)
 for row,style in enumerate(['Base','Cartoon']):
  stem=name+('' if style=='Base' else '_'+style)
  for i,a in enumerate([0,90,180,270]):
   geo.paste(thumb(HERE/'previews'/f'{stem}_view{a}.png',(240,240)),(i*240,row*280+25));gd.text((i*240+5,row*280+5),f'{style} {a} degrees',fill='black')
 geo.paste(thumb(HERE/'reference'/f'{name}.png',(230,500)),(965,25));geo.save(HERE/f'{name}_geometry.png')
 x=j%4*300;y=j//4*320
 overview.paste(thumb(HERE/'previews'/f'{name}.png',(300,280)),(x,y+30));od.text((x+5,y+5),name.replace('PokeS_Ruins',''),fill='black')
overview.crop((0,0,1200,960)).save(HERE/'overview.png')
for page in range(3):
 fs=m['families'][page*4:(page+1)*4];im=Image.new('RGB',(1680,len(fs)*320),'#d9dfd4');d=ImageDraw.Draw(im)
 for j,f in enumerate(fs):
  d.text((5,j*320+4),f['name'],fill='black');im.paste(Image.open(HERE/(f['name']+'_variations.png')),(0,j*320+25))
 im.save(HERE/f'styles_{page+1}.png')
 geo=Image.new('RGB',(1200,len(fs)*560),'#d9dfd4')
 for j,f in enumerate(fs):geo.paste(Image.open(HERE/(f['name']+'_geometry.png')),(0,j*560))
 geo.save(HERE/f'geometry_{page+1}.png')
print('Sheets complete')
