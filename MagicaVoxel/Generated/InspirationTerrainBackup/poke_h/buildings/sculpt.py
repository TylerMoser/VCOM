"""The poke_h building's geometry, on VCOM's grid, as the poke_g buildings are
drawn (their helpers copied from poke_f/buildings/sculpt.py). poke_h's farmhouse
is poke_b's flower cottage drawn again with a porch across its front, so its body
is poke_b/game_buildings/sculpt.py's cottage, copied and moved a tile back to
make room for the porch's row.

Every model is drawn on the game's tile grid so that it can be cut into the
game's 16-cubed pieces cleanly (a middle, an edge or a corner slot each):

- 16 voxels a tile. Tile boundaries run at x = 8 + 16i and y = 8 + 16j: every
  canvas has half a tile of margin all round the footprint, which holds the
  outer halves of the edge pieces (eaves, sills, flower boxes, the stringer).
- Levels are z = 16k. Level 0 (z 0-15) is a building's own floor, a foundation
  standing in for the map's ground blocks under it. Units stand on the top of a
  cell: a floor at level 0 is stood on at level 1.
- A wall is two voxels thick across its tile boundary B (voxels B - 1 and B).
- A door is closed, as drawn, and each leaf fills exactly one doorway slot: one
  tile wide, the two levels a unit fills (the user's choice, 2026-10-28).
- A window keeps within its tile. Its glass is over a solid sill course a level
  high, so a unit vaults in over the sill and has half cover at it; the upper
  storey's tall window by the stair is glass at both its levels, climbed in by.
- Upper floors are real (a slab a level, a room over it), reached only where the
  art draws a way up (the user's choice): here the outside stair.
- Corners where four tiles meet are decoration to the fight: the house's corner
  posts and the porch's posts and their vines stand there.
- The porch is a row of tiles of the footprint in front of the house: its floor
  level-0 pieces, its roof a level over a unit's head.
- MagicaVoxel axes: x across the front, y from the front (low y) to the back, z
  up. The front faces -y (Godot +z), as every building in this workspace.

Voxels carry material labels (palettes.LABELS), not colours, and each its role
for the game's slots (Model.role). Cartoon builds the same building simplified
and regularised on the same grid: its doors, windows and slots are the Base's.
Each model also says what the rules must see of it (storeys, stairs, climbs,
cuts), which qa/integration.py checks in the game.
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
# The farmhouse (middle of poke_h.png): poke_b's flower cottage drawn again
# (poke_b/game_buildings/sculpt.py's cottage, whose body, roof, windows and stair
# this copies) with a porch across its front in place of the two hoods over the
# door and the bay: a shingled roof a tile out on two posts wrapped in flowering
# vines, as drawn, and vines up the stair's stringer. Five tiles by three, two
# storeys of two courses, cream walls, a bell-cast roof with its ridge front to back
# and two roof lights on its left slope, a small window high in the front gable; the
# front: the door with a sidelight (tile 1), a box bay window (tile 3), two-pane
# windows over flower boxes upstairs. On its right, the outside stair, a level a
# tile over three tiles to a landing at the upper door. The porch's tiles are a row
# of the footprint in front of the house (its floor boards, its roof over a unit's
# head); the garden's flower borders round it are left out (scenery, not the house).

def bell(d, rise):
    """The roof's underside over a wall top, [d] voxels in from the wall line, for
    a roof rising [rise] to its ridge 40 in: flat at the eave and the ridge,
    steepest between, as drawn; a little drooping past the wall."""
    if d < 0:
        return d // 2
    return round(rise * (1 - math.cos(math.pi * min(d, 40) / 40)) / 2)


def porch_boards(x, y, cartoon):
    """The porch's floor: boards four voxels wide (eight in Cartoon) across it, in
    the stair's treads' colours."""
    w = 8 if cartoon else 4
    if (x - 8) % w == 0:
        return "co_riser"
    return "co_tread" if ((x - 8) // w) % 2 or cartoon else "co_tread_mid"


def vines(m, cx, cy, half, z0, z1, reach, role, seed, cartoon):
    """Flowering vines round the post of [half] centred on the grid point (cx, cy),
    from z0 to z1, up to [reach] voxels out from its faces: leaves in clumps,
    flowers among them, placed by a fixed hash (the same every build), as drawn;
    each one touching the post or a vine already grown, so they hold together."""
    flowers = ("co_flower_pink", "fh_flower_rose", "co_flower_orange", "co_flower_yellow")
    lo_x, hi_x, lo_y, hi_y = cx - half, cx + half - 1, cy - half, cy + half - 1
    step = 4 if cartoon else 2
    for _ in range(2):
        for ring in range(1, reach + 1):
            for z in range(z0, z1 + 1):
                for x in range(lo_x - ring, hi_x + ring + 1):
                    for y in range(lo_y - ring, hi_y + ring + 1):
                        if max(lo_x - x, x - hi_x, lo_y - y, y - hi_y) != ring or (x, y, z) in m.v:
                            continue
                        h = (x * 73 + y * 151 + z * 37 + seed * 11) % 23
                        if (z // step + x + y) % 3 == 0 and h > 8:
                            continue
                        if not (h < 16 or cartoon):
                            continue
                        if not any((x + dx, y + dy, z + dz) in m.v for dx, dy, dz in
                                   ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))):
                            continue
                        if h < 3:
                            m.put(x, y, z, flowers[(h + z // 5) % 4], role)
                        else:
                            m.put(x, y, z, "co_leaf" if (h + z) % 2 or cartoon else "co_leaf_dark", role)


def farmhouse(cartoon):
    house = {(i, j) for i in range(5) for j in range(1, 4)}
    porch = {(i, 0) for i in range(5)}
    stair_tiles = {(5, j) for j in range(1, 4)}
    m = Model(6, 4, 8, "PokeH_Farmhouse", house | porch | stair_tiles)
    m.roof_tiles = house | porch
    x0, x1, y0, y1 = X(0), X(5), Y(1), Y(4)            # walls on x 8, 88 and y 24, 72
    floor = Z(1)
    foundation(m, house | porch | stair_tiles,
               lambda x, y: (porch_boards if ((x - 8) // 16, (y - 8) // 16) in porch else planks)(x, y, cartoon))
    front = Wall(m, "x", y0, -1)
    back = Wall(m, "x", y1, +1)
    left = Wall(m, "y", x0, -1)
    right = Wall(m, "y", x1, +1)
    EAVE = Z(6)                                          # the walls' top, z 96

    def paint(u, z):
        if z < 18:
            return "co_roof_dark"
        if z < 21 and not cartoon:
            return "co_wall_mid"
        if 52 <= z < 56:
            return "co_band" if z > 52 or cartoon else "co_band_dark"
        return "co_wall"

    for wall, (u0, u1) in ((front, (x0, x1 - 1)), (back, (x0, x1 - 1)), (left, (y0, y1 - 1)), (right, (y0, y1 - 1))):
        wall.fill(u0, u1, floor, EAVE - 1, paint)
        for u in range(u0, u1 + 1):
            for z in (16, 17):
                wall.put(u, -1, z, "co_roof_dark")
            for z in range(52, 56):
                wall.put(u, -1, z, "co_band" if z > 52 else "co_band_dark")

    def window(wall, c, z0, z1, two_pane=True, width=16):
        u0, u1 = c - width // 2, c - width // 2 + width - 1
        bars = ((c - 1, None), (c, None)) if two_pane else ()
        wall.pane(u0, u1, z0, z1, "co_white", "glass_cottage", bars=bars)
        if not cartoon:
            for u in range(u0, u1 + 1):
                wall.put(u, 0, z1, "co_frame")
                wall.put(u, 1, z1, "co_frame")
        for u in range(u0, u1 + 1):
            wall.put(u, -1, z0, "co_frame_dark")

    # The front's ground floor: the door, tile 1 (closed), its leaf teal with a brass
    # plate and knob, a glazed sidelight beside it.
    m.doors += [("ey", 1, 1, 1), ("ey", 1, 1, 2)]
    d0, d1 = X(1), X(2) - 1                            # x 24..39
    for u in range(d0, d1 + 1):
        for z in range(floor, 46):
            if u in (d0, d1) or z in (44, 45):
                label = "co_timber"
            elif u <= d0 + 9:
                k = u - d0
                if k in (1, 9) or z in (floor, floor + 1):
                    label = "co_door_dark"
                elif not cartoon and k in (2, 8):
                    label = "co_door_mid"
                else:
                    label = "co_door"
            elif u == d0 + 10 or u == d1 - 1 or z in (floor + 2, 42, 43):
                label = "co_white"
            else:
                front.erase(u, 0, z)
                front.put(u, 1, z, "glass_cottage")
                continue
            front.put(u, 0, z, label)
            front.put(u, 1, z, label)
    for z in range(36, 38):
        for u in range(d0 + 3, d0 + 7):
            front.put(u, -1, z, "co_brass")
    front.put(d0 + 7, -1, 30, "co_brass")
    front.put(d0 + 7, -1, 31, "co_brass")

    # The bay, tile 3 and the posts either side: a box standing out four voxels, a
    # red-brown base, a cream panel (the sill course), a white-framed window in level 2,
    # dark posts at its corners; the house's wall open behind its window.
    b0, b1 = X(3) - 6, X(4) + 4                         # x 50..76
    bay = Wall(m, "x", y0 - 4, -1)                      # its front's outer face y 19
    for u in range(b0, b1 + 1):
        for z in range(floor, 47):
            if z < 20:
                label = "co_roof_dark"
            elif z < 32:
                label = "co_wall_mid" if not cartoon else "co_wall"
            else:
                label = "co_wall"
            if u in (b0, b0 + 1, b1 - 1, b1):
                label = "co_timber_dark"
            bay.put(u, 0, z, label)
            bay.put(u, 1, z, label)
        for y in range(y0 - 3, y0 - 1):
            for z in range(floor, 47):
                if u in (b0, b0 + 1, b1 - 1, b1):
                    m.put(u, y, z, "co_timber_dark", "ey")
    for u in range(b0 + 2, b1 - 1):
        for y in range(y0 - 3, y0 - 1):
            for z in range(floor, 32):
                m.put(u, y, z, "found" if z < 30 else planks(u, y, cartoon), "ey")
    window(bay, X(3) + 8, 32, 46, two_pane=False)
    front.cut(X(3) + 1, X(4) - 2, 32, 45)
    # The bay's top, a shingled lid under the porch roof.
    for u in range(b0, b1 + 1):
        for y in range(y0 - 5, y0 - 1):
            m.put(u, y, 47, "co_roof_edge" if y == y0 - 5 or u in (b0, b1) else "co_roof", "ey")

    # The porch (level 3): a shingled roof across the front a tile out, from just
    # over the band at the wall (z 58) down to its front edge (z 50, its underside a
    # voxel over a unit's head), on two posts at its front corners wrapped in
    # flowering vines, as drawn: its shingles in rows darker toward the edge, joints
    # every six voxels, staggered.
    depth = 17
    pu0, pu1 = x0 - 4, x1 + 3                           # x 4..91
    for u in range(pu0, pu1 + 1):
        for dd in range(1, depth + 1):
            zt = 58 - (dd * 8) // depth
            for z in range(zt - 2, zt + 1):
                if z == zt - 2:
                    label = "co_timber"
                elif dd >= depth - 1 or u in (pu0, pu1):
                    label = "co_roof_black" if z < zt else "co_roof_edge"
                elif z < zt:
                    label = "co_roof_dark"
                else:
                    rowh = 6 if cartoon else 4
                    row = (dd - 1) // rowh
                    joint = not cartoon and (u + 3 * (row % 2)) % 6 == 0
                    label = ("co_roof_light", "co_roof_hi", "co_roof", "co_roof_dark", "co_roof_dark")[min(row, 4)]
                    if joint:
                        label = "co_roof_hi" if row < 2 else "co_roof_dark"
                # Past the house's right wall it is the porch's own edge piece, never one
                # between the stair's first tile and the grass before it (it would block
                # the way up).
                front.put(u, -dd, z, label, "ex" if u >= x1 else None)
    half = 3 if cartoon else 2

    def post_label(x, y, z):
        if z < floor + 2:
            return "fh_post_dark"
        return "fh_post_mid" if (x + y) % 2 and not cartoon else "fh_post"

    for n, cx in enumerate((x0, x1)):
        post(m, cx, Y(0), floor, 47, post_label, half)
        vines(m, cx, Y(0), half, floor, 47, 2, "corner", n, cartoon)

    # Upstairs: the two-pane windows (tiles 1 and 3), glass in level 5 over the sill
    # course, the flower boxes under them.
    for c in (X(1) + 8, X(3) + 8):
        window(front, c, 79, 94)
        bw = 5 if cartoon else 4
        for u in range(c - 8, c + 8):
            for w in range(-bw, 0):
                for z in range(62, 71):
                    rim = z == 70 and (w == -bw or u in (c - 8, c + 7))
                    if rim and not cartoon:
                        label = "co_box_dark"
                    else:
                        label = "co_box"
                    front.put(u, w, z, label)
        flowers = ("co_flower_pink", "co_flower_orange", "co_flower_yellow")
        for u in range(c - 7, c + 7):
            for w in range(-bw + 1, 0):
                h = (u * 7 + w * 13 + c) % 17
                tall = 3 if cartoon else (2 + h % 3)
                for k in range(1, tall + 1):
                    front.put(u, w, 70 + k, "co_leaf" if (cartoon or h % 2) else "co_leaf_dark")
                if cartoon:
                    if (u - c) % 3 == 1 and w in (-bw + 2, -2):
                        front.put(u, w, 70 + tall + 1, flowers[((u - c) // 3) % 2])
                elif h % 2 == 0:
                    front.put(u, w, 70 + tall + 1, flowers[(h // 2) % 3])

    # Sides and back are unseen in the art (the left is behind trees, the right
    # behind the stair): windows of the front's kind on the left and at the back, both
    # storeys; on the right only the upper door (tile 3, closed) at the landing and, so
    # the upper floor can be entered from the stair, a tall window in tile 2 reaching
    # down to its floor (levels 4 and 5), which one climbs in by from the stair.
    window(left, Y(2) + 8, 32, 46)
    window(left, Y(2) + 8, 79, 94)
    for c in (X(1) + 8, X(3) + 8):
        window(back, c, 32, 46)
        window(back, c, 79, 94)
    window(right, Y(2) + 8, 65, 94, width=12)
    m.doors += [("ex", 5, 3, 4), ("ex", 5, 3, 5)]
    for u in range(Y(3), Y(4)):
        for z in range(64, 92):
            if u in (Y(3), Y(4) - 1) or z in (90, 91):
                label = "co_timber"
            elif (u - Y(3)) in (1, 14) or z in (64, 65):
                label = "co_door_dark"
            elif not cartoon and (u - Y(3)) in (2, 13):
                label = "co_door_mid"
            else:
                label = "co_door"
            right.put(u, 0, z, label)
            right.put(u, 1, z, label)
    right.put(Y(3) + 3, -1, 78, "co_brass")
    right.put(Y(3) + 3, -1, 79, "co_brass")

    # Corner posts, dark timber, a voxel proud.
    for cx in (x0, x1):
        for cy in (y0, y1):
            m.box(cx - half, cx + half - 1, cy - half, cy + half - 1, floor, EAVE - 1, "co_timber", "corner")

    # The upper floor (level 3).
    slab(m, house, 56, 63, lambda x, y: planks(x, y, cartoon))

    # The roof: bell-cast, its ridge along y over x 47 and 48, rising 22 (26 in
    # Cartoon) from the walls' top, three voxels of shingles in rows along the ridge,
    # eaves four voxels out, verges four.
    rise = 26 if cartoon else 22
    ov = 4
    mid = (x0 + x1) // 2                                # 48
    yv0, yv1 = y0 - 1 - ov, y1 + ov                     # the verges, y 19..76
    rowh = 8 if cartoon else 4
    jw = 16 if cartoon else 8

    def dist(x):
        return x - x0 if x < mid else (x1 - 1) - x

    def under(x, y):
        return EAVE + bell(dist(x), rise)

    def roof_paint(x, y, z, b, t):
        d = dist(x)
        if z == b:
            return "co_roof_edge" if (d < 0 or y in (yv0, yv1)) else "co_timber"
        if y in (yv0, yv1) or d <= -ov:
            return "co_roof_edge"
        if d >= 38:
            return "co_roof_mid"
        s = d + ov
        row = s // rowh
        if s % rowh == 0:
            return "co_roof_dark"
        if (y + (jw // 2) * (row % 2)) % jw == 0:
            return "co_roof_dark"
        if cartoon:
            return "co_roof"
        h = ((y % 16) * 5 + (row % 4) * 11 + (1 if x < mid else 0) * 3) % 13
        return "co_roof_light" if h == 0 else ("co_roof_hi" if h in (4, 9) else "co_roof")

    cols = [(x, y) for x in range(x0 - 1 - ov, x1 + ov + 1) for y in range(yv0, yv1 + 1)]
    fill_roof(m, cols, under, lambda x, y: under(x, y) + 2, roof_paint)

    # The gables, front and back, cream up to the roof's underside; a small window
    # high in each, as drawn on the front.
    for wall in (front, back):
        for u in range(x0, x1):
            for z in range(EAVE, under(u, y0)):
                wall.put(u, 0, z, "co_wall")
                wall.put(u, 1, z, "co_wall")
        wall.pane(mid - 4, mid + 3, 99, 109, "co_timber", "glass_cottage")

    # Two roof lights on the left slope, as drawn: dark glass in a raised grey frame.
    m.role_now = "roof"
    for (ya, yb) in ((Y(1) + 8, Y(2) + 3), (Y(3) - 2, Y(3) + 9)):
        for x in range(x0 + 6, x0 + 19):
            for y in range(ya, yb + 1):
                zt = under(x, y) + 2
                frame = x in (x0 + 6, x0 + 18) or y in (ya, yb)
                if frame:
                    m.put(x, y, zt + 1, "co_sky_frame" if not cartoon else "co_sky_frame_dark")
                    m.put(x, y, zt, "co_sky_frame_dark")
                else:
                    m.put(x, y, zt, "glass_dark")
                    for z in range(zt - 2, zt):
                        m.erase(x, y, z)
    m.role_now = "mid"

    # The outside stair, tiles (5, 1-3): treads a level a tile, to a grey landing at
    # the upper door; a red-brown stringer on its open side, a cap along it, vines
    # with flowers up it, as drawn.
    step = 8 if cartoon else 4

    def stair_labels(r, top):
        if top == Z(4):
            return ("co_landing", "co_landing_dark", "co_riser_dark")
        return ("co_tread", "co_riser", "co_riser_dark")

    ys, ye, surface = stair(m, 5, 1, 3, X(5) + 1, X(6) - 2, step, stair_labels)
    sx = X(6)                                           # the stringer across x 103..104
    for y in range(ys + step, ye + 1):
        cap = surface(y) + 4
        for x in (sx - 1, sx):
            for z in range(Z(1), cap):
                if z >= cap - 1:
                    label = "co_stringer_black" if not cartoon else "co_stringer_dark"
                elif x == sx and not cartoon and (z - 16) % 8 == 0:
                    label = "co_stringer_dark"
                else:
                    label = "co_stringer"
                m.put(x, y, z, label, "ex")
        if cartoon:
            m.put(sx + 1, y, cap - 1, "co_stringer_dark", "ex")
        flowers = ("co_flower_pink", "fh_flower_rose", "co_flower_orange", "co_flower_yellow")
        for x in (sx + 1, sx + 2):
            for z in range(Z(1), cap - 1):
                h = (x * 29 + y * 17 + z * 13) % 19
                if h > 13 or (x == sx + 2 and (h > 9 or (sx + 1, y, z) not in m.v)):
                    continue
                if h < 3:
                    label = flowers[(y // 3 + z // 4) % 4]
                else:
                    label = "co_leaf" if (h % 2 or cartoon) else "co_leaf_dark"
                m.put(x, y, z, label, "ex")

    m.storeys = [{"stand": 1, "tiles": set(house), "entry": "vault", "cut": 3},
                 {"stand": 4, "tiles": set(house), "entry": "stair", "cut": 6}]
    m.stairs = {(5, 1): 2, (5, 2): 3, (5, 3): 4}
    m.climbs = [((5, 2, 3), (4, 2, 4))]
    m.figure = (2, 0, 1, 200)
    return m


BUILDINGS = {
    "Farmhouse": farmhouse,
}


def build(kind, cartoon):
    return BUILDINGS[kind](cartoon)
