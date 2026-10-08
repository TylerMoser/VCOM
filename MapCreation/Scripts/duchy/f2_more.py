"""More figures for Features.md: where the two rivers that do not reach the sea end, what the
sketch's pink is, the borders' lengths counted one way, the coast's ink, the peaks, the marks'
sizes, and what the lines hide of each other.

Usage: f2_more.py <repo root> <water out dir> <duchy out dir> <roads out dir> <facts out dir>
"""
import json
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, WATER, OUT, ROADS, FACTS = sys.argv[1:6]
KM = 0.335
KM2 = KM * KM


def load(name):
    return np.asarray(Image.open(ROOT + "/MapCreation/" + name).convert("RGBA"))


def is_colour(picture, colour):
    return (picture[..., 0] == colour[0]) & (picture[..., 1] == colour[1]) & (picture[..., 2] == colour[2])


with open(FACTS + "/facts.json", encoding="utf-8") as handle:
    facts = json.load(handle)
for name, entry in facts["files"].items():
    if "other" in entry:
        print("%-22s other colours %7d px, alpha %s" % (name, entry["other"], entry["alpha"]))

fields = np.load(OUT + "/fields1.npz")
king, island_king, lake, river = fields["king"], fields["island_king"], fields["lake"], fields["river"]
mainland = king > 0
land = mainland | (island_king > 0)
country = np.where(mainland, king, island_king)
h, w = land.shape
elevation = np.asarray(Image.open(ROOT + "/MapCreation/Elevation.png")).astype(np.float64) / 10.0

with open(WATER + "/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
rows, cols, flow = water["rows"], water["cols"], water["flow_flat"]
for reach in water["reaches"]:
    if reach["end"] not in ("sea", "joins"):
        cells = reach["cells"]
        y, x = int(rows[cells[-1]] * 2 + 1), int(cols[cells[-1]] * 2 + 1)
        print("a river that ends %s: from (%d, %d) to (%d, %d), %.0f m3/s at most; its last cell is %s, kingdom %d; the nearest lake pixel is %.1f km off" % (
            reach["end"], cols[cells[0]] * 2 + 1, rows[cells[0]] * 2 + 1, x, y, flow[cells].max(),
            "in a lake" if lake[y, x] else "on land", country[y, x], ndimage.distance_transform_edt(~lake[y - 60: y + 61, x - 60: x + 61])[60, 60] * KM))
pools, n = ndimage.label(lake, structure=np.ones((3, 3)))
salt = pools[1509, 2098]
print("the salt lake: %.0f km2, %.1f m up at its middle, heights of its bed %.1f to %.1f m" % (
    (pools == salt).sum() * KM2, elevation[1509, 2098], elevation[pools == salt].min(), elevation[pools == salt].max()))

sketch = load("WorldMapRegions.png")
coast = load("WorldMapV1.png")
pink = is_colour(sketch, (233, 0, 255))
parts, n_parts = ndimage.label(pink, structure=np.ones((3, 3)))
sizes = ndimage.sum_labels(pink, parts, index=np.arange(1, n_parts + 1))
boxes = ndimage.find_objects(parts)
print("the sketch's pink: %d px in %d pieces; pieces: %s" % (pink.sum(), n_parts, sorted(
    ((int(s), (b[1].start, b[0].start, b[1].stop - b[1].start, b[0].stop - b[0].start)) for s, b in zip(sizes, boxes)), reverse=True)[:16]))
differs = (sketch != coast).any(axis=2)
values, tally = np.unique(sketch[differs].reshape(-1, 4), axis=0, return_counts=True)
order = np.argsort(-tally)[:6]
print("the sketch differs from the coast map in %d px; commonest colours there: %s" % (differs.sum(), [(tuple(int(v) for v in values[i]), int(tally[i])) for i in order]))

# Borders, each counted the same way: the pixels down the middle of the drawn line.
county = np.load(OUT + "/county_map_f3.npy")
with open(OUT + "/counties_f3.pickle", "rb") as handle:
    duchy = pickle.load(handle)["duchy"]


def middle_px(labels, same=None):
    core = np.zeros((h, w), dtype=bool)
    for dy, dx in ((0, 1), (1, 0)):
        a = labels[: h - dy, : w - dx]; b = labels[dy:, dx:]
        meet = (a != b) & (a > 0) & (b > 0)
        if same is not None:
            meet &= same[: h - dy, : w - dx] == same[dy:, dx:]
        core[: h - dy, : w - dx] |= meet
    return int(core.sum())


main_county, main_duchy = np.where(mainland, county, 0), np.where(mainland, duchy, 0)
print("borders, pixels down the middle and km: kingdoms %d (%.0f km), duchies %d (%.0f km), counties %d (%.0f km)" % (
    middle_px(king), middle_px(king) * KM, middle_px(main_duchy, king), middle_px(main_duchy, king) * KM,
    middle_px(main_county, main_duchy), middle_px(main_county, main_duchy) * KM))

# The coast's ink: how thick the dark line round the land is.
dark = (coast[..., :3].astype(np.int32).sum(axis=2) < 200)
ink = dark & ndimage.binary_dilation(land, iterations=10) & ~land
deep = ndimage.distance_transform_edt(ink)
spine = ink & (deep == ndimage.maximum_filter(deep, size=5)) & (deep >= 2)
print("the coast's ink: %d dark px beside the land; thickness %.0f px at the median, %.0f at the 90th percentile" % (ink.sum(), np.median(2 * deep[spine] - 1), np.percentile(2 * deep[spine] - 1, 90)))
print("dark px on the coast map in all: %d; of them further than 10 px from land (ripples in the sea): %d" % (dark.sum(), (dark & ~ndimage.binary_dilation(land, iterations=10)).sum()))
print("white px off the land mask: %d; land px that are not white on the coast map: %d" % (((coast[..., :3] >= 250).all(axis=2) & ~land).sum(), (land & ~(coast[..., :3] >= 250).all(axis=2)).sum()))

# Peaks: the highest ground in each kingdom, and the volcanoes.
for k in range(1, 10):
    here = np.where(country == k, elevation, -1.0)
    y, x = np.unravel_index(int(np.argmax(here)), here.shape)
    print("kingdom %d highest point: %.0f m at (%d, %d)" % (k, here[y, x], x, y))
smooth = ndimage.gaussian_filter(elevation, 6.0)
peaks = (smooth == ndimage.maximum_filter(smooth, size=121)) & (country == 2) & (elevation > 900)
ys, xs = np.nonzero(peaks)
print("kingdom 2, tops standing over everything within 20 km: %s" % sorted(((int(elevation[y - 6: y + 7, x - 6: x + 7].max()), (int(x), int(y))) for y, x in zip(ys, xs)), reverse=True))
caldera = pools[266, 1549]
if caldera:
    mine = pools == caldera
    print("the round lake at (1549, 266): %.0f km2, its water at %.0f m, ground within 15 km as high as %.0f m" % (
        mine.sum() * KM2, elevation[mine].min(), elevation[max(266 - 45, 0): 266 + 46, 1549 - 45: 1549 + 46].max()))

# Marks' sizes in the pictures.
roads = load("Roads.png")
settlements = load("Settlements.png")
counties_png = load("Counties.png")
umber = is_colour(roads, (60, 35, 15))
marks, n_marks = ndimage.label(umber, structure=np.ones((3, 3)))
mark_sizes = ndimage.sum_labels(umber, marks, index=np.arange(1, n_marks + 1))
long_side = [max(b[0].stop - b[0].start, b[1].stop - b[1].start) for b in ndimage.find_objects(marks)]
print("bridge marks: %d; px %d to %d, median %d; longest side px %d to %d, median %d" % (n_marks, mark_sizes.min(), mark_sizes.max(), np.median(mark_sizes), min(long_side), max(long_side), np.median(long_side)))
red = is_colour(roads, (200, 40, 30))
at_sea = red & ~land
print("red px off the land: %d" % at_sea.sum())
strait = umber & ~land
strait_mark = marks == marks[strait][0]
print("the bridge over the strait: %d px of it off the land, x %d..%d, y %d..%d; the whole mark %d px, x %d..%d, y %d..%d" % (
    strait.sum(), np.nonzero(strait)[1].min(), np.nonzero(strait)[1].max(), np.nonzero(strait)[0].min(), np.nonzero(strait)[0].max(),
    strait_mark.sum(), np.nonzero(strait_mark)[1].min(), np.nonzero(strait_mark)[1].max(), np.nonzero(strait_mark)[0].min(), np.nonzero(strait_mark)[0].max()))
river_marks = [i for i in range(1, n_marks + 1) if i != marks[strait][0]]
long_axis = []
for i in river_marks:
    py, px = np.nonzero(marks == i)
    pts = np.stack([px, py], axis=1).astype(float)
    pts -= pts.mean(axis=0)
    vals, vecs = np.linalg.eigh(np.cov(pts.T))
    a = pts @ vecs[:, 1]
    long_axis.append(a.max() - a.min() + 1)
print("river bridges' marks: %d; length along the mark %.1f to %.1f px, median %.1f" % (len(river_marks), min(long_axis), max(long_axis), np.median(long_axis)))
# What roads hide of the borders, and where roads cross them.
for name, colour in (("kingdom (pink)", (233, 0, 255)), ("duchy (purple)", (110, 30, 180)), ("county (grey)", (128, 128, 128))):
    before = is_colour(settlements, colour); after = is_colour(roads, colour)
    lost = before & ~after
    crossings = ndimage.label(lost, structure=np.ones((3, 3)))[1]
    print("roads cover %d px of %s lines, in %d places" % (lost.sum(), name, crossings))
dots = (settlements != counties_png).any(axis=2)
print("dots: %d px" % dots.sum())
all_png = load("All.png")
blue = is_colour(all_png, (28, 112, 224))
print("All.png: water px %d; rivers and lakes on land hidden under other marks %d" % (blue.sum(), ((river | lake) & ~blue).sum()))
with open(ROADS + "/network.pickle", "rb") as handle:
    laid = pickle.load(handle)["laid"]
longest = max(laid.items(), key=lambda item: item[1]["km"])
shortest = min(laid.items(), key=lambda item: item[1]["km"])
kms = np.array([r["km"] for r in laid.values()])
print("road links: %d; km %.0f to %.0f, median %.0f; the link over the strait %s" % (len(laid), kms.min(), kms.max(), np.median(kms), [(k, round(v["km"])) for k, v in laid.items() if v["ferry"]]))
