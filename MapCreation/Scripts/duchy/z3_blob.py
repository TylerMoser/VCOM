"""The purple patch where a duchy border meets the coast at the join (2686, 2400): what the
duchies' own map says is there, pixel by pixel.

Usage: z3_blob.py <MapCreation dir> <duchy out dir> <picture to look at> x0 y0 w h
"""
import pickle
import sys
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
MAPS, OUT, NAME = sys.argv[1:4]
x0, y0, w, h = (int(v) for v in sys.argv[4:8])
old = np.asarray(Image.open(MAPS + "/WorldMapV1.png").convert("RGB")).astype(int)
cont = np.asarray(Image.open(MAPS + "/Continent.png").convert("RGB")).astype(int)
picture = np.asarray(Image.open(NAME).convert("RGB")).astype(int)
old_land = (old >= 250).all(axis=2)
new_land = (cont == 255).all(axis=2)
duchy = np.load(OUT + "/duchy_map.npy")
with open(OUT + "/counties_f3.pickle", "rb") as handle:
    solved = pickle.load(handle)
duchy2 = solved["duchy"]
county = np.load(OUT + "/county_map_f3.npy")
letters = {}


def letter(value):
    if value == 0:
        return " "
    if value not in letters:
        letters[value] = "abcdefghijklmnop"[len(letters)]
    return letters[value]


print("the duchies' map (letters; blank is not land), with * where the picture is purple:")
print("     " + "".join(str((x // 10) % 10) for x in range(x0, x0 + w)))
print("     " + "".join(str(x % 10) for x in range(x0, x0 + w)))
for y in range(y0, y0 + h):
    row = ""
    for x in range(x0, x0 + w):
        purple = tuple(picture[y, x]) == (110, 30, 180)
        row += "*" if purple else letter(int(duchy2[y, x]))
    print("%4d %s" % (y, row))
print("duchies by letter: %s" % {v: k for k, v in letters.items()})
print()
print("the land: . old and new, + new only (added), - old only (taken away), blank neither; P where the picture is purple on land, p where purple off the old land")
for y in range(y0, y0 + h):
    row = ""
    for x in range(x0, x0 + w):
        purple = tuple(picture[y, x]) == (110, 30, 180)
        o, n = old_land[y, x], new_land[y, x]
        row += ("P" if o else "p") if purple else "." if o and n else "+" if n else "-" if o else " "
    print("%4d %s" % (y, row))
