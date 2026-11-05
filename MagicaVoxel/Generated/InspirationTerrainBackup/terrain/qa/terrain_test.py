"""Tests that the terrain kits and whole islands go into VCOM cleanly, in a scratch
copy of the game.

    python qa/terrain_test.py --game <copy of VoxelXCOM/vcom> [--styles poke_n,...]
                              [--treatments Base,...] [--islands] [--render] [--out <folder>]
                              [--files <output/ or a dry run's folder>]

It never touches the game itself or output/: give it a copy of the game's vcom
folder. For every style and treatment it cuts each piece's column into the game's
16-cubed cells (one a level, as the level editor places them), copies the image's
own ground tiles in, lays the pieces out in the style's standard layout (straight
runs, outer and inner corners, a ridge with both ends, a pillar, the raised fill,
and the extras the style has: a fall fed by a channel into its pool, a cave mouth
or archway, a drain, a notch) on a field of its ground (none round a floating
rim), runs godot/terrain_probe.gd there and checks its report: every tile a floor
at its level and nothing stood on inside the cliff; a one-level face climbed and
a taller one not; the plateau reached from below only over a one-level face (from
its own top on a floating rim); and the level the game stamps the pieces voxel
for voxel. A whole island (--islands, or every one when no style is named) is cut
into cells where it hangs and checked the same way: its top a floor everywhere,
reached all over, nothing else stood on, stamped exactly. With --render, frames
by day, dusk and night in the game's own renderer.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import islands as ISL  # noqa: E402
import kit  # noqa: E402
import layout  # noqa: E402
import styles as STY  # noqa: E402
from voxlib import read, write  # noqa: E402

GODOT = r"C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe"
SHORT = {"Base": "B", "Cartoon": "C", "CratePalette": "P", "TwoColor": "T", "Cartoon_TwoColor": "CT",
         "CratePalette_TwoColor": "PT", "Cartoon_CratePalette_TwoColor": "CPT"}
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
MARGIN = 4
SIDES = {"-y": (0, -1), "+y": (0, 1), "-x": (-1, 0), "+x": (1, 0)}
# Views: yaw, pitch, distance (times the layout's size), height looked at (a share
# of its top), field of view; the last is the game's own camera.
VIEWS = [[-30, 35, 2.4, 0.3, 30], [150, 35, 2.4, 0.3, 30], [60, 30, 2.4, 0.3, 30], [-40, 55, 1.3, 0.2, 75]]
# An island hangs below its top: look at it higher up, from further off.
ISLAND_VIEWS = [[-30, 25, 3.2, 0.6, 30], [150, 25, 3.2, 0.6, 30], [60, 10, 3.2, 0.5, 30], [-40, 55, 1.6, 0.9, 75]]
P_SUM, P_KEY = 2305843009213693951, 17179869143


def checksum(placed):
    """What terrain_probe.gd sums over the level the game stamps, voxel by voxel."""
    total = 0
    for (gx, gy, gz), (r, g, b) in placed:
        h = ((gx + 4096) * 8192 + (gy + 4096)) * 8192 + (gz + 4096)
        total = (total + (h % P_KEY) * 33554432 + (r * 65536 + g * 256 + b) * 2) % P_SUM
    return total


def ground_file(family, treatment):
    return kit.ROOT / kit.GROUND_FILES[(family, treatment)]["file"]


def gcell(tx, ty, k):
    """The Godot cell of layout tile (tx, ty) at level k: the layout's y is Godot's -z."""
    return [tx, k, -1 - ty]


def components(tiles):
    """The tiles in 4-neighbour connected groups."""
    left, groups = set(tiles), []
    while left:
        seed = left.pop()
        group, todo = {seed}, [seed]
        while todo:
            x, y = todo.pop()
            for dx, dy in SIDES.values():
                n = (x + dx, y + dy)
                if n in left:
                    left.discard(n)
                    group.add(n)
                    todo.append(n)
        groups.append(group)
    return groups


def exact_of(world):
    placed = sorted(world.items())
    xs = [p[0] for p, c in placed]
    ys = [p[1] for p, c in placed]
    zs = [p[2] for p, c in placed]
    return {"box": [min(xs), min(ys), min(zs), max(xs) + 1, max(ys) + 1, max(zs) + 1], "count": len(placed),
            "sum": str(checksum(placed))}


def write_cells(folder, res, name, stem, v, pal, levels, kinds, floor0):
    """Cuts a piece's column (voxels -> palette index) into one 16-cubed file a level."""
    for k in range(levels):
        cell = {(x, y, z - 16 * k): i for (x, y, z), i in v.items() if 16 * k <= z < 16 * k + 16}
        if not cell:
            continue
        fname = "%s_%d.vox" % (stem, k)
        write(folder / fname, (16, 16, 16), cell, pal)
        (folder / (fname + ".import")).write_text(IMPORT.format(res="%s/%s" % (res, fname)))
        kinds["%s_%s_%d" % (name, stem, k)] = {"file": "res://%s/%s" % (res, fname), "floor": floor0 and k == 0}


def suffix(treatment):
    return "" if treatment == "Base" else "_" + treatment


def delivered(files, style, part, treatment):
    """(voxels -> index, palette) of a delivered file under [files] (output/ or a dry
    run's folder): the test then places the files themselves."""
    size, vox, pal, mats = read(files / style.source / ("%s_%s%s.vox" % (STY.prefix(style.source), part,
                                                                           suffix(treatment))))
    return vox, [tuple(c) for c in pal]


def job_for(style, treatment, game, name, files=None):
    rows = style.test
    mask, tiles, extra = layout.parse(rows)
    H = len(rows)
    W = max(len(l) for l in rows)
    folder = game / "Blocks" / "Terrain" / name
    folder.mkdir(parents=True, exist_ok=True)
    res = "Blocks/Terrain/%s" % name
    kinds, pieces, world, painted, gkind = {}, [], {}, {}, {}
    L = style.levels
    floating = style.bottom is None

    def ground_kind(family):
        if family not in gkind:
            gname = "%s_G%d" % (name, len(gkind))
            fname = "G%d.vox" % len(gkind)
            shutil.copy(ground_file(family, treatment), folder / fname)
            (folder / (fname + ".import")).write_text(IMPORT.format(res=res + "/" + fname))
            kinds[gname] = {"file": "res://%s/%s" % (res, fname), "floor": True}
            gkind[family] = (gname, {p: rgb for p, (i, rgb, g) in kit.ground(family, treatment).items()})
        return gkind[family]

    lower = {}
    for tx in range(-MARGIN, W + MARGIN):
        for ty in range(-MARGIN, H + MARGIN):
            if (tx, ty) in mask:
                piece, q = layout.place(mask, extra, tx, ty)
                if piece not in painted:
                    if files:
                        v, pal = delivered(files, style, "%s_%s" % (style.name, piece), treatment)
                    else:
                        v, pal, groups = kit.paint(style, kit.build(style, piece, "Cartoon" in treatment), treatment)
                    painted[piece] = (v, pal)
                    write_cells(folder, res, name, piece, v, pal, L + 1, kinds, not floating)
                v, pal = painted[piece]
                for k in range(L + 1):
                    kind = "%s_%s_%d" % (name, piece, k)
                    if kind in kinds:
                        c = gcell(tx, ty, k)
                        pieces.append({"kind": kind, "slot": [2 * c[0], k, 2 * c[2]], "turn": q})
                vox = layout.turn_voxels({p: pal[i - 1][:3] for p, i in v.items()}, q)
            else:
                family = layout.lower_family(style, tiles[(tx, ty)]) if (tx, ty) in tiles else style.bottom
                if family is None:
                    continue
                gname, vox = ground_kind(family)
                lower[(tx, ty)] = family
                c = gcell(tx, ty, 0)
                pieces.append({"kind": gname, "slot": [2 * c[0], 0, 2 * c[2]], "turn": 0})
            for (x, y, z), rgb in vox.items():
                world[(16 * tx + x, z, -1 - (16 * ty + y))] = tuple(rgb)
    # What the rules must see.
    e = {"floors": [], "not_floors": [], "climbs": [], "blocked_steps": [], "closed": []}
    targets = []
    for (tx, ty) in sorted(mask):
        e["floors"].append(gcell(tx, ty, L + 1))
        e["not_floors"] += [gcell(tx, ty, k) for k in range(1, L + 1)]
        for side, (dx, dy) in SIDES.items():
            o = (tx + dx, ty + dy)
            if o not in mask and o in lower:
                step = [gcell(o[0], o[1], 1), gcell(tx, ty, L + 1)]
                (e["climbs"] if L == 1 else e["blocked_steps"]).append(step)
    if floating:
        # From the top of the main block, every top of it; the ridge and the pillar
        # stand apart in the void.
        main = max(components(mask), key=len)
        start_tile = min(main, key=lambda t: (t[1], t[0]))
        start = gcell(start_tile[0], start_tile[1], L + 1)
        targets = [gcell(t[0], t[1], L + 1) for t in sorted(main)]
        figure = [start_tile[0], L + 1, -1 - start_tile[1], 200]
    else:
        for (tx, ty) in sorted(lower):
            if 0 <= tx < W and 0 <= ty < H:
                e["floors"].append(gcell(tx, ty, 1))
                targets.append(gcell(tx, ty, 1))
        for (tx, ty) in sorted(mask):
            (targets if L == 1 else e["closed"]).append(gcell(tx, ty, L + 1))
        start = gcell(W // 2, -1, 1)
        figure = [W // 2, 1, 0, 200]
    e["reach"] = [start, targets]
    return {"name": name, "style": "%s:%s" % (style.source, style.name), "treatment": treatment, "kinds": kinds,
            "pieces": pieces, "expect": e, "exact": exact_of(world), "views": VIEWS, "centre": [W / 2.0, -H / 2.0],
            "extent": max(W, H), "top": L + 1, "figure": figure}


def island_job(style, island, treatment, game, name, files=None):
    """A whole island cut into the game's cells where it hangs: level 0 its lowest."""
    iname, rows, depth = island
    if files:
        v, pal = delivered(files, style, iname, treatment)
    else:
        raw, size = ISL.raw(style, rows, depth, "Cartoon" in treatment)
        v, pal, groups = kit.paint(style, raw, treatment)
    folder = game / "Blocks" / "Terrain" / name
    folder.mkdir(parents=True, exist_ok=True)
    res = "Blocks/Terrain/%s" % name
    kinds, pieces, world = {}, [], {}
    cells = {}
    for (x, y, z), i in v.items():
        cells.setdefault((x // 16, y // 16, z // 16), {})[(x % 16, y % 16, z % 16)] = i
        world[(x, z, -1 - y)] = tuple(pal[i - 1][:3])
    for (cx, cy, cz), cell in sorted(cells.items()):
        fname = "C_%d_%d_%d.vox" % (cx, cy, cz)
        write(folder / fname, (16, 16, 16), cell, pal)
        (folder / (fname + ".import")).write_text(IMPORT.format(res="%s/%s" % (res, fname)))
        kind = "%s_%d_%d_%d" % (name, cx, cy, cz)
        kinds[kind] = {"file": "res://%s/%s" % (res, fname), "floor": False}
        c = gcell(cx, cy, cz)
        pieces.append({"kind": kind, "slot": [2 * c[0], cz, 2 * c[2]], "turn": 0})
    mask, tiles, extra = layout.parse(rows)
    top = depth + style.levels + 1
    e = {"floors": [gcell(t[0], t[1], top) for t in sorted(mask)],
         "not_floors": [gcell(t[0], t[1], k) for t in sorted(mask) for k in range(1, top)],
         "climbs": [], "blocked_steps": [], "closed": []}
    start = min(mask, key=lambda t: (t[1], t[0]))
    e["reach"] = [gcell(start[0], start[1], top), [gcell(t[0], t[1], top) for t in sorted(mask)]]
    H, W = len(rows), max(len(r) for r in rows)
    return {"name": name, "style": "%s:%s" % (style.source, iname), "treatment": treatment, "kinds": kinds,
            "pieces": pieces, "expect": e, "exact": exact_of(world), "views": ISLAND_VIEWS,
            "centre": [W / 2.0, -H / 2.0], "extent": max(W, H) + 2, "top": top,
            "figure": [start[0], top, -1 - start[1], 200]}


def run(game, args):
    log = game / "_probe" / "godot.log"
    with open(log, "w") as f:
        p = subprocess.run([GODOT] + args, cwd=game, stdout=f, stderr=subprocess.STDOUT, timeout=5400)
    return p.returncode, log.read_text(errors="replace")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--game", required=True, type=Path)
    a.add_argument("--render", action="store_true")
    a.add_argument("--styles", default="")
    a.add_argument("--islands", action="store_true")
    a.add_argument("--treatments", default=",".join(kit.TREATMENTS))
    a.add_argument("--out", type=Path, default=None)
    a.add_argument("--files", type=Path, default=None, help="place the delivered files under this folder")
    args = a.parse_args()
    files = args.files.resolve() if args.files else None
    game = args.game.resolve()
    assert (game / "project.godot").exists(), "not a copy of the game's vcom folder"
    real = (kit.ROOT.parent / "VoxelXCOM" / "vcom").resolve()
    assert game != real, "give a scratch copy of the game, not the game itself"
    chosen = [s for spec in args.styles.split(",") if spec for s in STY.by_name(spec)] if args.styles else STY.STYLES
    sources = sorted({s.source for s in chosen})
    probe_dir = game / "_probe"
    probe_dir.mkdir(exist_ok=True)
    shutil.copy(HERE / "godot" / "terrain_probe.gd", probe_dir / "terrain_probe.gd")
    blocks = game / "Blocks" / "Terrain"
    if blocks.exists():
        shutil.rmtree(blocks)
    jobs = []
    for style in chosen:
        for t in args.treatments.split(","):
            name = "%s_%s_%s" % (STY.prefix(style.source), style.name, SHORT[t])
            jobs.append(job_for(style, t, game, name, files))
    if args.islands or not args.styles:
        for src in sources:
            rim = [s for s in STY.STYLES if s.source == src and s.family == "IslandRim"]
            for island in ISL.ISLANDS.get(src, []):
                for t in args.treatments.split(","):
                    name = "%s_%s_%s" % (STY.prefix(src), island[0], SHORT[t])
                    jobs.append(island_job(rim[0], island, t, game, name, files))
    out = (args.out or (probe_dir / "terrain_results")).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (probe_dir / "terrain_jobs.json").write_text(json.dumps({"jobs": jobs, "out": str(out).replace("\\", "/"),
                                                             "render": args.render}))
    print("jobs:", len(jobs))
    code, text = run(game, ["--headless", "--path", ".", "--import"])
    errors = [l for l in text.splitlines() if "ERROR" in l]
    print("import:", code, "errors:", len(errors))
    for l in errors[:10]:
        print("  ", l)
    flags = [] if args.render else ["--headless"]
    code, text = run(game, flags + ["--path", ".", "--script", "res://_probe/terrain_probe.gd", "--",
                                    str(probe_dir / "terrain_jobs.json").replace("\\", "/")])
    print(text[-1500:])
    report = json.loads((out / "report.json").read_text())
    failed = [(n, c, r["notes"]) for n, r in report.items() for c, ok in r["checks"].items() if not ok]
    print("scenes:", len(report), "failed checks:", len(failed))
    for n, c, notes in failed[:30]:
        bad = {k: v for k, v in notes.items() if isinstance(v, list) and v and k != "stamped"}
        print("  FAIL", n, c, json.dumps(bad)[:500], notes.get("stamped") if c == "stamped_exactly" else "")
    return 0 if not failed and len(report) == len(jobs) else 1


if __name__ == "__main__":
    sys.exit(main())
