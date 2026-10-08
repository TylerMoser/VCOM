"""Which roads there are, and where each runs.

Of the pairs r2_candidates.py costed, a road is made between two settlements when the way
between them by the roads already chosen is more than STRETCH times what a road of their own
would cost, the cheapest pairs taken first (so every settlement is joined, and a pair well
served by going round gets no road). STRETCH is larger where roads are dear to keep and traffic
thin, smaller where they are cheap, and smaller for a capital, which draws more roads.

The highways are the ways, by those roads, between the capitals of kingdoms that share a border.
They are laid first, then the other roads from the cheapest up, each free to use what is laid
already (roadnet.py), so lesser roads branch off greater ones and make for bridges that exist.

Usage: r3_network.py <duchy out dir> <roads out dir>
"""
import heapq
import pickle
import sys
import time
import numpy as np

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
from roadnet import Ground

OUT, ROADS = sys.argv[1], sys.argv[2]
# How far round, against a road of their own, two settlements will go before a road is made.
STRETCH = {1: 1.9, 2: 1.9, 3: 1.75, 4: 1.9, 5: 1.45, 6: 1.6, 7: 2.0, 8: 1.45, 9: 1.7}
DRAWS = {"kingdom": 0.75, "duchy": 0.88, "county": 1.0}

with open(ROADS + "/towns.pickle", "rb") as handle:
    towns = pickle.load(handle)
centres, rank = towns["centres"], towns["rank"]
with open(ROADS + "/candidates.pickle", "rb") as handle:
    candidates = pickle.load(handle)
found, off = candidates["found"], candidates["off"]
with open(OUT + "/county_list_f3.pickle", "rb") as handle:
    of_duchy = np.asarray(pickle.load(handle)["of_duchy"])
with open(OUT + "/capital_candidates.pickle", "rb") as handle:
    kingdom_of_duchy = {row["duchy"]: row["kingdom"] for row in pickle.load(handle)}
kingdom = {c: kingdom_of_duchy[int(of_duchy[c])] for c in centres}
names = sorted(centres)


def ways_from(source, links, stop_at=None):
    """Cheapest way from one settlement to the others by the roads in [links]."""
    best = {source: 0.0}
    before = {}
    queue = [(0.0, source)]
    while queue:
        so_far, at = heapq.heappop(queue)
        if so_far > best.get(at, np.inf):
            continue
        if at == stop_at:
            break
        for other, cost in links.get(at, ()):
            if so_far + cost < best.get(other, np.inf):
                best[other] = so_far + cost
                before[other] = at
                heapq.heappush(queue, (so_far + cost, other))
    return best, before


# -- which roads --------------------------------------------------------------------------------------
links = {}
chosen = []
ferries = 0
for (u, v), road in sorted(found.items(), key=lambda item: item[1]["cost"]):
    if road["ferry"] and ferries:
        continue                                         # one ferry is enough for the island
    stretch = max(STRETCH[kingdom[u]], STRETCH[kingdom[v]]) * min(DRAWS[rank[u]], DRAWS[rank[v]])
    by_road = ways_from(u, links, stop_at=v)[0].get(v, np.inf)
    if by_road > stretch * road["cost"]:
        chosen.append((u, v))
        links.setdefault(u, []).append((v, road["cost"]))
        links.setdefault(v, []).append((u, road["cost"]))
        ferries += road["ferry"]
reached = ways_from(names[0], links)[0]
degree = {c: len(links.get(c, ())) for c in names}
print("roads chosen: %d of %d pairs; settlements joined: %d of %d; roads at a settlement: mean %.2f, by rank %s; with one road only: %d" % (
    len(chosen), len(found), len(reached), len(names), np.mean(list(degree.values())),
    {r: round(float(np.mean([degree[c] for c in names if rank[c] == r])), 2) for r in ("kingdom", "duchy", "county")},
    sum(1 for d in degree.values() if d == 1)))
print("by kingdom, roads per settlement: %s" % {k: round(float(np.mean([degree[c] for c in names if kingdom[c] == k])), 2) for k in range(1, 10)})

# -- the highways ------------------------------------------------------------------------------------
fields = np.load(OUT + "/fields1.npz")
king = fields["king"]
beside = set()
for dy, dx in ((0, 6), (6, 0)):                          # across the pink line's width
    a = king[: king.shape[0] - dy, : king.shape[1] - dx]; b = king[dy:, dx:]
    meet = (a != b) & (a > 0) & (b > 0)
    for pair in np.unique(np.stack([np.minimum(a[meet], b[meet]), np.maximum(a[meet], b[meet])], axis=1), axis=0):
        beside.add((int(pair[0]), int(pair[1])))
capital = {kingdom[c]: c for c in names if rank[c] == "kingdom"}
highway = set()
print("kingdoms that share a border: %s" % sorted(beside))
for k1, k2 in sorted(beside):
    best, before = ways_from(capital[k1], links, stop_at=capital[k2])
    at = capital[k2]
    hops = 0
    while at != capital[k1]:
        highway.add((min(at, before[at]), max(at, before[at])))
        at = before[at]
        hops += 1
    print("  capital of %d to capital of %d: %d roads, %.0f km of effort" % (k1, k2, hops, best[capital[k2]]))
print("highway roads: %d of %d" % (len(highway), len(chosen)))

# -- where each runs, laid in order -------------------------------------------------------------------
from scipy.spatial import cKDTree
THROUGH = 30             # px: a road that would pass a settlement nearer than this goes through it
ground = Ground(ROADS, with_steps=True)
order = sorted(chosen, key=lambda pair: (pair not in highway, found[pair]["cost"]))
laid = {}
tree = cKDTree(np.array([centres[c] for c in names], dtype=np.float64))
through = 0


def lay(u, v, ferry, is_highway, depth=0):
    """Lay the road from u to v; by way of any settlement it would pass close to."""
    global through
    key = (min(u, v), max(u, v))
    if key in laid:
        laid[key]["highway"] = laid[key]["highway"] or is_highway
        return
    cost, path = ground.route(centres[u], centres[v], ferry=ferry, reuse=True)
    if not ferry and depth < 4:
        points = np.array(path, dtype=np.float64)[::2, ::-1]
        gaps, nearest = tree.query(points)
        near = [(gap, names[i]) for gap, i in zip(gaps, nearest) if gap < THROUGH and names[i] not in (u, v)]
        if near:
            by = min(near)[1]
            through += 1
            lay(u, by, False, is_highway, depth + 1)
            lay(by, v, False, is_highway, depth + 1)
            return
    ground.add_road(path)
    alone = found.get(key) or found.get((key[1], key[0]))
    laid[key] = {"path": path if key == (u, v) else path[::-1], "cost": cost, "km": ground.length_of(path), "highway": is_highway, "ferry": ferry,
                 "alone": alone["cost"] if alone else cost, "alone_km": alone["km"] if alone else ground.length_of(path)}


t0 = time.time()
for done, (u, v) in enumerate(order, start=1):
    lay(u, v, found[(u, v)]["ferry"], (u, v) in highway)
    if done % 100 == 0:
        print("  %d laid (%.0fs)" % (done, time.time() - t0), flush=True)
print("roads taken through a settlement they would have passed within %.0f km of: %d" % (THROUGH * 0.335, through))
total = sum(road["km"] for road in laid.values())
cells = set()
for road in laid.values():
    cells.update(road["path"])
print("laid %d roads, %.0f km end to end; distinct cells of road %d (%.0f%% of the cells walked, the rest shared)  (%.0fs)" % (
    len(laid), total, len(cells), 100.0 * len(cells) / sum(len(road["path"]) for road in laid.values()), time.time() - t0))
longer = np.array([road["km"] / road["alone_km"] for road in laid.values()])
print("a road laid among the others against one laid alone, length: median %.2f, 90th %.2f, most %.2f" % (np.median(longer), np.percentile(longer, 90), longer.max()))
with open(ROADS + "/network.pickle", "wb") as handle:
    pickle.dump({"laid": laid, "order": order, "kingdom": kingdom, "capital": capital}, handle)
print("saved")
