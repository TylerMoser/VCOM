"""How the three masks of the land's lines lie to the watersheds, the rivers and each other.

Usage: e12_look.py <staged source data> <MapCreation dir>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
SRC, MAPS = sys.argv[1:3]
ridge = np.asarray(Image.open(SRC + "/Ridges.png")) > 0
spur = np.asarray(Image.open(SRC + "/Spurs.png")) > 0
brook = np.asarray(Image.open(SRC + "/Brooks.png")) > 0
shed = np.asarray(Image.open(SRC + "/WatershedMap.png")).astype(np.int32)
h, w = shed.shape
edge = np.zeros((h, w), dtype=bool)
for dy, dx in ((0, 1), (1, 0)):
    a, b = shed[: h - dy, : w - dx], shed[dy:, dx:]
    meet = (a != b) & (a > 0) & (b > 0)
    edge[: h - dy, : w - dx] |= meet
    edge[dy:, dx:] |= meet
to_ridge = ndimage.distance_transform_edt(~ridge)
to_edge = ndimage.distance_transform_edt(~edge)
print("watershed edges: %d px; within 3 px of a ridge pixel: %.1f%%; within 6 px: %.1f%%" % (edge.sum(), 100.0 * (to_ridge[edge] <= 3).mean(), 100.0 * (to_ridge[edge] <= 6).mean()))
print("ridge pixels: %d; within 3 px of a watershed edge: %.1f%%; within 6 px: %.1f%%" % (ridge.sum(), 100.0 * (to_edge[ridge] <= 3).mean(), 100.0 * (to_edge[ridge] <= 6).mean()))
print("spur pixels: %d; that are also ridge: %.1f%%; ridge pixels that are also spur: %.1f%%; brook pixels on a ridge or spur: %d" % (
    spur.sum(), 100.0 * (spur & ridge).sum() / spur.sum(), 100.0 * (spur & ridge).sum() / ridge.sum(), (brook & (ridge | spur)).sum()))
land = (np.asarray(Image.open(MAPS + "/WorldMapV1.png").convert("RGB")) >= 250).all(axis=2)
pieces = ndimage.label(land)[0]
main = pieces == int(np.argmax(np.bincount(pieces.ravel())[1:])) + 1
print("on the islands: ridge %d px, spur %d px, brook %d px" % ((ridge & ~main).sum(), (spur & ~main).sum(), (brook & ~main).sum()))
blue = (np.asarray(Image.open(MAPS + "/Water.png").convert("RGB")) == (28, 112, 224)).all(axis=2)
near_river = ndimage.distance_transform_edt(~blue)
print("brooks: nearest any comes to drawn water: %.1f px; share within 6 px of water: %.1f%%" % (near_river[brook].min(), 100.0 * (near_river[brook] <= 6).mean()))
for name, mask in (("ridge", ridge), ("spur", spur), ("brook", brook)):
    blocks = mask.reshape(h // 2, 2, w // 2, 2)
    whole = blocks.all(axis=(1, 3)).sum()
    part = blocks.any(axis=(1, 3)).sum() - whole
    print("%s: 2 px squares wholly set %d, partly set %d" % (name, whole, part))
