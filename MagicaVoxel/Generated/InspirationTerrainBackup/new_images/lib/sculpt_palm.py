"""Palms from their sprites: a stout ringed trunk, and fronds radiating from its
top.

Measured on the sprite: the trunk's width row by row below the crown (its foot
flaring as drawn), the crown's reach (the frond tips' distance out), the height
where the fronds leave the trunk, the crown's top and the height the drooping
tips fall to. Each frond is a long blade from the crown's heart outward: it rises,
then droops to the tips' height, widest a third of the way out, a darker midrib
down its length, its edges cut into leaflets; a few shorter fronds stand up in the
middle, as the sprites draw them. Paint: the sprite's own leaf shades, light on the
fronds' upper faces, darker beneath and at the midrib; the trunk's bark in rings.

Cartoon: the fronds evenly spaced (exact quarter-turn symmetry), smooth-edged and
a little broader, two tones of leaf and one of bark.
"""
import math

import numpy as np

from sprites import hue_sat, quantize
from sculpt_tree import classify, connected_main


class Palm:
    def __init__(self, sprite, fronds=8, upright=3, seed=0):
        self.s = sprite
        rgb = sprite.rgb.astype(int)
        cls, lum = classify(rgb, sprite.mask)
        self.H, self.W = sprite.mask.shape
        leaf = cls == "leaf"
        wood = cls == "wood"
        hh, ss, vv = hue_sat(rgb)
        lp = rgb[(leaf | (cls == "line")) & (hh > 60) & (hh < 180) & (ss > 0.15)]
        self.leaf_pal = sorted([tuple(int(v) for v in c) for c in quantize(lp, 4).tolist()], key=sum)
        wp = rgb[wood]
        self.wood_pal = sorted([tuple(int(v) for v in c) for c in (quantize(wp, 3) if len(wp) else
                                                                     np.array([[110, 75, 45]])).tolist()], key=sum)
        rows_leaf = np.nonzero(leaf.any(axis=1))[0]
        self.crown_top = int(rows_leaf.min())
        # the trunk: brown pixels only, the run round the axis, from the ground up
        brown = sprite.mask & (((hh >= 8) & (hh <= 55) & (ss > 0.22)) | ((ss < 0.25) & (vv < 120) & ~leaf))
        bottom_rows = [r for r in range(self.H - 1, -1, -1) if brown[r].any()][:4]
        centres = []
        for r in bottom_rows:
            c = np.nonzero(brown[r])[0]
            centres.append((c.min() + c.max() + 1) / 2.0)
        self.cx = float(np.median(centres)) if centres else self.W / 2.0
        self.trunk = {}
        r = self.H - 1
        while r >= 0:
            c0 = int(self.cx)
            if not brown[r, max(0, c0 - 1):c0 + 2].any():
                if self.trunk:
                    break
                r -= 1
                continue
            a = c0
            while a - 1 >= 0 and brown[r, a - 1]:
                a -= 1
            b = c0
            while b + 1 < self.W and brown[r, b + 1]:
                b += 1
            self.trunk[r] = (a, b + 1)
            r -= 1
        cols = np.nonzero(sprite.mask.any(axis=0))[0]
        self.reach = max(self.cx - cols.min(), cols.max() + 1 - self.cx)
        self.trunk_top = min(self.trunk) if self.trunk else int(self.H * 0.7)
        # the fronds leave the trunk where it disappears, fanning up and out to the
        # crown's widest row, their tips drooping a little below it
        self.heart_row = self.trunk_top
        width_rows = [(np.count_nonzero(sprite.mask[r]), r) for r in range(self.crown_top, self.trunk_top)]
        self.wide_row = max(width_rows)[1] if width_rows else (self.crown_top + self.trunk_top) // 2
        self.tip_row = min(self.trunk_top, self.wide_row + 3)
        self.fronds, self.upright, self.seed = fronds, upright, seed

    def _trunk(self, out, n, C, cartoon):
        H = self.H
        rows = sorted(self.trunk)
        top = rows[0]
        wood = self.wood_pal
        for r in range(top, H):
            a, b = self.trunk.get(r, self.trunk[rows[0]])
            rad = max(1.5, (b - a) / 2.0)
            z = H - 1 - r
            for x in range(n):
                for y in range(n):
                    dx, dy = x + 0.5 - C, y + 0.5 - C
                    d = math.hypot(dx, dy)
                    if d <= rad:
                        if cartoon:
                            col = wood[len(wood) // 2]
                        else:
                            ring = (z // 2) % 2
                            col = wood[-1] if (ring == 0 and d > rad - 1.2) else wood[len(wood) // 2]
                            if d > rad - 0.8 and (z % 2 == 1):
                                col = wood[0]
                        out[(x, y, z)] = ("wood", col)
        # the trunk runs up into the heart of the crown
        zt = H - 1 - rows[0]
        zh = H - 1 - self.heart_row
        rad = max(1.5, (self.trunk[rows[0]][1] - self.trunk[rows[0]][0]) / 2.0 - 1)
        for z in range(zt, min(H, zh + 5)):
            for x in range(n):
                for y in range(n):
                    if math.hypot(x + 0.5 - C, y + 0.5 - C) <= rad:
                        out.setdefault((x, y, z), ("wood", wood[len(wood) // 2]))

    def _frond(self, out, n, C, ang, el, length, z0, stretch, width, cartoon, sag=0.18):
        """One frond from the heart (C, C, z0) along azimuth [ang] at elevation [el]
        (radians), [length] out across the ground, its rise stretched by [stretch],
        sagging at the tip; widest a third of the way out, tapering to a point."""
        light, midc, dark = self.leaf_pal[-1], self.leaf_pal[len(self.leaf_pal) // 2], self.leaf_pal[0]
        ux, uy = math.cos(ang), math.sin(ang)
        vx, vy = -uy, ux
        rise = length * math.tan(el) * stretch if el < 1.45 else length * 6 * stretch
        steps = int(max(length, abs(rise)) * 2.5) + 2
        for i in range(steps + 1):
            t = i / float(steps)
            zc = z0 + rise * t - sag * length * t * t * (1.0 - 0.6 * el)
            w = width * (math.sin(math.pi * min(1.0, 0.12 + t * 0.82)) ** 0.9)
            w = max(0.7, w if t < 0.9 else w * (1 - t) * 10)
            for k in range(-int(w) - 1, int(w) + 2):
                if abs(k) > w:
                    continue
                if not cartoon and abs(k) > w * 0.7 and (i // 3 + (k > 0)) % 2 == 0:
                    continue
                px = C + ux * t * length + vx * k
                py = C + uy * t * length + vy * k
                zz = int(round(zc - (0.0 if abs(k) < w * 0.5 else 0.8)))
                x, y = int(math.floor(px)), int(math.floor(py))
                if not (0 <= x < n and 0 <= y < n) or zz < 0 or zz >= self.H:
                    continue
                if cartoon:
                    col = light if abs(k) >= 1 else midc
                else:
                    col = dark if abs(k) < 0.6 else (light if abs(k) < w * 0.75 else midc)
                out[(x, y, zz)] = ("leaf", col)
                if zz - 1 >= 0:
                    out.setdefault((x, y, zz - 1), ("leaf", dark if not cartoon else midc))

    def build(self, cartoon=False):
        n = int(math.ceil(2 * self.reach)) + 2
        n += n % 2
        C = n / 2.0
        H = self.H
        out = {}
        self._trunk(out, n, C, cartoon)
        # the heart a little above the trunk's visible top; the fronds at their own
        # angles (a 3/4 view draws a crown taller than it is: its far fronds higher)
        z0 = H - 1 - self.heart_row + 3
        R = self.reach - 0.5
        width = max(2.0, self.reach / 3.4) * (1.08 if cartoon else 1.0)
        rings = [(8, math.radians(14), 1.0), (6, math.radians(40), 0.85), (3, math.radians(68), 0.6)]
        stretch = 1.0
        rnd = np.random.RandomState(self.seed)
        for ri, (count, el, frac) in enumerate(rings):
            count = count if not cartoon else {8: 8, 6: 8, 3: 4}[count]
            for i in range(count):
                ang = 2 * math.pi * i / count + (ri % 2) * math.pi / count
                if not cartoon:
                    ang += rnd.uniform(-0.15, 0.15)
                ln = R * frac * (1.0 if cartoon else rnd.uniform(0.9, 1.05))
                self._frond(out, n, C, ang, el, ln, z0, stretch, width * (1.0 - 0.1 * ri), cartoon, sag=0.14 if ri == 0 else 0.12)

        out = connected_main(out)
        if cartoon:
            out = _symmetrize(out, n)
        top = max(z for (x, y, z) in out) + 1
        return out, (n, n, top)


def _symmetrize(out, n):
    """Exact quarter-turn symmetry from the quarter x >= n/2, y >= n/2."""
    half = n // 2
    full = {}
    for (x, y, z), v in out.items():
        if x >= half and y >= half:
            for xx, yy in ((x, y), (n - 1 - y, x), (n - 1 - x, n - 1 - y), (y, n - 1 - x)):
                full[(xx, yy, z)] = v
    return connected_main(full)
