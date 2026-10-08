"""The kingdoms' old borders as a network: the fifteen borders, the seven places three kingdoms
meet, the nine places a border reaches the coast, and for each border the zone its new line may
run in.

A border's zone is the mainland within BAND km of it that is nearer to it than to any other
border, and the land within JOIN km of the meeting places at its ends, where the three borders
that meet there may all run.

Usage: kb1_network.py <duchy out dir> <network out dir> [band km] [join km]
"""
import os
import pickle
import sys
import numpy as np
from scipy import ndimage

OUT, NET = sys.argv[1], sys.argv[2]
BAND = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0
JOIN = float(sys.argv[4]) if len(sys.argv) > 4 else 22.0
os.makedirs(NET, exist_ok=True)
KM = 0.335

king = np.load(OUT + "/fields1.npz")["king"]
mainland = king > 0
h, w = king.shape
square = np.ones((3, 3), dtype=bool)

# Which border each border cell is on: 10 x the lesser kingdom + the greater.
pair_at = np.zeros((h, w), dtype=np.int16)
for dy, dx in ((0, 1), (1, 0), (1, 1), (1, -1)):
    if dx >= 0:
        a = king[: h - dy, : w - dx]; b = king[dy:, dx:]
        sa = (slice(0, h - dy), slice(0, w - dx)); sb = (slice(dy, h), slice(dx, w))
    else:
        a = king[: h - dy, -dx:]; b = king[dy:, : w + dx]
        sa = (slice(0, h - dy), slice(-dx, w)); sb = (slice(dy, h), slice(0, w + dx))
    meet = (a != b) & (a > 0) & (b > 0)
    code = (np.minimum(a, b).astype(np.int16) * 10 + np.maximum(a, b))
    for part in (sa, sb):
        view = pair_at[part]
        view[meet & (view == 0)] = code[meet & (view == 0)]
codes = sorted(int(c) for c in np.unique(pair_at) if c > 0)
print("borders: %d: %s" % (len(codes), codes))

# Where three kingdoms meet: cells with three kingdoms within two pixels.
cover = np.zeros((h, w), dtype=np.int8)
for k in range(1, 10):
    cover += ndimage.binary_dilation(king == k, structure=square, iterations=2)
meeting, n_meet = ndimage.label((cover >= 3) & mainland, structure=square)
joins = []
for i in range(1, n_meet + 1):
    ys, xs = np.nonzero(meeting == i)
    near = king[max(ys.min() - 3, 0): ys.max() + 4, max(xs.min() - 3, 0): xs.max() + 4]
    joins.append({"at": (int(round(ys.mean())), int(round(xs.mean()))), "kingdoms": sorted(int(k) for k in np.unique(near) if k > 0)})
print("meeting places: %d: %s" % (len(joins), [(j["at"][::-1], j["kingdoms"]) for j in joins]))

# Where a border reaches the coast.
border = pair_at > 0
by_sea = border & ndimage.binary_dilation(~mainland, structure=square, iterations=5)
ends_map, n_ends = ndimage.label(by_sea, structure=square)
landings = []
for i in range(1, n_ends + 1):
    ys, xs = np.nonzero(ends_map == i)
    landings.append({"at": (int(round(ys.mean())), int(round(xs.mean()))), "code": int(np.bincount(pair_at[ys, xs]).argmax())})
print("coast ends: %d: %s" % (len(landings), [(l["at"][::-1], l["code"]) for l in landings]))

away, (iy, ix) = ndimage.distance_transform_edt(~border, return_indices=True)
away = (away * KM).astype(np.float32)
nearest = pair_at[iy, ix]
del iy, ix
coastal = mainland & (~mainland[:, :1].repeat(w, axis=1) | True)   # placeholder, replaced below
shore = np.zeros((h, w), dtype=bool)
shore[1:, :] |= mainland[1:, :] & ~mainland[:-1, :]
shore[:-1, :] |= mainland[:-1, :] & ~mainland[1:, :]
shore[:, 1:] |= mainland[:, 1:] & ~mainland[:, :-1]
shore[:, :-1] |= mainland[:, :-1] & ~mainland[:, 1:]
yy, xx = np.mgrid[0:h, 0:w]
segments = []
for code in codes:
    a, b = divmod(code, 10)
    ends = [("join", i) for i, j in enumerate(joins) if a in j["kingdoms"] and b in j["kingdoms"]]
    ends += [("coast", i) for i, l in enumerate(landings) if l["code"] == code]
    zone = mainland & (away <= BAND) & (nearest == code)
    for kind, i in ends:
        if kind == "join":
            y, x = joins[i]["at"]
            zone |= mainland & (np.hypot(yy - y, xx - x) * KM <= JOIN)
    # A zone is one piece: the part its own border lies in.
    parts, n_parts = ndimage.label(zone)
    if n_parts > 1:
        zone = parts == int(np.bincount(parts[(pair_at == code) & zone]).argmax())
    rows = np.flatnonzero(zone.any(axis=1)); cols = np.flatnonzero(zone.any(axis=0))
    box = (slice(max(rows[0] - 2, 0), min(rows[-1] + 3, h)), slice(max(cols[0] - 2, 0), min(cols[-1] + 3, w)))
    sets = {}
    for kind, i in ends:
        if kind == "coast":
            y, x = landings[i]["at"]
            sets[i] = np.argwhere(zone & shore & (np.hypot(yy - y, xx - x) * KM <= BAND))
    segments.append({"code": code, "a": a, "b": b, "ends": ends, "box": box, "zone": zone[box].copy(), "shores": sets})
    print("  border %d|%d: ends %s, zone %d cells, coast cells %s" % (a, b, ends, zone.sum(), {i: len(v) for i, v in sets.items()}))
    assert len(ends) == 2, "a border with %d ends" % len(ends)
with open(NET + "/network.pickle", "wb") as handle:
    pickle.dump({"segments": segments, "joins": joins, "landings": landings, "band": BAND, "join": JOIN}, handle)
np.savez_compressed(NET + "/near.npz", away=away, pair_at=pair_at)
print("saved %s/network.pickle" % NET)
