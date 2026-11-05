from pathlib import Path
from PIL import Image,ImageDraw
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];m=json.loads((HERE/'manifest.json').read_text())
styles=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
labels=['Base','Cartoon','Crate palette','Flat colors','Cartoon + flat','Crate + flat','All three']
def thumb(path,size):
 im=Image.open(path).convert('RGB');im.thumbnail(size);return im
overview=Image.new('RGB',(1400,((len(m['families'])+3)//4)*250),'#d9dfd4');od=ImageDraw.Draw(overview)
for j,f in enumerate(m['families']):
 folder=ROOT/'output'/Path(f['source']).stem/'codex_waterfalls_caves';name=f['name']
 sheet=Image.new('RGB',(1680,220),'#d9dfd4');d=ImageDraw.Draw(sheet)
 for i,s in enumerate(styles):
  stem=name+('' if s=='Base' else '_'+s);d.text((i*240+4,5),labels[i],fill='black');sheet.paste(thumb(folder/'previews'/f'{stem}.png',(238,185)),(i*240,28))
 sheet.save(folder/(name+'_variations.png'))
 geo=Image.new('RGB',(1440,465),'#d9dfd4');d=ImageDraw.Draw(geo)
 for row,s in enumerate(['Base','Cartoon']):
  stem=name+('' if s=='Base' else '_'+s)
  for i,angle in enumerate([0,90,180,270,'underside']):
   suffix='_'+angle if angle=='underside' else '_view'+str(angle)
   d.text((i*240+4,row*230+4),s+' '+str(angle),fill='black');geo.paste(thumb(folder/'previews'/(stem+suffix+'.png'),(238,190)),(i*240,row*230+25))
 geo.paste(thumb(folder/'reference'/(name+'.png'),(235,400)),(1200,25));geo.save(folder/(name+'_geometry.png'))
 x=j%4*350;y=j//4*250;overview.paste(thumb(folder/'previews'/(name+'.png'),(345,215)),(x,y+27));od.text((x+4,y+5),name,fill='black')
overview.save(HERE/'overview.png')
for page in range((len(m['families'])+3)//4):
 fs=m['families'][page*4:(page+1)*4];sheet=Image.new('RGB',(1680,len(fs)*250),'#d9dfd4');geo=Image.new('RGB',(1440,len(fs)*490),'#d9dfd4');d=ImageDraw.Draw(sheet);dg=ImageDraw.Draw(geo)
 for i,f in enumerate(fs):
  folder=ROOT/'output'/Path(f['source']).stem/'codex_waterfalls_caves';name=f['name'];d.text((4,i*250+4),name,fill='black');dg.text((4,i*490+4),name,fill='black')
  sheet.paste(Image.open(folder/(name+'_variations.png')),(0,i*250+25));geo.paste(Image.open(folder/(name+'_geometry.png')),(0,i*490+25))
 sheet.save(HERE/f'styles_{page+1}.png');geo.save(HERE/f'geometry_{page+1}.png')
print('Composed',len(m['families']),'families')
