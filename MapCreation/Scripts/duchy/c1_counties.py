"""Share each duchy out among its counties, the way the kingdoms were shared among duchies.

Each duchy gets 4, 5 or 6 counties, whichever brings a county nearest COUNTY km2, so counties
come out much the same size across the whole island though the duchies do not. The duchy's own
seat stays as the seat of one of its counties; the others are found by trying scatterings, as
for the duchies (d2_solve.py), and the land goes to the seat cheapest to reach (realm.py).
Water and the lines of ridge are shared to their two sides, as they will be drawn. The best few
scatterings are then evened out once more as tidied for drawing (tidy.py), and the best of
those is kept, so the sizes found are the sizes drawn.

The two great islands off the swamp, with the islets nearer them than the mainland, are a
county of their own in the duchy they lie off. Every other islet goes with the nearest shore.

The duchies are worked on side by side, a process each, at the map's own size.

Usage: c1_counties.py <duchy out dir> <tag> [ease] [near enough] [duchy numbers, e.g. 3,17]
"""
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy import ndimage

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
from realm import Realm

COUNTY = 3150.0          # km2 a county is meant to be
STARTS = 32              # scatterings of seats tried per duchy
MOVES = 6                # times the seats are moved toward the middles of their shares
FINISHED = 3             # of the scatterings, how many are evened out as tidied
ISLES = 2000             # px: an island this big is one of the great isles
SPRAWL = 0.4             # what a scattering loses for each 1.0 its counties sprawl beyond discs
KM = 0.335
SEED = 20261011
NAMES = ("height", "river", "lake", "divide", "ridge", "cross", "going", "seat")


def judge(realm, seats, owner, off, near_enough):
    """A scattering's score, less the better: most of its borders on rivers, lakes and ridges,
    shares even enough, the land not needlessly far from its seats, the seats on good sites
    and the counties not sprawling."""
    count = len(seats)
    kept = realm.on_features(owner)
    worth = float(realm.seat_worth[seats[1:]].mean()) if count > 1 else 0.0
    sprawl = realm.sprawl(owner, count)
    mean_far = float(realm.far.mean())
    score = (-kept + 4.0 * max(off - near_enough, 0.0) + 0.003 * mean_far - 0.01 * worth
             + SPRAWL * (float(sprawl.mean()) - 1.0) + 0.5 * max(float(sprawl.max()) - 1.5, 0.0))
    return score, kept, mean_far, sprawl


def solve(task):
    """One duchy: its counties as a grid over its box, and their seats."""
    number, count, seat_xy, box, mask, fields, islets, ease, near_enough = task
    rng = np.random.default_rng(SEED + number)
    realm = Realm(mask, fields, KM, islets, ease=ease, to_sides=True)
    dry = realm.seat_worth > -50.0
    # The duchy's own seat is the first county's and is never moved.
    sy, sx = seat_xy[1] - box[0].start, seat_xy[0] - box[1].start
    fixed = realm.cell_at(sy, sx) if 0 <= sy < mask.shape[0] and 0 <= sx < mask.shape[1] else -1
    if fixed < 0 or not dry[fixed]:
        fixed = realm.nearest_dry(sy, sx)
    tried = []
    for start_number in range(STARTS):
        seats = [fixed]
        while len(seats) < count:                        # each new seat likelier the further from those placed
            gap = np.min([np.hypot(realm.rows - realm.rows[s], realm.cols - realm.cols[s]) for s in seats], axis=0)
            odds = gap ** 2 * dry
            seats.append(int(rng.choice(realm.n, p=odds / odds.sum())))
        seats = np.array(seats)
        starts = np.zeros(count)
        for move in range(MOVES):
            starts, owner, off = realm.even_out(seats, starts, near_enough=max(near_enough, 0.12), tries=12, step=14.0, most=40.0)
            empty = np.flatnonzero(np.bincount(owner, minlength=count) == 0)
            if empty.size:                               # a seat swallowed by its neighbours: set down afresh, far from the rest
                for d in empty:
                    if d == 0:
                        continue
                    others = np.delete(seats, d)
                    gap = np.min([np.hypot(realm.rows - realm.rows[s], realm.cols - realm.cols[s]) for s in others], axis=0)
                    seats[d] = int(np.argmax(gap * dry))
                starts = np.zeros(count)
                continue
            moved = np.array([fixed] + [realm.best_seat(owner, d, reach_km=16.0, pull_km=11.0) for d in range(1, count)])
            if (moved == seats).all():
                break
            seats = moved
        for d in range(1, count):
            if not dry[seats[d]]:
                seats[d] = realm.nearest_dry(realm.rows[seats[d]], realm.cols[seats[d]])
        starts, owner, off = realm.even_out(seats, starts, near_enough=near_enough, tries=40, step=14.0, most=40.0)
        owner = realm.claim(seats, starts)
        if np.bincount(owner, minlength=count).min() == 0:
            continue
        score = judge(realm, seats, owner, off, near_enough)[0]
        if not any((seats == t[1]).all() for t in tried):
            tried.append((score, seats.copy(), starts.copy()))
    tried.sort(key=lambda t: t[0])
    # The best few, evened out again as they will be drawn.
    finished = []
    for score, seats, starts in tried[:FINISHED]:
        starts, owner, off = realm.even_out(seats, starts, near_enough=near_enough, tries=40, step=14.0, most=40.0, tidied=True)
        if np.bincount(owner, minlength=count).min() == 0:
            continue
        realm.claim(seats, starts)                       # for how far the land is from its seats
        score, kept, mean_far, sprawl = judge(realm, seats, owner, off, near_enough)
        finished.append((score, seats, starts, owner, off, kept, mean_far, sprawl))
    score, seats, starts, owner, off, kept, mean_far, sprawl = min(finished, key=lambda t: t[0])
    size = realm.sizes(owner, count) * KM * KM
    return {"duchy": number, "box": box, "owner": realm.on_grid(owner).astype(np.int8), "off": off, "km2": size,
            "features": kept, "far": mean_far, "starts": starts, "sprawl": sprawl, "scatterings": len(tried),
            "seats": [(int(realm.cols[s]) + box[1].start, int(realm.rows[s]) + box[0].start) for s in seats]}


if __name__ == "__main__":
    OUT, TAG = sys.argv[1], sys.argv[2]
    ease = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
    near_enough = float(sys.argv[4]) if len(sys.argv) > 4 else 0.03
    only = [int(v) for v in sys.argv[5].split(",")] if len(sys.argv) > 5 else None
    full = dict(np.load(OUT + "/fields1.npz"))
    duchy = np.load(OUT + "/duchy_map.npy").astype(np.int16)
    with open(OUT + "/duchies_all.pickle", "rb") as handle:
        duchies = pickle.load(handle)
    seats = [None] + [seat for k in sorted(duchies) for seat in duchies[k]["seats"]]
    mainland = full["king"] > 0
    h, w = duchy.shape

    # Every island goes whole to one duchy; the great isles, and the islets nearer them than the
    # mainland, are a county of the duchy they lie off.
    islands = (duchy > 0) & ~mainland
    pieces, n = ndimage.label(islands, structure=np.ones((3, 3)))
    sizes = ndimage.sum_labels(islands, pieces, index=np.arange(1, n + 1))
    great = np.isin(pieces, np.flatnonzero(sizes >= ISLES) + 1)
    to_great = ndimage.distance_transform_edt(~great) if great.any() else np.full((h, w), 1e9)
    to_main = ndimage.distance_transform_edt(~mainland)
    isles = great.copy()
    for i in range(1, n + 1):
        mine = pieces == i
        duchy[mine] = int(np.bincount(duchy[mine]).argmax())
        if not great[mine].any() and to_great[mine].min() < to_main[mine].min():
            isles |= mine
    isle_duchy = int(np.bincount(duchy[isles]).argmax()) if isles.any() else 0
    duchy[isles] = isle_duchy
    print("the isles: %d islands, %.0f km2, a county of duchy %d" % (len(np.unique(pieces[isles])), isles.sum() * KM * KM, isle_duchy))

    tasks, plan = [], {}
    for number in range(1, len(seats)):
        mine = duchy == number
        km2 = float(mine.sum()) * KM * KM
        count = int(np.clip(round(km2 / COUNTY), 4, 6))
        if number == isle_duchy:
            count -= 1                                   # the isles are one of its counties already
        plan[number] = count
        if only and number not in only:
            continue
        on_main = mine & mainland
        islets = mine & islands & ~isles
        rows = np.flatnonzero((on_main | islets).any(axis=1)); cols = np.flatnonzero((on_main | islets).any(axis=0))
        box = (slice(max(rows[0] - 3, 0), min(rows[-1] + 4, h)), slice(max(cols[0] - 3, 0), min(cols[-1] + 4, w)))
        tasks.append((number, count, seats[number], box, on_main[box], {name: full[name][box] for name in NAMES}, islets[box],
                      ease, near_enough))
    print("%d duchies to share out; counties in all: %d" % (len(tasks), sum(plan.values()) + (1 if isle_duchy else 0)))

    t0 = time.time()
    results = {}
    with ProcessPoolExecutor(max_workers=14) as pool:
        for result in pool.map(solve, tasks):
            results[result["duchy"]] = result
            print("duchy %2d: %d counties of %s km2 (within %.1f%% of their mean), %.0f%% of borders on features, land %.0f km from its seat, sprawl %s  (%.0fs)" % (
                result["duchy"], len(result["seats"]), np.round(result["km2"]).astype(int).tolist(), 100 * result["off"],
                100 * result["features"], result["far"], np.round(result["sprawl"], 2).tolist(), time.time() - t0), flush=True)
    offs = np.array([r["off"] for r in results.values()]); kept = np.array([r["features"] for r in results.values()])
    sprawls = np.concatenate([r["sprawl"] for r in results.values()]); fars = np.array([r["far"] for r in results.values()])
    print("SUMMARY ease %.2f, near enough %.3f: worst duchy within %.1f%%, mean %.1f%%; duchies over: %d %s; borders on features %.1f%%; land %.1f km from its seat; sprawl mean %.3f, worst %.2f, over 1.5: %d" % (
        ease, near_enough, 100 * offs.max(), 100 * offs.mean(), int((offs > near_enough + 1e-9).sum()),
        sorted(d for d, r in results.items() if r["off"] > near_enough + 1e-9), 100 * kept.mean(), fars.mean(),
        sprawls.mean(), sprawls.max(), int((sprawls > 1.5).sum())))
    with open(OUT + "/counties_%s.pickle" % TAG, "wb") as handle:
        pickle.dump({"results": results, "isles": isles, "isle_duchy": isle_duchy, "duchy": duchy, "plan": plan,
                     "ease": ease, "near_enough": near_enough}, handle)
    print("saved")
