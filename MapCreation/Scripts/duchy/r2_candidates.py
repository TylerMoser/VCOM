"""Every pair of neighbouring settlements, and what a road between them would cost by itself.

Neighbours are the pairs a triangulation of the settlements joins, less the long ones that run
round the island's outside. The island town's pairs are costed with a ferry. Worked on side by
side; saves each pair's cost, length and course.

Usage: r2_candidates.py <roads out dir>
"""
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy.spatial import Delaunay

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
from roadnet import Ground

LONGEST = 330            # px: a pair further apart than this is not tried
ground = None


def ready(folder):
    global ground
    ground = Ground(folder)


def cost_of(task):
    u, v, a, b, ferry = task
    found = ground.route(a, b, ferry=ferry, reuse=False)
    if found is None:
        return u, v, None, None, None
    cost, path = found
    return u, v, cost, ground.length_of(path), path


if __name__ == "__main__":
    ROADS = sys.argv[1]
    with open(ROADS + "/towns.pickle", "rb") as handle:
        towns = pickle.load(handle)
    centres = towns["centres"]
    land = np.load(ROADS + "/land.npy", mmap_mode="r")
    passable = np.load(ROADS + "/passable.npy", mmap_mode="r")
    names = sorted(centres)
    points = np.array([centres[c] for c in names], dtype=np.float64)
    pairs = set()
    for a, b, c in Delaunay(points).simplices:
        for u, v in ((a, b), (b, c), (a, c)):
            pairs.add((names[min(u, v)], names[max(u, v)]))
    # Which settlements are off the mainland: the largest piece of land is the mainland.
    from scipy import ndimage
    pieces, n = ndimage.label(np.array(land))
    sizes = ndimage.sum_labels(np.array(land), pieces, index=np.arange(1, n + 1))
    main = int(np.argmax(sizes)) + 1
    off = {c for c in names if pieces[centres[c][1], centres[c][0]] != main}
    print("settlements off the mainland: %s" % sorted(off))
    tasks = []
    for u, v in sorted(pairs):
        reach = float(np.hypot(centres[u][0] - centres[v][0], centres[u][1] - centres[v][1]))
        ferry = (u in off) != (v in off)
        if reach <= LONGEST or ferry and reach <= 2 * LONGEST:
            tasks.append((u, v, centres[u], centres[v], ferry))
    print("pairs: %d of %d tried (%d with a ferry)" % (len(tasks), len(pairs), sum(t[4] for t in tasks)))
    t0 = time.time()
    found = {}
    with ProcessPoolExecutor(max_workers=12, initializer=ready, initargs=(ROADS,)) as pool:
        for done, (u, v, cost, km, path) in enumerate(pool.map(cost_of, tasks, chunksize=4), start=1):
            if cost is not None:
                found[(u, v)] = {"cost": cost, "km": km, "path": path, "ferry": (u in off) != (v in off)}
            if done % 100 == 0:
                print("  %d done (%.0fs)" % (done, time.time() - t0), flush=True)
    costs = np.array([f["cost"] for f in found.values()]); kms = np.array([f["km"] for f in found.values()])
    straight = np.array([np.hypot(centres[u][0] - centres[v][0], centres[u][1] - centres[v][1]) * 0.335 for u, v in found])
    print("roads found: %d; length km: median %.0f, longest %.0f; effort over length: median %.2f, 90th %.2f; length over the straight line: median %.2f, 90th %.2f, most %.2f  (%.0fs)" % (
        len(found), np.median(kms), kms.max(), np.median(costs / kms), np.percentile(costs / kms, 90),
        np.median(kms / straight), np.percentile(kms / straight, 90), (kms / straight).max(), time.time() - t0))
    with open(ROADS + "/candidates.pickle", "wb") as handle:
        pickle.dump({"found": found, "off": off}, handle)
    print("saved")
