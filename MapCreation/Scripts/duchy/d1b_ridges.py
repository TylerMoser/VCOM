"""The ridges between neighbouring rivers, as lines a border can follow.

Rivers.png draws the lines between whole watersheds; inside a watershed there is as real a ridge
between each river and the next. Every land cell is filed under the drawn river it runs down to
(or, running straight to the sea or a lake, under that), and the lines between those are the
lesser ridges. They are added to the fields d1_fields.py made, as "ridge", at both sizes.

Usage: d1b_ridges.py <water out dir> <duchy out dir>
"""
import pickle
import sys
import numpy as np
from scipy import ndimage

WATER, OUT = sys.argv[1], sys.argv[2]
with open(WATER + "/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
rows, cols, to, z, sea = water["rows"], water["cols"], water["to"], water["z"], water["sea"]
n = rows.size
shape = water["lake"].shape

# Each river line's own cells; where a lesser stream ends on a greater, that cell is the greater's.
line_of = np.zeros(n, dtype=np.int64)
for number, reach in sorted(enumerate(water["reaches"], start=1), key=lambda r: len(r[1]["cells"])):
    cells = reach["cells"]
    line_of[cells if reach["end"] != "joins" else cells[:-1]] = number
lake = water["lake_flat"]
count = len(water["reaches"])
# Down from every cell to the first drawn river it reaches.
under = line_of.tolist()                                # a lake belongs to the river that drains it
to_list = to.tolist()
for i in np.argsort(z, kind="stable").tolist():            # lowest first, so the cell below is filed already
    if under[i] == 0 and to_list[i] != sea:
        under[i] = under[to_list[i]]
under = np.array(under)
filed = np.zeros(shape, dtype=np.int64)
filed[rows, cols] = under
# What runs straight to the sea: each stretch of such shore country is one more piece.
land = np.zeros(shape, dtype=bool)
land[rows, cols] = True
loose, pieces = ndimage.label((filed == 0) & land)
filed = np.where(loose > 0, count + int(lake.max()) + loose, filed)

ridge2 = np.zeros(shape, dtype=bool)
for dy, dx in ((0, 1), (1, 0)):
    a = filed[: shape[0] - dy, : shape[1] - dx]; b = filed[dy:, dx:]
    meet = (a != b) & (a > 0) & (b > 0)
    ridge2[: shape[0] - dy, : shape[1] - dx] |= meet
    ridge2[dy:, dx:] |= meet
half = dict(np.load(OUT + "/fields2.npz"))
full = dict(np.load(OUT + "/fields1.npz"))
half["ridge"] = ridge2 & ~half["river"] & ~half["lake"]
h, w = full["king"].shape
ridge1 = np.zeros((h, w), dtype=bool)
up = np.repeat(np.repeat(ridge2, 2, axis=0), 2, axis=1)
ridge1[: up.shape[0], : up.shape[1]] = up[:h, :w]
full["ridge"] = ridge1 & ~full["river"] & ~full["lake"] & (full["king"] > 0)
np.savez_compressed(OUT + "/fields2.npz", **half)
np.savez_compressed(OUT + "/fields1.npz", **full)
print("pieces of country by the river they drain to: %d; ridge cells at half size: %d (the drawn watershed lines: %d)" % (
    len(np.unique(filed)) - 1, int(half["ridge"].sum()), int(half["divide"].sum())))
