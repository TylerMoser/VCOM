"""Write MapCreation/Kingdoms.png: the coast map with the nine kingdoms' borders in pink, shifted
from the regions sketch so that every kingdom covers the same area.

Needs what the earlier steps left in <out dir>: network.pickle (net_build.py: the sketch's
borders as curves) and kingdom_map_flow.npy (kingdoms2.py: the land flowed within its coast until
the areas are equal, which says where everything should go).

The points where borders meet, and where they meet the coast, are put as near as may be to where
the flow carried them; each sketched line is carried between its points keeping its own curve;
and the points are adjusted until the areas are equal. Equal is judged on the written picture
itself, read back as a paint bucket would fill it, each kingdom counted with its share of the
line and with its islands; the borders are solved again against what that finds until it agrees.

Usage: make_kingdoms.py <repo root> <out dir> <picture to write> [line width]
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
ROOT, OUT, WRITE_TO = sys.argv[1], sys.argv[2], sys.argv[3]
WIDTH = int(sys.argv[4]) if len(sys.argv) > 4 else 5
PINK = (233, 0, 255, 255)          # the colour of the lines in WorldMapRegions.png
INTO_INK = 3                       # pixels a line runs on into the coast's ink
TAIL = 14                          # pixels a line is carried past its last point, to be sure of reaching it
HOLD = 0.001                       # how firmly each point is held to where the flow put it
CLOSE_ENOUGH = 0.0003              # of a ninth: stop when every kingdom is this near it

base = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
h, w = base.shape[:2]
white = (base[..., 0] >= 250) & (base[..., 1] >= 250) & (base[..., 2] >= 250)
pieces, count = ndimage.label(white)
sizes = ndimage.sum_labels(white, pieces, index=np.arange(1, count + 1))
mainland = pieces == (int(np.argmax(sizes)) + 1)
islands = white & ~mainland
land = mainland | islands
total = int(land.sum())
ninth = total / 9.0
allowed = ndimage.binary_dilation(mainland, structure=np.ones((3, 3), dtype=bool), iterations=INTO_INK)
reach = WIDTH // 2
yy, xx = np.mgrid[-reach:reach + 1, -reach:reach + 1]
nib = (yy * yy + xx * xx) <= (reach + 0.5) ** 2

with open(OUT + "/network.pickle", "rb") as handle:
    net = pickle.load(handle)
junctions, coasts = net.names()
x0 = net.home_x()
flowed = Network(np.load(OUT + "/kingdom_map_flow.npy"), mainland)
if set(flowed.home) != set(net.home):
    raise SystemExit("the flow's borders do not meet as the sketched ones do")
aim = flowed.home_x()
n_j = 2 * len(junctions)
lap = net.coast_length             # the same stretch of coast may be numbered a lap apart
aim[n_j:] = x0[n_j:] + (aim[n_j:] - x0[n_j:] + lap / 2) % lap - lap / 2


def drawn(moved):
    """The pixels the borders [moved] take, as one mask."""
    line = np.zeros((h, w), dtype=bool)
    for stroke in net.strokes:
        points = []
        for key, rev in stroke:
            part = moved[key][::-1] if rev else moved[key]
            points.append(part if not points else part[1:])
        points = np.vstack(points)
        first_key, first_rev = stroke[0]
        last_key, last_rev = stroke[-1]
        on_coast = (net.ends[first_key][1 if first_rev else 0][0] == "coast",
                    net.ends[last_key][0 if last_rev else 1][0] == "coast")
        body = Image.new("1", (w, h), 0)
        ImageDraw.Draw(body).line([(float(c) + 0.5, float(r) + 0.5) for r, c in points], fill=1, width=1)
        whole = body.copy()
        pen = ImageDraw.Draw(whole)
        for at_start, coast_end in zip((True, False), on_coast):
            if not coast_end:
                continue
            tip = points[0] if at_start else points[-1]
            back = points[min(4, len(points) - 1)] if at_start else points[-1 - min(4, len(points) - 1)]
            along = (tip - back) / np.hypot(*(tip - back))
            beyond = tip + TAIL * along
            pen.line([(float(tip[1]) + 0.5, float(tip[0]) + 0.5), (float(beyond[1]) + 0.5, float(beyond[0]) + 0.5)], fill=1, width=1)
        body = ndimage.binary_dilation(np.asarray(body, dtype=bool), structure=nib)
        whole = ndimage.binary_dilation(np.asarray(whole, dtype=bool), structure=nib) & allowed
        # A tail may cross a creek and land on the far bank: keep only what joins the stroke itself.
        parts, n = ndimage.label(whole, structure=np.ones((3, 3), dtype=bool))
        keep = np.unique(parts[body & whole])
        line |= np.isin(parts, keep[keep > 0])
    return line


def read_back(picture, guide):
    """The kingdoms as the picture alone shows them: the pieces the pink cuts the mainland into,
    four-connected as a paint bucket fills, named by [guide] (a rough map of which is where), each
    then given the mainland under the line and the islands nearest it. Returns the map, the
    number of pieces, and any scraps of land the line has cut off."""
    whiteish = (picture[..., 0] >= 250) & (picture[..., 1] >= 250) & (picture[..., 2] >= 250)
    found, n = ndimage.label(whiteish)
    found_sizes = ndimage.sum_labels(whiteish, found, index=np.arange(1, n + 1))
    here = np.unique(found[mainland & whiteish])
    here = here[here > 0]
    big = [int(k) for k in here if found_sizes[k - 1] > 20000]
    scraps = [(int(found_sizes[k - 1]),) + tuple(int(v) for v in np.argwhere(found == k).mean(axis=0)[::-1])
              for k in here if found_sizes[k - 1] <= 20000]
    seeds = np.zeros((h, w), dtype=np.uint8)
    for k in big:
        votes = np.bincount(guide[found == k], minlength=10)
        seeds[found == k] = int(np.argmax(votes[1:])) + 1
    _, (ny, nx) = ndimage.distance_transform_edt(seeds == 0, return_indices=True)
    final = np.where(land, seeds[ny, nx], 0).astype(np.uint8)
    return final, len(big), scraps


def guide_of(x):
    rings, moved = net.polygons(x)
    image = Image.new("L", (w, h), 0)
    pen = ImageDraw.Draw(image)
    for i in net.regions:
        pen.polygon([(float(c) + 0.5, float(r) + 0.5) for r, c in rings[i]], fill=i)
    return np.asarray(image), moved


x = aim.copy()
guide, moved = guide_of(x)
picture = base.copy()
picture[drawn(moved)] = PINK
final, n_pieces, scraps = read_back(picture, guide)
areas = np.bincount(final[final > 0], minlength=10)[1:].astype(np.float64)
print("at the flow's points:", " ".join("%d:%+.2f%%" % (i + 1, 100 * (a - ninth) / ninth) for i, a in enumerate(areas)))
wanted = net.areas(x) + (ninth - areas)
for again in range(10):
    x, rounds, miss = solve(net, x, wanted, aim, HOLD, 0.0)
    guide, moved = guide_of(x)
    picture = base.copy()
    picture[drawn(moved)] = PINK
    final, n_pieces, scraps = read_back(picture, guide)
    areas = np.bincount(final[final > 0], minlength=10)[1:].astype(np.float64)
    worst = np.abs(areas - ninth).max() / ninth
    print("pass %d: %2d rounds, outlines within %4.0f px; in the picture %d pieces, %d scraps, worst %.3f%% off a ninth" % (
        again + 1, rounds, miss, n_pieces, len(scraps), 100 * worst))
    if worst < CLOSE_ENOUGH and n_pieces == 9 and not scraps:
        break
    wanted = wanted + (ninth - areas)

Image.fromarray(picture, "RGBA").save(WRITE_TO)
print("wrote %s" % WRITE_TO)
where, along = net.unpack(x)
flow_where, _ = net.unpack(aim)
print("point                        in the sketch     now             moved")
for name in junctions + coasts:
    print("  %-24s (%5.0f, %5.0f)   (%5.0f, %5.0f)   %4.0f px" % (
        "%s %s" % (name[0], "|".join(str(v) for v in name[1:4] if v) if name[0] == "coast" else "-".join(str(v) for v in name[1:])),
        net.home[name][1], net.home[name][0], where[name][1], where[name][0], np.hypot(*(where[name] - net.home[name]))))
print("border  length  in the sketch")
for key in sorted(moved):
    now = float(np.hypot(*np.diff(moved[key], axis=0).T).sum())
    print("  %d|%d   %5.0f   %5.0f" % (key[0], key[1], now, net.length[key]))
np.save(OUT + "/kingdoms_final.npy", final)
with open(OUT + "/kingdoms_final_lines.pickle", "wb") as handle:
    pickle.dump({"x": x, "moved": moved, "where": where, "along": along, "wanted": wanted}, handle)
