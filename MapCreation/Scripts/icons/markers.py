"""The proposals for marking a capital: a mark to go with a settlement's icon, saying what it is the
capital of. There are three ranks (kingdom, duchy, county) and the proposals come in families: number
7 of each rank belongs with number 7 of the others, the kingdom's the grandest and the county's the
plainest of the same idea.

A mark is drawn by itself, standing on the icon's ground line, 666 x 666 like every icon. How it
is meant to go with a settlement's icon is its "place": above it, behind it or under it.
"""
import numpy as np
from PIL import Image, ImageDraw
import kit
import parts as P
from kit import box, oval, star

KINGDOM, DUCHY, COUNTY = 3, 2, 1
RANKS = {"Kingdom Capital": KINGDOM, "Duchy Capital": DUCHY, "County Capital": COUNTY}


def _ink(ic, outlines, cuts=()):
    L = ic.layer(ic.ink())
    L["add"] += list(outlines)
    L["cut"] += list(cuts)
    return L


def _paper(ic, outlines, marks=(), line=kit.LINE):
    part = ic.paper(line)
    part["add"] += list(outlines)
    part["marks"] += list(marks)
    return part


def shield(w=130, h=150, cx=0.0, y=0.0):
    side = [(cx + w / 2 * np.sqrt(max(0.0, 1.0 - (1.0 - t) ** 2.2)), y + h * 0.55 * t) for t in np.linspace(0.0, 1.0, 14)]
    return [(cx, y)] + side + [(cx + w / 2, y + h), (cx - w / 2, y + h)] + [(2 * cx - px, py) for px, py in reversed(side)]


def chevron(w, h, t, y):
    return [(-w / 2, y), (0, y + h), (w / 2, y), (w / 2, y - t), (0, y + h - t), (-w / 2, y - t)]


def fleur(scale=1.0):
    s = scale
    out = [[(0, 160 * s), (24 * s, 104 * s), (17 * s, 62 * s), (0, 50 * s), (-17 * s, 62 * s), (-24 * s, 104 * s)],
           box(-46 * s, 42 * s, 46 * s, 58 * s), [(-9 * s, 46 * s), (0, 0), (9 * s, 46 * s)]]
    for side in (-1, 1):
        out.append([(side * 12 * s, 60 * s), (side * 30 * s, 80 * s), (side * 50 * s, 112 * s), (side * 68 * s, 104 * s), (side * 74 * s, 80 * s),
                    (side * 58 * s, 60 * s), (side * 42 * s, 64 * s), (side * 30 * s, 50 * s)])
        out.append([(side * 12 * s, 46 * s), (side * 34 * s, 22 * s), (side * 26 * s, 8 * s), (side * 8 * s, 28 * s)])
    return out


# -- the families: each draws its mark for a rank ------------------------------------------------------------
def crown_balls(ic, rank):
    _ink(ic, P.crown({KINGDOM: 5, DUCHY: 3, COUNTY: 1}[rank], {KINGDOM: 176, DUCHY: 140, COUNTY: 104}[rank], 30, {KINGDOM: 66, DUCHY: 54, COUNTY: 44}[rank]))


def crown_paper(ic, rank):
    _paper(ic, P.crown({KINGDOM: 5, DUCHY: 3, COUNTY: 1}[rank], {KINGDOM: 176, DUCHY: 140, COUNTY: 104}[rank], 30, {KINGDOM: 66, DUCHY: 54, COUNTY: 44}[rank]))


def crown_plain(ic, rank):
    _ink(ic, P.crown({KINGDOM: 5, DUCHY: 4, COUNTY: 3}[rank], {KINGDOM: 180, DUCHY: 150, COUNTY: 120}[rank], {KINGDOM: 34, DUCHY: 30, COUNTY: 26}[rank],
                     {KINGDOM: 72, DUCHY: 46, COUNTY: 24}[rank], balls=False))


def crown_heraldic(ic, rank):
    """A king's crown with a cross, a duke's with five pearls, a count's with three."""
    if rank == KINGDOM:
        shapes = P.crown(5, 176, 30, 60)
        shapes += [box(-5, 96, 5, 142), box(-19, 116, 19, 126)]
        _ink(ic, shapes)
    else:
        count = 5 if rank == DUCHY else 3
        w = 156 if rank == DUCHY else 116
        shapes = [box(-w / 2, 0, w / 2, 30)]
        for x in np.linspace(-w / 2 + 12, w / 2 - 12, count):
            shapes += [box(x - 4.5, 26, x + 4.5, 52), oval(x, 58, 12, 12)]
        _ink(ic, shapes)


def pack_banner(ic, rank):
    name, scale = {KINGDOM: ("Banner 3", 0.5), DUCHY: ("Banner 2", 0.66), COUNTY: ("Banner 1", 0.62)}[rank]
    ic.piece(name, 0, 0, scale)


def pack_location(ic, rank):
    ic.piece({KINGDOM: "Location Icon 1", DUCHY: "Location Icon 2", COUNTY: "Location Icon 3"}[rank], 0, 0, 0.9)


def flag_ink(ic, rank):
    """A black flag on a pole: a long swallow-tailed banner, a pennant, a small square flag."""
    if rank == KINGDOM:
        _ink(ic, [box(-74, 0, -62, 200), [(-68, 200), (80, 196), (48, 158), (84, 116), (-68, 112)]])
    elif rank == DUCHY:
        _ink(ic, [box(-56, 0, -44, 170), [(-50, 170), (70, 132), (-50, 94)]])
    else:
        _ink(ic, [box(-40, 0, -28, 140), box(-34, 84, 42, 140)])


def flag_paper(ic, rank):
    """A white flag with a charge: a star, a dot, nothing."""
    cloth = [(-44, 150), (-10, 158), (30, 146), (66, 152), (64, 78), (30, 72), (-8, 84), (-44, 76)]
    marks = {KINGDOM: [star(10, 114, 30)], DUCHY: [oval(10, 114, 17, 17)], COUNTY: []}[rank]
    _paper(ic, [box(-56, 0, -44, 164), cloth], marks)


def stars(ic, rank):
    if rank == KINGDOM:
        _ink(ic, [star(0, 62, 52), star(-98, 36, 36), star(98, 36, 36)])
    elif rank == DUCHY:
        _ink(ic, [star(-50, 44, 44), star(50, 44, 44)])
    else:
        _ink(ic, [star(0, 44, 44)])


def star_shapes(ic, rank):
    """A star of eight points, of five, of four."""
    if rank == KINGDOM:
        _ink(ic, [star(0, 80, 80, 8, 0.52)])
    elif rank == DUCHY:
        _ink(ic, [star(0, 62, 62, 5, 0.45)])
    else:
        _ink(ic, [star(0, 50, 50, 4, 0.42)])


def shield_ink(ic, rank):
    """A black shield: charged with a crown, with a chevron, plain."""
    cuts = {KINGDOM: [c for c in [[(x, y + 62) for x, y in shape] for shape in P.crown(3, 86, 18, 38, balls=False)]],
            DUCHY: [chevron(74, 34, 15, 76)], COUNTY: []}[rank]
    _ink(ic, [shield({KINGDOM: 136, DUCHY: 124, COUNTY: 112}[rank], {KINGDOM: 164, DUCHY: 150, COUNTY: 136}[rank])], cuts)


def shield_paper(ic, rank):
    """A white shield: with a crown, with two bars, with one."""
    marks = {KINGDOM: [[(x, y + 64) for x, y in shape] for shape in P.crown(3, 88, 18, 40, balls=False)],
             DUCHY: [box(-70, 104, 70, 118), box(-70, 74, 70, 88)], COUNTY: [box(-70, 86, 70, 100)]}[rank]
    _paper(ic, [shield({KINGDOM: 136, DUCHY: 124, COUNTY: 112}[rank], {KINGDOM: 164, DUCHY: 150, COUNTY: 136}[rank])], marks)


def plate(ic, rank):
    """A white plate to stand a settlement's icon on: rayed like a sun, double rimmed, plain."""
    if rank == KINGDOM:
        _paper(ic, [star(0, 170, 176, 20, 0.86, 0.0)])
        _paper(ic, [oval(0, 170, 126, 126, 72)], line=5)
    elif rank == DUCHY:
        _paper(ic, [oval(0, 160, 160, 160, 72)])
        _paper(ic, [oval(0, 160, 138, 138, 72)], line=5)
    else:
        _paper(ic, [oval(0, 150, 150, 150, 72)])


def pips(ic, rank):
    xs = {KINGDOM: (-52, 0, 52), DUCHY: (-28, 28), COUNTY: (0,)}[rank]
    _ink(ic, [oval(x, 22, 20, 20) for x in xs])


def chevrons(ic, rank):
    _ink(ic, [chevron(120, 46, 18, 18 + i * 34) for i in range(rank)])


def bars(ic, rank):
    """Lines to go under a settlement's icon."""
    _ink(ic, [box(-110 + i * 18, i * 26, 110 - i * 18, i * 26 + 13) for i in range(rank)])


def lily(ic, rank):
    """A fleur-de-lis, a trefoil, a single leaf."""
    if rank == KINGDOM:
        _ink(ic, fleur(1.0))
    elif rank == DUCHY:
        _ink(ic, [oval(0, 96, 30, 34), oval(-36, 56, 30, 30), oval(36, 56, 30, 30), box(-6, 0, 6, 60)])
    else:
        _ink(ic, [[(0, 110), (34, 60), (0, 10), (-34, 60)], box(-5, 0, 5, 30)])


def heavens(ic, rank):
    """The sun, the moon, a star."""
    if rank == KINGDOM:
        _ink(ic, [star(0, 84, 84, 12, 0.62), oval(0, 84, 50, 50)])
    elif rank == DUCHY:
        _ink(ic, [oval(0, 66, 66, 66, 60)], [oval(30, 80, 56, 56, 60)])
    else:
        _ink(ic, [star(0, 48, 48)])


def banner_charged(ic, rank):
    """The pack's banner bearing a crown, a star, a dot."""
    ic.piece("Banner 2", 0, 0, 0.72)
    charge = {KINGDOM: [[(x, y + 88) for x, y in shape] for shape in P.crown(3, 92, 18, 40, balls=False)],
              DUCHY: [star(0, 104, 32)], COUNTY: [oval(0, 104, 17, 17)]}[rank]
    L = ic.layer(ic.ink())
    L["add"] += charge


def pack_stronghold(ic, rank):
    """The pack's Castle, its Tower, its Flag: small, as a badge."""
    name, scale = {KINGDOM: ("Castle", 0.62), DUCHY: ("Tower", 0.5), COUNTY: ("Flag", 0.4)}[rank]
    ic.piece(name, 0, 0, scale)


def gems(ic, rank):
    xs = {KINGDOM: (-62, 0, 62), DUCHY: (-34, 34), COUNTY: (0,)}[rank]
    _ink(ic, [[(x, 78 if x == 0 else 66), (x + 28, 39 if x == 0 else 33), (x, 0), (x - 28, 39 if x == 0 else 33)] for x in xs])


def pennants(ic, rank):
    """A pole flying three pennants, two, one."""
    shapes = [box(-6, 0, 6, 70 + rank * 44)]
    for i in range(rank):
        top = 70 + rank * 44 - i * 44
        shapes.append([(0, top), (84 - i * 8, top - 19), (0, top - 38)])
    _ink(ic, shapes)


def ring_marks(ic, rank):
    """A ring to go round a settlement's foot: three rings, two, one."""
    for i in range(rank):
        r = 150 - i * 30
        _paper(ic, [oval(0, 150, r, r, 72)], line=7 if i == 0 else 5)


def towers(ic, rank):
    """Three turrets on a wall, two, one."""
    L = ic.layer(ic.ink())
    xs = {KINGDOM: (-64, 0, 64), DUCHY: (-36, 36), COUNTY: (0,)}[rank]
    L["add"].append(box(xs[0] - 30, 0, xs[-1] + 30, 34))
    for x in xs:
        P.tower(ic, x, 44, 70 if x == 0 and rank == KINGDOM else 56, "flat", door=False, window=False, join=L)


FAMILIES = [
    (crown_balls, "above", ("a crown of five points", "a coronet of three points", "a circlet with one point")),
    (crown_paper, "above", ("a white crown of five points", "a white coronet of three", "a white circlet")),
    (crown_plain, "above", ("a tall plain crown", "a lower crown of four points", "a low crown of three")),
    (crown_heraldic, "above", ("a king's crown with its cross", "a duke's coronet of five pearls", "a count's coronet of three pearls")),
    (pack_banner, "above", ("the pack's long banner", "the pack's shield banner", "the pack's small banner")),
    (pack_location, "above", ("the pack's star in a ring", "the pack's ring and dot", "the pack's dot")),
    (flag_ink, "above", ("a long swallow-tailed banner", "a pennant", "a small flag")),
    (flag_paper, "above", ("a white flag with a star", "a white flag with a dot", "a white flag")),
    (stars, "above", ("three stars", "two stars", "one star")),
    (star_shapes, "above", ("a star of eight points", "a star of five points", "a star of four points")),
    (shield_ink, "above", ("a shield with a crown", "a shield with a chevron", "a plain shield")),
    (shield_paper, "above", ("a white shield with a crown", "a white shield with two bars", "a white shield with one bar")),
    (plate, "behind", ("a rayed plate behind the icon", "a double-rimmed plate behind the icon", "a plain plate behind the icon")),
    (pips, "above", ("three dots", "two dots", "one dot")),
    (chevrons, "above", ("three chevrons", "two chevrons", "one chevron")),
    (bars, "under", ("three lines under the icon", "two lines under the icon", "one line under the icon")),
    (lily, "above", ("a fleur-de-lis", "a trefoil", "a single leaf")),
    (heavens, "above", ("the sun", "the moon", "a star")),
    (banner_charged, "above", ("the pack's banner bearing a crown", "the pack's banner bearing a star", "the pack's banner bearing a dot")),
    (pack_stronghold, "above", ("the pack's Castle as a badge", "the pack's Tower as a badge", "the pack's Flag as a badge")),
    (gems, "above", ("three gems", "two gems", "one gem")),
    (pennants, "above", ("a pole flying three pennants", "a pole flying two pennants", "a pole flying one pennant")),
    (ring_marks, "behind", ("three rings behind the icon", "two rings behind the icon", "one ring behind the icon")),
    (towers, "above", ("three turrets", "two turrets", "one turret")),
]


def _draw(family, rank):
    return lambda ic: family(ic, rank)


SETS = {kind: [_draw(family, rank) for family, _, _ in FAMILIES] for kind, rank in RANKS.items()}
WHAT = {kind: [words[3 - rank] for _, _, words in FAMILIES] for kind, rank in RANKS.items()}
PLACES = [place for _, place, _ in FAMILIES]

LAND, SEA = (255, 255, 255), (181, 235, 255)
CELL_W, CELL_H = 330, 400


def with_icon(mark, place, sample, size):
    """A settlement's icon with a mark put with it as the mark is meant to go: a picture [size] px square."""
    canvas = Image.new("RGBA", (kit.SIZE, kit.SIZE + 240), (0, 0, 0, 0))
    drop = 200                                            # room above the icon for a mark
    box_s = sample.getbbox()
    box_m = mark.getbbox()
    cut = mark.crop(box_m)
    if place == "behind":
        scale = 1.15 * max(box_s[2] - box_s[0], box_s[3] - box_s[1]) / max(cut.width, cut.height) * 1.25
        cut = cut.resize((max(1, round(cut.width * scale)), max(1, round(cut.height * scale))), Image.LANCZOS)
        cx, cy = (box_s[0] + box_s[2]) / 2.0, (box_s[1] + box_s[3]) / 2.0 + drop
        canvas.alpha_composite(cut, (round(cx - cut.width / 2.0), round(cy - cut.height / 2.0)))
        canvas.alpha_composite(sample, (0, drop))
    else:
        canvas.alpha_composite(sample, (0, drop))
        scale = 0.62
        cut = cut.resize((max(1, round(cut.width * scale)), max(1, round(cut.height * scale))), Image.LANCZOS)
        cx = (box_s[0] + box_s[2]) / 2.0
        if place == "above":
            canvas.alpha_composite(cut, (round(cx - cut.width / 2.0), round(box_s[1] + drop - cut.height - 4)))
        else:
            canvas.alpha_composite(cut, (round(cx - cut.width / 2.0), round(box_s[3] + drop + 6)))
    used = canvas.getbbox()
    side = max(used[2] - used[0], used[3] - used[1]) + 16
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.alpha_composite(canvas.crop(used), ((side - (used[2] - used[0])) // 2, side - 8 - (used[3] - used[1])))
    return square.resize((size, size), Image.LANCZOS)


def sheet_of(kind, icons, what, columns=6):
    """A sheet of one rank's marks: each large by itself, then with the pack's Town and Village as it
    is meant to go with an icon, large and at map sizes."""
    from build import font
    rows = (len(icons) + columns - 1) // columns
    head = 64
    sheet = Image.new("RGB", (columns * CELL_W, head + rows * CELL_H), LAND)
    pen = ImageDraw.Draw(sheet)
    pen.rectangle((0, 0, sheet.width, head), fill=(40, 40, 40))
    pen.text((16, 14), "%s: %d proposals for its mark" % (kind, len(icons)), fill=(255, 255, 255), font=font(30))
    pen.text((sheet.width - 900, 22), "left: the mark by itself.  right: as it would go with an icon (the pack's Town, then its Village small, on land and sea)", fill=(210, 210, 210), font=font(16))
    town = Image.new("RGBA", (kit.SIZE, kit.SIZE), (0, 0, 0, 0))
    town.alpha_composite(kit.pack("Town"))
    village = Image.new("RGBA", (kit.SIZE, kit.SIZE), (0, 0, 0, 0))
    village.alpha_composite(kit.pack("Village"))
    for i, mark in enumerate(icons):
        x, y = (i % columns) * CELL_W, head + (i // columns) * CELL_H
        pen.rectangle((x, y, x + CELL_W - 1, y + CELL_H - 1), outline=(215, 215, 215))
        pen.line((x + 6, y + 150, x + CELL_W - 6, y + 190), fill=(128, 128, 128), width=3)
        pen.line((x + 6, y + 220, x + CELL_W - 6, y + 176), fill=(200, 40, 30), width=4)
        box_m = mark.getbbox()
        cut = mark.crop(box_m)
        scale = min(0.5, 130.0 / cut.width, 170.0 / cut.height)
        alone = cut.resize((max(1, round(cut.width * scale)), max(1, round(cut.height * scale))), Image.LANCZOS)
        sheet.paste(alone, (x + 78 - alone.width // 2, y + 236 - alone.height), alone)
        shown = with_icon(mark, PLACES[i], town, 190)
        sheet.paste(shown, (x + 138, y + 48), shown)
        strip = y + 262
        pen.rectangle((x + CELL_W // 2, strip, x + CELL_W - 2, strip + 86), fill=SEA)
        for half in range(2):
            at = x + 10 + half * (CELL_W // 2)
            for sample, size in ((town, 80), (village, 52)):
                small = with_icon(mark, PLACES[i], sample, size)
                sheet.paste(small, (at, strip + 84 - size), small)
                at += size + 8
        pen.text((x + 10, y + 6), "%02d" % (i + 1), fill=(0, 0, 0), font=font(26))
        pen.text((x + 10, y + CELL_H - 40), what[i], fill=(60, 60, 60), font=font(15))
        pen.text((x + 10, y + CELL_H - 22), "goes %s the icon" % PLACES[i], fill=(140, 140, 140), font=font(13))
    return sheet
