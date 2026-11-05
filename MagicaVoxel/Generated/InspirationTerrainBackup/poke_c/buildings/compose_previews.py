"""Composes the preview sheets from the frames qa/integration.py --render took in the
game's own renderer (the buildings cut into pieces and placed in a level, lit as
TestMap is), and the source crops from poke_c.png.

    python output/poke_c/buildings/compose_previews.py <render folder>

Writes into previews/: for each family a sheet of the source and all seven
treatments under one camera and light (_family), four sides of Base and Cartoon
(_geometry) and the game's view of it by day, cut away, at dusk and at night
(_ingame); the assembled bridge the same; and overview.png.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from generate import FAMILIES, STYLES

HERE = Path(__file__).resolve().parent
WORK = HERE.parent.parent.parent
OUT = HERE / "previews"
LABELS = ["Base", "Cartoon", "CratePalette", "TwoColor", "Cartoon + TwoColor", "CratePalette + TwoColor",
          "Cartoon + Crate + TwoColor"]
BG = "#eff1e8"
INK = "#26372c"
SUB = "#526252"


def font(n):
    return ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", n)


def is_background(p):
    r, g, b = p
    sky = b > 140 and b >= g >= r - 10
    grass = g > 120 and g > r + 12 and g > b + 15
    return sky or grass


def bbox(im):
    """The building's box in a day frame: what is neither sky nor grass, looked for
    in the middle of the frame (the ground's edges lie outside it), padded."""
    small = im.resize((im.width // 4, im.height // 4))
    w, h = small.size
    px = small.load()
    rows, cols = {}, {}
    for y in range(int(h * 0.06), int(h * 0.97)):
        for x in range(int(w * 0.12), int(w * 0.88)):
            if not is_background(px[x, y][:3]):
                rows[y] = rows.get(y, 0) + 1
                cols[x] = cols.get(x, 0) + 1
    # Rows and columns with a few of the building's pixels, not a stray one.
    ys = [y for y, n in rows.items() if n >= 3]
    xs = [x for x, n in cols.items() if n >= 3]
    if not xs or not ys:
        return (0, 0, im.width, im.height)
    x0, x1, y0, y1 = min(xs) * 4, max(xs) * 4 + 4, min(ys) * 4, max(ys) * 4 + 4
    pad = int(max(x1 - x0, y1 - y0) * 0.06)
    return (max(0, x0 - pad), max(0, y0 - pad), min(im.width, x1 + pad), min(im.height, y1 + pad))


def fit(im, w, h):
    im = im.copy()
    im.thumbnail((w, h), Image.LANCZOS)
    tile = Image.new("RGB", (w, h), BG)
    tile.paste(im, ((w - im.width) // 2, (h - im.height) // 2))
    return tile


def sheet(size, title, sub):
    im = Image.new("RGB", size, BG)
    d = ImageDraw.Draw(im)
    d.text((18, 10), title, font=font(24), fill=INK)
    d.text((18, 46), sub, font=font(15), fill=SUB)
    return im, d


def frame(renders, scene, name):
    return Image.open(renders / scene / (name + ".png")).convert("RGB")


def crop_like(day, other):
    return other.crop(bbox(day))


def main():
    renders = Path(sys.argv[1])
    OUT.mkdir(exist_ok=True)
    src = Image.open(WORK / "poke_c.png").convert("RGB")
    scenes = {kind: kind for kind in FAMILIES}
    scenes["Bridge"] = "Bridge"
    titles = dict((k, v["title"]) for k, v in FAMILIES.items())
    titles["Bridge"] = "Covered bridge (two pavilions and a span)"
    overview = []
    for kind, scene in scenes.items():
        region = FAMILIES[kind]["regions"][0] if kind in FAMILIES else [250, 310, 535, 455]
        source = src.crop(tuple(region))
        source = source.resize((source.width * 4, source.height * 4), Image.NEAREST)
        # Every treatment, one camera and light.
        im, d = sheet((1300, 860), "PokeC_%s  |  %s  |  seven treatments" % (kind, titles[kind]),
                      "Rendered in VCOM: cut into 16-cubed pieces, placed in a level, lit as TestMap by day. "
                      "One camera and light for all. The figure is a soldier, two cells tall.")
        d.text((14, 80), "Source (poke_c.png, x4)", font=font(16), fill=INK)
        im.paste(fit(source, 300, 340), (8, 104))
        for i, (style, label) in enumerate(zip(STYLES, LABELS), 1):
            day = frame(renders, "%s_%s" % (scene, style), "day_0")
            x, y = (i % 4) * 323, 80 + (i // 4) * 390
            d.text((x + 14, y), label, font=font(16), fill=INK)
            im.paste(fit(day.crop(bbox(day)), 310, 350), (x + 8, y + 24))
            if style == "Base":
                overview.append((kind, day.crop(bbox(day))))
        im.save(OUT / ("PokeC_%s_family.png" % kind))
        # Four sides of Base and Cartoon.
        views = ["day_0", "day_1", "day_2", "day_3"] if kind != "Bridge" else ["day_0", "day_1"]
        im, d = sheet((1440, 820), "PokeC_%s  |  Base above, Cartoon below" % kind,
                      "Front-left, back-right, front-right, back-left. Doors, windows and slots are the same in both.")
        for row, style in enumerate(("Base", "Cartoon")):
            for col, v in enumerate(views):
                day = frame(renders, "%s_%s" % (scene, style), v)
                im.paste(fit(day.crop(bbox(day)), 340, 350), (col * 355 + 12, 90 + row * 365))
        im.save(OUT / ("PokeC_%s_geometry.png" % kind))
        # The game's own view, cut away, dusk and night.
        base = "%s_Base" % scene
        shots = [("Game camera (55 degrees, 75 field of view)", frame(renders, base, "day_4" if kind != "Bridge" else "day_2"))]
        if kind != "Bridge" and kind != "BridgeSpan":
            shots.append(("Cut away (floor selector)", frame(renders, base, "day_5")))
        day0 = frame(renders, base, "day_0")
        shots.append(("Dusk", crop_like(day0, frame(renders, base, "dusk_0"))))
        shots.append(("Night", crop_like(day0, frame(renders, base, "night_0"))))
        im, d = sheet((1300, 820), "PokeC_%s  |  in the game" % kind,
                      "Base. The time of day is the game's own (TimeOfDay), glass its own shader. No lights: the user's choice.")
        for i, (label, shot) in enumerate(shots):
            x, y = (i % 2) * 645, 80 + (i // 2) * 370
            d.text((x + 14, y), label, font=font(16), fill=INK)
            im.paste(fit(shot, 630, 340), (x + 8, y + 24))
        im.save(OUT / ("PokeC_%s_ingame.png" % kind))
    im, d = sheet((1300, 880), "poke_c buildings  |  Base",
                  "Five complete models (the covered bridge is two: a pavilion, placed twice, and the span), shown in VCOM. "
                  "Each is framed on its own.")
    for i, (kind, shot) in enumerate(overview):
        x, y = (i % 3) * 430, 80 + (i // 3) * 400
        d.text((x + 14, y), kind, font=font(17), fill=INK)
        im.paste(fit(shot, 415, 360), (x + 8, y + 26))
    im.save(HERE / "overview.png")
    print("Saved the sheets for %d families and the bridge, and overview.png." % len(FAMILIES))


if __name__ == "__main__":
    main()
