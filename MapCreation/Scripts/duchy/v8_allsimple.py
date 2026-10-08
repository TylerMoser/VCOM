"""Is AllSimple.png everything in All.png on the outline of Continent.png? Checked from the
pictures alone.

Usage: v8_allsimple.py <folder of the pictures> [name of the picture]
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize

Image.MAX_IMAGE_PIXELS = None
FOLDER = sys.argv[1]
NAME = sys.argv[2] if len(sys.argv) > 2 else "AllSimple.png"
SEA, WHITE, BLACK = (181, 235, 255), (255, 255, 255), (0, 0, 0)
BLUE, RED, UMBER = (28, 112, 224), (200, 40, 30), (60, 35, 15)
RANKS = (("kingdom", (233, 0, 255)), ("duchy", (110, 30, 180)), ("county", (128, 128, 128)))
KINDS = {"water": BLUE, "kingdom border": RANKS[0][1], "duchy border": RANKS[1][1], "county border": RANKS[2][1], "road": RED, "bridge": UMBER}
SQUARE = np.ones((3, 3), dtype=bool)
SHEET, INTO = 400, 3
problems = []


def said(ok, text):
    print(("ok    " if ok else "WRONG ") + text)
    if not ok:
        problems.append(text)


def load(name):
    return np.asarray(Image.open(FOLDER + "/" + name).convert("RGBA"))


def is_colour(picture, colour):
    return (picture[..., 0] == colour[0]) & (picture[..., 1] == colour[1]) & (picture[..., 2] == colour[2])


def disc(radius):
    r = int(np.floor(radius))
    y, x = np.ogrid[-r: r + 1, -r: r + 1]
    return x * x + y * y <= radius * radius


image = Image.open(FOLDER + "/" + NAME)
said(image.size == (3100, 4000) and image.mode == "RGBA", "%s is %d x %d, %s" % (NAME, image.size[0], image.size[1], image.mode))
simple, everything, cont, old, water_png, counties, settlements, roads = (load(n) for n in (
    NAME, "All.png", "Continent.png", "WorldMapV1.png", "Water.png", "Counties.png", "Settlements.png", "Roads.png"))
h, w = simple.shape[:2]
said(int(simple[..., 3].min()) == 255, "nothing is transparent")
base = is_colour(simple, SEA) | is_colour(simple, WHITE) | is_colour(simple, BLACK)
marked = np.zeros((h, w), dtype=bool)
for colour in KINDS.values():
    marked |= is_colour(simple, colour)
said(int((base | marked).sum()) == h * w, "nine colours and no others: sea, white, black, and the six of the marks (pixels of any other colour: %d). Nothing is left of the hand-drawn ink" % (h * w - (base | marked).sum()))
said(bool((simple[base] == cont[base]).all()), "wherever nothing is drawn, the picture is Continent.png: its sea, its land, its black shoreline (%d px)" % base.sum())
new_land, new_line = is_colour(cont, WHITE), is_colour(cont, BLACK)
old_land = (old[..., :3] >= 250).all(axis=2)
reach = ndimage.binary_dilation(new_land, structure=SQUARE, iterations=INTO)
deck = is_colour(simple, UMBER)
said(not (marked & ~reach & ~deck).any(), "no river, border or road is drawn further than %d px off the land (such pixels: %d)" % (INTO, (marked & ~reach & ~deck).sum()))
covered = new_line & marked
said(bool(((new_line & ~reach) == (new_line & ~reach & (is_colour(simple, BLACK) | deck))).all()),
     "the shoreline is whole: its outer %d px are black everywhere but under the one bridge at sea (%d px of the line are under a river's mouth, a border's end or that bridge)" % (7 - INTO, covered.sum()))

# -- the marks are All.png's -----------------------------------------------------------------------------
drawn = (everything[..., :3] != old[..., :3]).any(axis=2)
differs = np.zeros((h, w), dtype=bool)
tally = {}
for name, colour in KINDS.items():
    was, now = drawn & is_colour(everything, colour), is_colour(simple, colour)
    tally[name] = (int(was.sum()), int(now.sum()), int((was != now).sum()))
    differs |= was != now
places, n_places = ndimage.label(ndimage.binary_dilation(differs, structure=SQUARE, iterations=8), structure=SQUARE)
where = [tuple(int(v) for v in reversed(ndimage.center_of_mass(places == i))) for i in range(1, n_places + 1)]
sizes = ndimage.sum_labels(differs, places, index=np.arange(1, n_places + 1)).astype(int).tolist() if n_places else []
ys = np.nonzero(differs)[0]
from_join = np.abs(((ys + SHEET // 2) % SHEET) - SHEET // 2 + 0.5).max() if len(ys) else 0.0
said(n_places <= 4 and from_join <= 24, "every mark is All.png's, pixel for pixel, but for %d px in %d places, all within %d rows of a join between the hand-drawn sheets: %s" % (
    differs.sum(), n_places, int(np.ceil(from_join)), list(zip(where, sizes))))
for name, (was, now, changed) in tally.items():
    print("      %-15s %7d px in All.png, %7d here, %3d differ" % (name, was, now, changed))
dots = (settlements != counties).any(axis=2)
said(tally["road"][2] == 0 and tally["bridge"][2] == 0 and bool((simple[dots] == settlements[dots]).all()), "roads, bridges and the capitals' dots are exactly All.png's")
said(bool((is_colour(simple, RED) == is_colour(roads, RED)).all()) and bool((deck == is_colour(roads, UMBER)).all()), "and exactly Roads.png's")
pieces, _ = ndimage.label(new_land, structure=SQUARE)
at_sea = deck & ~new_land
marks, _ = ndimage.label(deck, structure=SQUARE)
bridge = marks == marks[at_sea][0] if at_sea.any() else at_sea
shores = set(np.unique(pieces[ndimage.binary_dilation(bridge, structure=SQUARE, iterations=2)]).tolist()) - {0}
said(len(set(np.unique(marks[at_sea]).tolist())) == 1 and len(shores) == 2, "one bridge is at sea, and it stands on two pieces of land (%d px of it off the land)" % at_sea.sum())

# -- rivers' mouths and borders' ends reach the new coast ------------------------------------------------
lost, ends = [], 0
for name in ("water", "kingdom border", "duchy border", "county border"):
    colour = KINDS[name]
    was = drawn & is_colour(everything, colour) & ~dots & ~old_land        # where it ran off the old land
    now = is_colour(simple, colour) & ~dots & new_line                      # where it runs into the new line
    near_now = ndimage.distance_transform_edt(~now)
    found, n = ndimage.label(was, structure=SQUARE)
    ends += n
    for i, far in enumerate(ndimage.minimum(near_now, found, index=np.arange(1, n + 1)), start=1):
        if far > 12.0:
            lost.append((name, tuple(int(v) for v in reversed(ndimage.center_of_mass(found == i)))))
said(not lost, "every river's mouth and border's end that reached the coast in All.png (%d places) runs into the new shoreline (those that do not: %s)" % (ends, lost))
# No two counties run together: each white piece here lies in one white piece of Counties.png.
county_pieces, _ = ndimage.label((counties[..., :3] >= 250).all(axis=2) & old_land)
white_here, n_white = ndimage.label(is_colour(simple, WHITE))
index = np.arange(1, n_white + 1)
least = ndimage.minimum(np.where(county_pieces > 0, county_pieces, 10 ** 6), white_here, index=index)
most = ndimage.maximum(county_pieces, white_here, index=index)
mixed = int(((least != most) & (least < 10 ** 6)).sum())
said(mixed == 0, "no border leaks: every one of the %d white pieces here lies within a single county (and island) of Counties.png (pieces spanning two: %d)" % (n_white, mixed))

# -- no line hides another, as in All.png ----------------------------------------------------------------
blue = is_colour(water_png, BLUE)
shown = is_colour(simple, BLUE)
hidden = blue & ~shown
border_now = np.zeros((h, w), dtype=bool)
for _, colour in RANKS:
    border_now |= is_colour(simple, colour)
under_border = hidden & border_now & ~dots
cut = hidden & ~dots & ~deck & ~border_now                 # a river's mouth cut back at a join: the outline shows
open_water = ndimage.binary_opening(blue, structure=disc(4.0))
said(not (under_border & ~open_water).any() and cut.sum() <= 20, "no river lies under a border: %d of the water's %d px show; the rest is under dots (%d), bridges (%d), borders crossing lakes (%d), or cut back at a join (%d)" % (
    shown.sum(), blue.sum(), (hidden & dots).sum(), (hidden & deck & ~dots).sum(), under_border.sum(), cut.sum()))
said(not (shown & ~blue & ~ndimage.binary_dilation(blue, structure=SQUARE, iterations=6)).any(), "water is drawn only where Water.png has it, or within 6 px of that where a river's mouth is carried on to the new coast (%d px)" % (shown & ~blue).sum())
drawn_lines = (counties[..., :3] != old[..., :3]).any(axis=2)
worst = 0.0
for name, colour in RANKS:
    line = drawn_lines & is_colour(counties, colour)
    middle = skeletonize(line)
    showing = is_colour(simple, colour) & ~dots
    lost_middle = middle & ~showing
    away = ndimage.distance_transform_edt(~showing)
    deepest = float(away[lost_middle].max()) if lost_middle.any() else 0.0
    worst = max(worst, deepest)
    print("      %s borders: %.1f%% of the line shows; where its middle does not, its colour shows within %.1f px" % (name, 100.0 * (line & showing).sum() / line.sum(), deepest))
said(worst <= 11.0, "no border is lost under a river or a road: its colour shows within %.1f px of any hidden point of its middle" % worst)
print()
print("ALL RIGHT: %s is All.png on the standard outline" % NAME if not problems else "PROBLEMS: %d\n  %s" % (len(problems), "\n  ".join(problems)))
