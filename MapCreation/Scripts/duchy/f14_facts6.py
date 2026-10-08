"""The measured figures once more, with the rivers counted and measured as they are drawn.

f1_facts.py counted the river lines the water was worked out as (305) and measured them from
cell to cell. Fourteen of those are too short to draw, and a drawn line, smoothed and wandering,
is not as long as its cells' zigzag. The source data's Rivers.json holds the lines as drawn
(drawing them gives the picture's river pixels exactly), so the figures are taken from there.
The lakes with no outlet are counted too.

Usage: f14_facts6.py <scratch out dir> <staged source data> <facts to read> <facts to write>
"""
import json
import os
import pickle
import shutil
import sys
import numpy as np

OUT, SRC, OLD, NEW = sys.argv[1:5]
os.makedirs(NEW, exist_ok=True)
for name in ("layers.json", "continent.json", "allsimple.json", "kingdoms.md"):
    shutil.copyfile(OLD + "/" + name, NEW + "/" + name)
with open(OLD + "/facts.json", encoding="utf-8") as handle:
    facts = json.load(handle)
with open(SRC + "/Rivers.json", encoding="utf-8") as handle:
    rivers = json.load(handle)
with open(SRC + "/Lakes.json", encoding="utf-8") as handle:
    lakes = json.load(handle)["lakes"]

lines = rivers["rivers"]
old = facts["rivers"]
print("as it was: %d lines, ends %s, %.0f km, longest %.0f km, middle %.1f km, 100 km or more %d" % (
    old["lines"], old["ends"], old["km"], old["longest_km"], old["median_km"], old["lines_over_100km"]))
print("a mouth as it was:", old["mouths"][0])
lengths = np.array([r["length_km"] for r in lines])
ends = {"sea": sum(r["ends_in"] == "sea" for r in lines), "joins": sum(r["ends_in"] == "river" for r in lines), "dry": sum(r["ends_in"] == "salt lake" for r in lines)}
by_rank = sorted((r for r in lines if r["sea_rank"]), key=lambda r: r["sea_rank"])
mouths = []
for mouth, river in zip(old["mouths"], by_rank):
    assert abs(mouth["flow"] - river["largest_flow_m3s"]) < 0.06, (mouth["flow"], river["largest_flow_m3s"])
    assert abs(mouth["from"][0] - river["points"][0][0]) <= 1 and abs(mouth["from"][1] - river["points"][0][1]) <= 1, (mouth["from"], river["points"][0])
    assert mouth["kingdom"] == river["to_kingdom"], (mouth["kingdom"], river["to_kingdom"], river["id"])
    mouths.append(dict(mouth, km=river["length_km"], km_along_cells=mouth["km"], river=river["id"], from_kingdom=river["from_kingdom"], at_mouth=river["flow_at_end_m3s"]))
shore = [e for e in rivers["left_out"] if e["ends_in"] == "sea"]
facts["rivers"] = dict(old, lines=len(lines), ends=ends, km=float(lengths.sum()), longest_km=float(lengths.max()), median_km=float(np.median(lengths)),
                       lines_over_100km=int((lengths >= 100.0).sum()), mouths=mouths,
                       worked_out={"lines": old["lines"], "ends": old["ends"], "km_along_cells": old["km"]},
                       not_drawn={"lines": len(rivers["left_out"]), "at_the_shore": len(shore), "most_flow_at_the_shore": max(e["flow_m3s"] for e in shore),
                                  "joining_a_river": len(rivers["left_out"]) - len(shore), "longest_at_the_shore_km": max(e["length_px"] for e in shore) * 0.335,
                                  "joining_px": max(e["length_px"] for e in rivers["left_out"] if e["ends_in"] != "sea"), "most_flow": max(e["flow_m3s"] for e in rivers["left_out"])})
with open(SRC + "/Drainage.json", encoding="utf-8") as handle:
    drainage_lakes = {l["id"]: l for l in json.load(handle)["lakes"]}
drawn_lakes = {l["id"]: l for l in lakes}
small = [r for r in lines if r["flow_m3s"][0] < 14.95]
for r in small:                                          # each runs out of a lake of 60 km2 or more
    assert r["from_lake"] and max(drainage_lakes[d]["km2"] for d in drawn_lakes[r["from_lake"]]["drainage_lakes"]) >= 60.0, r["id"]
assert all(r["flow_m3s"][0] >= 14.95 for r in lines if not r["from_lake"])
facts["rivers"]["from_lakes_under_15"] = {"lines": len(small), "least_flow": min(r["flow_m3s"][0] for r in small), "points": sum(1 for r in lines for v in r["flow_m3s"] if v < 14.95),
                                          "least_at_an_end": min(r["flow_at_end_m3s"] for r in lines)}
print("rivers that begin at a lake's outlet with less than 15 m3/s:", facts["rivers"]["from_lakes_under_15"])
losing = [r for r in lines if r["largest_flow_m3s"] - r["flow_at_end_m3s"] > 0.5]
assert all(set(r["kingdoms"]) & {4, 5} for r in losing), "a river loses water outside the Desert and the Grassland"
facts["rivers"]["losing_water"] = {"lines": len(losing), "rivers": [{"id": r["id"], "sea_rank": r["sea_rank"], "most": r["largest_flow_m3s"], "at_end": r["flow_at_end_m3s"]} for r in losing]}
print("rivers that end with less than the most they carry:", facts["rivers"]["losing_water"])
new = facts["rivers"]
assert new["worked_out"]["lines"] - new["not_drawn"]["lines"] == new["lines"]
print("as drawn:  %d lines, ends %s, %.0f km, longest %.1f km, middle %.2f km, 100 km or more %d; not drawn %s" % (
    new["lines"], new["ends"], new["km"], new["longest_km"], new["median_km"], new["lines_over_100km"], new["not_drawn"]))
for i, m in enumerate(mouths, start=1):
    print("   river %d: %.0f m3/s, %.1f km as drawn (%.0f from cell to cell), from %s in kingdom %d to %s in kingdom %d" % (
        i, m["flow"], m["km"], m["km_along_cells"], m["from"], m["from_kingdom"], m["at"], m["kingdom"]))

# The lakes with no outlet, and whether any stream runs into the craters.
with open(OUT + "/water/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
flow, lake_flat, to, sea = water["flow_flat"], water["lake_flat"], water["to"], water["sea"]
shut = [l for l in lakes if not l["has_outlet"]]
craters = [l for l in shut if l["kind"] == "crater"]
salt = [l for l in shut if l["kind"] == "salt"]
assert len(shut) == 7 and len(craters) == 6 and len(salt) == 1
runs_in = to < sea
most_in, most_inside = 0.0, 0.0
for lake in craters:
    for working in lake["drainage_lakes"]:
        mine = lake_flat == working
        entering = runs_in & ~mine
        entering[entering] = mine[to[entering]]
        most_in = max(most_in, float(flow[entering].max()) if entering.any() else 0.0)
        most_inside = max(most_inside, float(flow[mine].max()))
print("lakes with no outlet: %s; the most water any cell brings into a crater lake: %.2f m3/s; the most passing through a cell of one: %.2f m3/s" % (
    [(l["id"], l["kind"], l["km2"], list(l["kingdoms"])) for l in shut], most_in, most_inside))
facts["lakes"]["no_outlet"] = {"count": len(shut), "salt": {"id": salt[0]["id"], "km2": salt[0]["km2"]},
                               "craters": {"count": len(craters), "least_km2": min(l["km2"] for l in craters), "most_km2": max(l["km2"] for l in craters),
                                           "kingdoms": sorted({k for l in craters for k in l["kingdoms"]}), "most_water_in_m3s": most_in}}
with open(NEW + "/facts.json", "w", encoding="utf-8", newline="\n") as handle:
    json.dump(facts, handle, indent=1, ensure_ascii=False)
print("wrote", NEW + "/facts.json")
