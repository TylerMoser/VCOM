"""The forests alone as shapes, for m2_scene.gd to make into the scene's nodes: SourceData/Forests.json
cut into pieces by the counties as the scene has them (../scene/forestshapes.py, which m1_shapes.py
uses too, with the counties it makes). Cut by the scene's own outlines, the pieces fit the land as it
is, even after a hand edit to a county or the coast; while the land is as the program made it, they
are the very pieces a scene made afresh would have.

Usage: f2_shapes.py <MapCreation dir> <the map's scene, .tscn> <shapes .json to write>
"""
import json
import re
import sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scene"))
import forestshapes  # noqa: E402

MC, SCENE, WRITE_TO = sys.argv[1:4]
LAND = re.compile(r'^\[node name="County(\d+)(?:Island\d+)?" type="Polygon2D" parent="Land/Kingdom(\d+)/Duchy(\d+)"[^\]]*\]\n'
                  r'(?:[^\[\n][^\n]*\n)*?polygon = PackedVector2Array\(([^)]*)\)', re.M)


def counties_of(text):
    """The counties as the scene has them: their numbers and their outlines (the county's own and any
    island's), in the scene's units."""
    found = {}
    for m in LAND.finditer(text):
        number = int(m.group(1))
        c = found.setdefault(number, {"number": number, "kingdom": int(m.group(2)), "duchy": int(m.group(3)), "pieces": []})
        c["pieces"].append(np.array([float(v) for v in m.group(4).split(",")]).reshape(-1, 2))
    return [found[n] for n in sorted(found)]


with open(SCENE, encoding="utf-8") as handle:
    counties = counties_of(handle.read())
with open(Path(MC) / "SourceData" / "Forests.json", encoding="utf-8") as handle:
    forests = json.load(handle)
pieces, figures = forestshapes.shapes(forests, counties)
with open(WRITE_TO, "w", encoding="utf-8", newline="\n") as handle:
    json.dump({"about": "The forests alone, as m1_shapes.py gives them in the whole map's shapes, cut by the counties of %s; points in "
                        "the scene's units." % Path(SCENE).name, "forests": pieces, "forest_figures": figures}, handle, separators=(",", ":"))
print("counties read from the scene: %d (%d outlines)" % (len(counties), sum(len(c["pieces"]) for c in counties)))
print("wrote %s: %d pieces (%s), %d points; cut in two to be drawable %d times and for size %d, %d dropped (%.2f km2), %d slivers left out; "
      "by kind, km2: %s" % (WRITE_TO, figures["pieces"], ", ".join("%s %d" % kv for kv in figures["by_group"].items()), figures["points"],
                            figures["cut_in_two"], figures["split_for_size"], figures["dropped"], figures["dropped_km2"], figures["slivers"],
                            ", ".join("%s %.0f" % kv for kv in figures["by_kind_km2"].items())))
