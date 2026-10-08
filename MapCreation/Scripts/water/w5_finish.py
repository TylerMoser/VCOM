"""Put the finished rivers picture in MapCreation, with the heights it was worked out from, and
check the picture from the saved file alone.

Usage: w5_finish.py <repo root> <out dir> <factor> <draft picture>
"""
import pickle
import shutil
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT, FACTOR, DRAFT = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
BLUE = (28, 112, 224, 255)
BROWN = (196, 118, 44, 255)
KM = 0.335
BIOMES = ["Tundra Mountains", "Volcanic Mountains / Ruins", "Temperate Mountains", "Desert", "Grassland",
          "Evergreen Temperate Rainforest", "Swamp", "Deciduous Forest", "Tropical Rainforest"]

shutil.copyfile(DRAFT, ROOT + "/MapCreation/Rivers.png")
full = np.load(OUT + "/grid1.npz")
land, mainland, king = full["land"], full["mainland"], full["king"]
h, w = land.shape
with open(OUT + "/water%d.pickle" % FACTOR, "rb") as handle:
    water = pickle.load(handle)

# The heights: tenths of a metre above the sea, sixteen bits, the sea itself nought.
coarse = water["height"].astype(np.float64)
height = ndimage.zoom(coarse, FACTOR, order=1)[:h, :w]
height = np.where(land, np.maximum(height, 0.1), 0.0)
Image.fromarray(np.clip(np.rint(height * 10.0), 0, 65535).astype(np.uint16)).save(ROOT + "/MapCreation/Elevation.png")
print("wrote Elevation.png: highest %.0f m" % height.max())

# -- the check, from the saved picture ---------------------------------------------------------------
picture = np.asarray(Image.open(ROOT + "/MapCreation/Rivers.png").convert("RGBA"))
plain = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
changed = (picture != plain).any(axis=2)
colours, counts = np.unique(picture[changed].reshape(-1, 4), axis=0, return_counts=True)
print("Rivers.png: %d x %d; pixels changed from the coast map: %d, in colours %s" % (
    w, h, changed.sum(), {tuple(int(v) for v in c): int(n) for c, n in zip(colours, counts)}))
blue = (picture[..., :3] == BLUE[:3]).all(axis=2)
brown = (picture[..., :3] == BROWN[:3]).all(axis=2)
sea_blue = (plain[..., 2].astype(int) - plain[..., 0].astype(int) >= 40) & ~land
print("blue on the open sea: %d px; brown on the open sea: %d px; blue off the land (in the coast's ink): %d px" % (
    (blue & sea_blue).sum(), (brown & sea_blue).sum(), (blue & ~land).sum()))
wet = blue & land
print("kingdom  biome                            under water")
for k in range(1, 10):
    here = king == k
    print("   %d   %-32s %5.2f%%" % (k, BIOMES[k - 1], 100.0 * (wet & here).sum() / here.sum()))
print("the whole land: %.2f%% under water (%d of %d px), about %.0f km2" % (
    100.0 * wet.sum() / land.sum(), wet.sum(), land.sum(), wet.sum() * KM * KM))

# Lakes as drawn: blue pieces too broad to be river.
drawn = np.load(OUT + "/drawn%d.npz" % FACTOR)
pools, count = ndimage.label(drawn["lakes"], structure=np.ones((3, 3), dtype=bool))
sizes = ndimage.sum_labels(drawn["lakes"], pools, index=np.arange(1, count + 1)) * KM * KM
print("lakes drawn: %d, %.0f km2 in all; over 100 km2: %d; over 500 km2: %d" % (count, sizes.sum(), (sizes > 100).sum(), (sizes > 500).sum()))
order = np.argsort(-sizes)[:8]
for n in order:
    cy, cx = ndimage.center_of_mass(pools == n + 1)
    print("   %6.0f km2 at (%4.0f, %4.0f), kingdom %d" % (sizes[n], cx, cy, king[int(cy), int(cx)]))
sheds = drawn["shed"]
print("watersheds drawn: %d" % (len(np.unique(sheds)) - 1))

# Rivers: the longest and the biggest, and that every one runs downhill.
flow, z, rows, cols = water["flow_flat"], water["z"], water["rows"], water["cols"]
coarse_king = np.load(OUT + "/grid%d.npz" % FACTOR)["king"]
to_sea = [r for r in water["reaches"] if r["end"] == "sea"]
print("river lines: %d, of which %d reach the sea, %d end in the salt lake, %d join another" % (
    len(water["reaches"]), len(to_sea), sum(r["end"] == "sink" for r in water["reaches"]), sum(r["end"] == "joins" for r in water["reaches"])))
uphill = sum(int((np.diff(z[r["cells"]]) >= 0).sum()) for r in water["reaches"])
print("steps along the rivers that do not go down: %d" % uphill)
def length_km(cells):
    return float(np.hypot(np.diff(rows[cells]), np.diff(cols[cells])).sum()) * KM * FACTOR
print("biggest rivers: flow at the mouth m3/s, length km, source height m, mouth (x, y), kingdoms crossed")
for r in sorted(to_sea, key=lambda r: -float(flow[r["cells"][-1]]))[:10]:
    cells = r["cells"]
    crossed = []
    for k in coarse_king[rows[cells], cols[cells]].tolist():
        if k and (not crossed or crossed[-1] != k):
            crossed.append(k)
    print("   %5.0f  %5.0f  %5.0f  (%4d, %4d)  %s" % (flow[cells[-1]], length_km(cells), z[cells[0]],
          cols[cells[-1]] * FACTOR, rows[cells[-1]] * FACTOR, "-".join(str(k) for k in crossed)))
