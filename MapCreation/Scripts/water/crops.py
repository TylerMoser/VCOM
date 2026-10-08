"""Full-size crops of a rivers picture, for a close look."""
import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
src, out = sys.argv[1], sys.argv[2]
image = Image.open(src).convert("RGB")
spots = {"swamp": (700, 1900, 1700, 2700), "tundra": (650, 250, 1650, 1050), "desert": (1700, 900, 2700, 1700),
         "south": (1900, 3100, 2900, 3900), "west": (60, 1000, 1060, 1800), "east": (2000, 1750, 3000, 2550),
         "volcanoes": (1150, 100, 1950, 900), "neck": (1300, 2500, 2300, 3300)}
for name, box in spots.items():
    if len(sys.argv) > 3 and name not in sys.argv[3:]:
        continue
    image.crop(box).save(out + "/crop_%s.png" % name)
print("done")
