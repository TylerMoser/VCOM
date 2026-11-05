"""The poke_c buildings' geometry, on VCOM's grid.

Every model is drawn on the game's tile grid so that it can be cut into the
game's 16-cubed pieces cleanly (a middle, an edge or a corner slot each), as the
street lamp is drawn whole and cut by make_street_lamp.py:

- 16 voxels a tile. Tile boundaries run at x = 8 + 16i and y = 8 + 16j: every
  canvas has half a tile of margin all round the footprint, which holds the
  outer halves of the edge pieces (eaves, frames, sills, the porch hood).
- Levels are z = 16k. Level 0 (z 0-15) is a house's own floor, a foundation
  that stands in for the map's ground blocks under it; the floor surface, where
  units stand, is z = 16. Walls are three courses (levels 1-3), as TestMap's
  house: a window's glass in the middle course at a unit's eye, over a sill
  course with no glass in it (half cover), under a lintel course.
- A wall is two voxels thick across its tile boundary B (voxels B - 1 and B),
  as SimpleWall1 is across its edge.
- A door is closed, as drawn, and each leaf fills exactly one doorway slot: one
  tile wide, levels 1 and 2 (the user's choice, 2026-10-28). A window keeps
  within its tile, or spans two whole tiles as two window pieces side by side.
- Every pattern (slates, boards, paving, masonry) repeats every 16 voxels on the
  tile grid, as poke_c.png is drawn in 16-pixel tiles: the same part of a wall or
  roof in two tiles is the same piece, so a cut building needs few kinds.
- MagicaVoxel axes: x across the front, y from the front (low y) to the back, z
  up. The front faces -y (Godot +z), as every building in this workspace.

Voxels carry material labels (palettes.LABELS), not colours, and each its role
for the game's slots (Model.role). Cartoon builds the same building simplified
and regularised on the same grid: its doors, windows and slots are the Base's.
"""
import math

TILE = 16


def X(i):
    """The model x of tile boundary i (tile i runs from X(i) to X(i + 1) - 1)."""
    return 8 + TILE * i


Y = X


def Z(k):
    return TILE * k


class Model:
    """A canvas of labelled voxels: [tiles_x] by [tiles_y] tiles of footprint plus
    half a tile of margin all round, [levels] levels tall."""

    def __init__(self, tiles_x, tiles_y, levels, name, footprint=None):
        self.size = ((tiles_x + 1) * TILE, (tiles_y + 1) * TILE, levels * TILE)
        self.tiles = (tiles_x, tiles_y)
        self.name = name
        self.v = {}
        # What each voxel is to the game's slots: "mid" (in a cell's middle: floor,
        # deck, chimney, stone), "ex" / "ey" (on an edge across an x or a y tile
        # boundary: walls, gables, doors, windows, beams, rails), "corner" (posts),
        # "roof" (a cell's middle inside the footprint, the nearest edge or corner
        # under the eaves).
        self.role = {}
        self.role_now = "mid"
        # The footprint's tiles (i, j), and the edge slots each door leaf fills, as
        # cut_pieces' slots: ("ey", tile i, boundary j, level) or ("ex", boundary
        # i, tile j, level).
        self.footprint = footprint or {(i, j) for i in range(tiles_x) for j in range(tiles_y)}
        self.doors = []

    def inside(self, x, y, z):
        W, D, H = self.size
        return 0 <= x < W and 0 <= y < D and 0 <= z < H

    def put(self, x, y, z, label, role=None):
        if self.inside(x, y, z):
            self.v[(x, y, z)] = label
            self.role[(x, y, z)] = role or self.role_now

    def get(self, x, y, z):
        return self.v.get((x, y, z))

    def erase(self, x, y, z):
        self.v.pop((x, y, z), None)
        self.role.pop((x, y, z), None)

    def box(self, x0, x1, y0, y1, z0, z1, label, role=None):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.put(x, y, z, label(x, y, z) if callable(label) else label, role)

    def clear(self, x0, x1, y0, y1, z0, z1):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    self.erase(x, y, z)


class Wall:
    """A wall two voxels thick across a tile boundary, seen as a plane: u along it,
    z up, w across it from the outside (w 0 the outer layer, 1 the inner, -1 a
    voxel proud of the outer face, 2 a voxel in from the inner face).

    [axis] 'x' runs along x on boundary y = [line]; 'y' runs along y on boundary
    x = [line]. [out] is the outward direction across it, -1 or +1."""

    def __init__(self, m, axis, line, out):
        self.m, self.axis, self.line, self.out = m, axis, line, out
        self.outer = line - 1 if out < 0 else line

    def at(self, u, w, z):
        across = self.outer - self.out * w
        return (u, across, z) if self.axis == "x" else (across, u, z)

    def put(self, u, w, z, label):
        self.m.put(*self.at(u, w, z), label, "ey" if self.axis == "x" else "ex")

    def erase(self, u, w, z):
        self.m.erase(*self.at(u, w, z))

    def get(self, u, w, z):
        return self.m.get(*self.at(u, w, z))

    def fill(self, u0, u1, z0, z1, label, layers=(0, 1)):
        for u in range(u0, u1 + 1):
            for z in range(z0, z1 + 1):
                for w in layers:
                    self.put(u, w, z, label(u, z) if callable(label) else label)

    def cut(self, u0, u1, z0, z1, layers=(0, 1)):
        for u in range(u0, u1 + 1):
            for z in range(z0, z1 + 1):
                for w in layers:
                    self.erase(u, w, z)

    def window(self, u0, u1, z0, z1, frame, glass, mullions=(), transoms=(), sill=True, frame_width=1,
               sill_label=None, bars=None):
        """A window in the wall: a frame [frame_width] wide round the opening
        [u0..u1] x [z0..z1] (inclusive, frame included), bars at the u in
        [mullions] and the z in [transoms] (in [bars], or the frame's label), glass
        in the inner layer, a voxel back from the outer face, as SimpleWindow1 has
        it, and a sill a voxel proud of both faces along its foot."""
        for u in range(u0, u1 + 1):
            for z in range(z0, z1 + 1):
                ring = u < u0 + frame_width or u > u1 - frame_width or z < z0 + frame_width or z > z1 - frame_width
                bar = u in mullions or z in transoms
                if ring or bar:
                    label = frame if ring else (bars or frame)
                    self.put(u, 0, z, label)
                    self.put(u, 1, z, label)
                else:
                    self.erase(u, 0, z)
                    self.put(u, 1, z, glass)
        if sill:
            for u in range(u0, u1 + 1):
                self.put(u, -1, z0, sill_label or frame)
                self.put(u, 2, z0, sill_label or frame)


def post(m, cx, cy, z0, z1, label, half=2):
    """A square timber post centred on the grid point (cx, cy): [half] * 2 voxels a
    side, from voxel cx - half to cx + half - 1."""
    m.box(cx - half, cx + half - 1, cy - half, cy + half - 1, z0, z1, label, "corner")


# ----------------------------------------------------------------------------
# Patterns, each repeating every 16 voxels on the tile grid.

def slates(a, s, cartoon):
    """Rectangular slates, three rows and three tiles to the 16 voxels (5, 5, 6), as
    the art's 16-pixel roof tiles: a dark joint along each row's lower edge and
    between tiles, rows staggered, a fixed sprinkle of lighter and darker tiles.
    [a] runs along the ridge, [s] up the slope from the eave. Cartoon: two rows of
    two to the 16."""
    if cartoon:
        row = (s % 16) // 8
        if s % 8 == 0 or (a - 4 * row) % 8 == 0:
            return "slate_gap"
        return "slate"
    s16 = s % 16
    row = 0 if s16 < 5 else (1 if s16 < 10 else 2)
    if s16 in (0, 5, 10):
        return "slate_gap"
    a16 = (a - (0, 8, 3)[row]) % 16
    if a16 in (0, 5, 10):
        return "slate_gap"
    t = 0 if a16 < 5 else (1 if a16 < 10 else 2)
    return ("slate", "slate_light", "slate_mid")[((0, 1, 0), (2, 0, 0), (0, 0, 1))[row][t]]


def scallops(a, s, cartoon):
    """Fish-scale slates, as the manor's: two rows of two scales to the 16 voxels
    (one of one in Cartoon), staggered by half a scale, each scale's rounded lower
    edge dark and the upper middle of it lighter."""
    size = 16 if cartoon else 8
    half = size / 2 - 0.5
    sl = s % size
    row = (s // size) % 2
    al = (a + (size // 2) * row) % size
    edge = round((size // 4) * (abs(al - half) / half) ** 2)
    if sl == edge:
        return "slate_dark"
    if not cartoon and sl in (4, 5, 6) and 1 <= al <= 6:
        return "slate"
    return "slate_blue"


def paving(x, y, cartoon):
    """Cream stone paving in blocks of eight (sixteen in Cartoon), rows staggered
    by half a block, as the bridge's walkway: dark joints, lighter and mid blocks."""
    size = 16 if cartoon else 8
    row = (y // size) % 2
    if y % size == 0 or (x + (size // 2) * row) % size == 0:
        return "paving_dark"
    if cartoon:
        return "paving"
    block = ((x + 4 * row) // 8) % 2 + 2 * ((y // 8) % 2)
    return ("paving", "paving_hi", "paving_mid", "paving")[block]


def masonry(u, z, cartoon, face=0):
    """Dark stone courses four voxels high (eight in Cartoon), blocks eight long
    (sixteen), staggered course to course."""
    h = 8 if cartoon else 4
    length = 16 if cartoon else 8
    course = (z // h) % 2
    if z % h == h - 1 or (u + (length // 2) * course) % length == 0:
        return "masonry_dark" if cartoon else "masonry_black"
    if cartoon:
        return "masonry"
    block = (((u + 4 * course) // 8) + face) % 4
    return ("masonry", "masonry_dark", "masonry", "masonry_light")[(block + course) % 4]


def planks(u, cartoon):
    """Vertical boards four voxels wide (eight in Cartoon) with dark joints."""
    w = 8 if cartoon else 4
    if u % w == 0:
        return "plank_line"
    if cartoon:
        return "plank"
    return ("plank", "plank_mid", "plank", "plank_dark")[(u // 4) % 4]


def foundation(m, cells, cartoon):
    """Level 0 under [cells] (tiles i, j): buried stone, for it stands where the
    map's ground blocks would, a voxel's strip of it under each wall's outer layer,
    and on top a floor of boards four voxels wide running along y, their ends
    staggered: an invented interior, as the art shows none."""
    for (i, j) in cells:
        for x in range(X(i) - 1, X(i + 1) + 1):
            for y in range(Y(j) - 1, Y(j + 1) + 1):
                inside = X(i) <= x < X(i + 1) and Y(j) <= y < Y(j + 1)
                if not inside and ((x - 8) // 16, (y - 8) // 16) in cells:
                    continue
                for z in range(0, 16):
                    joint = z % 4 == 3 or (x + 4 * (z // 4)) % 8 == 0
                    m.put(x, y, z, "found_dark" if joint else "found", "mid")
                if inside:
                    board = (x - 8) // 4
                    gap = (x - 8) % 4 == 0 or (y - 8 + 8 * (board % 2)) % 16 == 0
                    label = "floor_gap" if gap else ("floor" if cartoon or board % 3 else "floor_dark")
                    for z in (14, 15):
                        m.put(x, y, z, label, "mid")


# ----------------------------------------------------------------------------
# Roofs.

def fill_roof(m, columns, bottom, thickness, paint):
    """A roof over [columns] ((x, y) pairs): each column solid from its underside
    [bottom](x, y) (None to skip) through [thickness] voxels, painted by
    [paint](x, y, z, b) with b the underside's height. Thicker than the steepest
    step between columns, it is closed and face-connected."""
    m.role_now = "roof"
    top = 0
    for (x, y) in columns:
        b = bottom(x, y)
        if b is None:
            continue
        for z in range(b, b + thickness):
            m.put(x, y, z, paint(x, y, z, b))
            top = max(top, z)
    m.role_now = "mid"
    return top


def gable_roof(m, axis, lo, hi, ends, base, pitch, thickness, overhang, end_over, pattern, cartoon,
               edge_label="slate_edge", eave_label="slate_black", ceiling="timber_dark", ridge_label=None):
    """A gable roof rising from the walls on boundaries [lo] and [hi] to a ridge
    midway, its ends over the gable walls on boundaries ends[0] and ends[1]. [axis]
    'y': the ridge runs along y (lo, hi are x boundaries); 'x': along x. The
    underside sits on the wall top at [base] and climbs [pitch] voxels for each
    voxel in toward the ridge; [overhang] = (lo side, hi side) voxels of eave past
    the walls' outer faces and [end_over] = (front, back) of verge. [pattern](a, s,
    cartoon) paints the slates, a along the ridge, s up the slope from the eave's
    edge. Returns the roof's highest voxel."""
    mid0 = lo + (hi - lo) // 2 - 1
    a0, a1 = ends[0] - 1 - end_over[0], ends[1] + end_over[1]
    c0, c1 = lo - 1 - overhang[0], hi + overhang[1]

    def d_of(c):
        return c - lo if c <= mid0 else (hi - 1) - c

    def bottom(x, y):
        c = x if axis == "y" else y
        return base + pitch * d_of(c)

    def paint(x, y, z, b):
        c, a = (x, y) if axis == "y" else (y, x)
        if z < b + pitch:
            outside = c < lo - 1 or c > hi or a < ends[0] - 1 or a > ends[1]
            return eave_label if outside else ceiling
        if a in (a0, a1) or c in (c0, c1):
            return edge_label
        side = overhang[0] if c <= mid0 else overhang[1]
        return pattern(a, d_of(c) + side + 1, cartoon)

    cols = [(c, a) if axis == "y" else (a, c) for c in range(c0, c1 + 1) for a in range(a0, a1 + 1)]
    top = fill_roof(m, cols, bottom, thickness, paint)
    # The ridge cap, a voxel proud over the two ridge columns and one either side.
    m.role_now = "roof"
    width = 2 if cartoon else 1
    zr = base + pitch * (mid0 - lo) + thickness - 1
    for c in range(mid0 - width, mid0 + 2 + width):
        for a in range(a0, a1 + 1):
            for z in range(zr, zr + (3 if cartoon else 2)):
                if cartoon and c in (mid0 - width, mid0 + 1 + width) and z == zr + 2:
                    continue
                x, y = (c, a) if axis == "y" else (a, c)
                m.put(x, y, z, ridge_label or edge_label)
                top = max(top, z)
    m.role_now = "mid"
    return top


def gable_wall(wall, lo, hi, base, pitch, infill):
    """Fills the triangle of a gable wall from [base] up, under a roof of [pitch]
    rising from boundaries [lo] and [hi] along the wall (its underside's line)."""
    mid0 = lo + (hi - lo) // 2 - 1
    for u in range(lo - 1, hi + 1):
        d = (u - lo) if u <= mid0 else (hi - 1 - u)
        # Up to the roof's underside: nothing over the outer layer at the eave
        # (d -1), which the eave covers, so no corner of it shows through a steep roof.
        for z in range(base, base + pitch * d + pitch):
            label = infill(u, z) if callable(infill) else infill
            wall.put(u, 0, z, label)
            wall.put(u, 1, z, label)


def chimney(m, x0, x1, y0, y1, z_top, body, cap, flue, base_label, flue_box, cartoon=False, lip=1):
    """A chimney stack standing on the roof under it: solid [body] from the top of
    whatever is below each column up to [z_top], a [cap] lip, and a dark flue hole
    [flue_box] = (x0, x1, y0, y1, depth) in its top."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            ground = max((z for z in range(z_top) if (x, y, z) in m.v), default=0)
            for z in range(ground + 1, z_top + 1):
                m.put(x, y, z, body, "mid")
            m.put(x, y, ground + 1, base_label, "mid")
    for x in range(x0 - lip, x1 + lip + 1):
        for y in range(y0 - lip, y1 + lip + 1):
            for z in range(z_top - (2 if cartoon else 1), z_top + 1):
                m.put(x, y, z, cap, "mid")
    fx0, fx1, fy0, fy1, depth = flue_box
    for x in range(fx0, fx1 + 1):
        for y in range(fy0, fy1 + 1):
            for z in range(z_top - depth + 1, z_top):
                m.put(x, y, z, flue, "mid")
            m.erase(x, y, z_top)


# ----------------------------------------------------------------------------
# The cottages: four tiles across, three deep, a front gable: poke_c.png's eight
# small houses, A with flower boxes (three of them) and B without (five).

def cottage(flower_boxes, cartoon):
    m = Model(4, 3, 7, "PokeC_FlowerBoxCottage" if flower_boxes else "PokeC_Cottage")
    x0, x1, y0, y1 = X(0), X(4), Y(0), Y(3)       # walls on boundaries x 8, 72 and y 8, 56
    floor, top = Z(1), Z(4) - 1                   # floor surface z 16, wall top z 63
    foundation(m, m.footprint, cartoon)
    front = Wall(m, "x", y0, -1)
    back = Wall(m, "x", y1, +1)
    left = Wall(m, "y", x0, -1)
    right = Wall(m, "y", x1, +1)
    for wall, (u0, u1) in ((front, (x0, x1 - 1)), (back, (x0, x1 - 1)), (left, (y0, y1 - 1)), (right, (y0, y1 - 1))):
        wall.fill(u0, u1, floor, top, lambda u, z: "timber_dark" if z <= floor + 1 else "plaster")

    # The front's left bay is wooden: the door in tile 0, its slot, boards on to a
    # post at x 33-35, as drawn; plaster from there with the two windows.
    bay_end = 33
    board = 8 if cartoon else 4
    for u in range(x0, bay_end):
        for z in range(floor + 2, top + 1):
            front.put(u, 0, z, "door_wood_mid" if ((u - x0) // board) % 2 == 0 else "door_wood_dark")
            front.put(u, 1, z, "door_wood_mid")
    m.doors += [("ey", 0, 0, 1), ("ey", 0, 0, 2)]
    d0, d1 = X(0) + 1, X(1) - 2                   # frame x 9..22, the leaf x 10..21
    for u in range(d0, d1 + 1):
        for z in range(floor, floor + 32):
            if u in (d0, d1) or z >= floor + 30:
                for w in (-1, 0, 1):
                    front.put(u, w, z, "timber")
            else:
                groove = not cartoon and (u - d0) % 4 == 0
                front.put(u, 0, z, "door_wood_mid" if groove else "door_wood")
                front.put(u, 1, z, "door_wood")
    front.window(13, 18, floor + 18, floor + 27, "frame", "glass_cottage", sill=False)
    # The knob on the left, as drawn: the door hangs on its right.
    for z in (floor + 12, floor + 13):
        front.put(11, -1, z, "brass")
    if not cartoon:
        front.put(12, -1, floor + 13, "brass_dark")

    # The two-pane windows, centred in tiles 2 and 3, in the light grey surround.
    if not cartoon:
        for u in range(37, 70):
            for z in (floor + 15, floor + 33):
                front.put(u, 0, z, "frame")
        for z in range(floor + 15, floor + 34):
            for u in (37, 69):
                front.put(u, 0, z, "frame")
    fw = 2 if cartoon else 1

    def two_pane(wall, c):
        wall.window(c - 7, c + 6, floor + 18, floor + 29, "frame", "glass_cottage", mullions=(c - 1, c), frame_width=fw)

    for i in (2, 3):
        two_pane(front, X(i) + 8)
    # Side and back walls are unseen in the art: plaster with windows of the same
    # kind, one in each side, two at the back, so every side has one to vault.
    two_pane(left, Y(1) + 8)
    two_pane(right, Y(1) + 8)
    for i in (1, 2):
        two_pane(back, X(i) + 8)

    # Eave beams along the wall tops, a voxel proud, and the corner posts.
    for wall, (u0, u1) in ((front, (x0 - 2, x1 + 1)), (back, (x0 - 2, x1 + 1)), (left, (y0, y1 - 1)), (right, (y0, y1 - 1))):
        for u in range(u0, u1 + 1):
            for z in range(top - 3, top + 1):
                for w in (-1, 0, 1):
                    wall.put(u, w, z, "beam_hi" if (z == top and not cartoon) else "beam")
    half = 3 if cartoon else 2
    for cx in (x0, x1):
        for cy in (y0, y1):
            post(m, cx, cy, floor, top - 4, "timber", half)
    for z in range(floor, top - 3):
        for u in range(bay_end, bay_end + 3):
            for w in (-1, 0, 1):
                front.put(u, w, z, "timber")

    # Gables: dark infill, a king post on the ridge line, two braces leaning in,
    # and a small window either side of the king post (tiles 1 and 2, level 4).
    base = Z(4)
    for wall in (front, back):
        gable_wall(wall, x0, x1, base, 1, "gable_dark")
        for z in range(base, base + 32):
            for u in (39, 40):
                for w in ((-1, 0, 1) if cartoon else (0, 1)):
                    wall.put(u, w, z, "timber")
        for step in range(16):
            for side in (-1, 1):
                for du in (0, 1):
                    u = 20 + step // 2 + du if side < 0 else 59 - step // 2 - du
                    wall.put(u, 0, base + 1 + step, "timber" if cartoon else "beam")
        wall.window(29, 38, base + 2, base + 13, "frame", "glass_cottage", sill=not cartoon)
        wall.window(41, 50, base + 2, base + 13, "frame", "glass_cottage", sill=not cartoon)

    # The roof: 45 degrees, ridge along y over x 39 and 40, three voxels of slate
    # (four in Cartoon) on dark boards, eaves four voxels out (five), verges two
    # (three), so the gable shows under the roof's edge as drawn.
    ov = 5 if cartoon else 4
    gable_roof(m, "y", x0, x1, (y0, y1), base, 1, 4 if cartoon else 3, (ov, ov),
               (3, 3) if cartoon else (2, 2), slates, cartoon)

    # Two tan chimneys on the right slope toward the back, as drawn.
    if cartoon:
        chimney(m, 57, 68, 43, 54, 94, "tan", "tan_light", "flue", "tan_dark", (60, 65, 46, 51, 4), cartoon=True)
        chimney(m, 58, 67, 27, 36, 88, "tan", "tan_light", "flue", "tan_dark", (61, 64, 30, 33, 4), cartoon=True)
    else:
        chimney(m, 58, 69, 44, 53, 92, "tan", "tan_light", "flue", "tan_dark", (61, 66, 47, 50, 6))
        chimney(m, 59, 67, 28, 35, 86, "tan", "tan_light", "flue", "tan_dark", (61, 64, 30, 33, 5))
        for x in range(58, 70):
            if m.get(x, 44, 90) == "tan":
                m.put(x, 44, 90, "tan_shade")

    if flower_boxes:
        for i in (2, 3):
            c = X(i) + 8
            flower_box(front, c - 7, c + 6, floor + 17, cartoon, seed=i)
    return m


def flower_box(wall, u0, u1, z_top, cartoon, seed):
    """A planter hung under a window, as drawn: a wooden box proud of the wall with
    a dark rim, its top just under the window's frame, leaves and flowers in it
    standing in front of the sill."""
    depth = 5 if cartoon else 4
    height = 6 if cartoon else 5
    for u in range(u0, u1 + 1):
        for w in range(-depth, 0):
            for z in range(z_top - height + 1, z_top + 1):
                rim = z == z_top and (w == -depth or u in (u0, u1))
                if rim and not cartoon:
                    label = "box_edge"
                elif z == z_top - 1 and w == -depth and not cartoon:
                    label = "timber_mid"
                else:
                    label = "timber_dark"
                wall.put(u, w, z, label)
    flowers = ("flower_yellow", "flower_orange", "flower_blue", "flower_orange_light", "flower_blue_light")
    for u in range(u0 + 1, u1):
        for w in range(-depth + 1, -1):
            h = (u * 7 + w * 13 + seed * 5) % 17
            tall = (2 + h % 2) if not cartoon else 3
            for k in range(1, tall + 1):
                wall.put(u, w, z_top + k, ("leaf_dark", "leaf", "leaf_light")[h % 3] if not cartoon else "leaf")
            if cartoon:
                if (u - u0) % 3 == 1 and w == -depth + 2:
                    wall.put(u, w, z_top + tall + 1, ("flower_yellow", "flower_orange")[((u - u0) // 3) % 2])
            elif h % 4 == 0:
                wall.put(u, w, z_top + tall + 1, flowers[(h // 4) % len(flowers)])


# ----------------------------------------------------------------------------
# The manor (top right of poke_c.png): a main block six tiles by four under a
# scalloped slate roof, a barrel dormer over the double door and its hood; a
# half-timbered wing two tiles wide set back a tile on the left, its steep gable
# and tall window to the front, its chimney at the back; a bay on the right end.

MANOR_WING = {(i, j) for i in (0, 1) for j in (1, 2, 3)}
MANOR_MAIN = {(i, j) for i in range(2, 8) for j in range(4)}
MANOR_BAY = {(8, 1), (8, 2)}


def manor(cartoon):
    m = Model(9, 4, 8, "PokeC_Manor", MANOR_WING | MANOR_MAIN | MANOR_BAY)
    floor, top = Z(1), Z(4) - 1
    foundation(m, m.footprint, cartoon)
    ox0, ox1 = X(2), X(8)              # main block x 40..135
    oy0, oy1 = Y(0), Y(4)              # y 8..71
    wx0, wx1, wy0 = X(0), X(2), Y(1)   # wing x 8..39, y 24..71
    bx1, by0, by1 = X(9), Y(1), Y(3)   # bay x 136..151, y 24..55

    def plaster(u, z):
        return "mtimber_dark" if z <= floor + 1 else "plaster_mid"

    main_front = Wall(m, "x", oy0, -1)
    main_back = Wall(m, "x", oy1, +1)
    main_left = Wall(m, "y", ox0, -1)    # its front tile faces out; the rest is shared with the wing
    main_right = Wall(m, "y", ox1, +1)
    wing_front = Wall(m, "x", wy0, -1)
    wing_back = Wall(m, "x", oy1, +1)
    wing_left = Wall(m, "y", wx0, -1)
    bay_front = Wall(m, "x", by0, -1)
    bay_back = Wall(m, "x", by1, +1)
    bay_side = Wall(m, "y", bx1, +1)

    main_front.fill(ox0, ox1 - 1, floor, top, plaster)
    main_back.fill(ox0, ox1 - 1, floor, top, plaster)
    main_left.fill(oy0, oy1 - 1, floor, top, plaster)
    main_right.fill(oy0, by0 - 1, floor, top, plaster)
    main_right.fill(by1, oy1 - 1, floor, top, plaster)
    main_right.fill(by0, by1 - 1, top - 3, top, plaster)    # a beam over the opening into the bay
    for wall in (wing_front, wing_back):
        wall.fill(wx0, wx1 - 1, floor, top, plaster)
    wing_left.fill(wy0, oy1 - 1, floor, top, plaster)
    for wall in (bay_front, bay_back):
        wall.fill(ox1, bx1 - 1, floor, top, plaster)
    bay_side.fill(by0, by1 - 1, floor, top, plaster)
    # The wing opens into the hall through the shared wall's middle tile.
    main_left.cut(Y(2), Y(3) - 1, floor, floor + 31)

    # Half-timbering on the wing, as drawn on its front: two inner timbers making
    # narrow, wide and narrow panels between the corner posts, a rail across the
    # narrow ones, the timbers a voxel proud.
    def half_timber(wall, u0, u1):
        studs = [u0 + 10, u0 + 11, u1 - 11, u1 - 10] if cartoon else [u0 + 6, u0 + 7, u0 + 8, u1 - 8, u1 - 7, u1 - 6]
        for u in range(u0, u1 + 1):
            for z in range(floor + 2, top - 3):
                narrow = u < studs[0] or u > studs[-1]
                if u in studs or (narrow and z in (floor + 24, floor + 25)):
                    wall.put(u, 0, z, "mtimber")
                    wall.put(u, -1, z, "mtimber")
                elif not cartoon and (z == floor + 2 or z == top - 4):
                    wall.put(u, 0, z, "plaster_shade")
                else:
                    wall.put(u, 0, z, "plaster" if (cartoon or not narrow) else "plaster_mid")

    half_timber(wing_front, wx0, wx1 - 1)
    for j in (1, 2, 3):
        half_timber(wing_left, Y(j), Y(j + 1) - 1)
    half_timber(wing_back, wx0, wx1 - 1)

    fw = 2 if cartoon else 1

    def tall_window(wall, c, width, transom=True):
        """A tall window centred at [c], [width] across, reaching down the wall as the
        art's do, in a cream surround: its glass in two rows from the middle course
        up to under the top plate, and below the glass, in the sill course, a solid
        light panel in the same frame, so the course stays a wall (half cover) and
        no glass stands in it."""
        u0, u1 = c - width // 2, c + width // 2 - 1
        for u in range(u0 - 2, u1 + 3):
            for z in range(floor + 4, top - 3):
                if u < u0 or u > u1 or z < floor + 6:
                    edge = u in (u0 - 2, u1 + 2) or z == floor + 4
                    wall.put(u, 0, z, "plaster_shade" if (edge and not cartoon) else "plaster")
        for u in range(u0, u1 + 1):
            for z in range(floor + 6, floor + 16):
                frame = u < u0 + fw or u > u1 - fw or z < floor + 6 + fw or z == floor + 15
                wall.put(u, 0, z, "frame_light" if frame else ("frame" if not cartoon else "frame_light"))
                wall.put(u, 1, z, "frame_light")
            wall.put(u, -1, floor + 6, "plaster_shade")
            wall.put(u, 2, floor + 6, "plaster_shade")
        mull = (c - 1, c) if width > 12 else ()
        wall.window(u0, u1, floor + 15, top - 5, "frame_light", "glass_manor", mullions=mull,
                    transoms=(floor + 28, floor + 29) if transom else (), frame_width=fw, sill=False)

    # The main front: two tall windows over two tiles each, the double door between
    # them in tiles 4 and 5, posts on the boundaries 40, 72, 104 and 136, as drawn.
    tall_window(main_front, X(3), 20)
    tall_window(main_front, X(7), 20)
    for c in (X(3), X(7)):
        tall_window(main_back, c, 20)
    tall_window(main_left, Y(0) + 8, 10)
    tall_window(main_right, Y(0) + 8, 10)
    tall_window(main_right, Y(3) + 8, 10)

    # The double door: a leaf in each of tiles 4 and 5 (a doorway slot each, levels
    # 1 and 2), red-brown with two panes in each, a brass handle on the left.
    m.doors += [("ey", 4, 0, 1), ("ey", 4, 0, 2), ("ey", 5, 0, 1), ("ey", 5, 0, 2)]
    door_mid = X(5)
    for u in range(door_mid - 11, door_mid + 11):
        for z in range(floor, floor + 32):
            if u in (door_mid - 11, door_mid - 10, door_mid + 9, door_mid + 10) or z >= floor + 30:
                for w in (-1, 0, 1):
                    main_front.put(u, w, z, "redwood_dark")
                continue
            local = u - (door_mid - 9) if u < door_mid else u - door_mid
            stile = local in (0, 8) or z in (floor, floor + 1, floor + 14, floor + 15, floor + 28, floor + 29)
            main_front.put(u, 0, z, "redwood" if stile else "redwood_light")
            main_front.put(u, 1, z, "redwood")
            if not stile and (floor + 3 <= z <= floor + 12 or floor + 17 <= z <= floor + 26):
                pane = 2 <= local <= 6 and (floor + 4 <= z <= floor + 11 or floor + 18 <= z <= floor + 25)
                if pane:
                    main_front.erase(u, 0, z)
                    main_front.put(u, 1, z, "glass_manor")
                else:
                    main_front.put(u, 0, z, "door_black")
    for z in range(floor + 13, floor + 17):
        main_front.put(door_mid - 8, -1, z, "brass")
        if cartoon:
            main_front.put(door_mid + 7, -1, z, "brass")
    for u in range(door_mid - 11, door_mid + 11):
        main_front.put(u, -1, floor, "redwood_dark")       # the threshold

    # The bay: a window in each face, its outer corners cut on the diagonal.
    tall_window(bay_front, X(8) + 6, 8)
    tall_window(bay_back, X(8) + 6, 8)
    tall_window(bay_side, Y(2) - 5, 10)            # a pair meeting at the middle of the bay's face,
    tall_window(bay_side, Y(2) + 5, 10)            # each within its own tile, clear of the chamfers
    cham = 4
    for cy, sy in ((by0, +1), (by1, -1)):
        for z in range(floor, top + 1):
            for x in range(bx1 - cham, bx1 + 1):
                for k in range(0, cham + 2):
                    y = (cy - 1 + k) if sy > 0 else (cy - k)
                    m.erase(x, y, z)
            for t in range(cham + 1):
                x = bx1 - cham + t
                for k in (0, 1):
                    y = (cy - 1 + t + k) if sy > 0 else (cy - t - k)
                    label = "mtimber_dark" if z <= floor + 1 else ("mtimber" if z >= top - 3 else "plaster_mid")
                    m.put(x, y, z, label, "corner")
                    if t == cham:
                        m.put(x - 1, y, z, label, "corner")

    # Posts: the corners, and on the front's bay boundaries, proud of the wall.
    for cx, cy, h in ((ox0, oy0, 3), (ox1, oy0, 3), (ox0, oy1, 3), (ox1, oy1, 3), (wx0, wy0, 2), (wx0, oy1, 2),
                      (wx1, wy0, 2), (ox1, by0, 2), (ox1, by1, 2)):
        post(m, cx, cy, floor, top - 4, "mtimber", h)
    for b in (X(4), X(6)):
        for u in range(b - 3, b + 3):
            for z in range(floor, top - 3):
                for w in (-2, -1, 0, 1):
                    main_front.put(u, w, z, "mtimber_light" if (u == b - 3 and not cartoon) else "mtimber")

    # Top plates under the eaves, a voxel proud all round.
    for wall, u0, u1 in ((main_front, ox0 - 3, ox1 + 2), (main_back, wx0 - 3, ox1 + 2), (wing_front, wx0 - 3, wx1 - 1),
                         (wing_left, wy0, oy1 - 1), (bay_front, ox1, bx1 - cham - 1), (bay_back, ox1, bx1 - cham - 1),
                         (bay_side, by0 + cham, by1 - cham - 1), (main_right, oy0, by0 - 1), (main_right, by1, oy1 - 1)):
        for u in range(u0, u1 + 1):
            for z in range(top - 3, top + 1):
                for w in (-1, 0, 1):
                    wall.put(u, w, z, "mtimber_dark" if z == top - 3 else "mtimber")

    base = Z(4)
    # Gables: the main block's ends, plaster, a small window high in the right one
    # over the bay's roof; the wing's steep ones, plaster, the tall window in front.
    for wall in (main_left, main_right):
        gable_wall(wall, oy0, oy1, base, 1, "plaster_mid")
    main_right.window(Y(2) - 6, Y(2) + 5, base + 18, base + 28, "frame_light", "glass_manor",
                      mullions=(Y(2) - 1, Y(2)), frame_width=fw, sill_label="plaster_shade")
    wing_pitch = 3
    for wall in (wing_front, wing_back):
        gable_wall(wall, wx0, wx1, base, wing_pitch, "plaster_mid")
    c = X(1)
    wing_front.window(c - 4, c + 3, base + 4, base + 37, "redwood_dark", "glass_manor",
                      transoms=(base + 15, base + 16, base + 26, base + 27), sill=not cartoon,
                      sill_label="redwood_dark")

    # Roofs: the main block's (45 degrees, ridge along x over y 39 and 40, no verge
    # on the left where it meets the wing), the bay's hip, then the wing's steep
    # one, its right eave stopping at the main block's gable.
    # Eaves three voxels out (four in Cartoon), so the tall windows start right under
    # the eave line, as drawn; a ridge of the scales' own slate, as the art has none.
    ov = 4 if cartoon else 3
    gable_roof(m, "x", oy0, oy1, (ox0, ox1), base, 1, 4 if cartoon else 3, (ov, ov), (0, ov),
               scallops, cartoon, edge_label="slate_dark", ridge_label="slate_blue")
    cols = [(x, y) for x in range(ox1 - 1, bx1 + 4) for y in range(by0 - 4, by1 + 4)]

    def bay_bottom(x, y):
        d = min(bx1 - 1 - x, y - by0, by1 - 1 - y)
        return base + d if x >= ox1 - 1 and d <= 16 else None

    def bay_paint(x, y, z, b):
        d_side, d_front, d_back = bx1 - 1 - x, y - by0, by1 - 1 - y
        if z == b:
            return "slate_black" if (x >= bx1 or y < by0 or y >= by1) else "timber_dark"
        if min(d_side, d_front, d_back) == -4:
            return "slate_dark"
        if d_side <= min(d_front, d_back):
            return scallops(y, d_side + 5, cartoon)
        return scallops(x, (d_front if d_front <= d_back else d_back) + 5, cartoon)

    fill_roof(m, cols, bay_bottom, 3, bay_paint)
    wov = 4 if cartoon else 3
    gable_roof(m, "y", wx0, wx1, (wy0, oy1), base, wing_pitch, 5, (wov, -1), (wov + 1, wov + 1), slates, cartoon)

    dormer(m, door_mid, base, cartoon)
    hood(m, main_front, door_mid, top, cartoon)
    # The wing's chimney, blue-grey stone, at its back on the left slope.
    chimney(m, wx0 + 1, wx0 + 13, oy1 - 12, oy1 - 1, Z(7) + 12, "cstone", "cstone_light", "cflue", "cstone_dark",
            (wx0 + 4, wx0 + 9, oy1 - 9, oy1 - 5, 6), cartoon=cartoon)
    if not cartoon:
        # Stone courses, a darker joint every fifth voxel up, as a stack's.
        for (x, y, z), label in list(m.v.items()):
            if label == "cstone" and z % 5 == 0:
                m.put(x, y, z, "cstone_mid", "mid")
    return m


def dormer(m, cx, base, cartoon):
    """A barrel-roofed dormer on the main roof's front slope, centred at x [cx]:
    a front wall standing on the slope with a window, cheeks, and a curved roof
    of slates running back into the main roof, which is opened under it."""
    x0, x1 = cx - 12, cx + 11
    yf = Y(0) + 6                       # its front wall, on the slope's first tile
    z_floor = base + (yf - Y(0))        # the slope's underside there
    spring, crown = base + 22, base + 30
    half = (x1 - x0 + 1) / 2

    def arch(x):
        t = (x + 0.5 - cx) / (half + 1)
        return spring + int((crown - spring) * math.sqrt(max(0.0, 1 - t * t)))

    m.role_now = "roof"
    # Open the main roof under it, so its window looks into the attic.
    for x in range(x0 + 2, x1 - 1):
        for y in range(yf + 2, yf + 40):
            for z in range(base + (y - Y(0)), arch(x)):
                if m.role.get((x, y, z)) == "roof":
                    m.erase(x, y, z)
    for x in range(x0, x1 + 1):
        for z in range(z_floor, arch(x)):
            for y in (yf, yf + 1):
                m.put(x, y, z, "plaster_shade")
    for x in (x0, x0 + 1, x1 - 1, x1):
        for y in range(yf, yf + 32):
            for z in range(base + (y - Y(0)), arch(x)):
                m.put(x, y, z, "plaster_shade")
    for x in range(cx - 7, cx + 7):
        for z in range(z_floor + 4, z_floor + 18):
            ring = x in (cx - 7, cx + 6) or z in (z_floor + 4, z_floor + 17)
            bar = x in (cx - 1, cx) or z in (z_floor + 10, z_floor + 11)
            if ring or bar:
                m.put(x, yf, z, "redwood_dark")
                m.put(x, yf + 1, z, "redwood_dark")
            else:
                m.erase(x, yf, z)
                m.put(x, yf + 1, z, "glass_manor")
    for x in range(cx - 8, cx + 8):
        m.put(x, yf - 1, z_floor + 4, "plaster_shade")
    for x in range(x0 - 2, x1 + 3):
        z_top = arch(min(max(x, x0), x1)) + (1 if x0 <= x <= x1 else 0)
        for y in range(yf - 2, yf + 40):
            if base + (y - Y(0)) + 2 >= z_top + 1:
                break
            for z in range(z_top - 1, z_top + 2):
                edge = y == yf - 2 or x in (x0 - 2, x1 + 2)
                m.put(x, y, z, "slate_dark" if edge else scallops(x, y, cartoon))
    m.role_now = "mid"


def hood(m, wall, cx, top, cartoon):
    """The curved hood over the manor's door, as drawn: a dark slate canopy over
    the door bay and the posts either side, standing out seven voxels, its lower
    edge arched (down nearly to the door's head at the sides, up in the middle)
    and rimmed light, its top tucked under the eave."""
    half = 18
    for u in range(cx - half, cx + half):
        t = (u + 0.5 - cx) / half
        low = top - 15 + round(6 * math.sqrt(max(0.0, 1 - t * t)))
        for w in range(-7, 0):
            high = top - 1 - (w + 7) // 3 if w < -4 else top - 1
            for z in range(low, high + 1):
                if z == low and not cartoon:
                    label = "plaster_shade"
                elif w == -7 or z == high:
                    label = "slate_dark"
                else:
                    label = "slate_blue"
                wall.put(u, w, z, label)


# ----------------------------------------------------------------------------
# The covered bridge (middle of poke_c.png): two identical pavilions eight tiles
# apart on a stone span, as two models (the user's choice): the pavilion on its
# own section of deck, five tiles by two, and the arched span between, three by
# two. Both stand on z 0, the river's bed, their walkway on z 64.

DECK = Z(4)          # the walkway's surface


def deck(m, x0, x1, y0, y1, cartoon):
    """The walkway's slab (level 3) under [x0..x1) x [y0..y1): stone under cream
    paving."""
    for x in range(x0, x1):
        for y in range(y0, y1):
            for z in range(DECK - 16, DECK):
                if z >= DECK - 2:
                    m.put(x, y, z, paving(x - 8, y - 8, cartoon), "mid")
                else:
                    m.put(x, y, z, masonry(x + y, z, cartoon), "mid")


def pavilion(cartoon):
    m = Model(5, 2, 13, "PokeC_BridgePavilion")
    x0, x1, y0, y1 = X(0), X(5), Y(0), Y(2)
    front = Wall(m, "x", y0, -1)
    back = Wall(m, "x", y1, +1)
    left = Wall(m, "y", x0, -1)
    right = Wall(m, "y", x1, +1)
    # Below the deck: a boarded base on all four sides, down to the river's bed.
    for wall, (u0, u1) in ((front, (x0, x1 - 1)), (back, (x0, x1 - 1)), (left, (y0, y1 - 1)), (right, (y0, y1 - 1))):
        wall.fill(u0, u1, 0, DECK - 17, lambda u, z: planks(u - 8, cartoon))
    deck(m, x0, x1, y0, y1, cartoon)
    # The deck's beams, red-brown along the front and back, a voxel proud.
    for wall in (front, back):
        for u in range(x0 - 3, x1 + 3):
            for z in range(DECK - 12, DECK):
                for w in (-1, 0):
                    wall.put(u, w, z, "redwood_dark" if z == DECK - 12 else "redwood")
    storey = DECK + 48 - 1             # the walls' top, z 111
    # The walls at the walkway: white stone-like plaster with short grey dashes, as
    # drawn, on the front and back; the ends open for the walkway to pass through.

    def white(u, z):
        if z <= DECK + 1:
            return "redwood"
        if not cartoon and z % 8 == 3 and (u + 5 * (z // 8)) % 16 in (2, 3, 4, 5, 10, 11):
            return "plaster_shade"
        return "plaster_mid"

    for wall in (front, back):
        wall.fill(x0, x1 - 1, DECK, storey, white)
        for u in range(x0 - 3, x1 + 3):
            for z in range(storey - 5, storey + 1):
                for w in (-1, 0, 1):
                    wall.put(u, w, z, "redwood_dark" if z == storey - 5 else "redwood")
    ph = 4 if cartoon else 3
    for cx in (x0, x1):
        for cy in (y0, y1):
            post(m, cx, cy, 0, storey - 6, "redwood", ph)
    # Gables: sage boards over a tie beam, two struts, steep (two up for one across).
    base = storey + 1
    pitch = 2
    for wall in (front, back):
        gable_wall(wall, x0, x1, base, pitch,
                   lambda u, z: "sage_dark" if (not cartoon and (u - 8) % 4 == 0) else "sage")
        for u in range(x0, x1):
            for z in range(base, base + 4):
                for w in (-1, 0, 1):
                    wall.put(u, w, z, "redwood_dark" if z == base else "redwood")
        for s in (-1, 1):
            c = 48 + s * 16 - (1 if s > 0 else 2)
            for u in range(c, c + 3):
                d = min(u - x0, x1 - 1 - u)
                for z in range(base, base + pitch * d):
                    for w in (-1, 0):
                        wall.put(u, w, z, "redwood")
    ov = 6 if cartoon else 4
    gable_roof(m, "y", x0, x1, (y0, y1), base, pitch, 6 if cartoon else 5, (ov, ov),
               (3, 3) if cartoon else (2, 2), slates, cartoon)
    return m


def span(cartoon):
    m = Model(3, 2, 5, "PokeC_BridgeSpan")
    x0, x1, y0, y1 = X(0), X(3), Y(0), Y(2)
    mid = (x0 + x1) / 2 - 0.5        # 31.5
    # Base: a low arch as drawn, its sides rising to z 12 and its crown z 30.
    # Cartoon: a round arch, as tall, its ring of voussoirs standing a voxel proud.
    radius, rise = 15, (15 if cartoon else 18)
    spring = 15 if cartoon else 12

    def opening(x, z):
        if abs(x - mid) > radius:
            return False
        if z < spring:
            return True
        return ((x - mid) / radius) ** 2 + ((z - spring) / rise) ** 2 <= 1.0

    for x in range(x0, x1):
        for y in range(y0, y1):
            face = y in (y0, y1 - 1)
            for z in range(0, DECK - 16):
                if opening(x, z):
                    continue
                ring = face and z >= spring - 3 and any(
                    opening(x + dx, z + dz) for dx, dz in ((0, -3), (-3, 0), (3, 0), (-2, -2), (2, -2)))
                if ring:
                    # The arch ring in lighter voussoirs, cut radially.
                    ang = math.degrees(math.atan2(z - spring, x - mid))
                    label = "masonry_light" if int(ang // (30 if cartoon else 15)) % 2 else "masonry"
                    m.put(x, y, z, label, "mid")
                    if cartoon:
                        m.put(x, y - 1 if y == y0 else y + 1, z, label, "ey")
                else:
                    m.put(x, y, z, masonry(x + (0 if face else y), z, cartoon, face=0 if face else 1), "mid")
    deck(m, x0, x1, y0, y1, cartoon)
    # The rails: solid red-brown timber a level high along both edges, a darker
    # post on each tile boundary, a cap a voxel proud on the outside.
    front = Wall(m, "x", y0, -1)
    back = Wall(m, "x", y1, +1)
    posts = (0, 1, 15) if not cartoon else (0, 1, 2, 13, 14, 15)
    for wall in (front, back):
        for u in range(x0, x1):
            for z in range(DECK, DECK + 12):
                for w in (-1, 0, 1):
                    if z >= DECK + 10:
                        label = "redwood_light"
                    elif (u - 8) % 16 in posts:
                        label = "redwood_dark"
                    else:
                        label = "redwood"
                    wall.put(u, w, z, label)
            for z in (DECK + 10, DECK + 11):
                wall.put(u, -2, z, "redwood_light")
                if cartoon:
                    wall.put(u, 2, z, "redwood_light")
            if cartoon and (u - 8) % 16 in posts:
                # Chunky posts standing above the cap, rounded off.
                for z in (DECK + 12, DECK + 13):
                    for w in (-2, -1, 0, 1, 2):
                        if z == DECK + 13 and w in (-2, 2):
                            continue
                        wall.put(u, w, z, "redwood_dark")
    return m


BUILDINGS = {
    "Cottage": lambda cartoon: cottage(False, cartoon),
    "FlowerBoxCottage": lambda cartoon: cottage(True, cartoon),
    "Manor": manor,
    "BridgePavilion": pavilion,
    "BridgeSpan": span,
}


def build(kind, cartoon):
    return BUILDINGS[kind](cartoon)
