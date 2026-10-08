"""Tidy shares as they will be drawn: the same for the solver, which evens out what tidying
leaves, and for the picture.

Four things, the last three done twice since each can leave a little for the others:
  smooth   each share's shape is blurred and a cell goes to whichever is strongest there;
  threads  a part of a share under five cells across goes to the nearest body of another
           share, so a neck that thin is cut and what hung by it is then a scrap;
  arms     a part too narrow for a disc of ARM_RADIUS, yet ARM_SIZE cells or more, that lies
           more against a neighbour than against its own share, goes whole to that neighbour
           (a strip left between a ridge and a river: the border moves to the other of the two);
  scraps   a share keeps its one largest piece, and the rest goes to whatever is nearest (so a
           thread that was really the share's own, a spit of coast, comes back to it).
"""
import numpy as np
from scipy import ndimage

SMOOTH = 2.0
ARM_RADIUS = 9.0
ARM_SIZE = 300
SQUARE = np.ones((3, 3), dtype=bool)


def _grown(box, by, shape):
    return (slice(max(box[0].start - by, 0), min(box[0].stop + by, shape[0])),
            slice(max(box[1].start - by, 0), min(box[1].stop + by, shape[1])))


def tidy(grid, inside, count, arms=True, sigma=SMOOTH):
    """[grid]: which share (0 .. count - 1) each cell [inside] the realm is in. Returns the
    same, tidied, with -1 outside."""
    labels = np.where(inside, grid, -1).astype(np.int16)
    shape = labels.shape
    presence = np.maximum(ndimage.gaussian_filter(inside.astype(np.float32), sigma), 1e-6)
    best = np.zeros(shape, dtype=np.float32)
    smooth = labels.copy()
    for c, box in enumerate(ndimage.find_objects(labels + 1, max_label=count)):
        if box is None:
            continue
        box = _grown(box, 8, shape)
        mine = ndimage.gaussian_filter((labels[box] == c).astype(np.float32), sigma) / presence[box]
        better = mine > best[box]
        smooth[box][better] = c
        best[box][better] = mine[better]
    labels = np.where(inside, smooth, -1).astype(np.int16)

    for again in range(2):
        # Threads.
        boxes = ndimage.find_objects(labels + 1, max_label=count)
        kept = np.zeros(shape, dtype=bool)
        for c, box in enumerate(boxes):
            if box is not None:
                box = _grown(box, 3, shape)
                kept[box] |= ndimage.binary_opening(labels[box] == c, structure=SQUARE, iterations=2)
        thin = inside & ~kept
        if thin.any():
            moved = labels.copy()
            for c, box in enumerate(boxes):
                if box is None:
                    continue
                box = _grown(box, 14, shape)
                mine = thin[box] & (labels[box] == c)
                others = kept[box] & (labels[box] != c)
                if mine.any() and others.any():
                    _, (ty, tx) = ndimage.distance_transform_edt(~others, return_indices=True)
                    moved[box][mine] = labels[box][ty[mine], tx[mine]]
            labels = moved
        # Arms.
        if arms:
            for c, box in enumerate(ndimage.find_objects(labels + 1, max_label=count)):
                if box is None:
                    continue
                box = _grown(box, 2, shape)
                mine = labels[box] == c
                inner = ndimage.distance_transform_edt(mine) > ARM_RADIUS
                if not inner.any():
                    continue
                arm = mine & ~(ndimage.distance_transform_edt(~inner) <= ARM_RADIUS)
                bits, n = ndimage.label(arm, structure=SQUARE)
                if n == 0:
                    continue
                sizes = ndimage.sum_labels(arm, bits, index=np.arange(1, n + 1))
                patch = labels[box]
                for i in np.flatnonzero(sizes >= ARM_SIZE):
                    part = bits == i + 1
                    ring = ndimage.binary_dilation(part, structure=SQUARE) & ~part
                    beside = patch[ring]
                    others = beside[(beside >= 0) & (beside != c)]
                    if others.size and np.bincount(others).max() > int((beside == c).sum()):
                        patch[part] = int(np.bincount(others).argmax())
        # Scraps.
        scrap = np.zeros(shape, dtype=bool)
        for c, box in enumerate(ndimage.find_objects(labels + 1, max_label=count)):
            if box is None:
                continue
            mine = labels[box] == c
            parts, n = ndimage.label(mine)
            if n > 1:
                sizes = ndimage.sum_labels(mine, parts, index=np.arange(1, n + 1))
                scrap[box] |= mine & (parts != int(np.argmax(sizes)) + 1)
        if scrap.any():
            _, (sy, sx) = ndimage.distance_transform_edt(scrap | ~inside, return_indices=True)
            labels = np.where(scrap, labels[sy, sx], labels)
    # "Nearest" can be across water: a scrap on one spit of coast handed to the share on the next
    # spit leaves that share in two pieces. Any piece still apart from its share's largest goes to
    # the share it lies most against.
    for again in range(4):
        mended = False
        for c, box in enumerate(ndimage.find_objects(labels + 1, max_label=count)):
            if box is None:
                continue
            box = _grown(box, 1, shape)
            mine = labels[box] == c
            parts, n = ndimage.label(mine)
            if n < 2:
                continue
            sizes = ndimage.sum_labels(mine, parts, index=np.arange(1, n + 1))
            patch = labels[box]
            for i in range(1, n + 1):
                if i == int(np.argmax(sizes)) + 1:
                    continue
                part = parts == i
                beside = patch[ndimage.binary_dilation(part) & ~part]
                others = beside[(beside >= 0) & (beside != c)]
                if others.size:
                    patch[part] = int(np.bincount(others).argmax())
                    mended = True
        if not mended:
            break
    return labels
