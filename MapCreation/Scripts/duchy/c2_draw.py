"""Draw the counties' borders in grey over Duchies.png, and check the picture by itself.

The shares come from c1_counties.py already tidied (tidy.py), so they are drawn as found. Lines
are 2 px, hard-edged, and stop at the duchies' purple, the kingdoms' pink and three pixels into
the coast's ink, so every county is sealed for a paint-bucket fill, by four neighbours or by
eight.

Usage: c2_draw.py <repo root> <duchy out dir> <tag> <picture to write> [look]
"""
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT, TAG, WRITE_TO = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
LOOK = len(sys.argv) > 5
GREY = (128, 128, 128, 255)
PURPLE = (110, 30, 180)
PINK = (233, 0, 255)
INTO_INK = 3
SLIVER = 400             # px: a sealed bit of land smaller than this, between lines, is inked over
KM = 0.335

base = np.asarray(Image.open(ROOT + "/MapCreation/Duchies.png").convert("RGBA"))
coast = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
h, w = base.shape[:2]
fields = np.load(OUT + "/fields1.npz")
king = fields["king"]
river, lake, divide, ridge = fields["river"], fields["lake"], fields["divide"], fields["ridge"]
mainland = king > 0
with open(OUT + "/counties_%s.pickle" % TAG, "rb") as handle:
    data = pickle.load(handle)
results, isles, isle_duchy, duchy = data["results"], data["isles"], data["isle_duchy"], data["duchy"]
land = duchy > 0
islands = land & ~mainland
pink = (base[..., 0] == PINK[0]) & (base[..., 1] == PINK[1]) & (base[..., 2] == PINK[2])
purple = (base[..., 0] == PURPLE[0]) & (base[..., 1] == PURPLE[1]) & (base[..., 2] == PURPLE[2])
sea = (coast[..., 2].astype(np.int32) - coast[..., 0].astype(np.int32) >= 40) & ~land

county = np.zeros((h, w), dtype=np.int16)               # 0 off the land, else a number for each county
of_duchy, seats = [0], [None]
for number in sorted(results):
    result = results[number]
    owner = result["owner"].astype(np.int16)
    view = county[result["box"]]
    here = owner >= 0
    view[here] = len(of_duchy) + owner[here]
    for seat in result["seats"]:
        of_duchy.append(number)
        seats.append(seat)
mainland_counties = len(of_duchy) - 1
assert (county[mainland] > 0).all(), "mainland left out of every county"
several = 0
for c, box in enumerate(ndimage.find_objects(county), start=1):
    several += int(ndimage.label(county[box] == c)[1] != 1)
print("counties in more than one piece as found: %d" % several)

# The islets go whole to the nearest county of their own duchy; the isles are a county.
main_county = np.where(mainland, county, 0)
pieces, n = ndimage.label(islands & ~isles, structure=np.ones((3, 3)))
for i in range(1, n + 1):
    mine = pieces == i
    number = int(duchy[mine][0])
    box = ndimage.find_objects(mine.astype(np.uint8))[0]
    window = (slice(max(box[0].start - 400, 0), min(box[0].stop + 400, h)), slice(max(box[1].start - 400, 0), min(box[1].stop + 400, w)))
    own = np.where(duchy[window] == number, main_county[window], 0)
    _, (iy, ix) = ndimage.distance_transform_edt(own == 0, return_indices=True)
    near = own[iy, ix][mine[window]]
    county[mine] = int(np.bincount(near).argmax())
if isles.any():
    county[isles] = len(of_duchy)
    of_duchy.append(isle_duchy)
    parts, n_parts = ndimage.label(isles, structure=np.ones((3, 3)))
    greatest = parts == int(np.argmax(ndimage.sum_labels(isles, parts, index=np.arange(1, n_parts + 1)))) + 1
    worth = np.where(greatest, fields["seat"], -99.0)
    if worth.max() > -50.0:
        sy, sx = np.unravel_index(int(np.argmax(worth)), worth.shape)
    else:
        ys, xs = np.nonzero(isles)
        nearest = int(np.argmin(np.hypot(ys - ys.mean(), xs - xs.mean())))
        sy, sx = ys[nearest], xs[nearest]
    seats.append((int(sx), int(sy)))
of_duchy = np.array(of_duchy)
count = len(of_duchy) - 1
assert (county[land] > 0).all() and (of_duchy[county[land]] == duchy[land]).all(), "a county outside its duchy"

# -- the lines ---------------------------------------------------------------------------------------
_, (ny, nx) = ndimage.distance_transform_edt(main_county == 0, return_indices=True)
near_land = ndimage.binary_dilation(mainland, structure=np.ones((3, 3), dtype=bool), iterations=INTO_INK)
field = np.where(near_land, main_county[ny, nx], 0)
duchy_of = of_duchy[field]
core = np.zeros((h, w), dtype=bool)
for dy, dx in ((0, 1), (1, 0)):
    a = field[: h - dy, : w - dx]; b = field[dy:, dx:]
    meet = (a != b) & (a > 0) & (b > 0) & (duchy_of[: h - dy, : w - dx] == duchy_of[dy:, dx:])
    core[: h - dy, : w - dx] |= meet
line = ndimage.binary_dilation(core, structure=np.ones((2, 2), dtype=bool))
line &= near_land & ~pink & ~purple & ~sea
picture = base.copy()
picture[line] = GREY
# A sliver of land sealed between two lines that run close together belongs to nothing: inked over.
open_land = (picture[..., :3] >= 250).all(axis=2) & mainland
bits, n_bits = ndimage.label(open_land)
bit_sizes = ndimage.sum_labels(open_land, bits, index=np.arange(1, n_bits + 1))
sliver = np.isin(bits, np.flatnonzero(bit_sizes < SLIVER) + 1)
print("slivers inked over: %d, of %s px; other small pieces: %s" % (
    int((bit_sizes < SLIVER).sum()), sorted(int(s) for s in bit_sizes[bit_sizes < SLIVER]),
    sorted(int(s) for s in bit_sizes[(bit_sizes >= SLIVER) & (bit_sizes < 8000)])))
picture[sliver] = GREY
line |= sliver
Image.fromarray(picture, "RGBA").save(WRITE_TO)
np.save(OUT + "/county_map_%s.npy" % TAG, county)
with open(OUT + "/county_list_%s.pickle" % TAG, "wb") as handle:
    pickle.dump({"of_duchy": of_duchy, "seats": seats}, handle)
print("wrote %s: %d grey pixels" % (WRITE_TO, int(line.sum())))

# -- the check, from the saved picture ---------------------------------------------------------------
saved = np.asarray(Image.open(WRITE_TO).convert("RGBA"))
changed = (saved != base).any(axis=2)
colours = {tuple(int(v) for v in c): int(n) for c, n in zip(*np.unique(saved[changed].reshape(-1, 4), axis=0, return_counts=True))}
print("pixels changed from Duchies.png: %d, in colours %s; grey on the open sea: %d; pink or purple painted over: %d" % (
    changed.sum(), colours, (changed & sea).sum(), (changed & (pink | purple)).sum()))
white = (saved[..., :3] >= 250).all(axis=2) & mainland
for name, structure in (("four", None), ("eight", np.ones((3, 3)))):
    found, n = ndimage.label(white, structure=structure)
    print("filling by %s neighbours, the lines cut the mainland into %d pieces (wanted %d)" % (name, n, mainland_counties))
pieces, n = ndimage.label(white)
# Each piece is one county's and each mainland county has one piece.
flat_piece, flat_county = pieces[white], county[white]
pair = np.bincount(flat_piece.astype(np.int64) * (count + 1) + flat_county, minlength=(n + 1) * (count + 1)).reshape(n + 1, count + 1)
piece_county = pair.argmax(axis=1)
mixed = int((pair.sum(axis=1) - pair.max(axis=1))[1:].sum())
print("pieces holding more than one county's land: %d px astray; counties with no piece or several: %d" % (
    mixed, int((np.bincount(piece_county[1:], minlength=count + 1)[1: mainland_counties + 1] != 1).sum())))
_, (py, px) = ndimage.distance_transform_edt(pieces == 0, return_indices=True)
final = np.where(mainland, piece_county[pieces[py, px]], 0)
final = np.where(islands, county, final)                 # islands are whole pieces of the picture already
area = np.bincount(final[final > 0], minlength=count + 1).astype(np.float64) * KM * KM
print("counties: %d (%d on the mainland, the isles 1); areas %.0f to %.0f km2, mean %.0f; within %.1f%% of the island's mean" % (
    count, mainland_counties, area[1:].min(), area[1:].max(), area[1:].mean(), 100 * np.abs(area[1:] - area[1:].mean()).max() / area[1:].mean()))
worst = 0.0
print("duchy (kingdom): counties' areas in km2, smallest to largest; furthest from the duchy's mean")
table, spreads = {}, []
for number in sorted(results):
    areas = np.sort(area[np.flatnonzero(of_duchy == number)])
    off = float(np.abs(areas - areas.mean()).max() / areas.mean())
    worst = max(worst, off)
    spreads.append(off)
    kingdom = int(np.bincount(king[(duchy == number) & mainland]).argmax())
    table.setdefault(kingdom, []).append((len(areas), int(round(areas.min())), int(round(areas.max()))))
    print("  %2d (%d): %d: %s  %.1f%%" % (number, kingdom, len(areas), np.round(areas).astype(int).tolist(), 100 * off))
for kingdom, rows in sorted(table.items()):
    print("kingdom %d: %d counties in duchies of %s; %d to %d km2" % (
        kingdom, sum(r[0] for r in rows), [r[0] for r in rows], min(r[1] for r in rows), max(r[2] for r in rows)))
print("furthest any county is from its duchy's mean: %.1f%% (duchies over 3%%: %d, over 4%%: %d)" % (
    100 * worst, sum(s > 0.03 for s in spreads), sum(s > 0.04 for s in spreads)))

# What the borders run along.
total = float(core.sum())
on_river = core & ndimage.binary_dilation(river, iterations=3)
on_lake = core & ndimage.binary_dilation(lake, iterations=3) & ~on_river
on_divide = core & ndimage.binary_dilation(divide, iterations=5) & ~on_river & ~on_lake
on_ridge = core & ndimage.binary_dilation(ridge, iterations=5) & ~on_river & ~on_lake & ~on_divide
rest = total - on_river.sum() - on_lake.sum() - on_divide.sum() - on_ridge.sum()
print("county borders, about %.0f km in all: %.0f%% along rivers, %.0f%% along or across lakes, %.0f%% along the drawn watershed lines, %.0f%% along ridges between rivers, %.0f%% across open country" % (
    total * KM, 100 * on_river.sum() / total, 100 * on_lake.sum() / total, 100 * on_divide.sum() / total,
    100 * on_ridge.sum() / total, 100 * rest / total))

if LOOK:
    rng = np.random.default_rng(11)
    tints = np.vstack([[255, 255, 255], rng.integers(170, 246, size=(count, 3))]).astype(np.uint8)
    look = tints[county]
    look[~land] = (181, 235, 255)
    look[(coast[..., :3].astype(np.int32).sum(axis=2) < 300)] = 0
    look[ridge] = (212, 190, 165)
    look[ndimage.binary_dilation(divide, iterations=1)] = (200, 140, 85)
    look[river | lake] = (28, 112, 224)
    look[line] = (70, 70, 70)
    look[ndimage.binary_dilation(purple, iterations=1)] = PURPLE
    look[ndimage.binary_dilation(pink, iterations=1)] = PINK
    image = Image.fromarray(look)
    from PIL import ImageDraw
    pen = ImageDraw.Draw(image)
    duchy_seats = set()
    for number in sorted(results):
        duchy_seats.add(results[number]["seats"][0])
    for seat in seats[1:]:
        r = 9 if seat in duchy_seats else 5
        pen.ellipse([seat[0] - r, seat[1] - r, seat[0] + r, seat[1] + r], fill=(0, 0, 0), outline=(255, 255, 255), width=2)
    image.save(OUT + "/counties_look_full_%s.png" % TAG)
    image.resize((w // 2, h // 2), Image.LANCZOS).save(OUT + "/counties_look_%s.png" % TAG)
    print("saved counties_look_%s.png" % TAG)
