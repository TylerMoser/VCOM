#!/usr/bin/env python3
"""Builds the basic shapes in this folder: one MagicaVoxel model each, 16 x 16 x 16
voxels, a block's size (the game imports blocks at Scale 0.0625, one cell to sixteen
voxels).

    python3 make_shapes.py              # every shape
    python3 make_shapes.py Ladder Rock  # only these (named as their files, no .vox)

Running it overwrites the files it writes, so a shape edited by hand in MagicaVoxel
is lost if it is built again: name only the ones to rebuild.

Every file takes its palette, materials, layers and render settings from
../LeafCluster1.vox, so the shapes share the colours of the art already drawn (the
Apollo palette, indices 193-254) and open in MagicaVoxel looking as the rest do. Its
one model sits where MagicaVoxel puts a new one (translation 0 0 8: centred, its
bottom on the ground), as BrightGrass1.vox's does.

MagicaVoxel's axes: x and y across, z up. The importer turns them into Godot's x, -z
and y, so a shape's +y side is Godot's -z (forward). Everything random is seeded per
shape, so a shape comes out the same every time it is built.
"""

import math
import os
import random
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "LeafCluster1.vox")
N = 16

# Palette indices (as XYZI stores them, from 1), each row dark to light.
GREY = (193, 194, 195, 196)           # cool greys to off-white
SLATE = (201, 202, 203, 204, 205, 206)  # near black to blue-grey
PURPLE = (209, 210, 211, 212, 213, 214)
RED = (217, 218, 219, 220, 221, 222)  # plum to orange
BROWN = (225, 226, 227, 228, 229, 230)  # dark brown to straw
TAN = (233, 234, 235, 236, 237, 238)  # dark earth to pale sand
GREEN = (241, 242, 243, 244, 245, 246)
BLUE = (249, 250, 251, 252, 253, 254)
WHITE = 248
BLACK = 240

# The grass block's own colours, so ground blocks sit beside it.
DIRT = TAN[2]
DIRT_DARK = TAN[1]
GRASS = GREEN[3]


# ----------------------------------------------------------------------------
# Noise, all of it seeded and most of it tiling every 16 voxels across, so a
# ground block's pattern runs on into the next one's.

def _hash(x, y, z, seed):
    h = (x * 374761393 + y * 668265263 + z * 1440662683 + seed * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def white(x, y, z, seed):
    """A different number in [0, 1] for every voxel."""
    return _hash(x, y, z, seed)


def _fade(t):
    return t * t * (3.0 - 2.0 * t)


def noise(x, y, z, size, seed, tile=True):
    """Smooth value noise in [0, 1], its bumps about `size` voxels across. With
    `tile` it repeats every 16 voxels along x and y (size must divide 16)."""
    fx, fy, fz = x / size, y / size, z / size
    ix, iy, iz = math.floor(fx), math.floor(fy), math.floor(fz)
    tx, ty, tz = _fade(fx - ix), _fade(fy - iy), _fade(fz - iz)
    period = max(1, round(N / size))

    def at(a, b, c):
        if tile:
            a %= period
            b %= period
        return _hash(a, b, c, seed)

    def lerp(a, b, t):
        return a + (b - a) * t

    x0 = lerp(at(ix, iy, iz), at(ix + 1, iy, iz), tx)
    x1 = lerp(at(ix, iy + 1, iz), at(ix + 1, iy + 1, iz), tx)
    x2 = lerp(at(ix, iy, iz + 1), at(ix + 1, iy, iz + 1), tx)
    x3 = lerp(at(ix, iy + 1, iz + 1), at(ix + 1, iy + 1, iz + 1), tx)
    return lerp(lerp(x0, x1, ty), lerp(x2, x3, ty), tz)


def cells(x, y, z, size, seed, tile_z=False):
    """Worley noise: the nearest and second nearest of a point jittered in each
    `size`-voxel cell (tiling every 16 along x and y, and z with tile_z), and the
    nearest's id. Stones, cobbles, chunks of rubble."""
    period = N // size
    cx, cy, cz = x // size, y // size, z // size
    best = [1e9, 1e9]
    owner = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                gx, gy, gz = cx + dx, cy + dy, cz + dz
                kx, ky = gx % period, gy % period
                kz = gz % period if tile_z else gz
                px = gx * size + _hash(kx, ky, kz, seed) * size
                py = gy * size + _hash(kx, ky, kz, seed + 1) * size
                pz = gz * size + _hash(kx, ky, kz, seed + 2) * size
                d = math.sqrt((x + 0.5 - px) ** 2 + (y + 0.5 - py) ** 2 + (z + 0.5 - pz) ** 2)
                if d < best[0]:
                    best = [d, best[0]]
                    owner = (kx, ky, kz)
                elif d < best[1]:
                    best[1] = d
    return best[0], best[1], owner


def pick(options, t):
    """One of `options` by a number in [0, 1]."""
    return options[min(int(t * len(options)), len(options) - 1)]


# ----------------------------------------------------------------------------
# A model and the few ways shapes are put into it.

class Model:
    def __init__(self):
        self.voxels = {}

    def inside(self, x, y, z):
        return 0 <= x < N and 0 <= y < N and 0 <= z < N

    def set(self, x, y, z, color):
        if self.inside(x, y, z):
            if color is None:
                self.voxels.pop((x, y, z), None)
            else:
                self.voxels[(x, y, z)] = color

    def get(self, x, y, z):
        return self.voxels.get((x, y, z))

    def box(self, x0, x1, y0, y1, z0, z1, color):
        """Fills x0..x1, y0..y1, z0..z1, inclusive; `color` may be a function of
        (x, y, z)."""
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    self.set(x, y, z, color(x, y, z) if callable(color) else color)

    def fill(self, test, color):
        """Sets every voxel where test(x, y, z) holds."""
        for x in range(N):
            for y in range(N):
                for z in range(N):
                    if test(x, y, z):
                        self.set(x, y, z, color(x, y, z) if callable(color) else color)

    def open_to(self, x, y, z, direction):
        dx, dy, dz = direction
        return self.get(x + dx, y + dy, z + dz) is None

    def exposed(self, x, y, z):
        """Whether the voxel has a face open to the air inside the model (faces
        on the model's bounds count as open)."""
        for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            if self.open_to(x, y, z, d):
                return True
        return False

    def top(self, x, y):
        """The highest voxel's z in a column, or -1."""
        for z in range(N - 1, -1, -1):
            if (x, y, z) in self.voxels:
                return z
        return -1

    def recolor(self, color):
        """Paints every voxel again by color(x, y, z, old)."""
        for key, old in list(self.voxels.items()):
            new = color(*key, old)
            if new is not None:
                self.voxels[key] = new


def all_cells():
    for x in range(N):
        for y in range(N):
            for z in range(N):
                yield x, y, z


def radius(x, y, cx=7.5, cy=7.5):
    return math.hypot(x + 0.5 - (cx + 0.5), y + 0.5 - (cy + 0.5))


def angle(x, y, cx=7.5, cy=7.5):
    return math.atan2(y - cy, x - cx)


def on_side(x, y):
    return x in (0, N - 1) or y in (0, N - 1)


# ----------------------------------------------------------------------------
# Ground: whole blocks, tiling with one another.

def dirt():
    m = Model()

    def color(x, y, z):
        n, r = noise(x, y, z, 4, 11), white(x, y, z, 12)
        if r < 0.05:
            return DIRT_DARK
        if r > 0.96:
            return TAN[3]
        return DIRT_DARK if n < 0.18 and r < 0.6 else DIRT
    m.box(0, 15, 0, 15, 0, 15, color)
    # A few pebbles and darker clods on top.
    for x in range(N):
        for y in range(N):
            r = white(x, y, 15, 13)
            if r < 0.02:
                m.set(x, y, 15, GREY[0])
            elif r < 0.1:
                m.set(x, y, 15, TAN[3])
    return m


def sand():
    m = Model()

    def ripple(x, y):
        # Diagonal ridges, warped, repeating every 16 voxels both ways.
        phase = 2.0 * math.pi * (2 * x + y) / N + 2.2 * noise(x, y, 0, 8, 21)
        return math.sin(phase)

    def color(x, y, z):
        r = white(x, y, z, 22)
        if r < 0.03:
            return TAN[3]
        if r > 0.93:
            return TAN[5]
        band = (z + 2.0 * noise(x, y, z, 4, 23)) // 3
        return TAN[3] if band % 4 == 0 and r < 0.35 else TAN[4]
    m.box(0, 15, 0, 15, 0, 15, color)
    for x in range(N):
        for y in range(N):
            s = ripple(x, y)
            if s < -0.55:
                m.set(x, y, 15, None)          # a trough
                m.set(x, y, 14, TAN[3])
            elif s > 0.6:
                m.set(x, y, 15, TAN[5])        # a crest, catching the light
    return m


def stone():
    m = Model()

    def color(x, y, z):
        n = noise(x, y, z, 4, 31)
        r = white(x, y, z, 33)
        if r < 0.03:
            return SLATE[5]
        if r < 0.1:
            return GREY[0]
        if r > 0.95:
            return GREY[2]
        return GREY[0] if n < 0.3 else GREY[1]
    m.box(0, 15, 0, 15, 0, 15, color)
    return m


def cobblestone():
    """Rounded stones set in dark mortar, through and through, standing a voxel
    proud of the mortar on top."""
    m = Model()
    shades = (GREY[1], GREY[1], GREY[2])
    gap = 0.6

    def color(x, y, z):
        d1, d2, owner = cells(x, y, z, 4, 41, tile_z=True)
        if d2 - d1 < gap:
            return SLATE[5] if z == 15 or white(x, y, z, 42) < 0.5 else GREY[0]
        base = pick(shades, _hash(*owner, 43))
        if d1 < 1.1 and z == 15:
            return GREY[GREY.index(base) + 1]
        return base
    m.box(0, 15, 0, 15, 0, 15, color)
    for x in range(N):
        for y in range(N):
            d1, d2, _ = cells(x, y, 15, 4, 41, tile_z=True)
            if d2 - d1 < gap:
                m.set(x, y, 15, None)
    return m


def fringed(top, seed, depth=2, drip=3):
    """A block of dirt under a layer of `top`, which hangs down its sides by up
    to `drip` voxels more, as the grass block's turf does."""
    m = dirt()
    for x, y, z in all_cells():
        hang = 0
        if on_side(x, y):
            hang = int(drip * noise(x, y, 0, 2, seed) + 0.5)
        if z >= N - depth - hang:
            m.set(x, y, z, top(x, y, z))
    return m


def snow():
    def top(x, y, z):
        r = white(x, y, z, 51)
        if r < 0.06:
            return WHITE
        if noise(x, y, z, 4, 52) < 0.3:
            return GREY[2]
        return GREY[3]
    return fringed(top, 53, depth=3, drip=3)


def mud():
    m = Model()

    def color(x, y, z):
        n, r = noise(x, y, z, 4, 61), white(x, y, z, 62)
        if r < 0.1:
            return TAN[0]
        return TAN[0] if n < 0.2 and r < 0.5 else TAN[1]
    m.box(0, 15, 0, 15, 0, 15, color)
    for x in range(N):
        for y in range(N):
            wet = noise(x, y, 0, 4, 63)
            if wet > 0.66:
                # A puddle, a voxel down, grey with the sky in it.
                m.set(x, y, 15, None)
                m.set(x, y, 14, GREY[0] if white(x, y, 14, 64) < 0.2 else SLATE[5])
            elif white(x, y, 15, 65) < 0.08:
                m.set(x, y, 15, BROWN[1])
    return m


def ash():
    m = Model()

    def color(x, y, z):
        n, r = noise(x, y, z, 4, 71), white(x, y, z, 72)
        if r < 0.05:
            return SLATE[5]
        return SLATE[3] if n < 0.45 else SLATE[4]
    m.box(0, 15, 0, 15, 0, 15, color)
    for x in range(N):
        for y in range(N):
            r = white(x, y, 15, 73)
            if r < 0.02:
                m.set(x, y, 15, RED[5])        # an ember
            elif r < 0.035:
                m.set(x, y, 15, RED[4])
            elif r < 0.12:
                m.set(x, y, 15, GREY[0])       # pale flakes
    return m


def liquid(depth_colors):
    """A pool block: 14 voxels deep, so its surface sits two below a ground
    block's top, darker the deeper it goes."""
    m = Model()
    for x, y, z in all_cells():
        if z <= 13:
            wave = 1.6 * (noise(x, y, z, 4, 85) - 0.5)
            band = int((z + wave) * len(depth_colors) / 13)
            m.set(x, y, z, depth_colors[max(0, min(band, len(depth_colors) - 1))])
    return m


def water():
    m = liquid((BLUE[1], BLUE[1], BLUE[2], BLUE[2], BLUE[3]))
    for x in range(N):
        for y in range(N):
            # Ripples: warped bands repeating every 16 voxels, glints between.
            phase = 2.0 * math.pi * (x + 2 * y) / N + 3.0 * noise(x, y, 0, 8, 82)
            s = math.sin(phase)
            c = BLUE[4]
            if s > 0.9:
                c = BLUE[5]
            if white(x, y, 13, 83) < 0.015:
                c = WHITE
            m.set(x, y, 13, c)
    return m


def lava():
    m = liquid((RED[2], RED[2], RED[3], RED[3], RED[4]))
    for x in range(N):
        for y in range(N):
            crust = noise(x, y, 0, 4, 92)
            heat = noise(x, y, 0, 2, 93)
            if crust > 0.64:
                m.set(x, y, 13, RED[1] if white(x, y, 13, 94) < 0.3 else SLATE[3])
            elif crust > 0.58:
                m.set(x, y, 13, BROWN[5])      # glowing at the crust's edge
            else:
                m.set(x, y, 13, BROWN[4] if heat > 0.6 else RED[5])
    return m


def ice():
    m = Model()
    rng = random.Random(101)

    def color(x, y, z):
        n, r = noise(x, y, z, 4, 102), white(x, y, z, 103)
        streak = (x + z + int(3 * noise(x, y, z, 8, 104))) % 9 == 0
        if streak:
            return GREY[3]
        if r < 0.04:
            return WHITE
        return BLUE[4] if n < 0.32 else BLUE[5]
    m.box(0, 15, 0, 15, 0, 15, color)
    # Frost on top.
    for x in range(N):
        for y in range(N):
            r = white(x, y, 15, 105)
            if r < 0.25:
                m.set(x, y, 15, GREY[3])
            elif r < 0.3:
                m.set(x, y, 15, WHITE)
    # A few cracks wandering over the top and down a side.
    for _ in range(3):
        x, y, z = rng.randrange(2, 14), rng.randrange(2, 14), 15
        dx, dy = rng.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
        for _ in range(rng.randrange(8, 14)):
            m.set(x, y, z, BLUE[3])
            if rng.random() < 0.35:
                dx, dy = rng.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
            nx, ny = x + dx, y + dy
            if 0 <= nx < N and 0 <= ny < N:
                x, y = nx, ny
            else:
                z -= 1                          # over the edge and down
                if z < 9:
                    break
    return m


def wood_planks():
    """A floor of planks along x, four voxels wide, their joints staggered."""
    m = Model()
    shades = (BROWN[2], BROWN[3], BROWN[3], BROWN[4])

    def color(x, y, z):
        row, layer = y // 4, z // 4
        joint = (row * 5 + layer * 3 + 3) % N
        if y % 4 == 3 or z % 4 == 0:
            return BROWN[1]                     # the gaps between planks
        if x == joint:
            return BROWN[1]
        tone = pick(shades, _hash(row, layer, 1 if x > joint else 0, 111))
        grain = white(x, y, z, 112)
        if grain < 0.12:
            return BROWN[2]
        return tone
    m.box(0, 15, 0, 15, 0, 15, color)
    # Nails either side of each joint, on top.
    for row in range(4):
        joint = (row * 5 + 3 * 3 + 3) % N
        for x in (joint - 1, joint + 1):
            if 0 <= x < N:
                m.set(x, row * 4 + 1, 15, SLATE[3])
    return m


# ----------------------------------------------------------------------------
# Walls: whole blocks, for buildings and ruins.

def masonry(stone_colors, mortar, seed, length=8, course=4, recess=True):
    """Bricks or dressed stones, `length` long and `course` high (mortar
    included), half a stone's offset from one course to the next, through the
    whole block. With `recess` the mortar on every face is a voxel in."""
    m = Model()

    def is_joint(x, y, z):
        c = z // course
        offset = (length // 2) * (c % 2)
        return z % course == 0 or (x + offset) % length == 0 or (y + offset) % length == 0

    def color(x, y, z):
        if is_joint(x, y, z):
            return mortar(x, y, z) if callable(mortar) else mortar
        c = z // course
        offset = (length // 2) * (c % 2)
        stone_id = ((x + offset) // length, (y + offset) // length, c)
        base = pick(stone_colors, _hash(*stone_id, seed))
        r = white(x, y, z, seed + 1)
        if r < 0.08:
            return stone_colors[0]
        return base
    m.box(0, 15, 0, 15, 0, 15, color)
    if recess:
        for x, y, z in all_cells():
            if is_joint(x, y, z) and (x in (0, 15) or y in (0, 15) or z == 15):
                m.set(x, y, z, None)
    return m


def stone_brick():
    return masonry((GREY[1], GREY[2], GREY[2], GREY[3]), GREY[0], 121)


def brick():
    return masonry((RED[2], RED[3], RED[3], RED[4]),
                   lambda x, y, z: TAN[4] if white(x, y, z, 131) > 0.2 else TAN[3], 132)


def wood_wall():
    """Horizontal boards round a frame of dark corner posts."""
    m = Model()
    shades = (BROWN[2], BROWN[3], BROWN[3])

    def color(x, y, z):
        corner = x in (0, 1, 14, 15) and y in (0, 1, 14, 15)
        if corner:
            return BROWN[1] if white(x, y, z, 141) > 0.15 else BROWN[0]
        if z % 4 == 0 or z == 15 and y % 4 == 0:
            return BROWN[1]
        tone = pick(shades, _hash(z // 4, y // 4 if z == 15 else 0, 0, 142))
        return BROWN[2] if white(x, y, z, 143) < 0.12 else tone
    m.box(0, 15, 0, 15, 0, 15, color)
    # Nail heads near the posts, two to a board.
    for z in range(2, N, 4):
        for a in (3, 12):
            for x, y in ((a, 0), (a, 15), (0, a), (15, a)):
                m.set(x, y, z, SLATE[3])
    return m


def ruined_wall():
    """A stone wall broken off unevenly, stones missing, moss on what is left."""
    m = stone_brick()
    # Whole stones come away: one is kept only while its course is below the
    # broken top where it lies (stones are 8 long, 4 high, staggered by 4), a
    # top falling away from one corner to the other, stone by stone.
    for x, y, z in all_cells():
        course = z // 4
        offset = 4 * (course % 2)
        sx, sy = ((x + offset) // 8) * 8 - offset + 4, ((y + offset) // 8) * 8 - offset + 4
        height = 3.0 + 13.0 * (sx + sy) / 32.0 + 7.0 * (_hash(sx, sy, course, 151) - 0.5)
        if 4 * course + 3 > height:
            m.set(x, y, z, None)
    # Knock a few stones out of the faces.
    rng = random.Random(152)
    for _ in range(5):
        side = rng.choice(("x0", "x15", "y0", "y15"))
        a, z = rng.randrange(1, 13), rng.randrange(1, 10)
        for da in range(rng.randrange(2, 4)):
            for dz in range(2):
                for depth in range(2):
                    if side == "x0":
                        m.set(depth, a + da, z + dz, None)
                    elif side == "x15":
                        m.set(15 - depth, a + da, z + dz, None)
                    elif side == "y0":
                        m.set(a + da, depth, z + dz, None)
                    else:
                        m.set(a + da, 15 - depth, z + dz, None)
    # Moss on the broken top, now and then hanging a voxel down.
    for x in range(N):
        for y in range(N):
            z = m.top(x, y)
            if z >= 0 and noise(x, y, 0, 2, 153) > 0.7:
                m.set(x, y, z, GREEN[3] if white(x, y, z, 154) < 0.6 else GREEN[2])
                if on_side(x, y) and white(x, y, z, 155) < 0.4:
                    m.set(x, y, z - 1, GREEN[2])
    return m


# ----------------------------------------------------------------------------
# Getting about.

def ladder():
    """Two rails and rungs against the model's +y side (Godot's -z), the whole
    height of the block, so ladders stack."""
    m = Model()
    for z in range(N):
        for x in (2, 3, 12, 13):
            for y in (14, 15):
                c = BROWN[2] if y == 14 else BROWN[1]
                if white(x, y, z, 161) < 0.1:
                    c = BROWN[1]
                m.set(x, y, z, c)
    for z in (2, 6, 10, 14):
        for x in range(4, 12):
            m.set(x, 14, z, BROWN[3] if white(x, 14, z, 162) > 0.15 else BROWN[4])
        for x in (3, 12):
            m.set(x, 14, z, SLATE[3])           # a nail where it meets the rail
    return m


def stone_stairs():
    """Four steps, each four voxels up and four along, rising toward +y
    (Godot's -z) to the block's full height."""
    m = Model()

    def color(x, y, z):
        step = y // 4
        tread = z == 4 * step + 3
        r = white(x, y, z, 171)
        # Each step is laid in blocks, their joints staggered step to step.
        joint = (x + 3 * step) % 6 == 0
        if tread:
            if joint and y % 4 != 0:
                return GREY[0]
            return GREY[3] if r < 0.15 else GREY[2]
        if joint or z % 4 == 0 and z // 4 < step:
            return GREY[0]
        return GREY[1] if r > 0.1 else GREY[0]
    m.fill(lambda x, y, z: z <= 4 * (y // 4) + 3, color)
    return m


def wood_stairs():
    """Open wooden stairs: treads and risers between two side boards, nothing
    under them, rising toward +y (Godot's -z)."""
    m = Model()
    for x, y, z in all_cells():
        step = y // 4
        line = 4 * step + 3                     # the tread's top
        if x in (0, 1, 14, 15):
            # The side boards (stringers), six voxels deep under the stair line.
            slope = (y + 1) - 0.5
            if z <= line and z >= slope - 6:
                m.set(x, y, z, BROWN[1] if x in (0, 15) else BROWN[2])
        elif z in (line, line - 1) and z >= 0:
            m.set(x, y, z, BROWN[4] if z == line and white(x, y, z, 181) > 0.2 else BROWN[3])
        elif y == 4 * step and z < line - 1 and z >= line - 3:
            m.set(x, y, z, BROWN[2])            # the riser
    # The bottom of each side board where it meets the ground.
    for x in (0, 1, 14, 15):
        for y in range(4):
            m.set(x, y, 0, BROWN[1])
    return m


# ----------------------------------------------------------------------------
# Fences: a split-rail fence through the middle of the block, a post at its
# centre and rails running out to the block's edges, so pieces join up.

EAST, WEST, NORTH, SOUTH = (1, 0), (-1, 0), (0, 1), (0, -1)


def fence(*sides):
    m = Model()
    # The post, 4 x 4 and 12 high, its top capped smaller.
    for x in range(6, 10):
        for y in range(6, 10):
            for z in range(12):
                edge = x in (6, 9) and y in (6, 9)
                m.set(x, y, z, BROWN[1] if edge or white(x, y, z, 191) < 0.1 else BROWN[2])
    m.box(7, 8, 7, 8, 12, 12, BROWN[3])
    # Two rails each way asked for, 2 x 2, the top face lighter.
    for dx, dy in sides:
        for z0 in (3, 8):
            for s in range(0, 8):
                for a in (7, 8):
                    for z in (z0, z0 + 1):
                        if dx:
                            x = 7 - s if dx < 0 else 8 + s
                            if 6 <= x <= 9:
                                continue
                            y = a
                        else:
                            y = 7 - s if dy < 0 else 8 + s
                            if 6 <= y <= 9:
                                continue
                            x = a
                        c = BROWN[4] if z == z0 + 1 else BROWN[3]
                        if white(x, y, z, 192) < 0.1:
                            c = BROWN[2]
                        m.set(x, y, z, c)
    return m


# ----------------------------------------------------------------------------
# Plants.

def bush():
    """A round, leafy bush, lumpy and holed at its surface, on a few stems."""
    m = Model()
    for x, y, z in all_cells():
        dx, dy, dz = (x - 7.5) / 7.0, (y - 7.5) / 7.0, (z - 6.0) / 6.5
        d = dx * dx + dy * dy + dz * dz
        lumpy = 1.0 + 0.45 * (noise(x, y, z, 4, 201, tile=False) - 0.5)
        if d <= lumpy and z >= 1:
            m.set(x, y, z, GREEN[2])
    # Holes in the surface, and colour by height: dark below, light on top.
    for (x, y, z) in list(m.voxels):
        if m.exposed(x, y, z) and white(x, y, z, 202) < 0.18:
            m.set(x, y, z, None)
    for (x, y, z) in list(m.voxels):
        r = white(x, y, z, 203)
        if z >= 10:
            c = GREEN[4] if r < 0.35 else GREEN[3]
        elif z >= 6:
            c = GREEN[3] if r < 0.6 else GREEN[2]
        else:
            c = GREEN[2] if r < 0.6 else GREEN[1]
        m.set(x, y, z, c)
    for x, y in ((7, 7), (8, 8), (7, 8)):
        m.set(x, y, 0, BROWN[1])
    return m


def hedge():
    """A clipped hedge running along x, edge to edge, so hedges join up."""
    m = Model()
    for x, y, z in all_cells():
        if 2 <= y <= 13 and z <= 12:
            depth = min(y - 2, 13 - y, 12 - z)
            if depth >= 1 or noise(x, y, z, 2, 211) > 0.38:
                r = white(x, y, z, 212)
                if z >= 11:
                    c = GREEN[4] if r < 0.4 else GREEN[3]
                else:
                    c = GREEN[3] if r < 0.45 else GREEN[2]
                if z <= 2 and r < 0.5:
                    c = GREEN[1]
                m.set(x, y, z, c)
    return m


def flowers():
    """Seven flowers, stems and leaves standing on the ground, in four colours."""
    m = Model()
    rng = random.Random(221)
    petals = (RED[4], PURPLE[5], GREY[3], BROWN[5], BLUE[4], PURPLE[4], RED[3])
    spots, tries = [], 0
    while len(spots) < 7 and tries < 500:
        tries += 1
        x, y = rng.randrange(2, 14), rng.randrange(2, 14)
        if all(abs(x - a) + abs(y - b) >= 5 for a, b in spots):
            spots.append((x, y))
    for i, (x, y) in enumerate(spots):
        height = rng.randrange(4, 9)
        for z in range(height):
            m.set(x, y, z, GREEN[2])
        # A leaf or two low on the stem.
        for _ in range(2):
            dx, dy = rng.choice((EAST, WEST, NORTH, SOUTH))
            z = rng.randrange(0, 3)
            m.set(x + dx, y + dy, z, GREEN[3])
            m.set(x + 2 * dx, y + 2 * dy, z + 1, GREEN[4])
        petal = petals[i % len(petals)]
        top = height
        m.set(x, y, top, BROWN[4] if petal != BROWN[5] else RED[4])
        for dx, dy in (EAST, WEST, NORTH, SOUTH):
            m.set(x + dx, y + dy, top, petal)
        if rng.random() < 0.5:
            m.set(x, y, top + 1, petal)         # a bud above the middle
    return m


def tall_grass():
    m = Model()
    rng = random.Random(231)
    for _ in range(46):
        x, y = rng.randrange(0, N), rng.randrange(0, N)
        height = rng.randrange(3, 10)
        dx, dy = rng.choice(((1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)))
        for z in range(height):
            bend = z * 2 // max(height, 1)       # leans a voxel over its last half
            c = GREEN[2] if z < height // 3 else (GREEN[3] if z < 2 * height // 3 else GREEN[4])
            m.set(x + dx * bend, y + dy * bend, z, c)
    return m


def fern():
    """Fronds arching out from the middle and drooping at their tips."""
    m = Model()
    rng = random.Random(241)
    count = 7
    for k in range(count):
        a = 2.0 * math.pi * k / count + rng.uniform(-0.25, 0.25)
        length = rng.uniform(6.0, 7.4)
        steps = int(length * 3)
        for i in range(steps + 1):
            t = length * i / steps
            x = 7.5 + math.cos(a) * t
            y = 7.5 + math.sin(a) * t
            z = 1.0 + 6.0 * math.sin(math.pi * 0.85 * t / length)
            vx, vy, vz = int(round(x - 0.5)), int(round(y - 0.5)), int(round(z - 0.5))
            m.set(vx, vy, vz, GREEN[1] if t < 1.5 else GREEN[2])
            # Leaflets either side, longer near the base.
            reach = 2 if t < length * 0.5 else 1
            if i % 3 == 0 and t > 1.5:
                for side in (-1, 1):
                    for s in range(1, reach + 1):
                        lx = x - math.sin(a) * side * s
                        ly = y + math.cos(a) * side * s
                        m.set(int(round(lx - 0.5)), int(round(ly - 0.5)), vz,
                              GREEN[3] if s == 1 else GREEN[4])
    m.box(7, 8, 7, 8, 0, 1, GREEN[1])
    return m


def reeds():
    """Cattails: tall stalks, most with a brown head, and leaf blades."""
    m = Model()
    rng = random.Random(252)
    spots = []
    while len(spots) < 9:
        x, y = rng.randrange(1, 15), rng.randrange(1, 15)
        if all(abs(x - a) + abs(y - b) >= 3 for a, b in spots):
            spots.append((x, y))
    for x, y in spots:
        height = rng.randrange(9, 15)
        for z in range(height):
            m.set(x, y, z, GREEN[2] if z < height // 2 else GREEN[3])
        if rng.random() < 0.7:
            for z in range(height - 4, height - 1):
                m.set(x, y, z, BROWN[1] if z != height - 2 else BROWN[2])
            m.set(x, y, height - 1, GREEN[3])
        # A leaf blade from the foot, curving out.
        dx, dy = rng.choice((EAST, WEST, NORTH, SOUTH))
        length = rng.randrange(5, 9)
        for z in range(length):
            out = z // 3
            m.set(x + dx * out, y + dy * out, z, GREEN[3] if z > 2 else GREEN[2])
    return m


def wheat():
    """Ripe wheat in rows along x, two stalks wide, repeating every 4 voxels
    across, so a field is blocks side by side."""
    m = Model()
    rng = random.Random(261)
    for x in range(N):
        for y in range(N):
            if y % 4 not in (1, 2) or rng.random() > 0.6:
                continue
            height = rng.randrange(9, 13)
            lean = rng.choice(((0, 0), (0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)))
            for z in range(height):
                c = GREEN[4] if z < 3 else BROWN[4]
                head = z >= height - 3
                if head:
                    c = BROWN[5] if (z + x) % 2 == 0 else BROWN[4]
                ox, oy = (lean if head else (0, 0))
                m.set(x + ox, y + oy, z, c)
    return m


def cactus():
    """A saguaro: a ribbed trunk with an arm either side, a flower on top."""
    m = Model()

    def column(x0, y0, z0, z1):
        for x in range(x0, x0 + 4):
            for y in range(y0, y0 + 4):
                if x in (x0, x0 + 3) and y in (y0, y0 + 3):
                    continue                    # rounded corners
                for z in range(z0, z1 + 1):
                    rib = (x - x0) in (1, 2) and (y - y0) in (0, 3) or (y - y0) in (1, 2) and (x - x0) in (0, 3)
                    c = GREEN[2] if rib and (x + y) % 2 == 0 else GREEN[3]
                    m.set(x, y, z, c)

    column(6, 6, 0, 14)
    # The east arm: out at 5, up to 11.
    m.box(10, 12, 7, 8, 5, 7, GREEN[3])
    column(11, 6, 5, 11)
    # The west arm: out at 8, up to 13.
    m.box(3, 5, 7, 8, 8, 10, GREEN[3])
    column(2, 6, 8, 13)
    # Spines here and there, and a flower.
    for (x, y, z), c in list(m.voxels.items()):
        if m.exposed(x, y, z) and white(x, y, z, 271) < 0.07:
            m.set(x, y, z, TAN[5])
    m.box(7, 8, 7, 8, 15, 15, PURPLE[5])
    return m


def mushrooms():
    """Three mushrooms: a red, white-spotted toadstool, a brown one, a small pale one."""
    m = Model()

    def cap(cx, cy, z0, radii, colors, spots=None, seed=0):
        for dz, r in enumerate(radii):
            for x in range(N):
                for y in range(N):
                    if radius(x, y, cx, cy) <= r:
                        c = colors[0] if dz < len(radii) - 1 else colors[1]
                        if spots and white(x, y, z0 + dz, seed) < 0.18:
                            c = spots
                        m.set(x, y, z0 + dz, c)

    # The toadstool.
    m.box(4, 5, 5, 6, 0, 4, TAN[5])
    cap(4.5, 5.5, 5, (3.6, 3.1, 2.0), (RED[3], RED[3]), GREY[3], 281)
    for x in range(N):
        for y in range(N):
            if 1.5 < radius(x, y, 4.5, 5.5) <= 3.6:
                m.set(x, y, 4, TAN[4])          # the gills underneath
    # The brown one.
    m.box(11, 11, 10, 10, 0, 2, TAN[5])
    cap(11, 10, 3, (2.3, 1.6), (BROWN[2], BROWN[3]))
    # The small pale one.
    m.box(10, 10, 3, 3, 0, 1, TAN[5])
    cap(10, 3, 2, (1.5,), (TAN[3], TAN[3]))
    return m


def pumpkin():
    """A pumpkin of eight lobes, with a stem and a leaf."""
    m = Model()
    for x, y, z in all_cells():
        # The grooves between the lobes run straight down the voxels: two
        # along the axes and two along the diagonals, a voxel in.
        groove = x == 7 or y == 7 or x == y or x + y == 15
        rib = 1.0 if groove else 0.0
        rx = 6.6 - 0.9 * rib
        dz = (z + 0.5 - 4.8) / 4.8
        if dz < -1 or dz > 1:
            continue
        r = radius(x, y)
        flat = 1.0 - 0.25 * max(dz, 0)          # flatter on top
        if (r / rx) ** 2 + dz * dz <= 1.0 * flat:
            c = RED[4] if groove else RED[5]
            if dz > 0.75 and not groove:
                c = BROWN[4]                     # light on the lobes' tops
            m.set(x, y, z, c)
    top = m.top(7, 7)
    for z in range(top + 1, top + 4):
        m.set(7, 7, z, GREEN[1])
        m.set(8, 7, z, GREEN[1] if z < top + 3 else None)
    m.set(8, 8, top + 3, GREEN[1])              # the stem's curl
    for x, y in ((9, 6), (10, 6), (10, 5), (11, 5), (9, 5)):
        m.set(x, y, top + 1, GREEN[3])
    return m


# ----------------------------------------------------------------------------
# Stone and wood lying about: cover, in XCOM's sense.

def rock_shape(m, rx, ry, height, seed, lump=0.5, power=2.0):
    """Half a lumpy ellipsoid on the ground; a higher `power` squares it off."""
    for x, y, z in all_cells():
        dx, dy = (x + 0.5 - 8.0) / rx, (y + 0.5 - 8.0) / ry
        dz = (z + 0.5) / height
        d = abs(dx) ** power + abs(dy) ** power + abs(dz) ** power
        if d <= 1.0 + lump * (noise(x, y, z, 4, seed, tile=False) - 0.5):
            m.set(x, y, z, GREY[1])

    def color(x, y, z, old):
        r = white(x, y, z, seed + 1)
        n = noise(x, y, z, 2, seed + 2, tile=False)
        if m.open_to(x, y, z, (0, 0, 1)):
            c = GREY[1] if r > 0.25 else GREY[2]
            if n > 0.8:
                c = GREEN[3] if r < 0.6 else GREEN[2]   # moss
            return c
        if z <= 1:
            return SLATE[5]
        return GREY[0] if n < 0.45 or r < 0.1 else GREY[1]
    m.recolor(color)
    return m


def rock():
    return rock_shape(Model(), 6.3, 5.4, 8.5, 291, lump=0.35)


def boulder():
    """A boulder the full height of the block."""
    return rock_shape(Model(), 7.8, 7.3, 15.5, 301, lump=0.3, power=2.8)


def rubble():
    """A low heap of broken stone and brick: rough ground, not cover."""
    m = Model()
    for x, y, z in all_cells():
        r = radius(x, y)
        height = 6.5 * (1.0 - (r / 7.8) ** 1.6) + 2.2 * (noise(x, y, 0, 4, 311, tile=False) - 0.5)
        if z < height:
            m.set(x, y, z, GREY[1])

    def color(x, y, z, old):
        d1, d2, owner = cells(x, y, z, 3, 312)
        kind = _hash(*owner, 313)
        if kind < 0.1:
            # Broken brick, kept off blood's red.
            return RED[4] if white(x, y, z, 314) > 0.25 else BROWN[2]
        if kind < 0.2:
            return DIRT_DARK
        return pick((GREY[0], GREY[1], GREY[2]), _hash(*owner, 315))
    m.recolor(color)
    # Gaps between the chunks at the surface.
    for (x, y, z) in list(m.voxels):
        d1, d2, _ = cells(x, y, z, 3, 312)
        if d2 - d1 < 0.5 and m.exposed(x, y, z) and z > 0:
            m.set(x, y, z, None)
    return m


def sandbags():
    """Sandbags stacked four high along x, staggered, so a wall of them runs on
    from one block to the next."""
    m = Model()

    def bag(x0, x1, y0, y1, z0, z1):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    end_x = x in (x0, x1)
                    if y in (y0, y1) and z in (z0, z1):
                        continue                # rounded edges
                    if end_x and (y in (y0, y1) or z == z1):
                        continue                # tucked-in ends
                    c = TAN[4]
                    if z == z1 and white(x, y, z, 321) < 0.15:
                        c = TAN[5]
                    if end_x:
                        c = TAN[3]              # the sewn ends
                    m.set(x, y, z, c)

    for layer in range(4):
        z0 = layer * 3
        y0, y1 = (4, 11) if layer < 2 else (5, 10)
        offset = 0 if layer % 2 == 0 else -4
        for start in range(offset, N, 8):
            bag(start, start + 7, y0, y1, z0, z0 + 2)
    return m


def hay_bale():
    """A square bale of straw tied with two loops of twine."""
    m = Model()
    straws = (BROWN[4], BROWN[5], BROWN[5], TAN[5], BROWN[3])
    for x in range(1, 15):
        for y in range(3, 13):
            for z in range(0, 9):
                if y in (3, 12) and z in (0, 8):
                    continue                    # rounded long edges
                c = pick(straws, _hash(x // 3, y, z, 331))
                if x in (1, 14):
                    c = pick(straws, white(x, y, z, 332))  # cut ends
                if x in (4, 11) and (y in (3, 12) or z in (0, 8)):
                    c = BROWN[1]                # twine
                m.set(x, y, z, c)
    return m


def barrel():
    """A wooden barrel: bulging staves, two iron hoops at each end, a lid."""
    m = Model()
    height = 14
    for x, y, z in all_cells():
        if z >= height:
            continue
        bulge = 5.3 + 1.3 * math.sin(math.pi * (z + 0.5) / height)
        r = radius(x, y)
        if r > bulge:
            continue
        a = angle(x, y)
        stave = int((a + math.pi) / (2 * math.pi) * 14) % 2
        c = BROWN[2] if stave else BROWN[3]
        if white(x, y, z, 341) < 0.08:
            c = BROWN[1]
        if r > bulge - 1.2 and z in (1, 2, 11, 12):
            c = SLATE[4] if z in (1, 11) else SLATE[5]   # the hoops
        if z == height - 1 and r < bulge - 1.0:
            c = BROWN[1] if (x + 1) % 4 == 0 else BROWN[2]  # the lid's boards
        m.set(x, y, z, c)
    m.set(9, 6, height - 1, BROWN[0])           # the bung
    return m


def log():
    """A fallen log along x, bark round it, rings at its cut ends, moss on top."""
    m = Model()
    cy, cz, rmax = 7.5, 4.5, 4.6
    for x in range(1, 15):
        for y in range(N):
            for z in range(N):
                r = math.hypot(y - cy, z + 0.5 - cz - 0.5)
                if r > rmax:
                    continue
                if x in (1, 14) and r < rmax - 1.0:
                    ring = int(r * 1.5) % 2
                    c = BROWN[3] if r < 1.0 else (BROWN[4] if ring else BROWN[5])
                else:
                    a = math.atan2(z - cz, y - cy)
                    groove = int((a + math.pi) / (2 * math.pi) * 16) % 3 == 0
                    c = BROWN[1] if groove else BROWN[2]
                    if white(x, y, z, 351) < 0.15:
                        c = BROWN[1]
                    if z >= cz + 3.2 and noise(x, y, z, 4, 352, tile=False) > 0.6:
                        c = GREEN[3] if white(x, y, z, 353) < 0.6 else GREEN[2]
                m.set(x, y, z, c)
    m.box(6, 7, 12, 13, 5, 6, BROWN[2])         # a broken-off branch
    m.set(6, 14, 6, BROWN[2])
    return m


def stump():
    """A tree stump: bark round it, rings on its sawn top, roots at its foot."""
    m = Model()
    height = 6
    for x, y, z in all_cells():
        r = radius(x, y)
        a = angle(x, y)
        reach = 5.1
        if z <= 1:
            # Five roots spreading out at the foot.
            root = max(0.0, math.cos(5 * a + 0.7))
            reach += (2.4 if z == 0 else 1.2) * root ** 3
        if z >= height or r > reach:
            continue
        if z == height - 1 and r < 4.2:
            ring = int(r * 1.4) % 2
            c = BROWN[3] if r < 0.9 else (BROWN[4] if ring else BROWN[5])
        else:
            groove = int((a + math.pi) / (2 * math.pi) * 18) % 3 == 0
            c = BROWN[1] if groove else BROWN[2]
            if white(x, y, z, 361) < 0.12:
                c = BROWN[1]
        m.set(x, y, z, c)
    return m


def pillar():
    """A fluted stone column on a square plinth under a square capital, for
    temples and ruins."""
    m = Model()

    def marble(x, y, z):
        vein = abs(noise(x, y, z, 8, 371, tile=False) - 0.5) < 0.02
        if vein:
            return GREY[1]
        return GREY[3] if white(x, y, z, 372) > 0.12 else GREY[2]

    m.box(1, 14, 1, 14, 0, 0, marble)
    m.box(2, 13, 2, 13, 1, 1, marble)
    m.box(1, 14, 1, 14, 15, 15, marble)
    m.box(2, 13, 2, 13, 14, 14, marble)
    for x, y, z in all_cells():
        if 2 <= z <= 13:
            r = radius(x, y)
            groove = math.cos(12 * angle(x, y)) > 0.55
            if r <= (4.0 if groove else 4.9):
                m.set(x, y, z, GREY[2] if groove and r > 3.0 else marble(x, y, z))
    return m


# ----------------------------------------------------------------------------
# The .vox file: the template's chunks with this model in place of its own.

def _chunk(cid, content, children=b""):
    return cid.encode() + struct.pack("<ii", len(content), len(children)) + content + children


def _string(s):
    data = s.encode()
    return struct.pack("<i", len(data)) + data


def _dict(d):
    out = struct.pack("<i", len(d))
    for k, v in d.items():
        out += _string(k) + _string(v)
    return out


def _template_chunks():
    data = open(TEMPLATE, "rb").read()
    assert data[:4] == b"VOX ", TEMPLATE
    chunks, offset = [], 20
    while offset < len(data):
        cid = data[offset:offset + 4].decode()
        n, m = struct.unpack_from("<ii", data, offset + 4)
        chunks.append((cid, data[offset:offset + 12 + n + m]))
        offset += 12 + n + m
    return chunks


def write(path, model):
    voxels = sorted(model.voxels.items(), key=lambda kv: (kv[0][2], kv[0][1], kv[0][0]))
    xyzi = struct.pack("<i", len(voxels))
    for (x, y, z), c in voxels:
        assert 1 <= c <= 255 and 0 <= x < N and 0 <= y < N and 0 <= z < N
        xyzi += struct.pack("<BBBB", x, y, z, c)
    graph = (
        _chunk("nTRN", struct.pack("<i", 0) + _dict({}) + struct.pack("<iiii", 1, -1, -1, 1) + _dict({}))
        + _chunk("nGRP", struct.pack("<i", 1) + _dict({}) + struct.pack("<ii", 1, 2))
        + _chunk("nTRN", struct.pack("<i", 2) + _dict({}) + struct.pack("<iiii", 3, -1, 0, 1)
                 + _dict({"_t": "0 0 8"}))
        + _chunk("nSHP", struct.pack("<i", 3) + _dict({}) + struct.pack("<i", 1)
                 + struct.pack("<i", 0) + _dict({}))
    )
    body = b""
    for cid, raw in _template_chunks():
        if cid == "SIZE":
            body += _chunk("SIZE", struct.pack("<iii", N, N, N))
        elif cid == "XYZI":
            body += _chunk("XYZI", xyzi)
        elif cid in ("nTRN", "nGRP", "nSHP"):
            if graph:
                body += graph
                graph = b""
        else:
            body += raw
    with open(path, "wb") as f:
        f.write(b"VOX " + struct.pack("<i", 200) + _chunk("MAIN", b"", body))


SHAPES = {
    # Asked for.
    "Ladder": ladder,
    "StoneStairs": stone_stairs,
    "WoodStairs": wood_stairs,
    "Bush": bush,
    "FenceStraight": lambda: fence(EAST, WEST),
    "FenceCorner": lambda: fence(EAST, NORTH),
    "FenceT": lambda: fence(EAST, WEST, NORTH),
    "FenceCross": lambda: fence(EAST, WEST, NORTH, SOUTH),
    "FenceEnd": lambda: fence(EAST),
    "Water": water,
    "Ice": ice,
    "Flowers": flowers,
    "Rock": rock,
    "Sand": sand,
    "Barrel": barrel,
    "Pumpkin": pumpkin,
    # Ground.
    "Dirt": dirt,
    "Stone": stone,
    "Cobblestone": cobblestone,
    "Snow": snow,
    "Mud": mud,
    "Ash": ash,
    "Lava": lava,
    "WoodPlanks": wood_planks,
    # Walls.
    "StoneBrick": stone_brick,
    "Brick": brick,
    "WoodWall": wood_wall,
    "RuinedWall": ruined_wall,
    # Cover and clutter.
    "Boulder": boulder,
    "Sandbags": sandbags,
    "HayBale": hay_bale,
    "Hedge": hedge,
    "Log": log,
    "Stump": stump,
    "Pillar": pillar,
    "Rubble": rubble,
    # Plants.
    "TallGrass": tall_grass,
    "Fern": fern,
    "Reeds": reeds,
    "Wheat": wheat,
    "Cactus": cactus,
    "Mushrooms": mushrooms,
}


def main(names):
    unknown = [n for n in names if n not in SHAPES]
    if unknown:
        sys.exit("Unknown shapes: %s. Known: %s" % (", ".join(unknown), ", ".join(SHAPES)))
    for name in names or SHAPES:
        model = SHAPES[name]()
        path = os.path.join(HERE, name + ".vox")
        write(path, model)
        print("%-14s %5d voxels" % (name, len(model.voxels)))


if __name__ == "__main__":
    main(sys.argv[1:])
