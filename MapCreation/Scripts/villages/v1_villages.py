"""Villages and hamlets for the map, where people would have settled, and the lanes and channels
that join the villages to the roads and the rivers.

What was asked (2026-10-17): villages and hamlets in the proportions each kingdom's country
suits, at a density for play (about 2,000 in all, about 9 a county), at realistic sites; each
village joined to the network by a lane laid as the roads were, the hamlets left without; and in
the Swamp, a village joined by a channel to the rivers and lakes instead.

1. Every pixel of land is scored as a site for a village and for a hamlet: by its water (a
   river, a lake, a stream of the drainage), how high and how steep it is, in the mountains how
   low it lies in its valley, in the swamp how far it stands above the wet ground round it, the
   sea (fishing), the roads, a market town a morning's walk off, and a little unevenness.
2. Each kingdom's share of the places (SUPPORTS, VILLAGE_SHARE) is drawn from its land, a site
   the likelier the better it scores, none closer to another than APART: the villages first,
   then the hamlets among them.
3. A village within ON_ROAD of a road is moved on to it: the road runs through it.
4. A village in the swamp's country with no water within AT_WATER is joined by a channel dug to
   the nearest river, lake or the sea, along the lowest ground, never across a road.
5. Every other village is joined by a lane to the network as it then is: the roads, the lanes
   laid before, a village already joined, a capital. A lane is the cheapest way there by the
   roads' own rules (../duchy/r1_ground.py, ../duchy/roadnet.py), and the villages nearest the
   roads go first, so that one further off joins the lanes of those before it.

Everything random comes from SEED, so the same files give the same places. The pictures to look
at, if a folder is given for them, are the whole map at half size and close views at full size.

Usage: v1_villages.py <MapCreation dir> <Villages.json to write> [<folder for pictures to look at>]
"""
import json
import sys
import time
from collections import defaultdict
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.sparse import csgraph
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "duchy"))
import roadnet  # noqa: E402

Image.MAX_IMAGE_PIXELS = None
MC, WRITE_TO = sys.argv[1:3]
LOOK = sys.argv[3] if len(sys.argv) > 3 else None
SRC = MC + "/SourceData"
KM = 0.335
SEED = 20261017

# -- what is placed ---------------------------------------------------------------------------------
TOTAL = 2000
# How many people each kind of country feeds, the deciduous forest's farmland being 1: a kingdom's
# share of the places is its area times this.
SUPPORTS = {8: 1.0, 5: 0.5, 3: 0.35, 6: 0.3, 7: 0.25, 9: 0.25, 2: 0.2, 1: 0.08, 4: 0.06}
# How many of a kingdom's places are villages; the rest are hamlets. Open plains and oases gather
# people into villages; mountains, wet forest and tundra scatter them into hamlets.
VILLAGE_SHARE = {5: 0.65, 4: 0.60, 8: 0.50, 7: 0.40, 9: 0.40, 2: 0.35, 3: 0.30, 6: 0.30, 1: 0.20}
# km between the middles of two places, at the least: so that no two icons touch where they first
# show (a village at 100 miles tall, 225 m a screen pixel; a hamlet at 50, 112 m).
APART = {("village", "village"): 6.0, ("village", "capital"): 6.5,
         ("hamlet", "village"): 3.5, ("hamlet", "hamlet"): 3.5, ("hamlet", "capital"): 4.5}
# How strongly the better sites are preferred, a power of their score. A village is choosy (a quarter
# of them within 1 km of a river or lake the map draws, against 7% of the land); a hamlet takes
# what is left.
KEENNESS = {"village": 3.0, "hamlet": 1.0}
# How much better or worse the ground is from one stretch of country to the next, 12 px across, for
# no reason the map shows: a share of a site's score, one standard deviation of it. Twice this hid
# the rivers: a village was no likelier by a river than anywhere else.
UNEVEN = 0.15

# -- what makes a site, by the kind of country (TerrainMap.png's numbers) ------------------------------------
# Heights (m) up to which a village farms as well as anywhere, and from which none is founded. A
# hamlet (a shieling, a herder's steading) goes HAMLET_HIGHER further up.
HIGH = {1: (300, 900), 2: (700, 1500), 3: (1200, 2000), 4: (800, 1600), 5: (800, 1500), 6: (500, 1100),
        7: (300, 900), 8: (900, 1600), 9: (900, 1700)}
HAMLET_HIGHER = 300.0
# What water is worth to a site, at the most, and the km over which that falls away: a river or a
# lake as the map draws it (a mill, fish, boats), a brook of the drainage (1 m3/s or more), a rill
# (0.2 m3/s or more). Rivers and lakes count for most, so that the river valleys and lake shores are
# the most settled ground, as they were.
WATER = {"village": {"river": (1.6, 1.2), "lake": (1.3, 1.0), "brook": (0.75, 0.8), "rill": (0.55, 0.6)},
         "hamlet": {"river": (1.2, 2.0), "lake": (1.0, 1.6), "brook": (0.8, 1.3), "rill": (0.7, 1.0)}}
# What a site with no water near is worth: a well. Next to nothing in the desert.
DRY = {1: 0.10, 2: 0.10, 3: 0.10, 4: 0.005, 5: 0.04, 6: 0.15, 7: 0.15, 8: 0.15, 9: 0.15}
# How much the sea draws a settlement to the shore: fishing, a harbour.
SEA_DRAW = {1: 2.5, 2: 0.8, 3: 0.0, 4: 1.5, 5: 0.4, 6: 1.5, 7: 0.6, 8: 0.4, 9: 0.8}
MOUNTAINS = (1, 2, 3)      # where people keep to the valleys
SWAMP = 7
VALLEY_KM = 6.0            # how far round a site its valley's floor and tops are looked for
RAISED_KM = 3.0            # how far round a swamp site the ground it stands above is averaged
SALT_LAKE = 4              # Lakes.json: the desert's salt lake is no water to live by

# -- links ------------------------------------------------------------------------------------------------
ON_ROAD = 1.0              # km: a village this near a road is moved on to it
AT_WATER = 1.0             # km: a swamp village this near a river, a lake or the sea needs no channel
CHANNEL_MOST = 15.0        # km: a longer channel is not dug; the village gets a lane
LANE_WIDTH_PX = 1.2        # how wide a lane is drawn on the pictures to look at
SMOOTH = 3.0               # px, along a lane or a channel, as the roads were smoothed
ON_BANK = 2.0              # px a lane's bridge reaches on to each bank, as a road's does

started = time.time()


def say(*parts):
    print("[%5.0f s] " % (time.time() - started) + " ".join(str(p) for p in parts), flush=True)


def load(name):
    with open(SRC + "/" + name, encoding="utf-8") as handle:
        return json.load(handle)


def grey(path):
    return np.asarray(Image.open(path)).astype(np.int32)


def number_map(path):
    rgb = np.asarray(Image.open(path).convert("RGB")).astype(np.int64)
    return rgb[..., 0] + 256 * rgb[..., 1]


def filled(values, known):
    """The values where known, and elsewhere the value of the nearest pixel that is."""
    index = ndimage.distance_transform_edt(~known, return_distances=False, return_indices=True)
    return values[index[0], index[1]]


def km_from(mask):
    return (ndimage.distance_transform_edt(~mask) * KM).astype(np.float32)


def fall(d, scale):
    return np.exp(-(d / scale) ** 2).astype(np.float32)


def along(points, spacing):
    """A line's points set [spacing] apart (../duchy/r5b_draw.py)."""
    gaps = np.hypot(*np.diff(points, axis=0).T)
    reach = np.concatenate([[0.0], np.cumsum(gaps)])
    at = np.linspace(0.0, reach[-1], max(int(np.ceil(reach[-1] / spacing)) + 1, 2))
    return np.stack([np.interp(at, reach, points[:, 0]), np.interp(at, reach, points[:, 1])], axis=1)


def smoothed(points, sigma):
    """The points moved on to a smooth line, the two ends staying where they are (r5b_draw.py)."""
    if sigma <= 0.0 or len(points) < 5:
        return points
    pad = min(int(4 * sigma) + 1, len(points) - 1)
    front = 2.0 * points[0] - points[pad:0:-1]
    back = 2.0 * points[-1] - points[-2: -pad - 2: -1]
    whole = np.concatenate([front, points, back])
    whole = ndimage.gaussian_filter1d(whole, sigma, axis=0, mode="nearest")
    return whole[pad: pad + len(points)]


def runs_of(flags):
    """[start, stop) of each run of True."""
    edges = np.flatnonzero(np.diff(np.concatenate([[False], flags, [False]]).astype(np.int8)))
    return list(zip(edges[::2], edges[1::2]))


def cells_of(points):
    """The pixels (row, column) a line of closely set (x, y) points passes through, none twice running."""
    cells = np.round(points[:, ::-1]).astype(np.int64)
    keep = np.concatenate([[True], (np.diff(cells, axis=0) != 0).any(axis=1)])
    return cells[keep]


def length_px(points):
    return float(np.hypot(*np.diff(points, axis=0).T).sum())


def rounded_points(points):
    return [[round(float(x), 2), round(float(y), 2)] for x, y in points]


# == the map ===============================================================================================
county = grey(SRC + "/CountyMap.png")
h, w = county.shape
land = county > 0
kingdom = grey(SRC + "/KingdomMap.png")
terrain = grey(SRC + "/TerrainMap.png")
terrain = np.where(land, filled(terrain, terrain > 0), 0)
lake_id = number_map(SRC + "/LakeMap.png")
lake = lake_id > 0
blue = (np.asarray(Image.open(MC + "/Water.png").convert("RGB")) == (28, 112, 224)).all(axis=2)
river = blue & ~lake & land
sea = ~land
lakes_table = {l["id"]: l for l in load("Lakes.json")["lakes"]}
surface = np.zeros(max(lakes_table) + 1, dtype=np.float32)
for i, l in lakes_table.items():
    surface[i] = l["surface_m"]
raw_height = np.asarray(Image.open(MC + "/Elevation.png")).astype(np.float32) / 10.0
height = np.where(land, filled(raw_height, raw_height > 0), 0.0).astype(np.float32)
height = np.where(lake, surface[lake_id], height)           # a lake's surface, not its bed
flow = np.repeat(np.repeat(number_map(SRC + "/DrainageFlow.png") / 32.0, 2, axis=0), 2, axis=1)[:h, :w].astype(np.float32)
regions = load("Regions.json")
county_duchy = {c["number"]: c["duchy"] for c in regions["counties"]}
county_kingdom = {c["number"]: c["kingdom"] for c in regions["counties"]}
kingdom_km2 = {k["number"]: k["km2"] for k in regions["kingdoms"]}
say("map read: %d x %d, %d px of land" % (w, h, land.sum()))

# Smoothed inside the land, as the roads read it.
weight = ndimage.gaussian_filter(land.astype(np.float32), 1.5)
smooth = ndimage.gaussian_filter(np.where(land, height, 0.0), 1.5) / np.maximum(weight, 1e-3)
smooth = np.where(land, smooth, 0.0).astype(np.float32)
gy, gx = np.gradient(smooth)
slope = (np.hypot(gy, gx) / (KM * 1000.0)).astype(np.float32)

# The capitals, and their dots as the pictures draw them.
settlements = load("Settlements.json")["settlements"]
DOT = {"kingdom": 13, "duchy": 9, "county": 6}
capital_at = np.array([[s["x"], s["y"]] for s in settlements], dtype=np.float64)
town = np.zeros((h, w), dtype=np.int16)
for s in settlements:
    r = DOT[s["rank"]]
    ys, xs = slice(max(s["y"] - r, 0), s["y"] + r + 1), slice(max(s["x"] - r, 0), s["x"] + r + 1)
    yy, xx = np.ogrid[ys, xs]
    town[ys, xs] = np.where((yy - s["y"]) ** 2 + (xx - s["x"]) ** 2 <= (r + 0.4) ** 2, s["county"], town[ys, xs])
dots = town > 0

# The roads, as points half a pixel apart, each with its stretch.
roads_table = load("Roads.json")
road_parts, road_owner = [], []
for stretch in roads_table["stretches"]:
    dense = along(np.asarray(stretch["points"], dtype=np.float64), 0.5)
    road_parts.append(dense)
    road_owner.append(np.full(len(dense), stretch["id"]))
road_points = np.concatenate(road_parts)
road_owner = np.concatenate(road_owner)
road_tree = cKDTree(road_points)
road = np.zeros((h, w), dtype=bool)
road_cells = np.round(road_points[:, ::-1]).astype(np.int64)
road[road_cells[:, 0], road_cells[:, 1]] = True

# The rivers' points, to name the river a lane crosses.
river_rows = load("Rivers.json")["rivers"]
river_points = np.concatenate([np.asarray(r["points"], dtype=np.float64) for r in river_rows])
river_owner = np.concatenate([np.full(len(r["points"]), r["id"]) for r in river_rows])
river_flow = np.concatenate([np.asarray(r["flow_m3s"], dtype=np.float64) for r in river_rows])
river_tree = cKDTree(river_points)

# == 1. sites ==============================================================================================
fresh_lake = lake & (lake_id != SALT_LAKE)
d_river = km_from(river)
d_lake = km_from(fresh_lake)
d_brook = km_from((flow >= 1.0) & land & ~lake)
d_rill = km_from((flow >= 0.2) & land & ~lake)
d_sea = (ndimage.distance_transform_edt(land) * KM).astype(np.float32)
d_road = km_from(road)
capital_mask = np.zeros((h, w), dtype=bool)
capital_mask[capital_at[:, 1].astype(int), capital_at[:, 0].astype(int)] = True
d_capital = km_from(capital_mask)
say("distances worked out")


def by_kind(values):
    table = np.zeros(10, dtype=np.float32)
    for k, v in values.items():
        table[k] = v
    return table[terrain]


full_at, none_at = by_kind({k: v[0] for k, v in HIGH.items()}), by_kind({k: v[1] for k, v in HIGH.items()})
dry = by_kind(DRY)
sea_draw = by_kind(SEA_DRAW)
mountain = np.isin(terrain, MOUNTAINS)
reach = int(round(VALLEY_KM / KM)) * 2 + 1
low = ndimage.minimum_filter(np.where(land, smooth, 0.0), size=reach)
top = ndimage.maximum_filter(np.where(land, smooth, 0.0), size=reach)
up_the_valley = np.clip((smooth - low) / (top - low + 30.0), 0.0, 1.0).astype(np.float32)
reach = int(round(RAISED_KM / KM)) * 2 + 1
round_about = ndimage.uniform_filter(np.where(land, smooth, 0.0), size=reach) / np.maximum(ndimage.uniform_filter(land.astype(np.float32), size=reach), 1e-3)
raised = (smooth - round_about).astype(np.float32)
rng = np.random.default_rng(SEED)
lumps = ndimage.gaussian_filter(rng.standard_normal((h, w)).astype(np.float32), 12.0)
unevenness = np.clip(1.0 + UNEVEN * lumps / lumps.std(), 0.5, 1.6).astype(np.float32)
town_pull = (1.0 + 0.3 * fall(d_capital - 12.0, 8.0)).astype(np.float32)
bank = ndimage.binary_dilation(river | lake, structure=np.ones((3, 3), dtype=bool))
site_ok = land & ~bank & (d_sea >= 2.5 * KM) & ~dots
del low, top, round_about, lumps


def score(kind):
    """How good every pixel is as a site for a village or a hamlet: 0 where none can be."""
    village = kind == "village"
    worth = WATER[kind]
    s = np.maximum.reduce([worth[name][0] * fall(d, worth[name][1]) for name, d in
                           (("river", d_river), ("lake", d_lake), ("brook", d_brook), ("rill", d_rill))] + [dry if village else 2.0 * dry])
    full, none = (full_at, none_at) if village else (full_at + HAMLET_HIGHER, none_at + HAMLET_HIGHER)
    with np.errstate(divide="ignore", invalid="ignore"):         # off the land, where no kind of country is
        s *= np.clip((none - height) / (none - full), 0.0, 1.0)
    s *= np.exp(-(slope / (0.10 if village else 0.18)) ** 2)
    s *= np.where(mountain, 1.0 - (0.75 if village else 0.4) * up_the_valley, 1.0)
    s *= np.where(terrain == SWAMP, np.clip(0.4 + 0.3 * raised, 0.15, 1.6), 1.0)
    s *= 1.0 + sea_draw * fall(d_sea, 1.5)
    s *= 1.0 + (0.6 if village else 0.15) * fall(d_road, 2.0)
    s *= town_pull * unevenness
    return np.where(site_ok, s, 0.0).astype(np.float32)


# Each kingdom's share, by its area and what its country supports, to the whole place.
weights = {k: kingdom_km2[k] * SUPPORTS[k] for k in SUPPORTS}
exact = {k: TOTAL * v / sum(weights.values()) for k, v in weights.items()}
quota = {k: int(np.floor(v)) for k, v in exact.items()}
for k in sorted(exact, key=lambda k: exact[k] - quota[k], reverse=True)[: TOTAL - sum(quota.values())]:
    quota[k] += 1
villages_wanted = {k: int(round(quota[k] * VILLAGE_SHARE[k])) for k in quota}
hamlets_wanted = {k: quota[k] - villages_wanted[k] for k in quota}
say("places wanted by kingdom (villages + hamlets):", ", ".join("%d: %d + %d" % (k, villages_wanted[k], hamlets_wanted[k]) for k in sorted(quota)))

CELL = max(APART.values()) / KM


class Placed:
    """The places so far, by squares of CELL px, to find those near a point quickly."""

    def __init__(self):
        self.squares = defaultdict(list)

    def add(self, x, y, kind):
        self.squares[(int(x // CELL), int(y // CELL))].append((x, y, kind))

    def clear_of(self, x, y, kind):
        cx, cy = int(x // CELL), int(y // CELL)
        for sx in (cx - 1, cx, cx + 1):
            for sy in (cy - 1, cy, cy + 1):
                for px, py, other in self.squares.get((sx, sy), ()):
                    gap = APART.get((kind, other)) or APART.get((other, kind))
                    if gap and (px - x) ** 2 + (py - y) ** 2 < (gap / KM) ** 2:
                        return False
        return True


placed = Placed()
for x, y in capital_at:
    placed.add(float(x), float(y), "capital")
places = []
for kind, wanted in (("village", villages_wanted), ("hamlet", hamlets_wanted)):
    s = score(kind)
    for k in sorted(wanted):
        index = np.flatnonzero((kingdom == k).ravel() & (s.ravel() > 0.0))
        weight_k = s.ravel()[index].astype(np.float64) ** KEENNESS[kind]
        keys = np.log(rng.random(len(index))) / weight_k           # the larger the likelier (Efraimidis and Spirakis)
        order = index[np.argsort(-keys)]
        got = 0
        for cell in order:
            y, x = divmod(int(cell), w)
            if placed.clear_of(float(x), float(y), kind):
                placed.add(float(x), float(y), kind)
                places.append({"kind": kind, "x": float(x), "y": float(y), "score": float(s[y, x])})
                got += 1
                if got == wanted[k]:
                    break
        if got < wanted[k]:
            say("kingdom %d: only %d of %d %ss found room" % (k, got, wanted[k], kind))
    del s
say("placed %d villages and %d hamlets" % (sum(p["kind"] == "village" for p in places), sum(p["kind"] == "hamlet" for p in places)))

# == 3. villages on the roads ===============================================================================
on_road = 0
for p in places:
    if p["kind"] != "village":
        continue
    off, i = road_tree.query([p["x"], p["y"]])
    if off * KM > ON_ROAD:
        continue
    x, y = road_points[i]
    r, c = int(round(y)), int(round(x))
    if river[r, c] or lake[r, c] or dots[r, c]:
        continue
    p["x"], p["y"] = round(float(x), 2), round(float(y), 2)
    p["link"] = {"kind": "road", "stretch": int(road_owner[i])}
    on_road += 1
say("villages moved on to a road: %d" % on_road)

# Where each is, and its name: numbered in its county, villages then hamlets, the nearest its capital first.
capital_of = {s["county"]: (s["x"], s["y"]) for s in settlements}
for p in places:
    r, c = int(round(p["y"])), int(round(p["x"]))
    p["county"] = int(county[r, c])
    p["duchy"] = county_duchy[p["county"]]
    p["kingdom"] = county_kingdom[p["county"]]
    p["terrain"] = int(terrain[r, c])
    p["height_m"] = round(float(height[r, c]), 1)
    cx, cy = capital_of[p["county"]]
    p["from_capital_km"] = round(float(np.hypot(p["x"] - cx, p["y"] - cy)) * KM, 1)
places.sort(key=lambda p: (p["kind"] != "village", p["county"], p["from_capital_km"]))
counted = defaultdict(int)
for i, p in enumerate(places):
    counted[(p["county"], p["kind"])] += 1
    p["id"] = i + 1
    p["name"] = "County%03d%s%d" % (p["county"], p["kind"].capitalize(), counted[(p["county"], p["kind"])])

# == the ground, as the roads met it (../duchy/r1_ground.py) ================================================
COUNTRY = {1: 1.25, 2: 1.25, 3: 1.10, 4: 1.15, 5: 1.00, 6: 1.30, 7: 1.70, 8: 1.15, 9: 1.40}
square = np.ones((3, 3), dtype=bool)
beside_town = np.zeros((h, w), dtype=bool)
for s in settlements:
    reach_px = DOT[s["rank"]] + 10
    ys, xs = slice(max(s["y"] - reach_px, 0), s["y"] + reach_px + 1), slice(max(s["x"] - reach_px, 0), s["x"] + reach_px + 1)
    yy, xx = np.ogrid[ys, xs]
    beside_town[ys, xs] |= (yy - s["y"]) ** 2 + (xx - s["x"]) ** 2 <= reach_px ** 2
loose = land & ~lake
passable = loose & ~((ndimage.binary_dilation(lake, structure=square) | ndimage.binary_dilation(sea, structure=square)) & ~dots)
going = np.ones((h, w), dtype=np.float32)
for k, factor in COUNTRY.items():
    going[kingdom == k] = factor
going *= 1.0 + np.minimum((slope / 0.10) ** 2, 6.0)
going *= 1.0 + np.maximum(smooth - 1800.0, 0.0) / 800.0
far = ndimage.distance_transform_edt(~(river | lake)) * KM
going *= np.where(kingdom == 4, 1.0 + 0.5 * np.minimum(far / 30.0, 1.0), 1.0)
near_river = ndimage.binary_dilation(river, structure=square)
going *= np.where(near_river & ~river, 4.0, np.where(ndimage.binary_dilation(river, structure=square, iterations=2) & ~river, 1.5, 1.0))
going *= np.where(ndimage.binary_dilation(lake, iterations=3) & ~lake, 1.5, 1.0)
going *= np.where(ndimage.binary_dilation(sea, iterations=4) & land, 1.4, 1.0)
rough_rng = np.random.default_rng(20261012)
rough = ndimage.gaussian_filter(rough_rng.standard_normal((h, w)).astype(np.float32), 2.0)
going *= 1.0 + 0.10 * rough / rough.std()
going[river] = 6.0
going = np.where(dots & ~river, going * 0.6, going)
going = np.where(loose, going, 0.0).astype(np.float32)
size = np.where(river, np.maximum(np.repeat(np.repeat(ndimage.maximum_filter(number_map(SRC + "/DrainageFlow.png") / 32.0, size=7), 2, axis=0), 2, axis=1)[:h, :w], 15.0), 0.0)
crossing = np.where(river, 3.0 + 3.0 * (size / 15.0) ** 0.6, 0.0)
crossing = np.where(beside_town, crossing * 0.3, crossing)
crossing = np.where(ndimage.binary_dilation(dots, structure=square, iterations=2) & river, 1.0e4, crossing).astype(np.float32)
del far, rough, size
say("the ground made")


def ground_of(**arrays):
    """A roadnet.Ground over arrays held here rather than read from a folder."""
    g = roadnet.Ground.__new__(roadnet.Ground)
    g.steps, g.on_road = None, None
    for name, array in arrays.items():
        setattr(g, name, array)
    g.loose = arrays["passable"]
    g.sea = sea
    g.shape = arrays["passable"].shape
    return g


def route_to_any(ground, start, targets, margin, most):
    """The cheapest way over [ground] from [start] (x, y) to any pixel of [targets]: (cost, cells as
    (row, column), the pixel reached), or None if there is none within [most] px. Searched in a
    window round the start, widened until no way out of it could be cheaper than the best found
    inside it, or until it reaches [most]."""
    x, y = start
    margin = min(margin, most)
    while True:
        ys = slice(max(y - margin, 0), min(y + margin + 1, h))
        xs = slice(max(x - margin, 0), min(x + margin + 1, w))
        widest = margin >= most
        inside = targets[ys, xs]
        if not inside.any():
            if widest:
                return None
            margin = min(margin * 2, most)
            continue
        graph, ww = ground._graph((ys, xs), False, False)
        source = (y - ys.start) * ww + (x - xs.start)
        cost, before = csgraph.dijkstra(graph, directed=False, indices=source, return_predecessors=True)
        candidates = np.flatnonzero(inside.ravel())
        best = candidates[np.argmin(cost[candidates])]
        if not np.isfinite(cost[best]):
            if widest:
                return None
            margin = min(margin * 2, most)
            continue
        rim = np.zeros(inside.shape, dtype=bool)
        if ys.start > 0:
            rim[0, :] = True
        if ys.stop < h:
            rim[-1, :] = True
        if xs.start > 0:
            rim[:, 0] = True
        if xs.stop < w:
            rim[:, -1] = True
        if not widest and (cost[rim.ravel()] < cost[best]).any():
            margin = min(margin * 2, most)
            continue
        cells = [int(best)]
        while cells[-1] != source:
            cells.append(int(before[cells[-1]]))
        cells.reverse()
        path = [(c // ww + ys.start, c % ww + xs.start) for c in cells]
        return float(cost[best]), path, path[-1]


def drawn_line(cells, start_at, end_at, keep_on, water):
    """A link's cells as a smooth line from [start_at] to [end_at] (x, y), smoothed as the roads were
    as far as it stays on [keep_on] and crosses [water] as often as the cells did."""
    raw = np.array([(c, r) for r, c in cells], dtype=np.float64)
    raw[0], raw[-1] = start_at, end_at
    if len(raw) == 1:
        raw = np.array([start_at, end_at], dtype=np.float64)
    even = along(raw, 1.0)
    first = cells_of(even)
    wanted = len(runs_of(water[first[:, 0], first[:, 1]]))
    for sigma in (SMOOTH, SMOOTH / 2, SMOOTH / 4, 0.0):
        line = along(smoothed(even, sigma), 0.5)
        lc = cells_of(line)
        inner = lc[1:-1] if len(lc) > 2 else lc[:0]
        if keep_on[inner[:, 0], inner[:, 1]].all() and len(runs_of(water[lc[:, 0], lc[:, 1]])) == wanted:
            return line
    return along(raw, 0.5)


# == 4. channels in the swamp ===============================================================================
for p in places:
    p.setdefault("link", None)
village_list = [p for p in places if p["kind"] == "village"]
open_water = river | fresh_lake
coast_cells = land & ndimage.binary_dilation(sea, structure=square)
channel_of = np.zeros((h, w), dtype=np.int32)          # which channel a pixel is on
channels = []
wet_ground = ground_of(passable=(land & ~ndimage.binary_dilation(road, structure=square) & ~ndimage.binary_dilation(dots, structure=square)) | open_water | coast_cells,
                       going=np.where(lake | river, 1.0, 1.0 + np.maximum(smooth, 0.0) / 2.0).astype(np.float32),
                       height=smooth, river=np.zeros((h, w), dtype=bool), crossing=np.zeros((h, w), dtype=np.float32))
d_open = np.minimum(km_from(open_water), d_sea)
swamp_villages = [p for p in village_list if p["kingdom"] == SWAMP and p["terrain"] == SWAMP and p["link"] is None]
swamp_villages.sort(key=lambda p: d_open[int(round(p["y"])), int(round(p["x"]))])
for p in swamp_villages:
    r, c = int(round(p["y"])), int(round(p["x"]))
    if d_open[r, c] <= AT_WATER:
        p["link"] = {"kind": "water"}
        continue
    found = route_to_any(wet_ground, (c, r), open_water | coast_cells | (channel_of > 0), int(max(30, 2.0 * d_open[r, c] / KM)),
                         int(CHANNEL_MOST / KM))
    if found is None:
        continue
    cost, cells, (er, ec) = found
    if channel_of[er, ec]:
        ends_in = {"kind": "channel", "id": int(channel_of[er, ec])}
    elif lake[er, ec]:
        ends_in = {"kind": "lake", "id": int(lake_id[er, ec])}
    elif river[er, ec]:
        ends_in = {"kind": "river", "id": int(river_owner[river_tree.query([ec, er])[1]])}
    else:
        ends_in = {"kind": "sea"}
    end_at = (float(ec), float(er))
    if ends_in["kind"] == "sea":                    # on to the land's edge, half a pixel on
        out = [(rr, cc) for rr, cc in ((er - 1, ec), (er + 1, ec), (er, ec - 1), (er, ec + 1)) if 0 <= rr < h and 0 <= cc < w and sea[rr, cc]]
        if out:
            end_at = (ec + 0.5 * (out[0][1] - ec), er + 0.5 * (out[0][0] - er))
    line = drawn_line(cells, (p["x"], p["y"]), end_at, wet_ground.passable, np.zeros((h, w), dtype=bool))
    km = length_px(line) * KM
    if km > CHANNEL_MOST:
        continue
    lc = cells_of(line)
    record = {"id": len(channels) + 1, "village": p["id"], "ends_in": ends_in, "km": round(km, 2), "points": rounded_points(line[::2] if len(line) > 4 else line)}
    record["points"][-1] = rounded_points([line[-1]])[0]
    channel_of[lc[:, 0], lc[:, 1]] = np.where(channel_of[lc[:, 0], lc[:, 1]] == 0, record["id"], channel_of[lc[:, 0], lc[:, 1]])
    channels.append(record)
    p["link"] = {"kind": "channel", "id": record["id"]}
say("swamp villages: %d; on the water already %d, by a channel %d (%.0f km), left for a lane %d" % (
    len(swamp_villages), sum(p["link"] == {"kind": "water"} for p in swamp_villages), len(channels), sum(ch["km"] for ch in channels),
    sum(p["link"] is None for p in swamp_villages)))

# == 5. lanes ==============================================================================================
# The channels are crossed as small rivers are, on a bridge.
channel = channel_of > 0
lane_river = river | channel
lane_crossing = np.where(channel & ~river, 3.0, crossing).astype(np.float32)
lane_going = np.where(channel & ~river, 6.0, going).astype(np.float32)
lane_ground = ground_of(passable=passable, going=lane_going, height=smooth, river=lane_river, crossing=lane_crossing)
network = road | dots
whose = np.zeros((h, w), dtype=np.int32)                # which lane (its village's id) a pixel of a lane is on, or which village a village's pixel is
lanes = []
lane_lines = {}
for p in village_list:
    if p["link"] is not None and p["link"]["kind"] == "road":
        r, c = int(round(p["y"])), int(round(p["x"]))
        network[max(r - 1, 0): r + 2, max(c - 1, 0): c + 2] = True
        whose[max(r - 1, 0): r + 2, max(c - 1, 0): c + 2] = -p["id"]
waiting = [p for p in village_list if p["link"] is None]
waiting.sort(key=lambda p: d_road[int(round(p["y"])), int(round(p["x"]))])
unreached = []
for n, p in enumerate(waiting):
    r, c = int(round(p["y"])), int(round(p["x"]))
    found = route_to_any(lane_ground, (c, r), network, int(max(40, 1.5 * d_road[r, c] / KM + 20)), 300)
    if found is None:
        unreached.append(p)
        continue
    cost, cells, (er, ec) = found
    if len(cells) < 2:                               # a lane laid before runs through it
        p["link"] = {"kind": "on_lane", "village": int(whose[er, ec])}
        network[max(r - 1, 0): r + 2, max(c - 1, 0): c + 2] = True
        continue
    # What it reaches, and the point on that where the lane ends.
    if road[er, ec]:
        off, i = road_tree.query([ec, er])
        joins = {"kind": "road", "stretch": int(road_owner[i])}
        end_at = (float(road_points[i][0]), float(road_points[i][1]))
    elif dots[er, ec]:
        s = next(s for s in settlements if s["county"] == town[er, ec])
        joins = {"kind": "settlement", "county": s["county"]}
        end_at = (float(s["x"]), float(s["y"]))
        cells = cells + [(s["y"], s["x"])]
    elif whose[er, ec] < 0:
        other = next(q for q in village_list if q["id"] == -int(whose[er, ec]))
        joins = {"kind": "village", "id": other["id"]}
        end_at = (other["x"], other["y"])
    else:
        other = lane_lines[int(whose[er, ec])]
        near = other[np.argmin(np.hypot(other[:, 0] - ec, other[:, 1] - er))]
        joins = {"kind": "lane", "village": int(whose[er, ec])}
        end_at = (float(near[0]), float(near[1]))
    line = drawn_line(cells, (p["x"], p["y"]), end_at, passable | dots, lane_river)
    lc = cells_of(line)
    # Bridges: where the lane lies on a river or a channel, and a little on to each bank.
    wet = lane_river[lc[:, 0], lc[:, 1]]
    bridges = []
    on_line = np.round(line[:, ::-1]).astype(np.int64)
    wet_points = lane_river[on_line[:, 0], on_line[:, 1]]
    for a, b in runs_of(wet_points):
        a2, b2 = max(a - int(ON_BANK / 0.5), 0), min(b + int(ON_BANK / 0.5), len(line)) - 1
        middle = line[(a + b - 1) // 2]
        over_river = river[int(round(middle[1])), int(round(middle[0]))]
        bridge = {"over": "river" if over_river else "channel", "from": rounded_points([line[a2]])[0], "to": rounded_points([line[b2]])[0]}
        if over_river:
            k = river_tree.query(middle)[1]
            bridge["river"] = int(river_owner[k])
            bridge["river_m3s"] = round(float(river_flow[k]), 1)
        else:
            mr, mc = int(round(middle[1])), int(round(middle[0]))
            bridge["channel"] = int(channel_of[max(mr - 1, 0): mr + 2, max(mc - 1, 0): mc + 2].max())
        bridges.append(bridge)
    km = length_px(line) * KM
    lane = {"id": len(lanes) + 1, "village": p["id"], "joins": joins, "km": round(km, 2), "bridges": bridges,
            "points": rounded_points(line[::2] if len(line) > 4 else line)}
    lane["points"][-1] = rounded_points([line[-1]])[0]
    lanes.append(lane)
    lane_lines[p["id"]] = line
    p["link"] = {"kind": "lane", "id": lane["id"]}
    network[lc[:, 0], lc[:, 1]] = True
    whose[lc[:, 0], lc[:, 1]] = np.where(whose[lc[:, 0], lc[:, 1]] == 0, p["id"], whose[lc[:, 0], lc[:, 1]])
    network[max(r - 1, 0): r + 2, max(c - 1, 0): c + 2] = True
    whose[max(r - 1, 0): r + 2, max(c - 1, 0): c + 2] = -p["id"]
    if (n + 1) % 100 == 0:
        say("lanes laid: %d of %d" % (n + 1, len(waiting)))
for p in unreached:
    p["link"] = {"kind": "none"}
say("lanes: %d, %.0f km, %d bridges; villages no lane could reach: %d" % (len(lanes), sum(l["km"] for l in lanes), sum(len(l["bridges"]) for l in lanes), len(unreached)))

# == the file ==============================================================================================
for p in places:
    p["x"], p["y"] = round(p["x"], 2), round(p["y"], 2)
    p.pop("score", None)
out = {
    "about": "The villages and hamlets, and the lanes and channels that join the villages to the roads and the rivers, made by "
             "MapCreation/Scripts/villages/v1_villages.py. Coordinates are the pictures' pixels, a whole number being the middle of a pixel.",
    "fields": {
        "places": "id; kind (village or hamlet); name (as the scene names its node); county, duchy, kingdom; terrain (TerrainMap.png's kind of "
                  "country there); x, y; height_m; from_capital_km (from its county's capital); link: how a village is joined to the "
                  "network: {kind: road, stretch} on a road (Roads.json's stretch), {kind: lane, id}, {kind: channel, id}, {kind: water} on a "
                  "river, lake or the sea, {kind: none}; null for a hamlet",
        "lanes": "id; village (its place's id); joins: what its last point lies on: {kind: road, stretch}, {kind: lane, village} (the "
                 "lane of that village), {kind: village, id}, {kind: settlement, county}; km; bridges: where it crosses a river (river, "
                 "river_m3s) or a channel (channel), from and to being the ends of the bridge, 2 px on to each bank; points: the line from "
                 "the village to where it joins, about a pixel apart",
        "channels": "id; village; ends_in: {kind: river, id}, {kind: lake, id}, {kind: sea} or {kind: channel, id}; km; points: the line "
                    "from the village to the water, about a pixel apart, the last point in the water (or on the land's edge, for the sea)",
    },
    "rules": {"total": TOTAL, "supports": SUPPORTS, "village_share": VILLAGE_SHARE, "apart_km": {"%s-%s" % k: v for k, v in APART.items()},
              "on_road_km": ON_ROAD, "at_water_km": AT_WATER, "seed": SEED},
    "places": places,
    "lanes": lanes,
    "channels": channels,
}
with open(WRITE_TO, "w", encoding="utf-8", newline="\n") as handle:
    handle.write("{\n")
    head = list(out.items())
    for i, (key, value) in enumerate(head):
        last = i == len(head) - 1
        if isinstance(value, list):
            handle.write(' "%s": [\n' % key)
            for j, row in enumerate(value):
                handle.write("  " + json.dumps(row, separators=(", ", ": ")) + (",\n" if j < len(value) - 1 else "\n"))
            handle.write(" ]" + ("\n" if last else ",\n"))
        else:
            handle.write(' "%s": %s%s' % (key, json.dumps(value, separators=(", ", ": ")), "\n" if last else ",\n"))
    handle.write("}\n")
say("wrote", WRITE_TO)

# == figures ===============================================================================================
vill = [p for p in places if p["kind"] == "village"]
ham = [p for p in places if p["kind"] == "hamlet"]
for k in sorted(quota):
    vk, hk = [p for p in vill if p["kingdom"] == k], [p for p in ham if p["kingdom"] == k]
    links = defaultdict(int)
    for p in vk:
        links[p["link"]["kind"]] += 1
    say("kingdom %d: %d villages (%s), %d hamlets; median height %.0f m; lanes %.0f km" % (
        k, len(vk), ", ".join("%s %d" % kv for kv in sorted(links.items())), len(hk), np.median([p["height_m"] for p in vk + hk]),
        sum(l["km"] for l in lanes if next(q for q in vill if q["id"] == l["village"])["kingdom"] == k)))
per_county = defaultdict(int)
for p in places:
    per_county[p["county"]] += 1
counts = np.array([per_county[c] for c in range(1, 221)])
say("places a county: least %d, median %.0f, most %d; counties with none: %d" % (counts.min(), np.median(counts), counts.max(), (counts == 0).sum()))
xy = np.array([[p["x"], p["y"]] for p in places])
gap = cKDTree(xy).query(xy, k=2)[0][:, 1] * KM
say("nearest neighbour among villages and hamlets: least %.1f km, median %.1f" % (gap.min(), np.median(gap)))

# == pictures to look at ====================================================================================
if LOOK:
    Path(LOOK).mkdir(parents=True, exist_ok=True)
    base = Image.open(MC + "/AllSimple.png").convert("RGB")
    draw = ImageDraw.Draw(base)
    for ch in channels:
        draw.line([tuple(q) for q in ch["points"]], fill=(28, 112, 224), width=2)
    for l in lanes:
        draw.line([tuple(q) for q in l["points"]], fill=(200, 40, 30), width=1)
        for b in l["bridges"]:
            draw.line([tuple(b["from"]), tuple(b["to"])], fill=(60, 35, 15), width=3)
    for p in places:
        r = 3.5 if p["kind"] == "village" else 2.2
        colour = (255, 170, 0) if p["kind"] == "village" else (0, 160, 60)
        draw.ellipse([p["x"] - r, p["y"] - r, p["x"] + r, p["y"] + r], fill=colour, outline=(0, 0, 0))
    base.save(LOOK + "/villages_full.png")
    base.resize((w // 2, h // 2), Image.LANCZOS).save(LOOK + "/villages_half.png")
    for name, (x, y) in {"k1": (981, 499), "k2": (1487, 835), "k3": (1600, 1950), "k4": (2031, 1515), "k5": (2600, 2150),
                         "k6": (500, 1550), "k7": (1150, 2450), "k8": (1900, 2850), "k9": (2450, 3400)}.items():
        base.crop((x - 350, y - 250, x + 350, y + 250)).save(LOOK + "/villages_%s.png" % name)
    say("pictures in", LOOK)
