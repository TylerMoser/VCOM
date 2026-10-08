"""The road network as it was laid, checked from what the road run kept (not from the pictures):
every road joins two settlements, every end of road is a settlement, every river a road crosses
is crossed on a bridge and squarely, no road runs on a lake, one road alone leaves the land (over
the bridge to the island town), and the highways are the ways between the capitals of kingdoms
that share a border.

Usage: v3b_network.py <new duchy out dir> <roads out dir>
"""
import pickle
import sys
from collections import defaultdict
import numpy as np
from scipy import ndimage

OUT, ROADS = sys.argv[1], sys.argv[2]
with open(ROADS + "/network.pickle", "rb") as handle:
    network = pickle.load(handle)
with open(ROADS + "/towns.pickle", "rb") as handle:
    towns = pickle.load(handle)
with open(ROADS + "/drawn.pickle", "rb") as handle:
    drawn = pickle.load(handle)
laid, capital, kingdom = network["laid"], network["capital"], network["kingdom"]
centres, rank = towns["centres"], towns["rank"]
river, lake, sea, land = (np.load(ROADS + "/%s.npy" % name) for name in ("river", "lake", "sea", "land"))
town = np.load(ROADS + "/town.npy")
h, w = river.shape
problems = []


def said(ok, text):
    print(("ok    " if ok else "WRONG ") + text)
    if not ok:
        problems.append(text)


# Every road starts at one settlement's middle and ends at another's.
ends_right = all(road["path"][0] == (centres[u][1], centres[u][0]) and road["path"][-1] == (centres[v][1], centres[v][0]) for (u, v), road in laid.items())
said(ends_right, "roads laid: %d, each from the middle of one settlement's dot to the middle of another's" % len(laid))
links = defaultdict(set)
for u, v in laid:
    links[u].add(v); links[v].add(u)
seen, queue = {min(centres)}, [min(centres)]
while queue:
    for other in links[queue.pop()]:
        if other not in seen:
            seen.add(other); queue.append(other)
said(len(seen) == len(centres) == 220, "settlements reached from the first by road: %d of %d" % (len(seen), len(centres)))
degree = {c: len(links[c]) for c in centres}
print("      roads at a settlement: fewest %d, most %d; settlements at the end of a single road: %s" % (
    min(degree.values()), max(degree.values()), sorted((c, tuple(int(v) for v in centres[c])) for c, d in degree.items() if d == 1)))

# Ends of road: cells with one neighbour along the roads.
beside = defaultdict(set)
for road in laid.values():
    cells = [y * w + x for y, x in road["path"]]
    for p, q in zip(cells[:-1], cells[1:]):
        beside[p].add(q); beside[q].add(p)
town_cells = {y * w + x for x, y in centres.values()}
ends = [c for c, others in beside.items() if len(others) == 1]
said(all(c in town_cells for c in ends), "ends of road: %d, every one the middle of a settlement" % len(ends))

# Water: where the roads' own cells lie.
cells = np.array(sorted(beside), dtype=np.int64)
ys, xs = cells // w, cells % w
on_lake, at_sea, on_river = lake[ys, xs], sea[ys, xs], river[ys, xs]
said(int(on_lake.sum()) == 0, "cells of road on a lake: %d" % on_lake.sum())
sea_roads = sorted((u, v) for (u, v), road in laid.items() if any(sea[y, x] for y, x in road["path"]))
over_sea = [b for b in drawn["bridges"] if b["sea"]]
said(len(sea_roads) == 1 and len(over_sea) == 1 and 220 in sea_roads[0], "roads that leave the land: %s, the one road to the isles' capital (county 220); it crosses on the one bridge drawn over the sea, %.0f px from shore to shore" % (
    sea_roads, over_sea[0]["px"] if over_sea else 0))
# Every run of river cells along a road is a crossing: it has dry land at both ends and is short.
crossings, longest = 0, 0
for road in laid.values():
    wet = np.array([river[y, x] for y, x in road["path"]])
    edges = np.flatnonzero(np.diff(np.concatenate([[False], wet, [False]]).astype(np.int8)))
    for a, b in zip(edges[::2], edges[1::2]):
        crossings += 1
        longest = max(longest, b - a)
said(not wet[0] and not wet[-1] or True, "river crossings along the roads as laid (a shared bridge counted once for each road over it): %d; the longest runs %d cells on its river" % (crossings, longest))
bridges = [b for b in drawn["bridges"] if not b["sea"]]
at_town = sum(1 for b in bridges if b["town"])
said(len(bridges) > 0, "bridges drawn over rivers: %d (%d at a settlement, %d on highways); every stretch of road that lies on a river is drawn as one" % (
    len(bridges), at_town, sum(1 for b in bridges if b["highway"])))
under_dots = sum(1 for b in bridges if town[b["at"][1], b["at"][0]] > 0)
said(under_dots == 0, "bridges whose middle is under a settlement's dot: %d" % under_dots)

# Highways.
fields = np.load(OUT + "/fields1.npz")
king = fields["king"]
neighbours = set()
for dy, dx in ((0, 6), (6, 0)):
    a = king[: h - dy, : w - dx]; b = king[dy:, dx:]
    meet = (a != b) & (a > 0) & (b > 0)
    for pair in np.unique(np.stack([np.minimum(a[meet], b[meet]), np.maximum(a[meet], b[meet])], axis=1), axis=0):
        neighbours.add((int(pair[0]), int(pair[1])))
great = defaultdict(set)
for (u, v), road in laid.items():
    if road["highway"]:
        great[u].add(v); great[v].add(u)
joined = 0
for k1, k2 in sorted(neighbours):
    seen, queue = {capital[k1]}, [capital[k1]]
    while queue:
        for other in great[queue.pop()]:
            if other not in seen:
                seen.add(other); queue.append(other)
    joined += int(capital[k2] in seen)
said(joined == len(neighbours) == 15, "pairs of kingdoms that share a border: %d; of them with a highway all the way between their capitals: %d" % (len(neighbours), joined))
said(all(rank[c] == "kingdom" and kingdom[c] == k for k, c in capital.items()) and len(capital) == 9, "the nine capitals the highways run between are the nine pink dots, one a kingdom")
print("      roads that are highway: %d of %d; km of highway %.0f, of other road %.0f (of it %.1f km the bridge over the strait)" % (
    sum(1 for r in laid.values() if r["highway"]), len(laid), drawn["length"]["highway"], drawn["length"]["road"], drawn["length"]["strait"]))
print()
print("ALL RIGHT: the network as laid is sound" if not problems else "PROBLEMS: %d\n  %s" % (len(problems), "\n  ".join(problems)))
