"""The land and the nine kingdoms as grids, read from the two pictures in MapCreation, at the
picture's own size and at a half and a quarter of it (the water is worked out on the coarser
ones and drawn on the full one).

Usage: w0_grids.py <repo root> <out dir>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT = sys.argv[1], sys.argv[2]
# Where each kingdom's white piece of Kingdoms.png has its middle (x, y).
MIDDLES = {1: (993, 944), 2: (1492, 691), 3: (1698, 1942), 4: (2192, 1315), 5: (2484, 2087),
           6: (582, 1454), 7: (1079, 2254), 8: (1916, 2906), 9: (2409, 3521)}

plain = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
drawn = np.asarray(Image.open(ROOT + "/MapCreation/Kingdoms.png").convert("RGBA"))
h, w = plain.shape[:2]
white = (plain[..., 0] >= 250) & (plain[..., 1] >= 250) & (plain[..., 2] >= 250)
pieces, count = ndimage.label(white)
sizes = ndimage.sum_labels(white, pieces, index=np.arange(1, count + 1))
mainland = pieces == (int(np.argmax(sizes)) + 1)
land = white

# The kingdoms: the nine pieces the pink cuts the mainland into, each then given the pink and
# the islands nearest it.
open_land = (drawn[..., 0] >= 250) & (drawn[..., 1] >= 250) & (drawn[..., 2] >= 250) & mainland
found, n = ndimage.label(open_land)
found_sizes = ndimage.sum_labels(open_land, found, index=np.arange(1, n + 1))
big = np.flatnonzero(found_sizes > 20000) + 1
if big.size != 9:
    raise SystemExit("Kingdoms.png cuts the mainland into %d pieces, not nine" % big.size)
seeds = np.zeros((h, w), dtype=np.uint8)
for k in big:
    cy, cx = ndimage.center_of_mass(found == k)
    name = min(MIDDLES, key=lambda i: (MIDDLES[i][0] - cx) ** 2 + (MIDDLES[i][1] - cy) ** 2)
    seeds[found == k] = name
if len(np.unique(seeds)) != 10:
    raise SystemExit("could not tell the nine kingdoms apart")
_, (ny, nx) = ndimage.distance_transform_edt(seeds == 0, return_indices=True)
king = np.where(land, seeds[ny, nx], 0).astype(np.uint8)
np.savez_compressed(OUT + "/grid1.npz", land=land, mainland=mainland, king=king)
print("full size %d x %d: land %d px, kingdoms %s" % (w, h, land.sum(), np.bincount(king[land], minlength=10)[1:].tolist()))

_, (ly, lx) = ndimage.distance_transform_edt(king == 0, return_indices=True)
for factor in (2, 4):
    hh, ww = h // factor, w // factor
    share = land[: hh * factor, : ww * factor].reshape(hh, factor, ww, factor).mean(axis=(1, 3))
    coarse = share >= 0.5
    cy = np.arange(hh) * factor + factor // 2
    cx = np.arange(ww) * factor + factor // 2
    gy, gx = np.meshgrid(cy, cx, indexing="ij")
    labels = king[ly[gy, gx], lx[gy, gx]]
    labels = np.where(coarse, labels, 0).astype(np.uint8)
    main_share = mainland[: hh * factor, : ww * factor].reshape(hh, factor, ww, factor).mean(axis=(1, 3))
    np.savez_compressed(OUT + "/grid%d.npz" % factor, land=coarse, mainland=coarse & (main_share >= 0.25), king=labels)
    print("1/%d size %d x %d: land %d cells (%.3f of the true area), kingdoms %s" % (
        factor, ww, hh, coarse.sum(), coarse.sum() * factor * factor / land.sum(), np.bincount(labels[coarse], minlength=10)[1:].tolist()))
