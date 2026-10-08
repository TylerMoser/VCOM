"""Where tidying moved land from one county to another: the solver's shares against the map drawn.

Usage: c4_compare.py <duchy out dir> <tag> <county number> [picture out]
"""
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

OUT, TAG, WHICH = sys.argv[1], sys.argv[2], int(sys.argv[3])
with open(OUT + "/counties_%s.pickle" % TAG, "rb") as handle:
    data = pickle.load(handle)
tidied = np.load(OUT + "/county_map_%s.npy" % TAG)
fields = np.load(OUT + "/fields1.npz")
mainland = fields["king"] > 0
solved = np.zeros(tidied.shape, dtype=np.int16)
number = 0
for duchy in sorted(data["results"]):
    result = data["results"][duchy]
    owner = result["owner"].astype(np.int16)
    view = solved[result["box"]]
    here = owner >= 0
    view[here] = number + 1 + owner[here]
    number += len(result["seats"])
moved = mainland & (solved != tidied) & ((solved == WHICH) | (tidied == WHICH))
print("county %d: solved %d px, tidied %d px; lost %d, gained %d" % (
    WHICH, (solved == WHICH).sum(), ((tidied == WHICH) & mainland).sum(), (moved & (solved == WHICH)).sum(), (moved & (tidied == WHICH)).sum()))
bits, n = ndimage.label(moved, structure=np.ones((3, 3)))
sizes = ndimage.sum_labels(moved, bits, index=np.arange(1, n + 1))
for i in np.argsort(-sizes)[:6]:
    box = ndimage.find_objects(bits)[i]
    part = bits[box] == i + 1
    was = np.bincount(solved[box][part]).argmax(); now = np.bincount(tidied[box][part]).argmax()
    thickness = ndimage.distance_transform_edt(part).max() * 2
    print("  %d px at x %d..%d, y %d..%d: was county %d, now %d; about %.0f px across at its thickest" % (
        sizes[i], box[1].start, box[1].stop, box[0].start, box[0].stop, was, now, thickness))
if len(sys.argv) > 4:
    ys, xs = np.nonzero((solved == WHICH) | (tidied == WHICH))
    box = (slice(max(ys.min() - 20, 0), ys.max() + 20), slice(max(xs.min() - 20, 0), xs.max() + 20))
    look = np.full(solved[box].shape + (3,), 255, dtype=np.uint8)
    look[~mainland[box]] = (181, 235, 255)
    look[fields["ridge"][box]] = (212, 190, 165)
    look[fields["divide"][box]] = (200, 140, 85)
    look[fields["river"][box] | fields["lake"][box]] = (28, 112, 224)
    both = (solved[box] == WHICH) & (tidied[box] == WHICH)
    look[both] = (0.6 * look[both] + 0.4 * np.array([120, 200, 120])).astype(np.uint8)
    look[(solved[box] == WHICH) & (tidied[box] != WHICH)] = (230, 60, 60)
    look[(solved[box] != WHICH) & (tidied[box] == WHICH)] = (60, 60, 230)
    edge = np.zeros(look.shape[:2], dtype=bool)
    patch = tidied[box]
    edge[:, :-1] |= patch[:, :-1] != patch[:, 1:]
    edge[:-1, :] |= patch[:-1, :] != patch[1:, :]
    look[edge & mainland[box]] = (40, 40, 40)
    Image.fromarray(look).save(sys.argv[4])
    print("saved %s, corner at x %d, y %d" % (sys.argv[4], box[1].start, box[0].start))
