"""How the seats sit: pairs that are close together, and seats hard against a border.

Usage: v5_seats.py <name> <duchy out dir> <folder with that build's Counties.png> [...]
"""
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None


def study(name, out, pictures):
    with open(out + "/county_list_f3.pickle", "rb") as handle:
        listing = pickle.load(handle)
    with open(out + "/settlements.pickle", "rb") as handle:
        settled = pickle.load(handle)
    seats, of_duchy, rank = listing["seats"], np.asarray(listing["of_duchy"]), settled["rank"]
    points = np.array([seats[c] for c in range(1, 221)], dtype=np.float64)
    gap = np.hypot(points[:, None, 0] - points[None, :, 0], points[:, None, 1] - points[None, :, 1]) * 0.335
    np.fill_diagonal(gap, 1e9)
    close = sorted((round(float(gap[a, b]), 1), a + 1, b + 1, rank[a + 1], rank[b + 1], int(of_duchy[a + 1]), int(of_duchy[b + 1]))
                   for a in range(220) for b in range(a + 1, 220) if gap[a, b] < 18.0)
    print("%s: pairs of seats under 18 km apart (km, county, county, ranks, duchies): %s" % (name, close))
    counties = np.asarray(Image.open(pictures + "/Counties.png").convert("RGB"))
    clear = ndimage.distance_transform_edt((counties >= 250).all(axis=2))
    room = {c: float(clear[seats[c][1], seats[c][0]]) for c in range(1, 221)}
    for kind in ("kingdom", "duchy", "county"):
        mine = sorted((round(room[c], 1), c, tuple(int(v) for v in seats[c]), int(of_duchy[c])) for c in room if rank[c] == kind)
        print("  %s seats, room to the nearest line or coast in px: least %s; under 12 px: %d of %d; median %.0f" % (
            kind, mine[:5], sum(1 for m in mine if m[0] < 12), len(mine), np.median([m[0] for m in mine])))


arguments = sys.argv[1:]
for i in range(0, len(arguments), 3):
    study(*arguments[i: i + 3])
