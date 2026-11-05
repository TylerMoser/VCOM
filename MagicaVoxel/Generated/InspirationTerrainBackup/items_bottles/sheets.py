from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
here=Path(__file__).resolve().parent
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
titlefont=ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf',25)
colors=['Red','Blue','Pink','Cyan','Purple','Green','Yellow']
for size in ['Small','Medium','Large']:
    sheet=Image.new('RGB',(7*240,630),'#162630');d=ImageDraw.Draw(sheet)
    d.text((20,10),size+' potions | Top: translucent liquid / Bottom: opaque liquid',font=titlefont,fill='white')
    for y,mode in enumerate(['Translucent','Opaque']):
        for x,color in enumerate(colors):
            im=Image.open(here/'previews'/f'PotionBottle_{size}_{color}_{mode}.png').resize((240,240))
            sheet.paste(im,(x*240,60+y*280));d.text((x*240+12,300+y*280),color,font=font,fill='white')
    sheet.save(here/f'{size.lower()}_comparison.png')
sheet=Image.new('RGB',(960,730),'#162630');d=ImageDraw.Draw(sheet)
d.text((20,12),'Glass potion bottles | same scale in every panel',font=titlefont,fill='white')
for x,size in enumerate(['Small','Medium','Large']):
    for y,suffix in enumerate(['','_bottom']):
        im=Image.open(here/'previews'/f'PotionBottle_{size}_Empty{suffix}.png')
        sheet.paste(im,(x*320,60+y*330))
    d.text((x*320+18,365),size+' / below: underside',font=font,fill='white')
sheet.save(here/'empty_sizes.png')
