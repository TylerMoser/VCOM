"""Source data, part 3: the roads as a network. Its places (the 220 settlements and the forks
between them), the stretches of road from one place to the next as the lines that were drawn,
the 351 roads between neighbouring settlements as runs of stretches, and the bridges.

The stretches' lines are made again here exactly as the picture's were, and the proof is that
drawing them gives the red and the dark brown of Roads.png back, every pixel.

Usage: e4_roads.py <MapCreation dir> <scratch out dir> <folder to write to>
"""
import json
import pickle
import sys
from collections import defaultdict
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import cKDTree
from sourcefiles import save_json, KM

Image.MAX_IMAGE_PIXELS = None
MAPS, OUT, TO = sys.argv[1:4]
ROADS = OUT + "/roads2"
SMOOTH, ON_BANK = 3.0, 2.0

base = np.asarray(Image.open(MAPS + "/Settlements.png").convert("RGBA"))
picture = np.asarray(Image.open(MAPS + "/Roads.png").convert("RGB"))
h, w = base.shape[:2]
land, sea = np.load(ROADS + "/land.npy"), np.load(ROADS + "/sea.npy")
passable, river, lake = np.load(ROADS + "/passable.npy"), np.load(ROADS + "/river.npy"), np.load(ROADS + "/lake.npy")
town, flow = np.load(ROADS + "/town.npy"), np.load(ROADS + "/flow.npy")
with open(ROADS + "/network.pickle", "rb") as handle:
    network = pickle.load(handle)
with open(ROADS + "/towns.pickle", "rb") as handle:
    towns = pickle.load(handle)
centres = towns["centres"]
laid = network["laid"]

# -- the stretches, as the drawing found them ---------------------------------------------------------------
beside = defaultdict(set)
great = {}
for road in laid.values():
    cells = [y * w + x for y, x in road["path"]]
    for p, q in zip(cells[:-1], cells[1:]):
        beside[p].add(q); beside[q].add(p)
        key = (min(p, q), max(p, q))
        great[key] = great.get(key, False) or road["highway"]
town_cells = {int(y) * w + int(x): c for c, (x, y) in centres.items()}
nodes = {c for c, others in beside.items() if len(others) != 2} | set(town_cells)
stretches = []
walked = set()
for node in sorted(nodes):
    for first in sorted(beside[node]):
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
forks = sorted(nodes - set(town_cells))
node_id = dict(town_cells)
for i, cell in enumerate(forks, start=221):
    node_id[cell] = i


def along(points, spacing):
    gaps = np.hypot(*np.diff(points, axis=0).T)
    reach = np.concatenate([[0.0], np.cumsum(gaps)])
    at = np.linspace(0.0, reach[-1], max(int(np.ceil(reach[-1] / spacing)) + 1, 2))
    return np.stack([np.interp(at, reach, points[:, 0]), np.interp(at, reach, points[:, 1])], axis=1)


def smoothed(points, sigma):
    if sigma <= 0.0 or len(points) < 5:
        return points
    pad = min(int(4 * sigma) + 1, len(points) - 1)
    front = 2.0 * points[0] - points[pad:0:-1]
    back = 2.0 * points[-1] - points[-2: -pad - 2: -1]
    whole = np.concatenate([front, points, back])
    whole = ndimage.gaussian_filter1d(whole, sigma, axis=0, mode="nearest")
    return whole[pad: pad + len(points)]


def pixels_of(points):
    cells = np.round(points).astype(np.int64)
    keep = np.concatenate([[True], (np.diff(cells, axis=0) != 0).any(axis=1)])
    return cells[keep]


def runs_of(flags):
    edges = np.flatnonzero(np.diff(np.concatenate([[False], flags, [False]]).astype(np.int8)))
    return list(zip(edges[::2], edges[1::2]))


minor_line, major_line = np.zeros((h, w), dtype=bool), np.zeros((h, w), dtype=bool)
minor_bridge, major_bridge = np.zeros((h, w), dtype=bool), np.zeros((h, w), dtype=bool)
strait_line = np.zeros((h, w), dtype=bool)
bridges, lines_of = [], []
for number, (chain, highway) in enumerate(stretches, start=1):
    raw = np.array([(c // w, c % w) for c in chain], dtype=np.float64)
    raw_cells = raw.astype(np.int64)
    at_sea = sea[raw_cells[:, 0], raw_cells[:, 1]]
    parts = []
    start = 0
    on_shore = int(ON_BANK)
    for i in range(1, len(raw) + 1):
        if i == len(raw) or at_sea[i] != at_sea[start]:
            a, b = max(start - on_shore, 0) if at_sea[start] else start, min(i + on_shore, len(raw)) if at_sea[start] else i
            parts.append((raw[a:b], bool(at_sea[start])))
            start = i
    drawn_parts = []
    for points, over_sea in parts:
        if len(points) < 2:
            continue
        even = along(points, 1.0)
        if over_sea:
            assert not highway
            line = along(smoothed(even, SMOOTH), 0.5)
            cells = pixels_of(line)
            strait_line[cells[:, 0], cells[:, 1]] = True
            wet = sea[np.round(line[:, 0]).astype(np.int64), np.round(line[:, 1]).astype(np.int64)]
            middle = line[len(line) // 2]
            bridges.append({"stretch": number, "over": "sea", "at": middle, "from": line[0], "to": line[-1], "flow": None,
                            "water_px": float(wet.sum()) * 0.5, "highway": False, "town": True})
            drawn_parts.append(line)
            continue
        wanted = len(runs_of(river[raw_cells[:, 0], raw_cells[:, 1]]))
        for sigma in (SMOOTH, SMOOTH / 2, SMOOTH / 4, 0.0):
            line = along(smoothed(even, sigma), 0.5)
            cells = pixels_of(line)
            on_river = river[cells[:, 0], cells[:, 1]]
            if passable[cells[:, 0], cells[:, 1]].all() and len(runs_of(on_river)) == wanted:
                break
        (major_line if highway else minor_line)[cells[:, 0], cells[:, 1]] = True
        wet = river[np.round(line[:, 0]).astype(np.int64), np.round(line[:, 1]).astype(np.int64)]
        for a, b in runs_of(wet):
            a2, b2 = max(a - int(ON_BANK / 0.5), 0), min(b + int(ON_BANK / 0.5), len(line))
            deck = pixels_of(line[a2:b2])
            (major_bridge if highway else minor_bridge)[deck[:, 0], deck[:, 1]] = True
            middle = line[(a + b) // 2]
            y, x = int(round(middle[0])), int(round(middle[1]))
            near = town[max(y - 12, 0): y + 13, max(x - 12, 0): x + 13]
            bridges.append({"stretch": number, "over": "river", "at": middle, "from": line[a2], "to": line[b2 - 1],
                            "flow": float(flow[np.round(line[a:b, 0]).astype(int), np.round(line[a:b, 1]).astype(int)].max()),
                            "water_px": (b - a) * 0.5, "highway": highway, "town": bool((near > 0).any())})
        drawn_parts.append(line)
    # One line for the stretch: its parts end to end, without the few points where two overlap.
    whole = drawn_parts[0]
    for part in drawn_parts[1:]:
        nearest = int(np.argmin(np.hypot(*(part - whole[-1]).T)))
        whole = np.vstack([whole, part[nearest + 1:]])
    lines_of.append(whole)

# -- drawn as the picture drew them: do they give the picture back? -------------------------------------------
two, three = np.ones((2, 2), dtype=bool), np.ones((3, 3), dtype=bool)
road = ndimage.binary_dilation(minor_line, structure=two) | ndimage.binary_dilation(major_line, structure=three)
deck = (ndimage.binary_dilation(ndimage.binary_dilation(minor_bridge, structure=three), structure=two) |
        ndimage.binary_dilation(major_bridge, structure=three, iterations=2))
dots = town > 0
strait = ndimage.binary_dilation(ndimage.binary_dilation(strait_line, structure=three), structure=two) & ~dots
deck &= land & ~lake & ~dots
deck |= strait
road &= land & ~lake & ~dots & ~(river & ~deck)
is_red = (picture == (200, 40, 30)).all(axis=2)
is_umber = (picture == (60, 35, 15)).all(axis=2)
same = bool((is_red == (road & ~deck)).all()) and bool((is_umber == deck).all())
print("stretches: %d between %d places (%d settlements, %d forks); drawn, they give the red and dark brown of Roads.png exactly: %s (road %d px, bridge %d px; differing %d)" % (
    len(stretches), len(nodes), len(town_cells), len(forks), same, is_red.sum(), is_umber.sum(), (is_red != (road & ~deck)).sum() + (is_umber != deck).sum()))
assert same

# -- the network, written out --------------------------------------------------------------------------------
edge_of = {}
for number, (chain, _) in enumerate(stretches, start=1):
    for i, (p, q) in enumerate(zip(chain[:-1], chain[1:])):
        edge_of[(p, q)] = (number, True)
        edge_of[(q, p)] = (number, False)
places = [{"id": c, "kind": "settlement", "x": int(centres[c][0]), "y": int(centres[c][1])} for c in sorted(centres)]
places += [{"id": node_id[cell], "kind": "fork", "x": int(cell % w), "y": int(cell // w)} for cell in forks]
out_stretches, km_by = [], {True: 0.0, False: 0.0}
for number, ((chain, highway), line) in enumerate(zip(stretches, lines_of), start=1):
    km = float(np.hypot(*np.diff(line, axis=0).T).sum()) * KM
    km_by[highway] += km
    keep = np.zeros(len(line), dtype=bool)
    keep[::2] = True
    keep[-1] = True
    out_stretches.append({"id": number, "from": node_id[chain[0]], "to": node_id[chain[-1]], "highway": bool(highway), "km": round(km, 2),
                          "bridges": [i for i, b in enumerate(bridges, start=1) if b["stretch"] == number],
                          "points": [[round(float(x), 2), round(float(y), 2)] for y, x in line[keep]]})
with open(TO + "/Rivers.json", encoding="utf-8") as handle:
    rivers = json.load(handle)["rivers"]
river_points = np.array([p for r in rivers for p in r["points"]])
river_ids = np.array([r["id"] for r in rivers for _ in r["points"]])
river_wide = np.array([v for r in rivers for v in r["drawn_px"]])
tree = cKDTree(river_points)
out_bridges, furthest = [], 0.0
for i, b in enumerate(bridges, start=1):
    crossed = None
    if b["over"] == "river":
        gaps, nearest = tree.query([float(b["at"][1]), float(b["at"][0])], k=8)
        best = int(nearest[np.argmax(river_wide[nearest] / 2.0 - gaps)])     # the river whose water the point is deepest in
        crossed = int(river_ids[best])
        furthest = max(furthest, float(gaps[list(nearest).index(best)]) - river_wide[best] / 2.0)
    out_bridges.append({"id": i, "stretch": b["stretch"], "over": b["over"], "river": crossed, "at": [round(float(b["at"][1]), 1), round(float(b["at"][0]), 1)],
                        "from": [round(float(b["from"][1]), 1), round(float(b["from"][0]), 1)], "to": [round(float(b["to"][1]), 1), round(float(b["to"][0]), 1)],
                        "river_m3s": None if b["flow"] is None else round(b["flow"], 1), "water_px": round(b["water_px"], 1), "highway": bool(b["highway"]),
                        "at_settlement": bool(b["town"])})
print("bridges over rivers: each is given the river of Rivers.json it crosses; the furthest a bridge's middle lies outside its river's drawn width: %.1f px" % furthest)
out_roads = []
for (u, v), laid_road in sorted(laid.items()):
    cells = [int(y) * w + int(x) for y, x in laid_road["path"]]
    run = []
    for p, q in zip(cells[:-1], cells[1:]):
        number, forward = edge_of[(p, q)]
        if not run or run[-1][0] != number:
            run.append([number, forward])
    assert node_id[cells[0]] == u and node_id[cells[-1]] == v
    out_roads.append({"between": [int(u), int(v)], "km": round(float(laid_road["km"]), 1), "highway": bool(laid_road["highway"]), "over_the_sea": bool(laid_road["ferry"]),
                      "stretches": run})
used = {number for r in out_roads for number, _ in r["stretches"]}
print("roads between settlements: %d (%d highways, %d over the sea); every stretch is part of some road: %s; km of highway %.0f, of other road %.0f" % (
    len(out_roads), sum(r["highway"] for r in out_roads), sum(r["over_the_sea"] for r in out_roads), used == set(range(1, len(stretches) + 1)), km_by[True], km_by[False]))
print("bridges: %d (over rivers %d, over the sea %d); points written: %d" % (
    len(out_bridges), sum(b["over"] == "river" for b in out_bridges), sum(b["over"] == "sea" for b in out_bridges), sum(len(s["points"]) for s in out_stretches)))
save_json(TO + "/Roads.json", {
    "about": "The road network. places are its nodes: the 220 settlements (ids 1 to 220, a settlement's id being its county's number) and the forks where roads part outside a settlement (ids from 221). stretches are its edges: road from one place to the next. roads are the 351 roads between neighbouring settlements, each a run of stretches; roads share stretches where they run together.",
    "drawing": "A stretch is drawn 3 px wide if highway, otherwise 2 px. Drawing the stretches as the picture did gives the red and the dark brown of Roads.png exactly.",
    "fields": {"points": "[x, y] in pixels of the map, about a pixel apart, from the stretch's from place to its to place. A settlement's end is the middle of its dot, which the picture draws over.",
               "km": "the stretch's length along its line; a road's km is the length it was laid at, a little longer than its stretches' lines, which are smoothed",
               "stretches (of a road)": "[stretch id, true if the road runs it from its from to its to]", "highway": "a road on the way between the capitals of two kingdoms that share a border; a stretch is highway if any road over it is",
               "bridges": "at is the middle of the water crossed; from and to are the ends of the mark, which reaches 2 px on to each bank; water_px is how much water the road crosses; river is the river of Rivers.json it crosses and river_m3s that river's flow there; at_settlement is true within 12 px of a dot. A bridge is drawn 2 px wider than its road. The one bridge over the sea joins the island town (220) to the mainland."},
    "places": places, "stretches": out_stretches, "roads": out_roads, "bridges": out_bridges})
