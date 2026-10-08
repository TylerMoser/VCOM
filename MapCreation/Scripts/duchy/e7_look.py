"""The rivers as Features.md has them against the rivers as drawn, and how the drainage treats lakes.

Usage: e7_look.py <MapCreation dir> <scratch out dir> <staged folder>
"""
import json
import pickle
import sys
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
MAPS, OUT, TO = sys.argv[1:4]
with open(TO + "/measurements.json", encoding="utf-8") as handle:
    measured = json.load(handle)
facts = measured["facts"]


def brief(value, depth=0):
    if isinstance(value, dict):
        return {k: brief(v, depth + 1) for k, v in list(value.items())[:14]} if depth < 2 else "{%d keys}" % len(value)
    if isinstance(value, list):
        return ("[%d] " % len(value)) + (str(brief(value[0], depth + 1)) if value and depth < 2 else "")
    if isinstance(value, float):
        return round(value, 2)
    return value


for key in ("rivers", "lakes", "water", "watersheds", "land", "height"):
    print("facts.%s: %s" % (key, json.dumps(brief(facts[key]), ensure_ascii=False)[:1500]))
print("facts.files keys:", list(facts["files"].keys()))
print("facts.kingdoms[0]:", json.dumps(brief(facts["kingdoms"][0]), ensure_ascii=False)[:900])
print("facts.duchies[0]:", json.dumps(brief(facts["duchies"][0]), ensure_ascii=False)[:900])
print("facts.counties[0]:", json.dumps(brief(facts["counties"][0]), ensure_ascii=False)[:900])
print("facts.settlements:", json.dumps(brief(facts["settlements"]), ensure_ascii=False)[:900])
print("facts.borders:", json.dumps(brief(facts["borders"]), ensure_ascii=False)[:900])
print("facts.roads:", json.dumps(brief(facts["roads"]), ensure_ascii=False)[:1500])

with open(TO + "/rivers.json", encoding="utf-8") as handle:
    rivers = json.load(handle)
print()
print("left out:", rivers["left_out"])
by_rank = sorted((r for r in rivers["rivers"] if r["sea_rank"]), key=lambda r: r["sea_rank"])
for r in by_rank[:14]:
    print("   sea rank %d: id %d, flow at the end %.0f, largest %.0f, %.0f km, from %s to %s, kingdoms %s" % (
        r["sea_rank"], r["id"], r["flow_m3s"][-1], r["largest_flow_m3s"], r["length_km"], r["points"][0], r["points"][-1], r["kingdoms"]))
lengths = sorted(r["length_km"] for r in rivers["rivers"])
print("lines: %d; total %.0f km; longest %.0f km; middle %.1f km; shortest %.1f km" % (len(lengths), sum(lengths), lengths[-1], lengths[len(lengths) // 2], lengths[0]))
course = sum(float(np.hypot(*np.diff(np.array(r["course"]), axis=0).T).sum()) for r in rivers["rivers"]) * 0.335
print("along the courses (cell to cell): %.0f km" % course)

with open(OUT + "/water/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
rows, cols, to, sea = water["rows"], water["cols"], water["to"], water["sea"]
flow, lake = water["flow_flat"], water["lake_flat"]
every = sorted(water["reaches"], key=lambda r: -float(flow[r["cells"]].max()))
print("reaches: %d; cells in a reach %d to %d; by end %s" % (len(every), min(len(r["cells"]) for r in every), max(len(r["cells"]) for r in every),
                                                         {e: sum(1 for r in every if r["end"] == e) for e in ("sea", "joins", "dry")}))
total = sum(float(np.hypot(np.diff(rows[r["cells"]] * 2.0), np.diff(cols[r["cells"]] * 2.0)).sum()) for r in every) * 0.335
print("   along every reach's cells: %.0f km" % total)

# The drainage and the lakes.
ends = to >= sea
shut = {l["id"] for l in water["lakes"] if l["shut"]}
in_shut = np.isin(lake, list(shut))
grid_land = np.zeros(water["flow"].shape, dtype=bool)
grid_land[rows, cols] = True
pad = np.pad(grid_land, 1)
by_sea = np.zeros(len(rows), dtype=bool)
for dy in (-1, 0, 1):
    for dx in (-1, 0, 1):
        by_sea |= ~pad[rows + 1 + dy, cols + 1 + dx]
print("cells whose water leaves the grid: %d; of them beside a cell that is not land %d; inside a lake without an outlet %d; neither %d" % (
    ends.sum(), (ends & by_sea).sum(), (ends & in_shut).sum(), (ends & ~by_sea & ~in_shut).sum()))
print("cells in lakes: %d; in lakes without an outlet %d (lakes %s)" % ((lake > 0).sum(), in_shut.sum(), sorted(shut)))
inside = lake > 0
print("flow inside lakes: below nought %d, nought to 1 %d, 1 to 15 %d, 15 or more %d" % (
    (flow[inside] < 0).sum(), ((flow[inside] >= 0) & (flow[inside] < 1)).sum(), ((flow[inside] >= 1) & (flow[inside] < 15)).sum(), (flow[inside] >= 15).sum()))
for lid in (1, 2, 508, 1059):
    mine = lake == lid
    if mine.any():
        record = next(l for l in water["lakes"] if l["id"] == lid)
        out = record["outlet"]
        print("   working lake %d (%s, %d cells, shut %s): flow in it least %.1f, middle %.1f, most %.1f; at its outlet %.1f; outlet is in the lake: %s; outlet's next cell in the lake: %s" % (
            lid, record["kind"], mine.sum(), record["shut"], flow[mine].min(), np.median(flow[mine]), flow[mine].max(), flow[out], bool(mine[out]),
            (bool(mine[to[out]]) if to[out] < sea else "leaves the grid")))
salt = lake == 1059
print("salt lake: cells %d; cells of it whose water leaves the grid %d; flow at those %s" % (salt.sum(), (salt & ends).sum(), np.round(flow[salt & ends], 1)[:6]))
print("least_river:", water["least_river"], "; cells with 15 or more: %d; with 5 or more: %d; with 1 or more: %d" % ((flow >= 15).sum(), (flow >= 5).sum(), (flow >= 1).sum()))
