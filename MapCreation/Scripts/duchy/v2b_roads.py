"""Are the roads and bridges right? Checked from the pictures alone.

Usage: v2b_roads.py <folder of the pictures>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize

Image.MAX_IMAGE_PIXELS = None
FOLDER = sys.argv[1]
RED, UMBER, BLUE = (200, 40, 30), (60, 35, 15), (28, 112, 224)
PINK, PURPLE, GREY = (233, 0, 255), (110, 30, 180), (128, 128, 128)
SQUARE = np.ones((3, 3), dtype=bool)
problems = []


def load(name):
    return np.asarray(Image.open(FOLDER + "/" + name).convert("RGB"))


def is_colour(picture, colour):
    return (picture == np.array(colour, dtype=np.uint8)).all(axis=2)


def said(ok, text):
    print(("ok    " if ok else "WRONG ") + text)
    if not ok:
        problems.append(text)


coast, water, counties, settlements, roads, everything = (load(n) for n in ("WorldMapV1.png", "Water.png", "Counties.png", "Settlements.png", "Roads.png", "All.png"))
land = (coast >= 250).all(axis=2)
blue = is_colour(water, BLUE)
road, deck = is_colour(roads, RED), is_colour(roads, UMBER)
dots = (settlements != counties).any(axis=2)
changed = (roads != settlements).any(axis=2)
# Besides road and bridge, Roads.png may add a border's own colour beside a road that runs along
# that border: on land that was white, within 3 px of the road.
beside = changed & ~road & ~deck
by_road = ndimage.distance_transform_edt(~(road | deck)) <= 3.0
border_colour = is_colour(roads, PINK) | is_colour(roads, PURPLE) | is_colour(roads, GREY)
was_white = (settlements == 255).all(axis=2) & land
said(bool((border_colour & by_road & was_white)[beside].all()) and not is_colour(settlements, RED).any() and not is_colour(settlements, UMBER).any(),
     "Roads.png is Settlements.png with road (%d px) and bridge (%d px) added, and %d px of a border's colour beside roads that run along that border; nothing else changed" % (
         road.sum(), deck.sum(), beside.sum()))
said(not (changed & dots).any(), "no dot is drawn over: roads stop at a settlement's rim")

# -- water --------------------------------------------------------------------------------------------
said(int((road & blue).sum()) == 0, "no road pixel lies on water: %d (a road crosses water only as a bridge)" % (road & blue).sum())
said(int((road & ~land).sum()) == 0, "no road pixel is off the land: %d (nothing is drawn at sea but one bridge; there is no ferry)" % (road & ~land).sum())
marks, n_marks = ndimage.label(deck, structure=SQUARE)
index = np.arange(1, n_marks + 1)
over = ndimage.sum_labels(blue, marks, index=index)
off_land = ndimage.sum_labels(~land, marks, index=index)
at_sea = np.flatnonzero(off_land > 0) + 1
said(len(at_sea) == 1, "bridge marks with pixels off the land: %d (the one bridge over the sea, to the island town)" % len(at_sea))
said(bool((over[off_land == 0] > 0).all()), "bridge marks: %d; every one but the sea's is over a river (least %d px of water under a mark)" % (n_marks, over[off_land == 0].min()))
if len(at_sea) == 1:
    mine = marks == at_sea[0]
    ys, xs = np.nonzero(mine)
    pieces, n_land = ndimage.label(land, structure=SQUARE)
    shores = set(np.unique(pieces[ndimage.binary_dilation(mine, structure=SQUARE, iterations=2)]).tolist()) - {0}
    sizes = np.bincount(pieces.ravel())
    said(len(shores) == 2, "the sea's bridge (%d px, x %d to %d, y %d to %d) stands on two pieces of land: %s px and %s px, the mainland and the largest island" % (
        mine.sum(), xs.min(), xs.max(), ys.min(), ys.max(), *sorted((int(sizes[s]) for s in shores), reverse=True)))
    said(int((mine & blue).sum()) == 0, "the sea's bridge is over no river or lake")
# Water 13 px wide or more is a lake: a river is 2 to 8 px. A bridge may stand where a river
# enters or leaves a lake and touch the lake's edge, but none lies over a lake: a third of a
# mark over wide water would be one that does.
wide = ndimage.binary_opening(blue, structure=np.ones((13, 13), dtype=bool))
on_lake = ndimage.sum_labels(wide, marks, index=index)
mark_px = ndimage.sum_labels(deck, marks, index=index)
said(int((on_lake > mark_px / 3.0).sum()) == 0, "no bridge is built over a lake (marks with a third or more of their pixels over water 13 px wide: %d; marks touching such water: %d)" % (
    int((on_lake > mark_px / 3.0).sum()), int((on_lake > 0).sum())))
loose = 0
for i, box in enumerate(ndimage.find_objects(marks), start=1):
    grown = (slice(max(box[0].start - 3, 0), box[0].stop + 3), slice(max(box[1].start - 3, 0), box[1].stop + 3))
    mine = marks[grown] == i
    rim = ndimage.binary_dilation(mine, structure=SQUARE, iterations=2) & ~mine
    loose += int(ndimage.label((road[grown] | dots[grown]) & rim, structure=SQUARE)[1] < 2)
said(loose == 0, "every bridge has road, or a settlement, at both its ends (bridges without: %d)" % loose)

# -- one network --------------------------------------------------------------------------------------
net = road | deck | dots
pieces, n_pieces = ndimage.label(net, structure=SQUARE)
blobs, n_dots = ndimage.label(dots, structure=SQUARE)
homes = ndimage.maximum(pieces, blobs, index=np.arange(1, n_dots + 1)).astype(int)
said(n_dots == 220 and len(set(homes.tolist())) == 1, "settlements: %d, all on one network: any can be reached from any other by road and bridge (networks holding a settlement: %d)" % (
    n_dots, len(set(homes.tolist()))))
stray = len(set(np.unique(pieces[road | deck]).tolist()) - {0}) - 1
said(stray == 0, "no piece of road or bridge stands apart from the network (pieces apart: %d)" % stray)
touching = 0
roads_at = []
for i, box in enumerate(ndimage.find_objects(blobs), start=1):
    grown = (slice(max(box[0].start - 3, 0), box[0].stop + 3), slice(max(box[1].start - 3, 0), box[1].stop + 3))
    mine = blobs[grown] == i
    rim = ndimage.binary_dilation(mine, structure=SQUARE, iterations=2) & ~mine
    arms = ndimage.label((road | deck)[grown] & rim, structure=SQUARE)[1]
    touching += int(arms > 0)
    roads_at.append(arms)
said(touching == n_dots, "every settlement has a road at its dot (%d of %d); roads meeting at a dot: 1 at %d settlements, 2 at %d, 3 or more at %d" % (
    touching, n_dots, roads_at.count(1), roads_at.count(2), sum(1 for a in roads_at if a >= 3)))

# -- no road ends in the open -------------------------------------------------------------------------
lines = road | deck
bones = skeletonize(lines)


def ends_of(mask):
    neighbours = ndimage.convolve(mask.astype(np.uint8), np.ones((3, 3), dtype=np.uint8), mode="constant") - mask
    return mask & (neighbours == 1)


for _ in range(6):                                           # trim the skeleton's whiskers
    bones &= ~ends_of(bones)
tips = ends_of(bones)
# An end is at a settlement if the road it is the end of runs on to a dot within 25 px of it
# (a bridge at a town's edge is longer than the trimming, so the end can stand a little off).
rim = ndimage.binary_dilation(dots, structure=SQUARE, iterations=2)
loose_ends = []
h, w = lines.shape
for y, x in zip(*np.nonzero(tips)):
    window = (slice(max(y - 25, 0), min(y + 26, h)), slice(max(x - 25, 0), min(x + 26, w)))
    near, _ = ndimage.label(lines[window], structure=SQUARE)
    mine = near == near[y - window[0].start, x - window[1].start]
    if not (mine & rim[window]).any():
        loose_ends.append((int(x), int(y)))
said(not loose_ends, "no road ends in the open: every end of a road is at a settlement (ends of road found: %d; of them elsewhere: %s)" % (int(tips.sum()), loose_ends[:12]))

# -- highways -----------------------------------------------------------------------------------------
# A highway is 3 px wide and any other road 2 px: what is left of the red after a 3 x 3 opening is highway.
highway = ndimage.binary_opening(road, structure=SQUARE)
great = highway | deck | dots
found, _ = ndimage.label(great, structure=SQUARE)
pink = dots & is_colour(settlements, PINK)
capitals, n_capitals = ndimage.label(pink, structure=SQUARE)
homes = ndimage.maximum(found, capitals, index=np.arange(1, n_capitals + 1)).astype(int)
said(n_capitals == 9 and len(set(homes.tolist())) == 1, "the nine kingdoms' capitals are joined to each other by highways alone (highway networks holding a capital: %d); highway is %.0f%% of the road pixels" % (
    len(set(homes.tolist())), 100.0 * highway.sum() / road.sum()))

# -- All.png ------------------------------------------------------------------------------------------
said(bool((is_colour(everything, RED) == road).all()) and bool((is_colour(everything, UMBER) == deck).all()) and bool((everything[dots] == settlements[dots]).all()),
     "All.png has the same roads, bridges and dots as Roads.png, none of them under anything")
print()
print("ALL RIGHT: the roads and bridges are sound" if not problems else "PROBLEMS: %d\n  %s" % (len(problems), "\n  ".join(problems)))
