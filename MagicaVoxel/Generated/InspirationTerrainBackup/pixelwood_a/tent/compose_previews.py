"""Compose tent source comparison, all treatments and cardinal geometry views."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
R=Path(__file__).resolve().parent
m=json.loads((R/'manifest.json').read_text())
font=lambda n:ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
im=Image.new('RGB',(1200,850),'#eff1e8');d=ImageDraw.Draw(im)
d.text((20,10),'Pixelwood A | ridge tent | 64 x 64 x 32 voxels',font=font(24),fill='#26372c')
d.text((20,45),'Source plus seven treatments. Matched camera and light; TwoColor stores exactly two paint colors.',font=font(16),fill='#526252')
source=Image.open(R.parent/'reference/tent-source-enlarged.png');source.thumbnail((250,310));im.paste(source,((300-source.width)//2,105))
d.text((15,78),'Source reference',font=font(17),fill='#26372c')
labels=['Base','Cartoon','CratePalette','TwoColor','Cartoon + TwoColor','Crate + TwoColor','Cartoon + Crate + Two']
for i,(row,label) in enumerate(zip(m['models'],labels),1):
 x=i%4*300;y=78+i//4*380
 p=Image.open(R/'previews'/Path(row['file']).with_suffix('.png').name);p=p.resize((285,332))
 im.paste(p,(x+7,y+28));d.text((x+8,y),label,font=font(16),fill='#26372c')
im.save(R/'comparison.png')
im=Image.new('RGB',(1440,810),'#eff1e8');d=ImageDraw.Draw(im)
d.text((20,12),'Tent geometry | Base above, Cartoon below',font=font(24),fill='#26372c')
d.text((20,48),'Front / right / rear / left. Bilateral symmetry preserves different front and rear walls.',font=font(16),fill='#526252')
for row,style in enumerate(['','_Cartoon']):
 for col,angle in enumerate([0,90,180,270]):
  p=Image.open(R/'previews'/f'PixelwoodA_Tent{style}_view{angle}.png').resize((300,350))
  im.paste(p,(col*360+30,85+row*360))
im.save(R/'geometry.png')
print('Saved tent comparison and four-side geometry sheets.')
