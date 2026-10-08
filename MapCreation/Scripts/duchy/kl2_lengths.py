"""How long the borders of the old kingdoms, the duchies and the counties are, measured as
kl_lengths.py measures a kingdom's: the shortest chain of cells along each stretch of border
from end to end, smoothed, and its length. A duchy border here is one between two duchies of
one kingdom, and a county border one between two counties of one duchy, as the pictures draw
them.

Usage: kl2_lengths.py <duchy out dir>
"""
import pickle
import sys
import numpy as np
from scipy import ndimage, sparse
from scipy.sparse import csgraph

OUT = sys.argv[1]
KM = 0.335
SMOOTH = 2.5
square = np.ones((3, 3), dtype=bool)


def chain_length(band):
    """The length in px of one connected stretch of border cells: its longest shortest chain, smoothed."""
    ys, xs = np.nonzero(band)
    n = len(ys)
    if n < 3:
        return float(n)
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
    far = csgraph.dijkstra(graph, directed=False, indices=[0])[0]
    one = int(np.argmax(np.where(np.isfinite(far), far, -1)))
    far, before = csgraph.dijkstra(graph, directed=False, indices=[one], return_predecessors=True)
    far, before = far[0], before[0]
    other = int(np.argmax(np.where(np.isfinite(far), far, -1)))
    chain = [other]
    while before[chain[-1]] >= 0:
        chain.append(int(before[chain[-1]]))
    points = np.column_stack([ys[chain], xs[chain]]).astype(np.float64)
    if len(points) < 8:
        return float(np.hypot(*np.diff(points, axis=0).T).sum())
    gaps = np.hypot(*np.diff(points, axis=0).T)
    along = np.concatenate([[0.0], np.cumsum(gaps)])
    even = np.linspace(0.0, along[-1], max(int(along[-1]) + 1, 2))
    points = np.column_stack([np.interp(even, along, points[:, 0]), np.interp(even, along, points[:, 1])])
    pad = min(int(4 * SMOOTH) + 1, len(points) - 1)
    whole = np.concatenate([2.0 * points[0] - points[pad:0:-1], points, 2.0 * points[-1] - points[-2: -pad - 2: -1]])
    points = ndimage.gaussian_filter1d(whole, SMOOTH, axis=0, mode="nearest")[pad: pad + len(points)]
    return float(np.hypot(*np.diff(points, axis=0).T).sum())


def borders(grid, parent, name):
    """The summed length of the borders between regions of one parent."""
    h, w = grid.shape
    pairs = set()
    for a, b in ((grid[:, :-1], grid[:, 1:]), (grid[:-1, :], grid[1:, :])):
        meet = (a != b) & (a > 0) & (b > 0)
        code = np.unique(np.minimum(a, b)[meet].astype(np.int64) * 1000 + np.maximum(a, b)[meet])
        pairs |= {(int(c // 1000), int(c % 1000)) for c in code}
    boxes = ndimage.find_objects(grid)
    total, kept, stretches = 0.0, 0, 0
    for a, b in sorted(pairs):
        if parent is not None and parent[a] != parent[b]:
            continue
        (ya, xa), (yb, xb) = boxes[a - 1], boxes[b - 1]
        box = (slice(max(min(ya.start, yb.start) - 1, 0), min(max(ya.stop, yb.stop) + 1, h)),
               slice(max(min(xa.start, xb.start) - 1, 0), min(max(xa.stop, xb.stop) + 1, w)))
        first, second = grid[box] == a, grid[box] == b
        band = (first & ndimage.binary_dilation(second, structure=square)) | (second & ndimage.binary_dilation(first, structure=square))
        parts, count = ndimage.label(band, structure=square)
        for i, piece in enumerate(ndimage.find_objects(parts), start=1):
            total += chain_length(parts[piece] == i)
            stretches += 1
        kept += 1
    print("%s: %d borders in %d stretches, %.0f km in all" % (name, kept, stretches, total * KM), flush=True)
    return total * KM


fields = np.load(OUT + "/fields1.npz")
king = fields["king"].astype(np.int32)
duchy = np.load(OUT + "/duchy_map.npy").astype(np.int32)
county = np.load(OUT + "/county_map_f3.npy").astype(np.int32)
mainland = king > 0
borders(king, None, "kingdoms (Kingdoms.png)")
kingdom_of = {int(d): int(np.bincount(king[(duchy == d) & mainland]).argmax()) for d in range(1, 45)}
borders(np.where(mainland, duchy, 0), kingdom_of, "duchies of one kingdom (the purple lines)")
duchy_of = {}
for c in range(1, 221):
    inside = (county == c) & mainland
    if inside.any():
        duchy_of[c] = int(np.bincount(duchy[inside]).argmax())
borders(np.where(mainland, county, 0), duchy_of, "counties of one duchy (the grey lines)")
