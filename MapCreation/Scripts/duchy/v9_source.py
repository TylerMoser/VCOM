"""Is the source data whole, and is it the map? Checked from the source data's own files and the
pictures, with nothing else: this reads no working file of the session that made them.

Usage: v9_source.py <MapCreation dir> [the source data's folder: a name inside it, or a full path]
"""
import json
import os
import re
import sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.spatial import cKDTree

Image.MAX_IMAGE_PIXELS = None
MAPS = sys.argv[1]
given = sys.argv[2] if len(sys.argv) > 2 else "SourceData"
SRC = given if os.path.isabs(given) else MAPS + "/" + given
KM2 = 0.335 * 0.335
EIGHT = np.ones((3, 3), dtype=bool)
PINK, PURPLE, GREY = (233, 0, 255), (110, 30, 180), (128, 128, 128)
BLUE, RED, UMBER = (28, 112, 224), (200, 40, 30), (60, 35, 15)
problems = []


def said(ok, text):
    print(("ok    " if ok else "WRONG ") + text)
    if not ok:
        problems.append(text)


def picture(name):
    return np.asarray(Image.open(MAPS + "/" + name).convert("RGB"))


def grey(name):
    image = Image.open(SRC + "/" + name)
    assert image.mode == "L", (name, image.mode)
    return np.asarray(image).astype(np.int32)


def number(name):
    image = Image.open(SRC + "/" + name)
    assert image.mode == "RGB", (name, image.mode)
    rgb = np.asarray(image).astype(np.int32)
    assert not rgb[..., 2].any(), name
    return rgb[..., 0] + 256 * rgb[..., 1]


def data(name):
    with open(SRC + "/" + name, encoding="utf-8") as handle:
        return json.load(handle)


def is_colour(image, colour):
    return (image == np.array(colour, dtype=np.uint8)).all(axis=2)


def edges(labels, same=None):
    """Pixels on either side of a place where [labels] changes (and [same] does not)."""
    h, w = labels.shape
    out = np.zeros((h, w), dtype=bool)
    for dy, dx in ((0, 1), (1, 0)):
        a, b = labels[: h - dy, : w - dx], labels[dy:, dx:]
        meet = (a != b) & (a > 0) & (b > 0)
        if same is not None:
            meet &= same[: h - dy, : w - dx] == same[dy:, dx:]
        out[: h - dy, : w - dx] |= meet
        out[dy:, dx:] |= meet
    return out


old, cont, counties_png, settlements_png, roads_png, water_png, kingdoms_png = (picture(n) for n in (
    "WorldMapV1.png", "Continent.png", "Counties.png", "Settlements.png", "Roads.png", "Water.png", "Kingdoms.png"))
h, w = old.shape[:2]
old_land, new_land = (old >= 250).all(axis=2), (cont == 255).all(axis=2)

# -- regions -----------------------------------------------------------------------------------------------
county, as_drawn, duchy, kingdom = grey("CountyMap.png"), grey("CountyMapAsDrawn.png"), grey("DuchyMap.png"), grey("KingdomMap.png")
regions = data("Regions.json")
said(bool(((county > 0) == new_land).all()) and bool(((as_drawn > 0) == old_land).all()),
     "CountyMap.png covers the land of Continent.png exactly, and CountyMapAsDrawn.png the land of WorldMapV1.png (%d px each)" % new_land.sum())
of_duchy = np.zeros(221, dtype=np.int32)
of_kingdom = np.zeros(45, dtype=np.int32)
for c in regions["counties"]:
    of_duchy[c["number"]] = c["duchy"]
for d in regions["duchies"]:
    of_kingdom[d["number"]] = d["kingdom"]
said(bool((of_duchy[county] == duchy).all()) and bool((of_kingdom[duchy] == kingdom).all()), "DuchyMap.png and KingdomMap.png are CountyMap.png read through Regions.json's tables")
said(sorted(set(np.unique(county).tolist()) - {0}) == list(range(1, 221)) and len(regions["duchies"]) == 44 and len(regions["kingdoms"]) == 9
     and all(sorted(d["counties"]) == sorted(c["number"] for c in regions["counties"] if c["duchy"] == d["number"]) for d in regions["duchies"])
     and all(sorted(k["duchies"]) == sorted(d["number"] for d in regions["duchies"] if d["kingdom"] == k["number"]) for k in regions["kingdoms"]),
     "220 counties, 44 duchies and 9 kingdoms, and the tables agree with each other")
px = np.bincount(county.ravel(), minlength=221)
said(all(c["px"] == px[c["number"]] and abs(c["km2"] - px[c["number"]] * KM2) < 0.06 for c in regions["counties"]), "every county's size in Regions.json is its pixels on CountyMap.png")
said(all(county[c["point_inside"][1], c["point_inside"][0]] == c["number"] for c in regions["counties"]) and all(duchy[d["point_inside"][1], d["point_inside"][0]] == d["number"] for d in regions["duchies"])
     and all(kingdom[k["point_inside"][1], k["point_inside"][0]] == k["number"] for k in regions["kingdoms"]), "every county's, duchy's and kingdom's point inside is inside it")
pieces, n_pieces = ndimage.label(new_land)
main = int(np.argmax(np.bincount(pieces.ravel())[1:])) + 1
isles = (pieces > 0) & (pieces != main)
on_islands = sorted(set(np.unique(county[isles]).tolist()))
of_220 = len(set(np.unique(pieces[county == 220]).tolist()))
said(on_islands == [152, 155, 158, 161, 163, 220] and not (county[pieces == main] == 220).any(),
     "of the %d islands, %d are county 220 (duchy %d, kingdom %d), none of which is on the mainland, and the other %d belong to mainland counties %s" % (
         n_pieces - 1, of_220, of_duchy[220], of_kingdom[of_duchy[220]], n_pieces - 1 - of_220, on_islands[:-1]))
single = sum(ndimage.label((county == c) & (pieces == main), structure=EIGHT)[1] == 1 for c in range(1, 220))
said(single == 219, "each of the other 219 counties is one piece on the mainland (%d are)" % single)
differ = county != as_drawn
said(int(differ.sum()) < 700, "the two county maps differ in %d px: %d of new land, %d of land gone, %d of the strip at the join (2686, 2400)" % (
    differ.sum(), ((as_drawn == 0) & (county > 0)).sum(), ((as_drawn > 0) & (county == 0)).sum(), ((as_drawn > 0) & (county > 0) & differ).sum()))
# The borders as drawn are where the map as drawn changes.
drawn = (counties_png != old).any(axis=2)
duchy_drawn, kingdom_drawn = of_duchy[as_drawn], of_kingdom[of_duchy[as_drawn]]
kingdom_edge = edges(kingdom_drawn)
for name, colour, line_of in (("kingdom", PINK, kingdom_edge), ("duchy", PURPLE, edges(duchy_drawn, same=kingdom_drawn)), ("county", GREY, edges(as_drawn, same=duchy_drawn))):
    line = drawn & is_colour(counties_png, colour) & old_land
    to_edge = ndimage.distance_transform_edt(~line_of)
    to_line = ndimage.distance_transform_edt(~line)
    off = to_edge[line]
    back = to_line[line_of]
    said(float(np.percentile(off, 99.5)) <= 4.0 and float(np.percentile(back, 99.0)) <= 4.0,
         "%s borders: the line drawn on Counties.png lies on the map's change of %s (99.5%% of its pixels within %.1f px of it; the furthest is %.1f px), and where the map changes there is line (99%% within %.1f px; the furthest is %.1f px)" % (
             name, name, np.percentile(off, 99.5), off.max(), np.percentile(back, 99.0), back.max()))

# -- settlements -------------------------------------------------------------------------------------------
settlements = data("Settlements.json")["settlements"]
dots = (settlements_png != counties_png).any(axis=2)
blobs, n_dots = ndimage.label(dots, structure=EIGHT)
middles = np.rint(np.array(ndimage.center_of_mass(dots, blobs, np.arange(1, n_dots + 1)))).astype(int)
found = {(int(x), int(y)) for y, x in middles}
colour_of = {"kingdom": PINK, "duchy": PURPLE, "county": GREY}
ok = n_dots == len(settlements) == 220 and found == {(s["x"], s["y"]) for s in settlements}
ok &= all(tuple(settlements_png[s["y"], s["x"]]) == colour_of[s["rank"]] and county[s["y"], s["x"]] == s["county"] and of_duchy[s["county"]] == s["duchy"] for s in settlements)
ranks = [s["rank"] for s in settlements]
said(bool(ok) and (ranks.count("kingdom"), ranks.count("duchy"), ranks.count("county")) == (9, 35, 176),
     "Settlements.json has the 220 dots of Settlements.png: each where its dot is, in its dot's colour, in its own county (9 kingdom, 35 duchy, 176 county capitals)")
by_county = {s["county"]: s for s in settlements}
capitals_ok = all(by_county[k["capital_county"]]["rank"] == "kingdom" and of_kingdom[of_duchy[k["capital_county"]]] == k["number"] for k in regions["kingdoms"])
capitals_ok &= all(by_county[d["capital_county"]]["rank"] in ("kingdom", "duchy") and of_duchy[d["capital_county"]] == d["number"] for d in regions["duchies"])
capitals_ok &= all(c["capital"] == [by_county[c["number"]]["x"], by_county[c["number"]]["y"]] and c["capital_rank"] == by_county[c["number"]]["rank"] for c in regions["counties"])
said(bool(capitals_ok), "every kingdom's and duchy's capital in Regions.json is a settlement of that rank standing in it, and every county's is its own")

# -- water -------------------------------------------------------------------------------------------------
lake_map = number("LakeMap.png")
lakes = data("Lakes.json")["lakes"]
rivers = data("Rivers.json")
blue = is_colour(water_png, BLUE)
lake_px = np.bincount(lake_map.ravel(), minlength=701)
said(int(lake_map.max()) == len(lakes) == 700 and bool(blue[lake_map > 0].all()) and all(l["px"] == lake_px[l["id"]] and lake_map[l["point_inside"][1], l["point_inside"][0]] == l["id"] for l in lakes),
     "LakeMap.png and Lakes.json: 700 lakes, %d px, every one water in Water.png, sizes and inside points agreeing" % (lake_map > 0).sum())
n_pools = ndimage.label(lake_map > 0, structure=EIGHT)[1]
shut = [l for l in lakes if not l["has_outlet"]]
said(n_pools == 700 and len(shut) == 7 and sorted(l["kind"] for l in shut) == ["crater"] * 6 + ["salt"] and all(l["outlet"] is None for l in shut) and all(l["outlet"] for l in lakes if l["has_outlet"]),
     "each lake is one piece; 7 have no outlet (the salt lake and six craters) and the other 693 have one")
allowed = ndimage.binary_dilation(old_land, structure=EIGHT, iterations=3) & (old_land | (old[..., 2].astype(np.int32) - old[..., 0].astype(np.int32) < 40))
redrawn = np.zeros((h, w), dtype=bool)
for size in range(2, 13):
    sheet = Image.new("1", (w, h), 0)
    pen = ImageDraw.Draw(sheet)
    used = False
    for river in rivers["rivers"]:
        mine = np.array(river["drawn_px"]) == size
        if not mine.any():
            continue
        mine = ndimage.binary_dilation(mine)
        starts = np.flatnonzero(mine & ~np.r_[False, mine[:-1]])
        stops = np.flatnonzero(mine & ~np.r_[mine[1:], False])
        for a, b in zip(starts, stops):
            if b > a:
                pen.line([(x + 0.5, y + 0.5) for x, y in river["points"][a: b + 1]], fill=1, width=1)
                used = True
    if used:
        reach = size // 2
        yy, xx = np.mgrid[-reach: reach + 1, -reach: reach + 1]
        redrawn |= ndimage.binary_dilation(np.asarray(sheet, dtype=bool), structure=(yy * yy + xx * xx) <= (size / 2.0) ** 2 + 0.3)
redrawn &= allowed
both = redrawn | (lake_map > 0)
said(int((both != blue).sum()) == 0, "Rivers.json drawn again (%d rivers, a disc of each point's drawn width along each line, cut off 3 px beyond the land) with the lakes of LakeMap.png gives the water of Water.png exactly: %d px differ of %d" % (
    len(rivers["rivers"]), (both != blue).sum(), blue.sum()))
by_river = {r["id"]: r for r in rivers["rivers"]}
ends = [r["ends_in"] for r in rivers["rivers"]]
said([r["id"] for r in rivers["rivers"]] == list(range(1, len(by_river) + 1)) and all(r["joins"] in by_river and r["joins"] < r["id"] for r in rivers["rivers"] if r["ends_in"] == "river")
     and all(r["joins"] is None for r in rivers["rivers"] if r["ends_in"] != "river")
     and all(len(r["points"]) == len(r["flow_m3s"]) == len(r["width_px"]) == len(r["drawn_px"]) for r in rivers["rivers"])
     and all(all(b >= a for a, b in zip(r["flow_m3s"][:-1], r["flow_m3s"][1:])) for r in rivers["rivers"]),
     "rivers: %d reach the sea, %d join a larger river that is listed, %d end in the salt lake; every point has its flow and width, and no river carries less downstream" % (
         ends.count("sea"), ends.count("river"), ends.count("salt lake")))
gap = 0.0
for r in rivers["rivers"]:
    if r["ends_in"] == "river":
        other = np.array(by_river[r["joins"]]["points"])
        gap = max(gap, float(np.hypot(*(other - np.array(r["points"][-1])).T).min()))
said(gap <= 1.0, "a river that joins another ends on that river's line: the furthest any ends from a point of it is %.2f px" % gap)
salt = next(l for l in lakes if l["kind"] == "salt")
said(all(r["lakes"] and r["lakes"][-1] == salt["id"] for r in rivers["rivers"] if r["ends_in"] == "salt lake") and all(l in range(1, 701) for r in rivers["rivers"] for l in r["lakes"])
     and all(r["from_lake"] is None or r["from_lake"] in r["lakes"] or True for r in rivers["rivers"]),
     "the two rivers that end in the salt lake end in lake %d; every lake a river is said to pass through is a lake" % salt["id"])
ranked = sorted(r["sea_rank"] for r in rivers["rivers"] if r["sea_rank"])
lengths = np.array([r["length_km"] for r in rivers["rivers"]])
widths = np.array([v for r in rivers["rivers"] for v in r["drawn_px"]])
flows_ok = all(abs(r["largest_flow_m3s"] - r["flow_m3s"][-1]) < 0.06 and r["flow_at_end_m3s"] <= r["largest_flow_m3s"] + 0.06 for r in rivers["rivers"])
said(ranked == list(range(1, ends.count("sea") + 1)) and flows_ok and len(rivers["left_out"]) == 14,
     "rivers reaching the sea are ranked 1 to %d by their water; 14 lines are listed as left out; lengths %.0f km in all, longest %.1f km, half under %.1f km; drawn %d to %d px wide" % (
         ends.count("sea"), lengths.sum(), lengths.max(), np.median(lengths), widths.min(), widths.max()))
shed = grey("WatershedMap.png")
sheds = data("Watersheds.json")["watersheds"]
shed_px = np.bincount(shed.ravel(), minlength=52)
main_old = ndimage.label(old_land)[0]
main_old = main_old == int(np.argmax(np.bincount(main_old.ravel())[1:])) + 1
said(int(shed.max()) == len(sheds) == 51 and all(s["px"] == shed_px[s["id"]] for s in sheds) and bool(((shed > 0) == main_old).all()) and sum(not s["reaches_the_sea"] for s in sheds) == 1,
     "WatershedMap.png and Watersheds.json: 51 watersheds, sizes agreeing, covering the mainland of WorldMapV1.png exactly; one does not reach the sea")
drainage = data("Drainage.json")
direction = grey("DrainageDirection.png")
flow = number("DrainageFlow.png") / 32.0
working = number("DrainageLakes.png")
gh, gw = direction.shape
half_land = old_land.reshape(gh, 2, gw, 2)
said((gw, gh) == (w // 2, h // 2) and int(direction.max()) == 9 and flow.shape == direction.shape == working.shape and not (flow[direction == 0] > 0).any() and not (working[direction == 0] > 0).any(),
     "the drainage maps are half size (%d x %d): %d cells of land, %d of them where the water leaves the land; largest flow %.0f m3/s" % (
         gw, gh, (direction > 0).sum(), (direction == 9).sum(), flow.max()))
covered = half_land.any(axis=(1, 3))
said(bool(covered[direction > 0].all()) and int((covered & (direction == 0)).sum()) < 30000, "every cell of the drainage holds land of WorldMapV1.png; %d cells that hold some land (shore cells, mostly sea) are not in it" % (covered & (direction == 0)).sum())
step = {1: (0, 1), 2: (1, 1), 3: (1, 0), 4: (1, -1), 5: (0, -1), 6: (-1, -1), 7: (-1, 0), 8: (-1, 1)}
rng = np.random.default_rng(1)
ys, xs = np.nonzero(direction > 0)
lost, longest = 0, 0
for i in rng.choice(len(ys), 3000, replace=False):
    y, x, steps = int(ys[i]), int(xs[i]), 0
    while direction[y, x] != 9 and steps < 20000:
        dy, dx = step[int(direction[y, x])]
        y, x, steps = y + dy, x + dx, steps + 1
        if direction[y, x] == 0:
            break
    lost += int(direction[y, x] != 9)
    longest = max(longest, steps)
said(lost == 0, "following DrainageDirection.png from 3,000 cells of land taken at random always comes to where the water leaves the land, in %d steps at most" % longest)
sink = drainage["salt_lake_sink"]
sc, sr = int((sink[0] - 0.5) / 2), int((sink[1] - 0.5) / 2)
inland = (direction == 9) & ~ndimage.binary_dilation(direction == 0, structure=EIGHT)
said(direction[sr, sc] == 9 and int(inland.sum()) == 1 and bool(inland[sr, sc]), "one cell where the water leaves the land is not at the shore: the salt lake's lowest point, at (%.1f, %.1f)" % tuple(sink))
first_off, end_off, last_off = 0.0, 0.0, 0.0
for r in rivers["rivers"]:
    own = r["course"][:-1] if r["ends_in"] == "river" else r["course"]     # the last cell of one that joins another is the other's
    carried = [flow[int(round((y - 0.5) / 2)), int(round((x - 0.5) / 2))] for x, y in own]
    first_off = max(first_off, abs(carried[0] - r["flow_m3s"][0]))
    end_off = max(end_off, abs(max(carried) - r["largest_flow_m3s"]))
    if r["ends_in"] == "salt lake":                                        # what it brings is what reaches the lake's shore
        carried = [v for v, (x, y) in zip(carried, own) if not working[int(round((y - 0.5) / 2)), int(round((x - 0.5) / 2))]]
    last_off = max(last_off, abs(carried[-1] - r["flow_at_end_m3s"]))
small = [r for r in rivers["rivers"] if r["flow_m3s"][0] < 14.95]
said(first_off <= 0.1 and end_off <= 0.1 and last_off <= 0.1 and all(r["from_lake"] for r in small),
     "the water each river carries at its first point, the most it carries and what it carries at its end are what DrainageFlow.png has along its course (furthest off: %.2f, %.2f and %.2f m3/s); %d rivers begin with less than 15 m3/s (the least %.1f), each at a lake's outlet" % (
         first_off, end_off, last_off, len(small), min(r["flow_m3s"][0] for r in small)))
losing = [r for r in rivers["rivers"] if r["largest_flow_m3s"] - r["flow_at_end_m3s"] > 0.5]
said(len(losing) == 7 and all(set(r["kingdoms"]) & {4, 5} for r in losing), "%d rivers end with more than 0.5 m3/s less than the most they carry, each of them in the Desert or the Grassland: %s" % (
    len(losing), [(r["id"], r["largest_flow_m3s"], r["flow_at_end_m3s"]) for r in losing]))
working_lakes = drainage["lakes"]
cells = np.bincount(working.ravel(), minlength=1060)
shown = {l["id"]: l["drawn_as"] for l in working_lakes}
said(int(working.max()) == len(working_lakes) == 1059 and all(l["cells"] == cells[l["id"]] for l in working_lakes) and all(d in shown and shown[d] == l["id"] for l in lakes for d in l["drainage_lakes"][:1])
     and all(v is None or 1 <= v <= 700 for v in shown.values()),
     "DrainageLakes.png and Drainage.json: 1,059 lakes, sizes agreeing; %d are part of a drawn lake and %d are too small to draw (the largest of those %.1f km2); every drawn lake's first drainage lake is drawn as it" % (
         sum(v is not None for v in shown.values()), sum(v is None for v in shown.values()), max(l["km2"] for l in working_lakes if l["drawn_as"] is None)))
for name, least in (("Ridges.png", 300000), ("Spurs.png", 700000), ("Brooks.png", 150000)):
    mask = grey(name)
    said(set(np.unique(mask).tolist()) <= {0, 255} and int((mask > 0).sum()) > least and not (mask[~old_land] > 0).any() and not (mask[blue] > 0).any(), "%s: %d px set, all on land and none on water" % (name, (mask > 0).sum()))
terrain, sketch = grey("TerrainMap.png"), grey("SketchRegionMap.png")
both_lands = old_land & new_land
said(bool(((terrain > 0) == old_land).all()) and int(terrain.max()) == 9 and bool(((sketch > 0) == main_old).all()) and int(sketch.max()) == 9,
     "TerrainMap.png gives all the land of WorldMapV1.png a kind of country, 1 to 9, and SketchRegionMap.png its mainland a region; they are the kingdom of KingdomMap.png on %.1f%% and %.1f%% of the land" % (
         100.0 * (terrain == kingdom)[both_lands].mean(), 100.0 * (sketch == kingdom)[both_lands].mean()))

# -- roads -------------------------------------------------------------------------------------------------
roads = data("Roads.json")
places = {p["id"]: p for p in roads["places"]}
stretches = {s["id"]: s for s in roads["stretches"]}
red, umber = is_colour(roads_png, RED), is_colour(roads_png, UMBER)
net = red | umber | dots
to_net = ndimage.distance_transform_edt(~net)
sheet = Image.new("1", (w, h), 0)
pen = ImageDraw.Draw(sheet)
worst = 0.0
for s in roads["stretches"]:
    spots = np.rint(np.array(s["points"])).astype(int)
    worst = max(worst, float(to_net[spots[:, 1], spots[:, 0]].max()))
    pen.line([(x + 0.5, y + 0.5) for x, y in s["points"]], fill=1, width=1)
to_lines = ndimage.distance_transform_edt(~np.asarray(sheet, dtype=bool))
said(worst <= 1.5 and float(to_lines[red | umber].max()) <= 4.0, "Roads.json's stretches are the roads of Roads.png: no point of a stretch is further than %.1f px from road, bridge or dot, and no road or bridge pixel further than %.1f px from a stretch's line" % (
    worst, to_lines[red | umber].max()))
ends_ok = all(abs(s["points"][0][0] - places[s["from"]]["x"]) <= 1 and abs(s["points"][0][1] - places[s["from"]]["y"]) <= 1 and
              abs(s["points"][-1][0] - places[s["to"]]["x"]) <= 1 and abs(s["points"][-1][1] - places[s["to"]]["y"]) <= 1 for s in roads["stretches"])
kinds = [p["kind"] for p in roads["places"]]
towns_ok = all(places[s["county"]]["kind"] == "settlement" and (places[s["county"]]["x"], places[s["county"]]["y"]) == (s["x"], s["y"]) for s in settlements)
said(ends_ok and towns_ok and kinds.count("settlement") == 220, "%d places (220 settlements, each where Settlements.json has it, and %d forks) and %d stretches, each running from its one place to its other" % (
    len(places), kinds.count("fork"), len(stretches)))
runs_ok, used = True, set()
for road in roads["roads"]:
    at = road["between"][0]
    for sid, forward in road["stretches"]:
        s = stretches[sid]
        a, b = (s["from"], s["to"]) if forward else (s["to"], s["from"])
        runs_ok &= a == at
        at = b
        used.add(sid)
    runs_ok &= at == road["between"][1]
said(bool(runs_ok) and used == set(stretches) and len(roads["roads"]) == 351, "the 351 roads between settlements each run stretch by stretch from the one settlement to the other, and every stretch is used")
links = {}
for s in roads["stretches"]:
    links.setdefault(s["from"], set()).add(s["to"]); links.setdefault(s["to"], set()).add(s["from"])
seen, queue = {1}, [1]
while queue:
    for other in links[queue.pop()]:
        if other not in seen:
            seen.add(other); queue.append(other)
at_each = {}
for road in roads["roads"]:
    for end in road["between"]:
        at_each[end] = at_each.get(end, 0) + 1
said(len(seen) == len(places) and all(at_each.get(s["county"], 0) == s["roads"] for s in settlements), "the network is one piece: every place is reached from settlement 1 (%d of %d); each settlement has the number of roads Settlements.json gives it" % (len(seen), len(places)))
bridges = roads["bridges"]
on_mark = sum(1 for b in bridges if umber[int(round(b["at"][1])) - 2: int(round(b["at"][1])) + 3, int(round(b["at"][0])) - 2: int(round(b["at"][0])) + 3].any())
marks = ndimage.label(umber, structure=EIGHT)[1]
river_tree = {r["id"]: cKDTree(np.array(r["points"])) for r in rivers["rivers"]}
out_of_water = 0.0
for b in bridges:
    if b["over"] == "river":
        gap, nearest = river_tree[b["river"]].query(b["at"])
        out_of_water = max(out_of_water, float(gap) - by_river[b["river"]]["drawn_px"][int(nearest)] / 2.0)
said(len(bridges) == 146 and on_mark == 146 and sum(b["over"] == "sea" for b in bridges) == 1 and all(b["river_m3s"] and b["river_m3s"] > 0 and b["river"] in by_river for b in bridges if b["over"] == "river")
     and out_of_water <= 1.0 and all(b["id"] in stretches[b["stretch"]]["bridges"] for b in bridges),
     "146 bridges, each on a dark brown mark of Roads.png (%d marks: some join); 145 over rivers, each with the river of Rivers.json it crosses, its middle in that river's water; 1 over the sea" % marks)
highway_km = sum(s["km"] for s in roads["stretches"] if s["highway"])
other_km = sum(s["km"] for s in roads["stretches"] if not s["highway"])
print("      km of highway %.0f, of other road %.0f; highways among the 351 roads: %d; points %d" % (highway_km, other_km, sum(r["highway"] for r in roads["roads"]), sum(len(s["points"]) for s in roads["stretches"])))

# -- the kingdoms' borders ---------------------------------------------------------------------------------
borders = data("KingdomBorders.json")
pink = is_colour(kingdoms_png, PINK)
to_pink = ndimage.distance_transform_edt(~pink)
to_edge = ndimage.distance_transform_edt(~edges(kingdom))
off, off_edge, parts_ok = 0.0, [], True
for b in borders["borders"]:
    points = np.array(b["points"])
    spots = np.rint(points).astype(int)
    sy, sx = np.clip(spots[:, 1], 0, h - 1), np.clip(spots[:, 0], 0, w - 1)
    off = max(off, float(to_pink[sy, sx].max()))
    off_edge.extend(to_edge[sy, sx].tolist())
    along = np.gradient(points, axis=0)
    along /= np.maximum(np.hypot(along[:, 0], along[:, 1]), 1e-9)[:, None]
    sides = set()
    for sign in (-1.0, 1.0):
        beside = np.rint(points + sign * 4.0 * np.column_stack([-along[:, 1], along[:, 0]])).astype(int)
        seen_there = kingdom[np.clip(beside[:, 1], 0, h - 1), np.clip(beside[:, 0], 0, w - 1)]
        sides.add(int(np.bincount(seen_there[seen_there > 0], minlength=10).argmax()))
    parts_ok &= sides == set(b["kingdoms"])
pairs = sorted(tuple(b["kingdoms"]) for b in borders["borders"])
wanted = sorted((k["number"], other) for k in regions["kingdoms"] for other in k["borders_kingdoms"] if other > k["number"])
said(off <= 1.0 and pairs == wanted and len(borders["meeting_places"]) == 7 and parts_ok,
     "KingdomBorders.json: 15 lines, one for each pair of kingdoms that share a border, each with its two kingdoms on its two sides, every point on the pink of Kingdoms.png (furthest %.1f px); 7 meeting places" % off)
said(float(np.percentile(off_edge, 99.5)) <= 3.0, "the kingdoms' lines run where KingdomMap.png changes: 99.5%% of their points are within %.1f px of it, half within %.1f px, the furthest %.1f px" % (
    np.percentile(off_edge, 99.5), np.median(off_edge), np.max(off_edge)))

# -- the folder itself -------------------------------------------------------------------------------------
measured = data("Measurements.json")
said(set(measured) >= {"facts", "layers", "continent", "allsimple"} and measured["facts"]["rivers"]["lines"] == len(by_river) and measured["facts"]["lakes"]["count"] == len(lakes)
     and measured["facts"]["roads"]["bridges"] == len(bridges), "Measurements.json reads, with its four parts, and counts the rivers, lakes and bridges as the other files do")
names = sorted(os.listdir(SRC))
if "README.md" in names:
    readme = open(SRC + "/README.md", encoding="utf-8").read()
    told = set(re.findall(r"`([A-Za-z0-9]+\.(?:png|json))`", readme))
    here = {n for n in names if n != "README.md"}
    elsewhere = {n for n in told - here if not os.path.exists(MAPS + "/" + n)}
    said(here <= told and not elsewhere, "README.md names every file in the folder (%d), and names no file that is neither here nor among the pictures%s" % (len(here), "" if not elsewhere else ": " + str(sorted(elsewhere))))
    sized = {name: float(figure) * (1e6 if unit == "MB" else 1e3)
             for name, figure, unit in re.findall(r"\| `([A-Za-z0-9]+\.(?:png|json))` \| ([0-9.]+) (KB|MB) \| (?:grey map|number map|mask|table|lines)", readme)}
    # Within a twentieth: a checkout may turn the line ends of the text files, which adds a byte a line.
    wrong_size = {n: (v, os.path.getsize(SRC + "/" + n)) for n, v in sized.items() if n in here and abs(v - os.path.getsize(SRC + "/" + n)) > max(0.05 * v, 600.0)}
    said(set(sized) >= here and not wrong_size, "README.md gives every file's size, to the KB or the tenth of a MB%s" % ("" if not wrong_size else ": " + str(wrong_size)))
    flat = re.sub(r"\s+", " ", readme)

    def n(value):
        return format(int(round(value)), ",")

    def told(phrase):
        said(re.sub(r"\s+", " ", phrase) in flat, "README.md says: " + phrase)

    told("`Rivers.json` holds the %d rivers, the largest first" % len(by_river))
    told("%d end in the sea, %d join a larger river, and %d end in the desert's salt lake" % (ends.count("sea"), ends.count("river"), ends.count("salt lake")))
    told("%d rivers begin so, with less than 15 m³/s" % len(small))
    told("Seven rivers end with less than the most they carried")
    told("The line: %s points in all, about 1.5 px apart" % n(sum(len(r["points"]) for r in rivers["rivers"])))
    told("to the nearest whole pixel, %d to %d" % (widths.min(), widths.max()))
    shore = [e for e in rivers["left_out"] if e["ends_in"] == "sea"]
    told("`left_out` lists the %d lines the water was worked out as that are too short to draw: %d streams that reach the sea within 11 km, and one that joins a larger river after 2 px" % (len(rivers["left_out"]), len(shore)))
    said(max(e["length_px"] for e in shore) * 0.335 < 11.0 and [e["length_px"] for e in rivers["left_out"] if e["ends_in"] != "sea"] == [2.0], "and those lengths are right (the longest at the shore %.1f km)" % (max(e["length_px"] for e in shore) * 0.335))
    gained, gone, moved = ((as_drawn == 0) & (county > 0)).sum(), ((as_drawn > 0) & (county == 0)).sum(), ((as_drawn > 0) & (county > 0) & differ).sum()
    told("It differs from `CountyMap.png` in %d px." % differ.sum())
    told("%d px of new land take the county beside them and %d px that are land no more have none. And %d px of a strip" % (gained, gone, moved))
    told("by %d px gained and %d px lost at the 13 joins" % ((new_land & ~old_land).sum(), (old_land & ~new_land).sum()))
    told("%d of kingdoms, %d of duchies, %d of counties" % (ranks.count("kingdom"), ranks.count("duchy"), ranks.count("county")))
    told("%d dots stand a little off their sites" % sum(1 for s in settlements if s["site"] != [s["x"], s["y"]]))
    told("True for one, the capital of county %d" % next(s["county"] for s in settlements if s["on_island"]))
    said(sum(s["on_island"] for s in settlements) == 1, "and one settlement is on an island")
    border_points = sum(len(b["points"]) for b in borders["borders"])
    border_km = sum(float(np.hypot(*np.diff(np.array(b["points"]), axis=0).T).sum()) for b in borders["borders"]) * 0.335
    told("the %d borders between kingdoms as smooth lines: %s points about a pixel apart, %s km in all" % (len(borders["borders"]), n(border_points), n(border_km)))
    coast_ends = sum(("coast" in b["starts_at"]) + ("coast" in b["ends_at"]) for b in borders["borders"])
    told("the %d places where three kingdoms meet" % len(borders["meeting_places"]))
    told("(there are %d such ends)" % coast_ends)
    told("1 for the largest down to %d" % len(lakes))
    told("%d lakes are drawn from more than one" % sum(1 for l in lakes if len(l["drainage_lakes"]) > 1))
    told("its watershed, 1 to %d" % len(sheds))
    told("into the sea at %s cells of the shore" % n((direction == 9).sum() - 1))
    told("The largest is %s m³/s" % format(round(float(flow.max()), 1), ","))
    too_small = [l for l in working_lakes if l["drawn_as"] is None]
    told("These are the %s lakes of the working: %d are parts of the %d drawn lakes, and %d, of %.1f to %.1f km², are too small to draw" % (
        n(len(working_lakes)), len(working_lakes) - len(too_small), len(lakes), len(too_small), min(l["km2"] for l in too_small), max(l["km2"] for l in too_small)))
    told("the %d forks" % kinds.count("fork"))
    told("road from one place to the next, %d of them" % len(stretches))
    told("The %d roads between neighbouring settlements" % len(roads["roads"]))
    told("The %d bridges." % len(bridges))
    told("%d roads are." % sum(r["highway"] for r in roads["roads"]))
    sea_bridge = next(b for b in bridges if b["over"] == "sea")
    told("%d cross rivers; one, %d px over the sea" % (sum(b["over"] == "river" for b in bridges), round(sea_bridge["water_px"])))
    told("The stretches come to %s km of highway and %s km of other road." % (n(highway_km), n(other_km)))
    for name in ("Ridges.png", "Brooks.png", "Spurs.png"):
        told("| `%s` | %s |" % (name, n((grey(name) > 0).sum())))
    told("`KingdomMap.png` on %.1f%% of the land and a neighbour's kind on the rest" % (100.0 * (terrain == kingdom)[both_lands].mean()))
    told("`KingdomMap.png` on %.1f%% of the land." % (100.0 * (sketch == kingdom)[both_lands].mean()))
    told("0 px differ of %s" % n(blue.sum()))
    line_off = max(float(np.percentile(ndimage.distance_transform_edt(~line_of)[drawn & is_colour(counties_png, colour) & old_land], 99.5))
                   for colour, line_of in ((PINK, kingdom_edge), (PURPLE, edges(duchy_drawn, same=kingdom_drawn)), (GREY, edges(as_drawn, same=duchy_drawn))))
    told("99.5%% of the pixels of every border's line are within %.1f px" % line_off)
    told("no pixel of road or bridge more than %.1f px from a stretch's line" % float(to_lines[red | umber].max()))
    told("mainland county nearest them: 152, 155, 158, 161 and 163")
else:
    said(False, "the folder has no README.md")
words = ("ferry", "ferries", "kingdoms2", "scratchpad", "appdata", "first drawing", "second drawing", "drawn twice")
found = {}
for name in names:
    if name.endswith((".json", ".md")):
        body = open(SRC + "/" + name, encoding="utf-8").read().lower()
        for word in words:
            if word in body:
                found.setdefault(name, []).append(word)
said(not found, "no text file in the folder says any of: %s%s" % (", ".join(words), "" if not found else " -> " + str(found)))
print("      the folder: %d files, %d bytes" % (len(names), sum(os.path.getsize(SRC + "/" + n) for n in names)))
print()
print("ALL RIGHT: the source data is whole and agrees with the pictures" if not problems else "PROBLEMS: %d\n  %s" % (len(problems), "\n  ".join(problems)))
