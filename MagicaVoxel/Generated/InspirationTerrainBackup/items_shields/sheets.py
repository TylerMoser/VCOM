from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
here=Path(__file__).resolve().parent;rows=json.loads((here/'manifest.json').read_text())
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',19)
title=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',26)
for kind in dict.fromkeys(r['kind'] for r in rows):
 subset=[r for r in rows if r['kind']==kind]
 sheet=Image.new('RGB',(1280,755),'#162630');d=ImageDraw.Draw(sheet)
 d.text((18,10),kind+' shields | front and rear | individually framed',font=title,fill='white')
 for x,r in enumerate(subset):
  stem=r['name'][:-4]
  for y,suffix in enumerate(['','_back']):
   sheet.paste(Image.open(here/'previews'/f'{stem}{suffix}.png'),(x*320,55+y*350))
  d.text((x*320+10,374),r['design'],font=font,fill='white')
  d.text((x*320+10,726),' × '.join(map(str,r['canvas']))+' voxels',font=font,fill='white')
 sheet.save(here/f'{kind}_comparison.png')
overview=Image.new('RGB',(1280,8*265+65),'#162630');d=ImageDraw.Draw(overview)
d.text((18,10),'32 shield designs | four per type | individually framed',font=title,fill='white')
for idx,r in enumerate(rows):
 x=idx%4;y=idx//4
 im=Image.open(here/'previews'/f"{r['name'][:-4]}.png").resize((240,240))
 overview.paste(im,(x*320+40,55+y*265))
 d.text((x*320+8,55+y*265+239),r['kind']+' / '+r['design'],font=font,fill='white')
overview.save(here/'Overview.png')
