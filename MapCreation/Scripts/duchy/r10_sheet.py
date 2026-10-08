"""A sheet of close-ups of bridges, the largest marks first (the likeliest to be wrong) or a
random lot: 20 to a sheet, each 50 px square shown four times its size.

Usage: r10_sheet.py <look picture> <draft picture> <out png> [largest|random|forks] [skip]
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
LOOK, DRAFT, WRITE_TO = sys.argv[1:4]
HOW = sys.argv[4] if len(sys.argv) > 4 else "largest"
SKIP = int(sys.argv[5]) if len(sys.argv) > 5 else 0
look = np.asarray(Image.open(LOOK).convert("RGB"))
draft = np.asarray(Image.open(DRAFT).convert("RGB"))
deck = (draft[..., 0] == 60) & (draft[..., 1] == 35) & (draft[..., 2] == 15)
road = (draft[..., 0] == 200) & (draft[..., 1] == 40) & (draft[..., 2] == 30)
if HOW == "forks":
    # Places where three or more roads meet: road pixels with much road round them.
    thick = ndimage.uniform_filter(road.astype(np.float32), size=9) * 81
    peaks = (thick == ndimage.maximum_filter(thick, size=25)) & (thick >= 30)
    ys, xs = np.nonzero(peaks)
    order = np.argsort(-thick[ys, xs])
    places = [(int(xs[i]), int(ys[i])) for i in order]
else:
    marks, n = ndimage.label(deck, structure=np.ones((3, 3)))
    sizes = ndimage.sum_labels(deck, marks, index=np.arange(1, n + 1))
    middles = ndimage.center_of_mass(deck, marks, np.arange(1, n + 1))
    order = np.argsort(-sizes) if HOW == "largest" else np.random.default_rng(3).permutation(n)
    places = [(int(middles[i][1]), int(middles[i][0])) for i in order]
places = places[SKIP: SKIP + 20]
sheet = np.full((4 * 204, 5 * 204, 3), 40, dtype=np.uint8)
for i, (x, y) in enumerate(places):
    y0, x0 = max(y - 25, 0), max(x - 25, 0)
    tile = look[y0: y0 + 50, x0: x0 + 50]
    tile = np.repeat(np.repeat(tile, 4, axis=0), 4, axis=1)
    r, c = divmod(i, 5)
    sheet[r * 204: r * 204 + tile.shape[0], c * 204: c * 204 + tile.shape[1]] = tile
Image.fromarray(sheet).save(WRITE_TO)
print("places: %s" % places)
