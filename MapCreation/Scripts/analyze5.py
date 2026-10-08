"""Where the game's present map objects fall among the nine regions, and what sizes the land
would have at a few real-world scales."""
import math, sys
import numpy as np
OUT = sys.argv[1]
region_map = np.load(OUT + "/region_map.npy")
SX, SY, TX, TY = 0.42289, 0.45030, -316.02, 0.30   # art px -> creation px
ROT = math.radians(-10.0)                           # the Map sprite's rotation in WorldMap.tscn

def world_to_creation(wx, wy):
    # world -> the sprite's own space (undo its rotation) -> art pixels -> creation pixels
    c, s = math.cos(-ROT), math.sin(-ROT)
    lx, ly = wx * c - wy * s, wx * s + wy * c
    u, v = lx + 4440.0, ly + 4440.0
    return u, v, u * SX + TX, v * SY + TY

def region_at(wx, wy):
    u, v, x, y = world_to_creation(wx, wy)
    xi, yi = int(round(x)), int(round(y))
    inside = 0 <= yi < region_map.shape[0] and 0 <= xi < region_map.shape[1]
    return (u, v, x, y, int(region_map[yi, xi]) if inside else -1)

things = {"Party start": (0, 0), "Village1": (1000, 0), "Forest polygon origin": (-735, -1377)}
forest_poly = [(-1122, -84), (-970, -507), (-50, -600), (709, -734), (1013, -279), (980, 252), (655, 555), (-537, 653), (-851, 306)]
for name, (wx, wy) in things.items():
    u, v, x, y, r = region_at(wx, wy)
    print("%-22s world (%6.0f, %6.0f) -> art px (%6.0f, %6.0f) -> creation px (%5.0f, %5.0f) -> region %d" % (name, wx, wy, u, v, x, y, r))
tally = {}
for i in range(20000):
    # sample the forest polygon's bounding box and keep points inside it
    pass
import random
random.seed(1)
def inside(poly, px, py):
    hit = False
    for i in range(len(poly)):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 <= py) != (y2 <= py) and px < x1 + (py - y1) * (x2 - x1) / (y2 - y1):
            hit = not hit
    return hit
xs = [p[0] for p in forest_poly]; ys = [p[1] for p in forest_poly]
n = 0
for i in range(60000):
    px = random.uniform(min(xs), max(xs)); py = random.uniform(min(ys), max(ys))
    if inside(forest_poly, px, py):
        n += 1
        r = region_at(px - 735, py - 1377)[4]
        tally[r] = tally.get(r, 0) + 1
print("forest polygon by region:", {k: "%.0f%%" % (100.0 * v / n) for k, v in sorted(tally.items())})
area = 0.0
for i in range(len(forest_poly)):
    x1, y1 = forest_poly[i]; x2, y2 = forest_poly[(i + 1) % len(forest_poly)]
    area += x1 * y2 - x2 * y1
print("forest polygon area: %.0f art px^2 = %.2f%% of the land" % (abs(area) / 2, 100 * abs(area) / 2 / 32604144))

# Scales. The land in the game's art: 32,604,144 px^2, 7082 wide by 8849 tall (unrotated art).
LAND_PX = 32604144.0
W, H = 7082.0, 8849.0
print()
print("if the land were as big as...      km/px    N-S km   E-W km   deg lat   day's walk (30 km) in px   party crosses N-S at 250 px/s")
for name, km2 in (("Ireland (84,400 km2)", 84421), ("Great Britain (209,300)", 209331), ("Honshu (227,900)", 227960),
                  ("Madagascar (587,000)", 587041), ("Iberia (583,000)", 583254), ("Borneo (743,300)", 743330),
                  ("Greenland (2,166,000)", 2166086), ("Australia (7,692,000)", 7692024)):
    k = math.sqrt(km2 / LAND_PX)
    print("  %-26s %7.3f  %7.0f  %7.0f   %6.1f   %8.0f                    %.0f s" % (
        name, k, H * k, W * k, H * k / 111.2, 30.0 / k, H / 250.0))
