"""The poke_o buildings' geometry, on VCOM's grid, as the poke_n buildings are
drawn (their helpers copied from poke_n/buildings/sculpt.py).

poke_o.png is native pixel art: a tile is 16 of its pixels, so a voxel is one of
its pixels across and in depth. Its heights are foreshortened to 0.375 (every door
is 12 pixels tall for its two levels), less than in the earlier images.

Every model is drawn on the game's tile grid so that it can be cut into the
game's 16-cubed pieces cleanly (a middle, an edge or a corner slot each):

- 16 voxels a tile. Tile boundaries run at x = 8 + 16i and y = 8 + 16j: every
  canvas has half a tile of margin all round the footprint, which holds the
  outer halves of the edge pieces (eaves, verges, sills, boards, handles).
- Levels are z = 16k. Level 0 (z 0-15) is a house's own floor, a foundation
  standing in for the map's ground blocks under it. Units stand on the top of a
  cell: a floor at level 0 is stood on at level 1.
- A wall is two voxels thick across its tile boundary B (voxels B - 1 and B).
- A door is closed, as drawn, and each leaf fills exactly one doorway slot: one
  tile wide, the two levels a unit fills (the user's choice, 2026-10-28).
- A window keeps within its tile, or stands over a tile boundary, each half its
  own window piece. Its glass is over a solid sill course a level high, so a unit
  vaults in over the sill and has half cover at it.
- A wall with an opening a unit walks through (the wide house's, from its wing to
  its main block) is open in whole tiles at the levels a unit fills, the wall over
  it on piers at the corners between the tiles.
- Upper floors are reached only where the art draws a way up (the user's
  choice): poke_o draws none, so every house is one storey open to its roof.
- Corners where four tiles meet are decoration to the fight: the piers stand there.
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
# Shapes the poke_o buildings share: one tileset, so their walls, doors, windows and
# roofs are drawn alike.

def cream(u, z, top, cartoon):
    """The art's cream walls at height z on a stretch of wall under something at
    [top] (a lintel, a board, the eaves): lit near its foot and darker toward its top,
    in three bands with a dithered seam in Base (two plain bands in Cartoon), as drawn."""
    k = top - z                                        # voxels under what is over it
    if cartoon:
        return "wall" if k <= 15 else "wall_light"
    if k <= 9:
        return "wall_line" if not (k == 9 and (u + z) % 2) else "wall"
    if k <= 20:
        return "wall" if not (k == 20 and (u + z) % 2) else "wall_light"
    return "wall_light"


def house_wall(wall, u0, u1, top, cartoon, z0=16):
    """A wall's face from u0 to u1 in both its layers, from z0 to [top](u) (inclusive):
    the ground floor's cream darkening toward the lintel over it (z 48-50, dark on the
    outside), the cream above it darkening toward the wall's top."""
    for u in range(u0, u1 + 1):
        t = top(u)
        for z in range(z0, t + 1):
            if z < 48:
                label = cream(u, z, 48, cartoon)
            elif z <= 50:
                label = None
            else:
                label = cream(u, z, t + 1, cartoon)
            wall.put(u, 0, z, label or "lintel")
            wall.put(u, 1, z, label or "wall")


def foot(wall, u0, u1, skip=()):
    """The teal strip along a wall's foot (z 16-19, outside), as drawn, but where a
    door is ([skip]: u ranges)."""
    for u in range(u0, u1 + 1):
        if any(a <= u <= b for a, b in skip):
            continue
        for z in range(16, 20):
            wall.put(u, 0, z, "teal_dark" if z == 19 else "teal")


def door(wall, u0, cartoon):
    """The art's red door, closed, filling one doorway slot: one tile wide from u0, the
    two levels a unit fills (z 16-47), in both of the wall's layers; a dark frame, a
    darker band across its top holding three small dark panes (one long one in
    Cartoon), darker red at its foot and under the band, a gold handle at its left, as
    drawn."""
    for u in range(u0, u0 + 16):
        k = u - u0
        for z in range(16, 48):
            if k in (0, 15) or z == 47:
                label = "door_line"
            elif z >= 41:
                if cartoon:
                    pane = 43 <= z <= 45 and 3 <= k <= 12
                else:
                    pane = 43 <= z <= 45 and (3 <= k <= 4 or 6 <= k <= 9 or 11 <= k <= 12)
                label = "door_pane" if pane else "door_band"
            elif z <= 21 or 37 <= z <= 40:
                label = "door_dark"
            else:
                label = "door"
            wall.put(u, 0, z, label)
            wall.put(u, 1, z, label)
    ks = range(4, 8) if cartoon else range(5, 8)
    zs = range(28, 34) if cartoon else range(29, 33)
    for k in ks:
        for z in zs:
            wall.put(u0 + k, -1, z, "handle_dark" if (z == zs[0] or k == ks[-1]) else "handle")


def window(wall, ua, ub, cartoon):
    """A ground-floor window across u ua..ub, as drawn: glass in level 2 (z 32-46) in
    the inner layer, a voxel back from a grey frame, over a white sill at the top of
    the solid sill course (z 28-31), its foot a voxel proud; an inner frame in Cartoon."""
    wall.pane(ua, ub, 31, 47, "frame", "glass", inner="frame" if cartoon else None)
    for u in range(ua, ub + 1):
        for z in range(28, 32):
            wall.put(u, 0, z, "sill")
            wall.put(u, 1, z, "sill")
        for z in (28, 29):
            wall.put(u, -1, z, "sill")


def high_window(wall, ua, ub, z0, z1, cartoon, sill=False):
    """A window high in a wall or a gable, dark glass in a grey frame, as drawn (the
    wide house's upper windows over a white sill)."""
    wall.pane(ua, ub, z0, z1, "frame", "glass_dark", inner="frame" if cartoon else None)
    if sill:
        for u in range(ua, ub + 1):
            for z in (z0 - 2, z0 - 1):
                wall.put(u, -1, z, "sill")
                wall.put(u, 0, z, "sill")


def split_roof(m, x0, x1, y0, y1, xs, top, pitch, cartoon, inside, rise=0.0):
    """The art's split roof over columns x0..x1, y0..y1, three voxels thick: flat at
    [top] from x [xs] on, and west of it a facet descending [pitch] a voxel to its
    eave; the flat part plain under a dark outline, the facet in courses that darken
    toward its eave, as drawn; a ceiling under it where [inside](x, y). [rise] tips it
    up toward the back, that much a voxel (a lean-to against a higher wall). Returns
    its top at each x and y."""
    def top_at(x, y=None):
        t = top + (int(rise * (y - y0) + 0.5) if rise else 0)
        return t if x >= xs else t - int(pitch * (xs - x) + 0.5)

    def flat(x, y):
        return (top_at(x, y), ("f",)) if x >= xs else None

    def facet(x, y):
        return (top_at(x, y), ("s",)) if x < xs else None

    def paint(x, y, z, t, n, f):
        if z < t:
            return "ceiling" if (z == t - 2 and inside(x, y)) else "roof_deep"
        if x in (x0, x1) or y in (y0, y1):
            return "roof_line"
        if f[0] == "f":
            return "roof_light"
        if (y - 8) % (16 if cartoon else 8) == 0:
            return "roof_dark" if cartoon else "roof_deep"
        s = x - x0                                     # up the facet from its eave
        if s < (12 if cartoon else 8):
            return "roof_dark"
        if cartoon or s < 22:
            return "roof_mid" if s < 22 else "roof"
        return "roof"

    cols = [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)]
    height_roof(m, cols, [flat, facet], 3, paint)
    return top_at


def ac_unit(m, x0, y0, z0, cartoon):
    """A grey air-conditioning unit standing on a flat roof, as drawn: 12 voxels wide,
    9 deep, 16 tall; a light rim round a dark fan grille on its top, two rows of dark
    slots across its front (one in Cartoon), its right side shaded, a darker foot."""
    x1, y1, z1 = x0 + 11, y0 + 8, z0 + 15
    rows_ = ((z0 + 4, z0 + 6),) if cartoon else ((z0 + 3, z0 + 4), (z0 + 8, z0 + 9))
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                if z == z1:
                    ring = min(x - x0, x1 - x, y - y0, y1 - y)
                    label = "unit_light" if ring == 0 else ("unit_mid" if ring == 1 else "unit_grille")
                elif z == z0:
                    label = "unit_foot"
                elif y == y0 and x0 + 2 <= x <= x1 - 2 and any(a <= z <= b for a, b in rows_):
                    label = "unit_dark"
                elif x == x1:
                    label = "unit_dark"
                else:
                    label = "unit"
                m.put(x, y, z, label, "mid")


# ----------------------------------------------------------------------------
# The gabled house (three in poke_o.png, alike): four tiles by two, one storey of
# three courses and more, open to its roof: cream walls darkening toward the lintel
# over the ground floor and a light board across the front under its khaki gable; a
# front gable roof of pink tiles, its ridge front to back, in stripes along it under a
# light band; a dormer on its left slope, its glazed triangular gable facing left; the
# red door in tile 1 and a window in tile 2, the teal strip along the walls' foot.

def gable_house(cartoon):
    m = Model(4, 2, 7, "PokeO_GableHouse")
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    x0, x1, y0, y1 = X(0), X(4), Y(0), Y(2)            # walls on x 8, 72 and y 8, 40
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front, back, left, right = walls["front"], walls["back"], walls["left"], walls["right"]
    # The roof: a front gable rising 0.97 a voxel in from its eaves (three out, z 68) to
    # its ridge over x 39 and 40 (z 101), its verges three out front and back, as drawn;
    # the side walls under its eaves to z 67.
    rx0, rx1, ry0, ry1 = x0 - 4, x1 + 3, y0 - 4, y1 + 3    # x 4..75, y 4..43
    PITCH = 0.97

    def d_of(x):
        return min(x - rx0, rx1 - x)

    def top(x):
        return 68 + int(PITCH * d_of(x))

    # The dormer on the left slope: a little gable along x, its ridge at z 93 over y 23
    # and 24, its gable facing left at x 14, where the drawn triangle is.
    YC, ZR = 24, 93

    def dormer_top(x, y):
        return ZR - int(1.4 * abs(y - YC + 0.5))

    def main(x, y):
        return (top(x), ("m",))

    def dormer(x, y):
        if not (14 <= x <= 31 and YC - 11 <= y <= YC + 10):
            return None
        return (dormer_top(x, y), ("d",))

    def paint(x, y, z, t, n, f):
        if z < t:
            return "ceiling" if (z == t - 2 and x0 <= x < x1 and y0 <= y < y1) else "roof_deep"
        if f[0] == "d":
            if y in (YC - 1, YC):
                return "roof_light"                    # its ridge
            if x == 14 or y in (YC - 11, YC + 10):
                return "roof_line"
            return "roof"
        d = d_of(x)
        if y in (ry0, ry1) or d == 0:
            return "roof_line"                         # the verges' and the eaves' edges
        if d >= 28:
            return "roof_light"                        # the light band along the ridge
        if cartoon:
            return "roof_mid" if d % 16 in (6, 7) else "roof"
        return "roof_mid" if d % 8 in (4, 5) else "roof"

    cols = [(x, y) for x in range(rx0, rx1 + 1) for y in range(ry0, ry1 + 1)]
    height_roof(m, cols, [main, dormer], 3, paint)
    # The dormer's glazed gable at x 14, on the main roof's layers carried on under it:
    # a triangle of glass in a white frame up to the dormer's own roof.
    m.role_now = "roof"
    zb = top(14) + 1
    for y in range(YC - 11, YC + 11):
        zt = dormer_top(14, y) - 3
        for z in range(top(14) - 2, zt + 1):
            if z < zb:
                label = "roof_deep" if z < top(14) else "roof"
            else:
                label = "sill" if z in (zb, zt) else "glass"
            m.put(14, y, z, label)
    m.role_now = "mid"

    # The walls: the front and back under the board (z 64-67), the gables over it to the
    # roof; the sides to the eaves.
    for wall in (front, back):
        house_wall(wall, x0 - 1, x1, lambda u: 63, cartoon)
    for key in ("left", "right"):
        u0, u1 = spans[key]
        house_wall(walls[key], u0 - 1, u1 + 1, lambda u: 67, cartoon)
    # The light board across the front and back under the gable, as drawn: three voxels
    # out, under the verges.
    for wall, out in ((front, 3), (back, 3)):
        for u in range(x0 - 2, x1 + 2):
            for w in range(-out, 2):
                for z in range(64, 68):
                    wall.put(u, w, z, "wall_light" if z == 67 else ("wall_line" if z == 64 else "wall"))
    # The gables: khaki, darker high up under the roof.
    for wall in (front, back):
        for u in range(x0 - 1, x1 + 1):
            for z in range(68, top(u) - 2):
                label = "gable" if z < 72 else "gable_dark"
                wall.put(u, 0, z, label)
                wall.put(u, 1, z, label)
        high_window(wall, X(2) - 6, X(2) + 5, 71, 84, cartoon)      # the vent, x 34..45, as drawn

    # The front: the red door in tile 1 (closed), the window in tile 2, as drawn; the
    # sides and back (unseen): windows of its kind.
    m.doors += [("ey", 1, 0, 1), ("ey", 1, 0, 2)]
    door(front, X(1), cartoon)
    window(front, X(2) + 1, X(3) - 2, cartoon)
    window(back, X(1) + 1, X(2) - 2, cartoon)
    window(back, X(2) + 1, X(3) - 2, cartoon)
    for key in ("left", "right"):
        window(walls[key], Y(1) + 1, Y(2) - 2, cartoon)
    foot(front, x0 - 1, x1, skip=[(X(1), X(2) - 1)])
    foot(back, x0 - 1, x1)
    for key in ("left", "right"):
        foot(walls[key], y0 - 1, y1)

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 4}]
    m.figure = (0, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The skylight house (two in poke_o.png, alike): four tiles by two, one storey open
# to its roof: the art's split roof, flat over tiles 2 and 3 with a skylight in it
# and a facet over tiles 0 and 1 descending to the left eave; cream walls, a light
# board across the front under a band of wall with a small high window; the red
# door in tile 1 and a window in tile 2, the teal strip along the walls' foot.

def skylight_house(cartoon):
    m = Model(4, 2, 7, "PokeO_SkylightHouse")
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    x0, x1, y0, y1 = X(0), X(4), Y(0), Y(2)            # walls on x 8, 72 and y 8, 40
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front, back = walls["front"], walls["back"]
    # The roof: flat at z 95 from x 40, the facet descending 0.6 a voxel to the left
    # eave (z 73, three out); four voxels out in front and three at the back, as drawn.
    top = split_roof(m, x0 - 4, x1 + 3, y0 - 5, y1 + 3, X(2), 95, 0.6, cartoon,
                     lambda x, y: x0 <= x < x1 and y0 <= y < y1)

    def under(u):
        return top(u) - 3

    for wall in (front, back):
        house_wall(wall, x0 - 1, x1, under, cartoon)
    for key in ("left", "right"):
        u0, u1 = spans[key]
        edge = x0 - 1 if key == "left" else x1
        house_wall(walls[key], u0 - 1, u1 + 1, lambda u, e=edge: under(e), cartoon)
    # The light board across the front at z 64-67, a voxel proud, as drawn.
    for u in range(x0 - 1, x1 + 1):
        for w in (-1, 0, 1):
            for z in range(64, 68):
                front.put(u, w, z, "wall_light" if z == 67 else "wall")
    high_window(front, X(2), X(2) + 6, 68, 75, cartoon)              # over the board, x 40..46, as drawn

    # The skylight on the flat roof, as drawn: a pane flush with its top in a dark frame
    # a voxel proud, the frame three voxels deep along its back.
    m.role_now = "roof"
    for x in range(47, 65):
        for y in range(17, 33):
            if x in (47, 48, 63, 64) or y == 17 or y >= 30:
                m.put(x, y, 96, "roof_dark")
            else:
                m.put(x, y, 95, "glass")
                m.erase(x, y, 94)
                m.erase(x, y, 93)
    m.role_now = "mid"

    m.doors += [("ey", 1, 0, 1), ("ey", 1, 0, 2)]
    door(front, X(1), cartoon)
    window(front, X(2) + 1, X(3) - 2, cartoon)
    window(back, X(1) + 1, X(2) - 2, cartoon)
    window(back, X(2) + 1, X(3) - 2, cartoon)
    for key in ("left", "right"):
        window(walls[key], Y(1) + 1, Y(2) - 2, cartoon)
    foot(front, x0 - 1, x1, skip=[(X(1), X(2) - 1)])
    foot(back, x0 - 1, x1)
    for key in ("left", "right"):
        foot(walls[key], y0 - 1, y1)

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 4}]
    m.figure = (0, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The wide house (one in poke_o.png): a main block of six tiles by two under the
# skylight house's split roof (flat over tiles 2-5 with two grey air-conditioning
# units on it, the facet over tiles 0 and 1), and in front of its tiles 1-3 a wing a
# tile deep under a lower split roof, the red door in its middle tile; one storey,
# the wing open to the main block through those tiles at the levels a unit fills.
# The main block's front: a window in tile 4, two high windows over it, as drawn.

def wide_house(cartoon):
    wing = {(i, 0) for i in (1, 2, 3)}
    block = {(i, j) for i in range(6) for j in (1, 2)}
    m = Model(6, 3, 7, "PokeO_WideHouse", wing | block)
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))

    def W(axis, line, out):
        return Wall(m, axis, line, out)

    mf, mb, ml, mr = W("x", Y(1), -1), W("x", Y(3), +1), W("y", X(0), -1), W("y", X(6), +1)
    wf, wl, wr = W("x", Y(0), -1), W("y", X(1), -1), W("y", X(4), +1)

    # The roofs: the main block's flat at z 95 from x 40, its facet descending 0.6 a
    # voxel to the left eave, three out at the sides, four in front and three at the
    # back; the wing's, a lean-to against the main block's wall, rising from z 68 at
    # its front to z 76 there (so its back meets the main roof's edge, as drawn), its
    # facet over tile 1, two out.
    top = split_roof(m, X(0) - 4, X(6) + 3, Y(1) - 5, Y(3) + 3, X(2), 95, 0.6, cartoon,
                     lambda x, y: X(0) <= x < X(6) and Y(1) <= y < Y(3))
    wtop = split_roof(m, X(1) - 3, X(4) + 2, Y(0) - 3, Y(1) - 2, X(2), 68, 0.67, cartoon,
                      lambda x, y: X(1) <= x < X(4) and Y(0) <= y < Y(1) - 1, rise=0.47)
    back = Y(1) - 2                                    # the wing roof's last row, y 22
    for y0u in (Y(1) + 2, Y(2) + 4):                 # the units, y 26..34 and 44..52, as drawn
        ac_unit(m, 82, y0u, 96, cartoon)

    # The walls, each to the roof over it.
    house_wall(mb, X(0) - 1, X(6), lambda u: top(u) - 3, cartoon)
    house_wall(ml, Y(1) - 1, Y(3), lambda u: top(X(0) - 1) - 3, cartoon)
    house_wall(mr, Y(1) - 1, Y(3), lambda u: top(X(6)) - 3, cartoon)
    house_wall(wf, X(1) - 1, X(4), lambda u: wtop(u, Y(0) - 1) - 3, cartoon)
    house_wall(wl, Y(0) - 1, Y(1) - 1, lambda u: wtop(X(1) - 1, min(u, back)) - 3, cartoon)
    house_wall(wr, Y(0) - 1, Y(1) - 1, lambda u: wtop(X(4), min(u, back)) - 3, cartoon)
    # The main block's front: whole beside the wing; behind it, open where a unit goes
    # (the wing's tiles' width, up to the wing's roof) on piers at the tile corners,
    # the wall going on over the wing's roof.
    house_wall(mf, X(0) - 1, X(1), lambda u: top(u) - 3, cartoon)
    house_wall(mf, X(4) - 1, X(6), lambda u: top(u) - 3, cartoon)
    for u in range(X(1) + 1, X(4) - 1):
        z0 = wtop(u, back) - 2
        for z in range(z0, top(u) - 2):
            label = cream(u, z, top(u) - 2, cartoon)
            mf.put(u, 0, z, label)
            mf.put(u, 1, z, label)
    for cx in (X(2), X(3)):
        post(m, cx, Y(1), 16, wtop(cx, back) - 3, "wall", 2)

    # The door in the wing's middle tile (closed); the main block's front window in
    # tile 4 and the two high windows over it, as drawn; the unseen sides and back:
    # windows of the front's kind.
    m.doors += [("ey", 2, 0, 1), ("ey", 2, 0, 2)]
    door(wf, X(2), cartoon)
    window(mf, X(4) + 3, X(5) - 1, cartoon)
    high_window(mf, X(4) + 1, X(4) + 10, 70, 86, cartoon, sill=True)
    high_window(mf, X(4) + 12, X(4) + 21, 70, 86, cartoon, sill=True)
    window(mb, X(1) + 1, X(2) - 2, cartoon)
    window(mb, X(4) + 2, X(5) - 2, cartoon)
    high_window(mb, X(4) + 1, X(4) + 10, 70, 86, cartoon, sill=True)
    high_window(mb, X(4) + 12, X(4) + 21, 70, 86, cartoon, sill=True)
    window(ml, Y(2) + 1, Y(3) - 2, cartoon)
    window(mr, Y(1) + 1, Y(2) - 2, cartoon)
    foot(wf, X(1) - 1, X(4), skip=[(X(2), X(3) - 1)])
    foot(wl, Y(0) - 1, Y(1) - 1)
    foot(wr, Y(0) - 1, Y(1) - 1)
    foot(mf, X(0) - 1, X(1))
    foot(mf, X(4) - 1, X(6))
    foot(mb, X(0) - 1, X(6))
    foot(ml, Y(1) - 1, Y(3))
    foot(mr, Y(1) - 1, Y(3))

    m.storeys = [{"stand": 1, "tiles": wing | block, "entry": "vault", "cut": 4}]
    m.figure = (0, 0, 1, 200)
    return m


BUILDINGS = {
    "GableHouse": gable_house,
    "SkylightHouse": skylight_house,
    "WideHouse": wide_house,
}


def build(kind, cartoon):
    return BUILDINGS[kind](cartoon)
