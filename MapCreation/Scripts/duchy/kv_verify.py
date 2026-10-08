"""Check Kingdoms2.png from the saved pictures alone, and say what it does to the pictures made
on the old borders.

Usage: kv_verify.py <MapCreation dir>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
FOLDER = sys.argv[1]
KM = 0.335
PINK, PURPLE, GREY = (233, 0, 255), (110, 30, 180), (128, 128, 128)
BLUE, BROWN = (28, 112, 224), (196, 118, 44)
MIDDLES = {1: (993, 944), 2: (1492, 691), 3: (1698, 1942), 4: (2192, 1315), 5: (2484, 2087), 6: (582, 1454), 7: (1079, 2254), 8: (1916, 2906), 9: (2409, 3521)}


def read(name):
    picture = Image.open("%s/%s" % (FOLDER, name))
    return picture, np.asarray(picture.convert("RGB"))


def is_colour(picture, colour):
    return (picture == np.array(colour, dtype=np.uint8)).all(axis=2)


base_file, base = read("WorldMapV1.png")
new_file, new = read("Kingdoms2.png")
_, old = read("Kingdoms.png")
land = (base >= 250).all(axis=2)
print("Kingdoms2.png: %s, %s; WorldMapV1.png: %s, %s" % (new_file.size, new_file.mode, base_file.size, base_file.mode))
changed = (new != base).any(axis=2)
colours = {tuple(int(v) for v in c): int(n) for c, n in zip(*np.unique(new[changed].reshape(-1, 3), axis=0, return_counts=True))}
print("pixels unlike WorldMapV1.png: %d, in colours %s; of them on land %d, on the coast's ink or its ripples %d" % (
    changed.sum(), colours, (changed & land).sum(), (changed & ~land).sum()))
alpha = np.asarray(new_file.convert("RGBA"))[..., 3]
print("alpha: %s" % np.unique(alpha).tolist())
print("land (white in WorldMapV1.png): %d px = %.0f km2; a ninth: %.0f km2" % (land.sum(), land.sum() * KM * KM, land.sum() * KM * KM / 9))


def kingdoms_of(picture, name):
    """The kingdom of every land pixel: the white piece it is in, or the nearest one if it is under a line."""
    white = (picture >= 250).all(axis=2)
    for label, structure in (("four", None), ("eight", np.ones((3, 3)))):
        print("  %s, white pieces filling by %s neighbours: %d" % (name, label, ndimage.label(white, structure=structure)[1]))
    parts, count = ndimage.label(white)
    sizes = ndimage.sum_labels(white, parts, index=np.arange(1, count + 1))
    big = np.argsort(-sizes)[:9] + 1
    number = np.zeros(count + 1, dtype=np.int16)
    for k, (x, y) in MIDDLES.items():
        assert white[y, x], "kingdom %d's middle is not white in %s" % (k, name)
        number[parts[y, x]] = k
    assert sorted(number[big].tolist()) == list(range(1, 10)), "the nine largest pieces are not the nine kingdoms in %s" % name
    isles = [int(s) for s in np.sort(sizes)[::-1][9:]]
    print("  %s: nine large pieces and %d small ones (the islands), the largest of those %d px, %d px in all" % (name, len(isles), isles[0], sum(isles)))
    number[(number == 0) & (np.arange(count + 1) > 0)] = 7          # the islands go with kingdom 7
    held = number[parts]
    mainland_white = np.isin(parts, big)
    _, (iy, ix) = ndimage.distance_transform_edt(~mainland_white, return_indices=True)
    nearest = held[iy, ix]
    out = np.where(white, held, nearest)
    return np.where(land, out, 0)


print("pieces:")
new_k = kingdoms_of(new, "Kingdoms2.png")
old_k = kingdoms_of(old, "Kingdoms.png")
for name, grid in (("Kingdoms2.png", new_k), ("Kingdoms.png", old_k)):
    area = np.bincount(grid[land], minlength=10)[1:] * KM * KM
    off = 100.0 * (area - area.mean()) / area.mean()
    print("%s: areas km2 %s; from a ninth, %% %s; furthest %.2f%%" % (name, np.round(area).astype(int).tolist(), np.round(off, 2).tolist(), np.abs(off).max()))
moved = land & (new_k != old_k)
print("land in another kingdom than in Kingdoms.png: %d px = %.0f km2 = %.2f%% of the land" % (moved.sum(), moved.sum() * KM * KM, 100.0 * moved.sum() / land.sum()))
for k in range(1, 10):
    lost = (moved & (old_k == k)).sum() * KM * KM
    won = (moved & (new_k == k)).sum() * KM * KM
    print("  kingdom %d: gives up %5.0f km2, gains %5.0f km2" % (k, lost, won))

# -- the lines themselves -------------------------------------------------------------------------------
for name, picture in (("Kingdoms2.png", new), ("Kingdoms.png", old)):
    pink = is_colour(picture, PINK)
    deep = ndimage.distance_transform_edt(pink)
    middle = pink & (deep >= 2.0)
    print("%s: pink %d px; deepest point of a line %.1f px from its edge; pink on land %d, off it %d" % (
        name, pink.sum(), deep.max(), (pink & land).sum(), (pink & ~land).sum()))
new_pink, old_pink = is_colour(new, PINK), is_colour(old, PINK)
from_old = ndimage.distance_transform_edt(~old_pink)[new_pink] * KM
print("new pink from old pink: on it %.1f%%; %.1f km on average; half within %.1f km; a tenth beyond %.1f km; furthest %.1f km" % (
    100.0 * (from_old == 0).mean(), from_old.mean(), np.median(from_old), np.percentile(from_old, 90), from_old.max()))

# -- against the water and the watersheds -------------------------------------------------------------
_, water = read("Water.png")
_, rivers = read("Rivers.png")
blue = is_colour(water, BLUE)
brown = is_colour(rivers, BROWN)
lakes = ndimage.binary_opening(blue, structure=np.ones((3, 3), bool), iterations=7)        # water over 14 px across: a lake, or a river's widest reach
lakes = ndimage.binary_dilation(lakes, structure=np.ones((3, 3), bool), iterations=7) & blue
for name, pink in (("Kingdoms2.png", new_pink), ("Kingdoms.png", old_pink)):
    on_land = pink & land
    total = float(on_land.sum())
    on_blue = on_land & blue
    near_blue = on_land & ndimage.binary_dilation(blue, iterations=2)
    near_brown = on_land & ndimage.binary_dilation(brown, iterations=2) & ~near_blue
    print("%s: of the pink on land, %.0f%% lies on Water.png's blue (%.0f%% on its lakes and widest water), %.0f%% on or within 2 px of it; a further %.0f%% on or within 2 px of Rivers.png's brown" % (
        name, 100 * on_blue.sum() / total, 100 * (on_land & lakes).sum() / total, 100 * near_blue.sum() / total, 100 * near_brown.sum() / total))

# -- against the settlements, duchies and counties made on the old borders -------------------------------
_, settlements = read("Settlements.png")
_, counties = read("Counties.png")
_, duchies = read("Duchies.png")
dots = (settlements != counties).any(axis=2)
dot_parts, dot_count = ndimage.label(dots, structure=np.ones((3, 3)))
centres = ndimage.center_of_mass(dots, dot_parts, index=np.arange(1, dot_count + 1))
ranks = {PINK: "kingdom", PURPLE: "duchy", GREY: "county"}
tally = {"kingdom": [0, 0, 0], "duchy": [0, 0, 0], "county": [0, 0, 0]}        # dots, in another kingdom, under the new line
touched = []
for i, (cy, cx) in enumerate(centres, start=1):
    y, x = int(round(cy)), int(round(cx))
    rank = ranks.get(tuple(int(v) for v in settlements[y, x]), "?")
    here = dot_parts == i if False else None
    tally[rank][0] += 1
    if new_k[y, x] != old_k[y, x]:
        tally[rank][1] += 1
window = ndimage.find_objects(dot_parts)
for i, box in enumerate(window, start=1):
    if (new_pink[box] & (dot_parts[box] == i)).any():
        cy, cx = centres[i - 1]
        rank = ranks.get(tuple(int(v) for v in settlements[int(round(cy)), int(round(cx))]), "?")
        tally[rank][2] += 1
        touched.append((rank, int(round(cx)), int(round(cy))))
print("settlements in Settlements.png: %d dots; by rank [dots, now in another kingdom, under the new line]: %s" % (dot_count, tally))
if touched:
    print("  dots the new line runs over: %s" % touched)
gap = ndimage.distance_transform_edt(~new_pink)
nearest = sorted((float(gap[int(round(cy)), int(round(cx))]) * KM, int(round(cx)), int(round(cy))) for cy, cx in centres)[:5]
print("  the settlements nearest the new line (km from the dot's middle, x, y): %s" % [(round(d, 1), x, y) for d, x, y in nearest])


def cut(picture, name, least):
    """How many of a picture's white pieces the new borders cut, giving each side at least `least` of the piece."""
    white = (picture >= 250).all(axis=2) & land
    parts, count = ndimage.label(white)
    sizes = np.bincount(parts.ravel(), minlength=count + 1)
    table = np.zeros((count + 1, 10), dtype=np.int64)
    np.add.at(table, (parts[white], new_k[white]), 1)
    whole = [i for i in range(1, count + 1) if sizes[i] >= 3000]
    split = [i for i in whole if np.sort(table[i])[-2] >= least * sizes[i]]
    lost = sum(int(np.sort(table[i])[-2]) for i in split) * KM * KM
    print("%s: %d pieces of 3,000 px or more; the new borders cut %d of them with at least %.0f%% on the lesser side (%.0f km2 on those lesser sides)" % (
        name, len(whole), len(split), 100 * least, lost))


for least in (0.01, 0.05, 0.20):
    cut(duchies, "Duchies.png", least)
    cut(counties, "Counties.png", least)
print("done")
