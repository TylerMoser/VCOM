"""Where the road network of Roads.png falls into pieces, and which bridge marks lack two ends.

Usage: r8_pieces.py <repo root>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT = sys.argv[1]


def load(name):
    return np.asarray(Image.open(ROOT + "/MapCreation/" + name).convert("RGBA"))


def is_colour(picture, colour):
    return (picture[..., 0] == colour[0]) & (picture[..., 1] == colour[1]) & (picture[..., 2] == colour[2])


roads, settlements, counties, coast = load("Roads.png"), load("Settlements.png"), load("Counties.png"), load("WorldMapV1.png")
road, deck = is_colour(roads, (200, 40, 30)), is_colour(roads, (60, 35, 15))
dots = (settlements != counties).any(axis=2)
white_land = (coast[..., :3] >= 250).all(axis=2)
for closing in (0, 4):
    ferry = ndimage.binary_closing(road & ~white_land, structure=np.ones((3, 3)), iterations=closing) if closing else np.zeros_like(road)
    net = road | deck | dots | ferry
    pieces, n = ndimage.label(net, structure=np.ones((3, 3)))
    sizes = ndimage.sum_labels(net, pieces, index=np.arange(1, n + 1))
    print("ferry's dashes closed by %d: %d pieces" % (closing, n))
    for i in np.argsort(-sizes)[:8]:
        box = ndimage.find_objects(pieces)[i]
        held = len(np.unique(ndimage.label(dots & (pieces == i + 1), structure=np.ones((3, 3)))[0])) - 1
        print("  %7d px at x %d..%d, y %d..%d, holding %d settlements" % (sizes[i], box[1].start, box[1].stop, box[0].start, box[0].stop, held))

marks, n = ndimage.label(deck, structure=np.ones((3, 3)))
for i, box in enumerate(ndimage.find_objects(marks), start=1):
    grown = (slice(max(box[0].start - 3, 0), box[0].stop + 3), slice(max(box[1].start - 3, 0), box[1].stop + 3))
    mine = marks[grown] == i
    rim = ndimage.binary_dilation(mine, structure=np.ones((3, 3)), iterations=2) & ~mine
    ends = ndimage.label((road[grown] | dots[grown]) & rim, structure=np.ones((3, 3)))[1]
    if ends < 2:
        print("bridge mark with %d end(s) at x %d..%d, y %d..%d, %d px" % (ends, box[1].start, box[1].stop, box[0].start, box[0].stop, mine.sum()))
