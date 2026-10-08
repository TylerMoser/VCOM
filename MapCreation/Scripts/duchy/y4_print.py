"""Print a patch of WorldMapV1.png as letters: y4_print.py <MapCreation dir> x0 y0 w h"""
import sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
coast = np.asarray(Image.open(sys.argv[1] + "/WorldMapV1.png").convert("RGBA")).astype(int)
x0, y0, w, h = (int(v) for v in sys.argv[2:6])
rgb = coast[..., :3]
land = (rgb >= 250).all(axis=2)
sea = (rgb == (181, 235, 255)).all(axis=2)
dark = rgb.sum(axis=2) < 200
print("     " + "".join(str((x // 10) % 10) for x in range(x0, x0 + w)))
print("     " + "".join(str(x % 10) for x in range(x0, x0 + w)))
for y in range(y0, y0 + h):
    print("%4d %s" % (y, "".join("." if land[y, x] else "~" if sea[y, x] else "#" if dark[y, x] else "+" for x in range(x0, x0 + w))))
