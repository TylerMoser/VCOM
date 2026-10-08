"""Rivers that lose water on the way: the most each carries against what it carries at its end.

Usage: e14_look.py <the source data's folder>
"""
import json
import sys
import numpy as np
from PIL import Image

SRC = sys.argv[1]
rgb = np.asarray(Image.open(SRC + "/DrainageFlow.png").convert("RGB")).astype(np.int32)
flow = (rgb[..., 0] + 256 * rgb[..., 1]) / 32.0
rgb = np.asarray(Image.open(SRC + "/DrainageLakes.png").convert("RGB")).astype(np.int32)
lakes = rgb[..., 0] + 256 * rgb[..., 1]
with open(SRC + "/Rivers.json", encoding="utf-8") as handle:
    rivers = json.load(handle)["rivers"]


def cell(point):
    return int(round((point[1] - 0.5) / 2)), int(round((point[0] - 0.5) / 2))


rows = []
for r in rivers:
    own = r["course"][:-1] if r["ends_in"] == "river" else r["course"]
    carried = np.array([flow[cell(p)] for p in own])
    in_lake = np.array([lakes[cell(p)] > 0 for p in own])
    last = float(carried[-1])
    dry = carried[~in_lake]
    falls = int((np.diff(carried) < -0.05).sum())
    rows.append((r["id"], r["sea_rank"], r["ends_in"], r["kingdoms"], float(carried.max()), last, r["flow_at_end_m3s"], falls, bool(in_lake[-1])))
losing = [row for row in rows if row[4] - row[5] > 0.5]
print("rivers: %d; whose water at the end is more than 0.5 m3/s under the most they carry: %d" % (len(rows), len(losing)))
print("   of those, ending inside a lake of the drainage: %d; by where they end: %s" % (sum(1 for row in losing if row[8]), {e: sum(1 for row in losing if row[2] == e) for e in ("sea", "river", "salt lake")}))
for row in sorted(losing, key=lambda row: row[5] - row[4])[:25]:
    print("   river %d (sea rank %s, ends in %s, kingdoms %s): most %.1f, at its end %.1f (file: %.1f); steps down %d; ends in a lake cell: %s" % row)
print("the 14 largest to reach the sea:")
for row in sorted((row for row in rows if row[1] and row[1] <= 14), key=lambda row: row[1]):
    print("   rank %d, river %d, kingdoms %s: most %.1f, at its mouth %.1f" % (row[1], row[0], row[3], row[4], row[5]))
by_end = sorted((row for row in rows if row[2] == "sea"), key=lambda row: -row[5])
print("ranked by the water at the mouth instead: %s" % [(row[1], round(row[5])) for row in by_end[:16]])
