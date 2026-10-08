"""Source data, part 1: which county, duchy and kingdom every pixel of land belongs to, and the
tables that tie them together with their capitals.

The pictures' borders were drawn where these maps change from one number to another. The maps
were made on the hand-drawn coast (WorldMapV1.png). CountyMapAsDrawn.png is that map exactly.
CountyMap.png, DuchyMap.png and KingdomMap.png are the same fitted to the standard outline
(Continent.png), as AllSimple.png is drawn: land that the mended joins added takes the county
beside it, land they took away has none, and the strip of land at the join (2686, 2400) that
Duchies.png inked over goes to the county north of it.

Usage: e2_regions.py <MapCreation dir> <scratch out dir> <folder to write to>
"""
import json
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
from sourcefiles import save_json, save_grey, KM, KM2

Image.MAX_IMAGE_PIXELS = None
MAPS, OUT, TO = sys.argv[1:4]
EIGHT = np.ones((3, 3), dtype=bool)
BIOME = {1: "Tundra Mountains", 2: "Volcanic Mountains / Ruins", 3: "Temperate Mountains", 4: "Desert", 5: "Grassland",
         6: "Evergreen Temperate Rainforest", 7: "Swamp", 8: "Deciduous Forest", 9: "Tropical Rainforest"}

old = np.asarray(Image.open(MAPS + "/WorldMapV1.png").convert("RGB"))
cont = np.asarray(Image.open(MAPS + "/Continent.png").convert("RGB"))
old_land, new_land = (old >= 250).all(axis=2), (cont == 255).all(axis=2)
county = np.load(OUT + "/duchy2/county_map_f3.npy").astype(np.int32)
with open(OUT + "/duchy2/county_list_f3.pickle", "rb") as handle:
    listing = pickle.load(handle)
with open(OUT + "/duchy2/settlements.pickle", "rb") as handle:
    settled = pickle.load(handle)
with open(OUT + "/duchy2/capital_candidates.pickle", "rb") as handle:
    candidates = {row["duchy"]: row for row in pickle.load(handle)}
with open(OUT + "/facts5/facts.json", encoding="utf-8") as handle:
    facts = json.load(handle)
of_duchy = np.asarray(listing["of_duchy"]).astype(np.int32)
of_kingdom = np.zeros(45, dtype=np.int32)
for d, row in candidates.items():
    of_kingdom[d] = row["kingdom"]
assert ((county > 0) == old_land).all(), "the counties' map does not cover the hand-drawn land exactly"

# -- fitted to the standard outline ------------------------------------------------------------------------
fitted = county.copy()
strip = np.zeros_like(old_land)
strip[2380:2400, 2677:2701] = True
strip &= county == 103
assert strip.sum() == 106, strip.sum()
fitted[strip] = 101
_, (ny, nx) = ndimage.distance_transform_edt(fitted == 0, return_indices=True)
fitted = np.where(new_land, np.where(fitted > 0, fitted, fitted[ny, nx]), 0)
changed = fitted != county
print("the counties' map on the standard outline: %d px differ from the map as drawn: %d given a county (new land), %d given none (land gone), %d given another (the strip)" % (
    changed.sum(), ((county == 0) & (fitted > 0)).sum(), ((county > 0) & (fitted == 0)).sum(), ((county > 0) & (fitted > 0) & changed).sum()))
assert ((fitted > 0) == new_land).all()
# Every county in as many pieces as before, none of them a scrap.
for c in range(1, 221):
    before = ndimage.label(county == c, structure=EIGHT)[1]
    pieces, after = ndimage.label(fitted == c, structure=EIGHT)
    sizes = ndimage.sum_labels(fitted == c, pieces, index=np.arange(1, after + 1))
    if before != after or sizes.min() < 20:
        print("   county %d: %d pieces as drawn, %d fitted; smallest %d px" % (c, before, after, sizes.min()))
duchy = of_duchy[fitted]
kingdom = of_kingdom[duchy]
save_grey(TO + "/CountyMapAsDrawn.png", county)
save_grey(TO + "/CountyMap.png", fitted)
save_grey(TO + "/DuchyMap.png", duchy)
save_grey(TO + "/KingdomMap.png", kingdom)


def deepest(labels, count):
    """For each number on a map, the pixel furthest from the edge of its patch, and how far that is."""
    edge = np.zeros(labels.shape, dtype=bool)
    across, down = labels[:, :-1] != labels[:, 1:], labels[:-1, :] != labels[1:, :]
    edge[:, :-1] |= across; edge[:, 1:] |= across; edge[:-1, :] |= down; edge[1:, :] |= down
    depth = ndimage.distance_transform_edt(~edge)
    spots = ndimage.maximum_position(depth, labels, index=np.arange(1, count + 1))
    return [None] + [([int(x), int(y)], round(float(depth[y, x]) * KM, 1)) for y, x in spots]


# -- the tables --------------------------------------------------------------------------------------------
county_px = np.bincount(fitted.ravel(), minlength=221)
duchy_px = np.bincount(duchy.ravel(), minlength=45)
kingdom_px = np.bincount(kingdom.ravel(), minlength=10)
county_spot, duchy_spot, kingdom_spot = deepest(fitted, 220), deepest(duchy, 44), deepest(kingdom, 9)
mainland = ndimage.label(new_land)[0]
mainland = mainland == np.argmax(np.bincount(mainland.ravel())[1:]) + 1
measured = {c["number"]: c for c in facts["counties"]}
moved = {int(m[1]): m for m in settled["moved"]}
settlements = []
for c in range(1, 221):
    x, y = (int(v) for v in settled["centres"][c])
    sx, sy = (int(v) for v in listing["seats"][c])
    m = measured[c]
    assert fitted[y, x] == c and m["at"] == [x, y], c
    settlements.append({"county": c, "duchy": int(of_duchy[c]), "kingdom": int(of_kingdom[of_duchy[c]]), "rank": settled["rank"][c],
                        "x": x, "y": y, "site": [sx, sy], "on_island": bool(not mainland[y, x]), "height_m": round(m["height"], 1),
                        "sea_km": round(m["sea_km"], 1), "river_km": round(m["river_km"], 1), "lake_km": round(m["lake_km"], 1),
                        "largest_river_within_4_km_m3s": round(m["river"], 1), "roads": m["roads"]})
    if (sx, sy) != (x, y):
        assert c in moved, c
print("settlements: %d; drawn off their sites: %d; on an island: %s" % (
    len(settlements), sum(1 for s in settlements if s["site"] != [s["x"], s["y"]]), [s["county"] for s in settlements if s["on_island"]]))
counties = [{"number": c, "duchy": int(of_duchy[c]), "kingdom": int(of_kingdom[of_duchy[c]]), "px": int(county_px[c]), "km2": round(float(county_px[c] * KM2), 1),
             "capital_rank": settled["rank"][c], "capital": [s["x"], s["y"]], "point_inside": county_spot[c][0], "room_km": county_spot[c][1]}
            for c, s in zip(range(1, 221), settlements)]
duchies = []
for d in range(1, 45):
    mine = [c for c in range(1, 221) if of_duchy[c] == d]
    seat = int(settled["duchy_seat"][d])
    row = candidates[d]
    assert of_duchy[seat] == d
    duchies.append({"number": d, "kingdom": int(of_kingdom[d]), "capital_county": seat, "counties": mine, "px": int(duchy_px[d]), "km2": round(float(duchy_px[d] * KM2), 1),
                    "point_inside": duchy_spot[d][0], "room_km": duchy_spot[d][1]})
kingdoms = []
for k in range(1, 10):
    mine = [d for d in range(1, 45) if of_kingdom[d] == k]
    capital_duchy = int(settled["capital"][k])
    f = facts["kingdoms"][k - 1]
    assert of_kingdom[capital_duchy] == k and f["capital_duchy"] == capital_duchy and f["capital_county"] == int(settled["duchy_seat"][capital_duchy])
    kingdoms.append({"number": k, "biome": BIOME[k], "capital_duchy": capital_duchy, "capital_county": int(settled["duchy_seat"][capital_duchy]), "duchies": mine,
                     "counties": [c for c in range(1, 221) if of_kingdom[of_duchy[c]] == k], "px": int(kingdom_px[k]), "km2": round(float(kingdom_px[k] * KM2), 1),
                     "borders_kingdoms": f["beside"], "has_coast": f["coast"], "point_inside": kingdom_spot[k][0], "room_km": kingdom_spot[k][1]})
    print("   kingdom %d: furthest from its edge %s, %.0f km in; Features.md's point inside it %s" % (k, kingdom_spot[k][0], kingdom_spot[k][1], f["middle"]))
    assert kingdom[f["middle"][1], f["middle"][0]] == k
save_json(TO + "/Regions.json", {
    "about": "The nine kingdoms, 44 duchies and 220 counties: which belongs to which, their capitals and their sizes. Numbers are those of CountyMap.png, DuchyMap.png and KingdomMap.png, and of Features.md.",
    "sizes": "px counts the pixels of the map with that number (the standard outline); km2 is px times 0.112225. Features.md's areas were counted on the map as drawn (CountyMapAsDrawn.png): they differ by the 106 px strip (12 km2) that counts with county 103 and duchy 20 there and with county 101 and duchy 19 here, and by a few pixels at the mended joins.",
    "capitals": "A county's capital is a settlement (Settlements.json, by the county's number). A duchy's capital is the capital of its capital_county; a kingdom's is the capital of its capital_county, which is in its capital_duchy.",
    "fields": {"point_inside": "[x, y], the pixel of it furthest from its edge: a place for its name", "room_km": "how far that pixel is from the edge",
               "borders_kingdoms": "the kingdoms it shares a border with", "has_coast": "all nine have", "capital (of a county)": "[x, y] of its settlement"},
    "kingdoms": kingdoms, "duchies": duchies, "counties": counties})
save_json(TO + "/Settlements.json", {
    "about": "The 220 settlements on the map: one a county, its capital. They are numbered by their county.",
    "fields": {"rank": "kingdom, duchy or county: the highest thing it is the capital of (9, 35 and 176 of them). It is drawn as a disc of radius 13, 9 or 6 px in pink, purple or grey.",
               "x, y": "the middle of its dot as drawn, in pixels of the map", "site": "[x, y] where the settlement was sited; 16 dots stand a little off it, to keep clear of a border or the coast",
               "height_m": "the ground's height at the dot, from Elevation.png", "sea_km, river_km, lake_km": "straight-line distance to the sea, the nearest drawn river and the nearest lake",
               "largest_river_within_4_km_m3s": "the largest flow of any river within 12 px", "roads": "how many of the 351 roads between settlements end here"},
    "settlements": settlements})
print("regions: %d kingdoms (px %d to %d), %d duchies, %d counties (km2 %.0f to %.0f)" % (
    len(kingdoms), kingdom_px[1:].min(), kingdom_px[1:].max(), len(duchies), len(counties), min(c["km2"] for c in counties), max(c["km2"] for c in counties)))
