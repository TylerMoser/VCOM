"""A picture of the lines of the land a border may follow, each kind in its own colour, with one
variant's borders over them; and the long ruled runs in those borders, with what they lie on.

Usage: kb4_features.py <duchy out dir> <kingdom fields dir> <tag> <out png> x0,y0,x1,y1[,scale] ...
"""
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

OUT, KING, TAG, WRITE_TO = sys.argv[1:5]
fields = np.load(OUT + "/fields1.npz")
more = np.load(KING + "/fields.npz")
with open(KING + "/lines_%s.pickle" % TAG, "rb") as handle:
    lines = pickle.load(handle)
river, lake, divide = fields["river"], fields["lake"], fields["divide"]
ridge = fields["ridge"]
spur, brook = more["spur"], more["brook"]
h, w = river.shape
land = fields["king"] > 0
picture = np.full((h, w, 3), 255, dtype=np.uint8)
picture[~land] = (181, 235, 255)
picture[spur] = (205, 205, 150)          # spurs: pale olive
picture[brook] = (150, 215, 235)         # brooks: pale blue
picture[ridge] = (230, 160, 90)          # ridges between rivers: orange
picture[divide] = (150, 80, 20)          # watershed lines: brown
picture[lake] = (60, 130, 225)
picture[river] = (20, 80, 200)
names = (("river", river), ("lake", lake), ("watershed", divide), ("ridge", ridge), ("brook", brook), ("spur", spur))
for code, cells in zip(lines["codes"], lines["cells"]):
    picture[cells[:, 0], cells[:, 1]] = (233, 0, 255)
    # Ruled runs: stretches where the line keeps one of the eight compass ways.
    steps = np.sign(np.diff(cells, axis=0))
    start = 0
    for i in range(1, len(steps) + 1):
        if i == len(steps) or (steps[i] != steps[start]).any():
            if i - start >= 30:
                run = cells[start: i + 1]
                on = {name: float(mask[run[:, 0], run[:, 1]].mean()) for name, mask in names}
                best = max(on, key=on.get)
                print("border %d|%d: ruled for %d px from (%d, %d) to (%d, %d), heading (%d, %d): on %s for %.0f%%" % (
                    code // 10, code % 10, i - start, run[0, 1], run[0, 0], run[-1, 1], run[-1, 0], steps[start][1], steps[start][0], best, 100 * on[best]))
            start = i
for number, spec in enumerate(sys.argv[5:]):
    parts = spec.split(",")
    x0, y0, x1, y1 = (int(v) for v in parts[:4])
    scale = float(parts[4]) if len(parts) > 4 else 1.0
    crop = Image.fromarray(picture[y0:y1, x0:x1])
    if scale != 1.0:
        crop = crop.resize((int((x1 - x0) * scale), int((y1 - y0) * scale)), Image.NEAREST)
    crop.save(WRITE_TO.replace(".png", "_%d.png" % number))
print("done")
