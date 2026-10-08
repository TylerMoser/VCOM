"""Judge a roads draft: small loops, big-river bridges away from towns, and how the roads treat
the terrain against straight lines between the same settlements.

Usage: r6_judge.py <roads out dir> <draft picture>
"""
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROADS, PICTURE = sys.argv[1], sys.argv[2]
KM = 0.335
saved = np.asarray(Image.open(PICTURE).convert("RGBA"))
land, town = np.load(ROADS + "/land.npy"), np.load(ROADS + "/town.npy")
height, river, lake = np.load(ROADS + "/height.npy"), np.load(ROADS + "/river.npy"), np.load(ROADS + "/lake.npy")
is_road = (saved[..., 0] == 200) & (saved[..., 1] == 40) & (saved[..., 2] == 30)
is_deck = (saved[..., 0] == 60) & (saved[..., 1] == 35) & (saved[..., 2] == 15)
wall = is_road | is_deck | (town > 0) | ~land
faces, n = ndimage.label(~wall)
sizes = ndimage.sum_labels(~wall, faces, index=np.arange(1, n + 1))
small = np.flatnonzero(sizes < 400) + 1
places = ndimage.center_of_mass(~wall, faces, small) if small.size else []
print("land shut in by roads alone: %d pieces; under 400 px (45 km2): %d: %s" % (
    n, small.size, [(int(x), int(y), int(sizes[i - 1])) for (y, x), i in zip(places, small)]))
print("median piece of land between roads: %.0f km2" % (np.median(sizes[sizes >= 400]) * KM * KM))

with open(ROADS + "/drawn.pickle", "rb") as handle:
    drawn = pickle.load(handle)
far = sorted((b for b in drawn["bridges"] if not b["town"] and b["flow"] >= 300), key=lambda b: -b["flow"])
print("bridges over rivers of 300 m3/s or more away from any settlement: %s" % [(b["at"], int(b["flow"]), "highway" if b["highway"] else "road") for b in far])
per_road = {}
with open(ROADS + "/network.pickle", "rb") as handle:
    laid = pickle.load(handle)["laid"]
with open(ROADS + "/towns.pickle", "rb") as handle:
    centres = pickle.load(handle)["centres"]

climbs, straight_climbs, tops, straight_tops, lengths, straights, crossings, straight_crossings = [], [], [], [], [], [], [], []
for (u, v), road in laid.items():
    if road["ferry"]:
        continue
    path = np.array(road["path"])
    z = height[path[:, 0], path[:, 1]]
    (ax, ay), (bx, by) = centres[u], centres[v]
    count = int(np.hypot(ax - bx, ay - by)) + 1
    ys, xs = np.linspace(ay, by, count).round().astype(int), np.linspace(ax, bx, count).round().astype(int)
    if not land[ys, xs].all():
        continue                                           # the straight line leaves the land: no fair match
    zs = height[ys, xs]
    climbs.append(np.abs(np.diff(z)).sum()); straight_climbs.append(np.abs(np.diff(zs)).sum())
    tops.append(z.max() - max(z[0], z[-1])); straight_tops.append(zs.max() - max(zs[0], zs[-1]))
    lengths.append(road["km"]); straights.append(count * KM)
    wet = river[path[:, 0], path[:, 1]] ; wet_s = river[ys, xs] | lake[ys, xs]
    crossings.append(np.count_nonzero(np.diff(np.concatenate([[False], wet]).astype(np.int8)) == 1))
    straight_crossings.append(np.count_nonzero(np.diff(np.concatenate([[False], wet_s]).astype(np.int8)) == 1))
climbs, straight_climbs = np.array(climbs), np.array(straight_climbs)
print("roads matched against the straight line between their ends: %d" % len(climbs))
print("  length: %.0f km against %.0f km straight (%.0f%% longer)" % (sum(lengths), sum(straights), 100 * (sum(lengths) / sum(straights) - 1)))
print("  climbing and dropping: %.0f m a road on average against %.0f m straight (%.0f%% less)" % (
    climbs.mean(), straight_climbs.mean(), 100 * (1 - climbs.sum() / straight_climbs.sum())))
print("  rise above the higher end: %.0f m on average against %.0f m straight; worst road %.0f m against %.0f m" % (
    np.mean(tops), np.mean(straight_tops), np.max(tops), np.max(straight_tops)))
print("  water met: %.2f rivers a road against %.2f rivers and lakes a straight line" % (np.mean(crossings), np.mean(straight_crossings)))
grades = []
for road in laid.values():
    if road["ferry"]:
        continue
    path = np.array(road["path"])
    z = height[path[:, 0], path[:, 1]]
    run = np.hypot(*np.diff(path, axis=0).T) * KM * 1000.0
    grades.append(np.abs(np.diff(z)) / run)
grades = np.concatenate(grades) * 100
print("  slope along the roads, percent: median %.1f, 90th %.1f, 99th %.1f, steepest %.1f" % (*np.percentile(grades, [50, 90, 99]), grades.max()))
