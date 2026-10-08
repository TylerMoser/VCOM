"""Where a road lies along a border in Roads.png: how long, and how deep the border is hidden."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
Image.MAX_IMAGE_PIXELS = None
MAPS, LOOK = sys.argv[1:3]
PINK, PURPLE, GREY, RED, UMBER = (233, 0, 255), (110, 30, 180), (128, 128, 128), (200, 40, 30), (60, 35, 15)
EIGHT = np.ones((3, 3), bool)
def load(name):
    return np.asarray(Image.open(MAPS + "/" + name).convert("RGB"))
def is_colour(picture, colour):
    return (picture == np.array(colour, np.uint8)).all(axis=2)
coast, counties, roads = load("WorldMapV1.png"), load("Counties.png"), load("Roads.png")
land = (coast >= 250).all(axis=2)
over = is_colour(roads, RED) | is_colour(roads, UMBER)
shots = []
for name, colour in (("kingdom", PINK), ("duchy", PURPLE), ("county", GREY)):
    border = is_colour(counties, colour) & land
    hidden = border & over
    depth = ndimage.distance_transform_edt(~(border & ~hidden))
    pieces, n = ndimage.label(hidden, structure=EIGHT)
    rows = []
    for i, box in enumerate(ndimage.find_objects(pieces), start=1):
        mine = pieces[box] == i
        py, px = np.nonzero(mine)
        pts = np.stack([px, py], axis=1).astype(float)
        span = float(len(pts))
        if len(pts) > 2:
            c = pts - pts.mean(axis=0)
            vals, vecs = np.linalg.eigh(np.cov(c.T))
            a = c @ vecs[:, 1]
            span = a.max() - a.min() + 1
        rows.append((float(depth[box][mine].max()), span, len(px), int(box[1].start + px.mean()), int(box[0].start + py.mean())))
    rows.sort(reverse=True)
    deep = [r for r in rows if r[0] >= 3.0]
    print("%s borders under roads: %d places; hidden right across for a way (deepest pixel 3 px or more from any showing): %d" % (name, n, len(deep)))
    for r in rows[:10]:
        print("   deepest %.1f px, span %.0f px, %d px, at (%d, %d)" % r)
    shots += [(name, r) for r in rows[:3]]
for name, r in shots:
    x, y = r[3], r[4]
    crop = Image.fromarray(roads[max(y - 40, 0): y + 40, max(x - 50, 0): x + 50])
    crop.resize((crop.width * 6, crop.height * 6), Image.NEAREST).save(LOOK + "/along_%s_%d_%d.png" % (name, x, y))
