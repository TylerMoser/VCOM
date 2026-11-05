"""Small plants from their sprites: grasses, reeds and ferns as blades; sprouts
and seedlings as leaf lobes on a stem; lily pads seen from above; a columnar
cactus; a root stump. Each builder returns ({(x, y, z): (material, rgb)}, size)
for Base or Cartoon (cartoon=True); materials are 'leaf', 'wood', 'earth',
'flower', 'bloom' (a pale flower), and a model stands on z 0 (floating leaves: z 0
the water's surface; reeds: z 0 the water's surface they rise from).

Blades: a clump's blades stand on a round footprint as wide as the sprite's base
(a square tile for the tile tufts), each as tall as the sprite's silhouette above
its place across, leaning out from the middle and tapering from two voxels wide to
one, dark at the foot and light at the tip in the sprite's own greens. Cartoon:
the blades set on a regular pattern with exact quarter-turn symmetry, two bands
of colour.

Lobes: each leaf of a sprout is the round lobe the sprite draws, as wide and as
high as drawn and two-thirds as thick, on its own side of the stem (front-back
mirror: these plants are drawn bilateral); a mound of earth where the sprite
draws one. Cartoon: both sides mirrored exactly, the leaves one shade and a voxel thicker.

Pads: a lily pad is the shape the sprite draws seen from above, a voxel thick, a
big one with the raised rim and the notch pads have; a lotus two rings of petals
on its pad. Cactus: its columns where the sprite draws them, ribbed, domed.
"""
import math

import numpy as np

from sprites import hue_sat, interior, is_water, quantize
from sculpt_tree import classify, connected_main


def _greens(rgb, mask, k=4):
    h, s, v = hue_sat(rgb)
    sel = interior(mask) & (h > 50) & (h < 170) & (s > 0.18)
    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    if sel.sum() > 20:
        sel &= lum <= np.percentile(lum[sel], 92)   # no paler than the sprite's own light green
    px = rgb[sel]
    if not len(px):
        px = rgb[mask]
    return sorted([tuple(int(c) for c in q) for q in quantize(px, k).tolist()], key=sum)


def _sym4(out, n):
    half = n // 2
    full = {}
    for (x, y, z), v in out.items():
        if x >= half and y >= half:
            for xx, yy in ((x, y), (n - 1 - y, x), (n - 1 - x, n - 1 - y), (y, n - 1 - x)):
                full[(xx, yy, z)] = v
    return full


def _mirror_x(out, n):
    """Exact mirror symmetry across x (left to right), from the half x >= n/2."""
    full = {}
    for (x, y, z), v in out.items():
        if x >= n // 2:
            full[(x, y, z)] = v
            full[(n - 1 - x, y, z)] = v
    return full


def _mirror_xy(out, nx, ny):
    full = {}
    for (x, y, z), v in out.items():
        if x >= nx // 2 and y >= ny // 2:
            for xx in (x, nx - 1 - x):
                for yy in (y, ny - 1 - y):
                    full[(xx, yy, z)] = v
    return full


# ---------------------------------------------------------------------- blades
def blades(sprite, cartoon=False, footprint="round", count=None, lean=0.45, curl=0.0, seed=1, width=2,
           blooms=None, leaflets=False, tip_light=True, mat=None):
    """A clump of blades. footprint: 'round' (a disc as wide as the sprite's base)
    or 'tile' (a 16 x 16 square); curl: a sideways sweep (wind-blown blades);
    blooms: an RGB for small flowers at some blades' tips; leaflets: notched
    edges (a fern)."""
    rgb = sprite.rgb.astype(int)
    m = sprite.mask & ~is_water(sprite.rgb)
    H, W = m.shape
    # rows at and below the water's top are under water: the plant starts at its surface
    wet = is_water(sprite.rgb) & sprite.mask
    wet_rows = [r for r in range(H) if wet[r].sum() >= 3]
    if wet_rows:
        H = min(wet_rows)
        m = m[:H]
        rgb = rgb[:H]
    pal = _greens(rgb, m, 5)
    cols = np.nonzero(m.any(axis=0))[0]
    c0, c1 = cols.min(), cols.max() + 1
    cx = (c0 + c1) / 2.0
    half = (c1 - c0) / 2.0
    # the silhouette's top row at each column: the blade heights across
    top = {}
    for c in range(W):
        r = np.nonzero(m[:, c])[0]
        if len(r):
            top[c] = H - r.min()
    if footprint == "tile":
        n = 16
    else:
        n = int(math.ceil(2 * half)) + 2
        n += n % 2
    C = n / 2.0
    rnd = np.random.RandomState(seed)
    out = {}
    R = (n / 2.0 - 1.0) if footprint == "tile" else max(1.5, half * 0.55)
    count = count or max(10, int((n * n) / (7 if footprint == "tile" else 5)))
    pts = []
    if cartoon and curl:
        for j in range(count):
            pts.append((2.0 + (n - 4.0) * (j + 0.5) / count, C - 1.5 + 3.0 * ((j % 2))))
    elif cartoon:
        rings = max(2, int(R / 2.2))
        for ri in range(1, rings + 1):
            rr = R * ri / rings
            k = 4 * ri
            for j in range(k):
                a = 2 * math.pi * j / k + (math.pi / k if ri % 2 else 0)
                pts.append((C + rr * math.cos(a), C + rr * math.sin(a)))
    else:
        while len(pts) < count:
            if footprint == "tile":
                x, y = rnd.uniform(0.5, n - 0.5), rnd.uniform(0.5, n - 0.5)
            else:
                a, r = rnd.uniform(0, 2 * math.pi), R * math.sqrt(rnd.uniform(0, 1))
                x, y = C + r * math.cos(a), C + r * math.sin(a)
            pts.append((x, y))
    hmax = max(top.values())
    for i, (bx, by) in enumerate(pts):
        # the blade's height: the silhouette above its place across the front view
        u = bx - C
        col = int(min(c1 - 1, max(c0, math.floor(cx + u * (half / max(1.0, n / 2.0 - 1))))))
        h = top.get(col, hmax)
        if cartoon:
            dd = math.hypot(bx - C, by - C) / max(1.0, R)
            h = hmax * (0.9 - 0.3 * dd * dd)
        else:
            h = h * rnd.uniform(0.82, 1.0)
        h = max(2, int(round(h)))
        dx, dy = bx - C, by - C
        d = math.hypot(dx, dy) or 1.0
        ox, oy = dx / d, dy / d
        if curl:
            ox, oy = 1.0, 0.25 * (dy / d)
        k = lean * (d / max(1.0, R)) * h * 0.6 + abs(curl) * h
        for z in range(h):
            t = z / max(1.0, h - 1)
            sweep = k * (t ** 1.6)
            px, py = bx + ox * sweep * (1 if curl >= 0 else -1), by + oy * sweep
            w = width if t < 0.45 else 1
            for ex in range(w):
                for ey in range(1 if w == 1 else 2):
                    x, y = int(math.floor(px)) + ex, int(math.floor(py)) + ey
                    if not (0 <= x < n and 0 <= y < n):
                        continue
                    if leaflets and t > 0.25 and z % 3 == 0 and not cartoon:
                        for sx, sy in ((-oy, ox), (oy, -ox)):
                            lx, ly = int(math.floor(px + sx * 1.6)), int(math.floor(py + sy * 1.6))
                            if 0 <= lx < n and 0 <= ly < n:
                                out[(lx, ly, z)] = ("leaf", pal[-2])
                    if cartoon:
                        col_ = pal[-2] if t > 0.55 else pal[len(pal) // 2]
                    else:
                        band = min(len(pal) - 1, int(t * len(pal)))
                        col_ = pal[band] if tip_light else pal[len(pal) - 1 - band]
                    out[(x, y, z)] = ("leaf", col_)
        if blooms is not None and (i % 3 == 0):
            x, y = int(math.floor(bx + ox * k)), int(math.floor(by + oy * k))
            for q in ((x, y, h), (x + 1, y, h), (x, y + 1, h)):
                if 0 <= q[0] < n and 0 <= q[1] < n:
                    out[q] = ("bloom", tuple(blooms))
    if cartoon and not curl:
        out = _sym4(out, n)
    mat = mat or ("tile" if footprint == "tile" else "disc")
    if mat == "row":
        # the blades' feet joined by a low root ridge across the tile
        ys = sorted(int(math.floor(by)) for bx, by in pts)
        ymid = ys[len(ys) // 2]
        for (bx, by) in pts:
            xx = int(math.floor(bx))
            for y in range(min(ymid, int(math.floor(by))), max(ymid, int(math.floor(by))) + 1):
                if 0 <= xx < n and 0 <= y < n:
                    out.setdefault((xx, y, 0), ("leaf", pal[0]))
        xs_ = sorted(int(math.floor(bx)) for bx, by in pts)
        for x in range(max(0, xs_[0]), min(n, xs_[-1] + 1)):
            out.setdefault((x, ymid, 0), ("leaf", pal[0]))
    elif mat == "tile":
        # a tile clump: its blades meet at their feet on a low turf mat, one piece
        for x in range(n):
            for y in range(n):
                out.setdefault((x, y, 0), ("leaf", pal[0] if not cartoon else pal[len(pal) // 2]))
    else:
        rad = R + 0.5
        for x in range(n):
            for y in range(n):
                if math.hypot(x + 0.5 - C, y + 0.5 - C) <= rad:
                    out.setdefault((x, y, 0), ("leaf", pal[0] if not cartoon else pal[len(pal) // 2]))
    if cartoon and mat == "row":
        # balanced front to back (the sweep keeps its direction)
        full = {}
        for (x, y, z), v in out.items():
            if y >= n // 2:
                full[(x, y, z)] = v
                full[(x, n - 1 - y, z)] = v
        out = full
    out = connected_main(out)
    top_z = max(z for (x, y, z) in out) + 1
    return out, (n, n, top_z)


# ----------------------------------------------------------------------- lobes
def lobes(sprite, cartoon=False, mound=None, stem_rgb=None, thick=2.0, tilt=0.45):
    """A sprout or seedling: each leaf drawn (the sprite's leaf pixels either side of
    the stem) a thin disc as wide and as high as drawn, tilted up and out from the
    stem; a stem from the ground to where they meet; a mound of earth (mound: its
    RGB) where the sprite draws one."""
    if cartoon:
        thick += 1.0          # Cartoon: plumper leaves, a voxel thicker
    rgb = sprite.rgb.astype(int)
    m = sprite.mask
    H, W = m.shape
    hh, ss, vv = hue_sat(rgb)
    pal = _greens(rgb, m, 4)
    leafy = m & (hh > 50) & (hh < 175) & (ss > 0.15)
    cols = np.nonzero(m.any(axis=0))[0]
    cx = (cols.min() + cols.max() + 1) / 2.0
    leaves = []
    for side in (-1, 1):
        sel = leafy.copy()
        for c in range(W):
            if (c + 0.5 - cx) * side <= 1.0:
                sel[:, c] = False
        rs, cs = np.nonzero(sel)
        if len(rs) >= 4:
            leaves.append((side, rs.min(), rs.max(), cs.min(), cs.max()))
    lowest = max([l[2] for l in leaves] + [0])
    n = W + 2 + (W % 2)
    C = n / 2.0
    ny = max(6, int(round(max([l[4] - l[3] + 1 for l in leaves] + [4]) * 0.8)) + 2)
    ny += ny % 2
    Cy = ny / 2.0
    out = {}
    for (side, r0, r1, c0, c1) in leaves:
        rx = (c1 - c0 + 1) / 2.0
        ux = (c0 + c1 + 1) / 2.0 - cx
        zc = H - (r0 + r1 + 1) / 2.0
        ry = max(1.2, rx * 0.75)
        for x in range(n):
            for y in range(ny):
                for z in range(H):
                    dx = x + 0.5 - C - ux
                    dz = z + 0.5 - zc
                    e = (dx / rx) ** 2 + ((y + 0.5 - Cy) / ry) ** 2
                    if e <= 1.0 and abs(dz - (side * dx) * tilt) <= thick / 2.0 + 0.5 * (1 - e):
                        row = int(math.floor(H - 0.5 - z))
                        col = int(math.floor(cx + (x + 0.5 - C)))
                        if cartoon:
                            c_ = pal[-2] if (z + 0.5) > zc else pal[len(pal) // 2]
                        elif 0 <= row < H and 0 <= col < W and m[row, col]:
                            c_ = min(pal, key=lambda q: sum((q[i] - rgb[row, col][i]) ** 2 for i in range(3)))
                        else:
                            c_ = pal[len(pal) // 2]
                        out[(x, y, z)] = ("leaf", c_)
    # the leaves' lowest voxel: the stem reaches it
    leaf_low = min([z for (x, y, z) in out] or [1])
    # the stem's colour: brown drawn on the axis under the leaves, else the darkest green
    hh2, ss2, vv2 = hue_sat(rgb)
    axis = np.zeros_like(m)
    axis[min(H - 1, lowest):, max(0, int(cx) - 1):int(cx) + 1] = True
    brown = axis & m & (((hh2 < 55) | (hh2 > 330)) & (ss2 > 0.18))
    if stem_rgb is not None:
        stem_c = tuple(int(v) for v in stem_rgb)
    elif brown.sum() >= 2:
        stem_c = tuple(int(v) for v in np.median(rgb[brown], axis=0))
    else:
        stem_c = pal[0]
    stem_mat = "wood" if (stem_c[0] >= stem_c[1]) else "leaf"
    xs = int(math.floor(C))
    for z in range(0, leaf_low + 2):
        for x in (xs - 1, xs):
            for y in (int(Cy) - 1, int(Cy)):
                out.setdefault((x, y, z), (stem_mat, stem_c))
    # a stalk from the stem's top to each leaf's middle
    stalk = pal[0]
    zt = leaf_low + 1
    for (side, r0, r1, c0, c1) in leaves:
        ux = (c0 + c1 + 1) / 2.0 - cx
        zc = H - (r0 + r1 + 1) / 2.0
        steps = int(abs(ux) * 3) + 2
        for i in range(steps + 1):
            t = i / float(steps)
            x = int(math.floor(C + ux * t))
            z = int(round(zt + (zc - zt) * t * t))
            for y in (int(Cy) - 1, int(Cy)):
                if 0 <= x < n and 0 <= z < H:
                    out.setdefault((x, y, z), ("leaf", stalk))
    if mound is not None:
        for x in range(n):
            for y in range(ny):
                for z in range(2):
                    if math.hypot((x + 0.5 - C) / 3.5, (y + 0.5 - Cy) / 2.5) <= 1.0 - 0.35 * z:
                        out[(x, y, z)] = ("earth", tuple(mound))
    if cartoon:
        out = _mirror_x(out, n)
    out = connected_main(out)
    top_z = max(z for (x, y, z) in out) + 1
    return out, (n, ny, top_z)


# ------------------------------------------------------------------------ pads
def _pad_regions(sprite, exclude):
    """The sprite's lily pads: [(pixels, mean RGB)], each pad's lighter body grown
    out over the dark outline round it (overlapping pads are split at the outlines
    the sprite draws between them), and the sprite's greens."""
    rgb = sprite.rgb.astype(int)
    m = sprite.mask.copy() & ~is_water(sprite.rgb)
    H, W = m.shape
    if exclude is not None:
        ex0, ey0, ex1, ey1 = exclude
        m[ey0:ey1, ex0:ex1] = False
    hh, ss, vv = hue_sat(rgb)
    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    green = m & (hh > 70) & (hh < 160) & (ss > 0.3)
    thr = np.percentile(lum[green], 22) if green.sum() > 10 else 0
    core = green & (lum > thr)
    # the pad goes on under a flower drawn over it
    flower = m & ((hh < 20) | (hh > 300)) & (ss > 0.15)
    core |= flower
    green = green | flower
    lab = np.zeros((H, W), int)
    k = 0
    for r in range(H):
        for c in range(W):
            if core[r, c] and not lab[r, c]:
                k += 1
                stack = [(r, c)]
                lab[r, c] = k
                while stack:
                    a, b = stack.pop()
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        aa, bb = a + da, b + db
                        if 0 <= aa < H and 0 <= bb < W and core[aa, bb] and not lab[aa, bb]:
                            lab[aa, bb] = k
                            stack.append((aa, bb))
    # the outline pixels go to the pad they border, two pixels out at most
    for _ in range(2):
        grow = lab.copy()
        for r in range(H):
            for c in range(W):
                if green[r, c] and not lab[r, c]:
                    for da, db in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        aa, bb = r + da, c + db
                        if 0 <= aa < H and 0 <= bb < W and lab[aa, bb]:
                            grow[r, c] = lab[aa, bb]
                            break
        lab = grow
    pads = []
    for i in range(1, k + 1):
        pts = [(int(a), int(b)) for a, b in np.argwhere(lab == i)]
        if len(pts) >= 6:
            pads.append(pts)
    return pads, rgb, green


def _petals(out, fx, fy, z0, rad, pink, cartoon, seed=0):
    """A lotus at (fx, fy) on z0: an outer ring of eight petals spread low and an
    inner ring of six standing up, their tips curling up and their sides cupped, a
    yellow heart. Cartoon: built in one quarter round the voxel corner nearest the
    flower's middle and turned to the other three."""
    light = tuple(min(255, int(v * 1.1 + 12)) for v in pink)
    dark = tuple(int(v * 0.78) for v in pink)
    rnd = np.random.RandomState(seed)
    X, Y = (int(round(fx)), int(round(fy))) if cartoon else (fx, fy)
    rings = [(8, math.radians(24), rad, 1.6), (8 if cartoon else 6, math.radians(56), rad * 0.62, 1.25)]
    part = {}
    for ri, (count, el, L, w0) in enumerate(rings):
        for i in range(count):
            ang = 2 * math.pi * i / count + ri * math.pi / count
            if not cartoon:
                ang += rnd.uniform(-0.12, 0.12)
            ux, uy = math.cos(ang), math.sin(ang)
            vx, vy = -uy, ux
            steps = int(L * 4) + 2
            for s in range(steps + 1):
                t = s / float(steps)
                h = z0 + t * L * math.tan(el) + 0.8 * t * t
                w = w0 * math.sin(math.pi * min(1.0, 0.25 + 0.75 * t))
                kk = -w
                while kk <= w + 1e-6:
                    px = X + ux * t * L + vx * kk
                    py = Y + uy * t * L + vy * kk
                    q = (int(math.floor(px)), int(math.floor(py)), int(round(h + abs(kk) * 0.45)))
                    col = dark if t < 0.3 else (light if t > 0.72 else pink)
                    part[q] = ("flower", col)
                    kk += 0.5
    for x in range(int(X) - 3, int(X) + 4):
        for y in range(int(Y) - 3, int(Y) + 4):
            d = math.hypot(x + 0.5 - X, y + 0.5 - Y)
            if d <= 1.25:
                part[(x, y, z0)] = ("bloom", (238, 212, 96))
                part[(x, y, z0 + 1)] = ("bloom", (250, 232, 128))
            elif d <= 2.2:
                part.setdefault((x, y, z0), ("flower", dark))
    if cartoon:
        full = {}
        for (x, y, z), v in part.items():
            if x >= X and y >= Y:
                for xx, yy in ((x, y), (X + Y - 1 - y, x - X + Y), (2 * X - 1 - x, 2 * Y - 1 - y),
                               (y - Y + X, X + Y - 1 - x)):
                    full[(xx, yy, z)] = v
        part = full
    out.update(part)


def pads(sprite, cartoon=False, flower=None, exclude=None):
    """Lily pads, the sprite read as seen from above: each pad flat, a voxel thick,
    in the sprite's own greens; a big pad (four voxels or more across its middle
    from its edge) has the raised rim and the notch to its middle a lily pad has.
    [flower] an RGB for a lotus standing on its pad. exclude: (x0, y0, x1, y1) of
    the sprite to leave out (another sprite's). Cartoon: each pad a round disc of
    the same size where it lies, the notch the same way on all, two greens."""
    pads_, rgb, green = _pad_regions(sprite, exclude)
    H, W = green.shape
    pal = _greens(rgb, green, 4)
    nx, ny = W + 2, H + 2
    out = {}
    NOTCH = 0.6
    for pts in pads_:
        rs = np.array([p[0] for p in pts], float)
        cs = np.array([p[1] for p in pts], float)
        rc, cc = rs.mean() + 0.5, cs.mean() + 0.5
        req = math.sqrt(len(pts) / math.pi)
        big = req >= 3.8
        px0, py0 = cc + 1, (H - rc) + 1        # the pad's middle in voxels
        if cartoon:
            X, Y = round(px0), round(py0)
            cells = []
            for x in range(int(X - req) - 1, int(X + req) + 2):
                for y in range(int(Y - req) - 1, int(Y + req) + 2):
                    d = math.hypot(x + 0.5 - X, y + 0.5 - Y)
                    if d <= req + 0.2:
                        cells.append((x, y, d, math.atan2(y + 0.5 - Y, x + 0.5 - X)))
            for (x, y, d, ang) in cells:
                if big and d > 0.8 and abs(math.sin(ang - NOTCH)) * d < 0.6 and math.cos(ang - NOTCH) > 0:
                    continue
                rim = big and d > req - 1.0
                out[(x, y, 0)] = ("leaf", pal[-1] if rim else pal[len(pal) // 2])
                if rim:
                    out[(x, y, 1)] = ("leaf", pal[-1])
            continue
        # the ellipse its pixels fill (as wide and as deep as drawn), coloured from them
        mine = set(pts)
        ex = max(1.0, (cs.max() - cs.min() + 1) / 2.0)
        ey = max(1.0, (rs.max() - rs.min() + 1) / 2.0)
        fill = []
        for x in range(int(px0 - ex) - 1, int(px0 + ex) + 2):
            for y in range(int(py0 - ey) - 1, int(py0 + ey) + 2):
                dx, dy = x + 0.5 - px0, y + 0.5 - py0
                if (dx / (ex + 0.15)) ** 2 + (dy / (ey + 0.15)) ** 2 <= 1.0:
                    fill.append((x, y, dx, dy))
        cells = {(x, y) for (x, y, dx, dy) in fill}
        mean = tuple(int(v) for v in np.mean([rgb[r, c] for (r, c) in pts], axis=0))
        for (x, y, dx, dy) in fill:
            d = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            if big and d > 0.8 and abs(math.sin(ang - NOTCH)) * d < 0.6 and math.cos(ang - NOTCH) > 0:
                continue
            r, c = H - y, x - 1
            src = rgb[r, c] if (r, c) in mine and green[r, c] else mean
            col = min(pal, key=lambda q: sum((q[i] - src[i]) ** 2 for i in range(3)))
            out[(x, y, 0)] = ("leaf", col)
            edge = any(q not in cells for q in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
            if big and edge:
                out[(x, y, 1)] = ("leaf", pal[-1])
    if flower is not None:
        hh, ss, vv = hue_sat(rgb)
        pink = sprite.mask & ((hh < 20) | (hh > 300)) & (ss > 0.15)
        if pink.any():
            rs, cs = np.nonzero(pink)
            fx, fy = cs.mean() + 0.5 + 1, (H - (rs.mean() + 0.5)) + 1
            rad = max(2.5, math.sqrt(len(rs) / math.pi))
            _petals(out, fx, fy, 1, rad, tuple(flower), cartoon)
    out = {p: v for p, v in out.items() if 0 <= p[0] < nx and 0 <= p[1] < ny}
    return out, (nx, ny, max(z for (x, y, z) in out) + 1 if out else 1)


# ---------------------------------------------------------------------- cactus
def cactus(sprite, cartoon=False, columns=None, cartoon_columns=None):
    """A clump of upright columns, as the sprite draws them round its tallest:
    columns: [(azimuth in degrees, distance out, height, radius)], read off the
    sprite by eye (the middle column, the pair drawn high behind it, the two at the
    sides and the pair drawn low in front); Cartoon's evenly placed. Each column a
    round shaft with a domed top, four light ribs down it and dark grooves between,
    on a dark foot joining the clump."""
    rgb = sprite.rgb.astype(int)
    m = sprite.mask
    pal = _greens(rgb, m, 4)
    cols = cartoon_columns if cartoon else columns
    reach = max(d + r for (a, d, h, r) in cols)
    n = int(math.ceil(2 * reach)) + 2
    n += n % 2
    C = n / 2.0
    out = {}
    for (az, dist, hgt, r) in cols:
        a = math.radians(az)
        px, py = dist * math.cos(a), dist * math.sin(a)
        for x in range(n):
            for y in range(n):
                dx, dy = x + 0.5 - C - px, y + 0.5 - C - py
                d = math.hypot(dx, dy)
                if d > r + 0.25:
                    continue
                ang = (math.atan2(dy, dx) - a) % (2 * math.pi)
                sector = ang / (math.pi / 4)                  # eight: ribs on the even ones
                rib = abs(sector - round(sector)) < 0.28 and int(round(sector)) % 2 == 0
                groove = abs(sector - round(sector)) < 0.28 and int(round(sector)) % 2 == 1
                for z in range(int(hgt)):
                    cap = max(0.0, z + 0.5 - (hgt - r))
                    if d * d + cap * cap > (r + 0.25) ** 2:
                        continue
                    surface = d > r - 0.9 or cap > 0
                    if not surface:
                        col = pal[1]
                    elif cap > r * 0.45:
                        col = pal[-1]
                    elif cartoon:
                        col = pal[-1] if rib else pal[2]
                    else:
                        col = pal[-1] if rib else (pal[0] if groove else pal[2])
                    out.setdefault((x, y, z), ("leaf", col))
    # the dark foot the columns stand on
    for x in range(n):
        for y in range(n):
            dx, dy = x + 0.5 - C, y + 0.5 - C
            if math.hypot(dx, dy) <= reach - 1.5 or any(
                    math.hypot(dx - d * math.cos(math.radians(a)), dy - d * math.sin(math.radians(a))) <= r + 0.6
                    for (a, d, h, r) in cols):
                out[(x, y, 0)] = ("leaf", pal[0])
                if (x, y, 1) not in out:
                    out[(x, y, 1)] = ("leaf", pal[0])
    if cartoon:
        out = _sym4(out, n)
    out = connected_main(out)
    return out, (n, n, max(z for (x, y, z) in out) + 1)


# ------------------------------------------------------------------- root stump
def root_stump(sprite, cartoon=False, height=None):
    """A cut stump with its roots spread round its foot: its top as wide as the
    sprite's pale cut face, rings on it, bark below, five roots running out and
    down to the ground."""
    rgb = sprite.rgb.astype(int)
    m = sprite.mask
    H, W = m.shape
    hh, ss, vv = hue_sat(rgb)
    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    pale = m & (lum > 165)
    rows = np.nonzero(pale.any(axis=1))[0]
    cols = np.nonzero(pale.any(axis=0))[0]
    top_r = (cols.max() - cols.min() + 1) / 2.0
    face_rows = rows.max() - rows.min() + 1
    bark = m & ~pale & (lum < 150)
    barkpx = rgb[bark]
    bark_pal = sorted([tuple(int(c) for c in q) for q in quantize(barkpx, 3).tolist()], key=sum)
    face_pal = sorted([tuple(int(c) for c in q) for q in quantize(rgb[pale], 3).tolist()], key=sum)
    allcols = np.nonzero(m.any(axis=0))[0]
    spread = (allcols.max() - allcols.min() + 1) / 2.0
    # its height: the bark band drawn under the cut face
    hgt = height or max(6, int(H - rows.max() - 1 + face_rows * 0.35))
    n = int(math.ceil(2 * spread)) + 2
    n += n % 2
    C = n / 2.0
    out = {}
    for x in range(n):
        for y in range(n):
            dx, dy = x + 0.5 - C, y + 0.5 - C
            d = math.hypot(dx, dy)
            for z in range(hgt):
                r = top_r * (1.0 + 0.25 * max(0.0, (3 - z) / 3.0))
                if d <= r:
                    if z == hgt - 1:
                        ring = int(d) % 2 == 0
                        col = (face_pal[-1] if not ring else face_pal[len(face_pal) // 2]) if not cartoon else face_pal[-1]
                        if not cartoon and d < 1.2:
                            col = face_pal[0]
                        out[(x, y, z)] = ("cut", col)
                    else:
                        if cartoon:
                            col = bark_pal[len(bark_pal) // 2]
                        else:
                            col = bark_pal[0] if (int(math.degrees(math.atan2(dy, dx)) // 25) % 3 == 0) else bark_pal[len(bark_pal) // 2]
                        out[(x, y, z)] = ("wood", col)
    # roots: five (Cartoon: four) wedges from the trunk's foot out to the sprite's spread
    k = 4 if cartoon else 5
    for i in range(k):
        a = 2 * math.pi * i / k + (0.0 if cartoon else 0.3 * math.sin(i * 1.7))
        for step in range(int((spread - top_r) * 3) + 1):
            t = step / max(1.0, (spread - top_r) * 3)
            rr = top_r + t * (spread - top_r)
            zt = (1 - t) * min(4, hgt - 2)
            px, py = C + rr * math.cos(a), C + rr * math.sin(a)
            wdt = 1.6 * (1 - 0.6 * t)
            for x in range(int(px - 2), int(px + 3)):
                for y in range(int(py - 2), int(py + 3)):
                    if 0 <= x < n and 0 <= y < n and math.hypot(x + 0.5 - px, y + 0.5 - py) <= wdt:
                        for z in range(0, int(zt) + 1):
                            out.setdefault((x, y, z), ("wood", bark_pal[0] if not cartoon else bark_pal[len(bark_pal) // 2]))
    if cartoon:
        out = _sym4(out, n)
    return connected_main(out), (n, n, hgt)
