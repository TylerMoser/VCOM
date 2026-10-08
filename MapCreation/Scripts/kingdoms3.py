"""Even out the nine regions by moving where their borders meet, carrying the drawn curves along.

The drawn borders are read as curves (kingdom_net.py). What moves is the handful of points where
three borders meet and where a border meets the coast, the latter only along the coast; each
drawn line is then carried by the shifts of the points on it, smoothly along its length, so it
keeps its own curve. Of all the ways of placing those points that make the nine areas equal, the
one taken stretches and turns the lines least.

Usage: kingdoms3.py <repo root> <out dir> [strain|flow]
"""
import pickle
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage, optimize

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
from kingdom_net import Network, area_of

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT = sys.argv[1], sys.argv[2]
ANCHOR = 2e-5            # weight on plain distance moved, beside the stretching: only settles ties

creation = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
h, w = creation.shape[:2]
white = (creation[..., 0] >= 250) & (creation[..., 1] >= 250) & (creation[..., 2] >= 250)
pieces, count = ndimage.label(white)
sizes = ndimage.sum_labels(white, pieces, index=np.arange(1, count + 1))
mainland = pieces == (int(np.argmax(sizes)) + 1)
islands = white & ~mainland
start = np.load(OUT + "/start_map.npy")
_, (near_y, near_x) = ndimage.distance_transform_edt(~mainland, return_indices=True)
island_y, island_x = np.nonzero(islands)
island_near = (near_y[island_y, island_x], near_x[island_y, island_x])
main_y, main_x = np.nonzero(mainland)
total = main_y.size + island_y.size
target = total / 9.0

with open(OUT + "/network.pickle", "rb") as handle:
    net = pickle.load(handle)
junctions, coasts = net.names()
print("coast %d points, %.0f px round" % (len(net.coast), net.coast_length))
print("borders:")
for key in sorted(net.borders):
    print("  %d|%d  %5.0f px  %s -> %s" % (key[0], key[1], net.length[key], net.ends[key][0][:1] + net.ends[key][0][1:], net.ends[key][1]))
print("strokes:")
for stroke in net.strokes:
    print("  " + "  ".join("%d|%d%s" % (k[0], k[1], "'" if rev else "") for k, rev in stroke))
print("rings:")
for i in net.regions:
    print("  %d: %s" % (i, " ".join("coast" if p[0] == "coast" else "%d|%d%s" % (p[1][0], p[1][1], "'" if p[2] else "") for p in net.rings[i])))

x0 = net.home_x()
drawn_areas = net.areas(x0)
pixel_areas = np.bincount(start[main_y, main_x], minlength=10)[1:].astype(np.float64)
print("as drawn, by outline against by pixels:")
for i, (a, b) in enumerate(zip(drawn_areas, pixel_areas)):
    print("  %d: %9.0f  %9.0f  (%+.3f%%)" % (i + 1, a, b, 100 * (a - b) / b))


def raster(x):
    """The label map the outlines at [x] give, and each kingdom's area with its islands."""
    rings, moved = net.polygons(x)
    image = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(image)
    for i in net.regions:
        draw.polygon([(float(c) + 0.5, float(r) + 0.5) for r, c in rings[i]], fill=i)
    labels = np.asarray(image).copy()
    labels[~mainland] = 0
    bare = mainland & (labels == 0)
    if bare.any():
        _, (fy, fx) = ndimage.distance_transform_edt(labels == 0, return_indices=True)
        labels[bare] = labels[fy[bare], fx[bare]]
    counts = np.bincount(labels[main_y, main_x], minlength=10)[1:].astype(np.float64)
    counts += np.bincount(labels[island_near], minlength=10)[1:]
    return labels, counts, moved


def residuals(x):
    """What is to be made small, as a list whose squares are summed: for each border the
    difference between its two ends' shifts over the root of its length, and, weakly, every
    point's own shift."""
    where, _ = net.unpack(x)
    out = []
    for key, names in net.ends.items():
        a = where[names[0]] - net.home[names[0]]
        b = where[names[1]] - net.home[names[1]]
        out.extend(((b - a) / np.sqrt(net.length[key])).tolist())
    out.extend((np.sqrt(ANCHOR) * (x - x0)).tolist())
    return np.array(out)


def slopes(function, x, step=1.0):
    base = function(x)
    out = np.zeros((base.size, x.size))
    for k in range(x.size):
        up = x.copy(); up[k] += step
        down = x.copy(); down[k] -= step
        out[:, k] = (function(up) - function(down)) / (2 * step)
    return out


def solve(x, wanted, furthest=30.0, rounds=80):
    """Least stretching with the outlines enclosing [wanted]: Newton steps on the two together,
    no point moving more than [furthest] pixels in one."""
    gap = lambda x: (net.areas(x) - wanted)[:-1]            # the last follows from the rest
    for count in range(rounds):
        r = residuals(x); J = slopes(residuals, x)
        g = gap(x); A = slopes(gap, x)
        n, m = x.size, g.size
        system = np.block([[J.T @ J, A.T], [A, np.zeros((m, m))]])
        step = np.linalg.lstsq(system, np.concatenate([-J.T @ r, -g]), rcond=None)[0][:n]
        biggest = np.abs(step).max()
        if biggest > furthest:
            step *= furthest / biggest
        x = x + step
        if biggest < 0.05 and np.abs(g).max() < 30:
            break
    return x, count + 1, float(np.abs(gap(x)).max())


mode = sys.argv[3] if len(sys.argv) > 3 else "strain"

# What the outlines must enclose for the pixels, islands and all, to come out equal: found by
# drawing the result and correcting for what the outlines miss.
labels, counts, _ = raster(x0)
wanted = drawn_areas + (target - counts)
x = x0.copy()
for stage in np.linspace(0.1, 1.0, 10):
    x, rounds, miss = solve(x, drawn_areas + stage * (wanted - drawn_areas))
    print("  %3.0f%% of the way: strain %7.2f, %2d rounds, outlines within %.0f px" % (100 * stage, net.strain(x), rounds, miss))
for again in range(5):
    labels, counts, moved = raster(x)
    worst = np.abs(counts - target).max()
    print("drawn out: worst area error %.0f px (%.3f%%)" % (worst, 100 * worst / target))
    if worst < 150:
        break
    wanted = wanted + (target - counts)
    x, rounds, miss = solve(x, wanted)

where, along = net.unpack(x)
print("areas:  ", " ".join("%d:%.3f%%" % (i + 1, 100 * a / total) for i, a in enumerate(counts)))
print("points moved:")
for name in junctions + coasts:
    shift = where[name] - net.home[name]
    print("  %-28s (%5.0f, %5.0f) -> (%5.0f, %5.0f)   %4.0f px" % (
        "%s %s" % (name[0], "-".join(str(v) for v in name[1:])), net.home[name][1], net.home[name][0], where[name][1], where[name][0], np.hypot(*shift)))
print("borders, length now against as drawn:")
for key in sorted(moved):
    now = float(np.hypot(*np.diff(moved[key], axis=0).T).sum())
    print("  %d|%d  %5.0f  %5.0f  (x%.2f)" % (key[0], key[1], now, net.length[key], now / net.length[key]))


def borders_of(lab):
    lengths = np.zeros((9, 9))
    for dy, dx in ((0, 1), (1, 0)):
        a = lab[: h - dy, : w - dx]; b = lab[dy:, dx:]
        cross = (a != b) & (a > 0) & (b > 0)
        pairs = (a[cross].astype(np.int64) - 1) * 9 + (b[cross].astype(np.int64) - 1)
        tally = np.bincount(pairs, minlength=81).reshape(9, 9)
        lengths += tally + tally.T
    return lengths / 1.27

print("same neighbours as drawn: %s" % bool(((borders_of(start) > 20) == (borders_of(labels) > 20)).all()))
for i in range(1, 10):
    parts, n = ndimage.label(labels == i)
    if n != 1:
        part_sizes = np.sort(ndimage.sum_labels(labels == i, parts, index=np.arange(1, n + 1)))[::-1]
        print("  region %d is in %d pieces: %s" % (i, n, part_sizes[:8].astype(int).tolist()))

np.save(OUT + "/kingdom_map_net_%s.npy" % mode, labels)
with open(OUT + "/kingdom_net_%s.pickle" % mode, "wb") as handle:
    pickle.dump({"x": x, "moved": moved, "where": where, "along": along, "home": net.home,
                 "drawn": net.borders, "strokes": net.strokes}, handle)

palette = np.array([[181, 235, 255], [200, 215, 230], [190, 110, 90], [150, 160, 150], [235, 215, 140],
                    [190, 215, 120], [40, 120, 90], [110, 140, 110], [150, 190, 90], [60, 160, 60]], dtype=np.uint8)
picture = Image.fromarray(palette[labels])
canvas = np.asarray(picture).copy()
canvas[islands] = (255, 255, 255)
canvas[creation[..., :3].astype(np.int32).sum(axis=2) < 300] = 0
picture = Image.fromarray(canvas)
draw = ImageDraw.Draw(picture)
for key, points in net.borders.items():
    draw.line([(float(c) + 0.5, float(r) + 0.5) for r, c in points], fill=(0, 0, 0), width=4)
for key, points in moved.items():
    draw.line([(float(c) + 0.5, float(r) + 0.5) for r, c in points], fill=(233, 0, 255), width=7)
picture.resize((w // 2, h // 2), Image.LANCZOS).save(OUT + "/kingdoms_net_%s_preview.png" % mode)
print("saved kingdoms_net_%s_preview.png (drawn borders black, new pink)" % mode)
