"""Composes the preview sheets from the frames qa/integration.py --render took in the
game's own renderer (the buildings cut into pieces and placed in a level, lit as
TestMap is), and the source crops from poke_j.jpg.

    python output/poke_j/buildings/compose_previews.py <render folder>

Writes into previews/: for each family a sheet of the source and all seven
treatments under one camera and light (_family), four sides of Base and Cartoon
(_geometry) and the game's view of it by day, cut away at each storey, at dusk and
at night (_ingame); and overview.png.
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from generate import FAMILIES, STYLES, family_name

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
    for y in range(int(h * 0.03), int(h * 0.98)):
        for x in range(int(w * 0.08), int(w * 0.92)):
            if not is_background(px[x, y][:3]):
                rows[y] = rows.get(y, 0) + 1
                cols[x] = cols.get(x, 0) + 1
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


def main():
    renders = Path(sys.argv[1])
    OUT.mkdir(exist_ok=True)
    src = Image.open(WORK / "poke_j.jpg").convert("RGB")
    overview = []
    import sculpt
    for kind, info in FAMILIES.items():
        name = family_name(kind)
        source = src.crop(tuple(info["regions"][0]))
        # poke_j.jpg is the art at 0.765 of its size: enlarged to the models' scale.
        source = source.resize((round(source.width * 4 / 0.765), round(source.height * 4 / 0.765)), Image.BICUBIC)
        # Every treatment, one camera and light.
        im, d = sheet((1300, 860), "%s  |  %s  |  seven treatments" % (name, info["title"]),
                      "Rendered in VCOM: cut into 16-cubed pieces, placed in a level, lit as TestMap by day. "
                      "One camera and light for all. The figure is a soldier, two cells tall.")
        d.text((14, 80), "Source (poke_j.jpg, to scale)", font=font(16), fill=INK)
        im.paste(fit(source, 300, 340), (8, 104))
        # One camera for all seven, so one box frames them all: the union of what each
        # frame shows (a pale treatment's walls can read as sky on their own).
        days = {style: frame(renders, "%s_%s" % (kind, style), "day_0") for style in STYLES}
        boxes = [bbox(im_) for im_ in days.values()]
        box = (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))
        for i, (style, label) in enumerate(zip(STYLES, LABELS), 1):
            day = days[style]
            x, y = (i % 4) * 323, 80 + (i // 4) * 390
            d.text((x + 14, y), label, font=font(16), fill=INK)
            im.paste(fit(day.crop(box), 310, 350), (x + 8, y + 24))
            if style == "Base":
                overview.append((info["title"], day.crop(box)))
        im.save(OUT / ("%s_family.png" % name))
        # Four sides of Base and Cartoon.
        im, d = sheet((1440, 820), "%s  |  Base above, Cartoon below" % name,
                      "Front-left, back-right, front-right, back-left. Doors, windows, stairs and slots are the same in both.")
        for row, style in enumerate(("Base", "Cartoon")):
            for col, v in enumerate(["day_0", "day_1", "day_2", "day_3"]):
                day = frame(renders, "%s_%s" % (kind, style), v)
                im.paste(fit(day.crop(bbox(day)), 340, 350), (col * 355 + 12, 90 + row * 365))
        im.save(OUT / ("%s_geometry.png" % name))
        # The game's own view, cut away at each storey, dusk and night.
        base = "%s_Base" % kind
        m = sculpt.build(kind, False)
        shots = [("Game camera (55 degrees, 75 field of view)", frame(renders, base, "day_4"))]
        for n, st in enumerate(m.storeys):
            what = "ground floor" if n == 0 else "upper floor"
            shots.append(("Cut away to its %s (floor selector at %d)" % (what, st["cut"]), frame(renders, base, "day_%d" % (5 + n))))
        day0 = frame(renders, base, "day_0")
        box = bbox(day0)
        shots.append(("Dusk", frame(renders, base, "dusk_0").crop(box)))
        shots.append(("Night", frame(renders, base, "night_0").crop(box)))
        rows = (len(shots) + 1) // 2
        im, d = sheet((1300, 90 + rows * 360), "%s  |  in the game" % name,
                      "Base. The time of day is the game's own (TimeOfDay), glass its own shader. No lights: the user's choice.")
        for i, (label, shot) in enumerate(shots):
            x, y = (i % 2) * 645, 80 + (i // 2) * 360
            d.text((x + 14, y), label, font=font(16), fill=INK)
            im.paste(fit(shot, 630, 330), (x + 8, y + 24))
        im.save(OUT / ("%s_ingame.png" % name))
    im, d = sheet((1300, 560), "poke_j buildings  |  Base",
                  "Two complete models, shown in VCOM, each framed on its own (the red house stands three times in "
                  "the art).")
    for i, (title, shot) in enumerate(overview):
        x, y = i * 648, 80
        d.text((x + 14, y), title, font=font(17), fill=INK)
        im.paste(fit(shot, 636, 440), (x + 6, y + 26))
    im.save(HERE / "overview.png")
    print("Saved the sheets for %d families and overview.png." % len(FAMILIES))


if __name__ == "__main__":
    main()
