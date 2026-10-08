"""Shift the nine regions' borders so each covers the same area, keeping their shapes.

Each region gets one number, its weight. A pixel goes to the region whose signed distance to it,
less that region's weight, is least: with every weight nought that is the region it was in, and a
border between two regions moves, parallel to itself, by half the difference of their weights.
The weights are then solved for so that all nine areas come out equal. To first order that is the
least total movement of the borders that evens the areas.

Usage: kingdoms1.py <repo root> <out dir>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT = sys.argv[1], sys.argv[2]
SMOOTH = 4.0            # pixels: how far the drawn regions' edges are smoothed before anything else

creation = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
h, w = creation.shape[:2]
white = (creation[..., 0] >= 250) & (creation[..., 1] >= 250) & (creation[..., 2] >= 250)
pieces, count = ndimage.label(white)
sizes = ndimage.sum_labels(white, pieces, index=np.arange(1, count + 1))
mainland = pieces == (int(np.argmax(sizes)) + 1)
islands = white & ~mainland
drawn = np.load(OUT + "/region_map.npy")
assert drawn.shape == (h, w) and ((drawn > 0) == mainland).all()

# The regions as drawn, with the pixel steps of the hand-drawn lines smoothed away.
best = np.full((h, w), -1.0, dtype=np.float32)
start = np.zeros((h, w), dtype=np.uint8)
for i in range(1, 10):
    soft = ndimage.gaussian_filter((drawn == i).astype(np.float32), SMOOTH)
    better = soft > best
    start[better] = i
    best[better] = soft[better]
start[~mainland] = 0
del best
moved = int(((start != drawn) & mainland).sum())
print("smoothing the drawn regions moved %d pixels (%.3f%% of the mainland)" % (moved, 100.0 * moved / mainland.sum()))

# Islands go with the nearest mainland.
_, (near_y, near_x) = ndimage.distance_transform_edt(~mainland, return_indices=True)
island_y, island_x = np.nonzero(islands)
island_near = (near_y[island_y, island_x], near_x[island_y, island_x])
del near_y, near_x

main_y, main_x = np.nonzero(mainland)
n_main = main_y.size
total = n_main + island_y.size
target = total / 9.0
print("mainland %d px, islands %d px, target per kingdom %.0f px" % (n_main, island_y.size, target))

# Signed distance from every mainland pixel to each region: negative inside, measured from the
# region's borders with other regions only, never from the coast.
fields = np.empty((9, n_main), dtype=np.float32)
for i in range(1, 10):
    inside = start == i
    others = mainland & ~inside
    to_region = ndimage.distance_transform_edt(~inside)
    to_others = ndimage.distance_transform_edt(~others)
    signed = np.where(inside, -(to_others - 0.5), to_region - 0.5)
    fields[i - 1] = signed[main_y, main_x]
    del to_region, to_others, signed
print("distance fields ready")


def assign(weights):
    labels = np.zeros((h, w), dtype=np.uint8)
    labels[main_y, main_x] = np.argmin(fields - weights[:, None].astype(np.float32), axis=0) + 1
    return labels


def areas_of(labels):
    counts = np.bincount(labels[main_y, main_x], minlength=10)[1:].astype(np.float64)
    counts += np.bincount(labels[island_near], minlength=10)[1:]
    return counts


def borders_of(labels):
    """Length in pixels of each pair's shared border, as a 9x9 matrix."""
    lengths = np.zeros((9, 9))
    for dy, dx in ((0, 1), (1, 0)):
        a = labels[: h - dy, : w - dx]
        b = labels[dy:, dx:]
        cross = (a != b) & (a > 0) & (b > 0)
        pairs = (a[cross].astype(np.int64) - 1) * 9 + (b[cross].astype(np.int64) - 1)
        tally = np.bincount(pairs, minlength=81).reshape(9, 9)
        lengths += tally + tally.T
    return lengths / 1.27          # pixel edges of a slanting line overstate its length by about 4 / pi


weights = np.zeros(9)
labels = assign(weights)
areas = areas_of(labels)
print("as drawn: ", " ".join("%d:%.2f%%" % (i + 1, 100 * a / total) for i, a in enumerate(areas)))
original_adjacent = borders_of(labels) > 20
for step in range(40):
    error = target - areas
    if np.abs(error).max() < 60:
        break
    lengths = borders_of(labels)
    laplacian = np.diag(lengths.sum(axis=1)) - lengths
    delta = 2.0 * np.linalg.pinv(laplacian) @ error
    weights += 0.85 * delta
    weights -= weights.mean()
    labels = assign(weights)
    areas = areas_of(labels)
    print("step %2d: worst error %7.0f px (%.3f%%)" % (step + 1, np.abs(target - areas).max(), 100 * np.abs(target - areas).max() / target))

print("weights:", " ".join("%d:%+.1f" % (i + 1, v) for i, v in enumerate(weights)))
print("areas:  ", " ".join("%d:%.3f%%" % (i + 1, 100 * a / total) for i, a in enumerate(areas)))
lengths = borders_of(labels)
adjacent = lengths > 20
print("borders kept: %s" % bool((adjacent == original_adjacent).all()))
for i in range(9):
    for j in range(i + 1, 9):
        if adjacent[i, j] or original_adjacent[i, j]:
            print("  %d|%d: now %4.0f px long, moved %+6.1f px toward %d%s" % (
                i + 1, j + 1, lengths[i, j], (weights[i] - weights[j]) / 2.0, j + 1,
                "" if adjacent[i, j] == original_adjacent[i, j] else "   <-- adjacency changed"))
for i in range(1, 10):
    parts, n = ndimage.label(labels == i)
    if n != 1:
        part_sizes = np.sort(ndimage.sum_labels(labels == i, parts, index=np.arange(1, n + 1)))[::-1]
        print("  region %d is in %d pieces: %s" % (i, n, part_sizes[:6].astype(int).tolist()))

np.save(OUT + "/kingdom_map.npy", labels)
np.save(OUT + "/start_map.npy", start)
np.save(OUT + "/kingdom_weights.npy", weights)

# A look: new regions in flat colour, the drawn borders in black on top, new borders in white.
palette = np.array([[181, 235, 255], [200, 215, 230], [190, 110, 90], [150, 160, 150], [235, 215, 140],
                    [190, 215, 120], [40, 120, 90], [110, 140, 110], [150, 190, 90], [60, 160, 60]], dtype=np.uint8)
picture = palette[labels]
picture[islands] = (255, 255, 255)
ink = (creation[..., :3].astype(np.int32).sum(axis=2) < 300)
picture[ink] = 0
def edges(lab):
    edge = np.zeros((h, w), dtype=bool)
    for dy, dx in ((0, 1), (1, 0)):
        a = lab[: h - dy, : w - dx]; b = lab[dy:, dx:]
        cross = (a != b) & (a > 0) & (b > 0)
        edge[: h - dy, : w - dx] |= cross
        edge[dy:, dx:] |= cross
    return edge
old_edge = ndimage.binary_dilation(edges(start), iterations=2)
new_edge = ndimage.binary_dilation(edges(labels), iterations=3)
picture[new_edge] = (233, 0, 255)
picture[old_edge] = (0, 0, 0)
Image.fromarray(picture).resize((w // 2, h // 2), Image.LANCZOS).save(OUT + "/kingdoms_preview.png")
print("saved kingdoms_preview.png (old borders black, new pink)")
