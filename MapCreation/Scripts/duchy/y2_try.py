"""The coast with a standard line, tried at several widths, set beside the hand-drawn one; and
where the hand-drawn ink is thin or broken.

Usage: y2_try.py <MapCreation dir> <folder for pictures>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
MAPS, LOOK = sys.argv[1:3]
SEA, WHITE, BLACK = (181, 235, 255), (255, 255, 255), (0, 0, 0)
EIGHT = np.ones((3, 3), dtype=bool)
coast = np.asarray(Image.open(MAPS + "/WorldMapV1.png").convert("RGB"))
rgb = coast.astype(np.int32)
land = (rgb >= 250).all(axis=2)
dark = rgb.sum(axis=2) < 200
to_land = ndimage.distance_transform_edt(~land)

# Where the hand-drawn ink is thin: the ring 3 to 5 px out from the land should be all dark.
ring = ~land & (to_land > 2.0) & (to_land <= 5.0)
thin = ring & ~dark
places, n = ndimage.label(ndimage.binary_dilation(thin, structure=EIGHT, iterations=2), structure=EIGHT)
sizes = ndimage.sum_labels(thin, places, index=np.arange(1, n + 1)).astype(int)
order = np.argsort(-sizes)
print("the ring 3 to 5 px out from the land: %d px, not dark %d px (%.2f%%) in %d places; the largest: %s" % (
    ring.sum(), thin.sum(), 100.0 * thin.sum() / ring.sum(), n,
    [(int(sizes[i]), tuple(int(v) for v in reversed(ndimage.center_of_mass(places == i + 1)))) for i in order[:10]]))
# The hand-drawn line's outer edge: how far out the dark runs, ring by ring, in finer steps.
for reach in np.arange(5.5, 10.01, 0.5):
    band = ~land & (to_land > reach - 0.5) & (to_land <= reach)
    print("   %.1f px out: dark %5.1f%%" % (reach, 100.0 * (band & dark).sum() / max(band.sum(), 1)))

pictures = {}
for W in (5, 6, 7, 8):
    line = ~land & (to_land <= W)
    picture = np.empty_like(coast)
    picture[...] = SEA
    picture[land] = WHITE
    picture[line] = BLACK
    pictures[W] = picture
    left = ~land & ~line
    pools, n_pools = ndimage.label(left, structure=EIGHT)
    sizes = np.sort(ndimage.sum_labels(left, pools, index=np.arange(1, n_pools + 1)).astype(int))[::-1]
    # sea that the hand-drawn picture shows and this would ink over, and the other way
    was_sea = (rgb == np.array(SEA)).all(axis=2)
    print("a line %d px wide: %d px; sea in %d pieces (beside the open sea: %s); flat sea of the drawing inked over: %d px; dark ink of the drawing become sea: %d px" % (
        W, line.sum(), n_pools, sizes[1:].tolist(), (was_sea & line).sum(), (dark & left).sum()))
    # channels: sea narrower than 3 px left between two lines
    slim = left & ~ndimage.binary_opening(left, structure=np.ones((3, 3), dtype=bool))
    print("      sea left in slivers under 3 px wide: %d px" % slim.sum())

views = {"strait": (150, 2030, 180, 130, 4), "comb": (480, 2060, 600, 330, 1), "lagoon": (1990, 960, 220, 200, 3), "islets": (520, 2230, 260, 110, 3),
         "north": (1480, 0, 200, 110, 4), "southeast": (2850, 3480, 230, 180, 3), "cape": (2900, 1640, 150, 130, 4)}
for name, (x, y, w, h, scale) in views.items():
    tiles = [coast[y: y + h, x: x + w]] + [pictures[W][y: y + h, x: x + w] for W in (5, 7)]
    sheet = Image.new("RGB", (3 * w * scale + 2 * 8, h * scale), (200, 60, 60))
    for i, tile in enumerate(tiles):
        sheet.paste(Image.fromarray(tile).resize((w * scale, h * scale), Image.NEAREST), (i * (w * scale + 8), 0))
    sheet.save(LOOK + "/try_%s.png" % name)
print("saved the sheets: the drawing, a line 5 px wide, a line 7 px wide")
