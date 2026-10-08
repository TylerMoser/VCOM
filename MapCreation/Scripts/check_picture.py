"""Check a kingdoms picture knowing nothing but the picture: what the pink cuts the land into."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
Image.MAX_IMAGE_PIXELS = None
picture = np.asarray(Image.open(sys.argv[1]).convert("RGBA"))
plain = np.asarray(Image.open(sys.argv[2]).convert("RGBA"))
h, w = picture.shape[:2]
print("size %d x %d, mode as saved: %s" % (w, h, Image.open(sys.argv[1]).mode))
changed = (picture != plain).any(axis=2)
colours, counts = np.unique(picture[changed].reshape(-1, 4), axis=0, return_counts=True)
print("pixels that differ from the coast map: %d, in colours %s" % (changed.sum(), [tuple(int(v) for v in c) for c in colours]))
white_plain = (plain[..., 0] >= 250) & (plain[..., 1] >= 250) & (plain[..., 2] >= 250)
print("of them, on white land %d, on the coast's ink or its soft edge %d, on sea-blue %d" % (
    (changed & white_plain).sum(), (changed & ~white_plain & (plain[..., 2].astype(int) - plain[..., 0] < 40)).sum(),
    (changed & ~white_plain & (plain[..., 2].astype(int) - plain[..., 0] >= 40)).sum()))
white = (picture[..., 0] >= 250) & (picture[..., 1] >= 250) & (picture[..., 2] >= 250)
pieces, n = ndimage.label(white)                       # four-connected: a paint bucket
sizes = ndimage.sum_labels(white, pieces, index=np.arange(1, n + 1))
order = np.argsort(-sizes)
print("white pieces: %d; the biggest:" % n)
for k in order[:12]:
    cy, cx = ndimage.center_of_mass(white, pieces, k + 1)
    print("   %8d px  centred (%4.0f, %4.0f)" % (sizes[k], cx, cy))
print("   ... and %d more, of at most %d px (the islands)" % (n - 12, sizes[order[12]] if n > 12 else 0))
land = white_plain
big = order[:9] + 1
seeds = np.zeros((h, w), dtype=np.int32)
for rank, k in enumerate(big):
    seeds[pieces == k] = rank + 1
_, (ny, nx) = ndimage.distance_transform_edt(seeds == 0, return_indices=True)
final = np.where(land, seeds[ny, nx], 0)
areas = np.bincount(final[final > 0], minlength=10)[1:]
total = land.sum()
print("with the line's own pixels and the islands shared out to the nearest piece (land %d px, a ninth %.0f):" % (total, total / 9))
for rank, a in enumerate(areas):
    cy, cx = ndimage.center_of_mass(pieces == big[rank])
    print("   piece centred (%4.0f, %4.0f): %7d px  %.3f%% of the land  %+.3f%% off a ninth" % (cx, cy, a, 100 * a / total, 100 * (a - total / 9) / (total / 9)))
