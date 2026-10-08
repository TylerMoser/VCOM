"""What the other pictures draw at the places where Continent.png's land differs from WorldMapV1.png's."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
Image.MAX_IMAGE_PIXELS = None
FOLDER, CONT = sys.argv[1], sys.argv[2]
EIGHT = np.ones((3, 3), bool)
old = np.asarray(Image.open(FOLDER + "/WorldMapV1.png").convert("RGB"))
new = np.asarray(Image.open(CONT).convert("RGB"))
everything = np.asarray(Image.open(FOLDER + "/All.png").convert("RGB"))
old_land, land = (old >= 250).all(axis=2), (new == 255).all(axis=2)
differ = land != old_land
marks = (everything != old).any(axis=2)
names = {(233, 0, 255): "kingdom border (pink)", (110, 30, 180): "duchy border (purple)", (128, 128, 128): "county border (grey)", (28, 112, 224): "water", (200, 40, 30): "road", (60, 35, 15): "bridge"}
places, n = ndimage.label(ndimage.binary_dilation(differ, structure=EIGHT, iterations=6), structure=EIGHT)
for i in range(1, n + 1):
    here = places == i
    ys, xs = np.nonzero(here & differ)
    on = marks & differ & here
    near = marks & ndimage.binary_dilation(differ & here, structure=EIGHT, iterations=3)
    kinds = {}
    for colour, name in names.items():
        count = int(((everything == colour).all(axis=2) & near).sum())
        if count:
            kinds[name] = count
    on_kinds = {}
    for colour, name in names.items():
        count = int(((everything == colour).all(axis=2) & on).sum())
        if count:
            on_kinds[name] = count
    print("join about (%d, %d): land changed %d px; other pictures' marks on those very pixels: %s; within 3 px: %s" % (xs.mean(), ys.mean(), len(xs), on_kinds or "none", kinds or "none"))
