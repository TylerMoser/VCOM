"""Makes the pictures some map styles read at run time, from MapCreation's own data and the map's
scene.

All are 3100 by 4000, one pixel to a pixel of the MapCreation pictures (335 m, 3.35 of the map's
units), and grey (one byte a pixel):

  hillshade.png     shaded relief, lit from the north-west at 45 degrees with a little light from the
                    west and the north: 128 is flat ground (and the sea), lighter faces the light,
                    darker turns from it. Heights exaggerated 3 times, as relief at this scale wants.
  elevation.png     the ground's height: 255 times the square root of its share of 3,352 m, so the
                    lowlands get the most steps. The sea is 0.
  kingdom_edge.png  how far each pixel's middle is from the nearest kingdom border as the scene draws
                    it (its Line2Ds under Borders/Kingdoms, smooth, not the pixels' staircase), stored
                    as 255 times the square root of its share of EDGE_REACH pixels: fine steps near
                    the border, where a band is drawn close in, and reach enough for a band all the
                    way out. Read back as share = (value / 255)^2.

And four at half the size (1550 by 2000, a pixel 6.7 units), for the ground's colours
(MapStyles/12-biome-ground-colours/) and the fog of war (MapStyles/20-fog-of-war/), each 0 to 255:

  wetness.png       how near a river: every river of SourceData/Rivers.json drawn four times as wide as
                    it is (at least 3 px), blurred over 10 px (3.4 km), so the great rivers' valleys
                    are wide and green and a stream's a thread. 255 on the largest rivers.
  farmland.png      how near people: every settlement a disc by its rank (a kingdom's capital 26 px, a
                    duchy's 20, a county's 14, a village 7, a hamlet 4), blurred over 12 px (4 km), so
                    fields gather round towns and thin out between villages. 255 where most gather.
  coast.png         how near the sea: the share of the sea within a blur of 8 px (2.7 km), twice over,
                    on land only. 255 at the shore, 0 from about 5 km inland.
  forest_mask.png   the forests: every forest of SourceData/Forests.json filled, its clearings cut out
                    (the scene's 2,459 pieces were cut from these). 255 in a forest.

Needs numpy and Pillow (on this machine: py -3.9). Heights come from Elevation.png read as 16-bit,
which Godot cannot do (it reads it as 8-bit).

usage: py -3.9 make_data.py <repo root> <out folder> [name ...]   (names: as above, without .png;
                                                                   none given: all seven)
"""
import json
import re
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

PIXEL_M = 335.0
UNITS = 3.35
HIGHEST_M = 3352.1
SIZE = (3100, 4000)
## How far kingdom_edge.png reaches, in pixels: a 26-pixel band all the way out (18.6 units a screen
## pixel) needs 144.
EDGE_REACH = 160.0


def hillshade(h):
    """Shaded relief of heights h (metres), 128 for flat ground."""
    z = 3.0
    dzdx = np.zeros_like(h)
    dzdy = np.zeros_like(h)
    dzdx[:, 1:-1] = (h[:, 2:] - h[:, :-2]) / (2 * PIXEL_M)
    dzdy[1:-1, :] = (h[2:, :] - h[:-2, :]) / (2 * PIXEL_M)
    # The ground's normal in (east, north, up); the picture's y runs south.
    nx = -z * dzdx
    ny = z * dzdy
    nz = np.ones_like(h)
    length = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / length, ny / length, nz / length
    shade = np.zeros_like(h)
    altitude = np.radians(45.0)
    for azimuth, weight in ((315.0, 0.6), (270.0, 0.2), (0.0, 0.2)):
        a = np.radians(azimuth)
        lx, ly, lz = np.sin(a) * np.cos(altitude), np.cos(a) * np.cos(altitude), np.sin(altitude)
        shade += weight * np.clip(nx * lx + ny * ly + nz * lz, 0.0, 1.0)
    relief = shade - np.sin(altitude)
    return np.clip(128.0 + relief * 300.0, 0, 255)


def scene_lines(scene, parents):
    """The points of every Line2D directly under one of [parents] in the scene, each as an (n, 2) array
    in the map's units."""
    node = re.compile(r'^\[node name="[^"]+" type="Line2D" parent="([^"]+)"')
    lines = []
    current = False
    with open(scene, encoding="utf-8") as f:
        for text in f:
            if text.startswith("[node "):
                m = node.match(text)
                current = bool(m) and m.group(1) in parents
                continue
            if current and text.startswith("points = PackedVector2Array("):
                inside = text[len("points = PackedVector2Array("):text.rindex(")")]
                values = np.array([float(v) for v in inside.split(",")], dtype=np.float64)
                lines.append(values.reshape(-1, 2))
                current = False
    return lines


def line_distance(lines, reach):
    """The exact distance in pixels from every pixel's middle to the nearest of [lines] (in the map's
    units), up to [reach] (reach beyond). Each segment is drawn into the picture with the distance from
    every pixel of its box grown by reach, keeping the least."""
    width, height = SIZE
    best = np.full((height, width), reach * reach, dtype=np.float32)
    r = int(np.ceil(reach))
    for points in lines:
        # Pixel (x, y)'s middle is at ((x + 0.5) * UNITS, (y + 0.5) * UNITS).
        p = points / UNITS - 0.5
        for a, b in zip(p[:-1], p[1:]):
            x0 = max(int(np.floor(min(a[0], b[0]))) - r, 0)
            x1 = min(int(np.ceil(max(a[0], b[0]))) + r, width - 1)
            y0 = max(int(np.floor(min(a[1], b[1]))) - r, 0)
            y1 = min(int(np.ceil(max(a[1], b[1]))) + r, height - 1)
            if x0 > x1 or y0 > y1:
                continue
            xs = np.arange(x0, x1 + 1, dtype=np.float32)[None, :]
            ys = np.arange(y0, y1 + 1, dtype=np.float32)[:, None]
            d = b - a
            length2 = float(d[0] * d[0] + d[1] * d[1])
            if length2 <= 1e-12:
                t = 0.0
            else:
                t = np.clip(((xs - a[0]) * d[0] + (ys - a[1]) * d[1]) / length2, 0.0, 1.0)
            dx = xs - (a[0] + t * d[0])
            dy = ys - (a[1] + t * d[1])
            box = best[y0:y1 + 1, x0:x1 + 1]
            np.minimum(box, dx * dx + dy * dy, out=box)
    return np.sqrt(best)


def save_half(values, path):
    """A full-size picture of 0 to 1, saved at half the size, smoothly, as 0 to 255."""
    image = Image.fromarray(np.round(np.clip(values, 0.0, 1.0) * 255.0).astype(np.uint8), "L")
    image.resize((SIZE[0] // 2, SIZE[1] // 2), Image.LANCZOS).save(path, optimize=True)


def blurred(mask, radius):
    """A 0 to 1 picture blurred over [radius] pixels."""
    image = Image.fromarray(np.round(np.clip(mask, 0.0, 1.0) * 255.0).astype(np.uint8), "L")
    return np.asarray(image.filter(ImageFilter.GaussianBlur(radius))).astype(np.float32) / 255.0


def wetness(source, land):
    rivers = json.load(open(source + "/Rivers.json", encoding="utf-8"))["rivers"]
    image = Image.new("L", SIZE, 0)
    draw = ImageDraw.Draw(image)
    for river in rivers:
        points = river["points"]
        widths = river["width_px"]
        for (a, b, w) in zip(points[:-1], points[1:], widths[:-1]):
            draw.line([tuple(a), tuple(b)], fill=255, width=max(3, int(round(w * 4.0))))
    wet = blurred(np.asarray(image).astype(np.float32) / 255.0, 10)
    wet = np.sqrt(wet / max(float(wet.max()), 1e-6))
    wet[~land] = 0.0
    return wet


def farmland(source, land):
    image = Image.new("L", SIZE, 0)
    draw = ImageDraw.Draw(image)
    size = {"kingdom": 26, "duchy": 20, "county": 14, "village": 7, "hamlet": 4}
    places = [(float(s["x"]), float(s["y"]), s["rank"]) for s in
              json.load(open(source + "/Settlements.json", encoding="utf-8"))["settlements"]]
    places += [(float(p["x"]), float(p["y"]), p["kind"]) for p in
               json.load(open(source + "/Villages.json", encoding="utf-8"))["places"]]
    for x, y, rank in places:
        r = size[rank]
        draw.ellipse([x - r, y - r, x + r, y + r], fill=255)
    farm = blurred(np.asarray(image).astype(np.float32) / 255.0, 12)
    farm = farm / max(float(np.percentile(farm[land], 99.5)), 1e-6)
    farm[~land] = 0.0
    return farm


def coast(land):
    sea = (~land).astype(np.float32)
    near = blurred(blurred(sea, 8), 8)
    near = np.clip(near * 2.0, 0.0, 1.0)
    near[~land] = 0.0
    return near


def forest_mask(source):
    image = Image.new("L", SIZE, 0)
    draw = ImageDraw.Draw(image)
    for forest in json.load(open(source + "/Forests.json", encoding="utf-8"))["forests"]:
        draw.polygon([tuple(p) for p in forest["outline"]], fill=255)
        for hole in forest["holes"]:
            if len(hole) >= 3:
                draw.polygon([tuple(p) for p in hole], fill=0)
    return np.asarray(image).astype(np.float32) / 255.0


def main():
    repo, out = sys.argv[1], sys.argv[2]
    wanted = set(sys.argv[3:]) or {"hillshade", "elevation", "kingdom_edge", "wetness", "farmland", "coast",
                                   "forest_mask"}
    source = repo + "/MapCreation/SourceData"
    kingdoms = np.array(Image.open(source + "/KingdomMap.png"))
    land = kingdoms > 0
    written = []

    if wanted & {"hillshade", "elevation"}:
        heights = np.array(Image.open(repo + "/MapCreation/Elevation.png")).astype(np.float32) / 10.0
        if "hillshade" in wanted:
            shade = hillshade(heights)
            shade[~land] = 128
            Image.fromarray(shade.astype(np.uint8), "L").save(out + "/hillshade.png", optimize=True)
            written.append("hillshade.png")
        if "elevation" in wanted:
            height = 255.0 * np.sqrt(np.clip(heights / HIGHEST_M, 0.0, 1.0))
            height[~land] = 0
            Image.fromarray(height.astype(np.uint8), "L").save(out + "/elevation.png", optimize=True)
            written.append("elevation.png")

    if "kingdom_edge" in wanted:
        borders = scene_lines(repo + "/vcom/Scenes/Map.tscn", {"Borders/Kingdoms", "BordersOverLakes/Kingdoms"})
        distance = line_distance(borders, EDGE_REACH)
        encoded = np.round(255.0 * np.sqrt(np.clip(distance / EDGE_REACH, 0.0, 1.0)))
        Image.fromarray(encoded.astype(np.uint8), "L").save(out + "/kingdom_edge.png", optimize=True)
        written.append("kingdom_edge.png (from %d border lines)" % len(borders))

    if "wetness" in wanted:
        save_half(wetness(source, land), out + "/wetness.png")
        written.append("wetness.png")
    if "farmland" in wanted:
        save_half(farmland(source, land), out + "/farmland.png")
        written.append("farmland.png")
    if "coast" in wanted:
        save_half(coast(land), out + "/coast.png")
        written.append("coast.png")
    if "forest_mask" in wanted:
        save_half(forest_mask(source), out + "/forest_mask.png")
        written.append("forest_mask.png")
    print("wrote %s to %s" % (", ".join(written), out))


if __name__ == "__main__":
    main()
