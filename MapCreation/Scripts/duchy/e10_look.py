"""Do all drawn rivers carry 15 m3/s? Where they do not, why.

Usage: e10_look.py <staged source data> <scratch out dir>
"""
import json
import pickle
import sys
import numpy as np
from PIL import Image

SRC, OUT = sys.argv[1:3]
with open(SRC + "/Rivers.json", encoding="utf-8") as handle:
    rivers = json.load(handle)["rivers"]
rgb = np.asarray(Image.open(SRC + "/DrainageLakes.png").convert("RGB")).astype(np.int32)
lakes = rgb[..., 0] + 256 * rgb[..., 1]
rgb = np.asarray(Image.open(SRC + "/DrainageFlow.png").convert("RGB")).astype(np.int32)
flow = (rgb[..., 0] + 256 * rgb[..., 1]) / 32.0
with open(SRC + "/Drainage.json", encoding="utf-8") as handle:
    working = {l["id"]: l for l in json.load(handle)["lakes"]}


def cell(point):
    return int(round((point[1] - 0.5) / 2)), int(round((point[0] - 0.5) / 2))


small = [r for r in rivers if r["flow_m3s"][0] < 14.95]
print("rivers: %d; carrying under 15 m3/s at their first point: %d; of those starting in a lake of the drainage: %d; at a drawn lake: %d" % (
    len(rivers), len(small), sum(1 for r in small if lakes[cell(r["course"][0])]), sum(1 for r in small if r["from_lake"])))
print("   the least any carries at its first point: %.1f; points in all carrying under 15: %d of %d" % (
    min(r["flow_m3s"][0] for r in rivers), sum(1 for r in rivers for v in r["flow_m3s"] if v < 14.95), sum(len(r["flow_m3s"]) for r in rivers)))
for r in sorted(small, key=lambda r: r["flow_m3s"][0])[:12]:
    first = cell(r["course"][0])
    lake = int(lakes[first])
    under = [v for v in r["flow_m3s"] if v < 14.95]
    reach = 0.0
    for a, b, v in zip(r["points"][:-1], r["points"][1:], r["flow_m3s"]):
        if v < 14.95:
            reach += float(np.hypot(b[0] - a[0], b[1] - a[1]))
    print("   river %d (%s, %.0f m3/s at its end): %.1f at its first point %s; drainage lake there %d (%s, drawn as %s); under 15 for %d points, %.0f px; from_lake %s" % (
        r["id"], r["ends_in"], r["flow_at_end_m3s"], r["flow_m3s"][0], r["points"][0], lake, working[lake]["kind"] if lake else "-", working[lake]["drawn_as"] if lake else "-", len(under), reach, r["from_lake"]))
starts_in_lake = [r for r in rivers if lakes[cell(r["course"][0])]]
print("rivers whose course starts in a lake of the drainage: %d (from_lake given: %d); of them carrying 15 or more there: %d" % (
    len(starts_in_lake), sum(1 for r in starts_in_lake if r["from_lake"]), sum(1 for r in starts_in_lake if r["flow_m3s"][0] >= 14.95)))
not_lake = [r for r in small if not lakes[cell(r["course"][0])]]
print("carrying under 15 at the start and not starting in a lake: %s" % [(r["id"], r["flow_m3s"][0], r["points"][0]) for r in not_lake][:10])
with open(OUT + "/water/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
print("least_river:", water["least_river"], "; keys:", sorted(k for k in water if k not in ("flow", "height", "lake", "shed")))
