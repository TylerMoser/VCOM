"""Close-ups of the region lines' ends and junctions, and of the coast's features, enlarged."""
import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
root, out = sys.argv[1], sys.argv[2]
regions = Image.open(root + "/MapCreation/WorldMapRegions.png").convert("RGB")
spots = {
    "gap_north_coast_1233_206": (1233, 206), "junction_1336_955": (1336, 955), "junction_1497_1103": (1497, 1103),
    "junction_932_1201": (932, 1201), "junction_2026_2327": (2026, 2327), "gap_east_coast_2766_1376": (2766, 1376),
    "gap_2049_1605": (2049, 1605), "gap_1116_1556": (1116, 1556), "gap_1802_2300": (1802, 2300),
}
tiles = []
for name, (x, y) in spots.items():
    box = (x - 40, y - 40, x + 40, y + 40)
    tile = regions.crop(box).resize((320, 320), Image.NEAREST)
    tiles.append(tile)
sheet = Image.new("RGB", (320 * 3 + 20, 320 * 3 + 20), (60, 60, 60))
for i, tile in enumerate(tiles):
    sheet.paste(tile, (5 + (i % 3) * 325, 5 + (i // 3) * 325))
sheet.save(out + "/line_ends.png")
# Coast features at full resolution.
for name, box in {"fjords_islands": (40, 2020, 1140, 2700), "lagoon_ne": (1900, 880, 2300, 1220),
                  "south_tip": (1900, 3300, 3100, 4000), "coast_style": (2600, 1500, 3100, 1900)}.items():
    regions.crop(box).save(out + "/" + name + ".png")
print("done")
