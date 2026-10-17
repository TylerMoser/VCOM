"""Streams: the flowing water below the rivers, worked out on the drainage the rivers and lakes were
drawn from, so that they follow the same heights.

Where a stream begins. Wet country starts its streams on less ground than dry: a stream begins
where the ground it gathers and the water it carries, multiplied, come to what 20 km2 of the
Deciduous Forest gives (START, the square root of it), and it must carry at least Q_HEAD. The
drainage's water is the run-off the land was given as the water was made, blended at the
kingdoms' borders and split between the mountains' wet and dry sides, so this follows the
country cell by cell. It is the same as a stream beginning on START_AREA * (R / R_forest) ** -0.5
km2 of ground of run-off R: 9 km2 in the Evergreen Rainforest, 20 in the Deciduous Forest, 105 in
the Grassland, where Q_HEAD is what decides. Nowhere in the Desert does its own rain make one.

Where a stream runs. Once begun it runs on down the drainage until it meets a river, a lake, the
sea or a bigger stream; in the Desert and the Grassland, where water is lost to the bed, only
while it still carries Q_DRY. A lake that touches no river has its outlet drawn, however little
leaves it, down to what it reaches (in dry country while it carries Q_DRY; a lake nothing leaves
has none): that is what joins the lakes to the rivers. Lines are chained as the rivers' are: at a
meeting the stream carrying more goes on. A stream nothing joins is left out if it is shorter on
the land than LEAST_STUB, unless it is a lake's outlet.

How it is drawn. Like a river: the cell-to-cell steps smoothed away, made to wander where its bed
is nearly level and a little everywhere (never so far that it could reach a neighbour), ended
on the river's line as the scene draws it, inside the lake as the scene draws it, or a little
into the coast's line. The biggest are drawn first, and one that would cross a bigger is drawn
again with less wandering, or ended where it meets it. A stream is narrower than the narrowest
river, and widens with what it carries. Where it runs along a border it is put on the border's
line, with the border's colour laid under it; where a road runs along it, it is moved off beside
the road.

Usage: t1_streams.py <repo> <folder> [look x,y,w,h ...]
Reads the repository's MapCreation/SourceData, MapCreation/Elevation.png and vcom/Scenes/Map.tscn.
Writes Streams.json into the folder (the source data's, once looked at), and with look a picture
of each view given (x, y, width and height in pixels of the pictures) as the game shows it all the
way in: lookN_close.png, six screen pixels to a pixel of the pictures.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.spatial import cKDTree

REPO = Path(sys.argv[1])
OUT = Path(sys.argv[2])
LOOKS = sys.argv[4:] if len(sys.argv) > 3 and sys.argv[3] == "look" else []
sys.path.insert(0, str(REPO / "MapCreation" / "Scripts" / "scene"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import geo           # noqa: E402
import scene_read    # noqa: E402

Image.MAX_IMAGE_PIXELS = None
MC = REPO / "MapCreation"
SRC = MC / "SourceData"
OUT.mkdir(parents=True, exist_ok=True)
SEED = 20261017

# -- the rule -------------------------------------------------------------------------------------
CELL_KM = 0.67                       # a cell of the drainage is 2 x 2 px of the pictures
CELL_KM2 = CELL_KM * CELL_KM
FOREST_RUNOFF = 0.42                 # m a year: the Deciduous Forest's, as the water was made
START_AREA = 20.0                    # km2 of the Deciduous Forest on which a stream begins
START = START_AREA * np.sqrt(FOREST_RUNOFF * 1e6 / 31_557_600.0)    # sqrt(km2 * m3/s)
Q_HEAD = 0.2                         # m3/s: the least a stream may begin with
Q_DRY = 0.1                          # m3/s: in dry country, a stream ends once it carries less
DRY = (4, 5)                         # the kinds of country where water is lost: Desert, Grassland
LEAST_STUB = 4.5                     # px: a stream with nothing joining it is drawn only if this long
INTO_INK = 3.0                       # px a stream runs on past the land's edge into the coast's line
RES = 1.0                            # px between the points a stream is worked out at
WANDER_ROOM = 0.3                    # of the way to the nearest other water a stream may swing
SMALL_SWING, SMALL_WAVE = 0.7, 10.0  # px: the little wandering everywhere, so no stretch runs ruled
FLAT = 0.08                          # px: a width curve tells a stream's width to within this
WIDENS = 0.3                         # px: a stream that widens by less is drawn at its widest throughout
TURN = 10.0                          # degrees: no stream turns more than this at any of its points
COUNTY_FACTOR = 0.6045               # widths' factor where streams first show (100 miles tall)


def width_of(q, kind):
    """Pixels across for a stream carrying q m3/s: 0.94 px at 0.25 m3/s, 1.75 at 15, never as wide
    as the narrowest river's 2 px; a quarter wider in the Swamp and the Tropical Rainforest, as
    the rivers are there."""
    wide = 0.7 + 0.396 * np.maximum(q, 0.0) ** 0.36
    wide = wide * np.where((kind == 7) | (kind == 9), 1.25, 1.0)
    return np.clip(wide, 0.75, 1.95)


started = time.time()
rng = np.random.default_rng(SEED)


def grey(name):
    return np.asarray(Image.open(SRC / name))


def number(name):
    a = np.asarray(Image.open(SRC / name)).astype(np.int64)
    return a[..., 0] + 256 * a[..., 1]


def load(name):
    with open(SRC / name, encoding="utf-8") as handle:
        return json.load(handle)


# == the drainage ================================================================================
direction = grey("DrainageDirection.png").astype(np.int64)
H, W = direction.shape
n = H * W
flow = number("DrainageFlow.png").ravel() / 32.0
dlake = number("DrainageLakes.png").ravel()
drained = load("Drainage.json")
drawn_of = np.zeros(int(dlake.max()) + 1, dtype=np.int64)
for record in drained["lakes"]:
    drawn_of[record["id"]] = record["drawn_as"] or 0
lake_of_cell = drawn_of[dlake]                      # the drawn lake a cell lies in, 0 for none
terrain = grey("TerrainMap.png")
kind = np.zeros((H, W), dtype=np.int64)            # the cell's kind of country: the most of its 2 x 2
for dy in (0, 1):
    for dx in (0, 1):
        kind = np.maximum(kind, terrain[dy::2, dx::2][:H, :W])
kind = kind.ravel()
kingdom_px = grey("KingdomMap.png")
county_px = grey("CountyMap.png")
land_px = county_px > 0
elevation = np.asarray(Image.open(MC / "Elevation.png")).astype(np.float64) / 10.0

DC = np.array([0, 1, 1, 0, -1, -1, -1, 0, 1, 0])
DR = np.array([0, 0, 1, 1, 1, 0, -1, -1, -1, 0])
idx = np.arange(n).reshape(H, W)
rec = np.full(n, -1, dtype=np.int64)
rr, cc = np.nonzero((direction >= 1) & (direction <= 8))
d = direction[rr, cc]
rec[idx[rr, cc]] = idx[rr + DR[d], cc + DC[d]]
land = (direction > 0).ravel()
to_sea = (direction == 9).ravel()
sink = idx[int((drained["salt_lake_sink"][1] - 0.5) // 2), int((drained["salt_lake_sink"][0] - 0.5) // 2)]

depth = np.where(rec >= 0, 1, 0).astype(np.int64)
jump = rec.copy()
while (jump >= 0).any():
    has = jump >= 0
    depth[has] += depth[jump[has]]
    nxt = np.full(n, -1, dtype=np.int64)
    nxt[has] = jump[jump[has]]
    jump = nxt
area = land.astype(np.float64) * CELL_KM2
by_depth = np.nonzero(land)[0][np.argsort(-depth[land], kind="stable")]
levels = np.split(by_depth, np.flatnonzero(np.diff(depth[by_depth])) + 1)
for chunk in levels:
    r = rec[chunk]
    ok = r >= 0
    np.add.at(area, r[ok], area[chunk[ok]])


def centre(cells):
    """Middles of cells, in pixels from the pictures' corner."""
    r, c = np.divmod(np.asarray(cells), W)
    return np.column_stack([2.0 * c + 1.0, 2.0 * r + 1.0])


print("drainage: %d cells of land, %.1fs" % (land.sum(), time.time() - started))

# == the scene's water, borders and roads =========================================================
lines, polygons = scene_read.read(REPO / "vcom" / "Scenes" / "Map.tscn")
scene_rivers = {int(l.name[5:]): l for l in lines if l.parent == "Rivers"}
lake_polys = [p for p in polygons if p.parent == "Lakes" and "Island" not in p.name]
island_polys = [p for p in polygons if p.parent == "Lakes" and "Island" in p.name]
borders = [l for l in lines if l.parent.startswith("Borders/")]
roads = [l for l in lines if l.parent.startswith("Roads/")]
print("scene: %d rivers, %d lake shapes (%d islands), %d border lines, %d roads" % (
    len(scene_rivers), len(lake_polys), len(island_polys), len(borders), len(roads)))

rivers_table = load("Rivers.json")["rivers"]
lakes_table = load("Lakes.json")["lakes"]
river_cell = np.zeros(n, dtype=np.int64)            # the largest drawn river a cell's water runs in, 0 for none
for river in sorted(rivers_table, key=lambda r: -r["id"]):
    for x, y in river["course"]:
        c, r = int((x - 0.5) // 2), int((y - 0.5) // 2)
        if 0 <= r < H and 0 <= c < W:
            river_cell[idx[r, c]] = river["id"]
on_river = river_cell > 0
touched = set()
for river in rivers_table:
    touched.update(river.get("lakes") or [])
    if river.get("from_lake"):
        touched.add(river["from_lake"])


def sample_line(points, step):
    """Places [step] apart along a line, and how far along each is."""
    s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(points, axis=0).T))])
    at = np.arange(0.0, s[-1] + step * 0.5, step).clip(max=s[-1])
    return np.column_stack([np.interp(at, s, points[:, 0]), np.interp(at, s, points[:, 1])]), at


# The rivers as the scene draws them: places every half pixel with half the river's width there.
river_at, river_half, river_id = [], [], []
for rid, line in scene_rivers.items():
    pts, at = sample_line(line.points, 0.5)
    s = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(line.points, axis=0).T))])
    river_at.append(pts)
    river_half.append(0.5 * np.interp(at, s, line.widths()))
    river_id.append(np.full(len(pts), rid))
river_at = np.concatenate(river_at)
river_half = np.concatenate(river_half)
river_id = np.concatenate(river_id)
river_tree = cKDTree(river_at)

# The lakes as the scene draws them, on a grid of half pixels: which lake each half pixel is in.
LAKE_SCALE = 2
lake_grid = Image.new("I", (3100 * LAKE_SCALE, 4000 * LAKE_SCALE), 0)
pen = ImageDraw.Draw(lake_grid)
for p in lake_polys:
    lid = int("".join(ch for ch in p.name[4:] if ch.isdigit()))
    pen.polygon([(x * LAKE_SCALE, y * LAKE_SCALE) for x, y in p.points], fill=lid)
for p in island_polys:
    pen.polygon([(x * LAKE_SCALE, y * LAKE_SCALE) for x, y in p.points], fill=0)
lake_grid = np.asarray(lake_grid, dtype=np.int32)


def lake_at(points):
    """The drawn lake each point is in, 0 for none."""
    x = np.clip((points[:, 0] * LAKE_SCALE).astype(np.int64), 0, lake_grid.shape[1] - 1)
    y = np.clip((points[:, 1] * LAKE_SCALE).astype(np.int64), 0, lake_grid.shape[0] - 1)
    return lake_grid[y, x]


shore_at = []
for p in lake_polys:
    pts, _ = sample_line(np.vstack([p.points, p.points[:1]]), 1.0)
    shore_at.append(pts)
shore_at = np.concatenate(shore_at)

to_land = ndimage.distance_transform_edt(~land_px)
# Which way is straight out to sea, everywhere near the coast: down the land's depth, out along the
# sea's distance from it, smoothed so neighbouring streams go out side by side, not into each other.
_signed = ndimage.gaussian_filter(to_land - ndimage.distance_transform_edt(land_px), 3.0)
_out_y, _out_x = np.gradient(_signed)


def past_land(points):
    """How far beyond the land's edge each point lies (0 on land), as m1_shapes.py measures it."""
    dist = ndimage.map_coordinates(to_land, [points[:, 1] - 0.5, points[:, 0] - 0.5], order=1, mode="nearest")
    return np.maximum(dist - 0.5, 0.0)


def seaward(point):
    """The way straight out to sea from a point near the coast."""
    at = [[point[1] - 0.5], [point[0] - 0.5]]
    v = np.array([ndimage.map_coordinates(_out_x, at, order=1)[0], ndimage.map_coordinates(_out_y, at, order=1)[0]])
    return v / max(np.hypot(*v), 1e-9)


def height_at(points):
    return ndimage.map_coordinates(elevation, [points[:, 1] - 0.5, points[:, 0] - 0.5], order=1, mode="nearest")


print("scene read, %.1fs" % (time.time() - started))

# == which cells carry a stream ===================================================================
drawn_lake = lake_of_cell > 0
q_dry = np.where(np.isin(kind, DRY), Q_DRY, 0.0)
begins = land & ~on_river & ~drawn_lake & (np.sqrt(area * flow) >= START) & (flow >= Q_HEAD)
stream = begins.copy()
for chunk in levels:                                # from the top of each valley down
    r = rec[chunk]
    ok = (r >= 0) & stream[chunk]
    below = r[ok]
    go_on = ~on_river[below] & ~drawn_lake[below] & (flow[below] >= q_dry[below]) & (flow[below] > 0.0)
    stream[below[go_on]] = True

# A lake that touches no river has its outlet drawn, down to what it reaches.
outlet_of = {}                                      # first cell below a lake -> the lake
outlet_first = {}                                   # lake -> its last cell, and the first cell below it
lake_outlets = 0
for lake in lakes_table:
    if lake["id"] in touched or not lake["has_outlet"]:
        continue
    x, y = lake["outlet"]
    cell = idx[int((y - 0.5) // 2), int((x - 0.5) // 2)]
    last = cell
    while cell >= 0 and lake_of_cell[cell] == lake["id"]:
        last = cell
        cell = rec[cell]
    if cell < 0 or flow[cell] < max(q_dry[cell], 1e-6):
        continue
    outlet_first[lake["id"]] = (last, cell)
    lake_outlets += 1
    if on_river[cell] or drawn_lake[cell]:
        continue
    outlet_of[cell] = lake["id"]
    while cell >= 0 and not on_river[cell] and not drawn_lake[cell] and flow[cell] >= max(q_dry[cell], 1e-6):
        stream[cell] = True
        cell = rec[cell]
print("stream cells: %d (%d where one may begin); lakes off the rivers whose outlets are drawn: %d" % (
    stream.sum(), begins.sum(), lake_outlets))

# == the lines ====================================================================================
cells_by_flow = np.flatnonzero(stream)[np.argsort(-flow[stream], kind="stable")]
main_in = np.full(n, -1, dtype=np.int64)
for cell in cells_by_flow.tolist():
    below = rec[cell]
    if below >= 0 and stream[below] and main_in[below] < 0:
        main_in[below] = cell
fed = np.zeros(n, dtype=bool)
inner = stream & (rec >= 0)
fed[rec[inner]] = True
heads = np.flatnonzero(stream & ~(fed & stream))
rec_list = rec.tolist()
reaches = []
for head in heads.tolist():
    cells = [head]
    cell = head
    while True:
        below = rec_list[cell]
        if below < 0:
            end = "sink" if cell == sink else "sea"
            break
        if on_river[below]:
            end = "river"
            cells.append(below)
            break
        if drawn_lake[below]:
            end = "lake"
            cells.append(below)
            break
        if not stream[below]:
            end = "dry"
            break
        cells.append(below)
        if main_in[below] != cell:
            end = "joins"
            break
        cell = below
    from_lake = outlet_of.get(head, 0)
    if from_lake:
        # Start inside the lake, at its last cell, so the line can be begun on its shore.
        cells.insert(0, outlet_first[from_lake][0])
    reaches.append({"cells": np.array(cells, dtype=np.int64), "end": end, "from_lake": from_lake})
# A lake whose water runs at once into a river, another lake, or a cell another stream already runs
# through begins no line there of its own: it is given a short one, from its shore to that water, or
# it would lie beside the water it drains into, apart from it. Where the two are drawn touching,
# nothing of it is left to draw.
begun = {reach["from_lake"] for reach in reaches if reach["from_lake"]}
connectors = 0
for lake_id, (last, first) in outlet_first.items():
    if lake_id in begun:
        continue
    end = "river" if on_river[first] else "lake" if drawn_lake[first] else "joins" if stream[first] else None
    if end is None:
        continue
    reaches.append({"cells": np.array([last, first], dtype=np.int64), "end": end, "from_lake": lake_id})
    connectors += 1
print("lines: %d (%d of them a lake's short way to the water just below it); ends: %s" % (
    len(reaches), connectors, {e: sum(r["end"] == e for r in reaches) for e in ("joins", "river", "lake", "sea", "dry", "sink")}))

# Each line's place in the network: what it joins, and how much water it carries.
line_of_cell = np.zeros(n, dtype=np.int64)          # 1 + the line a stream cell's line is, 0 for none
for k, reach in enumerate(reaches):
    cells = reach["cells"]
    own = cells[(lake_of_cell[cells] != reach["from_lake"]) | (reach["from_lake"] == 0)]
    own = own[stream[own]]
    if reach["end"] == "joins":
        own = own[:-1]                              # the cell it joins at is the other line's
    line_of_cell[own] = k + 1
for k, reach in enumerate(reaches):
    cells = reach["cells"]
    mine = cells[line_of_cell[cells] == k + 1]
    reach["most_flow"] = float(flow[mine].max()) if len(mine) else 0.0
    reach["joins_line"] = int(line_of_cell[cells[-1]]) - 1 if reach["end"] == "joins" else -1
    reach["fed_by"] = 0
for reach in reaches:
    if reach["joins_line"] >= 0:
        reaches[reach["joins_line"]]["fed_by"] += 1

# == the room each has to wander ==================================================================
# Every other water a stream must keep clear of: other streams' cells, the rivers as drawn, lake shores.
room_points = [centre(np.flatnonzero(line_of_cell)), river_at[::2], shore_at]
room_labels = [line_of_cell[np.flatnonzero(line_of_cell)], np.zeros(len(river_at[::2]), dtype=np.int64),
               np.full(len(shore_at), -1, dtype=np.int64)]
room_points = np.concatenate(room_points)
room_labels = np.concatenate(room_labels)
room_tree = cKDTree(room_points)


def room_of(points, own):
    """How far each point is from water other than its own line's."""
    dist, which = room_tree.query(points, k=24, distance_upper_bound=12.0)
    labels = np.where(np.isfinite(dist), room_labels[np.minimum(which, len(room_labels) - 1)], own)
    other = (labels != own) & np.isfinite(dist)
    first = np.where(other.any(axis=1), dist[np.arange(len(points)), np.argmax(other, axis=1)], 12.0)
    return first


# == drawing each line ============================================================================
def smoothed(points, sigma):
    if len(points) < 4:
        return points.copy()
    soft = ndimage.gaussian_filter1d(points, sigma, axis=0, mode="nearest")
    t = np.linspace(0.0, 1.0, len(points))[:, None]
    return soft + (1 - t) * (points[0] - soft[0]) + t * (points[-1] - soft[-1])


def along(points):
    return np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(points, axis=0).T))])


def resampled(points, step):
    s = along(points)
    count = max(int(np.ceil(s[-1] / step)), 1)
    at = np.linspace(0.0, s[-1], count + 1)
    return np.column_stack([np.interp(at, s, points[:, 0]), np.interp(at, s, points[:, 1])]), at, s


def nearest_on(line, point):
    a, b = line[:-1], line[1:]
    dd = b - a
    length2 = np.maximum((dd * dd).sum(axis=1), 1e-12)
    t = np.clip(((point - a) * dd).sum(axis=1) / length2, 0.0, 1.0)
    near = a + dd * t[:, None]
    off = np.hypot(*(near - point).T)
    k = int(np.argmin(off))
    return near[k], float(off[k])


def river_point_near(point, rid):
    """The point of river rid's drawn line nearest a point."""
    return nearest_on(scene_rivers[rid].points, point)[0]


def wander(fine, wide, kinds, room, start_free, end_pinned, scale):
    """The line pushed from side to side: much where its bed is level, a little everywhere, never
    more than WANDER_ROOM of the way to other water, and not at all where it is pinned."""
    count = len(fine)
    if count < 4:
        return fine
    s = along(fine)
    z = ndimage.gaussian_filter1d(height_at(fine), 6.0, mode="nearest")
    fall = np.maximum(-np.gradient(z) / np.maximum(np.gradient(s) * 0.335, 1e-6), 0.0)
    lazy = np.clip((2.5 - fall) / 2.3, 0.0, 1.0) ** 1.5
    lazy *= np.where((kinds == 7) | (kinds == 9) | (kinds == 5), 1.25, 1.0)
    wave = 11.0 * wide + 16.0
    phase = np.cumsum(2.0 * np.pi * RES / wave) + rng.uniform(0, 2 * np.pi)
    phase += np.cumsum(rng.standard_normal(count) * 0.09)
    big = lazy * (1.9 * wide + 2.5) * np.sin(phase) * (0.75 + 0.25 * np.sin(0.37 * phase + 1.0))
    phase2 = np.cumsum(2.0 * np.pi * RES / SMALL_WAVE * (1.0 + 0.25 * np.sin(np.arange(count) * 0.05 + rng.uniform(0, 6.3)))) + rng.uniform(0, 2 * np.pi)
    small = SMALL_SWING * np.sin(phase2) * (0.6 + 0.4 * np.sin(0.29 * phase2 + 2.0))
    limit = WANDER_ROOM * room
    swing = np.clip(big + small, -limit, limit)
    total = s[-1]
    reach_end = min(1.5 * float(np.mean(wave)), 0.45 * total) if end_pinned else 2.0
    reach_start = 2.0 if start_free else min(float(np.mean(wave)), 0.3 * total)
    swing *= np.clip(s / max(reach_start, 1e-6), 0.0, 1.0) * np.clip((total - s) / max(reach_end, 1e-6), 0.0, 1.0)
    swing *= scale
    tangent = np.gradient(fine, axis=0)
    tangent /= np.maximum(np.hypot(tangent[:, 0], tangent[:, 1]), 1e-9)[:, None]
    return fine + swing[:, None] * np.column_stack([-tangent[:, 1], tangent[:, 0]])


# == borders and roads a stream runs along ========================================================
# No line may hide another. A stream is drawn over the borders, as the rivers are, and is narrower
# than any border, so it never hides one; but where it runs along one for long it is put on the
# border's own line and a line of the border's colour is laid under it, as wide as the stream and
# the border on both sides of it (named ...AlongStream), as the rivers have. Roads are drawn over
# the streams: where a road runs along one, the stream is moved off to the side the road leaves
# it, clear of the road as both are drawn where streams first show.
FOLLOW = 12.0            # px a stream keeps to a road before it is said to run along it; to a
                         # border, this and EASE at both ends, so that all of FOLLOW lies on it
NEAR_BORDER = 2.0        # px: a stream this close to a border's line that long is following it
EASE = 6.0               # px over which a stream is brought on to a border's line, or off a road
GAP = 0.35               # px left between a stream and a road it runs beside
RANKS = ("Kingdoms", "Duchies", "Counties")


def segment_index(line_list):
    """The segments of some lines, with which line each is, and a tree of their middles."""
    a, b, owner = [], [], []
    for k, l in enumerate(line_list):
        a.append(l.points[:-1])
        b.append(l.points[1:])
        owner.append(np.full(len(l.points) - 1, k))
    a, b, owner = np.concatenate(a), np.concatenate(b), np.concatenate(owner)
    reach = float(np.hypot(*(b - a).T).max()) * 0.5
    return a, b, owner, cKDTree(0.5 * (a + b)), reach


def project(points, index, within):
    """For each point, the nearest point of the indexed lines within [within]: (point, line, how far),
    line -1 where none is that near."""
    a, b, owner, tree, reach = index
    found = tree.query_ball_point(points, within + reach)
    near = np.zeros_like(points)
    which = np.full(len(points), -1, dtype=np.int64)
    off = np.full(len(points), np.inf)
    for i, segs in enumerate(found):
        if not segs:
            continue
        segs = np.asarray(segs)
        sa, sd = a[segs], b[segs] - a[segs]
        t = np.clip(((points[i] - sa) * sd).sum(axis=1) / np.maximum((sd * sd).sum(axis=1), 1e-12), 0.0, 1.0)
        cand = sa + sd * t[:, None]
        dist = np.hypot(*(cand - points[i]).T)
        j = int(np.argmin(dist))
        if dist[j] <= within:
            near[i], which[i], off[i] = cand[j], owner[segs[j]], dist[j]
    return near, which, off


border_lines = {rank: [l for l in borders if l.parent == "Borders/" + rank and "Along" not in l.name] for rank in RANKS}
border_index = {rank: segment_index(border_lines[rank]) for rank in RANKS}
road_index = segment_index(roads)
road_half = np.array([0.5 * l.width / scene_read.UNITS * COUNTY_FACTOR for l in roads])


def runs_of(flags):
    f = np.concatenate([[False], np.asarray(flags, dtype=bool), [False]])
    change = np.flatnonzero(f[1:] != f[:-1])
    return [(int(a), int(b) - 1) for a, b in zip(change[::2], change[1::2])]


def ramp(s, start, stop):
    """1 between two places along a line, falling to 0 over EASE outside them."""
    return np.clip(np.minimum((s - (start - EASE)) / EASE, ((stop + EASE) - s) / EASE), 0.0, 1.0)


def onto_borders(pts, wide, k, hold):
    """Puts the stretches of a stream that follow a border on the border's line, but for where
    [hold] keeps it (its end on the water it meets). Returns the new points and, for each such
    stretch, the line of the border's colour to lay under it."""
    casings = []
    for rank in RANKS:
        s = along(pts)
        near, which, off = project(pts, border_index[rank], NEAR_BORDER)
        for first, last in runs_of(which >= 0):
            # A run may follow one border and then another: split it where the border changes.
            start = first
            for i in range(first, last + 2):
                if i <= last and which[i] == which[start]:
                    continue
                s0, s1 = s[start], s[i - 1]
                if s1 - s0 >= FOLLOW + 2.0 * EASE:
                    w = np.zeros(len(pts))
                    w[start:i] = np.clip(np.minimum((s[start:i] - s0) / EASE, (s1 - s[start:i]) / EASE), 0.0, 1.0)
                    w *= hold
                    pts = pts * (1 - w[:, None]) + near * w[:, None]
                    line = border_lines[rank][which[start]]
                    full = np.flatnonzero(w >= 0.999)
                    if len(full) >= 2:
                        casings.append({"rank": rank, "border": line.name, "stream": k,
                                        "from": pts[full[0]].copy(), "to": pts[full[-1]].copy(),
                                        "stream_width": float(wide[full].max()), "border_width": line.width / scene_read.UNITS})
                        followed["borders"] += s[full[-1]] - s[full[0]]
                start = i
    return pts, casings


def off_roads(pts, wide, hold):
    """Moves the stretches of a stream that run along a road off to the side, clear of it, but for
    where [hold] keeps it."""
    clear_all = road_half.max() + 0.5 * wide.max() * COUNTY_FACTOR + GAP
    near, which, off = project(pts, road_index, clear_all)
    if (which < 0).all():
        return pts, 0.0
    s = along(pts)
    need = np.where(which >= 0, road_half[np.maximum(which, 0)] + 0.5 * wide * COUNTY_FACTOR + GAP, 0.0)
    close = (which >= 0) & (off < need)
    moved = 0.0
    out = pts.copy()
    for first, last in runs_of(close):
        if s[last] - s[first] < FOLLOW:
            continue
        # Which side of the road each point is on: where that changes the stream crosses it, and
        # the crossing is left where it is.
        tangent = np.gradient(pts, axis=0)
        side_vec = pts - near
        side = np.sign(side_vec[:, 0] * tangent[:, 1] - side_vec[:, 1] * tangent[:, 0])
        cross = [i for i in range(first + 1, last + 1) if side[i] != side[i - 1]]
        w = ramp(s, s[first], s[last])
        for i in cross:
            w *= np.clip(np.abs(s - s[i]) / 3.0, 0.0, 1.0)
        away = side_vec / np.maximum(off[:, None], 1e-9)
        bad = off < 1e-6
        if bad.any():
            normal = np.column_stack([-tangent[:, 1], tangent[:, 0]])
            normal /= np.maximum(np.hypot(normal[:, 0], normal[:, 1]), 1e-9)[:, None]
            away[bad] = normal[bad]
        target = near + away * need[:, None]
        push = np.where((which >= 0) & (off < need), 1.0, 0.0) * w * hold
        out = out * (1 - push[:, None]) + target * push[:, None]
        moved += s[last] - s[first]
    return out, moved


placed = {}                  # cell -> where the line through it ended up
final = [None] * len(reaches)
shore_lake = np.concatenate([np.full(len(sample_line(np.vstack([p.points, p.points[:1]]), 1.0)[0]),
                                     int("".join(ch for ch in p.name[4:] if ch.isdigit()))) for p in lake_polys])
shore_tree = cKDTree(shore_at)
followed = {"borders": 0.0, "roads": 0.0, "lake ends met": 0}
order = sorted(range(len(reaches)), key=lambda k: -reaches[k]["most_flow"])
dropped = {"stub": 0, "short": 0}
cut = {"river": 0, "lake": 0, "sea": 0}


def draw(k, scale=1.0):
    """Works out line k's points and widths. Returns None if nothing of it is left to draw."""
    reach = reaches[k]
    cells = reach["cells"]
    pts = centre(cells)
    q = flow[cells].copy()
    kinds = kind[cells]
    end = reach["end"]
    if end == "joins":
        target = placed.get(int(cells[-1]))
        if target is None:
            dropped["what it joins is not drawn"] = dropped.get("what it joins is not drawn", 0) + 1
            return None
        pts[-1] = target
        q[-1] = q[-2] if len(q) > 1 else q[-1]
    elif end == "river":
        rid = int(river_cell[cells[-1]])
        pts[-1] = river_point_near(pts[-2] if len(pts) > 1 else pts[-1], rid)
        q[-1] = q[-2] if len(q) > 1 else q[-1]
    elif end == "lake":
        q[-1] = q[-2] if len(q) > 1 else q[-1]
    elif end == "sea":
        # Out to sea straight from the coast, not on along its last step: neighbouring streams'
        # last steps often point at each other, and out that way they would cross.
        pts = np.vstack([pts, pts[-1] + 9.0 * seaward(pts[-1])])
        q = np.append(q, q[-1])
        kinds = np.append(kinds, kinds[-1])
    if reach["from_lake"] and len(q) > 1:
        q[0] = q[1]
    q = np.maximum.accumulate(q)
    if len(pts) < 2:
        return None
    pts = smoothed(pts, 1.4)
    fine, at, s = resampled(pts, RES)
    fq = np.interp(at, s, q)
    fk = kinds[np.clip(np.searchsorted(s, at), 0, len(kinds) - 1)]
    wide = width_of(fq, fk)
    room = room_of(fine, k + 1)
    fine = wander(fine, wide, fk, room, start_free=not reach["from_lake"], end_pinned=end != "dry", scale=scale)
    fine = smoothed(fine, 2.0)

    # Where it starts and ends as the scene draws the water.
    inside = lake_at(fine)
    first = 0
    if reach["from_lake"]:
        out = np.flatnonzero(inside != reach["from_lake"])
        if len(out) == 0:
            return None
        first = max(int(out[0]) - 1, 0)
    last = len(fine) - 1
    # The first lake it enters after leaving its own.
    entering = np.flatnonzero((inside > 0) & (np.arange(len(fine)) > first) & (inside != (reach["from_lake"] or -1)))
    if len(entering):
        last = min(last, int(entering[0]))
        cut["lake"] += end != "lake"
    # The first river it meets.
    dist, which = river_tree.query(fine[first: last + 1], distance_upper_bound=8.0)
    hit = np.isfinite(dist)
    touching = np.zeros(len(dist), dtype=bool)
    touching[hit] = dist[hit] <= np.maximum(river_half[which[hit]] * COUNTY_FACTOR, 0.5)
    meets = np.flatnonzero(touching)
    river_end = None
    if len(meets):
        at_meet = first + int(meets[0])
        if at_meet < last or end == "river":
            rid = int(river_id[which[meets[0]]])
            river_end = river_point_near(fine[at_meet], rid)
            last = at_meet
            cut["river"] += end != "river"
    fine_q, fine_w = fq, wide
    pts_out = fine[first: last + 1].copy()
    q_out = fine_q[first: last + 1].copy()
    w_out = fine_w[first: last + 1].copy()
    if river_end is not None:
        pts_out = np.vstack([pts_out, river_end])
        q_out = np.append(q_out, q_out[-1])
        w_out = np.append(w_out, w_out[-1])
    if end == "sea":
        beyond = past_land(pts_out)
        on = np.flatnonzero(beyond <= 0.0)
        if len(on):
            stop = next((j for j in range(int(on[-1]) + 1, len(pts_out)) if beyond[j] >= INTO_INK), None)
            if stop is not None:
                f = (INTO_INK - beyond[stop - 1]) / max(beyond[stop] - beyond[stop - 1], 1e-9)
                tip = pts_out[stop - 1] + f * (pts_out[stop] - pts_out[stop - 1])
                pts_out = np.vstack([pts_out[:stop], tip])
                q_out, w_out = q_out[: stop + 1], w_out[: stop + 1]
                cut["sea"] += 1
    if len(pts_out) < 2:
        return None
    # One that runs into a lake ends inside it as the scene draws the lake, which is smoothed and
    # can stop short of the cells the water was worked out on.
    if end == "lake" and lake_at(pts_out[-1:])[0] == 0:
        lid = int(lake_of_cell[cells[-1]])
        dist, which = shore_tree.query(pts_out[-1], k=64, distance_upper_bound=8.0)
        mine = [j for d_, j in zip(dist, which) if np.isfinite(d_) and shore_lake[j] == lid]
        if mine:
            shore = shore_at[mine[0]]
            step = shore - pts_out[-1]
            span = max(np.hypot(*step), 1e-9)
            extra = [pts_out[-1] + step * f for f in np.linspace(0.0, 1.0, int(np.ceil(span / RES)) + 1)[1:]]
            pts_out = np.vstack([pts_out] + extra + [shore + step / span * 1.0])
            q_out = np.concatenate([q_out, np.full(len(extra) + 1, q_out[-1])])
            w_out = np.concatenate([w_out, np.full(len(extra) + 1, w_out[-1])])
            followed["lake ends met"] += 1
    # Borders it runs along, and roads that run along it. Its end stays where it meets the water.
    s_all = along(pts_out)
    hold = np.clip((s_all[-1] - s_all) / EASE, 0.0, 1.0) if end != "dry" else np.ones(len(pts_out))
    pts_out, casings = onto_borders(pts_out, w_out, k, hold)
    pts_out, moved = off_roads(pts_out, w_out, hold)
    followed["roads"] += moved
    length = along(pts_out)[-1]
    if end == "sea":
        # Counted on the land alone: the part in the coast's line is not seen as a stream.
        out_at = np.flatnonzero(past_land(pts_out) > 0.0)
        length = along(pts_out[: max(int(out_at[0]), 1) + 1])[-1] if len(out_at) else length
    if length < LEAST_STUB and reach["fed_by"] == 0 and not reach["from_lake"]:
        dropped["stub"] += 1
        return None
    if length < 0.6:
        dropped["short"] += 1
        return None
    return {"points": pts_out, "flow": q_out, "width": w_out, "casings": casings}


# == crossings: no stream may cross another but where it joins it =================================
# Lines are drawn the biggest first, so a line is checked, as it is drawn, against the bigger ones
# already there: drawn again with less wandering if it crosses one, and if it still does, ended
# where it first meets it (or, where that is near its head, begun past it). Its own smaller
# streams are drawn after it, so they always join it where it finally runs.
GRID = 4.0
drawn_in = {}                # square of GRID px -> the lines with a point in it


def squares(points):
    cells = np.unique(np.floor(points / GRID).astype(np.int64), axis=0)
    return [(int(x), int(y)) for x, y in cells]


def first_crossing(p, q):
    """Where line p first crosses line q, as a place along p's points (2.5: halfway from its third
    to its fourth), or None. Touching at either end does not count."""
    a, r = p[:-1], np.diff(p, axis=0)
    b, s = q[:-1], np.diff(q, axis=0)
    lo, hi = q.min(axis=0) - 1.0, q.max(axis=0) + 1.0
    near = ((np.maximum(p[:-1], p[1:]) >= lo) & (np.minimum(p[:-1], p[1:]) <= hi)).all(axis=1)
    if not near.any():
        return None
    ia = np.flatnonzero(near)
    a, r = a[ia], r[ia]
    rxs = r[:, None, 0] * s[None, :, 1] - r[:, None, 1] * s[None, :, 0]
    qp = b[None, :, :] - a[:, None, :]
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (qp[..., 0] * s[None, :, 1] - qp[..., 1] * s[None, :, 0]) / rxs
        u = (qp[..., 0] * r[:, None, 1] - qp[..., 1] * r[:, None, 0]) / rxs
    hit = (t > 1e-6) & (t < 1 - 1e-6) & (u > 1e-6) & (u < 1 - 1e-6)
    if not hit.any():
        return None
    i, j = np.nonzero(hit)
    places = ia[i] + t[i, j]
    return float(places.min())


def crossing_with_drawn(result, k):
    """The first place line k's points cross a line already drawn: (place, other line), or None."""
    pts = result["points"]
    others = set()
    for sq in squares(pts):
        others.update(drawn_in.get(sq, ()))
    others.discard(k)
    best = None
    for other in others:
        place = first_crossing(pts, final[other]["points"])
        if place is not None and (best is None or place < best[0]):
            best = (place, other)
    return best


def cut_at(result, start, stop):
    """The part of a drawn line between two places along its points."""
    pts, q, w = result["points"], result["flow"], result["width"]
    idx_all = np.arange(len(pts), dtype=np.float64)

    def at(place):
        return np.array([np.interp(place, idx_all, pts[:, 0]), np.interp(place, idx_all, pts[:, 1])])

    inner = np.flatnonzero((idx_all > start + 1e-9) & (idx_all < stop - 1e-9))
    new_pts = np.vstack([at(start), pts[inner], at(stop)])
    new_q = np.concatenate([[np.interp(start, idx_all, q)], q[inner], [np.interp(stop, idx_all, q)]])
    new_w = np.concatenate([[np.interp(start, idx_all, w)], w[inner], [np.interp(stop, idx_all, w)]])
    kept_casings = [c for c in result.get("casings", [])
                    if nearest_on(new_pts, c["from"])[1] < 0.01 and nearest_on(new_pts, c["to"])[1] < 0.01]
    return {"points": new_pts, "flow": new_q, "width": new_w, "casings": kept_casings}


crossing_fix = {"less wandering": 0, "ended where it meets": 0, "begun past it": 0}
for k in order:
    result = draw(k)
    if result is not None:
        meeting = crossing_with_drawn(result, k)
        for scale in (0.5, 0.0):
            if meeting is None:
                break
            again = draw(k, scale)
            if again is None:
                break
            result, meeting = again, crossing_with_drawn(again, k)
            if meeting is None:
                crossing_fix["less wandering"] += 1
        while result is not None and meeting is not None:
            place, other = meeting
            length = len(result["points"]) - 1
            if place >= 0.5 * length:
                result = cut_at(result, 0.0, place)
                crossing_fix["ended where it meets"] += 1
            else:
                s_all = along(result["points"])
                past = float(np.interp(np.interp(place, np.arange(len(s_all)), s_all) + 1.5, s_all, np.arange(len(s_all))))
                result = cut_at(result, past, float(length)) if past < length - 1 else None
                crossing_fix["begun past it"] += 1
            if result is not None and along(result["points"])[-1] < 0.6:
                result = None
            meeting = crossing_with_drawn(result, k) if result is not None else None
    final[k] = result
    if result is None:
        continue
    for sq in squares(result["points"]):
        drawn_in.setdefault(sq, []).append(k)
    tree = cKDTree(result["points"])
    cells = reaches[k]["cells"]
    mine = cells[line_of_cell[cells] == k + 1]
    _, where = tree.query(centre(mine))
    for cell, w in zip(mine.tolist(), where.tolist()):
        placed[cell] = result["points"][w]
kept = [k for k in range(len(reaches)) if final[k] is not None]
print("drawn: %d lines (dropped: %s); ends moved by the drawn water: %s; crossings mended: %s; %.1fs" % (
    len(kept), dropped, cut, crossing_fix, time.time() - started))


def segments_of(keys):
    a, b, owner = [], [], []
    for k in keys:
        p = final[k]["points"]
        a.append(p[:-1])
        b.append(p[1:])
        owner.append(np.full(len(p) - 1, k))
    return np.concatenate(a), np.concatenate(b), np.concatenate(owner)


def crossings(keys):
    """Pairs of lines that cross somewhere other than one's end on the other."""
    a, b, owner = segments_of(keys)
    mid = 0.5 * (a + b)
    tree = cKDTree(mid)
    pairs = tree.query_pairs(2.0 * RES + 0.5, output_type="ndarray")
    if len(pairs) == 0:
        return set()
    i, j = pairs[:, 0], pairs[:, 1]
    keep = owner[i] != owner[j]
    i, j = i[keep], j[keep]
    p, r = a[i], b[i] - a[i]
    qq, s = a[j], b[j] - a[j]
    rxs = r[:, 0] * s[:, 1] - r[:, 1] * s[:, 0]
    qp = qq - p
    t = (qp[:, 0] * s[:, 1] - qp[:, 1] * s[:, 0]) / np.where(np.abs(rxs) < 1e-12, np.nan, rxs)
    u = (qp[:, 0] * r[:, 1] - qp[:, 1] * r[:, 0]) / np.where(np.abs(rxs) < 1e-12, np.nan, rxs)
    hit = (t > 1e-6) & (t < 1 - 1e-6) & (u > 1e-6) & (u < 1 - 1e-6)
    found = set()
    for x, y in zip(owner[i][hit].tolist(), owner[j][hit].tolist()):
        found.add((min(x, y), max(x, y)))
    return found


crossed = crossings(kept)
print("crossings left: %d" % len(crossed))

# == does every stream end on water? ==============================================================
# A stream that joins another ends on that one's line; one that reaches a river, on the river's
# line; a lake, inside the lake; the sea, past the land's edge. Anything else is left hanging.
ending = {"stream": 0, "river": 0, "lake": 0, "sea": 0, "dry": 0, "HANGING": 0}
hanging = []
river_samples = [(rid, sample_line(l.points, 0.05)[0]) for rid, l in scene_rivers.items()]
river_line_tree = cKDTree(np.concatenate([pts for _, pts in river_samples]))
river_line_ids = np.concatenate([np.full(len(pts), rid) for rid, pts in river_samples])
for k in kept:
    tip = final[k]["points"][-1]
    d_river, j_river = river_line_tree.query(tip)
    if lake_at(tip[None, :])[0] > 0:
        final[k]["ends"] = ("lake", int(lake_at(tip[None, :])[0]))
    elif past_land(tip[None, :])[0] > 1.0:
        final[k]["ends"] = ("sea", None)
    elif d_river < 0.06:
        final[k]["ends"] = ("river", int(river_line_ids[j_river]))
    else:
        found = None
        tx, ty = int(np.floor(tip[0] / GRID)), int(np.floor(tip[1] / GRID))
        for sq in [(tx + dx, ty + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]:
            for other in drawn_in.get(sq, ()):
                if other != k and final[other] is not None and nearest_on(final[other]["points"], tip)[1] < 0.06:
                    found = other
                    break
            if found is not None:
                break
        if found is not None:
            final[k]["ends"] = ("stream", found)
        elif reaches[k]["end"] == "dry":
            final[k]["ends"] = ("dry", None)
        else:
            final[k]["ends"] = ("HANGING", None)
            hanging.append(k)
    ending[final[k]["ends"][0]] += 1
print("where streams end: %s" % ending)

# == how much of the streams runs along a border or a road ========================================

casing_count = sum(len(final[k]["casings"]) for k in kept)
print("put on a border's line, with its colour laid under them: %d stretches of %d streams, %.0f km; moved off roads: %.0f km; lake ends brought into the lake as drawn: %d" % (
    casing_count, sum(1 for k in kept if final[k]["casings"]), followed["borders"] * 0.335, followed["roads"] * 0.335, followed["lake ends met"]))
# Still under a road for FOLLOW px or more, as both are drawn where streams first show?
under, under_px = 0, 0.0
for k in kept:
    pts = final[k]["points"]
    near, which, off = project(pts, road_index, 3.0)
    need = np.where(which >= 0, road_half[np.maximum(which, 0)] + 0.5 * final[k]["width"] * COUNTY_FACTOR, 0.0)
    s = along(pts)
    runs = [s[b] - s[a] for a, b in runs_of((which >= 0) & (off < need - 0.02)) if s[b] - s[a] >= FOLLOW]
    if runs:
        under += 1
        under_px += sum(runs)
print("streams still under a road for %.0f px or more: %d (%.0f px)" % (FOLLOW, under, under_px))
for k in hanging[:12]:
    print("   hanging: line %d, %s, ends at %s, joins line %d (drawn: %s)" % (
        k, reaches[k]["end"], np.round(final[k]["points"][-1], 1), reaches[k]["joins_line"],
        final[reaches[k]["joins_line"]] is not None if reaches[k]["joins_line"] >= 0 else "-"))

# == what was made ================================================================================
total_km = sum(along(final[k]["points"])[-1] for k in kept) * 0.335
by_kingdom = {}
for k in kept:
    p = final[k]["points"]
    kx = kingdom_px[np.clip(p[:, 1].astype(int), 0, 3999), np.clip(p[:, 0].astype(int), 0, 3099)]
    kx = kx[kx > 0]
    final[k]["kingdom"] = int(np.bincount(kx).argmax()) if len(kx) else 7
    final[k]["kingdoms"] = sorted(set(kx.tolist()))
    by_kingdom.setdefault(final[k]["kingdom"], [0, 0.0])
    by_kingdom[final[k]["kingdom"]][0] += 1
    by_kingdom[final[k]["kingdom"]][1] += along(p)[-1] * 0.335
land_km2 = {kk: float((kingdom_px == kk).sum()) * 0.112225 for kk in range(1, 10)}
print("streams: %d, %.0f km in all" % (len(kept), total_km))
for kk in range(1, 10):
    c, km = by_kingdom.get(kk, [0, 0.0])
    print("   kingdom %d: %5d streams, %7.0f km, %.3f km/km2; a closest view (2,874 km2) holds about %d streams" % (
        kk, c, km, km / land_km2[kk], round(c / land_km2[kk] * 2874)))
widths = np.concatenate([final[k]["width"] for k in kept])
print("widths: %.2f to %.2f px; points %d" % (widths.min(), widths.max(), sum(len(final[k]["points"]) for k in kept)))

# == written out ==================================================================================
# Numbered by the most water each carries, as the rivers are; a stream joining another comes after it.
sys.path.insert(0, str(REPO / "MapCreation" / "Scripts" / "duchy"))
import sourcefiles  # noqa: E402

numbered = sorted(kept, key=lambda k: (-round(float(np.max(final[k]["flow"])), 6), -along(final[k]["points"])[-1]))
number_of = {k: i + 1 for i, k in enumerate(numbered)}
THIN = 0.08              # px: a point is left out where the line moves less than this without it


def tidy_line(points, values, anchors):
    """A line with no more points than it needs to be drawn as smooth as it is: thinned where it
    runs straight, then given points where it bends, as the rivers' were. Every point another
    stream ends on is kept, so it still ends exactly on this line. The values carried along it
    are carried to the points kept."""
    pts = np.asarray(points, dtype=np.float64)
    cuts = sorted({0, len(pts) - 1} | set(anchors))
    parts = [geo.thinned(pts[a: b + 1], THIN) for a, b in zip(cuts[:-1], cuts[1:])]
    thin = np.concatenate([parts[0]] + [p[1:] for p in parts[1:]]) if len(parts) > 1 else parts[0]
    thin = np.asarray(thin, dtype=np.float64)
    # Where each kept point was among the old ones, to carry the values along.
    s_old = along(pts)
    tree = cKDTree(pts)
    _, at_old = tree.query(thin)
    s_thin = s_old[at_old]
    rounded, _, placed_at = geo.rounded(thin, False, TURN)
    s_new = np.interp(placed_at, np.arange(len(thin)), s_thin)
    carried = [np.interp(s_new, s_old, v) for v in values]
    return np.round(rounded, 3), carried


# Every stream that ends on another ends on one of its points: one ended where it met another
# (crossings mended) is put into that one's line where it lies.
to_insert = {}
for k in kept:
    kind_of_end, target = final[k]["ends"]
    if kind_of_end != "stream":
        continue
    tip = final[k]["points"][-1]
    other = final[target]["points"]
    if np.hypot(*(other - tip).T).min() > 1e-9:
        a, b = other[:-1], other[1:]
        dd = b - a
        t = np.clip(((tip - a) * dd).sum(axis=1) / np.maximum((dd * dd).sum(axis=1), 1e-12), 0.0, 1.0)
        seg = int(np.argmin(np.hypot(*(a + dd * t[:, None] - tip).T)))
        to_insert.setdefault(target, []).append((seg, float(t[seg]), tip))
for target, items in to_insert.items():
    f = final[target]
    for seg, t, tip in sorted(items, key=lambda x: (-x[0], -x[1])):
        f["points"] = np.insert(f["points"], seg + 1, tip, axis=0)
        f["flow"] = np.insert(f["flow"], seg + 1, f["flow"][seg] + t * (f["flow"][seg + 1] - f["flow"][seg]))
        f["width"] = np.insert(f["width"], seg + 1, f["width"][seg] + t * (f["width"][seg + 1] - f["width"][seg]))
anchors = {k: set() for k in kept}
for k in kept:
    kind_of_end, target = final[k]["ends"]
    if kind_of_end == "stream":
        other = final[target]["points"]
        j = int(np.argmin(np.hypot(*(other - final[k]["points"][-1]).T)))
        anchors[target].add(j)

streams_out, casings_out = [], []
total_points = 0
for k in numbered:
    f = final[k]
    pts, (q, w) = tidy_line(f["points"], [f["flow"], f["width"]], anchors[k])
    total_points += len(pts)
    at = along(pts)
    kind_of_end, target = f["ends"]
    joins = None
    if kind_of_end == "stream":
        joins = number_of[target]
    elif kind_of_end in ("river", "lake"):
        joins = target
    cells = reaches[k]["cells"]
    mine = cells[line_of_cell[cells] == k + 1]
    record = {"id": number_of[k], "ends_in": kind_of_end, "joins": joins,
              "from_lake": reaches[k]["from_lake"] or None,
              "kingdom": f["kingdom"], "kingdoms": f["kingdoms"],
              "largest_flow_m3s": round(float(np.max(q)), 2), "flow_at_end_m3s": round(float(q[-1]), 2),
              "length_km": round(float(at[-1]) * 0.335, 2),
              "points": sourcefiles.kept(pts - 0.5), "flow_m3s": np.round(q, 2), "width_px": np.round(w, 2),
              "course": centre(mine if len(mine) else cells) - 0.5}
    streams_out.append(record)
    for c in f["casings"]:
        line = next(l for l in border_lines[c["rank"]] if l.name == c["border"])
        # The border's own points from where the stream comes on to it to where it leaves.
        s_line = along(line.points)
        a0 = nearest_on(line.points, c["from"])[0]
        a1 = nearest_on(line.points, c["to"])[0]
        pos = []
        for p in (a0, a1):
            j = int(np.argmin(np.hypot(*(line.points[:-1] - p).T) + np.hypot(*(line.points[1:] - p).T) - np.hypot(*np.diff(line.points, axis=0).T)))
            pos.append(s_line[j] + np.hypot(*(p - line.points[j])))
        lo, hi = min(pos), max(pos)
        inner = (s_line > lo + 1e-6) & (s_line < hi - 1e-6)
        part = np.vstack([[np.interp(lo, s_line, line.points[:, 0]), np.interp(lo, s_line, line.points[:, 1])],
                          line.points[inner],
                          [np.interp(hi, s_line, line.points[:, 0]), np.interp(hi, s_line, line.points[:, 1])]])
        rank = {"Kingdoms": "kingdom", "Duchies": "duchy", "Counties": "county"}[c["rank"]]
        casings_out.append({"rank": rank, "border": c["border"], "stream": number_of[k],
                            "stream_width_px": round(c["stream_width"], 3),
                            "points": np.round(part, 3)})

about = {
    "about": "The %d streams as lines: the flowing water too small to be a river, worked out on the drainage the rivers and lakes were drawn from (DrainageDirection.png and DrainageFlow.png), and drawn as the rivers are. Made by Scripts/streams/t1_streams.py against vcom/Scenes/Map.tscn as it was then, whose rivers, lakes, borders and roads they meet, follow and keep clear of." % len(streams_out),
    "order": "Largest first: id 1 carries the most water. A stream is listed after the stream it joins.",
    "fields": {"ends_in": "stream (it joins the stream whose id is in joins), river (it ends on the line of the river whose id is in joins, as the game's scene draws it), lake (it ends inside the lake whose id is in joins), sea, or dry (it runs out of water in dry country)",
               "from_lake": "the lake of LakeMap.png it flows out of: every lake that touches no river and has water leaving it has its outlet drawn",
               "kingdom, kingdoms": "the kingdom of KingdomMap.png most of it lies in, and all it touches",
               "largest_flow_m3s, flow_at_end_m3s": "the most water it carries, and what it carries at its end",
               "length_km": "along the line",
               "points": "[x, y] in pixels of the map (a whole number is the middle of a pixel), thinned where it runs straight and with a point wherever it bends, so that it nowhere turns more than 10 degrees at one point",
               "flow_m3s, width_px": "the most water it has carried so far, and its width, at each point",
               "course": "the middles of the cells of DrainageDirection.png its water runs through, as the drainage has it: the line it was drawn from"},
    "which_are_drawn": "A stream begins where the ground it gathers (km2) times the water it carries (m3/s) reaches %.2f: what 20 km2 of the Deciduous Forest gives, so wet country begins its streams on less ground and dry on more (about 9 km2 in the Evergreen Rainforest, 18 in the Tundra, 105 in the Grassland), and only where it carries 0.2 m3/s or more. Once begun it runs on until it meets a river, a lake, the sea or a bigger stream; in the Desert and the Grassland, where water is lost to the ground, only while it carries 0.1 m3/s. The outlet of every lake that touches no river is drawn, down to what it reaches, if water leaves the lake. Nothing is drawn where only storms run: no dry washes. A stream that nothing joins is left out if it is under 1.5 km long." % (START * START),
    "width_rule": "width_px = 0.7 + 0.396 * flow ** 0.36, a quarter more in swamp and tropical rainforest country (7 and 9 on TerrainMap.png), and never under 0.75 or over 1.95: under the narrowest river's 2 px",
    "wandering": "A stream's line is its course smoothed, then swung from side to side, in loops about a dozen widths long where its bed is nearly level (as the rivers are) and a little everywhere, never more than %.1f of the way to other water; where it would still cross a bigger stream it is drawn with less, or ended where it meets it." % WANDER_ROOM,
    "meeting_other_lines": "A stream ends on the line of the river, or the stream, it joins, inside the lake it reaches, or %.0f px past the land's edge, in the coast's line. Where it follows a border's line for %.0f px or more it is put on that line, and along_borders gives the line of the border's colour the game's scene lays under it there. Where a road runs along it for %.0f px or more it is moved off to the side, clear of the road." % (INTO_INK, FOLLOW, FOLLOW),
    "along_borders_fields": "Where a stream runs on a border's line: the border's rank, the scene's name for the border, the stream's id, the stream's width there, and the line: the border's own points from where the stream comes on to it to where it leaves.",
}
data = dict(about)
data["streams"] = streams_out
data["along_borders"] = [{"rank": c["rank"], "border": c["border"], "stream": c["stream"],
                          "stream_width_px": c["stream_width_px"], "points": sourcefiles.kept(c["points"] - 0.5)} for c in casings_out]
sourcefiles.save_json(str(OUT / "Streams.json"), data)
sys.path.insert(0, str(REPO / "MapCreation" / "Scripts" / "scene"))
import streamshapes  # noqa: E402
with open(OUT / "Streams.json", encoding="utf-8") as handle:
    stream_shapes, stream_banks = streamshapes.shapes(json.load(handle))
print("wrote Streams.json: %d streams, %d stretches along borders; %d points, %d streams with a width curve; %.1fs" % (
    len(stream_shapes), len(stream_banks), total_points, sum(1 for s in stream_shapes if s["widths"]), time.time() - started))


# == looks ========================================================================================
SEA, LAND, WATER = (181, 235, 255), (255, 255, 255), (28, 112, 224)
RANK_COLOR = {"Kingdoms": (233, 0, 255), "Duchies": (110, 30, 180), "Counties": (128, 128, 128)}


def look(spec, factor, scale, name):
    """A view as the game would show it: [scale] screen pixels to a pixel of the pictures, every
    line [factor] times its scene width."""
    x0, y0, w, h = [float(v) for v in spec.split(",")]
    S = 2                                        # drawn twice as large, then shrunk, for soft edges
    px = scale * S
    img = Image.new("RGB", (int(w * px), int(h * px)), SEA)
    dr = ImageDraw.Draw(img)

    def tr(points):
        return [((x - x0) * px, (y - y0) * px) for x, y in points]

    box = (x0 - 20, y0 - 20, x0 + w + 20, y0 + h + 20)

    def near(points):
        return len(points) and (points[:, 0].max() >= box[0]) and (points[:, 0].min() <= box[2]) and (points[:, 1].max() >= box[1]) and (points[:, 1].min() <= box[3])

    for p in polygons:
        if p.parent.startswith("Land") and near(p.points):
            dr.polygon(tr(p.points), fill=LAND)
    for l in lines:
        if l.parent.startswith("Borders/") and near(l.points):
            color = RANK_COLOR[l.parent.split("/")[1]]
            dr.line(tr(l.points), fill=color, width=max(1, int(round(l.width / 3.35 * factor * px))), joint="curve")
    for k in kept:
        for c in final[k]["casings"]:
            line = next(l for l in border_lines[c["rank"]] if l.name == c["border"])
            seg = line.points
            ia = int(np.argmin(np.hypot(*(seg - c["from"]).T)))
            ib = int(np.argmin(np.hypot(*(seg - c["to"]).T)))
            part = seg[min(ia, ib): max(ia, ib) + 1]
            if len(part) >= 2 and near(part):
                wpx = (c["border_width"] + c["stream_width"]) * factor * px
                dr.line(tr(part), fill=RANK_COLOR[c["rank"]], width=max(1, int(round(wpx))), joint="curve")
    for p in polygons:
        if p.parent == "Lakes" and near(p.points):
            dr.polygon(tr(p.points), fill=LAND if "Island" in p.name else WATER)
    for k in kept:
        pts = final[k]["points"]
        if near(pts):
            wpx = float(np.max(final[k]["width"])) * factor * px
            dr.line(tr(pts), fill=WATER, width=max(1, int(round(wpx))), joint="curve")
    for l in lines:
        if l.parent == "Rivers" and near(l.points):
            wpx = l.width / 3.35 * factor * px
            dr.line(tr(l.points), fill=WATER, width=max(1, int(round(wpx))), joint="curve")
    for l in lines:
        if l.parent.startswith("Roads/") and near(l.points):
            dr.line(tr(l.points), fill=(200, 40, 30), width=max(1, int(round(l.width / 3.35 * factor * px))), joint="curve")
    img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    img.save(OUT / name)


for n_look, spec in enumerate(LOOKS):
    look(spec, 0.249, 6.0, "look%d_close.png" % n_look)
print("done, %.1fs" % (time.time() - started))
