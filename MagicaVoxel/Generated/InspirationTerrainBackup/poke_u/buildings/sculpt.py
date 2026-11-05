"""The poke_u buildings' geometry, on VCOM's grid, as the poke_r buildings are
drawn (their helpers copied from poke_r/buildings/sculpt.py).

poke_u.jpg is a JPEG of native pixel art: a tile is 16 of its pixels (the copies
of its trees and houses stand whole tiles apart), so a voxel is one of its
pixels across and in depth. Its heights are foreshortened to 0.4375 (every door
is 14 pixels tall for its two levels).

Every model is drawn on the game's tile grid so that it can be cut into the
game's 16-cubed pieces cleanly (a middle, an edge or a corner slot each):

- 16 voxels a tile. Tile boundaries run at x = 8 + 16i and y = 8 + 16j: every
  canvas has half a tile of margin all round the footprint, which holds the
  outer halves of the edge pieces (eaves, verges, beams, posts, flower boxes).
- Levels are z = 16k. Level 0 (z 0-15) is a house's own floor, a foundation
  standing in for the map's ground blocks under it. Units stand on the top of a
  cell: a floor at level 0 is stood on at level 1.
- A wall is two voxels thick across its tile boundary B (voxels B - 1 and B).
- A door is closed, as drawn, and each leaf fills exactly one doorway slot: one
  tile wide, the two levels a unit fills (the user's choice, 2026-10-28).
- A window keeps within its tile, each its own window piece. Its glass is over
  a solid sill course a level high, so a unit vaults in over the sill and has
  half cover at it.
- Upper floors are reached only where the art draws a way up (the user's
  choice): poke_u draws none, so each building is one storey open to its roof.
- Corners where four tiles meet are decoration to the fight: the timber posts
  stand there.
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
# Shapes the poke_u buildings share.

PITCH = 1.07          # the gables' rise for each voxel in toward the ridge, as drawn


def gable_top(x, ridge, mid):
    """A gable's top at x: [ridge] over the two voxels either side of its middle
    [mid], falling PITCH a voxel out to either side."""
    return ridge - int(math.floor(PITCH * (abs(x - mid) - 0.5)))


def tiles(s, a, cartoon, seed=0):
    """A roof's tiles by [s], voxels up the slope from its eave's edge, and [a] along
    the eave: courses six voxels deep (twelve in Cartoon), a dark line at the foot
    of each; tiles eight long (sixteen), staggered half a tile a course; in Base a
    few lighter on a fixed hash, as drawn."""
    w, l = (12, 16) if cartoon else (6, 8)
    course = s // w
    shift = (l // 2) * (course % 2)
    if s % w == 0 or (a + shift) % l == 0:
        return "roof_line"
    if cartoon:
        return "roof"
    tile = (a + shift) // l
    return "roof_light" if (course * 7 + tile * 5 + seed) % 11 in (0, 6) else "roof"


def beam(m, x0, x1, y0, y1, z0, z1, role):
    """A timber beam, its top lit and its underside dark, as drawn."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                m.put(x, y, z, "timber_light" if z == z1 else ("timber_dark" if z == z0 else "timber"), role)


def timber_post(m, x0, x1, y0, y1, z1):
    """A timber post standing proud of a front from the floor (z 16) to z1, its
    foot dark: a corner's, decoration to the fight."""
    m.box(x0, x1, y0, y1, 16, z1, lambda x, y, z: "timber_dark" if z == 16 else "timber", "corner")


def window(wall, ua, ub, cartoon, panes=2, box=True):
    """A ground-floor window across u ua..ub, as drawn: a white frame round its
    panes (glass z 32-37, over the sill course; the frame twice as thick in
    Cartoon), a dark sill under it, and below it a flower box two voxels proud
    (three in Cartoon), z 22-28, dark red, its flowers and leaves along its top."""
    bars = ()
    if panes == 2:
        mid = (ua + ub) // 2
        bars = ((mid, None), (mid + 1, None))
    wall.pane(ua, ub, 31, 38, "frame", "glass_house", inner="frame" if cartoon else None, bars=bars)
    for u in range(ua, ub + 1):
        wall.put(u, 0, 30, "frame_dark")
        wall.put(u, 1, 30, "frame_dark")
    if not box:
        return
    depth = 3 if cartoon else 2
    for u in range(ua, ub + 1):
        for w in range(-depth, 0):
            for z in range(22, 29):
                if z == 22:
                    label = "box_dark"
                elif z >= 27:
                    if cartoon:
                        label = "flower" if w == -depth else "leaf"
                    else:
                        label = "leaf" if (u - ua) % 3 == 2 else "flower"
                else:
                    label = "box"
                wall.put(u, w, z, label)


def door(wall, d0, cartoon):
    """The red door (closed) filling the doorway of the tile from u d0, as drawn:
    brown jambs, lit strips down its sides with shaded ones inside them, a window
    in a white frame in its upper half, a recessed panel below it (Base only) and a
    cream knob at the left."""
    light = (1, 2, 3, 12, 13, 14) if cartoon else (1, 2, 13, 14)
    shade = () if cartoon else (3, 12)
    for u in range(d0, d0 + 16):
        k = u - d0
        for z in range(16, 48):
            if k in (0, 15):
                label = "door_frame"
            elif z in (16, 47):
                label = "door_dark"
            elif 5 <= k <= 10 and 34 <= z <= 46:
                ring = k in (5, 10) or z in (34, 46) or (cartoon and (k in (6, 9) or z in (35, 45)))
                if not ring:
                    wall.erase(u, 0, z)
                    wall.put(u, 1, z, "glass_house")
                    continue
                label = "frame"
            elif k in light:
                label = "door_light"
            elif k in shade:
                label = "door_dark"
            elif not cartoon and 4 <= k <= 11 and 20 <= z <= 30 and (k in (4, 11) or z in (20, 30)):
                label = "door_dark"
            else:
                label = "door"
            wall.put(u, 0, z, label)
            wall.put(u, 1, z, label)
    for k in ((1, 2, 3) if cartoon else (1, 2)):
        for z in range(29, 32):
            wall.put(d0 + k, -1, z, "knob")


def stack(m, x0, x1, y0, y1, top, cap, shade, flue, cartoon):
    """A beige chimney stack standing on the roof, as drawn: its body from the roof
    up, a cap [cap] voxels tall a voxel wider all round, lit on top and shaded at
    its sides, as is the body [shade] voxels under it (one more in Cartoon), and a
    dark flue ([flue] = x0, x1, y0, y1) three voxels deep in its top."""
    foot = top - cap + 1
    shade += 1 if cartoon else 0
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            ground = max((z for z in range(top) if (x, y, z) in m.v), default=15)
            for z in range(ground + 1, foot):
                m.put(x, y, z, "chimney_band" if z >= foot - shade else "chimney", "mid")
    for x in range(x0 - 1, x1 + 2):
        for y in range(y0 - 1, y1 + 2):
            for z in range(foot, top + 1):
                m.put(x, y, z, "chimney_light" if z == top else "chimney_band", "mid")
    fx0, fx1, fy0, fy1 = flue
    for x in range(fx0, fx1 + 1):
        for y in range(fy0, fy1 + 1):
            for z in range(top - 2, top + 1):
                m.erase(x, y, z)
            m.put(x, y, top - 3, "flue", "mid")


def gable_frame(wall, top, mid, z0, cartoon, braces=()):
    """The timber in a gable over z0, as drawn: a post under the ridge (two voxels
    either side of [mid] in Cartoon, one in Base) up to the roof, and [braces], each
    (u, z, du) a strut from (u, z) climbing a voxel a step and moving du in u a
    step, two voxels wide, up to the roof's underside ([top](u) - 3)."""
    half = 2 if cartoon else 1
    for u in range(int(mid + 0.5) - half, int(mid + 0.5) + half):
        for z in range(z0, top(u) - 3):
            wall.put(u, 0, z, "timber")
            wall.put(u, 1, z, "timber")
    for (u0, z1, du) in braces:
        z = z1
        while True:
            u = int(round(u0 + du * (z - z1)))
            if z >= top(u) - 3 or z >= top(u + (1 if du > 0 else -1)) - 3:
                break
            for uu in (u, u + (1 if du < 0 else -1)):
                wall.put(uu, 0, z, "timber")
                wall.put(uu, 1, z, "timber")
            z += 1


# ----------------------------------------------------------------------------
# The cottage (three in poke_u.png, alike): three tiles by two, one storey open to
# its roof: a steep gable roof of red tiles, its ridge front to back, eaves seven
# voxels out; a timber frame at the front and back, two posts standing out from
# the corners under a beam across the front; the gables over it dark between
# timbers, a post under the ridge and two braces, two windows in each; cream walls;
# the red door with a window in tile 0, two windows of two panes with flower boxes
# under them in tiles 1 and 2; two beige chimney stacks on the right slope, the
# taller behind, as drawn.

def cottage(cartoon):
    m = Model(3, 2, 8, "PokeU_Cottage")
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    x0, x1, y0, y1 = X(0), X(3), Y(0), Y(2)            # walls on x 8, 56 and y 8, 40
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front, back, left, right = walls["front"], walls["back"], walls["left"], walls["right"]
    RIDGE, MID = 108, 31.5
    rx0, rx1, ry0, ry1 = 0, 63, 3, 45                  # eaves seven out, verges four and five

    def top(x):
        return gable_top(x, RIDGE, MID)

    # The walls: cream up to the beam (z 53) at the front and back and the gables'
    # dark infill above it up to the roof; the sides cream up to the roof.
    for wall in (front, back):
        for u in range(x0 - 1, x1 + 1):
            for z in range(16, top(u) - 3):
                label = "wall" if z < 54 else "gable"
                wall.put(u, 0, z, label)
                wall.put(u, 1, z, label)
    for wall in (left, right):
        for u in range(y0 - 1, y1 + 1):
            for w in (0, 1):
                x = wall.at(u, w, 0)[0]
                for z in range(16, top(x) - 3):
                    wall.put(u, w, z, "wall")

    # The roof: its ridge front to back over x 31 and 32 at z 108, falling 1.07 a
    # voxel to its eaves at the canvas's edges (z 75), four voxels thick, the verges'
    # boards three deeper, as drawn.
    def paint(x, y, z, t, n, facet):
        if y in (ry0, ry1):
            return "roof_edge"
        if z < t:
            inside = x0 <= x < x1 and y0 <= y < y1
            return "ceiling" if (z == t - 3 and inside) else "roof_under"
        if x in (rx0, rx1):
            return "roof_edge"
        if abs(x - MID) < (2 if cartoon else 1):
            return "roof_ridge"
        return tiles(x - rx0 if x < MID else rx1 - x, y, cartoon)

    cols = [(x, y) for x in range(rx0, rx1 + 1) for y in range(ry0, ry1 + 1)]
    height_roof(m, cols, [lambda x, y: (top(x), "gable")], 4, paint)
    m.role_now = "roof"
    for x in range(rx0, rx1 + 1):
        for y in (ry0, ry1):
            for z in range(top(x) - 6, top(x) - 3):
                m.put(x, y, z, "roof_edge")
    m.role_now = "mid"

    # The timber frame, front and back: posts standing three voxels out from the
    # corners (x 1-4 and 59-62, as drawn; wider and deeper in Cartoon), the walls
    # carried out to them, and a beam across on them two voxels out, z 54-63.
    p0, p1 = ((0, 5), (58, 63)) if cartoon else ((1, 4), (59, 62))
    c = 1 if cartoon else 0
    for (ya, yb, ba, bb) in ((4 - c, 6, 5 - c, 6), (41, 43 + c, 41, 42 + c)):
        for (a, b) in (p0, p1):
            timber_post(m, a, b, ya, yb, 53)
        beam(m, rx0, rx1, ba, bb, 54, 63, "ey")
    for (a, b) in ((p0[1] + 1, x0 - 2), (x1 + 1, p1[0] - 1)):
        for wall in (front, back):
            for u in range(a, b + 1):
                for z in range(16, 54):
                    wall.put(u, 0, z, "wall", "corner")
                    wall.put(u, 1, z, "wall", "corner")

    # The gables, front and back: the post under the ridge, the braces from beside
    # the windows' feet up to the roof, and two windows in white frames over tile 1,
    # as drawn (the back's inferred).
    for wall in (front, back):
        gable_frame(wall, top, MID, 59, cartoon, braces=((21, 59, -5 / 16.0), (42, 59, 5 / 16.0)))
        for ua in (24, 34):
            wall.pane(ua, ua + 5, 64, 77, "frame", "glass_house", inner="frame" if cartoon else None)

    # The ground floor: the red door in tile 0 (closed), two windows with flower
    # boxes in tiles 1 and 2, as drawn; windows in the sides and back, inferred.
    m.doors += [("ey", 0, 0, 1), ("ey", 0, 0, 2)]
    door(front, X(0), cartoon)
    window(front, X(1) + 1, X(2) - 2, cartoon)
    window(front, X(2) + 1, X(3) - 2, cartoon)
    window(back, X(0) + 1, X(1) - 2, cartoon, box=False)
    window(back, X(2) + 1, X(3) - 2, cartoon, box=False)
    for wall in (left, right):
        window(wall, Y(1) + 1, Y(2) - 2, cartoon, box=False)

    # The chimneys on the right slope: the taller behind (cap z 111-114), the
    # shorter in front of it and to its left, as drawn.
    stack(m, 45, 54, 28, 37, 114, 4, 3, (48, 52, 31, 34), cartoon)
    stack(m, 44, 50, 19, 25, 105, 2, 1, (46, 48, 21, 23), cartoon)

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 4}]
    m.figure = (0, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The wing house (one in poke_u.png): an L of thirteen tiles, one storey open to
# its roof: a wing three tiles by three on the right, its front a tile ahead of the
# rest, under a gable roof of red tiles with its ridge front to back; the part to
# its left two tiles by two under a lean-to rising to the wing's ridge at the back,
# hipped at its left end; timber posts and beams at both fronts, the wing's gable
# dark with a window of two panes; cream walls; the red door with a window and a
# small window with a flower box at the left, two windows with flower boxes in the
# wing; two beige chimney stacks on the wing's right slope, as drawn.

def wing_house(cartoon):
    fp = {(0, 1), (0, 2), (1, 1), (1, 2)} | {(i, j) for i in (2, 3, 4) for j in (0, 1, 2)}
    m = Model(5, 3, 8, "PokeU_WingHouse", footprint=fp)
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    W_RIDGE, W_MID = 104, 63.5
    EAVE, SHED, HIP = 70, 0.92, 1.4

    def wing_top(x):
        return gable_top(x, W_RIDGE, W_MID)

    def shed_top(x, y):
        """The lean-to's top at (x, y) and its face: rising 0.92 a voxel from its
        eave at the front (y 20, z 70) to the back (y 57, z 104), and 1.4 a voxel
        from its eave at the left end (x 0), the lower of the two."""
        s = EAVE + int(math.floor(SHED * (y - 20)))
        h = EAVE + int(math.floor(HIP * x))
        return (h, "hip") if h < s else (s, "shed")

    def wing_part(x, y):
        return (wing_top(x), "wing") if 35 <= x <= 92 and 3 <= y <= 57 else None

    def shed_part(x, y):
        return shed_top(x, y) if x <= 63 and 20 <= y <= 57 else None

    def roof_top(x, y):
        ts = [p[0] for p in (wing_part(x, y), shed_part(x, y)) if p is not None]
        return max(ts) if ts else None

    # The walls round the L, cream up to the roof; the wing's front gable over its
    # beam (z 56 up) dark infill, and its back gable where the wing's own roof is
    # over it (the right half: the lean-to covers the left).
    lf = Wall(m, "x", Y(1), -1)                        # the left part's front, y 23-24
    ll = Wall(m, "y", X(0), -1)                        # its left side, x 7-8
    wl = Wall(m, "y", X(2), -1)                        # the wing's left side, x 39-40, its front tile
    wf = Wall(m, "x", Y(0), -1)                        # the wing's front, y 7-8
    rt = Wall(m, "y", X(5), +1)                        # the right side, x 87-88
    bk = Wall(m, "x", Y(3), +1)                        # the back, y 55-56
    for wall, u0, u1 in ((lf, 7, 40), (ll, 23, 56), (wl, 7, 24), (wf, 39, 88), (rt, 7, 56), (bk, 7, 88)):
        for u in range(u0, u1 + 1):
            for w in (0, 1):
                x, y, _ = wall.at(u, w, 0)
                for z in range(16, roof_top(x, y) - 3):
                    gable = z >= 56 and ((wall is wf and x >= 39) or (wall is bk and x >= 64))
                    wall.put(u, w, z, "gable" if gable else "wall")

    # The roof: the wing's gable, its ridge front to back over x 63 and 64 at z 104,
    # falling 1.07 a voxel to its eaves four out (z 75), its verges four out at the
    # front and one at the back; the lean-to over the rest, its eave three out at the
    # front, hipped at the left; the higher wherever they meet; four voxels thick,
    # the edges' boards three deeper, as drawn.
    def inside(x, y):
        return ((x - 8) // 16, (y - 8) // 16) in fp and 9 <= x <= 86 and 9 <= y <= 54

    def paint(x, y, z, t, n, facet):
        if z < t:
            return "ceiling" if (z == t - 3 and inside(x, y)) else "roof_under"
        if facet == "wing":
            if y in (3, 57) or x in (35, 92):
                return "roof_edge"
            if abs(x - W_MID) < (2 if cartoon else 1):
                return "roof_ridge"
            return tiles(x - 35 if x < W_MID else 92 - x, y, cartoon)
        if y in (20, 57) or x == 0:
            return "roof_edge"
        s = EAVE + int(math.floor(SHED * (y - 20)))
        h = EAVE + int(math.floor(HIP * x))
        if abs(h - s) <= (2 if cartoon else 1):
            return "roof_ridge"                        # the hip's line
        if facet == "hip":
            return tiles(x, y, cartoon, seed=3)
        return tiles(y - 20, x, cartoon, seed=5)

    cols = sorted({(x, y) for x in range(35, 93) for y in range(3, 58)} |
                  {(x, y) for x in range(0, 64) for y in range(20, 58)})
    height_roof(m, cols, [wing_part, shed_part], 4, paint)
    m.role_now = "roof"
    for x in range(35, 93):
        t = wing_top(x)
        for z in range(t - 6, t - 3):
            m.put(x, 3, z, "roof_edge")
    for x in range(0, 39):
        t = roof_top(x, 20)
        for z in range(t - 6, t - 3):
            m.put(x, 20, z, "roof_edge")
    for x in range(0, 93):
        t = roof_top(x, 57)
        for z in range(t - 6, t - 3):
            m.put(x, 57, z, "roof_edge")
    m.role_now = "mid"

    # The timber frames: at the left part's front a post standing three voxels out
    # from its corner and a beam on it two out to the wing (z 52-58); at the wing's
    # front posts at its corners and a beam across (z 56-64), as drawn; wider and
    # deeper in Cartoon.
    d = 1 if cartoon else 0
    timber_post(m, 1 - d, 4 + d, 20 - d, 22, 51)
    beam(m, 0, 38, 21 - d, 22, 52, 58, "ey")
    for (a, b) in ((39, 42), (85, 88)):
        timber_post(m, a - d, b + d, 4 - d, 6, 55)
    beam(m, 35, 92, 5 - d, 6, 56, 64, "ey")
    for u in range(5 + d, 7):
        for z in range(16, 52):
            lf.put(u, 0, z, "wall", "corner")
            lf.put(u, 1, z, "wall", "corner")

    # The wing's gables: at the front a window of two panes in a white frame over
    # tile 3, timbers either side of it, as drawn; at the back one over tile 4, in
    # the half of the gable the lean-to leaves (inferred).
    wf.pane(56, 71, 64, 75, "frame", "glass_house", inner="frame" if cartoon else None, bars=((63, None), (64, None)))
    for u in (54, 55, 72, 73):
        for z in range(65, 77):
            wf.put(u, 0, z, "timber")
            wf.put(u, 1, z, "timber")
    bk.pane(73, 86, 64, 75, "frame", "glass_house", inner="frame" if cartoon else None, bars=((79, None), (80, None)))

    # The ground floor: the red door in tile 0 of the left part (closed) and a small
    # window with a flower box in tile 1; two windows with flower boxes in tiles 2
    # and 3 of the wing, as drawn (the second hidden by a tree, inferred); windows in
    # the sides and back, inferred.
    m.doors += [("ey", 0, 1, 1), ("ey", 0, 1, 2)]
    door(lf, X(0), cartoon)
    window(lf, 29, 34, cartoon, panes=1)
    window(wf, X(2) + 1, X(3) - 2, cartoon)
    window(wf, X(3) + 1, X(4) - 2, cartoon)
    window(ll, Y(2) + 1, Y(3) - 2, cartoon, box=False)
    window(wl, Y(0) + 1, Y(1) - 2, cartoon, box=False)
    for c in (Y(0), Y(2)):
        window(rt, c + 1, c + 14, cartoon, box=False)
    for c in (X(0), X(2), X(4)):
        window(bk, c + 1, c + 14, cartoon, box=False)

    # The chimneys on the wing's right slope: the taller behind (cap z 106-109), the
    # shorter in front of it, as drawn.
    stack(m, 76, 86, 38, 47, 109, 4, 3, (79, 83, 42, 44), cartoon)
    stack(m, 74, 80, 28, 35, 103, 2, 1, (76, 78, 32, 33), cartoon)

    m.storeys = [{"stand": 1, "tiles": set(fp), "entry": "vault", "cut": 4}]
    m.figure = (0, 0, 1, 200)
    return m


BUILDINGS = {
    "Cottage": cottage,
    "WingHouse": wing_house,
}


def build(kind, cartoon):
    return BUILDINGS[kind](cartoon)
