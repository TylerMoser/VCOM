"""The coast map with a plain line: sea, white land exactly as WorldMapV1.png has it, and every
pixel within W px of the land black. A trial picture, to look at.

Usage: y7_plain.py <MapCreation dir> <W> <picture to write>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
MAPS, W, WRITE_TO = sys.argv[1], float(sys.argv[2]), sys.argv[3]
coast = np.asarray(Image.open(MAPS + "/WorldMapV1.png").convert("RGB"))
land = (coast >= 250).all(axis=2)
to_land = ndimage.distance_transform_edt(~land)
picture = np.empty(coast.shape[:2] + (4,), dtype=np.uint8)
picture[...] = (181, 235, 255, 255)
picture[land] = (255, 255, 255, 255)
picture[~land & (to_land <= W)] = (0, 0, 0, 255)
Image.fromarray(picture, "RGBA").save(WRITE_TO)
print("wrote %s" % WRITE_TO)
