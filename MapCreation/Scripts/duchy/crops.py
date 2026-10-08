import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
src, out = sys.argv[1], sys.argv[2]
image = Image.open(src).convert("RGB")
spots = {"swamp": (900, 1900, 1900, 2700), "range": (1300, 1500, 2300, 2300), "west": (200, 1000, 1200, 1800),
         "desert": (1800, 900, 2800, 1700), "south": (1900, 3100, 2900, 3900), "north": (900, 300, 1900, 1100)}
for name, box in spots.items():
    if len(sys.argv) > 3 and name not in sys.argv[3:]:
        continue
    image.crop(box).save(out + "/dcrop_%s.png" % name)
print("done")
