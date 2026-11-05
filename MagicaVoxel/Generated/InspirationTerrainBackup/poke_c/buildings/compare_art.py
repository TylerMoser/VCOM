"""Draws each Base model in poke_c.png's own projection beside the source crop, at
the same scale, to check the reconstruction against the art: one voxel a pixel
across and in depth, heights foreshortened by K (0.46, measured on the cottage: its
three-course wall, 48 voxels, is 22 pixels in the art). Only front and top faces
show, as in the art; the foundation under the floor (z < 16) is left out.

    python output/poke_c/buildings/compare_art.py    # writes previews/<Family>_art.png
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import palettes
import sculpt
from generate import FAMILIES

HERE = Path(__file__).resolve().parent
WORK = HERE.parent.parent.parent
K = 0.46
SCALE = 4


def render(vox, k=K, scale=SCALE, ground_z=16):
    colors = {l: palettes.LABELS[l][0] for l in palettes.LABELS}
    glassy = {l for l in palettes.LABELS if palettes.LABELS[l][1] == "glass"}
    faces = [((0, -1, 0), ((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))), ((0, 0, 1), ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)))]
    d = (0.0, 1.0, -1.0 / k)
    polys = []
    for p, lab in vox.items():
        if p[2] < ground_z:
            continue
        isg = lab in glassy
        for n, quad in faces:
            q = (p[0] + n[0], p[1] + n[1], p[2] + n[2])
            if q in vox and (isg or vox[q] not in glassy):
                continue
            pts = [(p[0] + c[0], p[1] + c[1], p[2] + c[2]) for c in quad]
            depth = sum(pt[1] * d[1] + pt[2] * d[2] for pt in pts)
            col = colors[lab]
            if isg:
                col = tuple(int(0.7 * c + 0.3 * 250) for c in col)
            shade = 1.0 if n[2] else 0.86
            polys.append((depth, [(pt[0], -(pt[1] + k * (pt[2] - ground_z))) for pt in pts],
                          tuple(min(255, int(c * shade)) for c in col)))
    polys.sort(key=lambda t: -t[0])
    xs = [x for _, sp, _ in polys for x, _ in sp]
    ys = [y for _, sp, _ in polys for _, y in sp]
    minx, miny = min(xs), min(ys)
    im = Image.new("RGB", (int((max(xs) - minx) * scale) + 2, int((max(ys) - miny) * scale) + 2), (128, 158, 112))
    draw = ImageDraw.Draw(im)
    for _, sp, col in polys:
        draw.polygon([((x - minx) * scale, (y - miny) * scale) for x, y in sp], fill=col)
    return im


def main():
    src = Image.open(WORK / "poke_c.png").convert("RGB")
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 18)
    (HERE / "previews").mkdir(exist_ok=True)
    for kind, info in FAMILIES.items():
        x0, y0, x1, y1 = info["regions"][0]
        crop = src.crop((x0, y0, x1, y1)).resize(((x1 - x0) * SCALE, (y1 - y0) * SCALE), Image.NEAREST)
        model = render(sculpt.build(kind, False).v)
        h = max(crop.height, model.height)
        sheet = Image.new("RGB", (crop.width + model.width + 60, h + 50), (239, 241, 232))
        sheet.paste(crop, (20, 40))
        sheet.paste(model, (crop.width + 40, 40))
        d = ImageDraw.Draw(sheet)
        d.text((20, 10), "poke_c.png, pixels %d-%d x %d-%d (x%d)" % (x0, x1, y0, y1, SCALE), font=font, fill="#26372c")
        d.text((crop.width + 40, 10), "PokeC_%s, in the art's projection (heights x%.2f)" % (kind, K), font=font, fill="#26372c")
        sheet.save(HERE / "previews" / ("PokeC_%s_art.png" % kind))
    print("Saved %d comparisons with the art." % len(FAMILIES))


if __name__ == "__main__":
    main()
