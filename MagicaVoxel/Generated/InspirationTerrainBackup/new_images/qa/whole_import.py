"""Reads every new_1 and new_2 file whole through VCOM's own importer, in a scratch
copy of the game (never the game itself): that it reads, its voxel count, its
glass (the cottage's windows alone have any), and a mesh at the blocks' Scale
0.0625, grounded and as big as its voxels say. Writes qa/whole-import.json.

    python output/new_images/qa/whole_import.py --game <copy of VoxelXCOM/vcom> [--files <folder>] [--out <json>]

(the terrain collection's qa/whole_import.py, which has its probe from the poke_u
buildings, for these files)"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lib"))
from voxlib import read  # noqa: E402

GODOT = r"C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe"
REAL = Path(r"C:/Users/tandm/Documents/Projects/VoxelXCOM/vcom")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--game", required=True, type=Path)
    a.add_argument("--files", type=Path, default=HERE.parents[1])
    a.add_argument("--out", type=Path, default=HERE / "whole-import.json")
    args = a.parse_args()
    game, root = args.game.resolve(), args.files.resolve()
    assert (game / "project.godot").exists(), "not a copy of the game's vcom folder"
    assert game != REAL.resolve(), "a scratch copy, not the game"
    names = []
    for rel in ("new_1/elements/manifest.json", "new_2/elements/manifest.json"):
        names += [rel.split("/")[0] + "/" + r["file"] for r in json.loads((root / rel).read_text(encoding="utf-8"))["files"]]
    names += ["new_1/" + r["file"] for r in
              json.loads((root / "new_1" / "buildings" / "manifest.json").read_text(encoding="utf-8"))["models"]]
    rows = []
    for rel in names:
        size, vox, pal, mats = read(root / rel)
        glass = {i for i, m in mats.items() if m.get("_type") == "_glass"}
        rows.append({"file": rel, "voxels": len(vox), "glass_voxels": sum(1 for v in vox.values() if v in glass),
                     "occupied_min": [min(p[k] for p in vox) for k in range(3)],
                     "occupied_max": [max(p[k] for p in vox) for k in range(3)]})
    probe = game / "_probe"
    probe.mkdir(exist_ok=True)
    shutil.copy(HERE / "godot" / "whole_import.gd", probe / "whole_import.gd")
    (probe / "whole_list.json").write_text(json.dumps({"models": rows}))
    out = args.out.resolve()
    with open(probe / "whole.log", "w") as f:
        subprocess.run([GODOT, "--headless", "--path", ".", "--script", "res://_probe/whole_import.gd", "--",
                        str(probe / "whole_list.json").replace("\\", "/"), str(root).replace("\\", "/"),
                        str(out).replace("\\", "/")], cwd=game, stdout=f, stderr=subprocess.STDOUT, timeout=7200)
    d = json.loads(out.read_text())
    keys = ("read", "voxels_match", "mesh", "grounded", "size_match", "glass_voxels_match")
    bad = {f: r for f, r in d.items() if not all(r.get(k) for k in keys)}
    glassy = sorted(f for f, r in d.items() if r.get("glass"))
    print("imported:", len(d), "of", len(rows), "failing:", len(bad), "with glass:", len(glassy))
    for f, r in list(bad.items())[:10]:
        print("  ", f, {k: r.get(k) for k in keys})
    return 1 if bad or len(d) != len(rows) else 0


if __name__ == "__main__":
    sys.exit(main())
