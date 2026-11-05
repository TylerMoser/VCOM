"""new_1's grass and flowers, sculpted to measurements read off the image (see
new1_sculpt's notes). Each builder returns ({(x, y, z): (material, rgb)},
(sx, sy, sz)), standing on z 0."""
import math

import numpy as np

from new1_sculpt import _leaf, _mirror1, _mirror2
from sculpt_tree import connected_main

# ------------------------------------------------------------------ tall grass
GRASS = dict(light=(103, 187, 106), mid=(64, 138, 87), dark=(45, 107, 71), foot=(26, 64, 34))


def tall_grass(cartoon=False):
    """A tile of the tall leafy grass (the strip along the top, the patch at the
    left: one tile of it, repeated): pointed blades two voxels wide, narrowing to
    a point, 11 to 14 tall, in staggered rows, each leaning a little; lit on its
    left side, dark at its foot. Its pattern wraps at 16, so tiles join. Cartoon:
    a regular grid of blades, its rows alternately 12 and 13 tall, two tones."""
    n = 16
    out = {}
    rnd = np.random.RandomState(7)
    blades = []
    if cartoon:
        for i in range(4):
            for j in range(4):
                blades.append((2.0 + i * 4.0, 2.0 + j * 4.0, 12 + (j % 2), 0.0, 0.0))
    else:
        for j in range(5):
            for i in range(4 + (j % 2)):
                x = 1.6 + i * 3.6 + (1.8 if j % 2 else 0.0) + rnd.uniform(-0.5, 0.5)
                y = 1.4 + j * 3.3 + rnd.uniform(-0.4, 0.4)
                h = rnd.randint(11, 15)
                lx, ly = rnd.uniform(-0.18, 0.18), rnd.uniform(-0.18, 0.18)
                blades.append((x % 16, min(15.4, y), h, lx, ly))
    g = GRASS
    for (bx, by, h, lx, ly) in blades:
        for z in range(h):
            t = z / float(h - 1)
            cx, cy = bx + lx * z, by + ly * z
            if t >= 0.8:
                # the tip: one voxel, the one nearest the blade's middle
                cells = [(int(math.floor(cx)), int(math.floor(cy)))]
            else:
                w = 1.0 if t < 0.55 else 0.75
                cells = [(x, y) for x in range(int(cx - 2), int(cx + 3)) for y in range(int(cy - 2), int(cy + 3))
                         if abs(x + 0.5 - cx) <= w and abs(y + 0.5 - cy) <= w * 0.7]
            for (x, y) in cells:
                dx = x + 0.5 - cx
                if z < 2:
                    col = g["foot"]
                elif cartoon:
                    col = g["light"] if t > 0.5 else g["mid"]
                else:
                    col = g["light"] if (dx < 0 and t > 0.35) else (g["mid"] if t > 0.2 else g["dark"])
                out[((x % n), y, z)] = ("leaf", col)
    out = {p: v for p, v in out.items() if 0 <= p[1] < n}
    if cartoon:
        out = _mirror2(out, n)
    return out, (n, n, max(z for (x, y, z) in out) + 1)


# ------------------------------------------------------------------ flowers
SMALL_FLOWER = dict(petal=(238, 219, 100), heart=(250, 244, 192), stem=(60, 120, 60), leaf=(64, 142, 80),
                    leaf_dark=(36, 82, 45))


def small_flower(cartoon=False):
    """The small yellow flower in the tall grass: five petals round a cream heart,
    the head facing up, on a short stem with two small leaves. Cartoon: the same,
    mirrored across its middle."""
    n = 8
    C = n / 2.0
    out = {}
    f = SMALL_FLOWER
    for z in range(4):
        out[(int(C), int(C), z)] = ("leaf", f["stem"])
    pal = dict(light=f["leaf"], mid=f["leaf"], dark=f["leaf_dark"], vein=f["leaf_dark"])
    _leaf(out, C, (0.5, 0.5, 1.0), math.pi, 0.5, 2.8, 2.0, pal, cartoon, droop=0.5, cup=0.0, veins=False, thick=1)
    _leaf(out, C, (0.5, 0.5, 1.0), 0.0, 0.5, 2.8, 2.0, pal, cartoon, droop=0.5, cup=0.0, veins=False, thick=1)
    zc = 4
    for k in range(5):
        a = math.pi / 2 + 2 * math.pi * k / 5
        px, py = 1.55 * math.cos(a), 1.55 * math.sin(a)
        for x in range(n):
            for y in range(n):
                if math.hypot(x + 0.5 - C - px, y + 0.5 - C - py) <= 1.25:
                    out[(x, y, zc)] = ("yellow", f["petal"])
    for x in range(n):
        for y in range(n):
            if math.hypot(x + 0.5 - C, y + 0.5 - C) <= 0.75:
                out[(x, y, zc)] = ("bloom", f["heart"])
                out[(x, y, zc + 1)] = ("bloom", f["heart"])
    out = {p: v for p, v in out.items() if 0 <= p[0] < n and 0 <= p[1] < n and p[2] >= 0}
    out = connected_main(out)
    if cartoon:
        out = _mirror1(out, n)
    return out, (n, n, max(z for (x, y, z) in out) + 1)


FLOWER6 = {"Coral": dict(petal=(234, 91, 107), petal_mid=(194, 73, 82), petal_dark=(151, 53, 60)),
           "Blue": dict(petal=(15, 191, 237), petal_mid=(63, 177, 204), petal_dark=(34, 135, 162))}
FLOWER6_HEART = ((245, 176, 49), (226, 138, 36))
FLOWER6_GREEN = dict(stem=(52, 128, 70), leaf=(64, 142, 80), leaf_dark=(36, 82, 45))


def flower6(cartoon=False, colour="Coral"):
    """A six-petalled flower (red and blue, the same shape, drawn five times in
    the grass): round petals in a ring round an orange-yellow heart, the head on a
    short stem over two leaves, its petals cupped a little; each petal a darker
    line down its middle and a darker foot, as drawn. Cartoon: mirrored across
    both middles, plain petals."""
    n = 14
    C = n / 2.0
    out = {}
    p = FLOWER6[colour]
    g = FLOWER6_GREEN
    for z in range(4):
        for (x, y) in ((int(C) - 1, int(C) - 1), (int(C), int(C) - 1), (int(C) - 1, int(C)), (int(C), int(C))):
            out[(x, y, z)] = ("leaf", g["stem"])
    pal = dict(light=g["leaf"], mid=g["leaf"], dark=g["leaf_dark"], vein=g["leaf_dark"])
    for az in ((math.radians(200), math.radians(20)) if not cartoon else (math.pi, 0.0)):
        _leaf(out, C, (0.0, 0.0, 1.0), az, 0.45, 5.0, 3.0, pal, cartoon, droop=0.5, cup=0.2, veins=False)
    zc = 4
    for k in range(6):
        a = 2 * math.pi * k / 6
        px, py = 3.3 * math.cos(a), 3.3 * math.sin(a)
        for x in range(n):
            for y in range(n):
                dx, dy = x + 0.5 - C - px, y + 0.5 - C - py
                if math.hypot(dx, dy) <= 2.25:
                    along = dx * math.cos(a) + dy * math.sin(a)
                    across = -dx * math.sin(a) + dy * math.cos(a)
                    z = zc + (1 if along > 1.0 else 0)
                    if cartoon:
                        col = p["petal"]
                    elif abs(across) < 0.5 and along < 1.2:
                        col = p["petal_mid"]
                    elif along < -1.2:
                        col = p["petal_dark"]
                    else:
                        col = p["petal"]
                    out[(x, y, z)] = ("flower" if colour == "Coral" else "blue", col)
    for x in range(n):
        for y in range(n):
            d = math.hypot(x + 0.5 - C, y + 0.5 - C)
            if d <= 1.9:
                out[(x, y, zc)] = ("bloom", FLOWER6_HEART[1] if (d > 1.2 and not cartoon) else FLOWER6_HEART[0])
                if d <= 1.2:
                    out[(x, y, zc + 1)] = ("bloom", FLOWER6_HEART[0])
    out = {q: v for q, v in out.items() if 0 <= q[0] < n and 0 <= q[1] < n and q[2] >= 0}
    out = connected_main(out)
    if cartoon:
        out = _mirror2(out, n)
    return out, (n, n, max(z for (x, y, z) in out) + 1)


def flower6_blue(cartoon=False):
    return flower6(cartoon, "Blue")


ROOF_PLANT = dict(leaf=(89, 177, 91), leaf_mid=(66, 150, 74), leaf_dark=(40, 92, 52), petal=(248, 220, 96),
                  petal_dark=(243, 191, 46), heart=(236, 140, 36))


def roof_plant(cartoon=False):
    """The low flowering plant on the roof: a mound of round leaves, each tilted
    out from its middle, and three yellow star-shaped flowers of five pointed
    petals with orange hearts, as drawn (two behind, one in front). Cartoon: its
    leaves and four flowers set evenly, mirrored across both middles."""
    n = 22
    C = n / 2.0
    out = {}
    r = ROOF_PLANT
    rnd = np.random.RandomState(3)
    if cartoon:
        leaves = [(7.0 * math.cos(a), 5.0 * math.sin(a), 1.5, 3.0) for a in [k * math.pi / 4 for k in range(8)]] + \
                 [(2.6 * math.cos(a), 2.6 * math.sin(a), 3.0, 2.8) for a in
                  [k * math.pi / 2 + math.pi / 4 for k in range(4)]]
    else:
        leaves = [(-8.2, 1.0, 1.5, 2.8), (-5.5, -3.5, 1.5, 3.0), (-1.5, -5.6, 1.5, 3.0), (2.8, -4.8, 1.5, 3.0),
                  (6.8, -2.0, 1.5, 3.0), (8.6, 2.2, 1.5, 2.6), (4.8, 4.2, 2.0, 2.8), (-0.5, 5.0, 2.0, 3.0),
                  (-4.6, 4.0, 2.0, 2.8), (-2.5, 0.0, 3.2, 2.9), (2.4, 0.6, 3.2, 2.9)]
    for (lx, ly, lz, rad) in leaves:
        tilt_x, tilt_y = lx * 0.08, ly * 0.08
        for x in range(n):
            for y in range(n):
                dx, dy = x + 0.5 - C - lx, y + 0.5 - C - ly
                d = math.hypot(dx, dy)
                if d <= rad + 0.25:
                    z = int(round(lz + dx * tilt_x + dy * tilt_y + (0.0 if cartoon else rnd.uniform(-0.3, 0.3))))
                    if cartoon:
                        col = r["leaf"] if d < rad - 0.8 else r["leaf_mid"]
                    else:
                        col = r["leaf_mid"] if d > rad - 0.7 else (r["leaf"] if dx < 0.5 else r["leaf_mid"])
                    out[(x, y, max(0, z))] = ("leaf", col)
                    for zz in range(0, max(0, z)):
                        out.setdefault((x, y, zz), ("leaf", r["leaf_dark"] if zz == 0 else r["leaf_mid"]))
    flowers = ([(-6.0, 0.0), (6.0, 0.0), (0.0, -3.5), (0.0, 3.5)] if cartoon else
               [(-4.0, 3.0), (4.4, 2.6), (0.2, -2.6)])
    for (fx, fy) in flowers:
        zc = 5
        for x in range(n):
            for y in range(n):
                dx, dy = x + 0.5 - C - fx, y + 0.5 - C - fy
                d = math.hypot(dx, dy)
                a = math.atan2(dy, dx) - math.pi / 2
                star = 1.1 + 1.6 * (0.5 + 0.5 * math.cos(5 * a))       # five pointed petals
                if d <= star:
                    if d <= 0.95:
                        out[(x, y, zc)] = ("bloom", r["heart"])
                        out[(x, y, zc + 1)] = ("bloom", r["heart"])
                    else:
                        out[(x, y, zc)] = ("yellow", r["petal"] if (cartoon or d < star - 0.6) else r["petal_dark"])
                    for zz in range(3, zc):
                        out.setdefault((x, y, zz), ("leaf", r["leaf_mid"]))
    out = {q: v for q, v in out.items() if 0 <= q[0] < n and 0 <= q[1] < n and q[2] >= 0}
    out = connected_main(out)
    if cartoon:
        out = _mirror2(out, n)
    return out, (n, n, max(z for (x, y, z) in out) + 1)
