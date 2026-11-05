"""The poke_j buildings' geometry, on VCOM's grid, as the poke_i buildings are
drawn (their helpers copied from poke_i/buildings/sculpt.py, gable_pitch given a
pattern for the red house's rows of tiles).

poke_j.jpg is the art scaled down to 0.765 of its size and saved as a JPEG: a
tile is 12.25 pixels (measured from the forest's repeat, its trees two tiles
across), so every measurement here is in the art's own voxels (its pixels /
0.765), taken from regions and edges rather than single pixels, and the red
house's from its three copies averaged.

Every model is drawn on the game's tile grid so that it can be cut into the
game's 16-cubed pieces cleanly (a middle, an edge or a corner slot each):

- 16 voxels a tile. Tile boundaries run at x = 8 + 16i and y = 8 + 16j: every
  canvas has half a tile of margin all round the footprint, which holds the
  outer halves of the edge pieces (eaves, verges, sills, beams, flower boxes).
- Levels are z = 16k. Level 0 (z 0-15) is a building's own floor, a foundation
  standing in for the map's ground blocks under it. Units stand on the top of a
  cell: a floor at level 0 is stood on at level 1.
- A wall is two voxels thick across its tile boundary B (voxels B - 1 and B).
- A door is closed, as drawn, and each leaf fills exactly one doorway slot: one
  tile wide, the two levels a unit fills (the user's choice, 2026-10-28). The art
  draws its doors where the map's tiles are, its walls half a tile off them, so a
  door moves within half a tile of where it is drawn.
- A window keeps within its tile, or stands over a tile boundary, each half its
  own window piece. Its glass is over a solid sill course a level high, so a unit
  vaults in over the sill and has half cover at it.
- A wall with an opening a unit walks through (the grey house's arcade) is open
  in whole tiles at the two levels a unit fills, the wall above it on piers at the
  corners between the tiles: any piece in an edge's slot shuts it to the rules.
- Upper floors are reached only where the art draws a way up (the user's
  choice): poke_j draws none, so every building is one storey open to its roof.
- Corners where four tiles meet are decoration to the fight: the houses' corner
  posts and the grey house's piers stand there.
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


def gable_pitch(m, x0, x1, y0, y1, base, pitch, labels, ridge, edge, cartoon, ov=3, verge=3, thick=3, band=3,
                pattern=None):
    """A gable roof over the walls on boundaries x0, x1 (outer faces x0 - 1 and x1)
    and y0, y1, its ridge along y midway between them, its underside rising [pitch]
    voxels for each voxel in from the walls' outer faces (a fraction: the art's
    pitches are no whole number), [thick] voxels of shingles; eaves [ov] out,
    drooping a little, verges [verge] past the gables; a light band [band] voxels
    either side of the ridge, the eaves and verges [edge]; [pattern](s, a), if
    given, paints the surface in place of shingles (s up the slope from the eave,
    a along it). Returns under(x), its underside at x, for the gables under it."""
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
        return pattern(d + ov, y) if pattern else shingles(d + ov, y, cartoon, labels)

    cols = [(x, y) for x in range(x0 - 1 - ov, x1 + ov + 1) for y in range(ya, yb + 1)]
    fill_roof(m, cols, lambda x, y: under(x), lambda x, y: under(x) + thick - 1, paint)
    return under


def timber_frame(wall, u0, u1, z0, z1, label, step):
    """Dark posts across a wall face, a voxel proud, every [step] voxels from u0 to u1."""
    for u in range(u0, u1 + 1, step):
        for z in range(z0, z1 + 1):
            wall.put(u, -1, z, label)


# ----------------------------------------------------------------------------
# Shapes the poke_j buildings share.

def ashlar(u, z, cartoon, labels):
    """Stone along a wall face by u (along it) and z: courses four voxels tall (eight
    in Cartoon) from the floor, blocks eight voxels long (sixteen) staggered half a
    block a course, the joints a shade darker; in Base a few blocks lighter, on a
    rule that repeats every 16 voxels. [labels] (stone, light, line)."""
    stone, light, line = labels
    ch = 8 if cartoon else 4
    bl = 16 if cartoon else 8
    course = (z - 16) // ch
    shift = (bl // 2) * (course % 2)
    if (z - 16) % ch == ch - 1 or (u - 8 + shift) % bl == 0:
        return line
    if cartoon:
        return stone
    block = ((u - 8 + shift) % 16) // bl
    return light if (block + course) % 4 == 1 else stone


def tile_rows(s, cartoon, labels):
    """A roof tile's label by [s], voxels up the slope from the eave: rows four voxels
    deep (eight in Cartoon) running along the ridge, as the art draws them, a darker
    line at each row's foot and in Base every other row a shade lighter; no joints
    across the rows, as the art draws none."""
    light, base, shade, line = labels
    rowh = 8 if cartoon else 4
    if s % rowh == 0:
        return line
    if cartoon:
        return base
    return light if (s // rowh) % 2 else base


# ----------------------------------------------------------------------------
# The red house (three in poke_j.jpg): five tiles by three, one storey: cream stone
# walls between dark corner posts, a dark beam round it at the fifth course; a steep
# gable roof of red tiles, its ridge front to back, the eaves seven voxels out, as
# drawn, dark barge boards under the verges; a stone chimney at the back of the
# left slope; the front gable half-timbered over a fan window (a post up its
# middle, two braces from its foot out to the roof); the front: the red door
# (tile 1) in a dark frame, a window of four panes (tile 3).

def red_house(cartoon):
    m = Model(5, 3, 10, "PokeJ_RedHouse")
    floor = Z(1)
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    x0, x1, y0, y1 = X(0), X(5), Y(0), Y(3)            # walls on x 8, 88 and y 8, 56
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front, back = walls["front"], walls["back"]
    EAVE = 96                                          # the side walls' top, under the eaves
    stone = ("rh_stone", "rh_stone_light", "rh_stone_line")

    def face(u, z):
        if z < 18:
            return "rh_post"
        if 64 <= z < 72:
            return "rh_post" if z in (64, 71) else "rh_beam"
        return ashlar(u, z, cartoon, stone)

    for key, wall in walls.items():
        u0, u1 = spans[key]
        wall.fill(u0 - 1, u1 + 1, floor, EAVE - 1, face)
        # The beam, a voxel proud all round, as drawn.
        for u in range(u0 - 1, u1 + 2):
            for z in range(64, 72):
                wall.put(u, -1, z, "rh_post" if z in (64, 71) else "rh_beam")

    # The front: the door in tile 1 (closed), red boards; its dark frame five voxels a
    # side and a lintel over it, a voxel proud, as drawn.
    m.doors += [("ey", 1, 0, 1), ("ey", 1, 0, 2)]
    d0 = X(1)                                          # x 24..39
    for u in range(d0, d0 + 16):
        k = u - d0
        for z in range(floor, 48):
            if k in (0, 15) or z in (floor, 47):
                label = "rh_door_dark"
            else:
                label = "rh_door_line" if (k - 1) % (7 if cartoon else 3) == 0 else "rh_door"
            front.put(u, 0, z, label)
            front.put(u, 1, z, label)
    for u in list(range(d0 - 5, d0)) + list(range(d0 + 16, d0 + 21)):
        for z in range(floor, 48):
            for w in (-1, 0, 1):
                front.put(u, w, z, "rh_frame")
    for u in range(d0 - 5, d0 + 21):
        for z in range(48, 56):
            for w in (-1, 0, 1):
                front.put(u, w, z, "rh_frame")

    def window(wall, c):
        """A window of four panes, centred at u = c (a tile's middle): a dark frame,
        light bars, glass in levels 2 and 3 over the sill course, its head level with
        the door's lintel, as drawn."""
        wall.pane(c - 8, c + 7, 31, 56, "rh_frame", "glass_rh", inner="rh_frame" if cartoon else None,
                  bars=((c - 1, None), (c, None), (None, 44)), bar_label="rh_bar")
        for u in range(c - 8, c + 8):
            wall.put(u, -1, 31, "rh_frame")

    window(front, X(3) + 8)
    # The unseen sides and back: windows of the front's kind.
    for key in ("left", "right"):
        window(walls[key], Y(1) + 8)
    for c in (X(1) + 8, X(3) + 8):
        window(back, c)

    # The roof: steep, its ridge front to back over x 47 and 48, rising 1.1 for each
    # voxel in (to z 142, as drawn), three voxels of red tiles in rows along the
    # ridge, a dark line along the ridge; the eaves seven voxels out, the verges two.
    labels = ("rh_roof_light", "rh_roof", "rh_roof_shade", "rh_roof_line")
    OV, VERGE = 7, 2
    under = gable_pitch(m, x0, x1, y0, y1, EAVE, 1.1, labels, "rh_roof_line", "rh_roof_edge", cartoon,
                        ov=OV, verge=VERGE, thick=3, band=1, pattern=lambda s, a: tile_rows(s, cartoon, labels))
    # The barge boards under the verges, front and back, as drawn: dark, five voxels deep.
    m.role_now = "roof"
    for x in range(x0 - 1 - OV, x1 + OV + 1):
        b = under(x)
        for y in (y0 - 1 - VERGE, y1 + VERGE):
            for z in range(b - (6 if cartoon else 5), b):
                m.put(x, y, z, "rh_roof_edge")
    m.role_now = "mid"

    # The gables, front and back, from the beam up to the roof's underside: cream
    # stone, half-timbered as drawn: a post up the middle and two braces from its foot
    # out to the roof, a voxel proud, and between them the fan window, its arc in a
    # dark frame, its glass a voxel back; the timbers are its bars.
    pw = 3.0 if cartoon else 2.0                       # half the post's width
    bw = 2.0 if cartoon else 1.5                       # half a brace's width
    ring = 3.0 if cartoon else 2.0                     # the arc's frame
    SLOPE = 2.6                                        # a brace climbs 2.6 voxels a voxel out
    CX, FOOT, A, B = 48.0, 72, 22.0, 46.0              # the fan: about x 47.5, from z 72, 22 a side, 46 tall

    def timber(u, z):
        off = abs(u + 0.5 - CX)
        return off <= pw or abs(off - (z + 0.5 - FOOT) / SLOPE) <= bw

    def in_fan(u, z, grow=0.0):
        dx = (u + 0.5 - CX) / (A + grow)
        dz = (z + 0.5 - FOOT) / (B + grow)
        return dx * dx + dz * dz < 1.0

    for wall in (front, back):
        for u in range(x0 - 1, x1 + 1):
            for z in range(FOOT, under(u)):
                if timber(u, z):
                    for w in (-1, 0, 1):
                        wall.put(u, w, z, "rh_timber")
                elif in_fan(u, z):
                    wall.erase(u, 0, z)
                    wall.put(u, 1, z, "glass_fan")
                elif in_fan(u, z, ring):
                    for w in (-1, 0, 1):
                        wall.put(u, w, z, "rh_timber")
                else:
                    label = ashlar(u, z, cartoon, stone)
                    wall.put(u, 0, z, label)
                    wall.put(u, 1, z, label)

    # Dark corner posts, a voxel or two proud, up to the eaves' underside.
    half = 4 if cartoon else 3
    for cx in (x0, x1):
        for cy in (y0, y1):
            for x in range(cx - half, cx + half):
                for y in range(cy - half, cy + half):
                    for z in range(floor, min(EAVE, under(x))):
                        m.put(x, y, z, "rh_post", "corner")

    # The chimney at the back of the left slope, as drawn: cream stone in courses, a
    # darker head under its light cap, the flue dark; its top over the ridge.
    cx0, cx1, cy0, cy1, ctop = 16, 29, 38, 49, 151
    chimney(m, cx0, cx1, cy0, cy1, ctop, "rh_chim", "rh_chim_cap", "rh_flue", "rh_chim_shade",
            (19, 26, 41, 46, 6), cartoon, lip=2 if cartoon else 1, shade="rh_chim_shade")
    for (x, y, z), label in list(m.v.items()):
        if cx0 <= x <= cx1 and cy0 <= y <= cy1 and label in ("rh_chim", "rh_chim_shade"):
            if z >= ctop - 18:
                m.v[(x, y, z)] = "rh_chim_top"
            elif label == "rh_chim" and not cartoon and z % 4 == 0:
                m.v[(x, y, z)] = "rh_chim_line"

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 4}]
    m.figure = (1, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The grey house (the one at the top of poke_j.jpg): three parts, stepped as drawn:
# a low wing on the left (two tiles by two, set a tile back), the middle (three
# tiles by three) and the right part (two tiles by four, a tile in front of the
# middle); one storey, the wing's walls two and a half courses, the rest's four; cream stone
# walls, white posts at the corners; flat grey roofs with standing seams and dark
# edges in three bands, the wing's lower; a skylight on the right part's
# roof and three white vents at the back, as drawn. The front: the wing's window
# over a flower box; the middle's door (tile 3: wood, a pane in its top) under a
# long window; the right part's window of four panes over two flower boxes.
# Inside, one room: an arcade on piers opens the wing to the middle, and the
# middle is open to the right part.

def grey_house(cartoon):
    wing = {(i, j) for i in (0, 1) for j in (2, 3)}
    middle = {(i, j) for i in (2, 3, 4) for j in (1, 2, 3)}
    right = {(i, j) for i in (5, 6) for j in range(4)}
    m = Model(7, 4, 7, "PokeJ_GreyHouse", wing | middle | right)
    floor = Z(1)
    foundation(m, m.footprint, lambda x, y: stone_tiles(x, y, cartoon))
    EAVE, LOW = Z(5), 56                               # the walls' top z 80, the wing's z 56, as drawn
    stone = ("gh_stone", "gh_stone_light", "gh_stone_line")

    def face(u, z):
        return "gh_plinth" if z < 18 else ashlar(u, z, cartoon, stone)

    def wall(axis, line, out):
        return Wall(m, axis, line, out)

    # The wing: x 8..40, y 40..72.
    wing_front, wing_left, wing_back = wall("x", Y(2), -1), wall("y", X(0), -1), wall("x", Y(4), +1)
    wing_front.fill(X(0) - 1, X(2), floor, LOW - 1, face)
    wing_left.fill(Y(2) - 1, Y(4), floor, LOW - 1, face)
    wing_back.fill(X(0) - 1, X(2), floor, LOW - 1, face)
    # The middle: x 40..88, y 24..72; its left wall over the wing's roof only, the
    # arcade under it.
    mid_front, mid_left, mid_back = wall("x", Y(1), -1), wall("y", X(2), -1), wall("x", Y(4), +1)
    mid_front.fill(X(2) - 1, X(5), floor, EAVE - 1, face)
    mid_left.fill(Y(1) - 1, Y(2) - 1, floor, EAVE - 1, face)
    mid_left.fill(Y(2), Y(4), LOW, EAVE - 1, face)
    mid_back.fill(X(2), X(5), floor, EAVE - 1, face)
    # The right part: x 88..120, y 8..72, open to the middle behind its side.
    r_front, r_left, r_right, r_back = wall("x", Y(0), -1), wall("y", X(5), -1), wall("y", X(7), +1), wall("x", Y(4), +1)
    r_front.fill(X(5) - 1, X(7), floor, EAVE - 1, face)
    r_left.fill(Y(0) - 1, Y(1) - 1, floor, EAVE - 1, face)
    r_right.fill(Y(0) - 1, Y(4), floor, EAVE - 1, face)
    r_back.fill(X(5), X(7), floor, EAVE - 1, face)

    def window(w, ua, ub, z0, z1, mullions=(), transom=None):
        """Glass in a white frame across u ua..ub, from z0 + 1 to z1 - 1, its sill a
        voxel proud."""
        bars = tuple((u, None) for u in mullions) + (((None, transom),) if transom else ())
        w.pane(ua, ub, z0, z1, "gh_frame", "glass_gh", inner="gh_frame" if cartoon else None, bars=bars)
        for u in range(ua, ub + 1):
            w.put(u, -1, z0, "gh_frame")

    def flower_box(w, ua, ub):
        """A box of flowers at the foot of a wall, four voxels out, as drawn."""
        depth, top = 4, floor + 7
        for u in range(ua, ub + 1):
            for d in range(1, depth + 1):
                for z in range(floor, top + 1):
                    rim = z == top and (u in (ua, ub) or d == depth)
                    w.put(u, -d, z, "gh_box_dark" if rim or z == floor else "gh_box")
                if cartoon:
                    for z in (top + 1, top + 2):
                        w.put(u, -d, z, "gh_flower")
                    continue
                if u in (ua, ub) or d == depth:
                    continue
                h = ((u % 16) * 5 + d * 3) % 7
                w.put(u, -d, top + 1, "gh_leaf" if h == 3 else ("gh_flower_dark" if h == 5 else "gh_flower"))
                if h in (0, 2, 4):
                    w.put(u, -d, top + 2, "gh_flower")

    # The wing's front: a window of two panes over the tile boundary, a flower box
    # under it, as drawn.
    window(wing_front, X(1) - 10, X(1) + 9, 31, 50, (X(1) - 1, X(1)))
    flower_box(wing_front, X(0) + 2, X(2) - 3)
    # The middle's front: the door in tile 3 (closed): wood in a dark frame, a pane in
    # its top; the long window over it, as drawn.
    m.doors += [("ey", 3, 1, 1), ("ey", 3, 1, 2)]
    d0 = X(3)                                          # x 56..71
    for u in range(d0, d0 + 16):
        k = u - d0
        for z in range(floor, 48):
            if k in (0, 15) or z in (floor, 47):
                label = "gh_door_dark"
            elif 3 <= k <= 12 and 37 <= z <= 44:
                mid_front.erase(u, 0, z)
                mid_front.put(u, 1, z, "glass_gh_door")
                continue
            elif k in (2, 13) or z in (36, 45):
                label = "gh_door_dark"
            else:
                label = "gh_door_light" if (k - 1) % (7 if cartoon else 4) == 0 else "gh_door"
            mid_front.put(u, 0, z, label)
            mid_front.put(u, 1, z, label)
    for z in range(floor, 49):
        for u in (d0 - 1, d0 + 16):
            mid_front.put(u, 0, z, "gh_door_dark")
            mid_front.put(u, 1, z, "gh_door_dark")
    for u in range(d0 - 1, d0 + 17):
        mid_front.put(u, 0, 48, "gh_door_dark")
        mid_front.put(u, 1, 48, "gh_door_dark")
    window(mid_front, d0 - 10, d0 + 25, 57, 78, (d0 + 7, d0 + 8))
    # The right part's front: a window of four panes over the tile boundary, a light
    # apron under it and two flower boxes, as drawn.
    window(r_front, X(6) - 12, X(6) + 11, 31, 63, (X(6) - 1, X(6)), 47)
    r_front.fill(X(6) - 12, X(6) + 11, 18, 30, "gh_apron")
    flower_box(r_front, X(6) - 13, X(6) - 2)
    flower_box(r_front, X(6) + 1, X(6) + 12)
    # The unseen sides and backs: windows of the front's kinds.
    window(wing_left, Y(3), Y(3) + 15, 31, 50, (Y(3) + 7, Y(3) + 8))
    window(wing_back, X(1) - 10, X(1) + 9, 31, 50, (X(1) - 1, X(1)))
    window(mid_back, X(3), X(3) + 15, 31, 63, (X(3) + 7, X(3) + 8), 47)
    window(r_right, Y(2) - 12, Y(2) + 11, 31, 63, (Y(2) - 1, Y(2)), 47)
    window(r_back, X(6) - 12, X(6) + 11, 31, 63, (X(6) - 1, X(6)), 47)

    # White posts at the outer corners, as drawn; stone piers under the arcade.
    half = 3 if cartoon else 2
    for (cx, cy, z0, z1) in ((X(0), Y(2), floor, LOW), (X(0), Y(4), floor, LOW), (X(2), Y(1), floor, EAVE),
                             (X(5), Y(1), floor, EAVE), (X(5), Y(0), floor, EAVE), (X(7), Y(0), floor, EAVE),
                             (X(7), Y(4), floor, EAVE), (X(2), Y(4), LOW, EAVE)):
        post(m, cx, cy, z0, z1 - 1, "gh_post", half)
    for cy in (Y(2), Y(3)):
        post(m, X(2), cy, floor, LOW - 1, "gh_stone", 2)

    # The roofs: flat, as drawn, a level thick, two voxels out past the walls' outer
    # faces; their edges dark in three bands, their tops grey with standing seams
    # along y (the art's stripes), a dark line round the top.
    def seam(x):
        p, dark = (16, 6) if cartoon else (8, 3)
        k = (x - 8) % p
        return "gh_seam" if k >= p - dark else ("gh_roof_light" if k == 0 and not cartoon else "gh_roof")

    def roof(cols, z0, role_of):
        z1 = z0 + 15
        cols = set(cols)
        for (x, y) in cols:
            edge = any((x + dx, y + dy) not in cols for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            role = role_of(x, y)
            for z in range(z0, z1 + 1):
                if z == z1:
                    label = "gh_roof_edge" if edge else seam(x)
                elif edge:
                    d = z - z0
                    label = "gh_fascia_dark" if d < 5 else ("gh_fascia" if d < 11 else "gh_fascia_light")
                else:
                    label = "ceiling" if z == z0 else "gh_fascia"
                m.put(x, y, z, label, role)

    main_cols = [(x, y) for x in range(X(2) - 3, X(7) + 3) for y in range(Y(1) - 3, Y(4) + 3)]
    main_cols += [(x, y) for x in range(X(5) - 3, X(7) + 3) for y in range(Y(0) - 3, Y(1) - 3)]
    # The main roof's eave over the wing hangs from the middle's left wall: its edge.
    roof(main_cols, EAVE, lambda x, y: "ex" if x < X(2) else "roof")
    wing_cols = [(x, y) for x in range(X(0) - 3, X(2) - 1) for y in range(Y(2) - 3, Y(4) + 3)]
    roof(wing_cols, LOW, lambda x, y: "roof")

    # The skylight on the right part's roof, as drawn: a pane in a white frame two
    # voxels over the roof, the roof open under it; in Base light streaks across it.
    sx0, sx1, sy0, sy1 = X(5) + 3, X(7) - 4, Y(0) + 5, Y(2) - 2
    fw = 3 if cartoon else 2
    m.role_now = "roof"
    for x in range(sx0, sx1 + 1):
        for y in range(sy0, sy1 + 1):
            if sx0 + fw <= x <= sx1 - fw and sy0 + fw <= y <= sy1 - fw:
                for z in range(EAVE, EAVE + 16):
                    m.erase(x, y, z)
                streak = (not cartoon and (x - y) % 10 in (0, 1) and x > (sx0 + sx1) // 2 - 3
                          and y < (sy0 + sy1) // 2 + 3)
                m.put(x, y, EAVE + 16, "glass_sky_light" if streak else "glass_sky")
            else:
                for z in (EAVE + 15, EAVE + 16, EAVE + 17):
                    m.put(x, y, z, "gh_sky_frame")
    for x in range(sx0 + fw - 1, sx1 - fw + 2):
        for y in range(sy0 + fw - 1, sy1 - fw + 2):
            for z in range(EAVE, EAVE + 15):
                if (x, y, z) in m.v and m.v[(x, y, z)] != "ceiling":
                    m.v[(x, y, z)] = "gh_well"
    m.role_now = "mid"

    # The vents at the back, as drawn: a light grey stack under a white cap, a dark
    # slot across the cap's front: two on the main roof, one on the wing's.
    def vent(vx, vy, base):
        m.box(vx + 2, vx + 7, vy + 2, vy + 5, base, base + 7, "gh_vent_body", "mid")
        m.box(vx, vx + 9, vy, vy + 7, base + 8, base + 15,
              lambda x, y, z: "gh_vent_shade" if (x == vx + 9 and not cartoon) else "gh_vent", "mid")
        for x in range(vx + 2, vx + 8):
            for z in ((base + 10, base + 11, base + 12) if cartoon else (base + 11, base + 12)):
                m.put(x, vy, z, "gh_vent_slot", "mid")

    for vx in (X(2) + 5, X(3) + 4):
        vent(vx, Y(3) + 2, EAVE + 16)
    vent(X(0) + 8, Y(3) + 2, LOW + 16)

    m.storeys = [{"stand": 1, "tiles": wing | middle | right, "entry": "vault", "cut": 3}]
    m.figure = (3, 0, 1, 200)
    return m


BUILDINGS = {
    "RedHouse": red_house,
    "GreyHouse": grey_house,
}


def build(kind, cartoon):
    return BUILDINGS[kind](cartoon)
