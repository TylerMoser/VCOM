"""The poke_i buildings' geometry, on VCOM's grid, as the poke_g buildings are
drawn (their helpers copied from poke_f/buildings/sculpt.py).

poke_i.jpg is the art scaled down to 0.594 of its size and saved as a JPEG: a
tile is 9.5 pixels (measured from the forest's repeat and the fences' posts), so
every measurement here is in the art's own voxels (its pixels / 0.594), taken
from regions and edges rather than single pixels, which the scaling blurs.

Every model is drawn on the game's tile grid so that it can be cut into the
game's 16-cubed pieces cleanly (a middle, an edge or a corner slot each):

- 16 voxels a tile. Tile boundaries run at x = 8 + 16i and y = 8 + 16j: every
  canvas has half a tile of margin all round the footprint, which holds the
  outer halves of the edge pieces (eaves, sills, the canopy, the beams).
- Levels are z = 16k. Level 0 (z 0-15) is a building's own floor, a foundation
  standing in for the map's ground blocks under it. Units stand on the top of a
  cell: a floor at level 0 is stood on at level 1.
- A wall is two voxels thick across its tile boundary B (voxels B - 1 and B).
- A door is closed, as drawn, and each leaf fills exactly one doorway slot: one
  tile wide, the two levels a unit fills (the user's choice, 2026-10-28).
- A window keeps within its tile, or stands over a tile boundary, each half its
  own window piece. Its glass is over a solid sill course a level high, so a unit
  vaults in over the sill and has half cover at it.
- A wall with an opening a unit walks through (the day care's arcades) is open in
  whole tiles at the two levels a unit fills, the wall above it on piers at the
  corners between the tiles: any piece in an edge's slot shuts it to the rules.
- Upper floors are reached only where the art draws a way up (the user's
  choice): poke_i draws none, so every building is one storey open to its roof.
- Corners where four tiles meet are decoration to the fight: the houses' corner
  posts and the day care's piers stand there.
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
# Shapes the buildings below share.

def shingles(s, a, cartoon, labels):
    """A shingle's label by [s] (voxels up the slope from the eave) and [a] (along the
    eave): rows four voxels deep (eight in Cartoon), joints every eight (sixteen)
    staggered a row; a few lighter and darker shingles scattered on a fixed hash."""
    light, base, shade, line = labels
    rowh = 8 if cartoon else 4
    jw = 16 if cartoon else 8
    row = s // rowh
    if s % rowh == 0 or (a + (jw // 2) * (row % 2)) % jw == 0:
        return line
    if cartoon:
        return base
    h = ((a % 16) * 5 + (row % 4) * 11) % 13
    return light if h == 0 else (shade if h in (4, 9) else base)


def gable_pitch(m, x0, x1, y0, y1, base, pitch, labels, ridge, edge, cartoon, ov=3, verge=3, thick=3, band=3):
    """A gable roof over the walls on boundaries x0, x1 (outer faces x0 - 1 and x1)
    and y0, y1, its ridge along y midway between them, its underside rising [pitch]
    voxels for each voxel in from the walls' outer faces (a fraction: the art's
    pitches are no whole number), [thick] voxels of shingles; eaves [ov] out,
    drooping a little, verges [verge] past the gables; a light band [band] voxels
    either side of the ridge, the eaves and verges [edge]. Returns under(x), its
    underside at x, for the gables under it."""
    mid = (x0 - 1 + x1) / 2.0
    half = mid - (x0 - 1)

    def d_of(x):
        return (x - (x0 - 1)) if x < mid else (x1 - x)

    def under(x):
        return base + int(math.floor(pitch * d_of(x)))

    ya, yb = y0 - 1 - verge, y1 + verge

    def paint(x, y, z, b, t):
        d = d_of(x)
        if y in (ya, yb) or d <= -ov:
            return edge
        if z == b:
            return edge if (d < 0 or y < y0 - 1 or y > y1) else "ceiling"
        if z < t:
            return labels[2]
        if d >= half - band:
            return ridge
        if d + ov <= 1:
            return edge
        return shingles(d + ov, y, cartoon, labels)

    cols = [(x, y) for x in range(x0 - 1 - ov, x1 + ov + 1) for y in range(ya, yb + 1)]
    fill_roof(m, cols, lambda x, y: under(x), lambda x, y: under(x) + thick - 1, paint)
    return under


def timber_frame(wall, u0, u1, z0, z1, label, step):
    """Dark posts across a wall face, a voxel proud, every [step] voxels from u0 to u1."""
    for u in range(u0, u1 + 1, step):
        for z in range(z0, z1 + 1):
            wall.put(u, -1, z, label)


# ----------------------------------------------------------------------------
# The small house (three in poke_i.png): four tiles by two, one storey of three
# courses, brown board walls between dark corner posts, a beam under the eaves; a
# gable roof of orange shingles with its ridge front to back, a light band along
# the ridge and a light batten across the left slope, as drawn; the front gable of
# dark boards and battens; the front: the red door with a pale jamb (tile 1), a
# window in a thick white frame (tile 2).

def small_house(cartoon):
    m = Model(4, 2, 6, "PokeI_SmallHouse")
    floor = Z(1)
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    x0, x1, y0, y1 = X(0), X(4), Y(0), Y(2)            # walls on x 8, 72 and y 8, 40
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front, back = walls["front"], walls["back"]
    EAVE = Z(4)                                        # the walls' top, z 64
    board = 8 if cartoon else 4

    def boards(u, z):
        if z < 18:
            return "sh_post"
        if z >= 56:
            return "sh_post" if z in (56, 63) else "sh_beam"
        if (z - 18) % board == 0:
            return "sh_wall_line"
        return "sh_wall" if ((z - 18) // board) % 2 or cartoon else "sh_wall_light"

    for key, wall in walls.items():
        u0, u1 = spans[key]
        wall.fill(u0 - 1, u1 + 1, floor, EAVE - 1, boards)
        for u in range(u0 - 1, u1 + 2):
            for z in range(56, 64):
                wall.put(u, -1, z, "sh_beam" if 57 <= z <= 62 else "sh_post")

    def window(wall, c, z0=30, z1=47):
        """A two-pane window in a thick white frame, centred at u = c (a tile's
        middle or a tile boundary), glass in level 2 over the sill course."""
        wall.pane(c - 8, c + 7, z0, z1, "sh_frame", "glass_sh", inner="sh_frame", bars=((c - 1, None), (c, None)))
        for u in range(c - 8, c + 8):
            wall.put(u, -1, z0, "sh_frame")

    # The front: the door in tile 1 (closed), red boards in a dark frame, its knob; a
    # pale jamb at its left, as drawn; the window in tile 2.
    m.doors += [("ey", 1, 0, 1), ("ey", 1, 0, 2)]
    d0 = X(1)
    for u in range(d0, d0 + 16):
        k = u - d0
        for z in range(floor, 48):
            if k < 3:
                label = "sh_jamb"
            elif k in (3, 15) or z in (floor, 46, 47):
                label = "sh_door_dark"
            else:
                label = "sh_door_line" if (k - 4) % (6 if cartoon else 3) == 0 else "sh_door"
            front.put(u, 0, z, label)
            front.put(u, 1, z, label)
    for z in (30, 31):
        front.put(d0 + 12, -1, z, "sh_knob")
    window(front, X(2) + 8)
    # The unseen sides and back: windows of the front's kind.
    for key in ("left", "right"):
        window(walls[key], Y(1))
    for c in (X(1) + 8, X(2) + 8):
        window(back, c)

    # Dark corner posts, a voxel proud.
    half = 3 if cartoon else 2
    for cx in (x0, x1):
        for cy in (y0, y1):
            post(m, cx, cy, floor, EAVE - 1, "sh_post", half)

    # The roof: its ridge front to back over x 39 and 40, rising 0.8 for each voxel in
    # (26 to the ridge, as drawn), three voxels of shingles, eaves and verges three out.
    under = gable_pitch(m, x0, x1, y0, y1, EAVE, 0.8, ("sh_roof_light", "sh_roof", "sh_roof_shade", "sh_roof_line"),
                        "sh_ridge", "sh_roof_edge", cartoon, band=4 if cartoon else 3)
    # The gables, front and back: dark boards and battens up to the roof's underside.
    for wall in (front, back):
        for u in range(x0 - 1, x1 + 1):
            for z in range(EAVE, under(u)):
                batten = (u - 8) % (8 if cartoon else 4) == 0
                wall.put(u, 0, z, "sh_gable_board" if batten else "sh_gable")
                wall.put(u, 1, z, "sh_gable")
    # The light batten across the left slope, two voxels proud, as drawn.
    m.role_now = "roof"
    width = 4 if cartoon else 3
    for x in range(x0 - 4, 38):
        top = under(x) + 2
        for y in range(31, 31 + width):
            for z in (top + 1, top + 2):
                m.put(x, y, z, "sh_ridge")
    m.role_now = "mid"

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 4}]
    m.figure = (1, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The chimney house (two in poke_i.png): five tiles by three, one storey of four
# courses: brown board walls between dark posts, a beam round it at the eaves'
# course, the course above it cream; a steep gable roof of orange shingles, its
# ridge front to back with a light band along it, a stone chimney on the right
# slope at the back, as drawn; the front gable cream with dark boards under the
# ridge and two windows (tiles 1 and 3); the front: the red door (tile 1), a window
# in a cream panel (tile 3).

def chimney_house(cartoon):
    m = Model(5, 3, 9, "PokeI_ChimneyHouse")
    floor = Z(1)
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    x0, x1, y0, y1 = X(0), X(5), Y(0), Y(3)            # walls on x 8, 88 and y 8, 56
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front, back = walls["front"], walls["back"]
    EAVE = Z(5)                                        # the walls' top, z 80
    board = 8 if cartoon else 4

    def boards(u, z):
        if z < 18:
            return "ch_post"
        if z >= 72:
            return "ch_cream"
        if z >= 64:
            return "ch_post" if z in (64, 71) else "ch_beam"
        if (z - 18) % board == 0:
            return "ch_wall_line"
        return "ch_wall" if ((z - 18) // board) % 2 or cartoon else "ch_wall_light"

    for key, wall in walls.items():
        u0, u1 = spans[key]
        wall.fill(u0 - 1, u1 + 1, floor, EAVE - 1, boards)
        for u in range(u0 - 1, u1 + 2):
            for z in range(64, 72):
                wall.put(u, -1, z, "ch_post" if z in (64, 71) else "ch_beam")

    def window(wall, c, z0, z1, bars=1, width=16):
        """A window in a white frame centred at u = c, glass z0 + 1 .. z1 - 1; [bars]
        mullions."""
        u0, u1 = c - width // 2, c - width // 2 + width - 1
        mull = [u0 + round((u1 - u0) * (k + 1) / (bars + 1)) for k in range(bars)]
        wall.pane(u0, u1, z0, z1, "ch_frame", "glass_ch", inner="ch_frame" if cartoon else None,
                  bars=tuple((u, None) for u in mull))
        for u in range(u0, u1 + 1):
            wall.put(u, -1, z0, "ch_frame")

    # The front: the door in tile 1 (closed), red boards; the window in tile 3 in a
    # cream panel across tiles 2 to 4, as drawn.
    m.doors += [("ey", 1, 0, 1), ("ey", 1, 0, 2)]
    d0 = X(1)
    for u in range(d0, d0 + 16):
        k = u - d0
        for z in range(floor, 48):
            if k in (0, 1, 14, 15) or z in (floor, 46, 47):
                label = "ch_door_dark"
            else:
                label = "ch_door_line" if (k - 2) % (6 if cartoon else 3) == 0 else "ch_door"
            front.put(u, 0, z, label)
            front.put(u, 1, z, label)
    for z in (30, 31):
        front.put(d0 + 12, -1, z, "ch_knob")
    front.fill(X(2) + 2, X(4) + 7, 18, 59, "ch_panel")
    window(front, X(3) + 8, 31, 48, bars=2)
    # The unseen sides and back: windows of the front's kind.
    for key in ("left", "right"):
        window(walls[key], Y(1) + 8, 31, 48)
    for c in (X(1) + 8, X(3) + 8):
        window(back, c, 31, 48)

    # Dark posts at the corners and either side of the door, a voxel proud.
    half = 3 if cartoon else 2
    for cx in (x0, x1):
        for cy in (y0, y1):
            post(m, cx, cy, floor, EAVE - 1, "ch_post", half)

    # The roof: steep, its ridge front to back over x 47 and 48, rising 1.15 for each
    # voxel in (46 to the ridge, as drawn).
    under = gable_pitch(m, x0, x1, y0, y1, EAVE, 1.15, ("ch_roof_light", "ch_roof", "ch_roof_shade", "ch_roof_line"),
                        "ch_ridge", "ch_roof_edge", cartoon, band=4 if cartoon else 3)
    # The gables, front and back: cream, dark boards and battens for the top twelve
    # voxels under the ridge; two windows in each, over tiles 1 and 3, as drawn.
    for wall in (front, back):
        for u in range(x0 - 1, x1 + 1):
            top = under(u)
            for z in range(EAVE, top):
                if z >= top - 12 and abs(u - 47.5) < 12:
                    label = "ch_timber_board" if (u - 8) % (8 if cartoon else 4) == 0 else "ch_timber"
                else:
                    label = "ch_cream"
                wall.put(u, 0, z, label)
                wall.put(u, 1, z, label)
        for c in (X(1) + 8, X(3) + 8):
            window(wall, c, 80, 92, bars=1, width=14)

    # The chimney on the right slope at the back, grey stone, its cap and flue, as
    # drawn, standing over the ridge.
    chimney(m, 66, 77, 40, 51, 129, "ch_stone", "ch_stone_light", "ch_flue", "ch_stone_shade",
            (69, 74, 43, 48, 6), cartoon, lip=1, shade="ch_stone_shade")

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 5}]
    m.figure = (1, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The day care (top of poke_i.png): a hall six tiles by three and a wing two by two
# on its right, one storey of four courses, cream walls between dark timber posts,
# a beam round it; the hall a nave of four tiles between two aisles of one, as a
# clerestory hall is built: the aisles under a hipped roof of orange tiles rising
# from the eaves, the nave's walls rising over it two courses more, windows in
# them, under a faceted roof with a flat top and two light rails along it, as
# drawn; the wing under a hipped roof of its own, a valley between them. The front:
# the double door of dark glass (tiles 2 and 3) under a tiled canopy, windows in
# tiles 1 and 4 and over the wing's two tiles; in the nave's front, over the
# canopy, the clerestory window. Arcades on corner piers open the aisles and the
# wing to the nave.

def day_care(cartoon):
    main = {(i, j) for i in range(6) for j in range(3)}
    wing = {(i, j) for i in (6, 7) for j in range(2)}
    m = Model(8, 3, 8, "PokeI_DayCare", main | wing)
    floor = Z(1)
    foundation(m, main | wing, lambda x, y: planks(x, y, cartoon))
    EAVE = Z(5)                                        # the walls' top, z 80
    mx0, mx1, y0, y1 = X(0), X(6), Y(0), Y(3)          # the hall: walls on x 8, 104 and y 8, 56
    wx0, wx1, wy1 = X(6), X(8), Y(2)                   # the wing: x 104..136, y 8..40
    hall, hspan = walls_of(m, mx0, mx1, y0, y1)
    wingw, wspan = walls_of(m, wx0, wx1, y0, wy1)

    def cream(u, z):
        if z < 19:
            return "day_base"
        if 64 <= z < 72:
            return "day_post" if z in (64, 71) else "day_beam"
        return "day_wall"

    # The outer walls (the hall's right wall only behind the wing).
    for key in ("front", "back", "left"):
        u0, u1 = hspan[key]
        hall[key].fill(u0 - 1, u1 + 1, floor, EAVE - 1, cream)
    hall["right"].fill(Y(2) - 1, Y(3), floor, EAVE - 1, cream)
    for key in ("front", "back", "right"):
        u0, u1 = wspan[key]
        wingw[key].fill(u0 - 1, u1 + 1, floor, EAVE - 1, cream)
    # The beam, a voxel proud round the outside.
    for wall, (ua, ub) in ((hall["front"], (6, 137)), (hall["back"], (6, 105)), (hall["left"], (6, 57)),
                           (hall["right"], (40, 57)), (wingw["back"], (103, 137)), (wingw["right"], (6, 41))):
        for u in range(ua, ub + 1):
            for z in range(64, 72):
                wall.put(u, -1, z, "day_post" if z in (64, 71) else "day_beam")

    # Dark timber posts a voxel proud at the corners, either side of the door's bay
    # and where the wing meets the hall, as drawn.
    half = 3 if cartoon else 2
    for cx in (mx0, X(2), X(4), mx1, wx1):
        post(m, cx, y0, floor, EAVE - 1, "day_post", half)
    for cx in (mx0, mx1):
        post(m, cx, y1, floor, EAVE - 1, "day_post", half)
    post(m, wx1, wy1, floor, EAVE - 1, "day_post", half)

    def window(wall, ua, ub, z0, z1, mullions=(), transom=None):
        """Glass in a light frame across u ua..ub, levels from z0 + 1 to z1 - 1."""
        bars = tuple((u, None) for u in mullions) + (((None, transom),) if transom else ())
        wall.pane(ua, ub, z0, z1, "day_frame", "glass_day", inner="day_frame" if cartoon else None, bars=bars)
        for u in range(ua, ub + 1):
            wall.put(u, -1, z0, "day_frame")

    front = hall["front"]
    # Windows in tiles 1 and 4 (glass in levels 2 and 3), over the wing's two tiles.
    for t in (1, 4):
        window(front, X(t) + 1, X(t) + 14, 31, 60, (X(t) + 7, X(t) + 8), 46)
    window(front, X(6) + 2, X(8) - 3, 31, 60, (X(7) - 1, X(7)), 46)
    # The unseen back and sides: windows of the front's kind.
    for t in (1, 4):
        window(hall["back"], X(t) + 1, X(t) + 14, 31, 60, (X(t) + 7, X(t) + 8), 46)
    window(hall["left"], Y(1) + 1, Y(1) + 14, 31, 60, (Y(1) + 7, Y(1) + 8), 46)
    window(hall["right"], Y(2) + 1, Y(2) + 14, 31, 60, (Y(2) + 7, Y(2) + 8), 46)
    window(wingw["right"], Y(0) + 2, Y(2) - 3, 31, 60, (Y(1) - 1, Y(1)), 46)
    window(wingw["back"], X(6) + 2, X(8) - 3, 31, 60, (X(7) - 1, X(7)), 46)

    # The double door, tiles 2 and 3 (closed): two leaves of dark glass in dark frames.
    m.doors += [("ey", 2, 0, 1), ("ey", 2, 0, 2), ("ey", 3, 0, 1), ("ey", 3, 0, 2)]
    for leaf0 in (X(2), X(3)):
        for u in range(leaf0, leaf0 + 16):
            k = u - leaf0
            for z in range(floor, 48):
                if k in (0, 1, 14, 15) or z in (floor, floor + 1, 46, 47):
                    front.put(u, 0, z, "day_post")
                    front.put(u, 1, z, "day_post")
                else:
                    front.erase(u, 0, z)
                    front.put(u, 1, z, "glass_door")
    for u in (X(3) - 3, X(3) + 2):
        for z in (30, 31, 32):
            front.put(u, 0, z, "day_frame")

    # The canopy over the door: a hood of red-brown tiles seven voxels out, from just
    # under the eaves at the wall down to its front edge over the door, as drawn.
    for u in range(X(2) - 4, X(4) + 4):
        for dd in range(1, 8):
            zt = 78 - (dd * 18) // 7
            for z in range(zt - 3, zt + 1):                 # four thick, so its steep rows hold together
                if z == zt - 3:
                    label = "day_post"
                elif dd == 7 or u in (X(2) - 4, X(4) + 3):
                    label = "day_canopy_dark"
                else:
                    row = (dd - 1) // (4 if cartoon else 2)
                    label = "day_canopy_dark" if (not cartoon and (u + 3 * (row % 2)) % 6 == 0) else "day_canopy"
                front.put(u, -dd, z, label)

    # The arcades between the aisles and the nave (x 24 and 88), and between the hall
    # and the wing (x 104): open at the two levels a unit fills, the wall above them
    # on piers at the corners between the tiles (decoration to the fight).
    def arcade(line, rows, top):
        wall = Wall(m, "y", line, +1)
        wall.fill(Y(0) + 1, Y(rows) - 2, 48, top, lambda u, z: "day_post" if z in (48, 49) else "day_wall")
        for j in range(1, rows):
            post(m, line, Y(j), floor, 47, "day_post", 2)

    arcade(X(1), 3, 111)
    arcade(X(5), 3, 111)
    arcade(X(6), 2, 79)

    # The nave's walls over the aisles' roof (z 80-111): cream, a light line under its
    # roof; the clerestory window over the canopy (tiles 2 and 3) and the back's,
    # a window in each side over the middle tile, as drawn on the front.
    for line, out in ((X(1), -1), (X(5), +1)):
        side = Wall(m, "y", line, out)
        side.fill(Y(0) - 1, Y(3), EAVE, 111, lambda u, z: "day_frame" if z >= 110 else "day_wall")
        window(side, Y(1) + 2, Y(2) - 3, 95, 108, (Y(1) + 7, Y(1) + 8))
    for wall in (hall["front"], hall["back"]):
        wall.fill(X(1) - 1, X(5), EAVE, 111, lambda u, z: "day_frame" if z >= 110 else "day_wall")
        window(wall, X(2) + 2, X(4) - 3, 95, 108, (X(3) - 1, X(3)))

    # The aisles' roof: hipped, from the eaves (z 80, three voxels out) rising a voxel
    # for each in, up to the nave's walls; the wing's the same over its own walls; a
    # valley between them. Painted in rows of tiles, the eaves darker.
    ov = 3
    labels = ("day_roof_light", "day_roof", "day_roof_dark", "day_roof_line")

    def hip(x, y, xa, xb, ya, yb):
        """(distance in from the walls' outer faces xa..xb, ya..yb, negative outside;
        the coordinate along the eave of the face it is on)."""
        dx, dy = min(x - xa, xb - x), min(y - ya, yb - y)
        return (dx, y) if dx < dy else (dy, x)

    def lower(x, y):
        best = None
        if mx0 - 1 - ov <= x <= mx1 + ov and y0 - 1 - ov <= y <= y1 + ov:
            in_nave = X(1) - 1 <= x <= X(5) and y0 - 1 <= y <= y1
            if not in_nave:
                best = hip(x, y, mx0 - 1, mx1, y0 - 1, y1)
        if wx0 - ov <= x <= wx1 + ov and y0 - 1 - ov <= y <= wy1 + ov:
            d = hip(x, y, wx0, wx1, y0 - 1, wy1)
            best = d if best is None or d[0] > best[0] else best
        return best

    def roof_top(x, y):
        return EAVE + min(16, lower(x, y)[0])

    def roof_paint(x, y, z, b, t):
        d, a = lower(x, y)
        if z < t:
            return "day_roof_dark" if d < 0 else "ceiling"
        if d <= -ov or d >= 15:
            return "day_roof_line"
        if d + ov <= 1:
            return "day_roof_edge"
        return shingles(d + ov, a, cartoon, labels)

    cols = [(x, y) for x in range(mx0 - 1 - ov, wx1 + ov + 1) for y in range(y0 - 1 - ov, y1 + ov + 1)
            if lower(x, y) is not None]
    fill_roof(m, cols, lambda x, y: roof_top(x, y) - 2, roof_top, roof_paint)

    # The nave's roof: faceted, its sides rising from the nave's walls to a flat top
    # (z 124), two voxels out, two light rails along the top's edges, as drawn.
    nx0, nx1 = X(1) - 3, X(5) + 2                      # x 21..90

    def nave_top(x, y):
        e = min(x - nx0, nx1 - x)
        return 112 + min(12, (e * 2) // 3)

    def nave_paint(x, y, z, b, t):
        e = min(x - nx0, nx1 - x)
        if y in (y0 - 3, y1 + 2) or e == 0:
            return "day_roof_edge"
        if z < t:
            return "ceiling" if z == b and X(1) <= x < X(5) and y0 <= y < y1 else "day_roof_dark"
        if e >= 18:
            return "day_roof_top"
        return shingles(e, y, cartoon, labels)

    cols = [(x, y) for x in range(nx0, nx1 + 1) for y in range(y0 - 3, y1 + 3)]
    fill_roof(m, cols, lambda x, y: nave_top(x, y) - 2, nave_top, nave_paint)
    m.role_now = "roof"
    for rx in ((X(2) - 1, X(2) + 1) if not cartoon else (X(2) - 2, X(2) + 1), (X(4) - 2, X(4)) if not cartoon else (X(4) - 2, X(4) + 1)):
        for x in range(rx[0], rx[1] + 1):
            for y in range(y0 - 3, y1 + 3):
                top = nave_top(x, y)
                for z in (top + 1, top + 2):
                    m.put(x, y, z, "day_rail")
    m.role_now = "mid"
    # The nave's gables, front and back, cream up to its roof's underside.
    for wall in (hall["front"], hall["back"]):
        for u in range(X(1) - 1, X(5) + 1):
            for z in range(112, nave_top(u, 0) - 2):
                wall.put(u, 0, z, "day_wall")
                wall.put(u, 1, z, "day_wall")

    m.storeys = [{"stand": 1, "tiles": main | wing, "entry": "vault", "cut": 5}]
    m.figure = (2, -1, 1, 200)
    return m


BUILDINGS = {
    "SmallHouse": small_house,
    "ChimneyHouse": chimney_house,
    "DayCare": day_care,
}


def build(kind, cartoon):
    return BUILDINGS[kind](cartoon)
