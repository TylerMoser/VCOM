"""Draws the collection's previews from the files on disk (never from memory):
for each image, output/<image>/terrain/previews/:
  <Style>_layout.png      the style's standard layout assembled from its files, in
                          3D, and in the image's own projection beside the art it
                          was measured from, at one scale;
  <Style>_pieces.png      every piece on its own, Base and Cartoon;
  <Style>_treatments.png  the layout in all seven treatments;
  <Island>.png            each whole island, all seven treatments;
and output/terrain/overview.png, every style's layout side by side.
    python compose_previews.py [--root DIR] [--only <image>]
"""
import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fastview  # noqa: E402
import kit  # noqa: E402
import layout  # noqa: E402
import styles as STY  # noqa: E402
from voxlib import read  # noqa: E402

FONT = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
SMALL = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
BG = (240, 240, 235)


def load(path):
    size, vox, pal, mats = read(path)
    return {p: pal[i - 1][:3] for p, i in vox.items()}


def suffix(t):
    return "" if t == "Base" else "_" + t


def assembled(root, st, treatment):
    """The style's standard layout put together from its files on disk."""
    mask, tiles, extra = layout.parse(st.test)
    pre = STY.prefix(st.source)
    cache, world = {}, {}
    for (tx, ty), ch in tiles.items():
        if (tx, ty) in mask:
            piece, q = layout.place(mask, extra, tx, ty)
            if piece not in cache:
                cache[piece] = load(root / st.source / ("%s_%s_%s%s.vox" % (pre, st.name, piece, suffix(treatment))))
            vox = layout.turn_voxels(cache[piece], q)
        else:
            fam = layout.lower_family(st, ch)
            if fam is None:
                continue
            vox = {p: rgb for p, (i, rgb, g) in kit.ground(fam, treatment).items()}
        for (x, y, z), c in vox.items():
            world[(16 * tx + x, 16 * ty + y, z)] = c
    return world


def row_of(images, title, gap=16):
    h = max(i.height for i in images) + 24
    w = sum(i.width for i in images) + gap * (len(images) - 1)
    im = Image.new("RGB", (max(w, 400), h), BG)
    ImageDraw.Draw(im).text((4, 2), title, font=FONT, fill=(0, 0, 0))
    x = 0
    for i in images:
        im.paste(i, (x, 24))
        x += i.width + gap
    return im


def stack(rows):
    W = max(r.width for r in rows)
    im = Image.new("RGB", (W, sum(r.height for r in rows)), BG)
    y = 0
    for r in rows:
        im.paste(r, (0, y))
        y += r.height
    return im


def labelled(im, text):
    out = Image.new("RGB", (im.width, im.height + 18), BG)
    out.paste(im, (0, 18))
    ImageDraw.Draw(out).text((3, 1), text, font=SMALL, fill=(0, 0, 0))
    return out


def grid(images, cols):
    w = max(i.width for i in images)
    h = max(i.height for i in images)
    rows = (len(images) + cols - 1) // cols
    im = Image.new("RGB", (cols * (w + 10), rows * (h + 10)), BG)
    for k, i in enumerate(images):
        im.paste(i, ((k % cols) * (w + 10), (k // cols) * (h + 10)))
    return im


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--root", type=Path, default=kit.ROOT / "output")
    a.add_argument("--only", default="")
    args = a.parse_args()
    root = args.root.resolve()
    manifest = json.loads((root / "terrain" / "manifest.json").read_text(encoding="utf-8"))
    overview = []
    for st in STY.STYLES:
        if args.only and st.source != args.only:
            continue
        out = root / st.source / "terrain" / "previews"
        out.mkdir(parents=True, exist_ok=True)
        base = assembled(root, st, "Base")
        a3d = fastview.view3d(base, -28, 40, 2.4)
        ob = fastview.oblique(base, st.K, 4.0)
        art = Image.open(kit.ROOT / st.image).convert("RGB").crop(st.art)
        s = 4.0 * 16 / st.ppt
        art = art.resize((max(1, int(art.width * s)), max(1, int(art.height * s))), Image.NEAREST)
        title = "%s %s: %s, %d level%s, K %g; 3D, the image's projection, the art at the same scale" % (
            st.source, st.name, st.family, st.levels, "" if st.levels == 1 else "s", st.K)
        row_of([a3d, ob, art], title).save(out / ("%s_layout.png" % st.name))
        overview.append(labelled(fastview.view3d(base, -28, 40, 1.3), "%s %s" % (st.source, st.name)))
        pieces = []
        for piece in st.pieces:
            for t in ("Base", "Cartoon"):
                f = root / st.source / ("%s_%s_%s%s.vox" % (STY.prefix(st.source), st.name, piece, suffix(t)))
                pieces.append(labelled(fastview.view3d(load(f), -30, 30, 4.0), "%s %s" % (piece, t)))
        stack([row_of([grid(pieces, 6)], "%s %s: every piece, Base and Cartoon" % (st.source, st.name))]).save(
            out / ("%s_pieces.png" % st.name))
        tr = [labelled(fastview.view3d(assembled(root, st, t), -28, 40, 1.4), t) for t in kit.TREATMENTS]
        row_of([grid(tr, 4)], "%s %s: the seven treatments" % (st.source, st.name)).save(
            out / ("%s_treatments.png" % st.name))
        print(st.source, st.name)
    for src, items in manifest["islands"].items():
        if args.only and src != args.only:
            continue
        out = root / src / "terrain" / "previews"
        out.mkdir(parents=True, exist_ok=True)
        for isl in items:
            ims = []
            for t in kit.TREATMENTS:
                f = root / src / ("%s_%s%s.vox" % (STY.prefix(src), isl["name"], suffix(t)))
                ims.append(labelled(fastview.view3d(load(f), -30, 18, 3.0), t))
            row_of([grid(ims, 4)], "%s %s: a whole island, the seven treatments" % (src, isl["name"])).save(
                out / ("%s.png" % isl["name"]))
            print(src, isl["name"])
    if overview and not args.only:
        g = grid(overview, 6)
        g.save(root / "terrain" / "overview.png")
        print("overview", g.size)


if __name__ == "__main__":
    main()
