"""Does any line hide another? Checked from the pictures alone.

In All.png a river must never lie under a border, and a border must never be lost under a river
or a road: where one of those runs along it, the border's colour shows along both sides. In
Roads.png, which has no water, the same holds of roads and borders.

Usage: v6_layers.py <folder of the pictures>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize

Image.MAX_IMAGE_PIXELS = None
FOLDER = sys.argv[1]
SEA = (181, 235, 255)
RED, UMBER, BLUE, BROWN = (200, 40, 30), (60, 35, 15), (28, 112, 224), (196, 118, 44)
RANKS = (("kingdom", (233, 0, 255)), ("duchy", (110, 30, 180)), ("county", (128, 128, 128)))
SQUARE = np.ones((3, 3), dtype=bool)
OUT_OF_SIGHT = 11.0      # px: no hidden point of a border's middle may be further than this from its colour showing
problems = []


def load(name):
    return np.asarray(Image.open(FOLDER + "/" + name).convert("RGB"))


def is_colour(picture, colour):
    return (picture == np.array(colour, dtype=np.uint8)).all(axis=2)


def disc(radius):
    r = int(np.floor(radius))
    y, x = np.ogrid[-r: r + 1, -r: r + 1]
    return x * x + y * y <= radius * radius


def said(ok, text):
    print(("ok    " if ok else "WRONG ") + text)
    if not ok:
        problems.append(text)


coast, water, rivers, counties, settlements, roads, everything = (load(n) for n in (
    "WorldMapV1.png", "Water.png", "Rivers.png", "Counties.png", "Settlements.png", "Roads.png", "All.png"))
land = (coast >= 250).all(axis=2)
blue = is_colour(water, BLUE)
dots = (settlements != counties).any(axis=2)
road, deck = is_colour(roads, RED), is_colour(roads, UMBER)
drawn = (counties != coast).any(axis=2)

# -- what All.png is made of ----------------------------------------------------------------------------
changed = (everything != coast).any(axis=2)
kinds = is_colour(everything, BLUE) | is_colour(everything, RED) | is_colour(everything, UMBER)
for _, colour in RANKS:
    kinds |= is_colour(everything, colour)
said(bool(kinds[changed].all()), "every pixel of All.png is the coast map's, or water, a border's colour, road or bridge (%d px changed from the coast map)" % changed.sum())
shown_blue = is_colour(everything, BLUE)
said(not (shown_blue & ~blue).any(), "All.png has water only where Water.png has it (%d px show)" % shown_blue.sum())
said(bool((is_colour(everything, RED) == road).all()) and bool((is_colour(everything, UMBER) == deck).all()) and bool((everything[dots] == settlements[dots]).all()),
     "roads, bridges and dots are those of Roads.png and nothing lies over them")

# -- water under borders --------------------------------------------------------------------------------
hidden = blue & ~shown_blue
under_dot, under_deck = hidden & dots, hidden & deck & ~dots
under_border = hidden & ~dots & ~deck
border_now = np.zeros_like(blue)
for _, colour in RANKS:
    border_now |= is_colour(everything, colour)
said(bool(border_now[under_border].all()), "water that does not show (%d px of %d, %.1f%%) is under a dot (%d), a bridge (%d) or a border's line (%d), and nothing else" % (
    hidden.sum(), blue.sum(), 100.0 * hidden.sum() / blue.sum(), under_dot.sum(), under_deck.sum(), under_border.sum()))
# A river is at most 8 px wide. Water under a border must be open water: 9 px across or more.
open_water = ndimage.binary_opening(blue, structure=disc(4.0))
said(not (under_border & ~open_water).any(), "no river lies under a border: all water under a border's line is in water at least 9 px across, the body of a lake (water under a border elsewhere: %d px)" % (
    under_border & ~open_water).sum())
core = ndimage.binary_opening(blue, structure=disc(8.0))
bodies, n_bodies = ndimage.label(ndimage.binary_propagation(core, structure=SQUARE, mask=open_water), structure=SQUARE)
index = np.arange(1, n_bodies + 1)
share = ndimage.sum_labels(shown_blue, bodies, index=index) / ndimage.sum_labels(bodies > 0, bodies, index=index)
said(bool((share > 0.5).all()), "of every lake a border crosses as a line, more than half shows (bodies of open water: %d; least showing %.0f%%; under three quarters: %d)" % (
    n_bodies, 100.0 * share.min(), (share < 0.75).sum()))
pools, n_pools = ndimage.label(blue, structure=SQUARE)
index = np.arange(1, n_pools + 1)
whole = ndimage.sum_labels(blue, pools, index=index)
seen = ndimage.sum_labels(shown_blue, pools, index=index)
least = int(np.argmin(seen / whole))
said(bool((seen > 0).all()), "no piece of water is hidden altogether (pieces of water: %d; the least showing: %.0f%% of %d px)" % (n_pools, 100.0 * seen[least] / whole[least], whole[least]))

# -- borders under rivers and roads ---------------------------------------------------------------------
for picture_name, picture in (("All.png", everything), ("Roads.png", roads)):
    for name, colour in RANKS:
        line = drawn & is_colour(counties, colour)
        middle = skeletonize(line)
        shown = is_colour(picture, colour) & ~dots
        lost = middle & ~shown
        away = ndimage.distance_transform_edt(~shown)
        deepest = float(away[lost].max()) if lost.any() else 0.0
        where = np.unravel_index(int(np.argmax(np.where(lost, away, 0.0))), lost.shape)
        runs, n_runs = ndimage.label(lost, structure=SQUARE)
        longest = int(ndimage.sum_labels(lost, runs, index=np.arange(1, n_runs + 1)).max()) if n_runs else 0
        added = shown & ~is_colour(counties, colour)
        said(deepest <= OUT_OF_SIGHT, "%s, %s borders: %.1f%% of the line shows; where its middle does not, its colour shows within %.1f px at the furthest (at %s); "
             "its colour beside a river or road: %d px" % (picture_name, name, 100.0 * (line & shown).sum() / line.sum(), deepest, (int(where[1]), int(where[0])), added.sum()))
border_extra = np.zeros_like(blue)
for _, colour in RANKS:
    border_extra |= is_colour(everything, colour) & ~is_colour(counties, colour) & ~dots
near_line = ndimage.distance_transform_edt(~(blue | road | deck)) <= 3.0
said(bool(near_line[border_extra].all()), "a border's colour is added only beside a river or a road that runs along it: %d px, all within 3 px of one" % border_extra.sum())

# -- Rivers.png -----------------------------------------------------------------------------------------
said(bool((is_colour(rivers, BLUE) == blue).all()), "in Rivers.png no watershed line lies over water: its water is Water.png's, pixel for pixel")
print()
print("ALL RIGHT: no line hides another" if not problems else "PROBLEMS: %d\n  %s" % (len(problems), "\n  ".join(problems)))
