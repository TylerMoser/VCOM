"""Does holding the duchies nearer to equal pull their borders off rivers and ridges?

Runs d2_solve.py's search for some kingdoms at half size with the costs as they are now, once
for each tolerance, from the same scatterings of seats, and prints how much of the borders lies
on features. Writes nothing.

Usage: d2_tolerance_test.py <duchy out dir> <kingdoms, e.g. 3,5,7> <tolerances, e.g. 0.08,0.03>
"""
import sys
import time
import numpy as np

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
from realm import Realm

OUT = sys.argv[1]
KINGDOMS = [int(v) for v in sys.argv[2].split(",")]
TOLERANCES = [float(v) for v in sys.argv[3].split(",")]
DUCHIES = {1: 4, 2: 4, 3: 6, 4: 4, 5: 5, 6: 5, 7: 6, 8: 5, 9: 5}
STARTS, MOVES, SEED = 24, 7, 20261010

half = dict(np.load(OUT + "/fields2.npz"))
t0 = time.time()
for k in KINGDOMS:
    count = DUCHIES[k]
    realm = Realm(half["king"] == k, half, 0.67, half["island_king"] == k)
    for tolerance in TOLERANCES:
        rng = np.random.default_rng(SEED + k)
        tried = []
        for start_number in range(STARTS):
            seats = [int(rng.integers(realm.n))]
            while len(seats) < count:
                gap = np.min([np.hypot(realm.rows - realm.rows[s], realm.cols - realm.cols[s]) for s in seats], axis=0)
                seats.append(int(rng.choice(realm.n, p=gap ** 2 / (gap ** 2).sum())))
            seats = np.array(seats)
            starts = np.zeros(count)
            for move in range(MOVES):
                starts, owner, off = realm.even_out(seats, starts, near_enough=0.12, tries=14)
                empty = np.flatnonzero(np.bincount(owner, minlength=count) == 0)
                if empty.size:
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
            starts, owner, off = realm.even_out(seats, starts, near_enough=tolerance, tries=60)
            owner = realm.claim(seats, starts)
            mean_far = float(realm.far.mean())
            kept = realm.on_features(owner)
            tried.append((-kept + 4.0 * max(off - tolerance, 0.0) + 0.0015 * mean_far, off, kept))
        score, off, kept = min(tried)
        reached = sum(1 for t in tried if t[1] <= tolerance + 1e-9)
        print("kingdom %d, shares within %.0f%%: best scattering has %.0f%% of borders on features (shares within %.1f%%); %d of %d scatterings got that even; mean over those %.0f%%  (%.0fs)" % (
            k, 100 * tolerance, 100 * kept, 100 * off, reached, STARTS,
            100 * np.mean([t[2] for t in tried if t[1] <= tolerance + 1e-9]) if reached else float("nan"), time.time() - t0), flush=True)
