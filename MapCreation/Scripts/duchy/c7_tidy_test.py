"""Is what the solver gave back tidy? Tidies each duchy's counties again and counts what changes.

Usage: c7_tidy_test.py <duchy out dir> <tag> [duchy to print round a spot: number x y]
"""
import pickle
import sys
import numpy as np
from scipy import ndimage

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
from tidy import tidy, SQUARE

OUT, TAG = sys.argv[1], sys.argv[2]
with open(OUT + "/counties_%s.pickle" % TAG, "rb") as handle:
    data = pickle.load(handle)
total = 0
for number in sorted(data["results"]):
    result = data["results"][number]
    owner = result["owner"].astype(np.int16)
    inside = owner >= 0
    count = len(result["seats"])
    again = tidy(owner, inside, count)
    changed = int((again != owner).sum())
    total += changed
    # Threads left: cells of a share outside its own opening.
    kept = np.zeros(inside.shape, dtype=bool)
    for c in range(count):
        kept |= ndimage.binary_opening(owner == c, structure=SQUARE, iterations=2)
    # Necks: with the cells under five across taken out, is any county in more than one piece
    # of any size?
    hanging = 0
    for c in range(count):
        parts, n = ndimage.label((owner == c) & kept)
        if n > 1:
            sizes = np.sort(ndimage.sum_labels(owner == c, parts, index=np.arange(1, n + 1)))
            hanging += int(sizes[:-1].sum())
    if hanging:
        print("duchy %2d: %d cells hang by a neck under five across (tidying again changes %d cells)" % (number, hanging, changed))
    total_hanging = locals().get("total_hanging", 0) + hanging
    if len(sys.argv) > 5 and int(sys.argv[3]) == number:
        x, y = int(sys.argv[4]) - result["box"][1].start, int(sys.argv[5]) - result["box"][0].start
        window = (slice(y - 14, y + 14), slice(x - 14, x + 14))
        for name, grid in (("as found", owner), ("tidied again", again), ("kept by the opening", np.where(kept, owner, -1))):
            print(name)
            for row in grid[window]:
                print("".join("." if v < 0 else chr(ord("a") + int(v)) for v in row))
print("cells that tidying again would change, all duchies: %d" % total)
print("cells hanging by a thin neck, all duchies: %d" % total_hanging)
