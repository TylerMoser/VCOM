"""The fine print of the working data, before it is exported: how records are laid out and whether
the pieces agree with each other.

Usage: e1_details.py <scratch out dir>
"""
import collections
import pickle
import sys
import numpy as np

OUT = sys.argv[1]
with open(OUT + "/water/water2.pickle", "rb") as handle:
    water = pickle.load(handle)
rows, cols, to, flow, z = water["rows"], water["cols"], water["to"], water["flow_flat"], water["z"]
print("water: factor %d; land cells %d; to: %s %s min %d max %d; sea: %s" % (
    water["factor"], len(rows), to.shape, to.dtype, to.min(), to.max(), type(water["sea"]).__name__ + " " + str(getattr(water["sea"], "shape", water["sea"]))))
ok = to < water["sea"]
dr, dc = rows[to[ok]] - rows[ok], cols[to[ok]] - cols[ok]
print("   cells that drain to another: %d; steps longer than one cell: %d; cells that drain to the sea: %d; to == itself: %d" % (
    ok.sum(), ((np.abs(dr) > 1) | (np.abs(dc) > 1)).sum(), (~ok).sum(), (to == np.arange(len(to))).sum()))
far = ok.copy()
far[ok] = (np.abs(dr) > 1) | (np.abs(dc) > 1)
if far.any():
    reach = np.hypot(rows[to[far]] - rows[far], cols[to[far]] - cols[far])
    print("   the longer steps: %d cells, up to %.0f cells long; of them starting in a lake: %d" % (far.sum(), reach.max(), (water["lake_flat"][far] > 0).sum()))
print("   lake_flat: %s; z: %s min %.1f max %.1f; height grid %s" % (water["lake_flat"].dtype, z.dtype, z.min(), z.max(), water["height"].shape))
print("lakes: %d records; kinds %s" % (len(water["lakes"]), dict(collections.Counter(l["kind"] for l in water["lakes"]))))
for lake in water["lakes"][:3]:
    print("   %s" % {k: (v if not hasattr(v, "__len__") or isinstance(v, str) else "len %d" % len(v)) for k, v in lake.items()})
print("   shut lakes: %s" % [(l["id"], l["kind"], round(l["km2"])) for l in water["lakes"] if l["shut"]])
print("sheds: %s" % water["sheds"][0])
print("reaches: ends %s; cells per reach: %d to %d" % (dict(collections.Counter(r["end"] for r in water["reaches"])), min(len(r["cells"]) for r in water["reaches"]), max(len(r["cells"]) for r in water["reaches"])))

with open(OUT + "/king30/lines_u3.pickle", "rb") as handle:
    lines = pickle.load(handle)
print("kingdom lines: codes %s" % lines["codes"])
print("   curve 0 first points %s ... last %s; cells 0 first %s" % (lines["curves"][0][:2].tolist(), lines["curves"][0][-1].tolist(), lines["cells"][0][:2].tolist()))
print("   meet %s" % lines["meet"])
print("   points per curve: %s" % [len(c) for c in lines["curves"]])

with open(OUT + "/duchy2/county_list_f3.pickle", "rb") as handle:
    listing = pickle.load(handle)
print("county list: of_duchy[:8] %s; seats[1:4] %s" % (listing["of_duchy"][:8].tolist(), listing["seats"][1:4]))
with open(OUT + "/duchy2/settlements.pickle", "rb") as handle:
    settlements = pickle.load(handle)
print("settlements: moved[0] %s; capital %s; duchy_seat[1..3] %s" % (settlements["moved"][0], settlements["capital"], [settlements["duchy_seat"][d] for d in (1, 2, 3)]))
with open(OUT + "/duchy2/capital_candidates.pickle", "rb") as handle:
    candidates = pickle.load(handle)
print("capital candidates[0]: %s" % candidates[0])
with open(OUT + "/roads2/network.pickle", "rb") as handle:
    network = pickle.load(handle)
first = next(iter(network["laid"].items()))
print("road %s: path[:3] %s, km %.1f, highway %s, ferry %s, alone_km %s" % (first[0], first[1]["path"][:3], first[1]["km"], first[1]["highway"], first[1]["ferry"], first[1]["alone_km"]))
print("   order[:3] %s; roads with ferry: %s" % (network["order"][:3], [k for k, v in network["laid"].items() if v["ferry"]]))

# Do the regions' maps agree with each other?
fields = np.load(OUT + "/duchy2/fields1.npz")
king, island_king = fields["king"], fields["island_king"]
county = np.load(OUT + "/duchy2/county_map_f3.npy")
with open(OUT + "/duchy2/counties_f3.pickle", "rb") as handle:
    duchy = pickle.load(handle)["duchy"]
land = (king > 0) | (island_king > 0)
country = np.where(king > 0, king, island_king)
of_duchy = np.asarray(listing["of_duchy"])
kingdom_of_duchy = np.zeros(45, dtype=int)
for row in candidates:
    kingdom_of_duchy[row["duchy"]] = row["kingdom"]
print("land %d px; county 0 on land: %d; county set off land: %d" % (land.sum(), ((county == 0) & land).sum(), ((county > 0) & ~land).sum()))
print("duchy of each pixel's county against the duchies' map: differ on %d land px (mainland %d)" % (
    (of_duchy[county] != duchy)[land].sum(), ((of_duchy[county] != duchy) & (king > 0)).sum()))
print("kingdom of each pixel's county against the kingdoms' map: differ on %d land px" % (kingdom_of_duchy[of_duchy[county]] != country)[land].sum())
kingdoms_u3 = np.load(OUT + "/king30/kingdoms_u3.npy")
print("kingdoms_u3 against fields1 king: differ on %d px" % (kingdoms_u3 != king).sum())
ridge, divide = fields["ridge"], fields["divide"]
kfields = np.load(OUT + "/king30/fields.npz")
print("feature lines, px: ridge %d, watershed %d, spur %d, brook %d" % (ridge.sum(), divide.sum(), kfields["spur"].sum(), kfields["brook"].sum()))
drawn = np.load(OUT + "/water/drawn2.npz")
print("drawn water: river %d px, lakes %d px, both %d; fields1 river %d lake %d; same river: %s; same lake: %s" % (
    drawn["river"].sum(), drawn["lakes"].sum(), (drawn["river"] & drawn["lakes"]).sum(), fields["river"].sum(), fields["lake"].sum(),
    bool((fields["river"] == (drawn["river"] & ~drawn["lakes"])).all()), bool((fields["lake"] == drawn["lakes"]).all())))
flow_full = np.load(OUT + "/roads2/flow.npy")
coarse = water["flow"]
up = np.repeat(np.repeat(coarse, 2, axis=0), 2, axis=1)[:4000, :3100]
print("full-size flow against the half-size one doubled: largest difference %.3f; equal on %.1f%% of px" % (np.abs(flow_full - up).max(), 100.0 * (np.abs(flow_full - up) < 1e-3).mean()))
