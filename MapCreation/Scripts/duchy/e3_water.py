"""Source data, part 2: the water. The lakes, the rivers as lines with the water they carry, the
watersheds, the drainage they were all worked out from, and the lines of the land that are drawn
on no picture (ridges, spurs, brooks).

The rivers' lines are made again here exactly as the picture's were (the same smoothing, the same
wandering from the same seed), and the proof is that drawing them, from the very numbers written
to the file, gives the picture's river pixels back, every one.

Usage: e3_water.py <MapCreation dir> <scratch out dir> <folder to write to>
"""
import pickle
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from sourcefiles import save_json, save_grey, save_mask, save_number, kept, KM, KM2

Image.MAX_IMAGE_PIXELS = None
MAPS, OUT, TO = sys.argv[1:4]
FACTOR = 2
INTO_INK = 3
SEED = 20261008
EIGHT = np.ones((3, 3), dtype=bool)

base = np.asarray(Image.open(MAPS + "/WorldMapV1.png").convert("RGBA"))
h, w = base.shape[:2]
full = np.load(OUT + "/water/grid1.npz")
land = full["land"]
new_land = (np.asarray(Image.open(MAPS + "/Continent.png").convert("RGB")) == 255).all(axis=2)
with open(OUT + "/water/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
drawn = np.load(OUT + "/water/drawn2.npz")
kingdom_map = np.asarray(Image.open(TO + "/KingdomMap.png")).astype(np.int32)
_, (near_y, near_x) = ndimage.distance_transform_edt(kingdom_map == 0, return_indices=True)
kingdom_near = kingdom_map[near_y, near_x]                # the kingdom of the nearest land, for points at the shore
rng = np.random.default_rng(SEED)
allowed = ndimage.binary_dilation(land, structure=EIGHT, iterations=INTO_INK)
allowed &= land | (base[..., 2].astype(np.int32) - base[..., 0].astype(np.int32) < 40)
rows, cols = water["rows"], water["cols"]
flow, z, lake_flat = water["flow_flat"], water["z"], water["lake_flat"]
terrain = full["king"].astype(np.int32)
king_flat = np.load(OUT + "/water/grid2.npz")["king"][rows, cols]
gh, gw = water["flow"].shape


def centre(cell):
    """The middle of a half-size cell, in pixels of the map, as [x, y]."""
    return [float(cols[cell] * FACTOR + 0.5), float(rows[cell] * FACTOR + 0.5)]


# -- the kind of country the land was shaped as, and the sketch ------------------------------------------------
assert ((terrain > 0) == land).all() and terrain.max() == 9
save_grey(TO + "/TerrainMap.png", terrain)
other = (terrain != kingdom_map) & land & new_land
print("TerrainMap.png: the kind of country every pixel of land was shaped as; it is not the kingdom of KingdomMap.png on %d px of the land the two share (%.1f%%)" % (
    other.sum(), 100.0 * other.sum() / (land & new_land).sum()))
sketch = np.load(OUT + "/region_map.npy").astype(np.int32)
print("the sketch's regions: values %s; land without a region %d; a region off the land %d; not the kingdom of KingdomMap.png on %d px (%.1f%%)" % (
    np.unique(sketch).tolist(), (land & (sketch == 0)).sum(), (~land & (sketch > 0)).sum(), ((sketch != kingdom_map) & land & new_land).sum(),
    100.0 * ((sketch != kingdom_map) & land & new_land).sum() / (land & new_land).sum()))
save_grey(TO + "/SketchRegionMap.png", sketch)

# -- lakes ---------------------------------------------------------------------------------------------------
lakes = drawn["lakes"]
pools, count = ndimage.label(lakes, structure=EIGHT)
index = np.arange(1, count + 1)
sizes = ndimage.sum_labels(lakes, pools, index=index).astype(int)
middles = ndimage.center_of_mass(lakes, pools, index)
order = sorted(range(count), key=lambda i: (-sizes[i], middles[i][0], middles[i][1]))
renumber = np.zeros(count + 1, dtype=np.int32)
for new, i in enumerate(order, start=1):
    renumber[i + 1] = new
lake_map = renumber[pools]
coarse = np.repeat(np.repeat(water["lake"], FACTOR, axis=0), FACTOR, axis=1)[:h, :w].astype(np.int64)
by_id = {l["id"]: l for l in water["lakes"]}
both = (coarse > 0) & (lake_map > 0)
keys, shared = np.unique(coarse[both] * 1000 + lake_map[both], return_counts=True)
under = {}                                              # drawn lake -> [(px shared, working lake)]
shows = {}                                              # working lake -> (px shared, drawn lake)
for key, px in zip(keys.tolist(), shared.tolist()):
    working, shown = divmod(key, 1000)
    under.setdefault(shown, []).append((px, working))
    if px > shows.get(working, (0, 0))[0]:
        shows[working] = (px, shown)
deep = ndimage.distance_transform_edt(lakes)
boxes = ndimage.find_objects(lake_map)
table = []
for number, box in enumerate(boxes, start=1):
    mine = lake_map[box] == number
    px = int(mine.sum())
    ys, xs = np.nonzero(mine)
    inside = np.unravel_index(int(np.argmax(np.where(mine, deep[box], 0.0))), mine.shape)
    below = sorted(under[number], reverse=True)
    source = by_id[below[0][1]]
    realms = np.bincount(kingdom_map[box][mine], minlength=10)
    table.append({"id": number, "px": px, "km2": round(px * KM2, 1), "middle": [round(float(box[1].start + xs.mean()), 1), round(float(box[0].start + ys.mean()), 1)],
                  "point_inside": [int(box[1].start + inside[1]), int(box[0].start + inside[0])],
                  "box": [int(box[1].start), int(box[0].start), int(box[1].stop - 1), int(box[0].stop - 1)],
                  "kingdoms": {str(k): int(realms[k]) for k in range(1, 10) if realms[k]},
                  "kind": source["kind"], "surface_m": round(source["level"], 1), "has_outlet": not source["shut"],
                  "outlet": None if source["shut"] else centre(source["outlet"]),
                  "drainage_lakes": [working for shared_px, working in below if shared_px >= 4]})
kinds = {}
for entry in table:
    kinds[entry["kind"]] = kinds.get(entry["kind"], 0) + 1
shut = [(e["id"], e["kind"], e["km2"]) for e in table if not e["has_outlet"]]
print("lakes: %d drawn, %d px; by kind %s; without an outlet: %s; made of more than one of the drainage's lakes: %d; pixels of a lake in no kingdom: %d" % (
    count, lakes.sum(), kinds, shut, sum(1 for e in table if len(e["drainage_lakes"]) > 1), sum(e["px"] - sum(e["kingdoms"].values()) for e in table)))
save_number(TO + "/LakeMap.png", lake_map)
save_json(TO + "/Lakes.json", {
    "about": "The 700 lakes as drawn. LakeMap.png gives every pixel its lake's id (red + 256 x green; 0 where there is no lake). The lakes' shores are in no file as lines: they are the edges of LakeMap.png's patches.",
    "order": "Largest first: id 1 is the largest lake.",
    "fields": {"px, km2": "its size: pixels of LakeMap.png, and those times 0.112225", "middle": "[x, y], the average of its pixels, which for a crooked lake may lie outside it",
               "point_inside": "[x, y], a pixel that is in the lake: the one furthest from its shore", "box": "[x0, y0, x1, y1], the smallest box that holds it",
               "kingdoms": "how many of its pixels lie in each kingdom of KingdomMap.png (a border may run through a lake)",
               "kind": "what made it when the water was worked out: caldera, crater, salt, or where on a stream it lies (trunk: on a main river; stream; head: at a valley's head; foot: where a river leaves the mountains; high: a mountain tarn; low; any)",
               "surface_m": "the height of its surface above the sea. Elevation.png holds its bed, which is lower", "has_outlet": "false for the salt lake, which two rivers end in, and for the six crater lakes, which no stream enters or leaves",
               "outlet": "[x, y], the middle of the half-size cell where its water leaves it (Drainage.json)", "drainage_lakes": "the ids, in DrainageLakes.png and Drainage.json, of the lakes of the drainage that it is drawn from, the largest first"},
    "lakes": table})

# -- rivers: the lines, made as the picture's were -------------------------------------------------------------
def width_of(q, k):
    wide = 1.3 + 1.25 * (np.maximum(q, 1.0) / 40.0) ** 0.36
    wide = wide * np.where((k == 7) | (k == 9), 1.25, 1.0)
    return np.clip(wide, 2.0, 12.0)


def smoothed(points, sigma):
    if len(points) < 4:
        return points.copy()
    soft = ndimage.gaussian_filter1d(points, sigma, axis=0, mode="nearest")
    t = np.linspace(0.0, 1.0, len(points))[:, None]
    return soft + (1 - t) * (points[0] - soft[0]) + t * (points[-1] - soft[-1])


def along(points):
    return np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(points, axis=0).T))])


def where_of(reach):
    return [int(cols[reach["cells"][0]] * FACTOR), int(rows[reach["cells"][0]] * FACTOR)]


def run_px(reach):
    """A line's length from cell to cell, in pixels of the map."""
    return round(float(np.hypot(np.diff(rows[reach["cells"]] * 1.0), np.diff(cols[reach["cells"]] * 1.0)).sum()) * FACTOR, 1)


def own_flow(reach):
    """The most water a line carries itself: the last cell of one that joins another is the other's."""
    mine = reach["cells"][:-1] if reach["end"] == "joins" and len(reach["cells"]) > 1 else reach["cells"]
    return round(float(flow[mine].max()), 1)


reaches = sorted(water["reaches"], key=lambda r: -float(flow[r["cells"]].max()))
placed, owner = {}, {}
lines, records, left_out = [], [], []
for reach in reaches:
    cells = reach["cells"]
    ends_in = {"sea": "sea", "joins": "river", "dry": "salt lake"}[reach["end"]]
    if len(cells) < 2:
        left_out.append({"why": "a single cell", "at": where_of(reach), "flow_m3s": own_flow(reach), "length_px": run_px(reach), "ends_in": ends_in})
        continue
    points = np.column_stack([rows[cells] * FACTOR + (FACTOR - 1) / 2.0, cols[cells] * FACTOR + (FACTOR - 1) / 2.0]).astype(np.float64)
    course = points.copy()
    q = flow[cells].astype(np.float64).copy()
    k = king_flat[cells]
    height = z[cells].astype(np.float64)
    joins = None
    if reach["end"] == "joins":
        q[-1] = q[-2]
        if int(cells[-1]) in placed:
            points[-1] = placed[int(cells[-1])]
            joins = owner[int(cells[-1])]
    elif reach["end"] == "sea":
        step = points[-1] - points[-2]
        points = np.vstack([points, points[-1] + (1.5 * FACTOR + 6.0) * step / max(np.hypot(*step), 1e-9)])
        q = np.append(q, q[-1]); k = np.append(k, k[-1]); height = np.append(height, 0.0)
    q = np.maximum.accumulate(q)
    points = smoothed(points, 1.4)
    s = along(points)
    if s[-1] < 3.0:
        left_out.append({"why": "under 3 px long", "at": where_of(reach), "flow_m3s": own_flow(reach), "length_px": run_px(reach), "ends_in": ends_in})
        continue
    if reach["end"] == "sea" and s[-1] < 34.0 and not lake_flat[cells[0]]:
        left_out.append({"why": "a stream at the shore under 34 px long", "at": where_of(reach), "flow_m3s": own_flow(reach), "length_px": run_px(reach), "ends_in": ends_in})
        continue
    at = np.linspace(0.0, s[-1], max(int(s[-1] / 1.5), 2) + 1)
    fine = np.column_stack([np.interp(at, s, points[:, 0]), np.interp(at, s, points[:, 1])])
    fine_q = np.interp(at, s, q)
    fine_k = k[np.clip(np.searchsorted(s, at), 0, len(k) - 1)]
    wide = width_of(fine_q, fine_k)
    fall = np.maximum(-np.gradient(ndimage.gaussian_filter1d(height, 2.0, mode="nearest")), 0.0) / np.maximum(np.gradient(s) * KM, 1e-6)
    fine_fall = np.interp(at, s, fall)
    lazy = np.clip((2.5 - fine_fall) / 2.3, 0.0, 1.0) ** 1.5
    lazy *= np.where((fine_k == 7) | (fine_k == 9) | (fine_k == 5), 1.25, 1.0)
    wave = 11.0 * wide + 16.0
    phase = np.cumsum(2.0 * np.pi * 1.5 / wave) + rng.uniform(0, 2 * np.pi)
    phase += np.cumsum(rng.standard_normal(len(at)) * 0.09)
    swing = lazy * (1.9 * wide + 2.5) * np.sin(phase) * (0.75 + 0.25 * np.sin(0.37 * phase + 1.0))
    ends = np.minimum(at, s[-1] - at)
    swing *= np.clip(ends / (1.5 * wave), 0.0, 1.0)
    tangent = np.gradient(fine, axis=0)
    tangent /= np.maximum(np.hypot(tangent[:, 0], tangent[:, 1]), 1e-9)[:, None]
    fine = fine + swing[:, None] * np.column_stack([-tangent[:, 1], tangent[:, 0]])
    fine = smoothed(fine, 1.5)
    number = len(lines) + 1
    for cell, where in zip(cells.tolist(), np.interp(s[: len(cells)], at, np.arange(len(at))).astype(int)):
        if cell not in placed:
            placed[cell] = fine[min(where, len(fine) - 1)].copy()
            owner[cell] = number
    lines.append((kept(fine), wide))                     # the points as the file holds them
    own = cells[:-1] if reach["end"] == "joins" else cells   # the last cell of one that joins another is the other's
    if reach["end"] == "dry":                                # it ends in the salt lake: what it brings is what reaches the shore
        own = own[lake_flat[own] == 0]
    records.append({"reach": reach, "flow": fine_q, "course": course, "joins": joins, "ends_in": ends_in, "at_end": float(flow[own[-1]])})

# Drawn as the picture drew them, from the points as the file holds them: do they give the picture's river back?
river = np.zeros((h, w), dtype=bool)
for size in range(2, 13):
    sheet = Image.new("1", (w, h), 0)
    pen = ImageDraw.Draw(sheet)
    used = False
    for fine, wide in lines:
        mine = np.rint(wide).astype(int) == size
        if not mine.any():
            continue
        mine = ndimage.binary_dilation(mine)
        starts = np.flatnonzero(mine & ~np.r_[False, mine[:-1]])
        stops = np.flatnonzero(mine & ~np.r_[mine[1:], False])
        for a, b in zip(starts, stops):
            if b > a:
                pen.line([(float(x) + 0.5, float(y) + 0.5) for y, x in fine[a: b + 1]], fill=1, width=1)
                used = True
    if not used:
        continue
    reach_px = size // 2
    yy, xx = np.mgrid[-reach_px: reach_px + 1, -reach_px: reach_px + 1]
    nib = (yy * yy + xx * xx) <= (size / 2.0) ** 2 + 0.3
    river |= ndimage.binary_dilation(np.asarray(sheet, dtype=bool), structure=nib)
river &= allowed
same = bool((river == drawn["river"]).all())
print("rivers: %d lines made again from %d reaches (%d left out); drawn from the points as written, they give the picture's river pixels exactly: %s (%d px; differing %d)" % (
    len(lines), len(reaches), len(left_out), same, river.sum(), (river != drawn["river"]).sum()))
assert same
water_png = np.asarray(Image.open(MAPS + "/Water.png").convert("RGB"))
blue = (water_png == (28, 112, 224)).all(axis=2)
assert (blue == (drawn["river"] | drawn["lakes"])).all(), "Water.png is not these rivers and lakes"
print("Water.png's blue is these rivers and the drawn lakes, pixel for pixel: True (%d px)" % blue.sum())

sea_rank, rank = {}, 0
for number, record in enumerate(records, start=1):
    if record["ends_in"] == "sea":
        rank += 1
        sea_rank[number] = rank
out = []
total_km, total_points = 0.0, 0
for number, ((fine, wide), record) in enumerate(zip(lines, records), start=1):
    cells = np.rint(fine).astype(int)
    cy, cx = np.clip(cells[:, 0], 0, h - 1), np.clip(cells[:, 1], 0, w - 1)
    on_land = new_land[cy, cx] | (lake_map[cy, cx] > 0)
    last = int(np.flatnonzero(on_land)[-1]) if record["ends_in"] == "sea" else len(fine) - 1
    km = float(along(fine)[last]) * KM
    realm = kingdom_near[cy[: last + 1], cx[: last + 1]]
    through = [int(v) for v in dict.fromkeys(lake_map[cy, cx][lake_map[cy, cx] > 0].tolist())]
    window = lake_map[max(cy[0] - 3, 0): cy[0] + 4, max(cx[0] - 3, 0): cx[0] + 4]
    first_lake = int(np.bincount(window[window > 0]).argmax()) if lake_flat[record["reach"]["cells"][0]] and (window > 0).any() else None
    total_km += km
    total_points += len(fine)
    out.append({"id": number, "ends_in": record["ends_in"], "joins": record["joins"], "sea_rank": sea_rank.get(number), "largest_flow_m3s": round(float(record["flow"][-1]), 1), "flow_at_end_m3s": round(record["at_end"], 1),
                "length_km": round(km, 1), "from_kingdom": int(realm[0]), "to_kingdom": int(realm[-1]), "kingdoms": sorted(set(realm.tolist())),
                "from_lake": first_lake, "lakes": through,
                "points": [[float(x), float(y)] for y, x in fine],
                "flow_m3s": [round(float(v), 1) for v in record["flow"]], "width_px": [round(float(v), 2) for v in wide], "drawn_px": [int(v) for v in np.rint(wide)],
                "course": [[float(x), float(y)] for y, x in record["course"]]})
tally = {}
for entry in out:
    tally[entry["ends_in"]] = tally.get(entry["ends_in"], 0) + 1
lengths = sorted(e["length_km"] for e in out)
print("rivers written: %d (%s); %.0f km along the lines over the land; longest %.1f km, middle %.1f km, 100 km or more: %d; %d points; joining a river that is listed: %d of %d; starting at a drawn lake: %d" % (
    len(out), tally, total_km, lengths[-1], float(np.median(lengths)), sum(1 for v in lengths if v >= 100.0), total_points,
    sum(1 for e in out if e["ends_in"] == "river" and e["joins"]), tally.get("river", 0), sum(1 for e in out if e["from_lake"])))
print("   left out:", [(e["why"], e["at"], e["flow_m3s"], e["ends_in"]) for e in left_out])
print("   the 14 largest to reach the sea:", [(e["sea_rank"], e["id"], e["largest_flow_m3s"], e["flow_at_end_m3s"], e["length_km"], e["from_kingdom"], e["to_kingdom"]) for e in out if e["sea_rank"] and e["sea_rank"] <= 14])
losing = [(e["id"], e["ends_in"], e["largest_flow_m3s"], e["flow_at_end_m3s"]) for e in out if e["largest_flow_m3s"] - e["flow_at_end_m3s"] > 0.5]
print("   rivers that end with more than 0.5 m3/s less than the most they carry: %d: %s" % (len(losing), losing))
print("   cells whose flow is below nought: %d in lakes, %d outside any" % ((flow[lake_flat > 0] < 0).sum(), (flow[lake_flat == 0] < 0).sum()))
save_json(TO + "/Rivers.json", {
    "about": "The 291 rivers as lines: where each runs as drawn, and the water it carries at every point. Drawn as the picture drew them, they give the river pixels of Water.png exactly.",
    "order": "Largest first: id 1 carries the most water. A river is listed after the river it joins.",
    "fields": {"ends_in": "sea, river (it joins the river whose id is in joins), or salt lake (the desert's two rivers)",
               "sea_rank": "for a river that reaches the sea: its place among those by the most water it carries, 1 the largest (the numbering of Features.md's table of rivers)",
               "largest_flow_m3s, flow_at_end_m3s": "the most water it carries anywhere, and what it carries at its end: where it reaches the sea, the river it joins or the salt lake's shore. They are the same but for the seven rivers that lose water crossing the Desert or the Grassland",
               "length_km": "along the line, as far as the land of Continent.png goes", "from_kingdom, to_kingdom, kingdoms": "the kingdoms of KingdomMap.png at its first point, at its last point on land, and all it touches. A river that is itself a border touches both its kingdoms all the way",
               "from_lake": "the lake of LakeMap.png it flows out of, if its line starts at a lake's outlet", "lakes": "the lakes of LakeMap.png its line passes through, in order",
               "points": "[x, y] in pixels of the map, about 1.5 px apart, from where the river is first drawn to its end. A river that reaches the sea runs on some 9 px past the land's edge, to be cut off where the coast is drawn; a river that joins another ends on that river's line",
               "flow_m3s": "the most water it has carried so far at each point: its flow, but never less than upstream, so that a river losing water to its bed is drawn no narrower for it. DrainageFlow.png has the flow itself, cell by cell", "width_px": "its width at each point by the rule below", "drawn_px": "the width the pictures draw it at each point: width_px rounded to a whole number of pixels",
               "course": "[x, y], the river's bed as it was routed over the land: the middles of the half-size cells of DrainageDirection.png it runs through, before it was smoothed and made to wander. This is the line that runs downhill on Elevation.png"},
    "which_are_drawn": "A stream is drawn where it carries 15 m3/s or more. The stream out of a lake of 60 km2 or more is drawn too, however small, down to the next river or the sea: 32 rivers begin so, carrying less than 15 m3/s at first.",
    "width_rule": "width_px = 1.3 + 1.25 * (flow / 40) ** 0.36, a quarter more in swamp and tropical rainforest country (7 and 9 on TerrainMap.png), and never under 2 or over 12",
    "how_drawn": "Each point is drawn as a disc drawn_px across, and the points are joined. On the pictures with the hand-drawn coast a river is cut off 3 px beyond the land.",
    "wandering": "A river's line is its course smoothed, then swung from side to side where its bed is nearly level (not at all where it falls 2.5 m in a km or more), in loops about a dozen widths long.",
    "left_out_fields": "The 14 river lines the water was worked out as that are too short to draw: why, where each starts ([x, y]), the water it carries, its length from cell to cell, and where it ends.",
    "left_out": left_out, "rivers": out})

# -- watersheds ------------------------------------------------------------------------------------------------
shed = drawn["shed"]
save_grey(TO + "/WatershedMap.png", shed)
shed_px = np.bincount(shed.ravel(), minlength=52)
sheds = [{"id": s["id"], "px": int(shed_px[s["id"]]), "km2": round(float(shed_px[s["id"]] * KM2), 1), "mouth": [s["x"], s["y"]], "flow_at_mouth_m3s": round(s["flow"], 1),
          "reaches_the_sea": not s["shut"], "kingdom_at_mouth": int(kingdom_near[s["y"], s["x"]])} for s in water["sheds"]]
print("watersheds: %d; px %d to %d; not reaching the sea: %s; land of the mainland in none: %d px" % (
    len(sheds), shed_px[1:].min(), shed_px[1:].max(), [s["id"] for s in sheds if not s["reaches_the_sea"]], (full["mainland"] & (shed == 0)).sum()))
save_json(TO + "/Watersheds.json", {
    "about": "The 51 watersheds of the mainland. WatershedMap.png gives every pixel its watershed's id (0 on the islands and off the land). All the rain that falls in one leaves the land at the same river mouth, except that a river system gathering less than 1,500 km2 has no watershed of its own and is counted with the one beside it. Rivers.png draws the lines between them in brown.",
    "fields": {"mouth": "[x, y] where its river reaches the sea, or for the desert's closed basin the salt lake's lowest point", "px, km2": "its size on WatershedMap.png, whose edges are smoothed",
               "kingdom_at_mouth": "the kingdom of KingdomMap.png at the mouth"},
    "watersheds": sheds})

# -- the drainage the rivers came from, at half size ------------------------------------------------------------
to = water["to"]
code = np.zeros((gh, gw), dtype=np.uint8)
goes = to < water["sea"]
dr, dc = rows[to[goes]] - rows[goes], cols[to[goes]] - cols[goes]
compass = {(0, 1): 1, (1, 1): 2, (1, 0): 3, (1, -1): 4, (0, -1): 5, (-1, -1): 6, (-1, 0): 7, (-1, 1): 8}
codes = np.zeros(len(dr), dtype=np.uint8)
for (a, b), value in compass.items():
    codes[(dr == a) & (dc == b)] = value
assert (codes > 0).all()
code[rows[goes], cols[goes]] = codes
code[rows[~goes], cols[~goes]] = 9
save_grey(TO + "/DrainageDirection.png", code)
flow_grid = np.clip(np.rint(np.maximum(water["flow"], 0.0) * 32.0), 0, 65535).astype(np.int32)
save_number(TO + "/DrainageFlow.png", flow_grid)
save_number(TO + "/DrainageLakes.png", water["lake"])
shut_ids = {l["id"] for l in water["lakes"] if l["shut"]}
sinks = np.flatnonzero(~goes & np.isin(lake_flat, list(shut_ids)))
assert len(sinks) == 1
drainage_lakes = []
for l in water["lakes"]:
    px, shown = shows.get(l["id"], (0, None))
    drawn_as = shown if px >= l["cells"] else None       # a quarter or more of it (a cell is 4 px) lies under the drawn lake
    drainage_lakes.append({"id": l["id"], "kind": l["kind"], "terrain": l["kingdom"], "cells": l["cells"], "km2": round(l["km2"], 1), "surface_m": round(l["level"], 1),
                           "has_outlet": not l["shut"], "outlet": None if l["shut"] else centre(l["outlet"]), "drawn_as": drawn_as})
print("drainage at half size: %d x %d; cells of land %d, where the water leaves the land %d (one of them the salt lake's lowest point, at %s); flow kept to 1/32 m3/s, largest %.1f; cells whose flow was below nought (kept as 0): %d" % (
    gw, gh, len(rows), (~goes).sum(), centre(int(sinks[0])), flow_grid.max() / 32.0, (water["flow"] < 0).sum()))
small = [l for l in drainage_lakes if not l["drawn_as"]]
print("   its lakes: %d, of which drawn %d and too small to draw %d (%d to %d cells, %.1f to %.1f km2)" % (
    len(drainage_lakes), len(drainage_lakes) - len(small), len(small), min(l["cells"] for l in small), max(l["cells"] for l in small),
    min(l["km2"] for l in small), max(l["km2"] for l in small)))
save_json(TO + "/Drainage.json", {
    "about": "How the water runs over the land, on a grid of half the map's size (1550 x 2000 cells): the working the rivers, lakes and watersheds were all drawn from. Three maps: DrainageDirection.png, DrainageFlow.png and DrainageLakes.png.",
    "grid": "Cell (column c, row r) covers the map's pixels x = 2c and 2c + 1, y = 2r and 2r + 1; its middle is (2c + 0.5, 2r + 0.5).",
    "DrainageDirection.png": "8-bit grey. 0: not land. 1 to 8: the neighbour the cell's water runs to: 1 east (c + 1), 2 south-east, 3 south (r + 1), 4 south-west, 5 west, 6 north-west, 7 north, 8 north-east. 9: the water leaves the land here: into the sea, or at one cell (salt_lake_sink) into the floor of the salt lake.",
    "DrainageFlow.png": "The water passing through each cell, in m3/s times 32 (red + 256 x green). A river is drawn where this is 15 m3/s (480) or more, and below a lake of 60 km2 or more whatever it carries; smaller streams can be read from it at any lesser figure. In the Desert and the Grassland a river loses water to its bed and a lake to the sun, so there the figure can fall downstream; it is 0 in the cells of a lake that has lost more than has reached them.",
    "DrainageLakes.png": "The id of the lake each cell lies in (red + 256 x green; 0 for none): the 1,059 lakes of this working, which the 700 drawn lakes were made from. The rest are too small to draw.",
    "fields": {"kind": "as in Lakes.json", "terrain": "the kind of country it lies in, 1 to 9, as on TerrainMap.png", "cells, km2": "its size: half-size cells, each 0.4489 km2",
               "surface_m": "the height of its surface", "outlet": "[x, y], the middle of the cell where its water leaves it", "drawn_as": "the id in LakeMap.png and Lakes.json of the drawn lake it is part of, or null if it is too small to be drawn"},
    "salt_lake_sink": centre(int(sinks[0])), "lakes": drainage_lakes})

# -- lines of the land that no picture draws --------------------------------------------------------------------
fields = np.load(OUT + "/duchy2/fields1.npz")
king_fields = np.load(OUT + "/king30/fields.npz")
save_mask(TO + "/Ridges.png", fields["ridge"])
save_mask(TO + "/Spurs.png", king_fields["spur"])
save_mask(TO + "/Brooks.png", king_fields["brook"])
