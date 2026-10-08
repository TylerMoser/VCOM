"""Why one duchy's counties will not come out even: what the old seats give under larger limits on
the head starts, and each scattering's result.

Usage: n3_probe.py <old duchy out dir> <new duchy out dir> <duchy>
"""
import sys
import numpy as np

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
import n3_counties
from realm import Realm

OLD, NEW, NUMBER = sys.argv[1], sys.argv[2], int(sys.argv[3])
tasks, plan, isles, isle_duchy, duchy, before = n3_counties.prepare(OLD, NEW, "f3", [NUMBER], say=lambda *a: None)
number, count, seat_xy, box, mask, fields, islets, old_seats, old_starts, old_worth, old_sprawl = tasks[0]
realm = Realm(mask, fields, 0.335, islets, ease=1.0, to_sides=True)
print("duchy %d: %d cells of mainland (%.0f km2), islets %d cells; %d counties; duchy seat %s; old seats %s" % (
    number, realm.n, realm.n * 0.112225, int(islets.sum()), count, seat_xy, old_seats))
dry = realm.seat_worth > -50.0
fixed = realm.cell_at(seat_xy[1] - box[0].start, seat_xy[0] - box[1].start)
print("duchy seat's site worth %.1f; the best site in the duchy %.1f; share of dry cells %.2f" % (
    realm.seat_worth[fixed], realm.seat_worth.max(), dry.mean()))
seats = np.array([fixed] + [realm.cell_at(y - box[0].start, x - box[1].start) for x, y in old_seats[1:]])
print("old seats' cells: %s (a cell under nought is outside the duchy now)" % seats.tolist())
for d in range(1, count):
    if seats[d] < 0 or not dry[seats[d]]:
        sx, sy = old_seats[d]
        seats[d] = realm.nearest_dry(sy - box[0].start, sx - box[1].start)
for most in (40.0, 60.0, 80.0):
    for tidied in (False, True):
        starts, owner, off = realm.even_out(seats, np.array(old_starts, dtype=float), near_enough=0.03, tries=90, step=5.0, most=most, tidied=tidied)
        size = realm.sizes(owner, count) * 0.112225
        astray = [d for d, s in enumerate(seats) if int(owner[s]) != d]
        print("  old seats, head starts within %.0f km, %s: within %.1f%%; sizes %s; head starts %s; seats outside their county %s; sprawl %s" % (
            most, "tidied" if tidied else "as claimed", 100 * off, np.round(size).astype(int).tolist(), np.round(starts).astype(int).tolist(),
            astray, np.round(realm.sprawl(owner, count), 2).tolist()))
