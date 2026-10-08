"""The strait at the island town, pixel by pixel, and what the runs kept about the ferry."""
import pickle, sys
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
MAPS, ROADS = sys.argv[1:3]
coast = np.asarray(Image.open(MAPS + "/WorldMapV1.png").convert("RGB")).astype(int)
roads = np.asarray(Image.open(MAPS + "/Roads.png").convert("RGB")).astype(int)
sett = np.asarray(Image.open(MAPS + "/Settlements.png").convert("RGB")).astype(int)
land = (coast >= 250).all(axis=2)
sea = (coast == (181, 235, 255)).all(axis=2)
red = (roads == (200, 40, 30)).all(axis=2)
dot = (sett != np.asarray(Image.open(MAPS + "/Counties.png").convert("RGB")).astype(int)).any(axis=2)
print("   " + "".join(str(x % 10) for x in range(205, 262)))
for y in range(2072, 2114):
    row = ""
    for x in range(205, 262):
        row += "O" if dot[y, x] else "R" if red[y, x] else "." if land[y, x] else "~" if sea[y, x] else "#"
    print("%4d %s" % (y, row))
for name in ("network.pickle", "drawn.pickle", "towns.pickle"):
    with open(ROADS + "/" + name, "rb") as handle:
        data = pickle.load(handle)
    print(name, type(data).__name__, (sorted(data.keys()) if isinstance(data, dict) else len(data)))
    if isinstance(data, dict):
        for key, value in data.items():
            if "ferr" in str(key).lower():
                print("   ", key, ":", str(value)[:600])
