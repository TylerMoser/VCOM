"""new_2's leafy hedge as a kit of tile pieces, as the terrain kits are: each piece
one tile (16 x 16) and as tall as the hedge is drawn, its sides rounded where the
hedge ends, turned and placed side by side to build any hedge the sheet draws
(the 3 x 3 field, the 2 x 2 interior, the 2 x 1 and 1 x 2 pills, the single round
clump). Pieces: Fill (hedge all round), Straight (its edge on local -y),
OuterCorner (-y and -x, rounded), InnerCorner (hedge all round but the -x -y
diagonal), Ridge (-y and +y: a hedge a tile wide), RidgeEnd (-y, +y and -x: a
pill's end), Pillar (the single round clump), FillMarked (Fill with the small dark
mark the sheet draws in its interior). A piece stands on z 0 with no soil, as the
vegetation collection's patches do.

The top is the sheet's own interior swatch (its 16 x 16 tile), its lighter spots
raised a voxel; the sides darken to the outline at the foot, as drawn. Cartoon:
the swatch's spots in a regular pattern, one shade a side, the top edge more
rounded. Every pattern repeats every 16 voxels, so the pieces join.
"""
import math

import numpy as np

from sprites import quantize

PIECES = ("Fill", "Straight", "OuterCorner", "InnerCorner", "Ridge", "RidgeEnd", "Pillar", "FillMarked")
HEIGHT = 9
F = 0.5            # how far a face is set in from the tile's edge
R_CORNER = 6.5     # convex corners' radius in plan
R_IN = 2.0


def plan(piece, x, y):
    """Distance of column (x, y) inside the hedge's outline (negative outside)."""
    px, py = x + 0.5, y + 0.5
    if piece in ("Fill", "FillMarked"):
        return 99.0
    if piece == "Straight":
        return py - F
    if piece == "OuterCorner":
        dx, dy = px - F, py - F
        if dx < R_CORNER and dy < R_CORNER:
            return R_CORNER - math.hypot(R_CORNER - dx, R_CORNER - dy)
        return min(dx, dy)
    if piece == "InnerCorner":
        dx, dy = px - F, py - F
        if dx < 0 and dy < 0:
            if dx > -R_IN and dy > -R_IN:
                return math.hypot(dx + R_IN, dy + R_IN) - R_IN
            return max(dx, dy)
        if dx >= 0 and dy >= 0:
            return 99.0
        return dy if dx < 0 else dx
    if piece == "Ridge":
        return min(py - F, (16 - F) - py)
    if piece == "RidgeEnd":
        a, b, c = py - F, (16 - F) - py, px - F
        r = 8 - F
        dmin = min(a, b)
        if c < r:
            return r - math.hypot(r - c, 8 - py)
        return dmin
    if piece == "Pillar":
        return (8 - F) - math.hypot(px - 8, py - 8)
    raise ValueError(piece)


class Hedge:
    def __init__(self, sprite_field, sprite_interior):
        rgb = sprite_interior.rgb.astype(int)
        self.swatch = rgb[0:16, 0:16]                       # the interior tile
        lum = 0.299 * self.swatch[..., 0] + 0.587 * self.swatch[..., 1] + 0.114 * self.swatch[..., 2]
        self.lum = lum
        allpx = np.concatenate([sprite_field.rgb.reshape(-1, 3), rgb.reshape(-1, 3)])
        keep = allpx[(allpx[:, 1] > allpx[:, 0] + 20)]
        self.pal = sorted([tuple(int(v) for v in c) for c in quantize(keep, 5).tolist()], key=sum)
        mark = (lum < np.percentile(lum, 4))
        self.mark = mark

    def build(self, piece, cartoon=False):
        out = {}
        h = HEIGHT
        re = 5.0 if cartoon else 4.0
        lo, hi = np.percentile(self.lum, 25), np.percentile(self.lum, 80)
        for x in range(16):
            for y in range(16):
                d = plan(piece, x, y)
                if d < 0:
                    continue
                # the top's rounded edge
                top = h
                if d < re:
                    top = h - (re - math.sqrt(max(0.0, re * re - (re - d) ** 2)))
                sw = self.swatch[15 - y, x]
                spot = self.lum[15 - y, x] > hi
                if cartoon:
                    spot = ((x // 4 + y // 4) % 2 == 0) and (x % 4 in (1, 2)) and (y % 4 in (1, 2))
                ztop = int(round(top)) + (1 if (spot and d >= re) else 0)
                for z in range(max(1, ztop)):
                    if z == ztop - 1:
                        if cartoon:
                            col = self.pal[-2] if spot else self.pal[-3]
                        else:
                            col = min(self.pal, key=lambda q: sum((q[i] - sw[i]) ** 2 for i in range(3)))
                    else:
                        # the sides: mid green, darkening to the outline at the foot
                        col = self.pal[0] if z == 0 else (self.pal[1] if z < 3 else self.pal[2])
                        if cartoon:
                            col = self.pal[1] if z < 3 else self.pal[2]
                    out[(x, y, z)] = ("leaf", col)
        if piece == "FillMarked":
            # the small dark mark: a tent-shaped dent at the tile's middle
            for x in range(16):
                for y in range(16):
                    dx, dy = abs(x + 0.5 - 8), (y + 0.5 - 8)
                    if dx <= 2.5 - (dy + 2) * 0.6 and -2.5 <= dy <= 1.5:
                        for z in range(h - 1, h + 1):
                            out.pop((x, y, z), None)
                        out[(x, y, h - 2)] = ("leaf", self.pal[0])
        return out, (16, 16, HEIGHT + 1)
