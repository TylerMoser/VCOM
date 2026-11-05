"""The poke_f buildings' geometry, on VCOM's grid, as the poke_b game-ready
buildings are drawn (poke_b/game_buildings/sculpt.py, whose helpers this copies,
and poke_c/buildings/sculpt.py's gable roof).

Every model is drawn on the game's tile grid so that it can be cut into the
game's 16-cubed pieces cleanly (a middle, an edge or a corner slot each):

- 16 voxels a tile. Tile boundaries run at x = 8 + 16i and y = 8 + 16j: every
  canvas has half a tile of margin all round the footprint, which holds the
  outer halves of the edge pieces (eaves, canopies, sills, planters, pillars).
- Levels are z = 16k. Level 0 (z 0-15) is a building's own floor, a foundation
  standing in for the map's ground blocks under it. Units stand on the top of a
  cell: a floor at level 0 is stood on at level 1.
- A wall is two voxels thick across its tile boundary B (voxels B - 1 and B).
- A door is closed, as drawn, and each leaf fills exactly one doorway slot: one
  tile wide, the two levels a unit fills (the user's choice, 2026-10-28).
- A window keeps within its tile, or spans two whole tiles as two window pieces
  side by side. Its glass is over a solid sill course a level high, so a unit
  vaults in over the sill and has half cover at it.
- Upper floors are real (a slab a level, a room over it), reached only where the
  art draws a way up (the user's choice): here nowhere, so the round shop's and
  the teal hall's upper rooms are closed off.
- Corners where four tiles meet are decoration to the fight: the centre's pillars
  and the round shop's rounded corners stand there.
- MagicaVoxel axes: x across the front, y from the front (low y) to the back, z
  up. The front faces -y (Godot +z), as every building in this workspace.

Voxels carry material labels (palettes.LABELS), not colours, and each its role
for the game's slots (Model.role). Cartoon builds the same building simplified
and regularised on the same grid: its doors, windows and slots are the Base's.
Each model also says what the rules must see of it (storeys, cuts), which
qa/integration.py checks in the game.
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
        # slab, stair), "ex" / "ey" (on an edge across an x or a y tile boundary:
        # walls, doors, windows, cornices, cheeks), "corner" (where four tiles meet),
        # "roof" (a cell's middle inside roof_tiles, else the nearest edge or corner).
        self.role = {}
        self.role_now = "mid"
        self.footprint = footprint or {(i, j) for i in range(tiles_x) for j in range(tiles_y)}
        # The tiles a roof's voxels may fill the middles of: the building's, not a
        # stair's beside it, which must keep its headroom.
        self.roof_tiles = set(self.footprint)
        # The edge slots each door leaf fills, as cut_pieces' slots: ("ey", tile i,
        # boundary j, level) or ("ex", boundary i, tile j, level).
        self.doors = []
        # What the rules must see: each storey's tiles and the level units stand at
        # there, how it is entered ("vault" over a sill from the street, "climb" from
        # a level below, "stair" from the outside stair, None: closed off) and the
        # level the view is cut away from to see into it; a stair's tiles and their
        # levels; and where a soldier stands for scale (tile i, j, level, yaw).
        self.storeys = []
        self.stairs = {}
        self.climbs = []
        self.figure = (0, -2, 1, 200)

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

    def put(self, u, w, z, label, role=None):
        self.m.put(*self.at(u, w, z), label, role or ("ey" if self.axis == "x" else "ex"))

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

    def pane(self, u0, u1, z0, z1, ring, glass, inner=None, bars=(), bar_label=None, w=0):
        """A window in the wall's two layers from [w]: a ring of [ring] round the
        opening [u0..u1] x [z0..z1] (inclusive), an inner ring of [inner] if given,
        bars ((u or None, z or None) pairs: a mullion at u, a transom at z), glass
        in the inner layer, a voxel back from the outer face, as SimpleWindow1 has it."""
        for u in range(u0, u1 + 1):
            for z in range(z0, z1 + 1):
                outer = u in (u0, u1) or z in (z0, z1)
                second = inner and (u in (u0 + 1, u1 - 1) or z in (z0 + 1, z1 - 1))
                bar = any((bu is not None and u == bu) or (bz is not None and z == bz) for bu, bz in bars)
                if outer or second or bar:
                    label = ring if outer else (inner if second else (bar_label or ring))
                    self.put(u, w, z, label)
                    self.put(u, w + 1, z, label)
                else:
                    self.erase(u, w, z)
                    self.put(u, w + 1, z, glass)


def ring_box(m, x0, x1, y0, y1, z0, z1, label, role):
    """The faces of a box, for hollow solids: only voxels on its outside."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                if x in (x0, x1) or y in (y0, y1) or z in (z0, z1):
                    m.put(x, y, z, label(x, y, z) if callable(label) else label, role)


# ----------------------------------------------------------------------------
# Floors and slabs, each repeating every 16 voxels on the tile grid.

def planks(x, y, cartoon):
    """Floorboards four voxels wide (eight in Cartoon) along y, their ends staggered:
    an invented interior, as the art shows none."""
    w = 8 if cartoon else 4
    board = (x - 8) // w
    gap = (x - 8) % w == 0 or (y - 8 + 8 * (board % 2)) % 16 == 0
    if gap:
        return "floor_gap"
    return "floor" if cartoon or board % 4 else "floor_dark"


def stone_tiles(x, y, cartoon):
    """Square floor tiles eight voxels a side (sixteen in Cartoon) with thin joints:
    the lab's and the clinic's invented floors."""
    s = 16 if cartoon else 8
    return "tiles_line" if (x - 8) % s == 0 or (y - 8) % s == 0 else "tiles"


def foundation(m, cells, surface):
    """Level 0 under [cells]: buried stone, for it stands where the map's ground
    blocks would, a voxel's strip of it under each wall's outer layer, and on top
    (z 14-15) the floor painted by [surface](x, y), if any."""
    for (i, j) in cells:
        for x in range(X(i) - 1, X(i + 1) + 1):
            for y in range(Y(j) - 1, Y(j + 1) + 1):
                inside = X(i) <= x < X(i + 1) and Y(j) <= y < Y(j + 1)
                if not inside and ((x - 8) // 16, (y - 8) // 16) in cells:
                    continue
                for z in range(0, 16):
                    joint = z % 4 == 3 or (x + 4 * (z // 4)) % 8 == 0
                    m.put(x, y, z, "found_dark" if joint else "found", "mid")
                if inside and surface:
                    for z in (14, 15):
                        m.put(x, y, z, surface(x, y), "mid")


def slab(m, cells, z0, z1, surface):
    """A floor slab in [cells]' middles from z0 to z1 (inclusive), where no wall
    stands: its top two voxels the floor ([surface](x, y)), a ceiling under it.
    It is an upper storey's floor, a whole level to the rules, however thin."""
    for (i, j) in cells:
        for x in range(X(i), X(i + 1)):
            for y in range(Y(j), Y(j + 1)):
                for z in range(z0, z1 + 1):
                    if (x, y, z) in m.v:
                        continue
                    m.put(x, y, z, surface(x, y) if z >= z1 - 1 else "ceiling", "mid")


def fill_roof(m, columns, bottom, top, paint):
    """A roof over [columns] ((x, y) pairs): each column solid from [bottom](x, y)
    to [top](x, y) (None to skip), painted by [paint](x, y, z, b, t)."""
    m.role_now = "roof"
    for (x, y) in columns:
        b = bottom(x, y)
        if b is None:
            continue
        t = top(x, y)
        for z in range(b, t + 1):
            m.put(x, y, z, paint(x, y, z, b, t))
    m.role_now = "mid"


def stair(m, i, j_first, rows, x0, x1, step, labels):
    """A stair across x [x0..x1] climbing toward +y from row [j_first], a level a
    tile over [rows] rows: row r's block stands to level r + 1, stood on at level
    r + 2. Its treads rise [step] voxels in [step] from the ground half a tile in
    front of the first row, one even flight, so each row's middle, where a unit
    stands, is exactly at its top; the treads rising above a row's top toward the
    next lie in the edge slot between the two (their role), the rest in the row's
    middle. The last row's back half is flat at the top. [labels](r, top) gives
    (tread, riser, body) for a column of row r whose surface is [top]."""
    y_start = Y(j_first) - 8
    y_end = Y(j_first + rows) - 1

    def surface(y):
        return min(16 + step * ((y - y_start) // step), Z(rows + 1))

    for y in range(y_start, y_end + 1):
        top = surface(y)
        before = surface(y - 1) if y > y_start else 16
        r = (y - Y(j_first)) // 16
        row_top = r + 1 if r >= 0 else 0
        tread, riser, body = labels(r, top)
        for x in range(x0, x1 + 1):
            for z in range(16, top):
                if z == top - 1:
                    label = tread
                elif z >= before:
                    label = riser
                else:
                    label = body
                m.put(x, y, z, label, "mid" if z // 16 <= row_top else "ey")
    return y_start, y_end, surface




def post(m, cx, cy, z0, z1, label, half=2):
    """A square post centred on the grid point (cx, cy): [half] * 2 voxels a side,
    from voxel cx - half to cx + half - 1."""
    m.box(cx - half, cx + half - 1, cy - half, cy + half - 1, z0, z1, label, "corner")


def gable_roof(m, axis, lo, hi, ends, base, pitch, thickness, overhang, end_over, pattern, cartoon,
               edge_label, eave_label, ceiling, ridge_label=None):
    """A gable roof rising from the walls on boundaries [lo] and [hi] to a ridge
    midway, its ends over the gable walls on boundaries ends[0] and ends[1]
    (poke_c's). [axis] 'y': the ridge runs along y (lo, hi are x boundaries). The
    underside sits on the wall top at [base] and climbs [pitch] voxels for each
    voxel in toward the ridge; [overhang] = (lo side, hi side) voxels of eave past
    the walls' outer faces and [end_over] = (front, back) of verge. [pattern](a, s,
    cartoon) paints the tiles, a along the ridge, s up the slope from the eave."""
    mid0 = lo + (hi - lo) // 2 - 1
    a0, a1 = ends[0] - 1 - end_over[0], ends[1] + end_over[1]
    c0, c1 = lo - 1 - overhang[0], hi + overhang[1]

    def d_of(c):
        return c - lo if c <= mid0 else (hi - 1) - c

    def bottom(x, y):
        c = x if axis == "y" else y
        return base + pitch * d_of(c)

    def paint(x, y, z, b, t):
        c, a = (x, y) if axis == "y" else (y, x)
        if z < b + pitch:
            outside = c < lo - 1 or c > hi or a < ends[0] - 1 or a > ends[1]
            return eave_label if outside else ceiling
        if a in (a0, a1) or c in (c0, c1):
            return edge_label
        side = overhang[0] if c <= mid0 else overhang[1]
        return pattern(a, d_of(c) + side + 1, cartoon)

    cols = [(c, a) if axis == "y" else (a, c) for c in range(c0, c1 + 1) for a in range(a0, a1 + 1)]
    fill_roof(m, cols, bottom, lambda x, y: bottom(x, y) + thickness - 1, paint)
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
    m.role_now = "mid"
    return zr


def gable_wall(wall, lo, hi, base, pitch, infill):
    """Fills the triangle of a gable wall from [base] up, under a roof of [pitch]
    rising from boundaries [lo] and [hi] along the wall (its underside's line)."""
    mid0 = lo + (hi - lo) // 2 - 1
    for u in range(lo - 1, hi + 1):
        d = (u - lo) if u <= mid0 else (hi - 1 - u)
        for z in range(base, base + pitch * d + pitch):
            label = infill(u, z) if callable(infill) else infill
            wall.put(u, 0, z, label)
            wall.put(u, 1, z, label)


def chimney(m, x0, x1, y0, y1, z_top, body, cap, flue, base_label, flue_box, cartoon=False, lip=1, shade=None):
    """A chimney stack standing on the roof under it: solid [body] from the top of
    whatever is below each column up to [z_top] (its right side [shade]), a [cap]
    lip, and a dark flue hole [flue_box] = (x0, x1, y0, y1, depth) in its top."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            ground = max((z for z in range(z_top) if (x, y, z) in m.v), default=0)
            for z in range(ground + 1, z_top + 1):
                m.put(x, y, z, shade if (shade and x == x1) else body, "mid")
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


def walls_of(m, x0, x1, y0, y1):
    """The four walls of a box on boundaries x0..x1, y0..y1, and their spans."""
    walls = {"front": Wall(m, "x", y0, -1), "back": Wall(m, "x", y1, +1),
             "left": Wall(m, "y", x0, -1), "right": Wall(m, "y", x1, +1)}
    spans = {"front": (x0, x1 - 1), "back": (x0, x1 - 1), "left": (y0, y1 - 1), "right": (y0, y1 - 1)}
    return walls, spans


# ----------------------------------------------------------------------------
# The blue house (six in poke_f.png, two of them in pairs side by side, the right
# one a tile further back): four tiles by three, one storey of three courses
# under a 45-degree blue tiled roof with its ridge front to back, the front gable
# dark timber with two small windows, two chimneys on the right slope; the front:
# a blue door with a window and a brass knob (tile 1), a double window over flower
# boxes (tiles 2-3), dark corner posts, a timber band under the eaves.

def blue_tiles(a, s, cartoon):
    """Blue roof tiles in rows, three rows and three tiles to the 16 voxels (5, 5,
    6), rows staggered, darker joints, a fixed sprinkle of lighter and darker tiles,
    as the art's; two rows of two in Cartoon. [a] runs along the ridge, [s] up the slope."""
    if cartoon:
        row = (s % 16) // 8
        if s % 8 == 0 or (a - 4 * row) % 8 == 0:
            return "bh_roof_shade"
        return "bh_roof"
    s16 = s % 16
    row = 0 if s16 < 5 else (1 if s16 < 10 else 2)
    if s16 in (0, 5, 10):
        return "bh_roof_dark"
    a16 = (a - (0, 8, 3)[row]) % 16
    if a16 in (0, 5, 10):
        return "bh_roof_shade"
    t = 0 if a16 < 5 else (1 if a16 < 10 else 2)
    return ("bh_roof", "bh_roof_light", "bh_roof_mid")[((0, 1, 0), (2, 0, 0), (0, 0, 1))[row][t]]


def blue_house(cartoon):
    m = Model(4, 3, 7, "PokeF_BlueHouse")
    x0, x1, y0, y1 = X(0), X(4), Y(0), Y(3)            # walls on x 8, 72 and y 8, 56
    floor, top = Z(1), Z(4) - 1                         # floor surface z 16, wall top z 63
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front, back, left, right = walls["front"], walls["back"], walls["left"], walls["right"]

    def paint(u, z):
        if z < 18:
            return "bh_timber_dark"
        if z >= top - 3:
            return "bh_timber"
        return "bh_wall"

    for key, wall in walls.items():
        u0, u1 = spans[key]
        wall.fill(u0, u1, floor, top, paint)

    fw = 2 if cartoon else 1

    def pane(wall, c, width, z0=31, z1=50, flowers=False, seed=0):
        """A window centred at [c], [width] wide: a white surround, a grey frame,
        glass in level 2 over the sill course, a white sill; a flower box under it."""
        u0, u1 = c - width // 2, c - width // 2 + width - 1
        for u in range(u0 - 1, u1 + 2):
            for z in range(z0 - 1, z1 + 2):
                if not (u0 <= u <= u1 and z0 <= z <= z1):
                    wall.put(u, 0, z, "bh_wall_light")
        wall.pane(u0, u1, z0, z1, "bh_frame", "glass_house", inner="bh_frame" if cartoon else None)
        for u in range(u0 - 1, u1 + 2):
            wall.put(u, -1, z0, "bh_wall_light")
        if flowers:
            depth = 4 if cartoon else 3
            for u in range(u0, u1 + 1):
                for w in range(-depth, 0):
                    for z in range(z0 - 5, z0):
                        rim = z == z0 - 1 and (w == -depth or u in (u0, u1)) and not cartoon
                        wall.put(u, w, z, "bh_door_dark" if rim else "bh_box")
            for u in range(u0 + 1, u1):
                for w in range(-depth + 1, 0):
                    h = (u * 7 + w * 13 + seed) % 11
                    tall = 3 if cartoon else (2 + h % 3)
                    for k in range(tall):
                        wall.put(u, w, z0 + k, "bh_leaf" if (cartoon or h % 2) else "bh_leaf_light")
                    if cartoon:
                        if (u - u0) % 3 == 1 and w == -2:
                            wall.put(u, w, z0 + tall, ("bh_flower_yellow", "bh_flower_red")[((u - u0) // 3) % 2])
                    elif h % 2 == 0:
                        wall.put(u, w, z0 + tall, "bh_flower_yellow" if h % 4 == 0 else "bh_flower_red")

    # The door, tile 1 (closed): blue, panelled, a small window in its upper part, the
    # brass knob on its left, as drawn.
    m.doors += [("ey", 1, 0, 1), ("ey", 1, 0, 2)]
    d0, d1 = X(1), X(2) - 1                             # x 24..39
    for u in range(d0, d1 + 1):
        for z in range(floor, 48):
            k = u - d0
            if k in (0, 15) or z in (46, 47):
                label = "bh_timber_dark"
            elif k in (1, 14) or z in (floor, floor + 1) or (not cartoon and z == 32):
                label = "bh_door_dark"
            else:
                label = "bh_door"
            front.put(u, 0, z, label)
            front.put(u, 1, z, label)
    front.pane(d0 + 4, d0 + 11, 34, 43, "bh_frame", "glass_house")
    for z in (28, 29):
        front.put(d0 + 2, -1, z, "bh_brass")
        if not cartoon:
            front.put(d0 + 3, -1, z, "bh_brass")

    # The double window over tiles 2 and 3, its two panes one a tile, flower boxes.
    for i, c in ((2, X(2) + 9), (3, X(3) + 7)):
        pane(front, c, 12, flowers=True, seed=i)
    # The unseen sides and back: windows of the same kind, one in each side, two at
    # the back, so every side has one to enter by.
    for wall in (left, right):
        pane(wall, Y(1) + 8, 12)
    for c in (X(1) + 8, X(2) + 8):
        pane(back, c, 12)

    # The timber band under the eaves, a voxel proud, light on top, as drawn; dark
    # corner posts.
    for key, wall in walls.items():
        u0, u1 = spans[key]
        ext = 2 if key in ("front", "back") else 0
        for u in range(u0 - ext, u1 + ext + 1):
            for z in range(top - 3, top + 1):
                label = "bh_timber_light" if (z == top and not cartoon) else ("bh_timber_dark" if z == top - 3 else "bh_timber")
                for w in (-1, 0, 1):
                    wall.put(u, w, z, label)
    half = 3 if cartoon else 2
    for cx in (x0, x1):
        for cy in (y0, y1):
            post(m, cx, cy, floor, top - 4, "bh_timber_dark", half)

    # The gables, front and back: dark timber, a king post and two braces, two small
    # windows (the attic's) either side of the king post, as drawn on the front.
    base = Z(4)
    mid = (x0 + x1) // 2                                 # 40
    for wall in (front, back):
        gable_wall(wall, x0, x1, base, 1, "bh_timber")
        for z in range(base, base + 32):
            for u in (mid - 1, mid):
                for w in ((-1, 0, 1) if cartoon else (0, 1)):
                    wall.put(u, w, z, "bh_timber_dark")
        for step in range(14):
            for du in ((0, 1) if not cartoon else (0, 1, 2)):
                for w in ((0,) if not cartoon else (-1, 0)):
                    wall.put(x0 + 8 + step + du, w, base + 1 + step, "bh_timber_light" if not cartoon else "bh_timber_dark")
                    wall.put(x1 - 9 - step - du, w, base + 1 + step, "bh_timber_light" if not cartoon else "bh_timber_dark")
        for (a, b) in ((mid - 10, mid - 3), (mid + 2, mid + 9)):
            wall.pane(a, b, base + 4, base + 15, "bh_frame", "glass_house", inner="bh_frame" if cartoon else None)

    # The roof: 45 degrees, ridge along y over x 39 and 40, three voxels of blue tile
    # (four in Cartoon), eaves four voxels out (five), verges three (four).
    ov = 5 if cartoon else 4
    eo = 4 if cartoon else 3
    gable_roof(m, "y", x0, x1, (y0, y1), base, 1, 4 if cartoon else 3, (ov, ov), (eo, eo), blue_tiles, cartoon,
               edge_label="bh_roof_black", eave_label="bh_roof_dark", ceiling="bh_timber_dark",
               ridge_label="bh_roof_dark")

    # Two chimneys on the right slope, as drawn: the back one taller.
    lipc = 2 if cartoon else 1
    chimney(m, x1 - 20, x1 - 9, y1 - 16, y1 - 9, 108, "bh_chim", "bh_chim_light", "bh_flue", "bh_chim_shade",
            (x1 - 17, x1 - 12, y1 - 14, y1 - 11, 5), cartoon=cartoon, lip=lipc, shade="bh_chim_shade")
    chimney(m, x1 - 22, x1 - 15, y0 + 14, y0 + 21, 98, "bh_chim", "bh_chim_light", "bh_flue", "bh_chim_shade",
            (x1 - 20, x1 - 17, y0 + 16, y0 + 19, 4), cartoon=cartoon, lip=lipc, shade="bh_chim_shade")

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 4}]
    m.figure = (0, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The domed centre (middle of poke_f.png): six tiles by four, one tall storey (five
# courses): white walls with purple-blue windows over two tiles each and a glass
# double door under a dark blue canopy, flanked by banded posts; above them a band
# of blue panels; a flat blue roof; on it the red dome, the top of a Poke Ball,
# with its band and its button at the front (as drawn: the user's choice); tall
# banded wooden pillars at the four corners; steps before the door.

def dome_center(cartoon):
    m = Model(6, 4, 9, "PokeF_DomeCenter")
    x0, x1, y0, y1 = X(0), X(6), Y(0), Y(4)            # walls on x 8, 104 and y 8, 72
    floor = Z(1)
    foundation(m, m.footprint, lambda x, y: stone_tiles(x, y, cartoon))
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front = walls["front"]
    grid = 16 if cartoon else 8

    def panels(u, z):
        line = (u - 8) % grid == 0 or (z - 64) % grid == 0
        if line:
            return "dc_panel_light"
        return "dc_panel" if (((u - 8) // grid) + ((z - 64) // grid)) % 2 else "dc_panel_mid"

    def paint(u, z):
        if z < 18:
            return "dc_white_shade"
        if z < 64:
            return "dc_white"
        if z < 68:
            return "dc_band_dark" if z == 64 else "dc_band"
        return panels(u, z)

    for key, wall in walls.items():
        u0, u1 = spans[key]
        wall.fill(u0 - 1, u1 + 1, floor, Z(6) - 1, paint)

    def window(wall, c):
        """A purple-blue window over two tiles, centred on boundary [c]: glass in
        levels 2-3 over the sill course, a light frame, a sill."""
        u0, u1 = c - 8, c + 7
        wall.pane(u0, u1, 33, 60, "dc_frame", "glass_center", inner="dc_frame" if cartoon else "dc_white_shade")
        for u in range(u0 - 1, u1 + 2):
            wall.put(u, -1, 33, "dc_frame")
            wall.put(u, 2, 33, "dc_frame")

    for c in (X(1), X(5)):
        window(front, c)
        window(walls["back"], c)
    for key in ("left", "right"):
        window(walls[key], Y(2))

    # The double door over tiles 2 and 3 (two leaves, closed), glass in light frames.
    m.doors += [("ey", 2, 0, 1), ("ey", 2, 0, 2), ("ey", 3, 0, 1), ("ey", 3, 0, 2)]
    for leaf0 in (X(2) + 4, X(3)):                       # x 44..55 and 56..67
        for u in range(leaf0, leaf0 + 12):
            for z in range(floor, 48):
                frame = u in (leaf0, leaf0 + 11) or z in (floor, floor + 1, 46, 47)
                if frame:
                    front.put(u, 0, z, "dc_frame")
                    front.put(u, 1, z, "dc_frame")
                else:
                    front.erase(u, 0, z)
                    front.put(u, 1, z, "glass_center")
    # The banded posts either side of the door, standing proud up to the canopy.
    for p0 in (X(2) - 2, X(4) - 4):                      # x 38..43 and 68..73
        for u in range(p0, p0 + 6):
            for z in range(floor, 60):
                band = (z - floor) % 8 < 2 and not cartoon
                label = "dc_pillar_light" if z >= 56 else ("dc_pillar_dark" if band else "dc_pillar")
                for w in (-2, -1, 0, 1):
                    front.put(u, w, z, label)
    # The canopy over the door, dark blue, standing out to the canvas edge.
    for u in range(X(2) - 6, X(4) + 6):                  # x 34..77
        for w in range(-6, 0):
            for z in range(60, 68):
                rim = z in (60, 67) or w == -6
                front.put(u, w, z, "dc_band_dark" if rim else "dc_band")
    # Two steps before the door, as drawn.
    for u in range(X(2) - 10, X(4) + 10):                # x 30..81
        for w in range(-6, 0):
            front.put(u, w, floor, "dc_step_dark" if w == -6 else "dc_step")
            if X(2) - 4 <= u < X(4) + 4 and w >= -3:
                front.put(u, w, floor + 1, "dc_step")
                front.put(u, w, floor + 2, "dc_step")

    # The roof (level 6): a flat slab of blue panels, a dark rim round it.
    def roof_paint(x, y, z, b, t):
        if z == b:
            return "ceiling"
        if z < t:
            return "dc_panel_dark"
        line = (x - 8) % grid == 0 or (y - 8) % grid == 0
        return "dc_panel_light" if line else ("dc_panel" if (((x - 8) // grid) + ((y - 8) // grid)) % 2 else "dc_panel_mid")

    cols = [(x, y) for x in range(x0 - 1, x1 + 1) for y in range(y0 - 1, y1 + 1)]
    fill_roof(m, cols, lambda x, y: Z(6), lambda x, y: Z(6) + 7, roof_paint)
    for key, wall in walls.items():
        u0, u1 = spans[key]
        for u in range(u0 - 2, u1 + 3):
            for z in range(Z(6) + 4, Z(6) + 8):
                wall.put(u, -1, z, "dc_band_dark")

    # The dome: the red top of a Poke Ball on the roof, 56 voxels across, a highlight
    # on its upper left, the ball's dark band round its foot, its button at the front.
    cx, cy, R = (x0 + x1) / 2 - 0.5, (y0 + y1) / 2 - 0.5, 28.0
    zb = Z(6) + 8                                        # its foot, z 104
    band = 4 if cartoon else 3
    m.role_now = "roof"
    for x in range(int(cx - R) - 1, int(cx + R) + 2):
        for y in range(int(cy - R) - 1, int(cy + R) + 2):
            for z in range(zb, zb + int(R) + 1):
                d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2 + (z - zb + 0.5) ** 2)
                if d > R or d <= R - 3:
                    continue
                if z < zb + band:
                    label = "dc_ball_band_dark" if z == zb else "dc_ball_band"
                else:
                    nx, ny, nz = (x - cx) / d, (y - cy) / d, (z - zb + 0.5) / d
                    lit = -0.45 * nx - 0.35 * ny + 0.82 * nz
                    if lit > 0.93 and not cartoon:
                        label = "dc_red_light"
                    elif lit > 0.86:
                        label = "dc_red_hi"
                    elif z < zb + band + (5 if not cartoon else 3) and ny < -0.2:
                        label = "dc_red_shade"
                    elif nz < 0.25:
                        label = "dc_red_shade"
                    else:
                        label = "dc_red"
                m.put(x, y, z, label)
    # The button, on the band at the front, standing out: a light rim, a dark ring,
    # a light middle, as drawn.
    BR = 10.0 if cartoon else 9.0
    bz = zb + 1.5
    for x in range(int(cx - BR) - 1, int(cx + BR) + 2):
        for z in range(int(bz - BR) - 1, int(bz + BR) + 2):
            r = math.hypot(x - cx, z - bz)
            if r > BR:
                continue
            if r > BR * 0.75:
                label = "dc_button"
            elif r > BR * 0.45:
                label = "dc_button_dark" if r > BR * 0.6 else "dc_button_ring"
            else:
                label = "dc_button_mid" if r > BR * 0.2 else "dc_button"
            depth = 3 if r <= BR * 0.75 else 2
            for k in range(depth):
                yy = int(cy - R) + 2 - k
                m.put(x, yy, z, label)
                # Back to the dome's surface, so the button is joined to it.
            yy = int(cy - R) + 2
            while yy < int(cy) and (x, yy + 1, z) not in m.v and z >= zb:
                yy += 1
                m.put(x, yy, z, label)
    m.role_now = "mid"

    # The four pillars at the corners, banded wood, taller than the roof, capped.
    ph = 7 if cartoon else 6
    for gx in (x0, x1):
        for gy in (y0, y1):
            for x in range(gx - ph, gx + ph):
                for y in range(gy - ph, gy + ph):
                    edge = x in (gx - ph, gx + ph - 1) or y in (gy - ph, gy + ph - 1)
                    for z in range(floor, 120):
                        if z >= 116:
                            label = "dc_cap"
                        elif z >= 112:
                            label = "dc_pillar_light"
                        elif (z - floor) % 8 < 2 and not cartoon:
                            label = "dc_pillar_dark"
                        else:
                            label = "dc_pillar_mid" if edge and not cartoon else "dc_pillar"
                        m.put(x, y, z, label, "corner")
            for x in range(gx - ph - 1, gx + ph + 1):
                for y in range(gy - ph - 1, gy + ph + 1):
                    for z in (116, 117):
                        m.put(x, y, z, "dc_cap", "corner")

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 6}]
    m.figure = (1, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The round shop (bottom middle of poke_f.png): five tiles by two with rounded
# corners, two storeys of two courses: white panels in grey frames, dark rounded
# corner columns; the ground floor's windows (tiles 1, 3) over planters of pink
# flowers and its glass double door (tile 2); a red band between the storeys; a
# window in the upper storey's middle; a white band under a low hipped roof of
# salmon tiles, rounded at its corners like the walls.

def rounded_box(x0, x1, y0, y1, r):
    """The inward distance from the outline of the box [x0, x1] x [y0, y1] (faces,
    continuous) with corners rounded to radius [r], at a voxel's centre (x, y);
    negative outside."""
    def d(x, y):
        px, py = x + 0.5, y + 0.5
        qx = min(max(px, x0 + r), x1 - r)
        qy = min(max(py, y0 + r), y1 - r)
        if px == qx or py == qy:
            return min(px - x0, x1 - px, py - y0, y1 - py)
        return r - math.hypot(px - qx, py - qy)
    return d


def round_shop(cartoon):
    m = Model(5, 2, 7, "PokeF_RoundShop")
    x0, x1, y0, y1 = X(0), X(5), Y(0), Y(2)            # walls on x 8, 88 and y 8, 40
    floor = Z(1)
    foundation(m, m.footprint, lambda x, y: stone_tiles(x, y, cartoon))
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front = walls["front"]
    rc = 12.0 if cartoon else 10.0
    inward = rounded_box(x0 - 1, x1 + 1, y0 - 1, y1 + 1, rc)
    # The floor's paving stops at the rounded walls: past them, at the corners, the
    # foundation's stone.
    for x in range(x0 - 1, x1 + 1):
        for y in range(y0 - 1, y1 + 1):
            if inward(x, y) <= 0 and (x, y, 15) in m.v:
                m.put(x, y, 14, "found", "mid")
                m.put(x, y, 15, "found_dark", "mid")

    def course(u, z, corner):
        """The walls' face by height: a grey plinth, white panels in grey frames
        (dark columns at the rounded corners), the red band, the white upper storey,
        the white band under the roof."""
        if z < 18:
            return "rs_grey_dark"
        if 48 <= z < 64:
            if z == 48 or z == 63:
                return "rs_roof_edge"
            return "rs_band" if z < 60 or cartoon else "rs_roof_light"
        if z >= 90:
            return "rs_white_shade"
        if corner:
            return "rs_grey_light" if corner == 2 else "rs_grey_dark"
        k = (u - 8) % 16
        if k in (0, 15) or (z in (18, 19, 46, 47, 64, 65, 88, 89) and not cartoon):
            return "rs_grey"
        return "rs_white"

    # The shell: two voxels thick inside the rounded outline; the straight parts are
    # the edges' walls, the arcs the corners' (decoration to the fight).
    for x in range(x0 - 1, x1 + 1):
        for y in range(y0 - 1, y1 + 1):
            d = inward(x, y)
            if not 0 < d < 2.01:
                continue
            near_x = x < x0 + rc - 1 or x > x1 - rc
            near_y = y < y0 + rc - 1 or y > y1 - rc
            on_arc = near_x and near_y
            if on_arc:
                role = "corner"
                ang = math.atan2(y + 0.5 - (y0 + rc if y < (y0 + y1) / 2 else y1 - rc),
                                 x + 0.5 - (x0 + rc if x < (x0 + x1) / 2 else x1 - rc))
                corner = 2 if abs(math.cos(2 * ang)) < 0.35 else 1
            else:
                role = "ey" if (y < y0 + 1 or y > y1 - 2) else "ex"
                corner = 0
            u = x if role == "ey" else y
            for z in range(floor, Z(6)):
                m.put(x, y, z, course(u, z, corner), role)
    # The red band, a voxel proud all round, following the outline.
    for x in range(x0 - 2, x1 + 2):
        for y in range(y0 - 2, y1 + 2):
            d = inward(x, y)
            if -1.01 < d <= 0:
                near_x = x < x0 + rc - 1 or x > x1 - rc
                near_y = y < y0 + rc - 1 or y > y1 - rc
                role = "corner" if (near_x and near_y) else ("ey" if (y < y0 or y >= y1) else "ex")
                for z in range(50, 62):
                    m.put(x, y, z, "rs_band" if 51 < z < 61 else "rs_roof_edge", role)

    def window(wall, c, z0, z1):
        u0, u1 = c - 7, c + 6
        wall.pane(u0, u1, z0, z1, "rs_grey_dark", "glass_shop", inner="rs_grey" if not cartoon else None)
        for u in range(u0, u1 + 1):
            wall.put(u, -1, z0, "rs_grey")

    # Ground floor: the windows (tiles 1, 3) over planters, the door (tile 2).
    for c in (X(1) + 8, X(3) + 8):
        window(front, c, 32, 46)
        depth = 4
        for u in range(c - 7, c + 7):
            for w in range(-depth, 0):
                for z in range(floor, floor + 9):
                    rim = (z == floor + 8 and (w == -depth or u in (c - 7, c + 6))) and not cartoon
                    front.put(u, w, z, "rs_box_dark" if rim else "rs_box")
        for u in range(c - 6, c + 6):
            for w in range(-depth + 1, 0):
                h = (u * 5 + w * 11 + c) % 9
                tall = 2 if cartoon else 1 + h % 3
                for k in range(tall):
                    front.put(u, w, floor + 9 + k, "rs_leaf")
                if (h % 2 == 0) if not cartoon else ((u - c) % 3 == 0 and w == -2):
                    front.put(u, w, floor + 9 + tall, "rs_flower_pink" if h % 4 else "rs_flower_orange")
    m.doors += [("ey", 2, 0, 1), ("ey", 2, 0, 2)]
    d0 = X(2)                                            # x 40..55
    for u in range(d0, d0 + 16):
        for z in range(floor, 48):
            k = u - d0
            frame = k in (0, 1, 7, 8, 14, 15) or z in (floor, floor + 1, 46, 47)
            if frame:
                label = "rs_grey_dark" if k in (7, 8) or z in (46, 47) else "rs_grey"
                front.put(u, 0, z, label)
                front.put(u, 1, z, label)
            else:
                front.erase(u, 0, z)
                front.put(u, 1, z, "glass_shop")
    # Upper storey: the wide window in its middle (glass in level 5 over the sill
    # course), as drawn.
    front.pane(X(2), X(3) - 1, 79, 92, "rs_grey_dark", "glass_shop", inner="rs_grey" if not cartoon else None)
    for u in range(X(2), X(3)):
        front.put(u, -1, 79, "rs_grey")
    # The unseen sides and back: windows of the same kind on both storeys, the sides'
    # over the boundary between their two tiles.
    for key in ("left", "right"):
        window(walls[key], Y(1), 32, 46)
        window(walls[key], Y(1), 79, 92)
    for c in (X(1) + 8, X(3) + 8):
        window(walls["back"], c, 32, 46)
        window(walls["back"], c, 79, 92)

    # The upper floor (level 3), inside the rounded walls (a slab of whole tiles
    # would poke out past the curved corners).
    for (i, j) in m.footprint:
        for x in range(X(i), X(i + 1)):
            for y in range(Y(j), Y(j + 1)):
                if inward(x, y) < 2.01:
                    continue
                for z in range(56, 64):
                    if (x, y, z) not in m.v:
                        m.put(x, y, z, planks(x, y, cartoon) if z >= 62 else "ceiling", "mid")

    # The roof: low and hipped over the rounded outline, two voxels out past the walls,
    # rising one in two to a flat top, salmon tiles in rows along the edge, a dark
    # lowest row, lighter tiles staggered, as drawn.
    ov = 2
    rin = rounded_box(x0 - 1 - ov, x1 + 1 + ov, y0 - 1 - ov, y1 + 1 + ov, rc + ov)
    rowh = 8 if cartoon else 4

    def roof_paint(x, y, z, b, t):
        d = rin(x, y)
        if z == b:
            return "rs_roof_edge" if d < ov + 1 else "ceiling"
        if z < t:
            return "rs_roof_dark"
        if d < 1.5:
            return "rs_roof_edge"
        if d >= 20:
            a = x
            s = y
        else:
            dx = min(x - (x0 - 1 - ov), (x1 + ov) - x)
            dy = min(y - (y0 - 1 - ov), (y1 + ov) - y)
            a, s = (x, d) if dy <= dx else (y, d)
        s = int(s)
        if s % rowh == 0:
            return "rs_roof_dark"
        row = s // rowh
        k = (int(a) + (rowh // 2) * (row % 2)) % (2 * rowh)
        if k == 0:
            return "rs_roof_dark"
        if cartoon:
            return "rs_roof"
        return "rs_roof_light" if k in (2, 3, 4) and row % 2 == 0 else "rs_roof"

    cols = [(x, y) for x in range(x0 - 1 - ov, x1 + 1 + ov) for y in range(y0 - 1 - ov, y1 + 1 + ov)
            if rin(x, y) > 0]
    fill_roof(m, cols, lambda x, y: Z(6), lambda x, y: Z(6) + 1 + int(min(rin(x, y), 20)) // 2, roof_paint)

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 3},
                 {"stand": 4, "tiles": set(m.footprint), "entry": None, "cut": 6}]
    m.figure = (1, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The teal hall (bottom right of poke_f.png, off the image's edge and behind trees
# below its upper storey: only its left third shows, so it is completed mirrored,
# the user's choice). A main block eight tiles by three, two storeys (a ground
# storey of three courses, a beige band and the upper floor, an upper storey of two
# in a white strip of windows), a brown fascia, a hipped teal roof on the walls with
# a lighter flat top along its ridge; a lower teal wing a tile wide either side.

def teal_hall(cartoon):
    main = {(i, j) for i in range(1, 9) for j in range(3)}
    wings = {(0, j) for j in range(3)} | {(9, j) for j in range(3)}
    m = Model(10, 3, 9, "PokeF_TealHall", main | wings)
    floor = Z(1)
    foundation(m, main | wings, lambda x, y: stone_tiles(x, y, cartoon))
    mx0, mx1, y0, y1 = X(1), X(9), Y(0), Y(3)           # the main block: x 24..151, y 8..55
    wy1 = Y(3)                                           # the wings' back wall, y 56
    walls, spans = walls_of(m, mx0, mx1, y0, y1)
    front = walls["front"]

    def main_paint(u, z):
        if z < 18:
            return "th_wall_deep"
        if z < 32:
            return "th_wall_dark"
        if z < 64:
            return "th_wall"
        if z < 80:
            return "th_band_dark" if z in (64, 65) else ("th_band" if z >= 78 else "th_beige")
        if z < 108:
            return "th_white"
        if z < 112:
            return "th_band"
        return "th_brown"

    for key, wall in walls.items():
        u0, u1 = spans[key]
        wall.fill(u0 - 1, u1 + 1, floor, Z(8) - 1, main_paint)

    # The wings: a tile wide, three deep, four levels, a flat teal roof.
    for (wx0, wx1) in ((X(0), X(1)), (X(9), X(10))):
        ww, ws = walls_of(m, wx0, wx1, y0, wy1)
        for key in ("front", "back", "left" if wx0 == X(0) else "right"):
            u0, u1 = ws[key]
            ww[key].fill(u0 - 1, u1 + 1, floor, Z(5) - 1,
                         lambda u, z: "th_wall_deep" if z < 18 else ("th_wall_dark" if z < 32 else
                                                                      ("th_band" if z >= 74 else "th_wall")))
        # A window in its front (level 2, over the sill course), as the art's grey panel.
        c = wx0 + 8
        ww["front"].pane(c - 5, c + 4, 33, 46, "th_beige_mid", "glass_hall")
        for u in range(c - 5, c + 5):
            ww["front"].put(u, -1, 33, "th_beige_mid")
        # Its flat roof (level 5), a lip a voxel proud.
        m.role_now = "roof"
        # (up to the main block's side wall, not into it)
        rx0, rx1 = (wx0 - 2, wx1 - 2) if wx0 == X(0) else (wx0 + 1, wx1 + 1)
        for x in range(rx0, rx1 + 1):
            for y in range(y0 - 2, wy1 + 2):
                for z in range(Z(5), Z(5) + 6):
                    rim = x in (wx0 - 2, wx1 + 1) or y in (y0 - 2, wy1 + 1)
                    if z == Z(5):
                        label = "ceiling"
                    elif z == Z(5) + 5:
                        label = "th_roof_dark" if rim else "th_roof_light"
                    else:
                        label = "th_roof_shade" if rim else "th_roof"
                    m.put(x, y, z, label)
        m.role_now = "mid"
    # The wings open into the hall through its side walls' middle tile.
    walls["left"].cut(Y(1), Y(2) - 1, floor, floor + 31)
    walls["right"].cut(Y(1), Y(2) - 1, floor, floor + 31)

    fw = 2 if cartoon else 1

    # The upper storey's strip of windows, one a tile, as drawn: glass in level 6 over
    # the sill course, a beige frame.
    def strip_window(wall, c):
        wall.pane(c - 6, c + 5, 95, 107, "th_beige_mid", "glass_hall", inner="th_beige_mid" if cartoon else None)

    for i in range(1, 9):
        strip_window(front, X(i) + 8)
        strip_window(walls["back"], X(i) + 8)
    for key in ("left", "right"):
        for j in range(3):
            strip_window(walls[key], Y(j) + 8)

    # The ground storey (hidden in the art, inferred): a double door in its middle
    # (tiles 4 and 5, closed), tall windows in tiles 2, 3, 6 and 7 over the sill
    # course, in dark teal frames; windows at the back and in the ends.
    m.doors += [("ey", 4, 0, 1), ("ey", 4, 0, 2), ("ey", 5, 0, 1), ("ey", 5, 0, 2)]
    for leaf0 in (X(4) + 4, X(5)):
        for u in range(leaf0, leaf0 + 12):
            for z in range(floor, 48):
                frame = u in (leaf0, leaf0 + 11) or z in (46, 47) or z < floor + 2
                if frame:
                    label = "th_wall_deep"
                elif not cartoon and z in (30, 31):
                    label = "th_wall_dark"
                else:
                    label = "th_beige" if (u - leaf0) in (5, 6) and not cartoon else "th_beige_mid"
                front.put(u, 0, z, label)
                front.put(u, 1, z, label)
    for u in range(X(4) + 1, X(6) - 1):
        for z in range(48, 56):
            front.put(u, -1, z, "th_brown")

    def tall_window(wall, c):
        wall.pane(c - 6, c + 5, 32, 58, "th_wall_deep", "glass_hall", bars=((None, 45), (None, 46)),
                  bar_label="th_wall_dark")
        for u in range(c - 7, c + 7):
            wall.put(u, -1, 32, "th_beige_mid")

    for i in (2, 3, 6, 7):
        tall_window(front, X(i) + 8)
        tall_window(walls["back"], X(i) + 8)

    # The fascia (level 7): brown, a beige line along its top, a voxel proud, as drawn.
    for key, wall in walls.items():
        u0, u1 = spans[key]
        for u in range(u0 - 2, u1 + 3):
            for z in range(Z(7), Z(8)):
                if z >= Z(8) - 2:
                    label = "th_band"
                elif z == Z(7):
                    label = "th_brown_dark"
                else:
                    label = "th_brown"
                wall.put(u, -1, z, label)

    # The upper floor (level 4) of the main block.
    slab(m, main, 76, 79, lambda x, y: planks(x, y, cartoon))

    # The roof on the walls (level 8): hipped, teal tiles, eaves three voxels out
    # (four in Cartoon) over the fascia, rising one in two to a ridge with a lighter
    # flat top along it, hip lines from the corners, as drawn.
    ov = 4 if cartoon else 3
    ix0, ix1, iy0, iy1 = mx0 - 1 - ov, mx1 + ov, y0 - 1 - ov, y1 + ov
    course = 8 if cartoon else 4
    eave = Z(8)

    def depth(x, y):
        return min(x - ix0, ix1 - x, y - iy0, iy1 - y)

    def under(x, y):
        # One in two all the way: the eave's edge a voxel and a half low, the walls' top
        # where the roof meets them.
        return eave - ov // 2 + depth(x, y) // 2

    def top(x, y):
        return min(under(x, y) + 2, eave + 13)

    def roof_paint(x, y, z, b, t):
        d = depth(x, y)
        if z == b and z < t:
            return "th_roof_dark" if d < ov else "ceiling"
        if d < 1:
            return "th_roof_dark"
        if t >= eave + 13:
            return "th_roof_lighter" if not cartoon and ((x + y) % 16 in (0, 1)) else "th_roof_light"
        dx = min(x - ix0, ix1 - x)
        dy = min(y - iy0, iy1 - y)
        if abs(dx - dy) <= (1 if cartoon else 0):
            return "th_roof_shade"
        a, s = (x, dy) if dy < dx else (y, dx)
        if s % course == 0:
            return "th_roof_shade"
        row = s // course
        if (a + (course // 2) * (row % 2)) % (2 * course) == 0:
            return "th_roof_shade"
        return "th_roof" if (cartoon or row % 2) else "th_roof_light"

    cols = [(x, y) for x in range(ix0, ix1 + 1) for y in range(iy0, iy1 + 1)]
    fill_roof(m, cols, under, top, roof_paint)

    m.storeys = [{"stand": 1, "tiles": main | wings, "entry": "vault", "cut": 4},
                 {"stand": 5, "tiles": set(main), "entry": None, "cut": 7}]
    m.figure = (3, -1, 1, 200)
    return m


BUILDINGS = {
    "BlueHouse": blue_house,
    "DomeCenter": dome_center,
    "RoundShop": round_shop,
    "TealHall": teal_hall,
}


def build(kind, cartoon):
    return BUILDINGS[kind](cartoon)
