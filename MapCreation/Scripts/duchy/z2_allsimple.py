"""AllSimple.png: everything All.png draws, on the standard outline of Continent.png.

All.png is the hand-drawn coast map (WorldMapV1.png) with marks drawn on it: water, the three
ranks of border, roads, bridges and the capitals' dots. Every mark is taken as it is, pixel for
pixel, and put on Continent.png. Two kinds of mark cross the coast: a river's mouth and a
border's end each run 3 px into the coast's line, so that the river is seen to reach the sea and
the border closes its region off. Continent.png's land is the coast map's but at the 13 joins
between the hand-drawn sheets, and there those ends are fitted to the coast as it is now:

  - a mark that would lie more than 3 px off the new land is cut back to 3 px;
  - where the new coast lies further out than the old one, a river's mouth or a border's end
    that reached the old coast is carried straight on to 3 px beyond the new one;
  - marks that belong to the land alone (roads, bridges, dots, a border's colour beside a river
    or road) are kept wherever they are still on land. The one bridge over the sea stays whole.

Usage: z2_allsimple.py <MapCreation dir> <picture to write> <facts .json to write> [folder for trial pictures]
"""
import json
import os
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
MAPS, WRITE_TO, FACTS_TO = sys.argv[1:4]
LOOK = sys.argv[4] if len(sys.argv) > 4 else None
SEA, WHITE, BLACK = (181, 235, 255), (255, 255, 255), (0, 0, 0)
KINDS = {"water": (28, 112, 224), "pink": (233, 0, 255), "purple": (110, 30, 180), "grey": (128, 128, 128), "road": (200, 40, 30), "bridge": (60, 35, 15)}
INTO = 3                 # px a river's mouth or a border's end runs into the coast's line, counted as squares
SQUARE = np.ones((3, 3), dtype=bool)


def load(name):
    return np.asarray(Image.open(MAPS + "/" + name).convert("RGBA"))


def is_colour(picture, colour):
    return (picture[..., 0] == colour[0]) & (picture[..., 1] == colour[1]) & (picture[..., 2] == colour[2])


old, cont, everything, counties, settlements = (load(n) for n in ("WorldMapV1.png", "Continent.png", "All.png", "Counties.png", "Settlements.png"))
h, w = old.shape[:2]
old_land = (old[..., :3] >= 250).all(axis=2)
new_land = is_colour(cont, WHITE)
new_line = is_colour(cont, BLACK)
reach_old = ndimage.binary_dilation(old_land, structure=SQUARE, iterations=INTO)     # the land and as far off it as a mark may run
reach_new = ndimage.binary_dilation(new_land, structure=SQUARE, iterations=INTO)
_, (near_y, near_x) = ndimage.distance_transform_edt(~reach_old, return_indices=True)   # for a pixel beyond the old reach, the nearest pixel within it
further = reach_new & ~reach_old                         # where the new coast lies further out than the old


def onto_outline(picture, land_only):
    """[picture], which is the coast map with marks on it, drawn again on the standard outline.
    [land_only] is the marks that never leave the land (and the bridge over the sea)."""
    drawn = (picture[..., :3] != old[..., :3]).any(axis=2)
    crossing = drawn & ~land_only                        # rivers and borders' lines
    assert not (crossing & ~reach_old).any(), "a river or a border lies further off the land than %d px" % INTO
    out = cont.copy()
    here = crossing & reach_new                          # as it is, cut back to the new reach
    out[here] = picture[here]
    carried = further & crossing[near_y, near_x]         # carried straight on to the new reach
    out[carried] = picture[near_y[carried], near_x[carried]]
    stay = drawn & land_only & (new_land | ~old_land)    # on land still, or the bridge at sea
    out[stay] = picture[stay]
    out[..., 3] = 255
    tally = {"marks": int(drawn.sum()), "kept": int(here.sum() + stay.sum()), "cut_back": int((crossing & ~reach_new).sum()),
             "carried_on": int(carried.sum()), "land_marks_lost": int((drawn & land_only & old_land & ~new_land).sum())}
    return out, tally


# The duchies' picture has, in one place only, a patch of purple where its border is not a line.
# Above the join at (2686, 2400) the hand-drawn coast stood 5 px further out than below it, which
# left a strip of land 8 px wide hanging off the duchy to the south by a neck 2 px wide; the
# duchies' picture inked the strip over. On the mended coast there is no step and no strip: the
# border runs along the three rows under the patch straight to the sea. So the patch is not
# drawn, and the border's end is carried on to the coast as every other border's is.
PATCH_ROWS, PATCH_COLS, END_ROWS = (2380, 2400), (2677, 2701), (2400, 2403)


def plain_border(out):
    """In place: the one patch of purple drawn as a line's end. Returns (px taken out, px put in)."""
    purple = KINDS["purple"]
    rows, cols = slice(*PATCH_ROWS), slice(*PATCH_COLS)
    patch = is_colour(out[rows, cols], purple)
    if not patch.any():
        return 0, 0
    assert 150 <= patch.sum() <= 220, "the patch of purple is not what it was: %d px" % patch.sum()
    out[rows, cols][patch] = cont[rows, cols][patch]     # what the outline has there: land, or the coast's line
    put = 0
    for y in range(*END_ROWS):
        xs = np.flatnonzero(is_colour(out[y, PATCH_COLS[0] - 20: PATCH_COLS[1]], purple))
        assert len(xs), "the border's end is not in row %d" % y
        x = PATCH_COLS[0] - 20 + int(xs.max()) + 1
        while reach_new[y, x]:
            assert tuple(out[y, x, :3]) in (WHITE, BLACK), "something else is drawn where the border's end goes"
            out[y, x, :3] = purple
            put += 1
            x += 1
    return int(patch.sum()), put


def white_pieces(picture):
    white = is_colour(picture, WHITE)
    return int(ndimage.label(white)[1]), int(ndimage.label(white, structure=SQUARE)[1])


# -- the borders' own pictures, as a test that every region stays closed on the new outline --------------
facts = {"into_px": INTO, "sealed": {}}
nothing = np.zeros((h, w), dtype=bool)
for name, wanted in (("Kingdoms.png", 23), ("Duchies.png", 58), ("Counties.png", 233)):
    trial, tally = onto_outline(load(name), nothing)
    taken, put = plain_border(trial)
    if taken:
        print("%s: the patch of purple at the join (2686, 2400): %d px not drawn, the border's end carried on by %d px" % (name, taken, put))
    four, eight = white_pieces(trial)
    before = white_pieces(np.where((load(name)[..., :3] >= 250).all(axis=2)[..., None], np.uint8(255), load(name)))
    facts["sealed"][name] = {"four": four, "eight": eight, "wanted": wanted, "cut_back": tally["cut_back"], "carried_on": tally["carried_on"]}
    print("%s on the standard outline: white pieces by four neighbours %d, by eight %d (wanted %d; on the hand-drawn coast %s); ends cut back %d px, carried on %d px" % (
        name, four, eight, wanted, before, tally["cut_back"], tally["carried_on"]))
    assert four == eight == wanted, "%s does not close its regions on the new outline" % name
    if LOOK and name == "Counties.png":
        Image.fromarray(trial, "RGBA").save(LOOK + "/CountiesSimple_trial.png")

# -- everything ----------------------------------------------------------------------------------------
dots = (settlements != counties).any(axis=2)
drawn = (everything[..., :3] != old[..., :3]).any(axis=2)
land_only = drawn & (is_colour(everything, KINDS["road"]) | is_colour(everything, KINDS["bridge"]) | dots)
for name in ("pink", "purple", "grey"):                 # a border's colour that is not its line: beside a river or a road
    land_only |= drawn & is_colour(everything, KINDS[name]) & ~is_colour(counties, KINDS[name])
picture, tally = onto_outline(everything, land_only)
tally["patch_not_drawn"], tally["patch_end_carried"] = plain_border(picture)
print("the patch of purple at the join (2686, 2400): %d px not drawn, the border's end carried on by %d px" % (tally["patch_not_drawn"], tally["patch_end_carried"]))
Image.fromarray(picture, "RGBA").save(WRITE_TO)
saved = np.asarray(Image.open(WRITE_TO).convert("RGBA"))
assert (saved == picture).all()
print("wrote %s" % WRITE_TO)
print("marks in All.png: %d px; kept where they are %d; cut back at the coast %d; carried on to the new coast %d; land marks lost where land is gone %d" % (
    tally["marks"], tally["kept"], tally["cut_back"], tally["carried_on"], tally["land_marks_lost"]))
facts.update(tally)

# -- what it holds -------------------------------------------------------------------------------------
colours = {"sea": int(is_colour(saved, SEA).sum()), "white": int(is_colour(saved, WHITE).sum()), "black": int(is_colour(saved, BLACK).sum())}
for name, colour in KINDS.items():
    colours[name] = int(is_colour(saved, colour).sum())
facts["colours"] = colours
facts["other_px"] = int(h * w - sum(colours.values()))
print("pixels by colour: %s; of any other colour: %d" % (colours, facts["other_px"]))
before = {name: int((drawn & is_colour(everything, colour)).sum()) for name, colour in KINDS.items()}
print("the same marks in All.png: %s" % before)
facts["marks_in_all"] = before
differs = np.zeros((h, w), dtype=bool)
for name, colour in KINDS.items():
    differs |= is_colour(saved, colour) != (drawn & is_colour(everything, colour))
places, n_places = ndimage.label(ndimage.binary_dilation(differs, structure=SQUARE, iterations=8), structure=SQUARE)
where = [tuple(int(v) for v in reversed(ndimage.center_of_mass(places == i))) for i in range(1, n_places + 1)]
sizes = ndimage.sum_labels(differs, places, index=np.arange(1, n_places + 1)).astype(int).tolist() if n_places else []
facts["marks_differ_px"] = int(differs.sum())
facts["marks_differ_at"] = [{"at": list(p), "px": s} for p, s in zip(where, sizes)]
print("marks that differ from All.png's: %d px in %d places: %s" % (differs.sum(), n_places, list(zip(where, sizes))))
# Rivers' mouths and borders' ends: how many places each kind runs off the land, before and after.
ends = {}
for name in ("water", "pink", "purple", "grey"):
    colour = KINDS[name]
    was = ndimage.label(drawn & is_colour(everything, colour) & ~dots & ~old_land, structure=SQUARE)[1]
    now = ndimage.label(is_colour(saved, colour) & ~dots & ~new_land, structure=SQUARE)[1]
    ends[name] = {"in_all": int(was), "here": int(now)}
facts["runs_off_the_land"] = ends
print("places where each kind runs off the land, in All.png and here: %s" % ends)
to_new = ndimage.distance_transform_edt(~new_land)
off = np.zeros((h, w), dtype=bool)
for name in ("water", "pink", "purple", "grey", "road"):
    off |= is_colour(saved, KINDS[name]) & ~reach_new
facts["marks_beyond_reach"] = int(off.sum())
at_sea = is_colour(saved, KINDS["bridge"]) & ~new_land
facts["bridge_off_land_px"] = int(at_sea.sum())
print("marks further than %d px off the land, the sea's bridge apart: %d px; the bridge's pixels off the land: %d" % (INTO, off.sum(), at_sea.sum()))
facts["bytes"] = os.path.getsize(WRITE_TO)
with open(FACTS_TO, "w", encoding="utf-8") as handle:
    json.dump(facts, handle, indent=1)
print("saved %s (%d bytes of picture)" % (FACTS_TO, facts["bytes"]))
