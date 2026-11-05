"""The poke_g buildings' geometry, on VCOM's grid, as the poke_f buildings are
drawn (poke_f/buildings/sculpt.py, whose helpers this copies; poke_g's domed
centre is poke_f's drawing recoloured, so its geometry is copied whole).

Every model is drawn on the game's tile grid so that it can be cut into the
game's 16-cubed pieces cleanly (a middle, an edge or a corner slot each):

- 16 voxels a tile. Tile boundaries run at x = 8 + 16i and y = 8 + 16j: every
  canvas has half a tile of margin all round the footprint, which holds the
  outer halves of the edge pieces (eaves, canopies, sills, signs, posts).
- Levels are z = 16k. Level 0 (z 0-15) is a building's own floor, a foundation
  standing in for the map's ground blocks under it. Units stand on the top of a
  cell: a floor at level 0 is stood on at level 1.
- A wall is two voxels thick across its tile boundary B (voxels B - 1 and B).
- A door is closed, as drawn, and each leaf fills exactly one doorway slot: one
  tile wide, the two levels a unit fills (the user's choice, 2026-10-28).
- A window keeps within its tile, or stands over a tile boundary as the art
  draws it, each half its own window piece. Its glass is over a solid sill course
  a level high, so a unit vaults in over the sill and has half cover at it.
- Upper floors are real (a slab a level, a room over it), reached only where the
  art draws a way up (the user's choice): here nowhere, so the green houses'
  upper rooms are closed off.
- Corners where four tiles meet are decoration to the fight: the centres'
  pillars and rounded corners, the porch's posts stand there.
- A porch a tile out (the lodge's) is a tile of the footprint: its floor a
  level-0 piece, its roof the middle of its tile a level over a unit's head.
- MagicaVoxel axes: x across the front, y from the front (low y) to the back, z
  up. The front faces -y (Godot +z), as every building in this workspace.

Voxels carry material labels (palettes.LABELS), not colours, and each its role
for the game's slots (Model.role). Cartoon builds the same building simplified
and regularised on the same grid: its doors, windows and slots are the Base's.
Each model also says what the rules must see of it (storeys, cuts), which
qa/integration.py checks in the game.
"""
import math
from collections import deque

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
# The domed centre (middle of poke_g.png): poke_f's centre drawn again, its blue
# panels red-brown tiles (palettes.py), so its geometry is poke_f's, copied whole.
# Six tiles by four, one tall storey (five courses): white walls with purple-blue
# windows over two tiles each and a glass double door under a canopy, flanked by
# banded posts; above them a band of tiles; a flat tiled roof; on it the red dome,
# the top of a Poke Ball, with its band and its button at the front (as drawn: the
# user's choice); tall banded wooden pillars at the four corners; steps before the
# door.

def dome_center(cartoon):
    m = Model(6, 4, 9, "PokeG_DomeCenter")
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
# Shapes the buildings below share.

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


def ring_depths(cols):
    """For a set of (x, y) columns, how many steps each is in from the outside (0
    for those beside a column outside it), by a breadth-first search."""
    depth = {}
    queue = deque()
    for (x, y) in cols:
        if any((x + dx, y + dy) not in cols for dx, dy in STEPS):
            depth[(x, y)] = 0
            queue.append((x, y))
    while queue:
        x, y = queue.popleft()
        for dx, dy in STEPS:
            n = (x + dx, y + dy)
            if n in cols and n not in depth:
                depth[n] = depth[(x, y)] + 1
                queue.append(n)
    return depth


STEPS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def mirrored(m, name):
    """[m] mirrored left to right (across x), as the art draws one of the stepped
    green houses: every voxel and its role, the doors, storeys, stairs, climbs and
    the soldier. A tile boundary stays a tile boundary, so walls stay on the grid;
    the game turns pieces but cannot mirror them, so its pieces are kinds of their
    own (the user's choice: a model of its own)."""
    W = m.size[0]
    tx = m.tiles[0]
    flip = lambda i: tx - 1 - i
    out = Model(m.tiles[0], m.tiles[1], m.size[2] // TILE, name, {(flip(i), j) for (i, j) in m.footprint})
    for (x, y, z), label in m.v.items():
        out.put(W - 1 - x, y, z, label, m.role[(x, y, z)])
    out.roof_tiles = {(flip(i), j) for (i, j) in m.roof_tiles}
    out.doors = [("ey", flip(a), b, k) if t == "ey" else ("ex", tx - a, b, k) for (t, a, b, k) in m.doors]
    out.storeys = [dict(s, tiles={(flip(i), j) for (i, j) in s["tiles"]}) for s in m.storeys]
    out.stairs = {(flip(i), j): lv for (i, j), lv in m.stairs.items()}
    out.climbs = [((flip(a[0]), a[1], a[2]), (flip(b[0]), b[1], b[2])) for a, b in m.climbs]
    fi, fj, fk, yaw = m.figure
    out.figure = (flip(fi), fj, fk, yaw)
    return out


# ----------------------------------------------------------------------------
# The green houses (seven in poke_g.png), two designs under one flat roof of green
# standing seams, both of two storeys over three tiles' depth: brown panels framed
# by dark timber lines, cream window frames, a dark green plinth, a beam round the
# house between the storeys. The stepped house (three copies, one of them drawn
# mirrored: its own model) is a block of two storeys two tiles wide with a wing of
# one storey two tiles wide beside it, the door in the wing; the wide house (four
# copies), one block four tiles wide, the door in tile 1. Their windows are drawn
# over tile boundaries (each half a window piece) or, the wide house's ground
# floor's, within its tile. Upstairs is closed off: no stair is drawn.

def gh_beam(z, cartoon):
    """The beam round the house between the storeys (z 48-63), as drawn: a dark
    line under it, darker below, lighter above."""
    if z < 50:
        return "gh_timber"
    if cartoon:
        return "gh_panel_low" if z < 56 else "gh_beam"
    if z < 54:
        return "gh_panel_low"
    if z == 54:
        return "gh_beam_dark"
    return "gh_beam" if z < 62 else "gh_panel"


def gh_panel(storey, z, cartoon):
    """A panel's colour by height, as drawn: the ground storey's darker at its top
    and bottom, the upper storey's lighter in its middle."""
    if storey == "low":
        if cartoon:
            return "gh_panel_low"
        return "gh_panel_low_dark" if (z < 24 or z >= 41) else "gh_panel_low"
    if cartoon:
        return "gh_panel"
    if z >= 91:
        return "gh_panel_low"
    return "gh_panel_light" if 68 <= z < 87 else "gh_panel"


def gh_window(wall, c, g0, g1, cartoon, half=6, sash=2, frame=2):
    """A two-pane window centred on u = c (a tile boundary, or a tile's middle):
    glass across c - half .. c + half - 1 and up z g0..g1 in the inner layer, a
    mullion two voxels wide between its panes (c - 1, c); a sash round the glass,
    the cream frame round the sash, a cream sill a voxel proud under it."""
    gu0, gu1 = c - half, c + half - 1
    su0, su1 = gu0 - sash, gu1 + sash
    fu0, fu1 = su0 - frame, su1 + frame
    sz0, sz1 = g0 - sash, g1 + sash
    fz0, fz1 = sz0 - frame, sz1 + frame
    for u in range(fu0, fu1 + 1):
        for z in range(fz0, fz1 + 1):
            if gu0 <= u <= gu1 and g0 <= z <= g1:
                if u in (c - 1, c):
                    wall.put(u, 0, z, "gh_sash")
                    wall.put(u, 1, z, "gh_sash")
                else:
                    wall.erase(u, 0, z)
                    wall.put(u, 1, z, "glass_house")
                continue
            if su0 <= u <= su1 and sz0 <= z <= sz1:
                label = "gh_sash_dark" if (z > g1 and not cartoon) else "gh_sash"
            elif not cartoon and (z > sz1 or u < su0):
                label = "gh_frame_light"
            else:
                label = "gh_frame"
            wall.put(u, 0, z, label)
            wall.put(u, 1, z, label)
    for u in range(fu0, fu1 + 1):
        wall.put(u, -1, fz0, "gh_frame_shade")


def gh_door(wall, d0, knob_left, cartoon):
    """A closed door filling the tile from u d0 (its leaf one doorway slot, the two
    levels a unit fills), as drawn: red-brown planks three voxels and two, darker
    above, lighter below, dark edges, a brass knob."""
    for u in range(d0, d0 + 16):
        k = u - d0
        for z in range(16, 48):
            if k in (0, 15) or z in (16, 17):
                label = "gh_door_edge"
            else:
                dark = ((k - 1) % 5) >= 3 if not cartoon else (k - 1) % 7 == 6
                if z >= 32:
                    label = "gh_door_dark" if dark else "gh_door"
                else:
                    label = "gh_door" if dark else "gh_door_light"
            wall.put(u, 0, z, label)
            wall.put(u, 1, z, label)
    ku = d0 + 2 if knob_left else d0 + 12
    for z in (30, 31):
        for du in ((0, 1) if not cartoon else (0, 1, 2)):
            wall.put(ku + du, -1, z, "gh_brass")


def gh_face(wall, u0, u1, storey, feats, cartoon):
    """Paints a green house's wall over u0..u1 for one storey ('low', z 16-63: the
    dark green plinth, the panels, the beam, a voxel proud; 'up', z 64-95: the
    panels between dark lines), then its features over it in order: ('line', u) a
    dark timber line; ('cream', a, b) a cream panel; ('window', c, half, sash,
    frame, g0, g1) a window; ('door', d0, knob_left) a door."""
    z_lo, z_hi = (16, 63) if storey == "low" else (64, 95)
    for u in range(u0, u1 + 1):
        for z in range(z_lo, z_hi + 1):
            if storey == "low":
                label = "gh_plinth" if z < 20 else (gh_beam(z, cartoon) if z >= 48 else gh_panel("low", z, cartoon))
            else:
                label = "gh_timber" if z in (64, 95) else gh_panel("up", z, cartoon)
            wall.put(u, 0, z, label)
            wall.put(u, 1, z, label)
    if storey == "low":
        for u in range(u0 - 1, u1 + 2):
            for z in range(48, 64):
                wall.put(u, -1, z, gh_beam(z, cartoon))
    za, zb = (20, 47) if storey == "low" else (65, 94)
    for f in feats:
        if f[0] == "line":
            for z in range(za, zb + 1):
                wall.put(f[1], 0, z, "gh_timber")
                wall.put(f[1], 1, z, "gh_timber")
        elif f[0] == "cream":
            for u in range(f[1], f[2] + 1):
                for z in range(za, zb + 1):
                    wall.put(u, 0, z, "gh_frame")
                    wall.put(u, 1, z, "gh_frame")
        elif f[0] == "window":
            _, c, half, sash, frame, g0, g1 = f
            gh_window(wall, c, g0, g1, cartoon, half, sash, frame)
        elif f[0] == "door":
            gh_door(wall, f[1], f[2], cartoon)


def gh_roof(m, xa, xb, base, cartoon, verge=(1, 1)):
    """A flat roof of green standing seams over the walls whose outer faces run x
    xa..xb and y 7..56, as the art draws it (flat, its seams front to back and
    nothing else across it: a pitch would show its steps as lines across them); its
    eaves two voxels out and its verges [verge] past the ends; seams every eight
    voxels, lighter and darker panels between them, a darker edge and its outline
    at the eaves and verges, as drawn."""
    ov = 2
    ya, yb = 7, 56
    cx0, cx1 = xa - verge[0], xb + verge[1]
    cy0, cy1 = ya - ov, yb + ov
    thick = 3 if cartoon else 2

    def paint(x, y, z, b, t):
        e = min(y - cy0, cy1 - y)
        end = (x == cx0 and verge[0]) or (x == cx1 and verge[1])
        if z == b and (e == 0 or end):
            return "gh_roof_outline"
        if z == b and ya < y < yb and xa < x < xb:
            return "ceiling"
        if e <= 1 or end or z < t:
            return "gh_roof_edge"
        k = (x - 6) % 16
        if cartoon:
            return "gh_roof_seam" if k in (0, 8) else ("gh_roof_light" if k < 8 else "gh_roof")
        if k in (0, 8):
            return "gh_roof_seam"
        if k in (9, 15):
            return "gh_roof_mid"
        return "gh_roof_light" if 2 <= k <= 6 else "gh_roof"

    cols = [(x, y) for x in range(cx0, cx1 + 1) for y in range(cy0, cy1 + 1)]
    fill_roof(m, cols, lambda x, y: base, lambda x, y: base + thick - 1, paint)


def green_house(kind, cartoon):
    stepped = kind == "stepped"
    m = Model(4, 3, 7, "PokeG_GreenHouse" if stepped else "PokeG_GreenWideHouse")
    floor = Z(1)
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    y0, y1 = Y(0), Y(3)
    low, _ = walls_of(m, X(0), X(4), y0, y1)
    bx1 = X(2) if stepped else X(4)
    up, _ = walls_of(m, X(0), bx1, y0, y1)
    block = {(i, j) for i in range(2 if stepped else 4) for j in range(3)}

    def win(c, storey, half=6, sash=2, frame=2, g1=None):
        g0, g1d = (32, 43) if storey == "low" else (80, 91)
        return ("window", c, half, sash, frame, g0, g1 if g1 is not None else g1d)

    lines = lambda *us: [("line", u) for u in us]
    # The sides: a window in the middle tile on each storey, as the front's.
    side = lambda storey: lines(7, 8, 21, 42, 55, 56) + [win(Y(1) + 8, storey)]
    if stepped:
        # Ground floor: the block's window over the boundary in its middle, the door
        # in the wing's first tile (its knob on the right), a cream jamb beside it.
        gh_face(low["front"], 7, 72, "low", lines(7, 8, 13, 34, 39, 60, 71, 72) + [("cream", 56, 59),
                win(X(1), "low"), ("door", X(2), False)], cartoon)
        gh_face(low["back"], 7, 72, "low", lines(7, 8, 13, 34, 39, 40, 45, 66, 71, 72) + [win(X(1), "low"),
                win(X(3), "low")], cartoon)
        gh_face(low["left"], 7, 56, "low", side("low"), cartoon)
        gh_face(low["right"], 7, 56, "low", side("low"), cartoon)
        # The block's upper storey; its right wall stands over the wing's roof.
        gh_face(up["front"], 7, 40, "up", lines(7, 8, 13, 34, 39, 40) + [win(X(1), "up")], cartoon)
        gh_face(up["back"], 7, 40, "up", lines(7, 8, 13, 34, 39, 40) + [win(X(1), "up")], cartoon)
        gh_face(up["left"], 7, 56, "up", side("up"), cartoon)
        gh_face(up["right"], 7, 56, "up", side("up"), cartoon)
        # The block's ground floor opens into the wing through the middle tile of the
        # wall between them, which bears the upper storey's wall.
        inner = Wall(m, "y", X(2), +1)
        inner.fill(Y(0), Y(3) - 1, floor, 63, lambda u, z: gh_panel("low", z, cartoon))
        inner.cut(Y(1), Y(2) - 1, floor, 47)
        m.doors += [("ey", 2, 0, 1), ("ey", 2, 0, 2)]
    else:
        gh_face(low["front"], 7, 72, "low", lines(7, 8, 19, 56, 71, 72) + [("cream", 20, 23),
                ("door", X(1), True), win(X(2) + 8, "low", 6, 1, 1, 45)], cartoon)
        gh_face(low["back"], 7, 72, "low", lines(7, 8, 13, 34, 45, 66, 71, 72) + [win(X(1), "low"),
                win(X(3), "low")], cartoon)
        gh_face(low["left"], 7, 56, "low", side("low"), cartoon)
        gh_face(low["right"], 7, 56, "low", side("low"), cartoon)
        # Upstairs the front's two windows stand in one cream panel, as drawn.
        for key in ("front", "back"):
            gh_face(up[key], 7, 72, "up", lines(7, 8, 13, 66, 71, 72) + [("cream", 14, 65), win(X(1), "up"),
                    win(X(3), "up")], cartoon)
        gh_face(up["left"], 7, 56, "up", side("up"), cartoon)
        gh_face(up["right"], 7, 56, "up", side("up"), cartoon)
        m.doors += [("ey", 1, 0, 1), ("ey", 1, 0, 2)]

    # The upper floor (level 3), over the block.
    slab(m, block, 56, 63, lambda x, y: planks(x, y, cartoon))
    # The roofs: the block's from its walls' top (z 96); the stepped house's wing's
    # from its own (z 64), against the block's wall.
    gh_roof(m, 7, 40 if stepped else 72, Z(6), cartoon)
    if stepped:
        gh_roof(m, 41, 72, Z(4), cartoon, verge=(0, 1))

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 3},
                 {"stand": 4, "tiles": block, "entry": None, "cut": 6}]
    m.figure = (2 if stepped else 1, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The red centre (bottom middle of poke_g.png): five tiles by three, one storey of
# three courses with rounded white corners, light blue-grey walls, a dark line under
# a band round its top; dark grey pillars in its end tiles; the glass door (tile 2)
# under a red canopy narrowing to its front edge on two posts; the Poke Ball emblem
# over it (as drawn: the user's choice) on the middle section's front, which rises
# a course above the walls. Its roof is red in three sections front to back: a
# barrel vault in the middle and, either side, a quarter round rising from the side
# walls to it, shaded in stripes as drawn. The art shows only the front: the sides
# and back have windows of the door's glass.

def red_center(cartoon):
    m = Model(5, 3, 6, "PokeG_RedCenter")
    x0, x1, y0, y1 = X(0), X(5), Y(0), Y(3)            # walls on x 8, 88 and y 8, 56
    floor = Z(1)
    foundation(m, m.footprint, lambda x, y: stone_tiles(x, y, cartoon))
    walls, _ = walls_of(m, x0, x1, y0, y1)
    front, back = walls["front"], walls["back"]
    rc = 9.0 if cartoon else 8.0
    inward = rounded_box(x0 - 1, x1 + 1, y0 - 1, y1 + 1, rc)
    # The floor's paving stops at the rounded walls: past them, at the corners, the
    # foundation's stone.
    for x in range(x0 - 1, x1 + 1):
        for y in range(y0 - 1, y1 + 1):
            if inward(x, y) <= 0 and (x, y, 15) in m.v:
                m.put(x, y, 14, "found", "mid")
                m.put(x, y, 15, "found_dark", "mid")

    def course(z, corner):
        if z < 18:
            return "rc_foot_dark" if z == 16 else "rc_foot"
        if 48 <= z < 50:
            return "rc_line"
        if not cartoon and z in (50, 63):
            return "rc_wall_shade"
        return "rc_white" if corner else "rc_wall"

    # The shell, two voxels thick inside the rounded outline: the straight parts the
    # edges' walls, the arcs the corners' (decoration to the fight).
    for x in range(x0 - 1, x1 + 1):
        for y in range(y0 - 1, y1 + 1):
            d = inward(x, y)
            if not 0 < d < 2.01:
                continue
            near_x = x < x0 + rc - 1 or x > x1 - rc
            near_y = y < y0 + rc - 1 or y > y1 - rc
            if near_x and near_y:
                role, corner = "corner", True
            else:
                role, corner = ("ey" if (y < y0 + 1 or y > y1 - 2) else "ex"), False
            for z in range(floor, Z(4)):
                m.put(x, y, z, course(z, corner), role)

    # Pillars in the end tiles, front and back: dark grey, two voxels proud, fluted.
    def pillar(wall, c):
        for u in range(c - 3, c + 3):
            for w in (-2, -1, 0, 1):
                for z in range(floor, 48):
                    if z < 18:
                        label = "rc_pillar_edge"
                    elif z >= 46:
                        label = "rc_pillar_dark"
                    elif u in (c - 3, c + 2):
                        label = "rc_frame"
                    elif u == c and not cartoon:
                        label = "rc_pillar_mid"
                    else:
                        label = "rc_pillar"
                    wall.put(u, w, z, label)

    for wall in (front, back):
        pillar(wall, X(0) + 8)
        pillar(wall, X(4) + 8)

    def window(wall, c):
        """A window of the door's glass in a dark grey frame, glass in level 2 over
        the sill course."""
        wall.pane(c - 6, c + 5, 31, 47, "rc_frame", "glass_red")
        for u in range(c - 6, c + 6):
            wall.put(u, -1, 31, "rc_frame")

    for key in ("left", "right"):
        window(walls[key], Y(1) + 8)
    for c in (X(1) + 8, X(3) + 8):
        window(back, c)

    # The door, tile 2 (closed): one leaf of glass in a dark grey frame, its knob.
    m.doors += [("ey", 2, 0, 1), ("ey", 2, 0, 2)]
    d0 = X(2)
    for u in range(d0, d0 + 16):
        for z in range(floor, 48):
            k = u - d0
            if k in (0, 1, 14, 15) or z in (floor, floor + 1, 46, 47):
                front.put(u, 0, z, "rc_frame")
                front.put(u, 1, z, "rc_frame")
            else:
                front.erase(u, 0, z)
                front.put(u, 1, z, "glass_red")
    for z in (30, 31):
        front.put(d0 + 3, 0, z, "rc_knob")

    # The canopy over it (level 3): red, its top sloping a little from the wall,
    # seven voxels out, narrowing toward its front edge, as drawn; two posts under
    # its front corners.
    for dd in range(1, 8):
        ua, ub = 23 + dd, 72 - dd
        ztop = 53 - (dd * 3) // 7
        for u in range(ua, ub + 1):
            for z in range(48, ztop + 1):
                rim = dd == 7 or u in (ua, ub)
                if z == 48:
                    label = "rc_red_edge" if rim else "rc_red_deep"
                elif rim:
                    label = "rc_red_dark"
                else:
                    label = "rc_red" if z == ztop else "rc_red_mid"
                front.put(u, -dd, z, label)
    for (pa, pb) in ((33, 37), (58, 62)):
        for u in range(pa, pb + 1):
            for w in (-7, -6, -5):
                for z in range(floor, 48):
                    if z < 17:
                        label = "rc_pillar_edge"
                    elif z >= 45:
                        label = "rc_pillar_dark"
                    elif u in (pa, pb):
                        label = "rc_frame"
                    elif u == (pa + pb) // 2 and not cartoon:
                        label = "rc_pillar_mid"
                    else:
                        label = "rc_pillar"
                    front.put(u, w, z, label)

    # The roof (levels 4 and 5): a shell three voxels thick over the profile h(x), two
    # voxels out all round; the walls rise under it to meet it (its tympana, in the
    # walls' colour); a ceiling over the room at z 64.
    ov = 2
    xs0, xs1, ys0, ys1 = x0 - 1 - ov, x1 + ov, y0 - 1 - ov, y1 + ov

    def h(x):
        c = x + 0.5
        if c <= 28.5:
            t = (28.5 - c) / 24.0
            return 64 + 16 * math.sqrt(max(0.0, 1 - t * t))
        if c >= 67.5:
            t = (c - 67.5) / 24.0
            return 64 + 16 * math.sqrt(max(0.0, 1 - t * t))
        t = (c - 48.0) / 19.5
        return 80 + 12 * math.sqrt(max(0.0, 1 - t * t))

    def stripe(x):
        """The roof's colour across x, as drawn (lit from the left, its sections in
        stripes front to back)."""
        if cartoon:
            if x in (28, 67):
                return "rc_red"
            if 29 <= x <= 66:
                return "rc_red_hi" if x < 38 else ("rc_red" if x < 57 else "rc_red_mid")
            return "rc_red_light"
        if x <= 12:
            return "rc_red_mid" if x % 2 else "rc_red"
        if x <= 25:
            return "rc_red_light"
        if x <= 28:
            return "rc_red"
        if x <= 34:
            return "rc_red_hi" if x % 3 else "rc_red_light"
        if x <= 52:
            return "rc_red_light" if x in (37, 41, 45) else "rc_red"
        if x <= 60:
            return "rc_red_mid"
        if x <= 66:
            return "rc_red_shade"
        if x <= 68:
            return "rc_red"
        if x <= 81:
            return "rc_red_light"
        return "rc_red_mid" if x % 2 == 0 else "rc_red"

    thick = 3

    def top_of(x):
        return int(round(h(x)))

    def roof_paint(x, y, z, b, t):
        if rroof(x, y) < 1:
            return "rc_red_dark"
        if z < t:
            return "rc_red_deep"
        if y in (ys0 + 1, ys1 - 1):
            return "rc_red_mid"
        return stripe(x)

    rroof = rounded_box(xs0, xs1 + 1, ys0, ys1 + 1, rc + ov)
    cols = [(x, y) for x in range(xs0, xs1 + 1) for y in range(ys0, ys1 + 1) if rroof(x, y) > 0]
    fill_roof(m, cols, lambda x, y: top_of(x) - thick + 1, lambda x, y: top_of(x), roof_paint)
    # The tympana: the walls rise along their rounded outline to meet the shell (the
    # middle section's front a course above the walls, the emblem's ground).
    for x in range(x0 - 1, x1 + 1):
        for y in range(y0 - 1, y1 + 1):
            d = inward(x, y)
            if not 0 < d < 2.01:
                continue
            near_x = x < x0 + rc - 1 or x > x1 - rc
            near_y = y < y0 + rc - 1 or y > y1 - rc
            role = "corner" if (near_x and near_y) else ("ey" if (y < y0 + 1 or y > y1 - 2) else "ex")
            for z in range(Z(4), top_of(x) - thick + 1):
                shade = z == Z(5) - 1 and 29 <= x <= 66 and role == "ey" and not cartoon
                m.put(x, y, z, "rc_wall_shade" if shade else ("rc_white" if role == "corner" else "rc_wall"), role)
    # The ceiling over the room, inside the walls.
    for x in range(x0, x1):
        for y in range(y0, y1):
            if inward(x, y) >= 2.01 and (x, y, Z(4)) not in m.v:
                m.put(x, y, Z(4), "ceiling", "mid")

    # The emblem on the middle section's front, over the canopy: a Poke Ball seen
    # front on, in the walls' blues and white, two voxels proud, as drawn.
    cx, cz = X(2) + 7.5, 64.0
    R = 11.0 if cartoon else 10.0
    for u in range(int(cx - R) - 1, int(cx + R) + 2):
        for z in range(int(cz - R) - 1, int(cz + R) + 2):
            r = math.hypot(u - cx, z - cz)
            if r > R:
                continue
            if r > R - 1.3:
                label = "rc_ball_rim" if z > cz else "rc_ball_rim_dark"
            elif r <= 0.65 * R:
                if r > 0.52 * R:
                    label = "rc_ball_dark"
                elif r > 0.35 * R or cartoon:
                    label = "rc_ball_light" if (r > 0.22 * R or not cartoon) else "rc_ball_dark"
                elif r > 0.22 * R:
                    label = "rc_ball_dark"
                else:
                    label = "rc_ball_blue"
            elif abs(z - cz) < 0.2 * R:
                label = "rc_ball_dark"
            elif z > cz + 0.55 * R and not cartoon:
                label = "rc_ball_white"
            else:
                label = "rc_ball_light"
            for w in (-2, -1):
                front.put(u, w, z, label)

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 4}]
    m.figure = (1, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The Mart (bottom left of poke_g.png): four tiles by three, one storey of three
# courses, light blue-grey walls white at the corners, a dark line under a band
# round its top, a flat roof; on it a blue slab of square tiles with rounded
# corners and edges, a light stripe round its face; in front of it the sign, MART
# on it in blue (as drawn: the user's choice). The front: the glass door (tile 1),
# the shop window over tiles 2 and 3 on a grey riser, dark grey columns standing
# out between them, as drawn. The sides and back have windows of the shop's kind.

FONT = {  # five by five, as the art's sign draws them
    "M": ["#...#", "##.##", "#####", "#.#.#", "#...#"],
    "A": ["#####", "#...#", "#####", "#...#", "#...#"],
    "R": ["####.", "#...#", "####.", "#...#", "#...#"],
    "T": ["#####", "..#..", "..#..", "..#..", "..#.."],
}


def mart(cartoon):
    m = Model(4, 3, 6, "PokeG_Mart")
    x0, x1, y0, y1 = X(0), X(4), Y(0), Y(3)            # walls on x 8, 72 and y 8, 56
    floor = Z(1)
    foundation(m, m.footprint, lambda x, y: stone_tiles(x, y, cartoon))
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front = walls["front"]
    white = 5                                           # the white corners: five voxels of each wall

    def painter(lo, hi):
        def paint(u, z):
            if z < 18:
                return "mt_col_dark" if z == 16 else "mt_col"
            if 48 <= z < 50:
                return "mt_line"
            if z >= 50:
                return "mt_wall_shade" if (not cartoon and z in (50, 51, 62, 63)) else "mt_wall"
            return "mt_white" if (u < lo + white or u > hi - white) else "mt_wall"
        return paint

    for key, wall in walls.items():
        u0, u1 = spans[key]
        wall.fill(u0 - 1, u1 + 1, floor, Z(4) - 1, painter(u0 - 1, u1 + 1))

    def shop_window(wall, ua, ub, bars):
        """Glass in level 2 over a grey riser, a light grey frame, the bars at
        [bars], a transom near its top, as drawn."""
        wall.fill(ua, ub, 18, 30, "mt_frame")
        wall.pane(ua, ub, 31, 47, "mt_frame", "glass_mart",
                  bars=tuple((u, None) for u in bars) + (((None, 41), (None, 42)) if not cartoon else ((None, 42),)),
                  bar_label="mt_frame")
        for u in range(ua + 1, ub):
            if (u not in bars) and not cartoon:
                wall.put(u, 0, 42, "mt_bar")
                wall.put(u, 1, 42, "mt_bar")
            wall.put(u, -1, 31, "mt_bar")

    # The door, tile 1 (closed): glass in a dark grey frame, its knob.
    m.doors += [("ey", 1, 0, 1), ("ey", 1, 0, 2)]
    d0 = X(1)
    for u in range(d0, d0 + 16):
        for z in range(floor, 48):
            k = u - d0
            if k in (0, 1, 14, 15) or z in (floor, floor + 1, 46, 47):
                front.put(u, 0, z, "mt_frame_dark")
                front.put(u, 1, z, "mt_frame_dark")
            else:
                front.erase(u, 0, z)
                front.put(u, 1, z, "glass_mart")
    for z in (28, 29):
        front.put(d0 + 3, 0, z, "mt_knob")
    # The shop window over tiles 2 and 3, three panes; the sides' and back's.
    shop_window(front, X(2) + 2, X(4) - 10, (48, 49, 55, 56) if not cartoon else (55, 56))
    for key in ("left", "right"):
        shop_window(walls[key], Y(1) + 2, Y(2) - 2, (32,) if not cartoon else ())
    for c in (X(1) + 8, X(2) + 8):
        shop_window(walls["back"], c - 6, c + 6, (c,) if not cartoon else ())

    # Dark grey columns two voxels proud: by the left corner, between the door and the
    # window, and by the right corner, as drawn.
    for (ua, ub) in ((13, 17), (38, 42), (62, 66)):
        for u in range(ua, ub + 1):
            for w in (-2, -1, 0, 1):
                for z in range(floor, 48):
                    if z == floor:
                        label = "mt_col_edge"
                    elif z >= 46:
                        label = "mt_col_dark"
                    elif u in (ua, ub):
                        label = "mt_col_edge"
                    elif u == (ua + ub) // 2 and not cartoon:
                        label = "mt_col"
                    else:
                        label = "mt_col_light"
                    front.put(u, w, z, label)

    # The flat roof (level 4, z 64-65): the walls' colour, white over the corners.
    def flat_paint(x, y, z, b, t):
        inside = x0 <= x < x1 and y0 <= y < y1
        if z == b and inside:
            return "ceiling"
        corner = (x < x0 + white - 1 or x > x1 - white) and (y < y0 + white - 1 or y > y1 - white)
        return "mt_white" if corner else "mt_wall"

    fill_roof(m, [(x, y) for x in range(x0 - 1, x1 + 1) for y in range(y0 - 1, y1 + 1)],
              lambda x, y: Z(4), lambda x, y: Z(4) + 1, flat_paint)

    # The blue slab on it: x 12-67, y 12-51, rounded at its corners (radius 6) and
    # along its top edge (radius 4); square tiles with pale dots on its top, a light
    # stripe round its face, as drawn. Hollow: its faces and top two voxels thick.
    rin = rounded_box(12, 68, 12, 52, 7.0 if cartoon else 6.0)
    ri = 4.0

    def slab_top(x, y):
        d = rin(x, y)
        if d >= ri:
            return 87
        return 83 + int(round(math.sqrt(max(0.0, ri * ri - (ri - d) ** 2))))

    def slab_bottom(x, y):
        return 66 if rin(x, y) < 2 else slab_top(x, y) - 1

    dot = 16 if cartoon else 8
    dots = (6, 7, 8, 9) if cartoon else (3, 4)

    def slab_paint(x, y, z, b, t):
        d = rin(x, y)
        if d < 1:
            if z <= 67:
                return "mt_roof_edge"
            if z in ((71, 72) if not cartoon else (70, 71, 72)):
                return "mt_stripe"
            if z >= 83:
                return "mt_roof_mid"
            return "mt_roof_shade" if z >= 79 else "mt_roof_deep"
        if d < ri:
            return "mt_roof_mid" if z >= 84 else ("mt_roof_shade" if z == t else "mt_roof_dark")
        if z < t:
            return "mt_roof_dark"
        if (x - 12) % dot in dots and (y - 12) % dot in dots:
            return "mt_roof_dot"
        return "mt_roof"

    fill_roof(m, [(x, y) for x in range(12, 68) for y in range(12, 52) if rin(x, y) > 0],
              slab_bottom, slab_top, slab_paint)

    # The sign over the door and the window: a board in a grey frame three voxels
    # thick, standing in front of the slab's face from the band up, white along its
    # top, MART on its face in blue, as drawn (Cartoon: the letters a voxel proud).
    s0, s1, z0, z1 = 26, 53, 62, 87
    for u in range(s0, s1 + 1):
        for z in range(z0, z1 + 1):
            if z == z1:
                label = "mt_sign_edge"
            elif u in (s0, s1) or z == z0:
                label = "mt_sign_dark"
            elif z >= 82:
                label = "mt_sign_top"
            elif z >= 68:
                label = "mt_sign"
            else:
                label = "mt_sign_low"
            for w in (-3, -2, -1):
                front.put(u, w, z, label)
    tu0 = (s0 + s1) // 2 - 11
    for n, ch in enumerate("MART"):
        for row, bits in enumerate(FONT[ch]):
            for col, bit in enumerate(bits):
                if bit != "#":
                    continue
                for dz in (0, 1):
                    z = 75 - 2 * row - dz
                    front.put(tu0 + n * 6 + col, -4 if cartoon else -3, z, "mt_letter")

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 4}]
    m.figure = (0, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The wooden lodge (top right of poke_g.png): five tiles by four, one storey of
# three courses, under a thick flat roof of planks with a board fascia, on which a
# raised part with chamfered corners, planked and faced the same way; the front: a
# corner panel and a timber post in each end tile, windows of small panes in tiles
# 1 and 3 (glass in levels 2 and 3 over the sill course), the door in tile 2 under a
# porch: the flat roof carried a tile out over a flagged path on two posts, as
# drawn. The sides and back have windows of the front's kind.

def lodge_planks(x, y, cartoon):
    """The lodge's decks: planks along x in courses four voxels deep (eight in
    Cartoon), a dark joint and a lighter row in each, as drawn."""
    k = (y - 8) % (8 if cartoon else 4)
    if k == 0:
        return "wl_deck_line"
    if k == 1 and not cartoon:
        return "wl_deck_mid"
    return "wl_deck"


def lodge_boards(u, cartoon):
    """The fascias' vertical boards: two voxels light, two dark (four and four in
    Cartoon), as drawn."""
    k = (u - 8) % (8 if cartoon else 4)
    return "wl_fascia" if k < (4 if cartoon else 2) else "wl_fascia_dark"


def lodge_path(x, y, cartoon):
    """The flagged path under the porch: flags of eight (sixteen in Cartoon) with
    dark joints, staggered, as drawn."""
    s = 16 if cartoon else 8
    row = (y - 8) // s
    if (y - 8) % s == 0 or (x - 8 + (s // 2) * (row % 2)) % s == 0:
        return "wl_path_dark"
    return "wl_path" if (x // s + row) % 2 else "wl_path_mid"


def deck(m, cols, z0, z1, bottom, cartoon):
    """A flat roof over [cols] from z0 to z1 (inclusive), hollow: its outer two
    rings a board fascia (a dark line along its foot) under a light rim two voxels
    deep, its top a planked deck two voxels thick; [bottom](x, y) labels its
    underside where it shows (None to leave it out)."""
    depth = ring_depths(cols)
    m.role_now = "roof"
    for (x, y), d in depth.items():
        if d < 2:
            side = (x - 1, y) not in cols or (x + 1, y) not in cols
            if d == 1:
                side = side or (x - 2, y) not in cols or (x + 2, y) not in cols
            for z in range(z0, z1 + 1):
                if z >= z1 - 1:
                    label = "wl_rim"
                elif z == z0:
                    label = "wl_fascia_line"
                else:
                    label = lodge_boards(y if side else x, cartoon)
                m.put(x, y, z, label)
            continue
        for z in (z1 - 1, z1):
            m.put(x, y, z, "wl_rim" if d < 4 else lodge_planks(x, y, cartoon))
        under = bottom(x, y)
        if under:
            m.put(x, y, z0, under)
    m.role_now = "mid"


def wood_lodge(cartoon):
    house = {(i, j) for i in range(5) for j in range(1, 5)}
    porch = {(2, 0)}
    m = Model(5, 5, 6, "PokeG_WoodLodge", house | porch)
    x0, x1, y0, y1 = X(0), X(5), Y(1), Y(5)            # walls on x 8, 88 and y 24, 88
    floor = Z(1)
    foundation(m, house | porch, lambda x, y: (lodge_path if ((x - 8) // 16, (y - 8) // 16) in porch
                                                else planks)(x, y, cartoon))
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front = walls["front"]

    def paint(u, z, lo, hi):
        """A wall's face: the beam along its top; a corner panel and a timber post at
        each end, as drawn; plain panelling between (under and over the windows)."""
        if z >= 60:
            return "wl_timber" if z == 60 else ("wl_fascia" if z == 63 else "wl_beam")
        k = min(u - lo, hi - u)
        if k < 8:
            return "wl_panel_dark" if (z < 22 or z >= 54) and not cartoon else "wl_panel"
        if k < 16:
            if k in (8, 15):
                return "wl_timber"
            return "wl_post_dark" if z < 20 else "wl_post"
        return "wl_panel"

    for key, wall in walls.items():
        u0, u1 = spans[key]
        wall.fill(u0 - 1, u1 + 1, floor, 63, lambda u, z, lo=u0 - 1, hi=u1 + 1: paint(u, z, lo, hi))

    def grid_window(wall, u0):
        """A window of small panes filling the tile from u0: a grey frame, glass in
        levels 2 and 3 over the sill course, grey bars every five voxels across and
        white ones every seven up (fewer in Cartoon), as drawn; a grey sill."""
        for u in range(u0, u0 + 16):
            k = u - u0
            for z in range(31, 60):
                if k in (0, 15) or z == 31:
                    label = "wl_frame"
                elif (k in (5, 10)) if not cartoon else (k in (7, 8)):
                    label = "wl_frame"
                elif ((z - 32) % 7 == 6) if not cartoon else (z in (45, 46)):
                    label = "wl_bar"
                else:
                    wall.erase(u, 0, z)
                    wall.put(u, 1, z, "glass_lodge")
                    continue
                wall.put(u, 0, z, label)
                wall.put(u, 1, z, label)
            wall.put(u, -1, 31, "wl_frame")

    for t in (1, 3):
        grid_window(front, X(t))
    for t in (1, 2, 3):
        grid_window(walls["back"], X(t))
    for key in ("left", "right"):
        for t in (2, 3):
            grid_window(walls[key], Y(t))

    # The door, tile 2 (closed): dark planks in a timber frame, an iron ring.
    m.doors += [("ey", 2, 1, 1), ("ey", 2, 1, 2)]
    d0 = X(2)
    for u in range(d0, d0 + 16):
        k = u - d0
        for z in range(floor, 48):
            if k in (0, 15) or z == 47:
                label = "wl_timber"
            else:
                label = "wl_door_line" if (k % (6 if cartoon else 3) == 0) else "wl_door"
            front.put(u, 0, z, label)
            front.put(u, 1, z, label)
    for z in (30, 31, 32):
        front.put(d0 + 11, -1, z, "wl_beam")

    # The flat roof (level 4, z 64-81), three voxels out all round and over the porch
    # a tile out (x 32-63), as drawn; a ceiling over the room, the porch's underside
    # planked.
    ov = 2
    main = {(x, y) for x in range(x0 - 1 - ov, x1 + ov + 1) for y in range(y0 - 1 - ov, y1 + ov + 1)}
    over_porch = {(x, y) for x in range(X(2) - 8, X(3) + 8) for y in range(6, y0 - 1 - ov)}

    def underside(x, y):
        if (x, y) in over_porch:
            return "wl_deck_line"
        return "ceiling" if x0 <= x < x1 and y0 <= y < y1 else None

    deck(m, main | over_porch, Z(4), Z(5) + 1, underside, cartoon)
    # The raised part on it (z 82-95): x 15-80, y 30-83, its corners cut by five.
    cham = 6 if cartoon else 5
    raised = {(x, y) for x in range(15, 81) for y in range(30, 84)
              if min(x - 15, 80 - x) + min(y - 30, 83 - y) >= cham}
    deck(m, raised, Z(5) + 2, Z(6) - 1, lambda x, y: None, cartoon)

    # The porch's posts at its front corners (decoration to the fight), timber.
    half = 3 if cartoon else 2

    def post_label(x, y, z):
        if z < floor + 3:
            return "wl_post_dark"
        if z >= Z(4) - 3:
            return "wl_post_mid"
        return "wl_timber" if (x in (X(2) - half, X(3) - half) or x in (X(2) + half - 1, X(3) + half - 1)) else "wl_post"

    for cx in (X(2), X(3)):
        post(m, cx, Y(0), floor, Z(4) - 1, post_label, half)

    m.roof_tiles = house | porch
    m.storeys = [{"stand": 1, "tiles": house, "entry": "vault", "cut": 4}]
    m.figure = (2, 0, 1, 200)
    return m


BUILDINGS = {
    "GreenHouse": lambda cartoon: green_house("stepped", cartoon),
    "GreenHouseMirrored": lambda cartoon: mirrored(green_house("stepped", cartoon), "PokeG_GreenHouseMirrored"),
    "GreenWideHouse": lambda cartoon: green_house("wide", cartoon),
    "DomeCenter": dome_center,
    "RedCenter": red_center,
    "Mart": mart,
    "WoodLodge": wood_lodge,
}


def build(kind, cartoon):
    return BUILDINGS[kind](cartoon)
