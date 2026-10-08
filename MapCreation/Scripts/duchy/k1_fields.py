"""What a kingdom's border can settle on, beyond the rivers, lakes, watersheds and ridges the
duchies used: the small lines of the land, and the foot of the high country.

  brook   valley lines too small to be drawn as rivers: every cell gathering VALLEY km2 or more
  spur    the low ridges between one such valley and the next
  above   whether a cell stands higher than the old border does thereabouts: the line between
          above and below is the foot of the higher kingdom's country, running up each valley
          mouth and out round each spur
  weight  how much that line counts, 0 to 1, by how far the two kingdoms' heights differ there
  band    the land within BAND km of an old border, where a border may move
  core    each kingdom's land further in than that, which stays its own

Usage: k1_fields.py <water out dir> <duchy out dir> <kingdom out dir> [band km]
"""
import os
import pickle
import sys
import numpy as np
from scipy import ndimage

WATER, OUT, KING = sys.argv[1], sys.argv[2], sys.argv[3]
BAND = float(sys.argv[4]) if len(sys.argv) > 4 else 30.0
os.makedirs(KING, exist_ok=True)
KM = 0.335
VALLEY = 60.0            # km2 of ground a valley line gathers, at the least
ALONG = 30.0             # km: the old border's height is averaged over about this far along it
ACROSS = 12.0            # km: each kingdom's height near the border is averaged over about this far
LEAST, FULL = 40.0, 200.0   # m of difference at which the foot of the high country starts to count, and counts in full

fields = np.load(OUT + "/fields1.npz")
king, island_king, height = fields["king"], fields["island_king"], fields["height"].astype(np.float32)
river, lake = fields["river"], fields["lake"]
mainland = king > 0
h, w = king.shape
with open(WATER + "/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
drain = np.load(WATER + "/drain2.npz")
rows, cols, to, sea = water["rows"], water["cols"], water["to"], water["sea"]
flow = water["flow_flat"]
n = rows.size
half_shape = water["lake"].shape
cell_km2 = (2 * KM) ** 2
assert (drain["to"] == to).all()
order = drain["order"]                                   # lowest first: a cell's way down is settled before it

# -- valleys and spurs, at half size ---------------------------------------------------------------
gathered = [1] * n
to_list = to.tolist()
for i in order[::-1].tolist():                           # highest first
    d = to_list[i]
    if d != sea:
        gathered[d] += gathered[i]
gathered = np.array(gathered, dtype=np.float64) * cell_km2
valley = gathered >= VALLEY
# Each valley is one line, carried down along its larger branch; a lesser branch ends where it joins.
best_from = np.full(n + 1, -1, dtype=np.int64)
best_size = np.zeros(n + 1)
for i in np.flatnonzero(valley).tolist():
    d = to_list[i]
    if gathered[i] > best_size[d]:
        best_size[d] = gathered[i]
        best_from[d] = i
line = np.zeros(n, dtype=np.int64)
count = 0
is_valley = valley.tolist()
line_list = line.tolist()
for i in order[::-1].tolist():
    if not is_valley[i]:
        continue
    if line_list[i] == 0:
        count += 1
        line_list[i] = count
    d = to_list[i]
    if d != sea and best_from[d] == i:
        line_list[d] = line_list[i]
# Every cell is filed under the valley it runs down to.
under = line_list
for i in order.tolist():                                 # lowest first
    if under[i] == 0 and to_list[i] != sea:
        under[i] = under[to_list[i]]
under = np.array(under)
filed = np.zeros(half_shape, dtype=np.int64)
filed[rows, cols] = under
land2 = np.zeros(half_shape, dtype=bool)
land2[rows, cols] = True
shore, pieces = ndimage.label((filed == 0) & land2)      # what runs straight to the sea: each stretch a piece
filed = np.where(shore > 0, count + shore, filed)
spur2 = np.zeros(half_shape, dtype=bool)
for dy, dx in ((0, 1), (1, 0)):
    a = filed[: half_shape[0] - dy, : half_shape[1] - dx]; b = filed[dy:, dx:]
    spur2[: half_shape[0] - dy, : half_shape[1] - dx] |= (a != b) & (a > 0) & (b > 0)
brook2 = np.zeros(half_shape, dtype=bool)
small = valley & (flow < water["least_river"])
brook2[rows[small], cols[small]] = True


def doubled(grid):
    big = np.repeat(np.repeat(grid, 2, axis=0), 2, axis=1)
    out = np.zeros((h, w), dtype=grid.dtype)
    out[: min(h, big.shape[0]), : min(w, big.shape[1])] = big[:h, :w]
    return out


wet = river | lake
near_river = ndimage.binary_dilation(river, iterations=3)
brook = doubled(brook2) & mainland & ~wet & ~near_river
spur = doubled(spur2) & mainland & ~wet & ~brook
print("valleys gathering %.0f km2 or more: %d lines; brook cells %d, spur cells %d (rivers %d, ridges %d, watershed lines %d)" % (
    VALLEY, count, brook.sum(), spur.sum(), river.sum(), fields["ridge"].sum(), fields["divide"].sum()))

# -- the old borders, the band and the cores ---------------------------------------------------------
edge = np.zeros((h, w), dtype=bool)
for dy, dx in ((0, 1), (1, 0)):
    a = king[: h - dy, : w - dx]; b = king[dy:, dx:]
    meet = (a != b) & (a > 0) & (b > 0)
    edge[: h - dy, : w - dx] |= meet
    edge[dy:, dx:] |= meet
away = ndimage.distance_transform_edt(~edge) * KM
band = mainland & (away <= BAND)
core = np.where(mainland & ~band, king, 0).astype(np.uint8)
print("band of %.0f km: %d cells, %.1f%% of the mainland; cores by kingdom, share of each kingdom: %s" % (
    BAND, band.sum(), 100.0 * band.sum() / mainland.sum(),
    {k: round(float((core == k).sum() / (king == k).sum()), 2) for k in range(1, 10)}))

# -- the foot of the high country --------------------------------------------------------------------
soft = ndimage.gaussian_filter(np.where(mainland, height, 0.0), 2.0) / np.maximum(ndimage.gaussian_filter(mainland.astype(np.float32), 2.0), 1e-3)
sigma = ALONG / KM
on_edge = edge.astype(np.float32)
level = ndimage.gaussian_filter(soft * on_edge, sigma) / np.maximum(ndimage.gaussian_filter(on_edge, sigma), 1e-9)
above = mainland & (soft > level)
# Each kingdom's own height near the border, and the height of the kingdom across it.
sigma = ACROSS / KM
own = np.zeros((h, w), dtype=np.float32)
other = np.zeros((h, w), dtype=np.float32)
mean_of = {}
for k in range(1, 10):
    mine = (king == k).astype(np.float32)
    mean_of[k] = ndimage.gaussian_filter(soft * mine, sigma) / np.maximum(ndimage.gaussian_filter(mine, sigma), 1e-6)
    own = np.where(king == k, mean_of[k], own)
nearest = np.zeros((h, w), dtype=np.uint8)                # the kingdom across the nearest border
far = np.full((h, w), np.inf, dtype=np.float32)
for k in range(1, 10):
    gap = ndimage.distance_transform_edt(king != k).astype(np.float32)
    closer = (gap < far) & (king != k) & mainland
    nearest = np.where(closer, k, nearest).astype(np.uint8)
    far = np.where(closer, gap, far)
for k in range(1, 10):
    other = np.where(nearest == k, mean_of[k], other)
contrast = np.abs(own - other)
weight = np.clip((contrast - LEAST) / (FULL - LEAST), 0.0, 1.0).astype(np.float32)
weight = np.where(band, weight, 0.0).astype(np.float32)
# Specks either side of the line say nothing: a hillock under 3 km2 in the low ground, a hollow in the high.
for value in (True, False):
    bits, count_bits = ndimage.label((above == value) & band)
    sizes = ndimage.sum_labels(np.ones_like(bits, dtype=np.int32), bits, index=np.arange(1, count_bits + 1))
    above = np.where(np.isin(bits, np.flatnonzero(sizes < 27) + 1), not value, above)
print("the foot of the high country counts (weight over 0.5) along %.0f%% of the band; height differences across the borders, m: %s" % (
    100.0 * (weight[band] > 0.5).mean(), {k: int(np.median(contrast[band & (king == k)])) for k in range(1, 10)}))

np.savez_compressed(KING + "/fields.npz", spur=spur, brook=brook, above=above, weight=weight, band=band, core=core, edge=edge,
                    level=level.astype(np.float32), band_km=np.float32(BAND))
print("saved %s/fields.npz" % KING)
