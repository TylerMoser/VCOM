"""What All.png draws on the coast map, and how those marks sit against the coast: how far off
the land each kind reaches, and what there is at the 13 joins where Continent.png's land differs.

Usage: z1_marks.py <MapCreation dir>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
MAPS = sys.argv[1]
SEA, WHITE, BLACK = (181, 235, 255), (255, 255, 255), (0, 0, 0)
KINDS = {"water": (28, 112, 224), "pink": (233, 0, 255), "purple": (110, 30, 180), "grey": (128, 128, 128), "road": (200, 40, 30), "bridge": (60, 35, 15)}
EIGHT = np.ones((3, 3), dtype=bool)


def load(name):
    return np.asarray(Image.open(MAPS + "/" + name).convert("RGB"))


def is_colour(picture, colour):
    return (picture == np.array(colour, dtype=np.uint8)).all(axis=2)


old, everything, cont, counties, settlements = (load(n) for n in ("WorldMapV1.png", "All.png", "Continent.png", "Counties.png", "Settlements.png"))
old_land = (old >= 250).all(axis=2)
new_land = is_colour(cont, WHITE)
new_line = is_colour(cont, BLACK)
drawn = (everything != old).any(axis=2)
to_old = ndimage.distance_transform_edt(~old_land)
to_new = ndimage.distance_transform_edt(~new_land)
print("pixels All.png draws on the coast map: %d; of them on the land %d, off it %d" % (drawn.sum(), (drawn & old_land).sum(), (drawn & ~old_land).sum()))
known = np.zeros_like(drawn)
for name, colour in KINDS.items():
    mine = drawn & is_colour(everything, colour)
    known |= mine
    off = mine & ~old_land
    if off.any():
        d = to_old[off]
        steps = sorted(set(np.round(d, 2).tolist()))
        print("%-7s %7d px; off the land %5d px, reaching %.2f px at most; distances found: %s" % (name, mine.sum(), off.sum(), d.max(), steps[:14]))
        far = off & (to_old > 3.01)
        if far.any():
            parts, n = ndimage.label(far, structure=EIGHT)
            ys, xs = np.nonzero(far)
            print("        further than 3 px off the land: %d px in %d places, x %d..%d, y %d..%d" % (far.sum(), n, xs.min(), xs.max(), ys.min(), ys.max()))
    else:
        print("%-7s %7d px; none off the land" % (name, mine.sum()))
print("drawn pixels of no known colour: %d" % (drawn & ~known).sum())
same_colour_as_old = np.zeros_like(drawn)
for name, colour in KINDS.items():
    same_colour_as_old |= is_colour(everything, colour) & ~drawn
print("pixels of a mark's colour that the coast map already had (its own grey): %d" % same_colour_as_old.sum())
# Which border-coloured pixels are lines, which are the colour put beside rivers and roads, which are dots.
dots = (settlements != counties).any(axis=2)
for name in ("pink", "purple", "grey"):
    colour = KINDS[name]
    mine = drawn & is_colour(everything, colour)
    line = mine & is_colour(counties, colour) & ~dots
    beside = mine & ~is_colour(counties, colour) & ~dots
    print("%-7s lines %6d px (off the land %4d), beside rivers and roads %5d px (off the land %d), dots %5d px (off the land %d)" % (
        name, line.sum(), (line & ~old_land).sum(), beside.sum(), (beside & ~old_land).sum(), (mine & dots).sum(), (mine & dots & ~old_land).sum()))

# What happens to the marks if they are put on Continent.png as they are.
changed = old_land != new_land
print()
print("land that differs: %d px. Marks as they are, on the new outline:" % changed.sum())
for name, colour in KINDS.items():
    mine = drawn & is_colour(everything, colour)
    in_sea = mine & ~new_land & ~new_line
    deep = mine & new_line & (to_new > 3.01)
    print("   %-7s on new land %7d, on the new line within 3 px of land %5d, deeper in the line %4d, in the sea %4d" % (
        name, (mine & new_land).sum(), (mine & new_line & (to_new <= 3.01)).sum(), deep.sum(), in_sea.sum()))
# River mouths and border ends: pieces of each kind that run off the land, in All.png.
for name in ("water", "pink", "purple", "grey"):
    mine = drawn & is_colour(everything, KINDS[name]) & ~dots
    ends, n = ndimage.label(mine & ~old_land, structure=EIGHT)
    print("%-7s runs off the land in %d places" % (name, n))
