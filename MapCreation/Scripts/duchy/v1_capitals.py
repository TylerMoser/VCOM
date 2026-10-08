"""Does every kingdom, duchy and county have its capital? Checked from the pictures alone.

A kingdom is a white piece of the kingdoms' picture, a duchy one of Duchies.png, a county one of
Counties.png; a capital is a disc that Settlements.png has and Counties.png has not: pink for a
kingdom's, purple for a duchy's, grey for a county's. A kingdom's capital is also its duchy's and
its county's, and a duchy's is also its county's, so there is one dot a county.

Usage: v1_capitals.py <folder of the pictures> [name of the kingdoms' picture]
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
FOLDER = sys.argv[1]
KINGDOMS = sys.argv[2] if len(sys.argv) > 2 else "Kingdoms.png"
PINK, PURPLE, GREY = (233, 0, 255), (110, 30, 180), (128, 128, 128)
SIZES = {"pink": 561, "purple": 277, "grey": 129}
MIDDLES = {1: (993, 944), 2: (1492, 691), 3: (1698, 1942), 4: (2192, 1315), 5: (2484, 2087), 6: (582, 1454), 7: (1079, 2254), 8: (1916, 2906), 9: (2409, 3521)}
PLAN = {1: (4, 24), 2: (4, 24), 3: (6, 24), 4: (4, 24), 5: (5, 25), 6: (5, 25), 7: (6, 23), 8: (5, 25), 9: (5, 25)}   # duchies, counties on the mainland
problems = []


def load(name):
    return np.asarray(Image.open(FOLDER + "/" + name).convert("RGB"))


def is_colour(picture, colour):
    return (picture == np.array(colour, dtype=np.uint8)).all(axis=2)


def said(ok, text):
    print(("ok    " if ok else "WRONG ") + text)
    if not ok:
        problems.append(text)


coast, kingdoms, duchies, counties, settlements = (load(n) for n in ("WorldMapV1.png", KINGDOMS, "Duchies.png", "Counties.png", "Settlements.png"))
land = (coast >= 250).all(axis=2)
parts, n_land = ndimage.label(land)
mainland = parts == int(np.argmax(np.bincount(parts.ravel())[1:])) + 1
islands = land & ~mainland

# -- each picture is the one before with one thing added ----------------------------------------------
for name, picture, under, colour in ((KINGDOMS, kingdoms, coast, PINK), ("Duchies.png", duchies, kingdoms, PURPLE), ("Counties.png", counties, duchies, GREY)):
    changed = (picture != under).any(axis=2)
    said(bool(is_colour(picture, colour)[changed].all()), "%s is the picture under it with %d pixels of one colour added" % (name, changed.sum()))
dots = (settlements != counties).any(axis=2)
dot_colours = {name: dots & is_colour(settlements, colour) for name, colour in (("pink", PINK), ("purple", PURPLE), ("grey", GREY))}
said(int(sum(m.sum() for m in dot_colours.values())) == int(dots.sum()), "Settlements.png is Counties.png with %d pixels of pink, purple and grey added" % dots.sum())
said(bool((counties[dots] >= 250).all()), "every dot lies wholly on what was white land in Counties.png")
ring = (ndimage.distance_transform_edt(~dots) <= 2.0) & ~dots
said(bool((settlements[ring] >= 250).all()), "every pixel within 2 px of a dot is white: no dot touches a border, the coast or another dot")

# -- the dots -----------------------------------------------------------------------------------------
blobs, n_dots = ndimage.label(dots, structure=np.ones((3, 3)))
index = np.arange(1, n_dots + 1)
sizes = ndimage.sum_labels(dots, blobs, index).astype(int)
middles = np.round(np.array(ndimage.center_of_mass(dots, blobs, index))).astype(int)
colour_of = []
for i, (y, x) in enumerate(middles):
    name = [c for c, mask in dot_colours.items() if mask[y, x]]
    colour_of.append(name[0] if name else "?")
    if not name or sizes[i] != SIZES[name[0]]:
        problems.append("the dot at (%d, %d) is %s of %d px" % (x, y, name, sizes[i]))
tally = {c: colour_of.count(c) for c in ("pink", "purple", "grey")}
said(n_dots == 220 and tally == {"pink": 9, "purple": 35, "grey": 176}, "dots: %d, of them pink %d, purple %d, grey %d; each a disc of its rank's size" % (n_dots, tally["pink"], tally["purple"], tally["grey"]))
colour_of = np.array(colour_of)


def pieces_of(picture):
    white = (picture >= 250).all(axis=2)
    labels, count = ndimage.label(white)
    return labels, count


# -- kingdoms -----------------------------------------------------------------------------------------
k_labels, _ = pieces_of(kingdoms)
k_of_piece = {int(k_labels[y, x]): k for k, (x, y) in MIDDLES.items()}
said(len(k_of_piece) == 9 and 0 not in k_of_piece, "the nine kingdoms are nine separate white pieces of %s" % KINGDOMS)
for name, structure in (("four", None), ("eight", np.ones((3, 3)))):
    found = ndimage.label((kingdoms >= 250).all(axis=2) & mainland, structure=structure)[1]
    said(found == 9, "%s cuts the mainland into %d pieces, filling by %s neighbours" % (KINGDOMS, found, name))
dot_kingdom = np.array([k_of_piece.get(int(k_labels[y, x]), 0) for y, x in middles])
on_island = np.array([bool(islands[y, x]) for y, x in middles])
for k in range(1, 10):
    mine = dot_kingdom == k
    pink = int((mine & (colour_of == "pink")).sum()); purple = int((mine & (colour_of == "purple")).sum()); grey = int((mine & (colour_of == "grey")).sum())
    duchies_k, counties_k = PLAN[k]
    said(pink == 1 and pink + purple == duchies_k and pink + purple + grey == counties_k,
         "kingdom %d: 1 capital wanted, %d pink dot; %d duchies wanted, %d duchy capitals (pink or purple); %d mainland counties wanted, %d dots" % (
             k, pink, duchies_k, pink + purple, counties_k, pink + purple + grey))
said(int(on_island.sum()) == 1 and colour_of[on_island][0] == "grey", "the islands hold %d dot (grey): the isles' county has its capital; it is at %s" % (
    on_island.sum(), [(int(x), int(y)) for (y, x), isle in zip(middles, on_island) if isle]))

# -- duchies ------------------------------------------------------------------------------------------
d_labels, _ = pieces_of(duchies)
d_white = (duchies >= 250).all(axis=2) & mainland
d_ids = np.unique(d_labels[d_white])
said(len(d_ids) == 44, "Duchies.png cuts the mainland into %d white pieces (44 duchies)" % len(d_ids))
seats = np.isin(colour_of, ("pink", "purple")) & ~on_island
per_duchy = np.bincount(d_labels[middles[seats, 0], middles[seats, 1]], minlength=d_labels.max() + 1)
said(bool((per_duchy[d_ids] == 1).all()), "every duchy holds exactly one pink or purple dot (duchies with none: %d, with several: %d)" % (
    int((per_duchy[d_ids] == 0).sum()), int((per_duchy[d_ids] > 1).sum())))
# a duchy lies in one kingdom
d_kingdom = {}
for d in d_ids:
    inside = k_labels[d_labels == d]
    kinds = np.unique(inside)
    d_kingdom[int(d)] = [k_of_piece.get(int(v), 0) for v in kinds]
said(all(len(v) == 1 and v[0] > 0 for v in d_kingdom.values()), "every duchy lies inside one kingdom")
per_kingdom = {k: sum(1 for v in d_kingdom.values() if v == [k]) for k in range(1, 10)}
said(per_kingdom == {k: PLAN[k][0] for k in PLAN}, "duchies in each kingdom: %s" % per_kingdom)

# -- counties -----------------------------------------------------------------------------------------
c_labels, _ = pieces_of(counties)
c_white = (counties >= 250).all(axis=2) & mainland
c_ids = np.unique(c_labels[c_white])
said(len(c_ids) == 219, "Counties.png cuts the mainland into %d white pieces (219 counties; the 220th is the isles)" % len(c_ids))
for name, structure in (("four", None), ("eight", np.ones((3, 3)))):
    found = ndimage.label(c_white, structure=structure)[1]
    said(found == 219, "filling by %s neighbours finds %d county pieces on the mainland" % (name, found))
main_dots = ~on_island
per_county = np.bincount(c_labels[middles[main_dots, 0], middles[main_dots, 1]], minlength=c_labels.max() + 1)
said(bool((per_county[c_ids] == 1).all()), "every mainland county holds exactly one dot (counties with none: %d, with several: %d)" % (
    int((per_county[c_ids] == 0).sum()), int((per_county[c_ids] > 1).sum())))
c_duchy_ok = True
c_per_duchy = {}
for c in c_ids:
    kinds = np.unique(d_labels[c_labels == c])
    c_duchy_ok &= len(kinds) == 1
    c_per_duchy[int(kinds[0])] = c_per_duchy.get(int(kinds[0]), 0) + 1
said(bool(c_duchy_ok), "every county lies inside one duchy")
counts = sorted(c_per_duchy.values())
said(set(counts) <= {3, 4, 5, 6} and counts.count(3) == 1, "counties in a duchy: %s (the duchy with 3 on the mainland has the isles as its fourth)" % {v: counts.count(v) for v in sorted(set(counts))})
# The dot's own area: a dot never straddles two counties.
whole = True
for i, box in enumerate(ndimage.find_objects(blobs), start=1):
    under = c_labels[box][blobs[box] == i]
    whole &= len(np.unique(under)) == 1
said(bool(whole), "every dot lies wholly inside one county")
print("the kingdoms' capitals (kingdom: x, y): %s" % {int(k): (int(x), int(y)) for k, (y, x) in sorted(zip(dot_kingdom[colour_of == "pink"], middles[colour_of == "pink"]))})
print()
print("ALL RIGHT: every kingdom, duchy and county has its capital" if not problems else "PROBLEMS: %d\n  %s" % (len(problems), "\n  ".join(problems)))
