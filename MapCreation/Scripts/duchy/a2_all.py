"""Everything on one map, with no line hiding another.

From the bottom: the coast map; the broad water of the lakes; the borders; the rivers and all
other narrow water; the roads; the bridges; the settlements' dots. So a river is never under a
border. Where a border runs along a river (its middle under the river for layers.FOLLOW px or
more) the border's colour is put along both banks, half the border's width on each; where a
border only crosses a river the river passes over it. A border across a lake is a line across
the lake. Roads, bridges and dots are as Roads.png has them, with the border's colour Roads.png
put beside any road that runs along a border.

Usage: a2_all.py <folder of the pictures> <lake mask .npy> <picture to write> <facts .json to write>
"""
import json
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
import layers
from layers import BLUE, RED, UMBER, RANKS, EIGHT, is_colour

Image.MAX_IMAGE_PIXELS = None
FOLDER, LAKE, WRITE_TO, FACTS_TO = sys.argv[1:5]


def load(name):
    return np.asarray(Image.open(FOLDER + "/" + name).convert("RGBA"))


coast, counties, settlements, roads, water = (load(n) for n in ("WorldMapV1.png", "Counties.png", "Settlements.png", "Roads.png", "Water.png"))
land = (coast[..., :3] >= 250).all(axis=2)
blue = is_colour(water, BLUE)
lake = np.load(LAKE)
assert not (lake & ~blue).any(), "the lake mask is not the lakes of Water.png"
broad = layers.broad_water(lake)
narrow = blue & ~broad
dots = (settlements != counties).any(axis=2)
road, deck = is_colour(roads, RED), is_colour(roads, UMBER)
drawn = (counties != coast).any(axis=2)                  # what the borders' pictures added to the coast map
white = (settlements[..., :3] == 255).all(axis=2) & land
allowed = white & ~blue & layers.clear_of(dots)
cover = layers.Cover(narrow, layers.WIDEST_WATER)
facts = {"water_px": int(blue.sum()), "broad_px": int(broad.sum()), "narrow_px": int(narrow.sum()), "ranks": {}}
print("water: %d px; broad (the bodies of the lakes) %d; narrow (rivers, the lakes' thin arms and the small lakes) %d, of it lake %d" % (
    blue.sum(), broad.sum(), narrow.sum(), (narrow & lake).sum()))
pools_all, n_all = ndimage.label(lake, structure=EIGHT)
with_body = len(set(np.unique(pools_all[broad]).tolist()) - {0})
facts["lakes_with_body"] = with_body
print("lakes: %d; with a body drawn under the borders: %d; wholly narrow: %d" % (n_all, with_body, n_all - with_body))
widest_narrow = 2.0 * ndimage.distance_transform_edt(narrow).max() - 1.0
print("narrow water is at most %.0f px across" % widest_narrow)
assert widest_narrow < layers.WIDEST_WATER + 2
facts["narrow_lake_px"] = int((narrow & lake).sum())

picture = coast.copy()
picture[broad] = BLUE + (255,)
lines, middles, beside = {}, {}, {}
for name, colour, margin in RANKS:
    line = drawn & is_colour(counties, colour)
    middle = layers.middle_of(line)
    run, places = cover.runs_along(middle)
    sides = cover.both_sides(run, margin) & allowed
    by_road = is_colour(roads, colour) & ~is_colour(settlements, colour)
    lines[name], middles[name], beside[name] = line, middle, sides | by_road
    picture[line | sides | by_road] = colour + (255,)
    crossings = ndimage.label(middle & narrow, structure=EIGHT)[1] - places
    facts["ranks"][name] = {"line_px": int(line.sum()), "middle_px": int(middle.sum()), "along_water_places": places, "along_water_px": int(run.sum()),
                            "crossings_of_water": int(crossings), "beside_water_px": int(sides.sum()), "beside_road_px": int(by_road.sum())}
    print("%s borders: %d px; middle under narrow water for %d px or more in %d places (%d px of middle, %.0f km); short crossings %d; colour put on the banks %d px, beside roads %d px" % (
        name, line.sum(), layers.FOLLOW, places, run.sum(), run.sum() * 0.335, crossings, sides.sum(), by_road.sum()))
picture[narrow] = BLUE + (255,)
picture[road] = RED + (255,)
picture[deck] = UMBER + (255,)
picture[dots] = settlements[dots]
Image.fromarray(picture, "RGBA").save(WRITE_TO)
saved = np.asarray(Image.open(WRITE_TO).convert("RGBA"))
assert (saved == picture).all()
print("wrote %s" % WRITE_TO)

# -- what shows ----------------------------------------------------------------------------------------
shown_blue = is_colour(saved, BLUE)
hidden = blue & ~shown_blue
under = {"dots": int((hidden & dots).sum()), "bridges": int((hidden & deck).sum()), "roads": int((hidden & road).sum())}
for name, colour, _ in RANKS:
    mine = hidden & is_colour(saved, colour) & ~dots
    under[name] = int(mine.sum())
    assert not (mine & narrow).any(), "narrow water under a %s border" % name
facts["water_shown"] = int(shown_blue.sum())
facts["water_hidden_under"] = under
print("water showing: %d of %d (%.1f%%); hidden under %s; narrow water under a border: 0" % (shown_blue.sum(), blue.sum(), 100.0 * shown_blue.sum() / blue.sum(), under))
assert sum(under.values()) == int(hidden.sum()), (sum(under.values()), int(hidden.sum()))
for name, colour, _ in RANKS:
    shown = is_colour(saved, colour) & ~dots
    line = lines[name]
    deep, where = layers.deepest_hidden(middles[name], shown)
    longest, longest_at = layers.longest_hidden(middles[name], ndimage.binary_dilation(shown, structure=layers.disc(9.5)))
    entry_more = {"longest_unseen_px": longest, "longest_unseen_at": longest_at}
    entry = facts["ranks"][name]
    entry.update({"line_shown_px": int((line & shown).sum()), "line_under_water_px": int((line & narrow).sum()), "line_under_road_px": int((line & (road | deck)).sum()),
                  "colour_px": int(shown.sum()), "deepest_hidden_px": deep, "deepest_at": where})
    entry.update(entry_more)
    print("   the longest run of its middle with none of its colour showing within 9 px: %d px at %s" % (longest, longest_at))
    print("%s borders: %d of %d px of line show (%.1f%%); under narrow water %d, under roads and bridges %d; the furthest any hidden part of the middle is from its colour showing: %.1f px at %s" % (
        name, (line & shown).sum(), line.sum(), 100.0 * (line & shown).sum() / line.sum(), (line & narrow).sum(), (line & (road | deck)).sum(), deep, where))
pools, n = ndimage.label(lake, structure=EIGHT)
whole = ndimage.sum_labels(lake, pools, index=np.arange(1, n + 1))
seen = ndimage.sum_labels(shown_blue & lake, pools, index=np.arange(1, n + 1))
share = seen / whole
order = np.argsort(share)
facts["lakes"] = {"count": int(n), "under_half": int((share < 0.5).sum()), "under_three_quarters": int((share < 0.75).sum()), "least": float(share.min())}
print("lakes: %d; with less than half showing: %d; less than three quarters: %d; the least: %s" % (n, (share < 0.5).sum(), (share < 0.75).sum(), "; ".join(
    "%.0f%% of %d px at (%d, %d) under %s" % (100 * share[i], whole[i], *reversed(ndimage.center_of_mass(pools == i + 1)),
                                               "a dot" if (dots & (pools == i + 1)).any() else "a bridge" if (deck & (pools == i + 1)).any() else "a border") for i in order[:6])))
colours = {}
for name, colour in (("sea", (181, 235, 255)), ("white", (255, 255, 255)), ("blue", BLUE), ("pink", layers.PINK), ("purple", layers.PURPLE),
                     ("grey", layers.GREY), ("red", RED), ("umber", UMBER)):
    colours[name] = int(is_colour(saved, colour).sum())
facts["colours"] = colours
print("pixels by colour: %s" % colours)
same_roads = bool((is_colour(saved, RED) == road).all()) and bool((is_colour(saved, UMBER) == deck).all()) and bool((saved[dots] == settlements[dots]).all())
print("the roads, bridges and dots are those of Roads.png: %s" % same_roads)
with open(FACTS_TO, "w", encoding="utf-8") as handle:
    json.dump(facts, handle, indent=1)
print("saved %s" % FACTS_TO)
