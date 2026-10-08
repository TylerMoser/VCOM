"""What the rebuild on Kingdoms2.png changed, old against new: land that keeps its duchy and its
county, capitals that stay where they were, and roads and bridges that are the same.

Usage: v4_changes.py <old duchy out dir> <new duchy out dir> <old roads dir> <new roads dir> <old pictures> <new pictures>
"""
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.optimize import linear_sum_assignment

Image.MAX_IMAGE_PIXELS = None
OLD, NEW, OLD_ROADS, NEW_ROADS, OLD_PICTURES, NEW_PICTURES = sys.argv[1:7]
KM = 0.335
KM2 = KM * KM


def kept(folder, name):
    with open(folder + "/" + name, "rb") as handle:
        return pickle.load(handle)


old_king, new_king = np.load(OLD + "/fields1.npz")["king"], np.load(NEW + "/fields1.npz")["king"]
mainland = old_king > 0
old_duchy, new_duchy = np.load(OLD + "/duchy_map.npy"), np.load(NEW + "/duchy_map.npy")
old_county, new_county = np.load(OLD + "/county_map_f3.npy"), np.load(NEW + "/county_map_f3.npy")
old_list, new_list = kept(OLD, "county_list_f3.pickle"), kept(NEW, "county_list_f3.pickle")
old_set, new_set = kept(OLD, "settlements.pickle"), kept(NEW, "settlements.pickle")
land = old_duchy > 0
print("land in the same kingdom as before: %.1f%%; in the same duchy: %.1f%%" % (
    100.0 * (old_king == new_king)[mainland].mean(), 100.0 * (old_duchy == new_duchy)[land].mean()))

# Counties are matched old to new by the land they share (numbers may differ).
count = 220
table = np.zeros((count + 1, count + 1), dtype=np.int64)
np.add.at(table, (old_county[land], new_county[land]), 1)
rows, cols = linear_sum_assignment(-table[1:, 1:])
shared = table[1:, 1:][rows, cols]
old_size = table[1:, 1:].sum(axis=1)[rows]
share = shared / np.maximum(old_size, 1)
print("land in the county that best matches its old one: %.1f%%" % (100.0 * shared.sum() / land.sum()))
print("counties by how much of their old land they keep: all but 2%% of it %d, 90%% or more %d, half to 90%% %d, less than half %d" % (
    (share >= 0.98).sum(), ((share >= 0.9) & (share < 0.98)).sum(), ((share >= 0.5) & (share < 0.9)).sum(), (share < 0.5).sum()))
same_number = sum(1 for r, c in zip(rows, cols) if r == c)
print("counties whose best match has the same number in the lists the runs kept: %d of %d" % (same_number, count))

# Capitals.
old_at = {c: tuple(int(v) for v in at) for c, at in old_set["centres"].items()}
new_at = {c: tuple(int(v) for v in at) for c, at in new_set["centres"].items()}
old_points = np.array([old_at[c] for c in sorted(old_at)], dtype=np.float64)
new_points = np.array([new_at[c] for c in sorted(new_at)], dtype=np.float64)
gaps = np.hypot(old_points[:, None, 0] - new_points[None, :, 0], old_points[:, None, 1] - new_points[None, :, 1])
nearest = gaps.min(axis=0) * KM                           # for each new capital, how far the nearest old one is
ranks = np.array([new_set["rank"][c] for c in sorted(new_at)])
for name in ("kingdom", "duchy", "county"):
    mine = nearest[ranks == name]
    print("%s capitals: %d; where an old capital of any rank stood (within 1 km) %d, within 5 km %d, further %d (furthest %.0f km)" % (
        name, len(mine), (mine <= 1.0).sum(), ((mine > 1.0) & (mine <= 5.0)).sum(), (mine > 5.0).sum(), mine.max()))
print("all capitals: %d of 220 where one stood (within 1 km); %d within 5 km; %d new sites" % (
    (nearest <= 1.0).sum(), ((nearest > 1.0) & (nearest <= 5.0)).sum(), (nearest > 5.0).sum()))
gone = (gaps.min(axis=1) * KM > 5.0).sum()
print("old capitals with no capital within 5 km now: %d" % gone)
old_ranks = {old_at[c]: old_set["rank"][c] for c in old_at}
changed_rank = [(new_at[c], old_ranks[new_at[c]], new_set["rank"][c]) for c in sorted(new_at) if new_at[c] in old_ranks and old_ranks[new_at[c]] != new_set["rank"][c]]
print("capitals on the same spot whose rank changed: %s" % changed_rank)
print("kingdom capitals, old: %s" % sorted(old_at[c] for c in old_at if old_set["rank"][c] == "kingdom"))
print("kingdom capitals, new: %s" % sorted(new_at[c] for c in new_at if new_set["rank"][c] == "kingdom"))
old_seats = sorted(old_at[c] for c in old_at if old_set["rank"][c] != "county")
new_seats = sorted(new_at[c] for c in new_at if new_set["rank"][c] != "county")
moved_seats = [(a, b) for a, b in zip(old_seats, new_seats) if a != b]
print("duchy capitals (pink and purple) not on the very pixel they were: %s" % moved_seats)

# Roads.
def colour(folder, name, value):
    return (np.asarray(Image.open(folder + "/" + name).convert("RGB")) == np.array(value, dtype=np.uint8)).all(axis=2)


old_road, new_road = colour(OLD_PICTURES, "Roads.png", (200, 40, 30)), colour(NEW_PICTURES, "Roads.png", (200, 40, 30))
old_deck, new_deck = colour(OLD_PICTURES, "Roads.png", (60, 35, 15)), colour(NEW_PICTURES, "Roads.png", (60, 35, 15))
near_old = ndimage.binary_dilation(old_road | old_deck, iterations=3)
near_new = ndimage.binary_dilation(new_road | new_deck, iterations=3)
print("road pixels: %d before, %d now; of the new, within 1 km of an old road %.0f%%; of the old, within 1 km of a new road %.0f%%" % (
    old_road.sum(), new_road.sum(), 100.0 * (new_road & near_old).sum() / new_road.sum(), 100.0 * (old_road & near_new).sum() / old_road.sum()))
old_marks, n_old = ndimage.label(old_deck, structure=np.ones((3, 3)))
new_marks, n_new = ndimage.label(new_deck, structure=np.ones((3, 3)))
same_marks = len(set(np.unique(new_marks[ndimage.binary_dilation(old_deck, iterations=4) & new_deck]).tolist()) - {0})
print("bridge marks: %d before, %d now; of the new, standing where an old one stood: %d" % (n_old, n_new, same_marks))
old_net, new_net = kept(OLD_ROADS, "network.pickle"), kept(NEW_ROADS, "network.pickle")
old_links = {(old_at[u], old_at[v]) for u, v in old_net["laid"]} | {(old_at[v], old_at[u]) for u, v in old_net["laid"]}
same_links = sum(1 for u, v in new_net["laid"] if (new_at[u], new_at[v]) in old_links)
print("roads between two settlements: %d before, %d now; of the new, between the same two places as an old one: %d" % (len(old_net["laid"]), len(new_net["laid"]), same_links))
for name, a, b in (("pink", (233, 0, 255), None), ("purple", (110, 30, 180), None), ("grey", (128, 128, 128), None)):
    for picture in ("Counties.png",):
        before, after = colour(OLD_PICTURES, picture, a), colour(NEW_PICTURES, picture, a)
        print("%s in %s: %d px before, %d now; of the new, on the old %.0f%%, within 1 km of it %.0f%%" % (
            name, picture, before.sum(), after.sum(), 100.0 * (after & before).sum() / after.sum(),
            100.0 * (after & ndimage.binary_dilation(before, iterations=3)).sum() / after.sum()))
