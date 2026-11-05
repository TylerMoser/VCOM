"""Iterating on an image's styles: each style's test layout drawn in 3D and in the
image's own projection, beside the art it was measured from at the same scale,
built in memory from styles.py (the delivered previews are compose_previews.py's).
    python preview.py <source> [treatment]   -> <temp>/terrain_preview/<source>_preview_<treatment>.png"""
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import fastview
import kit
import layout
import styles as STY

OUT = Path(tempfile.gettempdir()) / "terrain_preview"


def sheet_for(source, treatment="Base"):
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 15)
    rows = []
    for st in STY.STYLES:
        if st.source != source:
            continue
        world = layout.assemble(st, st.test, treatment)
        a = fastview.view3d(world, -28, 40, 2.4)
        b = fastview.oblique(world, st.K, 4.0)
        art = None
        if getattr(st, "art", None):
            im = Image.open(kit.ROOT / st.image).convert("RGB").crop(st.art)
            s = 4.0 * 16 / st.ppt
            art = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.NEAREST)
        parts = [p for p in (a, b, art) if p is not None]
        h = max(p.height for p in parts)
        w = sum(p.width for p in parts) + 20 * len(parts)
        row = Image.new("RGB", (w, h + 22), (240, 240, 235))
        d = ImageDraw.Draw(row)
        d.text((4, 2), "%s %s (%s, %d levels; K %.3g)" % (st.source, st.name, st.family, st.levels, st.K), font=font,
               fill=(0, 0, 0))
        x = 0
        for p in parts:
            row.paste(p, (x, 22))
            x += p.width + 20
        rows.append(row)
    W = max(r.width for r in rows)
    sheet = Image.new("RGB", (W, sum(r.height for r in rows)), (240, 240, 235))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / ("%s_preview_%s.png" % (source, treatment))
    sheet.save(path)
    return path, sheet.size


if __name__ == "__main__":
    print(*sheet_for(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "Base"))
