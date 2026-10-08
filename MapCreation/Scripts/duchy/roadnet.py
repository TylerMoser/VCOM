"""Finding where a road goes: the cheapest way from one cell to another over the ground
r1_ground.py made.

A road costs its length times the going, plus CLIMB for every metre it rises or falls, plus the
river's crossing cost each time it is bridged. A step along a road already made costs REUSE of
that, and a bridge already built costs nothing more to cross, so later roads fall in with
earlier ones and make for their bridges. Leaving a road, joining one or crossing one costs
FORK, so a road does not cut a corner beside a town for the sake of a kilometre. Steps go to
the 8 cells round a cell and the 8 a knight's move away (never across or beside a river: a
river is entered and left squarely), so a road over open country is not held to eight
directions.

The search is done in a window round the two ends, widened if the road found runs along its
edge.
"""
import numpy as np
from scipy import sparse
from scipy.sparse import csgraph

KM = 0.335
CLIMB = 0.02             # km of effort for each metre climbed or dropped
REUSE = 0.5              # what a step along an existing road costs, of a new one
FORK = 4.0               # km of effort to leave an existing road and join one again
FERRY_GOING = 2.5        # the going on the sea, for the one road that has to cross it
FERRY_LANDING = 15.0     # km of effort to put to sea and to land again, each
DIRS = ((0, 1), (1, 0), (1, 1), (1, -1), (1, 2), (2, 1), (1, -2), (2, -1))
BETWEEN = {(1, 2): ((0, 1), (1, 1)), (2, 1): ((1, 0), (1, 1)), (1, -2): ((0, -1), (1, -1)), (2, -1): ((1, 0), (1, -1))}
DIR_INDEX = {d: i for i, d in enumerate(DIRS)}


class Ground:
    def __init__(self, folder, with_steps=False):
        load = lambda name: np.load(folder + "/%s.npy" % name, mmap_mode="r")
        self.passable, self.sea, self.going = load("passable"), load("sea"), load("going")
        self.loose = load("loose")
        self.height, self.river, self.crossing = load("height"), load("river"), load("crossing")
        self.shape = self.passable.shape
        # steps[d][y, x]: the step from (y, x) by DIRS[d] is part of a road; on_road: a road passes the cell.
        self.steps = [np.zeros(self.shape, dtype=bool) for _ in DIRS] if with_steps else None
        self.on_road = np.zeros(self.shape, dtype=bool) if with_steps else None

    def add_road(self, path):
        """Mark a road's steps, so later roads can use them."""
        for (y0, x0), (y1, x1) in zip(path[:-1], path[1:]):
            d = (y1 - y0, x1 - x0)
            if d in DIR_INDEX:
                self.steps[DIR_INDEX[d]][y0, x0] = True
            else:
                self.steps[DIR_INDEX[(-d[0], -d[1])]][y1, x1] = True
        for y, x in path:
            self.on_road[y, x] = True

    def _graph(self, window, ferry, reuse):
        ys, xs = window
        passable = np.array((self.loose if ferry else self.passable)[ys, xs])
        going = np.array(self.going[ys, xs], dtype=np.float64)
        height = np.array(self.height[ys, xs], dtype=np.float64)
        river = np.array(self.river[ys, xs])
        crossing = np.array(self.crossing[ys, xs], dtype=np.float64)
        reuse = reuse and self.steps is not None
        on_road = np.array(self.on_road[ys, xs], dtype=np.float64) if reuse else None
        sea = None
        if ferry:
            sea = np.array(self.sea[ys, xs])
            passable = passable | sea
            going = np.where(sea, FERRY_GOING, going)
        h, w = passable.shape
        index = np.arange(h * w).reshape(h, w)
        rows, cols, costs = [], [], []
        for d, (dy, dx) in enumerate(DIRS):
            ya, yb = slice(0, h - dy), slice(dy, h)
            xa, xb = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
            ok = passable[ya, xa] & passable[yb, xb]
            length = float(np.hypot(dy, dx)) * KM
            if (dy, dx) in BETWEEN:
                ok &= ~river[ya, xa] & ~river[yb, xb]
                total = going[ya, xa] + going[yb, xb]
                for my, mx in BETWEEN[(dy, dx)]:
                    ym, xm = slice(my, h - dy + my), slice(xa.start + mx, xa.stop + mx)
                    ok &= passable[ym, xm] & ~river[ym, xm]
                    total = total + going[ym, xm]
                    if ferry:                                # a knight's move never leaps the shore
                        ok &= sea[ym, xm] == sea[ya, xa]
                cost = length * total / 4.0
                lump = 0.0
                if ferry:
                    ok &= sea[ya, xa] == sea[yb, xb]
            else:
                cost = length * 0.5 * (going[ya, xa] + going[yb, xb])
                lump = 0.5 * np.where(river[ya, xa] != river[yb, xb], np.maximum(crossing[ya, xa], crossing[yb, xb]), 0.0)
                if ferry:
                    lump = lump + FERRY_LANDING * (sea[ya, xa] != sea[yb, xb])
            cost = cost + CLIMB * np.abs(height[yb, xb] - height[ya, xa])
            if reuse:
                made = self.steps[d][ys, xs][ya, xa]
                # (a fork on a bridge costs five times as much: roads part on the bank)
                fork = on_road[ya, xa] * (1.0 + 4.0 * river[ya, xa]) + on_road[yb, xb] * (1.0 + 4.0 * river[yb, xb])
                cost = np.where(made, REUSE * cost, cost + lump + 0.5 * FORK * fork)
            else:
                cost = cost + lump
            rows.append(index[ya, xa][ok]); cols.append(index[yb, xb][ok]); costs.append(cost[ok])
        rows, cols, costs = np.concatenate(rows), np.concatenate(cols), np.concatenate(costs)
        return sparse.coo_matrix((costs, (rows, cols)), shape=(h * w, h * w)).tocsr(), w

    def route(self, a, b, ferry=False, reuse=True, margin=None):
        """The cheapest road from a to b, each (x, y). Returns its cost in km of effort and its
        cells as (y, x), a first; None if there is no way."""
        (ax, ay), (bx, by) = a, b
        height, width = self.shape
        reach = float(np.hypot(ax - bx, ay - by))
        margin = int(max(50, 0.45 * reach)) if margin is None else margin
        for attempt in range(4):
            ys = slice(max(min(ay, by) - margin, 0), min(max(ay, by) + margin + 1, height))
            xs = slice(max(min(ax, bx) - margin, 0), min(max(ax, bx) + margin + 1, width))
            graph, w = self._graph((ys, xs), ferry, reuse)
            source = (ay - ys.start) * w + (ax - xs.start)
            target = (by - ys.start) * w + (bx - xs.start)
            reach_cost, before = csgraph.dijkstra(graph, directed=False, indices=source, return_predecessors=True)
            if not np.isfinite(reach_cost[target]):
                margin *= 2
                continue
            cells = [target]
            while cells[-1] != source:
                cells.append(int(before[cells[-1]]))
            cells.reverse()
            path = [(c // w + ys.start, c % w + xs.start) for c in cells]
            py = np.array([p[0] for p in path]); px = np.array([p[1] for p in path])
            at_edge = (((py - ys.start < 3) & (ys.start > 0)) | ((ys.stop - 1 - py < 3) & (ys.stop < height)) |
                       ((px - xs.start < 3) & (xs.start > 0)) | ((xs.stop - 1 - px < 3) & (xs.stop < width)))
            if at_edge.any() and attempt < 3:              # the window was too small to hold the best road
                margin *= 2
                continue
            return float(reach_cost[target]), path
        return None

    def length_of(self, path):
        """A road's length in km."""
        points = np.array(path, dtype=np.float64)
        return float(np.hypot(*(points[1:] - points[:-1]).T).sum()) * KM
