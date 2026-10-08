"""Crops of a picture, enlarged, side by side into one sheet: x5_crops.py <picture> <sheet> <scale> x,y,w,h ..."""
import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
picture = Image.open(sys.argv[1]).convert("RGB")
scale = int(sys.argv[3])
crops = []
for spec in sys.argv[4:]:
    x, y, w, h = (int(v) for v in spec.split(","))
    crop = picture.crop((x, y, x + w, y + h))
    crops.append(crop.resize((w * scale, h * scale), Image.NEAREST))
sheet = Image.new("RGB", (sum(c.width for c in crops) + 6 * (len(crops) - 1), max(c.height for c in crops)), (90, 90, 90))
at = 0
for c in crops:
    sheet.paste(c, (at, 0)); at += c.width + 6
sheet.save(sys.argv[2])
print("saved", sys.argv[2], sheet.size)
