"""Every figure Features.md states, measured from the pictures in MapCreation and from what the
runs that made them kept. Prints them, saves them as JSON, and writes the three long tables
(kingdoms, duchies, counties) as Markdown.

Usage: f1_facts.py <repo root> <water out dir> <duchy out dir> <roads out dir> <facts out dir>
"""
import json
import os
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, WATER, OUT, ROADS, FACTS = sys.argv[1:6]
os.makedirs(FACTS, exist_ok=True)
KM = 0.335
KM2 = KM * KM
BIOME = {1: "Tundra Mountains", 2: "Volcanic Mountains / Ruins", 3: "Temperate Mountains", 4: "Desert", 5: "Grassland",
         6: "Evergreen Temperate Rainforest", 7: "Swamp", 8: "Deciduous Forest", 9: "Tropical Rainforest"}
facts = {}


def load(name):
    return np.asarray(Image.open(ROOT + "/MapCreation/" + name).convert("RGBA"))


def is_colour(picture, colour):
    return (picture[..., 0] == colour[0]) & (picture[..., 1] == colour[1]) & (picture[..., 2] == colour[2])


COLOURS = {"sea": (181, 235, 255), "white": (255, 255, 255), "black": (0, 0, 0), "pink": (233, 0, 255), "purple": (110, 30, 180),
           "grey": (128, 128, 128), "blue": (28, 112, 224), "brown": (196, 118, 44), "red": (200, 40, 30), "umber": (60, 35, 15)}

# -- the files ----------------------------------------------------------------------------------------
files = {}
for name in sorted(os.listdir(ROOT + "/MapCreation")):
    if not name.lower().endswith(".png"):
        continue
    path = ROOT + "/MapCreation/" + name
    image = Image.open(path)
    entry = {"size": image.size, "mode": image.mode, "bytes": os.path.getsize(path)}
    if image.mode != "I;16":
        picture = np.asarray(image.convert("RGBA"))
        entry["colours"] = {key: int(is_colour(picture, value).sum()) for key, value in COLOURS.items()}
        entry["alpha"] = [int(picture[..., 3].min()), int(picture[..., 3].max())]
        entry["other"] = int(picture.shape[0] * picture.shape[1] - sum(entry["colours"].values()))
    files[name] = entry
    print("%-22s %s %s %8d bytes  %s" % (name, image.size, image.mode, entry["bytes"], entry.get("colours", "")))
facts["files"] = files

# -- the land -----------------------------------------------------------------------------------------
fields = np.load(OUT + "/fields1.npz")
king, island_king = fields["king"], fields["island_king"]
river, lake = fields["river"], fields["lake"]
mainland = king > 0
land = mainland | (island_king > 0)
country = np.where(mainland, king, island_king)
h, w = land.shape
ys, xs = np.nonzero(land)
elevation = np.asarray(Image.open(ROOT + "/MapCreation/Elevation.png")).astype(np.float64) / 10.0
facts["land"] = {"px": int(land.sum()), "km2": float(land.sum() * KM2), "mainland_px": int(mainland.sum()), "mainland_km2": float(mainland.sum() * KM2),
                 "box": [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
                 "wide_km": float((xs.max() - xs.min() + 1) * KM), "tall_km": float((ys.max() - ys.min() + 1) * KM),
                 "picture_km": [w * KM, h * KM], "sea_px": int((~land).sum())}
print("land: %s" % facts["land"])
far = {"north": (int(xs[np.argmin(ys)]), int(ys.min())), "south": (int(xs[np.argmax(ys)]), int(ys.max())),
       "west": (int(xs.min()), int(ys[np.argmin(xs)])), "east": (int(xs.max()), int(ys[np.argmax(xs)]))}
facts["land"]["furthest"] = far
print("furthest points of land: %s" % far)
islands = land & ~mainland
pieces, n = ndimage.label(islands, structure=np.ones((3, 3)))
sizes = ndimage.sum_labels(islands, pieces, index=np.arange(1, n + 1))
middles = ndimage.center_of_mass(islands, pieces, np.arange(1, n + 1))
facts["islands"] = sorted(({"km2": float(s * KM2), "px": int(s), "at": (int(m[1]), int(m[0]))} for s, m in zip(sizes, middles)), key=lambda i: -i["px"])
print("islands: %d, %.0f km2 in all; %s" % (n, islands.sum() * KM2, [(round(i["km2"]), i["at"]) for i in facts["islands"]]))
# The coast's length, as the edge between land and sea runs at this scale.
edge_h = (land[:, 1:] != land[:, :-1]).sum(); edge_v = (land[1:, :] != land[:-1, :]).sum()
from skimage import measure
coast_px = float(measure.perimeter(mainland, neighborhood=8))
facts["coast_km"] = coast_px * KM
print("mainland coast: about %.0f km (as the pixels run); pixel edges %d" % (coast_px * KM, edge_h + edge_v))
print("Elevation.png: %s to %s m on land; saved heights match the fields: %s" % (
    elevation[land].min(), elevation[land].max(), bool(np.abs(elevation - np.where(land, fields["height"], 0)).max() < 0.06)))
top = np.unravel_index(int(np.argmax(elevation)), elevation.shape)
facts["height"] = {"highest": float(elevation.max()), "highest_at": (int(top[1]), int(top[0])), "highest_kingdom": int(country[top]),
                   "mean": float(elevation[land].mean()), "median": float(np.median(elevation[land])),
                   "over_500": float((elevation[land] > 500).mean()), "over_1000": float((elevation[land] > 1000).mean()),
                   "over_2000": float((elevation[land] > 2000).mean()), "under_50": float((elevation[land] < 50).mean())}
print("heights: %s" % facts["height"])

# -- water --------------------------------------------------------------------------------------------
with open(WATER + "/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
drawn = np.load(WATER + "/drawn2.npz")
divide, shed = drawn["divide"], drawn["shed"]
water_png = load("Water.png")
blue = is_colour(water_png, COLOURS["blue"])
print("the masks kept match Water.png: %s (blue %d, river or lake %d)" % (bool((blue == ((river | lake) & True)).all()), blue.sum(), (river | lake).sum()))
wet = (river | lake) & land
facts["water"] = {"px": int(wet.sum()), "share": float(wet.sum() / land.sum()), "lake_px": int((lake & land).sum()),
                  "lake_share": float((lake & land).sum() / land.sum()), "river_px": int((river & ~lake & land).sum()),
                  "river_share": float((river & ~lake & land).sum() / land.sum())}
print("water: %s" % facts["water"])
pools, n_lakes = ndimage.label(lake, structure=np.ones((3, 3)))
lake_sizes = ndimage.sum_labels(lake, pools, index=np.arange(1, n_lakes + 1)) * KM2
lake_middles = ndimage.center_of_mass(lake, pools, np.arange(1, n_lakes + 1))
lake_king = [int(np.bincount(country[pools == i + 1]).argmax()) for i in np.argsort(-lake_sizes)[:12]]
order = np.argsort(-lake_sizes)
facts["lakes"] = {"count": int(n_lakes), "km2": float(lake_sizes.sum()), "least": float(lake_sizes.min()), "median": float(np.median(lake_sizes)),
                  "largest": [{"km2": float(lake_sizes[i]), "at": (int(lake_middles[i][1]), int(lake_middles[i][0])), "kingdom": k}
                              for i, k in zip(order[:12], lake_king)],
                  "over_100": int((lake_sizes >= 100).sum()), "over_500": int((lake_sizes >= 500).sum()), "under_20": int((lake_sizes < 20).sum())}
lake_home = ndimage.maximum(country, pools, index=np.arange(1, n_lakes + 1)).astype(int)
facts["lakes"]["by_kingdom"] = {k: int((lake_home == k).sum()) for k in range(1, 10)}
print("lakes: %s" % {key: value for key, value in facts["lakes"].items() if key != "largest"})
for entry in facts["lakes"]["largest"]:
    print("   lake of %.0f km2 at %s, kingdom %d" % (entry["km2"], entry["at"], entry["kingdom"]))
on_islands = int((lake & islands).sum())
print("lake pixels on islands: %d; river pixels on islands: %d" % (on_islands, int((river & islands).sum())))
rows, cols, flow, to = water["rows"], water["cols"], water["flow_flat"], water["to"]
reaches = water["reaches"]
ends = {}
lengths = []
for reach in reaches:
    cells = reach["cells"]
    ends[reach["end"]] = ends.get(reach["end"], 0) + 1
    steps = np.hypot(np.diff(rows[cells]), np.diff(cols[cells])).sum() * 2 * KM
    lengths.append(steps)
lengths = np.array(lengths)
longest = int(np.argmax(lengths))
mouths = []
for reach, km in zip(reaches, lengths):
    if reach["end"] in ("sea", "sink"):
        cells = reach["cells"]
        mouths.append({"flow": float(flow[cells].max()), "km": float(km), "at": (int(cols[cells[-1]] * 2 + 1), int(rows[cells[-1]] * 2 + 1)),
                       "from": (int(cols[cells[0]] * 2 + 1), int(rows[cells[0]] * 2 + 1)), "end": reach["end"],
                       "kingdom": int(country[min(rows[cells[-1]] * 2 + 1, h - 1), min(cols[cells[-1]] * 2 + 1, w - 1)])})
mouths.sort(key=lambda m: -m["flow"])
facts["rivers"] = {"lines": len(reaches), "ends": ends, "km": float(lengths.sum()), "longest_km": float(lengths.max()),
                   "least_flow": float(water["least_river"]), "most_flow": float(flow.max()), "mouths": mouths[:14],
                   "lines_over_100km": int((lengths >= 100).sum()), "median_km": float(np.median(lengths))}
print("rivers: %d lines, ends %s, %.0f km in all, longest %.0f km, median %.0f km, flow %.0f to %.0f m3/s" % (
    len(reaches), ends, lengths.sum(), lengths.max(), np.median(lengths), water["least_river"], flow.max()))
for m in mouths[:14]:
    print("   river of %.0f m3/s, %.0f km long, from %s to %s (%s), kingdom %d" % (m["flow"], m["km"], m["from"], m["at"], m["end"], m["kingdom"]))
# Widths as drawn: the widest disc that fits, at the middle of each river.
half = ndimage.distance_transform_edt(river)
spine = river & (half == ndimage.maximum_filter(half, size=3))
across = 2 * half[spine] - 1
facts["rivers"]["width_px"] = {"least": float(across.min()), "median": float(np.median(across)), "most": float(np.percentile(across, 99.5))}
print("rivers' width as drawn, px: least %.0f, median %.0f, 99.5th percentile %.0f" % (across.min(), np.median(across), np.percentile(across, 99.5)))
sheds = water["sheds"]
shed_ids = np.unique(shed[shed > 0])
shed_sizes = ndimage.sum_labels(shed > 0, shed, index=shed_ids) * KM2
facts["watersheds"] = {"count": int(len(shed_ids)), "largest_km2": float(shed_sizes.max()), "least_km2": float(shed_sizes.min()), "median_km2": float(np.median(shed_sizes)),
                       "over_20000": int((shed_sizes >= 20000).sum()), "line_px": int(is_colour(load("Rivers.png"), COLOURS["brown"]).sum())}
print("watersheds: %s; sheds listed by the water run: %d, shut ones %d" % (facts["watersheds"], len(sheds), sum(1 for s in sheds if s.get("shut"))))
big = np.argsort(-shed_sizes)[:6]
for i in big:
    mine = shed == shed_ids[i]
    m = ndimage.center_of_mass(mine)
    print("   watershed of %.0f km2 about (%d, %d)" % (shed_sizes[i], m[1], m[0]))

# -- kingdoms, duchies, counties ------------------------------------------------------------------------
county = np.load(OUT + "/county_map_f3.npy")
with open(OUT + "/county_list_f3.pickle", "rb") as handle:
    listing = pickle.load(handle)
of_duchy = np.asarray(listing["of_duchy"])
with open(OUT + "/counties_f3.pickle", "rb") as handle:
    duchy = pickle.load(handle)["duchy"]
with open(OUT + "/settlements.pickle", "rb") as handle:
    settlements = pickle.load(handle)
centres, rank, capital = settlements["centres"], settlements["rank"], settlements["capital"]
with open(OUT + "/capital_candidates.pickle", "rb") as handle:
    candidates = {row["duchy"]: row for row in pickle.load(handle)}
with open(ROADS + "/network.pickle", "rb") as handle:
    laid = pickle.load(handle)["laid"]
with open(ROADS + "/drawn.pickle", "rb") as handle:
    road_facts = pickle.load(handle)
flow_full = np.load(ROADS + "/flow.npy")
count = len(of_duchy) - 1
kingdom_of_duchy = {d: candidates[d]["kingdom"] for d in candidates}
county_area = np.bincount(county[land], minlength=count + 1) * KM2
duchy_area = np.bincount(duchy[land], minlength=45) * KM2
kingdom_area = np.bincount(country[land], minlength=10) * KM2
roads_at = {}
for (u, v) in laid:
    roads_at[u] = roads_at.get(u, 0) + 1; roads_at[v] = roads_at.get(v, 0) + 1
to_sea = ndimage.distance_transform_edt(land) * KM
big_flow = ndimage.maximum_filter(flow_full, size=25)
near_lake = ndimage.distance_transform_edt(~lake) * KM
near_river = ndimage.distance_transform_edt(~river) * KM

beside = {}
for dy, dx in ((0, 6), (6, 0)):
    a = king[: h - dy, : w - dx]; b = king[dy:, dx:]
    meet = (a != b) & (a > 0) & (b > 0)
    for pair in np.unique(np.stack([a[meet], b[meet]], axis=1), axis=0):
        beside.setdefault(int(pair[0]), set()).add(int(pair[1])); beside.setdefault(int(pair[1]), set()).add(int(pair[0]))
coastal = {k: bool((ndimage.binary_dilation(country == k, iterations=12) & ~land).any()) for k in range(1, 10)}

kingdoms = []
for k in range(1, 10):
    here = country == k
    on_main = king == k
    duchies_here = sorted(d for d, kk in kingdom_of_duchy.items() if kk == k)
    counties_here = [c for c in range(1, count + 1) if kingdom_of_duchy[int(of_duchy[c])] == k]
    cap = duchies_here and [c for c in counties_here if rank[c] == "kingdom"][0]
    heights = elevation[here]
    entry = {"number": k, "biome": BIOME[k], "km2": float(kingdom_area[k]), "mainland_km2": float(on_main.sum() * KM2),
             "duchies": len(duchies_here), "counties": len(counties_here), "capital": [int(v) for v in centres[cap]], "capital_duchy": int(of_duchy[cap]),
             "capital_county": int(cap), "beside": sorted(beside.get(k, ())), "coast": coastal[k],
             "height": [float(heights.min()), float(np.median(heights)), float(heights.max())],
             "water": float((wet & here).sum() / here.sum()), "lakes": float((lake & here).sum() / here.sum()),
             "rivers": float((river & ~lake & here).sum() / here.sum()), "lake_count": facts["lakes"]["by_kingdom"][k],
             "river_at_capital": float(candidates[int(of_duchy[cap])]["flow"]), "sea_from_capital": float(candidates[int(of_duchy[cap])]["sea"]),
             "height_at_capital": float(elevation[centres[cap][1], centres[cap][0]]), "duchy_numbers": duchies_here,
             "county_km2": [float(county_area[c]) for c in counties_here], "duchy_km2": [float(duchy_area[d]) for d in duchies_here]}
    kingdoms.append(entry)
    print("kingdom %d %s: %.0f km2, %d duchies, %d counties, capital %s (duchy %d), beside %s, coast %s, heights %s, water %.1f%% (%d lakes)" % (
        k, BIOME[k], entry["km2"], entry["duchies"], entry["counties"], entry["capital"], entry["capital_duchy"], entry["beside"], entry["coast"],
        [round(v) for v in entry["height"]], 100 * entry["water"], entry["lake_count"]))
facts["kingdoms"] = kingdoms
# A point well inside each kingdom, to tell the kingdoms apart by: the middle of its white piece of
# Kingdoms.png, or where that falls near a border, the point furthest from any border.
kingdoms_png = load("Kingdoms.png")
white_pieces, _ = ndimage.label((kingdoms_png[..., :3] >= 250).all(axis=2) & mainland)
for entry in kingdoms:
    k = entry["number"]
    piece = white_pieces == np.bincount(white_pieces[(king == k) & (white_pieces > 0)]).argmax()
    cy, cx = (int(round(v)) for v in ndimage.center_of_mass(piece))
    deep = ndimage.distance_transform_edt(piece)
    if deep[cy, cx] < 40:
        cy, cx = (int(v) for v in np.unravel_index(int(np.argmax(deep)), deep.shape))
    assert piece[cy, cx] and king[cy, cx] == k
    entry["middle"] = [cx, cy]
    entry["middle_from_border_km"] = float(deep[cy, cx] * KM)
print("a point well inside each kingdom: %s" % {e["number"]: (tuple(e["middle"]), round(e["middle_from_border_km"])) for e in kingdoms})

duchies = []
duchy_seat = settlements["duchy_seat"]
for d in range(1, 45):
    counties_here = [c for c in range(1, count + 1) if int(of_duchy[c]) == d]
    seat = duchy_seat[d]
    areas = np.array([county_area[c] for c in counties_here])
    duchies.append({"number": d, "kingdom": kingdom_of_duchy[d], "km2": float(duchy_area[d]), "counties": len(counties_here), "county_numbers": counties_here,
                    "seat": [int(v) for v in centres[seat]], "seat_county": int(seat), "rank": rank[seat],
                    "county_km2": [float(a) for a in areas], "spread": float(np.abs(areas - areas.mean()).max() / areas.mean()),
                    "height_at_seat": float(elevation[centres[seat][1], centres[seat][0]])})
facts["duchies"] = duchies
spreads = np.array([d["spread"] for d in duchies])
print("duchies: 44; km2 %.0f to %.0f; counties' furthest from their duchy's mean: %.1f%%" % (min(d["km2"] for d in duchies), max(d["km2"] for d in duchies), 100 * spreads.max()))
for k in range(1, 10):
    areas = np.array([d["km2"] for d in duchies if d["kingdom"] == k])
    print("   kingdom %d: duchies %s km2; furthest from the mean %.1f%%" % (k, np.round(np.sort(areas)).astype(int).tolist(), 100 * np.abs(areas - areas.mean()).max() / areas.mean()))

counties = []
for c in range(1, count + 1):
    x, y = (int(v) for v in centres[c])
    counties.append({"number": c, "duchy": int(of_duchy[c]), "kingdom": kingdom_of_duchy[int(of_duchy[c])], "rank": rank[c], "at": [x, y],
                     "km2": float(county_area[c]), "height": float(elevation[y, x]), "roads": int(roads_at.get(c, 0)),
                     "sea_km": float(to_sea[y, x]), "river": float(big_flow[y, x]), "river_km": float(near_river[y, x]), "lake_km": float(near_lake[y, x]),
                     "island": bool(not mainland[y, x])})
facts["counties"] = counties
areas = np.array([c["km2"] for c in counties])
print("counties: %d; km2 %.0f to %.0f, mean %.0f, median %.0f" % (count, areas.min(), areas.max(), areas.mean(), np.median(areas)))
on_coast = sum(1 for c in counties if c["sea_km"] < 6.0); on_river = sum(1 for c in counties if c["river_km"] < 4.0); on_lake = sum(1 for c in counties if c["lake_km"] < 4.0)
heights = np.array([c["height"] for c in counties])
gaps = []
points = np.array([c["at"] for c in counties], dtype=np.float64)
for i in range(count):
    away = np.hypot(*(points - points[i]).T); away[i] = 1e9
    gaps.append(away.min() * KM)
facts["settlements"] = {"coast": on_coast, "river": on_river, "lake": on_lake, "highest": float(heights.max()), "median_height": float(np.median(heights)),
                        "nearest_gap_km": [float(np.min(gaps)), float(np.median(gaps)), float(np.max(gaps))],
                        "ranks": {r: sum(1 for c in counties if c["rank"] == r) for r in ("kingdom", "duchy", "county")}}
print("settlements: %s" % facts["settlements"])

# -- borders ------------------------------------------------------------------------------------------
def edge_km(labels, same=None):
    total = 0
    for dy, dx in ((0, 1), (1, 0)):
        a = labels[: h - dy, : w - dx]; b = labels[dy:, dx:]
        meet = (a != b) & (a > 0) & (b > 0)
        if same is not None:
            meet &= same[: h - dy, : w - dx] == same[dy:, dx:]
        total += int(meet.sum())
    return total * KM / 1.2732                              # pixel edges overstate a slanting line by 4/pi on average


main_county = np.where(mainland, county, 0)
main_duchy = np.where(mainland, duchy, 0)
facts["borders"] = {"kingdom_km": edge_km(king), "duchy_km": edge_km(main_duchy, king), "county_km": edge_km(main_county, main_duchy)}
print("borders, km: %s" % facts["borders"])

# -- roads --------------------------------------------------------------------------------------------
bridges = road_facts["bridges"]
over_rivers = [b for b in bridges if not b["sea"]]
over_sea = [b for b in bridges if b["sea"]]
assert len(over_sea) == 1
flows = np.array([b["flow"] for b in over_rivers]); in_town = np.array([b["town"] for b in over_rivers])
facts["roads"] = {"links": len(laid), "highway_links": sum(1 for r in laid.values() if r["highway"]), "km": road_facts["length"],
                  "stretches": road_facts["stretches"], "bridges": len(bridges), "river_bridges": len(over_rivers), "sea_bridge": over_sea[0],
                  "beside_roads": road_facts["beside_roads"], "bridges_at_town": int(in_town.sum()),
                  "bridges_by_size": {"under 40": int((flows < 40).sum()), "40 to 100": int(((flows >= 40) & (flows < 100)).sum()),
                                      "100 to 300": int(((flows >= 100) & (flows < 300)).sum()), "300 to 800": int(((flows >= 300) & (flows < 800)).sum()),
                                      "800 and over": int((flows >= 800).sum())},
                  "bridges_highway": int(sum(1 for b in over_rivers if b["highway"])),
                  "roads_at": {r: float(np.mean([c["roads"] for c in counties if c["rank"] == r])) for r in ("kingdom", "duchy", "county")},
                  "dead_ends": [c["at"] for c in counties if c["roads"] == 1], "most_roads": int(max(c["roads"] for c in counties))}
print("roads: %s" % facts["roads"])
roads_png = load("Roads.png")
red, umber = is_colour(roads_png, COLOURS["red"]), is_colour(roads_png, COLOURS["umber"])
by_kingdom = {k: float(((red | umber) & (country == k)).sum()) for k in range(1, 10)}
facts["roads"]["px_by_kingdom"] = by_kingdom
print("road pixels by kingdom: %s" % {k: int(v) for k, v in by_kingdom.items()})

with open(FACTS + "/facts.json", "w", encoding="utf-8") as handle:
    json.dump(facts, handle, indent=1, default=lambda o: int(o) if isinstance(o, np.integer) else float(o))

# -- the long tables ----------------------------------------------------------------------------------
with open(FACTS + "/kingdoms.md", "w", encoding="utf-8") as handle:
    handle.write("| Kingdom | Biome | Area (km²) | Duchies | Counties | Capital (x, y) | Borders kingdoms | Heights: lowest, median, highest (m) | Water | Lakes |\n")
    handle.write("|---|---|---|---|---|---|---|---|---|---|\n")
    for e in kingdoms:
        handle.write("| %d | %s | %s | %d | %d | (%d, %d) | %s | %d, %d, %d | %.1f%% | %d |\n" % (
            e["number"], e["biome"], format(round(e["km2"]), ","), e["duchies"], e["counties"], e["capital"][0], e["capital"][1],
            ", ".join(str(b) for b in e["beside"]), round(e["height"][0]), round(e["height"][1]), round(e["height"][2]), 100 * e["water"], e["lake_count"]))
with open(FACTS + "/duchies.md", "w", encoding="utf-8") as handle:
    handle.write("| Duchy | Kingdom | Capital (x, y) | Capital is | Area (km²) | Counties | Counties' numbers | Height at capital (m) |\n")
    handle.write("|---|---|---|---|---|---|---|---|\n")
    for d in duchies:
        handle.write("| %d | %d | (%d, %d) | %s | %s | %d | %d to %d | %d |\n" % (
            d["number"], d["kingdom"], d["seat"][0], d["seat"][1], "kingdom capital (pink)" if d["rank"] == "kingdom" else "duchy capital (purple)",
            format(round(d["km2"]), ","), d["counties"], d["county_numbers"][0], d["county_numbers"][-1], round(d["height_at_seat"])))
with open(FACTS + "/counties.md", "w", encoding="utf-8") as handle:
    handle.write("| County | Duchy | Kingdom | Capital (x, y) | Dot | Area (km²) | Height (m) | Roads | Sea (km) | Nearest river (km) |\n")
    handle.write("|---|---|---|---|---|---|---|---|---|---|\n")
    for c in counties:
        handle.write("| %d | %d | %d | (%d, %d) | %s | %s | %d | %d | %d | %s |\n" % (
            c["number"], c["duchy"], c["kingdom"], c["at"][0], c["at"][1], {"kingdom": "pink", "duchy": "purple", "county": "grey"}[c["rank"]],
            format(round(c["km2"]), ","), round(c["height"]), c["roads"], round(c["sea_km"]), "%.0f" % c["river_km"] if c["river_km"] < 60 else "over 60"))
print("saved the facts and the three tables to %s" % FACTS)
