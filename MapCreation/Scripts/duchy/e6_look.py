"""Things the source data's files say about themselves, looked at before they are written down.

Usage: e6_look.py <MapCreation dir> <scratch out dir> <staged folder>
"""
import json
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
MAPS, OUT, TO = sys.argv[1:4]
FACTOR = 2

with open(OUT + "/water/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
grid1, grid2 = np.load(OUT + "/water/grid1.npz"), np.load(OUT + "/water/grid2.npz")
print("grid1:", {k: (grid1[k].shape, str(grid1[k].dtype)) for k in grid1.files})
print("grid2:", {k: (grid2[k].shape, str(grid2[k].dtype)) for k in grid2.files})

# 1. Which layout of the kingdoms did the water work on?
region = np.load(OUT + "/region_map.npy")
final = np.asarray(Image.open(TO + "/KingdomMap.png")).astype(np.int32)
drawn_county = np.asarray(Image.open(TO + "/CountyMapAsDrawn.png")).astype(np.int32)
king1 = grid1["king"].astype(np.int32)
land = grid1["land"]
print("region_map:", region.shape, region.dtype, np.unique(region)[:12])
print("water's king (full size) equals the sketch's regions on land: %d of %d px differ" % ((king1 != region)[land].sum(), land.sum()))
fields = np.load(OUT + "/duchy2/fields1.npz")
print("water's king equals the final kingdoms on land: %d px differ" % ((king1 != fields["king"])[land].sum()))
for k in (5, 7, 9):
    a, b = king1 == k, fields["king"] == k
    print("   kingdom %d: water's layout %d px, final %d px, shared %d px" % (k, a.sum(), b.sum(), (a & b).sum()))

# 2. Flow below nought: where, how much?
flow = water["flow"]
print("flow grid:", flow.shape, flow.dtype, "min %.2f max %.2f" % (np.nanmin(flow), np.nanmax(flow)), "nan %d" % np.isnan(flow).sum())
rows, cols = water["rows"], water["cols"]
on_land = np.zeros(flow.shape, dtype=bool)
on_land[rows, cols] = True
neg = flow < 0
print("cells below nought: %d, of them on land %d; values %s" % (neg.sum(), (neg & on_land).sum(), np.unique(np.round(flow[neg], 2))[:10]))
print("off-land cells: flow values %s" % np.unique(np.round(flow[~on_land], 2))[:6])
ff = water["flow_flat"]
print("flow_flat: min %.3f; below nought %d; below 0.03 %d; equal to grid at cells: %s" % (ff.min(), (ff < 0).sum(), (ff < 0.03125).sum(), bool(np.allclose(ff, flow[rows, cols]))))
lake_flat = water["lake_flat"]
if (ff < 0).any():
    which = np.unique(lake_flat[ff < 0])
    print("   cells below nought lie in lakes:", which[:20], "count", len(which))
    by = {l["id"]: l for l in water["lakes"]}
    print("   kinds:", sorted({by[int(i)]["kind"] for i in which if i > 0}))
    print("   values: min %.1f, median %.1f" % (ff[ff < 0].min(), np.median(ff[ff < 0])))

# 3. Does Elevation.png hold a lake's bed or its surface?
elev = np.asarray(Image.open(MAPS + "/Elevation.png"))
print("Elevation.png:", elev.shape, elev.dtype, elev.min(), elev.max())
elev = elev.astype(np.float64) / 10.0
with open(TO + "/lakes.json", encoding="utf-8") as handle:
    lakes = json.load(handle)["lakes"]
lake_map = np.asarray(Image.open(TO + "/LakeMap.png").convert("RGB")).astype(np.int32)
lake_map = lake_map[..., 0] + 256 * lake_map[..., 1]
height, z = water["height"], water["z"]
zgrid = np.full(flow.shape, np.nan)
zgrid[rows, cols] = z
print("height (half size) equals z at land cells: max difference %.3f" % np.abs(height[rows, cols] - z).max())
for lake in lakes[:6] + lakes[164:166] + lakes[300:302] + lakes[650:652]:
    mine = lake_map == lake["id"]
    values = elev[mine]
    print("   lake %d (%s, %.0f km2): surface_m %.1f; Elevation.png inside it: least %.1f, middle %.1f, most %.1f" % (
        lake["id"], lake["kind"], lake["km2"], lake["surface_m"], values.min(), np.median(values), values.max()))
gap = []
for lake in lakes:
    mine = lake_map == lake["id"] if lake["id"] <= 40 else None
    if mine is not None:
        gap.append(lake["surface_m"] - np.median(elev[mine]))
print("   surface less the middle of Elevation.png inside, the 40 largest lakes: least %.1f, middle %.1f, most %.1f" % (min(gap), np.median(gap), max(gap)))
coarse_level = {l["id"]: l["level"] for l in water["lakes"]}
ids = water["lake"]
inside = ids > 0
level_grid = np.zeros(flow.shape)
level_grid[inside] = [coarse_level[int(i)] for i in ids[inside]]
print("   half size: height less the lake's level, in lake cells: least %.2f, middle %.2f, most %.2f" % (
    (height[inside] - level_grid[inside]).min(), np.median(height[inside] - level_grid[inside]), (height[inside] - level_grid[inside]).max()))

# 4. The working's lakes against the drawn ones.
coarse = np.repeat(np.repeat(ids, FACTOR, axis=0), FACTOR, axis=1)
shown = set(np.unique(coarse[lake_map > 0]).tolist()) - {0}
print("working lakes: %d; of them under some drawn lake: %d; drawn lakes: %d" % (len(water["lakes"]), len(shown), len(lakes)))
missing = [l for l in water["lakes"] if l["id"] not in shown]
print("   not drawn: %d, cells %d to %d, km2 %.1f to %.1f; kinds %s" % (
    len(missing), min(l["cells"] for l in missing), max(l["cells"] for l in missing), min(l["km2"] for l in missing), max(l["km2"] for l in missing),
    {k: sum(1 for l in missing if l["kind"] == k) for k in sorted({l["kind"] for l in missing})}))
print("   a lake record:", {k: (v if not isinstance(v, np.ndarray) else v.shape) for k, v in water["lakes"][10].items()})
print("   a shed record:", water["sheds"][0])
print("   sheds' kingdoms against the final map at their mouths:", [(s["id"], s["kingdom"]) for s in water["sheds"]][:12])

# 5. What the measurements hold, and words that must not be in the folder.
with open(TO + "/measurements.json", encoding="utf-8") as handle:
    text = handle.read()
measured = json.loads(text)
for part in ("facts", "layers", "continent", "allsimple"):
    keys = measured[part]
    print("measurements.%s: %s" % (part, {k: (type(v).__name__ + (str(len(v)) if hasattr(v, "__len__") and not isinstance(v, str) else "")) for k, v in keys.items()}))
import os
for name in sorted(os.listdir(TO)):
    if name.endswith(".json"):
        with open(TO + "/" + name, encoding="utf-8") as handle:
            body = handle.read().lower()
        hits = {word: body.count(word) for word in ("ferry", "ferries", "kingdoms2", "scratchpad", "appdata", "first drawing", "second drawing") if word in body}
        print("%s: %s" % (name, hits or "none of the words"))
