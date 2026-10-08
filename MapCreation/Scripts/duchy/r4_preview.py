"""A picture to judge roads by: the land shaded by its relief and tinted by its height, the
water, the borders faintly, the settlements, and the roads as laid (cell by cell, unsmoothed).

Usage: r4_preview.py <repo root> <duchy out dir> <roads out dir> <name> [candidates]
"""
import pickle
import sys
import numpy as np
from PIL import Image
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
ROOT, OUT, ROADS, NAME = sys.argv[1:5]
CANDIDATES = len(sys.argv) > 5
fields = np.load(OUT + "/fields1.npz")
height, river, lake, king = fields["height"], fields["river"], fields["lake"], fields["king"]
land = np.load(ROADS + "/land.npy")
h, w = land.shape
base = np.asarray(Image.open(ROOT + "/MapCreation/Settlements.png").convert("RGB"))

# Relief: lit from the north-west, heights tinted green to brown to white.
z = ndimage.gaussian_filter(height.astype(np.float32), 1.2)
gy, gx = np.gradient(z)
steep = 8.0 / 335.0
shade = (-gx * steep - gy * steep + 1.0) / np.sqrt((gx * steep) ** 2 + (gy * steep) ** 2 + 1.0) / np.sqrt(3.0)
shade = np.clip(0.45 + 0.75 * shade, 0.25, 1.15)
stops = np.array([0, 150, 500, 1200, 2200, 3400], dtype=np.float32)
tints = np.array([[205, 225, 190], [225, 232, 195], [235, 222, 180], [215, 190, 155], [200, 185, 175], [250, 250, 250]], dtype=np.float32)
look = np.stack([np.interp(z, stops, tints[:, c]) for c in range(3)], axis=2) * shade[..., None]
look = np.clip(look, 0, 255).astype(np.uint8)
look[~land] = base[~land]
look[river | lake] = (60, 130, 225)
lines = land & (base < 250).any(axis=2)
grey = (base[..., 0] == 128) & (base[..., 1] == 128) & (base[..., 2] == 128)
purple = (base[..., 0] == 110) & (base[..., 1] == 30) & (base[..., 2] == 180)
pink = (base[..., 0] == 233) & (base[..., 1] == 0) & (base[..., 2] == 255)
town = np.load(ROADS + "/town.npy") > 0
border = (grey | purple | pink) & ~town
look[border] = (0.55 * look[border] + 0.45 * base[border]).astype(np.uint8)

if CANDIDATES:
    with open(ROADS + "/candidates.pickle", "rb") as handle:
        roads = [dict(road, highway=False) for road in pickle.load(handle)["found"].values()]
else:
    with open(ROADS + "/network.pickle", "rb") as handle:
        roads = list(pickle.load(handle)["laid"].values())
minor = np.zeros((h, w), dtype=bool)
major = np.zeros((h, w), dtype=bool)
for road in roads:
    path = np.array(road["path"])
    # Fill the knight's moves in, so the line is whole.
    steps = np.abs(np.diff(path, axis=0)).max(axis=1)
    if (steps > 1).any():
        filled = [path[0]]
        for a, b in zip(path[:-1], path[1:]):
            if np.abs(b - a).max() > 1:
                filled.append((a + b) // 2)
            filled.append(b)
        path = np.array(filled)
    (major if road["highway"] else minor)[path[:, 0], path[:, 1]] = True
look[ndimage.binary_dilation(minor, structure=np.ones((2, 2), dtype=bool))] = (200, 40, 30)
look[ndimage.binary_dilation(major, structure=np.ones((3, 3), dtype=bool))] = (120, 0, 0)
look[town] = base[town]
Image.fromarray(look).save(OUT + "/%s_full.png" % NAME)
Image.fromarray(look).resize((w // 2, h // 2), Image.LANCZOS).save(OUT + "/%s.png" % NAME)
print("saved %s.png" % NAME)
