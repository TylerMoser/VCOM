"""Lays new_1's ground tiles out together, as a map would, to check that they join:
a field of meadow with a patch of the sandy path and a patch of the light meadow in
it, each edged by its Edge and InnerCorner pieces turned as the game turns them
(VoxelVolume.turned(): a quarter turn takes MagicaVoxel's (x, y) to (15 - y, x)),
with an OuterCorner where the patch's edge turns in. Writes
output/new_1/elements/previews/ground_layout_<Treatment>.png.

    python output/new_images/ground_layout.py [--files <folder with the tiles>] [--out <png folder>]"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import fastview  # noqa: E402
from voxlib import read  # noqa: E402

# The map, a tile a letter: M meadow, S sand, L light meadow; the edge and corner
# pieces are worked out from the neighbours.
MAP = ["MMMMMMMM",
       "MSSSMMMM",
       "MSSSMLLM",
       "MSSSMLLM",
       "MMSSMMMM",
       "MMSSMMMM",
       "MMMMMMMM"]


def turn(vox, q):
    out = dict(vox)
    for _ in range(q % 4):
        out = {(15 - y, x, z): v for (x, y, z), v in out.items()}
    return out


def piece_for(grid, i, j, inner):
    """(tile name, quarter turns) for map cell (i, j): a core tile, or the edge or
    corner of the meadow round a patch of [inner] ('S' or 'L')."""
    H, W = len(grid), len(grid[0])
    me = grid[j][i]
    if me != "M":
        return ("SandPath" if me == "S" else "LightMeadow"), 0

    def at(di, dj):
        ii, jj = i + di, j + dj
        return 0 <= ii < W and 0 <= jj < H and grid[jj][ii] == inner

    # rows run down the map, y up the tile: a cell below on the map is -y
    e, w, s, n = at(1, 0), at(-1, 0), at(0, 1), at(0, -1)
    kind = "Path" if inner == "S" else "LightPatch"
    sides = [q for flag, q in ((e, 0), (n, 1), (w, 2), (s, 3)) if flag]
    if len(sides) == 1:
        # Edge: A (meadow) on local x < 8, B beyond it, turned so B faces the patch
        return kind + "Edge", sides[0]
    if len(sides) >= 2:
        # OuterCorner: A only in x < 8, y < 8, where the patch's edge turns in round this cell
        for (a, b, q) in ((s, w, 2), (s, e, 3), (n, e, 0), (n, w, 1)):
            if a and b:
                return kind + "OuterCorner", q
    if not sides:
        # InnerCorner: B only in x >= 8, y >= 8, the patch diagonal to the cell
        for (di, dj, q) in ((1, -1, 0), (-1, -1, 1), (-1, 1, 2), (1, 1, 3)):
            if at(di, dj):
                return kind + "InnerCorner", q
    return "Meadow", 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", type=Path, default=HERE.parent / "new_1")
    ap.add_argument("--out", type=Path, default=HERE.parent / "new_1" / "elements" / "previews")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
    for treatment in ("", "_Cartoon", "_TwoColor"):
        world = {}
        H = len(MAP)
        for j in range(H):
            for i in range(len(MAP[0])):
                near = [MAP[jj][ii] for jj in range(max(0, j - 1), min(H, j + 2))
                        for ii in range(max(0, i - 1), min(len(MAP[0]), i + 2))]
                inner = "S" if "S" in near else "L"
                name, q = piece_for(MAP, i, j, inner)
                size, vox, pal, mats = read(args.files / ("New1_Ground_%s%s.vox" % (name, treatment)))
                for (x, y, z), c in turn(vox, q).items():
                    world[(i * 16 + x, (H - 1 - j) * 16 + y, z)] = pal[c - 1][:3]
        a = fastview.view3d(world, 0, 90, 2.0)
        b = fastview.view3d(world, -28, 40, 2.0)
        im = Image.new("RGB", (a.width + b.width + 30, max(a.height, b.height) + 30), (240, 240, 236))
        im.paste(a, (10, 30))
        im.paste(b, (a.width + 20, 30))
        ImageDraw.Draw(im).text((10, 6), "new_1 ground tiles laid out together%s: a sand patch and a light-meadow "
                                         "patch in the meadow" % (" (" + treatment[1:] + ")" if treatment else ""),
                                font=font, fill=(0, 0, 0))
        dest = args.out / ("ground_layout_%s.png" % (treatment[1:] or "Base"))
        im.save(dest)
        print(dest, im.size)


if __name__ == "__main__":
    main()
