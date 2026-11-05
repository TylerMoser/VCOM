"""Reads every terrain file whole through VCOM's own importer, in a scratch copy of
the game (never the game itself): writes <out> (default output/terrain/qa/whole-import.json).
    python qa/whole_import.py --game <copy of VoxelXCOM/vcom> [--root <output/ or a dry run>] [--out <json>]"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import kit  # noqa: E402

GODOT = r"C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe"


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--game", required=True, type=Path)
    a.add_argument("--root", type=Path, default=kit.ROOT / "output")
    a.add_argument("--out", type=Path, default=None)
    args = a.parse_args()
    game, root = args.game.resolve(), args.root.resolve()
    assert (game / "project.godot").exists(), "not a copy of the game's vcom folder"
    assert game != (kit.ROOT.parent / "VoxelXCOM" / "vcom").resolve(), "a scratch copy, not the game"
    out = (args.out or (root / "terrain" / "qa" / "whole-import.json")).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    rows = json.loads((root / "terrain" / "manifest.json").read_text(encoding="utf-8"))["files"]
    lst = {"models": [{"file": r["file"], "voxels": r["voxels"], "glass_voxels": 0,
                       "occupied_min": r["occupied_min"], "occupied_max": r["occupied_max"]} for r in rows]}
    probe = game / "_probe"
    probe.mkdir(exist_ok=True)
    shutil.copy(HERE / "godot" / "whole_import.gd", probe / "whole_import.gd")
    (probe / "whole_list.json").write_text(json.dumps(lst))
    with open(probe / "whole.log", "w") as f:
        subprocess.run([GODOT, "--headless", "--path", ".", "--script", "res://_probe/whole_import.gd", "--",
                        str(probe / "whole_list.json").replace("\\", "/"), str(root).replace("\\", "/"),
                        str(out).replace("\\", "/")], cwd=game, stdout=f, stderr=subprocess.STDOUT, timeout=7200)
    d = json.loads(out.read_text())
    keys = ("read", "voxels_match", "mesh", "grounded", "size_match")
    bad = {f: r for f, r in d.items() if not all(r.get(k) for k in keys) or r.get("glass")}
    print("imported:", len(d), "of", len(rows), "failing:", len(bad))
    for f, r in list(bad.items())[:10]:
        print("  ", f, r)
    return 1 if bad or len(d) != len(rows) else 0


if __name__ == "__main__":
    sys.exit(main())
