"""How far apart the map's line colours are, as everyone sees them and with deuteranopia: each colour's
CIELAB lightness (L*), and the CIEDE2000 difference between every pair (about 2 is just noticeable
side by side; under about 10 two thin lines are easily mistaken for each other at a glance).

The simulation is Machado, Oliveira and Fernandes (2009) at full strength, as cvd_filter.gdshader.

usage: py -3.14 colour_check.py [current|recommended]
"""
import math
import sys

CURRENT = {
    "kingdom border": (0.9137255, 0.0, 1.0),
    "duchy border": (0.43137255, 0.11764706, 0.7058824),
    "county border": (0.5019608, 0.5019608, 0.5019608),
    "river": (0.10980392, 0.4392157, 0.8784314),
    "road": (0.78431374, 0.15686275, 0.11764706),
    "bridge": (0.23529412, 0.13725491, 0.05882353),
    "coast": (0.0, 0.0, 0.0),
    "party": (0.85, 0.1, 0.1),
}
## The recommended blend (28), each line as it shows over the land (alpha blended over its ground).
RECOMMENDED = {
    "kingdom border": (0.27 * 0.72 + 0.98 * 0.28, 0.22 * 0.72 + 0.972 * 0.28, 0.33 * 0.72 + 0.937 * 0.28),
    "duchy border": (0.27 * 0.55 + 0.98 * 0.45, 0.22 * 0.55 + 0.972 * 0.45, 0.33 * 0.55 + 0.937 * 0.45),
    "county border": (0.27 * 0.38 + 0.98 * 0.62, 0.22 * 0.38 + 0.972 * 0.62, 0.33 * 0.38 + 0.937 * 0.62),
    "river": (0x6f / 255, 0xae / 255, 0xe3 / 255),
    "highway": (0xff / 255, 0xc4 / 255, 0x51 / 255),
    "road casing": (0x9c / 255, 0x8f / 255, 0x7d / 255),
    "lane casing": (0xb5 / 255, 0xaa / 255, 0x9a / 255),
    "route": (0x1a / 255, 0x73 / 255, 0xe8 / 255),
    "route in forest": (0xd9 / 255, 0x3a / 255, 0x2b / 255),
}
DEUTAN = ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881))


def to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def to_srgb(c):
    c = min(max(c, 0.0), 1.0)
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def deutan(rgb):
    lin = [to_linear(c) for c in rgb]
    return tuple(to_srgb(sum(row[i] * lin[i] for i in range(3))) for row in DEUTAN)


def lab(rgb):
    r, g, b = (to_linear(c) for c in rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116

    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def ciede2000(lab1, lab2):
    l1, a1, b1 = lab1
    l2, a2, b2 = lab2
    c1, c2 = math.hypot(a1, b1), math.hypot(a2, b2)
    cbar = (c1 + c2) / 2
    g = 0.5 * (1 - math.sqrt(cbar ** 7 / (cbar ** 7 + 25 ** 7)))
    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dl, dc = l2 - l1, c2p - c1p
    dh = h2p - h1p
    if c1p * c2p == 0:
        dh = 0
    elif dh > 180:
        dh -= 360
    elif dh < -180:
        dh += 360
    dhh = 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(dh / 2))
    lbar, cbarp = (l1 + l2) / 2, (c1p + c2p) / 2
    if c1p * c2p == 0:
        hbar = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbar = (h1p + h2p) / 2
    else:
        hbar = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    t = (1 - 0.17 * math.cos(math.radians(hbar - 30)) + 0.24 * math.cos(math.radians(2 * hbar))
         + 0.32 * math.cos(math.radians(3 * hbar + 6)) - 0.20 * math.cos(math.radians(4 * hbar - 63)))
    sl = 1 + 0.015 * (lbar - 50) ** 2 / math.sqrt(20 + (lbar - 50) ** 2)
    sc = 1 + 0.045 * cbarp
    sh = 1 + 0.015 * cbarp * t
    rt = (-2 * math.sqrt(cbarp ** 7 / (cbarp ** 7 + 25 ** 7))
          * math.sin(math.radians(60 * math.exp(-(((hbar - 275) / 25) ** 2)))))
    return math.sqrt((dl / sl) ** 2 + (dc / sc) ** 2 + (dhh / sh) ** 2 + rt * (dc / sc) * (dhh / sh))


def main():
    colours = RECOMMENDED if len(sys.argv) > 1 and sys.argv[1] == "recommended" else CURRENT
    names = list(colours)
    print("| Colour | L* | L* with deuteranopia |")
    print("|---|---:|---:|")
    for n in names:
        print("| %s | %.0f | %.0f |" % (n, lab(colours[n])[0], lab(deutan(colours[n]))[0]))
    print()
    print("Pairs closest together (CIEDE2000), normal vision / deuteranopia:")
    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            normal = ciede2000(lab(colours[a]), lab(colours[b]))
            cvd = ciede2000(lab(deutan(colours[a])), lab(deutan(colours[b])))
            pairs.append((cvd, normal, a, b))
    pairs.sort()
    for cvd, normal, a, b in pairs[:12]:
        print("  %-16s %-16s %5.1f  %5.1f" % (a, b, normal, cvd))


if __name__ == "__main__":
    main()
