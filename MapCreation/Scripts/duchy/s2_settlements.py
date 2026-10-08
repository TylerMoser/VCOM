"""Draw the capitals over Counties.png: a dot for each county's seat, in the colour of the
highest thing it is the capital of, and check the picture by itself.

A kingdom's capital is one of its duchies' seats, and a duchy's seat is one of its counties'
(c1_counties.py kept it so), so there is one dot a county, 220 in all: pink for the nine
kingdoms' capitals, purple for the other duchies', grey for the rest. Which duchy seat is the
kingdom's capital is scored here: the size of its river, how near the kingdom's land is to it
by the going, and a sea harbour.

A dot is a hard-edged disc on its seat. Where that would touch a border, the coast or the sea,
it is moved the least it can be, inside its own county, to stand clear of them by two pixels,
so every dot lies whole on the white of its own county.

Usage: s2_settlements.py <repo root> <duchy out dir> <picture to write> [look]
"""
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT, WRITE_TO = sys.argv[1], sys.argv[2], sys.argv[3]
LOOK = len(sys.argv) > 4
TAG = "f3"
PINK = (233, 0, 255, 255)
PURPLE = (110, 30, 180, 255)
GREY = (128, 128, 128, 255)
RADIUS = {"kingdom": 13, "duchy": 9, "county": 6}
COLOUR = {"kingdom": PINK, "duchy": PURPLE, "county": GREY}
CLEAR = 2.5              # px of white kept between a dot and anything else
KM = 0.335

base = np.asarray(Image.open(ROOT + "/MapCreation/Counties.png").convert("RGBA"))
h, w = base.shape[:2]
county = np.load(OUT + "/county_map_%s.npy" % TAG)
with open(OUT + "/county_list_%s.pickle" % TAG, "rb") as handle:
    listing = pickle.load(handle)
of_duchy, seats = np.asarray(listing["of_duchy"]), listing["seats"]
with open(OUT + "/duchies_all.pickle", "rb") as handle:
    duchies = pickle.load(handle)
with open(OUT + "/capital_candidates.pickle", "rb") as handle:
    candidates = pickle.load(handle)
fields = np.load(OUT + "/fields1.npz")
river, lake = fields["river"], fields["lake"]
count = len(seats) - 1

# -- which seats are capitals of what -----------------------------------------------------------------
duchy_seat = {}                                          # duchy -> its county
for c in range(1, count + 1):
    duchy_seat.setdefault(int(of_duchy[c]), c)           # the first county listed for a duchy has the duchy's own seat
recorded = [None] + [seat for k in sorted(duchies) for seat in duchies[k]["seats"]]
drift = max(np.hypot(seats[c][0] - recorded[d][0], seats[c][1] - recorded[d][1]) for d, c in duchy_seat.items())
print("duchy seats: %d; furthest a duchy's first county seat is from the duchy seat as recorded: %.1f px" % (len(duchy_seat), drift))
kingdom_of_duchy = {row["duchy"]: row["kingdom"] for row in candidates}
print("kingdom capitals, scored as the size of the river + a harbour - how far the kingdom's land is by the going:")
capital = {}
for k in sorted(set(kingdom_of_duchy.values())):
    scored = []
    for row in candidates:
        if row["kingdom"] == k:
            harbour = row["sea"] < 5.0
            score = np.log2(1.0 + row["flow"] / 15.0) + 1.5 * harbour - row["reach"] / 50.0
            scored.append((score, row["duchy"], row, harbour))
    scored.sort(key=lambda s: -s[0])
    capital[k] = scored[0][1]
    print("  kingdom %d: %s" % (k, "; ".join("duchy %d %s %.2f (river %.0f m3/s, land %.0f km off%s)" % (
        d, row["seat"], score, row["flow"], row["reach"], ", harbour" if harbour else "") for score, d, row, harbour in scored)))
rank = {}
for c in range(1, count + 1):
    d = int(of_duchy[c])
    if duchy_seat[d] != c:
        rank[c] = "county"
    elif capital[kingdom_of_duchy[d]] == d:
        rank[c] = "kingdom"
    else:
        rank[c] = "duchy"
print("dots: %s" % {name: sum(1 for r in rank.values() if r == name) for name in ("kingdom", "duchy", "county")})

# -- where each dot goes ------------------------------------------------------------------------------
white = (base[..., :3] >= 250).all(axis=2)
clear = ndimage.distance_transform_edt(white)
dry = ~(river | lake)
centres, moved = {}, []
for c in range(1, count + 1):
    x, y = seats[c]
    need = RADIUS[rank[c]] + CLEAR
    if white[y, x] and county[y, x] == c and clear[y, x] >= need:
        centres[c] = (x, y)
        continue
    found = None
    for reach in (40, 90, 200):
        window = (slice(max(y - reach, 0), min(y + reach + 1, h)), slice(max(x - reach, 0), min(x + reach + 1, w)))
        good = white[window] & (county[window] == c) & (clear[window] >= need) & dry[window]
        if good.any():
            ys, xs = np.nonzero(good)
            ys += window[0].start; xs += window[1].start
            nearest = int(np.argmin((ys - y) ** 2 + (xs - x) ** 2))
            found = (int(xs[nearest]), int(ys[nearest]))
            break
    assert found is not None, "no room for county %d's dot" % c
    centres[c] = found
    moved.append((float(np.hypot(found[0] - x, found[1] - y)), c, rank[c], (x, y), found, float(clear[y, x])))
moved.sort(reverse=True)
print("dots moved off their seats to stand clear: %d of %d; furthest %.1f px (%.1f km); by rank %s" % (
    len(moved), count, moved[0][0] if moved else 0.0, (moved[0][0] if moved else 0.0) * KM,
    {name: sum(1 for m in moved if m[2] == name) for name in ("kingdom", "duchy", "county")}))
for far, c, name, seat, at, room in moved[:12]:
    print("  county %3d (%s): seat %s had %.1f px of room, dot at %s, %.1f px away" % (c, name, seat, room, at, far))

# -- draw ---------------------------------------------------------------------------------------------
picture = base.copy()
dots = np.zeros((h, w), dtype=np.uint8)                  # 0 none, 1 county, 2 duchy, 3 kingdom
for order, name in enumerate(("county", "duchy", "kingdom"), start=1):
    r = RADIUS[name]
    yy, xx = np.mgrid[-r - 1: r + 2, -r - 1: r + 2]
    disc = xx * xx + yy * yy <= (r + 0.4) ** 2
    for c in range(1, count + 1):
        if rank[c] != name:
            continue
        x, y = centres[c]
        window = (slice(y - r - 1, y + r + 2), slice(x - r - 1, x + r + 2))
        assert white[window][disc].all(), "county %d's dot is not on white" % c
        picture[window][disc] = COLOUR[name]
        dots[window][disc] = order
Image.fromarray(picture, "RGBA").save(WRITE_TO)
with open(OUT + "/settlements.pickle", "wb") as handle:
    pickle.dump({"rank": rank, "centres": centres, "capital": capital, "duchy_seat": duchy_seat, "moved": moved}, handle)
print("wrote %s" % WRITE_TO)

# -- the check, from the saved picture ---------------------------------------------------------------
saved = np.asarray(Image.open(WRITE_TO).convert("RGBA"))
changed = (saved != base).any(axis=2)
colours = {tuple(int(v) for v in c): int(n) for c, n in zip(*np.unique(saved[changed].reshape(-1, 4), axis=0, return_counts=True))}
print("pixels changed from Counties.png: %d, in colours %s; all of them white before: %s" % (changed.sum(), colours, bool(white[changed].all())))
blobs, n = ndimage.label(changed, structure=np.ones((3, 3)))
sizes = ndimage.sum_labels(changed, blobs, index=np.arange(1, n + 1)).astype(int)
print("dots found in the picture: %d; by size in px %s" % (n, {int(s): int((sizes == s).sum()) for s in np.unique(sizes)}))
ring = (ndimage.distance_transform_edt(~changed) <= 2.0) & ~changed
print("every pixel within 2 px of a dot is white: %s" % bool((saved[ring][:, :3] >= 250).all()))
for name, structure in (("four", None), ("eight", np.ones((3, 3)))):
    before = ndimage.label(white, structure=structure)[1]
    after = ndimage.label(white & ~changed, structure=structure)[1]
    print("white pieces filling by %s neighbours: %d in Counties.png, %d now" % (name, before, after))
# One dot a county, and the right colour.
pieces, n_pieces = ndimage.label(white)
dot_piece = pieces[[centres[c][1] for c in range(1, count + 1)], [centres[c][0] for c in range(1, count + 1)]]
print("dots sharing a white piece of Counties.png with another dot: %d" % (count - len(set(dot_piece.tolist()))))
wrong = 0
for c in range(1, count + 1):
    x, y = centres[c]
    wrong += int(tuple(int(v) for v in saved[y, x]) != COLOUR[rank[c]]) + int(county[y, x] != c)
print("dots of the wrong colour or outside their county: %d" % wrong)

if LOOK:
    coast = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
    look = saved[..., :3].copy()
    water = river | lake
    look[water & white] = (150, 195, 240)
    look[fields["divide"] & white & ~water] = (232, 205, 175)
    look[changed] = saved[changed][:, :3]
    Image.fromarray(look).save(OUT + "/settlements_look_full.png")
    Image.fromarray(look).resize((w // 2, h // 2), Image.LANCZOS).save(OUT + "/settlements_look.png")
    print("saved settlements_look.png")
