"""The one river line under 3 px long: what runs into it, and what the picture shows there.

Usage: e8b_stub.py <scratch out dir> <staged source data> <Water.png>
"""
import json
import pickle
import sys
import numpy as np
from PIL import Image

OUT, SRC, WATER = sys.argv[1:4]
with open(OUT + "/water/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
rows, cols, flow, lake = water["rows"], water["cols"], water["flow_flat"], water["lake_flat"]
to, sea = water["to"], water["sea"]
index = np.full(water["flow"].shape, -1, dtype=np.int64)
index[rows, cols] = np.arange(len(rows))
a = int(index[1752 // 2, 1290 // 2])
b = int(to[a])
print("the line's first cell: (%d, %d), flow %.1f, lake %d; it runs to (%d, %d), flow %.1f, lake %d" % (cols[a] * 2, rows[a] * 2, flow[a], lake[a], cols[b] * 2, rows[b] * 2, flow[b], lake[b]))
for cell in (a, b):
    feeders = np.flatnonzero(to == cell)
    print("   into (%d, %d) run: %s" % (cols[cell] * 2, rows[cell] * 2, [((int(cols[f] * 2), int(rows[f] * 2)), round(float(flow[f]), 1), int(lake[f])) for f in feeders]))
ends_here = [r for r in water["reaches"] if int(r["cells"][-1]) in (a, b)]
print("   river lines ending on these two cells: %s" % [(r["end"], len(r["cells"]), round(float(flow[r["cells"]].max()), 1), (int(cols[r["cells"][0]] * 2), int(rows[r["cells"][0]] * 2))) for r in ends_here])
through = [r for r in water["reaches"] if a in r["cells"].tolist() or b in r["cells"].tolist()]
print("   river lines holding either cell: %s" % [(r["end"], len(r["cells"]), round(float(flow[r["cells"]].max()), 1), r["cells"].tolist().index(a) if a in r["cells"].tolist() else None,
                                                  r["cells"].tolist().index(b) if b in r["cells"].tolist() else None) for r in through])
blue = (np.asarray(Image.open(WATER).convert("RGB")) == (28, 112, 224)).all(axis=2)
rgb = np.asarray(Image.open(SRC + "/LakeMap.png").convert("RGB")).astype(np.int32)
lake_map = rgb[..., 0] + 256 * rgb[..., 1]
print("Water.png round (1290, 1752), rows 1744 to 1761, columns 1278 to 1301 (# river, L lake, . neither):")
for y in range(1744, 1762):
    print("   " + "".join("L" if lake_map[y, x] else "#" if blue[y, x] else "." for x in range(1278, 1302)))
with open(SRC + "/Rivers.json", encoding="utf-8") as handle:
    rivers = json.load(handle)["rivers"]
near = [(r["id"], r["ends_in"], r["joins"], r["flow_at_end_m3s"], r["points"][0], r["points"][-1]) for r in rivers
        if min(abs(p[0] - 1290) + abs(p[1] - 1752) for p in (r["points"][0], r["points"][-1])) < 8]
print("rivers of Rivers.json starting or ending within 8 px:", near)
