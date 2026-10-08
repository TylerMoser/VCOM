"""The lie of the land and the way water leaves it, made together to suit the nine kingdoms.

Nothing in the repo says how high anything is, so this decides it, from how steep each kind of
country is meant to be: the central range steepest, the tundra and volcanic kingdoms a high
country with a gentler top, the forests hilly, the grassland and desert long aprons, the swamp all
but level. Steepness is then made uneven (winding strips of easy ground are the valleys), and
every cell is given the least total climb from the sea (hydro.climb): that is its height, and the
way of least climb is the way its water runs down. Where much water gathers the ground is made
easier and the climb worked out again, a few times over, so that streams collect into trunk
rivers as real ones do.

Usage: w2_drain.py <out dir> <factor: 4 for a quarter of the picture's size, 2 for a half>
"""
import sys
import time
import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
import hydro

OUT = sys.argv[1]
FACTOR = int(sys.argv[2]) if len(sys.argv) > 2 else 4
KM = 0.335 * FACTOR                      # one cell, at Texas's area for the island
SEED = 20261006
GATHER_ROUNDS = 3                        # times the climb is redone with rivers' ground eased
EASE = 0.45                              # how much a river eases its own ground: 1 / (1 + EASE * sqrt(flow / 40))

grids = np.load(OUT + "/grid%d.npz" % FACTOR)
land, king = grids["land"], grids["king"]
h, w = land.shape
yy, xx = np.mgrid[0:h, 0:w]
# The noise is made at a quarter of the picture's size whatever size is asked for, so the same
# land comes out at every size.
NOISE_FACTOR = 4
nh, nw = h * FACTOR // NOISE_FACTOR, w * FACTOR // NOISE_FACTOR
NOISE_KM = 0.335 * NOISE_FACTOR
rng = np.random.default_rng(SEED)


def blurred(field, sigma_km, mask=land):
    sigma = sigma_km / KM
    top = ndimage.gaussian_filter(np.where(mask, field, 0.0).astype(np.float64), sigma)
    under = ndimage.gaussian_filter(mask.astype(np.float64), sigma)
    return np.where(mask, top / np.maximum(under, 1e-9), 0.0)


def by_kingdom(values, sigma_km, default=0.0):
    table = np.full(10, default, dtype=np.float64)
    for k, v in values.items():
        table[k] = v
    return blurred(table[king], sigma_km)


def noise(scales_km, hurst=0.9):
    """Bumps at each of [scales_km], the broad ones tallest, with a spread of one."""
    total = np.zeros((nh, nw))
    for scale in scales_km:
        layer = ndimage.gaussian_filter(rng.standard_normal((nh, nw)), scale / NOISE_KM)
        total += (scale / scales_km[0]) ** hurst * layer / layer.std()
    total /= total.std()
    if (nh, nw) != (h, w):
        total = ndimage.zoom(total, (h / nh, w / nw), order=3)
    return total


def distance_to(mask):
    return ndimage.distance_transform_edt(~mask) * KM


is_k = {k: king == k for k in range(1, 10)}
sea = ~land
coast = distance_to(sea)
near = {k: distance_to(is_k[k]) for k in range(1, 10)}
high = is_k[1] | is_k[2] | is_k[3]
into_high = np.where(high, ndimage.distance_transform_edt(high) * KM, 0.0)
from_high = distance_to(high)

# -- how steep the ground is meant to be, metres of rise in a kilometre ---------------------------
steep = by_kingdom({1: 21.0, 2: 10.0, 3: 33.0, 4: 3.6, 5: 2.3, 6: 4.4, 7: 0.05, 8: 12.0, 9: 6.5}, 8.0)
# The high country of 1 and 2 flattens toward its middle: fells and lava plateau, not one peak.
plateau = np.where(is_k[1] | is_k[2], 0.45 + 0.55 * np.exp(-into_high / 90.0), 1.0)
steep *= blurred(plateau, 10.0)
# Fans of gravel where the mountains meet the swamp, and foothills in the rainforest.
steep += np.where(is_k[7], 4.0 * np.exp(-from_high / 13.0), 0.0)
steep += np.where(is_k[6], 4.5 * np.exp(-from_high / 45.0), 0.0)
steep += np.where(is_k[8] | is_k[9], 2.0 * np.exp(-coast / 25.0), 0.0)        # hills come down to these coasts

broad = noise([220, 110, 55])                              # whole districts easier or harder
valleys = noise([64, 32, 16, 8, 4], 0.45)                  # near nought along winding lines: the valleys
fine = noise([10, 5, 2.5], 0.3)
grain = rng.standard_normal((h, w))                        # cell by cell, so no way runs dead straight
uneven = np.exp(0.5 * broad) * (0.28 + 1.7 * np.abs(valleys) ** 0.8) * np.exp(0.35 * fine + 0.55 * grain)
# The desert's ranges and the forest kingdoms' ridges: long bumps along the island.
drawn_out = ndimage.gaussian_filter(rng.standard_normal((nh, nw)), (30.0 / NOISE_KM, 7.0 / NOISE_KM))
drawn_out = ndimage.rotate(drawn_out, 28.0, reshape=False, mode="reflect")
drawn_out /= drawn_out.std()
if (nh, nw) != (h, w):
    drawn_out = ndimage.zoom(drawn_out, (h / nh, w / nw), order=3)
uneven *= np.exp(by_kingdom({4: 0.75, 8: 0.5}, 10.0) * drawn_out)
steep = steep * uneven

# Bays are drowned valleys: the ground behind an inlet is easy, so rivers come out at inlets.
filled_in = ndimage.binary_closing(np.pad(land, 80), structure=np.ones((3, 3), dtype=bool), iterations=int(26.0 / KM))[80:-80, 80:-80]
inlets = filled_in & sea
steep *= 1.0 - 0.5 * np.exp(-distance_to(inlets) / 22.0) * (distance_to(inlets) < 80.0)

# 2, the volcanoes: cones on the lava plateau, one of them a collapsed ring with a hollow inside.
k2 = np.argwhere(is_k[2] & (ndimage.distance_transform_edt(is_k[2]) * KM > 34.0))
cone_rng = np.random.default_rng(SEED + 2)
picked = []
for _ in range(6000):
    if len(picked) >= 9:
        break
    y, x = k2[cone_rng.integers(len(k2))] * FACTOR                       # in the picture's pixels
    if all(np.hypot(y - py, x - px) * 0.335 > 54.0 for py, px in picked):
        picked.append((int(y), int(x)))
volcanoes = []
for n, (y, x) in enumerate(picked):
    r = np.hypot(yy * FACTOR - y, xx * FACTOR - x) * 0.335                # km
    if n == 0:
        ring_at, ring_wide = 15.0, 3.2
        steep += np.where(land, 150.0 * np.exp(-((r - ring_at) / ring_wide) ** 2) + 9.0 * np.exp(-(r / 42.0) ** 2), 0.0)
        steep = np.where(r < ring_at - 1.5 * ring_wide, steep * 0.08, steep)   # a level floor inside the ring
        volcanoes.append((y, x, 1, 0.0))
    else:
        tall, wide = cone_rng.uniform(1100.0, 2100.0), cone_rng.uniform(9.0, 13.0)
        steep += np.where(land, (tall / wide) * np.exp(-r / wide), 0.0)
        volcanoes.append((y, x, 0, tall))

# 4's basin: a hollow in the desert that no river leaves. Water may end there as well as in the sea.
basin_y, basin_x = 1505, 2065                                             # in the picture's pixels
# Its floor is a level pan with the mountains' apron running down to it, so the streams off the
# dry side of the range end here and not in the sea.
pan = np.hypot(yy * FACTOR - basin_y, xx * FACTOR - basin_x) * 0.335
steep *= np.where(pan < 80.0, 0.22 + 0.78 * (pan / 80.0) ** 2, 1.0)
steep = np.where(land, np.maximum(steep, 0.02), 0.0)

# -- rain: what runs off each cell in a year, metres of water -------------------------------------
across = near[7] + near[6]
lee = near[4] + near[5]
wet_side = np.where(is_k[3], lee / np.maximum(across + lee, 1e-9), 0.0)       # 1 at the wet edge, 0 at the dry
runoff = by_kingdom({1: 0.52, 2: 0.33, 3: 1.05, 4: 0.006, 5: 0.06, 6: 2.1, 7: 0.65, 8: 0.42, 9: 1.35}, 14.0)
runoff *= np.where(is_k[3], 0.5 + 1.0 * wet_side, 1.0)

grid = hydro.Grid(land)
CUMECS = (KM * KM) * 1e6 / 31.5e6                         # a metre a year off one cell, in m3/s
gain = grid.flat(runoff) * CUMECS
gathering = np.clip(grid.flat(runoff), 0.3, 0.9) * CUMECS  # for shaping valleys every land counts: dry ones by rare floods, wet ones not without limit
sink_cell = int(grid.index[basin_y // FACTOR, basin_x // FACTOR])
if sink_cell < 0:
    raise SystemExit("the desert basin's middle is not on land")
sinks = [(sink_cell, 5.0)]

t0 = time.time()
ground = grid.flat(steep)
eased = ground.copy()
for round_number in range(GATHER_ROUNDS + 1):
    z, to, order, closed = hydro.climb(grid, eased, KM, sinks)
    flow = hydro.gather(grid, order, to, gathering)
    eased = ground / (1.0 + EASE * np.sqrt(flow / 40.0))
    print("climb %d: highest %.0f m, mean %.0f m, biggest gathering %.0f m3/s  (%.0fs)" % (
        round_number + 1, z.max(), z.mean(), flow.max(), time.time() - t0))
flow = hydro.gather(grid, order, to, gain)
height = grid.full(z)
np.savez_compressed(OUT + "/drain%d.npz" % FACTOR, height=height, to=to, order=order, closed=closed, runoff=runoff,
                    steep=grid.full(eased), volcanoes=np.array(volcanoes), basin=np.array([basin_y, basin_x]))
for k in range(1, 10):
    values = height[is_k[k]]
    print("  kingdom %d: mean %5.0f m, highest %5.0f m, a tenth lies under %4.0f m" % (k, values.mean(), values.max(), np.percentile(values, 10)))
basin_cells = hydro.outlets(grid, order, to, closed) == sink_cell
print("the desert basin gathers %.0f km2" % (basin_cells.sum() * KM * KM))

# -- a look ---------------------------------------------------------------------------------------
gy, gx = np.gradient(height, KM * 1000.0)
light = np.clip(0.62 + 2.6 * (-gx - gy) / np.sqrt(1.0 + gx ** 2 + gy ** 2), 0.2, 1.35)
stops = np.array([0, 60, 300, 800, 1500, 2400, 3300], dtype=np.float64)
tints = np.array([[150, 190, 140], [185, 210, 150], [225, 220, 160], [205, 175, 125], [165, 130, 100], [200, 190, 185], [250, 250, 250]], dtype=np.float64)
tint = np.stack([np.interp(height, stops, tints[:, c]) for c in range(3)], axis=-1)
picture = np.clip(tint * light[..., None], 0, 255)
picture[~land] = (181, 235, 255)
river = grid.full(flow)
picture[(river > 15) & (river <= 60)] = (110, 160, 240)
picture[(river > 60) & (river <= 300)] = (40, 110, 230)
picture[river > 300] = (10, 60, 200)
border = np.zeros((h, w), dtype=bool)
border[:-1, :] |= (king[:-1, :] != king[1:, :]) & land[:-1, :] & land[1:, :]
border[:, :-1] |= (king[:, :-1] != king[:, 1:]) & land[:, :-1] & land[:, 1:]
picture[border] = (233, 0, 255)
scale = 2 if FACTOR == 4 else 1
Image.fromarray(picture.astype(np.uint8)).resize((w * scale, h * scale), Image.NEAREST).save(OUT + "/drain%d_look.png" % FACTOR)
print("biggest river %.0f m3/s; cells over 15 m3/s: %d (%.1f%% of the land)" % (river.max(), (river > 15).sum(), 100 * (river > 15).sum() / land.sum()))
print("saved drain%d.npz and drain%d_look.png" % (FACTOR, FACTOR))
