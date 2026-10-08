"""The duchies' and counties' maps about a place, as letters, with the old land's edge."""
import pickle, sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
MAPS, OUT = sys.argv[1:3]
x0, y0, w, h = (int(v) for v in sys.argv[3:7])
old = np.asarray(Image.open(MAPS + "/WorldMapV1.png").convert("RGB")).astype(int)
old_land = (old >= 250).all(axis=2)
duchy_map = np.load(OUT + "/duchy_map.npy")
with open(OUT + "/counties_f3.pickle", "rb") as handle:
    solved = pickle.load(handle)
county = np.load(OUT + "/county_map_f3.npy")
for name, labels in (("duchy_map.npy", duchy_map), ("the counties' run's duchies", solved["duchy"]), ("counties", county)):
    seen = {}
    print(name + " (blank: no label; lower case on land, upper case off the old land):")
    for y in range(y0, y0 + h):
        row = ""
        for x in range(x0, x0 + w):
            v = int(labels[y, x])
            if v == 0:
                row += " " if not old_land[y, x] else "?"
                continue
            if v not in seen:
                seen[v] = "abcdefghijklmnopqrstuvwxyz"[len(seen)]
            row += seen[v] if old_land[y, x] else seen[v].upper()
        print("%4d %s" % (y, row))
    print("   %s" % {v: k for k, v in seen.items()})
