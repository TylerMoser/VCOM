"""What each duchy seat has going for it as its kingdom's capital.

For every duchy seat: how far the kingdom's land is from it by the going (the same costs the
borders were found with), the river it stands on, the sea, its height, how near the kingdom's
border it is, and how good a town site it is. Prints a table and saves it.

Usage: s1_candidates.py <water out dir> <duchy out dir>
"""
import pickle
import sys
import numpy as np
from scipy import ndimage

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
from realm import Realm

WATER, OUT = sys.argv[1], sys.argv[2]
KM = 0.67
half = dict(np.load(OUT + "/fields2.npz"))
with open(OUT + "/duchies_all.pickle", "rb") as handle:
    duchies = pickle.load(handle)
with open(WATER + "/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
flow = water["flow"]
king = half["king"]
land = (king > 0) | (half["island_king"] > 0)
to_sea = ndimage.distance_transform_edt(land) * KM
edge = np.zeros(king.shape, dtype=bool)
for dy, dx in ((0, 1), (1, 0)):
    a = king[: king.shape[0] - dy, : king.shape[1] - dx]; b = king[dy:, dx:]
    meet = (a != b) & (a > 0) & (b > 0)
    edge[: king.shape[0] - dy, : king.shape[1] - dx] |= meet
    edge[dy:, dx:] |= meet
to_border = ndimage.distance_transform_edt(~edge) * KM
big_flow = ndimage.maximum_filter(flow, size=9)          # the largest river within 2.7 km
print("flow grid: %s, most %.0f m3/s; a drawn river is %.0f or more" % (flow.shape, flow.max(), water["least_river"]))

rows = []
number = 0
for k in sorted(duchies):
    realm = Realm(king == k, half, KM, half["island_king"] == k)
    ys, xs = np.nonzero(king == k)
    my, mx = ys.mean(), xs.mean()
    spread = float(np.sqrt(((ys - my) ** 2 + (xs - mx) ** 2).mean())) * KM
    kingdom_flow = float(flow[king == k].max())
    print("kingdom %d: middle (%d, %d) at full size, %.0f km from its middle on average (root mean square), largest river %.0f m3/s" % (
        k, mx * 2, my * 2, spread, kingdom_flow))
    for seat in duchies[k]["seats"]:
        number += 1
        y, x = seat[1] // 2, seat[0] // 2
        cell = realm.cell_at(y, x)
        if cell < 0 or realm.seat_worth[cell] < -50:
            cell = realm.nearest_dry(y, x)
        realm.claim(np.array([cell]), np.zeros(1))
        row = {"duchy": number, "kingdom": k, "seat": seat, "reach": float(realm.far.mean()), "worst": float(np.percentile(realm.far, 95)),
               "flow": float(big_flow[y, x]), "share": float(big_flow[y, x]) / kingdom_flow, "sea": float(to_sea[y, x]),
               "height": float(half["height"][y, x]), "border": float(to_border[y, x]), "worth": float(half["seat"][y, x]),
               "off_middle": float(np.hypot(y - my, x - mx)) * KM / spread}
        rows.append(row)
        print("  duchy %2d %-12s land %3.0f km off by the going (95%% within %3.0f); river %5.0f m3/s (%3.0f%% of the kingdom's largest); sea %3.0f km; %4.0f m up; border %3.0f km; site %4.1f; %.2f of the kingdom's spread from its middle" % (
            number, seat, row["reach"], row["worst"], row["flow"], 100 * row["share"], row["sea"], row["height"], row["border"], row["worth"], row["off_middle"]))
with open(OUT + "/capital_candidates.pickle", "wb") as handle:
    pickle.dump(rows, handle)
print("saved")
