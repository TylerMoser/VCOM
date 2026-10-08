"""The kingdoms' new borders, each the cheapest line through its zone.

A border is paid for by the pixel: least along a river (the bigger the cheaper), a watershed or
a ridge between rivers, more along a spur or a brook, most over open ground (less there along
its small crests and hollows); and everywhere more the further it strays from the old border,
steeply so over the band's last fifth. So a border runs along whatever line of the land goes
its way, for as far as that line does, and cuts across to the next by the shortest way. Where
three kingdoms meet, the meeting place is put where the three borders that reach it cost least
together. Each end at the coast is wherever on that stretch of coast is cheapest to reach.

(`across` above nought makes a line of the land cheap only while it runs the old border's way.
Tried and left off: it brought the sketch's smooth lines back.)

Kingdoms2.png was made with the defaults and `spare=0.0025`, on a network of band 30, join 22.

To keep the nine areas near equal, a border has a pressure every SECTION km along it, which
makes it cheaper on one side than the other there. A kingdom with one border has that border
set first, by its own area alone. Then the other pressures are taken one at a time, those of
the border between the two kingdoms furthest out of balance first, and moved a step if that
brings the nine areas nearer equal (the islands counted with kingdom 7, as before). Last, any
pressure that moves no border is taken off again.

Usage: kb2_paths.py <duchy out dir> <kingdom fields dir> <network dir> <tag> [name=value ...]
"""
import pickle
import sys
import time
import numpy as np
from scipy import ndimage, sparse
from scipy.sparse import csgraph

OUT, KING, NET, TAG = sys.argv[1:5]
options = dict(arg.split("=", 1) for arg in sys.argv[5:])
PULL = float(options.get("pull", 1.5))            # how much dearer a border is at the band's edge than on the old line
NEAR_ENOUGH = float(options.get("near", 0.01))
FINE = float(options.get("fine", 0.62))           # a spur or a brook, against 1 for open ground
RIDGE = float(options.get("ridge", 0.42))
DIVIDE = float(options.get("divide", 0.24))
LAKE = float(options.get("lake", 0.50))
FOOT = float(options.get("foot", 1.0))            # the foot of the high country: 1 leaves it out, since it is the old line again
RIVER = float(options.get("river", 0.30))         # the smallest river drawn
BIG = float(options.get("big", 0.12))             # a river eight pixels wide or more
ROUGH = float(options.get("rough", 0.40))         # how much cheaper open ground is along its small crests and hollows
CREASE = float(options.get("crease", 2.5))        # px across which those are looked for
ACROSS = float(options.get("across", 0.0))        # how much of a line's cheapness is lost across the border's way
KERB = float(options.get("kerb", 6.0))            # how much dearer still at the very edge of the band, over its last fifth
TREND = float(options.get("trend", 20.0))         # px the border's way is smoothed over
EVEN = int(options.get("even", 1))
LIMIT = float(options.get("limit", 1.0))          # the most pressure: more, and a border runs along its band's edge
SECTION = float(options.get("section", 40.0))     # km between the places a border's pressure is set
SPARE = float(options.get("spare", 0.0))          # how far from a ninth a kingdom may be left for the sake of less pressure
SMALLEST = 0.02
SMOOTH = 2.5
KM = 0.335
DIRS = ((0, 1), (1, 0), (1, 1), (1, -1), (1, 2), (2, 1), (1, -2), (2, -1))
BETWEEN = {(1, 2): ((0, 1), (1, 1)), (2, 1): ((1, 0), (1, 1)), (1, -2): ((0, -1), (1, -1)), (2, -1): ((1, 0), (1, -1))}
print("options: pull %.2f, kerb %.1f, fine %.2f, ridge %.2f, watershed %.2f, lake %.2f, foot %.2f, river %.2f to %.2f, rough %.2f over %.1f px, across %.2f, limit %.2f, section %.0f km" % (
    PULL, KERB, FINE, RIDGE, DIVIDE, LAKE, FOOT, RIVER, BIG, ROUGH, CREASE, ACROSS, LIMIT, SECTION), flush=True)

fields = np.load(OUT + "/fields1.npz")
more = np.load(KING + "/fields.npz")
near = np.load(NET + "/near.npz")
with open(NET + "/network.pickle", "rb") as handle:
    network = pickle.load(handle)
segments, joins, landings, BAND = network["segments"], network["joins"], network["landings"], network["band"]
king, island_king = fields["king"], fields["island_king"]
mainland = king > 0
h, w = king.shape
river, lake, divide = fields["river"], fields["lake"], fields["divide"]
ridge = fields["ridge"] | divide
core = more["core"]
away = near["away"]
islands_of_7 = int((island_king > 0).sum())
t0 = time.time()

# -- what a pixel of border costs -----------------------------------------------------------------------
# Open ground is not all one: a line over it keeps to the small crests and hollows of the land,
# so it is never ruled. The sea is levelled with the shore first, or the coast would be a crease.
height = fields["height"].astype(np.float32)
_, (iy, ix) = ndimage.distance_transform_edt(~mainland, return_indices=True)
crease = ndimage.gaussian_laplace(height[iy, ix], CREASE)
level = np.sqrt(ndimage.gaussian_filter(crease ** 2, 40.0)) + 1e-6
crease = np.clip(np.abs(crease) / level, 0.0, 3.0)
base = np.exp(ROUGH * (0.8 - crease)).astype(np.float32)
del height, iy, ix, level
line = np.zeros((h, w), dtype=bool)                          # cells on a line of the land, cheap only along the border's way
if FOOT < 1.0:
    above, weight = more["above"], more["weight"]
    foot = np.zeros((h, w), dtype=bool)
    for dy, dx in ((0, 1), (1, 0)):
        meet = (above[: h - dy, : w - dx] != above[dy:, dx:]) & (weight[: h - dy, : w - dx] > 0.3)
        foot[: h - dy, : w - dx] |= meet
        foot[dy:, dx:] |= meet
    base[foot] = FOOT; line |= foot
for mask, value in ((more["spur"] | more["brook"], FINE), (ridge, RIDGE), (divide, DIVIDE)):
    base[mask] = value; line |= mask
base[lake] = LAKE; line[lake] = False
half = ndimage.distance_transform_edt(river)
wide = np.clip(2.0 * ndimage.maximum_filter(half, size=11), 2.0, 12.0)
base[river] = np.clip(RIVER - (RIVER - BIG) / 6.0 * (wide[river] - 2.0), BIG, RIVER); line |= river
gap = (np.where(line, np.maximum(1.0 - base, 0.0), 0.0) * ACROSS).astype(np.float32)
reach = np.minimum(away, BAND) / BAND
pull = (1.0 + PULL * reach ** 2 + KERB * np.clip((reach - 0.8) / 0.2, 0.0, 1.0) ** 2).astype(np.float32)
del crease, half, wide

# A cell deep in each kingdom's core, to tell the pieces the borders cut the land into.
depth = ndimage.distance_transform_edt(core > 0)
deep = ndimage.maximum_position(depth, core, index=np.arange(1, 10))
deep_y = np.array([int(p[0]) for p in deep]); deep_x = np.array([int(p[1]) for p in deep])
del depth


class Zone:
    """One border's zone as a graph: steps to the 8 cells round a cell and the 8 a knight's
    move away, each costing its length times the cost of the ground it passes over."""

    def __init__(self, segment):
        self.box = segment["box"]
        mask = segment["zone"]
        self.mask = mask
        zh, zw = mask.shape
        self.n = n = int(mask.sum())
        self.index = -np.ones((zh, zw), dtype=np.int64)
        self.index[mask] = np.arange(n)
        self.ys, self.xs = np.nonzero(mask)
        a_parts, b_parts, m1_parts, m2_parts, length_parts, way_y, way_x = [], [], [], [], [], [], []
        for dy, dx in DIRS:
            ya, yb = slice(0, zh - dy), slice(dy, zh)
            xa, xb = (slice(0, zw - dx), slice(dx, zw)) if dx >= 0 else (slice(-dx, zw), slice(0, zw + dx))
            ia, ib = self.index[ya, xa], self.index[yb, xb]
            ok = (ia >= 0) & (ib >= 0)
            if (dy, dx) in BETWEEN:
                (my1, mx1), (my2, mx2) = BETWEEN[(dy, dx)]
                im1 = self.index[slice(my1, zh - dy + my1), slice(xa.start + mx1, xa.stop + mx1)]
                im2 = self.index[slice(my2, zh - dy + my2), slice(xa.start + mx2, xa.stop + mx2)]
                ok &= (im1 >= 0) & (im2 >= 0)
            else:
                im1, im2 = ia, ib
            count = int(ok.sum())
            a_parts.append(ia[ok]); b_parts.append(ib[ok]); m1_parts.append(im1[ok]); m2_parts.append(im2[ok])
            length_parts.append(np.full(count, np.hypot(dy, dx)))
            way_y.append(np.full(count, dy / np.hypot(dy, dx), dtype=np.float32))
            way_x.append(np.full(count, dx / np.hypot(dy, dx), dtype=np.float32))
        self.a, self.b = np.concatenate(a_parts), np.concatenate(b_parts)
        self.m1, self.m2, self.length = np.concatenate(m1_parts), np.concatenate(m2_parts), np.concatenate(length_parts)
        self.way_y, self.way_x = np.concatenate(way_y), np.concatenate(way_x)
        graph = sparse.coo_matrix((np.arange(1, self.a.size + 1, dtype=np.float64), (self.a, self.b)), shape=(n, n)).tocsr()
        self.order = graph.data.astype(np.int64) - 1
        self.graph = graph
        window = (self.box[0], self.box[1])
        old = king[window][mask]
        self.side = np.where(old == segment["b"], 1.0, np.where(old == segment["a"], -1.0, 0.0))
        self.reach = reach[window][mask].astype(np.float64)
        self.base = base[window][mask].astype(np.float64)
        self.gap = gap[window][mask].astype(np.float64)
        self.pull = pull[window][mask].astype(np.float64)

    def node(self, y, x):
        return int(self.index[y - self.box[0].start, x - self.box[1].start])

    def nearest(self, y, x):
        """The zone's cell nearest a place, as a node."""
        return int(np.argmin((self.ys + self.box[0].start - y) ** 2 + (self.xs + self.box[1].start - x) ** 2))

    def nodes(self, cells):
        return self.index[cells[:, 0] - self.box[0].start, cells[:, 1] - self.box[1].start]

    def measure(self, first, last):
        """How far along the border each cell is, by the shortest way through the zone from its
        first end; the places along it where its pressure is set; and how far across the
        border's way each step goes."""
        self.graph.data = self.length[self.order].astype(np.float64)
        along = csgraph.dijkstra(self.graph, directed=False, indices=[first], min_only=True)
        along[~np.isfinite(along)] = along[np.isfinite(along)].max()
        self.along = along
        whole = float(along[last])
        self.knots = np.linspace(0.0, whole, max(2, int(round(whole * KM / SECTION)) + 1))
        grid = np.zeros(self.mask.shape, dtype=np.float32)
        grid[self.mask] = along
        _, (iy, ix) = ndimage.distance_transform_edt(~self.mask, return_indices=True)
        gy, gx = np.gradient(grid[iy, ix])
        inside = self.mask.astype(np.float32)
        norm = np.maximum(ndimage.gaussian_filter(inside, TREND), 1e-6)
        gy = ndimage.gaussian_filter(np.where(self.mask, gy, 0.0).astype(np.float32), TREND) / norm
        gx = ndimage.gaussian_filter(np.where(self.mask, gx, 0.0).astype(np.float32), TREND) / norm
        size = np.maximum(np.hypot(gy, gx), 1e-6)
        ty, tx = (gy / size)[self.mask], (gx / size)[self.mask]
        self.trend = (ty, tx)
        with_it = self.way_y * ty[self.a] + self.way_x * tx[self.a]
        self.across = (1.0 - with_it ** 2).astype(np.float64)
        del self.way_y, self.way_x

    def spread(self, pressure, sources):
        """Cost of the cheapest border from the sources to every cell, and the way back."""
        here = np.interp(self.along, self.knots, pressure)
        tilt = self.pull * np.exp(-here * self.side * self.reach)
        plain, more_across = self.base * tilt, self.gap * tilt
        a, b, m1, m2 = self.a, self.b, self.m1, self.m2
        ground = plain[a] + plain[b] + plain[m1] + plain[m2] + self.across * (more_across[a] + more_across[b] + more_across[m1] + more_across[m2])
        self.graph.data = (self.length * 0.25 * ground)[self.order]
        far, before, _ = csgraph.dijkstra(self.graph, directed=False, indices=np.atleast_1d(sources), return_predecessors=True, min_only=True)
        return far, before

    def way(self, before, node):
        """The cells from a node back to the source it was reached from, as (y, x) of the picture."""
        out = [node]
        while before[out[-1]] >= 0:
            out.append(int(before[out[-1]]))
        out = np.array(out)
        return np.column_stack([self.ys[out] + self.box[0].start, self.xs[out] + self.box[1].start])


def old_place(end):
    kind, number = end
    return joins[number]["at"] if kind == "join" else landings[number]["at"]


zones = [Zone(segment) for segment in segments]
for zone, segment in zip(zones, segments):
    first, second = segment["ends"]
    zone.measure(zone.nearest(*old_place(first)), zone.nearest(*old_place(second)))
at = [tuple(join["at"]) for join in joins]                # where each meeting place is now
yy, xx = np.mgrid[0:h, 0:w]
discs = []
for join in joins:
    y, x = join["at"]
    discs.append(np.argwhere(mainland & (np.hypot(yy - y, xx - x) * KM <= network["join"])))
del yy, xx
at_join = [[i for i, s in enumerate(segments) if ("join", j) in s["ends"]] for j in range(len(joins))]
push = [np.zeros(len(zone.knots)) for zone in zones]     # each border's pressures: above nought its lesser kingdom gains ground
calls = {"lines": 0, "areas": 0}
print("zones ready: %d cells in all; pressures to set: %d  (%.0fs)" % (sum(z.n for z in zones), sum(len(p) for p in push), time.time() - t0), flush=True)


def source_of(i, end):
    kind, number = end
    if kind == "join":
        return np.array([zones[i].node(*at[number])])
    return zones[i].nodes(segments[i]["shores"][number])


def place_meetings():
    """Put each meeting place where the three borders that reach it cost least together."""
    for j in range(len(joins)):
        total = np.zeros(len(discs[j]))
        for i in at_join[j]:
            other = [e for e in segments[i]["ends"] if e != ("join", j)][0]
            far, _ = zones[i].spread(push[i], source_of(i, other))
            total += far[zones[i].nodes(discs[j])]
        at[j] = tuple(int(v) for v in discs[j][int(np.argmin(total))])


def line_of(i):
    """One border's line, as cells."""
    calls["lines"] += 1
    first, second = segments[i]["ends"]
    if first[0] != "join":                                   # start from a meeting place if the border has one
        first, second = second, first
    far, before = zones[i].spread(push[i], source_of(i, first))
    goal = source_of(i, second)
    return zones[i].way(before, int(goal[int(np.argmin(far[goal]))]))


def same(one, other):
    return len(one) == len(other) and bool((one == other).all())


def walls_of(lines):
    wall = np.zeros((h, w), dtype=bool)
    for cells in lines:
        wall[cells[:, 0], cells[:, 1]] = True
        jump = np.abs(np.diff(cells, axis=0)).max(axis=1) > 1
        if jump.any():                                       # a knight's move: fill the cell between
            mid = (cells[:-1][jump] + cells[1:][jump]) // 2
            wall[mid[:, 0], mid[:, 1]] = True
    return wall


def quick_sizes(lines):
    """The nine areas in pixels, each border's own cells shared between its two sides; None if
    the borders do not part the nine cores."""
    calls["areas"] += 1
    wall = walls_of(lines)
    parts, count = ndimage.label(mainland & ~wall)
    mine = parts[deep_y, deep_x]
    if (mine == 0).any() or len(set(mine.tolist())) < 9:
        return None
    area = np.bincount(parts.ravel(), minlength=count + 1)
    size = area[mine].astype(np.float64)
    for cells, segment in zip(lines, segments):
        size[segment["a"] - 1] += 0.5 * len(cells)
        size[segment["b"] - 1] += 0.5 * len(cells)
    size[6] += islands_of_7
    return size


def kingdoms_of(wall):
    """The kingdoms as a map, 1 to 9, from the borders as walls; None if they do not hold."""
    parts, count = ndimage.label(mainland & ~wall)
    mine = parts[deep_y, deep_x]
    if (mine == 0).any() or len(set(mine.tolist())) < 9:
        return None
    held = np.zeros(count + 1, dtype=np.int16)
    held[mine] = np.arange(1, 10)
    grid = held[parts]
    _, (iy, ix) = ndimage.distance_transform_edt(grid == 0, return_indices=True)
    return np.where(mainland, grid[iy, ix], 0).astype(np.int16)


def sizes(grid):
    size = np.bincount(grid[mainland], minlength=10)[1:].astype(np.float64)
    size[6] += islands_of_7
    return size


def uneven(lines):
    size = quick_sizes(lines)
    if size is None:
        return None
    return (size - size.mean()) / size.mean()


def even_out(lines, movable, lean_of, score, enough, rounds, name):
    """Move one pressure at a time, while that brings the score down."""
    out = uneven(lines)
    steps = {i: np.full(len(push[i]), 0.3) for i in movable}
    order_of = np.random.default_rng(7)
    for turn in range(rounds):
        if score(out) < enough:
            break
        waiting = []
        for i in movable:
            lean = lean_of(i, out)
            if lean != 0.0:
                waiting += [(-abs(lean), order_of.random(), i, k, lean) for k in range(len(push[i])) if steps[i][k] >= SMALLEST]
        better = False
        for _, _, i, k, lean in sorted(waiting):
            was, old = push[i][k], lines[i]
            now = float(np.clip(was - np.sign(lean) * steps[i][k], -LIMIT, LIMIT))
            if now == was:
                steps[i][k] = 0.0
                continue
            push[i][k] = now
            new = line_of(i)
            if same(new, old):
                continue                                     # the border did not move: keep the pressure and go on
            lines[i] = new
            trial = uneven(lines)
            if trial is not None and score(trial) < score(out) - 1e-12:
                out = trial
                steps[i][k] = min(steps[i][k] * 1.25, 0.4)
                better = True
                break
            push[i][k], lines[i] = was, old
            steps[i][k] *= 0.5
        if turn % 10 == 0 or not better:
            print("    %s, turn %3d: areas within %.2f%% of a ninth: %s; %d lines laid, %d areas taken  (%.0fs)" % (
                name, turn, 100 * np.abs(out).max(), np.round(100 * out, 1).tolist(), calls["lines"], calls["areas"], time.time() - t0), flush=True)
        if not better:
            break
    return out


def ease(lines):
    """Take off, or halve, every pressure that can go without moving its border."""
    eased = 0
    for i in range(len(segments)):
        for k in range(len(push[i])):
            was = push[i][k]
            if was == 0.0:
                continue
            for lighter in (0.0, 0.5 * was):
                push[i][k] = lighter
                if same(line_of(i), lines[i]):
                    eased += 1
                    break
                push[i][k] = was
    return eased


def spare(lines, most):
    """Take off, or halve, every pressure the areas can do without: the heaviest first, each
    going if every kingdom is still within `most` of a ninth without it."""
    out = uneven(lines)
    spared = 0
    for sweep in range(3):
        moved = False
        heaviest = sorted(((abs(push[i][k]), i, k) for i in range(len(segments)) for k in range(len(push[i])) if push[i][k] != 0.0), reverse=True)
        for _, i, k in heaviest:
            was, old = push[i][k], lines[i]
            for lighter in (0.0, 0.5 * was):
                push[i][k] = lighter
                new = line_of(i)
                if same(new, old):
                    spared += 1
                    break
                lines[i] = new
                trial = uneven(lines)
                if trial is not None and np.abs(trial).max() <= most:
                    out = trial
                    spared += 1
                    moved = True
                    break
                lines[i] = old
                push[i][k] = was
        print("    sparing, sweep %d: %d pressures taken off or halved so far; areas within %.2f%%  (%.0fs)" % (
            sweep + 1, spared, 100 * np.abs(out).max(), time.time() - t0), flush=True)
        if not moved:
            break
    return out, spared


for sweep in range(3):
    place_meetings()
lines = [line_of(i) for i in range(len(segments))]
out = uneven(lines)
if out is None:
    raise SystemExit("the borders do not close the kingdoms off")
print("with no pressure: areas within %.2f%% of a ninth: %s; meeting places %s  (%.0fs)" % (
    100 * np.abs(out).max(), np.round(100 * out, 1).tolist(), [a[::-1] for a in at], time.time() - t0), flush=True)
if EVEN:
    borders_of = {k: [i for i, s in enumerate(segments) if k in (s["a"], s["b"])] for k in range(1, 10)}
    settled = []
    for k, mine in borders_of.items():
        if len(mine) == 1:                                   # a kingdom with one border: that border alone sets its area
            i = mine[0]
            sign = 1.0 if segments[i]["a"] == k else -1.0
            out = even_out(lines, [i], lambda _, o, k=k, sign=sign: sign * o[k - 1], lambda o, k=k: o[k - 1] ** 2, (0.4 * NEAR_ENOUGH) ** 2, 200, "kingdom %d" % k)
            settled.append(i)
            print("kingdom %d set by its one border: %.2f%% from a ninth  (%.0fs)" % (k, 100 * out[k - 1], time.time() - t0), flush=True)
    rest = [i for i in range(len(segments)) if i not in settled]
    out = even_out(lines, rest, lambda i, o: o[segments[i]["a"] - 1] - o[segments[i]["b"] - 1], lambda o: float((o ** 2).sum()), 0.0, 600, "all")
    print("evened: areas within %.2f%%: %s  (%.0fs)" % (100 * np.abs(out).max(), np.round(100 * out, 2).tolist(), time.time() - t0), flush=True)
    print("pressures eased without moving a border: %d  (%.0fs)" % (ease(lines), time.time() - t0), flush=True)
    if SPARE > 0.0:
        heavy = sum(float(np.abs(p).sum()) for p in push)
        out, spared = spare(lines, SPARE)
        print("pressures the areas could spare: %d; pressure in all %.1f, was %.1f; areas within %.2f%%: %s  (%.0fs)" % (
            spared, sum(float(np.abs(p).sum()) for p in push), heavy, 100 * np.abs(out).max(), np.round(100 * out, 2).tolist(), time.time() - t0), flush=True)
print("kept: areas within %.2f%%; %d lines laid, %d areas taken  (%.0fs)" % (100 * np.abs(out).max(), calls["lines"], calls["areas"], time.time() - t0), flush=True)
for segment, p in zip(segments, push):
    print("  border %d|%d: pressures %s" % (segment["a"], segment["b"], np.round(p, 2).tolist()))


def smoothed(cells, sigma):
    points = cells.astype(np.float64)
    gaps = np.hypot(*np.diff(points, axis=0).T)
    along = np.concatenate([[0.0], np.cumsum(gaps)])
    even = np.linspace(0.0, along[-1], max(int(along[-1]) + 1, 2))
    points = np.column_stack([np.interp(even, along, points[:, 0]), np.interp(even, along, points[:, 1])])
    if sigma > 0 and len(points) > 6:
        pad = min(int(4 * sigma) + 1, len(points) - 1)
        whole = np.concatenate([2.0 * points[0] - points[pad:0:-1], points, 2.0 * points[-1] - points[-2: -pad - 2: -1]])
        points = ndimage.gaussian_filter1d(whole, sigma, axis=0, mode="nearest")[pad: pad + len(points)]
    gaps = np.hypot(*np.diff(points, axis=0).T)
    along = np.concatenate([[0.0], np.cumsum(gaps)])
    fine = np.linspace(0.0, along[-1], max(int(along[-1] / 0.5) + 1, 2))
    cells = np.round(np.column_stack([np.interp(fine, along, points[:, 0]), np.interp(fine, along, points[:, 1])])).astype(np.int64)
    cells = cells[np.concatenate([[True], (np.diff(cells, axis=0) != 0).any(axis=1)])]
    return cells[mainland[cells[:, 0], cells[:, 1]]], points


final, curves = [], []
for cells in lines:
    for sigma in (SMOOTH, SMOOTH / 2, 0.0):
        drawn, points = smoothed(cells, sigma)
        trial = final + [drawn] + [other for other in lines[len(final) + 1:]]
        if quick_sizes(trial) is not None:
            break
    final.append(drawn)
    curves.append(points)
grid = kingdoms_of(walls_of(final))
size = sizes(grid)
off = float(np.abs(size - size.mean()).max() / size.mean())
print("smoothed: areas within %.2f%%; km2 %s" % (100 * off, np.round(size * KM * KM).astype(int).tolist()))
moved = mainland & (grid != king)
print("land that changes kingdom: %.0f km2, %.1f%% of the mainland" % (moved.sum() * KM * KM, 100.0 * moved.sum() / mainland.sum()))
np.save(KING + "/kingdoms_%s.npy" % TAG, grid.astype(np.uint8))
with open(KING + "/lines_%s.pickle" % TAG, "wb") as handle:
    pickle.dump({"curves": curves, "cells": final, "meet": at, "pressure": push, "codes": [s["code"] for s in segments],
                 "options": options}, handle)
print("saved kingdoms_%s.npy  (%.0fs)" % (TAG, time.time() - t0))
