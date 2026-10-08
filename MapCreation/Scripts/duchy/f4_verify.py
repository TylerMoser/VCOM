"""Check the statements Features.md makes that f1 and f2 did not measure: the coast's shapes,
where the big rivers start, and that every picture's lines hold a fill of either kind.

Usage: f4_verify.py <repo root> <duchy out dir> <facts out dir>
"""
import json
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT, FACTS = sys.argv[1:4]
KM = 0.335
fields = np.load(OUT + "/fields1.npz")
king, island_king = fields["king"], fields["island_king"]
mainland = king > 0
land = mainland | (island_king > 0)
country = np.where(mainland, king, island_king)
h, w = land.shape


def load(name):
    return np.asarray(Image.open(ROOT + "/MapCreation/" + name).convert("RGBA"))


print("is it sea at the lagoon (2090, 1060): %s; at the bay (980, 2580): %s" % (not land[1060, 2090], not land[2580, 980]))
# The lagoon: water nearly shut in by land. Its piece of sea once a 40 px gate is closed.
shut = ndimage.binary_closing(land, structure=np.ones((3, 3)), iterations=25)
inner = shut & ~land
pieces, n = ndimage.label(inner)
sizes = ndimage.sum_labels(inner, pieces, index=np.arange(1, n + 1))
for i in np.argsort(-sizes)[:6]:
    m = ndimage.center_of_mass(pieces == i + 1)
    box = ndimage.find_objects(pieces)[i]
    print("  water shut in behind a gap under 17 km: %.0f km2 about (%d, %d), x %d..%d, y %d..%d" % (
        sizes[i] * KM * KM, m[1], m[0], box[1].start, box[1].stop, box[0].start, box[0].stop))
for name, rows in (("east cape", (1500, 1900)), ("south-east", (3300, 3900)), ("north tip", (0, 120))):
    part = land[rows[0]: rows[1]]
    ys, xs = np.nonzero(part)
    print("  %s: furthest east (%d, %d); furthest north (%d, %d)" % (name, xs.max(), ys[np.argmax(xs)] + rows[0], xs[np.argmin(ys)], ys.min() + rows[0]))
west = land[:, :400]
ys, xs = np.nonzero(west)
print("  west: furthest west (%d, %d)" % (xs.min(), ys[np.argmin(xs)]))
# The comb: where the south-west coast is cut into spits.
comb = (~land)[2000:2400, 400:1150]
print("  sea among the land in x 400..1150, y 2000..2400: %d px" % comb.sum())

with open(FACTS + "/facts.json", encoding="utf-8") as handle:
    facts = json.load(handle)
for i, river in enumerate(facts["rivers"]["mouths"], start=1):
    x, y = river["from"]
    mx, my = river["at"]
    near = country[max(my - 12, 0): my + 13, max(mx - 12, 0): mx + 13]
    print("river %2d: drawn from (%d, %d) in kingdom %d; mouth (%d, %d), kingdoms about it %s" % (
        i, x, y, country[y, x], mx, my, sorted(int(v) for v in np.unique(near) if v > 0)))
x, y = facts["rivers"]["mouths"][10]["at"]
print("river 11's mouth to the lagoon's middle: see above; sea within 20 px of it: %s" % bool((~land[y - 20: y + 21, x - 20: x + 21]).any()))

for name, wanted in (("Kingdoms.png", 23), ("Duchies.png", 58), ("Counties.png", 233), ("Settlements.png", 233)):
    picture = load(name)
    white = (picture[..., :3] >= 250).all(axis=2)
    four = ndimage.label(white)[1]
    eight = ndimage.label(white, structure=np.ones((3, 3)))[1]
    print("%s: white pieces by four neighbours %d, by eight %d (wanted %d)" % (name, four, eight, wanted))
sketch = load("WorldMapRegions.png")
white = (sketch[..., :3] >= 250).all(axis=2)
print("WorldMapRegions.png: white pieces by four neighbours %d" % ndimage.label(white)[1])
