"""Draw the kingdoms' new borders in pink over the coast map, and check the picture by itself.

Lines are 5 px, hard-edged, in the pink of Kingdoms.png, and run three pixels into the coast's
ink, so pink and coast close every kingdom off for a paint-bucket fill.

Usage: k3_draw.py <repo root> <duchy out dir> <kingdom out dir> <tag> <picture to write> [look]
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT, KING, TAG, WRITE_TO = sys.argv[1:6]
LOOK = len(sys.argv) > 6
PINK = (233, 0, 255, 255)
INTO_INK = 3
SLIVER = 600
KM = 0.335

base = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
old_picture = np.asarray(Image.open(ROOT + "/MapCreation/Kingdoms.png").convert("RGBA"))
h, w = base.shape[:2]
fields = np.load(OUT + "/fields1.npz")
more = np.load(KING + "/fields.npz")
old, island_king = fields["king"], fields["island_king"]
mainland = old > 0
land = mainland | (island_king > 0)
new = np.load(KING + "/kingdoms_%s.npy" % TAG).astype(np.int16)
sea = (base[..., 2].astype(np.int32) - base[..., 0].astype(np.int32) >= 40) & ~land

# -- the lines ---------------------------------------------------------------------------------------
_, (ny, nx) = ndimage.distance_transform_edt(new == 0, return_indices=True)
near_land = ndimage.binary_dilation(mainland, structure=np.ones((3, 3), dtype=bool), iterations=INTO_INK)
field = np.where(near_land, new[ny, nx], 0)


def edges_of(labels):
    core = np.zeros((h, w), dtype=bool)
    for dy, dx in ((0, 1), (1, 0)):
        a = labels[: h - dy, : w - dx]; b = labels[dy:, dx:]
        core[: h - dy, : w - dx] |= (a != b) & (a > 0) & (b > 0)
    return core


core = edges_of(field)
yy, xx = np.mgrid[-2:3, -2:3]
nib = (yy * yy + xx * xx) <= 2.5 ** 2 - 1.0               # a round nib five pixels across
line = ndimage.binary_dilation(core, structure=nib) & near_land & ~sea
picture = base.copy()
picture[line] = PINK
open_land = (picture[..., :3] >= 250).all(axis=2) & mainland
bits, n_bits = ndimage.label(open_land)
bit_sizes = ndimage.sum_labels(open_land, bits, index=np.arange(1, n_bits + 1))
sliver = np.isin(bits, np.flatnonzero(bit_sizes < SLIVER) + 1)
print("slivers inked over: %d, of %s px; other pieces under 20,000 px: %s" % (
    int((bit_sizes < SLIVER).sum()), sorted(int(s) for s in bit_sizes[bit_sizes < SLIVER]),
    sorted(int(s) for s in bit_sizes[(bit_sizes >= SLIVER) & (bit_sizes < 20000)])))
picture[sliver] = PINK
line |= sliver
Image.fromarray(picture, "RGBA").save(WRITE_TO)
print("wrote %s: %d pink pixels (Kingdoms.png has %d)" % (WRITE_TO, int(line.sum()), int(((old_picture != base).any(axis=2)).sum())))

# -- the check, from the saved picture ---------------------------------------------------------------
saved = np.asarray(Image.open(WRITE_TO).convert("RGBA"))
changed = (saved != base).any(axis=2)
colours = {tuple(int(v) for v in c): int(n) for c, n in zip(*np.unique(saved[changed].reshape(-1, 4), axis=0, return_counts=True))}
print("pixels changed from WorldMapV1.png: %d, in colours %s; pink on the open sea: %d" % (changed.sum(), colours, (changed & sea).sum()))
white = (saved[..., :3] >= 250).all(axis=2)
for name, structure in (("four", None), ("eight", np.ones((3, 3)))):
    print("filling by %s neighbours: %d white pieces (wanted 23: nine kingdoms and 14 islands)" % (name, ndimage.label(white, structure=structure)[1]))
pieces, n = ndimage.label(white & mainland)
sizes = ndimage.sum_labels(white & mainland, pieces, index=np.arange(1, n + 1))
which = np.zeros(n + 1, dtype=np.int64)
for i in range(1, n + 1):
    which[i] = int(np.bincount(new[pieces == i], minlength=10).argmax())
_, (py, px) = ndimage.distance_transform_edt(pieces == 0, return_indices=True)
final = np.where(mainland, which[pieces[py, px]], 0)
final = np.where(land & ~mainland, 7, final)
area = np.bincount(final[land], minlength=10)[1:] * KM * KM
print("kingdoms' areas from the picture, km2 (lines shared, islands with 7): %s" % np.round(area).astype(int).tolist())
print("a ninth is %.0f km2; furthest from it: %.2f%%; pieces of mainland: %d, kingdoms found: %s" % (
    area.mean(), 100 * np.abs(area - area.mean()).max() / area.mean(), n, sorted(which[1:].tolist())))

# -- what changed, and what the borders run along ------------------------------------------------------
moved = mainland & (new != old)
print("land that changes kingdom: %.0f km2 (%.1f%% of the mainland); by the kingdom it leaves: %s" % (
    moved.sum() * KM * KM, 100.0 * moved.sum() / mainland.sum(),
    {k: int(round((moved & (old == k)).sum() * KM * KM)) for k in range(1, 10)}))
old_core, new_core = edges_of(np.where(mainland, old, 0)), edges_of(np.where(mainland, new, 0))
from_old = ndimage.distance_transform_edt(~old_core)[new_core] * KM
print("the new border from the old: %.1f km on average, half within %.1f km, a tenth beyond %.1f km, furthest %.1f km" % (
    from_old.mean(), np.median(from_old), np.percentile(from_old, 90), from_old.max()))
river, lake, divide, ridge = fields["river"], fields["lake"], fields["divide"], fields["ridge"]
spur, brook, above, weight = more["spur"], more["brook"], more["above"], more["weight"]
front = np.zeros((h, w), dtype=bool)
for dy, dx in ((0, 1), (1, 0)):
    a = above[: h - dy, : w - dx]; b = above[dy:, dx:]
    front[: h - dy, : w - dx] |= (a != b) & (weight[: h - dy, : w - dx] > 0.3)
front &= mainland


def shares(core_px):
    total = float(core_px.sum())
    out, taken = [], np.zeros((h, w), dtype=bool)
    for name, mask, reach in (("rivers", river, 3), ("lakes", lake, 3), ("watershed lines", divide, 4), ("ridges between rivers", ridge, 4),
                              ("the foot of high country", front, 3), ("brooks", brook, 3), ("spurs", spur, 3)):
        on = core_px & ndimage.binary_dilation(mask, iterations=reach) & ~taken
        taken |= on
        out.append("%s %.0f%%" % (name, 100.0 * on.sum() / total))
    out.append("nothing %.0f%%" % (100.0 * (core_px & ~taken).sum() / total))
    return "about %.0f km: " % (total * KM) + ", ".join(out)


print("the old borders run along: " + shares(old_core))
print("the new borders run along: " + shares(new_core))
import pickle
with open(OUT + "/settlements.pickle", "rb") as handle:
    settlements = pickle.load(handle)
swapped = {"kingdom": 0, "duchy": 0, "county": 0}
for c, (x, y) in settlements["centres"].items():
    if mainland[y, x] and new[y, x] != old[y, x]:
        swapped[settlements["rank"][c]] += 1
print("capitals that would lie in another kingdom: %s" % swapped)

if LOOK:
    height = fields["height"]
    z = ndimage.gaussian_filter(height.astype(np.float32), 1.2)
    gy, gx = np.gradient(z)
    steep = 8.0 / 335.0
    shade = (-gx * steep - gy * steep + 1.0) / np.sqrt((gx * steep) ** 2 + (gy * steep) ** 2 + 1.0) / np.sqrt(3.0)
    shade = np.clip(0.45 + 0.75 * shade, 0.25, 1.15)
    stops = np.array([0, 150, 500, 1200, 2200, 3400], dtype=np.float32)
    tints = np.array([[205, 225, 190], [225, 232, 195], [235, 222, 180], [215, 190, 155], [200, 185, 175], [250, 250, 250]], dtype=np.float32)
    look = np.stack([np.interp(z, stops, tints[:, c]) for c in range(3)], axis=2) * shade[..., None]
    look = np.clip(look, 0, 255).astype(np.uint8)
    look[~land] = base[..., :3][~land]
    look[ndimage.binary_dilation(divide, iterations=1) & mainland] = (190, 130, 80)
    look[river | lake] = (60, 130, 225)
    look[ndimage.binary_dilation(old_core, iterations=1)] = (40, 40, 40)
    look[line] = PINK[:3]
    Image.fromarray(look).save(KING + "/look_%s_full.png" % TAG)
    Image.fromarray(look).resize((w // 2, h // 2), Image.LANCZOS).save(KING + "/look_%s.png" % TAG)
    print("saved look_%s.png (the old border in black, the new in pink)" % TAG)
