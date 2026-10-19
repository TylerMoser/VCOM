"""How heavy each kind of line on the new map is on the screen, at any height of the view, as the
map was when 10, 14 and 19 were revisited on 2026-10-19 ("now") and under each of their variants
(MapStyles/README.md, "Revisited on the applied look"). 10b, 14b and 19a were applied the same day,
so the map as it is since is the variant "together".

For each kind of line it works out:

- its width in screen pixels: its node's width times MapDetail's one factor,
  (miles / 220) ^ (1 - 0.36), times the camera's zoom, times a variant's own growth on top
  (14's: (miles / neutral) ^ growth);
- its weight: the width of a black line that would carry as much contrast. Each part of the
  line across (a road's casing and fill, a border's ink) counts its share of the width times its
  colour's difference from the white land (CIE76 delta E / 100), times how much of the line's
  length its pattern covers (a county border's dots cover 18%). A proxy for how much a line draws
  the eye, not a model of seeing: a saturated colour (the amber highways) draws it more than its
  delta E says, a thin dotted line less.

A kind that is not shown at a height (its tier, MapDetail.SHOWN_FROM, or a variant of 19's) is
left blank.

usage: py -3.14 line_weights.py table [variant ...]           # markdown tables, one per height
       py -3.14 line_weights.py ladder <out.png> [variant ...]  # every kind's weight by height,
                                                               # a panel a variant
       py -3.14 line_weights.py tiers <out.png> [variant ...]   # 19's layers: the heights each
                                                               # shows at, a panel a variant
The variants are named as in VARIANTS ("now", "10a", ..., "together") and, for tiers, as in
TIER_VARIANTS ("now", "19a" to "19d"); none given: all of them. Needs Pillow for the charts.
"""
import math
import sys

UNITS_A_MILE = 16.09344
SCREEN_H = 720.0
TRUE_MILES = 220.0
GROWTH = 0.36
WHITE = (1.0, 1.0, 1.0)
INK = (0.25, 0.2, 0.31)

# Heights the tables are given at: all the way out (the game's window over the land), the
# Kingdom tier, the four standard views' B to D, the far end of the Duchy tier, the hamlets' step
# and all the way in.
HEIGHTS = [832.0, 400.0, 180.0, 120.0, 80.0, 50.0, 30.0, 25.0]

# The map as it is (Docs/MAP.md, "Its look"). Widths in units at 220 miles tall.
NOW = {
    "kingdom": {"kind": "border", "width": 12.0, "alpha": 0.85, "pattern": (3.2, 1.0, 0.85, 0.9, False), "from": 9999},
    "duchy": {"kind": "border", "width": 8.0, "alpha": 0.7, "pattern": (2.4, 1.3, 0.0, 0.0, True), "from": 480},
    "county": {"kind": "border", "width": 6.0, "alpha": 0.5, "pattern": (0.0, 1.15, 0.85, 0.0, False), "from": 240},
    "highway": {"kind": "road", "width": 20.0, "fill": "#ffc451", "casing": "#b5761a", "share": 0.28,
                "min_px": 4.0, "narrow": "#e09a2a", "from": 480},
    "road": {"kind": "road", "width": 14.0, "fill": "#fffaf0", "casing": "#9c8f7d", "share": 0.30,
             "min_px": 4.5, "narrow": "#a3958a", "from": 240},
    "lane": {"kind": "road", "width": 7.0, "fill": "#ffffff", "casing": "#b5aa9a", "share": 0.34,
             "min_px": 5.0, "narrow": "#b8ad9d", "from": 100},
    "thin river": {"kind": "solid", "width": 6.7, "color": "#6dc2f3", "from": 240},
    "great river": {"kind": "solid", "width": 24.8, "color": "#6dc2f3", "from": 9999},
}
ORDER = list(NOW)
GROUPS = {"borders": ["kingdom", "duchy", "county"], "roads": ["highway", "road", "lane"]}


def variant(changes=None, growth=None, fade=None, shown=None, ramp=None):
    """A variant: per-kind changes to NOW, 14's growth ({kind or group: (growth, neutral miles)}),
    its fade ({kind: (alpha at the closest, from miles, to miles)}), 19's tiers ({kind: miles
    under which it shows}) and ramps ({kind: (starts at miles, whole at miles)})."""
    lines = {k: dict(v) for k, v in NOW.items()}
    for kind, change in (changes or {}).items():
        for k in GROUPS.get(kind, [kind]):
            lines[k].update(change)
    for kind, miles in (shown or {}).items():
        for k in GROUPS.get(kind, [kind]):
            lines[k]["from"] = miles
    expanded = {}
    for kind, value in (growth or {}).items():
        for k in GROUPS.get(kind, [kind]):
            expanded[k] = value
    return {"lines": lines, "growth": expanded, "fade": fade or {}, "ramp": ramp or {}}


# The variants of 10, 14 and 19 revisited on 2026-10-19, as their style scripts set them
# (harness/styles/1NN_*.gd hold the same numbers).
FADE = {"kingdom": (0.55, 240.0, 25.0), "duchy": (0.7, 240.0, 25.0)}
# A county's dots 1.15 widths apart: the shader puts its gap on both sides of a dot.
DENSER_DOTS = (0.0, 0.575, 0.85, 0.0, False)
ROADS_HOLD = {"road": {"width": 16.0, "share": 0.5, "min_px": 3.0}, "lane": {"width": 8.0}}
VARIANTS = {
    "now": variant(),
    "10a": variant({"kingdom": {"width": 9.0, "alpha": 0.75}, "duchy": {"width": 6.0, "alpha": 0.65},
                    "county": {"width": 4.5}, "highway": {"width": 26.0}, "road": {"width": 16.0},
                    "lane": {"width": 7.875}}),
    "10b": variant(ROADS_HOLD),
    "10c": variant({"county": {"alpha": 0.65, "width": 7.0, "pattern": DENSER_DOTS}}),
    "14a": variant(fade=FADE),
    "14b": variant(growth={"borders": (0.3, 220.0)}, fade=FADE),
    "14c": variant(growth={"borders": (0.3, 220.0), "roads": (-0.1, 220.0)}, fade=FADE),
    "19a": variant(shown={"county": 100.0}),
    "19b": variant(shown={"lane": 50.0}),
    "19c": variant(shown={"county": 100.0, "lane": 50.0}),
    "19d": variant(ramp={"county": (240.0, 120.0), "lane": (100.0, 60.0)}),
    "together": variant(ROADS_HOLD, growth={"borders": (0.3, 220.0)}, fade=FADE, shown={"county": 100.0}),
}

# 19's layers, as MapDetail.SHOWN_FROM and its sizes have them: [name, shows under (miles)].
LAYERS = [
    ["Kingdom borders and capitals", 9999], ["Duchy borders and capitals", 480], ["Highways", 480],
    ["Large forests (50 to 250 km²)", 480], ["County borders", 240], ["Roads and their bridges", 240],
    ["County capitals", 240], ["Small forests (10 to 50 km²)", 240], ["Lakes 2 to 3 km across", 240],
    ["Villages", 100], ["Lanes and their bridges", 100], ["The Swamp's channels", 100],
    ["Woods (under 10 km²)", 100], ["Hamlets", 50],
]
# Each of 19's variants: {layer: miles it shows under} and {layer: (starts, whole) of a ramp}.
TIER_VARIANTS = {
    "now": ({}, {}),
    "19a": ({"County borders": 100}, {}),
    "19b": ({"Lanes and their bridges": 50}, {}),
    "19c": ({"County borders": 100, "Lanes and their bridges": 50, "Woods (under 10 km²)": 50,
             "Lakes 2 to 3 km across": 100}, {}),
    "19d": ({}, {"County borders": (240, 120), "Lanes and their bridges": (100, 60)}),
}


def hex_rgb(code):
    code = code.lstrip("#")
    return tuple(int(code[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lab(rgb):
    r, g, b = (to_linear(c) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116

    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def contrast(rgb):
    """CIE76 delta E from the white land, / 100."""
    l1, a1, b1 = lab(rgb)
    l2, a2, b2 = lab(WHITE)
    return math.sqrt((l1 - l2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2) / 100.0


def mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def smoothstep(e0, e1, x):
    t = min(max((x - e0) / (e1 - e0), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def coverage(pattern):
    """How much of a border's length and width its pattern inks (map_line.gdshader's
    dash, gap, dot, dot_gap, round_dashes): a dot is a disc, a round dash a capsule."""
    dash, gap, dot, dot_gap, round_dashes = pattern
    g2 = dot_gap if dot_gap > 0 else gap
    period = dash + gap + (dot + g2 if dot > 0 else 0.0)
    inked = 0.0
    if dash > 0:
        inked += (dash - 1.0 + math.pi * 0.25) if round_dashes else dash
    if dot > 0:
        inked += math.pi * (dot * 0.5) ** 2
    return inked / period


def px_per_unit(miles):
    """Screen pixels a unit of a node's width takes at a height, by MapDetail's one factor."""
    return (miles / TRUE_MILES) ** (1.0 - GROWTH) * SCREEN_H / (miles * UNITS_A_MILE)


def shown_share(v, kind, miles):
    """How far in a kind is at a height: 0 out of its tier, else 1, or a ramp's share."""
    line = v["lines"][kind]
    if miles >= line["from"]:
        return 0.0
    if kind in v["ramp"]:
        start, whole = v["ramp"][kind]
        if miles >= start:
            return 0.0
        return min(1.0, math.log(start / miles) / math.log(start / whole))
    return 1.0


def faded(v, kind, miles):
    """A border's alpha share under 14's fade: whole at and over `top` miles, `least` at and under
    `bottom`, by the logarithm of the height between."""
    if kind not in v["fade"]:
        return 1.0
    least, top, bottom = v["fade"][kind]
    if miles >= top:
        return 1.0
    if miles <= bottom:
        return least
    t = math.log(top / miles) / math.log(top / bottom)
    return 1.0 + (least - 1.0) * t


def measure(v, kind, miles):
    """[screen px, weight] of a kind at a height, or None when it is not shown."""
    share = shown_share(v, kind, miles)
    if share <= 0.0:
        return None
    line = v["lines"][kind]
    growth, neutral = v["growth"].get(kind, (0.0, TRUE_MILES))
    px = line["width"] * px_per_unit(miles) * (miles / neutral) ** growth
    if line["kind"] == "border":
        alpha = line["alpha"] * faded(v, kind, miles) * share
        ink = mix(WHITE, INK, alpha)
        return px, px * coverage(line["pattern"]) * contrast(ink)
    if line["kind"] == "solid":
        return px, px * contrast(mix(WHITE, hex_rgb(line["color"]), share))
    fill, casing, narrow = (hex_rgb(line[k]) for k in ("fill", "casing", "narrow"))
    room = smoothstep(line["min_px"], line["min_px"] + 2.0, px)
    edge_colour = mix(narrow, mix(fill, casing, room), room)
    fill_colour = mix(narrow, fill, room)
    edges = line["share"] * px
    weight = edges * contrast(mix(WHITE, edge_colour, share)) + (px - edges) * contrast(mix(WHITE, fill_colour, share))
    return px, weight


def table(names):
    for miles in HEIGHTS:
        print("At %.0f miles tall: screen px / weight" % miles)
        print()
        print("| Kind | " + " | ".join(names) + " |")
        print("|---|" + "---:|" * len(names))
        for kind in ORDER:
            cells = []
            for name in names:
                got = measure(VARIANTS[name], kind, miles)
                cells.append("" if got is None else "%.1f / %.2f" % got)
            print("| %s | %s |" % (kind, " | ".join(cells)))
        print()


# -- charts -------------------------------------------------------------------------------------

COLOURS = {
    "kingdom": (64, 51, 80), "duchy": (120, 100, 150), "county": (175, 160, 195),
    "highway": (224, 154, 42), "road": (140, 125, 105), "lane": (190, 178, 160),
    "thin river": (109, 194, 243), "great river": (40, 120, 200),
}
DASHES = {"kingdom": (14, 4), "duchy": (8, 5), "county": (2, 5)}


def chart_panel(draw, font, box, v, kinds, title, top):
    """One chart: weight by height, the height on a log scale from all the way out (left) to all
    the way in (right)."""
    from PIL import ImageDraw  # noqa: F401  (draw is an ImageDraw)
    x0, y0, x1, y1 = box
    left, right, bottom, up = x0 + 46, x1 - 10, y1 - 30, y0 + 26
    draw.text((x0 + 8, y0 + 4), title, fill=(20, 20, 24), font=font)
    lo, hi = 25.0, 832.0

    def x_of(miles):
        return left + (right - left) * math.log(hi / miles) / math.log(hi / lo)

    def y_of(w):
        return bottom - (bottom - up) * min(w / top, 1.0)

    for miles in (832, 480, 240, 100, 50, 25):
        x = x_of(miles)
        draw.line([(x, up), (x, bottom)], fill=(222, 222, 226))
        draw.text((x - 10, bottom + 6), "%d" % miles, fill=(90, 90, 96), font=font)
    for step in range(0, int(top) + 1):
        y = y_of(step)
        draw.line([(left, y), (right, y)], fill=(236, 236, 240))
        draw.text((x0 + 14, y - 7), "%d" % step, fill=(90, 90, 96), font=font)
    draw.rectangle([left, up, right, bottom], outline=(150, 150, 156))
    for kind in kinds:
        points = []
        miles = hi
        while miles >= lo * 0.999:
            got = measure(v, kind, miles)
            points.append(None if got is None else (x_of(miles), y_of(got[1])))
            miles /= 1.01
        run = []
        for p in points + [None]:
            if p is None:
                if len(run) > 1:
                    _polyline(draw, run, COLOURS[kind], DASHES.get(kind))
                run = []
            else:
                run.append(p)


def _polyline(draw, points, colour, dashes):
    if dashes is None:
        draw.line(points, fill=colour, width=3, joint="curve")
        return
    on, off = dashes
    gone, drawing = 0.0, True
    for a, b in zip(points, points[1:]):
        seg = math.dist(a, b)
        t = 0.0
        while t < seg:
            left = (on if drawing else off) - gone
            step = min(left, seg - t)
            if drawing:
                p = (a[0] + (b[0] - a[0]) * t / seg, a[1] + (b[1] - a[1]) * t / seg)
                q = (a[0] + (b[0] - a[0]) * (t + step) / seg, a[1] + (b[1] - a[1]) * (t + step) / seg)
                draw.line([p, q], fill=colour, width=3)
            t += step
            gone += step
            if gone >= (on if drawing else off) - 1e-9:
                gone, drawing = 0.0, not drawing


def ladder(out, names):
    """Every kind's weight by height, a panel a variant, with a key: what leads at each zoom."""
    from PIL import Image, ImageDraw, ImageFont
    font = _font(ImageFont, 15)
    w, h = 620, 330
    columns = min(len(names), 2)
    rows = math.ceil(len(names) / columns)
    key_h = 70
    image = Image.new("RGB", (w * columns, h * rows + key_h), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    for i, name in enumerate(names):
        box = ((i % columns) * w, (i // columns) * h, (i % columns + 1) * w, (i // columns + 1) * h)
        chart_panel(draw, font, box, VARIANTS[name], ORDER, "%s: weight (px of black) by the view's height (miles)" % name, 8.0)
    y = h * rows + 10
    x = 12
    for kind in ORDER:
        _polyline(draw, [(x, y + 10), (x + 40, y + 10)], COLOURS[kind], DASHES.get(kind))
        draw.text((x + 46, y + 2), kind, fill=(20, 20, 24), font=font)
        x += 46 + draw.textlength(kind, font=font) + 24
        if x > image.width - 160:
            x, y = 12, y + 26
    image.save(out)
    print("saved", out)


def tiers(out, names):
    """19's layers, a row each, with a bar over the heights of the view it shows at, a panel a
    variant: grey where it is as now, orange where the variant changes it, a ramp fading in."""
    from PIL import Image, ImageDraw, ImageFont
    font = _font(ImageFont, 15)
    bold = _font(ImageFont, 17)
    label_w, chart_w, row_h, head, foot = 250, 760, 20, 52, 26
    panel_h = head + row_h * len(LAYERS) + foot
    image = Image.new("RGB", (label_w + chart_w + 20, panel_h * len(names)), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    lo, hi = 25.0, 832.0
    left, right = label_w, label_w + chart_w - 10

    def x_of(miles):
        miles = min(max(miles, lo), hi)
        return left + (right - left) * math.log(hi / miles) / math.log(hi / lo)

    titles = {"now": "The map as it is now", "19a": "19a  County borders at the County tier",
              "19b": "19b  Lanes with the hamlets", "19c": "19c  19 in full, small lakes at 3 km",
              "19d": "19d  Ramps, not steps"}
    for p, name in enumerate(names):
        y0 = p * panel_h
        shown, ramps = TIER_VARIANTS[name]
        draw.text((10, y0 + 8), titles.get(name, name), fill=(20, 20, 24), font=bold)
        bottom = y0 + head + row_h * len(LAYERS)
        for a, b, tier in ((832, 480, "Realm"), (480, 240, "Kingdom"), (240, 100, "Duchy"), (100, 25, "County")):
            mid = (x_of(a) + x_of(b)) / 2
            draw.text((mid - draw.textlength(tier, font=font) / 2, y0 + head - 22), tier, fill=(90, 90, 96), font=font)
        for miles in (480, 240, 100, 50):
            x = x_of(miles)
            draw.line([(x, y0 + head - 4), (x, bottom)], fill=(205, 205, 212))
            draw.text((x - 10, bottom + 4), "%d mi" % miles, fill=(90, 90, 96), font=font)
        draw.text((left, bottom + 4), "all the way out", fill=(90, 90, 96), font=font)
        draw.text((right - draw.textlength("all the way in", font=font), bottom + 4), "all the way in",
                  fill=(90, 90, 96), font=font)
        for r, (layer, under) in enumerate(LAYERS):
            y = y0 + head + r * row_h
            changed = layer in shown or layer in ramps
            draw.text((10, y + 1), layer, fill=(20, 20, 24) if changed else (70, 70, 76), font=font)
            colour = (232, 140, 40) if changed else (160, 160, 168)
            if layer in ramps:
                start, whole = ramps[layer]
                xs, xw = x_of(start), x_of(whole)
                for x in range(int(xs), int(xw) + 1):
                    t = (x - xs) / max(xw - xs, 1.0)
                    draw.line([(x, y + 4), (x, y + row_h - 4)], fill=tuple(int(255 + (c - 255) * t) for c in colour))
                draw.rectangle([xw, y + 4, right, y + row_h - 4], fill=colour)
            else:
                draw.rectangle([x_of(shown.get(layer, under)), y + 4, right, y + row_h - 4], fill=colour)
    image.save(out)
    print("saved", out)


def _font(image_font, size):
    for name in ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"):
        try:
            return image_font.truetype(name, size)
        except OSError:
            continue
    return image_font.load_default()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    mode = sys.argv[1]
    if mode == "table":
        table(sys.argv[2:] or list(VARIANTS))
    elif mode == "ladder":
        ladder(sys.argv[2], sys.argv[3:] or list(VARIANTS))
    elif mode == "tiers":
        tiers(sys.argv[2], sys.argv[3:] or list(TIER_VARIANTS))
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
