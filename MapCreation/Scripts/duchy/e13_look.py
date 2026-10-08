"""Are the brown lines of Rivers.png where WatershedMap.png changes? And what a lake does to the flow.

Usage: e13_look.py <MapCreation dir> <scratch out dir>
"""
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
MAPS, OUT = sys.argv[1:3]
SRC = MAPS + "/SourceData"
shed = np.asarray(Image.open(SRC + "/WatershedMap.png")).astype(np.int32)
h, w = shed.shape
edge = np.zeros((h, w), dtype=bool)
for dy, dx in ((0, 1), (1, 0)):
    a, b = shed[: h - dy, : w - dx], shed[dy:, dx:]
    meet = (a != b) & (a > 0) & (b > 0)
    edge[: h - dy, : w - dx] |= meet
    edge[dy:, dx:] |= meet
rivers_png = np.asarray(Image.open(MAPS + "/Rivers.png").convert("RGB"))
brown = (rivers_png == (196, 118, 44)).all(axis=2)
to_edge = ndimage.distance_transform_edt(~edge)
to_brown = ndimage.distance_transform_edt(~brown)
blue = (rivers_png == (28, 112, 224)).all(axis=2)
print("brown px %d; within 2 px of a change of WatershedMap.png: %.2f%%; the furthest %.1f px" % (brown.sum(), 100.0 * (to_edge[brown] <= 2.0).mean(), to_edge[brown].max()))
dry_edge = edge & ~ndimage.binary_dilation(blue, iterations=3)
print("changes of the map: %d px, of them clear of water %d; of those within 2 px of brown: %.2f%%; the furthest %.1f px" % (
    edge.sum(), dry_edge.sum(), 100.0 * (to_brown[dry_edge] <= 2.0).mean(), to_brown[dry_edge].max()))

with open(OUT + "/water/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
drain = np.load(OUT + "/water/drain2.npz")
print("drain2.npz:", {k: (drain[k].shape, str(drain[k].dtype)) for k in drain.files})
rows, cols, flow, lake, to, sea = water["rows"], water["cols"], water["flow_flat"], water["lake_flat"], water["to"], water["sea"]
runoff = drain["runoff"][rows, cols] if drain["runoff"].ndim == 2 else drain["runoff"]
# What each cell adds itself: what leaves it less what comes in.
came = np.zeros(len(rows))
inland = to < sea
np.add.at(came, to[inland], flow[inland])
own = flow - came
wet = lake > 0
print("what a cell adds of itself (m3/s): on dry land least %.4f, most %.4f; in lakes least %.3f, most %.3f; lake cells adding less than nought: %d of %d" % (
    own[~wet].min(), own[~wet].max(), own[wet].min(), own[wet].max(), (own[wet] < -1e-9).sum(), wet.sum()))
by = {l["id"]: l for l in water["lakes"]}
losing = {}
for i in np.flatnonzero(wet & (own < -1e-9)):
    losing[int(lake[i])] = losing.get(int(lake[i]), 0.0) + float(own[i])
kinds = {}
for lid, lost in losing.items():
    kinds.setdefault((by[lid]["kind"], by[lid]["kingdom"]), []).append(lost)
print("lakes with cells that take water away: %d; by kind and country: %s" % (len(losing), {k: (len(v), round(sum(v), 1)) for k, v in sorted(kinds.items(), key=lambda kv: str(kv[0]))}))
