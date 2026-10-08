"""What the county step has to work with: the islands, the greys already in Duchies.png, the
duchies' sizes, what the water run kept, and how many processors there are.

Usage: c0_look.py <repo root> <water out dir> <duchy out dir>
"""
import os
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, WATER, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
KM2 = 0.335 * 0.335
print("processors:", os.cpu_count())

duchy = np.load(OUT + "/duchy_map.npy")
fields = np.load(OUT + "/fields1.npz")
print("fields:", {name: (fields[name].dtype.str, fields[name].shape) for name in fields.files})
mainland = fields["king"] > 0
land = duchy > 0
print("land %d px, mainland %d px, islands %d px" % (land.sum(), mainland.sum(), (land & ~mainland).sum()))
print("mainland cells with no duchy: %d; duchy cells off the land: %d" % ((mainland & (duchy == 0)).sum(), ((duchy > 0) & ~land).sum()))

islands = land & ~mainland
pieces, n = ndimage.label(islands, structure=np.ones((3, 3)))
print("islands: %d" % n)
for i in range(1, n + 1):
    mine = pieces == i
    ys, xs = np.nonzero(mine)
    shares = np.bincount(duchy[mine])
    print("  island %2d: %6d px = %5.0f km2, middle (%d, %d), duchies %s" % (
        i, mine.sum(), mine.sum() * KM2, xs.mean(), ys.mean(), {int(d): int(c) for d, c in enumerate(shares) if c}))

with open(OUT + "/duchies_all.pickle", "rb") as handle:
    duchies = pickle.load(handle)
number = 0
for k in sorted(duchies):
    for seat in duchies[k]["seats"]:
        number += 1
        mine = duchy == number
        inside = bool(mine[seat[1], seat[0]])
        print("duchy %2d (kingdom %d): %6.0f km2, of it islands %5.0f; seat %s %s; /3150 = %.2f" % (
            number, k, mine.sum() * KM2, (mine & islands).sum() * KM2, seat, "" if inside else "NOT INSIDE IT", mine.sum() * KM2 / 3150.0))

picture = np.asarray(Image.open(ROOT + "/MapCreation/Duchies.png").convert("RGBA"))
grey = (picture[..., 0] == picture[..., 1]) & (picture[..., 1] == picture[..., 2])
levels = np.bincount(picture[..., 0][grey], minlength=256)
print("grey pixels in Duchies.png by level (level: count), 90 to 170:")
print("  " + ", ".join("%d: %d" % (v, levels[v]) for v in range(90, 171)))
print("levels never used: %s" % [v for v in range(256) if levels[v] == 0][:80])
print("alpha values: %s" % np.unique(picture[..., 3]).tolist())

with open(WATER + "/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
for key, value in water.items():
    if isinstance(value, np.ndarray):
        print("water[%r]: array %s %s" % (key, value.dtype, value.shape))
    elif isinstance(value, (list, tuple)):
        first = value[0] if len(value) else None
        print("water[%r]: %s of %d, first %s" % (key, type(value).__name__, len(value),
              ({k: (type(v).__name__, getattr(v, "shape", v if not hasattr(v, "__len__") else len(v))) for k, v in first.items()} if isinstance(first, dict) else type(first).__name__)))
    else:
        print("water[%r]: %r" % (key, value))
