"""new_1's ground tiles, made by the ground collection's own code.

The ground collection (output/ground/, knowledge/GROUND.md) makes every image's
floor tiles: 16 x 16 x 16, land's top at z 15, its motifs rebuilt to repeat every
16 voxels from a clean swatch's colour, a core / edge / corner kit for each pair of
surfaces that meet, and its own reading of the seven treatments (TwoColor keeps
turf and soil apart, CratePalette matched within each material's range). new_1's
tiles are made by that collection's functions themselves, so they follow its
conventions exactly: noise, palette_source, shift, surface, mat_rgb, contour_a,
model and paint, taken unchanged from output/ground/generate.py (checked by its
hash) by parsing the file, not importing it (importing it would run its own
generator), and run here over new_1's rows. Nothing in that collection is changed.

new_1's floor: the meadow, the lighter patches of meadow scattered over it, and
the sandy path to the door; where the path meets the meadow and where a light
patch does, an edge, an outer corner and an inner corner of each (A, the meadow,
on local x < 8, as the collection's kits have it).
"""
import ast
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(r"C:/Users/tandm/Documents/Projects/VoxelRidgeInspiration")
GEN = ROOT / "output" / "ground" / "generate.py"
GEN_SHA256 = "a925b232af248857589163b488b71f9586d81463ae220acd479d163a926d992a"
TAKE = ("noise", "palette_source", "shift", "surface", "mat_rgb", "contour_a", "model", "paint")
CONSTANTS = ("STYLES", "WATER", "PAVING", "EARTH")

SRC = "new_1.jpg"
CAT = [
    {"source": SRC, "name": "New1_Ground_Meadow", "kind": "grass", "crop": [672, 556, 728, 580], "role": "surface",
     "canvas": [16, 16, 16]},
    {"source": SRC, "name": "New1_Ground_LightMeadow", "kind": "grass", "crop": [150, 545, 200, 575],
     "role": "surface", "canvas": [16, 16, 16]},
    {"source": SRC, "name": "New1_Ground_SandPath", "kind": "sand", "crop": [335, 650, 385, 720], "role": "surface",
     "canvas": [16, 16, 16]},
]
for contour in ("Edge", "OuterCorner", "InnerCorner"):
    CAT.append({"source": SRC, "name": "New1_Ground_Path" + contour, "kind": "transition", "role": "transition",
                "contour": contour, "materials": ["New1_Ground_Meadow", "New1_Ground_SandPath"],
                "crop": [380, 640, 420, 720], "canvas": [16, 16, 16]})
for contour in ("Edge", "OuterCorner", "InnerCorner"):
    CAT.append({"source": SRC, "name": "New1_Ground_LightPatch" + contour, "kind": "transition",
                "role": "transition", "contour": contour,
                "materials": ["New1_Ground_Meadow", "New1_Ground_LightMeadow"],
                "crop": [100, 515, 230, 625], "canvas": [16, 16, 16]})


def load():
    """The ground collection's functions, bound to new_1's rows and colours."""
    src = GEN.read_bytes()
    assert hashlib.sha256(src).hexdigest() == GEN_SHA256, "output/ground/generate.py has changed"
    tree = ast.parse(src.decode("utf-8"))
    crate = json.loads((ROOT / "knowledge" / "palettes" / "crate-palette.json").read_text())
    ns = {"math": math, "json": json, "Image": Image, "Counter": Counter, "ROOT": ROOT, "CRATE": crate,
          "BY": {r["name"]: r for r in CAT}, "COL": {}}
    for node in tree.body:
        keep = (isinstance(node, ast.FunctionDef) and node.name in TAKE) or \
               (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in CONSTANTS
                                                     for t in node.targets))
        if keep:
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(GEN), "exec"), ns)
    for r in CAT:
        if r["role"] == "surface":
            ns["COL"][r["name"]] = ns["palette_source"](r)
    return ns


def build_all():
    """[(row, style, {(x, y, z): palette index}, 256 RGBA palette, groups)] of every tile."""
    ns = load()
    out = []
    for r in CAT:
        for style in ns["STYLES"]:
            raw, refs = ns["model"](r, "Cartoon" in style)
            v, palette, groups = ns["paint"](raw, refs, style)
            out.append((r, style, v, palette, groups))
    return out
