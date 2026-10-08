"""Close-ups of where each border meets the coast, and of the junctions, for two drafts side by side."""
import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
out = sys.argv[1]
names = sys.argv[2:]
spots = {"NW 1|6": (520, 700), "N 1|2": (1100, 230), "NE 2|4": (1850, 760), "E 4|5": (2800, 1420),
         "E 5|8": (2490, 2720), "W 6|7": (260, 1920), "SW 7|8": (1210, 2830), "S 8|9 west": (1712, 3265),
         "S 8|9 east": (2540, 3070), "J 1-3-6": (980, 1540), "J 1-2-3 / 2-3-4": (1540, 1420), "J 3-5-8 / 3-7-8": (1920, 2520)}
half = 170
sheet = Image.new("RGB", (len(spots) // 2 * (2 * half + 6) * 1, 2 * len(names) * (2 * half + 6)), (60, 60, 60))
for row, name in enumerate(names):
    image = Image.open(out + "/draft_%s.png" % name).convert("RGB")
    for k, (label, (x, y)) in enumerate(spots.items()):
        tile = image.crop((x - half, y - half, x + half, y + half))
        col = k % (len(spots) // 2)
        line = k // (len(spots) // 2)
        sheet.paste(tile, (col * (2 * half + 6), (row * 2 + line) * (2 * half + 6)))
sheet.save(out + "/ends_sheet.png")
print(sheet.size, list(spots))
