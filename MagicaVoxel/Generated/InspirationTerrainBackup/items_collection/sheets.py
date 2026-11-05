from voxlib import *
from PIL import Image,ImageDraw,ImageFont
from collections import defaultdict
import shutil
rows=json.loads((HERE/'render-list.json').read_text());groups=defaultdict(list);categories=defaultdict(list)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',13);title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',24)
for r in rows:
 if r['form']=='Standalone':groups[r['category'],r['item']].append(r)
out=HERE/'sheets';out.mkdir(exist_ok=True)
def image(r,suffix=''):return Image.open(HERE/'previews'/(r['preview_id']+suffix+'.png')).convert('RGB')
for (cat,item),rs in groups.items():
 base=[r for r in rs if r['style']=='Base'];crate=[r for r in rs if r['style']=='CratePalette']
 sheet=Image.new('RGB',(768,730),'#192832');d=ImageDraw.Draw(sheet)
 d.text((12,8),cat+' / '+item,font=title,fill='white')
 d.text((12,38),'Base front / crate palette front / Base rear — individually framed',font=small,fill='#bccbd6')
 for x,r in enumerate(base):
  for y,rr,suffix in ((0,r,''),(1,crate[x],''),(2,r,'_back')):sheet.paste(image(rr,suffix),(x*192,65+y*215))
  d.text((x*192+6,258),r['design'],font=font,fill='white')
  d.text((x*192+6,690),' × '.join(map(str,r['canvas']))+' vox',font=small,fill='white')
 folder=out/cat;folder.mkdir(exist_ok=True);sheet.save(folder/(item+'.png'))
 categories[cat].append(base[0])
for cat,rs in categories.items():
 # Every type, paginated to keep overview lettering legible.
 for start in range(0,len(rs),24):
  subset=rs[start:start+24];height=((len(subset)+3)//4)*220+65
  sheet=Image.new('RGB',(768,height),'#192832');d=ImageDraw.Draw(sheet)
  d.text((12,8),cat+' — one design per type',font=title,fill='white')
  d.text((12,37),'Each item has four designs and four crate-palette counterparts.',font=small,fill='#bccbd6')
  for j,r in enumerate(subset):
   x=j%4;y=j//4;sheet.paste(image(r),(x*192,60+y*220));d.text((x*192+4,250+y*220),r['item'],font=font,fill='white')
  sheet.save(out/cat/f'Overview_{start//24+1}.png')
  shutil.copy2(out/cat/f'Overview_{start//24+1}.png',DEST/cat/f'Preview_{start//24+1}.png')
 # Contact sheets of fitted parts shown on the unmodified-size body.
 fitted=[r for r in rows if r['category']==cat and r['form']=='Fitted' and r['style']=='Base']
 for start in range(0,len(fitted),16):
  subset=fitted[start:start+16];sheet=Image.new('RGB',(768,((len(subset)+3)//4)*220+55),'#192832');d=ImageDraw.Draw(sheet)
  d.text((12,8),cat+' — fitted on Character_Bigger',font=title,fill='white')
  for j,r in enumerate(subset):
   x=j%4;y=j//4;sheet.paste(image(r),(x*192,50+y*220));d.text((x*192+3,240+y*220),r['item']+' '+r['design'],font=small,fill='white')
  sheet.save(out/cat/f'Fitted_{start//16+1}.png')
print('Created',len(groups),'item comparison sheets and category/fitted overviews')
