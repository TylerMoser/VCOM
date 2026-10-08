"""The regions drawn on MapCreation/WorldMapRegions.png: what closes them, how big each is,
which touch, and how the creation images line up with the in-game art."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT = sys.argv[1]
OUT = sys.argv[2]


def load(path):
    return np.asarray(Image.open(path).convert("RGBA"))


regions = load(ROOT + "/MapCreation/WorldMapRegions.png")
creation = load(ROOT + "/MapCreation/WorldMapV1.png")
h, w = regions.shape[:2]
r = regions[..., 0].astype(np.int32)
g = regions[..., 1].astype(np.int32)
b = regions[..., 2].astype(np.int32)

white = (r >= 250) & (g >= 250) & (b >= 250)
# Magenta and its blends toward white: green well under red and blue.
magentaish = (g < r - 25) & (g < b - 25) & (r > 150) & (b > 150)
dark = (r + g + b) < 300
seaish = (b > 200) & (r < 215) & (g > 200) & ~white
print("pixels: white %d  magenta-ish %d  dark %d  sea-ish %d  other %d" % (
    white.sum(), magentaish.sum(), dark.sum(), seaish.sum(),
    (~white & ~magentaish & ~dark & ~seaish).sum()))

# What differs from the plain coastline image, by colour.
differ = (regions != creation).any(axis=2)
diff_pixels = regions[differ]
packed = (diff_pixels[:, 0].astype(np.uint32) << 16) | (diff_pixels[:, 1].astype(np.uint32) << 8) | diff_pixels[:, 2]
values, counts = np.unique(packed, return_counts=True)
order = np.argsort(-counts)
print("colours of the %d pixels added over the plain coastline (%d unique):" % (differ.sum(), values.size))
for i in order[:10]:
    v = int(values[i])
    print("   rgb(%3d,%3d,%3d) %7d" % ((v >> 16) & 255, (v >> 8) & 255, v & 255, counts[i]))

# Land in the plain image, everything inside the coastline ink: label the non-ink, take the
# pieces that are white.
plain_white = (creation[..., 0] >= 250) & (creation[..., 1] >= 250) & (creation[..., 2] >= 250)
land_labels, land_count = ndimage.label(plain_white)
land_sizes = ndimage.sum_labels(plain_white, land_labels, index=np.arange(1, land_count + 1))
big_land = np.argsort(-land_sizes)
print("plain image: %d white pieces; biggest:" % land_count)
for i in big_land[:14]:
    ys, xs = ndimage.center_of_mass(plain_white, land_labels, i + 1)
    print("   piece %4d  %9d px  centre (%.0f, %.0f)" % (i + 1, land_sizes[i], xs, ys))
total_land = float(land_sizes.sum())
print("   total white %d px" % total_land)

# The regions: white pieces of the regions image, 4-connected so a line one pixel wide that
# only steps diagonally still closes.
labels, count = ndimage.label(white)
all_slices = ndimage.find_objects(labels)
sizes = ndimage.sum_labels(white, labels, index=np.arange(1, count + 1))
order = np.argsort(-sizes)
print("regions image: %d white pieces; those over 2000 px:" % count)
pieces = []
for i in order:
    if sizes[i] < 2000:
        break
    index = i + 1
    cy, cx = ndimage.center_of_mass(white, labels, index)
    sl = all_slices[index - 1]
    pieces.append((index, int(sizes[i]), cx, cy, sl))
    print("   piece %5d  %8d px  %5.2f%% of land  centre (%.0f, %.0f)  box x %d..%d y %d..%d" % (
        index, sizes[i], 100.0 * sizes[i] / total_land, cx, cy,
        sl[1].start, sl[1].stop, sl[0].start, sl[0].stop))

# Which piece each number sits in: the commonest white piece in a ring round where it is drawn.
numbers = {1: (990, 694), 2: (1470, 414), 3: (1594, 1656), 4: (2030, 1280), 5: (2394, 1960),
           6: (636, 1296), 7: (1096, 2026), 8: (1904, 2820), 9: (2436, 3516)}
name_of = {}
for number, (x, y) in numbers.items():
    window = labels[y - 90:y + 90, x - 90:x + 90]
    found, tally = np.unique(window[window > 0], return_counts=True)
    # The piece a number sits in is the big one round it, not the holes in its own glyph.
    best = max(zip(found, tally), key=lambda pair: sizes[pair[0] - 1])
    name_of[int(best[0])] = number
print("number -> piece:", {v: k for k, v in name_of.items()})

region_of = np.zeros(count + 1, dtype=np.int32)
for index, number in name_of.items():
    region_of[index] = number
region_map = region_of[labels]
print()
print("region  area px   share of the nine   centre (x, y)        box")
nine_total = float(sum(sizes[i - 1] for i in name_of))
for index, number in sorted(name_of.items(), key=lambda pair: pair[1]):
    cy, cx = ndimage.center_of_mass(white, labels, index)
    sl = all_slices[index - 1]
    print("  %d   %8d   %5.2f%%   (%.0f, %.0f)   x %d..%d  y %d..%d  (%d x %d)" % (
        number, sizes[index - 1], 100.0 * sizes[index - 1] / nine_total, cx, cy,
        sl[1].start, sl[1].stop, sl[0].start, sl[0].stop,
        sl[1].stop - sl[1].start, sl[0].stop - sl[0].start))
print("  the nine together: %d px = %.2f%% of the plain image's white" % (nine_total, 100 * nine_total / total_land))

# Which regions touch across a magenta line, and which reach the coast: spread each region a few
# pixels and see what it runs into.
struct = ndimage.generate_binary_structure(2, 2)
touch = {}
coast = {}
sea_or_ink = (dark | seaish) & ~magentaish
for number in range(1, 10):
    grown = ndimage.binary_dilation(region_map == number, structure=struct, iterations=7)
    others, tally = np.unique(region_map[grown & (region_map != number) & (region_map > 0)], return_counts=True)
    touch[number] = {int(o): int(t) for o, t in zip(others, tally) if t > 300}
    coast[number] = int((grown & sea_or_ink).sum())
print()
for number in range(1, 10):
    print("region %d borders %s; coast pixels within reach: %d" % (number, sorted(touch[number]), coast[number]))

# The magenta: how much is line and how much is the numbers, and how thick the lines are.
m_labels, m_count = ndimage.label(magentaish, structure=struct)
m_sizes = ndimage.sum_labels(magentaish, m_labels, index=np.arange(1, m_count + 1))
m_slices = ndimage.find_objects(m_labels)
print()
print("magenta pieces (8-connected): %d" % m_count)
for i in np.argsort(-m_sizes)[:16]:
    sl = m_slices[i]
    print("   %7d px  box x %d..%d y %d..%d" % (m_sizes[i], sl[1].start, sl[1].stop, sl[0].start, sl[0].stop))
# Thickness: the distance transform inside the biggest piece (the lines).
lines = m_labels == (int(np.argmax(m_sizes)) + 1)
depth = ndimage.distance_transform_edt(lines)
print("line network: %d px; deepest point %.2f px from its edge; mean of ridge %.2f" % (
    lines.sum(), depth.max(), depth[lines].mean()))
# Runs along rows and columns: typical width where a line crosses.
def run_lengths(mask):
    lengths = []
    for row in mask[::37]:
        padded = np.concatenate(([0], row.astype(np.int8), [0]))
        edges = np.flatnonzero(np.diff(padded))
        lengths.extend((edges[1::2] - edges[::2]).tolist())
    return np.array(lengths)
across = run_lengths(lines)
down = run_lengths(lines.T)
print("row runs: median %s, 90th pct %s; column runs: median %s, 90th pct %s" % (
    np.median(across), np.percentile(across, 90), np.median(down), np.percentile(down, 90)))

# Save a flat-colour picture of the nine regions for a look.
palette = np.array([[181, 235, 255], [230, 159, 0], [86, 180, 233], [0, 158, 115], [240, 228, 66],
                    [0, 114, 178], [213, 94, 0], [204, 121, 167], [150, 150, 150], [120, 200, 80]], dtype=np.uint8)
picture = palette[region_map]
picture[dark] = 0
picture[(region_map == 0) & white] = 255
Image.fromarray(picture).resize((w // 2, h // 2), Image.LANCZOS).save(OUT + "/regions_flat.png")
np.save(OUT + "/region_map.npy", region_map.astype(np.uint8))
print("saved", OUT + "/regions_flat.png")
