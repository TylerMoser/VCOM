"""Lakes, rivers and watersheds on the land w2_drain.py made.

Lakes first. A lake is a valley flooded behind one point on its stream: all the ground upstream
of that point that lies below the water's level, so it follows the valley's own shape, runs up
the side valleys as arms, and has the one outlet. How many, how big and where depends on the
kingdom's biome (LAKES below): fell tarns and ribbon lakes in the tundra, lakes at the mountains'
foot round the central range, crater lakes and one flooded caldera among the volcanoes, broad
shallow sheets in the swamp, a few steppe lakes on the grassland, and in the desert one salt lake
with no outlet, as big as the rivers reaching it can keep full against the sun.

Then the water is added up down every stream (rain running off, less what lakes and desert
riverbeds lose), giving each river its size; the streams big enough to draw are chained into
rivers; and every cell is filed under the place its water leaves the land, which gives the
watersheds.

Usage: w3_water.py <out dir> <factor> [lake scale] [least river, m3/s]
"""
import heapq
import pickle
import sys
import numpy as np
from scipy import ndimage

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
import hydro

OUT = sys.argv[1]
FACTOR = int(sys.argv[2]) if len(sys.argv) > 2 else 4
LAKE_SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
LEAST_RIVER = float(sys.argv[4]) if len(sys.argv) > 4 else 15.0
KM = 0.335 * FACTOR
CELL = KM * KM                                           # km2
CUMECS = CELL * 1e6 / 31.5e6                             # a metre a year off one cell, in m3/s
SEED = 20261007
LEAST_BASIN = 1500.0                                     # km2: a river system gathering less joins the watershed beside it
OUTLET_FROM = 60.0                                       # km2: lakes this big always show their outlet stream

# Of each kingdom's land, the share to lie under lakes.
LAKE_SHARE = {1: 0.083, 2: 0.026, 3: 0.035, 4: 0.004, 5: 0.027, 6: 0.045, 7: 0.140, 8: 0.039, 9: 0.055}
# Per kingdom, kinds of lake: (how many, least and most area in km2, where, most the water may
# stand above its outlet in metres, least distance from the sea in km, and optionally "clumped").
# Where: "trunk" on a river of at least the given flow, "stream" on one between two flows,
# "head" on ground gathering under 150 km2, "any" anywhere, "foot" on a river leaving the
# mountains, "high" above a height, "low" on a river below one.
# Clumped kinds are the small lakes: many little and few bigger, gathered into lake districts
# with bare country between, as tarns, kettle holes and backwater pools are.
LAKES = {
    1: [(3, 400, 900, ("trunk", 40), 300, 30), (12, 80, 300, ("trunk", 8), 220, 20),
        (45, 15, 80, ("stream", 1, 30), 140, 8), (240, 4.5, 60, ("head",), 80, 4, "clumped")],
    2: [(2, 120, 260, ("stream", 3, 400), 140, 15), (7, 30, 110, ("stream", 1, 400), 120, 10),
        (20, 4.5, 40, ("head",), 60, 6, "clumped")],
    3: [(11, 110, 420, ("foot", 25), 260, 0), (12, 25, 100, ("stream", 2, 60), 160, 0),
        (30, 4.5, 30, ("high", 1500), 60, 0, "clumped")],
    4: [(2, 20, 55, ("trunk", 12), 25, 15)],
    5: [(4, 180, 480, ("stream", 2, 4000), 18, 20), (10, 15, 70, ("any",), 10, 10), (45, 4.5, 30, ("any",), 6, 5, "clumped")],
    6: [(8, 140, 560, ("trunk", 40), 200, 25), (26, 10, 55, ("stream", 3, 60), 90, 8)],
    7: [(3, 1100, 2400, ("trunk", 50), 6, 12), (10, 230, 600, ("stream", 3, 4000), 5, 8),
        (30, 40, 150, ("any",), 4, 5), (150, 4.5, 60, ("any",), 3, 3, "clumped")],
    8: [(5, 180, 560, ("trunk", 15), 120, 20), (26, 12, 70, ("stream", 1, 30), 60, 8)],
    9: [(3, 380, 850, ("low", 60, 160), 40, 15), (12, 75, 190, ("stream", 8, 4000), 30, 10), (70, 4.5, 50, ("any",), 20, 4, "clumped")],
}
SUN = {4: 2.8, 5: 0.6}                                   # metres a year a lake loses there, beyond its rain
BED_LOSS = {4: 0.0035, 5: 0.0005}                        # share of its water a river loses per km there

grids = np.load(OUT + "/grid%d.npz" % FACTOR)
land, king, mainland = grids["land"], grids["king"], grids["mainland"]
drain = np.load(OUT + "/drain%d.npz" % FACTOR)
h, w = land.shape
grid = hydro.Grid(land)
z = grid.flat(drain["height"])
to, order, closed = drain["to"], drain["order"], drain["closed"]
runoff = grid.flat(drain["runoff"])
kingdom = grid.flat(king)
rng = np.random.default_rng(SEED)
coast = grid.flat(ndimage.distance_transform_edt(land) * KM)
high = (king == 1) | (king == 2) | (king == 3)
into_high = grid.flat(np.where(high, ndimage.distance_transform_edt(high) * KM, 0.0))
starts, kids = hydro.upstream(grid, to)
starts_list, kids_list = starts.tolist(), kids.tolist()
z_list = z.tolist()

gain = runoff * CUMECS
flow0 = hydro.gather(grid, order, to, gain)
gathers = hydro.gather(grid, order, to, np.full(grid.n, CELL))          # km2 draining through each cell

lake = np.zeros(grid.n, dtype=np.int32)                 # which lake each cell is under, nought for none
lakes = []                                               # one record per lake


def flood(point, cells_wanted, most_rise):
    """The ground upstream of [point] in order of height, until [cells_wanted] are under water or
    the water would stand more than [most_rise] above the outlet. Stops at other lakes."""
    heap = [(z_list[point], point)]
    under = []
    top = z_list[point] + most_rise
    while heap and len(under) < cells_wanted:
        height, cell = heapq.heappop(heap)
        if height > top:
            break
        if lake[cell]:
            continue
        under.append(cell)
        for child in kids_list[starts_list[cell]: starts_list[cell + 1]]:
            heapq.heappush(heap, (z_list[child], child))
    return under


def add_lake(cells, kind, king_of, outlet, shut=False):
    number = len(lakes) + 1
    lake[cells] = number
    lakes.append({"id": number, "kind": kind, "kingdom": int(king_of), "cells": len(cells), "km2": len(cells) * CELL,
                  "outlet": int(outlet), "level": float(z[cells].max()), "shut": shut})
    return number


def crowded(point, km2, room=4.0):
    """Whether another lake already lies about where one of [km2] at [point] would, with
    [room] km to spare."""
    reach = int((0.9 * np.sqrt(km2 / np.pi) + room) / KM) + 1
    y, x = int(grid.rows[point]), int(grid.cols[point])
    return bool(lake_grid[max(y - reach, 0): y + reach + 1, max(x - reach, 0): x + reach + 1].any())


site_cache = {}


def sites(rule, k, from_sea):
    """Cells of kingdom [k] where a lake of this kind may have its outlet. Worked out once."""
    key = (rule, k, from_sea)
    if key not in site_cache:
        site_cache[key] = find_sites(rule, k, from_sea)
    return site_cache[key]


def find_sites(rule, k, from_sea):
    here = (kingdom == k) & (coast >= from_sea)
    name = rule[0]
    if name == "trunk":
        here &= flow0 >= rule[1]
    elif name == "stream":
        here &= (flow0 >= rule[1]) & (flow0 <= rule[2])
    elif name == "head":
        here &= gathers < 150.0
    elif name == "foot":                                 # big valleys where they leave the mountains
        here &= (flow0 >= rule[1]) & (into_high < 45.0)
    elif name == "high":
        here &= (z >= rule[1]) & (gathers < 150.0)
    elif name == "low":
        here &= (flow0 >= rule[1]) & (z <= rule[2])
    return np.flatnonzero(here)


lake_grid = np.zeros((h, w), dtype=bool)

# -- the volcanoes' lakes --------------------------------------------------------------------------
for y, x, is_ring, tall in drain["volcanoes"]:
    middle = int(grid.index[int(y) // FACTOR, int(x) // FACTOR])
    if middle < 0:
        continue
    if is_ring:
        # Down from the middle of the hollow to where its water crosses the ring: flood behind that.
        cell = middle
        while to[cell] != grid.sea and np.hypot(grid.rows[cell] * FACTOR - y, grid.cols[cell] * FACTOR - x) * 0.335 < 13.5:
            cell = int(to[cell])
        cells = flood(cell, int(LAKE_SCALE * 520.0 / CELL), 600.0)
        if cells:
            add_lake(np.array(cells), "caldera", 2, cell)
    elif tall > 1500.0:
        # A crater at the top of the taller cones: a round pool with no stream in or out.
        radius = rng.uniform(2.3, 3.2) * np.sqrt(LAKE_SCALE)
        near = np.flatnonzero(np.hypot(grid.rows * FACTOR - y, grid.cols * FACTOR - x) * 0.335 <= radius)
        if near.size:
            add_lake(near, "crater", 2, middle, shut=True)
lake_grid = grid.full(lake > 0, False, bool)

# -- the kingdoms' lakes ---------------------------------------------------------------------------
# Lake districts: broad patches where small lakes come thick, and bare country between.
district = ndimage.gaussian_filter(rng.standard_normal((h, w)), 34.0 / KM)
district = district / district.std() + 0.6 * (lambda f: f / f.std())(ndimage.gaussian_filter(rng.standard_normal((h, w)), 11.0 / KM))
favour = 1.0 / (1.0 + np.exp(-2.6 * grid.flat(district)))


def size_of(kind):
    least, most = kind[1], kind[2]
    if len(kind) > 6:                                    # clumped: many little, few bigger
        return float(min(least * (1.0 - rng.random()) ** (-1.0 / 1.05), most))
    return float(np.exp(rng.uniform(np.log(least), np.log(most))))


def pick(kind, k):
    """A place for a lake of this kind in kingdom [k]: anywhere it may go, or for clumped kinds
    mostly inside the lake districts."""
    choices = sites(kind[3], k, kind[5])
    if choices.size == 0:
        return -1
    if len(kind) > 6:
        key = ("weights", kind[3], k, kind[5])
        if key not in site_cache:
            site_cache[key] = np.cumsum(favour[choices])
        ladder = site_cache[key]
        return int(choices[min(int(np.searchsorted(ladder, rng.random() * ladder[-1])), choices.size - 1)])
    return int(choices[rng.integers(choices.size)])


for k in range(1, 10):
    king_km2 = float((kingdom == k).sum()) * CELL
    wanted_total = LAKE_SHARE[k] * LAKE_SCALE * king_km2
    made = sum(l["km2"] for l in lakes if l["kingdom"] == k)
    # Draw the sizes first and fit them, within reason, to the kingdom's share; biggest go in first.
    plan = []
    for kind in LAKES[k]:
        for _ in range(kind[0]):
            plan.append([size_of(kind), kind])
    fit = float(np.clip(max(wanted_total - made, 0.0) / max(sum(p[0] for p in plan), 1e-9), 0.6, 1.6))
    for p in plan:
        p[0] *= fit
    plan.sort(key=lambda p: -p[0])
    for km2, kind in plan:
        if made >= wanted_total:
            break
        clumped = len(kind) > 6
        for attempt in range(60):
            point = pick(kind, k)
            if point < 0:
                break
            if lake[point] or crowded(point, km2, 1.2 if clumped else 4.0):
                continue
            cells = flood(point, max(int(round(km2 / CELL)), 2), kind[4])
            if len(cells) < max(2, 0.35 * km2 / CELL):
                continue
            add_lake(np.array(cells), kind[3][0], k, point)
            lake_grid[grid.rows[cells], grid.cols[cells]] = True
            made += len(cells) * CELL
            break
    # Top up with small ones if the planned ones did not come to the share.
    smallest = LAKES[k][-1]
    tries, extra = 0, 0
    while made < 0.98 * wanted_total and tries < 6000 and extra < max(10, smallest[0] // 2):
        tries += 1
        km2 = size_of(smallest) * fit
        point = pick(smallest, k)
        if point < 0:
            break
        if lake[point] or crowded(point, km2, 1.2):
            continue
        cells = flood(point, max(int(round(km2 / CELL)), 2), smallest[4])
        if len(cells) < 2:
            continue
        add_lake(np.array(cells), smallest[3][0], k, point)
        lake_grid[grid.rows[cells], grid.cols[cells]] = True
        made += len(cells) * CELL
        extra += 1

# -- the desert's salt lake: as big as what reaches it can keep full ---------------------------------
keep = np.ones(grid.n)
for k, per_km in BED_LOSS.items():
    keep[kingdom == k] = np.exp(-per_km * KM)
sink = int(np.flatnonzero(closed)[0])
for _ in range(6):
    takes = gain.copy()
    for k, metres in SUN.items():
        takes[(lake > 0) & (kingdom == k)] = -metres * CUMECS
    flow = hydro.gather(grid, order, to, takes, pond=lake, keep=keep)
    salt = [l for l in lakes if l["kind"] == "salt"]
    reaching = flow[sink] + (SUN[4] * CUMECS * salt[0]["cells"] if salt else 0.0)       # before its own loss
    balance_km2 = reaching * 31.5 / SUN[4]
    if salt and abs(salt[0]["km2"] - balance_km2) < 0.03 * balance_km2 + CELL:
        break
    if salt:
        lake[lake == salt[0]["id"]] = 0
        lakes.remove(salt[0])
        for n, l in enumerate(lakes):                    # keep the numbering whole
            if l["id"] != n + 1:
                lake[lake == l["id"]] = n + 1
                l["id"] = n + 1
    cells = flood(sink, max(int(round(balance_km2 / CELL)), 2), 200.0)
    add_lake(np.array(cells), "salt", 4, sink, shut=True)
takes = gain.copy()
for k, metres in SUN.items():
    takes[(lake > 0) & (kingdom == k)] = -metres * CUMECS
flow = hydro.gather(grid, order, to, takes, pond=lake, keep=keep)
print("the salt lake: %.0f km2, kept by %.1f m3/s reaching it; by kingdom %s" % (
    lakes[-1]["km2"], reaching, dict(zip(*[v.tolist() for v in np.unique(kingdom[lake == lakes[-1]["id"]], return_counts=True)]))))

# -- rivers ---------------------------------------------------------------------------------------
river = flow >= LEAST_RIVER
# A sizeable lake always shows its stream out, down to the next river or the sea.
for l in lakes:
    if l["km2"] >= OUTLET_FROM and not l["shut"]:
        cell = l["outlet"]
        while cell != grid.sea and not (river[cell] and lake[cell] != l["id"]):
            river[cell] = True
            cell = int(to[cell])
to_list = to.tolist()
river_list = river.tolist()
# The biggest stream coming into each river cell carries the river's line on upstream.
main_in = np.full(grid.n, -1, dtype=np.int64)
for cell in np.flatnonzero(river)[np.argsort(-flow[river])].tolist():
    below = to_list[cell]
    if below != grid.sea and river_list[below] and main_in[below] < 0:
        main_in[below] = cell
has_in = np.zeros(grid.n, dtype=bool)
inland = river & (to != grid.sea)
has_in[to[inland]] = True
has_in &= river
# Every line starts at a source and runs down until it meets a bigger stream, whose line goes on.
reaches = []
for head in np.flatnonzero(river & ~has_in).tolist():
    line = [head]
    cell = head
    while True:
        below = to_list[cell]
        if below == grid.sea or not river_list[below]:
            end = "sink" if closed[cell] else ("sea" if below == grid.sea else "dry")
            break
        line.append(below)
        if main_in[below] != cell:
            end = "joins"
            break
        cell = below
    reaches.append({"cells": np.array(line), "end": end})
print("rivers: %d cells in %d lines" % (int(river.sum()), len(reaches)))
uphill = sum(int((np.diff(z[r["cells"]]) >= 0).sum()) for r in reaches)
print("steps along drawn rivers that do not go down: %d of %d" % (uphill, sum(len(r["cells"]) - 1 for r in reaches)))

# -- watersheds -----------------------------------------------------------------------------------
shut_at = closed.copy()
mouth = hydro.outlets(grid, order, to, shut_at)
names, counts = np.unique(mouth, return_counts=True)
size_km2 = dict(zip(names.tolist(), (counts * CELL).tolist()))
on_main = grid.flat(mainland)
kept = [m for m in names.tolist() if on_main[m] and (size_km2[m] >= LEAST_BASIN or closed[m])]
kept_set = np.isin(mouth, kept) & on_main
# Everything else, the short streams between the rivers' mouths, joins the watershed it lies
# nearest: each small river system whole, by where most of it lies nearest, so that no line is
# ever drawn across one of its streams.
seed = grid.full(np.where(kept_set, mouth + 1, 0), 0, np.int64)
_, (ny, nx) = ndimage.distance_transform_edt(seed == 0, return_indices=True)
nearest = grid.flat(seed[ny, nx])
loose = on_main & ~kept_set
pairs, votes = np.unique(np.stack([mouth[loose], nearest[loose]]), axis=1, return_counts=True)
joins = {}
for (small, big), count in zip(pairs.T.tolist(), votes.tolist()):
    if small not in joins or count > joins[small][1]:
        joins[small] = (big, count)
label = np.where(kept_set, mouth + 1, 0)
loose_cells = np.flatnonzero(loose)
label[loose_cells] = np.array([joins[m][0] for m in mouth[loose_cells].tolist()])
shed_grid = np.where(mainland, grid.full(label, 0, np.int64), 0)
ids = np.unique(shed_grid[shed_grid > 0])
relabel = {int(v): n + 1 for n, v in enumerate(ids)}
shed = np.zeros((h, w), dtype=np.int32)
for v, n in relabel.items():
    shed[shed_grid == v] = n
sheds = []
for v, n in relabel.items():
    m = v - 1
    sheds.append({"id": n, "mouth": m, "km2": float((shed == n).sum()) * CELL, "flow": float(flow[m]),
                  "shut": bool(closed[m]), "x": int(grid.cols[m] * FACTOR), "y": int(grid.rows[m] * FACTOR),
                  "kingdom": int(kingdom[m])})
print("watersheds: %d (of %d places water leaves the land)" % (len(sheds), len(names)))

# -- the account ------------------------------------------------------------------------------------
print("kingdom  lakes   lake km2   share   wanted   river cells   biggest flow")
for k in range(1, 10):
    here = kingdom == k
    mine = [l for l in lakes if l["kingdom"] == k]
    print("   %d     %4d   %8.0f   %5.2f%%   %5.2f%%   %7d   %8.0f" % (
        k, len(mine), sum(l["km2"] for l in mine), 100 * ((lake > 0) & here).sum() / here.sum(),
        100 * LAKE_SHARE[k] * LAKE_SCALE, int((river & here).sum()), flow[here].max()))
print("lakes in all: %d, %.0f km2, %.2f%% of the land" % (len(lakes), (lake > 0).sum() * CELL, 100 * (lake > 0).mean()))
big = sorted(sheds, key=lambda s: -s["km2"])[:12]
print("biggest watersheds (km2, m3/s at the mouth, mouth x y, kingdom of the mouth):")
for s in big:
    print("   %7.0f  %6.0f   (%4d, %4d)  %d%s" % (s["km2"], s["flow"], s["x"], s["y"], s["kingdom"], "  no outlet" if s["shut"] else ""))

with open(OUT + "/water%d.pickle" % FACTOR, "wb") as handle:
    pickle.dump({"factor": FACTOR, "lake": grid.full(lake, 0, np.int32), "lakes": lakes, "flow": grid.full(flow),
                 "height": drain["height"], "reaches": reaches, "rows": grid.rows, "cols": grid.cols,
                 "shed": shed, "sheds": sheds, "least_river": LEAST_RIVER, "flow_flat": flow, "lake_flat": lake,
                 "z": z, "to": to, "sea": grid.sea}, handle)
print("saved water%d.pickle" % FACTOR)
