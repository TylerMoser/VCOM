"""The villages and hamlets alone as shapes, for m2_scene.gd to make into the scene's nodes: what
m1_shapes.py puts into the whole map's shapes for them, worked out of SourceData/Villages.json by
the same code (../scene/villageshapes.py), so that villages added to the scene as it is are the
very nodes a scene made afresh would have.

Usage: v2_shapes.py <MapCreation dir> <shapes .json to write>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scene"))
import villageshapes  # noqa: E402

MC, WRITE_TO = sys.argv[1:3]
with open(Path(MC) / "SourceData" / "Villages.json", encoding="utf-8") as handle:
    places, lanes, bridges, channels = villageshapes.shapes(json.load(handle))
with open(WRITE_TO, "w", encoding="utf-8", newline="\n") as handle:
    json.dump({"about": "The villages and hamlets alone, as m1_shapes.py gives them in the whole map's shapes.",
               "villages": places, "lanes": lanes, "lane_bridges": bridges, "channels": channels}, handle, separators=(",", ":"))
print("wrote %s: %d villages, %d hamlets, %d lanes (%d points), %d bridges on them, %d channels (%d points)" % (
    WRITE_TO, sum(p["kind"] == "village" for p in places), sum(p["kind"] == "hamlet" for p in places), len(lanes),
    sum(len(l["points"]) // 2 for l in lanes), len(bridges), len(channels), sum(len(c["points"]) // 2 for c in channels)))
