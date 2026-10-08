"""Share each duchy out among its counties again, on the duchies as they now are, keeping the
counties it had where that still makes good counties.

Each duchy keeps its number of counties. Its counties are first tried with the seats and head
starts they had (c1_counties.py found them). A seat stays where it was unless the new borders
have made its site worse: it now lies outside its duchy, on water, or within 14 km of a
kingdom's border where it did not before. Such a seat is moved to the best site near the middle
of its own share, as seats were first found. The head starts are then adjusted, in small steps,
only as far as is needed for the counties to be within NEAR_ENOUGH of their duchy's mean, tidied
as they will be drawn (so a duchy that has not changed comes out exactly as it was), and then
tried a little either way to bring the borders back on to rivers, lakes and ridges.

The duchy is also shared out from scratch, as c1_counties.py does it. The old seats are kept
unless the fresh sharing is better by more than KEEP on c1_counties.py's own score (borders on
rivers, lakes and ridges, even shares, land near its seat, seats on good sites, counties not
sprawling), or the old seats cannot be made into even counties at all.

Usage: n3_counties.py <old duchy out dir> <new duchy out dir> <tag> [duchy numbers, e.g. 3,17]
"""
import pickle
import sys
import time
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from scipy import ndimage

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
import c1_counties
import n3_gates
from realm import Realm

COUNTY = c1_counties.COUNTY
ISLES = c1_counties.ISLES
KM = 0.335
MOVES = 6
EASE = 1.0
NEAR_ENOUGH = float(__import__("os").environ.get("N3_NEAR", "0.03"))   # (the isles' duchy is run again held closer: see n3_merge.py)
GATE = 0.04              # counties further than this from their duchy's mean are not good enough
SPRAWL_GATE = 1.6        # nor a county more sprawling than this, unless it was before
POLISH = 140             # head starts tried round the ones found
SIGMA = 4.0              # km: how far off those tries are
KEEP = 0.06              # how much better a fresh sharing must score before the old seats are given up
FINISHED = int(__import__("os").environ.get("N3_FINISHED", "6"))   # scatterings of a fresh search that are finished and looked at
LIMITS = (40.0, 60.0, 80.0)   # km a head start may be: the first that lets the old seats be evened
NAMES = c1_counties.NAMES


def finish(realm, seats, starts, count, most=40.0):
    """Even the shares out as they will be drawn; says whether the result will do."""
    starts, owner, off = realm.even_out(seats, starts, near_enough=NEAR_ENOUGH, tries=70, step=5.0, most=most, tidied=True)
    whole = np.bincount(owner, minlength=count).min() > 0
    astray = [d for d, s in enumerate(seats) if int(owner[s]) != d]
    sprawl = realm.sprawl(owner, count) if whole else np.full(count, 9.0)
    note = "within %.1f%%, seats outside their county %s, sprawl most %.2f, head starts %s" % (
        100 * off, astray, float(sprawl.max()), np.round(starts, 0).astype(int).tolist())
    return starts, owner, off, bool(whole and not astray and off <= GATE), sprawl, note


def polish(realm, seats, starts, owner, off, count, seed, most=40.0):
    """Try head starts a little either way, keeping any that scores better and is as even."""
    rng = np.random.default_rng(seed)
    realm.claim(seats, starts)
    best = c1_counties.judge(realm, seats, owner, off, NEAR_ENOUGH)[0]
    most_off = max(NEAR_ENOUGH, off)
    better = 0
    for _ in range(POLISH):
        trial = np.clip(starts + rng.normal(0.0, SIGMA, count), -most, most)
        got = realm.claim_tidied(seats, trial)
        size = realm.sizes(got, count)
        if np.bincount(got, minlength=count).min() == 0:
            continue
        trial_off = float(np.abs(size - size.mean()).max() / size.mean())
        if trial_off > most_off or any(int(got[s]) != d for d, s in enumerate(seats)):
            continue
        score = c1_counties.judge(realm, seats, got, trial_off, NEAR_ENOUGH)[0]
        if score < best - 1e-9:
            best, starts, owner, off = score, trial, got, trial_off
            better += 1
    return starts, owner, off, better


def search(number, count, fixed, box, realm, finished_most):
    """c1_counties.py's search from scratch, giving back every scattering it finishes, best
    first, and not only the best of them."""
    rng = np.random.default_rng(c1_counties.SEED + number)
    dry = realm.seat_worth > -50.0
    tried = []
    for start_number in range(c1_counties.STARTS):
        seats = [fixed]
        while len(seats) < count:
            gap = np.min([np.hypot(realm.rows - realm.rows[s], realm.cols - realm.cols[s]) for s in seats], axis=0)
            odds = gap ** 2 * dry
            seats.append(int(rng.choice(realm.n, p=odds / odds.sum())))
        seats = np.array(seats)
        starts = np.zeros(count)
        for move in range(c1_counties.MOVES):
            starts, owner, off = realm.even_out(seats, starts, near_enough=max(NEAR_ENOUGH, 0.12), tries=12, step=14.0, most=40.0)
            empty = np.flatnonzero(np.bincount(owner, minlength=count) == 0)
            if empty.size:
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
        starts, owner, off = realm.even_out(seats, starts, near_enough=NEAR_ENOUGH, tries=40, step=14.0, most=40.0)
        owner = realm.claim(seats, starts)
        if np.bincount(owner, minlength=count).min() == 0:
            continue
        score = c1_counties.judge(realm, seats, owner, off, NEAR_ENOUGH)[0]
        if not any((seats == t[1]).all() for t in tried):
            tried.append((score, seats.copy(), starts.copy()))
    tried.sort(key=lambda t: t[0])
    found = []
    for score, seats, starts in tried[:finished_most]:
        starts, owner, off = realm.even_out(seats, starts, near_enough=NEAR_ENOUGH, tries=40, step=14.0, most=40.0, tidied=True)
        if np.bincount(owner, minlength=count).min() == 0:
            continue
        realm.claim(seats, starts)
        score, features, far, sprawl = c1_counties.judge(realm, seats, owner, off, NEAR_ENOUGH)
        found.append({"duchy": number, "box": box, "owner": realm.on_grid(owner).astype(np.int8), "off": off,
                      "km2": realm.sizes(owner, count) * KM * KM, "features": features, "far": far, "starts": starts, "sprawl": sprawl,
                      "scatterings": len(tried), "score": score, "how": "searched", "most": 40.0,
                      "seats": [(int(realm.cols[s]) + box[1].start, int(realm.rows[s]) + box[0].start) for s in seats]})
    return sorted(found, key=lambda f: f["score"])


def solve(task):
    number, count, seat_xy, box, mask, fields, islets, old_seats, old_starts, old_worth, old_sprawl, old_room = task
    realm = Realm(mask, fields, KM, islets, ease=EASE, to_sides=True)
    dry = realm.seat_worth > -50.0

    def cell_of(x, y):
        sy, sx = y - box[0].start, x - box[1].start
        inside = 0 <= sy < mask.shape[0] and 0 <= sx < mask.shape[1]
        cell = realm.cell_at(sy, sx) if inside else -1
        if cell < 0 or not dry[cell]:
            return realm.nearest_dry(sy, sx), "off"
        if inside and realm.seat_worth[cell] < old_worth[sy, sx] - 1.0:
            return cell, "worse"
        return cell, ""

    fixed, _ = cell_of(*seat_xy)
    seats, worse, why = [fixed], [], {}
    for d in range(1, count):
        cell, state = cell_of(*old_seats[d])
        if cell in seats:                                # two seats come to one cell: set this one down far from the rest
            gap = np.min([np.hypot(realm.rows - realm.rows[s], realm.cols - realm.cols[s]) for s in seats], axis=0)
            cell, state = int(np.argmax(gap * dry)), "off"
        if state:
            worse.append(d)
            why[d] = state
        seats.append(cell)
    seats = np.array(seats)
    starts = np.array(old_starts, dtype=np.float64)
    limit = max(SPRAWL_GATE, float(np.max(old_sprawl)) + 0.05)
    for move in range(MOVES if worse else 0):
        starts, owner, off = realm.even_out(seats, starts, near_enough=0.12, tries=12, step=14.0, most=40.0)
        empty = [d for d in np.flatnonzero(np.bincount(owner, minlength=count) == 0) if d != 0]
        if empty:
            for d in empty:
                others = np.delete(seats, d)
                gap = np.min([np.hypot(realm.rows - realm.rows[s], realm.cols - realm.cols[s]) for s in others], axis=0)
                seats[d] = int(np.argmax(gap * dry))
                if d not in worse:
                    worse.append(d)
                    why[d] = "swallowed"
            starts = np.zeros(count)
            continue
        moved = seats.copy()
        for d in worse:
            moved[d] = realm.best_seat(owner, d, reach_km=16.0, pull_km=11.0)
        if (moved == seats).all():
            break
        seats = moved
    # A head start is held within 40 km, as it was; more is allowed only if the old seats cannot
    # be made into even counties without.
    notes = []
    for most in LIMITS:
        starts, owner, off, good, sprawl, note = finish(realm, seats, starts, count, most)
        good = good and float(sprawl.max()) <= limit
        notes.append("old seats, head starts within %.0f km: " % most + note + " (sprawl allowed %.2f)" % limit)
        if good:
            break
    kept = None
    if good:
        realm.claim(seats, starts)
        before = c1_counties.judge(realm, seats, owner, off, NEAR_ENOUGH)
        starts, owner, off, better = polish(realm, seats, starts, owner, off, count, 977 + number, most)
        realm.claim(seats, starts)
        score, features, far, sprawl = c1_counties.judge(realm, seats, owner, off, NEAR_ENOUGH)
        notes.append("old seats: %.0f%% of borders on features and score %.3f as evened; %.0f%% and %.3f after %d of %d other head starts were taken" % (
            100 * before[1], before[0], 100 * features, score, better, POLISH))
        size = realm.sizes(owner, count) * KM * KM
        kept = {"duchy": number, "box": box, "owner": realm.on_grid(owner).astype(np.int8), "off": off, "km2": size,
                "features": features, "far": far, "starts": starts, "sprawl": sprawl, "scatterings": 0, "score": score,
                "seats": [(int(realm.cols[s]) + box[1].start, int(realm.rows[s]) + box[0].start) for s in seats], "how": "kept", "most": most}
    # From scratch as well, to see whether the old seats still make as good counties as can be had.
    def sound(candidate):
        good, gap, room = n3_gates.passes(candidate["seats"], candidate["owner"], box, old_room)
        candidate["gap"], candidate["room"] = gap, room
        return good

    kept_sound = kept is not None and sound(kept)
    if kept is not None:
        notes.append("old seats: closest two seats %.1f km apart, the duchy seat's room %.1f px (was %.1f): %s" % (
            kept["gap"], kept["room"], old_room, "sound" if kept_sound else "not sound"))
    found = search(number, count, fixed, box, realm, FINISHED)
    fresh = None
    for candidate in found:
        fine = sound(candidate) and candidate["off"] <= GATE
        notes.append("from scratch: within %.1f%%, %.0f%% of borders on features, sprawl most %.2f, score %.3f; closest seats %.1f km, the duchy seat's room %.1f px: %s" % (
            100 * candidate["off"], 100 * candidate["features"], float(np.max(candidate["sprawl"])), candidate["score"],
            candidate["gap"], candidate["room"], "sound" if fine else "not sound"))
        if fine and fresh is None:
            fresh = candidate
    if kept_sound and (fresh is None or kept["score"] <= fresh["score"] + KEEP):
        chosen = kept
    elif fresh is not None:
        chosen = fresh
    elif kept is not None:
        chosen = kept
        notes.append("NOTHING SOUND: the old seats are taken as they are")
    else:
        chosen = found[0]
        notes.append("NOTHING SOUND: the best scattering is taken as it is")
    other = fresh if chosen is kept else kept
    chosen["notes"] = notes
    chosen["worse"] = {int(d): s for d, s in why.items()}
    chosen["old_seats"] = old_seats
    chosen["other_score"] = other["score"] if other is not None else None
    return chosen


def prepare(OLD, NEW, TAG, only=None, say=print):
    """The duchies as tasks for solve(), and what goes with them into the saved file."""
    full = dict(np.load(NEW + "/fields1.npz"))
    old_worth = np.load(OLD + "/fields1.npz")["seat"]
    duchy = np.load(NEW + "/duchy_map.npy").astype(np.int16)
    with open(NEW + "/duchies_all.pickle", "rb") as handle:
        duchies = pickle.load(handle)
    with open(OLD + "/counties_%s.pickle" % TAG, "rb") as handle:
        before = pickle.load(handle)
    seats = [None] + [seat for k in sorted(duchies) for seat in duchies[k]["seats"]]
    mainland = full["king"] > 0
    h, w = duchy.shape

    # Every island goes whole to one duchy; the great isles, and the islets nearer them than the
    # mainland, are a county of the duchy they lie off (as c1_counties.py has it).
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
    say("the isles: %d islands, %.0f km2, a county of duchy %d (before: duchy %d, the same islands: %s)" % (
        len(np.unique(pieces[isles])), isles.sum() * KM * KM, isle_duchy, before["isle_duchy"], bool((isles == before["isles"]).all())))
    say("island pixels in another duchy than before: %d" % int(((duchy != before["duchy"]) & islands).sum()))

    tasks, plan = [], {}
    for number in range(1, len(seats)):
        mine = duchy == number
        km2 = float(mine.sum()) * KM * KM
        count = int(np.clip(round(km2 / COUNTY), 4, 6))
        if number == isle_duchy:
            count -= 1
        plan[number] = count
        assert count == before["plan"][number], "duchy %d would have %d counties, not the %d it had" % (number, count, before["plan"][number])
        if only and number not in only:
            continue
        on_main = mine & mainland
        islets = mine & islands & ~isles
        rows = np.flatnonzero((on_main | islets).any(axis=1)); cols = np.flatnonzero((on_main | islets).any(axis=0))
        box = (slice(max(rows[0] - 3, 0), min(rows[-1] + 4, h)), slice(max(cols[0] - 3, 0), min(cols[-1] + 4, w)))
        was = before["results"][number]
        tasks.append((number, count, seats[number], box, on_main[box], {name: full[name][box] for name in NAMES}, islets[box],
                      [(int(x), int(y)) for x, y in was["seats"]], was["starts"], old_worth[box], was["sprawl"],
                      n3_gates.room_of(was["owner"], was["box"], was["seats"][0])))
    say("%d duchies to share out; counties in all: %d" % (len(tasks), sum(plan.values()) + (1 if isle_duchy else 0)))
    return tasks, plan, isles, isle_duchy, duchy, before


if __name__ == "__main__":
    OLD, NEW, TAG = sys.argv[1], sys.argv[2], sys.argv[3]
    only = [int(v) for v in sys.argv[4].split(",")] if len(sys.argv) > 4 else None
    tasks, plan, isles, isle_duchy, duchy, before = prepare(OLD, NEW, TAG, only)

    t0 = time.time()
    results = {}
    with ProcessPoolExecutor(max_workers=14) as pool:
        for result in pool.map(solve, tasks):
            number = result["duchy"]
            results[number] = result
            was = before["results"][number]
            print("duchy %2d (%s): %d counties of %s km2 (within %.1f%% of their mean), %.0f%% of borders on features (was %.0f%%), sprawl most %.2f (was %.2f), score %.3f (the other way %s)%s  (%.0fs)" % (
                number, result["how"], len(result["seats"]), np.round(result["km2"]).astype(int).tolist(), 100 * result["off"],
                100 * result["features"], 100 * was["features"], float(np.max(result["sprawl"])), float(np.max(was["sprawl"])), result["score"],
                "%.3f" % result["other_score"] if result["other_score"] is not None else "none",
                "; made worse by the new borders: %s" % result["worse"] if result["worse"] else "", time.time() - t0), flush=True)
            for note in result["notes"]:
                print("      " + note, flush=True)
    offs = np.array([r["off"] for r in results.values()]); kept = np.array([r["features"] for r in results.values()])
    sprawls = np.concatenate([r["sprawl"] for r in results.values()])
    hows = {name: sorted(d for d, r in results.items() if r["how"] == name) for name in ("kept", "searched")}
    print("SUMMARY: worst duchy within %.1f%%, mean %.1f%%; duchies over %.0f%%: %s; borders on features %.1f%%; sprawl mean %.3f, worst %.2f; duchies whose old seats were kept: %d; shared out afresh: %s" % (
        100 * offs.max(), 100 * offs.mean(), 100 * NEAR_ENOUGH, sorted(d for d, r in results.items() if r["off"] > NEAR_ENOUGH + 1e-9),
        100 * kept.mean(), sprawls.mean(), sprawls.max(), len(hows["kept"]), hows["searched"]))
    with open(NEW + "/counties_%s%s.pickle" % (TAG, "_part" if only else ""), "wb") as handle:
        pickle.dump({"results": results, "isles": isles, "isle_duchy": isle_duchy, "duchy": duchy, "plan": plan,
                     "ease": EASE, "near_enough": NEAR_ENOUGH}, handle)
    print("saved")
