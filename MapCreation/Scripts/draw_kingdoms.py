"""Draw a solved set of kingdom borders on the coast map, and check the picture by itself.

Each drawn stroke is laid down as one line in the regions file's pink, carried a few pixels
into the coast's ink so that every kingdom is sealed for a paint-bucket fill and nothing strays
into the sea. The check then reads the finished picture back with no help from the solver: the
pink must cut the mainland into exactly nine pieces, and their areas, each with its share of the
line and of the islands, are counted.

Usage: draw_kingdoms.py <repo root> <out dir> <name> <picture to write> [line width]
"""
import pickle
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
from kingdom_net import Network  # noqa: F401  (the pickled network needs its class)

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT, NAME, WRITE_TO = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
WIDTH = int(sys.argv[5]) if len(sys.argv) > 5 else 5
PINK = (233, 0, 255, 255)          # the colour of the lines in WorldMapRegions.png
INTO_INK = 3                       # pixels a line runs on into the coast's ink
TAIL = 14                          # pixels a line is carried past its last point, to be sure of reaching it

base = Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA")
pixels = np.asarray(base)
h, w = pixels.shape[:2]
white = (pixels[..., 0] >= 250) & (pixels[..., 1] >= 250) & (pixels[..., 2] >= 250)
pieces, count = ndimage.label(white)
sizes = ndimage.sum_labels(white, pieces, index=np.arange(1, count + 1))
mainland = pieces == (int(np.argmax(sizes)) + 1)
islands = white & ~mainland
allowed = ndimage.binary_dilation(mainland, structure=np.ones((3, 3), dtype=bool), iterations=INTO_INK)

with open(OUT + "/network.pickle", "rb") as handle:
    net = pickle.load(handle)
with open(OUT + "/kingdom_lines_%s.pickle" % NAME, "rb") as handle:
    solved = pickle.load(handle)
moved = solved["moved"]

line = np.zeros((h, w), dtype=bool)
for stroke in net.strokes:
    points = []
    for key, rev in stroke:
        part = moved[key][::-1] if rev else moved[key]
        points.append(part if not points else part[1:])
    points = np.vstack(points)
    first_key, first_rev = stroke[0]
    last_key, last_rev = stroke[-1]
    ends_on_coast = (net.ends[first_key][1 if first_rev else 0][0] == "coast",
                     net.ends[last_key][0 if last_rev else 1][0] == "coast")
    body = Image.new("1", (w, h), 0)
    ImageDraw.Draw(body).line([(float(c) + 0.5, float(r) + 0.5) for r, c in points], fill=1, width=WIDTH, joint="curve")
    whole = body.copy()
    draw = ImageDraw.Draw(whole)
    for at_start, on_coast in zip((True, False), ends_on_coast):
        if not on_coast:
            continue
        tip = points[0] if at_start else points[-1]
        back = points[min(4, len(points) - 1)] if at_start else points[-1 - min(4, len(points) - 1)]
        along = (tip - back) / np.hypot(*(tip - back))
        beyond = tip + TAIL * along
        draw.line([(float(tip[1]) + 0.5, float(tip[0]) + 0.5), (float(beyond[1]) + 0.5, float(beyond[0]) + 0.5)], fill=1, width=WIDTH)
    whole = np.asarray(whole, dtype=bool) & allowed
    # A tail may cross a creek and land on the far bank: keep only what joins the stroke itself.
    parts, n = ndimage.label(whole, structure=np.ones((3, 3), dtype=bool))
    keep = np.unique(parts[np.asarray(body, dtype=bool) & whole])
    line |= np.isin(parts, keep[keep > 0])

result = pixels.copy()
result[line] = PINK
Image.fromarray(result, "RGBA").save(WRITE_TO)
print("wrote %s: %d x %d, %d pink pixels, lines %d px wide" % (WRITE_TO, w, h, int(line.sum()), WIDTH))

# -- the check, from the written picture alone -----------------------------------------------
picture = np.asarray(Image.open(WRITE_TO).convert("RGBA"))
pink = (picture[..., 0] == PINK[0]) & (picture[..., 1] == PINK[1]) & (picture[..., 2] == PINK[2])
land = (picture[..., 0] >= 250) & (picture[..., 1] >= 250) & (picture[..., 2] >= 250)
found, n = ndimage.label(land)                       # four-connected, as a paint bucket fills
found_sizes = ndimage.sum_labels(land, found, index=np.arange(1, n + 1))
on_mainland = np.unique(found[mainland & land])
on_mainland = on_mainland[on_mainland > 0]
big = [int(k) for k in on_mainland if found_sizes[k - 1] > 20000]
small = [int(k) for k in on_mainland if found_sizes[k - 1] <= 20000]
print("the pink cuts the mainland into %d pieces%s" % (
    len(big), "" if not small else ", and leaves %d scraps of %s px" % (len(small), sorted(int(found_sizes[k - 1]) for k in small))))
for k in small:
    ys, xs = np.nonzero(found == k)
    print("   scrap of %d px at (%d, %d)" % (found_sizes[k - 1], xs.mean(), ys.mean()))

# Which piece is which kingdom: by the solver's own map of them.
solver_map = np.load(OUT + "/kingdom_map_%s.npy" % NAME)
kingdom_of = {}
for k in big:
    votes = np.bincount(solver_map[found == k], minlength=10)
    kingdom_of[k] = int(np.argmax(votes[1:])) + 1
if sorted(kingdom_of.values()) != list(range(1, 10)):
    print("!! the pieces are not the nine kingdoms: %s" % sorted(kingdom_of.values()))
# Every mainland pixel under the line, and every island, goes with the nearest piece.
seeds = np.zeros((h, w), dtype=np.uint8)
for k, kingdom in kingdom_of.items():
    seeds[found == k] = kingdom
_, (ny, nx) = ndimage.distance_transform_edt(seeds == 0, return_indices=True)
final = np.where(mainland | islands, seeds[ny, nx], 0).astype(np.uint8)
total = int((mainland | islands).sum())
areas = np.bincount(final[final > 0], minlength=10)[1:]
print("kingdom   pixels    share    against a ninth")
for i, a in enumerate(areas):
    print("   %d    %8d   %.3f%%   %+.3f%%" % (i + 1, a, 100.0 * a / total, 100.0 * (a - total / 9.0) / (total / 9.0)))
print("islands by kingdom:", {int(k): int(v) for k, v in zip(*np.unique(final[islands], return_counts=True))})
np.save(OUT + "/kingdom_final_%s.npy" % NAME, final)
