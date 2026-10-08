"""What the ground is like for someone travelling over it, as grids at the map's own size and at
half of it: the things that decide where one lord's land ends and the next one's begins.

From the map files: heights (Elevation.png), rivers and lakes (Water.png, split into the two by
the rivers stage's own masks), the lines between watersheds (Rivers.png's brown) and the kingdoms
(Kingdoms.png, already read into grid1.npz).

Saved for each size: the kingdom of each pixel, its height, whether it is river, lake or on a
watershed line, how many kilometres a river there costs to cross, how slow the going is, and how
good a place it would be for a duchy's seat.

Usage: d1_fields.py <repo root> <water out dir> <duchy out dir>
"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, WATER, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
KM = 0.335
SEED = 20261009

full = np.load(WATER + "/grid1.npz")
land, mainland, king = full["land"], full["mainland"], full["king"]
h, w = land.shape
height = np.asarray(Image.open(ROOT + "/MapCreation/Elevation.png")).astype(np.float32) / 10.0
rivers_png = np.asarray(Image.open(ROOT + "/MapCreation/Rivers.png").convert("RGBA"))
blue = (rivers_png[..., 0] == 28) & (rivers_png[..., 1] == 112) & (rivers_png[..., 2] == 224) & land
brown = (rivers_png[..., 0] == 196) & (rivers_png[..., 1] == 118) & (rivers_png[..., 2] == 44) & land
drawn = np.load(WATER + "/drawn2.npz")
lake = drawn["lakes"] & land
river = blue & ~lake
divide = (brown | (drawn["divide"] & land)) & ~blue        # the lines run on under the water they meet

# How wide the river is at each of its pixels, and so what it costs to cross: a brook is waded,
# a great river needs a ferry and is as good as a wall.
half = ndimage.distance_transform_edt(river)
wide = np.clip(2.0 * ndimage.maximum_filter(half, size=11), 2.0, 12.0)
cross = np.where(river, 8.0 + 0.9 * wide ** 2, 0.0).astype(np.float32)      # km: 12 for a brook, 40 at 6 px, 80 at 9

# How slow the going is: easy along the rivers where people live, slower out in the empty country
# between them, slow by boat on a lake; with a little unevenness so no border runs ruler-straight.
water_far = ndimage.distance_transform_edt(~(blue | ~land)) * KM
rng = np.random.default_rng(SEED)
small = (h // 8 + 1, w // 8 + 1)
bumps = ndimage.zoom(ndimage.gaussian_filter(rng.standard_normal(small), 5.0), 8, order=1)[:h, :w]
bumps += 0.6 * ndimage.zoom(ndimage.gaussian_filter(rng.standard_normal(small), 1.6), 8, order=1)[:h, :w]
bumps /= bumps.std()
going = (1.0 + 0.6 * np.minimum(water_far / 8.0, 1.5)) * np.exp(0.22 * bumps)
going = np.where(river, 0.8, np.where(lake, 1.4, going)).astype(np.float32)

# How good a place for a seat: on a big river, at a river's mouth, in a sheltered harbour, on a
# lake's shore; not high in the mountains, and not hard against the kingdom's own border.
coast = ndimage.distance_transform_edt(land) * KM
river_near = ndimage.maximum_filter(np.where(river, wide, 0.0), size=13)
big_lake, n = ndimage.label(lake)
lake_sizes = ndimage.sum_labels(lake, big_lake, index=np.arange(1, n + 1)) * KM * KM
lake_near = ndimage.maximum_filter(np.isin(big_lake, np.flatnonzero(lake_sizes >= 40.0) + 1), size=13)
border = np.zeros((h, w), dtype=bool)
border[:-1, :] |= (king[:-1, :] != king[1:, :]) & land[:-1, :] & land[1:, :]
border[:, :-1] |= (king[:, :-1] != king[:, 1:]) & land[:, :-1] & land[:, 1:]
border_far = ndimage.distance_transform_edt(~border) * KM
seat = 1.1 * river_near + 1.5 * (coast < 4.0) + 2.0 * ((coast < 5.0) & (river_near >= 2.0)) + 1.5 * lake_near
seat -= np.maximum(height - 1200.0, 0.0) / 350.0 + 4.0 * (border_far < 14.0)
seat = np.where(land & ~lake & ~river, seat, -99.0).astype(np.float32)

np.savez_compressed(OUT + "/fields1.npz", king=np.where(mainland, king, 0).astype(np.uint8), island_king=np.where(land & ~mainland, king, 0).astype(np.uint8),
                    height=height, river=river, lake=lake, divide=divide, cross=cross, going=going, seat=seat)
print("full size: river %d px, lake %d px, watershed lines %d px" % (river.sum(), lake.sum(), divide.sum()))

# The same at half size, for the trying-out: a cell is river, lake or line if any of its four
# pixels is; rivers are thickened a cell so none can be slipped across cornerwise.
hh, hw = h // 2, w // 2
def blocks(field):
    return field[: hh * 2, : hw * 2].reshape(hh, 2, hw, 2)
river2 = ndimage.binary_dilation(blocks(river).any(axis=(1, 3)), structure=np.ones((2, 2), dtype=bool))
lake2 = blocks(lake).mean(axis=(1, 3)) >= 0.5
divide2 = ndimage.binary_dilation(blocks(divide).any(axis=(1, 3)), structure=np.ones((2, 2), dtype=bool)) & ~river2 & ~lake2
main2 = np.load(WATER + "/grid2.npz")
king2 = np.where(main2["mainland"], main2["king"], 0).astype(np.uint8)
cross2 = ndimage.maximum_filter(blocks(cross).max(axis=(1, 3)), size=3) * river2
np.savez_compressed(OUT + "/fields2.npz", king=king2, island_king=np.where(main2["land"] & ~main2["mainland"], main2["king"], 0).astype(np.uint8),
                    height=blocks(height).mean(axis=(1, 3)), river=river2 & ~lake2, lake=lake2, divide=divide2, cross=cross2.astype(np.float32),
                    going=blocks(going).mean(axis=(1, 3)), seat=blocks(seat).max(axis=(1, 3)))
print("half size: river %d cells, lake %d cells, watershed lines %d cells" % ((river2 & ~lake2).sum(), lake2.sum(), divide2.sum()))
