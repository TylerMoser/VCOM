"""Put Features.md together: the written part (a template) with the tables made from the
figures f1_facts.py measured, so no table is typed by hand.

Usage: f3_build.py <duchy out dir> <facts out dir> <template> <file to write>
"""
import json
import pickle
import sys
import numpy as np
from scipy import ndimage

OUT, FACTS, TEMPLATE, WRITE_TO = sys.argv[1:5]
KM2 = 0.335 * 0.335
with open(FACTS + "/facts.json", encoding="utf-8") as handle:
    facts = json.load(handle)


def n(value):
    return format(int(round(value)), ",")


def runs(numbers):
    """1, 2, 3, 7 as "1 to 3, and 7"."""
    numbers = sorted(numbers)
    out, start = [], numbers[0]
    for a, b in zip(numbers, numbers[1:] + [None]):
        if b != a + 1:
            out.append("%d to %d" % (start, a) if a > start else "%d" % a)
            start = b
    return ", and ".join(out)


parts = {}

# The files and what each colour counts to in them.
order = ["WorldMapV1.png", "WorldMapRegions.png", "Continent.png", "Kingdoms.png", "Rivers.png", "Water.png", "Duchies.png", "Counties.png", "Settlements.png", "Roads.png", "All.png", "AllSimple.png"]
keys = [("sea", "Sea"), ("white", "White"), ("pink", "Pink"), ("purple", "Purple"), ("grey", "Grey"), ("blue", "Blue"), ("brown", "Brown"), ("red", "Red"), ("umber", "Dark brown")]
lines = ["| File | " + " | ".join(title for _, title in keys) + " | Other shades |", "|---|" + "---:|" * (len(keys) + 1)]
for name in order:
    entry = facts["files"][name]
    lines.append("| `%s` | " % name + " | ".join(n(entry["colours"][key]) if entry["colours"][key] else "" for key, _ in keys) + " | %s |" % n(entry["other"] + entry["colours"]["black"]))
parts["FILES"] = "\n".join(lines)
lines = ["| File | Pixels | Kind | Size on disk |", "|---|---|---|---:|"]
for name in order[:4] + ["Elevation.png"] + order[4:]:
    entry = facts["files"][name]
    lines.append("| `%s` | %d × %d | %s | %s bytes |" % (name, entry["size"][0], entry["size"][1],
                 "16-bit greyscale PNG" if entry["mode"] == "I;16" else "8-bit RGBA PNG", n(entry["bytes"])))
parts["FILE_SIZES"] = "\n".join(lines)

# Islands, with the county each belongs to.
county = np.load(OUT + "/county_map_f3.npy")
with open(OUT + "/county_list_f3.pickle", "rb") as handle:
    of_duchy = np.asarray(pickle.load(handle)["of_duchy"])
lines = ["| Island | Area (km²) | Pixels | Middle (x, y) | County | Duchy |", "|---:|---:|---:|---|---:|---:|"]
for i, island in enumerate(facts["islands"], start=1):
    x, y = island["at"]
    window = county[max(y - 3, 0): y + 4, max(x - 3, 0): x + 4]
    c = int(np.bincount(window[window > 0]).argmax())
    lines.append("| %d | %s | %s | (%d, %d) | %d | %d |" % (i, n(island["km2"]), n(island["px"]), x, y, c, int(of_duchy[c])))
parts["ISLANDS"] = "\n".join(lines)

parts["KINGDOMS"] = open(FACTS + "/kingdoms.md", encoding="utf-8").read().strip()
lines = ["| Kingdom | Duchies | Duchy sizes (km²) | Counties in each duchy | County sizes (km²) | Duchy numbers | County numbers |", "|---:|---:|---|---:|---|---|---|"]
for k in facts["kingdoms"]:
    mine = [c for c in facts["counties"] if c["kingdom"] == k["number"]]
    per = sorted({d["counties"] for d in facts["duchies"] if d["kingdom"] == k["number"]})
    lines.append("| %d | %d | %s to %s | %s | %s to %s | %s | %s |" % (
        k["number"], k["duchies"], n(min(k["duchy_km2"])), n(max(k["duchy_km2"])), " or ".join(str(p) for p in per),
        n(min(k["county_km2"])), n(max(k["county_km2"])), runs(k["duchy_numbers"]), runs([c["number"] for c in mine])))
parts["KINGDOM_SIZES"] = "\n".join(lines)
stands = {1: "the largest river any of its duchy capitals has, in the north of the kingdom",
          2: "the middle of the kingdom, on the largest river any of its duchy capitals has",
          3: "the main valley: its lowest duchy capital, on its biggest river",
          4: "where the desert's river reaches the salt lake",
          5: "its main river, in the lowlands",
          6: "the island's greatest river, a little above its mouth",
          7: "the harbour at the mouth of the swamp's main river",
          8: "the middle of the kingdom, on a mid-sized river",
          9: "its main river"}
lines = ["| Kingdom | Capital (x, y) | Duchy | County | Stands on | River there (m³/s) | Height (m) | To the sea (km) |", "|---:|---|---:|---:|---|---:|---:|---:|"]
for k in facts["kingdoms"]:
    lines.append("| %d | (%d, %d) | %d | %d | %s | %s | %d | %d |" % (
        k["number"], k["capital"][0], k["capital"][1], k["capital_duchy"], k["capital_county"], stands[k["number"]],
        n(k["river_at_capital"]), round(k["height_at_capital"]), round(k["sea_from_capital"])))
parts["CAPITALS"] = "\n".join(lines)

runoff = {1: 0.52, 2: 0.33, 3: 1.05, 4: 0.006, 5: 0.06, 6: 2.1, 7: 0.65, 8: 0.42, 9: 1.35}
steep = {1: 21, 2: 10, 3: 33, 4: 3.6, 5: 2.3, 6: 4.4, 7: 0.05, 8: 12, 9: 6.5}
lines = ["| Kingdom | Biome | Under water | Lakes | Rivers | Number of lakes | Run-off assumed (m a year) | Slope aimed at (m per km) |", "|---:|---|---:|---:|---:|---:|---:|---:|"]
for k in facts["kingdoms"]:
    lines.append("| %d | %s | %.1f%% | %.1f%% | %.1f%% | %d | %s | %s |" % (
        k["number"], k["biome"], 100 * k["water"], 100 * k["lakes"], 100 * k["rivers"], k["lake_count"], runoff[k["number"]], steep[k["number"]]))
lines.append("| all | | %.2f%% | %.2f%% | %.2f%% | %d | | |" % (100 * facts["water"]["share"], 100 * facts["water"]["lake_share"], 100 * facts["water"]["river_share"], facts["lakes"]["count"]))
parts["WATER"] = "\n".join(lines)

notes = {(2098, 1509): "the desert's salt lake: no outlet", (1549, 266): "the flooded caldera among the volcanoes"}
lines = ["| Lake | Area (km²) | Middle (x, y) | Kingdom | Note |", "|---:|---:|---|---:|---|"]
for i, lake in enumerate(facts["lakes"]["largest"], start=1):
    lines.append("| %d | %s | (%d, %d) | %d | %s |" % (i, n(lake["km2"]), lake["at"][0], lake["at"][1], lake["kingdom"], notes.get(tuple(lake["at"]), "")))
parts["LAKES"] = "\n".join(lines)
fields = np.load(OUT + "/fields1.npz")
country = np.where(fields["king"] > 0, fields["king"], fields["island_king"])
lines = ["| River | Most water it carries (m³/s) | Length of its main line (km) | Drawn from (x, y) | Starts in kingdom | Mouth (x, y) | Ends in kingdom |", "|---:|---:|---:|---|---:|---|---:|"]
for i, river in enumerate(facts["rivers"]["mouths"], start=1):
    lines.append("| %d | %s | %s | (%d, %d) | %d | (%d, %d) | %d |" % (i, n(river["flow"]), n(river["km"]), river["from"][0], river["from"][1],
                 int(country[river["from"][1], river["from"][0]]), river["at"][0], river["at"][1], river["kingdom"]))
parts["RIVERS"] = "\n".join(lines)

peaks = {1: (2620, (905, 876)), 2: (2794, (1320, 510)), 3: (3352, (1947, 2157)), 4: (1529, (1774, 1507)), 5: (1688, (2050, 2176)),
         6: (1017, (802, 1320)), 7: (1032, (1324, 1833)), 8: (2130, (1981, 2509)), 9: (1022, (1932, 3227))}
lines = ["| Kingdom | Biome | Lowest (m) | Median (m) | Highest (m) | Highest point (x, y) |", "|---:|---|---:|---:|---:|---|"]
for k in facts["kingdoms"]:
    lines.append("| %d | %s | %d | %d | %s | (%d, %d) |" % (k["number"], k["biome"], round(k["height"][0]), round(k["height"][1]), n(peaks[k["number"]][0]), *peaks[k["number"]][1]))
    assert abs(peaks[k["number"]][0] - k["height"][2]) < 1.0
parts["HEIGHTS"] = "\n".join(lines)

lines = ["| Duchy | Kingdom | Capital (x, y) | Its dot | Area (km²) | Counties | Counties' numbers | Height at capital (m) |", "|---:|---:|---|---|---:|---:|---|---:|"]
for d in facts["duchies"]:
    lines.append("| %d | %d | (%d, %d) | %s | %s | %d | %s | %s |" % (
        d["number"], d["kingdom"], d["seat"][0], d["seat"][1], "pink: also the kingdom's capital" if d["rank"] == "kingdom" else "purple",
        n(d["km2"]), d["counties"], runs(d["county_numbers"]), n(d["height_at_seat"])))
parts["DUCHIES"] = "\n".join(lines)
lines = ["| County | Duchy | Kingdom | Capital (x, y) | Dot | Area (km²) | Height (m) | Roads | Sea (km) | Nearest river (km) |", "|---:|---:|---:|---|---|---:|---:|---:|---:|---:|"]
for c in facts["counties"]:
    lines.append("| %d | %d | %d | (%d, %d) | %s | %s | %s | %d | %d | %s |" % (
        c["number"], c["duchy"], c["kingdom"], c["at"][0], c["at"][1], {"kingdom": "pink", "duchy": "purple", "county": "grey"}[c["rank"]],
        n(c["km2"]), n(c["height"]), c["roads"], round(c["sea_km"]), "%d" % round(c["river_km"]) if c["river_km"] < 60 else "over 60"))
parts["COUNTIES"] = "\n".join(lines)

# The rivers as drawn, and the lakes with no outlet: figures the written part gives in passing.
r = facts["rivers"]
assert r["not_drawn"]["lines"] == 14 and r["not_drawn"]["joining_a_river"] == 1
parts["RIVER_LINES"] = "%d" % r["lines"]
parts["RIVERS_TO_SEA"], parts["RIVERS_JOINING"], parts["RIVERS_DRY"] = "%d" % r["ends"]["sea"], "%d" % r["ends"]["joins"], "%d" % r["ends"]["dry"]
parts["RIVERS_NOT_DRAWN"], parts["RIVERS_NOT_DRAWN_SHORE"] = "Fourteen", "%d" % r["not_drawn"]["at_the_shore"]
parts["RIVERS_NOT_DRAWN_FLOW"] = "%d" % round(r["not_drawn"]["most_flow"])
parts["RIVERS_KM"] = n(round(r["km"], -2))
parts["RIVERS_SMALL"], parts["RIVERS_LEAST"] = "%d" % r["from_lakes_under_15"]["lines"], "%d" % round(r["from_lakes_under_15"]["least_flow"])
parts["RIVERS_LONGEST"] = n(r["longest_km"])
parts["RIVERS_HALF_UNDER"] = "%d" % int(np.ceil(r["median_km"]))
falling = [(i, m) for i, m in enumerate(r["mouths"], start=1) if m["flow"] - m["at_mouth"] > 0.5]
assert [i for i, _ in falling] == [11] and r["losing_water"]["lines"] == 7, falling
parts["RIVERS_LOSING"], parts["R11_MOST"], parts["R11_MOUTH"] = "Seven", n(falling[0][1]["flow"]), n(falling[0][1]["at_mouth"])
assert 0.30 < 1.0 - falling[0][1]["at_mouth"] / falling[0][1]["flow"] < 0.37                # "a third"
craters = facts["lakes"]["no_outlet"]["craters"]
parts["CRATERS_LEAST"], parts["CRATERS_MOST"] = "%d" % round(craters["least_km2"]), "%d" % round(craters["most_km2"])

if len(sys.argv) > 5:                                     # the parts by themselves, for whoever wants them
    PARTS_TO = sys.argv[5]
    with open(PARTS_TO, "wb") as handle:
        pickle.dump(parts, handle)
text = open(TEMPLATE, encoding="utf-8").read()
for key, value in parts.items():
    marker = "{{%s}}" % key
    assert marker in text, "the template has no %s" % marker
    text = text.replace(marker, value)
assert "{{" not in text, "a marker was left: %s" % text[text.index("{{"): text.index("{{") + 40]
with open(WRITE_TO, "w", encoding="utf-8", newline="\n") as handle:
    handle.write(text)
print("wrote %s: %d characters, %d lines" % (WRITE_TO, len(text), text.count("\n")))
