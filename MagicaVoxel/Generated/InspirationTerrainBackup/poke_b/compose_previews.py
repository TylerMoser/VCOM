"""Assemble labeled contact sheets from Godot-rendered VOX previews (Pillow).
Run only after qa/preview.gd finishes. Original inspiration image is read-only.
"""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
M=json.loads((ROOT/'manifest.json').read_text())
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
LABELS=['Base','Cartoon','Crate palette','Two color','Cartoon + Two','Crate + Two','Cartoon + Crate + Two']
def font(n):
 return ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',n)
def render(fam,style):
 name=fam['asset_id']+('' if style=='Base' else '_'+style)
 return Image.open(ROOT/'previews'/f'{name}.png').convert('RGB')
def sheet(size,title,subtitle):
 im=Image.new('RGB',size,'#eff1e8');d=ImageDraw.Draw(im)
 d.text((20,12),title,font=font(25),fill='#24372b');d.text((20,48),subtitle,font=font(15),fill='#526252')
 return im,d
overview,d=sheet((1120,1490),'poke_b | 16 tree appearances','Base VOX renders. Each card is framed independently; dimensions are canvas X x Y x Z, in voxels.')
for i,fam in enumerate(M['families']):
 x=i%4*280;y=85+i//4*350
 overview.paste(render(fam,'Base').resize((255,297),Image.Resampling.LANCZOS),(x+12,y))
 d.text((x+12,y+298),fam['asset_id'].replace('PokeB_',''),font=font(17),fill='#24372b')
 d.text((x+12,y+322),' x '.join(map(str,fam['canvas_xyz']))+' voxels',font=font(15),fill='#526252')
overview.save(ROOT/'overview.png')
source=Image.open(ROOT.parent.parent/'poke_b.png')
for fam in M['families']:
 im,d=sheet((1120,800),fam['asset_id']+' | complete style family','16 voxels = one map tile. Matched camera/lighting. TwoColor stores two paint colors; lighting still shades faces.')
 # Reference and seven models occupy eight cards.
 crop=source.crop(fam['source_region_xyxy_exclusive']);crop.thumbnail((210,250),Image.Resampling.NEAREST)
 # Enlarge source with nearest sampling, retaining original sprite pixel edges.
 box=source.crop(fam['source_region_xyxy_exclusive']);factor=min(230/box.width,260/box.height)
 box=box.resize((round(box.width*factor),round(box.height*factor)),Image.Resampling.NEAREST)
 im.paste(box,((280-box.width)//2,110+(260-box.height)//2));d.text((14,83),'Source region (includes neighbors)',font=font(14),fill='#24372b')
 for i,(style,label) in enumerate(zip(STYLES,LABELS),1):
  x=i%4*280;y=80+i//4*355
  im.paste(render(fam,style).resize((255,297),Image.Resampling.LANCZOS),(x+12,y+26))
  d.text((x+12,y),label,font=font(17),fill='#24372b')
 im.save(ROOT/'previews'/f"{fam['asset_id']}_family.png")
for batch in range(4):
 im,d=sheet((1260,1120),f'poke_b | validation contact sheet {batch+1}/4','Rows are independently framed. All seven treatments in each row share the same camera and lighting.')
 for col,label in enumerate(LABELS):d.text((col*180+6,78),label,font=font(12),fill='#24372b')
 for row,fam in enumerate(M['families'][batch*4:batch*4+4]):
  y=100+row*250
  for col,style in enumerate(STYLES):im.paste(render(fam,style).resize((171,200),Image.Resampling.LANCZOS),(col*180+4,y))
  d.text((8,y+205),fam['asset_id']+' | '+' x '.join(map(str,fam['canvas_xyz'])),font=font(16),fill='#24372b')
 im.save(ROOT/'previews'/f'contact_{batch+1:02}.png')
# Four azimuths for each Base and Cartoon, allowing shape and back-side review.
for batch in range(4):
 im,d=sheet((1280,1120),f'poke_b | four-view geometry review {batch+1}/4','Each pair: Base then Cartoon. Azimuths 25, 115, 205, 295 degrees. Fixed world light.')
 for row,fam in enumerate(M['families'][batch*4:batch*4+4]):
  for group,style in enumerate(['Base','Cartoon']):
   name=fam['asset_id']+('' if style=='Base' else '_Cartoon')
   for col,angle in enumerate([25,115,205,295]):
    suffix='' if angle==25 else '_view'+str(angle)
    image=Image.open(ROOT/'previews'/f'{name}{suffix}.png')
    im.paste(image.resize((154,180),Image.Resampling.LANCZOS),(group*640+col*160+3,90+row*250))
   d.text((group*640+8,275+row*250),name,font=font(15),fill='#24372b')
 im.save(ROOT/'previews'/f'geometry_{batch+1:02}.png')
print('Wrote overview, 16 family sheets, 4 style contact sheets and 4 multi-angle geometry sheets.')
