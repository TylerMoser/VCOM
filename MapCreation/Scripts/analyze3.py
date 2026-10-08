"""Where the region lines of WorldMapRegions.png leak: line ends that stop short of the coast
or of the line they should meet. Then the nine regions with the gaps closed."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT = sys.argv[1]
OUT = sys.argv[2]

regions = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapRegions.png").convert("RGBA"))
creation = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
h, w = regions.shape[:2]
r = regions[..., 0].astype(np.int32)
g = regions[..., 1].astype(np.int32)
b = regions[..., 2].astype(np.int32)
white = (r >= 250) & (g >= 250) & (b >= 250)
added = (regions != creation).any(axis=2)          # everything drawn over the plain coastline
plain_white = (creation[..., 0] >= 250) & (creation[..., 1] >= 250) & (creation[..., 2] >= 250)
ink = ~plain_white                                    # coast ink and sea of the plain picture
eight = ndimage.generate_binary_structure(2, 2)

# Lines against numerals: a numeral is a compact blob about 70 x 105; lines are long and thin.
a_labels, a_count = ndimage.label(added, structure=eight)
a_slices = ndimage.find_objects(a_labels)
a_sizes = ndimage.sum_labels(added, a_labels, index=np.arange(1, a_count + 1))
numeral = np.zeros_like(added)
line = np.zeros_like(added)
print("pieces drawn over the coastline (8-connected): %d" % a_count)
for i, sl in enumerate(a_slices):
    height = sl[0].stop - sl[0].start
    width = sl[1].stop - sl[1].start
    piece = a_labels[sl] == i + 1
    is_numeral = 85 <= height <= 125 and 45 <= width <= 90 and a_sizes[i] > 1500
    (numeral if is_numeral else line)[sl] |= piece
    if a_sizes[i] >= 40:
        print("   %s %6d px  box x %d..%d y %d..%d" % (
            "numeral" if is_numeral else "line   ", a_sizes[i], sl[1].start, sl[1].stop, sl[0].start, sl[0].stop))
print("line pixels %d, numeral pixels %d" % (line.sum(), numeral.sum()))

# Ends of the lines: a line pixel with one line neighbour (or none).
neighbours = ndimage.convolve(line.astype(np.int16), np.ones((3, 3), dtype=np.int16), mode="constant") - line
ends = line & (neighbours <= 1)
# How far each end is from the coast ink, and from any line pixel not its own piece.
to_ink = ndimage.distance_transform_edt(~ink)
l_labels, l_count = ndimage.label(line, structure=eight)
print()
print("line pieces: %d; ends:" % l_count)
ys, xs = np.nonzero(ends)
report = []
for y, x in zip(ys, xs):
    own = l_labels[y, x]
    y0, y1, x0, x1 = max(0, y - 40), min(h, y + 41), max(0, x - 40), min(w, x + 41)
    window = l_labels[y0:y1, x0:x1]
    other = (window > 0) & (window != own)
    if other.any():
        oy, ox = np.nonzero(other)
        gap = float(np.sqrt(((oy + y0 - y) ** 2 + (ox + x0 - x) ** 2).min()))
    else:
        gap = float("inf")
    report.append((x, y, own, float(to_ink[y, x]), gap))
for x, y, own, ink_distance, gap in sorted(report, key=lambda item: (item[2], item[1])):
    verdict = "meets the coast" if ink_distance <= 1.5 else (
        "GAP to coast %.1f px" % ink_distance if ink_distance < gap else "GAP to another line %.1f px" % gap)
    print("   piece %2d end at (%4d, %4d): coast %.1f px away, other line %s px away -> %s" % (
        own, x, y, ink_distance, "%.1f" % gap if gap != float("inf") else ">40", verdict))

# Close the gaps: thicken the lines until every number sits in a piece of its own.
numbers = {1: (990, 694), 2: (1470, 414), 3: (1594, 1656), 4: (2030, 1280), 5: (2394, 1960),
           6: (636, 1296), 7: (1096, 2026), 8: (1904, 2820), 9: (2436, 3516)}
land = plain_white.copy()
big_labels, big_count = ndimage.label(land)
big_sizes = ndimage.sum_labels(land, big_labels, index=np.arange(1, big_count + 1))
mainland = big_labels == (int(np.argmax(big_sizes)) + 1)
for grow in range(0, 12):
    barrier = ndimage.binary_dilation(line, structure=eight, iterations=grow) if grow else line
    open_land = mainland & ~barrier
    labels, count = ndimage.label(open_land)
    sizes = ndimage.sum_labels(open_land, labels, index=np.arange(1, count + 1))
    found = {}
    for number, (x, y) in numbers.items():
        window = labels[y - 110:y + 110, x - 110:x + 110]
        values, tally = np.unique(window[window > 0], return_counts=True)
        found[number] = int(values[np.argmax(tally)])
    distinct = len(set(found.values()))
    print("lines thickened %d px: %d pieces, numbers in %d distinct pieces" % (grow, count, distinct))
    if distinct == 9:
        break

# Give every mainland pixel to the nearest of the nine seeds found, so lines, numerals and the
# thickening all go to a region.
seed = np.zeros((h, w), dtype=np.int32)
for number, index in found.items():
    seed[labels == index] = number
_, (iy, ix) = ndimage.distance_transform_edt(seed == 0, return_indices=True)
region_map = np.where(mainland, seed[iy, ix], 0).astype(np.uint8)
np.save(OUT + "/region_map.npy", region_map)

total = float(mainland.sum())
print()
print("mainland %d px (plain image white, biggest piece)" % total)
print("region   area px   share    centre (x, y)    box")
slices = ndimage.find_objects(region_map)
for number in range(1, 10):
    mask = region_map == number
    cy, cx = ndimage.center_of_mass(mask)
    sl = slices[number - 1]
    print("  %d   %8d   %5.2f%%   (%4.0f, %4.0f)   x %d..%d  y %d..%d" % (
        number, mask.sum(), 100.0 * mask.sum() / total, cx, cy, sl[1].start, sl[1].stop, sl[0].start, sl[0].stop))

# Borders: length of each shared boundary, and each region's coast, counted as pixel edges.
print()
shared = {}
for dy, dx in ((0, 1), (1, 0)):
    first = region_map[: h - dy, : w - dx]
    second = region_map[dy:, dx:]
    crossing = (first != second) & (first > 0) & (second > 0)
    pairs = np.stack([np.minimum(first[crossing], second[crossing]), np.maximum(first[crossing], second[crossing])], axis=1)
    values, tally = np.unique(pairs, axis=0, return_counts=True)
    for (p, q), t in zip(values, tally):
        shared[(int(p), int(q))] = shared.get((int(p), int(q)), 0) + int(t)
coast = {}
not_main = ~mainland
for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
    shifted = np.roll(not_main, (dy, dx), axis=(0, 1))
    edge = mainland & shifted
    values, tally = np.unique(region_map[edge], return_counts=True)
    for v, t in zip(values, tally):
        coast[int(v)] = coast.get(int(v), 0) + int(t)
for (p, q), t in sorted(shared.items()):
    print("border %d-%d: %5d pixel edges" % (p, q, t))
for number in range(1, 10):
    print("region %d coast: %6d pixel edges" % (number, coast.get(number, 0)))

palette = np.array([[181, 235, 255], [230, 159, 0], [86, 180, 233], [0, 158, 115], [240, 228, 66],
                    [0, 114, 178], [213, 94, 0], [204, 121, 167], [150, 150, 150], [120, 200, 80]], dtype=np.uint8)
picture = palette[region_map]
picture[(~mainland) & plain_white] = 255
picture[ink & ((creation[..., :3].astype(np.int32).sum(axis=2)) < 300)] = 0
picture[line | numeral] = (255, 255, 255)
Image.fromarray(picture).resize((w // 2, h // 2), Image.LANCZOS).save(OUT + "/regions_flat.png")
print("saved regions_flat.png")
