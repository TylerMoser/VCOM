"""List the counties' seats by duchy, for the notes. Usage: c9_list.py <duchy out dir> <tag>"""
import pickle
import sys
import numpy as np

OUT, TAG = sys.argv[1], sys.argv[2]
with open(OUT + "/county_list_%s.pickle" % TAG, "rb") as handle:
    listing = pickle.load(handle)
with open(OUT + "/counties_%s.pickle" % TAG, "rb") as handle:
    data = pickle.load(handle)
fields = np.load(OUT + "/fields1.npz")
king = fields["king"]
county = np.load(OUT + "/county_map_%s.npy" % TAG)
of_duchy, seats = listing["of_duchy"], listing["seats"]
wrong = [c for c in range(1, len(seats)) if county[seats[c][1], seats[c][0]] != c]
print("seats not inside their own county: %s" % wrong)
on_water = [c for c in range(1, len(seats)) if fields["river"][seats[c][1], seats[c][0]] or fields["lake"][seats[c][1], seats[c][0]]]
print("seats on water: %s" % on_water)
line = {}
for number in sorted(data["results"]):
    kingdom = int(np.bincount(king[data["duchy"] == number]).argmax())
    mine = [c for c in range(1, len(seats)) if of_duchy[c] == number]
    line.setdefault(kingdom, []).append("D%d %s" % (number, " ".join("(%d,%d)" % (int(seats[c][0]), int(seats[c][1])) for c in mine)))
for kingdom in sorted(line):
    print("K%d: %s" % (kingdom, "; ".join(line[kingdom])))
print("the isles' seat: %s" % (seats[-1],))
near = []
for c in range(1, len(seats)):
    for d in range(c + 1, len(seats)):
        gap = np.hypot(seats[c][0] - seats[d][0], seats[c][1] - seats[d][1]) * 0.335
        if gap < 12.0:
            near.append((round(float(gap), 1), c, d))
print("pairs of seats under 12 km apart: %s" % sorted(near))
