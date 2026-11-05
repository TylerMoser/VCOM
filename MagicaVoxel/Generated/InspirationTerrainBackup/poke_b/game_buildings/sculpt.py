"""The poke_b buildings' geometry, on VCOM's grid, as the poke_c buildings are
drawn (poke_c/buildings/sculpt.py, whose helpers this copies).

Every model is drawn on the game's tile grid so that it can be cut into the
game's 16-cubed pieces cleanly (a middle, an edge or a corner slot each):

- 16 voxels a tile. Tile boundaries run at x = 8 + 16i and y = 8 + 16j: every
  canvas has half a tile of margin all round the footprint, which holds the
  outer halves of the edge pieces (cornices, sills, canopies, bays, stair cheeks).
- Levels are z = 16k. Level 0 (z 0-15) is a building's own floor, a foundation
  standing in for the map's ground blocks under it. Units stand on the top of a
  cell: a floor at level 0 is stood on at level 1, the mansard houses' raised
  floor (level 1) at level 2.
- A wall is two voxels thick across its tile boundary B (voxels B - 1 and B).
- A door is closed, as drawn, and each leaf fills exactly one doorway slot: one
  tile wide, the two levels a unit fills (the user's choice, 2026-10-28).
- A window keeps within its tile, or spans two whole tiles as two window pieces
  side by side. Its glass is where the rules want it: over a solid sill course a
  level high, so a unit vaults in over the sill and has half cover at it; or,
  in the mansard houses' raised storey and beside the cottage's stair, from the
  floor up through both levels a unit fills, so a unit climbs in from a level
  below (CombatGrid._crossing: both levels must be open), as the user chose.
- Upper floors are real (a slab a level, a room over it), reached only where the
  art draws a way up: the cottage's outside stair (the user's choice). The lab's
  and the mansard houses' upper rooms are closed off.
- A stair climbs a level a tile, as the game climbs. Its treads are cut so that
  each tile's middle, where a unit stands, is exactly at the tile's top, and the
  treads rising above a tile toward the next lie in the edge slot between them.
- MagicaVoxel axes: x across the front, y from the front (low y) to the back, z
  up. The front faces -y (Godot +z), as every building in this workspace.

Voxels carry material labels (palettes.LABELS), not colours, and each its role
for the game's slots (Model.role). Cartoon builds the same building simplified
and regularised on the same grid: its doors, windows, stairs and slots are the
Base's. Each model also says what the rules must see of it (storeys, stairs,
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


# ----------------------------------------------------------------------------
# The domed lab (top left of poke_b.png): seven tiles by four, two storeys of
# three courses under a flat red roof, a parapet with a raised middle, and a
# dome with a glazed band on the roof. The front: fluted pilasters at the corners,
# thin ones either side of the middle bay, a glass door there with a sign over it.

def lab(cartoon):
    m = Model(7, 4, 12, "PokeB_GameDomeLab")
    x0, x1, y0, y1 = X(0), X(7), Y(0), Y(4)            # walls on x 8, 120 and y 8, 72
    floor, TOP = Z(1), 143
    foundation(m, m.footprint, lambda x, y: stone_tiles(x, y, cartoon))
    walls = {"front": Wall(m, "x", y0, -1), "back": Wall(m, "x", y1, +1),
             "left": Wall(m, "y", x0, -1), "right": Wall(m, "y", x1, +1)}
    spans = {"front": (x0, x1 - 1), "back": (x0, x1 - 1), "left": (y0, y1 - 1), "right": (y0, y1 - 1)}

    def paint(u, z):
        if z < 20:
            return "lab_cream_dark"
        if z < 30:
            return "lab_cream"
        if z < 32:
            return "lab_cream_light"
        if z in (64, 79) and not cartoon:
            return "lab_wall_shade"
        if z < 118:
            return "lab_wall"
        if z < 142:
            return "lab_cream"
        return "lab_cream_light"

    for key, wall in walls.items():
        u0, u1 = spans[key]
        wall.fill(u0 - 1, u1 + 1, floor, TOP, paint)
        # The plinth, a voxel proud, its top a lighter ledge.
        for u in range(u0, u1 + 1):
            for z in range(floor, 32):
                wall.put(u, -1, z, "lab_cream_light" if z >= 30 else ("lab_cream" if z >= 20 else "lab_cream_dark"))

    # Windows: two panes, a brown frame and a white one inside it (one brown frame,
    # two voxels wide, in Cartoon), a sill under. Ground floor glass in levels 2-3
    # over the plinth course; upper floor glass in levels 6-7 over level 5.
    def window(wall, c, z0, z1, width=16):
        u0, u1 = c - width // 2, c + width // 2 - 1
        if cartoon:
            wall.pane(u0, u1, z0, z1, "lab_brown", "glass_lab", inner="lab_brown", bars=((c - 1, None), (c, None)),
                      bar_label="lab_white")
        else:
            wall.pane(u0, u1, z0, z1, "lab_brown", "glass_lab", inner="lab_white", bars=((c - 1, None), (c, None)),
                      bar_label="lab_white")
        for u in range(u0 - 1, u1 + 2):
            wall.put(u, -1, z0, "lab_cream_light")
            wall.put(u, 2, z0, "lab_cream_light")

    GROUND, UPPER = (34, 57), (94, 117)
    for key in ("front", "back"):
        for c in (X(1) + 8, X(5) + 8):
            for zz in (GROUND, UPPER):
                window(walls[key], c, *zz)
    window(walls["front"], X(3) + 8, *UPPER)
    window(walls["back"], X(3) + 8, *GROUND)
    window(walls["back"], X(3) + 8, *UPPER)
    for key in ("left", "right"):
        for c in (Y(1) + 8, Y(2) + 8):
            for zz in (GROUND, UPPER):
                window(walls[key], c, *zz, width=14)

    # Thin pilasters either side of the middle bay, front and back, from the plinth
    # to the cornice: cream between brown edge lines (two voxels proud in Cartoon).
    for key in ("front", "back"):
        for c in (X(2) + 8, X(4) + 8):
            for u in range(c - 3, c + 3):
                for z in range(32, 118):
                    edge = u in (c - 3, c + 2)
                    walls[key].put(u, -1, z, "lab_brown" if (edge and not cartoon) else "lab_cream")
                    if cartoon:
                        walls[key].put(u, -2, z, "lab_cream_mid" if edge else "lab_cream")

    # Small square panels in the band between the storeys, under the side windows.
    for key in ("front", "back"):
        for c in (X(1) + 8, X(5) + 8):
            starts = (c - 3,) if cartoon else (c - 6, c + 1)
            size = 7 if cartoon else 5
            for s0 in starts:
                for u in range(s0, s0 + size):
                    for z in range(67, 67 + size):
                        ring = u in (s0, s0 + size - 1) or z in (67, 66 + size)
                        walls[key].put(u, -1, z, "lab_brown" if ring else "lab_cream")

    # The door, tile 3: two glass leaves in a black frame (closed: the user's
    # choice), a glazed transom over it in level 3, handles either side of the meeting stiles.
    front = walls["front"]
    m.doors += [("ey", 3, 0, 1), ("ey", 3, 0, 2)]
    d0, d1 = X(3) + 1, X(4) - 2                       # x 57..70
    for u in range(d0 - 1, d1 + 2):
        for z in range(floor, 32):
            front.erase(u, -1, z)
    for u in range(d0, d1 + 1):
        for z in range(floor, 62):
            frame = u in (d0, d1) or z in (46, 47, 60, 61) or (z < floor + 4 and not cartoon) or u in (63, 64)
            if z >= 48 and u in (63, 64):
                frame = False
            if frame:
                front.put(u, 0, z, "lab_black")
                front.put(u, 1, z, "lab_black")
            else:
                front.erase(u, 0, z)
                front.put(u, 1, z, "glass_lab")
    for z in range(floor + 12, floor + 17):
        for u in (61, 66):
            front.put(u, 0, z, "lab_frame")

    # The sign over the door, between the thin pilasters: a white panel in a black
    # frame, two voxels proud, and on it the emblem, a blue leaf-like stroke rising
    # to the right with a light core and a dark rim (an interpretation of the art's).
    for u in range(X(2) + 11, X(4) + 13):              # x 51..76
        for z in range(66, 95):
            border = u in (X(2) + 11, X(4) + 12) or z in (66, 94)
            for w in (-2, -1):
                front.put(u, w, z, "lab_black" if border else "lab_white")
    ax, az, bx, bz = 56.0, 70.0, 72.0, 90.0
    length = math.hypot(bx - ax, bz - az)
    for u in range(52, 76):
        for z in range(67, 94):
            t = ((u - ax) * (bx - ax) + (z - az) * (bz - az)) / length ** 2
            if not 0 <= t <= 1:
                continue
            px, pz = ax + t * (bx - ax), az + t * (bz - az)
            dist = math.hypot(u - px, z - pz)
            width = (4.5 if cartoon else 3.6) * math.sin(math.pi * min(1.0, t * 1.15)) + 0.6
            if dist <= width:
                core = dist < 0.9 and 0.15 < t < 0.9 and not cartoon
                front.put(u, -3, z, "lab_emblem_light" if core else "lab_emblem")
            elif dist <= width + 1 and not cartoon:
                front.put(u, -3, z, "lab_black")

    # Fluted corner pilasters, wrapping both faces, two voxels proud (three in Cartoon).
    FLUTE = ["lab_cream_mid", "lab_cream_mid", "lab_cream_dark", "lab_cream", "lab_cream", "lab_brown", "lab_cream",
             "lab_cream_light", "lab_cream_light", "lab_cream", "lab_brown", "lab_cream", "lab_cream", "lab_cream_mid",
             "lab_cream_mid", "lab_cream_dark"]
    FLUTE_C = ["lab_cream_mid"] * 2 + ["lab_cream"] * 5 + ["lab_brown"] + ["lab_cream"] * 6 + ["lab_cream_mid"] * 2
    flute = FLUTE_C if cartoon else FLUTE
    proud = (-3, -2, -1) if cartoon else (-2, -1)
    for key, wall in walls.items():
        u0, u1 = spans[key]
        for start, step in ((u0 - 3, 1), (u1 + 3, -1)):
            for t in range(16):
                u = start + step * t
                for z in range(floor, 118):
                    label = flute[t] if z >= 32 else ("lab_cream_dark" if z < 20 else "lab_cream")
                    for w in proud:
                        wall.put(u, w, z, label)

    # The cornice: a shadow line, dentils (a fascia in Cartoon), a band; then the
    # parapet, four voxels thick, its cap a voxel proud each side; over the middle
    # bay a raised part, as drawn.
    for key, wall in walls.items():
        u0, u1 = spans[key]
        for u in range(u0 - 4, u1 + 5):
            for z in (118, 119):
                wall.put(u, -1, z, "lab_cream_dark")
                if cartoon:
                    wall.put(u, -2, z, "lab_cream_dark")
            for z in range(120, 128):
                if cartoon:
                    lab_ = "lab_cream_mid" if z < 124 else "lab_cream"
                    layers = (-2, -1) if z < 124 else (-3, -2, -1)
                else:
                    dent = (u - u0) % 8 < 5
                    lab_ = "lab_cream_light" if dent else "lab_cream_mid"
                    layers = (-3, -2, -1) if dent else (-2, -1)
                for w in layers:
                    wall.put(u, w, z, lab_)
            for z in range(128, 132):
                for w in (-3, -2, -1):
                    wall.put(u, w, z, "lab_cream_light" if z == 131 else "lab_cream")
        # The parapet, four voxels thick (w -1 to 2), its cap five; its ends meet the
        # other walls' at the corner without standing past them.
        for u in range(u0 - 3, u1 + 4):
            for z in range(132, 144):
                cap = z >= 142
                if not cap and u in (u0 - 3, u1 + 3):
                    continue
                for w in ((-2, -1, 0, 1, 2) if cap else (-1, 0, 1, 2)):
                    wall.put(u, w, z, "lab_cream_light" if cap else "lab_cream")
    for u in range(X(2) - 3, X(5) + 3):                # x 37..90
        if cartoon:
            h = 8 if X(2) + 6 <= u <= X(5) - 7 else 0
        else:
            h = max(0, round(6 - abs(u - 63.5) / 4.5))
        for z in range(144, 144 + h):
            for w in (-2, -1, 0, 1, 2):
                front.put(u, w, z, "lab_cream_light" if z == 143 + h else "lab_cream")

    # The upper floor (level 4), and the roof slab (level 8): red membrane in
    # stripes along y (every eight in Cartoon), under the parapet.
    slab(m, m.footprint, 76, 79, lambda x, y: stone_tiles(x, y, cartoon))
    stripe = 8 if cartoon else 4

    def roof_paint(x, y, z, b, t):
        if z == b:
            return "ceiling"
        if z < t - 1:
            return "lab_wall_shade"
        return "lab_roof_dark" if (y - 8) % stripe == 0 else "lab_roof"

    cols = [(x, y) for x in range(x0 + 1, x1 - 1) for y in range(y0 + 1, y1 - 1)]
    fill_roof(m, cols, lambda x, y: 128, lambda x, y: 135, roof_paint)

    # The dome, centred on the roof: a ring of red at its foot, a glazed band (a
    # cylinder of glass and white mullions, then the dome's lower part), a cream cap.
    cx, cy, R = 63.5, 39.5, 29.5
    Rv = 35.0 if cartoon else 33.0                    # its height over the drum: a little taller than round
    zc = 143.5
    mull_step = 45.0 if cartoon else 22.5
    m.role_now = "roof"
    for x in range(int(cx - R) - 1, int(cx + R) + 2):
        for y in range(int(cy - R) - 1, int(cy + R) + 2):
            r = math.hypot(x - cx, y - cy)
            ang = math.degrees(math.atan2(y - cy, x - cx)) % mull_step
            mullion = ang < 3.0 or ang > mull_step - 3.0
            for z in range(136, int(zc + Rv) + 2):
                if z <= 143:
                    rr = r
                else:
                    rr = math.sqrt(r * r + ((z - zc) * R / Rv) ** 2)
                if rr > R:
                    continue
                band_top = 153 if cartoon else 155
                glass_zone = 138 + (2 if cartoon else 0) <= z <= band_top
                if glass_zone and not mullion and z not in (band_top - 1, band_top):
                    if rr > R - 1.6:
                        m.put(x, y, z, "glass_lab")
                    continue
                if rr <= R - 3:
                    continue
                if z <= 137 + (2 if cartoon else 0):
                    label = "lab_ring"
                elif glass_zone:
                    label = "lab_white"
                elif z <= band_top + 2 and not cartoon:
                    label = "lab_dome_shade"
                else:
                    label = "lab_dome"
                m.put(x, y, z, label)
    if cartoon:
        for x in range(60, 68):
            for y in range(36, 44):
                for z in range(176, 184):
                    if math.sqrt((x - cx) ** 2 + (y - cy) ** 2 + (z - 180) ** 2) <= 3.1:
                        m.put(x, y, z, "lab_ring")
    m.role_now = "mid"

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 4},
                 {"stand": 5, "tiles": set(m.footprint), "entry": None, "cut": 8}]
    m.figure = (2, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The red clinic (top middle of poke_b.png): six tiles by four, one storey of four
# courses, a white parapet round a low red roof with a skylight on its right, dark
# corner pillars; the front: a red portico over the window, the glass door and the
# sign, a red-and-white roundel on it, a tank, and a dark teal window across two tiles.

def clinic(cartoon):
    m = Model(6, 4, 7, "PokeB_GameRedClinic")
    x0, x1, y0, y1 = X(0), X(6), Y(0), Y(4)            # walls on x 8, 104 and y 8, 72
    floor = Z(1)
    foundation(m, m.footprint, lambda x, y: stone_tiles(x, y, cartoon))
    walls = {"front": Wall(m, "x", y0, -1), "back": Wall(m, "x", y1, +1),
             "left": Wall(m, "y", x0, -1), "right": Wall(m, "y", x1, +1)}
    spans = {"front": (x0, x1 - 1), "back": (x0, x1 - 1), "left": (y0, y1 - 1), "right": (y0, y1 - 1)}

    def paint(u, z):
        if z < 18:
            return "cl_wall_dark"
        if z < 22 and not cartoon:
            return "cl_wall_mid"
        if z < 76:
            return "cl_wall"
        return "cl_wall_mid" if z < 78 else "cl_green_dark"

    for key, wall in walls.items():
        u0, u1 = spans[key]
        wall.fill(u0 - 1, u1 + 1, floor, Z(5) - 1, paint)

    def window(wall, c, width=12):
        u0, u1 = c - width // 2, c + width // 2 - 1
        wall.pane(u0, u1, 33, 46, "cl_trim_dark", "glass_clinic", inner=None if cartoon else "cl_wall_dark")
        for u in range(u0 - 1, u1 + 2):
            wall.put(u, -1, 33, "cl_wall_dark")
            wall.put(u, 2, 33, "cl_wall_dark")

    front = walls["front"]
    window(front, X(1) + 8)
    for key in ("left", "right"):
        for c in (Y(1) + 8, Y(2) + 8):
            window(walls[key], c)
    for c in (X(1) + 8, X(4) + 8):
        window(walls["back"], c)

    # The door, tile 2: two sliding glass leaves in a dark frame, closed.
    m.doors += [("ey", 2, 0, 1), ("ey", 2, 0, 2)]
    d0, d1 = X(2), X(3) - 1                            # x 40..55
    for u in range(d0, d1 + 1):
        for z in range(floor, 48):
            frame = u in (d0, d0 + 1, d1 - 1, d1) or z in (46, 47) or z < floor + 2 or u in (47, 48)
            if frame:
                label = "cl_frame_dark" if (u in (47, 48) or z < floor + 2) else "cl_frame"
                front.put(u, 0, z, label)
                front.put(u, 1, z, label)
            else:
                front.erase(u, 0, z)
                front.put(u, 1, z, "glass_clinic")
    for z in range(floor + 12, floor + 18):
        for u in (45, 50):
            front.put(u, 0, z, "cl_trim")

    # The sign, tile 3: a white panel in a dark frame, a red band and blocks on it
    # (no letters: generic marks, the user's choice).
    for u in range(X(3) + 1, X(4) - 1):                # x 57..70
        for z in range(30, 45):
            border = u in (X(3) + 1, X(4) - 2) or z in (30, 44)
            front.put(u, -1, z, "cl_frame" if border else "cl_white")
    for u in range(59, 69):
        for z in range(39, 42):
            front.put(u, -2 if cartoon else -1, z, "cl_red_shadow")
    for u, z0, z1, lab_ in ((59, 32, 36, "cl_red_dark"), (64, 33, 35, "cl_green_dark")):
        for uu in range(u, u + (4 if lab_ == "cl_red_dark" else 5)):
            for z in range(z0, z1 + 1):
                front.put(uu, -2 if cartoon else -1, z, lab_)

    # The teal window over tiles 4 and 5, as drawn, a solid panel under its glass
    # (the sill course), a small brass plate on the panel.
    t0, t1 = X(4) + 9, X(6) - 7                        # x 81..97
    for u in range(t0, t1 + 1):
        for z in range(18, 62):
            ring = u in (t0, t1) or z in (18, 61) or z == 31
            if ring:
                front.put(u, 0, z, "cl_frame_dark")
                front.put(u, 1, z, "cl_frame_dark")
            elif z < 31:
                front.put(u, 0, z, "cl_wall_dark" if not cartoon else "cl_wall_mid")
                front.put(u, 1, z, "cl_wall_dark")
            else:
                front.erase(u, 0, z)
                front.put(u, 1, z, "glass_teal")
    for u in range(89, 94):
        for z in range(24, 28):
            front.put(u, -1, z, "m_handle")

    # The tank in front of the teal window's left edge: a rounded grey cylinder.
    tx, ty, tr = 79.5, 3.5, (3.2 if cartoon else 2.7)
    for x in range(75, 85):
        for y in range(0, 8):
            r = math.hypot(x - tx, y - ty)
            if r > tr:
                continue
            for z in range(24, 71):
                cap = min(z - 24, 70 - z)
                if cap < 2 and r > tr - (2 - cap) * 1.1:
                    continue
                if z in (30, 64) and not cartoon:
                    label = "cl_frame_dark"
                else:
                    label = "cl_wall_dark" if x > tx + 0.5 else "cl_wall_mid"
                m.put(x, y, z, label, "ey")

    # The portico over tiles 1-3: a red canopy (level 3) standing out to the canvas
    # edge, red cheeks down to a red step, as drawn.
    p0, p1 = X(0) + 9, X(4) + 6                        # x 17..78
    cheek = 5 if cartoon else 4
    for u in range(p0, p1 + 1):
        for w in range(-5, 0):
            for z in range(48, 62):
                if cartoon and w == -5 and z == 61:
                    continue
                if z == 48:
                    label = "cl_red_deep"
                elif z < 50:
                    label = "cl_red_shadow"
                elif z == 61 or (z == 60 and cartoon):
                    label = "cl_red_light" if w == -5 else "cl_red"
                else:
                    label = "cl_red_dark" if w == -5 else "cl_red"
                front.put(u, w, z, label)
            for z in (floor, floor + 1):
                front.put(u, w, z, "cl_red_deep")
            if u < p0 + cheek or u > p1 - cheek:
                for z in range(floor + 2, 48):
                    front.put(u, w, z, "cl_red_shadow" if w == -5 else "cl_red_dark")

    # The roundel over the door, standing on the canopy's front: red above, white
    # below, a grey rim; no band and no button (generic marks, the user's choice).
    rc, zc, R = 47.5, 66.5, (8.4 if cartoon else 7.2)
    for u in range(int(rc - R) - 1, int(rc + R) + 2):
        for z in range(int(zc - R) - 1, int(zc + R) + 2):
            r = math.hypot(u - rc, z - zc)
            if r > R:
                continue
            if r > R - (1.6 if cartoon else 1.2):
                label = "cl_trim_dark"
            else:
                label = "cl_red" if z >= zc else "cl_white"
            for w in (-7, -6):
                front.put(u, w, z, label)

    # Dark corner pillars, two voxels proud (three in Cartoon), wrapping both faces.
    PILLAR = ["cl_pillar_dark", "cl_pillar_dark", "cl_pillar", "cl_pillar", "cl_pillar", "cl_pillar_mid",
              "cl_pillar", "cl_pillar_dark", "cl_pillar_dark", "cl_pillar_dark"]
    proud = (-3, -2, -1) if cartoon else (-2, -1)
    for key, wall in walls.items():
        u0, u1 = spans[key]
        for start, step in ((u0 - 3, 1), (u1 + 3, -1)):
            for t in range(10):
                u = start + step * t
                for z in range(floor, Z(5)):
                    for w in proud:
                        wall.put(u, w, z, "cl_pillar" if cartoon and 1 < t < 8 else PILLAR[t])

    # The parapet (level 5), all round: a light face, a white top.
    pw = (-3, -2, -1, 0, 1, 2) if cartoon else (-2, -1, 0, 1, 2)
    for key, wall in walls.items():
        u0, u1 = spans[key]
        for u in range(u0 - 3, u1 + 4):
            for z in range(80, 92):
                for w in pw:
                    label = "cl_white" if z >= 90 else ("cl_wall_mid" if z < 82 else "cl_wall")
                    wall.put(u, w, z, label)

    # The roof: low, rising four voxels from the parapet to a flat top, red tiles in
    # courses four voxels apart (eight in Cartoon), staggered joints, the lowest
    # course darker as drawn.
    ix0, ix1, iy0, iy1 = x0 + 2, x1 - 3, y0 + 2, y1 - 3        # inside the parapet: x 10..101, y 10..69
    course = 8 if cartoon else 4

    def depth(x, y):
        return min(x - ix0, ix1 - x, y - iy0, iy1 - y)

    def top(x, y):
        return 84 + min(depth(x, y), 8) // 2

    def roof_paint(x, y, z, b, t):
        if z == b:
            return "ceiling"
        if z < t:
            return "cl_red_deep"
        d = depth(x, y)
        if d < 2:
            return "cl_red_shadow"
        side = min(x - ix0, ix1 - x) < min(y - iy0, iy1 - y) and d < 8
        a, s = (y, x) if side else (x, y)
        if s % course == 0:
            return "cl_red_dark"
        row = s // course
        if (a + (course // 2) * (row % 2)) % (2 * course) == 0:
            return "cl_red_deep"
        if cartoon:
            return "cl_red"
        h = ((a % 16) * 7 + (row % 4) * 13) % 11
        return "cl_red_light" if h == 0 else ("cl_red_mid" if h in (3, 7) else "cl_red")

    cols = [(x, y) for x in range(ix0, ix1 + 1) for y in range(iy0, iy1 + 1)]
    fill_roof(m, cols, lambda x, y: 80, top, roof_paint)

    # The skylight on the roof's right, as drawn: a raised light frame and glass,
    # the roof open under it, so the room shows through.
    sx0, sx1, sy0, sy1 = 63, 90, 27, 58
    fw = 3 if cartoon else 2
    m.role_now = "roof"
    for x in range(sx0, sx1 + 1):
        for y in range(sy0, sy1 + 1):
            frame = x < sx0 + fw or x > sx1 - fw or y < sy0 + fw or y > sy1 - fw
            bar = cartoon and (x in (76, 77) or y in (42, 43))
            if frame or bar:
                for z in range(88, 92):
                    m.put(x, y, z, "cl_trim" if z == 91 else "cl_trim_dark")
            else:
                for z in range(80, 90):
                    m.erase(x, y, z)
                m.put(x, y, 90, "glass_sky")
    m.role_now = "mid"

    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 5}]
    m.figure = (1, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The mansard houses (middle and bottom left of poke_b.png): five tiles by three
# on a stone base a level high, a storey of boards (levels 2-3), a stone cornice,
# a mansard storey (levels 5-6) of steep slate slopes with two dormers each way, a
# low hipped top with a chimney. A (gray) and C (cyan, the same house recoloured):
# a door up a front stair in tile 2, a window in tile 1, a shallow bay over tiles
# 3-4. B: three windows across, no door on its front, as drawn.

SCHEMES = {
    "A": {"board": "a_board", "board_light": "a_board_light", "board_shade": "a_board_shade",
          "board_line": "a_board_line", "roof": "m_roof", "roof_mid": "m_roof_mid", "roof_shade": "m_roof_shade",
          "roof_dark": "m_roof_dark", "roof_black": "m_roof_black", "roof_line": "m_roof_line",
          "door": "m_door", "door_dark": "m_door_dark", "door_light": "m_door_light"},
    "B": {"board": "b_board", "board_light": "b_board_light", "board_shade": "b_board_dark",
          "board_line": "b_board_line", "roof": "m_roof", "roof_mid": "m_roof_mid", "roof_shade": "m_roof_shade",
          "roof_dark": "m_roof_dark", "roof_black": "m_roof_black", "roof_line": "m_roof_line"},
    "C": {"board": "cy_board", "board_light": "b_board_light", "board_shade": "b_board",
          "board_line": "b_board_line", "roof": "cy_roof", "roof_mid": "cy_roof_mid", "roof_shade": "cy_roof_shade",
          "roof_dark": "cy_roof_dark", "roof_black": "cy_roof_black", "roof_line": "m_stone_deep",
          "door": "cy_door", "door_dark": "cy_door_dark", "door_light": "cy_door_light"},
}
MANSARD_NAMES = {"A": "PokeB_GameGrayEntryHouse", "B": "PokeB_GameGrayWindowHouse", "C": "PokeB_GameCyanEntryHouse"}


def base_course(u, z):
    """The stone base's face, as drawn: bands of blue-grey stone, a joint every nine
    voxels in the middle band."""
    if z < 18:
        return "m_stone_deep"
    if z < 20:
        return "m_stone_dark"
    if z < 24:
        return "m_stone_dark" if (u - 8) % 8 == 0 else "m_stone"
    if z < 26:
        return "m_stone_dark"
    if z < 28:
        return "m_stone_light"
    return "m_stone_mid"


def cornice_course(u, z, cartoon):
    """The cornice's face (z 64-77), as drawn: a shadow under it, bands of stone with
    joints in two of them; plain bands in Cartoon."""
    if z < 68:
        return "m_stone_deep"
    if z < 70:
        return "m_stone_dark"
    if z < 72:
        return "m_stone_dark" if ((u - 8) % 8 == 0 and not cartoon) else "m_stone"
    if z < 74:
        return "m_stone_dark"
    if z < 76:
        return "m_stone_mid" if ((u - 4) % 8 == 0 and not cartoon) else "m_stone_light"
    return "m_stone_mid"


def mansard(variant, cartoon):
    S = SCHEMES[variant]
    entry = variant in ("A", "C")
    j0 = 1 if entry else 0
    house = {(i, j) for i in range(5) for j in range(j0, j0 + 3)}
    foot = house | ({(2, 0)} if entry else set())
    m = Model(5, j0 + 3, 8, MANSARD_NAMES[variant], foot)
    m.roof_tiles = set(house)
    x0, x1, y0, y1 = X(0), X(5), Y(j0), Y(j0 + 3)
    foundation(m, foot, None)
    walls = {"front": Wall(m, "x", y0, -1), "back": Wall(m, "x", y1, +1),
             "left": Wall(m, "y", x0, -1), "right": Wall(m, "y", x1, +1)}
    spans = {"front": (x0, x1 - 1), "back": (x0, x1 - 1), "left": (y0, y1 - 1), "right": (y0, y1 - 1)}
    def boards(u, z):
        # Three boards to the tile (5, 5 and 6 voxels: the art's are six), two in Cartoon.
        line = (u - 8) % 8 == 0 if cartoon else (u - 8) % 16 in (0, 5, 10)
        if z >= 62:
            return S["board_shade"]
        if z < 40 and not cartoon:
            return S["board_shade"] if line else S["board_light"]
        return S["board_line"] if line else S["board"]

    def paint(u, z):
        if z < 30:
            return base_course(u, z)
        if z < 32:
            return "m_light"
        if z < 64:
            return boards(u, z)
        return cornice_course(u, z, cartoon) if z < 78 else "m_light"

    for key, wall in walls.items():
        u0, u1 = spans[key]
        wall.fill(u0 - 1, u1 + 1, Z(1), Z(5) - 1, paint)

    # The base stands two voxels proud, its top a light ledge; the cornice three
    # (four in Cartoon), its top light, a shadow line under it.
    cw = (-4, -3, -2, -1) if cartoon else (-3, -2, -1)

    def base_and_cornice(wall, u0, u1):
        for u in range(u0 - 3, u1 + 4):
            for z in range(Z(1), 32):
                for w in (-2, -1):
                    wall.put(u, w, z, base_course(u, z) if z < 30 else "m_light")
        for u in range(u0 - 1 - len(cw), u1 + 2 + len(cw)):
            for z in range(64, 68):
                wall.put(u, -1, z, "m_stone_deep")
            for z in range(68, 80):
                for w in cw:
                    wall.put(u, w, z, cornice_course(u, z, cartoon) if z < 78 else "m_light")

    for key, wall in walls.items():
        base_and_cornice(wall, *spans[key])

    # Light pilasters at the corners of the boarded storey, a voxel proud.
    for key, wall in walls.items():
        u0, u1 = spans[key]
        for start, step in ((u0 - 1, 1), (u1 + 1, -1)):
            for t in range(4 if cartoon else 3):
                for z in range(32, 64):
                    wall.put(start + step * t, -1, z, "m_light" if t == 1 else "m_pale")

    def window(wall, c, width, w=0, cross=True):
        """A tall window from the floor up through both levels a unit fills (z 33-62):
        a white frame and a pale one in it (pale, two wide, for A's narrow one), glass,
        a white bar across, a white sill."""
        u0, u1 = c - width // 2, c - width // 2 + width - 1
        if width <= 10:
            wall.pane(u0, u1, 33, 62, "m_pale", "glass_house", inner="m_pale",
                      bars=((None, 47), (None, 48)) if cross else (), bar_label="m_white", w=w)
        else:
            wall.pane(u0, u1, 33, 62, "m_white", "glass_house", inner=None if cartoon else "m_pale",
                      bars=((None, 47), (None, 48)) if cross else (), bar_label="m_pale", w=w)
        for u in range(u0 - 1, u1 + 2):
            wall.put(u, w - 1, 33, "m_white")

    def shutter(wall, u0, w=-1):
        """A louvred shutter six voxels wide beside a window, a voxel proud."""
        for u in range(u0, u0 + 6):
            for z in range(34, 62):
                edge = u in (u0, u0 + 5) or z in (34, 61)
                if edge:
                    label = "sh_edge"
                elif cartoon:
                    label = "sh_dark" if (z - 34) % 9 == 0 else "sh"
                else:
                    label = ("sh_light", "sh_mid", "sh", "sh_dark")[((z - 35) // 2) % 4]
                wall.put(u, w, z, label)

    front = walls["front"]
    if entry:
        # Tile 1: a narrow window, a shutter on its left, as drawn.
        window(front, X(1) + 8, 10)
        shutter(front, X(1) - 4)
        # Tile 2: the door (levels 2 and 3, closed), up the stair.
        m.doors += [("ey", 2, j0, 2), ("ey", 2, j0, 3)]
        d0, d1 = X(2), X(3) - 1                        # x 40..55
        for u in range(d0, d1 + 1):
            for z in range(32, 60):
                if u in (d0, d1) or z in (58, 59):
                    label = "m_black"
                elif not cartoon and 44 <= u <= 51 and 46 <= z <= 55:
                    label = S["door_dark"]
                elif z < 44:
                    label = S["door_light"]
                else:
                    label = S["door"]
                front.put(u, 0, z, label)
                front.put(u, 1, z, label)
            for z in range(32, 60):
                front.erase(u, -1, z)
        for z in (42, 43):
            for u in (43, 44):
                front.put(u, -1, z, "m_handle")
        # Tiles 3-4: the bay, standing six voxels out, its front a wall with the base
        # and cornice on it, flush, a window over the boundary between its tiles, a
        # shutter either side, a flat light top; the house's wall open behind it.
        bay_y = y0 - 7                                  # its outer face, y 17
        bf = Wall(m, "x", bay_y + 1, -1)
        bu0, bu1 = X(3), X(5) - 1                       # x 56..87
        m.clear(bu0, bu1, bay_y - 1, y0 - 2, Z(1), Z(5) - 1)
        for u in range(bu0, bu1 + 1):
            for z in range(Z(1), Z(5)):
                bf.put(u, 0, z, paint(u, z))
                bf.put(u, 1, z, paint(u, z))
            for z in range(Z(1), 32):
                bf.put(u, -1, z, base_course(u, z) if z < 30 else "m_light")
            for z in range(68, 80):
                bf.put(u, -1, z, cornice_course(u, z, cartoon) if z < 78 else "m_light")
        for side_u in (bu0, bu0 + 1, bu1 - 1, bu1):
            for y in range(bay_y, y0):
                for z in range(Z(1), Z(5)):
                    m.put(side_u, y, z, paint(side_u, z), "ey")
        for x in range(bu0 + 2, bu1 - 1):
            for y in range(bay_y + 2, y0):
                for z in range(Z(1), 32):
                    m.put(x, y, z, "found" if z < 30 else planks(x, y, cartoon), "ey")
        for x in range(bu0, bu1 + 1):
            for y in range(bay_y - 1, y0 + 2):
                for z in (78, 79):
                    m.put(x, y, z, "m_light", "ey")
                for z in range(72, 78):
                    if y >= bay_y + 2:
                        m.put(x, y, z, "ceiling", "ey")
        front.cut(bu0 + 2, bu1 - 2, 32, 71)
        window(bf, X(4), 12)
        shutter(bf, X(4) - 12)
        shutter(bf, X(4) + 6)
        # The house-number plate, on the bay's side by the door (an interpretation:
        # drawn on the front just right of the door, where the bay is).
        for y in range(bay_y + 1, bay_y + 6):
            for z in range(50, 56):
                ring = y in (bay_y + 1, bay_y + 5) or z in (50, 55)
                m.put(bu0 - 1, y, z, "m_stone_dark" if ring else "m_stone_light", "ey")
        if not cartoon:
            for z in range(51, 55):
                m.put(bu0 - 2, bay_y + 3, z, "m_light", "ey")
        # The stair, tile 2, a level up to the door: light treads between cheeks
        # that run into the bay's side.
        step = 8 if cartoon else 4
        stair(m, 2, 0, 1, X(2) + 3, X(3) - 4, step, lambda r, top: ("m_tread", "m_riser", "m_riser_dark"))
        for (ca, cb) in ((X(2) - 3, X(2) + 2), (X(3) - 3, X(3) + 2)):
            for x in range(ca, cb + 1):
                for y in range(0, y0):
                    if x > X(3) - 1 and y >= bay_y:
                        continue
                    for z in range(Z(1), 32):
                        if z >= 30:
                            label = "m_cheek"
                        elif z >= 28:
                            label = "m_cheek_mid" if not cartoon else "m_cheek"
                        else:
                            label = base_course(y, z)
                        m.put(x, y, z, label, "ex")
    else:
        # B: three windows across, louvred shutters at the ends, as drawn.
        for c in (X(1) + 8, X(2) + 8, X(3) + 8):
            window(front, c, 13)
        shutter(front, X(1) - 7)
        shutter(front, X(4) + 2)
    # Sides and back are unseen in the art: windows of the front's kind, one in each
    # side's middle, at the back two (A, C) or three (B), so every side has one to enter by.
    for key in ("left", "right"):
        window(walls[key], Y(j0 + 1) + 8, 13)
    for c in ((X(1) + 8, X(3) + 8) if entry else (X(1) + 8, X(2) + 8, X(3) + 8)):
        window(walls["back"], c, 13)

    # Floors: the raised floor (level 1) and the mansard storey's (level 4).
    for (i, j) in house:
        for x in range(X(i), X(i + 1)):
            for y in range(Y(j), Y(j + 1)):
                for z in range(Z(1), 32):
                    if (x, y, z) not in m.v:
                        m.put(x, y, z, "found" if z < 30 else planks(x, y, cartoon), "mid")
    slab(m, house, 76, 79, lambda x, y: planks(x, y, cartoon))

    # The mansard storey (levels 5-6): its steep slopes lean in five voxels from the
    # cornice to the break, three voxels thick, slates in courses; dormers.
    yF, yB = y0 - 1, y1                                 # the walls' outer faces (y)
    xL, xR = x0 - 1, x1
    lean_top = 5
    course = 8 if cartoon else 4
    joint = 16 if cartoon else 8

    def lean(z):
        return round((z - 80) * lean_top / 31)

    def slate(u, z, edge):
        if edge:
            return S["roof_black"] if not cartoon else S["roof_dark"]
        c = (z - 80) // course
        if (z - 80) % course == course - 1:
            return S["roof_dark"]
        if (u + (joint // 2) * (c % 2)) % joint == 0:
            return S["roof_dark"]
        return S["roof_mid"] if c % 2 else S["roof_shade"]

    for z in range(80, 112):
        L = lean(z)
        ax0, ax1, ay0, ay1 = xL + L, xR - L, yF + L, yB - L
        for x in range(ax0, ax1 + 1):
            for y in range(ay0, ay1 + 1):
                df, db = y - ay0, ay1 - y
                dl, dr = x - ax0, ax1 - x
                near_y = min(df, db) < 3
                near_x = min(dl, dr) < 3
                if not (near_y or near_x):
                    continue
                if near_y and near_x:
                    role = "corner"
                    edge = True
                elif near_y:
                    role = "ey"
                    edge = min(dl, dr) < 5
                else:
                    role = "ex"
                    edge = min(df, db) < 5
                u = x if near_y else y
                m.put(x, y, z, slate(u, z, edge), role)

    def dormer(face, u0):
        """A dormer in tile [u0 .. u0 + 15] of a slope: grey cheeks, a white face with
        two narrow windows (glass in level 6, over a sill panel in level 5), a light flat
        top meeting the slope, a stone fascia under it."""
        out = -1 if face == "front" else 1
        y_out = yF if face == "front" else yB
        u1 = u0 + 15

        def at(u, d, z):                                # d: voxels in from the wall's face
            return (u, y_out - out * d, z)
        # Clear the slope where the dormer stands.
        for u in range(u0, u1 + 1):
            for d in range(0, 9):
                for z in range(80, 112):
                    m.erase(*at(u, d, z))
        for u in range(u0, u1 + 1):
            for z in range(80, 108):
                cheek = u in (u0, u1)
                if cheek:
                    label = "m_cheek_grey"
                elif z < 84:
                    label = "m_stone_light"
                elif z < 94:
                    label = "m_white"
                elif z in (94, 95, 105):
                    label = "m_pale"
                elif z >= 106:
                    label = "m_stone_light"
                else:
                    k = u - u0
                    pane = k in (4, 5, 6, 9, 10, 11) and 96 < z < 104
                    frame = k in (3, 7, 8, 12) or z in (96, 104)
                    if pane:
                        m.erase(*at(u, 0, z))
                        m.put(*at(u, 1, z), "glass_house", "ey")
                        continue
                    label = "m_dormer_frame" if (frame and 3 <= k <= 12) else "m_pale"
                m.put(*at(u, 0, z), label, "ey")
                m.put(*at(u, 1, z), label, "ey")
            for d in range(2, 9):
                for z in range(80, 108):
                    if u in (u0, u1):
                        m.put(*at(u, d, z), "m_cheek_grey", "ey")
        for u in range(u0 - 1, u1 + 2):
            for d in range(-1, 9):
                for z in range(108, 112):
                    m.put(*at(u, d, z), "m_light" if z >= 110 else "m_stone_light", "ey")
            m.put(*at(u, -1, 94), "m_pale", "ey")
        if cartoon:
            # A rounded top: the dormer's roof crowned along its middle.
            for u in range(u0 + 2, u1 - 1):
                for d in range(-1, 9):
                    m.put(*at(u, d, 112), "m_light", "ey")

    for face in ("front", "back"):
        for i in (1, 3):
            dormer(face, X(i))

    # The top (level 7): a light coping at the break, a stone line inside it, a low
    # hip rising to the flat top, its courses darker toward the edge, as drawn.
    L = lean_top
    cx0, cx1, cy0, cy1 = xL + L, xR - L, yF + L, yB - L
    cop = 4 if cartoon else 3
    m.role_now = "roof"
    for x in range(cx0, cx1 + 1):
        for y in range(cy0, cy1 + 1):
            d = min(x - cx0, cx1 - x, y - cy0, cy1 - y)
            if d < cop:
                for z in (112, 113):
                    m.put(x, y, z, "m_light")
                continue
            if d < cop + 2 and not cartoon:
                for z in (112, 113):
                    m.put(x, y, z, "m_stone_light")
                continue
            e = d - cop - (0 if cartoon else 2)
            h = 112 + min(e, 8) // 2 + (min(e, 4) // 2 if cartoon else 0)
            for z in range(112, h + 1):
                if z < h:
                    m.put(x, y, z, "ceiling" if z == 112 else S["roof_dark"])
                    continue
                if e == 0:
                    label = S["roof_line"]
                elif e < 3:
                    label = S["roof_dark"]
                elif e < 5:
                    label = S["roof_shade"]
                elif e < 7:
                    label = S["roof_mid"]
                else:
                    label = S["roof"]
                m.put(x, y, z, label)
    m.role_now = "mid"

    # The chimney, on the top's left toward the back, as drawn: light cap, dark flue.
    hx0, hx1 = X(0) + 9, X(1) + 2                       # x 17..26
    hy0 = yF + 25
    hy1 = hy0 + 8
    for x in range(hx0, hx1 + 1):
        for y in range(hy0, hy1 + 1):
            ground = max(z for z in range(112, 128) if (x, y, z) in m.v)
            for z in range(ground + 1, 128):
                if z >= 126:
                    label = "m_flue_top"
                elif x == hx1 or y == hy0:
                    label = "m_flue_shade" if x == hx1 else "m_flue_side"
                else:
                    label = "m_flue_side"
                m.put(x, y, z, label, "mid")
    for x in range(hx0 + 3, hx1 - 2):
        for y in range(hy0 + 3, hy1 - 2):
            for z in range(122, 128):
                m.put(x, y, z, "m_flue" if z < 127 else "m_roof_line", "mid")
            m.erase(x, y, 127)

    m.storeys = [{"stand": 2, "tiles": set(house), "entry": "climb", "cut": 4},
                 {"stand": 5, "tiles": set(house), "entry": None, "cut": 7}]
    if entry:
        m.stairs = {(2, 0): 2}
        m.figure = (2, 0, 2, 200)
    else:
        m.figure = (0, -1, 1, 200)
    return m


# ----------------------------------------------------------------------------
# The flower cottage (bottom right of poke_b.png): five tiles by three, two storeys
# of two courses, cream walls, a bell-cast roof with its ridge front to back and
# two roof lights on its left slope, a small window high in the front gable; the
# front: the door with a sidelight under a hood (tile 1), a box bay window under a
# hood (tile 3), two-pane windows over flower boxes upstairs. On its right, the
# outside stair, a level a tile over three tiles to a landing at the upper door.

def bell(d, rise):
    """The roof's underside over a wall top, [d] voxels in from the wall line, for
    a roof rising [rise] to its ridge 40 in: flat at the eave and the ridge,
    steepest between, as drawn; a little drooping past the wall."""
    if d < 0:
        return d // 2
    return round(rise * (1 - math.cos(math.pi * min(d, 40) / 40)) / 2)


def cottage(cartoon):
    house = {(i, j) for i in range(5) for j in range(3)}
    stair_tiles = {(5, j) for j in range(3)}
    m = Model(6, 3, 8, "PokeB_GameFlowerCottage", house | stair_tiles)
    m.roof_tiles = set(house)
    x0, x1, y0, y1 = X(0), X(5), Y(0), Y(3)            # walls on x 8, 88 and y 8, 56
    floor = Z(1)
    foundation(m, house | stair_tiles, lambda x, y: planks(x, y, cartoon))
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
    # plate and knob, a glazed sidelight beside it; the hood over it.
    m.doors += [("ey", 1, 0, 1), ("ey", 1, 0, 2)]
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

    def hood(u0, u1, depth, z_wall):
        """A pent roof standing [depth] out from the wall, sloping from [z_wall] at
        the wall down to its front edge, shingled, a dark edge, timber under it."""
        for u in range(u0, u1 + 1):
            for w in range(-depth, 0):
                zt = z_wall - round((-w) * 1.4)
                for z in range(zt - 2, zt + 1):
                    if z == zt - 2:
                        label = "co_timber"
                    elif w == -depth or u in (u0, u1):
                        label = "co_roof_black" if z < zt else "co_roof_edge"
                    else:
                        row = (-w) // (3 if cartoon else 2)
                        joint = (u + 3 * (row % 2)) % (8 if cartoon else 5) == 0
                        label = "co_roof_dark" if joint else ("co_roof" if row % 2 else "co_roof_hi")
                    front.put(u, w, z, label)

    hood(d0 - 1, d0 + 20, 6, 57)

    # The bay, tile 3 and the posts either side: a box standing out four voxels, a
    # red-brown base, a cream panel (the sill course), a white-framed window in level 2,
    # dark posts at its corners; the house's wall open behind its window; the hood over it.
    b0, b1 = X(3) - 6, X(4) + 4                         # x 50..76
    bay = Wall(m, "x", y0 - 4, -1)                      # its front's outer face y 3
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
    hood(b0, b1, 6, 58)

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
    # storeys; on the right only the upper door (tile 2, closed) at the landing and, so
    # the upper floor can be entered from the stair, a tall window in tile 1 reaching
    # down to its floor (levels 4 and 5), which one climbs in by from the stair.
    window(left, Y(1) + 8, 32, 46)
    window(left, Y(1) + 8, 79, 94)
    for c in (X(1) + 8, X(3) + 8):
        window(back, c, 32, 46)
        window(back, c, 79, 94)
    window(right, Y(1) + 8, 65, 94, width=12)
    m.doors += [("ex", 5, 2, 4), ("ex", 5, 2, 5)]
    for u in range(Y(2), Y(3)):
        for z in range(64, 92):
            if u in (Y(2), Y(3) - 1) or z in (90, 91):
                label = "co_timber"
            elif (u - Y(2)) in (1, 14) or z in (64, 65):
                label = "co_door_dark"
            elif not cartoon and (u - Y(2)) in (2, 13):
                label = "co_door_mid"
            else:
                label = "co_door"
            right.put(u, 0, z, label)
            right.put(u, 1, z, label)
    right.put(Y(2) + 3, -1, 78, "co_brass")
    right.put(Y(2) + 3, -1, 79, "co_brass")

    # Corner posts, dark timber, a voxel proud.
    half = 3 if cartoon else 2
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
    yv0, yv1 = y0 - 1 - ov, y1 + ov                     # the verges, y 3..60
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
    for (ya, yb) in ((Y(0) + 8, Y(1) + 3), (Y(2) - 2, Y(2) + 9)):
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

    # The outside stair, tiles (5, 0-2): treads a level a tile, to a grey landing at
    # the upper door; a red-brown stringer on its open side, a cap along it.
    step = 8 if cartoon else 4

    def stair_labels(r, top):
        if top == Z(4):
            return ("co_landing", "co_landing_dark", "co_riser_dark")
        return ("co_tread", "co_riser", "co_riser_dark")

    ys, ye, surface = stair(m, 5, 0, 3, X(5) + 1, X(6) - 2, step, stair_labels)
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

    m.storeys = [{"stand": 1, "tiles": set(house), "entry": "vault", "cut": 3},
                 {"stand": 4, "tiles": set(house), "entry": "stair", "cut": 6}]
    m.stairs = {(5, 0): 2, (5, 1): 3, (5, 2): 4}
    m.climbs = [((5, 1, 3), (4, 1, 4))]
    m.figure = (5, 0, 2, 200)
    return m


BUILDINGS = {
    "DomeLab": lab,
    "RedClinic": clinic,
    "GrayEntryHouse": lambda cartoon: mansard("A", cartoon),
    "GrayWindowHouse": lambda cartoon: mansard("B", cartoon),
    "CyanEntryHouse": lambda cartoon: mansard("C", cartoon),
    "FlowerCottage": cottage,
}


def build(kind, cartoon):
    return BUILDINGS[kind](cartoon)
