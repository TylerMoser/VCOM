"""Build the border network once and keep it, with the numbers that check it."""
import pickle, sys, time
import numpy as np
from PIL import Image
from scipy import ndimage
sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
from kingdom_net import Network

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT = sys.argv[1], sys.argv[2]
t = time.time()
creation = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
white = (creation[..., 0] >= 250) & (creation[..., 1] >= 250) & (creation[..., 2] >= 250)
pieces, count = ndimage.label(white)
sizes = ndimage.sum_labels(white, pieces, index=np.arange(1, count + 1))
mainland = pieces == (int(np.argmax(sizes)) + 1)
start = np.load(OUT + "/start_map.npy")
print("loaded %.1fs" % (time.time() - t)); t = time.time()
net = Network(start, mainland)
print("network built %.1fs" % (time.time() - t)); t = time.time()
junctions, coasts = net.names()
print("coast %d points, %.0f px round" % (len(net.coast), net.coast_length))
for key in sorted(net.borders):
    print("  %d|%d  %5.0f px  %d pts  %s -> %s" % (key[0], key[1], net.length[key], len(net.borders[key]), net.ends[key][0], net.ends[key][1]))
print("strokes:")
for stroke in net.strokes:
    print("  " + "  ".join("%d|%d%s" % (k[0], k[1], "'" if rev else "") for k, rev in stroke))
print("rings:")
for i in net.regions:
    print("  %d: %s" % (i, " ".join("coast" if p[0] == "coast" else "%d|%d%s" % (p[1][0], p[1][1], "'" if p[2] else "") for p in net.rings[i])))
x0 = net.home_x()
t = time.time()
for _ in range(20):
    a = net.areas(x0)
print("areas() takes %.1f ms" % ((time.time() - t) / 20 * 1000))
pixel = np.bincount(start[mainland], minlength=10)[1:].astype(np.float64)
for i, (p, q) in enumerate(zip(a, pixel)):
    print("  %d: outline %9.0f  pixels %9.0f  (%+.3f%%)" % (i + 1, p, q, 100 * (p - q) / q))
net.labels = None
with open(OUT + "/network.pickle", "wb") as handle:
    pickle.dump(net, handle)
print("saved network.pickle")
