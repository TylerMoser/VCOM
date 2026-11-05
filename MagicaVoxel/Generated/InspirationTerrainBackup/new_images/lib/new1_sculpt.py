"""new_1's elements, sculpted to measurements read off the image.

new_1 is a scene, not a sprite sheet: its trees overlap one another and the HUD,
its plants and figures stand on the meadow, so no element can be cut out whole by
colour as new_2's sprites are. Each is built here from its parts as the image
draws them, every size measured on the image in its own art pixels (16 a tile, a
pixel a voxel, as the house and the tree collections size things) and every colour
its median there (sample.py). Each builder returns
({(x, y, z): (material, rgb)}, (sx, sy, sz)), standing on z 0.

Base keeps the image's light: lit from the left (-x), its right side (+x) in
shadow, as every element here is drawn. Cartoon: exact quarter-turn symmetry (or a
mirror, for things with a front), the shading as broad bands, details evenly set.
"""
import math

import numpy as np

from sculpt_palm import _symmetrize
from sculpt_tree import connected_main

# The direction the image's light comes from: the left, a little from behind, above.
LIGHT = (-0.78, 0.25, 0.57)


def _lit(nx, ny, nz):
    return nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]


def _disc(out, n, C, z, r, val, cx=0.0, cy=0.0, keep=False):
    for x in range(n):
        for y in range(n):
            if math.hypot(x + 0.5 - C - cx, y + 0.5 - C - cy) <= r + 0.25:
                if keep:
                    out.setdefault((x, y, z), val)
                else:
                    out[(x, y, z)] = val


# ------------------------------------------------------------------ the conifer
CONE = dict(cap=(200, 200, 57), cap_mid=(170, 164, 33), lit=(161, 163, 40), shade=(100, 117, 57),
            mark_lit=(124, 128, 42), mark_shade=(62, 71, 39), skirt=(101, 114, 55), skirt_dark=(62, 71, 39),
            rim=(34, 36, 16), trunk=(135, 71, 55), trunk_dark=(86, 44, 43), root=(86, 44, 43), root_dark=(52, 34, 26))


def cone_tree(cartoon=False):
    """The olive conifer: a straight cone, lit on its left and shaded on its
    right, its leaves marked with small dark arcs, a pale cap at its tip; under it
    a skirt of two tiers of round scalloped leaves; a short round red-brown trunk
    and roots spread low round it. 35 tall, as drawn (cap to trunk foot)."""
    c = CONE
    n = 28
    C = n / 2.0
    out = {}
    # trunk and roots
    for z in range(9):
        for x in range(n):
            for y in range(n):
                dx, dy = x + 0.5 - C, y + 0.5 - C
                d = math.hypot(dx, dy)
                if d <= 3.6:
                    col = c["trunk"]
                    if not cartoon and (d > 2.4 and (_lit(dx / d, dy / d, 0) < -0.2 or (x * 3 + z) % 7 == 0)):
                        col = c["trunk_dark"]
                    out[(x, y, z)] = ("wood", col)
    k = 4 if cartoon else 5
    for i in range(k):
        a = 2 * math.pi * i / k + (math.pi / 4 if cartoon else 0.4 + 0.25 * math.sin(i * 2.1))
        ln = 10.5 if cartoon else 9.5 + 1.5 * math.cos(i * 1.7)
        steps = int(ln * 3)
        for s in range(steps + 1):
            t = s / float(steps)
            rr = 2.5 + t * (ln - 2.5)
            px, py = C + rr * math.cos(a), C + rr * math.sin(a)
            w = 1.7 * (1 - 0.55 * t)
            top = 2.0 * (1 - t)
            for x in range(int(px - 3), int(px + 4)):
                for y in range(int(py - 3), int(py + 4)):
                    if 0 <= x < n and 0 <= y < n and math.hypot(x + 0.5 - px, y + 0.5 - py) <= w:
                        for z in range(0, int(round(top)) + 1):
                            col = c["root"] if (cartoon or z > 0) else c["root_dark"]
                            out.setdefault((x, y, z), ("wood", col))
    # the skirt: a solid core and two tiers of round leaves round it
    for z in range(7, 14):
        _disc(out, n, C, z, 9.0, ("leaf", c["skirt_dark"]))
    tiers = [(11.6, 9.6, 2.3), (8.9, 9.2, 2.2)]
    for ti, (zc, ring, b) in enumerate(tiers):
        count = 8 if cartoon else 10
        for j in range(count):
            ang = 2 * math.pi * j / count + (ti * math.pi / count)
            if not cartoon:
                ang += 0.06 * math.sin(j * 2.3 + ti)
            lx, ly = ring * math.cos(ang), ring * math.sin(ang)
            a_across, a_out = 3.7, 2.7
            for z in range(int(zc - b) - 1, int(zc + b) + 2):
                for x in range(n):
                    for y in range(n):
                        dx, dy = x + 0.5 - C - lx, y + 0.5 - C - ly
                        rad = dx * math.cos(ang) + dy * math.sin(ang)
                        tan = -dx * math.sin(ang) + dy * math.cos(ang)
                        vz = (z + 0.5 - zc) / b
                        if (rad / a_out) ** 2 + (tan / a_across) ** 2 + vz ** 2 <= 1.0:
                            # the scallop's foot dark, its face lit or shaded by the side it is on
                            if vz < -0.55:
                                col = c["rim"] if ti == 1 else c["skirt_dark"]
                            elif cartoon:
                                col = c["skirt"] if ti == 0 else c["skirt_dark"]
                            else:
                                lit = _lit(math.cos(ang), math.sin(ang), 0.3) > -0.3
                                col = (c["skirt"] if lit else c["skirt_dark"]) if ti == 0 else \
                                      (c["skirt_dark"] if lit else c["rim"])
                            out[(x, y, z)] = ("leaf", col)
    # the cone
    z0, z1, r0, r1 = 12, 32, 9.6, 2.2
    for z in range(z0, z1 + 1):
        r = r0 + (r1 - r0) * (z - z0) / float(z1 - z0)
        for x in range(n):
            for y in range(n):
                dx, dy = x + 0.5 - C, y + 0.5 - C
                d = math.hypot(dx, dy)
                if d > r + 0.25:
                    continue
                surface = d > r - 0.9
                if not surface:
                    out[(x, y, z)] = ("leaf", c["shade"])
                    continue
                ang = math.atan2(dy, dx)
                if cartoon:
                    col = c["lit"] if z > z0 + 0.42 * (z1 - z0) else c["shade"]
                else:
                    col = c["lit"] if _lit(dx / max(d, 1e-6), dy / max(d, 1e-6), 0.45) > -0.3 else c["shade"]
                out[(x, y, z)] = ("leaf", col)
    # the small dark arcs on its leaves
    rows = [15, 19, 23, 27]
    for ri, zm in enumerate(rows):
        r = r0 + (r1 - r0) * (zm - z0) / float(z1 - z0)
        count = 4 if cartoon else max(3, int(r * 0.75))
        for j in range(count):
            ang = 2 * math.pi * j / count + (ri % 2) * math.pi / count + (math.pi / 4 if cartoon else 0.3 * ri)
            for (da, dz) in ((-0.22, 0), (0.0, -1), (0.22, 0)):
                aa = ang + da * 4.0 / max(r, 2.0)
                x, y = int(math.floor(C + (r - 0.3) * math.cos(aa))), int(math.floor(C + (r - 0.3) * math.sin(aa)))
                q = (x, y, zm + dz)
                if q in out and out[q][0] == "leaf":
                    lit = out[q][1] == c["lit"]
                    out[q] = ("leaf", c["mark_lit"] if lit else c["mark_shade"])
    # the cap
    for z, r in ((32, 2.6), (33, 2.3), (34, 1.4)):
        for x in range(n):
            for y in range(n):
                d = math.hypot(x + 0.5 - C, y + 0.5 - C)
                if d <= r + 0.25:
                    out[(x, y, z)] = ("leaf", c["cap"] if (d > 1.0 or z == 34) else c["cap_mid"])
    out = connected_main(out)
    if cartoon:
        out = _symmetrize(out, n)
    return out, (n, n, max(z for (x, y, z) in out) + 1)


# ------------------------------------------------------------------ leaves
def _leaf(out, C, base, az, el, L, W, pal, cartoon, droop=0.5, cup=0.35, notch=False, veins=True, mat="leaf",
          widest=0.42, thick=2):
    """One leaf from [base] (x, y, z offsets from the canvas middle) along azimuth
    [az] rising at [el] (radians) and arching down [droop] radians to its tip,
    [L] long and [W] wide, its edges cupped up, ovate (widest [widest] of the way
    out) or cut into teeth ([notch]); [thick] voxels thick, its underside the mid shade.
    pal: dict light, mid, dark, vein. Paint: the midrib dark and (Base, [veins])
    two side veins each way, the half toward the light light (Base), the tip and
    teeth darker."""
    bx, by, bz = base
    ux, uy = math.cos(az), math.sin(az)
    sx, sy = -uy, ux
    steps = int(L * 4) + 2
    x0, y0, z0 = bx, by, bz
    spine = []
    for i in range(steps + 1):
        t = i / float(steps)
        e = el - droop * t
        if i:
            x0 += ux * math.cos(e) * L / steps
            y0 += uy * math.cos(e) * L / steps
            z0 += math.sin(e) * L / steps
        spine.append((t, x0, y0, z0))
    lit_side = 1.0 if (sx * LIGHT[0] + sy * LIGHT[1]) > 0 else -1.0
    vein_ts = (0.38, 0.6) if (veins and not cartoon) else ()
    for (t, px, py, pz) in spine:
        prof = (t / widest) if t < widest else (1.0 - (t - widest) / (1.0 - widest))
        w = W / 2.0 * max(0.0, prof) ** 0.7
        tooth = notch and t > 0.22 and int(t * L * 1.4) % 2 == 1
        if tooth:
            w *= 0.6
        nk = int(w / 0.35) + 1
        for j in range(-nk, nk + 1):
            k = j * 0.35
            if abs(k) > w:
                continue
            s = k / max(w, 0.5)
            x = int(math.floor(C + px + sx * k))
            y = int(math.floor(C + py + sy * k))
            z = int(round(pz + cup * abs(k)))
            if abs(k) < 0.45 and 0.04 < t < 0.9:
                col = pal["vein"]
            elif any(abs(t - (vt + 0.12 * abs(s))) < 0.035 for vt in vein_ts) and abs(s) < 0.8:
                col = pal["vein"]
            elif t > 0.9 or (tooth and abs(s) > 0.6):
                col = pal["dark"]
            elif cartoon:
                col = pal["light"] if t > 0.3 else pal["mid"]
            else:
                col = pal["light"] if s * lit_side > -0.2 else pal["mid"]
            out[(x, y, z)] = (mat, col)
            for dz in range(1, thick):
                out.setdefault((x, y, z - dz), (mat, pal["mid"]))


def _mirror2(out, n):
    """Mirror symmetry across both middle planes (x and y), from the quarter x, y >= n/2."""
    half = n // 2
    full = {}
    for (x, y, z), v in out.items():
        if x >= half and y >= half:
            for xx in (x, n - 1 - x):
                for yy in (y, n - 1 - y):
                    full[(xx, yy, z)] = v
    return full


def _mirror1(out, n):
    """Mirror symmetry across x's middle plane, from the half x >= n/2."""
    full = {}
    for (x, y, z), v in out.items():
        if x >= n // 2:
            full[(x, y, z)] = v
            full[(n - 1 - x, y, z)] = v
    return full


ROSETTE = dict(light=(88, 196, 82), mid=(52, 151, 75), dark=(24, 74, 52), vein=(44, 110, 73), heart=(24, 74, 52))


def rosette(cartoon=False):
    """The broad-leaved plant (drawn three times, beside the house): five broad
    oval leaves from a dark heart, as drawn: two smaller ones rising behind, two
    big ones spreading at the sides, a small one in front; each leaf arching, its
    edges cupped, a dark midrib and side veins, its half toward the light lighter.
    Cartoon: four big leaves and four small between them, evenly set."""
    n = 24
    C = n / 2.0
    out = {}
    pal = ROSETTE
    if cartoon:
        leaves = [(math.pi / 4 + k * math.pi / 2, 1.02, 10.5, 7.0) for k in range(4)] + \
                 [(k * math.pi / 2, 1.35, 6.5, 4.6) for k in range(4)]
    else:
        # (azimuth, rise, length, width): +y is behind, -y in front
        leaves = [(math.radians(122), 1.35, 8.5, 6.0), (math.radians(58), 1.3, 8.8, 6.2),
                  (math.radians(192), 1.05, 11.2, 7.6), (math.radians(346), 1.0, 11.0, 7.4),
                  (math.radians(272), 1.0, 5.2, 4.4)]
    for (az, el, L, W) in leaves:
        _leaf(out, C, (0.0, 0.0, 1.0), az, el, L, W, pal, cartoon, droop=1.05, cup=0.3)
    for z in range(3):
        _disc(out, n, C, z, 2.2 - 0.5 * z, ("leaf", pal["heart"]))
    out = {p: v for p, v in out.items() if 0 <= p[0] < n and 0 <= p[1] < n and p[2] >= 0}
    out = connected_main(out)
    if cartoon:
        out = _symmetrize(out, n)
    return out, (n, n, max(z for (x, y, z) in out) + 1)


PLANTER_PLANT = dict(light=(98, 184, 102), mid=(59, 142, 74), dark=(44, 100, 58), vein=(40, 90, 50))


def planter_plant(cartoon=False):
    """The small jagged-leaved plant the house's planter holds (two, alike): a
    leaf standing up in the middle and four round it rising steeply, their edges
    cut into teeth. Cartoon: the four evenly set."""
    n = 10
    C = n / 2.0
    out = {}
    pal = PLANTER_PLANT
    if cartoon:
        leaves = [(math.pi / 4 + k * math.pi / 2, 1.0, 4.8, 3.0) for k in range(4)]
    else:
        leaves = [(math.radians(a), e, L, 3.0) for a, e, L in ((30, 1.05, 4.8), (150, 1.0, 4.7),
                                                                (215, 0.8, 4.6), (330, 0.85, 4.8))]
    for (az, el, L, W) in leaves:
        _leaf(out, C, (0.0, 0.0, 1.0), az, el, L, W, pal, cartoon, droop=0.5, cup=0.2, notch=True, veins=False)
    # the middle leaf, standing up
    _leaf(out, C, (0.0, 0.0, 1.0), math.pi / 2, 1.45, 7.5, 3.2, pal, cartoon, droop=0.3, cup=0.0, notch=True,
          veins=False)
    for z in range(2):
        _disc(out, n, C, z, 1.2, ("leaf", pal["vein"]))
    out = {p: v for p, v in out.items() if 0 <= p[0] < n and 0 <= p[1] < n and p[2] >= 0}
    out = connected_main(out)
    if cartoon:
        out = _symmetrize(out, n)
    return out, (n, n, max(z for (x, y, z) in out) + 1)


SPROUT = dict(light=(91, 191, 88), mid=(64, 142, 80), dark=(36, 82, 45), vein=(36, 82, 45))


def sprout(cartoon=False):
    """The tiny two-leaved sprout in the grass: a short stem and two leaves in a V,
    as drawn. Cartoon: the two mirrored exactly."""
    n = 10
    C = n / 2.0
    out = {}
    for z in range(2):
        out[(int(C) - 1, int(C), z)] = ("leaf", SPROUT["dark"])
        out[(int(C), int(C), z)] = ("leaf", SPROUT["dark"])
    for az, el in ((math.pi, 0.75), (0.0, 0.7 if not cartoon else 0.75)):
        _leaf(out, C, (0.0, 0.5, 1.5), az, el, 4.2, 2.8, SPROUT, cartoon, droop=0.6, cup=0.25, veins=False)
    out = {p: v for p, v in out.items() if 0 <= p[0] < n and 0 <= p[1] < n and p[2] >= 0}
    out = connected_main(out)
    if cartoon:
        out = _mirror1(out, n)
    return out, (n, n, max(z for (x, y, z) in out) + 1)
