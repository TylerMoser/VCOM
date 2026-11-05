"""Terrain kits for VCOM: the ground's shapes (cliffs, ledges, banks, walls, island
rims, platforms, waterfalls, cave mouths) as complete pieces, each one tile across
(16 x 16 voxels) and a whole number of levels tall, placed side by side and turned
in the level editor to build any layout (the user's choices, 2026-11-03: modular
kits, heights as drawn in whole levels).

A piece is a column standing on the game's grid:

- Level 0 (z 0-15) is the lower ground: the image's own ground tile (output/ground's)
  copied whole, so the kit meets the flat tiles round it exactly.
- Over it the body of the cliff (or wall, or bank) rises to the upper ground, whose
  top three layers are again the image's own ground tile, copied: a piece of
  height H levels has its top at z 16 (H + 1) - 1, stood on at level H + 1.
- Its face is set back F voxels inside the tile, so that the face's relief, the rim
  overhanging it and the foot spreading under it never leave the tile; neighbours
  then join at the tile's edges.
- The front faces -y (Godot +z). Straight has its face there; OuterCorner faces -y
  and -x; InnerCorner is a full column with the concave notch where those two
  meet; Fill has none. Turned a quarter at a time (the game's turn, (x, y) to
  (15 - y, x) in MagicaVoxel's axes) they make every edge and corner, and the
  face's texture runs on across a corner as it does along a straight run.
- Every side a piece shows (its face, and its tile edges where a neighbour is
  missing or lower) is drawn in the face's texture; only the inside is fill.

Each style is a family's look in an image's own colours (styles.py), painted in
the seven treatments here.
"""
import json
import math
from pathlib import Path

from voxlib import read

ROOT = Path(r"C:/Users/tandm/Documents/Projects/VoxelRidgeInspiration")
TILE = 16
TREATMENTS = ["Base", "Cartoon", "CratePalette", "TwoColor", "Cartoon_TwoColor", "CratePalette_TwoColor",
              "Cartoon_CratePalette_TwoColor"]
CRATE = json.loads((ROOT / "knowledge" / "palettes" / "crate-palette.json").read_text())
CRATE_RGBA = [tuple(c) for c in CRATE["rgba"]]
CRATE_GLASS = 253
# Crate palette indices each material class may use (the ground collection's ranges
# where they overlap, the buildings' elsewhere); 255 is never used.
CRATE_CLASSES = {
    "earth": [178, 179, 180, 225, 226, 227, 228, 229, 233, 234, 235, 236, 237, 238],
    "grass": [241, 242, 243, 244, 245, 246],
    "rock": [177, 193, 194, 195, 196, 201, 202, 203, 204, 205, 206, 249, 250],
    "warm_rock": [178, 179, 180, 233, 234, 235, 236, 237, 238, 193, 194, 195, 196],
    "sand": [229, 230, 236, 237, 238],
    "water": [249, 250, 251, 252, 254],
    "foam": [195, 196, 248, 254],
    "dark": [177, 201, 202, 203, 204, 225],
    "red": [178, 179, 180, 219, 220, 221, 222, 234, 235],
    "light": [193, 194, 195, 196, 230, 236, 237, 238, 248],
    "wood": [178, 179, 180, 225, 226, 227, 228, 229, 230, 233, 234, 235, 236, 237, 238],
    "orange": [221, 222, 228, 229, 230],
}
GROUND = json.loads((ROOT / "output" / "ground" / "manifest.json").read_text())
# The ground collection's water kinds (output/ground/generate.py's WATER).
WATER_KINDS = {"calm", "waves", "ripples", "caustic", "dapple"}
GROUND_FILES = {(r["family"], r["style"]): r for r in GROUND["models"]}


def geometry_of(treatment):
    """The treatment whose geometry [treatment] has: Base or Cartoon."""
    return "Cartoon" if "Cartoon" in treatment else "Base"


_ground = {}


def ground(family, treatment):
    """The ground tile [family] in [treatment], as output/ground delivered it:
    (x, y, z) -> (palette index, RGB, group), the group read off the tile's Base or
    Cartoon file (whose indices are one to a group)."""
    key = (family, treatment)
    if key not in _ground:
        row = GROUND_FILES[(family, treatment)]
        _, vox, pal, _ = read(ROOT / row["file"])
        geo = GROUND_FILES[(family, geometry_of(treatment))]
        _, gvox, _, _ = read(ROOT / geo["file"])
        group = {i: sem.split(":")[1] for sem, idxs in geo["groups"].items() for i in idxs}
        assert set(vox) == set(gvox), family
        _ground[key] = {p: (i, tuple(pal[i - 1][:3]), group[gvox[p]]) for p, i in vox.items()}
    return _ground[key]


# The four ways a face can look and its texture coordinate u along it, chosen so
# that a face runs on into the straight piece turned to face that way.
FACE_U = {"-y": lambda x, y: x, "+x": lambda x, y: y, "+y": lambda x, y: 15 - x, "-x": lambda x, y: 15 - y}
EDGE_DIST = {"-y": lambda x, y: y + 0.5, "+x": lambda x, y: 15.5 - x, "+y": lambda x, y: 15.5 - y,
             "-x": lambda x, y: x + 0.5}


def plan(piece, x, y, F, R, r_in):
    """(d, face) for the column (x, y): its centre's distance inside the body's
    nominal outline (negative outside) and the face nearest it, for a piece whose
    faces are set back F from the tile's edges, its convex corner rounded to R and
    its concave one to r_in."""
    px, py = x + 0.5, y + 0.5
    if piece == "Fill":
        return 99.0, None
    if piece == "Straight":
        return py - F, "-y"
    if piece == "OuterCorner":
        dx, dy = px - F, py - F
        face = "-y" if dy <= dx else "-x"
        if dx < R and dy < R:
            return R - math.hypot(R - dx, R - dy), face
        return min(dx, dy), face
    if piece == "InnerCorner":
        dx, dy = px - F, py - F
        face = "-y" if dy <= dx else "-x"
        if dx < 0 and dy < 0:
            if dx > -r_in and dy > -r_in:
                return math.hypot(dx + r_in, dy + r_in) - r_in, face
            return max(dx, dy), face
        if dx >= 0 and dy >= 0:
            return math.hypot(dx, dy), face
        return (dy if dx < 0 else dx), ("-y" if dx < 0 else "-x")
    if piece == "Ridge":                       # faces at -y and +y: a raised strip a tile wide
        a, b = py - F, (16 - F) - py
        return (a, "-y") if a <= b else (b, "+y")
    if piece == "RidgeEnd":                    # the strip ending at -x
        a, b, c = py - F, (16 - F) - py, px - F
        dmin = min(a, b)
        face = "-y" if a <= b else "+y"
        if c < R and dmin < R:
            return R - math.hypot(R - c, R - dmin), ("-x" if c < dmin else face)
        return (c, "-x") if c < dmin else (dmin, face)
    if piece == "Pillar":                      # a single raised tile, faces all round
        sides = sorted([(py - F, "-y"), ((16 - F) - py, "+y"), (px - F, "-x"), ((16 - F) - px, "+x")])
        (a, fa), (b, fb) = sides[0], sides[1]
        if a < R and b < R and {fa, fb} not in ({"-y", "+y"}, {"-x", "+x"}):
            return R - math.hypot(R - a, R - b), fa
        return a, fa
    raise ValueError(piece)


PIECES = ("Fill", "Straight", "OuterCorner", "InnerCorner", "Ridge", "RidgeEnd", "Pillar")


def build(style, piece, cartoon):
    """The piece's voxels in its geometry: (x, y, z) -> ("lab", label) for the body,
    or ("gnd", family, p) for a voxel copied from a ground tile (p its place in that
    tile). A style may give a piece another's plan (a waterfall the straight face's),
    its own ground tiles above and below, and finish it (style.decorate)."""
    H = style.levels
    ztop = TILE * (H + 1) - 1
    F, R, r_in = style.inset, style.radius, style.r_in
    base = style.plan_of(piece)
    top, bottom = style.top_for(piece), style.bottom_for(piece)
    v = {}
    under = {}
    if bottom:
        for p in ground(bottom, "Cartoon" if cartoon else "Base"):
            v[p] = ("gnd", bottom, p)
            under[p[:2]] = max(under.get(p[:2], -1), p[2])
    for x in range(TILE):
        for y in range(TILE):
            d, face = plan(base, x, y, F, R, r_in)
            u = FACE_U[face](x, y) if face else 0
            # The body stands on the lower tile: from the level up, or from just above
            # a surface lower than the level (water's), so it never floats over it.
            z0 = min(TILE, under.get((x, y), TILE - 1) + 1) if bottom else 0
            for z in range(z0, ztop + 1):
                r = style.relief(u, z, cartoon, face, piece) if face else style.fill_relief(x, y, z, cartoon, piece)
                if d + r < 0:
                    continue
                if z >= ztop - 2 and top:
                    tp = (x, y, z - (ztop - 15))
                    if tp in ground(top, "Cartoon" if cartoon else "Base"):
                        v[(x, y, z)] = ("gnd", top, tp)
                    continue
                if z >= ztop - 1 and not top:
                    # A top of the body's own material (a cave wall's rock).
                    v[(x, y, z)] = ("lab", style.top_texture(x, y, z, cartoon, piece))
                    continue
                # The nearest side the voxel shows: its face, or a tile edge.
                depth, side = (d + r, face) if face else (99.0, None)
                for e, dist in EDGE_DIST.items():
                    if e == face:
                        continue
                    if dist(x, y) < depth:
                        depth, side = dist(x, y), e
                su = FACE_U[side](x, y) if side else 0
                v[(x, y, z)] = ("lab", style.texture(su, z, depth, cartoon, side, piece))
    style.decorate(piece, v, cartoon)
    return drop_crumbs(v)


def drop_crumbs(v, most=64):
    """[v] without any six-connected scrap of at most [most] voxels cut off from the
    rest (rounding at a corner can leave one); a larger second part is kept, for the
    validator to find."""
    left = set(v)
    parts = []
    while left:
        todo = [left.pop()]
        part = set(todo)
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
        if len(part) <= most:
            for q in part:
                del v[q]
    return v


def under_top(style, piece, x, y, cartoon):
    """The top z of the lower tile's column (x, y) under [piece], -1 with none."""
    bottom = style.bottom_for(piece)
    if not bottom:
        return -1
    g = ground(bottom, "Cartoon" if cartoon else "Base")
    return max((z for z in range(TILE) if (x, y, z) in g), default=-1)


def paint(style, raw, treatment):
    """(voxels (x, y, z) -> palette index, palette of 256 RGBA, groups {semantic: indices})
    of a piece built by build(), painted in [treatment]. Non-crate palettes hold each
    distinct colour once; crate files use the pinned palette, each label on its
    class's nearest entry, the copied ground voxels on their own tiles' entries."""
    flat = "TwoColor" in treatment
    crate = "CratePalette" in treatment
    out, groups, colour_index, nearest = {}, {}, {}, {}
    palette = list(CRATE_RGBA) if crate else [(0, 0, 0, 255)] * 256

    def index_of(semantic, rgb, cls, fixed=None):
        if crate:
            if fixed is not None:
                idx = fixed
            else:
                if (cls, rgb) not in nearest:
                    nearest[(cls, rgb)] = min(CRATE_CLASSES[cls], key=lambda i: (
                        sum((CRATE_RGBA[i - 1][j] - rgb[j]) ** 2 for j in range(3)), i))
                idx = nearest[(cls, rgb)]
        else:
            if rgb not in colour_index:
                colour_index[rgb] = len(colour_index) + 1
                assert colour_index[rgb] <= 254, "too many colours"
                palette[colour_index[rgb] - 1] = tuple(rgb) + (255,)
            idx = colour_index[rgb]
        groups.setdefault(semantic, set()).add(idx)
        return idx

    for p, ref in raw.items():
        if ref[0] == "lab":
            rgb, group, cls = style.labels[ref[1]]
            if flat:
                out[p] = index_of(group, style.flat_colour(group, treatment), cls,
                                  style.flat_crate(group, treatment) if crate else None)
            else:
                out[p] = index_of(group, rgb, cls)
            continue
        family, gp = ref[1], ref[2]
        i, rgb, g = ground(family, treatment)[gp]
        # A copied ground voxel keeps its own tile's colour in this treatment, so the
        # piece's ground is the ground collection's tile exactly, side by side with it.
        out[p] = index_of(style.ground_group(g, family), rgb, None, i if crate else None)
    assert 255 not in out.values()
    return out, palette, {g: sorted(s) for g, s in groups.items()}
