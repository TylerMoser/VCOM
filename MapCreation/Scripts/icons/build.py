"""Draws every proposal and a sheet of each kind to choose from.

Each proposal is written as "<Kind>/<Kind> NN.png", 666 x 666 like the pack's icons, and each kind
gets "<Kind>/_<Kind> proposals.png": every proposal numbered, large on the map's white land with a
border and a road running under it (to show what its white edge does), and small, at about the
sizes it would have on the map, on the land and on the sea.

Usage: build.py <the pack's folder> <folder to write the kinds' folders into> [kind ...]
"""
import os
import sys
from multiprocessing import Pool
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import kit

LAND, SEA = (255, 255, 255), (181, 235, 255)
GREY, RED, BLUE, PINK = (128, 128, 128), (200, 40, 30), (28, 112, 224), (233, 0, 255)
CELL_W, CELL_H = 330, 366
SHOWN = 0.46                 # the large view's scale: every kind at the same, so their sizes can be told apart
SMALL = (56, 36, 22)         # px across, the sizes an icon is shown at small: about what it would be on the map


def centred(image):
    """The icon moved sideways so that what is drawn is in the middle."""
    box = image.getbbox()
    if box is None:
        return image
    shift = round(kit.SIZE / 2.0 - (box[0] + box[2]) / 2.0)
    out = Image.new("RGBA", image.size, (255, 255, 255, 0))
    out.paste(image, (shift, 0))
    return out


def draw_one(job):
    pack, kind, number, seed = job
    kit.PACK = pack
    import settlements
    import markers
    sets = dict(settlements.SETS)
    sets.update(markers.SETS)
    icon = kit.Icon(seed)
    sets[kind][number - 1](icon)
    return kind, number, centred(icon.render())


def font(size):
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def sheet_of(kind, icons, what, columns=6):
    rows = (len(icons) + columns - 1) // columns
    head = 64
    sheet = Image.new("RGB", (columns * CELL_W, head + rows * CELL_H), LAND)
    pen = ImageDraw.Draw(sheet)
    pen.rectangle((0, 0, sheet.width, head), fill=(40, 40, 40))
    pen.text((16, 14), "%s: %d proposals" % (kind, len(icons)), fill=(255, 255, 255), font=font(30))
    pen.text((sheet.width - 900, 22), "large: on the land, a border and a road running under it (all of a kind at one scale).  small: 56, 36 and 22 px, on land and on sea", fill=(210, 210, 210), font=font(16))
    cuts = [image.crop(image.getbbox()) for image in icons]
    scale = min(1.0, (CELL_W - 30.0) / max(c.width for c in cuts), 200.0 / max(c.height for c in cuts))
    for i, cut in enumerate(cuts):
        x, y = (i % columns) * CELL_W, head + (i // columns) * CELL_H
        pen.rectangle((x, y, x + CELL_W - 1, y + CELL_H - 1), outline=(215, 215, 215))
        ground = y + 244
        pen.line((x + 6, ground - 70, x + CELL_W - 6, ground - 34), fill=GREY, width=3)
        pen.line((x + 6, ground - 14, x + CELL_W - 6, ground - 52), fill=RED, width=4)
        big = cut.resize((max(1, round(cut.width * scale)), max(1, round(cut.height * scale))), Image.LANCZOS)
        sheet.paste(big, (x + CELL_W // 2 - big.width // 2, ground - big.height), big)
        strip = y + 254
        pen.rectangle((x + CELL_W // 2, strip, x + CELL_W - 2, strip + 66), fill=SEA)
        for half in range(2):
            at = x + 12 + half * (CELL_W // 2)
            for size in SMALL:
                k = size / float(max(cut.width, cut.height))
                small = cut.resize((max(1, round(cut.width * k)), max(1, round(cut.height * k))), Image.LANCZOS)
                sheet.paste(small, (at, strip + 62 - small.height), small)
                at += small.width + 12
        pen.text((x + 10, y + 6), "%02d" % (i + 1), fill=(0, 0, 0), font=font(26))
        label = what[i] if i < len(what) else ""
        words, lines = label.split(), [""]
        for word in words:
            if pen.textlength(lines[-1] + " " + word, font=font(15)) > CELL_W - 20:
                lines.append("")
            lines[-1] = (lines[-1] + " " + word).strip()
        for k, line in enumerate(lines[:2]):
            pen.text((x + 10, y + CELL_H - 42 + k * 18), line, fill=(60, 60, 60), font=font(15))
    return sheet


def main():
    pack, out = sys.argv[1:3]
    kit.PACK = pack
    import settlements
    import markers
    sets = dict(settlements.SETS)
    sets.update(markers.SETS)
    what = dict(settlements.WHAT)
    what.update(markers.WHAT)
    kinds = sys.argv[3:] or list(sets)
    jobs = [(pack, kind, n, 1000 * (list(sets).index(kind) + 1) + n) for kind in kinds for n in range(1, len(sets[kind]) + 1)]
    with Pool(6) as pool:
        drawn = pool.map(draw_one, jobs)
    by_kind = {}
    for kind, number, image in drawn:
        by_kind.setdefault(kind, {})[number] = image
    for kind in kinds:
        folder = os.path.join(out, kind)
        os.makedirs(folder, exist_ok=True)
        icons = [by_kind[kind][n] for n in sorted(by_kind[kind])]
        for n, image in enumerate(icons, start=1):
            image.save(os.path.join(folder, "%s %02d.png" % (kind, n)))
        maker = markers.sheet_of if kind in markers.SETS else sheet_of
        sheet = maker(kind, icons, what[kind])
        sheet.save(os.path.join(folder, "_%s proposals.png" % kind))
        widths = [im.getbbox()[2] - im.getbbox()[0] for im in icons]
        print("%s: %d proposals; what is drawn is %d to %d px wide; sheet %d x %d" % (kind, len(icons), min(widths), max(widths), sheet.width, sheet.height))


if __name__ == "__main__":
    main()
