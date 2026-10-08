"""Even areas with the drawn curves themselves, laid out as the smooth flow laid the land out.

kingdoms2.py's flow says where everything should go, but leaves its lines hooked at the coast
and bellied between their ends. Here the points where borders meet, and where they meet the
coast, are put as near as may be to where the flow carried them, and each drawn line is carried
between its points by kingdom_net.py, keeping its own curve; the points are then adjusted until
the nine areas, islands included, are equal.

Usage: kingdoms4.py <repo root> <out dir> <name> [junction weight] [coast weight] [strain weight]
"""
import pickle
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
from kingdom_net import Network
from net_solve import solve

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT, NAME = sys.argv[1], sys.argv[2], sys.argv[3]
JUNCTION_WEIGHT = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
COAST_WEIGHT = float(sys.argv[5]) if len(sys.argv) > 5 else 0.1
STRAIN_WEIGHT = float(sys.argv[6]) if len(sys.argv) > 6 else 0.0

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
del near_y, near_x
main_y, main_x = np.nonzero(mainland)
total = main_y.size + island_y.size
target = total / 9.0

with open(OUT + "/network.pickle", "rb") as handle:
    net = pickle.load(handle)
junctions, coasts = net.names()
x0 = net.home_x()

# Where the flow put each point.
flowed = Network(np.load(OUT + "/kingdom_map_flow.npy"), mainland)
if set(flowed.home) != set(net.home):
    raise SystemExit("the flow's borders do not meet as the drawn ones do")
aim = flowed.home_x()
n_j = 2 * len(junctions)
# The same stretch of coast may be numbered a whole lap apart: take the nearer.
lap = net.coast_length
aim[n_j:] = x0[n_j:] + (aim[n_j:] - x0[n_j:] + lap / 2) % lap - lap / 2
weights = np.concatenate([np.full(n_j, JUNCTION_WEIGHT), np.full(len(coasts), COAST_WEIGHT)])


def raster(x):
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


x = aim.copy()
labels, counts, moved = raster(x)
print("at the flow's points, before any adjusting:", " ".join("%d:%.2f%%" % (i + 1, 100 * a / total) for i, a in enumerate(counts)))
wanted = net.areas(x) + (target - counts)
for again in range(8):
    x, rounds, miss = solve(net, x, wanted, aim, weights, STRAIN_WEIGHT)
    labels, counts, moved = raster(x)
    worst = np.abs(counts - target).max()
    print("pass %d: %2d rounds, outlines within %5.0f px; drawn out, worst area error %6.0f px (%.3f%%)" % (
        again + 1, rounds, miss, worst, 100 * worst / target))
    if worst < 150:
        break
    if miss < 300:
        wanted = wanted + (target - counts)

where, along = net.unpack(x)
flow_where, _ = net.unpack(aim)
print("areas:  ", " ".join("%d:%.3f%%" % (i + 1, 100 * a / total) for i, a in enumerate(counts)))
print("point                         as drawn         where the flow put it   where it is     from drawn  from flow")
for name in junctions + coasts:
    print("  %-26s (%5.0f, %5.0f)   (%5.0f, %5.0f)          (%5.0f, %5.0f)   %5.0f px   %4.0f px" % (
        "%s %s" % (name[0], "-".join(str(v) for v in name[1:])), net.home[name][1], net.home[name][0],
        flow_where[name][1], flow_where[name][0], where[name][1], where[name][0],
        np.hypot(*(where[name] - net.home[name])), np.hypot(*(where[name] - flow_where[name]))))
print("border  length now  as drawn")
for key in sorted(moved):
    now = float(np.hypot(*np.diff(moved[key], axis=0).T).sum())
    print("  %d|%d   %5.0f     %5.0f   x%.2f" % (key[0], key[1], now, net.length[key], now / net.length[key]))


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
island_owner = np.bincount(labels[island_near], minlength=10)[1:]
print("islands go to:", {i + 1: int(v) for i, v in enumerate(island_owner) if v})

np.save(OUT + "/kingdom_map_%s.npy" % NAME, labels)
with open(OUT + "/kingdom_lines_%s.pickle" % NAME, "wb") as handle:
    pickle.dump({"x": x, "moved": moved, "where": where, "along": along}, handle)

palette = np.array([[181, 235, 255], [200, 215, 230], [190, 110, 90], [150, 160, 150], [235, 215, 140],
                    [190, 215, 120], [40, 120, 90], [110, 140, 110], [150, 190, 90], [60, 160, 60]], dtype=np.uint8)
canvas = palette[labels]
canvas[islands] = (255, 255, 255)
canvas[creation[..., :3].astype(np.int32).sum(axis=2) < 300] = 0
picture = Image.fromarray(canvas)
draw = ImageDraw.Draw(picture)
for key, points in net.borders.items():
    draw.line([(float(c) + 0.5, float(r) + 0.5) for r, c in points], fill=(0, 0, 0), width=4)
for key, points in moved.items():
    draw.line([(float(c) + 0.5, float(r) + 0.5) for r, c in points], fill=(233, 0, 255), width=7)
picture.resize((w // 2, h // 2), Image.LANCZOS).save(OUT + "/kingdoms_%s_preview.png" % NAME)
print("saved kingdoms_%s_preview.png (drawn borders black, new pink)" % NAME)
