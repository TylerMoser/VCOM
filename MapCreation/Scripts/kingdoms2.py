"""Even out the nine regions' areas by flowing the land within its own coast.

Where kingdoms1.py moves each border bodily by one distance, this stretches the whole interior
smoothly: every region that is too small swells evenly and every one too big shrinks evenly, the
land between giving way, and nothing crosses the coast. The borders are carried along, so each
keeps its curve and every meeting of three borders stays a meeting of the same three.

The flow is the gradient of a potential whose Laplacian is each region's share still to gain
(none through the coast), solved on a grid FACTOR times coarser than the image and taken in short
steps, measuring the true areas again before each, until they are equal.

Usage: kingdoms2.py <repo root> <out dir>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage, sparse
from scipy.sparse import linalg

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT = sys.argv[1], sys.argv[2]
FACTOR = 4
STEP = 1.5              # coarse cells: the furthest any point moves in one step

creation = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
h, w = creation.shape[:2]
white = (creation[..., 0] >= 250) & (creation[..., 1] >= 250) & (creation[..., 2] >= 250)
pieces, count = ndimage.label(white)
sizes = ndimage.sum_labels(white, pieces, index=np.arange(1, count + 1))
mainland = pieces == (int(np.argmax(sizes)) + 1)
islands = white & ~mainland
start = np.load(OUT + "/start_map.npy")           # the drawn regions, smoothed (kingdoms1.py)

# The drawn regions spread over the sea too, so a point carried just off the coast still reads
# as the land beside it.
_, (near_y, near_x) = ndimage.distance_transform_edt(~mainland, return_indices=True)
spread = start[near_y, near_x]
island_y, island_x = np.nonzero(islands)
island_near = (near_y[island_y, island_x], near_x[island_y, island_x])
del near_y, near_x
main_y, main_x = np.nonzero(mainland)
total = main_y.size + island_y.size
target = total / 9.0

# The coarse grid the flow is solved on.
H, W = h // FACTOR, w // FACTOR
coarse = mainland[: H * FACTOR, : W * FACTOR].reshape(H, FACTOR, W, FACTOR).mean(axis=(1, 3)) >= 0.5
parts, n = ndimage.label(coarse)
part_sizes = ndimage.sum_labels(coarse, parts, index=np.arange(1, n + 1))
coarse = parts == (int(np.argmax(part_sizes)) + 1)
cells = int(coarse.sum())
index = -np.ones((H, W), dtype=np.int64)
index[coarse] = np.arange(cells)
print("coarse grid %d x %d, %d land cells" % (W, H, cells))

rows, cols = [], []
for dy, dx in ((0, 1), (1, 0)):
    a = index[: H - dy, : W - dx]
    b = index[dy:, dx:]
    both = (a >= 0) & (b >= 0)
    rows.append(a[both]); cols.append(b[both])
rows = np.concatenate(rows); cols = np.concatenate(cols)
adjacency = sparse.coo_matrix((np.ones(rows.size), (rows, cols)), shape=(cells, cells))
adjacency = adjacency + adjacency.T
degree = np.asarray(adjacency.sum(axis=1)).ravel()
laplacian = (adjacency - sparse.diags(degree)).tolil()      # sum of neighbours less the cell
laplacian[0, :] = 0.0
laplacian[0, 0] = 1.0                                       # pin one cell: the rest is fixed up to that
solve = linalg.factorized(laplacian.tocsc())
print("flow solver ready")

_, (land_y, land_x) = ndimage.distance_transform_edt(~coarse, return_indices=True)
cy, cx = np.mgrid[0:H, 0:W].astype(np.float32)
# Where each coarse cell's land came from, in image pixels. Starts as where it is.
from_y = cy * FACTOR + (FACTOR - 1) / 2.0
from_x = cx * FACTOR + (FACTOR - 1) / 2.0
# Image pixels in coarse coordinates, for reading the coarse maps at every mainland pixel.
fine_at = np.vstack([(main_y - (FACTOR - 1) / 2.0) / FACTOR, (main_x - (FACTOR - 1) / 2.0) / FACTOR]).astype(np.float32)


def current_labels():
    sy = ndimage.map_coordinates(from_y, fine_at, order=1, mode="nearest")
    sx = ndimage.map_coordinates(from_x, fine_at, order=1, mode="nearest")
    iy = np.clip(np.rint(sy).astype(np.int64), 0, h - 1)
    ix = np.clip(np.rint(sx).astype(np.int64), 0, w - 1)
    labels = np.zeros((h, w), dtype=np.uint8)
    labels[main_y, main_x] = spread[iy, ix]
    return labels


def areas_of(labels):
    counts = np.bincount(labels[main_y, main_x], minlength=10)[1:].astype(np.float64)
    mainland_counts = counts.copy()
    counts += np.bincount(labels[island_near], minlength=10)[1:]
    return counts, mainland_counts


labels = current_labels()
areas, on_mainland = areas_of(labels)
print("as drawn: ", " ".join("%d:%.2f%%" % (i + 1, 100 * a / total) for i, a in enumerate(areas)))
for step in range(400):
    error = target - areas
    worst = np.abs(error).max()
    if step % 10 == 0 or worst < 80:
        print("step %3d: worst error %7.0f px (%.3f%%)" % (step, worst, 100 * worst / target))
    if worst < 80:
        break
    # Each region's own land swells or shrinks by the share it still has to gain.
    rate = error / on_mainland
    iy = np.clip(np.rint(from_y[coarse]).astype(np.int64), 0, h - 1)
    ix = np.clip(np.rint(from_x[coarse]).astype(np.int64), 0, w - 1)
    cell_label = spread[iy, ix]
    source = rate[cell_label - 1]
    source -= source.mean()                    # what swells must equal what shrinks
    source[0] = 0.0
    potential = np.zeros((H, W))
    potential[coarse] = solve(source)
    # The gradient, with nothing through the coast.
    flow_y = np.zeros((H, W)); flow_x = np.zeros((H, W))
    face = np.where(coarse[1:, :] & coarse[:-1, :], potential[1:, :] - potential[:-1, :], 0.0)
    flow_y[:-1, :] += 0.5 * face; flow_y[1:, :] += 0.5 * face
    face = np.where(coarse[:, 1:] & coarse[:, :-1], potential[:, 1:] - potential[:, :-1], 0.0)
    flow_x[:, :-1] += 0.5 * face; flow_x[:, 1:] += 0.5 * face
    speed = np.hypot(flow_y, flow_x)[coarse].max()
    scale = min(1.0, STEP / max(speed, 1e-9))
    flow_y = (flow_y * scale)[land_y, land_x].astype(np.float32)
    flow_x = (flow_x * scale)[land_y, land_x].astype(np.float32)
    # Land now at a cell came from where the land a step upstream came from.
    back = np.stack([cy - flow_y, cx - flow_x])
    from_y = ndimage.map_coordinates(from_y, back, order=1, mode="nearest")[land_y, land_x]
    from_x = ndimage.map_coordinates(from_x, back, order=1, mode="nearest")[land_y, land_x]
    labels = current_labels()
    areas, on_mainland = areas_of(labels)

print("areas:  ", " ".join("%d:%.3f%%" % (i + 1, 100 * a / total) for i, a in enumerate(areas)))
moved_y = from_y - (cy * FACTOR + (FACTOR - 1) / 2.0)
moved_x = from_x - (cx * FACTOR + (FACTOR - 1) / 2.0)
distance = np.hypot(moved_y, moved_x)[coarse]
print("land moved: mean %.0f px, 90th percentile %.0f px, most %.0f px" % (distance.mean(), np.percentile(distance, 90), distance.max()))


def borders_of(lab):
    lengths = np.zeros((9, 9))
    for dy, dx in ((0, 1), (1, 0)):
        a = lab[: h - dy, : w - dx]; b = lab[dy:, dx:]
        cross = (a != b) & (a > 0) & (b > 0)
        pairs = (a[cross].astype(np.int64) - 1) * 9 + (b[cross].astype(np.int64) - 1)
        tally = np.bincount(pairs, minlength=81).reshape(9, 9)
        lengths += tally + tally.T
    return lengths / 1.27


before = borders_of(start)
after = borders_of(labels)
print("borders kept: %s" % bool(((before > 20) == (after > 20)).all()))
for i in range(9):
    for j in range(i + 1, 9):
        if before[i, j] > 20 or after[i, j] > 20:
            print("  %d|%d: %4.0f px long, was %4.0f" % (i + 1, j + 1, after[i, j], before[i, j]))
for i in range(1, 10):
    parts, n = ndimage.label(labels == i)
    if n != 1:
        part_sizes = np.sort(ndimage.sum_labels(labels == i, parts, index=np.arange(1, n + 1)))[::-1]
        print("  region %d is in %d pieces: %s" % (i, n, part_sizes[:8].astype(int).tolist()))

np.save(OUT + "/kingdom_map_flow.npy", labels)
np.save(OUT + "/flow_from.npy", np.stack([from_y, from_x]))

palette = np.array([[181, 235, 255], [200, 215, 230], [190, 110, 90], [150, 160, 150], [235, 215, 140],
                    [190, 215, 120], [40, 120, 90], [110, 140, 110], [150, 190, 90], [60, 160, 60]], dtype=np.uint8)
picture = palette[labels]
picture[islands] = (255, 255, 255)
picture[creation[..., :3].astype(np.int32).sum(axis=2) < 300] = 0
def edges(lab):
    edge = np.zeros((h, w), dtype=bool)
    for dy, dx in ((0, 1), (1, 0)):
        a = lab[: h - dy, : w - dx]; b = lab[dy:, dx:]
        cross = (a != b) & (a > 0) & (b > 0)
        edge[: h - dy, : w - dx] |= cross
        edge[dy:, dx:] |= cross
    return edge
picture[ndimage.binary_dilation(edges(labels), iterations=3)] = (233, 0, 255)
picture[ndimage.binary_dilation(edges(start), iterations=2)] = (0, 0, 0)
Image.fromarray(picture).resize((w // 2, h // 2), Image.LANCZOS).save(OUT + "/kingdoms_flow_preview.png")
print("saved kingdoms_flow_preview.png (old borders black, new pink)")
