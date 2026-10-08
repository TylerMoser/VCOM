"""Check Roads.png from the pictures in MapCreation alone, with nothing the scripts kept.

Usage: r7_final_check.py <repo root>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT = sys.argv[1]
ROAD, BRIDGE = (200, 40, 30), (60, 35, 15)


def load(name):
    return np.asarray(Image.open(ROOT + "/MapCreation/" + name).convert("RGBA"))


def is_colour(picture, colour):
    return (picture[..., 0] == colour[0]) & (picture[..., 1] == colour[1]) & (picture[..., 2] == colour[2])


roads, settlements, counties, water, coast = load("Roads.png"), load("Settlements.png"), load("Counties.png"), load("Water.png"), load("WorldMapV1.png")
print("sizes: %s %s" % (roads.shape, settlements.shape))
changed = (roads != settlements).any(axis=2)
values, tally = np.unique(roads[changed].reshape(-1, 4), axis=0, return_counts=True)
print("Roads.png differs from Settlements.png in %d pixels, of colours %s" % (changed.sum(), {tuple(int(v) for v in c): int(n) for c, n in zip(values, tally)}))
print("neither colour was in Settlements.png before: %s" % bool(not is_colour(settlements, ROAD).any() and not is_colour(settlements, BRIDGE).any()))
road, deck = is_colour(roads, ROAD), is_colour(roads, BRIDGE)
dots = (settlements != counties).any(axis=2)
print("settlement dots: %d px, of them changed: %d" % (dots.sum(), (dots & changed).sum()))
white_land = (coast[..., :3] >= 250).all(axis=2)
sea_blue = (coast[..., 2].astype(np.int32) - coast[..., 0].astype(np.int32) >= 40)
at_sea = (road | deck) & ~white_land
print("road pixels off the white land of the coast map: %d (bridge pixels among them: %d)" % (at_sea.sum(), (deck & ~white_land).sum()))
if at_sea.any():
    ys, xs = np.nonzero(at_sea)
    print("  all within x %d..%d, y %d..%d: the ferry" % (xs.min(), xs.max(), ys.min(), ys.max()))
blue = is_colour(water, (28, 112, 224))
print("road pixels on the water of Water.png: %d; bridge pixels on it: %d of %d" % ((road & blue).sum(), (deck & blue).sum(), deck.sum()))
marks, n = ndimage.label(deck, structure=np.ones((3, 3)))
over = ndimage.sum_labels(blue, marks, index=np.arange(1, n + 1))
print("bridge marks: %d; each lies over water in Water.png: %s (least %d px of water under a mark)" % (n, bool((over > 0).all()), over.min()))
# Each bridge mark has road, or a settlement, at both ends: grow it a little and count what it touches.
loose_ends = 0
for i, box in enumerate(ndimage.find_objects(marks), start=1):
    grown = (slice(max(box[0].start - 3, 0), box[0].stop + 3), slice(max(box[1].start - 3, 0), box[1].stop + 3))
    mine = marks[grown] == i
    rim = ndimage.binary_dilation(mine, structure=np.ones((3, 3)), iterations=2) & ~mine
    ends = ndimage.label((road[grown] | dots[grown]) & rim, structure=np.ones((3, 3)))[1]
    loose_ends += int(ends < 2)
print("bridge marks without road or a settlement at two ends: %d" % loose_ends)

# Joined: every dot reached from every other along road, bridge and dot; the ferry's dashes closed up first.
ferry = ndimage.binary_dilation(road & ~white_land, structure=np.ones((3, 3)), iterations=3) & ~white_land
net = road | deck | dots | ferry
pieces, n_pieces = ndimage.label(net, structure=np.ones((3, 3)))
blobs, n_dots = ndimage.label(dots, structure=np.ones((3, 3)))
homes = ndimage.maximum(pieces, blobs, index=np.arange(1, n_dots + 1)).astype(int)
print("settlements: %d; pieces of road network holding them: %d (1 means every one can be reached from every other)" % (n_dots, len(set(homes.tolist()))))
touching = 0
for i, box in enumerate(ndimage.find_objects(blobs), start=1):
    grown = (slice(max(box[0].start - 2, 0), box[0].stop + 2), slice(max(box[1].start - 2, 0), box[1].stop + 2))
    mine = blobs[grown] == i
    rim = ndimage.binary_dilation(mine, structure=np.ones((3, 3))) & ~mine
    touching += int(((road | deck)[grown] & rim).any())
print("settlements with a road at their dot: %d of %d" % (touching, n_dots))
print("road pixels: %d; bridge pixels: %d; pieces of road and bridge not joined to the rest: %d" % (
    road.sum(), deck.sum(), len(set(np.unique(pieces[road | deck]).tolist())) - 1))
