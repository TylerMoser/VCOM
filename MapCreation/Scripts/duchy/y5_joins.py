"""Every place the coast crosses a join between the hand-drawn sheets: how far the land's edge
jumps there, and whether a join shows in the picture's other marks.

Usage: y5_joins.py <MapCreation dir> <folder for pictures>
"""
import pickle
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


def runs_of(flags):
    edges = np.flatnonzero(np.diff(np.concatenate([[False], flags, [False]]).astype(np.int8)))
    return [(int(a), int(b)) for a, b in zip(edges[::2], edges[1::2])]


# How much each row's land differs from the row above, in runs of 3 px or more: a join stands out.
row_jump = np.zeros(h, dtype=int)
row_places = {}
for y in range(1, h):
    found = [(a, b - a) for a, b in runs_of(land[y] != land[y - 1]) if b - a >= 3]
    row_jump[y] = sum(length for _, length in found)
    row_places[y] = found
col_jump = np.zeros(w, dtype=int)
col_places = {}
for x in range(1, w):
    found = [(a, b - a) for a, b in runs_of(land[:, x] != land[:, x - 1]) if b - a >= 3]
    col_jump[x] = sum(length for _, length in found)
    col_places[x] = found
print("rows that are a multiple of 400, and the land's edge against the row above (start x, px):")
for y in range(400, h, 400):
    print("   row %4d: %s" % (y, row_places[y]))
print("columns that are a multiple of 400:")
for x in range(400, w, 400):
    print("   column %4d: %s" % (x, col_places[x]))
# Is the jump there a jump, or a coast running along the row? Compare with how the edge moves in the rows about it.
joins = []
for y in range(400, h, 400):
    for start, length in row_places[y]:
        # the land's edge near here, 3 rows above the join and 3 below, to measure the sideways shift
        above, below = land[y - 1], land[y]
        lo, hi = max(start - 12, 0), min(start + length + 12, w)
        # which side is land: the run is land in the lower row if below[start]
        lower_has = bool(below[start])
        # shifts of the edge row to row just above and just below, for comparison
        def edge_at(row):
            cols = np.flatnonzero(land[row, lo:hi] != land[row, lo:hi][0])
            return lo + int(cols[0]) if len(cols) else None
        track = [edge_at(r) for r in range(y - 6, y + 6)]
        steps = [b - a for a, b in zip(track[:-1], track[1:]) if a is not None and b is not None]
        joins.append({"at": (start + length // 2, y), "px": length, "edge": track, "lower_has_more_land": lower_has})
        print("   join at (%d, %d): the edge jumps %d px; the edge's x in rows %d..%d: %s" % (start + length // 2, y, length, y - 6, y + 5, track))
print("places the coast crosses a join with a jump of 3 px or more: %d; jumps px: %s" % (len(joins), sorted(j["px"] for j in joins)))
# Other rows with as large a jump at a single place, which are not joins: the coast running level.
big = [(y, row_places[y]) for y in range(1, h) if y % 400 and any(length >= 6 for _, length in row_places[y])]
print("other rows with a run of 6 px or more: %d (a coast that runs level along a row gives these too)" % len(big))
# The ink at the joins: rows where the dark ink is missing right beside the land.
to_land = ndimage.distance_transform_edt(~land)
ring = ~land & (to_land > 2.0) & (to_land <= 5.0)
thin = ring & ~dark
rows_thin = thin.sum(axis=1)
worst = np.argsort(-rows_thin)[:24]
print("rows with most of the 3-to-5 px ring not dark: %s" % sorted((int(y), int(rows_thin[y])) for y in worst if rows_thin[y] > 0))
with open(LOOK + "/joins.pickle", "wb") as handle:
    pickle.dump(joins, handle)
