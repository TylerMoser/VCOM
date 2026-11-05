"""Trees and bushes sculpted from their sprites.

A sprite is a tree as seen from its front; seen from any other side it looks much
the same. So the tree is the solid that shows the sprite's silhouette from each
of its four sides, cut to a round column of each row's reach: where a row of the
sprite is whole the row is a round slice, where it has gaps (a trunk showing
between low clumps, the space under a crown) the clumps stand apart on the four
sides and the trunk shows between them. The sprite's rows are the heights (its
bottom row z 0), one of its pixels a voxel, as the workspace's tree collections
size their trees from their sprites.

Its dark outline lines, drawn between clumps and round tiers, are cut one voxel in
where they show on the surface, so the clumps stand out in the round. Each surface
voxel is painted from the side it faces (the sprite's colour at its height and its
place across that view), reduced to the family's own shades of leaf and wood. The
wood is the sprite's browns and greys, with a hidden trunk carried up inside the
crown so the wood is one piece from the ground; hanging vines (thin strands under
a crown) are hung round the crown's rim on its four sides.

A second colourway of the same art (the sheet's darker copies) shares the first's
geometry exactly and is painted from its own sprite, laid over the first.

Cartoon: the sprite's fuller half mirrored to make it symmetric, small notches
closed, built in one quarter and turned to the other three (exact quarter-turn
symmetry of shape and paint), shallow lobes cut round each tier, and painted in
broad bands of the sprite's own leaf shades: light at the top of each tier, dark
at its foot, the wood one brown.
"""
import math

import numpy as np

from sprites import hue_sat, nearest, quantize

PHIS = [k * math.pi / 4 for k in range(8)]
SIDES = PHIS[::2]


def classify(rgb, mask):
    """Per pixel: 'leaf', 'wood', 'line' (a dark outline) or None (background)."""
    h, s, v = hue_sat(rgb)
    lum = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    out = np.full(mask.shape, None, dtype=object)
    green = (h > 60) & (h < 180) & (s > 0.15)
    brown = (((h < 55) | (h > 320)) & (s > 0.12)) | ((s < 0.18) & (v < 160))
    out[mask & green] = "leaf"
    out[mask & ~green & brown] = "wood"
    out[mask & (out == None)] = "leaf"  # noqa: E711  other colours (blossom, fruit) belong to the crown
    dark = mask & (lum < 55)
    out[dark & (out == "leaf")] = "line"
    out[dark & (out == "wood") & (lum < 35)] = "line"
    return out, lum


def fill_lines(cls):
    """Each outline pixel takes the material of its nearest non-outline neighbour."""
    out = cls.copy()
    H, W = cls.shape
    for r in range(H):
        for c in range(W):
            if cls[r, c] != "line":
                continue
            best = None
            for d in range(1, 4):
                for dr, dc in ((0, -d), (0, d), (-d, 0), (d, 0)):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < H and 0 <= cc < W and cls[rr, cc] in ("leaf", "wood"):
                        best = cls[rr, cc]
                        break
                if best:
                    break
            out[r, c] = best or "leaf"
    return out


def connected_main(out):
    """The largest six-connected part of {voxel: value}."""
    left = set(out)
    best = set()
    while left:
        seed = left.pop()
        part, todo = {seed}, [seed]
        while todo:
            x, y, z = todo.pop()
            for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if q in left:
                    left.discard(q)
                    part.add(q)
                    todo.append(q)
        if len(part) > len(best):
            best = part
    return {p: out[p] for p in best}


def _runs(row, gap=1):
    """[(first, end)] of a row's runs of True, gaps of [gap] pixels or fewer closed."""
    runs = []
    for c in np.nonzero(row)[0]:
        c = int(c)
        if runs and c - runs[-1][1] <= gap:
            runs[-1][1] = c + 1
        else:
            runs.append([c, c + 1])
    return [(a, b) for a, b in runs]


def _components(vox):
    """The six-connected parts of a set of voxels, largest first."""
    left = set(vox)
    parts = []
    while left:
        seed = left.pop()
        part, todo = {seed}, [seed]
        while todo:
            x, y, z = todo.pop()
            for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if q in left:
                    left.discard(q)
                    part.add(q)
                    todo.append(q)
        parts.append(part)
    parts.sort(key=len, reverse=True)
    return parts


def align(a_mask, b_mask, reach=3):
    """The shift (dr, dc) of b over a that best overlaps their masks."""
    best, bs = -1, (0, 0)
    H, W = a_mask.shape
    for dr in range(-reach, reach + 1):
        for dc in range(-reach, reach + 1):
            sh = np.zeros_like(a_mask)
            r0, r1 = max(0, dr), min(H, b_mask.shape[0] + dr)
            c0, c1 = max(0, dc), min(W, b_mask.shape[1] + dc)
            if r1 <= r0 or c1 <= c0:
                continue
            sh[r0:r1, c0:c1] = b_mask[r0 - dr:r1 - dr, c0 - dc:c1 - dc]
            score = (sh & a_mask).sum() - 0.5 * (sh ^ a_mask).sum()
            if score > best:
                best, bs = score, (dr, dc)
    return bs


class SpriteTree:
    """A tree from a Sprite; [paint] another Sprite of the same art in another
    colourway, which paints this one's geometry. leaf_k / wood_k: Base shades a
    material; core: how far up the crown the hidden trunk goes; vines: hang the
    sprite's thin strands round the crown."""

    def __init__(self, sprite, paint=None, leaf_k=6, wood_k=3, core=0.55, groove=True, vines=False, vines_sprite=None):
        self.s = sprite
        self.rgb = sprite.rgb.astype(int)
        self.mask = sprite.mask.copy()
        self.H, self.W = self.mask.shape
        self.core, self.groove = core, groove
        self.cls_raw, self.lum = classify(self.rgb, self.mask)
        self.vines = []
        if vines:
            self._take_vines()
        if vines_sprite is not None:
            # another copy of this art that has hanging vines: its strands, moved onto this one
            other = SpriteTree(vines_sprite, vines=True)
            dr, dc = align(self.mask, other.mask)
            self.vines = [(c + dc, r0 + dr, r1 + dr) for (c, r0, r1) in other.vines
                          if 0 <= c + dc < self.W and 0 <= r0 + dr and r1 + dr <= self.H]
        self.cls = fill_lines(self.cls_raw)
        self.line = self.cls_raw == "line"
        # The colours: this sprite's, or the colourway's laid over it.
        prgb, pcls = self.rgb, self.cls_raw
        if paint is not None:
            dr, dc = align(self.mask, paint.mask)
            prgb = np.zeros_like(self.rgb)
            pmask = np.zeros_like(self.mask)
            H2, W2 = paint.mask.shape
            for r in range(self.H):
                for c in range(self.W):
                    rr, cc = r - dr, c - dc
                    if 0 <= rr < H2 and 0 <= cc < W2:
                        prgb[r, c] = paint.rgb[rr, cc]
                        pmask[r, c] = paint.mask[rr, cc]
            # Where the colourway's sprite has nothing (a pixel of shift), keep the geometry sprite's colour.
            prgb[~pmask] = self.rgb[~pmask]
            pcls, _ = classify(prgb, self.mask)
        self.prgb = prgb
        hh, ss, vv = hue_sat(prgb)
        sel = (pcls == "leaf") & (hh > 60) & (hh < 180) & self.mask
        leaf_px = prgb[sel & (ss > 0.3)]
        if len(leaf_px) < 30:
            leaf_px = prgb[sel & (ss > 0.15)]
        # Cartoon's three tones: saturated leaf colours at the 25th, 50th and 80th
        # percentiles of their lightness
        px = prgb[sel & (ss > 0.35)] if (sel & (ss > 0.35)).sum() >= 30 else leaf_px
        lum = px @ np.array([0.299, 0.587, 0.114])
        order = np.argsort(lum)
        def at(q):
            i = int(q * (len(order) - 1))
            win = px[order[max(0, i - 3):i + 4]]
            return tuple(int(v) for v in np.median(win, axis=0))
        self.bands = (at(0.82), at(0.5), at(0.22)) if len(px) else None
        wood_px = prgb[(pcls == "wood") & self.mask]
        self.leaf_pal = quantize(leaf_px, leaf_k) if len(leaf_px) else np.array([[70, 140, 70]])
        self.wood_pal = quantize(wood_px, wood_k) if len(wood_px) else np.array([[100, 70, 40]])
        # The axis: a real trunk's middle (wood two or more wide in the lowest rows,
        # standing in the middle of the silhouette), else the silhouette's middle.
        sil = np.nonzero(self.mask.any(axis=0))[0]
        mid = (sil.min() + sil.max() + 1) / 2.0
        half = (sil.max() + 1 - sil.min()) / 2.0
        cols = []
        for r in range(self.H - 1, max(-1, self.H - 8), -1):
            c = np.nonzero(self.cls[r] == "wood")[0]
            if len(c) >= 2:
                centre = (c.min() + c.max() + 1) / 2.0
                if abs(centre - mid) <= 0.3 * half:
                    cols.append(centre)
        self.cx = float(np.median(cols)) if len(cols) >= 2 else mid
        leaf_rows = np.nonzero((self.cls == "leaf").any(axis=1))[0]
        self.crown_top, self.crown_bottom = int(leaf_rows.min()), int(leaf_rows.max())
        trunk_w = []
        for r in range(self.crown_bottom - 1, self.H):
            c = np.nonzero(self.cls[r] == "wood")[0]
            if len(c):
                trunk_w.append(c.max() - c.min() + 1)
        self.trunk_r = max(1.0, (min(trunk_w) if trunk_w else 2) / 2.0)

    # ------------------------------------------------------------------ vines
    def _take_vines(self):
        """Finds the thin hanging strands (leaf or line pixels in horizontal runs of
        at most two, in vertical runs of four or more, below the crown's widest
        row), records them and takes them out of the silhouette."""
        m = self.mask & np.isin(self.cls_raw, ["leaf", "line"])
        widest = int(np.argmax(m.sum(axis=1)))
        thin = np.zeros_like(m)
        for r in range(widest, self.H):
            c = 0
            while c < self.W:
                if m[r, c]:
                    e = c
                    while e < self.W and m[r, e]:
                        e += 1
                    if e - c <= 2:
                        thin[r, c:e] = True
                    c = e
                else:
                    c += 1
        for c in range(self.W):
            r = widest
            while r < self.H:
                if thin[r, c]:
                    e = r
                    while e < self.H and thin[e, c]:
                        e += 1
                    if e - r >= 4:
                        self.vines.append((c, r, e))
                        self.mask[r:e, c] = False
                    r = e
                else:
                    r += 1

    # ------------------------------------------------------------------ geometry
    def _inside(self, mask, r, u, cx):
        col = int(math.floor(cx + u))
        return 0 <= col < mask.shape[1] and bool(mask[r, col])

    def _hull(self, mask, cx, size, symmetric=False):
        """The tree's voxels, a horizontal slice for each row of the sprite. A run of
        the row that reaches the axis is a round slice centred where the run is
        drawn (on the axis, for Cartoon), as wide as the run; a run of leaf off the
        axis is a clump, drawn where it is and turned to the front and back (Cartoon:
        to all four sides); wood off the trunk is a branch, a bar along the side it
        goes (Cartoon: all four). A clump left apart from the rest is joined to it by
        a branch. Sets self.hull_wood: the voxels that are wood whatever the sprite."""
        C = size / 2.0
        H = mask.shape[0]
        tr = self.trunk_r
        vox, wood = set(), set()
        for r in range(H):
            z = H - 1 - r
            discs, bars = [], []     # (mx, my, radius, wood), (u0, u1, side)
            for a, b in _runs(mask[r]):
                u0, u1 = a - cx, b - cx
                mid, rad = (u0 + u1) / 2.0, (u1 - u0) / 2.0
                woody = np.count_nonzero(self.cls[r, a:b] == "wood") / float(b - a) > 0.6
                if u0 <= 1.0 and u1 >= -1.0:
                    if woody and rad > tr + 1.5:
                        # the trunk, with a branch out of it each way it goes
                        discs.append((0.0, 0.0, tr, True))
                        if u1 > tr + 1:
                            bars.append((tr, u1))
                        if u0 < -tr - 1:
                            bars.append((u0, -tr))
                    else:
                        discs.append((0.0 if symmetric else mid, 0.0, rad, woody))
                elif woody:
                    bars.append((u0, u1))
                else:
                    discs.append((mid, 0.0, rad, False))
            placed = []
            for (mx, my, rad, w) in discs:
                if abs(mx) <= rad:                      # a slice round the axis
                    placed.append((mx, my, rad, w))
                    continue
                d = abs(mx)
                spots = [(mx, 0.0), (0.0, d), (0.0, -d)] + ([(-mx, 0.0)] if symmetric else [])
                placed += [(sx, sy, rad, w) for sx, sy in spots]
            lines = []                                 # (along x?, from, to)
            for (u0, u1) in bars:
                lo, hi = min(abs(u0), abs(u1)), max(abs(u0), abs(u1))
                sgn = 1.0 if u0 + u1 > 0 else -1.0
                lines.append((True, sgn * lo, sgn * hi))
                lines += [(False, lo, hi), (False, -hi, -lo)]
                if symmetric:
                    lines.append((True, -sgn * hi, -sgn * lo))
            for x in range(size):
                for y in range(size):
                    dx, dy = x + 0.5 - C, y + 0.5 - C
                    for (mx, my, rad, w) in placed:
                        if (dx - mx) ** 2 + (dy - my) ** 2 <= (rad + 0.25) ** 2:
                            vox.add((x, y, z))
                            if w:
                                wood.add((x, y, z))
                            break
                    else:
                        for (along_x, a, b) in lines:
                            u, v = (dx, dy) if along_x else (dy, dx)
                            if min(a, b) - 0.5 <= u <= max(a, b) + 0.5 and abs(v) <= 1.0:
                                vox.add((x, y, z))
                                wood.add((x, y, z))
                                break
        self.hull_wood = wood | self._attach(vox, size)
        return vox

    def _attach(self, vox, size):
        """Joins each part of [vox] apart from the largest to it by a bar of wood two
        voxels thick, run level from a third of the way up the part towards the axis.
        Adds the bar's voxels to [vox]; returns them."""
        C = size / 2.0
        added = set()
        for _ in range(6):
            parts = _components(vox)
            if len(parts) <= 1:
                break
            main = parts[0]
            for part in parts[1:]:
                if len(part) < 4:
                    continue
                zs = sorted(p[2] for p in part)
                z = zs[len(zs) // 3]
                ring = [p for p in part if p[2] == z]
                mx = sum(p[0] + 0.5 for p in ring) / len(ring) - C
                my = sum(p[1] + 0.5 for p in ring) / len(ring) - C
                d = math.hypot(mx, my)
                if d < 0.5:
                    continue
                steps = int(math.ceil(d * 2)) + 2
                for i in range(steps + 1):
                    t = 1.0 - i / float(steps)
                    px, py = C + mx * t, C + my * t
                    hit = False
                    for ox in (-0.5, 0.5):
                        for oy in (-0.5, 0.5):
                            q = (int(math.floor(px + ox)), int(math.floor(py + oy)), z)
                            if not (0 <= q[0] < size and 0 <= q[1] < size):
                                continue
                            if q in main:
                                hit = True
                            elif q not in vox:
                                vox.add(q)
                                added.add(q)
                    if hit:
                        break
        return added

    def _view(self, dx, dy):
        best, bk = -9, 0
        for k, p in enumerate(PHIS):
            f = dx * math.sin(p) - dy * math.cos(p)
            if f > best:
                best, bk = f, k
        p = PHIS[bk]
        return dx * math.cos(p) + dy * math.sin(p), bk

    def size(self):
        c = np.nonzero(self.mask.any(axis=0) | np.isin(np.arange(self.W), [v[0] for v in self.vines]))[0]
        half = max(self.cx - c.min(), c.max() + 1 - self.cx)
        n = int(math.ceil(2 * half)) + 2
        return n + (n % 2)

    def _sample(self, rgb, r, u):
        col = min(max(int(math.floor(self.cx + u)), 0), self.W - 1)
        if self.mask[r, col]:
            return rgb[r, col]
        cs = np.nonzero(self.mask[r])[0]
        if len(cs):
            return rgb[r, cs[np.argmin(np.abs(cs - col))]]
        return rgb[r, col]

    def _material(self, r, dx, dy, d):
        reach = self.crown_bottom - (self.crown_bottom - self.crown_top) * self.core
        if d <= self.trunk_r + 0.3 and r >= reach:
            return "wood"
        u, k = self._view(dx, dy)
        col = min(max(int(math.floor(self.cx + u)), 0), self.W - 1)
        c = self.cls[r, col]
        if c == "wood":
            return "wood"
        if c is None:
            row = [v for v in self.cls[r] if v in ("leaf", "wood")]
            return "wood" if row and row.count("wood") > row.count("leaf") else "leaf"
        return "leaf"

    def base(self):
        """({(x, y, z): (material, rgb)}, canvas size)."""
        n = self.size()
        C = n / 2.0
        H = self.H
        vox = self._hull(self.mask, self.cx, n)
        hull_wood = self.hull_wood

        def open_side(p, s):
            x, y, z = p
            return any(q not in s for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1)))

        carve = set()
        if self.groove:
            for p in vox:
                if not open_side(p, vox):
                    continue
                x, y, z = p
                r = H - 1 - z
                dx, dy = x + 0.5 - C, y + 0.5 - C
                u, k = self._view(dx, dy)
                col = min(max(int(math.floor(self.cx + u)), 0), self.W - 1)
                if self.line[r, col] and self.cls[r, col] == "leaf":
                    carve.add(p)
        keep = vox - carve
        leaf_mid = tuple(int(v) for v in sorted(self.leaf_pal.tolist(), key=sum)[len(self.leaf_pal) // 2])
        wood_mid = tuple(int(v) for v in sorted(self.wood_pal.tolist(), key=sum)[len(self.wood_pal) // 2])
        out = {}
        for p in keep:
            x, y, z = p
            r = H - 1 - z
            dx, dy = x + 0.5 - C, y + 0.5 - C
            mat = "wood" if p in hull_wood else self._material(r, dx, dy, math.hypot(dx, dy))
            if any(q not in keep for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1),
                                          (x, y, z - 1))):
                u, k = self._view(dx, dy)
                rgb = self._sample(self.prgb, r, u)
                pal = self.leaf_pal if mat == "leaf" else self.wood_pal
                out[p] = (mat, tuple(int(v) for v in nearest(rgb, pal)))
            else:
                out[p] = (mat, leaf_mid if mat == "leaf" else wood_mid)
        self._hang_vines(out, n, cartoon=False)
        return connected_main(out), (n, n, H)

    def _hang_vines(self, out, n, cartoon, crown=None):
        """Hangs each strand at its distance from the axis on the four sides, on the
        crown's rim at its top row, and runs it up into the crown so it is attached."""
        if not self.vines:
            return
        C = n / 2.0
        H = self.H
        pal = sorted([tuple(int(v) for v in c) for c in self.leaf_pal.tolist()], key=sum)
        for (c, r0, r1) in self.vines:
            u = c + 0.5 - self.cx
            # the crown's reach at the strand's top
            rr = r0 - 1
            while rr > 0 and not self.mask[rr].any():
                rr -= 1
            cols = np.nonzero(self.mask[rr])[0]
            reach = max(self.cx - cols.min(), cols.max() + 1 - self.cx) if len(cols) else abs(u) + 1
            depth = math.sqrt(max(0.0, reach * reach - u * u)) * 0.85
            for q in range(4):
                a = q * math.pi / 2
                # the strand's place on the side facing direction a: u across, depth out
                fx, fy = math.sin(a), -math.cos(a)
                rx, ry = math.cos(a), math.sin(a)
                px = C + u * rx + depth * fx
                py = C + u * ry + depth * fy
                x, y = int(math.floor(px)), int(math.floor(py))
                if not (0 <= x < n and 0 <= y < n):
                    continue
                for r in range(r0, r1):
                    z = H - 1 - r
                    rgb = tuple(int(v) for v in nearest(self.prgb[r, c], self.leaf_pal)) if not cartoon else pal[max(0, len(pal) // 4)]
                    out[(x, y, z)] = ("leaf", rgb)
                # up into the crown until it meets it
                body = out if crown is None else crown
                z = H - r0
                while z < H and (x, y, z) not in body:
                    out[(x, y, z)] = ("leaf", pal[max(0, len(pal) // 4)])
                    z += 1

    # ------------------------------------------------------------------ cartoon
    def cartoon(self):
        """The Cartoon tree: Base's own shape (uncut) made exactly symmetric under
        quarter turns from one quarter of it, its small notches filled, shallow
        lobes cut round each tier's foot, and painted in broad bands."""
        n = self.size()
        C = n / 2.0
        H = self.H
        vox = self._hull(self.mask, self.cx, n, symmetric=True)
        hull_wood = self.hull_wood
        half = n // 2
        quarter = {(x, y, z) for (x, y, z) in vox if x >= half and y >= half}
        sym = set()
        for (x, y, z) in quarter:
            for xx, yy in ((x, y), (n - 1 - y, x), (n - 1 - x, n - 1 - y), (y, n - 1 - x)):
                sym.add((xx, yy, z))
        # fill notches: empty voxels with four or more solid face-neighbours, twice
        for _ in range(2):
            add = set()
            xs = range(n)
            for z in range(H):
                for x in xs:
                    for y in xs:
                        if (x, y, z) in sym:
                            continue
                        k = sum(q in sym for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z),
                                                   (x, y, z + 1), (x, y, z - 1)))
                        if k >= 4:
                            add.add((x, y, z))
            sym |= add
        tiers = self._tiers()
        pal = sorted([tuple(int(v) for v in c) for c in self.leaf_pal.tolist()], key=sum)
        if self.bands:
            light, mid, dark = self.bands
        else:
            light, mid, dark = pal[-2] if len(pal) >= 3 else pal[-1], pal[len(pal) // 2], pal[max(0, len(pal) // 2 - 1)]
        wood = sorted([tuple(int(v) for v in c) for c in self.wood_pal.tolist()], key=sum)[len(self.wood_pal) // 2]
        reach = self.crown_bottom - (self.crown_bottom - self.crown_top) * self.core
        out = {}
        for (x, y, z) in sym:
            if x < half or y < half:
                continue
            r = H - 1 - z
            dx, dy = x + 0.5 - C, y + 0.5 - C
            d = math.hypot(dx, dy)
            if r > self.crown_bottom or (d <= self.trunk_r + 0.3 and r >= reach) or (x, y, z) in hull_wood:
                out[(x, y, z)] = ("wood", wood)
                continue
            t = tiers[r]
            ang = math.atan2(dy, dx)
            outer = not all(q in sym for q in ((x + 1, y, z), (x, y + 1, z), (x + 2, y, z), (x, y + 2, z)))
            if t > 0.6 and math.cos(8 * ang) > 0.93 and d > 2.5 and outer:
                continue
            out[(x, y, z)] = ("leaf", light if t < 0.34 else (mid if t < 0.72 else dark))
        full = {}
        for (x, y, z), v in out.items():
            for xx, yy in ((x, y), (n - 1 - y, x), (n - 1 - x, n - 1 - y), (y, n - 1 - x)):
                full[(xx, yy, z)] = v
        if self.vines:
            use_left = True
            keep = [(c, r0, r1) for (c, r0, r1) in self.vines if (c + 0.5 - self.cx) < 0]
            saved, self.vines = self.vines, []
            for (c, r0, r1) in keep:
                u = abs(c + 0.5 - self.cx)
                self.vines.append((int(math.floor(self.cx - u)), r0, r1))
            vfull = {}
            self._hang_vines(vfull, n, cartoon=True, crown=full)
            self.vines = saved
            # vines in the quarter, turned to the others
            for (x, y, z), v in vfull.items():
                if (x, y, z) in full:
                    continue
                for xx, yy in ((x, y), (n - 1 - y, x), (n - 1 - x, n - 1 - y), (y, n - 1 - x)):
                    full.setdefault((xx, yy, z), v)
        return connected_main(full), (n, n, H)

    def _edge(self, m, cx, r, d):
        col = int(math.floor(cx + d + 2))
        return col >= m.shape[1] or not m[r, col]

    def _tiers(self):
        line_share = []
        for r in range(self.H):
            leafy = (self.cls[r] == "leaf").sum()
            line_share.append((self.line[r] & (self.cls[r] == "leaf")).sum() / max(1, leafy))
        cuts = [self.crown_top]
        for r in range(self.crown_top + 4, self.crown_bottom - 2):
            if line_share[r] > 0.33 and line_share[r] >= max(line_share[r - 1], line_share[r + 1]) and r - cuts[-1] >= 5:
                cuts.append(r)
        cuts.append(self.crown_bottom + 1)
        t = [0.5] * self.H
        for a, b in zip(cuts, cuts[1:]):
            for r in range(a, b):
                t[r] = (r - a) / max(1.0, (b - a - 1))
        return t


def _close(m):
    d = m.copy()
    d[:, 1:] |= m[:, :-1]
    d[:, :-1] |= m[:, 1:]
    e = d.copy()
    e[:, 1:] &= d[:, :-1]
    e[:, :-1] &= d[:, 1:]
    return e | m
