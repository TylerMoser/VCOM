"""Where the hand-drawn sheets were joined: rows and columns at which the land's edge jumps
sideways, how far it jumps at each place the coast crosses them, and what the picture is like
along them.

Usage: y3_seams.py <MapCreation dir> <folder for pictures>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
MAPS, LOOK = sys.argv[1:3]
coast = np.asarray(Image.open(MAPS + "/WorldMapV1.png").convert("RGB"))
rgb = coast.astype(np.int32)
land = (rgb >= 250).all(axis=2)
dark = rgb.sum(axis=2) < 200
h, w = land.shape

# A row where the sheets meet: the land differs from the row above in runs several pixels long
# (the coast jumping sideways), where ordinarily it differs by a pixel or two at each crossing.
def jumps(mask, axis):
    """For each line along [axis], the runs of pixels that differ from the line before: (index, longest run, runs of 4 or more)."""
    out = []
    lines = mask if axis == 0 else mask.T
    differ = lines[1:] != lines[:-1]
    for i in range(differ.shape[0]):
        row = differ[i]
        if not row.any():
            continue
        edges = np.flatnonzero(np.diff(np.concatenate([[False], row, [False]]).astype(np.int8)))
        lengths = edges[1::2] - edges[::2]
        out.append((i + 1, int(lengths.max()), int((lengths >= 4).sum()), int(len(lengths)), [(int(a), int(b - a)) for a, b in zip(edges[::2], edges[1::2]) if b - a >= 4]))
    return out


for name, axis in (("rows", 0), ("columns", 1)):
    found = jumps(land, axis)
    # A seam shows as a line where MOST crossings jump; an ordinary line has long runs only where the coast runs along it.
    ranked = sorted(found, key=lambda f: -f[2])
    print("%s where the land's edge differs most from the line before (line, longest run, runs of 4 px or more, all runs):" % name)
    for line, longest, many, total, places in ranked[:16]:
        print("   %s %4d: longest %3d px, runs of 4 or more %2d of %2d" % ("y" if axis == 0 else "x", line, longest, many, total))
    counts = np.array([f[2] for f in found])
    print("   median over all %s: %d runs of 4 or more" % (name, np.median(counts)))

# The seam rows, then: every multiple of 400? Show what each crossing looks like in numbers.
print()
for y0 in range(400, 4000, 400):
    above, below = land[y0 - 1], land[y0]
    differ = above != below
    edges = np.flatnonzero(np.diff(np.concatenate([[False], differ, [False]]).astype(np.int8)))
    runs = [(int(a), int(b - a)) for a, b in zip(edges[::2], edges[1::2])]
    # compare with the rows two above and two below, to tell a jump from a coast that runs along the row
    quiet = [(int(a), int(b - a)) for a, b in runs if b - a >= 3]
    print("row %4d: the land's edge differs from row %d in %d places; of 3 px or more: %s" % (y0, y0 - 1, len(runs), quiet))
for x0 in range(400, 3100, 400):
    left, right = land[:, x0 - 1], land[:, x0]
    differ = left != right
    edges = np.flatnonzero(np.diff(np.concatenate([[False], differ, [False]]).astype(np.int8)))
    runs = [(int(a), int(b - a)) for a, b in zip(edges[::2], edges[1::2]) if b - a >= 3]
    print("column %4d: of 3 px or more: %s" % (x0, runs))
