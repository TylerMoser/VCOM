"""Put the duchies of a part run of n3_counties.py into the whole run's file.

Usage: n3_merge.py <new duchy out dir> <tag>
"""
import pickle
import sys
import numpy as np

NEW, TAG = sys.argv[1], sys.argv[2]
with open(NEW + "/counties_%s.pickle" % TAG, "rb") as handle:
    whole = pickle.load(handle)
with open(NEW + "/counties_%s_part.pickle" % TAG, "rb") as handle:
    part = pickle.load(handle)
assert (whole["duchy"] == part["duchy"]).all() and whole["plan"] == part["plan"]
for number, result in part["results"].items():
    was = whole["results"][number]
    print("duchy %d: was %s within %.1f%% (%s), now %s within %.1f%% (%s)" % (
        number, np.round(was["km2"]).astype(int).tolist(), 100 * was["off"], was["how"],
        np.round(result["km2"]).astype(int).tolist(), 100 * result["off"], result["how"]))
    whole["results"][number] = result
with open(NEW + "/counties_%s.pickle" % TAG, "wb") as handle:
    pickle.dump(whole, handle)
print("merged")
