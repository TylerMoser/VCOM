"""Forests for the map: where trees would stand on this island, each kingdom's country holding its
share, and where the people of its settlements have cleared them.

What was asked (2026-10-17): realistic forests for the whole map, scaled to each biome and fitting
the terrain. The user chose "wild" forests (about half the land; little cleared, and that round the
settlements the map shows) at these shares of each kingdom's land, its lakes left out (TARGET):
Tropical Rainforest 92%, Evergreen Temperate Rainforest 88%, Deciduous Forest 80%, Swamp and
Temperate Mountains 60%, Volcanic Mountains 30%, Tundra Mountains 20%, Grassland 9%, Desert 1.5%.

1. What would grow with nobody here, every pixel from 0 to 1 (`grows`): under the tree line, which
   is lower in the cold north and on a north face, and higher along water; in the dry country only
   by water (rivers, lakes, the streams of the drainage) or high enough up the mountains to catch
   the rain; in the cold country in the valleys rather than on the tops; nothing on cliffs, on a
   coast the wind keeps bare, on the floors of the great rivers' valleys (wet meadow), in the
   swamp's open marsh (round its great lakes, along its shore, in its wettest ground away from the
   rivers), on the volcanoes' cones and their young lava.
2. What people cleared (`cleared`): round every settlement, by its rank (RADIUS), as far as a cost
   of going reaches: cheap over flat valley floors near water and along the roads, dear up steep
   sides, so that a clearing runs along its valley and its road and stops at the hills. A kingdom
   where that would clear more than OPEN_BY_PEOPLE of the land its share leaves open clears less.
3. Each kingdom's share: of what people left, the land where `grows` (with an unevenness the map
   does not show: soil, fire, wind) is greatest, to the share's amount, the kingdoms' rules blended
   over a few km either side of their borders.
4. As outlines: the edges of that, smoothed, traced finer than a pixel; woods under MIN_FOREST
   dropped and clearings under MIN_CLEARING filled; points left out where the outline moves less
   than TOLERANCE without them. A forest runs on over the lakes as over its land (the lakes are
   drawn over it), and SEA_REACH px out over the sea, to be cut at the coast by the counties'
   own outlines when the scene is made (../scene/forestshapes.py).
5. Kinds, for their colours: where the land rises over CONIFER_ABOVE a kingdom's broadleaf forest
   gives way to conifers, and the swamp's own low country holds swamp forest. These are given as
   regions, for the scene to cut its pieces by, county by county.

Everything random comes from SEED, so the same files give the same forests. The pictures to look
at, if a folder is given for them, are the whole map at half size and close views at full size.

Usage: f1_forests.py <MapCreation dir> <Forests.json to write> [<folder for pictures to look at>]
"""
import json
import sys
import time
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import measure
from skimage.graph import MCP_Geometric
import shapely
from shapely.geometry import Polygon
from shapely.strtree import STRtree

Image.MAX_IMAGE_PIXELS = None
MC, WRITE_TO = sys.argv[1:3]
LOOK = sys.argv[3] if len(sys.argv) > 3 else None
SRC = MC + "/SourceData"
KM = 0.335
PX_KM2 = KM * KM
SEED = 20261018

# -- each kingdom's share, of its land with its lakes left out ------------------------------------------
TARGET = {1: 0.20, 2: 0.30, 3: 0.60, 4: 0.015, 5: 0.09, 6: 0.88, 7: 0.60, 8: 0.80, 9: 0.92}

# -- what would grow, by kingdom (each kingdom is a biome): blended over SPREAD km either side of a border --
SPREAD = 4.0
# The tree line (m), and how far it moves for a slope's facing: a south face holds trees higher.
TREELINE = {1: 560.0, 2: 1100.0, 3: 1700.0, 4: 1900.0, 5: 1900.0, 6: 1500.0, 7: 1700.0, 8: 1750.0, 9: 3500.0}
TREELINE_BAND = 300.0
FACING_M = {1: 120.0, 2: 100.0, 3: 120.0, 4: 150.0, 5: 150.0, 6: 60.0, 7: 60.0, 8: 80.0, 9: 50.0}
# The dry country, where trees grow only by water or above LOW (m), where the mountains catch the rain;
# a north face is moister, and holds them NORTH_LOWER m lower.
DRY = {4: 1.0, 5: 1.0}
LOW = {4: 1150.0, 5: 700.0}
NORTH_LOWER = 200.0
# How much a bank helps a tree, by kingdom: much in the dry and the cold country, little where trees
# grow everywhere anyway.
RIPARIAN = {1: 0.9, 2: 0.7, 3: 0.3, 4: 1.0, 5: 1.0, 6: 0.15, 7: 0.3, 8: 0.2, 9: 0.1}
# km of coast the wind and salt keep bare.
EXPOSED_KM = {1: 5.0, 2: 3.0, 3: 0.0, 4: 1.5, 5: 1.0, 6: 0.4, 7: 0.0, 8: 0.6, 9: 0.0}
# How much of the flat floor of a great river's valley is wet meadow rather than wood.
FLOODPLAIN = {1: 0.0, 2: 0.0, 3: 0.5, 4: 0.0, 5: 0.0, 6: 0.55, 7: 0.0, 8: 0.6, 9: 0.45}
# Where the forest keeps to the valleys, the tops being bare: what a place high on its valley's side loses.
VALLEYS = {1: 0.45, 2: 0.6}
# High bare ridges below the tree line (windswept tops, rock, the high pastures' upper edge).
RIDGES = {3: 0.7, 8: 0.35}
# How uneven the forest is for reasons the map does not show (soil, fire, wind, grazing): the weight
# of a broad and a middling unevenness in a place's score.
PATCHY = {1: 0.6, 2: 0.6, 3: 0.3, 4: 0.3, 5: 0.35, 6: 0.3, 7: 0.45, 8: 0.3, 9: 0.3}
# The swamp's own low country: TerrainMap.png's 7, under this height (m).
SWAMP_TERRAIN, SWAMP_BELOW = 7, 60.0
SALT_LAKE = 4                  # Lakes.json: the desert's salt lake keeps no trees by it
# The volcanoes of kingdom 2 (Features.md): x, y, height of the top (m). Bare round each to
# (CONE_KM + top / CONE_PER_KM) km, and young lava in patches further out.
CONES = [(1320, 511, 2794), (1387, 697, 2744), (1553, 1242, 2543), (1360, 324, 2347), (1556, 1066, 2242), (1652, 933, 2067),
         (1388, 976, 1994), (1521, 555, 1497)]
CONE_KM, CONE_PER_KM, LAVA_REACH = 3.0, 300.0, 2.8
VOLCANIC = 2

# -- what people cleared ---------------------------------------------------------------------------------
# km a settlement's people clear round it, on good flat ground: farther along a flat valley floor or a
# road, less up a slope (a cost of going).
RADIUS = {"kingdom": 6.0, "duchy": 5.0, "county": 4.0, "village": 2.4, "hamlet": 1.5}
# How far round a place each kingdom's people clear, against RADIUS. Lowered where it would clear more
# than OPEN_BY_PEOPLE of the land its share leaves open.
CLEARS = {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0, 5: 1.0, 6: 1.4, 7: 1.0, 8: 1.3, 9: 1.5}
OPEN_BY_PEOPLE = 0.8

# -- as outlines ---------------------------------------------------------------------------------------------
MIN_FOREST = 0.5               # km2: a smaller wood is dropped
MIN_CLEARING = 0.8             # km2: a smaller clearing is filled
TOLERANCE = 0.15               # px a simplified outline may leave the traced one (50 m)
SMOOTHING = 0.7                # px: the field is smoothed this much before it is traced
SEA_REACH = 4.0                # px a forest runs on over the sea, to be cut at the coast in the scene

# -- kinds -------------------------------------------------------------------------------------------------
BASE_KIND = {1: "conifer", 2: "conifer", 3: "broadleaf", 4: "broadleaf", 5: "broadleaf", 6: "conifer", 7: "swamp", 8: "broadleaf", 9: "tropical"}
CONIFER_ABOVE = {3: 1000.0, 4: 900.0, 5: 900.0, 7: 600.0, 8: 1100.0}
KIND_SMOOTHING = 3.0           # px: heights are smoothed this much before a region is traced from them

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


def ramp(x, at, band):
    """0 well below [at], 1 well above, a smooth step about [band] wide."""
    return (1.0 / (1.0 + np.exp(np.clip(-(x - at) / (band / 4.0), -60.0, 60.0)))).astype(np.float32)


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
lakes_table = {l["id"]: l for l in load("Lakes.json")["lakes"]}
surface = np.zeros(max(lakes_table) + 1, dtype=np.float32)
for i, l in lakes_table.items():
    surface[i] = l["surface_m"]
raw_height = np.asarray(Image.open(MC + "/Elevation.png")).astype(np.float32) / 10.0
height = np.where(land, filled(raw_height, raw_height > 0), 0.0).astype(np.float32)
height = np.where(lake, surface[lake_id], height)           # a lake's surface, not its bed
flow = np.repeat(np.repeat(number_map(SRC + "/DrainageFlow.png") / 32.0, 2, axis=0), 2, axis=1)[:h, :w].astype(np.float32)
counted = land & ~lake                                       # a kingdom's share is of this
say("map read: %d x %d, %d px of land" % (w, h, land.sum()))

# Smoothed inside the land, as the roads read it.
weight = ndimage.gaussian_filter(land.astype(np.float32), 1.5)
smooth = ndimage.gaussian_filter(np.where(land, height, 0.0), 1.5) / np.maximum(weight, 1e-3)
smooth = np.where(land, smooth, 0.0).astype(np.float32)
gy, gx = np.gradient(smooth)
slope = (np.hypot(gy, gx) / (KM * 1000.0)).astype(np.float32)
# Which way the ground faces, on a broader smoothing: +1 north, -1 south (y runs south), nothing where flat.
broad = ndimage.gaussian_filter(np.where(land, height, 0.0), 3.0) / np.maximum(ndimage.gaussian_filter(land.astype(np.float32), 3.0), 1e-3)
by, bx = np.gradient(broad)
steep = np.hypot(by, bx) / (KM * 1000.0)
north = np.where(steep > 0.005, by / np.maximum(np.hypot(by, bx), 1e-6), 0.0).astype(np.float32)
north *= np.clip(steep / 0.05, 0.0, 1.0).astype(np.float32)
del gy, gx, broad, by, bx, steep

# == water =================================================================================================
fresh = lake & (lake_id != SALT_LAKE)
d_river = km_from(river)
d_lake = km_from(fresh)
d_creek = km_from((flow >= 4.0) & land & ~lake)
d_brook = km_from((flow >= 1.0) & land & ~lake)
d_rill = km_from((flow >= 0.2) & land & ~lake)
d_sea = (ndimage.distance_transform_edt(land) * KM).astype(np.float32)
d_big_lake = km_from(np.isin(lake_id, [l["id"] for l in lakes_table.values() if l["km2"] >= 40.0]))
# How big the nearest river is: the drainage's flow along it, carried out to every pixel nearest it.
river_flow = np.where(river, np.maximum(ndimage.maximum_filter(flow, size=5), 15.0), 0.0).astype(np.float32)
nearest = ndimage.distance_transform_edt(~river, return_distances=False, return_indices=True)
near_river_flow = river_flow[nearest[0], nearest[1]]
del nearest, river_flow
say("water measured")

# == each kingdom's rules, blended over its border ==========================================================
share = np.zeros((10, h, w), dtype=np.float32)
landf = ndimage.gaussian_filter(land.astype(np.float32), SPREAD / KM)
for k in range(1, 10):
    share[k] = ndimage.gaussian_filter((kingdom == k).astype(np.float32), SPREAD / KM) / np.maximum(landf, 1e-3)
share[:, ~land] = 0.0
del landf


def blend(values):
    out = np.zeros((h, w), dtype=np.float32)
    for k, v in values.items():
        out += share[k] * v
    return out


rng = np.random.default_rng(SEED)


def noise(sigma):
    n = ndimage.gaussian_filter(rng.standard_normal((h, w)).astype(np.float32), sigma)
    return (n / n.std()).astype(np.float32)


n_broad = noise(14.0)
n_mid = noise(5.0)
n_fine = noise(1.3)
# The middling unevenness pushed about by a broad one, so that what it shapes is drawn out and bent
# rather than round.
push_x, push_y = noise(9.0) * 7.0, noise(9.0) * 7.0
rows, cols = np.mgrid[0:h, 0:w].astype(np.float32)
warped = ndimage.map_coordinates(n_mid, [rows + push_y, cols + push_x], order=1, mode="reflect").astype(np.float32)
del push_x, push_y, rows, cols

reach = int(round(5.0 / KM)) * 2 + 1
low_round = ndimage.minimum_filter(np.where(land, smooth, 0.0), size=reach)
top_round = ndimage.maximum_filter(np.where(land, smooth, 0.0), size=reach)
up_side = np.clip((smooth - low_round) / (top_round - low_round + 40.0), 0.0, 1.0).astype(np.float32)   # how far up its valley's side
del low_round, top_round
flat = np.exp(-(slope / 0.06) ** 2).astype(np.float32)

# == 1. what would grow ======================================================================================
dry = blend(DRY)
riparian = blend(RIPARIAN)
# A bank: a river (wider for a greater one), a lake, a stream of the drainage. In the dry country a
# rill is dry most of the year and keeps no trees.
river_reach = 0.6 + 0.9 * np.clip(np.log10(np.maximum(near_river_flow, 15.0) / 15.0) / 2.0, 0.0, 1.0)
bank = np.maximum.reduce([fall(d_river, river_reach), 0.85 * fall(d_lake, 0.8), 0.7 * fall(d_creek, 0.6), 0.55 * fall(d_brook, 0.45),
                          0.35 * fall(d_rill, 0.3) * (1.0 - dry)])
treeline = blend(TREELINE) - blend(FACING_M) * north + 150.0 * bank * riparian
grows = ramp(treeline - height, 0.0, TREELINE_BAND)
wet_enough = np.maximum(bank * riparian, 0.8 * ramp(height, blend(LOW) - NORTH_LOWER * north, 300.0))
grows *= (1.0 - dry) + dry * wet_enough
grows *= 1.0 - blend(VALLEYS) * up_side * (1.0 - bank)
grows *= 1.0 - blend(RIDGES) * ramp(up_side, 0.7, 0.3) * ramp(height, 1100.0, 400.0)
exposed = blend(EXPOSED_KM)
grows *= 1.0 - (exposed > 0) * fall(d_sea, np.maximum(exposed, 1e-3)) * 0.85
grows *= 1.0 - 0.85 * ramp(slope, 0.42, 0.2)
big_river = np.clip(np.log10(np.maximum(near_river_flow, 15.0) / 40.0) / 1.5, 0.0, 1.0)
plain = fall(d_river, 0.5 + 1.5 * big_river) * flat * (1.0 - up_side) * np.maximum(big_river, 0.4 * share[3])
grows *= 1.0 - blend(FLOODPLAIN) * plain
del near_river_flow, big_river, plain, exposed

# The swamp: open marsh round its great shallow lakes, along its shore, and in its wettest ground
# away from the rivers; swamp forest on what stands a little above that.
swamp_country = (terrain == SWAMP_TERRAIN) & (height < SWAMP_BELOW)
reach = int(round(3.0 / KM)) * 2 + 1
round_about = ndimage.uniform_filter(np.where(land, smooth, 0.0), size=reach) / np.maximum(ndimage.uniform_filter(land.astype(np.float32), size=reach), 1e-3)
raised = (smooth - round_about).astype(np.float32)
marsh = np.maximum.reduce([0.95 * fall(d_big_lake, 2.4), 0.95 * fall(d_sea, 3.0), 0.8 * ramp(-raised, 0.3, 1.5) * (1.0 - fall(d_river, 1.5))])
grows *= 1.0 - ndimage.gaussian_filter(swamp_country.astype(np.float32), 2.0) * marsh
del round_about, raised, marsh

# The volcanoes: their cones bare, and the young lava round them in patches.
bare = np.zeros((h, w), dtype=np.float32)
for x, y, top in CONES:
    r = (CONE_KM + top / CONE_PER_KM) / KM
    box = (slice(max(int(y - 4 * LAVA_REACH * r), 0), int(y + 4 * LAVA_REACH * r)), slice(max(int(x - 4 * LAVA_REACH * r), 0), int(x + 4 * LAVA_REACH * r)))
    yy, xx = np.ogrid[box]
    d = np.hypot(xx - x, yy - y)
    cone = np.exp(-(d / r) ** 2)
    lava = 0.9 * np.exp(-(d / (LAVA_REACH * r)) ** 2) * ramp(n_mid[box], 0.3, 0.8)
    bare[box] = np.maximum(bare[box], np.maximum(cone, lava))
grows *= 1.0 - 0.95 * bare * share[VOLCANIC]
del bare
grows = np.clip(grows, 0.0, 1.0)
grows[~land] = 0.0
say("what would grow worked out")

# == 2. what people cleared ===================================================================================
settlements = load("Settlements.json")["settlements"]
villages = load("Villages.json")["places"]
road = np.zeros((h, w), dtype=bool)
for stretch in load("Roads.json")["stretches"]:
    p = np.asarray(stretch["points"], dtype=np.float64)
    road[np.round(p[:, 1]).astype(int), np.round(p[:, 0]).astype(int)] = True
d_road = km_from(road)
# Cheap going for a clearing: a flat floor low in its valley, near water, and a road.
wet = np.maximum.reduce([fall(d_river, 1.6), fall(d_lake, 1.2), fall(d_creek, 1.0), 0.8 * fall(d_brook, 0.8), 0.5 * fall(d_rill, 0.6)])
floor = np.exp(-(slope / 0.08) ** 2).astype(np.float32) * (1.0 - up_side) ** 1.5
ease = (0.25 + 1.6 * floor * (0.3 + 0.7 * wet) + 1.0 * fall(d_road, 0.45)) * np.exp(0.45 * warped + 0.15 * n_fine)
going = np.where(counted, KM / ease, 1e6).astype(np.float64)
del wet, floor, ease, d_road
places = [(s["rank"], s["x"], s["y"]) for s in settlements] + [(p["kind"], p["x"], p["y"]) for p in villages]
reached = {}
for rank in RADIUS:
    starts = [(int(round(y)), int(round(x))) for r, x, y in places if r == rank]
    costs, _ = MCP_Geometric(going, fully_connected=True).find_costs(starts)
    reached[rank] = np.minimum(costs, 1e3).astype(np.float32)
    say("the clearings round %d %s%s worked out" % (len(starts), rank, "s" if rank in ("village", "hamlet") else " capitals"))
del going


def cleared_by(clears):
    c = np.zeros((h, w), dtype=np.float32)
    for rank in RADIUS:
        c = np.maximum(c, ramp(RADIUS[rank] * clears - reached[rank], 0.0, 0.6))
    return c


clears = dict(CLEARS)
for _ in range(12):
    cleared = cleared_by(blend(clears))
    changed = False
    for k in TARGET:
        mine = (kingdom == k) & counted
        got = (cleared[mine] > 0.5).mean()
        most = OPEN_BY_PEOPLE * (1.0 - TARGET[k])
        if got > most * 1.02:
            clears[k] *= (most / got) ** 0.6
            changed = True
    if not changed:
        break
cleared = cleared_by(blend(clears))
open_land = cleared > 0.5
del reached
say("clearings, against RADIUS, by kingdom: %s" % ", ".join("%d: %.2f" % (k, v) for k, v in sorted(clears.items())))

# == 3. each kingdom's share ==================================================================================
patchy = (0.5 * n_broad + 0.75 * warped) / np.hypot(0.5, 0.75)
score = np.log(np.maximum(grows, 1e-4)) + blend(PATCHY) * patchy + 0.12 * n_fine
score[~land] = -50.0
offsets = {k: -0.7 for k in TARGET}
for rounds in range(1, 41):
    t = blend(offsets)
    forest = (score > t) & ~open_land & counted
    worst = 0.0
    for k in TARGET:
        mine = (kingdom == k) & counted
        free = mine & ~open_land
        worst = max(worst, abs(forest[mine].mean() - TARGET[k]))
        # The score that would give the share among what people left, the other kingdoms as they are.
        wanted = TARGET[k] * mine.sum() / max(free.sum(), 1)
        offsets[k] = float(0.5 * offsets[k] + 0.5 * np.quantile((score - t + offsets[k])[free], float(np.clip(1.0 - wanted, 0.0, 1.0))))
    if worst < 0.002:
        break
t = blend(offsets)
forest = (score > t) & ~open_land & land
figures = {}
for k in TARGET:
    mine = (kingdom == k) & counted
    figures[k] = {"target": TARGET[k], "share": round(float(forest[mine].mean()), 4), "km2": round(float(forest[mine].sum() * PX_KM2), 0),
                  "cleared": round(float(open_land[mine].mean()), 4), "would_not_grow": round(float(((grows[mine] < 0.5) & ~open_land[mine]).mean()), 4)}
    say("kingdom %d: %.1f%% forest (wanted %.1f%%); cleared %.1f%%, where nothing would grow %.1f%%" % (
        k, 100 * figures[k]["share"], 100 * TARGET[k], 100 * figures[k]["cleared"], 100 * figures[k]["would_not_grow"]))
say("in %d rounds: %.1f%% of the land, its lakes left out" % (rounds, 100 * forest[counted].mean()))

# == 4. as outlines ===========================================================================================
# The forest's own field, a forest where it is over 0: what the share left, and less where people cleared.
field = np.minimum(score - t, 4.0 * (0.5 - cleared))
del score, t, cleared, grows, patchy, n_broad, n_mid, n_fine, warped
# Over the sea near the land, the value of the nearest land, so that a forest runs on past the coast and
# is cut at the coast's own line by the scene; under a lake, the value of its nearest shore.
off, index = ndimage.distance_transform_edt(~land, return_distances=True, return_indices=True)
field = np.where(off <= SEA_REACH, field[index[0], index[1]], -10.0)
water = lake & land
index = ndimage.distance_transform_edt(water, return_distances=False, return_indices=True)
field = np.where(water, field[index[0], index[1]], field)
del off, index, water
field = ndimage.gaussian_filter(field, SMOOTHING).astype(np.float32)


def traced(values, level):
    """The outlines where [values] crosses [level], in the pictures' pixels (a whole number the middle of a
    pixel): (outlines round what is over it, outlines round what is under it inside those)."""
    padded = np.pad(values, 1, constant_values=min(float(values.min()), level) - 1.0)
    outer, inner = [], []
    for r in measure.find_contours(padded, level, fully_connected="low", positive_orientation="high"):
        if len(r) < 4:
            continue
        xy = np.stack([r[:, 1] - 1.0, r[:, 0] - 1.0], axis=1)
        x, y = xy[:, 0], xy[:, 1]
        twice = float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
        (outer if twice < 0 else inner).append(Polygon(xy))
    return outer, inner


def nested(outer, inner, least_outline, least_hole):
    """Each outline with the holes inside it, as polygons. A hole is the smallest outline's that holds a
    point of its own edge (its middle may lie in a wood inside it). Outlines under [least_outline] px2 are
    dropped, holes under [least_hole] filled, and with a hole filled any outline inside it goes too."""
    tree = STRtree(outer)
    holes_of = [[] for _ in outer]
    inside_of = {}
    for hole in inner:
        edge = shapely.Point(hole.exterior.coords[0])
        holders = [j for j in tree.query(edge, predicate="within") if outer[j].area > hole.area]
        if holders:
            holes_of[min(holders, key=lambda j: outer[j].area)].append(hole)
    filled_holes = [hole for hs in holes_of for hole in hs if hole.area < least_hole]
    gone = set()
    if filled_holes:
        holes_tree = STRtree(filled_holes)
        for i, o in enumerate(outer):
            if len(holes_tree.query(shapely.Point(o.exterior.coords[0]), predicate="within")):
                gone.add(i)
    shapes = []
    for i, (o, hs) in enumerate(zip(outer, holes_of)):
        if i in gone or o.area < least_outline:
            continue
        p = Polygon(o.exterior.coords, [hole.exterior.coords for hole in hs if hole.area >= least_hole])
        if not p.is_valid:
            p = shapely.make_valid(p)
        for piece in getattr(p, "geoms", [p]):
            if piece.geom_type == "Polygon" and piece.area >= least_outline:
                shapes.append(piece)
    return shapes, len(gone)


outer, inner = traced(field, 0.0)
shapes, inside_filled = nested(outer, inner, MIN_FOREST / PX_KM2, MIN_CLEARING / PX_KM2)
traced_points = sum(len(p.exterior.coords) + sum(len(r.coords) for r in p.interiors) for p in shapes)
shapes = [p.simplify(TOLERANCE, preserve_topology=True) for p in shapes]
shapes = [p for p in shapes if p.geom_type == "Polygon" and not p.is_empty]
say("forests: %d (%d traced rings; woods under %.1f km2 and %d inside a filled clearing dropped; clearings under %.1f km2 filled); %d points, %d before simplifying within %.2f px" % (
    len(shapes), len(outer) + len(inner), MIN_FOREST, inside_filled, MIN_CLEARING,
    sum(len(p.exterior.coords) - 1 + sum(len(r.coords) - 1 for r in p.interiors) for p in shapes), traced_points, TOLERANCE))

# The land as the counties' map has it, to give each forest's area on land (the scene cuts it at the
# coast's own line, which is within a pixel of this).
land_outer, land_inner = traced(ndimage.gaussian_filter(land.astype(np.float32), 0.5), 0.5)
land_shape = shapely.make_valid(shapely.union_all([p.buffer(0) for p in land_outer]).difference(shapely.union_all([p.buffer(0) for p in land_inner])))
shapes.sort(key=lambda p: -p.area)
records = []
for i, p in enumerate(shapes, start=1):
    on_land = p.intersection(land_shape).area * PX_KM2
    ys, xs = np.asarray(p.exterior.coords)[:, 1], np.asarray(p.exterior.coords)[:, 0]
    records.append({"id": i, "km2": round(on_land, 2), "clearings": len(p.interiors),
                    "outline": [[round(float(x), 2), round(float(y), 2)] for x, y in p.exterior.coords[:-1]],
                    "holes": [[[round(float(x), 2), round(float(y), 2)] for x, y in r.coords[:-1]] for r in p.interiors]})
sizes = np.array([r["km2"] for r in records])
say("by size: 250 km2 or more %d, 50 to 250 %d, 10 to 50 %d, under 10 %d; the largest %.0f km2; %.0f km2 in all" % (
    (sizes >= 250).sum(), ((sizes >= 50) & (sizes < 250)).sum(), ((sizes >= 10) & (sizes < 50)).sum(), (sizes < 10).sum(), sizes.max(), sizes.sum()))

# == 5. kinds ==================================================================================================
kind_height = ndimage.gaussian_filter(filled(raw_height, raw_height > 0), KIND_SMOOTHING).astype(np.float32)


def region(values, level):
    """Where [values] is over [level], as polygons with holes, in the pictures' pixels."""
    outer, inner = traced(values, level)
    shapes, _ = nested(outer, inner, 4.0, 4.0)
    return [p.simplify(0.3, preserve_topology=True) for p in shapes]


def written(polygons):
    return [{"outline": [[round(float(x), 2), round(float(y), 2)] for x, y in p.exterior.coords[:-1]],
             "holes": [[[round(float(x), 2), round(float(y), 2)] for x, y in r.coords[:-1]] for r in p.interiors]} for p in polygons]


regions = {}
for level in sorted(set(CONIFER_ABOVE.values())):
    regions["above_%d" % level] = written(region(kind_height, level))
swamp_ground = ndimage.gaussian_filter(((terrain == SWAMP_TERRAIN) & (kind_height < SWAMP_BELOW)).astype(np.float32), 2.0)
regions["swamp_country"] = written(region(swamp_ground, 0.5))
say("kinds' regions: %s" % ", ".join("%s %d" % (k, len(v)) for k, v in regions.items()))

# == the file ==================================================================================================
out = {
    "about": "The forests, made by MapCreation/Scripts/forests/f1_forests.py. Coordinates are the pictures' pixels, a whole number "
             "being the middle of a pixel. A forest runs on under the lakes, and up to %g px out over the sea: the scene cuts it at "
             "the coast's own line, county by county (../Scripts/scene/forestshapes.py)." % SEA_REACH,
    "fields": {
        "forests": "id (by size, the largest first); km2 (its area on land, the lakes in it counted); clearings (how many holes it has); "
                   "outline: its edge, all the way round; holes: the edges of the clearings in it",
        "kinds": "base: each kingdom's kind of forest; conifer_above_m: the height (m) over which a kingdom's forest is conifer instead; "
                 "swamp: in kingdom 7, the swamp country is swamp forest, the rest broadleaf (conifer over its height); regions: where "
                 "the land is over each height (above_600 ...), and the swamp country, as outlines with holes",
        "figures": "by kingdom: target and share of its land (lakes left out) under forest, its km2, and the shares cleared by people "
                   "and where nothing would grow, as worked out on the pixels",
    },
    "rules": {"target": TARGET, "treeline_m": TREELINE, "radius_km": RADIUS, "clears": {k: round(v, 3) for k, v in clears.items()},
              "min_forest_km2": MIN_FOREST, "min_clearing_km2": MIN_CLEARING, "tolerance_px": TOLERANCE, "seed": SEED},
    "kinds": {"base": BASE_KIND, "conifer_above_m": CONIFER_ABOVE, "swamp": {"kingdom": 7, "region": "swamp_country"}, "regions": regions},
    "figures": figures,
    "forests": records,
}
with open(WRITE_TO, "w", encoding="utf-8", newline="\n") as handle:
    handle.write("{\n")
    head = list(out.items())
    for i, (key, value) in enumerate(head):
        last = i == len(head) - 1
        if isinstance(value, list):
            handle.write(' "%s": [\n' % key)
            for j, row in enumerate(value):
                handle.write("  " + json.dumps(row, separators=(",", ":")) + (",\n" if j < len(value) - 1 else "\n"))
            handle.write(" ]" + ("\n" if last else ",\n"))
        else:
            handle.write(' "%s": %s%s' % (key, json.dumps(value, separators=(",", ":")), "\n" if last else ",\n"))
    handle.write("}\n")
say("wrote", WRITE_TO)

# == pictures to look at =======================================================================================
if LOOK:
    Path(LOOK).mkdir(parents=True, exist_ok=True)
    base = np.asarray(Image.open(MC + "/AllSimple.png").convert("RGB")).astype(np.float32)
    green = np.array([60, 150, 70], dtype=np.float32)
    look = np.where((field > 0)[..., None] & land[..., None], base * 0.45 + green * 0.55, base)
    for p in villages:
        x, y = int(round(p["x"])), int(round(p["y"]))
        r = 2 if p["kind"] == "village" else 1
        look[y - r: y + r + 1, x - r: x + r + 1] = (230, 140, 0) if p["kind"] == "village" else (150, 60, 160)
    Image.fromarray(look.astype(np.uint8)).resize((w // 2, h // 2), Image.LANCZOS).save(LOOK + "/forests_half.png")
    for name, (x, y) in {"k1": (981, 499), "k2": (1487, 835), "k3": (1600, 1950), "k4": (2031, 1515), "k5": (2600, 2150),
                         "k6": (500, 1550), "k7": (1150, 2450), "k8": (1900, 2850), "k9": (2450, 3400)}.items():
        Image.fromarray(look[y - 250: y + 250, x - 350: x + 350].astype(np.uint8)).save(LOOK + "/forests_%s.png" % name)
    say("pictures in", LOOK)
