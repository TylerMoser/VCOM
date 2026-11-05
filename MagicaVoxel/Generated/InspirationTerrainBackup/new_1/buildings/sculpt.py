"""The new_1 cottage's geometry, on VCOM's grid, as the poke_u buildings are drawn
(their helpers copied from poke_u/buildings/sculpt.py, which has them from poke_r).

new_1.jpg is pixel art enlarged 4.6 times (its art pixels rebuilt in the
collection's new_1_native.png): a tile is 16 of its art pixels, so a voxel is one
of them across and in depth. Its heights are foreshortened to 0.6 (its door is
drawn 19.2 art pixels tall for its two levels).

Every model is drawn on the game's tile grid so that it can be cut into the
game's 16-cubed pieces cleanly (a middle, an edge or a corner slot each):

- 16 voxels a tile. Tile boundaries run at x = 8 + 16i and y = 8 + 16j: every
  canvas has half a tile of margin all round the footprint, which holds the outer
  halves of the edge pieces (the beam, the pillars, the flower boxes, the step).
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
  choice): new_1 draws none, so the cottage is one storey; its flat roof is no floor.
- Corners where four tiles meet are decoration to the fight: the corner pillars
  stand there.
- MagicaVoxel axes: x across the front, y from the front (low y) to the back, z
  up. The front faces -y (Godot +z), as every building in this workspace.

Voxels carry material labels (palettes.LABELS), not colours, and each its role
for the game's slots (Model.role). Cartoon builds the same building simplified
and regularised on the same grid: its door, windows and slots are the Base's.
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


def walls_of(m, x0, x1, y0, y1):
    """The four walls of a box on boundaries x0..x1, y0..y1, and their spans."""
    walls = {"front": Wall(m, "x", y0, -1), "back": Wall(m, "x", y1, +1),
             "left": Wall(m, "y", x0, -1), "right": Wall(m, "y", x1, +1)}
    spans = {"front": (x0, x1 - 1), "back": (x0, x1 - 1), "left": (y0, y1 - 1), "right": (y0, y1 - 1)}
    return walls, spans


def beam(m, x0, x1, y0, y1, z0, z1, role):
    """A timber beam, its top lit and its underside dark, as drawn."""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                m.put(x, y, z, "timber_light" if z == z1 else ("timber_dark" if z == z0 else "timber"), role)




# ----------------------------------------------------------------------------
# Plants the cottage holds, the same models as new_1's plant families (their own
# files), set on it where the art draws them; their colours become this palette's
# labels.

def _plant_labels(vox, labels):
    """{(x, y, z): label} of a plant model's {(x, y, z): (material, rgb)}: each voxel
    the nearest in colour of [labels]."""
    import palettes
    out = {}
    for p, (mat, rgb) in vox.items():
        out[p] = min(labels, key=lambda l: sum((palettes.LABELS[l][0][i] - rgb[i]) ** 2 for i in range(3)))
    return out


def place(m, vox, at, role="mid", over=False, keep=None):
    """Sets a plant model's voxels on the building with its middle (canvas middle,
    z 0) at [at] = (x, y, z); a voxel already there is kept unless [over]; [keep](q)
    leaves out the voxels it refuses (a plant's leaves that would grow into a wall)."""
    xs = [p[0] for p in vox]
    ys = [p[1] for p in vox]
    cx, cy = (min(xs) + max(xs) + 1) / 2.0, (min(ys) + max(ys) + 1) / 2.0
    for (x, y, z), label in vox.items():
        q = (int(math.floor(at[0] + x + 0.5 - cx)), int(math.floor(at[1] + y + 0.5 - cy)), at[2] + z)
        if keep is not None and not keep(q):
            continue
        if over or q not in m.v:
            m.put(*q, label, role)


def prune(m, labels):
    """Takes off the building any part apart from its main body made only of
    [labels] (a plant's leaf cut loose by the wall it would have grown into)."""
    left = set(m.v)
    parts = []
    while left:
        seed = left.pop()
        part, todo = {seed}, [seed]
        while todo:
            x, y, z = todo.pop()
            for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)):
                if q in left:
                    left.discard(q)
                    part.add(q)
                    todo.append(q)
        parts.append(part)
    parts.sort(key=len, reverse=True)
    for part in parts[1:]:
        assert all(m.v[q] in labels for q in part), ("a part of the building itself is apart", len(part))
        for q in part:
            m.erase(*q)


# ----------------------------------------------------------------------------
# The cottage (one in new_1.jpg): five tiles by two, one storey under a flat stone
# roof. Blue-grey stone walls in courses, a square stone pillar at each corner; the
# front's two window bays dark (the unlit inside), each over a flower box on the
# stone base course, the left box with two plants; the dark red-brown door of two
# leaves in tile 2 under a round-headed arch of lighter wood, a half round
# doorstep of slate in front of it; a dark beam all round under the roof; the
# roof's tan stone parapet over it, the roof's middle recessed and cracked, a
# chimney at its back left, moss and a flowering plant at its left end, as drawn.

def stone(u, z, cartoon):
    """The walls' stone in courses eight voxels high (sixteen in Cartoon) from the
    floor, blocks eight long (sixteen) staggered by half from course to course:
    dark joints, the top of each course lit, a few dark pits in each block (Base)."""
    ch = 16 if cartoon else 8
    bl = 16 if cartoon else 8
    course = (z - 16) // ch
    k = (z - 16) % ch
    if k == 0:
        return "stone_joint"
    if (u - 8 + (course % 2) * (bl // 2)) % bl == 0:
        return "stone_joint"
    if k == ch - 1:
        return "stone_light"
    if not cartoon:
        h = (u * 73 + z * 151 + course * 37) % 23
        if h == 0:
            return "stone_dark"
        if h in (5, 11):
            return "stone_pit"
    return "stone"


def rim_face(u, z, cartoon):
    """The parapet's face, z 56 to 72, over the beam: blocks of tan stone a tile
    long, their joints on the tile boundaries, lit along the top, dark at the foot."""
    if z == 72:
        return "rim_light"
    if (u - 8) % 16 == 0:
        return "rim_joint"
    if z == 56:
        return "rim_dark"
    if not cartoon and z >= 70:
        return "rim_light"
    return "rim"


ROOF_TOP, PARAPET, RIM_W = 68, 72, 6


def cottage(cartoon):
    import sys
    from pathlib import Path
    here = Path(__file__).resolve().parent
    # the plant builders: beside this folder while it is made, in output/new_images/lib once delivered
    for lib in (here.parent / "lib", here.parents[1] / "new_images" / "lib"):
        if (lib / "new1_plants.py").exists():
            sys.path.insert(0, str(lib))
            break
    import new1_plants
    import new1_sculpt

    m = Model(5, 2, 6, "New1_Cottage")
    foundation(m, m.footprint, lambda x, y: planks(x, y, cartoon))
    x0, x1, y0, y1 = X(0), X(5), Y(0), Y(2)            # walls on x 8, 88 and y 8, 40
    walls, spans = walls_of(m, x0, x1, y0, y1)
    front, back, left, right = walls["front"], walls["back"], walls["left"], walls["right"]

    # The walls: stone up to the beam (z 50), the beam z 50-55 a voxel proud, the
    # parapet's face over it to the roof (z 56-63), every wall the same.
    for wall, (ua, ub) in ((front, (x0 - 1, x1)), (back, (x0 - 1, x1)), (left, (y0 - 1, y1)),
                           (right, (y0 - 1, y1))):
        for u in range(ua, ub + 1):
            for z in range(16, 64):
                if z < 50:
                    label = stone(u, z, cartoon)
                elif z < 56:
                    label = "beam_light" if z == 55 else ("beam_dark" if z == 50 else "beam")
                else:
                    label = rim_face(u, z, cartoon)
                wall.put(u, 0, z, label)
                wall.put(u, 1, z, "ceiling" if z >= 56 else label)
            for z in range(50, 56):
                wall.put(u, -1, z, "beam_light" if z == 55 else ("beam_dark" if z == 50 else "beam"))

    # The corner pillars: square stone columns eight voxels a side at each corner,
    # standing a voxel proud of both walls, floor to beam. Decoration to the fight,
    # as the poke_u cottage's posts.
    for (xa, xb, ya, yb) in ((x0 - 2, x0 + 6, y0 - 2, y0 + 6), (x1 - 7, x1 + 1, y0 - 2, y0 + 6),
                             (x0 - 2, x0 + 6, y1 - 7, y1 + 1), (x1 - 7, x1 + 1, y1 - 7, y1 + 1)):
        for x in range(xa, xb + 1):
            for y in range(ya, yb + 1):
                for z in range(16, 50):
                    outer = x in (xa, xb) or y in (ya, yb)
                    if not outer and (x0 <= x < x1 and y0 <= y < y1):
                        continue
                    u = x if y in (ya, yb) else y
                    m.put(x, y, z, stone(u + 3, z, cartoon) if outer else "stone", "corner")

    # The front: the base course (the sill, z 16-30) whole; the window bays over it,
    # dark from the pillar to the door's frame, their glass only within tiles 1 and
    # 3 (each its own window piece); in the foot of each bay a flower box, z 30-37,
    # two voxels proud, the stone showing under it, as drawn.
    for (ra, rb) in ((x0 + 8, X(1) - 1), (X(4), x1 - 9)):          # the dark parts of the bays in tiles 0 and 4
        for u in range(ra, rb + 1):
            for z in range(31, 50):
                front.erase(u, 0, z)
                front.put(u, 1, z, "recess")
    for (ua, ub) in ((X(1), X(1) + 9), (X(4) - 10, X(4) - 1)):     # the windows in tiles 1 and 3
        front.pane(ua, ub, 31, 49, "recess", "glass_dark")
    proud = 3 if cartoon else 2
    BOX0, BOX1 = 30, 37
    for (ba, bb, plants) in ((x0 + 8, X(1) + 9, True), (X(4) - 10, x1 - 9, False)):
        for u in range(ba, bb + 1):
            for w in range(-proud, 1):
                for z in range(BOX0, BOX1 + 1):
                    edge = u in (ba, bb) or w == -proud
                    if z == BOX0:
                        label = "box_dark"
                    elif z == BOX1 and not edge:
                        label = "soil"
                    else:
                        label = "box"
                    front.put(u, w, z, label)
        if plants:
            # the two plants, their leaves pressed front to back to stand in the box
            pv, _ = new1_sculpt.planter_plant(cartoon)
            ys = [p[1] for p in pv]
            cy = (min(ys) + max(ys) + 1) / 2.0
            squashed = {}
            for (x, y, z), v in pv.items():
                squashed[(x, int(math.floor(cy + (y + 0.5 - cy) * 0.4)), z)] = v
            pl = _plant_labels(squashed, ["plant", "plant_mid", "plant_dark"])
            for u in (ba + 4.5, bb - 4.0):
                place(m, pl, (u, y0 - 1 - proud / 2.0, BOX1 + 1), "ey", over=True,
                      keep=lambda q: q[1] <= y0 - 1)

    # The door in tile 2 (closed, two leaves, one doorway slot), as drawn.
    m.doors += [("ey", 2, 0, 1), ("ey", 2, 0, 2)]
    d0 = X(2)
    seams = (0, 4, 8, 12) if cartoon else (0, 3, 6, 9, 12)
    for u in range(d0, d0 + 16):
        k = u - d0
        for z in range(16, 48):
            if k in (7, 8):
                label = "door_dark"
            elif z == 47:
                label = "door_light"
            elif (k % 8) in seams[1:] and (k % 8) != 0 and not cartoon and k % 8 in (3, 6):
                label = "door_dark"
            elif cartoon and k in (3, 12):
                label = "door_dark"
            else:
                label = "door"
            front.put(u, 0, z, label)
            front.put(u, 1, z, label)
    # its frame: posts either side, a voxel proud, and a round-headed arch over it
    fa, fb = X(2) - 6, X(3) + 5
    mid = (fa + fb) / 2.0
    for u in range(fa, fb + 1):
        top = 48 + 7.5 * (1 - ((u + 0.5 - mid - 0.5) / ((fb - fa) / 2.0 + 0.5)) ** 2) ** 0.5
        for z in range(16, int(top) + 1):
            in_door = d0 <= u < d0 + 16 and z < 48
            if in_door:
                continue
            label = "arch"
            if z >= int(top) - (1 if cartoon else 0):
                label = "arch_light"
            elif z == 48 and d0 <= u < d0 + 16:
                label = "arch_dark"
            for w in (-1, 0, 1):
                front.put(u, w, z, label)
    # the doorstep: a half round of slate in front of the door, its top at the floor's
    m.role_now = "ey"
    for x in range(fa - 2, fb + 3):
        for y in range(0, y0 - 1):
            d = ((x + 0.5 - mid - 0.5) ** 2 + ((y0 - 1) - (y + 0.5)) ** 2) ** 0.5
            if d <= 10.5:
                for z in range(13, 16):
                    m.put(x, y, z, "step_dark" if (z == 13 or (d > 9.5 and not cartoon)) else "step")
    m.role_now = "mid"

    # The back, inferred: two windows in tiles 1 and 3 over the base course, no
    # boxes. The sides, inferred: a window in tile 1 of each.
    for (ua, ub) in ((X(1) + 2, X(2) - 3), (X(3) + 2, X(4) - 3)):
        back.pane(ua, ub, 31, 49, "recess", "glass_dark")
    for wall in (left, right):
        wall.pane(Y(1) + 2, Y(2) - 4, 31, 49, "recess", "glass_dark")

    # The roof: a slab z 64-68 over the walls' outer faces, its underside the
    # ceiling, the parapet z 69-72 round its edge six voxels wide, the middle's top at
    # z 68 recessed four, cracked at the front, as drawn.
    m.role_now = "roof"
    rx0, rx1, ry0, ry1 = x0 - 1, x1, y0 - 1, y1
    for x in range(rx0, rx1 + 1):
        for y in range(ry0, ry1 + 1):
            rim = x < rx0 + RIM_W or x > rx1 - RIM_W or y < ry0 + RIM_W or y > ry1 - RIM_W
            edge = x in (rx0, rx1) or y in (ry0, ry1)
            top = PARAPET if rim else ROOF_TOP
            for z in range(64, top + 1):
                if z == 64 and not edge:
                    label = "ceiling"
                elif edge:
                    label = rim_face(x if y in (ry0, ry1) else y, z, cartoon)
                elif z == top:
                    if rim:
                        joint = (x - 8) % 16 == 0 if y < ry0 + RIM_W or y > ry1 - RIM_W else (y - 8) % 16 == 0
                        label = "rim_joint" if joint else "rim_light"
                    else:
                        label = "rim"
                else:
                    label = "rim_dark" if (rim and z == top - 1 and not cartoon) else "rim"
                m.put(x, y, z, label)
    if not cartoon:
        crack = [(47, 17), (52, 19), (56, 18), (60, 20), (66, 19), (71, 22), (74, 21)]
        branch = [(56, 18), (58, 15), (61, 14)]
        for line in (crack, branch):
            for (xa, ya), (xb, yb) in zip(line, line[1:]):
                steps = max(abs(xb - xa), abs(yb - ya)) * 2
                for s in range(steps + 1):
                    t = s / float(steps)
                    m.put(int(round(xa + (xb - xa) * t)), int(round(ya + (yb - ya) * t)), ROOF_TOP, "crack")

    # The chimney at the back left: a tan stone stack from the roof's middle to z 88,
    # its top lit, a dark flue three deep in it, its right side shaded (Base).
    cx0, cx1, cy0, cy1 = 18, 31, 26, 33
    for x in range(cx0, cx1 + 1):
        for y in range(cy0, cy1 + 1):
            for z in range(ROOF_TOP + 1, 89):
                if z == 88:
                    label = "chimney_light"
                elif not cartoon and x == cx1:
                    label = "rim_dark"
                elif (z - ROOF_TOP) % 8 == 0 and not cartoon:
                    label = "rim_joint"
                else:
                    label = "rim"
                m.put(x, y, z, label)
    for x in range(cx0 + 3, cx1 - 2):
        for y in range(cy0 + 2, cy1 - 1):
            for z in range(86, 89):
                m.erase(x, y, z)
            m.put(x, y, 85, "flue")

    # The moss over the roof's left end (the back two-thirds of the left parapet and
    # down its side), and a little right of the chimney, as drawn: the trees' olive,
    # four small yellow flowers in it and two tiny sprouts.
    def mossy(x, y, z):
        return (x < rx0 + RIM_W + 4 and y >= 22) or (cx1 + 1 <= x <= cx1 + 6 and cy0 + 2 <= y <= cy1 + 3)

    for (x, y, z), label in list(m.v.items()):
        if z < 60 or not mossy(x, y, z):
            continue
        if (x, y, z + 1) in m.v and not (x - 1, y, z) not in m.v:
            continue
        exposed = (x, y, z + 1) not in m.v or (x == rx0 and (x - 1, y, z) not in m.v)
        if not exposed:
            continue
        if cartoon:
            lab = "moss"
        else:
            lab = "moss_dark" if (x + y) % 9 == 0 else "moss"
        m.put(x, y, z, lab, m.role.get((x, y, z), "roof"))
    # its four small yellow flowers, and the two tiny sprouts in it (new_1's sprout),
    # where the art draws them
    for (fx, fy) in ((15, 40), (10, 36), (17, 36), (10, 31)):
        for x in (fx - 1, fx):
            for y in (fy - 1, fy):
                if (x, y, PARAPET) in m.v:
                    m.put(x, y, PARAPET, "moss_dot", "roof")
    sv, _ = new1_sculpt.sprout(cartoon)
    sl = _plant_labels(sv, ["plant", "plant_mid", "plant_dark"])
    for (sx, sy) in ((13.0, 38.0), (10.0, 24.0)):
        place(m, sl, (sx, sy, PARAPET + 1), "roof")
    m.role_now = "mid"

    # The flowering plant on the roof's front left, as drawn (new_1's roof plant).
    rv, _ = new1_plants.roof_plant(cartoon)
    rl = _plant_labels(rv, ["plant", "plant_mid", "plant_dark", "petal", "petal_dark", "petal_heart"])
    place(m, rl, (21.0, 17.0, ROOF_TOP + 1), "roof")

    prune(m, {"plant", "plant_mid", "plant_dark", "petal", "petal_dark", "petal_heart"})
    m.storeys = [{"stand": 1, "tiles": set(m.footprint), "entry": "vault", "cut": 4}]
    m.figure = (2, -1, 1, 200)
    return m


BUILDINGS = {"Cottage": cottage}


def build(kind, cartoon):
    return BUILDINGS[kind](cartoon)
