"""Assembles kit pieces into a layout as the level editor would: each raised tile
the piece and turn its neighbours call for (piece_for, place), from a layout drawn
as text (parse); the standard layout every style is checked and previewed in
(standard). Drawing it is fastview's."""
import kit

# The canonical pieces' exposed sides, and what a quarter turn makes of a side
# ((x, y) -> (15 - y, x): -y becomes +x, +x becomes +y, +y becomes -x, -x becomes -y).
TURN_SIDE = {"-y": "+x", "+x": "+y", "+y": "-x", "-x": "-y"}
NEIGHBOUR = {"-y": (0, -1), "+y": (0, 1), "-x": (-1, 0), "+x": (1, 0)}


def turned_sides(sides, q):
    for _ in range(q % 4):
        sides = {TURN_SIDE[s] for s in sides}
    return sides


def turn_voxels(vox, q):
    for _ in range(q % 4):
        vox = {(15 - y, x, z): c for (x, y, z), c in vox.items()}
    return vox


def piece_for(mask, tx, ty):
    """(piece, turn) for the raised tile (tx, ty) of [mask] (a set of raised tiles)."""
    lower = {s for s, (dx, dy) in NEIGHBOUR.items() if (tx + dx, ty + dy) not in mask}
    if not lower:
        for q, (dx, dy) in enumerate([(-1, -1), (1, -1), (1, 1), (-1, 1)]):
            if (tx + dx, ty + dy) not in mask:
                return "InnerCorner", q
        return "Fill", 0
    if len(lower) == 1:
        s = lower.pop()
        return "Straight", {"-y": 0, "+x": 1, "+y": 2, "-x": 3}[s]
    if len(lower) == 2:
        for q in range(4):
            if turned_sides({"-y", "-x"}, q) == lower:
                return "OuterCorner", q
        for q in range(2):
            if turned_sides({"-y", "+y"}, q) == lower:
                return "Ridge", q
    if len(lower) == 3:
        for q in range(4):
            if turned_sides({"-y", "+y", "-x"}, q) == lower:
                return "RidgeEnd", q
    if len(lower) == 4:
        return "Pillar", 0
    raise ValueError("no piece for %s at %s" % (sorted(lower), (tx, ty)))


# Letters in a layout for raised tiles that take an extra piece in place of the
# straight face their neighbours call for.
EXTRA = {"F": "Fall", "N": "NarrowFall", "C": "CaveMouth", "A": "Archway", "D": "Drain", "V": "Notch",
         "W": "Channel"}
# Letters for lower tiles of another ground: '~' the pool a waterfall falls into.
LOWER = {".": None, "~": "Fall"}


def parse(rows):
    """(raised tiles, all tiles, {tile: extra piece}) of a layout drawn as text:
    '#' raised, '.' lower, a letter of EXTRA a raised tile with that piece; the
    first row is the back (high y)."""
    H = len(rows)
    mask, tiles, extra = set(), {}, {}
    for ty, line in enumerate(rows):
        for tx, ch in enumerate(line):
            t = (tx, H - 1 - ty)
            tiles[t] = ch
            if ch not in LOWER:
                mask.add(t)
            if ch in EXTRA:
                extra[t] = EXTRA[ch]
    return mask, tiles, extra


def lower_family(style, ch):
    """The ground tile of a lower tile drawn [ch]: '~' is the pool of the style's
    fall (or its spring's)."""
    if LOWER.get(ch) == "Fall":
        for piece in ("Fall", "NarrowFall"):
            if piece in style.bottoms:
                return style.bottoms[piece]
    return style.bottom


def place(mask, extra, tx, ty):
    """(piece, turn) of raised tile (tx, ty): its extra piece in the straight face's
    turn, or what its neighbours call for."""
    piece, q = piece_for(mask, tx, ty)
    if (tx, ty) in extra:
        e = extra[(tx, ty)]
        if e == "Channel":
            assert piece == "Fill", ("a channel tile needs raised ground all round", (tx, ty), piece)
            return e, 0
        assert piece == "Straight", ("an extra piece needs a straight edge", (tx, ty), piece)
        return e, q
    return piece, q


def assemble(style, rows, treatment, painted=None):
    """World voxels (x, y, z) -> RGB of a layout drawn as text [rows] (see parse()),
    painted in [treatment]."""
    mask, tiles, extra = parse(rows)
    painted = painted if painted is not None else {}
    world = {}
    low = kit.ground(style.bottom, treatment) if style.bottom else {}
    for (tx, ty) in sorted(tiles):
        if (tx, ty) in mask:
            piece, q = place(mask, extra, tx, ty)
            key = (piece, treatment)
            if key not in painted:
                raw = kit.build(style, piece, "Cartoon" in treatment)
                v, pal, groups = kit.paint(style, raw, treatment)
                painted[key] = {p: pal[i - 1][:3] for p, i in v.items()}
            vox = turn_voxels(painted[key], q)
        else:
            fam = lower_family(style, tiles[(tx, ty)])
            low = kit.ground(fam, treatment) if fam else {}
            vox = {p: rgb for p, (i, rgb, g) in low.items()}
        for (x, y, z), c in vox.items():
            world[(16 * tx + x, 16 * ty + y, z)] = c
    return world


def standard(extra=()):
    """The layout every style is checked in: every base piece (straight faces, outer
    and inner corners, a ridge with both ends, a pillar, the raised fill) and, for a
    style with them, a waterfall fed by a channel into a pool on the front edge and
    a cave mouth (or archway) and a drain on the inner front edge, all facing the
    views."""
    rows = ["............",
            ".#######....",
            ".#######.#..",
            ".#######....",
            ".####...###.",
            ".####.......",
            "............"]
    grid = [list(r) for r in rows]
    if "Fall" in extra:
        for x in (2, 3):
            grid[5][x] = "F"
            grid[6][x] = "~"
            if "Channel" in extra:
                grid[4][x] = grid[3][x] = "W"
    if "NarrowFall" in extra:
        grid[5][3] = "N"
        grid[6][3] = "~"
    if "CaveMouth" in extra:
        grid[3][5] = "C"
    if "Archway" in extra:
        grid[3][5] = "A"
    if "Drain" in extra:
        grid[3][6] = "D"
    if "Notch" in extra:
        grid[3][6] = "V"
    return ["".join(r) for r in grid]
