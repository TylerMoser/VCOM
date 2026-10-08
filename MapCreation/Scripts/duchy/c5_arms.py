"""How many counties have arms: parts too narrow for a disc of RADIUS px, yet of some size.

Usage: c5_arms.py <duchy out dir> <tag> [radius] [picture out]
"""
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

OUT, TAG = sys.argv[1], sys.argv[2]
RADIUS = float(sys.argv[3]) if len(sys.argv) > 3 else 9.0
SIZE = 250
county = np.load(OUT + "/county_map_%s.npy" % TAG)
fields = np.load(OUT + "/fields1.npz")
mainland = fields["king"] > 0
arms = np.zeros(county.shape, dtype=bool)
found = []
for c, box in enumerate(ndimage.find_objects(county), start=1):
    if box is None:
        continue
    window = (slice(max(box[0].start - 12, 0), box[0].stop + 12), slice(max(box[1].start - 12, 0), box[1].stop + 12))
    mine = (county[window] == c) & mainland[window]
    if not mine.any():
        continue
    # Opening by a disc: what a disc of RADIUS can reach while staying inside.
    inner = ndimage.distance_transform_edt(mine) > RADIUS
    opened = ndimage.distance_transform_edt(~inner) <= RADIUS
    thin = mine & ~opened
    bits, n = ndimage.label(thin, structure=np.ones((3, 3)))
    if n == 0:
        continue
    sizes = ndimage.sum_labels(thin, bits, index=np.arange(1, n + 1))
    big = np.flatnonzero(sizes >= SIZE) + 1
    if big.size:
        arms[window] |= np.isin(bits, big)
        found.append((float(sizes[big - 1].sum()), c, sorted((int(s) for s in sizes[big - 1]), reverse=True)))
found.sort(reverse=True)
total = sum(f[0] for f in found)
print("radius %.0f px: %d counties have arms, %d px in all (%.2f%% of the land); the worst:" % (RADIUS, len(found), total, 100 * total / mainland.sum()))
for area, c, parts in found[:14]:
    print("  county %3d: %5d px in arms %s" % (c, area, parts[:5]))
if len(sys.argv) > 4:
    look = np.full(county.shape + (3,), 255, dtype=np.uint8)
    look[~mainland] = (181, 235, 255)
    look[fields["ridge"]] = (212, 190, 165)
    look[fields["divide"]] = (200, 140, 85)
    look[fields["river"] | fields["lake"]] = (28, 112, 224)
    look[arms] = (235, 70, 70)
    edge = np.zeros(county.shape, dtype=bool)
    edge[:, :-1] |= county[:, :-1] != county[:, 1:]
    edge[:-1, :] |= county[:-1, :] != county[1:, :]
    look[ndimage.binary_dilation(edge & mainland)] = (40, 40, 40)
    Image.fromarray(look).resize((county.shape[1] // 2, county.shape[0] // 2), Image.LANCZOS).save(sys.argv[4])
    print("saved", sys.argv[4])
