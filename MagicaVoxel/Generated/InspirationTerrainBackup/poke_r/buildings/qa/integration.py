"""Tests that the poke_r buildings go into VCOM cleanly, in a scratch copy of the
game (poke_b/game_buildings/qa/integration.py, for these buildings).

    python output/poke_r/buildings/qa/integration.py --game <copy of VoxelXCOM/vcom> [--render]

It never touches the game itself or output/: give it a copy of the game's vcom
folder. It cuts every building into the game's 16-cubed pieces (cut_pieces.py)
under <copy>/Blocks/PokeR/, imports them, builds a test level of grass and the cut
pieces for each building and treatment, runs godot/building_probe.gd there, and
checks its report: what the rules see of every storey (its floor a tile at its
level under the roof; round it, at the two levels a unit fills, every wall, sill
and closed door shut and every window open; a line of sight through each window
at the eye and none through the walls; a vault in over each sill, or a climb in
from a level below where the glass reaches the floor, and no step in anywhere
else), the stairs a level a tile, every storey drawn with a way in reachable from
the street and every one without (the user's choice) closed off, the view cut
away at each storey, and the level the game stamps the model voxel for voxel.
With --render, frames by day, dusk and night in the game's own renderer.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import palettes  # noqa: E402
import sculpt  # noqa: E402
from cut_pieces import cut  # noqa: E402

GODOT = r"C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe"
STYLES = ["Base", "Cartoon", "CratePalette", "TwoColor", "Cartoon_TwoColor", "CratePalette_TwoColor",
          "Cartoon_CratePalette_TwoColor"]
KINDS = ['RedHouse', 'Shop']
# Short names for the cut pieces' folders and kinds: Windows' paths stop at 260.
SHORT = {"RedHouse": "Red", "Shop": "Shp",
         "Base": "B", "Cartoon": "C", "CratePalette": "P", "TwoColor": "T", "Cartoon_TwoColor": "CT",
         "CratePalette_TwoColor": "PT", "Cartoon_CratePalette_TwoColor": "CPT"}
DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def gcell(i, j, k, cx=0, r=0):
    """The Godot cell of model tile (i, j) at level k: rows run toward -z."""
    return [cx + i, k, r - 1 - j]


def gdir(di, dj):
    """A model direction (x, y) as Godot's (x, z): the model's y is Godot's -z."""
    return [di, -dj]


def edge_slot(i, j, di, dj, k):
    """The cut's slot of the edge of tile (i, j) toward (di, dj) at level k."""
    if di == -1:
        return ("ex", i, j, k)
    if di == 1:
        return ("ex", i + 1, j, k)
    if dj == -1:
        return ("ey", i, j, k)
    return ("ey", i, j + 1, k)


def expect_house(m, lay):
    """What the rules must see of a cut building, from what the sculptor says of it
    (Model.storeys, stairs, climbs) and which pieces the cut found to be windows."""
    F = m.footprint
    windows = {tuple(p["model_slot"]) for p in lay["pieces"] if lay["kinds"][p["kind"]]["window"]}
    e = {"floors": [], "shut": [], "open": [], "sight": [], "vaults": [], "climbs": [], "blocked_steps": [],
         "under": [], "cuts": [], "closed": [], "walks": []}
    targets = []
    climbs = {(tuple(a), tuple(b)) for a, b in m.climbs}
    for st in m.storeys:
        s, T, entry = st["stand"], st["tiles"], st["entry"]
        e["cuts"].append(st["cut"])
        for (i, j) in sorted(T):
            e["floors"].append(gcell(i, j, s))
            e["under"].append(gcell(i, j, s))
            (targets if entry else e["closed"]).append(gcell(i, j, s))
            for (di, dj) in DIRS:
                out = (i + di, j + dj)
                if out in T:
                    continue
                if entry == "walk":
                    # A structure walked through (the gate): open all round at the two
                    # levels a unit fills, seen through, and stepped into from the ground.
                    for k in (s, s + 1):
                        e["open"].append([gcell(i, j, k), gdir(di, dj)])
                    e["sight"].append([gcell(*out, s + 1), gcell(i, j, s + 1), True])
                    e["walks"].append([gcell(*out, 1), gcell(i, j, s)])
                    continue
                for k in (s, s + 1):
                    if edge_slot(i, j, di, dj, k) in windows:
                        e["open"].append([gcell(i, j, k), gdir(di, dj)])
                    else:
                        e["shut"].append([gcell(i, j, k), gdir(di, dj)])
                e["sight"].append([gcell(*out, s + 1), gcell(i, j, s + 1), edge_slot(i, j, di, dj, s + 1) in windows])
                if out in F or entry not in ("vault", "climb"):
                    continue
                # From the street (level 1) in: a vault over the sill (level s) through
                # the window above it, or a climb a level up through glass at both levels.
                if entry == "vault":
                    opened = edge_slot(i, j, di, dj, s + 1) in windows and edge_slot(i, j, di, dj, s) not in windows
                else:
                    opened = all(edge_slot(i, j, di, dj, k) in windows for k in (s, s + 1))
                step = [gcell(*out, 1), gcell(i, j, s)]
                if opened:
                    e["vaults" if entry == "vault" else "climbs"].append(step)
                else:
                    e["blocked_steps"].append(step)
    for (i, j), s in sorted(m.stairs.items()):
        e["floors"].append(gcell(i, j, s))
        targets.append(gcell(i, j, s))
        # No step from the stair into a storey but the climbs drawn.
        for (di, dj) in DIRS:
            for st in m.storeys:
                if (i + di, j + dj) in st["tiles"] and -2 <= st["stand"] - s <= 1:
                    a, b = (i, j, s), (i + di, j + dj, st["stand"])
                    if (a, b) not in climbs:
                        e["blocked_steps"].append([gcell(*a[:2], a[2]), gcell(*b[:2], b[2])])
    for a, b in m.climbs:
        e["climbs"].append([gcell(a[0], a[1], a[2]), gcell(b[0], b[1], b[2])])
    start = gcell(min(i for i, j in F), min(j for i, j in F) - 3, 1)
    e["reach"] = [start, targets]
    return e


# Render views: yaw, pitch, distance (times the building's size in tiles), height
# looked at (a share of its height), field of view, and a level to cut the view
# away from. The fifth is the game's own camera: 55 degrees down, 75 of view.
HOUSE_VIEWS = [[-30, 30, 3.0, 0.42, 30], [150, 30, 3.0, 0.42, 30], [30, 30, 3.0, 0.42, 30], [-150, 30, 3.0, 0.42, 30],
               [-40, 55, 1.6, 0.35, 75]]


def views_for(m):
    return HOUSE_VIEWS + [[-30, 60, 3.0, 0.2, 30, st["cut"]] for st in m.storeys]


P_SUM, P_KEY = 2305843009213693951, 17179869143


def checksum(placed):
    """What building_probe.gd sums over the level the game stamps: for every voxel
    of [placed] ((gx, gy, gz), rgb, glass) its place, colour and glass, so a piece
    turned, put in the wrong slot, or a voxel lost or added anywhere changes it."""
    total = 0
    for (gx, gy, gz), (r, g, b), glass in placed:
        h = ((gx + 4096) * 8192 + (gy + 4096)) * 8192 + (gz + 4096)
        total = (total + (h % P_KEY) * 33554432 + ((r * 65536 + g * 256 + b) * 2 + glass)) % P_SUM
    return total


def placed_voxels(m, kind, style, cx, r):
    """The model's voxels where the game stamps them, the building's tile (0, 0) in
    cell (cx, ., r - 1): Godot x = x - 8 + 16 cx, y = z, z = 16 r + 7 - y."""
    pal, _ = palettes.palette_of(style, kind)
    out = []
    for (x, y, z), label in m.v.items():
        c = pal[palettes.paint(style, label, kind) - 1]
        out.append(((x - 8 + 16 * cx, z, 16 * r + 7 - y), c[:3], 1 if palettes.LABELS[label][1] == "glass" else 0))
    return out


def exact(placed):
    xs = [p[0][0] for p in placed]
    ys = [p[0][1] for p in placed]
    zs = [p[0][2] for p in placed]
    return {"box": [min(xs), min(ys), min(zs), max(xs) + 1, max(ys) + 1, max(zs) + 1],
            "count": len(placed), "sum": str(checksum(placed))}


def scenes(game, styles, kinds, wanted=None):
    """Cuts every family in [styles] (only the scenes [wanted], if given), and lays
    out one test scene for each building and treatment."""
    out = []
    blocks = game / "Blocks" / "PokeR"
    if blocks.exists():
        shutil.rmtree(blocks)
    for style in styles:
        cartoon = "Cartoon" in style
        for kind in kinds:
            if wanted and "%s_%s" % (kind, style) not in wanted:
                continue
            m = sculpt.build(kind, cartoon)
            short = "%s_%s" % (SHORT[kind], SHORT[style])
            lay = cut(m, kind, style, blocks / short, cx=0, r=0, family=short, res_prefix="Blocks/PokeR")
            fi, fj, fk, yaw = m.figure
            out.append({"name": "%s_%s" % (kind, style), "kind": kind, "style": style, "layouts": [lay],
                        "house": True, "expect": expect_house(m, lay), "views": views_for(m),
                        "ground_under": bool(getattr(m, "ground_under", False)),
                        "figure": gcell(fi, fj, fk) + [yaw], "exact": exact(placed_voxels(m, kind, style, 0, 0))})
    return out


def run(game, args):
    log = game / "_probe" / "godot.log"
    cmd = [GODOT] + args
    with open(log, "w") as f:
        p = subprocess.run(cmd, cwd=game, stdout=f, stderr=subprocess.STDOUT, timeout=5400)
    return p.returncode, log.read_text(errors="replace")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--game", required=True, type=Path)
    a.add_argument("--render", action="store_true")
    a.add_argument("--styles", default=",".join(STYLES))
    a.add_argument("--kinds", default=",".join(KINDS))
    a.add_argument("--scenes", default="", help="only these scenes (Kind_Style, comma separated)")
    a.add_argument("--out", type=Path, default=None)
    args = a.parse_args()
    game = args.game.resolve()
    assert (game / "project.godot").exists(), "not a copy of the game's vcom folder"
    real = (HERE.parents[4] / "VoxelXCOM" / "vcom").resolve()
    assert game != real, "give a scratch copy of the game, not the game itself"
    probe_dir = game / "_probe"
    probe_dir.mkdir(exist_ok=True)
    shutil.copy(HERE / "godot" / "building_probe.gd", probe_dir / "building_probe.gd")
    wanted = set(args.scenes.split(",")) if args.scenes else None
    jobs = scenes(game, args.styles.split(","), args.kinds.split(","), wanted)
    assert not wanted or len(jobs) == len(wanted), "unknown scene names"
    out = (args.out or (game / "_probe" / "results")).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (probe_dir / "jobs.json").write_text(json.dumps({"jobs": jobs, "out": str(out).replace("\\", "/"),
                                                      "render": args.render}, indent=0))
    code, text = run(game, ["--headless", "--path", ".", "--import"])
    errors = [l for l in text.splitlines() if "ERROR" in l or "SCRIPT ERROR" in l]
    print("import:", code, "errors:", len(errors))
    for l in errors[:10]:
        print("  ", l)
    flags = [] if args.render else ["--headless"]
    code, text = run(game, flags + ["--path", ".", "--script", "res://_probe/building_probe.gd", "--",
                                    str(probe_dir / "jobs.json").replace("\\", "/")])
    print(text[-3000:])
    report = json.loads((out / "report.json").read_text())
    failed = []
    for name, r in report.items():
        for check, ok in r["checks"].items():
            if not ok:
                failed.append((name, check, r["notes"]))
    print("scenes:", len(report), "failed checks:", len(failed))
    for name, check, notes in failed[:40]:
        bad = {k: v for k, v in notes.items() if isinstance(v, list) and v and k not in ("stamped",)}
        print("  FAIL", name, check, json.dumps(bad)[:600])
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
