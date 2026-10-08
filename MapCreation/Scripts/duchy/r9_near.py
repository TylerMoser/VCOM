"""Which roads run near a spot, and how: for looking into an odd bit of the drawing.

Usage: r9_near.py <roads out dir> <x> <y> [reach px]
"""
import pickle
import sys
import numpy as np

ROADS, X, Y = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
REACH = int(sys.argv[4]) if len(sys.argv) > 4 else 20
with open(ROADS + "/network.pickle", "rb") as handle:
    laid = pickle.load(handle)["laid"]
with open(ROADS + "/towns.pickle", "rb") as handle:
    towns = pickle.load(handle)
centres, rank = towns["centres"], towns["rank"]
river, town, crossing = np.load(ROADS + "/river.npy"), np.load(ROADS + "/town.npy"), np.load(ROADS + "/crossing.npy")
here = [c for c, (x, y) in centres.items() if abs(x - X) <= REACH and abs(y - Y) <= REACH]
print("settlements within %d px: %s" % (REACH, [(c, centres[c], rank[c]) for c in here]))
for (u, v), road in laid.items():
    path = np.array(road["path"])
    near = (np.abs(path[:, 1] - X) <= REACH) & (np.abs(path[:, 0] - Y) <= REACH)
    if not near.any():
        continue
    cells = path[near]
    wet = river[cells[:, 0], cells[:, 1]]
    print("road %d %s to %d %s%s: %d cells here, %d on the river; here it runs %s" % (
        u, centres[u], v, centres[v], " (highway)" if road["highway"] else "", near.sum(), wet.sum(),
        " ".join("(%d,%d)%s" % (x, y, "~" if river[y, x] else ("*" if town[y, x] else "")) for y, x in cells[:: max(len(cells) // 14, 1)])))
ys, xs = slice(Y - 14, Y + 15), slice(X - 22, X + 23)
print("the ground here (. land, ~ river, o dot, # no bridge allowed, digits: roads through the cell):")
count = np.zeros(river.shape, dtype=np.int8)
for road in laid.values():
    path = np.array(road["path"])
    near = (np.abs(path[:, 1] - X) <= 30) & (np.abs(path[:, 0] - Y) <= 30)
    count[path[near, 0], path[near, 1]] += 1
for y in range(ys.start, ys.stop):
    line = ""
    for x in range(xs.start, xs.stop):
        if count[y, x]:
            line += str(min(int(count[y, x]), 9))
        elif river[y, x]:
            line += "#" if crossing[y, x] > 1000 else "~"
        elif town[y, x]:
            line += "o"
        else:
            line += "."
    print(line)
