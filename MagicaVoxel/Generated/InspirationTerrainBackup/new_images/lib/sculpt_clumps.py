"""Two sprites the tree sculptor's slices cannot read: plants made of a few big
round parts, and a fern.

clumps(): a trunk carrying round leaf puffs, each a squat ellipsoid on a branch
from the trunk's top. Where the puffs sit is read off the sprite by eye and given
by the catalogue (centre across, centre depth, centre height, radius across,
radius up, all in voxels from the trunk's foot), since the sprite draws them
overlapping in a 3/4 view: the puffs it draws to the left and right stand left
and right, the one drawn low in front stands in front, the one drawn high stands
over the middle, and a puff the view hides behind them is added there. Paint: the
sprite's own leaf shades, light where a puff faces up, dark at its foot; Base also
draws the short dark leaf strokes the sprite draws on its puffs. The trunk is the
sprite's bark, flaring at the foot.

fern(): fronds rising from one heart at the ground, steep in the middle and
splaying outward round it, each the palm's frond (widest a third of the way up,
a dark midrib, its edges cut into leaflets).

Cartoon: the puffs or fronds evenly placed (exact quarter-turn symmetry), the
paint in three broad bands, no strokes.
"""
import math

import numpy as np

from sculpt_palm import Palm, _symmetrize
from sculpt_tree import connected_main
from sprites import hue_sat, quantize


def _shades(sprite):
    """(light, mid, dark) leaf greens and the sorted bark shades of a sprite."""
    rgb = sprite.rgb.astype(int)
    h, s, v = hue_sat(rgb)
    leaf = sprite.mask & (h > 60) & (h < 180) & (s > 0.3)
    px = rgb[leaf]
    lum = px @ np.array([0.299, 0.587, 0.114])
    order = np.argsort(lum)

    def at(q):
        i = int(q * (len(order) - 1))
        win = px[order[max(0, i - 3):i + 4]]
        return tuple(int(c) for c in np.median(win, axis=0))

    bark = sprite.mask & (((h < 55) | (h > 320)) & (s > 0.15)) & ~leaf
    wp = rgb[bark]
    wood = sorted([tuple(int(c) for c in q) for q in (quantize(wp, 3) if len(wp) >= 3 else
                                                       np.array([[96, 70, 44], [120, 88, 56], [70, 50, 32]])).tolist()],
                  key=sum)
    return (at(0.85), at(0.5), at(0.18)), wood


def _ellipsoid(cx, cy, cz, a, b, x, y, z):
    """How far (x, y, z), a voxel's centre, is inside the puff: below 1 inside.
    The puff's underside is a little flatter than its top."""
    bb = b if z >= cz else b * 0.8
    return ((x - cx) / a) ** 2 + ((y - cy) / a) ** 2 + ((z - cz) / bb) ** 2


def clumps(sprite, cartoon, puffs, cartoon_puffs, trunk_top, trunk_r, flare=1.5, strokes=True):
    """{(x, y, z): (material, rgb)} and the canvas. puffs / cartoon_puffs:
    [(across, depth, height, radius across, radius up)], the Cartoon's quarter-turn
    symmetric; trunk_top: the height the branches leave the trunk at."""
    (light, mid, dark), wood = _shades(sprite)
    ps = cartoon_puffs if cartoon else puffs
    reach = max(max(abs(px), abs(py)) + a for (px, py, pz, a, b) in ps)
    n = int(math.ceil(2 * reach)) + 2
    n += n % 2
    C = n / 2.0
    top = int(math.ceil(max(pz + b for (px, py, pz, a, b) in ps))) + 1
    out = {}
    # the trunk, flaring at the foot, and a branch to each puff
    for z in range(trunk_top + 1):
        rad = trunk_r + (flare if z == 0 else (flare * 0.5 if z == 1 else 0.0))
        for x in range(n):
            for y in range(n):
                dx, dy = x + 0.5 - C, y + 0.5 - C
                d = math.hypot(dx, dy)
                if d <= rad + 0.25:
                    if cartoon:
                        col = wood[len(wood) // 2]
                    else:
                        col = wood[0] if (d > rad - 0.9 and (x + y + z) % 3 == 0) else wood[len(wood) // 2]
                        if z <= 1 and d > trunk_r:
                            col = wood[-1]
                    out[(x, y, z)] = ("wood", col)
    for (px, py, pz, a, b) in ps:
        z0 = trunk_top - 1
        steps = int(math.hypot(px, py) * 2 + abs(pz - z0) * 2) + 2
        for i in range(steps + 1):
            t = i / float(steps)
            bx, by, bz = px * t, py * t, z0 + (pz - z0) * t
            for ox in (-0.5, 0.5):
                for oy in (-0.5, 0.5):
                    q = (int(math.floor(C + bx + ox)), int(math.floor(C + by + oy)), int(round(bz)))
                    out.setdefault(q, ("wood", wood[len(wood) // 2]))
    # the puffs
    leaf = {}
    for k, (px, py, pz, a, b) in enumerate(ps):
        for z in range(max(0, int(pz - b) - 1), int(pz + b) + 2):
            for x in range(n):
                for y in range(n):
                    dx, dy = x + 0.5 - C, y + 0.5 - C
                    e = _ellipsoid(px, py, pz, a, b, dx, dy, z + 0.5)
                    if e <= 1.0:
                        # the puff whose surface is nearest paints it
                        if (x, y, z) not in leaf or e > leaf[(x, y, z)][0]:
                            leaf[(x, y, z)] = (e, k)
    for p, (e, k) in leaf.items():
        out[p] = ("leaf", None, k)
    vox = {}
    for p, v in out.items():
        if v[0] == "wood":
            vox[p] = v
            continue
        x, y, z = p
        px, py, pz, a, b = ps[v[2]]
        exposed = any(q not in out for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z),
                                             (x, y, z + 1), (x, y, z - 1)))
        if not exposed:
            vox[p] = ("leaf", mid)
            continue
        # the puff's surface: light facing up, dark at the foot
        dz = (z + 0.5 - pz) / b
        if cartoon:
            col = light if dz > 0.35 else (mid if dz > -0.35 else dark)
        else:
            col = light if dz > 0.45 else (mid if dz > -0.3 else dark)
            if strokes and _on_stroke(x + 0.5 - C - px, y + 0.5 - C - py, z + 0.5 - pz, a, b, v[2]):
                col = dark
        vox[p] = ("leaf", col)
    vox = connected_main(vox)
    if cartoon:
        vox = _symmetrize(vox, n)
    return vox, (n, n, max(top, max(z for (x, y, z) in vox) + 1))


def _on_stroke(dx, dy, dz, a, b, k):
    """Whether a puff's surface voxel, at (dx, dy, dz) from its centre, lies on one
    of the short dark leaf strokes the sprite draws on its puffs: five a puff, on
    its upper half, each a slanting arc about four voxels long and one wide."""
    nx, ny, nz = dx / a, dy / a, dz / b
    r = math.sqrt(nx * nx + ny * ny + nz * nz)
    if r < 1e-6:
        return False
    lat = math.asin(max(-1.0, min(1.0, nz / r)))
    lon = math.atan2(ny, nx)
    length = 4.2 / (a * max(0.3, math.cos(lat)))          # radians of longitude for ~4 voxels
    half_w = 0.55 / b                                    # radians of latitude for ~1 voxel
    for i in range(5):
        lon0 = (i * 2 * math.pi / 5 + k * 1.3) % (2 * math.pi) - math.pi
        lat0 = 0.45 + 0.18 * ((i * 3 + k) % 3) / 2.0
        t = (lon - lon0 + math.pi) % (2 * math.pi) - math.pi
        if 0 <= t <= length and abs(lat - (lat0 + 0.35 * t)) <= half_w:
            return True
    return False


class _Fronds(Palm):
    """The palm's frond drawing, with a palette of one's own."""

    def __init__(self, leaf_pal, H):
        self.leaf_pal, self.H = leaf_pal, H


def fern(sprite, cartoon, height=None):
    """{(x, y, z): (material, rgb)} and the canvas: fronds from a heart at the ground."""
    (light, mid, dark), wood = _shades(sprite)
    rows = np.nonzero(sprite.mask.any(axis=1))[0]
    cols = np.nonzero(sprite.mask.any(axis=0))[0]
    H = height or int(rows.max() - rows.min() + 1)
    reach = (cols.max() + 1 - cols.min()) / 2.0
    n = int(math.ceil(2 * reach)) + 2
    n += n % 2
    C = n / 2.0
    painter = _Fronds([dark, mid, light], H + 2)
    out = {}
    if cartoon:
        fronds = [(i * math.pi / 2, 58, 0.95, 2.8) for i in range(4)] + \
                 [(i * math.pi / 2 + math.pi / 4, 70, 0.8, 3.0) for i in range(4)]
    else:
        fronds = [(0.3, 57, 0.95, 2.7), (2.4, 59, 0.9, 2.7), (4.4, 56, 1.0, 2.6),
                  (1.3, 69, 0.8, 3.0), (3.4, 67, 0.85, 2.9), (5.4, 70, 0.78, 3.0),
                  (0.9, 79, 0.45, 2.6), (3.9, 77, 0.5, 2.6)]
    for (ang, el, frac, width) in fronds:
        e = math.radians(el)
        rise = H - 1.5
        length = min(reach * frac, rise / math.tan(e) * (frac if el < 65 else 1.0))
        stretch = (rise * (0.7 if el < 65 else 1.0)) / (length * math.tan(e))
        painter._frond(out, n, C, ang, e, length, 0, stretch, width, cartoon, sag=0.25)
    # the heart: a low mound the fronds rise from
    for x in range(n):
        for y in range(n):
            if math.hypot(x + 0.5 - C, y + 0.5 - C) <= 2.3:
                for z in range(2):
                    out[(x, y, z)] = ("leaf", dark)
    out = connected_main(out)
    if cartoon:
        out = _symmetrize(out, n)
    return out, (n, n, max(z for (x, y, z) in out) + 1)
