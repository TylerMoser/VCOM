"""Is Continent.png what it should be? Checked from the pictures alone: three colours, no wave
lines, a black shoreline of one width with no gaps round every piece of land, and the land of
WorldMapV1.png but for the mended joins.

Usage: v7_continent.py <folder of the pictures> [name of the picture]
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
FOLDER = sys.argv[1]
NAME = sys.argv[2] if len(sys.argv) > 2 else "Continent.png"
SEA, WHITE, BLACK = (181, 235, 255), (255, 255, 255), (0, 0, 0)
LINE = 7.0
SHEET = 400
EIGHT = np.ones((3, 3), dtype=bool)
problems = []


def said(ok, text):
    print(("ok    " if ok else "WRONG ") + text)
    if not ok:
        problems.append(text)


def is_colour(picture, colour):
    return (picture[..., 0] == colour[0]) & (picture[..., 1] == colour[1]) & (picture[..., 2] == colour[2])


def runs_of(flags):
    edges = np.flatnonzero(np.diff(np.concatenate([[False], flags, [False]]).astype(np.int8)))
    return [(int(a), int(b)) for a, b in zip(edges[::2], edges[1::2])]


image = Image.open(FOLDER + "/" + NAME)
old_image = Image.open(FOLDER + "/WorldMapV1.png")
said(image.size == old_image.size == (3100, 4000) and image.mode == "RGBA", "%s is %d x %d, %s, as WorldMapV1.png is" % (NAME, image.size[0], image.size[1], image.mode))
picture = np.asarray(image.convert("RGBA"))
old = np.asarray(old_image.convert("RGB"))
h, w = picture.shape[:2]
sea, land, line = is_colour(picture, SEA), is_colour(picture, WHITE), is_colour(picture, BLACK)
said(int(sea.sum() + land.sum() + line.sum()) == h * w, "three colours and no others: sea %d px, white land %d px, black %d px (pixels of any other colour: %d)" % (
    sea.sum(), land.sum(), line.sum(), h * w - sea.sum() - land.sum() - line.sum()))
said(int(picture[..., 3].min()) == 255, "nothing is transparent (alpha %d to %d)" % (picture[..., 3].min(), picture[..., 3].max()))

# -- the line --------------------------------------------------------------------------------------------
to_land = ndimage.distance_transform_edt(~land)
wanted = ~land & (to_land <= LINE)
said(bool((line == wanted).all()), "the black is exactly the pixels within %g px of land that are not land: a line %g px wide round every piece of land (pixels that differ: %d)" % (
    LINE, LINE, (line != wanted).sum()))
said(not (line & (to_land > LINE)).any(), "no black stands apart from the land: no wave lines (black further than %g px from land: %d px)" % (LINE, (line & (to_land > LINE)).sum()))
touching = land & ndimage.binary_dilation(sea, structure=EIGHT)
nearest_sea = float(to_land[sea].min())
said(not touching.any() and nearest_sea > LINE, "no gaps: no land pixel touches the sea, and the nearest sea to any land is %.1f px away, across the line" % nearest_sea)
# Thickness, measured across the line: from the land's edge outward the black runs LINE px and then stops.
ring_in = ~land & (to_land <= LINE)
ring_out = ~land & (to_land > LINE) & (to_land <= LINE + 1.5)
said(bool(line[ring_in].all()) and not line[ring_out].any(), "the line is of one width: black all the way out to %g px from the land and nowhere beyond" % LINE)
pieces4, n4 = ndimage.label(land)
pieces8, n8 = ndimage.label(land, structure=EIGHT)
old_land = (old >= 250).all(axis=2)
old_sizes = np.sort(ndimage.sum_labels(old_land, ndimage.label(old_land)[0], index=np.arange(1, ndimage.label(old_land)[1] + 1)))[::-1].astype(int)
sizes = np.sort(ndimage.sum_labels(land, pieces4, index=np.arange(1, n4 + 1)))[::-1].astype(int)
said(n4 == n8 == 15 and sizes.tolist() == old_sizes.tolist(), "land: %d pieces by four neighbours and %d by eight, the mainland and 14 islands, each the size it is in WorldMapV1.png (%d px in all)" % (n4, n8, land.sum()))
rings, n_rings = ndimage.label(line, structure=EIGHT)
ring_of = [set(np.unique(rings[ndimage.binary_dilation(pieces4 == i, structure=EIGHT) & line]).tolist()) - {0} for i in range(1, n4 + 1)]
said(all(len(r) == 1 for r in ring_of), "every piece of land has the line all round it (pieces of line: %d, for %d pieces of land)" % (n_rings, n4))
closed = True
boxes = ndimage.find_objects(pieces4)
for i in range(1, n4 + 1):
    box = boxes[i - 1]
    grown = (slice(max(box[0].start - 2, 0), box[0].stop + 2), slice(max(box[1].start - 2, 0), box[1].stop + 2))
    mine = pieces4[grown] == i
    rim = ndimage.binary_dilation(mine, structure=EIGHT) & ~mine
    closed &= bool(line[grown][rim].all())
said(closed, "every pixel beside the land is black: the line is unbroken round each of the %d pieces" % n4)
sea_pieces = ndimage.label(sea, structure=EIGHT)[1]
said(sea_pieces == 1, "the sea is one piece: no water is shut in by the line (pieces of sea: %d)" % sea_pieces)

# -- against the drawing -------------------------------------------------------------------------------
differ = land != old_land
added, removed = int((land & ~old_land).sum()), int((old_land & ~land).sum())
ys, xs = np.nonzero(differ)
from_join = np.abs(((ys + SHEET // 2) % SHEET) - SHEET // 2 + 0.5) if len(ys) else np.array([0.0])
places, n_places = ndimage.label(ndimage.binary_dilation(differ, structure=EIGHT, iterations=6), structure=EIGHT)
said(added == removed and from_join.max() <= 24, "the land is WorldMapV1.png's but for %d px added and %d px taken away, in %d places, all within %d rows of a join between the hand-drawn sheets (rows %d, %d, ...)" % (
    added, removed, n_places, int(np.ceil(from_join.max())), SHEET, 2 * SHEET))
worst_before, worst_after, crossings = 0, 0, 0
for y0 in range(SHEET, h, SHEET):
    before = [b - a for a, b in runs_of(old_land[y0] != old_land[y0 - 1])]
    after = [b - a for a, b in runs_of(land[y0] != land[y0 - 1])]
    crossings += sum(1 for v in before if v >= 3)
    worst_before, worst_after = max(worst_before, max(before, default=0)), max(worst_after, max(after, default=0))
said(worst_after <= 2, "at the joins the land's edge no longer jumps: %d px at most from one row to the next (in WorldMapV1.png: %d px at most, 3 px or more at %d places)" % (worst_after, worst_before, crossings))
old_dark = old.astype(np.int32).sum(axis=2) < 200
old_sea = is_colour(old, SEA)
waves = old_dark & (ndimage.distance_transform_edt(~old_land) > 9.0)
said(not line[waves & (to_land > LINE)].any(), "the drawing's wave lines are gone: %d px of dark ink more than 9 px from land in WorldMapV1.png, none of it black here" % waves.sum())
print("      of the drawing's dark ink, %d px are sea here; of its flat sea, %d px are line here" % ((old_dark & sea).sum(), (old_sea & line).sum()))

# -- the other pictures: does anything of theirs lie where the land changed? ------------------------------
try:
    everything = np.asarray(Image.open(FOLDER + "/All.png").convert("RGB"))
    marks = (everything != old).any(axis=2)                # what the other layers drew on the coast map
    near = ndimage.binary_dilation(differ, structure=EIGHT, iterations=3)
    busy = sorted(set(np.unique(places[marks & near]).tolist()) - {0})
    where = [tuple(int(v) for v in reversed(ndimage.center_of_mass(places == i))) for i in busy]
    print("note  the other pictures draw something (a river's mouth, a border's end) within 3 px of the changed land at %d of the %d joins: %s; %d px of their marks. "
          "They were drawn for the coast as it was, and are not part of this picture" % (len(busy), n_places, where, (marks & near).sum()))
except FileNotFoundError:
    pass
print()
print("ALL RIGHT: %s is a plain, whole outline of the land" % NAME if not problems else "PROBLEMS: %d\n  %s" % (len(problems), "\n  ".join(problems)))
