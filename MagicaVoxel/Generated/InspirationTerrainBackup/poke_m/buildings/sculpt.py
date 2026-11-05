"""The poke_m buildings' geometry, on VCOM's grid, as the poke_j buildings are
drawn (their helpers copied from poke_j/buildings/sculpt.py).

poke_m.png is native pixel art: a tile is 16 of its pixels (its stairs are three
tiles across, its bridge deck five by three), so a voxel is one of its pixels
across and in depth. Its buildings' heights are foreshortened to 0.5 (their doors
are 15 and 16 pixels tall for the two levels a door fills), a little less than
the 0.46 of the earlier images.

Every model is drawn on the game's tile grid so that it can be cut into the
game's 16-cubed pieces cleanly (a middle, an edge or a corner slot each):

- 16 voxels a tile. Tile boundaries run at x = 8 + 16i and y = 8 + 16j: every
  canvas has half a tile of margin all round the footprint, which holds the
  outer halves of the edge pieces (eaves, verges, sills, log ends, porches).
- Levels are z = 16k. Level 0 (z 0-15) is a building's own floor, a foundation
  standing in for the map's ground blocks under it. Units stand on the top of a
  cell: a floor at level 0 is stood on at level 1.
- A wall is two voxels thick across its tile boundary B (voxels B - 1 and B),
  at the levels a unit fills; what stands higher, over the storey (the lodge's
  upper part), may stand where the art draws it.
- A door is closed, as drawn, and each leaf fills exactly one doorway slot: one
  tile wide, the two levels a unit fills (the user's choice, 2026-10-28).
- A window keeps within its tile, or stands over a tile boundary, each half its
  own window piece. Its glass is over a solid sill course a level high, so a unit
  vaults in over the sill and has half cover at it.
- Upper floors are reached only where the art draws a way up (the user's
  choice): poke_m draws none, so every building is one storey open to its roof.
- Corners where four tiles meet are decoration to the fight: the cabin's log ends
  and the lodge's corner posts stand there.
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
# Shapes the poke_m buildings share.

def courses(u, z, cartoon, labels, height=4, block=8):
    """A face in courses [height] voxels tall (twice in Cartoon) from the floor,
    joints every [block] voxels (twice in Cartoon) staggered half a block a course,
    the mortar a shade darker: [labels] (face, mortar). Repeats every 16 voxels."""
    face, mortar = labels
    ch = height * (2 if cartoon else 1)
    bl = block * (2 if cartoon else 1)
    course = (z - 16) // ch
    if (z - 16) % ch == ch - 1 or (u - 8 + (bl // 2) * (course % 2)) % bl == 0:
        return mortar
    return face


def stripes(a, cartoon, labels):
    """Boards running down a roof's slope, by [a] across them: two voxels dark, two
    light (five and three in Cartoon, eight a period), as the art's alternate."""
    dark, light = labels
    if cartoon:
        return dark if (a - 8) % 8 < 5 else light
    return dark if (a - 8) % 4 < 2 else light


def slate(s, a, cartoon, labels):
    """Slates by [s] up the slope and [a] along it: rows four voxels deep (eight in
    Cartoon), joints every eight (sixteen) staggered a row, each slate one of the
    art's four greys on a rule that repeats every 16 voxels; the joints darkest."""
    light, base, mid, dark = labels
    rowh = 8 if cartoon else 4
    jw = 16 if cartoon else 8
    row = s // rowh
    off = (jw // 2) * (row % 2)
    if s % rowh == 0 or (a - 8 + off) % jw == 0:
        return dark
    if cartoon:
        return base
    tone = (((a - 8 + off) % 16) // jw * 3 + (row % 4) * 2) % 5
    return (light, base, mid, base, light)[tone]


# ----------------------------------------------------------------------------
# The log cabin (by the marsh in poke_m.png): four tiles by two, one storey of
# four logs: log walls, the side walls' logs running out past the corners in
# round ends, as drawn; a steep gable roof of grey slates, its ridge front to back
# under a raised ridge cap, dark verges; the front gable of dark boards over a
# light beam, a king post up its middle and rafters under the verges; the front:
# the plank door (tile 1) and a window of two panes (tile 2).

def log_cabin(cartoon):
    m = Model(4, 2, 6, "PokeM_LogCabin")
    floor = Z(1)
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    x0, x1, y0, y1 = X(0), X(4), Y(0), Y(2)            # walls on x 8, 72 and y 8, 40
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front, back = walls["front"], walls["back"]
    EAVE = 48                                          # four logs, z 16-47, as drawn

    def log(u, z):
        """A log eight voxels tall: its seam dark, a shade under its rounded top."""
        k = (z - 16) % 8
        if k == 0:
            return "lc_log_dark"
        if cartoon:
            return "lc_log_light" if k == 7 else "lc_log"
        return "lc_log_shade" if k == 1 else ("lc_log_light" if k >= 6 else "lc_log")

    for key, wall in walls.items():
        u0, u1 = spans[key]
        wall.fill(u0 - 1, u1 + 1, floor, EAVE - 1, log)

    # The side walls' logs run out four voxels past the front and back walls, each in
    # a round end, as drawn: dark bark round a light heart.
    for cx in (x0, x1):
        for ya, yb, face in ((y0 - 5, y0 - 2, y0 - 5), (y1 + 1, y1 + 4, y1 + 4)):
            for c in range(4):
                zc = floor + 8 * c + 4
                for x in range(cx - 4, cx + 4):
                    for z in range(floor + 8 * c, floor + 8 * c + 8):
                        dx, dz = x + 0.5 - cx, z + 0.5 - zc
                        r = (dx * dx + dz * dz) ** 0.5
                        if r > 4.2:
                            continue
                        for y in range(ya, yb + 1):
                            if y != face:
                                label = "lc_log_dark" if r > 3.4 else "lc_log"
                            elif r > 3.0:
                                label = "lc_log_dark"
                            elif cartoon:
                                label = "lc_end"
                            else:
                                label = "lc_log" if r > 2.0 else ("lc_end" if r > 0.9 else "lc_log_light")
                            m.put(x, y, z, label, "corner")

    # The front: the door in tile 1 (closed), planks in a dark frame, a light handle,
    # as drawn; the window in tile 2.
    m.doors += [("ey", 1, 0, 1), ("ey", 1, 0, 2)]
    d0 = X(1)                                          # x 24..39
    for u in range(d0, d0 + 16):
        k = u - d0
        for z in range(floor, 48):
            if k in (0, 15) or z in (floor, 47):
                label = "lc_outline"
            elif (k - 1) % (7 if cartoon else 4) == 3:
                label = "lc_log_dark"
            else:
                board = (k - 1) // (7 if cartoon else 4)
                label = "lc_door_light" if (not cartoon and board == 1 and k % 4 == 2) else (
                    "lc_log_light" if board % 2 == 0 else "lc_log")
            front.put(u, 0, z, label)
            front.put(u, 1, z, label)
    for u in range(d0 + 2, d0 + 5):
        for z in (30, 31):
            front.put(u, -1, z, "lc_handle")

    def window(wall, ua):
        """A window of two panes across u ua..ua + 15: a light frame, a dark middle
        bar, glass in level 2 over the sill course with light streaks across it, a
        log sill under it."""
        wall.pane(ua, ua + 15, 31, 47, "lc_frame", "glass_lc", inner="lc_frame" if cartoon else None,
                  bars=((ua + 7, None), (ua + 8, None)), bar_label="lc_log_shade")
        if not cartoon:
            for u in range(ua + 1, ua + 15):
                for z in range(32, 47):
                    if (u - z) % 7 in (0, 1) and wall.get(u, 1, z) == "glass_lc":
                        wall.put(u, 1, z, "glass_lc_light")
        for u in range(ua - 1, ua + 17):
            wall.put(u, -1, 30, "lc_log_shade")
            wall.put(u, -1, 31, "lc_log_shade")

    window(front, X(2))
    # The unseen sides and back: windows of the front's kind.
    for key in ("left", "right"):
        window(walls[key], Y(1) - 8)
    window(back, X(2) - 8)

    # The roof: steep, its ridge front to back over x 39 and 40, rising 0.8 for each
    # voxel in (to z 75, as drawn), three voxels of grey slates; the eaves three out,
    # the verges one, dark at their edges.
    labels = ("lc_slate_light", "lc_slate", "lc_slate_mid", "lc_slate_dark")
    under = gable_pitch(m, x0, x1, y0, y1, EAVE, 0.8, labels, "lc_slate_mid", "lc_outline", cartoon,
                        ov=3, verge=1, thick=3, band=1, pattern=lambda s, a: slate(s, a, cartoon, labels))
    # The ridge cap, eight voxels wide and two high along the ridge, as drawn.
    m.role_now = "roof"
    ya, yb = y0 - 2, y1 + 1
    for x in range(36, 44):
        top = under(x) + 2
        for y in range(ya, yb + 1):
            for z in (top + 1, top + 2):
                edge = x in (36, 43) or y in (ya, yb)
                m.put(x, y, z, "lc_outline" if edge and z == top + 1 else ("lc_slate_light" if z == top + 2 else "lc_slate"))
    m.role_now = "mid"

    # The beam over the front and back walls, a light log a voxel proud, as drawn,
    # under the roof where the eaves come down past it.
    for wall in (front, back):
        for u in range(x0 - 1, x1 + 1):
            for z in range(EAVE, min(EAVE + 8, under(u))):
                k = z - EAVE
                label = "lc_log_dark" if k == 0 else ("lc_log_light" if k >= 5 else "lc_log")
                for w in (-1, 0, 1):
                    wall.put(u, w, z, label)

    # The gables, front and back, over the beam: dark boards with light battens, a
    # king post up the middle and rafters under the verges, a voxel proud, as drawn.
    rafter = 4 if cartoon else 3
    for wall in (front, back):
        for u in range(x0 - 1, x1 + 1):
            top = under(u)
            for z in range(EAVE + 8, top):
                if 38 <= u <= 41 or (cartoon and 37 <= u <= 42):
                    for w in (-1, 0, 1):
                        wall.put(u, w, z, "lc_log_light" if u in (38, 39) else "lc_log")
                elif z >= top - rafter:
                    for w in (-1, 0, 1):
                        wall.put(u, w, z, "lc_log")
                else:
                    batten = (u - 8) % (8 if cartoon else 4) == 0
                    wall.put(u, 0, z, "lc_log_shade" if batten else "lc_gable")
                    wall.put(u, 1, z, "lc_gable")

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 3}]
    m.figure = (1, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The lodge (two in poke_m.png, each cut off by the image's edge: the one at the
# bottom left shows its front but for its left end, the one at the bottom only its
# roof, whole across): four tiles by two, one storey of three courses, cream brick
# walls on a stone plinth between big timber corner posts; a dark fascia over them
# and a low gable roof of brown boards, its ridge along the front; rising through it
# in the middle an upper part with light boarded walls under a low gable roof of its
# own under a light ridge board, as drawn. The front: a window over a tile boundary, its dark sill;
# the door (tile 2) between two posts under a porch beam.

def lodge(cartoon):
    m = Model(4, 2, 7, "PokeM_Lodge")
    floor = Z(1)
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    x0, x1, y0, y1 = X(0), X(4), Y(0), Y(2)            # walls on x 8, 72 and y 8, 40
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front, back = walls["front"], walls["back"]
    EAVE = Z(4)                                        # the walls' top, z 64
    brick = ("lg_brick", "lg_mortar")

    def face(u, z):
        if z < 20:
            return "lg_plinth_dark" if z in (16, 19) else "lg_plinth"
        if z >= 56:
            return "lg_soffit_dark" if z == 56 else "lg_soffit"
        return courses(u, z, cartoon, brick)

    for key, wall in walls.items():
        u0, u1 = spans[key]
        wall.fill(u0 - 1, u1 + 1, floor, EAVE - 1, face)

    def window(wall, ua):
        """A window across u ua..ua + 15 in a dark frame, glass in level 2 over the
        sill course with a light streak across it, a dark sill under it, as drawn."""
        wall.pane(ua, ua + 15, 31, 47, "lg_frame", "glass_lg", inner="lg_frame" if cartoon else None)
        if not cartoon:
            for u in range(ua + 1, ua + 15):
                for z in range(32, 47):
                    if (u - z + 40) % 9 in (0, 1, 2) and wall.get(u, 1, z) == "glass_lg":
                        wall.put(u, 1, z, "glass_lg_light")
        for u in range(ua - 1, ua + 17):
            for z in (28, 29, 30):
                wall.put(u, -1, z, "lg_sill")
            wall.put(u, -2, 30, "lg_sill")

    # The front: the window over the boundary between tiles 0 and 1, as drawn.
    window(front, X(1) - 8)
    # The door in tile 2 (closed): grey-brown planks in a dark frame, a light band and
    # handle; a transom over it; posts either side and a porch beam over them, as drawn.
    m.doors += [("ey", 2, 0, 1), ("ey", 2, 0, 2)]
    d0 = X(2)                                          # x 40..55
    for u in range(d0, d0 + 16):
        k = u - d0
        for z in range(floor, 48):
            if k in (0, 15) or z in (floor, 47):
                label = "lg_door_frame"
            elif z in (30, 31):
                label = "lg_door_light"
            elif not cartoon and (k - 1) % 3 == 2:
                label = "lg_door_line"
            elif cartoon and (k - 1) % 7 == 6:
                label = "lg_door_line"
            else:
                label = "lg_door"
            front.put(u, 0, z, label)
            front.put(u, 1, z, label)
    for u in range(d0 + 3, d0 + 6):
        for z in (36, 37):
            front.put(u, -1, z, "lg_handle")
    front.fill(d0, d0 + 15, 48, 51, "lg_transom")
    pw = 6 if cartoon else 5
    for ua in (d0 - pw, d0 + 16):
        for u in range(ua, ua + pw):
            k = u - ua
            for z in range(floor, 52):
                label = "lg_post_line" if k in (0, pw - 1) else ("lg_post_light" if k == 1 else (
                    "lg_post_shade" if k == pw - 2 else "lg_post"))
                for w in (-2, -1, 0, 1):
                    front.put(u, w, z, label)
    for u in range(d0 - pw - 2, d0 + 16 + pw + 2):
        for z in range(52, 64):
            for w in (-3, -2, -1, 0, 1):
                edge = u in (d0 - pw - 2, d0 + 15 + pw + 2) or z in (52, 63)
                label = "lg_post_line" if edge else ("lg_post_light" if z >= 60 else (
                    "lg_post_shade" if z <= 54 else "lg_post"))
                front.put(u, w, z, label)
    # The unseen back and sides: windows of the front's kind.
    for ua in (X(1) - 8, X(3) - 8):
        window(back, ua)
    for key in ("left", "right"):
        window(walls[key], Y(1) - 8)

    # Big timber posts at the corners, light on their left, shaded on their right,
    # as drawn (the left end, cut off in the art, as the right).
    half = 5 if cartoon else 4
    for cx in (x0, x1):
        for cy in (y0, y1):
            for x in range(cx - half, cx + half):
                for y in range(cy - half, cy + half):
                    k = x - (cx - half)
                    edge = x in (cx - half, cx + half - 1) and y in (cy - half, cy + half - 1)
                    label = "lg_post_line" if edge else (
                        "lg_post_light" if k <= 2 else ("lg_post_shade" if k >= 2 * half - 3 else "lg_post"))
                    for z in range(floor, EAVE):
                        m.put(x, y, z, label, "corner")

    # The lower roof: a fascia of dark boards over the walls' top (z 64-71), and over
    # it a gable over the whole of it, its ridge along x over y 23 and 24, rising 0.5 a
    # voxel in from the walls (to z 82), its eaves three out at the front and back
    # and eight at the ends over barge boards, its boards dark in front and light
    # behind, a light ridge board where it shows beside the upper part, as drawn; the
    # upper part rises through it.
    for key, wall in walls.items():
        u0, u1 = spans[key]
        for u in range(u0 - 1, u1 + 2):
            for z in range(EAVE, EAVE + 8):
                label = "lg_roof_line" if z in (EAVE, EAVE + 7) else "lg_roof_dark"
                for w in (-1, 0, 1):
                    wall.put(u, w, z, label)
    ux0, ux1, uy0, uy1 = 17, 62, 12, 40               # the upper part's walls' outer faces
    lx0, lx1, ly0, ly1 = x0 - 8, x1 + 7, y0 - 4, y1 + 3   # x 0..79, y 4..43
    lmid = (y0 - 1 + y1) / 2.0                         # 23.5

    def lunder(y):
        d = (y - (y0 - 1)) if y < lmid else (y1 - y)
        return EAVE + 8 + int(math.floor(0.5 * d))

    m.role_now = "roof"
    for x in range(lx0, lx1 + 1):
        for y in range(ly0, ly1 + 1):
            if ux0 <= x <= ux1 and y >= uy0:
                continue                               # the upper part, and behind it
            b = lunder(y)
            edge = x in (lx0, lx1) or y in (ly0, ly1)
            for z in range(b, b + 3):
                if edge:
                    label = "lg_roof_line"
                elif z == b:
                    label = "ceiling" if (x0 <= x < x1 and y0 <= y < y1) else "lg_roof_dark"
                elif y < lmid:
                    label = stripes(x, cartoon, ("lg_roof_dark", "lg_roof"))
                else:
                    label = stripes(x, cartoon, ("lg_roof", "lg_roof_light"))
                m.put(x, y, z, label)
            if edge:
                for z in range(b - 4, b):
                    m.put(x, y, z, "lg_roof_dark")
    # The gable ends over the side walls: boards from the fascia up to the roof.
    for key in ("left", "right"):
        for u in range(y0 - 1, y1 + 1):
            for z in range(EAVE + 8, lunder(u)):
                walls[key].put(u, 0, z, "lg_roof_dark")
                walls[key].put(u, 1, z, "lg_roof_dark")
    # The ridge board beside the upper part, raised a voxel, light, as drawn.
    for x in list(range(lx0, ux0)) + list(range(ux1 + 1, lx1 + 1)):
        for y in range(21, 27):
            top = lunder(y) + 2
            m.put(x, y, top + 1, "lg_roof_line" if y in (21, 26) else "lg_roof_light")
    m.role_now = "mid"

    # The upper part's walls: light boards from the fascia up to z 87, a dark fascia
    # over them (z 88-95) under the upper roof's eaves, as drawn.
    upper = {"front": Wall(m, "x", uy0 + 1, -1), "back": Wall(m, "x", uy1, +1),
             "left": Wall(m, "y", ux0 + 1, -1), "right": Wall(m, "y", ux1, +1)}
    uspan = {"front": (ux0, ux1), "back": (ux0, ux1), "left": (uy0, uy1), "right": (uy0, uy1)}
    board = 6 if cartoon else 3

    def band(u, z):
        if z >= 88:
            return "lg_roof_line" if z in (88, 95) else "lg_roof_dark"
        return "lg_band_line" if (z - 64) % board == board - 1 else "lg_band"

    m.role_now = "roof"
    for key in ("front", "back"):
        ua, ub = uspan[key]
        for u in range(ua, ub + 1):
            for z in range(EAVE, 96):
                upper[key].put(u, 0, z, band(u, z), "roof")
                upper[key].put(u, 1, z, band(u, z), "roof")
    for key in ("left", "right"):
        ua, ub = uspan[key]
        for u in range(ua, ub + 1):
            for z in range(EAVE, 88):
                upper[key].put(u, 0, z, band(u, z), "roof")
                upper[key].put(u, 1, z, band(u, z), "roof")
    m.role_now = "mid"

    # The upper roof: a low gable, its ridge along x over y 26, rising 0.67 a voxel
    # in from the eaves (z 96, three out at the front and back, four at the ends), its
    # boards dark in front and light behind, a light ridge board on it, as drawn.
    rx0, rx1, ry0, ry1 = ux0 - 4, ux1 + 4, uy0 - 3, uy1 + 3
    mid = (uy0 + uy1) / 2.0

    def uunder(y):
        d = (y - uy0) if y < mid else (uy1 - y)
        return 96 + int(math.floor(0.67 * d))

    m.role_now = "roof"
    for x in range(rx0, rx1 + 1):
        for y in range(ry0, ry1 + 1):
            b = uunder(y)
            for z in range(b, b + 3):
                if x in (rx0, rx1) or y in (ry0, ry1):
                    label = "lg_roof_line"
                elif z < b + 1:
                    label = "ceiling" if (ux0 < x < ux1 and uy0 < y < uy1) else "lg_roof_dark"
                elif y < mid:
                    label = stripes(x, cartoon, ("lg_roof_dark", "lg_roof"))
                else:
                    label = stripes(x, cartoon, ("lg_roof", "lg_roof_light"))
                m.put(x, y, z, label)
    # The gable ends of the upper part, light boards up to the roof's underside.
    for key in ("left", "right"):
        for u in range(uy0, uy1 + 1):
            for z in range(88, uunder(u)):
                label = "lg_band_line" if (z - 64) % board == board - 1 else "lg_band"
                upper[key].put(u, 0, z, label, "roof")
                upper[key].put(u, 1, z, label, "roof")
    # The ridge board, five voxels across and raised a voxel, as drawn.
    rb0, rb1 = int(mid) - 2, int(mid) + 2
    for x in range(rx0, rx1 + 1):
        for y in range(rb0, rb1 + 1):
            top = uunder(y) + 2
            for z in (top + 1, top + 2):
                edge = y in (rb0, rb1) or x in (rx0, rx1)
                m.put(x, y, z, "lg_roof_line" if (edge and z == top + 1) else ("lg_roof_light" if z == top + 2 else "lg_roof"))
    m.role_now = "mid"

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 4}]
    m.figure = (2, -1, 1, 200)
    return m


BUILDINGS = {
    "LogCabin": log_cabin,
    "Lodge": lodge,
}


def build(kind, cartoon):
    return BUILDINGS[kind](cartoon)
