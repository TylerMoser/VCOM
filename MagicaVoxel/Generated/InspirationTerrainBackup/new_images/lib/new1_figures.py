"""new_1's four figures, as static voxel figures (the user's call, 2026-11-04: model
them; no rig, no animation): the hooded hero on the path, the yellow fairy floating
beside him, the green crested creature by the flowers and the crow on the roof.

Each is built of the round parts the image draws (heads, bodies, limbs, a hood, a
crest, feathers) at the scale that makes the hero as tall as the game's units (27
voxels, Characters/BaseCharacter.vox): 1.35 voxels a pixel of the image's art, the
same for all four, so they keep the sizes the image gives them against each other.
A figure faces the front (-y), the crow its right (+x), as drawn. Base: lit from the
upper left as drawn (a lighter shade where a part faces the light, a darker where
it faces away). Cartoon: flat colours, mirror-symmetric across the figure's middle, and a
little rounder or plainer in shape (the hero holds his staff upright in front of
him, so it stays one staff; the fairy rounder with bigger wings, the creature's
crest an even arch and its feathers plumper, the crow rounder with a longer beak).

The fairy floats about 6 voxels over the ground in the image (its shadow below
it); like every model here its lowest voxel is at z 0, so it is lifted when placed.
Its sparkles (the yellow triangles over it) are an effect, not modelled.
"""
import math

LIGHT = (-0.55, -0.38, 0.74)


def _unit(v):
    m = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / m for c in v)


L = _unit(LIGHT)


class Fig:
    """A canvas of (nx, ny, nz), its middle at (nx / 2, ny / 2) on z 0; parts are
    placed in voxels from there."""

    def __init__(self, nx, ny, nz, cartoon):
        self.nx, self.ny, self.nz = nx, ny, nz
        self.cx, self.cy = nx / 2.0, ny / 2.0
        self.cartoon = cartoon
        self.out = {}

    def _cells(self, lo, hi):
        x0 = max(0, int(math.floor(self.cx + lo[0])) - 1)
        x1 = min(self.nx, int(math.ceil(self.cx + hi[0])) + 1)
        y0 = max(0, int(math.floor(self.cy + lo[1])) - 1)
        y1 = min(self.ny, int(math.ceil(self.cy + hi[1])) + 1)
        z0 = max(0, int(math.floor(lo[2])) - 1)
        z1 = min(self.nz, int(math.ceil(hi[2])) + 1)
        for x in range(x0, x1):
            for y in range(y0, y1):
                for z in range(z0, z1):
                    yield x, y, z, (x + 0.5 - self.cx, y + 0.5 - self.cy, z + 0.5)

    def paint(self, mat, cols, n):
        """A part's colour where its surface faces n: (base, light, dark) or one colour."""
        if not isinstance(cols[0], tuple):
            return (mat, cols)
        base, light, dark = cols
        if self.cartoon:
            return (mat, base)
        d = n[0] * L[0] + n[1] * L[1] + n[2] * L[2]
        return (mat, light if d > 0.55 else (dark if d < -0.3 else base))

    def ellipsoid(self, c, r, mat, cols, keep=None, shell=None):
        """An ellipsoid at c, radii r; keep(dx, dy, dz) limits it; shell: only its
        outer [shell] voxels (a hood over a head)."""
        lo = tuple(c[i] - r[i] for i in range(3))
        hi = tuple(c[i] + r[i] for i in range(3))
        for x, y, z, p in self._cells(lo, hi):
            q = [(p[i] - c[i]) / r[i] for i in range(3)]
            e = q[0] * q[0] + q[1] * q[1] + q[2] * q[2]
            if e > 1.0:
                continue
            if shell is not None:
                inner = [(p[i] - c[i]) / max(0.5, r[i] - shell) for i in range(3)]
                if inner[0] ** 2 + inner[1] ** 2 + inner[2] ** 2 < 1.0:
                    continue
            if keep is not None and not keep(*p):
                continue
            n = _unit(tuple(q[i] / r[i] for i in range(3)))
            self.out[(x, y, z)] = self.paint(mat, cols, n)

    def capsule(self, a, b, r, mat, cols):
        """A rounded rod from a to b, radius r."""
        lo = tuple(min(a[i], b[i]) - r for i in range(3))
        hi = tuple(max(a[i], b[i]) + r for i in range(3))
        ab = tuple(b[i] - a[i] for i in range(3))
        ll = sum(v * v for v in ab) or 1e-9
        for x, y, z, p in self._cells(lo, hi):
            t = max(0.0, min(1.0, sum((p[i] - a[i]) * ab[i] for i in range(3)) / ll))
            q = tuple(p[i] - (a[i] + ab[i] * t) for i in range(3))
            if sum(v * v for v in q) <= r * r:
                self.out[(x, y, z)] = self.paint(mat, cols, _unit(q))

    def frustum(self, c, z0, z1, r0, r1, mat, cols):
        """An upright tapering oval column from z0 (radii r0) to z1 (radii r1)."""
        R = max(r0 + r1)
        for x, y, z, p in self._cells((c[0] - R, c[1] - R, z0), (c[0] + R, c[1] + R, z1)):
            if not (z0 <= p[2] <= z1):
                continue
            t = (p[2] - z0) / max(1e-6, z1 - z0)
            rx = r0[0] + (r1[0] - r0[0]) * t
            ry = r0[1] + (r1[1] - r0[1]) * t
            qx, qy = (p[0] - c[0]) / rx, (p[1] - c[1]) / ry
            if qx * qx + qy * qy <= 1.0:
                self.out[(x, y, z)] = self.paint(mat, cols, _unit((qx / rx, qy / ry, 0.25)))

    def recolour(self, pred, mat, col, surface_only=True):
        """Repaints the voxels pred(dx, dy, dz) picks (on the surface only, unless told)."""
        for (x, y, z), v in list(self.out.items()):
            p = (x + 0.5 - self.cx, y + 0.5 - self.cy, z + 0.5)
            if not pred(*p):
                continue
            if surface_only and all(q in self.out for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z),
                                                            (x, y - 1, z), (x, y, z + 1), (x, y, z - 1))):
                continue
            self.out[(x, y, z)] = (mat, col)

    def front(self, x, z, mat, col, depth=1):
        """Paints the frontmost voxel(s) of column (x, z), as a mark on the surface."""
        xi = int(math.floor(self.cx + x))
        zi = int(math.floor(z))
        for y in range(self.ny):
            if (xi, y, zi) in self.out:
                for k in range(depth):
                    if (xi, y + k, zi) in self.out:
                        self.out[(xi, y + k, zi)] = (mat, col)
                return

    def mirror_x(self):
        full = {}
        for (x, y, z), v in self.out.items():
            if x >= self.nx // 2:
                full[(x, y, z)] = v
                full[(self.nx - 1 - x, y, z)] = v
        self.out = full

    def mirror_y(self):
        full = {}
        for (x, y, z), v in self.out.items():
            if y >= self.ny // 2:
                full[(x, y, z)] = v
                full[(x, self.ny - 1 - y, z)] = v
        self.out = full

    def done(self):
        from sculpt_tree import connected_main
        out = connected_main(self.out)
        z0 = min(z for (x, y, z) in out)
        out = {(x, y, z - z0): v for (x, y, z), v in out.items()}
        return out, (self.nx, self.ny, max(z for (x, y, z) in out) + 1)


# ---------------------------------------------------------------------- the hero
HERO = dict(hood=((65, 95, 110), (95, 130, 145), (44, 68, 82)), hood_rim=(38, 58, 70),
            hair=((240, 190, 40), (252, 222, 96), (205, 150, 30)), gem=(200, 60, 40),
            skin=((240, 180, 150), (250, 205, 175), (215, 150, 120)), eye=(25, 22, 30),
            scarf=((55, 80, 85), (75, 104, 110), (38, 58, 62)),
            sleeve=((238, 238, 242), (252, 252, 255), (200, 204, 214)),
            tunic=((230, 110, 200), (245, 150, 222), (180, 72, 160)), pouch=(240, 240, 246),
            boot=((150, 90, 60), (176, 112, 76), (104, 62, 42)),
            gold=((240, 172, 32), (252, 210, 80), (196, 128, 24)), tip=(96, 196, 116))


def hero(cartoon=False):
    """The hooded hero: a big rounded slate hood with a point, its opening framed by
    golden hair, a red gem on the brow, a round face with two dark eyes; a slate
    scarf, white sleeves, a pink tunic with a white pouch, brown boots; a golden
    staff with a curled head and a green tip in his right hand. 27 tall."""
    h = HERO
    f = Fig(20, 16, 28, cartoon)
    # boots, tunic, scarf
    for sx in (-2.3, 2.3):
        f.ellipsoid((sx, -0.5, 1.2), (1.9, 2.5, 1.3), "boot", h["boot"])
    f.frustum((0.0, 0.0), 1.6, 7.4, (5.0, 4.2), (4.0, 3.4), "tunic", h["tunic"])
    f.recolour(lambda x, y, z: abs(x) < 1.2 and y < -2.5 and 3.6 < z < 5.6, "white", h["pouch"])
    f.ellipsoid((0.0, 0.0, 8.3), (4.5, 3.9, 1.5), "hood", h["scarf"])
    # arms: white sleeves down to the hands
    for sx in (-1.0, 1.0):
        if cartoon:
            f.capsule((sx * 4.3, -0.2, 8.6), (sx * 2.2, -3.6, 5.6), 1.45, "white", h["sleeve"])
            f.ellipsoid((sx * 1.5, -4.2, 5.4), (1.3, 1.3, 1.3), "skin", h["skin"])
        else:
            f.capsule((sx * 4.4, 0.0, 8.6), (sx * 5.3, -0.8, 4.9), 1.45, "white", h["sleeve"])
            f.ellipsoid((sx * 5.4, -1.0, 4.2), (1.3, 1.3, 1.3), "skin", h["skin"])
    # the head, its face, the hood over it
    f.ellipsoid((0.0, 0.0, 15.6), (6.4, 6.0, 6.4), "skin", h["skin"])
    opening = lambda x, y, z: y < -2.4 and 9.6 < z < 18.4 and abs(x) < 5.5 - max(0.0, z - 15.6) * 0.55
    f.ellipsoid((0.0, 0.4, 16.2), (8.0, 7.4, 8.2), "hood", h["hood"], keep=lambda x, y, z: not opening(x, y, z),
                shell=1.8)
    for k in range(4):
        f.frustum((0.0, 0.6), 23.8 + k * 0.8, 24.6 + k * 0.8, (2.4 - 0.55 * k, 2.2 - 0.5 * k),
                  (2.4 - 0.55 * (k + 1), 2.2 - 0.5 * (k + 1)), "hood", h["hood"])
    # the hood's rim round its opening darker, golden hair inside it
    rim = lambda x, y, z: y < -1.6 and 9.6 < z < 18.6 and opening(x, y + 0.9, z) and not opening(x, y - 0.0, z - 0.0) \
        if False else False
    f.recolour(lambda x, y, z: y < -2.0 and 9.0 < z < 18.6 and not opening(x, y, z) and
               (opening(x * 0.84, y, z) or opening(x, y, z - 0.9)), "hood", h["hood_rim"])
    f.recolour(lambda x, y, z: opening(x, y, z) and (z > 15.4 or abs(x) > 3.3), "gold", h["hair"][0])
    if not cartoon:
        f.recolour(lambda x, y, z: opening(x, y, z) and z > 16.4 and x < -1.0, "gold", h["hair"][1])
    f.recolour(lambda x, y, z: abs(x) < 0.8 and y < -4.5 and 16.0 < z < 17.4, "red", h["gem"])
    for ex in (-1.9, 1.9):
        for ez in (13.2, 14.2):
            f.front(ex, ez, "black", h["eye"])
    # the staff, in his right hand (the left as seen); Cartoon: upright in front of him
    sx, sy = (0.0, -5.6) if cartoon else (-6.6, -1.6)
    f.capsule((sx, sy, 0.6), (sx, sy, 16.0), 0.62, "gold", h["gold"])
    # its head: a ring and a curl
    for i in range(40):
        a = 2 * math.pi * i / 40
        p = (sx + 1.5 * math.cos(a) * (0.0 if cartoon else 1.0), sy + (1.5 * math.cos(a) if cartoon else 0.0),
             17.6 + 1.5 * math.sin(a))
        f.capsule(p, p, 0.62, "gold", h["gold"])
    f.capsule((sx, sy, 0.0), (sx, sy, 1.2), 0.75, "gold", h["tip"])
    if cartoon:
        f.mirror_x()
    return f.done()


# ------------------------------------------------------------------ the creature
CREATURE = dict(skin=((84, 190, 72), (140, 224, 108), (44, 124, 62)), claw=(244, 244, 248),
                belly=((242, 242, 250), (255, 255, 255), (198, 204, 230)), chest=(230, 72, 84),
                cape=((150, 62, 162), (182, 96, 196), (106, 40, 120)),
                scarf=((222, 82, 40), (246, 128, 66), (176, 56, 30)),
                crest=((230, 92, 40), (248, 142, 64), (182, 62, 30)),
                eye=(250, 250, 252), pupil=(20, 20, 26), feather_y=((242, 202, 62), (252, 228, 120), (200, 150, 40)),
                feather_b=((62, 92, 204), (100, 130, 230), (40, 60, 150)))


def creature(cartoon=False):
    """The green crested creature: a round green head with a big orange crest on
    top, three feathers each side (yellow, blue, yellow) like a headdress, round
    white eyes; an orange scarf and a purple cape round its shoulders, a red band
    over its white belly, green arms and feet with white claws. 38 tall."""
    c = CREATURE
    f = Fig(28, 20, 40, cartoon)
    for sx in (-3.6, 3.6):
        f.ellipsoid((sx, -0.6, 1.4), (2.7, 3.4, 1.5), "scale", c["skin"])
        f.capsule((sx * 0.95, 0.2, 1.5), (sx * 0.95, 0.2, 5.0), 2.0, "scale", c["skin"])
        for k in (-1.0, 0.0, 1.0):
            f.capsule((sx + k * 1.2, -3.9, 0.6), (sx + k * 1.2, -4.3, 0.6), 0.55, "white", c["claw"])
    f.ellipsoid((0.0, 0.4, 10.6), (7.0, 6.0, 7.6), "scale", c["skin"])
    f.recolour(lambda x, y, z: y < -1.5 and 3.0 < z < 13.4 and (x / 4.8) ** 2 + ((z - 8.2) / 5.4) ** 2 < 1.0,
               "white", c["belly"][0] if cartoon else c["belly"][0])
    if not cartoon:
        f.recolour(lambda x, y, z: y < -1.5 and 3.0 < z < 6.0 and (x / 4.8) ** 2 + ((z - 8.2) / 5.4) ** 2 < 1.0,
                   "white", c["belly"][2])
    f.recolour(lambda x, y, z: y < -1.0 and 13.2 < z < 15.4 and abs(x) < 5.6, "red", c["chest"])
    # the cape round its shoulders and down its back, the scarf over it
    f.ellipsoid((0.0, 0.8, 15.6), (8.0, 7.0, 3.0), "purple", c["cape"], keep=lambda x, y, z: y > -3.2)
    f.frustum((0.0, 2.4), 8.0, 15.0, (6.8, 4.6), (7.6, 5.4), "purple", c["cape"])
    f.out = {p: v for p, v in f.out.items()
             if not (v[0] == "purple" and (p[1] + 0.5 - f.cy) < 1.0 and p[2] < 14)}
    f.ellipsoid((0.0, -0.2, 18.4), (7.2, 6.4, 1.8), "orange", c["scarf"])
    # arms
    for sx in (-1.0, 1.0):
        f.capsule((sx * 6.8, -0.6, 15.0), (sx * 8.4, -2.2, 9.0), 1.8, "scale", c["skin"])
        for k in (-0.7, 0.7):
            f.capsule((sx * 8.4 + k, -3.6, 8.0), (sx * 8.4 + k, -4.1, 7.4), 0.55, "white", c["claw"])
    # the head
    f.ellipsoid((0.0, -0.4, 26.6), (8.6, 7.8, 8.0), "scale", c["skin"])
    for sx in (-1.0, 1.0):
        ex = sx * 4.4
        f.ellipsoid((ex, -6.4, 26.4), (2.1, 1.2, 2.1), "white", c["eye"])
        f.ellipsoid((ex + sx * 0.3, -7.3, 26.3), (1.0, 0.6, 1.1), "black", c["pupil"])
    # the crest: a fin along the top of its head, front to back, leaning back
    for i in range(60):
        t = i / 59.0
        yy = -4.8 + 10.0 * t
        top = 4.2 + 3.0 * math.sin(math.pi * min(1.0, t * 1.15))
        base_z = 26.6 + 8.0 * math.sqrt(max(0.0, 1.0 - ((yy + 0.4) / 7.8) ** 2)) - 1.0
        lean = 0.0 if cartoon else 0.8 * t       # Cartoon: an even arch standing straight up
        f.capsule((0.0, yy, base_z), (0.0, yy + lean, base_z + top), 1.5, "orange", c["crest"])
    # the feathers each side: yellow up and out, blue out, yellow out and down
    for sx in (-1.0, 1.0):
        for (z0, ang, mat, cols) in ((31.0, 0.85, "yellow", c["feather_y"]), (27.4, 0.12, "blue", c["feather_b"]),
                                     (23.8, -0.42, "yellow", c["feather_y"])):
            base = (sx * 7.2, 0.0, z0)
            ln, rad = (5.0, 1.55) if cartoon else (5.8, 1.25)     # Cartoon: plumper, shorter feathers
            tip = (sx * (7.2 + ln * math.cos(ang)), 0.6, z0 + ln * math.sin(ang))
            f.capsule(base, tip, rad, mat, cols)
    if cartoon:
        f.mirror_x()
    return f.done()


# ---------------------------------------------------------------------- the crow
CROW = dict(body=((48, 48, 54), (78, 78, 88), (30, 30, 36)), wing=((36, 36, 42), (60, 60, 70), (24, 24, 30)),
            crown=(96, 96, 108), beak=((250, 188, 58), (255, 220, 110), (220, 140, 30)), eye=(10, 10, 12),
            glint=(236, 236, 240), feet=(240, 112, 60))


def crow(cartoon=False):
    """The crow perched on the roof, facing its right (+x) as drawn: a round black
    body, its folded wings darker, a short tail, a round head with a grey sheen on
    its crown, a dark eye with a white glint, an orange-yellow beak and orange feet.
    Cartoon: mirrored across its middle (y)."""
    c = CROW
    f = Fig(22, 14, 19, cartoon)
    for sy in (-1.6, 1.6):
        f.capsule((0.6, sy, 0.4), (0.6, sy, 3.4), 0.6, "orange", c["feet"])
        f.capsule((0.6, sy, 0.4), (2.6, sy, 0.4), 0.55, "orange", c["feet"])
    f.ellipsoid((-0.6, 0.0, 8.0), (6.4, 4.8, 5.2) if cartoon else (6.8, 4.6, 4.8), "black", c["body"])
    for sy in (-1.0, 1.0):
        f.ellipsoid((-1.6, sy * 4.1, 8.4), (6.0, 1.4, 3.6), "black", c["wing"])
    for i in range(12):
        t = i / 11.0
        f.capsule((-6.0 - 4.2 * t, 0.0, 8.6 - 1.2 * t), (-6.0 - 4.2 * t, 0.0, 8.6 - 1.2 * t), 2.2 - 1.2 * t,
                  "black", c["wing"])
    f.ellipsoid((4.6, 0.0, 13.0), (4.4, 4.0, 4.4), "black", c["body"])
    if not cartoon:
        f.recolour(lambda x, y, z: z > 15.4 and 2.4 < x < 5.6, "black", c["crown"])
    for i in range(10):
        t = i / 9.0
        x = 8.2 + (3.8 if cartoon else 3.0) * t
        f.capsule((x, 0.0, 13.0 - 0.3 * t), (x, 0.0, 13.0 - 0.3 * t), 1.25 - 0.75 * t, "orange", c["beak"])
    for sy in (-1.0, 1.0):
        f.ellipsoid((6.4, sy * 3.5, 14.0), (0.8, 0.7, 0.9), "black", c["eye"])
        f.ellipsoid((6.9, sy * 3.4, 14.8), (0.45, 0.45, 0.45), "white", c["glint"])
    if cartoon:
        f.mirror_y()
    return f.done()


# ---------------------------------------------------------------------- the fairy
FAIRY = dict(body=((250, 206, 46), (255, 240, 150), (232, 156, 30)), eye=(24, 20, 16),
             wing=((226, 246, 242), (248, 255, 254), (176, 228, 222)), feet=(236, 160, 32))


def fairy(cartoon=False):
    """The fairy: a round glowing yellow body, lighter at its upper left, with two
    dark eyes, two small pale wings on its back and two tiny feet. Floats about 6
    voxels over the ground as drawn (lift it when placing it)."""
    c = FAIRY
    f = Fig(18, 14, 16, cartoon)
    f.ellipsoid((0.0, 0.0, 7.0), (6.0, 6.0, 6.0) if cartoon else (6.1, 5.6, 6.0), "yellow", c["body"])
    eyes = ((-2.0, 7.6), (2.0, 7.6)) if cartoon else ((-2.4, 7.8), (1.6, 7.2))
    for (ex, ez) in eyes:
        for k in (0.0, 1.0):
            f.front(ex, ez - k, "black", c["eye"])
    for sx in (-1.0, 1.0):
        if cartoon:                          # Cartoon: bigger wings, set higher
            f.ellipsoid((sx * 3.9, 4.2, 12.0), (3.8, 1.0, 2.7), "white", c["wing"])
        else:
            f.ellipsoid((sx * 3.6, 4.0, 11.4), (3.2, 0.9, 2.3), "white", c["wing"])
    for sx in (-1.8, 1.8):
        f.ellipsoid((sx, -0.8, 1.0), (1.0, 1.0, 0.9), "yellow", c["feet"])
    if cartoon:
        f.mirror_x()
    return f.done()
