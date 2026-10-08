"""What the map's working data holds: the shape of every file that the pictures were drawn from.

Usage: e0_inventory.py <scratch out dir>
"""
import pickle
import sys
import numpy as np

OUT = sys.argv[1]


def describe(value, depth=0, name="", limit=12):
    pad = "   " * depth
    if isinstance(value, np.ndarray):
        extra = ""
        if value.size and value.dtype.kind in "biuf":
            extra = " min %s max %s" % (value.min(), value.max())
        print("%s%s: array %s %s%s" % (pad, name, value.shape, value.dtype, extra))
    elif isinstance(value, dict):
        keys = list(value.keys())
        print("%s%s: dict of %d; keys %s%s" % (pad, name, len(keys), [str(k)[:28] for k in keys[:limit]], " ..." if len(keys) > limit else ""))
        if depth < 3:
            shown = 0
            for key in keys:
                if shown >= (limit if depth == 0 else 3):
                    break
                describe(value[key], depth + 1, str(key)[:40])
                shown += 1
    elif isinstance(value, (list, tuple)):
        print("%s%s: %s of %d" % (pad, name, type(value).__name__, len(value)))
        if len(value) and depth < 3:
            describe(value[0], depth + 1, "[0]")
    else:
        text = repr(value)
        print("%s%s: %s %s" % (pad, name, type(value).__name__, text[:110]))


for path in ("water/water2.pickle", "duchy2/county_list_f3.pickle", "duchy2/settlements.pickle", "duchy2/capital_candidates.pickle", "duchy2/county_shapes_f3.pickle",
             "roads2/network.pickle", "roads2/towns.pickle", "roads2/drawn.pickle", "king30/lines_u3.pickle"):
    print("=== %s" % path)
    with open(OUT + "/" + path, "rb") as handle:
        describe(pickle.load(handle))
for path in ("water/drawn2.npz", "water/grid2.npz", "water/grid1.npz", "duchy2/fields1.npz", "duchy2/fields2.npz", "king30/fields.npz"):
    print("=== %s" % path)
    with np.load(OUT + "/" + path, allow_pickle=True) as data:
        for key in data.files:
            describe(data[key], 1, key)
for path in ("duchy2/county_map_f3.npy", "duchy2/duchy_map.npy", "king30/kingdoms_u3.npy", "roads2/flow.npy", "roads2/town.npy", "region_map.npy"):
    describe(np.load(OUT + "/" + path), 0, path)
print("=== duchy2/counties_f3.pickle (top level only)")
with open(OUT + "/duchy2/counties_f3.pickle", "rb") as handle:
    solved = pickle.load(handle)
describe(solved, 0, "counties_f3", limit=20)
