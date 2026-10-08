"""Draw the roads and bridges over Settlements.png, and check the picture by itself.

The roads r3_network.py laid share cells where they run together. They are first taken apart
into stretches between forks (and settlements), so that no stretch is drawn twice; each stretch
is smoothed, its ends held where they are, as far as it can be without leaving the land,
touching a lake, or changing how often it crosses a river. A stretch is then a hard-edged line:
3 px for a highway, 2 px for any other road, in the roads' red. Where it lies on a river as
drawn it is a bridge: a bar in dark brown, 2 px wider than its road and reaching 2 px on to
each bank. The one stretch off the land, the strait between the mainland and the island town, is
a bridge too, drawn the same way from shore to shore. Settlements' dots are left as they are,
the roads running up to them. Borders are drawn over where a road crosses them; where a road
runs along a border, the border is drawn along both sides of the road (see layers.py).

Usage: r5b_draw.py <repo root> <duchy out dir> <roads out dir> <picture to write> [look]
"""
import pickle
import sys
from collections import defaultdict
import numpy as np
from PIL import Image
from scipy import ndimage
import layers

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT, ROADS, WRITE_TO = sys.argv[1:5]
LOOK = len(sys.argv) > 5
ROAD = (200, 40, 30, 255)
BRIDGE = (60, 35, 15, 255)
SMOOTH = 3.0             # px, along a stretch
ON_BANK = 2.0            # px a bridge reaches on to each bank
KM = 0.335

base = np.asarray(Image.open(ROOT + "/MapCreation/Settlements.png").convert("RGBA"))
h, w = base.shape[:2]
land, sea = np.load(ROADS + "/land.npy"), np.load(ROADS + "/sea.npy")
passable, river, lake = np.load(ROADS + "/passable.npy"), np.load(ROADS + "/river.npy"), np.load(ROADS + "/lake.npy")
town, flow = np.load(ROADS + "/town.npy"), np.load(ROADS + "/flow.npy")
with open(ROADS + "/network.pickle", "rb") as handle:
    network = pickle.load(handle)
with open(ROADS + "/towns.pickle", "rb") as handle:
    towns = pickle.load(handle)
centres, rank = towns["centres"], towns["rank"]
laid = network["laid"]

# -- the stretches ------------------------------------------------------------------------------------
beside = defaultdict(set)
great = {}                                               # a step -> is it a highway's
for road in laid.values():
    cells = [y * w + x for y, x in road["path"]]
    for p, q in zip(cells[:-1], cells[1:]):
        beside[p].add(q); beside[q].add(p)
        key = (min(p, q), max(p, q))
        great[key] = great.get(key, False) or road["highway"]
town_cells = {y * w + x for x, y in centres.values()}
nodes = {c for c, others in beside.items() if len(others) != 2} | town_cells
stretches = []
walked = set()
for node in nodes:
    for first in beside[node]:
        if (node, first) in walked:
            continue
        chain = [node, first]
        walked.add((node, first)); walked.add((first, node))
        while chain[-1] not in nodes:
            ahead = [c for c in beside[chain[-1]] if c != chain[-2]][0]
            walked.add((chain[-1], ahead)); walked.add((ahead, chain[-1]))
            chain.append(ahead)
        highway = any(great[(min(p, q), max(p, q))] for p, q in zip(chain[:-1], chain[1:]))
        stretches.append((chain, highway))
steps = sum(len(chain) - 1 for chain, _ in stretches)
print("stretches of road between forks and settlements: %d; forks: %d; steps %d of %d taken up" % (
    len(stretches), len(nodes - town_cells), steps, len(great)))
print("forks that stand on a river: %s" % [(c % w, c // w) for c in nodes - town_cells if river[c // w, c % w]])


def along(points, spacing):
    """A line's points set [spacing] apart."""
    gaps = np.hypot(*np.diff(points, axis=0).T)
    reach = np.concatenate([[0.0], np.cumsum(gaps)])
    at = np.linspace(0.0, reach[-1], max(int(np.ceil(reach[-1] / spacing)) + 1, 2))
    return np.stack([np.interp(at, reach, points[:, 0]), np.interp(at, reach, points[:, 1])], axis=1)


def smoothed(points, sigma):
    """The points moved on to a smooth line, the two ends staying where they are."""
    if sigma <= 0.0 or len(points) < 5:
        return points
    pad = min(int(4 * sigma) + 1, len(points) - 1)
    front = 2.0 * points[0] - points[pad:0:-1]
    back = 2.0 * points[-1] - points[-2: -pad - 2: -1]
    whole = np.concatenate([front, points, back])
    whole = ndimage.gaussian_filter1d(whole, sigma, axis=0, mode="nearest")
    return whole[pad: pad + len(points)]


def pixels_of(points):
    """The cells a line of closely set points passes through, in order, none twice running."""
    cells = np.round(points).astype(np.int64)
    keep = np.concatenate([[True], (np.diff(cells, axis=0) != 0).any(axis=1)])
    return cells[keep]


def runs_of(flags):
    """[start, stop) of each run of True."""
    edges = np.flatnonzero(np.diff(np.concatenate([[False], flags, [False]]).astype(np.int8)))
    return list(zip(edges[::2], edges[1::2]))


minor_line = np.zeros((h, w), dtype=bool)
major_line = np.zeros((h, w), dtype=bool)
minor_bridge = np.zeros((h, w), dtype=bool)
major_bridge = np.zeros((h, w), dtype=bool)
strait_line = np.zeros((h, w), dtype=bool)
bridges = []
eased = defaultdict(int)
length = {"highway": 0.0, "road": 0.0, "strait": 0.0}
for chain, highway in stretches:
    raw = np.array([(c // w, c % w) for c in chain], dtype=np.float64)
    raw_cells = raw.astype(np.int64)
    at_sea = sea[raw_cells[:, 0], raw_cells[:, 1]]
    # Off the land a stretch is the bridge over the strait; on land it is road. Take the two
    # apart, the bridge reaching on to each shore as a river's bridge reaches on to each bank.
    parts = []
    start = 0
    on_shore = int(ON_BANK)
    for i in range(1, len(raw) + 1):
        if i == len(raw) or at_sea[i] != at_sea[start]:
            a, b = max(start - on_shore, 0) if at_sea[start] else start, min(i + on_shore, len(raw)) if at_sea[start] else i
            parts.append((raw[a:b], bool(at_sea[start])))
            start = i
    for points, over_sea in parts:
        if len(points) < 2:
            continue
        even = along(points, 1.0)
        if over_sea:
            assert not highway, "the strait's bridge is drawn as a lesser road's"
            line = along(smoothed(even, SMOOTH), 0.5)
            cells = pixels_of(line)
            strait_line[cells[:, 0], cells[:, 1]] = True
            span = float(np.hypot(*np.diff(line, axis=0).T).sum())
            wet = sea[np.round(line[:, 0]).astype(np.int64), np.round(line[:, 1]).astype(np.int64)]
            length["road"] += span * KM
            length["strait"] += float(wet.sum()) * 0.5 * KM
            middle = line[len(line) // 2]
            bridges.append({"at": (int(round(middle[1])), int(round(middle[0]))), "flow": 0.0, "px": float(wet.sum()) * 0.5,
                            "highway": False, "town": True, "sea": True})
            continue
        wanted = len(runs_of(river[raw_cells[:, 0], raw_cells[:, 1]]))
        for sigma in (SMOOTH, SMOOTH / 2, SMOOTH / 4, 0.0):
            line = along(smoothed(even, sigma), 0.5)
            cells = pixels_of(line)
            on_river = river[cells[:, 0], cells[:, 1]]
            if passable[cells[:, 0], cells[:, 1]].all() and len(runs_of(on_river)) == wanted:
                break
        eased[sigma] += 1
        (major_line if highway else minor_line)[cells[:, 0], cells[:, 1]] = True
        length["highway" if highway else "road"] += float(np.hypot(*np.diff(line, axis=0).T).sum()) * KM
        # Bridges: where the line lies on the river, and a little on to each bank.
        wet = river[np.round(line[:, 0]).astype(np.int64), np.round(line[:, 1]).astype(np.int64)]
        for a, b in runs_of(wet):
            a2, b2 = max(a - int(ON_BANK / 0.5), 0), min(b + int(ON_BANK / 0.5), len(line))
            deck = pixels_of(line[a2:b2])
            (major_bridge if highway else minor_bridge)[deck[:, 0], deck[:, 1]] = True
            middle = line[(a + b) // 2]
            y, x = int(round(middle[0])), int(round(middle[1]))
            near = town[max(y - 12, 0): y + 13, max(x - 12, 0): x + 13]
            bridges.append({"at": (x, y), "flow": float(flow[np.round(line[a:b, 0]).astype(int), np.round(line[a:b, 1]).astype(int)].max()),
                            "px": (b - a) * 0.5, "highway": highway, "town": bool((near > 0).any()), "sea": False})
print("stretches smoothed by %s px; km of highway %.0f, of other road %.0f (of it %.1f km the bridge over the strait, shore to shore)" % (
    dict(eased), length["highway"], length["road"], length["strait"]))

# -- the picture ---------------------------------------------------------------------------------------
two, three = np.ones((2, 2), dtype=bool), np.ones((3, 3), dtype=bool)
road = ndimage.binary_dilation(minor_line, structure=two) | ndimage.binary_dilation(major_line, structure=three)
deck = (ndimage.binary_dilation(ndimage.binary_dilation(minor_bridge, structure=three), structure=two) |
        ndimage.binary_dilation(major_bridge, structure=three, iterations=2))
dots = town > 0
strait = ndimage.binary_dilation(ndimage.binary_dilation(strait_line, structure=three), structure=two) & ~dots
deck &= land & ~lake & ~dots
deck |= strait                                           # the one bridge that is not over a river
road &= land & ~lake & ~dots & ~(river & ~deck)          # a road's edge never laps over water
# Pinholes: a few pixels of land shut in by road alone, where two roads part at a fine angle.
open_land = land & ~lake & ~river & ~dots & ~road & ~deck & (base[..., :3] >= 250).all(axis=2)
holes, n_holes = ndimage.label(open_land)
hole_sizes = ndimage.sum_labels(open_land, holes, index=np.arange(1, n_holes + 1))
closed_up = 0
for i in np.flatnonzero(hole_sizes < 16) + 1:
    box = ndimage.find_objects(holes, max_label=i)[i - 1]
    grown = (slice(max(box[0].start - 1, 0), box[0].stop + 1), slice(max(box[1].start - 1, 0), box[1].stop + 1))
    mine = holes[grown] == i
    rim = ndimage.binary_dilation(mine, structure=np.ones((3, 3), dtype=bool)) & ~mine
    if (road[grown] | deck[grown] | dots[grown])[rim].all():
        road[grown] |= mine
        closed_up += 1
print("pinholes between roads closed: %d" % closed_up)
picture = base.copy()
# A border a road runs along: its colour along both sides of the road, on land that was white.
rgb = base[..., :3]
near_land = ndimage.binary_dilation(land, structure=three, iterations=4)
lines = layers.border_lines(rgb, dots, near_land)
cover = layers.Cover(road | deck, layers.WIDEST_ROAD)
allowed = land & (rgb == 255).all(axis=2) & layers.clear_of(dots) & ~road & ~deck
beside_roads = {}
for name, colour, margin in layers.RANKS:
    run, places = cover.runs_along(layers.middle_of(lines[name]))
    sides = cover.both_sides(run, margin) & allowed
    picture[sides] = colour + (255,)
    beside_roads[name] = {"places": places, "px": int(sides.sum()), "run_px": int(run.sum())}
    print("%s borders a road runs along for %d px or more: %d places, %d px of the border's middle; its colour put beside the road: %d px" % (
        name, layers.FOLLOW, places, run.sum(), sides.sum()))
picture[road] = ROAD
picture[deck] = BRIDGE
Image.fromarray(picture, "RGBA").save(WRITE_TO)
with open(ROADS + "/drawn.pickle", "wb") as handle:
    pickle.dump({"bridges": bridges, "stretches": len(stretches), "length": length, "beside_roads": beside_roads}, handle)
print("wrote %s" % WRITE_TO)

over_rivers = [b for b in bridges if not b["sea"]]
flows = np.array([b["flow"] for b in over_rivers])
in_town = np.array([b["town"] for b in over_rivers])
print("bridges: %d, of them over the strait %d; of those over rivers, at a settlement: %d (%.0f%%); by the river's size in m3/s:" % (
    len(bridges), len(bridges) - len(over_rivers), in_town.sum(), 100.0 * in_town.mean()))
for low, high in ((0, 40), (40, 100), (100, 300), (300, 800), (800, 5000)):
    mine = (flows >= low) & (flows < high)
    print("  %4d to %4d: %3d bridges, %3d of them at a settlement" % (low, high, mine.sum(), (mine & in_town).sum()))

# -- the check, from the saved picture -----------------------------------------------------------------
saved = np.asarray(Image.open(WRITE_TO).convert("RGBA"))
changed = (saved != base).any(axis=2)
colours = {tuple(int(v) for v in c): int(n) for c, n in zip(*np.unique(saved[changed].reshape(-1, 4), axis=0, return_counts=True))}
print("pixels changed from Settlements.png: %d, in colours %s" % (changed.sum(), colours))
is_road = (saved[..., 0] == ROAD[0]) & (saved[..., 1] == ROAD[1]) & (saved[..., 2] == ROAD[2])
is_deck = (saved[..., 0] == BRIDGE[0]) & (saved[..., 1] == BRIDGE[1]) & (saved[..., 2] == BRIDGE[2])
print("dots changed: %d px; road or bridge on a lake: %d px; road on a river outside a bridge: %d px; road off the land: %d px; bridge off the land: %d px (the strait's: %d)" % (
    (changed & dots).sum(), ((is_road | is_deck) & lake).sum(), (is_road & river).sum(), (is_road & sea).sum(), (is_deck & sea).sum(), (strait & sea).sum()))
# Joined: every settlement's dot reached from every other by road, bridge and dot.
closed = is_road | is_deck | dots
pieces, n = ndimage.label(closed, structure=np.ones((3, 3)))
found = {int(pieces[y, x]) for x, y in centres.values()}
print("settlements joined in one piece of road: %s (pieces holding a settlement: %d)" % (len(found) == 1, len(found)))
decks, n_decks = ndimage.label(is_deck, structure=np.ones((3, 3)))
shown = sum(1 for b in bridges if is_deck[max(b["at"][1] - 4, 0): b["at"][1] + 5, max(b["at"][0] - 4, 0): b["at"][0] + 5].any())
print("bridge marks in the picture: %d (bridges made: %d, of them with their mark showing: %d)" % (n_decks, len(bridges), shown))
ys, xs = np.nonzero(strait)
print("the strait's bridge: %d px, x %d..%d, y %d..%d; %.1f px from shore to shore" % (strait.sum(), xs.min(), xs.max(), ys.min(), ys.max(), length["strait"] / KM))
deck_sizes = ndimage.sum_labels(is_deck, decks, index=np.arange(1, n_decks + 1))
print("bridge marks' sizes in px: least %d, median %d, most %d" % (deck_sizes.min(), np.median(deck_sizes), deck_sizes.max()))
# Slivers: bits of land shut in between roads, too small to be meant.
white_before = (base[..., :3] >= 250).all(axis=2)
white_after = (saved[..., :3] >= 250).all(axis=2)
bits, n_bits = ndimage.label(white_after)
bit_sizes = ndimage.sum_labels(white_after, bits, index=np.arange(1, n_bits + 1))
before = ndimage.label(white_before)[1]
small = np.flatnonzero(bit_sizes < 150) + 1
print("white pieces: %d in Settlements.png, %d now; under 150 px: %d" % (before, n_bits, small.size))
for i in small[:40]:
    box = ndimage.find_objects(bits == i)[0] if False else None
places = ndimage.center_of_mass(white_after, bits, small) if small.size else []
print("  slivers at (x, y, px): %s" % [(int(x), int(y), int(bit_sizes[i - 1])) for (y, x), i in zip(places, small)][:40])
with open(ROADS + "/slivers.pickle", "wb") as handle:
    pickle.dump([(int(x), int(y), int(bit_sizes[i - 1])) for (y, x), i in zip(places, small)], handle)

if LOOK:
    water = river | lake
    look = saved[..., :3].copy()
    wash = water & land & ~is_road & ~is_deck & ~dots
    look[wash] = (120, 175, 235)
    Image.fromarray(look).save(OUT + "/roads_look_full.png")
    Image.fromarray(look).resize((w // 2, h // 2), Image.LANCZOS).save(OUT + "/roads_look.png")
    print("saved roads_look.png")
