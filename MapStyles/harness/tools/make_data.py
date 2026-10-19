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

Needs numpy and Pillow (on this machine: py -3.9). Heights come from Elevation.png read as 16-bit,
which Godot cannot do (it reads it as 8-bit).

usage: py -3.9 make_data.py <repo root> <out folder>
"""
import re
import sys
import numpy as np
from PIL import Image

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


def main():
    repo, out = sys.argv[1], sys.argv[2]
    heights = np.array(Image.open(repo + "/MapCreation/Elevation.png")).astype(np.float32) / 10.0
    kingdoms = np.array(Image.open(repo + "/MapCreation/SourceData/KingdomMap.png"))
    land = kingdoms > 0

    shade = hillshade(heights)
    shade[~land] = 128
    Image.fromarray(shade.astype(np.uint8), "L").save(out + "/hillshade.png", optimize=True)

    height = 255.0 * np.sqrt(np.clip(heights / HIGHEST_M, 0.0, 1.0))
    height[~land] = 0
    Image.fromarray(height.astype(np.uint8), "L").save(out + "/elevation.png", optimize=True)

    borders = scene_lines(repo + "/vcom/Scenes/Map.tscn", {"Borders/Kingdoms", "BordersOverLakes/Kingdoms"})
    distance = line_distance(borders, EDGE_REACH)
    encoded = np.round(255.0 * np.sqrt(np.clip(distance / EDGE_REACH, 0.0, 1.0)))
    Image.fromarray(encoded.astype(np.uint8), "L").save(out + "/kingdom_edge.png", optimize=True)
    print("wrote hillshade.png, elevation.png, kingdom_edge.png (from %d border lines) to %s" % (len(borders), out))


if __name__ == "__main__":
    main()
