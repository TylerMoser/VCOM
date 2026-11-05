"""Tests that the poke_c buildings go into VCOM cleanly, in a scratch copy of the game.

    python output/poke_c/buildings/qa/integration.py --game <copy of VoxelXCOM/vcom> [--render]

It never touches the game itself or output/: give it a copy of the game's vcom
folder (49 MB with its import cache). It cuts every building into the game's
16-cubed pieces (cut_pieces.py) under <copy>/Blocks/PokeC/, imports them, builds
test levels of grass and the cut pieces (the covered bridge assembled from two
pavilions and a span between raised banks), runs godot/building_probe.gd there,
and checks its report: what the rules see (every room's floor a tile, doors shut,
windows seen, shot and vaulted through over a solid sill, walls shut, the bridge's
walkway end to end) and, with --render, frames by day, dusk and night in the
game's own renderer, glass and all.
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
HOUSES = ["Cottage", "FlowerBoxCottage", "Manor"]
# Short names for the cut pieces' folders and kinds: Windows' paths stop at 260.
SHORT = {"Cottage": "Cot", "FlowerBoxCottage": "FBC", "Manor": "Man", "BridgePavilion": "Pav", "BridgeSpan": "Spn",
         "Base": "B", "Cartoon": "C", "CratePalette": "P", "TwoColor": "T", "Cartoon_TwoColor": "CT",
         "CratePalette_TwoColor": "PT", "Cartoon_CratePalette_TwoColor": "CPT"}


def gcell(i, j, k, cx=0, r=0):
    """The Godot cell of model tile (i, j) at level k: rows run toward -z."""
    return [cx + i, k, r - 1 - j]


def gdir(di, dj):
    """A model direction (x, y) as Godot's (x, z): the model's y is Godot's -z."""
    return [di, -dj]


def _inside_edge(t, a, b, k, F):
    """The footprint tile beside edge slot (t, a, b, k) and the way out across it."""
    if t == "ey":
        return ((a, b, k), (0, -1)) if (a, b) in F else ((a, b - 1, k), (0, 1))
    return ((a, b, k), (-1, 0)) if (a, b) in F else ((a - 1, b, k), (1, 0))


def expect_house(m, lay):
    """What the rules must see of a cut house: every tile of its footprint a floor
    under its roof; round the outside, at levels 1 and 2, every wall and closed door
    shut and every window open at its own level over a shut sill, a line of sight
    through each eye-level window and none through the walls beside them, a vault
    in through each such window and no step in anywhere else; every room reachable
    from outside; and the roof cut away from level 4."""
    F = m.footprint
    doors = {_inside_edge(*d, F) for d in m.doors}
    windows = {_inside_edge(*p["model_slot"], F) for p in lay["pieces"] if lay["kinds"][p["kind"]]["window"]}
    floors, shut, opened, sight, vaults, blocked, under = [], [], [], [], [], [], []
    for (i, j) in sorted(F):
        floors.append(gcell(i, j, 1))
        under.append(gcell(i, j, 1))
        for (di, dj) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (i + di, j + dj) in F:
                continue
            for k in (1, 2):
                edge = ((i, j, k), (di, dj))
                if edge in windows:
                    opened.append([gcell(i, j, k), gdir(di, dj)])
                    if k == 2:
                        sight.append([gcell(i + di, j + dj, 2), gcell(i, j, 2), True])
                        vaults.append([gcell(i + di, j + dj, 1), gcell(i, j, 1)])
                else:
                    shut.append([gcell(i, j, k), gdir(di, dj)])
                    if k == 2 and edge not in doors:
                        sight.append([gcell(i + di, j + dj, 2), gcell(i, j, 2), False])
            if ((i, j, 2), (di, dj)) not in windows:
                blocked.append([gcell(i + di, j + dj, 1), gcell(i, j, 1)])
    for (cell, d) in sorted(windows):
        if cell[2] > 2:
            opened.append([gcell(*cell), gdir(*d)])
    start = gcell(min(i for i, j in F), min(j for i, j in F) - 3, 1)
    return {"floors": floors, "shut": shut, "open": opened, "sight": sight, "vaults": vaults,
            "blocked_steps": blocked, "reach": [start, floors], "under": under, "cut": 4}


def expect_bridge():
    """What the rules must see of the bridge (pavilion x 0-4, span 5-7, pavilion
    8-12, rows z -1 and -2, banks beyond): its walkway a floor end to end at level 4,
    shut along both sides (the rails, the pavilions' walls), crossable bank to bank,
    and under the pavilions' roofs."""
    floors, shut, under = [], [], []
    for x in range(-1, 14):
        for z in (-1, -2):
            floors.append([x, 4, z])
    for x in range(0, 13):
        pav = x < 5 or x > 7
        for k in ((4, 5, 6) if pav else (4,)):
            shut.append([[x, k, -1], [0, 1]])
            shut.append([[x, k, -2], [0, -1]])
        if pav:
            under += [[x, 4, -1], [x, 4, -2]]
    return {"floors": floors, "shut": shut, "open": [], "sight": [], "vaults": [], "blocked_steps": [],
            "reach": [[-2, 4, -1], [[14, 4, -1], [14, 4, -2], [6, 4, -1]]], "under": under}


# Render views: yaw, pitch, distance (times the building's size in tiles), height
# looked at (a share of its height), field of view, and a level to cut the view
# away from. The fifth is the game's own camera: 55 degrees down, 75 of view.
HOUSE_VIEWS = [[-30, 32, 3.4, 0.42, 30], [150, 32, 3.4, 0.42, 30], [30, 32, 3.4, 0.42, 30], [-150, 32, 3.4, 0.42, 30],
               [-40, 55, 1.4, 0.25, 75], [-30, 62, 3.2, 0.2, 30, 4]]
BRIDGE_VIEWS = [[-20, 24, 2.7, 0.45, 30], [160, 24, 2.7, 0.45, 30], [-40, 55, 0.85, 0.3, 75]]
PIECE_VIEWS = [[-30, 28, 3.2, 0.45, 30], [150, 28, 3.2, 0.45, 30], [30, 28, 3.2, 0.45, 30], [-150, 28, 3.2, 0.45, 30],
               [-40, 55, 1.3, 0.35, 75], [-30, 62, 3.0, 0.3, 30, 7]]


def expect_piece(width, pavilion):
    """A lone bridge piece, [width] tiles long from x 0, rows z -1 and -2: its walkway
    a floor at level 4, shut along both sides (walls three levels high for a
    pavilion, a rail a level high for a span), and a pavilion's under its roof."""
    floors, shut, under = [], [], []
    for x in range(width):
        for z in (-1, -2):
            floors.append([x, 4, z])
            if pavilion:
                under.append([x, 4, z])
        for k in ((4, 5, 6) if pavilion else (4,)):
            shut.append([[x, k, -1], [0, 1]])
            shut.append([[x, k, -2], [0, -1]])
    e = {"floors": floors, "shut": shut, "open": [], "sight": [], "vaults": [], "blocked_steps": [], "under": under}
    if pavilion:
        e["cut"] = 7
    return e


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


def placed_voxels(m, style, cx, r, dx=0):
    """The model's voxels where the game stamps them, the building's tile (0, 0) in
    cell (cx, ., r - 1): Godot x = x - 8 + 16 cx, y = z, z = 16 r + 7 - y."""
    pal, _ = palettes.palette_of(style)
    out = []
    for (x, y, z), label in m.v.items():
        c = pal[palettes.paint(style, label) - 1]
        out.append(((x - 8 + 16 * cx + dx, z, 16 * r + 7 - y), c[:3], 1 if palettes.LABELS[label][1] == "glass" else 0))
    return out


def merged(lists):
    """Several placed buildings as the level stamps them, a later one winning where
    two put a voxel (the pavilions' end walls and the span's piers meet)."""
    at = {}
    for placed in lists:
        for p in placed:
            at[p[0]] = p
    return list(at.values())


def exact(placed):
    xs = [p[0][0] for p in placed]
    ys = [p[0][1] for p in placed]
    zs = [p[0][2] for p in placed]
    return {"box": [min(xs), min(ys), min(zs), max(xs) + 1, max(ys) + 1, max(zs) + 1],
            "count": len(placed), "sum": str(checksum(placed))}


def scenes(game, styles):
    """Cuts every family in [styles], and lays out one test scene for each house and
    treatment and one bridge per treatment."""
    out = []
    blocks = game / "Blocks" / "PokeC"
    if blocks.exists():
        shutil.rmtree(blocks)
    for style in styles:
        cartoon = "Cartoon" in style
        for kind in HOUSES:
            m = sculpt.build(kind, cartoon)
            short = "%s_%s" % (SHORT[kind], SHORT[style])
            lay = cut(m, style, blocks / short, cx=0, r=0, family=short, res_prefix="Blocks/PokeC")
            figure = {"Cottage": [0, 1, 1, 200], "FlowerBoxCottage": [0, 1, 1, 200], "Manor": [3, 1, 1, 200]}[kind]
            out.append({"name": "%s_%s" % (kind, style), "kind": kind, "style": style, "layouts": [lay],
                        "house": True, "expect": expect_house(m, lay), "views": HOUSE_VIEWS, "figure": figure,
                        "exact": exact(placed_voxels(m, style, 0, 0))})
        pav = sculpt.build("BridgePavilion", cartoon)
        spn = sculpt.build("BridgeSpan", cartoon)
        fam_p, fam_s = "Pav_%s" % SHORT[style], "Spn_%s" % SHORT[style]
        left = cut(pav, style, blocks / fam_p, cx=0, r=0, family=fam_p)
        middle = cut(spn, style, blocks / fam_s, cx=5, r=0, family=fam_s)
        right = dict(left)
        right["pieces"] = [dict(p, slot=[p["slot"][0] + 16, p["slot"][1], p["slot"][2]]) for p in left["pieces"]]
        right["footprint"] = [[c[0] + 8, c[1]] for c in left["footprint"]]
        out.append({"name": "Bridge_%s" % style, "kind": "Bridge", "style": style, "layouts": [left, middle, right],
                    "house": False, "expect": expect_bridge(), "views": BRIDGE_VIEWS, "figure": [6, 4, -2, 160],
                    "exact": exact(merged([placed_voxels(pav, style, 0, 0), placed_voxels(spn, style, 5, 0),
                                           placed_voxels(pav, style, 0, 0, dx=128)]))})
        out.append({"name": "BridgePavilion_%s" % style, "kind": "BridgePavilion", "style": style, "layouts": [left],
                    "house": False, "banks": False, "expect": expect_piece(5, True), "views": PIECE_VIEWS,
                    "figure": [2, 4, -2, 160], "exact": exact(placed_voxels(pav, style, 0, 0))})
        out.append({"name": "BridgeSpan_%s" % style, "kind": "BridgeSpan", "style": style,
                    "layouts": [dict(middle, pieces=[dict(p, slot=[p["slot"][0] - 10, p["slot"][1], p["slot"][2]])
                                                     for p in middle["pieces"]],
                                     footprint=[[c[0] - 5, c[1]] for c in middle["footprint"]])],
                    "house": False, "banks": False, "expect": expect_piece(3, False), "views": PIECE_VIEWS,
                    "figure": [1, 4, -2, 160], "exact": exact(placed_voxels(spn, style, 0, 0))})
    return out


def run(game, args):
    log = game / "_probe" / "godot.log"
    cmd = [GODOT] + args
    with open(log, "w") as f:
        p = subprocess.run(cmd, cwd=game, stdout=f, stderr=subprocess.STDOUT, timeout=3000)
    return p.returncode, log.read_text(errors="replace")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--game", required=True, type=Path)
    a.add_argument("--render", action="store_true")
    a.add_argument("--styles", default=",".join(STYLES))
    a.add_argument("--out", type=Path, default=None)
    args = a.parse_args()
    game = args.game.resolve()
    assert (game / "project.godot").exists(), "not a copy of the game's vcom folder"
    real = (HERE.parents[4] / "VoxelXCOM" / "vcom").resolve()
    assert game != real, "give a scratch copy of the game, not the game itself"
    probe_dir = game / "_probe"
    probe_dir.mkdir(exist_ok=True)
    shutil.copy(HERE / "godot" / "building_probe.gd", probe_dir / "building_probe.gd")
    jobs = scenes(game, args.styles.split(","))
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
                failed.append((name, check))
    print("scenes:", len(report), "failed checks:", len(failed))
    for f in failed[:40]:
        print("  FAIL", f)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
