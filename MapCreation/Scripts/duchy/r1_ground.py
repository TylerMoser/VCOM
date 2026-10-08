"""The ground as a road-builder meets it, at the map's own size.

Saved as plain arrays a process can map without copying:
  passable  land a road's middle can run on: the mainland and the islands, not the lakes, and
            not the last pixel beside a lake or the sea (so a road 2 or 3 px wide never laps
            over them), except under a settlement's dot
  loose     the same without that last pixel, for the ferry's two landings
  sea       everything off the land, the coast's ink included (a ferry's water)
  going     km of effort for each km of road: the kind of country, how steep it is, how high,
            how near a bank or a shore; 3 on a river (a bridge's deck is dear by the metre)
  height    metres, smoothed a little so a road reads the valley and not the pixel
  river     the rivers as drawn
  crossing  km of effort to bridge the river at that cell, by the river's size; less beside a
            settlement; never under its dot, so that a town's bridge shows at the dot's edge
  town      which settlement's dot a cell is under (0 none)

Usage: r1_ground.py <water out dir> <duchy out dir> <roads out dir>
"""
import os
import pickle
import sys
import numpy as np
from scipy import ndimage

WATER, OUT, ROADS = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(ROADS, exist_ok=True)
KM = 0.335
# How hard a road is to make and keep in each kingdom's country, grassland being 1.
COUNTRY = {1: 1.25, 2: 1.25, 3: 1.10, 4: 1.15, 5: 1.00, 6: 1.30, 7: 1.70, 8: 1.15, 9: 1.40}
STEEP = 0.10             # the slope at which a road costs twice as much to carry
HIGH, HIGHER = 1800.0, 800.0   # above HIGH m a road costs more, twice as much HIGHER m further up
BANK, NEAR_BANK = 4.0, 1.5     # the pixel beside a river, and the one beyond it
SHORE, COAST = 1.5, 1.4        # within 3 px of a lake; within 4 px of the sea
DECK = 6.0               # the going on the river itself: a bridge goes straight over
TOWN_BRIDGE = 0.3        # a river is this much cheaper to bridge within BESIDE px of a dot's edge
BESIDE = 10
CLEAR_OF_DOT = 2         # px round a dot in which no bridge is built, so its mark stands apart
NEVER = 1.0e4            # no bridge under a dot
IN_TOWN = 0.6            # the going under a settlement's dot

fields = np.load(OUT + "/fields1.npz")
king, island_king = fields["king"], fields["island_king"]
height, river, lake = fields["height"], fields["river"], fields["lake"]
h, w = king.shape
mainland = king > 0
land = mainland | (island_king > 0)
country = np.where(mainland, king, island_king)
with open(OUT + "/settlements.pickle", "rb") as handle:
    settlements = pickle.load(handle)
centres, rank = settlements["centres"], settlements["rank"]
with open(WATER + "/water2.pickle", "rb") as handle:
    flow2 = pickle.load(handle)["flow"]
sea = ~land

town = np.zeros((h, w), dtype=np.int16)
beside_town = np.zeros((h, w), dtype=bool)
radius = {"kingdom": 13, "duchy": 9, "county": 6}
for c, (x, y) in centres.items():
    r = radius[rank[c]]
    reach = r + BESIDE
    window = (slice(max(y - reach, 0), min(y + reach + 1, h)), slice(max(x - reach, 0), min(x + reach + 1, w)))
    yy, xx = np.ogrid[window[0], window[1]]
    away = (yy - y) ** 2 + (xx - x) ** 2
    beside_town[window] |= away <= reach ** 2
    town[window] = np.where(away <= (r + 0.4) ** 2, c, town[window])
dots = town > 0

loose = land & ~lake
square = np.ones((3, 3), dtype=bool)
passable = loose & ~((ndimage.binary_dilation(lake, structure=square) | ndimage.binary_dilation(sea, structure=square)) & ~dots)

# Height, smoothed inside the land only.
weight = ndimage.gaussian_filter(land.astype(np.float32), 1.5)
smooth = ndimage.gaussian_filter(np.where(land, height, 0.0).astype(np.float32), 1.5) / np.maximum(weight, 1e-3)
smooth = np.where(land, smooth, 0.0).astype(np.float32)
gy, gx = np.gradient(smooth)
slope = np.hypot(gy, gx) / (KM * 1000.0)

going = np.ones((h, w), dtype=np.float32)
for k, factor in COUNTRY.items():
    going[country == k] = factor
going *= 1.0 + np.minimum((slope / STEEP) ** 2, 6.0)
going *= 1.0 + np.maximum(smooth - HIGH, 0.0) / HIGHER
# The desert's roads keep to its water: up to half as much again 30 km from any.
water = river | lake
far = ndimage.distance_transform_edt(~water) * KM
going *= np.where(country == 4, 1.0 + 0.5 * np.minimum(far / 30.0, 1.0), 1.0)
bank = ndimage.binary_dilation(river, structure=square) & ~river
going *= np.where(bank, BANK, np.where(ndimage.binary_dilation(river, structure=square, iterations=2) & ~river, NEAR_BANK, 1.0))
going *= np.where(ndimage.binary_dilation(lake, iterations=3) & ~lake, SHORE, 1.0)
going *= np.where(ndimage.binary_dilation(sea, iterations=4) & land, COAST, 1.0)
# A little unevenness, so that a road over level country is not ruled.
rng = np.random.default_rng(20261012)
rough = ndimage.gaussian_filter(rng.standard_normal((h, w)).astype(np.float32), 2.0)
going *= 1.0 + 0.10 * rough / rough.std()
going[river] = DECK
going = np.where(dots & ~river, going * IN_TOWN, going)
going = np.where(loose, going, 0.0).astype(np.float32)

# Bridging: by the river's size, which is its flow (the drawn width follows it in steps).
flow = np.repeat(np.repeat(ndimage.maximum_filter(flow2, size=7), 2, axis=0), 2, axis=1)[:h, :w]
size = np.where(river, np.maximum(flow, 15.0), 0.0)
crossing = np.where(river, 3.0 + 3.0 * (size / 15.0) ** 0.6, 0.0)
crossing = np.where(beside_town, crossing * TOWN_BRIDGE, crossing)
near_dot = ndimage.binary_dilation(dots, structure=square, iterations=CLEAR_OF_DOT)
crossing = np.where(near_dot & river, NEVER, crossing).astype(np.float32)

for name, array in (("passable", passable), ("loose", loose), ("sea", sea), ("going", going), ("height", smooth), ("river", river),
                    ("crossing", crossing), ("town", town), ("land", land), ("lake", lake), ("flow", flow.astype(np.float32))):
    np.save(ROADS + "/%s.npy" % name, array)
with open(ROADS + "/towns.pickle", "wb") as handle:
    pickle.dump({"centres": centres, "rank": rank}, handle)
dry = passable & ~river
print("going on dry land: median %.2f, 90th %.2f, 99th %.2f, most %.2f" % (*np.percentile(going[dry], [50, 90, 99]), going[dry].max()))
values = crossing[river & ~beside_town]
print("bridging a river away from any town, km of effort: least %.0f, median %.0f, 90th %.0f, most %.0f" % (
    values.min(), np.median(values), np.percentile(values, 90), values.max()))
print("settlements whose dot's middle is not on passable dry land: %s" % [c for c, (x, y) in centres.items() if not dry[y, x]])
print("rivers under a dot: %d settlements" % len(np.unique(town[dots & river])))
print("saved to %s" % ROADS)
