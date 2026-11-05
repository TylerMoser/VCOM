"""Compose the Godot renders into a labeled original/variation comparison."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=Path(__file__).resolve().parent/'previews'
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
board=Image.new('RGB',(1280,1320),'#eef2e8');d=ImageDraw.Draw(board)
d.text((22,12),'poke_a - tree style variations',font=font,fill='#203d35')
for c,label in enumerate(['Original','Cartoon / symmetric','Crate palette','Two colors']):d.text((c*320+14,54),label,font=small,fill='#203d35')
for row,(base,label) in enumerate([('PokeA_ForestTree_Large','Large tree - 32 x 32 x 64'),('PokeA_ForestTree','Original size - 16 x 16 x 32'),('PokeA_Sapling','Sapling - 16 x 16 x 16')]):
 y=88+row*400;d.text((14,y),label,font=small,fill='#203d35')
 for col,suffix in enumerate(['','_Cartoon','_CratePalette','_TwoColor']):
  im=Image.open(p/(base+suffix+'.png')).resize((310,362),Image.Resampling.LANCZOS);board.paste(im,(col*320+5,y+28))
d.text((14,1294),'Rows are framed separately. Two-color models have no painted shading; lighting still shades surfaces.',font=small,fill='#203d35')
board.save(p/'variations_comparison.png')
