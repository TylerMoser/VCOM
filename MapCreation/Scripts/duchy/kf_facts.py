"""The figures Features.md gives for Kingdoms2.png.

Usage: kf_facts.py <MapCreation dir> <duchy out dir> <kingdom fields dir> <network dir> <tag>
"""
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
FOLDER, OUT, KING, NET, TAG = sys.argv[1:6]
KM = 0.335
new_picture = np.asarray(Image.open(FOLDER + "/Kingdoms2.png").convert("RGB"))
old_picture = np.asarray(Image.open(FOLDER + "/Kingdoms.png").convert("RGB"))
base = np.asarray(Image.open(FOLDER + "/WorldMapV1.png").convert("RGB"))
h, w = base.shape[:2]


def count(picture, colour):
    return int((picture == np.array(colour, dtype=np.uint8)).all(axis=2).sum())


for name, picture in (("Kingdoms.png", old_picture), ("Kingdoms2.png", new_picture)):
    sea, white, pink, grey = count(picture, (181, 235, 255)), count(picture, (255, 255, 255)), count(picture, (233, 0, 255)), count(picture, (128, 128, 128))
    print("%s: sea %d, white %d, pink %d, grey %d, other %d" % (name, sea, white, pink, grey, h * w - sea - white - pink - grey))

fields = np.load(OUT + "/fields1.npz")
more = np.load(KING + "/fields.npz")
old = fields["king"].astype(np.int16)
new = np.load(KING + "/kingdoms_%s.npy" % TAG).astype(np.int16)
mainland = old > 0
with open(KING + "/lines_%s.pickle" % TAG, "rb") as handle:
    lines = pickle.load(handle)
with open(NET + "/network.pickle", "rb") as handle:
    network = pickle.load(handle)
print("meeting places, old: %s" % [(j["kingdoms"], j["at"][::-1]) for j in network["joins"]])
print("meeting places, new: %s" % [(j["kingdoms"], m[::-1]) for j, m in zip(network["joins"], lines["meet"])])
print("coast ends, old: %s" % [(l["code"], l["at"][::-1]) for l in network["landings"]])


def border_cells(grid):
    """For every pair of kingdoms, the cells of the one whose neighbour to the right or below is the other's."""
    out = {}
    marked = np.zeros((h, w), dtype=np.int16)
    for dy, dx in ((0, 1), (1, 0)):
        a = grid[: h - dy, : w - dx]; b = grid[dy:, dx:]
        meet = (a != b) & (a > 0) & (b > 0)
        code = np.minimum(a, b) * 10 + np.maximum(a, b)
        view = marked[: h - dy, : w - dx]
        view[meet & (view == 0)] = code[meet & (view == 0)]
    for code in np.unique(marked[marked > 0]):
        out[int(code)] = marked == code
    return out


old_cells, new_cells = border_cells(old), border_cells(new)
old_any = np.zeros((h, w), dtype=bool)
for mask in old_cells.values():
    old_any |= mask
from_old = ndimage.distance_transform_edt(~old_any) * KM
river, lake, divide, ridge = fields["river"], fields["lake"], fields["divide"], fields["ridge"]
spur, brook = more["spur"], more["brook"]
kinds = (("rivers", ndimage.binary_dilation(river, iterations=3)), ("lakes", ndimage.binary_dilation(lake, iterations=3)),
         ("watersheds", ndimage.binary_dilation(divide, iterations=4)), ("ridges", ndimage.binary_dilation(ridge, iterations=4)),
         ("brooks", ndimage.binary_dilation(brook, iterations=3)), ("spurs", ndimage.binary_dilation(spur, iterations=3)))
print("border | old km | new km | from the old line: average, furthest km | new runs along: " + ", ".join(k for k, _ in kinds) + ", other %")
totals = np.zeros(len(kinds) + 1); whole_old = whole_new = 0.0
for code in sorted(new_cells):
    cells = new_cells[code]
    far = from_old[cells]
    taken = np.zeros((h, w), dtype=bool)
    shares = []
    for _, mask in kinds:
        on = cells & mask & ~taken
        taken |= on
        shares.append(float(on.sum()))
    shares.append(float((cells & ~taken).sum()))
    totals += np.array(shares)
    n_old, n_new = float(old_cells[code].sum()), float(cells.sum())
    whole_old += n_old; whole_new += n_new
    print("%d|%d | %4.0f | %4.0f | %4.1f, %4.1f | %s" % (code // 10, code % 10, n_old * KM, n_new * KM, far.mean(), far.max(),
                                                       ", ".join("%2.0f" % (100 * s / n_new) for s in shares)))
print("all | %4.0f | %4.0f | %s" % (whole_old * KM, whole_new * KM, ", ".join("%2.0f" % (100 * s / whole_new) for s in totals)))
ends = []
for code, curve in zip(lines["codes"], lines["curves"]):
    length = float(np.hypot(*np.diff(curve, axis=0).T).sum()) * KM
    ends.append((code, [int(round(curve[0][1])), int(round(curve[0][0]))], [int(round(curve[-1][1])), int(round(curve[-1][0]))], round(length)))
print("each line's two ends (x, y) and its length along the smoothed line, km: %s" % ends)
print("sum of those lengths: %.0f km" % sum(e[3] for e in ends))
areas = np.bincount(new[mainland], minlength=10)[1:] * KM * KM
print("mainland areas by the kingdoms' map, km2: %s" % np.round(areas).astype(int).tolist())
height = fields["height"]
for k in range(1, 10):
    gained = mainland & (new == k) & (old != k)
    lost = mainland & (old == k) & (new != k)
    print("kingdom %d: gains %5.0f km2 (median height %4.0f m), gives up %5.0f km2 (median height %4.0f m); its old land's median height %4.0f m" % (
        k, gained.sum() * KM * KM, np.median(height[gained]), lost.sum() * KM * KM, np.median(height[lost]), np.median(height[old == k])))
print("done")
