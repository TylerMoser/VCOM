"""Check Counties.png from the pictures alone, with nothing the scripts kept: what was added to
Duchies.png, how many pieces a paint bucket finds, and how big they are within each duchy.

Usage: c8_final_check.py <repo root>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT = sys.argv[1]
KM2 = 0.335 * 0.335
counties = np.asarray(Image.open(ROOT + "/MapCreation/Counties.png").convert("RGBA"))
duchies = np.asarray(Image.open(ROOT + "/MapCreation/Duchies.png").convert("RGBA"))
kingdoms = np.asarray(Image.open(ROOT + "/MapCreation/Kingdoms.png").convert("RGBA"))
coast = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
print("sizes: %s %s %s" % (counties.shape, duchies.shape, coast.shape))
changed = (counties != duchies).any(axis=2)
values, tally = np.unique(counties[changed].reshape(-1, 4), axis=0, return_counts=True)
print("Counties.png differs from Duchies.png in %d pixels, of colours %s" % (changed.sum(), {tuple(int(v) for v in c): int(n) for c, n in zip(values, tally)}))
sea = coast[..., 2].astype(np.int32) - coast[..., 0].astype(np.int32) >= 40
print("of them on the coast map's sea blue: %d; on its white land: %d; on its ink and greys: %d" % (
    (changed & sea).sum(), (changed & (coast[..., :3] >= 250).all(axis=2)).sum(),
    (changed & ~sea & ~(coast[..., :3] >= 250).all(axis=2)).sum()))


def pieces_of(picture):
    white = (picture[..., :3] >= 250).all(axis=2)
    labels, n = ndimage.label(white)
    sizes = ndimage.sum_labels(white, labels, index=np.arange(1, n + 1))
    return labels, sizes


labels_c, sizes_c = pieces_of(counties)
labels_d, sizes_d = pieces_of(duchies)
labels_k, sizes_k = pieces_of(kingdoms)
labels_0, sizes_0 = pieces_of(coast)
# The land: the coast map's white pieces. Its largest is the mainland; the rest are islands.
main = int(np.argmax(sizes_0)) + 1
mainland = labels_0 == main
print("white pieces: coast map %d (mainland %d px; islands %s)" % (
    (sizes_0 > 20).sum(), sizes_0[main - 1], sorted((int(s) for i, s in enumerate(sizes_0) if s > 20 and i != main - 1), reverse=True)))
for name, labels, sizes in (("Kingdoms.png", labels_k, sizes_k), ("Duchies.png", labels_d, sizes_d), ("Counties.png", labels_c, sizes_c)):
    inside = np.unique(labels[mainland & (labels > 0)])
    big = [i for i in inside if sizes[i - 1] >= 400]
    print("%s: the mainland is in %d white pieces (and %d specks under 400 px)" % (name, len(big), len(inside) - len(big)))

# Each county piece's duchy and kingdom, by the piece of those pictures it lies in.
county_ids = np.array([i for i in np.unique(labels_c[mainland & (labels_c > 0)]) if sizes_c[i - 1] >= 400])
where = np.isin(labels_c, county_ids)
duchy_of = {}
kingdom_of = {}
flat_c, flat_d, flat_k = labels_c[where], labels_d[where], labels_k[where]
order = np.argsort(flat_c, kind="stable")
flat_c, flat_d, flat_k = flat_c[order], flat_d[order], flat_k[order]
starts = np.flatnonzero(np.diff(np.concatenate([[-1], flat_c])))
for a, b in zip(starts, list(starts[1:]) + [flat_c.size]):
    c = int(flat_c[a])
    d = np.bincount(flat_d[a:b])
    k = np.bincount(flat_k[a:b])
    assert d.argmax() > 0 and d.max() == d.sum() and k.max() == k.sum(), "a county piece lies in two duchies or kingdoms"
    duchy_of[c], kingdom_of[c] = int(d.argmax()), int(k.argmax())
print("every county piece lies inside one duchy piece and one kingdom piece: yes")
# Kingdom pieces numbered 1..9 by the sketch's order is not known here; number them by their middles.
by_duchy = {}
for c in county_ids:
    by_duchy.setdefault(duchy_of[int(c)], []).append(float(sizes_c[c - 1]) * KM2)
per_kingdom = {}
for d, areas in by_duchy.items():
    k = kingdom_of[[c for c in county_ids if duchy_of[int(c)] == d][0]]
    per_kingdom.setdefault(k, []).append(len(areas))
counts = sorted(len(v) for v in by_duchy.values())
print("duchies: %d; counties in each, fewest to most: %s" % (len(by_duchy), counts))
print("counties per kingdom piece (white pieces only, so without the isles): %s" % sorted((sum(v), sorted(v)) for v in per_kingdom.values()))
worst = 0.0
for d, areas in by_duchy.items():
    areas = np.array(areas)
    if len(areas) == 3:                                # the duchy whose fourth county is the isles
        isles = float(sum(s for i, s in enumerate(sizes_0) if s > 20 and i != main - 1 and s >= 180)) * KM2
        print("  the duchy with 3 mainland pieces: %s km2 of white each; the islands off it hold %.0f km2 more" % (np.round(np.sort(areas)).astype(int).tolist(), isles))
    worst = max(worst, float(np.abs(areas - areas.mean()).max() / areas.mean()))
white_all = np.array([float(sizes_c[c - 1]) * KM2 for c in county_ids])
print("white land in a county piece (lines not counted): %.0f to %.0f km2, mean %.0f" % (white_all.min(), white_all.max(), white_all.mean()))
print("furthest a county's white land is from its duchy's mean: %.1f%%" % (100 * worst))
