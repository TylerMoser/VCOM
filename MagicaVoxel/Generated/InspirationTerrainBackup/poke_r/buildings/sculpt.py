"""The poke_r buildings' geometry, on VCOM's grid, as the poke_o buildings are
drawn (their helpers copied from poke_o/buildings/sculpt.py).

poke_r.png is native pixel art: a tile is 16 of its pixels, so a voxel is one of
its pixels across and in depth. Its heights are foreshortened to 0.375, as in
poke_o.png (every door is 12 pixels tall for its two levels).

Every model is drawn on the game's tile grid so that it can be cut into the
game's 16-cubed pieces cleanly (a middle, an edge or a corner slot each):

- 16 voxels a tile. Tile boundaries run at x = 8 + 16i and y = 8 + 16j: every
  canvas has half a tile of margin all round the footprint, which holds the
  outer halves of the edge pieces (eaves, verges, boards, awnings, handles).
- Levels are z = 16k. Level 0 (z 0-15) is a house's own floor, a foundation
  standing in for the map's ground blocks under it. Units stand on the top of a
  cell: a floor at level 0 is stood on at level 1.
- A wall is two voxels thick across its tile boundary B (voxels B - 1 and B).
- A door is closed, as drawn, and each leaf fills exactly one doorway slot: one
  tile wide, the two levels a unit fills (the user's choice, 2026-10-28).
- A window keeps within its tile, or stands over a tile boundary, each part its
  own window piece. Its glass is over a solid sill course a level high, so a unit
  vaults in over the sill and has half cover at it.
- Upper floors are reached only where the art draws a way up (the user's
  choice): poke_r draws none, so each building is one storey open to its roof.
- Corners where four tiles meet are decoration to the fight: the corner boards
  and bricks stand there.
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
                pattern=None, verge_back=None):
    """A gable roof over the walls on boundaries x0, x1 (outer faces x0 - 1 and x1)
    and y0, y1, its ridge along y midway between them, its underside rising [pitch]
    voxels for each voxel in from the walls' outer faces (a fraction: the art's
    pitches are no whole number), [thick] voxels of shingles; eaves [ov] out,
    drooping a little, verges [verge] past the gables (the back one [verge_back]
    if given); a light band [band] voxels
    either side of the ridge, the eaves and verges [edge]; [pattern](s, a), if
    given, paints the surface in place of shingles (s up the slope from the eave,
    a along it). Returns under(x), its underside at x, for the gables under it."""
    mid = (x0 - 1 + x1) / 2.0
    half = mid - (x0 - 1)

    def d_of(x):
        return (x - (x0 - 1)) if x < mid else (x1 - x)

    def under(x):
        return base + int(math.floor(pitch * d_of(x)))

    ya, yb = y0 - 1 - verge, y1 + (verge if verge_back is None else verge_back)

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
# Shapes the poke_n buildings shared, copied from theirs.

def blocks(u, z, cartoon, labels, height=4, block=8):
    """A face in courses [height] voxels tall (twice in Cartoon) from the floor,
    joints every [block] voxels (twice in Cartoon) staggered half a block a course;
    in Base a few blocks a shade lighter on a rule that repeats every 16 voxels:
    [labels] (face, light, joint)."""
    face, light, joint = labels
    ch = height * (2 if cartoon else 1)
    bl = block * (2 if cartoon else 1)
    course = (z - 16) // ch
    shift = (bl // 2) * (course % 2)
    if (z - 16) % ch == ch - 1 or (u - 8 + shift) % bl == 0:
        return joint
    if cartoon:
        return face
    blk = ((u - 8 + shift) % 16) // bl
    return light if (blk + course) % 3 == 1 else face


def rows(s, cartoon, labels, rowh=4):
    """A roof's surface by [s], voxels up the slope from its eave: rows [rowh] deep
    (twice in Cartoon) running along the eave, a dark line at each row's foot and in
    Base every third row a shade lighter, as the art draws them: [labels] (base,
    light, line)."""
    base, light, line = labels
    h = rowh * (2 if cartoon else 1)
    if s % h == 0:
        return line
    if cartoon:
        return base
    return light if (s // h) % 3 == 1 else base


def height_roof(m, cols, parts, thick, paint, role="roof"):
    """A roof made of [parts], each a function (x, y) -> (top z, facet) or None
    where it does not cover: each column of [cols] filled [thick] voxels down from
    the highest part's top, painted by [paint](x, y, z, top, part, facet)."""
    m.role_now = role
    for (x, y) in cols:
        best = None
        for n, part in enumerate(parts):
            r = part(x, y)
            if r is not None and (best is None or r[0] > best[0]):
                best = (r[0], n, r[1])
        if best is None:
            continue
        top, n, facet = best
        for z in range(top - thick + 1, top + 1):
            m.put(x, y, z, paint(x, y, z, top, n, facet))
    m.role_now = "mid"


# ----------------------------------------------------------------------------
# Shapes the poke_r buildings share.

def siding(u, z, cartoon):
    """The red house's white siding, as drawn: horizontal boards eight voxels tall
    (sixteen in Cartoon) from the floor, each lit along its top and shaded at its foot."""
    h = 16 if cartoon else 8
    k = (z - 16) % h
    if k == 0:
        return "siding_line"
    if k >= h - 2:
        return "siding_light"
    if k == 1 and not cartoon:
        return "siding_mid"
    return "siding"


def bricks(z, cartoon):
    """The shop's corner bricks: courses two voxels tall (four in Cartoon), ochre and
    pale ochre in turn, as drawn."""
    h = 4 if cartoon else 2
    return "ochre" if ((z - 16) // h) % 2 else "cream_dark"


def pane2(wall, ua, ub, z0, z1, glass, cartoon, bars=()):
    """A window across u ua..ub, glass z0 + 1 .. z1 - 1, in a dark outline and a grey
    frame within it, as drawn (the frame twice as wide in Cartoon)."""
    wall.pane(ua, ub, z0, z1, "trim_dark", glass, inner="frame", bars=tuple((u, None) for u in bars),
              bar_label="trim_dark")
    if cartoon:
        for u in range(ua + 2, ub - 1):
            for z in (z0 + 2, z1 - 2):
                wall.put(u, 0, z, "frame")
                wall.put(u, 1, z, "frame")


# ----------------------------------------------------------------------------
# The red house (four in poke_r.png, alike): five tiles by three, one storey open
# to its roof: a steep gable roof of red, its ridge front to back, darker lines down
# its slopes near the eaves and a dark red verge; white siding, a white board across
# the front under the tall front gable, two windows of two panes in the gable and a
# louvred vent at its top; the red door in tile 1 and a window over tiles 2 and 3, a
# blue strip along the walls' foot, grey boards at the corners.

def red_house(cartoon):
    m = Model(5, 3, 9, "PokeR_RedHouse")
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    x0, x1, y0, y1 = X(0), X(5), Y(0), Y(3)            # walls on x 8, 88 and y 8, 56
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front, back, left, right = walls["front"], walls["back"], walls["left"], walls["right"]
    # The roof: a steep gable, its ridge front to back over x 47 and 48, its top rising
    # 1.7 a voxel in from its eaves (three out, z 69) to the ridge (z 142), four voxels
    # thick; its verge two out in front and four at the back, as drawn.
    rx0, rx1, ry0, ry1 = x0 - 4, x1 + 3, y0 - 3, y1 + 4     # x 4..91, y 5..60
    PITCH, EAVE = 1.7, 69

    def d_of(x):
        return min(x - rx0, rx1 - x)

    def top(x):
        return EAVE + int(PITCH * d_of(x))

    def face(u, z):
        return siding(u, z, cartoon)

    # The walls: the sides to the eaves (z 70), the front and back to the board (z 62)
    # and their gables over it up to the roof.
    for key in ("left", "right"):
        u0, u1 = spans[key]
        walls[key].fill(u0 - 1, u1 + 1, 16, 70, face)
    for wall in (front, back):
        wall.fill(x0 - 1, x1, 16, 62, face)
        for u in range(x0 - 1, x1 + 1):
            for z in range(71, top(u) - 3):
                wall.put(u, 0, z, face(u, z))
                wall.put(u, 1, z, face(u, z))
    # The white board across the front and back at z 63-70, four voxels out, its top
    # white and its face pale grey, as drawn.
    for wall in (front, back):
        for u in range(x0 - 2, x1 + 2):
            for w in range(-4, 2):
                for z in range(63, 71):
                    if z == 70:
                        label = "siding_light"
                    elif z == 63:
                        label = "siding_line"
                    else:
                        label = "siding_mid" if w == -4 else "siding"
                    wall.put(u, w, z, label)

    def paint(x, y, z, t, n, f):
        if z < t:
            inside = x0 <= x < x1 and y0 <= y < y1
            return "ceiling" if (z == t - 3 and inside) else "roof_dark"
        d = d_of(x)
        if y in (ry0, ry0 + 1, ry1) or d == 0:
            return "roof_edge"                         # the verges and the eaves' edges
        if d < 20 and d % (8 if cartoon else 4) == 2:
            return "roof_line"                         # lines down the slopes near the eaves
        return "roof"

    cols = [(x, y) for x in range(rx0, rx1 + 1) for y in range(ry0, ry1 + 1)]
    height_roof(m, cols, [lambda x, y: (top(x), ("r",))], 4, paint)

    # The gables: two windows of two panes over the board and a louvred vent near the
    # top, front and back, as drawn (the back's inferred).
    for wall in (front, back):
        pane2(wall, X(1) + 4, X(2) + 3, 71, 97, "glass_house", cartoon, bars=(X(1) + 12,))      # x 28..43
        pane2(wall, X(2) + 12, X(3) + 12, 71, 97, "glass_house", cartoon, bars=(X(3) + 5,))     # x 52..68
        for u in range(X(2) + 3, X(2) + 13):                                                    # x 43..52
            for z in range(105, 127):
                edge = u in (X(2) + 3, X(2) + 12) or z in (105, 126)
                louvre = (z - 105) % (6 if cartoon else 3) == 0
                label = "frame" if edge else ("siding_line" if louvre else "siding_mid")
                wall.put(u, 0, z, label)
                wall.put(u, 1, z, label)

    # The ground floor: the red door in tile 1 (closed), a window in its upper part, a
    # lighter lower panel and a white handle; a window of two panes over tiles 2 and 3,
    # as drawn; the sides' and back's windows inferred.
    m.doors += [("ey", 1, 0, 1), ("ey", 1, 0, 2)]
    d0 = X(1)                                          # x 24..39
    for u in range(d0, d0 + 16):
        k = u - d0
        for z in range(16, 48):
            if k in (0, 15) or z in (16, 47):
                label = "door_frame"
            elif 2 <= k <= 13 and 31 <= z <= 46:
                if k in (2, 13) or z in (31, 46):
                    label = "trim_dark"
                else:
                    front.erase(u, 0, z)
                    front.put(u, 1, z, "glass_house")
                    continue
            elif 22 <= z <= 29 and 3 <= k <= 13:
                label = "door_panel"
            else:
                label = "door"
            front.put(u, 0, z, label)
            front.put(u, 1, z, label)
    for k in range(1, 5 if cartoon else 4):
        for z in (26, 27, 28):
            front.put(d0 + k, -1, z, "siding_light" if z > 26 else "siding_mid")
    pane2(front, X(2) + 12, X(4) - 2, 31, 47, "glass_house", cartoon, bars=(X(3) + 5,))          # x 52..70
    pane2(back, X(1) + 1, X(2) - 2, 31, 47, "glass_house", cartoon)
    pane2(back, X(3) + 1, X(4) - 2, 31, 47, "glass_house", cartoon)
    for key in ("left", "right"):
        pane2(walls[key], Y(1) + 1, Y(2) - 2, 31, 47, "glass_house", cartoon)
    # The blue strip along the walls' foot (z 16-19), but at the door.
    for wall, (u0, u1) in ((front, (x0 - 1, x1)), (back, (x0 - 1, x1)), (left, (y0 - 1, y1)), (right, (y0 - 1, y1))):
        for u in range(u0, u1 + 1):
            if wall is front and d0 <= u < d0 + 16:
                continue
            for z in range(16, 20):
                wall.put(u, 0, z, "base")
    # Grey boards at the corners of the ground floor, as drawn.
    half = 3 if cartoon else 2
    for (cx, cy) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        for x in range(cx - half, cx + half):
            for y in range(cy - half, cy + half):
                for z in range(20, 63):
                    edge = x in (cx - half, cx + half - 1) and y in (cy - half, cy + half - 1)
                    m.put(x, y, z, "siding_line" if edge else "siding_mid", "corner")

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 4}]
    m.figure = (0, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The shop (one in poke_r.png): seven tiles by three, one storey of six courses open
# to its roof: cream walls, ochre bricks at the corners and an ochre band under the
# roof; three pairs of windows above and two pairs under red awnings below, the green
# door with a round window in tile 3 between ochre pilasters; a flat roof of grey
# tiles inside a grey parapet, a tall red housing on it with a dark opening in its
# top, as drawn.

def shop(cartoon):
    m = Model(7, 3, 11, "PokeR_Shop")
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    x0, x1, y0, y1 = X(0), X(7), Y(0), Y(3)            # walls on x 8, 120 and y 8, 56
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front, back, left, right = walls["front"], walls["back"], walls["left"], walls["right"]
    TOP = 112                                          # the walls' top

    def face(u, z):
        if z >= 100:
            return "ochre_dark" if z in (100, TOP) else "ochre"    # the band under the roof
        return "cream"

    for wall in (front, back):
        wall.fill(x0 - 1, x1, 16, TOP, face)
    for key in ("left", "right"):
        u0, u1 = spans[key]
        walls[key].fill(u0 - 1, u1 + 1, 16, TOP, face)
    # Ochre bricks at the corners, up to the band, as drawn.
    half = 4 if cartoon else 3
    for (cx, cy) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        for x in range(cx - half, cx + half):
            for y in range(cy - half, cy + half):
                for z in range(16, 100):
                    m.put(x, y, z, bricks(z, cartoon), "corner")

    # The roof: a slab over the walls (z 113-122), its top a floor of grey tiles in a
    # grid; a parapet round it to z 130, six voxels wide at the sides and back and four
    # at the front, its outer face dark below the floor's level and light above, its
    # inner face dark, as drawn.
    FLOOR, PARAPET = 122, 130
    m.role_now = "roof"
    step = 16 if cartoon else 8
    for x in range(x0 - 1, x1 + 1):
        for y in range(y0 - 1, y1 + 1):
            ring = x <= x0 + 4 or x >= x1 - 5 or y <= y0 + 2 or y >= y1 - 5
            outer = x in (x0 - 1, x1) or y in (y0 - 1, y1)
            for z in range(TOP + 1, (PARAPET if ring else FLOOR) + 1):
                if outer:
                    label = "slab_dark" if z <= FLOOR else "slab_light"
                elif z == PARAPET:
                    label = "slab_light"
                elif ring and z > FLOOR:
                    inner = (x == x0 + 4 or x == x1 - 5 or y == y0 + 2 or y == y1 - 5)
                    label = "slab_dark" if inner else "slab"
                elif z == FLOOR and not ring:
                    label = "tile_line" if ((x - 8) % step == 0 or (y - 8) % step == 0) else "tile"
                else:
                    label = "slab"
                m.put(x, y, z, label)
    m.role_now = "mid"

    # The red housing on the roof, as drawn: 18 by 13, standing on the tiles to z 172,
    # its front lighter at its edges, its left side shaded, its top a red rim round a
    # darker ring and a dark opening.
    hx0, hx1, hy0, hy1, htop = 83, 100, 18, 30, 172
    for x in range(hx0, hx1 + 1):
        for y in range(hy0, hy1 + 1):
            for z in range(FLOOR + 1, htop + 1):
                if z == htop:
                    ring = min(x - hx0, hx1 - x, y - hy0, hy1 - y)
                    label = "red" if ring < 2 else ("red_shadow" if ring == 2 else "red_dark")
                elif x == hx0:
                    label = "red_shadow"
                elif y == hy0 and (x <= hx0 + 3 or x >= hx1 - 3):
                    label = "red"
                else:
                    label = "red_dark"
                m.put(x, y, z, label, "mid")
    for x in range(hx0 + 4, hx1 - 3):                  # the opening, x 87..96, y 21..27
        for y in range(hy0 + 3, hy1 - 2):
            for z in range(htop - 3, htop + 1):
                m.erase(x, y, z)
            m.put(x, y, htop - 4, "opening", "mid")

    # The front: three pairs of windows above (glass z 79-95), two pairs below (glass in
    # level 2) under red awnings, the green door in tile 3 between ochre pilasters, as
    # drawn; the sides' and back's windows inferred.
    for ua in (21, 50, 79):
        for wall in (front, back):
            pane2(wall, ua, ua + 27, 78, 96, "glass_shop", cartoon, bars=(ua + 13, ua + 14))
    for ua in (21, 79):
        for wall in (front, back):
            pane2(wall, ua, ua + 27, 31, 47, "glass_shop", cartoon, bars=(ua + 13, ua + 14))
            for u in range(ua, ua + 28):                   # its grey sill frame under it, as drawn
                for z in (28, 29, 30):
                    wall.put(u, 0, z, "trim_dark" if z == 28 else "frame")
                    wall.put(u, 1, z, "trim_dark" if z == 28 else "frame")
        # The awning over it: red, sloping down three voxels out just over its frame,
        # darker at its ends and its front edge, as drawn.
        for u in range(ua - 2, ua + 31):
            for d in range(1, 4):
                zt = 60 - d
                for z in (zt - 1, zt):
                    end = u in (ua - 2, ua + 30)
                    label = "red_shadow" if (d == 3 or z == zt - 1) else ("red_dark" if end else "red")
                    front.put(u, -d, z, label)
    for key in ("left", "right"):
        pane2(walls[key], Y(1) + 1, Y(2) - 2, 31, 47, "glass_shop", cartoon)
        pane2(walls[key], Y(1) + 1, Y(2) - 2, 78, 96, "glass_shop", cartoon)

    m.doors += [("ey", 3, 0, 1), ("ey", 3, 0, 2)]
    d0 = X(3)                                          # x 56..71
    for u in range(d0, d0 + 16):
        k = u - d0
        for z in range(16, 48):
            oval = ((k - 7.5) / 5.0) ** 2 + ((z - 39.0) / 7.0) ** 2
            if k in (0, 15) or z == 47:
                label = "green_dark"
            elif oval <= 1.0:
                front.erase(u, 0, z)
                front.put(u, 1, z, "glass_shop")
                continue
            elif oval <= 1.6:
                label = "green_dark"
            else:
                label = "green_light" if k <= 2 else "green"
            front.put(u, 0, z, label)
            front.put(u, 1, z, label)
    for k in range(1, 5 if cartoon else 4):
        for z in (25, 26, 27):
            front.put(d0 + k, -1, z, "handle")
    # The door's surround: ochre pilasters a voxel proud either side and a lintel over
    # it, as drawn.
    for u in list(range(X(3) - 4, X(3) - 2)) + list(range(X(4) + 2, X(4) + 4)):
        for z in range(16, 59):
            front.put(u, -1, z, "ochre")
    for u in range(X(3) - 4, X(4) + 4):
        for z in range(55, 59):
            front.put(u, -1, z, "ochre_dark" if z == 55 else "ochre")

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 4}]
    m.figure = (2, -1, 1, 200)
    return m


BUILDINGS = {
    "RedHouse": red_house,
    "Shop": shop,
}


def build(kind, cartoon):
    return BUILDINGS[kind](cartoon)
