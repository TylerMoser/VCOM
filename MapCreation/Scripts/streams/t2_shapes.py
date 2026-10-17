"""The streams alone as shapes, for m2_scene.gd to make into the scene's nodes: what m1_shapes.py
puts into the whole map's shapes for them, worked out of SourceData/Streams.json by the same code
(../scene/streamshapes.py), so that streams added to the scene as it is are the very nodes a scene
made afresh would have.

Usage: t2_shapes.py <MapCreation dir> <shapes .json to write>
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scene"))
import streamshapes  # noqa: E402

MC, WRITE_TO = sys.argv[1:3]
with open(Path(MC) / "SourceData" / "Streams.json", encoding="utf-8") as handle:
    streams, banks = streamshapes.shapes(json.load(handle))
with open(WRITE_TO, "w", encoding="utf-8", newline="\n") as handle:
    json.dump({"about": "The streams alone, as m1_shapes.py gives them in the whole map's shapes.", "streams": streams, "banks": banks},
              handle, separators=(",", ":"))
print("wrote %s: %d streams (%d with a width curve), %d banks along borders, %d points" % (
    WRITE_TO, len(streams), sum(1 for s in streams if s["widths"]), len(banks), sum(len(s["points"]) // 2 for s in streams)))
