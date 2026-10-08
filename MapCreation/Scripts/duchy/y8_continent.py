"""Continent.png: the coast map with a standard outline.

WorldMapV1.png was put together from hand-drawn sheets 400 px tall. Its shoreline is an inked
line of uneven weight with soft edges, wave lines are drawn in the sea beside it, and where the
coast crosses from one sheet to the next the two sheets do not meet: the land's edge jumps
sideways by 3 to 11 px there and the ink is broken.

This makes the plain version:
  - the land is WorldMapV1.png's (every pixel whose red, green and blue are all 250 or more),
    pixel for pixel, except at those joins, where the rows either side are slid sideways, less
    and less with distance from the join, until the two edges meet halfway;
  - the coast is every pixel that is not land within LINE px of land, pure black;
  - everything else is the sea's colour. Three colours, hard edges, nothing transparent.

Usage: y8_continent.py <MapCreation dir> <picture to write> <facts .json to write> [plain]
("plain" leaves the joins as they are)
"""
import json
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
MAPS, WRITE_TO, FACTS_TO = sys.argv[1:4]
MEND = not (len(sys.argv) > 4 and sys.argv[4] == "plain")
SEA, WHITE, BLACK = (181, 235, 255, 255), (255, 255, 255, 255), (0, 0, 0, 255)
LINE = 7.0               # px: the line's width, the weight of the hand-drawn ink
SHEET = 400              # px: the height of a hand-drawn sheet
JUMP = 3                 # px: a sideways jump of the land's edge at a join that is mended
EIGHT = np.ones((3, 3), dtype=bool)

coast = np.asarray(Image.open(MAPS + "/WorldMapV1.png").convert("RGB"))
old_land = (coast >= 250).all(axis=2)
h, w = old_land.shape
land = old_land.copy()


def runs_of(flags):
    edges = np.flatnonzero(np.diff(np.concatenate([[False], flags, [False]]).astype(np.int8)))
    return [(int(a), int(b)) for a, b in zip(edges[::2], edges[1::2])]


# -- the joins -----------------------------------------------------------------------------------------
joins = []
for y0 in range(SHEET, h, SHEET):
    for a, b in runs_of(old_land[y0] != old_land[y0 - 1]):
        if b - a >= JUMP:
            joins.append((y0, a, b))
mended = []
for y0, a, b in joins:
    lower_land = bool(old_land[y0, a])                     # the run is land in the lower row, sea in the upper
    # Which way the lower sheet's edge lies from the upper's: the run is where the two rows differ.
    # Land lies to one side of the edge; find it from the upper row just outside the run.
    left_is_land = bool(old_land[y0 - 1, a - 1])
    # The upper edge is at a (if land is on the left and the lower row has more land) or at b, and so on.
    if left_is_land:
        delta = (b - a) if lower_land else -(b - a)        # the lower edge is this far to the right of the upper
    else:
        delta = -(b - a) if lower_land else (b - a)
    size = abs(delta)
    reach = max(10, 2 * size)                              # rows either side over which the slide dies away
    half = None
    for try_half in range(size + 16, 140, 8):              # a window wide enough to hold the coast for all those rows
        x0, x1 = max((a + b) // 2 - try_half, 0), min((a + b) // 2 + try_half, w)
        rows = old_land[y0 - reach: y0 + reach, x0:x1]
        crossings = (rows[:, 1:] != rows[:, :-1]).sum(axis=1)
        margin = size // 2 + 3
        clear = (rows[:, :margin] == rows[:, :1]).all() and (rows[:, -margin:] == rows[:, -1:]).all()
        if (crossings == 1).all() and clear and (rows[:, 0] == rows[0, 0]).all() and (rows[:, -1] == rows[0, -1]).all():
            half = try_half
            break
    entry = {"at": [int((a + b) // 2), int(y0)], "jump": int(size), "towards": "east" if delta > 0 else "west", "rows": int(reach)}
    if half is None:
        entry["mended"] = False
        print("join at (%d, %d): a jump of %d px, NOT mended: the coast about it is not one simple edge" % ((a + b) // 2, y0, size))
        mended.append(entry)
        continue
    if MEND:
        before = land[y0 - reach: y0 + reach, x0:x1].copy()
        for row in range(y0 - reach, y0 + reach):
            away = (y0 - 0.5 - row) if row < y0 else (row - (y0 - 0.5))      # 0.5, 1.5, ... rows from the join
            taper = 0.5 * (1.0 + np.cos(np.pi * min(away / reach, 1.0)))
            slide = int(round((delta / 2.0) * taper)) * (1 if row < y0 else -1)   # the upper rows go towards the lower edge, and the lower towards the upper
            if slide:
                strip = old_land[row, x0:x1]
                moved = np.empty_like(strip)
                if slide > 0:
                    moved[slide:] = strip[:-slide]; moved[:slide] = strip[0]
                else:
                    moved[:slide] = strip[-slide:]; moved[slide:] = strip[-1]
                land[row, x0:x1] = moved
        after = land[y0 - reach: y0 + reach, x0:x1]
        entry.update({"mended": True, "added": int((after & ~before).sum()), "removed": int((before & ~after).sum()), "window": [int(x0), int(y0 - reach), int(x1), int(y0 + reach)]})
        left = runs_of(land[y0] != land[y0 - 1])
        entry["jump_after"] = int(max((q - p for p, q in left if p >= x0 and q <= x1), default=0))
        print("join at (%d, %d): the land's edge jumped %d px %s; rows slid over %d rows either side; land added %d px, taken away %d px; the jump now %d px" % (
            entry["at"][0], y0, size, entry["towards"], reach, entry["added"], entry["removed"], entry["jump_after"]))
    mended.append(entry)
print("joins where the coast jumps %d px or more: %d; mended: %d" % (JUMP, len(mended), sum(1 for m in mended if m.get("mended"))))

# -- the picture ---------------------------------------------------------------------------------------
to_land = ndimage.distance_transform_edt(~land)
line = ~land & (to_land <= LINE)
picture = np.empty((h, w, 4), dtype=np.uint8)
picture[...] = SEA
picture[land] = WHITE
picture[line] = BLACK
Image.fromarray(picture, "RGBA").save(WRITE_TO)
saved = np.asarray(Image.open(WRITE_TO).convert("RGBA"))
assert (saved == picture).all()
print("wrote %s" % WRITE_TO)

# -- what it holds -------------------------------------------------------------------------------------
sea = ~land & ~line
pieces = {name: int(ndimage.label(land, structure=s)[1]) for name, s in (("four", None), ("eight", EIGHT))}
sea_pieces = int(ndimage.label(sea, structure=EIGHT)[1])
line_pieces = int(ndimage.label(line, structure=EIGHT)[1])
touching = int((land & ndimage.binary_dilation(sea, structure=EIGHT)).sum())
old_dark = coast.astype(np.int32).sum(axis=2) < 200
old_sea = (coast == np.array(SEA[:3], dtype=np.uint8)).all(axis=2)
shut = sea & ~ndimage.binary_opening(sea, structure=np.ones((3, 3), dtype=bool))
closed = ~land & (to_land <= LINE) & (ndimage.distance_transform_edt(~line) > 0)
facts = {"line_px_wide": LINE, "land_px": int(land.sum()), "old_land_px": int(old_land.sum()), "land_added": int((land & ~old_land).sum()),
         "land_removed": int((old_land & ~land).sum()), "line_px": int(line.sum()), "sea_px": int(sea.sum()), "land_pieces": pieces, "sea_pieces": sea_pieces,
         "line_pieces": line_pieces, "land_touching_sea": touching, "joins": mended, "bytes": None,
         "old_ink_now_sea": int((old_dark & sea).sum()), "old_sea_now_line": int((old_sea & line).sum()), "sea_slivers_px": int(shut.sum())}
import os
facts["bytes"] = os.path.getsize(WRITE_TO)
print("land %d px (WorldMapV1.png: %d; added %d, taken away %d); line %d px; sea %d px" % (
    facts["land_px"], facts["old_land_px"], facts["land_added"], facts["land_removed"], facts["line_px"], facts["sea_px"]))
print("land pieces: %s; sea pieces: %d; pieces of line: %d; land pixels touching sea: %d" % (pieces, sea_pieces, line_pieces, touching))
print("dark ink of the drawing that is sea now: %d px; flat sea of the drawing that is line now: %d px; sea left in slivers under 3 px wide: %d px" % (
    facts["old_ink_now_sea"], facts["old_sea_now_line"], facts["sea_slivers_px"]))
with open(FACTS_TO, "w", encoding="utf-8") as handle:
    json.dump(facts, handle, indent=1)
print("saved %s (%d bytes of picture)" % (FACTS_TO, facts["bytes"]))
