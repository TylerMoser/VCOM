"""Move the kingdoms' borders on to the land's own lines.

Each kingdom keeps its core, the land further than the band's width from its old border. The
band between is shared out afresh: a cell goes to the kingdom whose core is nearest it, where
"near" is plain distance plus a toll for every line of the land crossed on the way: a river (by
its size), a lake shore, a watershed, a ridge, a spur, a brook, and (if asked) the foot of the
high country. The tolls are large beside the distances, so the border comes to rest on those
lines nearly everywhere: where nothing greater is within reach it runs along the spurs and
brooks nearest the old line, and where a river or a watershed runs its way it takes that. Each
kingdom also has a head start, adjusted until the nine areas are near enough equal again (the
islands counted with kingdom 7, as before).

The result is tidied as it will be drawn (tidy.py), the areas evened once more as tidied, and
saved as a map of kingdoms.

Usage: k2_solve.py <duchy out dir> <kingdom out dir> <tag> [major] [spur toll] [front toll] [near enough]
"""
import sys
import time
import numpy as np
from scipy import ndimage, sparse
from scipy.sparse import csgraph

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
from tidy import tidy

OUT, KING, TAG = sys.argv[1], sys.argv[2], sys.argv[3]
MAJOR = float(sys.argv[4]) if len(sys.argv) > 4 else 3.0     # what the lines drawn on the maps count for, beside the duchies' tolls
SPUR = float(sys.argv[5]) if len(sys.argv) > 5 else 15.0     # km to cross a spur or a brook
FRONT = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0     # km to cross the foot of the high country, where it counts in full
NEAR_ENOUGH = float(sys.argv[7]) if len(sys.argv) > 7 else 0.01
LAKE, DIVIDE = 15.0 * MAJOR, 22.0 * MAJOR                    # a lake, and what a watershed adds to a ridge
RIDGE = SPUR + 10.0                                          # a ridge between two rivers
KM = 0.335
SMOOTH = 3.0

fields = np.load(OUT + "/fields1.npz")
more = np.load(KING + "/fields.npz")
king, island_king = fields["king"], fields["island_king"]
mainland = king > 0
h, w = king.shape
river, lake, divide = fields["river"], fields["lake"], fields["divide"]
ridge = fields["ridge"] | divide
spur, brook, above, weight = more["spur"], more["brook"], more["above"], more["weight"]
band, core = more["band"], more["core"]
islands_of_7 = int((island_king > 0).sum())
t0 = time.time()

# -- the band as a graph ------------------------------------------------------------------------------
square = np.ones((3, 3), dtype=bool)
rim = (core > 0) & ndimage.binary_dilation(band, structure=square)
chosen = band | rim
n = int(chosen.sum())
index = -np.ones((h, w), dtype=np.int64)
index[chosen] = np.arange(n)
rows_of, cols_of = np.nonzero(chosen)
flat = lambda grid: grid[chosen]
f_river, f_lake, f_divide, f_ridge = flat(river), flat(lake), flat(divide), flat(ridge)
f_spur, f_brook, f_above = flat(spur & ~ridge), flat(brook), flat(above)
f_weight = flat(weight).astype(np.float64)
f_cross = flat(fields["cross"]).astype(np.float64) * MAJOR
a_parts, b_parts, cost_parts = [], [], []
for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
    if dx >= 0:
        a = index[: h - dy, : w - dx]; b = index[dy:, dx:]
    else:
        a = index[: h - dy, -dx:]; b = index[dy:, : w + dx]
    both = (a >= 0) & (b >= 0)
    a, b = a[both], b[both]
    toll = 0.5 * np.where(f_river[a] != f_river[b], np.maximum(f_cross[a], f_cross[b]), 0.0)
    toll += 0.5 * LAKE * (f_lake[a] != f_lake[b]) + 0.5 * DIVIDE * (f_divide[a] != f_divide[b]) + 0.5 * RIDGE * (f_ridge[a] != f_ridge[b])
    toll += 0.5 * SPUR * ((f_spur[a] != f_spur[b]).astype(np.float64) + (f_brook[a] != f_brook[b]))
    if FRONT > 0.0:
        toll += FRONT * 0.5 * (f_weight[a] + f_weight[b]) * (f_above[a] != f_above[b])
    a_parts.append(a); b_parts.append(b); cost_parts.append(np.hypot(dy, dx) * KM + toll)
# Nine more nodes, one a kingdom, each joined to every cell of its core's rim by a link whose
# length is the head start the kingdom lacks.
rim_cells = [index[rim & (core == k)] for k in range(1, 10)]
for k, cells in enumerate(rim_cells):
    a_parts.append(np.full(cells.size, n + k)); b_parts.append(cells); cost_parts.append(np.ones(cells.size))
graph = sparse.coo_matrix((np.concatenate(cost_parts), (np.concatenate(a_parts), np.concatenate(b_parts))), shape=(n + 9, n + 9)).tocsr()
links = [slice(graph.indptr[n + k], graph.indptr[n + k + 1]) for k in range(9)]
print("the band's graph: %d cells, %d links; tolls: river %.0f to %.0f, lake %.0f, watershed %.0f, ridge %.0f, spur and brook %.0f, foot of high country %.0f  (%.0fs)" % (
    n, graph.nnz, 12 * MAJOR, 138 * MAJOR, LAKE, DIVIDE + RIDGE, RIDGE, SPUR, FRONT, time.time() - t0), flush=True)

# Cells on a line of the land are counted with the side their nearest plain cell is on.
lines = river | lake | ridge | spur | brook
plain = mainland & ~lines
_, (iy, ix) = ndimage.distance_transform_edt(~plain, return_indices=True)
on_line = band & lines
line_at = np.nonzero(on_line)
side_at = (iy[on_line], ix[on_line])
del iy, ix
base = core.astype(np.int16)


def claim(starts):
    """The kingdoms as a map (1 to 9, 0 off the mainland), given each one's head start."""
    lack = float(np.max(starts)) + 1.0 - np.asarray(starts, dtype=np.float64)
    for k in range(9):
        graph.data[links[k]] = lack[k]
    _, _, source = csgraph.dijkstra(graph, directed=False, indices=np.arange(n, n + 9), return_predecessors=True, min_only=True)
    grid = base.copy()
    grid[rows_of, cols_of] = source[:n] - n + 1
    grid[rim] = core[rim]
    grid[line_at] = grid[side_at]
    return grid


def tidied(grid):
    out = tidy(grid.astype(np.int16) - 1, mainland, 9, sigma=SMOOTH) + 1
    return np.where(core > 0, core, out).astype(np.int16)


def sizes(grid):
    size = np.bincount(grid[mainland], minlength=10)[1:].astype(np.float64)
    size[6] += islands_of_7
    return size


def shared(grid):
    length = np.zeros((9, 9))
    for dy, dx in ((0, 1), (1, 0)):
        a = grid[: h - dy, : w - dx]; b = grid[dy:, dx:]
        meet = (a != b) & (a > 0) & (b > 0)
        tally = np.bincount((a[meet] - 1) * 9 + (b[meet] - 1), minlength=81).reshape(9, 9)
        length += tally + tally.T
    return length


def even_out(starts, near_enough, tries, finish=None, step=12.0):
    best = None
    for attempt in range(tries):
        grid = claim(starts)
        if finish is not None:
            grid = finish(grid)
        size = sizes(grid)
        wanted = size.sum() / 9.0
        off = float(np.abs(size - wanted).max() / wanted)
        if best is None or off < best[2]:
            best = (starts.copy(), grid, off)
        print("  try %2d: areas within %.2f%% of a ninth; head starts %s  (%.0fs)" % (
            attempt + 1, 100 * off, np.round(starts, 1).tolist(), time.time() - t0), flush=True)
        if off < near_enough:
            break
        length = shared(grid)
        spread = np.diag(length.sum(axis=1)) - length
        # A head start moves a border the less the more tolls stand in its way: allow for them.
        push = 2.0 * np.linalg.pinv(spread) @ (wanted - size) * KM * (1.0 + SPUR / 9.0) * max(0.3, 0.93 ** attempt)
        starts = np.clip(starts + np.clip(push, -step, step), -90.0, 90.0)
        starts -= starts.mean()
    return best


starts, grid, off = even_out(np.zeros(9), NEAR_ENOUGH, 60)
print("as claimed: areas within %.2f%%" % (100 * off), flush=True)
starts, grid, off = even_out(starts, NEAR_ENOUGH, 12, finish=tidied, step=6.0)
print("as tidied: areas within %.2f%%; head starts %s" % (100 * off, np.round(starts, 1).tolist()))
size = sizes(grid) * KM * KM
print("areas, km2: %s" % np.round(size).astype(int).tolist())
moved = mainland & (grid != king)
print("land that changes kingdom: %.0f km2, %.1f%% of the mainland" % (moved.sum() * KM * KM, 100.0 * moved.sum() / mainland.sum()))
np.save(KING + "/kingdoms_%s.npy" % TAG, grid.astype(np.uint8))
np.save(KING + "/starts_%s.npy" % TAG, starts)
print("saved kingdoms_%s.npy  (%.0fs)" % (TAG, time.time() - t0))
