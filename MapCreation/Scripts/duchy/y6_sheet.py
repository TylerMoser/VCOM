"""Sheets of the same places from several pictures, enlarged, in a grid: one row a place, one
column a picture.

Usage: y6_sheet.py <sheet to write> <scale> <w> <h> <picture>[,<picture>...] x,y [x,y ...]
(each x,y is the middle of a place)
"""
import sys
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
write_to, scale, w, h = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
pictures = [Image.open(p).convert("RGB") for p in sys.argv[5].split(",")]
places = [tuple(int(v) for v in spec.split(",")) for spec in sys.argv[6:]]
gap = 6
sheet = Image.new("RGB", (len(pictures) * (w * scale + gap) - gap, len(places) * (h * scale + gap) - gap), (200, 60, 60))
for row, (x, y) in enumerate(places):
    for col, picture in enumerate(pictures):
        crop = picture.crop((x - w // 2, y - h // 2, x - w // 2 + w, y - h // 2 + h)).resize((w * scale, h * scale), Image.NEAREST)
        sheet.paste(crop, (col * (w * scale + gap), row * (h * scale + gap)))
sheet.save(write_to)
print("saved %s %s" % (write_to, sheet.size))
