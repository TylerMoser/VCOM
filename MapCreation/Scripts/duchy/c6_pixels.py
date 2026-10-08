"""Print a patch of a county draft as letters: what the picture holds, the counties, the duchies.

Usage: c6_pixels.py <repo root> <duchy out dir> <tag> <picture> <x0> <y0> <x1> <y1>
"""
import pickle
import sys
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT, TAG, PICTURE = sys.argv[1:5]
x0, y0, x1, y1 = (int(v) for v in sys.argv[5:9])
saved = np.asarray(Image.open(PICTURE).convert("RGBA"))[y0:y1, x0:x1]
county = np.load(OUT + "/county_map_%s.npy" % TAG)[y0:y1, x0:x1]
with open(OUT + "/counties_%s.pickle" % TAG, "rb") as handle:
    duchy = pickle.load(handle)["duchy"][y0:y1, x0:x1]
fields = np.load(OUT + "/fields1.npz")
mainland = (fields["king"] > 0)[y0:y1, x0:x1]


def letter(pixel):
    r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])
    if (r, g, b) == (233, 0, 255):
        return "K"
    if (r, g, b) == (110, 30, 180):
        return "D"
    if (r, g, b) == (128, 128, 128):
        return "c"
    if min(r, g, b) >= 250:
        return "."
    if max(r, g, b) < 90:
        return "#"
    return "~" if b - r >= 40 else "+"


print("picture (K pink, D purple, c grey, . white, # ink, ~ sea):")
for row in saved:
    print("".join(letter(p) for p in row))
names = {int(c): chr(ord("a") + i % 26) for i, c in enumerate(np.unique(county))}
print("counties %s:" % {v: k for k, v in names.items()})
for y in range(county.shape[0]):
    print("".join(names[int(c)] if m else " " for c, m in zip(county[y], mainland[y])))
names = {int(c): chr(ord("A") + i % 26) for i, c in enumerate(np.unique(duchy))}
print("duchies %s:" % {v: k for k, v in names.items()})
for y in range(duchy.shape[0]):
    print("".join(names[int(c)] for c in duchy[y]))
