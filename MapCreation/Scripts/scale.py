"""The island at Texas's area: kilometres per pixel of the new shape, each kingdom's area, and
what 4-6 duchies of 4-6 counties come to."""
import math, sys
import numpy as np
OUT = sys.argv[1]
region_map = np.load(OUT + "/region_map.npy")
LAND_PX = 6199855.0            # every white pixel of MapCreation/WorldMapV1.png, islands included
MAINLAND_PX = float((region_map > 0).sum())
for label, km2 in (("Texas, total area", 695662.0), ("Texas, land only", 676587.0)):
    k2 = km2 / LAND_PX
    k = math.sqrt(k2)
    print("%s %.0f km2: %.5f km per px (%.1f m), %.5f km2 per px2; land box 2996 x 3985 px = %.0f x %.0f km; %.1f deg of latitude" % (
        label, km2, k, k * 1000, k2, 2996 * k, 3985 * k, 3985 * k / 111.2))
K2 = 695662.0 / LAND_PX
K = math.sqrt(K2)
print("islands off the mainland: %.0f px = %.0f km2" % (LAND_PX - MAINLAND_PX, (LAND_PX - MAINLAND_PX) * K2))
print()
print("kingdom  area km2   as a circle: radius km   5x5: duchy / county km2   best 4-6 x 4-6 for ~3,000 km2 counties")
total_counties = 0
areas = {}
for n in range(1, 10):
    area = float((region_map == n).sum()) * K2
    areas[n] = area
    best = None
    for d in (4, 5, 6):
        for c in (4, 5, 6):
            county = area / (d * c)
            score = abs(math.log(county / 3000.0))
            if best is None or score < best[0] - 1e-9:
                best = (score, d, c, county)
    _, d, c, county = best
    total_counties += d * c
    print("  %d     %7.0f      %5.0f                  %6.0f / %5.0f           %d x %d = %2d counties of %5.0f km2, duchies of %6.0f km2" % (
        n, area, math.sqrt(area / math.pi), area / 5, area / 25, d, c, d * c, county, area / d))
print("counties in all, sized that way: %d (Texas has 254); with 5 x 5 everywhere: 225; range possible 144 to 324" % total_counties)
mean = sum(areas.values()) / 9
print("mean kingdom %.0f km2; mean duchy at 5 per kingdom %.0f; mean county at 25 per kingdom %.0f" % (mean, mean / 5, mean / 25))
for name, a in (("county 3,000 km2", 3000.0), ("duchy 15,500 km2", 15500.0), ("kingdom 77,000 km2", 77000.0)):
    print("%s: circle radius %.0f km, square side %.0f km; in px: radius %.0f, side %.0f" % (
        name, math.sqrt(a / math.pi), math.sqrt(a), math.sqrt(a / math.pi) / K, math.sqrt(a) / K))
print("a day's walk of 30 km = %.0f px; a day's ride of 50 km = %.0f px" % (30 / K, 50 / K))
