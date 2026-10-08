"""Draw the rivers, lakes and watersheds w3_water.py worked out on the coast map, at the map's
own size.

Rivers are drawn as lines whose width grows with the water they carry; each is smoothed, and
where its bed is nearly level it is made to wander from side to side as lowland rivers do. Lakes
are drawn as shapes over them. Watersheds are drawn as the lines between them. All three in flat
colour with hard edges, so the picture can be read back exactly.

Usage: w4_draw.py <repo root> <out dir> <factor> <picture to write> [look]
"""
import pickle
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT, FACTOR, WRITE_TO = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
LOOK = len(sys.argv) > 5
BLUE = (28, 112, 224, 255)             # rivers and lakes
BROWN = (196, 118, 44, 255)            # the lines between watersheds
DIVIDE_WIDTH = 3
INTO_INK = 3                           # pixels a line may run on into the coast's ink
SEED = 20261008
KM = 0.335

base = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
h, w = base.shape[:2]
full = np.load(OUT + "/grid1.npz")
land, mainland, king = full["land"], full["mainland"], full["king"]
with open(OUT + "/water%d.pickle" % FACTOR, "rb") as handle:
    water = pickle.load(handle)
rng = np.random.default_rng(SEED)
allowed = ndimage.binary_dilation(land, structure=np.ones((3, 3), dtype=bool), iterations=INTO_INK)
allowed &= land | (base[..., 2].astype(np.int32) - base[..., 0].astype(np.int32) < 40)      # the ink, never the sea
rows, cols = water["rows"], water["cols"]
flow, z, lake_flat = water["flow_flat"], water["z"], water["lake_flat"]
coarse_king = np.load(OUT + "/grid%d.npz" % FACTOR)["king"]
king_flat = coarse_king[rows, cols]


def width_of(q, k):
    """Pixels across for a river carrying [q] m3/s: wider in the swamp and the rainforest."""
    wide = 1.3 + 1.25 * (np.maximum(q, 1.0) / 40.0) ** 0.36
    wide = wide * np.where((k == 7) | (k == 9), 1.25, 1.0)
    return np.clip(wide, 2.0, 12.0)


def smoothed(points, sigma):
    if len(points) < 4:
        return points.copy()
    soft = ndimage.gaussian_filter1d(points, sigma, axis=0, mode="nearest")
    t = np.linspace(0.0, 1.0, len(points))[:, None]
    return soft + (1 - t) * (points[0] - soft[0]) + t * (points[-1] - soft[-1])


def along(points):
    return np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(points, axis=0).T))])


# -- rivers -----------------------------------------------------------------------------------------
reaches = sorted(water["reaches"], key=lambda r: -float(flow[r["cells"]].max()))
placed = {}                             # cell -> where its river's line ended up, for streams joining it
lines = []
for reach in reaches:
    cells = reach["cells"]
    if len(cells) < 2:
        continue
    points = np.column_stack([rows[cells] * FACTOR + (FACTOR - 1) / 2.0, cols[cells] * FACTOR + (FACTOR - 1) / 2.0]).astype(np.float64)
    q = flow[cells].astype(np.float64).copy()
    k = king_flat[cells]
    height = z[cells].astype(np.float64)
    if reach["end"] == "joins":
        q[-1] = q[-2]                                    # the last cell is the bigger river's, not this one's
        if int(cells[-1]) in placed:
            points[-1] = placed[int(cells[-1])]
    elif reach["end"] == "sea":
        step = points[-1] - points[-2]
        points = np.vstack([points, points[-1] + (1.5 * FACTOR + 6.0) * step / max(np.hypot(*step), 1e-9)])
        q = np.append(q, q[-1]); k = np.append(k, k[-1]); height = np.append(height, 0.0)
    q = np.maximum.accumulate(q)                         # a river is drawn no narrower downstream
    # Smooth the cell-to-cell steps away, then lay points every pixel and a half.
    points = smoothed(points, 1.4)
    s = along(points)
    if s[-1] < 3.0 or (reach["end"] == "sea" and s[-1] < 34.0 and not lake_flat[cells[0]]):
        continue                                         # a stub at the shore says nothing
    at = np.linspace(0.0, s[-1], max(int(s[-1] / 1.5), 2) + 1)
    fine = np.column_stack([np.interp(at, s, points[:, 0]), np.interp(at, s, points[:, 1])])
    fine_q = np.interp(at, s, q)
    fine_k = k[np.clip(np.searchsorted(s, at), 0, len(k) - 1)]
    wide = width_of(fine_q, fine_k)
    # How steep the bed is, metres in a kilometre, over a few cells.
    fall = np.maximum(-np.gradient(ndimage.gaussian_filter1d(height, 2.0, mode="nearest")), 0.0) / np.maximum(np.gradient(s) * KM, 1e-6)
    fine_fall = np.interp(at, s, fall)
    # Wandering: nought on a steep bed, full on a level one; loops a dozen widths long.
    lazy = np.clip((2.5 - fine_fall) / 2.3, 0.0, 1.0) ** 1.5
    lazy *= np.where((fine_k == 7) | (fine_k == 9) | (fine_k == 5), 1.25, 1.0)
    wave = 11.0 * wide + 16.0
    phase = np.cumsum(2.0 * np.pi * 1.5 / wave) + rng.uniform(0, 2 * np.pi)
    phase += np.cumsum(rng.standard_normal(len(at)) * 0.09)             # no two loops alike
    swing = lazy * (1.9 * wide + 2.5) * np.sin(phase) * (0.75 + 0.25 * np.sin(0.37 * phase + 1.0))
    ends = np.minimum(at, s[-1] - at)
    swing *= np.clip(ends / (1.5 * wave), 0.0, 1.0)                     # still at both ends, so joins stay joined
    tangent = np.gradient(fine, axis=0)
    tangent /= np.maximum(np.hypot(tangent[:, 0], tangent[:, 1]), 1e-9)[:, None]
    fine = fine + swing[:, None] * np.column_stack([-tangent[:, 1], tangent[:, 0]])
    fine = smoothed(fine, 1.5)
    for cell, where in zip(cells.tolist(), np.interp(s[: len(cells)], at, np.arange(len(at))).astype(int)):
        placed.setdefault(cell, fine[min(where, len(fine) - 1)].copy())
    lines.append((fine, wide))

river = np.zeros((h, w), dtype=bool)
for size in range(2, 13):
    sheet = Image.new("1", (w, h), 0)
    pen = ImageDraw.Draw(sheet)
    used = False
    for fine, wide in lines:
        mine = np.rint(wide).astype(int) == size
        if not mine.any():
            continue
        mine = ndimage.binary_dilation(mine)             # overlap the neighbours, so widths meet without a gap
        starts = np.flatnonzero(mine & ~np.r_[False, mine[:-1]])
        stops = np.flatnonzero(mine & ~np.r_[mine[1:], False])
        for a, b in zip(starts, stops):
            if b > a:
                pen.line([(float(x) + 0.5, float(y) + 0.5) for y, x in fine[a: b + 1]], fill=1, width=1)
                used = True
    if not used:
        continue
    reach_px = size // 2
    yy, xx = np.mgrid[-reach_px: reach_px + 1, -reach_px: reach_px + 1]
    nib = (yy * yy + xx * xx) <= (size / 2.0) ** 2 + 0.3
    river |= ndimage.binary_dilation(np.asarray(sheet, dtype=bool), structure=nib)
river &= allowed

# -- lakes ------------------------------------------------------------------------------------------
coarse_lake = water["lake"] > 0
soft = np.repeat(np.repeat(coarse_lake.astype(np.float32), FACTOR, axis=0), FACTOR, axis=1)
soft = ndimage.gaussian_filter(soft, 0.55 * FACTOR)
lakes = np.zeros((h, w), dtype=bool)
lakes[: soft.shape[0], : soft.shape[1]] = soft[:h, :w] > 0.42          # a little under half, so the smallest tarns survive
lakes &= land
# A lake too thin to read as one (a few cells strung along a stream) is left out.
pools, count = ndimage.label(lakes, structure=np.ones((3, 3), dtype=bool))
deep = ndimage.distance_transform_edt(lakes)
widest = ndimage.maximum(deep, pools, index=np.arange(1, count + 1))
lakes &= ~np.isin(pools, np.flatnonzero(widest < 2.6) + 1)

# -- watersheds -------------------------------------------------------------------------------------
shed = np.repeat(np.repeat(water["shed"], FACTOR, axis=0), FACTOR, axis=1)
shed_full = np.zeros((h, w), dtype=np.int32)
shed_full[: shed.shape[0], : shed.shape[1]] = shed[:h, :w]
_, (ny, nx) = ndimage.distance_transform_edt(shed_full == 0, return_indices=True)
shed_full = np.where(mainland, shed_full[ny, nx], 0)
best = np.zeros((h, w), dtype=np.float32)
smooth_shed = np.zeros((h, w), dtype=np.int32)
margin = 6 * FACTOR
for number, box in enumerate(ndimage.find_objects(shed_full), start=1):
    if box is None:
        continue
    window = (slice(max(box[0].start - margin, 0), min(box[0].stop + margin, h)),
              slice(max(box[1].start - margin, 0), min(box[1].stop + margin, w)))
    mine = ndimage.gaussian_filter((shed_full[window] == number).astype(np.float32), 1.6 * FACTOR)
    better = mine > best[window]
    smooth_shed[window][better] = number
    best[window][better] = mine[better]
smooth_shed[~mainland] = 0
# Smoothing can leave a scrap of one watershed cut off inside another: each keeps only its one
# largest piece, and the scraps go to whatever lies round them.
scrap = np.zeros((h, w), dtype=bool)
for number, box in enumerate(ndimage.find_objects(smooth_shed), start=1):
    if box is None:
        continue
    mine = smooth_shed[box] == number
    parts, n = ndimage.label(mine)
    if n > 1:
        sizes = ndimage.sum_labels(mine, parts, index=np.arange(1, n + 1))
        scrap[box] |= mine & (parts != int(np.argmax(sizes)) + 1)
if scrap.any():
    _, (sy, sx) = ndimage.distance_transform_edt(scrap | (smooth_shed == 0), return_indices=True)
    smooth_shed = np.where(scrap, smooth_shed[sy, sx], smooth_shed)
edge = np.zeros((h, w), dtype=bool)
for dy, dx in ((0, 1), (1, 0)):
    a = smooth_shed[: h - dy, : w - dx]; b = smooth_shed[dy:, dx:]
    cross = (a != b) & (a > 0) & (b > 0)
    edge[: h - dy, : w - dx] |= cross
    edge[dy:, dx:] |= cross
divide = ndimage.binary_dilation(edge, iterations=(DIVIDE_WIDTH - 2 + 1) // 2) if DIVIDE_WIDTH > 2 else edge
divide &= allowed

# -- the picture ------------------------------------------------------------------------------------
picture = base.copy()
picture[divide] = BROWN
picture[river] = BLUE
picture[lakes] = BLUE
Image.fromarray(picture, "RGBA").save(WRITE_TO)
wet = (river | lakes) & land
print("wrote %s" % WRITE_TO)
print("kingdom   water   of which lakes   rivers")
for k in range(1, 10):
    here = king == k
    print("   %d     %5.2f%%      %5.2f%%      %5.2f%%" % (k, 100 * (wet & here).sum() / here.sum(), 100 * (lakes & here).sum() / here.sum(),
                                                         100 * (river & ~lakes & here).sum() / here.sum()))
print("the whole land: %.2f%% under water (lakes %.2f%%, rivers %.2f%%); watershed lines %.2f%%" % (
    100 * wet.sum() / land.sum(), 100 * (lakes & land).sum() / land.sum(), 100 * (river & ~lakes & land).sum() / land.sum(),
    100 * (divide & land & ~wet).sum() / land.sum()))
np.savez_compressed(OUT + "/drawn%d.npz" % FACTOR, river=river, lakes=lakes, divide=divide, shed=smooth_shed)

if LOOK:
    # The same with the kingdoms' borders over it, shrunk, to judge the whole.
    kingdoms = np.asarray(Image.open(ROOT + "/MapCreation/Kingdoms.png").convert("RGBA"))
    pink = (kingdoms[..., 0] == 233) & (kingdoms[..., 1] == 0) & (kingdoms[..., 2] == 255)
    look = picture.copy()
    look[ndimage.binary_dilation(divide, iterations=1) & ~wet] = BROWN
    look[ndimage.binary_dilation(river, iterations=1)] = BLUE
    look[lakes] = BLUE
    look[ndimage.binary_dilation(pink, iterations=2) & ~wet] = (233, 0, 255, 255)
    Image.fromarray(look, "RGBA").convert("RGB").resize((w // 2, h // 2), Image.LANCZOS).save(OUT + "/water_look.png")
    print("saved water_look.png")
