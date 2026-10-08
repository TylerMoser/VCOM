"""The hand-drawn coast of WorldMapV1.png, measured: what colours it is made of, how thick the
ink is, where it is broken, what the wave lines are, and how near the shores come to each other.

Usage: y1_coast.py <MapCreation dir> <folder for pictures>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
MAPS, LOOK = sys.argv[1:3]
KM = 0.335
SEA = (181, 235, 255)
EIGHT = np.ones((3, 3), dtype=bool)
image = Image.open(MAPS + "/WorldMapV1.png")
print("WorldMapV1.png: %s, mode %s" % (image.size, image.mode))
coast = np.asarray(image.convert("RGBA"))
rgb = coast[..., :3].astype(np.int32)
h, w = rgb.shape[:2]
land = (rgb >= 250).all(axis=2)
sea = (rgb == np.array(SEA)).all(axis=2)
other = ~land & ~sea
pure_white = (rgb == 255).all(axis=2)
print("land (all of red, green, blue 250 or more): %d px, of it pure white %d; flat sea colour: %d px; everything else (ink, its soft edges, wave lines): %d px" % (
    land.sum(), pure_white.sum(), sea.sum(), other.sum()))
print("alpha: %d to %d; pixels not fully opaque: %d (of them land %d, sea %d, other %d)" % (
    coast[..., 3].min(), coast[..., 3].max(), (coast[..., 3] < 255).sum(), (land & (coast[..., 3] < 255)).sum(), (sea & (coast[..., 3] < 255)).sum(), (other & (coast[..., 3] < 255)).sum()))
dark = rgb.sum(axis=2) < 200
print("of the rest: dark (ink proper, sum of channels under 200) %d; in between %d" % ((other & dark).sum(), (other & ~dark).sum()))

# -- the land's pieces and holes -------------------------------------------------------------------------
for name, structure in (("four", None), ("eight", EIGHT)):
    pieces, n = ndimage.label(land, structure=structure)
    sizes = np.sort(ndimage.sum_labels(land, pieces, index=np.arange(1, n + 1)))[::-1].astype(int)
    print("land pieces by %s neighbours: %d; sizes %s" % (name, n, sizes.tolist()))
off, n_off = ndimage.label(~land, structure=EIGHT)
off_sizes = ndimage.sum_labels(~land, off, index=np.arange(1, n_off + 1)).astype(int)
order = np.argsort(-off_sizes)
print("pieces of everything that is not land (by eight neighbours): %d; sizes %s" % (n_off, off_sizes[order][:12].tolist()))
for i in order[1:12]:
    ys, xs = np.nonzero(off == i + 1)
    print("   a piece of %d px shut in by land at x %d..%d, y %d..%d; of it flat sea %d, dark ink %d" % (
        off_sizes[i], xs.min(), xs.max(), ys.min(), ys.max(), (sea & (off == i + 1)).sum(), (dark & (off == i + 1)).sum()))
open_sea = off == order[0] + 1

# -- gaps: land that touches the sea with no ink between ------------------------------------------------
beside_sea = ndimage.binary_dilation(sea, structure=EIGHT)
gaps = land & beside_sea
print("land pixels touching flat sea colour directly (by eight neighbours): %d" % gaps.sum())
to_land = ndimage.distance_transform_edt(~land)
ring1 = ~land & (to_land <= 1.0)                           # the pixels just outside the land
print("pixels just outside the land: %d; of them dark %d (%.1f%%), flat sea %d, in between %d" % (
    ring1.sum(), (ring1 & dark).sum(), 100.0 * (ring1 & dark).sum() / ring1.sum(), (ring1 & sea).sum(), (ring1 & ~dark & ~sea).sum()))
# Where the ink is thin: walk out from the land and see how far the dark runs.
for reach in (1, 2, 3, 4, 5, 6, 7, 8, 10, 12):
    band = ~land & (to_land > reach - 1) & (to_land <= reach)
    print("   %2d px out from the land: %6d px; dark %5.1f%%, flat sea %5.1f%%, in between %5.1f%%" % (
        reach, band.sum(), 100.0 * (band & dark).sum() / band.sum(), 100.0 * (band & sea).sum() / band.sum(), 100.0 * (band & ~dark & ~sea).sum() / band.sum()))

# -- the ink beside the land, and the wave lines beyond it ----------------------------------------------
ink = dark & ~land
inked, n_ink = ndimage.label(ink, structure=EIGHT)
touches = np.zeros(n_ink + 1, dtype=bool)
touches[np.unique(inked[ndimage.binary_dilation(land, structure=EIGHT, iterations=2) & ink])] = True
touches[0] = False
shore_ink = touches[inked]
waves = ink & ~shore_ink
wave_pieces = int((~touches[1:]).sum())
print("dark ink: %d px in %d pieces; joined to the land's edge %d px in %d pieces; standing apart in the sea (wave lines) %d px in %d pieces" % (
    ink.sum(), n_ink, shore_ink.sum(), touches.sum(), waves.sum(), wave_pieces))
if waves.any():
    away = to_land[waves]
    print("   wave lines stand %.1f to %.1f px from the land (median %.1f); the furthest dark pixel of any kind is %.1f px out" % (away.min(), away.max(), np.median(away), to_land[ink].max()))
# Thickness of the ink joined to the land, measured outward from the land's edge.
reach = np.where(shore_ink, to_land, 0.0)
# for each land-edge pixel, the furthest shore-ink pixel whose nearest land pixel it is
_, (iy, ix) = ndimage.distance_transform_edt(~land, return_indices=True)
thick = np.zeros((h, w), dtype=np.float32)
ys, xs = np.nonzero(shore_ink)
np.maximum.at(thick, (iy[ys, xs], ix[ys, xs]), to_land[ys, xs].astype(np.float32))
edge = land & ndimage.binary_dilation(~land, structure=EIGHT)
t = thick[edge]
print("the ink's thickness outward from each of %d pixels of land's edge: none %d (%.2f%%); median %.1f px, 10th %.1f, 90th %.1f, 99th %.1f, most %.1f" % (
    edge.sum(), (t == 0).sum(), 100.0 * (t == 0).mean(), np.median(t[t > 0]), np.percentile(t[t > 0], 10), np.percentile(t[t > 0], 90), np.percentile(t[t > 0], 99), t.max()))
for lo, hi in ((0, 0), (0.5, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 9), (9, 12), (12, 100)):
    share = ((t >= lo) & (t <= hi)).mean() if lo == hi else ((t > lo) & (t <= hi)).mean()
    print("      thickness %s: %.1f%% of the land's edge" % ("none" if lo == hi else "%g to %g px" % (lo, hi), 100.0 * share))

# -- how near the shores come to each other -------------------------------------------------------------
# Sea pixels by how far they are from land: a channel narrower than 2 W is all line at width W.
for W in (2, 3, 4, 5, 6):
    line = ~land & (to_land <= W)
    left = ~land & ~line
    pools, n_pools = ndimage.label(left, structure=EIGHT)
    sizes = ndimage.sum_labels(left, pools, index=np.arange(1, n_pools + 1)).astype(int)
    small = np.sort(sizes)[:-1]
    print("a line %d px wide: %d px of line; sea left %d px in %d pieces (all but the open sea: %s%s)" % (
        W, line.sum(), left.sum(), n_pools, np.sort(small)[::-1][:14].tolist(), " ..." if len(small) > 14 else ""))
print("flat sea colour as it is now: %d pieces by eight neighbours" % ndimage.label(sea, structure=EIGHT)[1])
np.save(LOOK + "/coast_thickness.npy", thick)
