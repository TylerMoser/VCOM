"""The figures typed into Features.md's written part, each held against what was measured, and
the words the document must no longer use.

Usage: f8c_check.py <folder holding MapCreation> <duchy out dir> <roads out dir> <facts out dir> <document> [the source data's folder]
"""
import json
import os
import pickle
import re
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT, ROADS, FACTS, DOC = sys.argv[1:6]
SOURCE = sys.argv[6] if len(sys.argv) > 6 else ROOT + "/MapCreation/SourceData"
with open(FACTS + "/facts.json", encoding="utf-8") as handle:
    facts = json.load(handle)
with open(FACTS + "/layers.json", encoding="utf-8") as handle:
    layers = json.load(handle)
text = open(DOC, encoding="utf-8").read()
flat = re.sub(r"\s+", " ", text)
wrong = []


def n(value):
    return format(int(round(value)), ",")


def has(phrase, what):
    """The document says this, in these words."""
    ok = re.sub(r"\s+", " ", phrase) in flat
    print(("ok    " if ok else "WRONG ") + what + ": " + phrase)
    if not ok:
        wrong.append(what)


def true(ok, what):
    print(("ok    " if ok else "WRONG ") + what)
    if not ok:
        wrong.append(what)


def load(name):
    return np.asarray(Image.open(ROOT + "/MapCreation/" + name).convert("RGB"))


def is_colour(picture, colour):
    return (picture == np.array(colour, dtype=np.uint8)).all(axis=2)


kingdoms, duchies, counties, roads, files = facts["kingdoms"], facts["duchies"], facts["counties"], facts["roads"], facts["files"]
# -- words that must be gone ---------------------------------------------------------------------------
for word in ("ferry", "ferries", "Kingdoms2", "first drawing", "second drawing", "drawn twice", "as first drawn", "made again", "dashes"):
    found = len(re.findall(re.escape(word), text, flags=re.I))
    true(found == 0, "the document does not say \"%s\" (times found: %d)" % (word, found))
true("Kingdoms2.png" not in files and "Kingdoms.png" in files, "the folder has Kingdoms.png and no Kingdoms2.png")
named = set(re.findall(r"`([A-Za-z0-9]+\.png)`", text))
in_source = {name for name in os.listdir(SOURCE) if name.endswith(".png")}
true(named <= set(files) | in_source, "every picture the document names is in the folder, or in its folder of source data (named: %s)" % sorted(named))
true(set(files) <= named, "every picture in the folder is named in the document")
anchors = set(re.findall(r"\]\(#([a-z0-9-]+)\)", text))
heads = {re.sub(r"[^a-z0-9 -]", "", h.lower()).replace(" ", "-") for h in re.findall(r"^#{2,3} (.+)$", text, flags=re.M)}
true(anchors <= heads, "every link inside the document leads to a heading (not found: %s)" % sorted(anchors - heads))

# -- kingdoms ------------------------------------------------------------------------------------------
areas = [k["km2"] for k in kingdoms]
ninth = facts["land"]["km2"] / 9.0
has("%s to %s km²" % (n(min(areas)), n(max(areas))), "the kingdoms' sizes")
off = [100.0 * (a - ninth) / ninth for a in areas]
true(max(abs(v) for v in off) < 0.3, "every kingdom is within 0.3%% of a ninth of the land (furthest %.2f%%)" % max(abs(v) for v in off))
low, high = int(np.argmin(off)), int(np.argmax(off))
has("from %.2f%% under (the %s) to %.2f%% over (the %s)" % (-off[low], kingdoms[low]["biome"], off[high], kingdoms[high]["biome"]), "the kingdoms' furthest from a ninth")
has("its mainland is %s km²" % n(kingdoms[6]["mainland_km2"]), "kingdom 7's mainland")
has("%s px, about 4,060 km of border" % n(files["Kingdoms.png"]["colours"]["pink"]), "the kingdoms' lines")
has("border: " + ", ".join("%d (%d, %d)" % (k["number"], k["middle"][0], k["middle"][1]) for k in kingdoms[:5]) + ",", "points inside kingdoms 1 to 5")
has(", ".join("%d (%d, %d)" % (k["number"], k["middle"][0], k["middle"][1]) for k in kingdoms[5:]) + ".", "points inside kingdoms 6 to 9")
true(min(k["middle_from_border_km"] for k in kingdoms) >= 50.0, "each of those points is at least 50 km from any border (nearest %.0f km)" % min(k["middle_from_border_km"] for k in kingdoms))
picture = load("Kingdoms.png")
white = (picture >= 250).all(axis=2)
pieces = ndimage.label(white)[0]
homes = [int(pieces[k["middle"][1], k["middle"][0]]) for k in kingdoms]
true(len(set(homes)) == 9 and 0 not in homes, "the nine points lie in nine different white pieces of Kingdoms.png")
sketch = np.load(OUT + "/../region_map.npy")
king = np.load(OUT + "/fields1.npz")["king"]
main = (king > 0) & (sketch > 0)
share = 100.0 * (sketch[main] == king[main]).mean()
has("%d%% of the mainland is in the kingdom it was sketched in" % round(share), "land in the kingdom it was sketched in (%.1f%%)" % share)

# -- duchies, counties, settlements --------------------------------------------------------------------
d_areas = [d["km2"] for d in duchies]
has("A duchy is %s to %s km²" % (n(min(d_areas)), n(max(d_areas))), "the duchies' sizes")
spread = []
for k in range(1, 10):
    mine = np.array([d["km2"] for d in duchies if d["kingdom"] == k])
    spread.append(100.0 * np.abs(mine - mine.mean()).max() / mine.mean())
has("none is more than %.1f%% from its kingdom's average" % max(spread), "how even the duchies are")
has("%s px, about 6,730 km of border" % n(files["Duchies.png"]["colours"]["purple"]), "the duchies' lines")
c_areas = [c["km2"] for c in counties]
has("A county is %s to %s km², %s km² on average" % (n(min(c_areas)), n(max(c_areas)), n(np.mean(c_areas))), "the counties' sizes")
grey_lines = files["Counties.png"]["colours"]["grey"] - files["Duchies.png"]["colours"]["grey"]
has("%s px, about 15,540 km of border" % n(grey_lines), "the counties' lines")
s = facts["settlements"]
has("%d of the 220 are within 4 km of a river on the map, %d within 4 km of a lake, and %d within 6 km of the sea" % (s["river"], s["lake"], s["coast"]), "where capitals stand")
has("Neighbours are %d km apart at the median. The closest pair is %d km apart, and the loneliest capital is %d km" % (
    round(s["nearest_gap_km"][1]), round(s["nearest_gap_km"][0]), round(s["nearest_gap_km"][2])), "capitals' spacing")
true(s["nearest_gap_km"][0] >= 13.0, "no two capitals are within 13 km of each other (closest %.1f km)" % s["nearest_gap_km"][0])

# -- roads and bridges ---------------------------------------------------------------------------------
has("roads: %s px" % n(files["Roads.png"]["colours"]["red"]), "the roads' pixels")
roads_png = load("Roads.png")
umber = is_colour(roads_png, (60, 35, 15))
marks, n_marks = ndimage.label(umber, structure=np.ones((3, 3)))
has("bridges: %s px in %d marks" % (n(files["Roads.png"]["colours"]["umber"]), n_marks), "the bridges' pixels and marks")
coast = load("WorldMapV1.png")
land = (coast >= 250).all(axis=2)
strait = marks == marks[umber & ~land][0]
ys, xs = np.nonzero(strait)
has("at x %d to %d, y %d to %d" % (xs.min(), xs.max(), ys.min(), ys.max()), "where the sea's bridge is")
bridge = roads["sea_bridge"]
has("is %d px from shore to shore as drawn (%.1f km" % (round(bridge["px"]), bridge["px"] * 0.335), "the sea's bridge from shore to shore")
pts = np.stack([xs, ys], axis=1).astype(float)
pts -= pts.mean(axis=0)
vals, vecs = np.linalg.eigh(np.cov(pts.T))
long_axis = (pts @ vecs[:, 1]).max() - (pts @ vecs[:, 1]).min() + 1
short_axis = (pts @ vecs[:, 0]).max() - (pts @ vecs[:, 0]).min() + 1
has("| The bridge over the sea | 4 px wide, %d px long | 1.3 km wide, %d km long |" % (round(long_axis), round(long_axis * 0.335)), "the sea's bridge as a mark (%.1f by %.1f px)" % (long_axis, short_axis))
beside = roads["beside_roads"]
has("%d px in %d places, %d on county borders and %d on duchy borders" % (
    sum(v["px"] for v in beside.values()), sum(v["places"] for v in beside.values()), beside["county"]["places"], beside["duchy"]["places"]), "borders' colour beside roads")
true(beside["kingdom"]["places"] == 0, "no road runs along a kingdom's border")
km = roads["km"]
has("About 19,300 km of road**: 5,290 km of highway and 14,020 km of other road", "the roads' length")
true(abs(km["highway"] + km["road"] - 19300) < 50 and abs(km["highway"] - 5290) < 5 and abs(km["road"] - 14020) < 5, "which is what was laid: %.0f and %.0f km" % (km["highway"], km["road"]))
has("%d roads between neighbouring settlements" % roads["links"], "roads")
has("%d bridges**: %d over rivers and the one over the sea" % (roads["bridges"], roads["river_bridges"]), "bridges")
has("%d of the river bridges, %d%%, are within 4 km of a settlement" % (roads["bridges_at_town"], round(100.0 * roads["bridges_at_town"] / roads["river_bridges"])), "bridges at settlements")
b = roads["bridges_by_size"]
has("%d over rivers of less than 40 m³/s, %d over 40 to 100, %d over 100 to 300, %d over 300 to 800, and %d over the largest rivers" % (
    b["under 40"], b["40 to 100"], b["100 to 300"], b["300 to 800"], b["800 and over"]), "bridges by river")
has("%d of the river bridges are on highways" % roads["bridges_highway"], "bridges on highways")
has("a kingdom's capital %.1f, the busiest %d" % (roads["roads_at"]["kingdom"], roads["most_roads"]), "roads at a settlement")
ends = sorted(tuple(e) for e in roads["dead_ends"])
has("Three settlements are dead ends:** the island town and (2856, 2103), (2679, 1214)", "dead ends")
true(ends == [(217, 2104), (2679, 1214), (2856, 2103)], "which are the settlements with one road: %s" % ends)
true(not (is_colour(roads_png, (200, 40, 30)) & ~land).any(), "no road pixel is off the land")

# -- the layers ----------------------------------------------------------------------------------------
r = layers["ranks"]
places = [r[name]["along_water_places"] for name in ("kingdom", "duchy", "county")]
has("There are %d such stretches: %d on kingdom borders" % (sum(places), places[0]), "borders along rivers")
has("%d on duchy borders" % places[1], "duchy borders along rivers")
has("and %d on county borders" % places[2], "county borders along rivers")
kms = [r[name]["along_water_px"] * 0.335 for name in ("kingdom", "duchy", "county")]
has("(about %d km of border), %d on duchy borders (%d km) and %d on county borders (%s km)" % (
    round(kms[0], -1), places[1], round(kms[1], -1), places[2], n(round(kms[2], -1))), "how long those stretches are (%.0f, %.0f, %.0f km)" % tuple(kms))
has("without running along it: %d, %d and %d times" % tuple(r[name]["crossings_of_water"] for name in ("kingdom", "duchy", "county")), "crossings of narrow water")
everything = load("All.png")
extra = 0
for colour in ((233, 0, 255), (110, 30, 180), (128, 128, 128)):
    extra += int((is_colour(everything, colour) & ~is_colour(roads_png, colour)).sum())
has("no other picture has: %s px" % n(extra), "border colour on the banks")
has("%d of the 700 lakes have such a body" % layers["lakes_with_body"], "lakes with a body")
has("the %d lakes too small" % (700 - layers["lakes_with_body"]), "lakes wholly narrow")
shown = layers["water_shown"]
has("%s of the water's 415,040 px show in `All.png` (%.1f%%)" % (n(shown), 100.0 * shown / 415040), "water showing")
true(shown == files["All.png"]["colours"]["blue"], "which is the blue of All.png")
under = layers["water_hidden_under"]
has("%s are under dots, %s under bridges, and %s under the lines of borders that cross lakes: %s under grey, %s under purple and %s under pink" % (
    n(under["dots"]), n(under["bridges"]), n(under["county"] + under["duchy"] + under["kingdom"]), n(under["county"]), n(under["duchy"]), n(under["kingdom"])), "what hides water")
true(under["roads"] == 0, "no water is under a road")
shares = [100.0 * r[name]["line_shown_px"] / r[name]["line_px"] for name in ("kingdom", "duchy", "county")]
has("%d%% of the kingdoms', %d%% of the duchies' and %d%% of the counties'" % tuple(round(v) for v in shares), "how much of the borders' lines show")
deepest = max(r[name]["deepest_hidden_px"] for name in r)
has("more than %.1f px (%.1f km)" % (deepest, deepest * 0.335), "how far a border's hidden middle is from its colour")
for name, wanted in (("Kingdoms.png", 23), ("Duchies.png", 58), ("Counties.png", 233), ("Settlements.png", 233)):
    picture = load(name)
    white = (picture >= 250).all(axis=2)
    four, eight = ndimage.label(white)[1], ndimage.label(white, structure=np.ones((3, 3)))[1]
    true(four == eight == wanted, "%s: white pieces by four neighbours %d, by eight %d (wanted %d)" % (name, four, eight, wanted))
# -- Continent.png ----------------------------------------------------------------------------------------
with open(FACTS + "/continent.json", encoding="utf-8") as handle:
    cont = json.load(handle)
entry = files["Continent.png"]
true(entry["colours"]["sea"] == cont["sea_px"] and entry["colours"]["white"] == cont["land_px"] and entry["colours"]["black"] == cont["line_px"] and entry["other"] == 0
     and entry["alpha"] == [255, 255], "Continent.png holds three colours and nothing else, as measured when it was made (sea %d, white %d, black %d)" % (
         entry["colours"]["sea"], entry["colours"]["white"], entry["colours"]["black"]))
true(entry["bytes"] == cont["bytes"], "the Continent.png in the folder is the one that was checked (%d bytes)" % entry["bytes"])
has("the mainland and the 14 islands alike: %s px" % n(cont["line_px"]), "the standard line's pixels")
has("Everything further than 7 px from land is sea: %s px" % n(cont["sea_px"]), "Continent.png's sea")
joins = cont["joins"]
has("That moved %d px of land: %d added and %d taken away, in patches of %d to %d px" % (
    cont["land_added"], cont["land_added"], cont["land_removed"], min(j["added"] for j in joins), max(j["added"] for j in joins)), "land moved at the joins")
true(cont["land_px"] == cont["old_land_px"] == facts["land"]["px"] and cont["land_added"] == cont["land_removed"], "the land's area is unchanged: %d px" % cont["land_px"])
has("the same ones but for %d" % cont["land_added"], "land moved, in the colours' section")
true(len(joins) == 13 and all(j["mended"] for j in joins), "joins mended: %d" % len(joins))
for j in joins:
    has("| (%d, %d) | %d px %s | %d |" % (j["at"][0], j["at"][1], j["jump"], j["towards"], j["added"]), "the join at %s" % (tuple(j["at"]),))
has("sideways by %d to %d px" % (min(j["jump"] for j in joins), max(j["jump"] for j in joins)), "the joins' jumps")
has("over %d to %d rows" % (min(j["rows"] for j in joins), max(j["rows"] for j in joins)), "the rows a join is mended over")
continent = load("Continent.png")
new_land = (continent == 255).all(axis=2)
differ = new_land != land
runs = ndimage.label(differ, structure=np.array([[0, 0, 0], [1, 1, 1], [0, 0, 0]]))
most = int(ndimage.sum_labels(differ, runs[0], index=np.arange(1, runs[1] + 1)).max())
has("the coast shifting by %d px at most" % most, "how far the coast moved at a join")
has("up to %d px away at the 13 joins" % most, "the same, among the things that may look like mistakes")
marks = (everything != coast).any(axis=2)
places, n_places = ndimage.label(ndimage.binary_dilation(differ, structure=np.ones((3, 3), dtype=bool), iterations=6), structure=np.ones((3, 3), dtype=bool))
near = ndimage.binary_dilation(differ, structure=np.ones((3, 3), dtype=bool), iterations=3)
with_marks = sorted({int(round(ndimage.center_of_mass(places == i)[0] / 400.0)) * 400 for i in np.unique(places[marks & near]) if i})
busy = sorted(j["at"][1] for j in joins if any(abs(j["at"][1] - y) < 5 for y in with_marks))
true(len(set(np.unique(places[marks & near]).tolist()) - {0}) == 4, "another picture draws something within 3 px of the changed land at 4 of the 13 joins (rows %s)" % with_marks)
dark = coast.astype(np.int32).sum(axis=2) < 200
apart = dark & (ndimage.distance_transform_edt(~land) > 8.99)
strokes = ndimage.label(apart, structure=np.ones((3, 3)))[1]
print("      the drawing's dark ink 9 px or more from land: %d px in %d pieces" % (apart.sum(), strokes))
# -- AllSimple.png ----------------------------------------------------------------------------------------
with open(FACTS + "/allsimple.json", encoding="utf-8") as handle:
    simple = json.load(handle)
entry = files["AllSimple.png"]
true(entry["other"] == 0 and entry["alpha"] == [255, 255], "AllSimple.png holds nine colours and nothing else, none of it transparent")
true(entry["bytes"] == simple["bytes"] and entry["colours"]["blue"] == simple["colours"]["water"] and entry["colours"]["black"] == simple["colours"]["black"],
     "the AllSimple.png in the folder is the one that was checked (%d bytes)" % entry["bytes"])
has("but for %d px at four of the 13 joins" % simple["marks_differ_px"], "marks that differ from All.png's")
true(len(simple["marks_differ_at"]) == 4, "which are in %d places" % len(simple["marks_differ_at"]))
ends = sum(v["in_all"] for v in simple["runs_off_the_land"].values())
has("in the other pictures: %d places" % ends, "rivers' mouths and borders' ends at the coast")
has("%s of the water's 415,040 px show." % n(entry["colours"]["blue"]), "water showing in AllSimple.png")
for (jx, jy), words in (((1749, 400), "%d px differ |"), ((438, 800), "the same. %d px differ |"), ((1941, 3600), "the same. %d px differ |"), ((2686, 2400), "%d px differ |")):
    near = min(simple["marks_differ_at"], key=lambda m: abs(m["at"][0] - jx) + abs(m["at"][1] - jy))
    true(abs(near["at"][0] - jx) + abs(near["at"][1] - jy) < 40, "marks differ near the join (%d, %d)" % (jx, jy))
    row = [line for line in text.split("\n") if line.startswith("| (%d, %d) | " % (jx, jy)) and "differ" in line]
    true(len(row) == 1 and row[0].endswith(words % near["px"]), "the join (%d, %d): %d px differ" % (jx, jy, near["px"]))
has("a patch of purple, %d px, where a duchy border meets the coast" % simple["patch_not_drawn"], "the patch of purple")
has("%d px of it new" % simple["patch_end_carried"], "the border's end drawn in its place")
with open(OUT + "/counties_f3.pickle", "rb") as handle:
    solved = pickle.load(handle)
strip = solved["duchy"][2380:2400, 2677:2701] == 20
county_there = set(np.unique(np.load(OUT + "/county_map_f3.npy")[2380:2400, 2677:2701][strip]).tolist())
has("still count the strip (%d km²) with duchy 20 and county %d" % (round(strip.sum() * 0.335 * 0.335), min(county_there)), "the strip of land under the patch (%d px)" % strip.sum())
widths = strip.sum(axis=1)
has("a strip of land %d px wide" % round(float(np.median(widths[widths > 0]))), "the strip's width")
# -- the rivers as they are drawn, the lakes with no outlet, the folder of source data -------------------------
def source(name):
    with open(SOURCE + "/" + name, encoding="utf-8") as handle:
        return json.load(handle)


river_file = source("Rivers.json")
lines = river_file["rivers"]
lengths = np.array([r["length_km"] for r in lines])
ends = [r["ends_in"] for r in lines]
measured = facts["rivers"]
true(measured["lines"] == len(lines) and measured["ends"] == {"sea": ends.count("sea"), "joins": ends.count("river"), "dry": ends.count("salt lake")} and abs(measured["km"] - lengths.sum()) < 0.5
     and abs(measured["longest_km"] - lengths.max()) < 0.05 and abs(measured["median_km"] - np.median(lengths)) < 0.05,
     "the measured figures count and measure the rivers as Rivers.json has them (%d lines, %.0f km)" % (len(lines), lengths.sum()))
has("**%d river lines.** %d reach the sea, %d are tributaries that join another river, and %d end in the desert's salt lake." % (
    len(lines), ends.count("sea"), ends.count("river"), ends.count("salt lake")), "the river lines as drawn")
has("**About %s km of river** in all, measured along the lines as drawn. The longest single line is %s km; half are under %d km." % (
    n(round(float(lengths.sum()), -2)), n(lengths.max()), int(np.ceil(np.median(lengths)))), "the rivers' lengths as drawn")
small = [r for r in lines if r["flow_m3s"][0] < 14.95]
has("%d lines begin so with less than 15 m³/s, the least with %d." % (len(small), round(min(r["flow_m3s"][0] for r in small))), "rivers that begin at a lake's outlet")
true(all(r["from_lake"] for r in small) and all(r["flow_m3s"][0] >= 14.95 for r in lines if not r["from_lake"]), "each of them runs out of a lake, and every other river carries 15 m3/s where it begins")
left = river_file["left_out"]
shore = [e for e in left if e["ends_in"] == "sea"]
has("**Fourteen streams that do carry 15 m³/s are too short to draw:** %d that reach the sea within 11 km of gathering it, and one that joins a larger river 2 px from where it gathers it. The largest of them carries %d m³/s." % (
    len(shore), round(max(e["flow_m3s"] for e in left))), "the streams too short to draw")
true(len(left) == 14 and len(left) - len(shore) == 1 and max(e["length_px"] for e in shore) * 0.335 < 11.0 and [e["length_px"] for e in left if e["ends_in"] != "sea"] == [2.0]
     and min(e["flow_m3s"] for e in left) >= 15.0, "they are 14: 13 at the shore, %.1f km long at most, and one of 2 px; each carries 15 m3/s or more" % (max(e["length_px"] for e in shore) * 0.335))
by_rank = sorted((r for r in lines if r["sea_rank"]), key=lambda r: r["sea_rank"])
rows = [line for line in text.split("\n") if re.match(r"\| \d+ \| [\d,]+ \| \d+ \| \(\d+, \d+\) \| \d \| \(\d+, \d+\) \| \d \|$", line)]
true(len(rows) == 14 and all(row.startswith("| %d | %s | %s | (" % (i, n(r["largest_flow_m3s"]), n(r["length_km"]))) and row.endswith(" | %d |" % r["to_kingdom"])
                            for i, (row, r) in enumerate(zip(rows, by_rank), start=1)), "the table of the 14 largest rivers gives each its water, its length as drawn and the kingdom it ends in")
lake_file = source("Lakes.json")["lakes"]
shut = [l for l in lake_file if not l["has_outlet"]]
craters = [l for l in shut if l["kind"] == "crater"]
has("**Seven lakes have no outlet.**", "the lakes with no outlet")
true(len(shut) == 7 and len(craters) == 6 and all(list(l["kingdoms"]) == ["2"] for l in craters) and [l["kind"] for l in shut if l["kind"] != "crater"] == ["salt"],
     "they are the salt lake and six crater lakes, all six in kingdom 2")
has("lakes of kingdom 2, %d to %d km² each, which no stream enters or leaves" % (round(min(l["km2"] for l in craters)), round(max(l["km2"] for l in craters))), "the crater lakes' sizes")
true(facts["lakes"]["no_outlet"]["craters"]["most_water_in_m3s"] < 0.05, "no cell brings water into a crater lake (the most: %.2f m3/s)" % facts["lakes"]["no_outlet"]["craters"]["most_water_in_m3s"])
part = text[text.index("## The source data"): text.index("## Decisions and assumptions")]
told = set(re.findall(r"`([A-Za-z0-9]+\.(?:png|json))`", part)) - set(files)
here = set(os.listdir(SOURCE)) - {"README.md"}
true(told == here and os.path.exists(SOURCE + "/README.md"), "the document's table of the source data names every file in SourceData/ and no other (%d files), and the folder has its README.md" % len(here))
road_file = source("Roads.json")
has("The %d rivers as lines" % len(lines), "the rivers in the source data")
has("The %d lakes |" % len(lake_file), "the lakes in the source data")
has("The %d watersheds |" % len(source("Watersheds.json")["watersheds"]), "the watersheds in the source data")
has("the %d roads and the %d bridges" % (len(road_file["roads"]), len(road_file["bridges"])), "the roads in the source data")
true(len(source("KingdomBorders.json")["borders"]) == 15, "the kingdoms' fifteen borders in the source data")
has("Rivers drawn from 15 m³/s up, and below every lake of 60 km² or more", "which rivers are drawn")
losing = [r for r in lines if r["largest_flow_m3s"] - r["flow_at_end_m3s"] > 0.5]
has("Seven rivers end with less than they carried higher up.", "rivers that lose water")
true(len(losing) == 7 and all(set(r["kingdoms"]) & {4, 5} for r in losing), "they are %d, each of them in the Desert or the Grassland" % len(losing))
eleventh = by_rank[10]
has("it carries %s m³/s at the most and brings %s to its mouth" % (n(eleventh["largest_flow_m3s"]), n(eleventh["flow_at_end_m3s"])), "river 11's water")
true([r["sea_rank"] for r in losing if r["sea_rank"] and r["sea_rank"] <= 14] == [11] and all(abs(r["largest_flow_m3s"] - r["flow_at_end_m3s"]) < 0.06 for r in by_rank[:14] if r["sea_rank"] != 11),
     "of the 14 largest rivers only river 11 brings less to its mouth than the most it carries")
has("| River | Most water it carries (m³/s) |", "the heading of the rivers' table")
has("The programs are in the folder `Scripts/`. Its `README.md` says which made what", "where the programs are")
true(os.path.exists(ROOT + "/MapCreation/Scripts/README.md") and os.path.exists(ROOT + "/MapCreation/Scripts/duchy/f3_build.py"),
     "the folder of programs is there, with its README.md and the program that builds this document")
true("{{" not in text, "no marker is left in the document")
print()
print("ALL RIGHT: the written figures are the measured ones" if not wrong else "WRONG: %s" % wrong)
