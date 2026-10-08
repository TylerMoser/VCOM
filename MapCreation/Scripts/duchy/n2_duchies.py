"""Share each kingdom of Kingdoms2.png out among its duchies, keeping the duchies it had.

The kingdoms' borders have moved, so each kingdom is shared out again by the same rule as before
(realm.py: land goes to the seat cheapest to reach), from the seats and the head starts the
duchies had. A seat stays where it was unless the new border has made its site worse: it now
lies outside its kingdom, on water, or within 14 km of the kingdom's border where it did not
before. Such a seat is moved to the best site near the middle of its own share, as seats were
first found (d2_solve.py). The head starts are then adjusted only as far as is needed for the
duchies to be as even as they were before the borders moved.

Usage: n2_duchies.py <old duchy out dir> <new duchy out dir>
"""
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor
import numpy as np

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
from realm import Realm

KM = 0.335
MOVES = 6
EVEN = 0.03              # a kingdom whose duchies were more even than this before is held to this
STEP = 5.0               # km a head start is moved at a time
ISLES = 20000            # px of islands that make a kingdom the one with the great isles
ISLE_EVEN = 0.02         # how even that kingdom's duchies are held
NAMES = ("height", "river", "lake", "divide", "ridge", "cross", "going", "seat")


def solve(task):
    k, box, mask, islands, fields, old_worth, old_seats, old_starts, was_off = task
    realm = Realm(mask, fields, KM, islands)
    count = len(old_seats)
    dry = realm.seat_worth > -50.0
    seats, worse = [], []
    for d, (x, y) in enumerate(old_seats):
        sy, sx = y - box[0].start, x - box[1].start
        cell = realm.cell_at(sy, sx) if 0 <= sy < mask.shape[0] and 0 <= sx < mask.shape[1] else -1
        if cell < 0 or not dry[cell]:
            cell = realm.nearest_dry(sy, sx)
            worse.append(d)
        elif realm.seat_worth[cell] < old_worth[sy, sx] - 1.0:
            worse.append(d)
        seats.append(cell)
    seats = np.array(seats)
    starts = np.array(old_starts, dtype=np.float64)
    target = max(was_off, EVEN)
    if int(islands.sum()) >= ISLES:
        # The kingdom with the great isles: they are a county by themselves, of a size that cannot
        # change, so the duchy they belong to must not be much larger than its neighbours or its
        # other counties would all be larger than the isles.
        target = min(target, ISLE_EVEN)
    notes = []
    for move in range(MOVES if worse else 0):
        starts, owner, off = realm.even_out(seats, starts, near_enough=max(target, 0.12), tries=14)
        if np.bincount(owner, minlength=count).min() == 0:
            raise RuntimeError("kingdom %d: a duchy's seat was swallowed by its neighbours" % k)
        moved = seats.copy()
        for d in worse:
            moved[d] = realm.best_seat(owner, d)
        if (moved == seats).all():
            break
        seats = moved
    first = realm.sizes(realm.claim(seats, starts), count)
    first_off = float(np.abs(first - first.mean()).max() / first.mean())
    # Small steps, so the shares that come out are the nearest to the old ones that are even enough.
    # A head start is held within 70 km, as it was; more is allowed only if the shares cannot be
    # made even enough without.
    for most in (70.0, 90.0, 110.0):
        starts, owner, off = realm.even_out(seats, starts, near_enough=target, tries=90, step=STEP, most=most)
        if off <= target:
            break
    if np.bincount(owner, minlength=count).min() == 0 or any(int(owner[s]) != d for d, s in enumerate(seats)):
        raise RuntimeError("kingdom %d: a duchy's seat was swallowed by its neighbours" % k)
    realm.claim(seats, starts)
    size = realm.sizes(owner, count) * KM * KM
    new_seats = [(int(realm.cols[s]) + box[1].start, int(realm.rows[s]) + box[0].start) for s in seats]
    moved_far = [round(float(np.hypot(a[0] - b[0], a[1] - b[1])) * KM, 1) for a, b in zip(old_seats, new_seats)]
    grid = realm.on_grid(owner).astype(np.int8)
    islands_at = (realm.island_at[0] + box[0].start, realm.island_at[1] + box[1].start)
    return {"kingdom": k, "box": box, "owner": grid, "seats": new_seats, "starts": starts, "km2": size, "off": off, "target": target,
            "features": realm.on_features(owner), "far": float(realm.far.mean()), "worse": worse, "moved_km": moved_far, "first_off": first_off,
            "islands": (islands_at, owner[realm.island_cell] if realm.island_cell.size else None),
            "seat_in_own": [int(owner[s]) == d for d, s in enumerate(seats)]}


if __name__ == "__main__":
    OLD, NEW = sys.argv[1], sys.argv[2]
    full = dict(np.load(NEW + "/fields1.npz"))
    old_seat_worth = np.load(OLD + "/fields1.npz")["seat"]
    with open(OLD + "/duchies_all.pickle", "rb") as handle:
        old = pickle.load(handle)
    h, w = full["king"].shape
    tasks = []
    for k in sorted(old):
        mask = full["king"] == k
        islands = full["island_king"] == k
        rows = np.flatnonzero((mask | islands).any(axis=1)); cols = np.flatnonzero((mask | islands).any(axis=0))
        box = (slice(max(rows[0] - 3, 0), min(rows[-1] + 4, h)), slice(max(cols[0] - 3, 0), min(cols[-1] + 4, w)))
        size = old[k]["km2"]
        was_off = float(np.abs(size - size.mean()).max() / size.mean())
        tasks.append((k, box, mask[box], islands[box], {name: full[name][box] for name in NAMES}, old_seat_worth[box],
                      [(int(x), int(y)) for x, y in old[k]["seats"]], old[k]["starts"], was_off))
    t0 = time.time()
    results = {}
    with ProcessPoolExecutor(max_workers=5) as pool:
        for r in pool.map(solve, tasks):
            k = r["kingdom"]
            owner = np.full((h, w), -1, dtype=np.int8)
            owner[r["box"]] = r["owner"]
            results[k] = {"owner": owner, "seats": r["seats"], "starts": r["starts"], "km2": r["km2"], "islands": r["islands"]}
            print("kingdom %d: with the old head starts within %.1f%%; %d duchies of %s km2 (within %.1f%% of their mean; held to %.1f%%), %.0f%% of borders on features, land %.0f km from its seat; seats made worse by the new border: %s; seats moved by km: %s; every seat in its own duchy: %s; head starts %s (were %s)  (%.0fs)" % (
                k, 100 * r["first_off"], len(r["seats"]), np.round(r["km2"]).astype(int).tolist(), 100 * r["off"], 100 * r["target"], 100 * r["features"], r["far"],
                r["worse"], r["moved_km"], all(r["seat_in_own"]), np.round(r["starts"], 1).tolist(), np.round(old[k]["starts"], 1).tolist(),
                time.time() - t0), flush=True)
    with open(NEW + "/duchies_all.pickle", "wb") as handle:
        pickle.dump(results, handle)
    print("saved")
