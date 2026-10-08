"""Source data, part 4: the kingdoms' fifteen borders as the smooth lines they were drawn from,
and every figure that was measured off the pictures for Features.md.

Usage: e5_borders.py <MapCreation dir> <scratch out dir> <folder to write to> <facts dir>
"""
import json
import os
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
from sourcefiles import save_json, kept, KM

Image.MAX_IMAGE_PIXELS = None
MAPS, OUT, TO, FACTS = sys.argv[1:5]
with open(OUT + "/king30/lines_u3.pickle", "rb") as handle:
    lines = pickle.load(handle)
kingdoms = np.asarray(Image.open(MAPS + "/Kingdoms.png").convert("RGB"))
coast = np.asarray(Image.open(MAPS + "/WorldMapV1.png").convert("RGB"))
new_land = (np.asarray(Image.open(MAPS + "/Continent.png").convert("RGB")) == 255).all(axis=2)
kingdom_map = np.asarray(Image.open(TO + "/KingdomMap.png")).astype(np.int32)
pink = (kingdoms == (233, 0, 255)).all(axis=2)
land = (coast >= 250).all(axis=2)
h, w = land.shape
to_pink = ndimage.distance_transform_edt(~pink)
to_land, to_sea = ndimage.distance_transform_edt(~new_land), ndimage.distance_transform_edt(new_land)
meets = [(float(x), float(y)) for y, x in lines["meet"]]
borders, covered = [], np.zeros_like(pink)
worst, between = 0.0, 0.0
for curve, code in zip(lines["curves"], lines["codes"]):
    a, b = divmod(int(code), 10)
    points = np.round(np.asarray(curve, dtype=np.float64), 2)    # (y, x)
    cells = np.rint(points).astype(int)
    cy, cx = np.clip(cells[:, 0], 0, h - 1), np.clip(cells[:, 1], 0, w - 1)
    ends = []
    for end, (ey, ex) in ((points[0], (cy[0], cx[0])), (points[-1], (cy[-1], cx[-1]))):
        near = [i for i, (mx, my) in enumerate(meets, start=1) if np.hypot(end[1] - mx, end[0] - my) < 3.0]
        if near:
            ends.append({"meeting_place": near[0]})
        else:
            assert new_land[ey, ex] and land[ey, ex] and to_sea[ey, ex] <= 1.0, (code, ey, ex)   # on the last pixel of land
            ends.append({"coast": [float(end[1]), float(end[0])]})
    worst = max(worst, float(to_pink[cy, cx].max()))
    covered[cy, cx] = True
    # The kingdoms either side of the line, a few pixels off it: are they the two it is said to part?
    step = np.gradient(points, axis=0)
    step /= np.maximum(np.hypot(step[:, 0], step[:, 1]), 1e-9)[:, None]
    sides = set()
    right = 0
    for sign in (-1.0, 1.0):
        off = np.rint(points + sign * 4.0 * np.column_stack([-step[:, 1], step[:, 0]])).astype(int)
        seen = kingdom_map[np.clip(off[:, 0], 0, h - 1), np.clip(off[:, 1], 0, w - 1)]
        seen = seen[seen > 0]
        counts = np.bincount(seen, minlength=10)
        sides.add(int(counts.argmax()))
        right += int(counts.max())
        between += len(seen)
    assert sides == {a, b}, (code, sides)
    km = float(np.hypot(*np.diff(points, axis=0).T).sum()) * KM
    borders.append({"kingdoms": [a, b], "km": round(km, 1), "starts_at": ends[0], "ends_at": ends[1],
                    "points": [[float(x), float(y)] for y, x in points]})
to_curve = ndimage.distance_transform_edt(~covered)
far = float(to_curve[pink & land].max())
places = []
for i, (mx, my) in enumerate(meets, start=1):
    three = sorted({k for border in borders for k in border["kingdoms"]
                    if border["starts_at"].get("meeting_place") == i or border["ends_at"].get("meeting_place") == i})
    places.append({"id": i, "at": [mx, my], "kingdoms": three})
    assert len(three) == 3, three
coast_ends = [e for border in borders for e in (border["starts_at"], border["ends_at"]) if "coast" in e]
print("kingdom borders: %d lines, %.0f km, %d points; no point of a line is further than %.1f px from the pink of Kingdoms.png, and no pink on land further than %.1f px from a line; each line has its two kingdoms on its two sides" % (
    len(borders), sum(b["km"] for b in borders), sum(len(b["points"]) for b in borders), worst, far))
print("meeting places: %s" % [(p["at"], p["kingdoms"]) for p in places])
print("ends at the coast: %d, each on the last pixel of land, on the hand-drawn coast and on the standard outline alike: %s" % (len(coast_ends), [e["coast"] for e in coast_ends]))
save_json(TO + "/KingdomBorders.json", {
    "about": "The fifteen borders between kingdoms as smooth lines, each from a place where three kingdoms meet, or from the coast, to another. They are the lines the pink of Kingdoms.png was drawn along, 5 px wide.",
    "fields": {"kingdoms": "the two kingdoms the line parts", "points": "[x, y] in pixels of the map, about a pixel apart, along the middle of the border", "km": "length along the line",
               "starts_at, ends_at": "the meeting place it runs from or to (by id), or the point where it ends at the coast: the last pixel of land, on the hand-drawn coast and on the standard outline alike. A line is to be carried on from there across the coast's own line; the pictures draw it 3 px on"},
    "note": "Duchies' and counties' borders have no lines of their own: they are where DuchyMap.png and CountyMap.png change from one number to another. Where a kingdom's border and KingdomMap.png's edge differ by a pixel, the map is the one the duchies and counties were made on.",
    "meeting_places": places, "borders": borders})

merged = {"about": "Every figure measured off the pictures and the working data for Features.md, as it stood on 2026-10-07. facts: sizes, heights, water, regions, settlements, roads, and what each picture file holds. layers: how All.png is put together. continent: Continent.png and the 13 joins. allsimple: AllSimple.png. Areas of regions here are counted on the hand-drawn coast (CountyMapAsDrawn.png)."}
for key, name in (("facts", "facts.json"), ("layers", "layers.json"), ("continent", "continent.json"), ("allsimple", "allsimple.json")):
    with open(FACTS + "/" + name, encoding="utf-8") as handle:
        merged[key] = json.load(handle)
with open(TO + "/Measurements.json", "w", encoding="utf-8", newline="\n") as handle:
    json.dump(merged, handle, indent=1, ensure_ascii=False)
    handle.write("\n")
print("wrote Measurements.json: %d bytes" % os.path.getsize(TO + "/Measurements.json"))
