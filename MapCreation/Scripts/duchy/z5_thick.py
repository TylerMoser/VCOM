"""Places where a border's colour is a patch and not a line: in the borders' own pictures."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
Image.MAX_IMAGE_PIXELS = None
MAPS = sys.argv[1]
EIGHT = np.ones((3, 3), bool)
old = np.asarray(Image.open(MAPS + "/WorldMapV1.png").convert("RGB"))
for name, colour, wide in (("Kingdoms.png", (233, 0, 255), 5), ("Duchies.png", (110, 30, 180), 3), ("Counties.png", (128, 128, 128), 2)):
    picture = np.asarray(Image.open(MAPS + "/" + name).convert("RGB"))
    line = (picture == np.array(colour, np.uint8)).all(axis=2) & (picture != old).any(axis=2)
    size = wide + 4
    thick = ndimage.binary_opening(line, structure=np.ones((size, size), bool))
    patches, n = ndimage.label(ndimage.binary_dilation(thick, structure=EIGHT, iterations=2) & line, structure=EIGHT)
    found = []
    for i, box in enumerate(ndimage.find_objects(patches), start=1):
        mine = patches[box] == i
        ys, xs = np.nonzero(mine)
        found.append((int(mine.sum()), int(box[1].start + xs.mean()), int(box[0].start + ys.mean()), int(np.round(((box[0].start + ys.mean() + 200) % 400) - 200))))
    found.sort(reverse=True)
    print("%s: places where the %d px line's colour is a patch at least %d px across: %d" % (name, wide, size, n))
    for px, x, y, from_join in found[:20]:
        print("    %4d px about (%d, %d)%s" % (px, x, y, "   <- %d rows from a join between sheets" % from_join if abs(from_join) <= 30 else ""))
