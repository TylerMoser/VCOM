"""Check Settlements.png from the pictures alone, with nothing the scripts kept.

Usage: s3_final_check.py <repo root>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT = sys.argv[1]
PINK, PURPLE, GREY = (233, 0, 255, 255), (110, 30, 180, 255), (128, 128, 128, 255)


def load(name):
    return np.asarray(Image.open(ROOT + "/MapCreation/" + name).convert("RGBA"))


settlements, counties, duchies, kingdoms = load("Settlements.png"), load("Counties.png"), load("Duchies.png"), load("Kingdoms.png")
print("sizes: %s %s" % (settlements.shape, counties.shape))
changed = (settlements != counties).any(axis=2)
values, tally = np.unique(settlements[changed].reshape(-1, 4), axis=0, return_counts=True)
print("Settlements.png differs from Counties.png in %d pixels, of colours %s" % (
    changed.sum(), {tuple(int(v) for v in c): int(n) for c, n in zip(values, tally)}))
was_white = (counties[..., :3] >= 250).all(axis=2)
print("all of them were white land in Counties.png: %s" % bool(was_white[changed].all()))
near = (ndimage.distance_transform_edt(~changed) <= 2.0) & ~changed
print("every pixel within 2 px of a dot is still white: %s" % bool((settlements[near][:, :3] >= 250).all()))

blobs, n = ndimage.label(changed, structure=np.ones((3, 3)))
index = np.arange(1, n + 1)
sizes = ndimage.sum_labels(changed, blobs, index=index).astype(int)
middles = np.array(ndimage.center_of_mass(changed, blobs, index))
colour = [tuple(int(v) for v in settlements[int(round(y)), int(round(x))]) for y, x in middles]
name = {PINK: "pink", PURPLE: "purple", GREY: "grey"}
kinds = {}
for size, c in zip(sizes, colour):
    kinds[(name.get(c, str(c)), int(size))] = kinds.get((name.get(c, str(c)), int(size)), 0) + 1
print("dots: %d; by colour and size in px: %s" % (n, kinds))
# Round: every dot is a disc about its middle.
worst = 0.0
for i, box in enumerate(ndimage.find_objects(blobs), start=1):
    ys, xs = np.nonzero(blobs[box] == i)
    r = np.hypot(ys + box[0].start - middles[i - 1][0], xs + box[1].start - middles[i - 1][1]).max()
    worst = max(worst, abs(np.pi * (r + 0.5) ** 2 / sizes[i - 1] - 1.0))
print("every dot is a filled disc (area against its radius within %.0f%%)" % (100 * worst))


def pieces_of(picture):
    white = (picture[..., :3] >= 250).all(axis=2)
    labels, count = ndimage.label(white)
    return labels, count


for title, picture in (("county", counties), ("duchy", duchies), ("kingdom", kingdoms)):
    labels, count = pieces_of(picture)
    at = labels[np.round(middles[:, 0]).astype(int), np.round(middles[:, 1]).astype(int)]
    assert (at > 0).all()
    for wanted, colours in (("county", (PINK, PURPLE, GREY)), ("duchy", (PINK, PURPLE)), ("kingdom", (PINK,))):
        if wanted != title:
            continue
        mine = np.array([c in colours for c in colour])
        per_piece = np.bincount(at[mine], minlength=count + 1)
        holding = int((per_piece > 0).sum())
        print("%s pieces holding a %s capital: %d, each exactly one: %s (pieces of white in that picture: %d)" % (
            title, title, holding, bool((per_piece[per_piece > 0] == 1).all()), count))
after = pieces_of(settlements)[1]
print("white pieces: %d in Counties.png, %d in Settlements.png" % (pieces_of(counties)[1], after))
sea = settlements[..., 2].astype(np.int32) - settlements[..., 0].astype(np.int32) >= 40
print("dot pixels by where they are: %d on what was white, %d elsewhere" % (int((changed & was_white).sum()), int((changed & ~was_white).sum())))
order = np.argsort([-s for s in sizes])
print("the pink dots' middles (x, y): %s" % [(int(round(middles[i][1])), int(round(middles[i][0]))) for i in range(n) if colour[i] == PINK])
