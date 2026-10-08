"""The drawn regions and drafts side by side, lines thickened so they survive the shrinking."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage
Image.MAX_IMAGE_PIXELS = None
root, out, save_as = sys.argv[1], sys.argv[2], sys.argv[3]
paths = [root + "/MapCreation/WorldMapRegions.png"] + sys.argv[4:]
tiles = []
for path in paths:
    pixels = np.asarray(Image.open(path).convert("RGB")).copy()
    r, g, b = pixels[..., 0].astype(int), pixels[..., 1].astype(int), pixels[..., 2].astype(int)
    pink = (g < r - 60) & (g < b - 60) & (r > 150) & (b > 150)
    pixels[ndimage.binary_dilation(pink, iterations=4)] = (233, 0, 255)
    tiles.append(Image.fromarray(pixels).resize((pixels.shape[1] // 4, pixels.shape[0] // 4), Image.LANCZOS))
sheet = Image.new("RGB", (sum(t.width for t in tiles) + 8 * (len(tiles) - 1), tiles[0].height), (40, 40, 40))
x = 0
for t in tiles:
    sheet.paste(t, (x, 0)); x += t.width + 8
sheet.save(save_as)
print(sheet.size)
