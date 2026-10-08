"""What the river lines that are not drawn are: where each starts and ends, and how long it is.

Usage: e8_stub.py <scratch out dir> <staged source data>
"""
import json
import pickle
import sys
import numpy as np
from PIL import Image

OUT, SRC = sys.argv[1:3]
with open(OUT + "/water/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
rows, cols, flow, lake = water["rows"], water["cols"], water["flow_flat"], water["lake_flat"]
to, sea = water["to"], water["sea"]
rgb = np.asarray(Image.open(SRC + "/LakeMap.png").convert("RGB")).astype(np.int32)
lake_map = rgb[..., 0] + 256 * rgb[..., 1]
with open(SRC + "/Rivers.json", encoding="utf-8") as handle:
    rivers = json.load(handle)
blue = np.asarray(Image.open(sys.argv[3]).convert("RGB")) if len(sys.argv) > 3 else None
for reach in sorted(water["reaches"], key=lambda r: -float(flow[r["cells"]].max())):
    cells = reach["cells"]
    start = [int(cols[cells[0]] * 2), int(rows[cells[0]] * 2)]
    if not any(e["at"] == start for e in rivers["left_out"]):
        continue
    px = float(np.hypot(np.diff(rows[cells] * 2.0), np.diff(cols[cells] * 2.0)).sum())
    last = cells[-1]
    y0, x0, y1, x1 = int(rows[cells[0]] * 2), int(cols[cells[0]] * 2), int(rows[last] * 2), int(cols[last] * 2)
    print("%-6s %d cells, %.1f px from cell to cell, flow %.1f; starts at (%d, %d): in the drainage's lake %d, drawn lake %d; ends at (%d, %d): in the drainage's lake %d, drawn lake %d%s" % (
        reach["end"], len(cells), px, flow[cells].max(), x0, y0, lake[cells[0]], lake_map[y0:y0 + 2, x0:x0 + 2].max(), x1, y1, lake[last], lake_map[y1:y1 + 2, x1:x1 + 2].max(),
        "" if blue is None else "; Water.png is blue at its start: %s, at its end: %s" % (
            bool((blue[y0:y0 + 2, x0:x0 + 2] == (28, 112, 224)).all(axis=2).any()), bool((blue[y1:y1 + 2, x1:x1 + 2] == (28, 112, 224)).all(axis=2).any()))))
widest = max(max(r["drawn_px"]) for r in rivers["rivers"])
print("widest any river is drawn: %d px; narrowest %d px" % (widest, min(min(r["drawn_px"]) for r in rivers["rivers"])))
