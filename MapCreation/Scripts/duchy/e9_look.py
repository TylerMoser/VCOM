"""Three things the check of the source data tripped on: which counties the islands are, which
counties are in more than one piece, and what a river's course carries inside a lake.

Usage: e9_look.py <MapCreation dir> <staged source data>
"""
import json
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
MAPS, SRC = sys.argv[1:3]
EIGHT = np.ones((3, 3), dtype=bool)
county = np.asarray(Image.open(SRC + "/CountyMap.png")).astype(np.int32)
drawn = np.asarray(Image.open(SRC + "/CountyMapAsDrawn.png")).astype(np.int32)
land = county > 0
for name, structure in (("4 neighbours", None), ("8 neighbours", EIGHT)):
    pieces, n = ndimage.label(land, structure=structure)
    sizes = np.bincount(pieces.ravel())[1:]
    main = int(np.argmax(sizes)) + 1
    isles = (pieces > 0) & (pieces != main)
    print("land pieces joined through %s: %d; the mainland %d px, the rest %d px; counties off the mainland: %s; px of county 220 on the mainland: %d" % (
        name, n, sizes.max(), isles.sum(), {int(c): int((county[isles] == c).sum()) for c in np.unique(county[isles])}, ((pieces == main) & (county == 220)).sum()))
pieces, n = ndimage.label(land)
main = int(np.argmax(np.bincount(pieces.ravel())[1:])) + 1
with open(SRC + "/Regions.json", encoding="utf-8") as handle:
    regions = json.load(handle)
duchy_of = {c["number"]: c["duchy"] for c in regions["counties"]}
for c in range(1, 221):
    for what, labels in (("fitted", county), ("as drawn", drawn)):
        parts, k = ndimage.label(labels == c, structure=EIGHT)
        if k > 1:
            sizes = sorted(np.bincount(parts.ravel())[1:].tolist(), reverse=True)
            spots = ndimage.center_of_mass(labels == c, parts, range(1, k + 1))
            on_main = [bool((pieces[parts == i] == main).all()) for i in range(1, k + 1)] if what == "fitted" else "-"
            print("county %d (duchy %d), %s: %d pieces of %s px at %s; on the mainland: %s" % (c, duchy_of[c], what, k, sizes[:8], [(int(x), int(y)) for y, x in spots][:8], on_main))

rgb = np.asarray(Image.open(SRC + "/DrainageFlow.png").convert("RGB")).astype(np.int32)
flow = (rgb[..., 0] + 256 * rgb[..., 1]) / 32.0
rgb = np.asarray(Image.open(SRC + "/DrainageLakes.png").convert("RGB")).astype(np.int32)
lakes = rgb[..., 0] + 256 * rgb[..., 1]
with open(SRC + "/Rivers.json", encoding="utf-8") as handle:
    rivers = json.load(handle)["rivers"]
dry, wet, low = [], [], []
for r in rivers:
    for x, y in r["course"][:-1]:
        c, rr = int(round((x - 0.5) / 2)), int(round((y - 0.5) / 2))
        (wet if lakes[rr, c] else dry).append(flow[rr, c])
        if not lakes[rr, c] and flow[rr, c] < 14.9:
            low.append((r["id"], x, y, round(float(flow[rr, c]), 1)))
print("cells of courses outside any lake: %d, carrying %.2f m3/s at the least; inside a lake: %d, carrying %.2f at the least (below 15: %d)" % (
    len(dry), min(dry), len(wet), min(wet), sum(1 for v in wet if v < 15)))
print("   outside a lake and under 14.9:", low[:12])
last = [flow[int(round((r["course"][-1][1] - 0.5) / 2)), int(round((r["course"][-1][0] - 0.5) / 2))] for r in rivers]
print("   the last cell of a course carries %.1f at the least" % min(last))
