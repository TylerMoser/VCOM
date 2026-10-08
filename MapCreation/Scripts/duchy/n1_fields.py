"""The fields d1_fields.py and d1b_ridges.py made, again, for the kingdoms as Kingdoms2.png has
them.

Only two of the fields depend on the kingdoms: which kingdom a pixel is in, and how good a place
it is for a seat (a seat keeps 14 km clear of its kingdom's border). Everything else (heights,
water, watershed lines, ridges, the going) is the land's own and is carried over unchanged. The
recipe for the seats is d1_fields.py's; it is first run on the old kingdoms and compared with
what d1_fields.py saved, to be sure it is the same recipe.

Usage: n1_fields.py <old duchy out dir> <new kingdoms .npy> <new duchy out dir>
"""
import os
import sys
import numpy as np
from scipy import ndimage

OLD, KINGDOMS, NEW = sys.argv[1:4]
os.makedirs(NEW, exist_ok=True)
KM = 0.335

full = dict(np.load(OLD + "/fields1.npz"))
half = dict(np.load(OLD + "/fields2.npz"))
h, w = full["king"].shape
hh, hw = half["king"].shape
mainland = full["king"] > 0
islands = full["island_king"] > 0
land = mainland | islands
height, river, lake = full["height"], full["river"], full["lake"]

# What does not depend on the kingdoms.
coast = ndimage.distance_transform_edt(land) * KM
wide = np.clip(2.0 * ndimage.maximum_filter(ndimage.distance_transform_edt(river), size=11), 2.0, 12.0)
river_near = ndimage.maximum_filter(np.where(river, wide, 0.0), size=13)
big_lake, n = ndimage.label(lake)
lake_sizes = ndimage.sum_labels(lake, big_lake, index=np.arange(1, n + 1)) * KM * KM
lake_near = ndimage.maximum_filter(np.isin(big_lake, np.flatnonzero(lake_sizes >= 40.0) + 1), size=13)
worth = 1.1 * river_near + 1.5 * (coast < 4.0) + 2.0 * ((coast < 5.0) & (river_near >= 2.0)) + 1.5 * lake_near
worth -= np.maximum(height - 1200.0, 0.0) / 350.0


def seat_of(king):
    """How good a place for a seat each pixel is, the kingdoms being [king] (islands included)."""
    border = np.zeros((h, w), dtype=bool)
    border[:-1, :] |= (king[:-1, :] != king[1:, :]) & land[:-1, :] & land[1:, :]
    border[:, :-1] |= (king[:, :-1] != king[:, 1:]) & land[:, :-1] & land[:, 1:]
    border_far = ndimage.distance_transform_edt(~border) * KM
    seat = worth - 4.0 * (border_far < 14.0)
    return np.where(land & ~lake & ~river, seat, -99.0).astype(np.float32), border_far


def blocks(field):
    return field[: hh * 2, : hw * 2].reshape(hh, 2, hw, 2)


old_king = np.where(mainland, full["king"], full["island_king"])
again, _ = seat_of(old_king)
gap = float(np.abs(again - full["seat"]).max())
print("the seats' recipe, run on the old kingdoms, against what was saved: greatest difference %.6f" % gap)
assert gap < 1e-4, "not the recipe d1_fields.py used"
assert float(np.abs(blocks(again).max(axis=(1, 3)) - half["seat"]).max()) < 1e-4

new = np.load(KINGDOMS).astype(np.uint8)
assert new.shape == (h, w) and ((new > 0) == mainland).all(), "the new kingdoms are not on the same mainland"
moved = mainland & (new != full["king"])
print("mainland in another kingdom than before: %d px, %.0f km2, %.2f%%" % (moved.sum(), moved.sum() * KM * KM, 100.0 * moved.sum() / mainland.sum()))
new_all = np.where(mainland, new, full["island_king"])
seat, border_far = seat_of(new_all)
dry = land & ~lake & ~river
print("dry land within 14 km of a kingdom's border: %.1f%% (was %.1f%%)" % (
    100.0 * ((border_far < 14.0) & dry).sum() / dry.sum(), 100.0 * ((again < full["seat"].max() + 1) & dry & (np.abs(worth - 4.0 - again) < 1e-4)).sum() / dry.sum()))
full["king"] = new
full["seat"] = seat
np.savez_compressed(NEW + "/fields1.npz", **full)

# Half size: a cell has the kingdom of its lower-right pixel, as before; where that pixel is off
# the mainland, of whichever of its pixels is on it.
picked = new[1: hh * 2: 2, 1: hw * 2: 2]
other = blocks(new).max(axis=(1, 3))
king2 = np.where(half["king"] > 0, np.where(picked > 0, picked, other), 0).astype(np.uint8)
assert ((king2 > 0) == (half["king"] > 0)).all()
old_picked = full["king"][1: hh * 2: 2, 1: hw * 2: 2]
print("half size: %d cells of mainland; %d in another kingdom than before (%.2f%%)" % (
    (king2 > 0).sum(), ((king2 != half["king"]) & (king2 > 0)).sum(), 100.0 * ((king2 != half["king"]) & (king2 > 0)).sum() / (king2 > 0).sum()))
half["king"] = king2
half["seat"] = blocks(seat).max(axis=(1, 3))
np.savez_compressed(NEW + "/fields2.npz", **half)
sizes = np.bincount(new[mainland], minlength=10)[1:] * KM * KM
print("kingdoms' mainland, km2: %s" % np.round(sizes).astype(int).tolist())
print("saved to %s" % NEW)
