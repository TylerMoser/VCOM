"""Before the three changes: the ferry's surroundings, how wide the strait is, and where one
line now lies along another (roads on borders, borders on water).

Usage: x1_look.py <MapCreation dir> <roads out dir> <folder for pictures>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
MAPS, ROADS, LOOK = sys.argv[1:4]
KM = 0.335
SEA, PINK, PURPLE, GREY = (181, 235, 255), (233, 0, 255), (110, 30, 180), (128, 128, 128)
BLUE, RED, UMBER = (28, 112, 224), (200, 40, 30), (60, 35, 15)
EIGHT = np.ones((3, 3), bool)


def load(name):
    return np.asarray(Image.open(MAPS + "/" + name).convert("RGB"))


def is_colour(picture, colour):
    return (picture == np.array(colour, np.uint8)).all(axis=2)


coast, counties, settlements, roads, water, everything = (load(n) for n in (
    "WorldMapV1.png", "Counties.png", "Settlements.png", "Roads.png", "Water.png", "All.png"))
land = (coast >= 250).all(axis=2)
blue = is_colour(water, BLUE)
river, lake = np.load(ROADS + "/river.npy"), np.load(ROADS + "/lake.npy")
print("water in Water.png: %d px; the runs' river mask %d, lake mask %d, both %d; river or lake but not blue %d; blue but neither %d" % (
    blue.sum(), river.sum(), lake.sum(), (river & lake).sum(), ((river | lake) & ~blue).sum(), (blue & ~(river | lake)).sum()))

# 1. The ferry.
red, umber = is_colour(roads, RED), is_colour(roads, UMBER)
at_sea = red & ~land
ys, xs = np.nonzero(at_sea)
print("red off the land (the ferry, and road ends in the ink): %d px, x %d..%d, y %d..%d" % (at_sea.sum(), xs.min(), xs.max(), ys.min(), ys.max()))
pieces, n = ndimage.label(at_sea, structure=EIGHT)
for i in range(1, n + 1):
    py, px = np.nonzero(pieces == i)
    print("   piece %d: %d px, x %d..%d, y %d..%d" % (i, len(px), px.min(), px.max(), py.min(), py.max()))
box = (140, 2020, 340, 2170)
for name, picture in (("roads", roads), ("coast", coast)):
    crop = Image.fromarray(picture[box[1]: box[3], box[0]: box[2]])
    crop.resize((crop.width * 5, crop.height * 5), Image.NEAREST).save(LOOK + "/ferry_%s.png" % name)

# 2. The strait: each piece of land, and how far the big island is from the mainland.
parts, n = ndimage.label(land, structure=EIGHT)
sizes = ndimage.sum_labels(land, parts, index=np.arange(1, n + 1))
order = np.argsort(-sizes)
mainland, island = parts == order[0] + 1, parts == order[1] + 1
to_main, where = ndimage.distance_transform_edt(~mainland, return_indices=True)
shore = island & ~ndimage.binary_erosion(island, structure=EIGHT)
ys, xs = np.nonzero(shore)
gap = to_main[ys, xs]
near = np.argsort(gap)
print("the big island's shore: %d px; nearest the mainland %.1f px (%.1f km)" % (len(xs), gap.min(), gap.min() * KM))
seen = []
for j in near:
    if all(abs(xs[j] - a) + abs(ys[j] - b) > 25 for a, b in seen):
        seen.append((xs[j], ys[j]))
        print("   from the island at (%d, %d) to the mainland at (%d, %d): %.1f px, %.1f km of sea and ink" % (
            xs[j], ys[j], where[1][ys[j], xs[j]], where[0][ys[j], xs[j]], gap[j], gap[j] * KM))
    if len(seen) == 8:
        break
dots = (settlements != counties).any(axis=2)
dys, dxs = np.nonzero(dots & island)
print("the island town's dot: middle (%.1f, %.1f), %d px" % (dxs.mean(), dys.mean(), len(dxs)))
print("   from the dot's middle to the mainland: %.1f px" % to_main[int(round(dys.mean())), int(round(dxs.mean()))])

# 3. Lines along lines. A border's pixels are those of Counties.png; what lies over them.
def runs(hidden, what, least=0):
    pieces, n = ndimage.label(hidden, structure=EIGHT)
    if n == 0:
        print("   %s: none" % what)
        return
    found = ndimage.find_objects(pieces)
    spans = []
    for i, box in enumerate(found, start=1):
        py, px = np.nonzero(pieces[box] == i)
        pts = np.stack([px, py], axis=1).astype(float)
        if len(pts) > 2:
            pts -= pts.mean(axis=0)
            vals, vecs = np.linalg.eigh(np.cov(pts.T))
            along = pts @ vecs[:, 1]
            span = along.max() - along.min() + 1
        else:
            span = float(len(pts))
        spans.append((span, len(px), box[1].start + px.mean(), box[0].start + py.mean()))
    spans.sort(reverse=True)
    lengths = np.array([s[0] for s in spans])
    print("   %s: %d places, %d px; span in px: median %.0f, 90th %.0f, most %.0f; places spanning 12 px or more: %d, 20 or more: %d, 40 or more: %d" % (
        what, n, hidden.sum(), np.median(lengths), np.percentile(lengths, 90), lengths.max(), (lengths >= 12).sum(), (lengths >= 20).sum(), (lengths >= 40).sum()))
    print("      the longest: " + "; ".join("%.0f px at (%d, %d)" % (s[0], s[2], s[3]) for s in spans[:8]))
    return spans


over = red | umber
for name, colour, wide in (("kingdom", PINK, 5), ("duchy", PURPLE, 3), ("county", GREY, 2)):
    border = is_colour(counties, colour) & land
    print("%s borders: %d px on land" % (name, border.sum()))
    runs(border & over, "under roads and bridges")
    runs(border & river & ~lake, "on rivers")
    runs(border & lake, "on lakes")
    shown = is_colour(everything, colour) & border
    print("   showing in All.png: %d of %d (%.1f%%)" % (shown.sum(), border.sum(), 100.0 * shown.sum() / border.sum()))

# 4. Water as it shows now.
shown = is_colour(everything, BLUE)
print("water showing in All.png: %d of %d" % ((shown & blue).sum(), blue.sum()))
hidden = blue & ~shown
for name, colour in (("pink", PINK), ("purple", PURPLE), ("grey", GREY), ("red", RED), ("dark brown", UMBER)):
    under = hidden & is_colour(everything, colour)
    print("   hidden under %s: %d px, of it river %d, lake %d" % (name, under.sum(), (under & river & ~lake).sum(), (under & lake).sum()))
# Lakes that a dot or a line hides.
lakes, n = ndimage.label(lake, structure=EIGHT)
whole = ndimage.sum_labels(lake, lakes, index=np.arange(1, n + 1))
seen_px = ndimage.sum_labels(shown & lake, lakes, index=np.arange(1, n + 1))
share = seen_px / whole
worst = np.argsort(share)[:10]
print("lakes: %d; least of one showing: " % n + "; ".join("%.0f%% of %d px at (%d, %d)" % (
    100 * share[i], whole[i], *reversed(ndimage.center_of_mass(lakes == i + 1))) for i in worst[:6]))
print("lakes with less than half showing: %d; less than three quarters: %d" % ((share < 0.5).sum(), (share < 0.75).sum()))
