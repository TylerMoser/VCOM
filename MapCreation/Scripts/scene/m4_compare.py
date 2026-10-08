"""The scene as Godot draws it, set beside the picture it was made from.

Both are 3100 x 4000 with the same nine colours. Every pixel is given its colour's name; then, for
each colour, how much of the picture's lies within a pixel or two of the same colour in the drawing
and the other way about. What differs by more than that is listed by place, largest first, and
saved as a picture.

Usage: m4_compare.py <AllSimple.png> <the drawing .png> <folder to write to> [how many places to list]
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
PICTURE, DRAWING, OUT = sys.argv[1:4]
LIST = int(sys.argv[4]) if len(sys.argv) > 4 else 25
COLOURS = {"sea": (181, 235, 255), "land": (255, 255, 255), "ink": (0, 0, 0), "water": (28, 112, 224), "kingdom": (233, 0, 255),
           "duchy": (110, 30, 180), "county": (128, 128, 128), "road": (200, 40, 30), "bridge": (60, 35, 15)}
NAMES = list(COLOURS)


def classes(path):
    rgb = np.asarray(Image.open(path).convert("RGB")).astype(np.int32)
    out = np.full(rgb.shape[:2], -1, dtype=np.int8)
    best = np.full(rgb.shape[:2], 10 ** 9, dtype=np.int64)
    for i, name in enumerate(NAMES):
        c = np.array(COLOURS[name])
        d = ((rgb - c) ** 2).sum(axis=2)
        nearer = d < best
        out[nearer] = i
        best[nearer] = d[nearer]
    return out, int((best > 0).sum())


a, a_off = classes(PICTURE)
b, b_off = classes(DRAWING)
assert a.shape == b.shape, (a.shape, b.shape)
print("pixels not exactly one of the nine colours: picture %d, drawing %d" % (a_off, b_off))
print("%-8s %10s %10s   %s" % ("", "picture", "drawing", "of the picture's, the share with the same colour in the drawing within 0 / 1 / 2 px; then of the drawing's in the picture"))
three = np.ones((3, 3), dtype=bool)
far = np.zeros(a.shape, dtype=bool)
for i, name in enumerate(NAMES):
    pa, pb = a == i, b == i
    row = []
    for one, other in ((pa, pb), (pb, pa)):
        grown = other
        shares = []
        for reach in range(3):
            shares.append(100.0 * (one & grown).sum() / max(one.sum(), 1))
            grown = ndimage.binary_dilation(grown, structure=three)
        row.append(shares)
        far |= one & ~ndimage.binary_dilation(other, structure=three, iterations=2)
    print("%-8s %10d %10d   %6.2f %6.2f %6.2f     %6.2f %6.2f %6.2f" % (name, pa.sum(), pb.sum(), *row[0], *row[1]))
same = (a == b).mean() * 100.0
print("the same colour at the same pixel: %.3f%% of the map; differing by more than 2 px: %d px" % (same, far.sum()))
places, n = ndimage.label(far, structure=three)
sizes = ndimage.sum_labels(far, places, index=np.arange(1, n + 1))
order = np.argsort(-sizes)
print("places that differ by more than 2 px: %d; the largest:" % n)
for k in order[:LIST]:
    ys, xs = np.nonzero(places == k + 1)
    y, x = int(ys.mean()), int(xs.mean())
    in_a = np.bincount(a[ys, xs].astype(np.int64), minlength=len(NAMES))
    in_b = np.bincount(b[ys, xs].astype(np.int64), minlength=len(NAMES))
    print("   %4d px at (%4d, %4d): picture %s; drawing %s" % (sizes[k], x, y,
          ", ".join("%s %d" % (NAMES[j], in_a[j]) for j in np.argsort(-in_a) if in_a[j]), ", ".join("%s %d" % (NAMES[j], in_b[j]) for j in np.argsort(-in_b) if in_b[j])))
look = np.full(a.shape + (3,), 255, dtype=np.uint8)
look[a != b] = (255, 200, 120)
look[far] = (220, 0, 0)
Image.fromarray(look).save(OUT + "/differs.png")
np.save(OUT + "/far.npy", far)
print("wrote differs.png")
