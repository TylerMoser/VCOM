"""Compose the nine mixture renders; requires Pillow and completed Godot previews."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parent/'previews'
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',17)
board=Image.new('RGB',(1080,1400),'#eef2e8');d=ImageDraw.Draw(board)
d.text((18,12),'poke_a - combined tree styles',font=font,fill='#203d35')
labels=['Cartoon + TwoColor','CratePalette + TwoColor','Cartoon + CratePalette + TwoColor']
styles=['Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
for c,label in enumerate(labels):d.text((c*360+10,54),label,font=small,fill='#203d35')
for row,(base,label) in enumerate([('PokeA_ForestTree_Large','Large tree - 32 x 32 x 64'),('PokeA_ForestTree','Original size - 16 x 16 x 32'),('PokeA_Sapling','Sapling - 16 x 16 x 16')]):
 y=88+row*425;d.text((14,y),label,font=small,fill='#203d35')
 for col,style in enumerate(styles):
  im=Image.open(p/(base+'_'+style+'.png')).resize((340,397),Image.Resampling.LANCZOS);board.paste(im,(col*360+10,y+25))
d.text((14,1375),'Exactly two paint colors per model. Render lighting still shades surfaces. Rows are framed separately.',font=small,fill='#203d35')
board.save(p/'mixtures_comparison.png')
