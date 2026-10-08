"""First look at the MapCreation images and how they relate to the in-game art."""
import sys
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ROOT = sys.argv[1]


def load(path):
    image = Image.open(path).convert("RGBA")
    return np.asarray(image)


def top_colours(pixels, count=12):
    flat = pixels.reshape(-1, 4)
    packed = (flat[:, 0].astype(np.uint32) << 24) | (flat[:, 1].astype(np.uint32) << 16) \
        | (flat[:, 2].astype(np.uint32) << 8) | flat[:, 3].astype(np.uint32)
    values, counts = np.unique(packed, return_counts=True)
    order = np.argsort(-counts)
    total = flat.shape[0]
    print("  %d unique colours" % values.size)
    for i in order[:count]:
        v = int(values[i])
        print("    rgba(%3d,%3d,%3d,%3d)  %9d  %6.2f%%" % (
            (v >> 24) & 255, (v >> 16) & 255, (v >> 8) & 255, v & 255, counts[i], 100.0 * counts[i] / total))


def bbox(mask):
    rows = np.flatnonzero(mask.any(axis=1))
    cols = np.flatnonzero(mask.any(axis=0))
    return cols[0], rows[0], cols[-1] + 1, rows[-1] + 1


creation = load(ROOT + "/MapCreation/WorldMapV1.png")
regions = load(ROOT + "/MapCreation/WorldMapRegions.png")
art = load(ROOT + "/vcom/WorldMap/WorldMapV1.png")
mask = load(ROOT + "/vcom/WorldMap/WorldMapV1LandMask.png")

for name, pixels in (("MapCreation/WorldMapV1", creation), ("MapCreation/WorldMapRegions", regions),
                     ("vcom art", art), ("vcom mask", mask)):
    print(name, pixels.shape)
    top_colours(pixels)

# The sea in the creation images, and what is not sea.
sea = creation[0, 0]
print("creation sea colour (corner):", sea)
print("corners:", creation[0, 0], creation[0, -1], creation[-1, 0], creation[-1, -1])

# Land in each: more than half white after opacity, as BakeLand has it.
def land_of(pixels):
    rgb = pixels[..., :3].astype(np.float32)
    alpha = pixels[..., 3:4].astype(np.float32) / 255.0
    lum = (rgb * alpha).mean(axis=2)
    return lum > 127.5

# In the creation images the sea is light blue, which is "more than half white"
# by luminance, so tell land by being near white in all three channels instead.
def white_of(pixels, floor=240):
    return (pixels[..., 0] >= floor) & (pixels[..., 1] >= floor) & (pixels[..., 2] >= floor) & (pixels[..., 3] >= 128)

art_land = land_of(art)
art_drawn = art[..., 3] > 0
print("vcom art: land px", int(art_land.sum()), "bbox land", bbox(art_land), "bbox drawn", bbox(art_drawn))
mask_land = land_of(mask)
print("vcom mask: land px", int(mask_land.sum()), "bbox", bbox(mask_land),
      "same as art land:", bool((mask_land == art_land).all()), "differing px", int((mask_land != art_land).sum()))

creation_white = white_of(creation)
dark = (creation[..., :3].astype(np.int32).sum(axis=2) < 200)
print("creation: white px", int(creation_white.sum()), "bbox white", bbox(creation_white),
      "dark px", int(dark.sum()), "bbox dark", bbox(dark))

# Scale between them, from the land boxes.
ax0, ay0, ax1, ay1 = bbox(art_land)
cx0, cy0, cx1, cy1 = bbox(creation_white)
print("art land box size", ax1 - ax0, ay1 - ay0, " creation white box size", cx1 - cx0, cy1 - cy0)
print("scale x", (cx1 - cx0) / (ax1 - ax0), "scale y", (cy1 - cy0) / (ay1 - ay0))
dx0, dy0, dx1, dy1 = bbox(art_drawn)
ex0, ey0, ex1, ey1 = bbox(dark)
print("art drawn box", (dx0, dy0, dx1, dy1), "size", dx1 - dx0, dy1 - dy0)
print("creation dark box", (ex0, ey0, ex1, ey1), "size", ex1 - ex0, ey1 - ey0)
print("scale by ink x", (ex1 - ex0) / (dx1 - dx0), "y", (ey1 - ey0) / (dy1 - dy0))

# Differences between the two creation images.
differ = (creation != regions).any(axis=2)
print("creation vs regions: differing px", int(differ.sum()), "bbox", bbox(differ) if differ.any() else None)
