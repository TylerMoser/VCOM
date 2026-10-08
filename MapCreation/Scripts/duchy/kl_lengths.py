"""How long each border between two kingdoms is, old and new, measured one way: the shortest
chain of cells along the border from end to end, smoothed as the new lines were, and its length.

Usage: kl_lengths.py <duchy out dir> <kingdom fields dir> <tag>
"""
import sys
import numpy as np
from scipy import ndimage, sparse
from scipy.sparse import csgraph

OUT, KING, TAG = sys.argv[1:4]
KM = 0.335
SMOOTH = 2.5
old = np.load(OUT + "/fields1.npz")["king"].astype(np.int16)
new = np.load(KING + "/kingdoms_%s.npy" % TAG).astype(np.int16)
h, w = old.shape
square = np.ones((3, 3), dtype=bool)


def length_of(grid, a, b):
    """The length, in km, of the border between kingdoms a and b."""
    first, second = grid == a, grid == b
    rows = np.flatnonzero((first | second).any(axis=1)); cols = np.flatnonzero((first | second).any(axis=0))
    box = (slice(rows[0], rows[-1] + 1), slice(cols[0], cols[-1] + 1))
    first, second = first[box], second[box]
    band = (first & ndimage.binary_dilation(second, structure=square)) | (second & ndimage.binary_dilation(first, structure=square))
    parts, count = ndimage.label(band, structure=square)
    if count > 1:
        band = parts == int(np.argmax(np.bincount(parts.ravel())[1:])) + 1
    ys, xs = np.nonzero(band)
    n = len(ys)
    index = -np.ones(band.shape, dtype=np.int64)
    index[ys, xs] = np.arange(n)
    rows_a, rows_b, lengths = [], [], []
    zh, zw = band.shape
    for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
        ya, yb = slice(0, zh - dy), slice(dy, zh)
        xa, xb = (slice(0, zw - dx), slice(dx, zw)) if dx >= 0 else (slice(-dx, zw), slice(0, zw + dx))
        ia, ib = index[ya, xa], index[yb, xb]
        ok = (ia >= 0) & (ib >= 0)
        rows_a.append(ia[ok]); rows_b.append(ib[ok]); lengths.append(np.full(int(ok.sum()), np.hypot(dy, dx)))
    graph = sparse.coo_matrix((np.concatenate(lengths), (np.concatenate(rows_a), np.concatenate(rows_b))), shape=(n, n)).tocsr()
    # The two ends: the cell furthest from any cell, then the cell furthest from that.
    far = csgraph.dijkstra(graph, directed=False, indices=[0])[0]
    one = int(np.argmax(np.where(np.isfinite(far), far, -1)))
    far, before = csgraph.dijkstra(graph, directed=False, indices=[one], return_predecessors=True)
    far, before = far[0], before[0]
    other = int(np.argmax(np.where(np.isfinite(far), far, -1)))
    chain = [other]
    while before[chain[-1]] >= 0:
        chain.append(int(before[chain[-1]]))
    points = np.column_stack([ys[chain], xs[chain]]).astype(np.float64)
    gaps = np.hypot(*np.diff(points, axis=0).T)
    along = np.concatenate([[0.0], np.cumsum(gaps)])
    even = np.linspace(0.0, along[-1], max(int(along[-1]) + 1, 2))
    points = np.column_stack([np.interp(even, along, points[:, 0]), np.interp(even, along, points[:, 1])])
    pad = min(int(4 * SMOOTH) + 1, len(points) - 1)
    whole = np.concatenate([2.0 * points[0] - points[pad:0:-1], points, 2.0 * points[-1] - points[-2: -pad - 2: -1]])
    points = ndimage.gaussian_filter1d(whole, SMOOTH, axis=0, mode="nearest")[pad: pad + len(points)]
    return float(np.hypot(*np.diff(points, axis=0).T).sum()) * KM


pairs = sorted({(int(min(a, b)), int(max(a, b))) for a, b in zip(old[:, :-1][old[:, :-1] != old[:, 1:]], old[:, 1:][old[:, :-1] != old[:, 1:]]) if a > 0 and b > 0}
               | {(int(min(a, b)), int(max(a, b))) for a, b in zip(old[:-1, :][old[:-1, :] != old[1:, :]], old[1:, :][old[:-1, :] != old[1:, :]]) if a > 0 and b > 0})
total_old = total_new = 0.0
print("border: old km, new km")
for a, b in pairs:
    was, now = length_of(old, a, b), length_of(new, a, b)
    total_old += was; total_new += now
    print("  %d|%d: %4.0f  %4.0f" % (a, b, was, now))
print("  all: %4.0f  %4.0f  (the new %.0f%% longer)" % (total_old, total_new, 100 * (total_new / total_old - 1)))
