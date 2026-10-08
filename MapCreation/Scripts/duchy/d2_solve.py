"""Share each kingdom out among its duchies.

For each kingdom a number of seats (DUCHIES) is placed and each claims the land cheapest to
reach from it (realm.py), with head starts adjusted until the shares are about equal. Where the
seats go is found by trying: from several random starts, each seat is moved again and again to
the best site near the middle of its own share (a river town, a harbour, a lake shore), and the
start that ends with the land nearest its seats, by the going, is kept. That is done at half the
map's size; the borders are then worked out once more at full size from the same seats, on the
rivers and lakes exactly as they are drawn.

Usage: d2_solve.py <duchy out dir> [kingdoms, e.g. 3,7]
"""
import pickle
import sys
import time
import numpy as np

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
from realm import Realm

OUT = sys.argv[1]
ONLY = [int(v) for v in sys.argv[2].split(",")] if len(sys.argv) > 2 else list(range(1, 10))
# How many duchies each kingdom has: broken country (mountain valleys, swamp) makes many small
# lordships, empty country (tundra, lava, desert) few large ones.
DUCHIES = {1: 4, 2: 4, 3: 6, 4: 4, 5: 5, 6: 5, 7: 6, 8: 5, 9: 5}
STARTS = 24              # random starts tried per kingdom
MOVES = 7                # times the seats are moved toward the middles of their shares
NEAR_ENOUGH = 0.08       # shares within this of their mean are even enough: nearer would pull borders off their rivers
SEED = 20261010

half = dict(np.load(OUT + "/fields2.npz"))
full = dict(np.load(OUT + "/fields1.npz"))
rng = np.random.default_rng(SEED)
results = {}
t0 = time.time()
for k in ONLY:
    count = DUCHIES[k]
    realm = Realm(half["king"] == k, half, 0.67, half["island_king"] == k)
    tried = []
    for start_number in range(STARTS):
        # Seats scattered: each new one likelier the further it is from those already placed.
        seats = [int(rng.integers(realm.n))]
        while len(seats) < count:
            gap = np.min([np.hypot(realm.rows - realm.rows[s], realm.cols - realm.cols[s]) for s in seats], axis=0)
            seats.append(int(rng.choice(realm.n, p=gap ** 2 / (gap ** 2).sum())))
        seats = np.array(seats)
        starts = np.zeros(count)
        for move in range(MOVES):
            starts, owner, off = realm.even_out(seats, starts, near_enough=0.12, tries=14)
            empty = np.flatnonzero(np.bincount(owner, minlength=count) == 0)
            if empty.size:                               # a seat swallowed by its neighbours: set it down afresh, far from the rest
                for d in empty:
                    others = np.delete(seats, d)
                    gap = np.min([np.hypot(realm.rows - realm.rows[s], realm.cols - realm.cols[s]) for s in others], axis=0)
                    seats[d] = int(np.argmax(gap))
                starts = np.zeros(count)
                continue
            moved = np.array([realm.best_seat(owner, d) for d in range(count)])
            if (moved == seats).all():
                break
            seats = moved
        starts, owner, off = realm.even_out(seats, starts, near_enough=NEAR_ENOUGH, tries=40)
        owner = realm.claim(seats, starts)
        mean_far = float(realm.far.mean())
        kept = realm.on_features(owner)
        # Best is the start whose borders lie most on rivers, lakes and ridges, with shares even
        # enough and the land not needlessly far from its seats.
        tried.append((-kept + 4.0 * max(off - NEAR_ENOUGH, 0.0) + 0.0015 * mean_far, seats, starts, off, mean_far, kept))
        print("  kingdom %d, start %2d: %.0f%% of borders on features, shares within %.1f%%, land %.0f km from its seat" % (
            k, start_number + 1, 100 * kept, 100 * off, mean_far))
    _, seats, starts, off, mean_far, kept = min(tried, key=lambda t: t[0])

    # The same seats at the map's own size, on the water as drawn.
    big = Realm(full["king"] == k, full, 0.335, full["island_king"] == k)
    big_seats = []
    for s in seats:
        y, x = int(realm.rows[s]) * 2 + 1, int(realm.cols[s]) * 2 + 1
        cell = big.cell_at(y, x)
        if cell < 0 or big.seat_worth[cell] < -50:       # off the kingdom, or in the water: the nearest dry cell of it
            dry = np.flatnonzero(big.seat_worth > -50)
            cell = int(dry[np.argmin(np.hypot(big.rows[dry] - y, big.cols[dry] - x))])
        big_seats.append(cell)
    big_seats = np.array(big_seats)
    starts, owner, off = big.even_out(big_seats, starts, near_enough=NEAR_ENOUGH, tries=24)
    size = big.sizes(owner, count) * 0.335 * 0.335
    results[k] = {"owner": big.on_grid(owner).astype(np.int8), "seats": [(int(big.cols[s]), int(big.rows[s])) for s in big_seats],
                  "starts": starts, "km2": size, "islands": (big.island_at, owner[big.island_cell] if big.island_cell.size else None)}
    print("kingdom %d: %d duchies of %s km2 (within %.1f%% of their mean), %.0f%% of borders on features; seats at %s  (%.0fs)" % (
        k, count, np.round(size).astype(int).tolist(), 100 * off, 100 * big.on_features(owner), results[k]["seats"], time.time() - t0))

with open(OUT + "/duchies_%s.pickle" % ("all" if len(ONLY) == 9 else "_".join(str(k) for k in ONLY)), "wb") as handle:
    pickle.dump(results, handle)
print("saved")
