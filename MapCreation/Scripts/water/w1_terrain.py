"""The lie of the land: a height for every cell, made to suit the nine kingdoms' biomes and then
worn by its own rivers.

Nothing in the repo says how high anything is, so this decides it. The three mountain kingdoms
(1 tundra, 2 volcanic, 3 temperate) are taken as one high country, highest where it is furthest
from its own edge; the other kingdoms fall away from its foot to the sea, each in its own way
(the swamp drops at once to sea level, the grassland and desert are long aprons, the forest
kingdoms carry the range on south as hills). That is roughened and then eroded: water is run
over the land again and again, each river cutting its bed down toward the level of the water
below it, the more the more water it carries, so valleys, ridges and rivers come to agree.

Worked at a quarter of the picture's size. Usage: w1_terrain.py <out dir> [rounds]
"""
import sys
import time
import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, sys.argv[0].replace("\\", "/").rsplit("/", 1)[0])
import hydro

OUT = sys.argv[1]
ROUNDS = int(sys.argv[2]) if len(sys.argv) > 2 else 60
FACTOR = 4
KM = 0.335 * FACTOR                      # one cell, at Texas's area for the island
SEED = 20261006
PULL = 0.10                              # how hard a river of 1 m3/s draws its bed down in a round
SLUMP = 0.12                             # share of each round's surface taken from its own blur

grids = np.load(OUT + "/grid%d.npz" % FACTOR)
land, king = grids["land"], grids["king"]
h, w = land.shape
rng = np.random.default_rng(SEED)
yy, xx = np.mgrid[0:h, 0:w]


def blurred(field, sigma_km, mask=land):
    """[field] smoothed over [mask] only, so what lies outside never drags a value down."""
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
    """Rough ground: bumps at each of [scales_km], the broad ones tallest. About -1 to 1."""
    total = np.zeros((h, w))
    weight = 0.0
    for scale in scales_km:
        layer = ndimage.gaussian_filter(rng.standard_normal((h, w)), scale / KM)
        layer /= layer.std()
        amount = (scale / scales_km[0]) ** hurst
        total += amount * layer
        weight += amount ** 2
    return total / np.sqrt(weight) / 2.0


def distance_to(mask):
    return ndimage.distance_transform_edt(~mask) * KM


is_k = {k: king == k for k in range(1, 10)}
sea = ~land
coast = distance_to(sea)                                  # km to the sea
near = {k: distance_to(is_k[k]) for k in range(1, 10)}
unit = lambda field, mask: np.where(mask, field / max(field[mask].max(), 1e-9), 0.0)

# -- the broad shape ---------------------------------------------------------------------------
high = is_k[1] | is_k[2] | is_k[3]                        # the high country
low = land & ~high
into_high = np.where(high, ndimage.distance_transform_edt(high) * KM, 0.0)      # km in from its edge
from_high = distance_to(high)                             # km out from its foot

# The low kingdoms: each falls from a height at the mountains' foot to a level far from them.
far = by_kingdom({4: 380, 5: 110, 6: 140, 7: 5, 8: 230, 9: 130}, 12.0)
foot = by_kingdom({4: 820, 5: 520, 6: 620, 7: 170, 8: 650, 9: 130}, 12.0)
apron = by_kingdom({4: 85, 5: 110, 6: 70, 7: 26, 8: 60, 9: 30}, 12.0, default=50.0)
lowland = far + (foot - far) * np.exp(-from_high / np.maximum(apron, 1.0))
# 8 and 9 carry the range on south as hills, highest along the middle of the neck and the tail.
spine8 = np.where(is_k[8], distance_to(sea | is_k[7] | is_k[5]), 0.0)
spine9 = np.where(is_k[9], coast, 0.0)
lowland += 560.0 * unit(spine8, is_k[8]) ** 1.15 + 620.0 * unit(spine9, is_k[9]) ** 1.3
# 6: two ridges run out to its capes.
lowland += 330.0 * unit(np.where(is_k[6], coast, 0.0), is_k[6]) ** 1.2

# The high country stands on the level of whatever lies at its foot, and rises from there.
_, (fy, fx) = ndimage.distance_transform_edt(~low, return_indices=True)
footing = blurred(np.where(high, lowland[fy, fx], 0.0), 30.0, high)
reach = np.minimum(coast, 60.0) / 60.0                    # a shore under the mountains has no foot to stand on
rise = by_kingdom({1: 1550, 2: 950, 3: 2350}, 18.0)
highland = footing * reach + rise * (1.0 - np.exp(-into_high / 60.0))
design = np.where(high, highland, lowland)
design = blurred(design, 6.0)

# 2, the volcanoes: cones on the lava plateau, one of them a collapsed ring.
cones = np.zeros((h, w))
k2 = np.argwhere(is_k[2] & (ndimage.distance_transform_edt(is_k[2]) * KM > 34.0))
picked = []
for _ in range(4000):
    if len(picked) >= 9:
        break
    y, x = k2[rng.integers(len(k2))]
    if all(np.hypot(y - py, x - px) * KM > 54.0 for py, px in picked):
        picked.append((int(y), int(x)))
volcanoes = []
for n, (y, x) in enumerate(picked):
    r = np.hypot(yy - y, xx - x) * KM
    if n == 0:
        cones += 700.0 * np.exp(-(r / 30.0) ** 2)         # the ring and its hollow are cut in later, with the lakes
        volcanoes.append((y, x, 1))
    else:
        cones += rng.uniform(1100.0, 2100.0) * np.exp(-r / rng.uniform(9.0, 13.0)) + 260.0 * np.exp(-(r / 30.0) ** 2)
        volcanoes.append((y, x, 0))
design += np.where(land, cones, 0.0)

# -- roughness ---------------------------------------------------------------------------------
rough = by_kingdom({1: 430, 2: 190, 3: 560, 4: 250, 5: 40, 6: 330, 7: 4, 8: 230, 9: 210}, 12.0)
ridges = 1.0 - 2.0 * np.abs(noise([80, 40, 20, 10], 0.8))                 # sharp crests, broad valleys
bumps = noise([140, 70, 35, 17, 8, 4], 0.85)
height = design + rough * (1.1 * bumps + 0.5 * (ridges - 0.4))
# The desert's ranges and the forest's ridges: bumps drawn out along the island.
drawn_out = ndimage.gaussian_filter(rng.standard_normal((h, w)), (26.0 / KM, 7.0 / KM))
drawn_out = ndimage.rotate(drawn_out, 28.0, reshape=False, mode="reflect")
drawn_out /= drawn_out.std()
height += by_kingdom({4: 280.0, 8: 170.0}, 12.0) * drawn_out

# -- the coast -----------------------------------------------------------------------------------
shelf = by_kingdom({1: 12, 2: 11, 3: 10, 4: 26, 5: 42, 6: 13, 7: 70, 8: 18, 9: 22}, 14.0)
height = np.maximum(height, 0.0) * (1.0 - np.exp(-coast / np.maximum(shelf, 1.0)))
least = 0.6 + 0.10 * coast                                                # always some fall to the sea
height = np.where(land, np.maximum(height, least), 0.0)

# -- rain ---------------------------------------------------------------------------------------
# What runs off each cell in a year, in metres of water: the kingdoms' climates, with more on the
# windward side of the central range (the wind is from the west) and less in its lee.
across = near[7] + near[6]
lee = near[4] + near[5]
wet_side = np.where(is_k[3], lee / np.maximum(across + lee, 1e-9), 0.0)       # 1 at the wet edge, 0 at the dry
runoff = by_kingdom({1: 0.52, 2: 0.33, 3: 1.05, 4: 0.006, 5: 0.06, 6: 2.1, 7: 0.65, 8: 0.42, 9: 1.35}, 14.0)
runoff *= np.where(is_k[3], 0.5 + 1.0 * wet_side, 1.0)

grid = hydro.Grid(land)
CUMECS = (KM * KM) * 1e6 / 31.5e6                         # a metre a year off one cell, in m3/s
z = grid.flat(height).astype(np.float64) + rng.random(grid.n) * 1e-3
gain = grid.flat(runoff) * CUMECS
wearing = np.maximum(grid.flat(runoff), 0.15) * CUMECS    # dry land still wears, by its rare floods
least_flat = grid.flat(least)
print("heights laid out: highest %.0f m, mean %.0f m" % (z.max(), z.mean()))

# -- wear ----------------------------------------------------------------------------------------
t0 = time.time()
for round_number in range(ROUNDS):
    order, to = hydro.route(grid, z)
    filled = hydro.spill_levels(grid, z, order, to)
    ponded = float((filled > z + 0.5).mean())
    flow = hydro.gather(grid, order, to, wearing)
    pull = PULL * np.sqrt(flow) / hydro.step_lengths(grid, to)
    cut = hydro.incise(grid, filled, order, to, pull)
    soft = grid.flat(blurred(grid.full(cut), 1.2 * KM))
    wanted = np.maximum((1.0 - SLUMP) * cut + SLUMP * soft, least_flat)
    z = hydro.settle(grid, wanted, order, to) + rng.random(grid.n) * 1e-5
    if round_number % 10 == 9 or round_number == ROUNDS - 1:
        print("round %3d: highest %.0f m, mean %.0f m, ponded before it %.2f%%  (%.0fs)" % (
            round_number + 1, z.max(), z.mean(), 100 * ponded, time.time() - t0))

order, to = hydro.route(grid, z)
filled = hydro.spill_levels(grid, z, order, to)
flow = hydro.gather(grid, order, to, gain)
np.savez_compressed(OUT + "/terrain%d.npz" % FACTOR, height=grid.full(filled), design=np.where(land, height, 0.0),
                    runoff=runoff, volcanoes=np.array(volcanoes))
for k in range(1, 10):
    values = grid.full(filled)[is_k[k]]
    print("  kingdom %d: mean %5.0f m, highest %5.0f m, a tenth lies under %4.0f m" % (k, values.mean(), values.max(), np.percentile(values, 10)))

# -- a look ---------------------------------------------------------------------------------------
ground = grid.full(filled)
gy, gx = np.gradient(ground, KM * 1000.0)
light = np.clip(0.62 + 2.6 * (-gx - gy) / np.sqrt(1.0 + gx ** 2 + gy ** 2), 0.2, 1.35)
stops = np.array([0, 60, 300, 800, 1500, 2400, 3300], dtype=np.float64)
tints = np.array([[150, 190, 140], [185, 210, 150], [225, 220, 160], [205, 175, 125], [165, 130, 100], [200, 190, 185], [250, 250, 250]], dtype=np.float64)
tint = np.stack([np.interp(ground, stops, tints[:, c]) for c in range(3)], axis=-1)
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
Image.fromarray(picture.astype(np.uint8)).resize((w * 2, h * 2), Image.NEAREST).save(OUT + "/terrain%d_look.png" % FACTOR)
print("biggest river %.0f m3/s; cells over 15 m3/s: %d (%.1f%% of the land)" % (river.max(), (river > 15).sum(), 100 * (river > 15).sum() / land.sum()))
print("saved terrain%d.npz and terrain%d_look.png" % (FACTOR, FACTOR))
