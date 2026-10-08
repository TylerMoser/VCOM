"""Draw the duchies' borders in purple over Kingdoms.png, and check the picture by itself.

Before drawing, the shares d2_solve.py found are tidied: water is given to whichever bank is
nearest, so a border that follows a river runs down its middle and one that crosses a lake
divides it between its shores; the lines are smoothed a little; and a scrap of one duchy left
inside another goes to the one round it. Lines are 3 px, hard-edged, and stop at the kingdoms'
pink and three pixels into the coast's ink, so every duchy is sealed for a paint-bucket fill.

Usage: d3_draw.py <repo root> <duchy out dir> <picture to write> [look]
"""
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT, WRITE_TO = sys.argv[1], sys.argv[2], sys.argv[3]
LOOK = len(sys.argv) > 4
PURPLE = (110, 30, 180, 255)
PINK = (233, 0, 255, 255)
SMOOTH = 2.5
INTO_INK = 3
KM = 0.335

base = np.asarray(Image.open(ROOT + "/MapCreation/Kingdoms.png").convert("RGBA"))
h, w = base.shape[:2]
fields = np.load(OUT + "/fields1.npz")
king, island_king = fields["king"], fields["island_king"]
river, lake, divide = fields["river"], fields["lake"], fields["divide"]
ridge = fields["ridge"]
mainland = king > 0
land = mainland | (island_king > 0)
with open(OUT + "/duchies_all.pickle", "rb") as handle:
    results = pickle.load(handle)

duchy = np.zeros((h, w), dtype=np.int16)                # 0 off the land, else a number for each duchy
of_kingdom = [0]
seats = [None]
for k in sorted(results):
    owner = results[k]["owner"]
    here = owner >= 0
    duchy[here] = len(of_kingdom) + owner[here]
    for seat in results[k]["seats"]:
        of_kingdom.append(k)
        seats.append(seat)
of_kingdom = np.array(of_kingdom)
count = len(of_kingdom) - 1
water = river | lake

for k in sorted(results):
    realm = king == k
    # Water goes to the nearest bank.
    dry = realm & ~water
    _, (ny, nx) = ndimage.distance_transform_edt(~dry, return_indices=True)
    wet = realm & water
    duchy[wet] = duchy[ny[wet], nx[wet]]
    # Smooth: each duchy's shape blurred, each pixel to whichever is strongest there.
    box = ndimage.find_objects(realm.astype(np.uint8))[0]
    window = (slice(max(box[0].start - 8, 0), box[0].stop + 8), slice(max(box[1].start - 8, 0), box[1].stop + 8))
    inside = realm[window]
    presence = np.maximum(ndimage.gaussian_filter(inside.astype(np.float32), SMOOTH), 1e-6)
    best = np.zeros(inside.shape, dtype=np.float32)
    smooth = np.zeros(inside.shape, dtype=np.int16)
    for d in np.flatnonzero(of_kingdom == k):
        mine = ndimage.gaussian_filter((duchy[window] == d).astype(np.float32), SMOOTH) / presence
        better = mine > best
        smooth[better] = d
        best[better] = mine[better]
    duchy[window] = np.where(inside, smooth, duchy[window])
    # Scraps: each duchy keeps its one largest piece.
    scrap = np.zeros(inside.shape, dtype=bool)
    for d in np.flatnonzero(of_kingdom == k):
        mine = duchy[window] == d
        parts, n = ndimage.label(mine)
        if n > 1:
            sizes = ndimage.sum_labels(mine, parts, index=np.arange(1, n + 1))
            scrap |= mine & (parts != int(np.argmax(sizes)) + 1)
    if scrap.any():
        _, (sy, sx) = ndimage.distance_transform_edt(scrap | ~inside, return_indices=True)
        patch = duchy[window]
        duchy[window] = np.where(scrap, patch[sy, sx], patch)
# Islands go with the duchy they lie off.
_, (ny, nx) = ndimage.distance_transform_edt(duchy == 0, return_indices=True)
spread = duchy[ny, nx]
whole = np.where(land, spread, 0)

# -- the lines ---------------------------------------------------------------------------------------
near_land = ndimage.binary_dilation(mainland, structure=np.ones((3, 3), dtype=bool), iterations=INTO_INK)
field = np.where(near_land, spread, 0)
kingdom_of = of_kingdom[field]
core = np.zeros((h, w), dtype=bool)
for dy, dx in ((0, 1), (1, 0)):
    a = field[: h - dy, : w - dx]; b = field[dy:, dx:]
    meet = (a != b) & (a > 0) & (b > 0) & (kingdom_of[: h - dy, : w - dx] == kingdom_of[dy:, dx:])
    core[: h - dy, : w - dx] |= meet
line = ndimage.binary_dilation(core, structure=np.ones((3, 3), dtype=bool))
pink = (base[..., 0] == PINK[0]) & (base[..., 1] == PINK[1]) & (base[..., 2] == PINK[2])
sea_blue = (base[..., 2].astype(np.int32) - base[..., 0].astype(np.int32) >= 40) & ~pink & ~land
line &= near_land & ~pink & ~sea_blue
picture = base.copy()
picture[line] = PURPLE
# Where two lines run close together a sliver of land can be left sealed between them, belonging
# to nothing: such slivers are inked over.
open_land = (picture[..., 0] >= 250) & (picture[..., 1] >= 250) & (picture[..., 2] >= 250) & mainland
bits, n_bits = ndimage.label(open_land)
bit_sizes = ndimage.sum_labels(open_land, bits, index=np.arange(1, n_bits + 1))
sliver = np.isin(bits, np.flatnonzero(bit_sizes < 3000) + 1)
picture[sliver] = PURPLE
line |= sliver
Image.fromarray(picture, "RGBA").save(WRITE_TO)
np.save(OUT + "/duchy_map.npy", whole)
print("wrote %s: %d purple pixels" % (WRITE_TO, int(line.sum())))

# -- the check, from the saved picture ---------------------------------------------------------------
saved = np.asarray(Image.open(WRITE_TO).convert("RGBA"))
changed = (saved != base).any(axis=2)
colours = {tuple(int(v) for v in c): int(n) for c, n in zip(*np.unique(saved[changed].reshape(-1, 4), axis=0, return_counts=True))}
print("pixels changed from Kingdoms.png: %d, in colours %s; purple on the open sea: %d" % (changed.sum(), colours, (changed & sea_blue).sum()))
white = (saved[..., 0] >= 250) & (saved[..., 1] >= 250) & (saved[..., 2] >= 250)
pieces, n = ndimage.label(white & mainland)
sizes = ndimage.sum_labels(white & mainland, pieces, index=np.arange(1, n + 1))
big = np.flatnonzero(sizes > 5000) + 1
print("the pink and purple cut the mainland into %d pieces (wanted %d); scraps under 5,000 px: %d %s" % (
    len(big), count, n - len(big), sorted(int(s) for s in sizes[sizes <= 5000])[:12]))
seeds = np.zeros((h, w), dtype=np.int32)
for rank, piece in enumerate(big):
    seeds[pieces == piece] = rank + 1
_, (ny, nx) = ndimage.distance_transform_edt(seeds == 0, return_indices=True)
final = np.where(land, seeds[ny, nx], 0)
print("kingdom  duchies' areas in km2 (line and islands shared to the nearest)          smallest to largest")
piece_kingdom = {}
for rank, piece in enumerate(big):
    piece_kingdom[rank + 1] = int(np.argmax(np.bincount(king[pieces == piece], minlength=10)[1:])) + 1
area_of = np.bincount(final[final > 0], minlength=len(big) + 1).astype(np.float64) * KM * KM
worst = 0.0
for k in range(1, 10):
    areas = np.sort([area_of[d] for d, kk in piece_kingdom.items() if kk == k])
    worst = max(worst, float(np.abs(areas - areas.mean()).max() / areas.mean()))
    print("   %d    %d: %s   1 : %.2f" % (k, len(areas), np.round(areas).astype(int).tolist(), areas.max() / areas.min()))
print("furthest any duchy is from its kingdom's mean: %.1f%%" % (100 * worst))

# What the borders run along.
total = float(core.sum())
on_river = core & ndimage.binary_dilation(river, iterations=3)
on_lake = core & ndimage.binary_dilation(lake, iterations=3) & ~on_river
on_divide = core & ndimage.binary_dilation(divide, iterations=5) & ~on_river & ~on_lake
on_ridge = core & ndimage.binary_dilation(ridge, iterations=5) & ~on_river & ~on_lake & ~on_divide
rest = total - on_river.sum() - on_lake.sum() - on_divide.sum() - on_ridge.sum()
print("duchy borders, about %.0f km in all: %.0f%% along rivers, %.0f%% along or across lakes, %.0f%% along the drawn watershed lines, %.0f%% along lesser ridges between rivers, %.0f%% across open country" % (
    total * KM, 100 * on_river.sum() / total, 100 * on_lake.sum() / total, 100 * on_divide.sum() / total, 100 * on_ridge.sum() / total, 100 * rest / total))

if LOOK:
    rng = np.random.default_rng(5)
    tints = np.vstack([[255, 255, 255], rng.integers(175, 245, size=(count, 3))]).astype(np.uint8)
    look = tints[whole]
    look[~land] = (181, 235, 255)
    look[(base[..., :3].astype(np.int32).sum(axis=2) < 300)] = 0
    look[ridge] = (215, 200, 185)
    look[ndimage.binary_dilation(divide, iterations=1)] = (205, 150, 100)
    look[water] = (28, 112, 224)
    look[ndimage.binary_dilation(line, iterations=1) & ~pink] = PURPLE[:3]
    look[ndimage.binary_dilation(pink, iterations=1)] = PINK[:3]
    image = Image.fromarray(look)
    from PIL import ImageDraw
    pen = ImageDraw.Draw(image)
    for seat in seats[1:]:
        pen.ellipse([seat[0] - 9, seat[1] - 9, seat[0] + 9, seat[1] + 9], fill=(0, 0, 0), outline=(255, 255, 255), width=3)
    image.resize((w // 2, h // 2), Image.LANCZOS).save(OUT + "/duchies_look.png")
    image.save(OUT + "/duchies_look_full.png")
    print("saved duchies_look.png")
