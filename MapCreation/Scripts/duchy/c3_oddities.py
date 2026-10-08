"""Find what looks wrong in a county draft: marks that are not borders, and counties of odd shape.

Usage: c3_oddities.py <repo root> <duchy out dir> <tag> <picture>
"""
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT, TAG, PICTURE = sys.argv[1:5]
KM = 0.335
base = np.asarray(Image.open(ROOT + "/MapCreation/Duchies.png").convert("RGBA"))
saved = np.asarray(Image.open(PICTURE).convert("RGBA"))
county = np.load(OUT + "/county_map_%s.npy" % TAG)
with open(OUT + "/county_list_%s.pickle" % TAG, "rb") as handle:
    listing = pickle.load(handle)
of_duchy, seats = listing["of_duchy"], listing["seats"]
fields = np.load(OUT + "/fields1.npz")
mainland = fields["king"] > 0
grey = (saved != base).any(axis=2)
h, w = grey.shape

# Grey that does not part two counties: every grey pixel should have two different counties
# within two pixels of it.
low = ndimage.minimum_filter(np.where(mainland, county, 32000), size=5)
high = ndimage.maximum_filter(np.where(mainland, county, 0), size=5)
idle = grey & mainland & (low == high)
bits, n = ndimage.label(idle, structure=np.ones((3, 3)))
print("grey pixels that part nothing: %d, in %d marks" % (idle.sum(), n))
for i, box in enumerate(ndimage.find_objects(bits)[:30], start=1):
    print("  mark %d: %d px at x %d..%d, y %d..%d" % (i, (bits[box] == i).sum(), box[1].start, box[1].stop, box[0].start, box[0].stop))

# Shape: how much of the circle round its own middle a county fills, how far its seat is from
# its middle, and how long it is for its width.
print("county: duchy, km2, seat, fills of its circle, long to wide, seat off middle in km")
rows = []
for c in range(1, len(of_duchy)):
    mine = county == c
    ys, xs = np.nonzero(mine)
    my, mx = ys.mean(), xs.mean()
    reach = np.hypot(ys - my, xs - mx).max()
    cov = np.cov(np.vstack([xs, ys]))
    values = np.sort(np.linalg.eigvalsh(cov))
    seat = seats[c]
    rows.append((ys.size / (np.pi * reach * reach), c, int(of_duchy[c]), ys.size * KM * KM, seat, float(np.sqrt(values[1] / values[0])),
                 float(np.hypot(seat[0] - mx, seat[1] - my) * KM), (int(mx), int(my))))
rows.sort()
for fill, c, d, km2, seat, stretch, off, middle in rows[:16]:
    print("  county %3d: duchy %2d, %4.0f km2, seat %s, middle %s, fills %.2f, long to wide %.1f, seat %3.0f km off" % (c, d, km2, seat, middle, fill, stretch, off))
fills = np.array([r[0] for r in rows]); stretches = np.array([r[5] for r in rows]); offs = np.array([r[6] for r in rows])
print("fills of circle: least %.2f, median %.2f; long to wide: median %.2f, most %.2f; seat off middle: median %.0f km, most %.0f km" % (
    fills.min(), np.median(fills), np.median(stretches), stretches.max(), np.median(offs), offs.max()))
with open(OUT + "/county_shapes_%s.pickle" % TAG, "wb") as handle:
    pickle.dump(rows, handle)
