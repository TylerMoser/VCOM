"""Review sheets of every new_1 and new_2 family, drawn from the files on disk: the
image's crop of each (its first region, or its sprite), then Base, Cartoon,
TwoColor and CratePalette from one angle; new_1's figures and props also from the
back. Writes output/new_X/elements/previews/review_NN.png.

    python output/new_images/review.py [--files <folder holding new_1/ and new_2/>] [--out <folder>]"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "lib"))
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import fastview  # noqa: E402
from voxlib import read  # noqa: E402

W = Path(r"C:/Users/tandm/Documents/Projects/VoxelRidgeInspiration")
FONT = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
TREAT = ("", "_Cartoon", "_TwoColor", "_CratePalette")


def card(src, region, files, stem, ground=False):
    x0, y0, x1, y1 = region
    sc = max(1.0, min(5.0, 170.0 / max(1, (y1 - y0))))
    parts = [src.crop((x0, y0, x1, y1)).resize((max(1, int((x1 - x0) * sc)), max(1, int((y1 - y0) * sc))),
                                                Image.NEAREST)]
    size = None
    for t in TREAT:
        size, vox, pal, mats = read(files / (stem + t + ".vox"))
        w = {p: pal[i - 1][:3] for p, i in vox.items()}
        if ground:
            w = {(x + ox, y + oy, z): c for (x, y, z), c in w.items() for ox in (0, 16) for oy in (0, 16)}
        scale = max(2.0, min(7.0, 170.0 / max(size)))
        parts.append(fastview.view3d(w, -28, 26, scale))
    Wd = sum(p.width for p in parts) + 8 * len(parts)
    Hd = max(p.height for p in parts) + 18
    im = Image.new("RGB", (Wd, Hd), (236, 238, 236))
    x = 0
    for p in parts:
        im.paste(p, (x, 18))
        x += p.width + 8
    ImageDraw.Draw(im).text((2, 1), "%s %s" % (stem, tuple(size)), font=FONT, fill=(0, 0, 0))
    return im


def pages(cards, prefix, per=10):
    out = []
    for page in range(0, len(cards), per):
        chunk = cards[page:page + per]
        rows, cur, cw = [], [], 0
        for c in chunk:
            if cw + c.width > 1900 and cur:
                rows.append(cur)
                cur, cw = [], 0
            cur.append(c)
            cw += c.width + 12
        rows.append(cur)
        Wd = max(sum(c.width + 12 for c in r) for r in rows)
        Hd = sum(max(c.height for c in r) + 8 for r in rows)
        sheet = Image.new("RGB", (Wd, Hd), (250, 250, 250))
        y = 0
        for r in rows:
            x = 0
            for c in r:
                sheet.paste(c, (x, y))
                x += c.width + 12
            y += max(c.height for c in r) + 8
        dest = Path("%s_%02d.png" % (prefix, page // per))
        sheet.save(dest)
        out.append(dest)
        print(dest, sheet.size)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", type=Path, default=HERE.parent)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    # new_2: each family's sprite
    boxes = json.loads((HERE / "lib" / "boxes_new2.json").read_text())
    m2 = json.loads((args.files / "new_2" / "elements" / "manifest.json").read_text(encoding="utf-8"))
    src = Image.open(W / "new_2.jpg").convert("RGB")
    cards = []
    for f in m2["families"]:
        key = f.get("paint") or f.get("sprite") or f.get("geo") or f.get("box")
        cards.append(card(src, boxes[key], args.files / "new_2", "New2_" + f["name"]))
    out2 = (args.out or (args.files / "new_2" / "elements" / "previews"))
    out2.mkdir(parents=True, exist_ok=True)
    pages(cards, str(out2 / "review"))
    # new_1: each family's first region, the cottage, the ground tiles
    m1 = json.loads((args.files / "new_1" / "elements" / "manifest.json").read_text(encoding="utf-8"))
    src = Image.open(W / "new_1.jpg").convert("RGB")
    cards = []
    for f in m1["families"]:
        if f.get("layer") == "Ground":
            cards.append(card(src, f["row"]["crop"], args.files / "new_1", f["row"]["name"], ground=True))
        else:
            cards.append(card(src, f["regions"][0], args.files / "new_1", "New1_" + f["name"]))
    cards.insert(0, card(src, [175, 100, 550, 475], args.files / "new_1", "New1_Cottage"))
    out1 = (args.out or (args.files / "new_1" / "elements" / "previews"))
    out1.mkdir(parents=True, exist_ok=True)
    pages(cards, str(out1 / "review"), per=8)


if __name__ == "__main__":
    main()
