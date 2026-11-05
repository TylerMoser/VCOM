"""Cuts a poke_b game-ready building into VCOM's 16-cubed level pieces, to test
that it goes into the game cleanly (poke_c/buildings/qa/cut_pieces.py, for these
buildings). Validation tooling: it writes pieces only into the directory it is
given (a scratch copy of the game), never into output/; the delivered models stay
whole, as the user asked (no cell files).

Each voxel goes to one slot (a cell's middle, an edge across a tile boundary, or a
corner where four tiles meet) by the role the sculptor gave it (sculpt.Model.role)
and the building's footprint: a roof's voxels fill the middles only of the
building's own tiles (Model.roof_tiles), so an eave over the cottage's stair is an
edge piece and the stair keeps its headroom. A piece's .vox keeps the model's own
orientation; kinds are shared between slots whose voxels match, turned or not, and
the pieces put back together, each as the game stamps it, are the model voxel for
voxel (checked).

    from cut_pieces import cut
    layout = cut(model, kind, treatment, out_dir, cx=4, r=0)   # writes .vox + .import

The layout says, for each kind, its file and what it is to the rules: a window
(an edge piece with glass that is no door), a door (closed, solid: the user's
choice), a floor (level 0, not cut away), everything else a building piece cut
away with the walls.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import palettes  # noqa: E402
from voxlib import write  # noqa: E402

IMPORT = """[remap]

importer="MagicaVoxel.With.Extensions.To.Mesh"
type="Mesh"

[deps]

source_file="res://{res}"

[params]

Scale=0.0625
GreedyMeshGenerator=true
SnapToGround=false
FirstKeyframeOnly=true
"""


def _turn(voxels, q):
    """[voxels] (a piece's, box-local in MagicaVoxel's axes) as the game stamps them
    turned [q] quarter turns: VoxelVolume.turned() takes Godot's (x, z) to
    (z, 15 - x) a turn, which in MagicaVoxel's axes (Godot z = 15 - y) is (x, y) to
    (15 - y, x)."""
    out = dict(voxels)
    for _ in range(q % 4):
        out = {(15 - y, x, z): v for (x, y, z), v in out.items()}
    return out


def _key(voxels):
    return hashlib.sha1(repr(sorted((p, c) for p, (c, g) in voxels.items())).encode()).hexdigest()[:16]


def _bound(c):
    """The tile boundary nearest voxel coordinate c: boundaries at 8 + 16 b."""
    return round((c + 0.5 - 8) / 16)


def resolve(m, x, y, z, role):
    """The model-space slot of voxel (x, y, z): ("mid", i, j, k), ("ex", b, j, k),
    ("ey", i, b, k) or ("corner", bi, bj, k); None if it touches no tile of the
    footprint at all."""
    F = m.footprint
    i, j, k = (x - 8) // 16, (y - 8) // 16, z // 16
    bi, bj = _bound(x), _bound(y)
    if (role == "mid" and (i, j) in F) or (role == "roof" and (i, j) in m.roof_tiles):
        return ("mid", i, j, k)
    cands = {
        "ex": ("ex", bi, j, k) if ((bi - 1, j) in F or (bi, j) in F) else None,
        "ey": ("ey", i, bj, k) if ((i, bj - 1) in F or (i, bj) in F) else None,
        "corner": ("corner", bi, bj, k) if any(c in F for c in ((bi - 1, bj - 1), (bi, bj - 1), (bi - 1, bj), (bi, bj))) else None,
    }
    R = m.roof_tiles
    if role == "ex":
        order = ("ex", "ey", "corner")
    elif role == "ey":
        order = ("ey", "ex", "corner")
    elif role == "corner":
        order = ("corner", "ex", "ey")
    elif role == "roof":
        # An eave or a verge goes to the edge of the roof it hangs from: past an x
        # boundary of the roof's tiles, the edge across it; past a y one, that one;
        # past both, the corner. (An eave over the cottage's stair is the house's
        # side wall's edge, never one between two of the stair's tiles.)
        if (bi - 1, j) in R or (bi, j) in R:
            order = ("ex", "ey", "corner")
        elif (i, bj - 1) in R or (i, bj) in R:
            order = ("ey", "ex", "corner")
        else:
            order = ("corner", "ex", "ey")
    else:
        nearer_x = abs(x + 0.5 - (8 + 16 * bi)) < abs(y + 0.5 - (8 + 16 * bj))
        order = ("ex", "ey", "corner") if nearer_x else ("ey", "ex", "corner")
    for o in order:
        if cands[o] is not None:
            return cands[o]
    return None


def box_origin(slot):
    t = slot[0]
    if t == "mid":
        return 8 + 16 * slot[1], 8 + 16 * slot[2], 16 * slot[3]
    if t == "ex":
        return 16 * slot[1], 8 + 16 * slot[2], 16 * slot[3]
    if t == "ey":
        return 8 + 16 * slot[1], 16 * slot[2], 16 * slot[3]
    return 16 * slot[1], 16 * slot[2], 16 * slot[3]


def godot_slot(slot, cx, r):
    """The LevelData slot of a model-space slot, the building's tile (0, 0) in cell
    (cx, ., r - 1) and its rows running toward -z (MagicaVoxel's y is Godot's -z)."""
    t, a, b, k = slot
    if t == "mid":
        return (2 * (a + cx), k, 2 * (r - 1 - b))
    if t == "ex":
        return (2 * (a + cx) - 1, k, 2 * (r - 1 - b))
    if t == "ey":
        return (2 * (a + cx), k, 2 * (r - b) - 1)
    return (2 * (a + cx) - 1, k, 2 * (r - b) - 1)


def cut(m, kind, treatment, out_dir, cx=4, r=0, res_prefix="Blocks/PokeB", family=None):
    family = family or kind
    palette, glass = palettes.palette_of(treatment, kind)
    glass_labels = {l for l in palettes.LABELS if palettes.LABELS[l][1] == "glass"}
    slots = {}
    for (x, y, z), label in m.v.items():
        slot = resolve(m, x, y, z, m.role[(x, y, z)])
        assert slot is not None, ("voxel touches no tile of the footprint", m.name, (x, y, z), label)
        ox, oy, oz = box_origin(slot)
        local = (x - ox, y - oy, z - oz)
        assert all(0 <= c < 16 for c in local), (slot, (x, y, z), local, label)
        slots.setdefault(slot, {})[local] = (palettes.paint(treatment, label, kind), label in glass_labels)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    kinds, pieces, by_hash, stored = {}, [], {}, {}
    doors = {(t, a, b, k) for (t, a, b, k) in m.doors}
    stairs = set(getattr(m, "stairs", {}) or {})

    def stair_only(slot):
        t, a, b, k = slot
        if t == "mid":
            tiles = [(a, b)]
        elif t == "ex":
            tiles = [(a - 1, b), (a, b)]
        elif t == "ey":
            tiles = [(a, b - 1), (a, b)]
        else:
            tiles = [(a - 1, b - 1), (a, b - 1), (a - 1, b), (a, b)]
        touching = [c for c in tiles if c in m.footprint]
        return bool(touching) and all(c in stairs for c in touching)
    for slot in sorted(slots):
        voxels = slots[slot]
        t, k = slot[0], slot[3]
        has_glass = any(g for c, g in voxels.values())
        is_door = slot in doors
        flags = {
            "floor": t == "mid" and k == 0,
            "door": is_door,
            "window": t in ("ex", "ey") and has_glass and not is_door,
            "edge": t in ("ex", "ey"),
            "corner": t == "corner",
        }
        # Cut away with the building: everything but its floor and an outside stair
        # (the cottage's, the mansard houses' front step), which stays in view as the
        # ground does.
        flags["cutaway"] = not flags["floor"] and not stair_only(slot)
        # A piece that is a kind already cut turned a quarter, a half or three
        # quarters is that kind, placed turned: R^q(V) == K means V is K turned 4 - q.
        found = None
        for q in range(4):
            fkey = (_key(_turn(voxels, q)), tuple(sorted(flags.items())))
            if fkey in by_hash:
                found = (by_hash[fkey], (4 - q) % 4)
                break
        if found is None:
            kid = "PB_%s_%03d" % (family, len(by_hash))
            by_hash[(_key(voxels), tuple(sorted(flags.items())))] = kid
            stored[kid] = voxels
            name = kid + ".vox"
            write(out_dir / name, (16, 16, 16), {p: c for p, (c, g) in voxels.items()}, palette, glass, name=kid)
            (out_dir / (name + ".import")).write_text(IMPORT.format(res="%s/%s/%s" % (res_prefix, family, name)))
            kinds[kid] = dict(flags, file="res://%s/%s/%s" % (res_prefix, family, name), voxels=len(voxels),
                              glass=sum(1 for c, g in voxels.values() if g))
            found = (kid, 0)
        pieces.append({"kind": found[0], "turn": found[1], "slot": godot_slot(slot, cx, r), "model_slot": list(slot)})
    # Put back together as the game stamps them, each kind turned as placed, the
    # pieces are the model.
    back = {}
    for p in pieces:
        ox, oy, oz = box_origin(tuple(p["model_slot"]))
        for (lx, ly, lz), (c, g) in _turn(stored[p["kind"]], p["turn"]).items():
            q = (lx + ox, ly + oy, lz + oz)
            assert q not in back, ("two pieces hold", q)
            back[q] = c
    assert back == {p: palettes.paint(treatment, l, kind) for p, l in m.v.items()}
    layout = {"family": family, "treatment": treatment, "cx": cx, "r": r, "kinds": kinds, "pieces": pieces,
              "footprint": [[cx + i, r - 1 - j] for (i, j) in sorted(m.footprint)]}
    (out_dir / "layout.json").write_text(json.dumps(layout, indent=1))
    return layout


if __name__ == "__main__":
    import argparse
    import sculpt
    a = argparse.ArgumentParser()
    a.add_argument("kind")
    a.add_argument("out_dir")
    a.add_argument("--treatment", default="Base")
    a.add_argument("--cx", type=int, default=4)
    a.add_argument("--r", type=int, default=0)
    args = a.parse_args()
    model = sculpt.build(args.kind, "Cartoon" in args.treatment)
    lay = cut(model, args.kind, args.treatment, args.out_dir, args.cx, args.r)
    print("%s %s: %d pieces, %d kinds (%d windows, %d doors)" % (
        args.kind, args.treatment, len(lay["pieces"]), len(lay["kinds"]),
        sum(1 for k in lay["kinds"].values() if k["window"]), sum(1 for k in lay["kinds"].values() if k["door"])))
