"""What the roads have to work with: how steep the land is in each kingdom, how wide the rivers
are drawn, how far apart the settlements are, and which colours Settlements.png already uses.

Usage: r0_look.py <repo root> <water out dir> <duchy out dir>
"""
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import Delaunay

Image.MAX_IMAGE_PIXELS = None
ROOT, WATER, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
M = 335.0
fields = np.load(OUT + "/fields1.npz")
king, height, river, lake = fields["king"], fields["height"], fields["river"], fields["lake"]
island_king = fields["island_king"]
land = (king > 0) | (island_king > 0)
print("height: %s, %.0f to %.0f m on land" % (height.dtype, height[land].min(), height[land].max()))
for sigma in (0.0, 1.5, 3.0):
    z = ndimage.gaussian_filter(np.where(land, height, 0.0), sigma) / np.maximum(ndimage.gaussian_filter(land.astype(np.float32), sigma), 1e-3) if sigma else height
    gy, gx = np.gradient(z)
    slope = np.hypot(gy, gx) / M
    inner = ndimage.binary_erosion(land, iterations=3) & ~river & ~lake
    print("slope with heights smoothed %.1f px, percent rise: median, 75th, 90th, 99th percentile by kingdom" % sigma)
    for k in range(1, 10):
        s = slope[inner & (king == k)] * 100
        print("  kingdom %d: %5.1f %5.1f %5.1f %5.1f   heights %4.0f to %4.0f m, median %4.0f" % (
            k, *np.percentile(s, [50, 75, 90, 99]), height[king == k].min(), height[king == k].max(), np.median(height[king == k])))

half = ndimage.distance_transform_edt(river)
wide = np.clip(2.0 * ndimage.maximum_filter(half, size=11), 2.0, 12.0)
values = wide[river]
print("river cells: %d; drawn width in px, share of river cells: %s" % (river.sum(), {int(v): round(float((np.round(values) == v).mean()), 3) for v in range(2, 13)}))
print("lake cells: %d (%d lakes)" % (lake.sum(), ndimage.label(lake)[1]))

with open(OUT + "/settlements.pickle", "rb") as handle:
    settlements = pickle.load(handle)
centres, rank = settlements["centres"], settlements["rank"]
points = np.array([centres[c] for c in sorted(centres)], dtype=np.float64)
tri = Delaunay(points)
edges = set()
for a, b, c in tri.simplices:
    for u, v in ((a, b), (b, c), (a, c)):
        edges.add((min(u, v), max(u, v)))
lengths = np.array([np.hypot(*(points[u] - points[v])) for u, v in edges])
print("settlements: %d; Delaunay edges: %d; length px: median %.0f, 90th %.0f, longest %.0f; over 330 px: %d" % (
    len(points), len(edges), np.median(lengths), np.percentile(lengths, 90), lengths.max(), (lengths > 330).sum()))
on_river = 0
for x, y in points.astype(int):
    on_river += bool(river[max(y - 12, 0): y + 13, max(x - 12, 0): x + 13].any())
print("settlements with a drawn river within 12 px (4 km): %d" % on_river)

picture = np.asarray(Image.open(ROOT + "/MapCreation/Settlements.png").convert("RGBA"))
for name, colour in (("road red", (200, 40, 30)), ("bridge dark", (60, 35, 15)), ("vermilion", (215, 60, 20)), ("black", (0, 0, 0)), ("orange", (255, 140, 0))):
    same = (picture[..., 0] == colour[0]) & (picture[..., 1] == colour[1]) & (picture[..., 2] == colour[2])
    print("pixels already %s %s in Settlements.png: %d" % (name, colour, same.sum()))
strait = ~land
print("mainland %d px, islands %d px" % ((king > 0).sum(), (island_king > 0).sum()))
