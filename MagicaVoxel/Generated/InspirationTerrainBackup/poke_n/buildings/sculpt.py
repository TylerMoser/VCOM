"""The poke_n buildings' geometry, on VCOM's grid, as the poke_m buildings are
drawn (their helpers copied from poke_m/buildings/sculpt.py, gable_pitch given a
back verge of its own).

poke_n.png is native pixel art: a tile is 16 of its pixels (its forest's trees,
two tiles across, repeat every 32), so a voxel is one of its pixels across and in
depth, its heights foreshortened to 0.46 as in the earlier images.

Every model is drawn on the game's tile grid so that it can be cut into the
game's 16-cubed pieces cleanly (a middle, an edge or a corner slot each):

- 16 voxels a tile. Tile boundaries run at x = 8 + 16i and y = 8 + 16j: every
  canvas has half a tile of margin all round the footprint, which holds the
  outer halves of the edge pieces (eaves, verges, sills, the bay, flower boxes).
- Levels are z = 16k. Level 0 (z 0-15) is a house's own floor, a foundation
  standing in for the map's ground blocks under it; the gate stands on the map's
  own ground. Units stand on the top of a cell: a floor at level 0 is stood on at
  level 1.
- A wall is two voxels thick across its tile boundary B (voxels B - 1 and B).
- A door is closed, as drawn, and each leaf fills exactly one doorway slot: one
  tile wide, the two levels a unit fills (the user's choice, 2026-10-28).
- A window keeps within its tile, or stands over a tile boundary, each half its
  own window piece. Its glass is over a solid sill course a level high, so a unit
  vaults in over the sill and has half cover at it.
- A wall with an opening a unit walks through (the chalet's, from its wing to its
  A-frame block) is open in whole tiles at the two levels a unit fills, the roof
  over it on piers at the corners between the tiles.
- Upper floors are reached only where the art draws a way up (the user's
  choice): poke_n draws none, so every house is one storey open to its roof.
- Corners where four tiles meet are decoration to the fight: the corner posts,
  quoins and piers, and the gate's posts, stand there.
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
# Shapes the poke_n buildings share.

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


def flower_box(w, ua, ub, z0, cartoon, depth=4):
    """A box of flowers along a wall from u ua to ub, its top at z0 + 6, [depth]
    voxels out: dark wood, green leaves and pink, purple and orange flowers over it,
    as drawn (plain flowers in Cartoon)."""
    top = z0 + 5
    for u in range(ua, ub + 1):
        for d in range(1, depth + 1):
            for z in range(z0, top + 1):
                rim = u in (ua, ub) or d == depth or z in (z0, top)
                w.put(u, -d, z, "rh_box_dark" if rim else "rh_box")
            if cartoon:
                w.put(u, -d, top + 1, "rh_flower")
                continue
            h = ((u % 16) * 5 + d * 7) % 9
            w.put(u, -d, top + 1, "rh_leaf" if h in (1, 4, 7) else ("rh_flower_orange" if h == 2 else "rh_flower"))
            if h in (0, 3, 5):
                w.put(u, -d, top + 2, "rh_flower" if h != 5 else "rh_flower_orange")


# ----------------------------------------------------------------------------
# The red house (two in poke_n.png, alike): five tiles by two, one storey of four
# courses open to its roof: the ground floor's cream walls between stone quoins, a
# dark beam over it, the upper floor's two wide windows over flower boxes between
# dark timbers; a steep gable roof of red tiles, its ridge front to back under a
# light band, grey verges (the back one seven out), the eaves eight voxels out, as
# drawn; a shed dormer on its right slope; a brick chimney under a tall light cap at
# the back of its left slope; the front: a bay window under a red awning (its glass
# in tile 1) and the blue double door (tile 3).

def red_house(cartoon):
    m = Model(5, 2, 9, "PokeN_RedHouse")
    floor = Z(1)
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    x0, x1, y0, y1 = X(0), X(5), Y(0), Y(2)            # walls on x 8, 88 and y 8, 40
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front, back = walls["front"], walls["back"]
    EAVE = 84                                          # the walls' top, under the eaves, as drawn
    plaster = ("rh_wall", "rh_wall_light", "rh_wall_line")

    def face(u, z):
        if z < 48:
            return "rh_wall_line" if z < 18 else blocks(u, z, cartoon, plaster, 4, 16)
        if z < 56:
            return "rh_beam_dark" if z in (48, 55) else "rh_beam"
        return "rh_timber" if (z - 56) % (8 if cartoon else 4) else "rh_timber_dark"

    for key, wall in walls.items():
        u0, u1 = spans[key]
        wall.fill(u0 - 1, u1 + 1, floor, EAVE - 1, face)
        for u in range(u0 - 1, u1 + 2):
            for z in range(48, 56):
                wall.put(u, -1, z, "rh_beam_dark" if z in (48, 55) else "rh_beam")

    # Stone quoins at the ground floor's corners, a dark timber over them to the
    # eaves, as drawn.
    half = 4 if cartoon else 3
    for cx in (x0, x1):
        for cy in (y0, y1):
            for x in range(cx - half, cx + half):
                for y in range(cy - half, cy + half):
                    for z in range(floor, EAVE):
                        if z < 48:
                            course = (z - 16) // (8 if cartoon else 4)
                            joint = (z - 16) % (8 if cartoon else 4) == (7 if cartoon else 3)
                            label = "rh_stone_dark" if joint else ("rh_stone" if course % 2 else "rh_stone_light")
                        elif z < 56:
                            label = "rh_beam"
                        else:
                            label = "rh_timber"
                        m.put(x, y, z, label, "corner")

    # The front: the bay window across tiles 1 and 2 (x 24..47), its glass in level
    # 2 over a solid base and within tile 1 (x 31..39), cream panels either side of
    # it, a red awning over it; the blue double door in tile 3 (closed), as drawn.
    bx0, bx1 = X(1), X(1) + 23                         # x 24..47
    gx0, gx1 = X(1) + 7, X(2) - 1                      # x 31..39
    for u in range(bx0, bx1 + 1):
        for d in range(1, 6):
            for z in range(floor, 46):
                if z < 31:
                    label = "rh_wall_line" if (z < 18 or z == 30) else "rh_wall"
                elif z in (31, 45):
                    label = "rh_frame"
                elif u in (bx0, bx1):
                    label = "rh_wall"
                elif d < 5:
                    label = None
                elif gx0 <= u <= gx1:
                    label = "glass_rh"
                elif gx0 - 2 <= u <= gx1 + 2:
                    label = "rh_frame"
                else:
                    label = "rh_wall_light"
                if label:
                    front.put(u, -d, z, label)
        for d in range(0, 7):                          # the awning, sloping out and down
            zt = 52 - d
            for z in (zt - 1, zt):
                front.put(u, -d, z, "rh_roof_line" if z == zt - 1 else ("rh_roof_light" if d % 2 else "rh_roof"))
    # The bay opens into the room: no wall behind it at level 2 in tile 1.
    for u in range(bx0 + 1, X(2)):
        for z in range(32, 45):
            front.erase(u, 0, z)
            front.erase(u, 1, z)
    m.doors += [("ey", 3, 0, 1), ("ey", 3, 0, 2)]
    d0 = X(3)                                          # x 56..71
    for u in range(d0, d0 + 16):
        k = u - d0
        for z in range(floor, 48):
            if k in (0, 15) or z in (floor, 47):
                label = "rh_door_dark"
            elif k in (7, 8):
                label = "rh_door_line"
            elif z in (31, 32) or (not cartoon and k in (3, 12) and 20 <= z <= 43):
                label = "rh_door_mid"
            else:
                label = "rh_door"
            front.put(u, 0, z, label)
            front.put(u, 1, z, label)
    for u in (d0 + 6, d0 + 9):
        for z in (30, 31):
            front.put(u, -1, z, "rh_knob")

    def window(wall, ua, ub, z0, z1, bars=()):
        """A window across u ua..ub, glass z0 + 1 .. z1 - 1 in a white frame."""
        wall.pane(ua, ub, z0, z1, "rh_frame", "glass_rh", inner="rh_frame" if cartoon else None,
                  bars=tuple((u, None) for u in bars))

    # The upper floor: two wide windows of two panes over flower boxes, as drawn.
    for ua, ub in ((20, 43), (52, 75)):
        window(front, ua, ub, 66, 82, ((ua + ub) // 2, (ua + ub) // 2 + 1))
    for ua, ub in ((23, 40), (55, 72)):
        flower_box(front, ua, ub, 58, cartoon)
    # The unseen sides and back: a window of the bay's kind in each side's tile 0
    # and in the back's tiles 1 and 3, the upper floor's over them.
    for key in ("left", "right"):
        window(walls[key], Y(0) + 1, Y(1) - 2, 31, 46)
        window(walls[key], Y(0) + 1, Y(2) - 2, 66, 82, (Y(1) - 1, Y(1)))
    for c in (X(1), X(3)):
        window(back, c + 1, c + 14, 31, 46)
    for ua, ub in ((20, 43), (52, 75)):
        window(back, ua, ub, 66, 82, ((ua + ub) // 2, (ua + ub) // 2 + 1))

    # The roof: steep, its ridge front to back over x 47 and 48, rising 1.05 for each
    # voxel in (to z 128, as drawn), red tiles in rows along the ridge under a light
    # band; the eaves eight voxels out, the verges grey, the front one two out and
    # the back one seven, as drawn (the roof runs further back than the front).
    labels = ("rh_roof", "rh_roof_light", "rh_roof_line")
    OV, VERGE, VERGE_BACK = 8, 2, 7
    under = gable_pitch(m, x0, x1, y0, y1, EAVE, 1.05, ("rh_roof_light", "rh_roof", "rh_roof_dark", "rh_roof_line"),
                        "rh_ridge", "rh_verge", cartoon, ov=OV, verge=VERGE, thick=3, band=2,
                        pattern=lambda s, a: rows(s, cartoon, labels), verge_back=VERGE_BACK)
    # The eaves' outer edges dark red, as drawn: only the verges are grey.
    for (x, y, z), label in list(m.v.items()):
        if label == "rh_verge" and (x <= x0 - OV or x >= x1 + OV - 1) and y not in (y0 - 1 - VERGE, y1 + VERGE_BACK):
            m.v[(x, y, z)] = "rh_roof_line"
    # Grey barge boards under the verges, four voxels deep, as drawn.
    m.role_now = "roof"
    for x in range(x0 - 1 - OV, x1 + OV + 1):
        b = under(x)
        for y in (y0 - 1 - VERGE, y1 + VERGE_BACK):
            for z in range(b - 4, b):
                m.put(x, y, z, "rh_verge_dark" if z == b - 4 else "rh_verge")
    m.role_now = "mid"
    # The gables, front and back: a dark timber over the walls, cream above it.
    for wall in (front, back):
        for u in range(x0 - 1, x1 + 1):
            for z in range(EAVE, under(u)):
                label = "rh_timber" if z < EAVE + 6 else ("rh_gable_line" if (z - EAVE) % 8 == 7 and not cartoon else "rh_gable")
                wall.put(u, 0, z, label)
                wall.put(u, 1, z, label)

    # The shed dormer on the right slope, as drawn: a flat roof of the roof's tiles
    # from the slope out over the right wall, a light boarded face toward the front.
    dz = 118                                           # its roof's top
    dy0, dy1 = Y(0) + 9, Y(1) + 8                      # y 17..32
    m.role_now = "roof"
    xs = 88 - int((dz - 2 - EAVE) / 1.05)              # where its roof leaves the slope
    for x in range(xs, x1 + 3):
        for y in range(dy0, dy1 + 1):
            for z in (dz - 2, dz - 1, dz):
                edge = y in (dy0, dy1) or x == x1 + 2
                m.put(x, y, z, "rh_roof_line" if edge and z == dz else ("rh_roof_light" if z == dz else "rh_roof"))
            base = under(x) + 3
            if x <= x1:
                for z in range(base, dz - 2):
                    if y == dy0:
                        louvre = (z - base) % (6 if cartoon else 3) == 0
                        m.put(x, y, z, "rh_dormer_line" if louvre else "rh_dormer")
                    elif x == x1:
                        m.put(x, y, z, "rh_dormer")
                    elif y == dy1:
                        m.put(x, y, z, "rh_dormer")
    m.role_now = "mid"

    # The chimney at the back of the left slope, as drawn: red-brown brick in courses
    # standing on the roof, through its back over the back wall, under a tall light
    # cap a voxel wider all round, its top a light rim round a darker inside and the
    # dark flue; its top over the ridge.
    cx0, cx1, cy0, cy1 = 15, 30, 34, 45                # the cap; the brick a voxel in
    cap0, ctop = 121, 132
    course = 4 if cartoon else 2
    for x in range(cx0 + 1, cx1):
        for y in range(cy0 + 1, cy1):
            ground = max((z for z in range(cap0) if (x, y, z) in m.v), default=0)
            for z in range(ground + 1, cap0):
                dark = x == cx1 - 1 or (z // course) % 2 == 1
                m.put(x, y, z, "rh_chim_dark" if dark else "rh_chim", "mid")
    for x in range(cx0, cx1 + 1):
        for y in range(cy0, cy1 + 1):
            ring = min(x - cx0, cx1 - x, y - cy0, cy1 - y)
            for z in range(cap0, ctop + 1):
                if z == ctop:
                    if ring < 2:
                        label = "rh_chim_cap"
                    elif ring == 2 and not cartoon:
                        label = "rh_chim_ring"
                    else:
                        label = "rh_chim_top"
                elif ring > 0:
                    label = "rh_chim_top"
                elif z < cap0 + 5 or z >= ctop - 2:
                    label = "rh_chim_face_dark"
                else:
                    label = "rh_chim_face"
                m.put(x, y, z, label, "mid")
    for x in range(20, 27):                            # the flue, x 20..26, y 38..42
        for y in range(38, 43):
            for z in range(ctop - 5, ctop):
                m.put(x, y, z, "rh_flue", "mid")
            m.erase(x, y, ctop)

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 3}]
    m.figure = (3, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The chalet (the house at the top of poke_n.png): an L, a wing of two tiles by
# three on the left under a steep hipped roof, a tile back from the A-frame block
# of four tiles by two on the right; one storey of two courses open to the roofs.
# The A-frame block's steep gable roof rises 3.2 a voxel in to a flat top (z 120),
# its front gable cream with dark braces and three windows under a white verge, as
# drawn; its ground floor's two windows between timber posts under a dark beam. The
# wing's front: the door with a pane (tile 1) and a lamp beside it (unlit, by the
# user's choice of no lights), under a white fascia. A tall pale chimney stands down
# the A-frame's right slope. Inside, one room: the wing opens to the A-frame block.

def chalet(cartoon):
    wing = {(i, j) for i in (0, 1) for j in (1, 2, 3)}
    block = {(i, j) for i in (2, 3, 4, 5) for j in (0, 1)}
    m = Model(6, 4, 9, "PokeN_Chalet", wing | block)
    floor = Z(1)
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    EAVE = Z(3)                                        # the walls' top, z 48
    stone = ("ch_wall", "ch_wall_light", "ch_wall_line")

    def face(u, z):
        return "ch_post_dark" if z < 18 else blocks(u, z, cartoon, stone)

    def W(axis, line, out):
        return Wall(m, axis, line, out)

    # The A-frame block: x 40..104, y 8..40; its left wall in front of the wing only.
    a_front, a_back, a_right, a_left = W("x", Y(0), -1), W("x", Y(2), +1), W("y", X(6), +1), W("y", X(2), -1)
    a_front.fill(X(2) - 1, X(6), floor, EAVE - 1, face)
    a_back.fill(X(2), X(6), floor, EAVE - 1, face)
    a_right.fill(Y(0) - 1, Y(2), floor, EAVE - 1, face)
    a_left.fill(Y(0) - 1, Y(1), floor, EAVE - 1, face)
    # The wing: x 8..40, y 24..72.
    w_front, w_back, w_left, w_right = W("x", Y(1), -1), W("x", Y(4), +1), W("y", X(0), -1), W("y", X(2), +1)
    w_front.fill(X(0) - 1, X(2) - 1, floor, EAVE - 1, face)
    w_back.fill(X(0) - 1, X(2), floor, EAVE - 1, face)
    w_left.fill(Y(1) - 1, Y(4), floor, EAVE - 1, face)
    w_right.fill(Y(2) - 1, Y(4), floor, EAVE - 1, face)
    # The opening between them (x 40, y 24..40) at the two levels a unit fills: no
    # wall; the roof over it rests on piers at its ends.
    for cy in (Y(1), Y(2)):
        post(m, X(2), cy, floor, EAVE - 1, "ch_post", 2)

    # Timber posts at the outer corners, a dark beam over the A-frame block's front
    # and back walls, as drawn.
    half = 4 if cartoon else 3
    for (cx, cy) in ((X(2), Y(0)), (X(6), Y(0)), (X(6), Y(2)), (X(0), Y(1)), (X(0), Y(4)), (X(2), Y(4))):
        for x in range(cx - half, cx + half):
            for y in range(cy - half, cy + half):
                k = x - (cx - half)
                edge = x in (cx - half, cx + half - 1) and y in (cy - half, cy + half - 1)
                label = "ch_post_dark" if edge else ("ch_post_light" if k <= 1 else "ch_post")
                for z in range(floor, EAVE):
                    m.put(x, y, z, label, "corner")

    def window(wall, ua, ub, z0, z1, bars=(), sill=True):
        """A window across u ua..ub, glass z0 + 1 .. z1 - 1 in a white frame, a dark
        sill under it."""
        wall.pane(ua, ub, z0, z1, "ch_frame", "glass_ch", inner="ch_frame" if cartoon else None,
                  bars=tuple((u, None) for u in bars))
        if sill:
            for u in range(ua - 1, ub + 2):
                for z in (z0 - 2, z0 - 1):
                    wall.put(u, -1, z, "ch_post_dark")

    # The A-frame block's ground floor: a window in each middle tile, as drawn.
    window(a_front, X(3) + 1, X(4) - 2, 31, 46)
    window(a_front, X(4) + 1, X(5) - 2, 31, 46)
    # The wing's front: the door in tile 1 (closed), red-brown boards with a pane in its
    # top; the lamp beside it, unlit; as drawn.
    m.doors += [("ey", 1, 1, 1), ("ey", 1, 1, 2)]
    d0 = X(1)                                          # x 24..39
    for u in range(d0, d0 + 16):
        k = u - d0
        for z in range(floor, 48):
            if k in (0, 15) or z in (floor, 47):
                label = "ch_door_dark"
            elif 4 <= k <= 11 and 36 <= z <= 43:
                w_front.erase(u, 0, z)
                w_front.put(u, 1, z, "glass_ch")
                continue
            elif k in (3, 12) and 35 <= z <= 44 or z in (35, 44) and 3 <= k <= 12:
                label = "ch_frame"
            else:
                label = "ch_door_line" if (k - 1) % (7 if cartoon else 3) == 0 else "ch_door"
            w_front.put(u, 0, z, label)
            w_front.put(u, 1, z, label)
    for z in range(34, 44):
        for u in (X(1) - 5, X(1) - 4, X(1) - 3):
            for w in (-2, -1):
                frame = z in (34, 43) or u != X(1) - 4
                w_front.put(u, w, z, "ch_lamp" if frame else "ch_lamp_glass")
    # The unseen sides and backs: windows of the front's kind.
    window(a_right, Y(0) + 1, Y(1) - 2, 31, 46)
    window(a_right, Y(1) + 1, Y(2) - 2, 31, 46)
    window(a_back, X(3) + 1, X(4) - 2, 31, 46)
    window(a_back, X(4) + 1, X(5) - 2, 31, 46)
    window(w_left, Y(2) + 1, Y(3) - 2, 31, 46)
    window(w_back, X(0) + 1, X(1) - 2, 31, 46)
    window(w_right, Y(3) + 1, Y(4) - 2, 31, 46)

    # The roofs: the A-frame block's steep gable, rising 3.2 a voxel in from its side
    # walls to a flat top at z 120, its eaves three out, verges two; the wing's steep
    # hip, rising 2.5 a voxel in from its eaves to a ridge along y (z 90). Where
    # they meet, the higher wins.
    ax0, ax1, ay0, ay1 = X(2) - 1, X(6), Y(0) - 1, Y(2)    # the A-frame block's outer faces
    wx0, wx1, wy0, wy1 = X(0) - 1, X(2), Y(1) - 1, Y(4)    # the wing's
    TOP = 120

    def aframe(x, y):
        if not (ax0 - 3 <= x <= ax1 + 3 and ay0 - 2 <= y <= ay1 + 2):
            return None
        d = min(x - ax0, ax1 - x)
        return (min(TOP, EAVE + int(3.2 * d) + 2), ("a", d, y))

    def hip(x, y):
        if not (wx0 - 3 <= x <= wx1 and wy0 - 3 <= y <= wy1 + 3):
            return None
        dx = min(x - wx0, wx1 - x)
        dy = min(y - wy0, wy1 - y)
        d = min(dx, dy)
        return (EAVE + int(2.5 * d) + 2, ("h", d, y if dx < dy else x))

    def paint(x, y, z, top, n, facet):
        kind, d, a = facet
        if z < top:
            return "ch_roof_dark"
        if kind == "a":
            if y in (ay0 - 2, ay1 + 2) or x in (ax0 - 3, ax1 + 3):
                return "ch_verge"
            if top >= TOP:
                return "ch_roof_line" if (x - 8) % (16 if cartoon else 8) == 0 else "ch_roof"
            return rows(d + 3, cartoon, ("ch_roof", "ch_roof_light", "ch_roof_line"), 3)
        if d <= -3:
            return "ch_verge"
        return rows(d + 3, cartoon, ("ch_roof", "ch_roof_light", "ch_roof_line"), 3)

    cols = [(x, y) for x in range(wx0 - 3, ax1 + 4) for y in range(ay0 - 2, wy1 + 4)]
    height_roof(m, cols, [aframe, hip], 5, paint)                   # five thick: steps of 3 or 4 hold together
    # The white fascia along the wing's front eave, under its edge, as drawn.
    m.role_now = "roof"
    for x in range(wx0 - 3, wx1):                      # up to the A-frame block's wall
        top = hip(x, wy0 - 3)[0]
        for z in range(top - 5, top + 1):
            m.put(x, wy0 - 3, z, "ch_verge_dark" if z == top - 5 else "ch_verge")
    m.role_now = "mid"

    # The A-frame's gables, front and back, from the beam (z 48-55) up under the
    # roof: cream, dark braces in its lower corners, three windows on the front, a
    # white verge over it, as drawn.
    for wall in (a_front, a_back):
        for u in range(ax0, ax1 + 1):
            d = min(u - ax0, ax1 - u)
            limit = min(TOP, EAVE + int(3.2 * d) + 2) - 2
            for z in range(EAVE, limit):
                if z < EAVE + 8:
                    label = "ch_beam_dark" if z in (EAVE, EAVE + 7) else "ch_beam"
                    for w in (-1, 0, 1):
                        wall.put(u, w, z, label)
                    continue
                spot = not cartoon and (u * 3 + z * 5) % 23 == 0
                label = "ch_gable_spot" if spot else "ch_gable"
                wall.put(u, 0, z, label)
                wall.put(u, 1, z, label)
            for z in range(max(EAVE + 8, limit - 3), limit):
                for w in (-1, 0, 1):
                    wall.put(u, w, z, "ch_verge")
        # The braces: dark timbers rising from the beam's ends toward the middle.
        for k in range(0, 22):
            for t in range(-1, 2 if cartoon else 1):
                for u in (ax0 + 8 + k // 2 + t, ax1 - 8 - k // 2 - t):
                    z = EAVE + 8 + k
                    for w in (-1, 0, 1):
                        wall.put(u, w, z, "ch_brace")
    for ua, ub in ((57, 67), (76, 86)):
        window(a_front, ua, ub, 63, 79, sill=False)
    window(a_front, X(4) - 6, X(4) + 5, 89, 109, sill=False)
    window(a_back, X(4) - 6, X(4) + 5, 63, 85, sill=False)

    # The chimney down the A-frame's right slope, near its back, as drawn: pale stone,
    # two dark vents near its top, its top over the roof.
    m.role_now = "mid"
    for x in range(86, 99):
        for y in range(28, 37):
            ground = max((z for z in range(TOP + 20) if (x, y, z) in m.v), default=EAVE)
            for z in range(ground + 1, TOP + 13):
                edge = x in (86, 98) or y in (28, 36)
                vent = y == 28 and 90 <= x <= 94 and z in (TOP + 6, TOP + 7, TOP + 1, TOP + 2)
                label = "ch_vent" if vent else ("ch_chim_dark" if (edge and x == 98) else (
                    "ch_chim_light" if z >= TOP + 11 else "ch_chim"))
                m.put(x, y, z, label)

    m.storeys = [{"stand": 1, "tiles": wing | block, "entry": "vault", "cut": 3}]
    m.figure = (1, 0, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The roofed gate (over the path at the bottom of poke_n.png): four tiles by one,
# open: a dark post at each corner, tie beams between them a level over a unit's
# head, and a gable roof of brown planks over them, its ridge along the gate
# under a dark cap, as drawn. Units walk under it; its posts are corner pieces,
# decoration to the fight. It stands on the map's own ground.

def roofed_gate(cartoon):
    m = Model(4, 1, 5, "PokeN_RoofedGate")
    m.ground_under = True
    x0, x1, y0, y1 = X(0), X(4), Y(0), Y(1)            # posts on x 8, 72 and y 8, 24
    rx0, rx1, ry0, ry1 = x0 - 8, x1 + 7, y0 - 8, y1 + 7    # the roof: x 0..79, y 0..31
    mid = (ry0 + ry1) / 2.0

    def under(y):
        """The roof's underside over row y."""
        d = (y - ry0) if y < mid else (ry1 - y)
        return 48 + int(math.floor(1.1 * d))

    # A post at each corner from its footing in the ground up to the roof.
    half = 3 if cartoon else 2
    for cx in (x0, x1):
        for cy in (y0, y1):
            for x in range(cx - half, cx + half):
                for y in range(cy - half, cy + half):
                    for z in range(0, under(y)):
                        light = x == cx - half
                        m.put(x, y, z, "gt_post_light" if light else ("gt_post_dark" if x == cx + half - 1 else "gt_post"),
                              "corner")
    # Tie beams over the posts, front and back and at the ends, from level 3 up to the
    # roof, so nothing of them is in the levels a unit fills.
    m.role_now = "roof"
    for cy in (y0, y1):
        for x in range(x0 - half - 2, x1 + half + 2):
            for y in range(cy - 1, cy + 1):
                for z in range(48, under(y)):
                    m.put(x, y, z, "gt_beam_dark" if z == 48 else "gt_beam")
    for cx in (x0, x1):
        for y in range(y0, y1):
            for x in range(cx - 1, cx + 1):
                for z in range(48, under(y)):
                    m.put(x, y, z, "gt_beam_dark" if z == 48 else "gt_beam")
    m.role_now = "mid"

    # The roof: a gable, its ridge along x over y 15 and 16, rising 1.1 a voxel in
    # from its eaves (z 48, eight out all round), resting on the tie beams, planks down
    # its slopes, a dark cap along the ridge and dark edges; its back slope the art's
    # dark band along the top, as drawn.
    m.role_now = "roof"
    for x in range(rx0, rx1 + 1):
        for y in range(ry0, ry1 + 1):
            b = under(y)
            for z in range(b, b + 3):
                if x in (rx0, rx1) or y in (ry0, ry1):
                    label = "gt_cap"
                elif z < b + 1:
                    label = "gt_plank_dark"
                else:
                    p = 16 if cartoon else 8
                    k = (x - 8) % p
                    if k in (0, p - 1):
                        label = "gt_gap"
                    elif k in (1, p - 2):
                        label = "gt_plank_dark"
                    elif cartoon or k not in (p // 2 - 1, p // 2):
                        label = "gt_plank"
                    else:
                        label = "gt_plank_light"
                m.put(x, y, z, label)
    for x in range(rx0, rx1 + 1):
        for y in range(int(mid) - 1, int(mid) + 2):
            top = under(y) + 2
            for z in (top + 1, top + 2):
                m.put(x, y, z, "gt_cap" if z == top + 2 or x in (rx0, rx1) else "gt_cap_light")
    m.role_now = "mid"

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "walk", "cut": 3}]
    m.figure = (1, 0, 1, 200)
    return m


BUILDINGS = {
    "RedHouse": red_house,
    "Chalet": chalet,
    "RoofedGate": roofed_gate,
}


def build(kind, cartoon):
    return BUILDINGS[kind](cartoon)
