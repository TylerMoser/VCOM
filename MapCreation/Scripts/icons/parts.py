"""Buildings and other things to make settlements' icons of, each drawn on to an Icon.

Every one takes the icon, where it stands (x, the middle of its foot, in the pack's pixels to the
right of the icon's middle), its sizes, and "behind": the ink layer to join, or None to stand as a
layer of its own in front of what is there. All return the layer they drew on.
"""
import numpy as np
from kit import box, oval, arch, star


def _layer(ic, join):
    return join if join is not None else ic.layer()


def house(ic, x, w=110, wall=50, roof=60, eave=13, chimney=1, door=True, window=False, y=0.0, join=None):
    """A house seen end on: wall, a pointed gable with eaves, a chimney on one slope (1 right, -1 left, 0 none)."""
    L = _layer(ic, join)
    L["add"].append(box(x - w / 2, y, x + w / 2, y + wall + 6))
    L["add"].append([(x - w / 2 - eave, y + wall - 9), (x - w / 2 - eave - 3, y + wall + 7), (x - 4, y + wall + roof), (x + 4, y + wall + roof),
                     (x + w / 2 + eave + 3, y + wall + 7), (x + w / 2 + eave, y + wall - 9)])
    if chimney:
        cx = x + chimney * w * 0.27
        L["add"].append(box(cx - 10, y + wall + roof * 0.25, cx + 10, y + wall + roof * 1.0))
    if door:
        L["cut"].append(arch(x - (w * 0.12 if window else 0.0), 16, wall * 0.78, y))
    if window:
        L["cut"].append(oval(x + w * 0.2, y + wall * 0.55, 6.5, 9))
    return L


def house_side(ic, x, w=150, wall=46, roof=44, lean=26, eave=10, chimney=1, door=True, windows=0, y=0.0, join=None):
    """A house seen from the side: a long wall under a roof that slopes in at both ends."""
    L = _layer(ic, join)
    L["add"].append(box(x - w / 2, y, x + w / 2, y + wall + 4))
    L["add"].append([(x - w / 2 - eave, y + wall - 8), (x - w / 2 - eave - 2, y + wall + 6), (x - w / 2 + lean, y + wall + roof), (x + w / 2 - lean, y + wall + roof),
                     (x + w / 2 + eave + 2, y + wall + 6), (x + w / 2 + eave, y + wall - 8)])
    if chimney:
        cx = x + chimney * (w / 2 - lean - 14)
        L["add"].append(box(cx - 9, y + wall + roof * 0.5, cx + 9, y + wall + roof + 18))
    if door:
        L["cut"].append(arch(x - w * 0.22, 16, wall * 0.8, y))
    for i in range(windows):
        L["cut"].append(oval(x + w * (0.05 + 0.2 * i), y + wall * 0.55, 6, 8))
    return L


def hut(ic, x, w=84, wall=30, roof=66, eave=16, door=True, y=0.0, join=None):
    """A round hut: a low wall under a tall thatch."""
    L = _layer(ic, join)
    L["add"].append(box(x - w / 2, y, x + w / 2, y + wall + 6))
    L["add"].append([(x - w / 2 - eave, y + wall - 10), (x - w / 2 - eave - 2, y + wall + 6), (x - w * 0.3, y + wall + roof * 0.5), (x - 5, y + wall + roof), (x + 5, y + wall + roof),
                     (x + w * 0.3, y + wall + roof * 0.5), (x + w / 2 + eave + 2, y + wall + 6), (x + w / 2 + eave, y + wall - 10)])
    if door:
        L["cut"].append(arch(x, 16, wall * 0.95, y))
    return L


def tent(ic, x, w=96, h=78, y=0.0, join=None):
    L = _layer(ic, join)
    L["add"].append([(x - w / 2, y), (x - 6, y + h), (x - 12, y + h + 14), (x, y + h + 4), (x + 12, y + h + 14), (x + 6, y + h), (x + w / 2, y)])
    L["cut"].append([(x - 11, y - 2), (x, y + h * 0.6), (x + 11, y - 2)])
    return L


def barn(ic, x, w=128, wall=44, roof=62, door=True, y=0.0, join=None):
    """A barn: a broad front under a roof that breaks half way up."""
    L = _layer(ic, join)
    L["add"].append([(x - w / 2, y), (x - w / 2, y + wall), (x - w / 2 - 8, y + wall - 2), (x - w * 0.3, y + wall + roof * 0.62), (x, y + wall + roof),
                     (x + w * 0.3, y + wall + roof * 0.62), (x + w / 2 + 8, y + wall - 2), (x + w / 2, y + wall), (x + w / 2, y)])
    if door:
        L["cut"].append(box(x - 17, y - 2, x + 17, y + wall * 0.82))
        L["add"].append(box(x - 3.5, y, x + 3.5, y + wall * 0.82))
    L["cut"].append(oval(x, y + wall + roof * 0.42, 8, 8))
    return L


def longhouse(ic, x, w=190, wall=30, roof=50, door=True, y=0.0, join=None):
    """A long hall under a low sweeping thatch."""
    L = _layer(ic, join)
    L["add"].append(box(x - w / 2 + 8, y, x + w / 2 - 8, y + wall + 6))
    L["add"].append([(x - w / 2 - 6, y + wall - 4), (x - w / 2 + 18, y + wall + roof * 0.8), (x - w / 2 + 6, y + wall + roof + 14), (x - w / 2 + 30, y + wall + roof),
                     (x + w / 2 - 30, y + wall + roof), (x + w / 2 - 6, y + wall + roof + 14), (x + w / 2 - 18, y + wall + roof * 0.8), (x + w / 2 + 6, y + wall - 4)])
    if door:
        L["cut"].append(arch(x, 17, wall * 0.95, y))
    return L


def haystack(ic, x, w=56, h=46, y=0.0, join=None):
    L = _layer(ic, join)
    L["add"].append(oval(x, y, w / 2, h, 30, 0, 180) + [(x - w / 2, y), (x + w / 2, y)])
    return L


def well(ic, x, y=0.0, join=None):
    L = _layer(ic, join)
    L["add"].append(box(x - 28, y, x + 28, y + 26))
    L["add"].append(box(x - 27, y + 22, x - 18, y + 68))
    L["add"].append(box(x + 18, y + 22, x + 27, y + 68))
    L["add"].append([(x - 42, y + 60), (x - 40, y + 72), (x, y + 98), (x + 40, y + 72), (x + 42, y + 60)])
    return L


def fence(ic, x0, x1, h=30, y=0.0, join=None):
    L = _layer(ic, join)
    L["add"].append(box(x0, y + h * 0.42, x1, y + h * 0.42 + 9))
    n = max(2, int(round((x1 - x0) / 26.0)) + 1)
    for px in np.linspace(x0 + 5, x1 - 5, n):
        L["add"].append([(px - 5, y), (px - 5, y + h - 4), (px, y + h + 4), (px + 5, y + h - 4), (px + 5, y)])
    return L


def windmill(ic, x, h=110, w=58, y=0.0, join=None):
    """A windmill: a tapering body, a cap and four sails."""
    L = _layer(ic, join)
    L["add"].append([(x - w / 2, y), (x - w * 0.3, y + h), (x + w * 0.3, y + h), (x + w / 2, y)])
    L["add"].append(oval(x, y + h - 4, w * 0.36, 24, 24, 0, 180))
    hub = (x, y + h + 2)
    for turn in (35, 125, 215, 305):
        a = np.radians(turn)
        along = np.array([np.cos(a), np.sin(a)])
        across = np.array([-np.sin(a), np.cos(a)])
        L["add"].append([tuple(hub + across * 4.5), tuple(hub + along * 78 + across * 4.5), tuple(hub + along * 78 - across * 4.5), tuple(hub - across * 4.5)])
        L["add"].append([tuple(hub + along * 28 + across * 4), tuple(hub + along * 76 + across * 4), tuple(hub + along * 76 + across * 26), tuple(hub + along * 28 + across * 20)])
    L["cut"].append(arch(x, 15, 34, y))
    return L


def tower(ic, x, w=58, h=150, roof="cone", rh=84, eave=16, door=True, window=True, y=0.0, join=None):
    """A tower. Its top is a cone (with eaves), battlements ("flat"), a dome, or a thin spire."""
    L = _layer(ic, join)
    L["add"].append(box(x - w / 2, y, x + w / 2, y + h + 4))
    if roof == "cone":
        L["add"].append([(x - w / 2 - eave, y + h - 10), (x - w / 2 - eave - 2, y + h + 6), (x - w * 0.24, y + h + rh * 0.5), (x - 4, y + h + rh), (x + 4, y + h + rh),
                         (x + w * 0.24, y + h + rh * 0.5), (x + w / 2 + eave + 2, y + h + 6), (x + w / 2 + eave, y + h - 10)])
    elif roof == "flat":
        L["add"].append(box(x - w / 2 - 8, y + h - 4, x + w / 2 + 8, y + h + 14))
        n = max(2, int(round((w + 16) / 30.0)))
        each = (w + 16) / (2 * n - 1)
        for i in range(n):
            x0 = x - w / 2 - 8 + i * 2 * each
            L["add"].append(box(x0, y + h + 10, x0 + each, y + h + 34))
    elif roof == "dome":
        L["add"].append(oval(x, y + h, w / 2 + 6, rh * 0.62, 30, 0, 180))
        L["add"].append(box(x - 4.5, y + h + rh * 0.5, x + 4.5, y + h + rh))
        L["add"].append(oval(x, y + h + rh, 8, 8))
    elif roof == "spire":
        L["add"].append([(x - w / 2 - 6, y + h - 4), (x - 4, y + h + rh), (x + 4, y + h + rh), (x + w / 2 + 6, y + h - 4)])
    if door:
        L["cut"].append(arch(x, 15, min(40.0, h * 0.4), y))
    if window:
        L["cut"].append(oval(x, y + h * 0.72, 5.5, 11))
    return L


def keep(ic, x, w=120, h=120, door=True, windows=2, y=0.0, join=None):
    """A square keep with battlements."""
    L = tower(ic, x, w, h, "flat", door=False, window=False, y=y, join=join)
    if door:
        L["cut"].append(arch(x, 24, h * 0.36, y))
    for i in range(windows):
        wx = x + (i - (windows - 1) / 2.0) * w * 0.42
        L["cut"].append(oval(wx, y + h * 0.66, 5.5, 11))
    return L


def wall(ic, x0, x1, h=56, gate=None, y=0.0, join=None):
    """A battlemented wall from x0 to x1, with a gateway at gate (an x) if given."""
    L = _layer(ic, join)
    L["add"].append(box(x0, y, x1, y + h))
    n = max(2, int(round((x1 - x0 + 15.0) / 39.0)))
    gap = 15.0
    each = (x1 - x0 - gap * (n - 1)) / n
    for i in range(n):
        L["add"].append(box(x0 + i * (each + gap), y + h - 4, x0 + i * (each + gap) + each, y + h + 19))
    if gate is not None:
        L["cut"].append(arch(gate, 26, h * 0.7, y))
    return L


def church(ic, x, w=130, wall=50, roof=46, steeple=1, tw=44, th=110, spire=70, cross=True, y=0.0, join=None):
    """A church: a nave seen from the side, and at one end (1 right, -1 left) a tower with a spire and a cross."""
    L = _layer(ic, join)
    L["add"].append(box(x - w / 2, y, x + w / 2, y + wall + 4))
    L["add"].append([(x - w / 2 - 8, y + wall - 2), (x - w / 2 + 20, y + wall + roof), (x + w / 2 - 20, y + wall + roof), (x + w / 2 + 8, y + wall - 2)])
    tx = x + steeple * (w / 2 - tw / 2 + 6)
    L["add"].append(box(tx - tw / 2, y, tx + tw / 2, y + th))
    L["add"].append([(tx - tw / 2 - 7, y + th - 4), (tx - 4, y + th + spire), (tx + 4, y + th + spire), (tx + tw / 2 + 7, y + th - 4)])
    if cross:
        top = y + th + spire
        L["add"].append(box(tx - 4.5, top - 6, tx + 4.5, top + 34))
        L["add"].append(box(tx - 15, top + 12, tx + 15, top + 21))
    L["cut"].append(arch(tx, 15, 36, y))
    L["cut"].append(oval(tx, y + th * 0.72, 5.5, 10))
    for i in range(2):
        L["cut"].append(oval(x - steeple * (w * 0.08 + i * w * 0.24), y + wall * 0.55, 6, 10))
    return L


def cathedral(ic, x, w=170, wall=74, roof=56, tw=46, th=150, spire=92, y=0.0, join=None):
    """A great church: a tall gabled front between two spired towers."""
    L = _layer(ic, join)
    L["add"].append([(x - w / 2, y), (x - w / 2, y + wall), (x, y + wall + roof), (x + w / 2, y + wall), (x + w / 2, y)])
    for side in (-1, 1):
        tx = x + side * (w / 2 + tw / 2 - 10)
        L["add"].append(box(tx - tw / 2, y, tx + tw / 2, y + th))
        L["add"].append([(tx - tw / 2 - 7, y + th - 4), (tx - 4, y + th + spire), (tx + 4, y + th + spire), (tx + tw / 2 + 7, y + th - 4)])
        L["cut"].append(oval(tx, y + th * 0.74, 5.5, 11))
    L["cut"].append(arch(x, 26, wall * 0.5, y))
    L["cut"].append(oval(x, y + wall * 0.86, 13, 13))
    return L


def hall(ic, x, w=150, wall=62, roof=52, y=0.0, join=None):
    """A great hall: a broad gabled front with a tall doorway and a turret on the ridge."""
    L = house(ic, x, w, wall, roof, eave=10, chimney=0, door=False, y=y, join=join)
    L["add"].append(box(x - 9, y + wall + roof - 6, x + 9, y + wall + roof + 22))
    L["add"].append([(x - 16, y + wall + roof + 18), (x, y + wall + roof + 48), (x + 16, y + wall + roof + 18)])
    L["cut"].append(arch(x, 24, wall * 0.62, y))
    for side in (-1, 1):
        L["cut"].append(oval(x + side * w * 0.3, y + wall * 0.55, 6, 10))
    return L


def dome(ic, x, w=120, wall=56, rise=60, y=0.0, join=None):
    """A domed hall."""
    L = _layer(ic, join)
    L["add"].append(box(x - w / 2, y, x + w / 2, y + wall))
    L["add"].append(oval(x, y + wall - 2, w / 2 - 8, rise, 36, 0, 180))
    L["add"].append(box(x - 4.5, y + wall + rise - 6, x + 4.5, y + wall + rise + 26))
    L["add"].append(oval(x, y + wall + rise + 26, 8, 8))
    L["cut"].append(arch(x, 22, wall * 0.66, y))
    return L


def gatehouse(ic, x, w=120, h=84, tw=40, th=120, y=0.0, join=None):
    """A gate between two battlemented turrets."""
    L = _layer(ic, join)
    L["add"].append(box(x - w / 2, y, x + w / 2, y + h))
    for side in (-1, 1):
        tower(ic, x + side * (w / 2), tw, th, "flat", door=False, window=False, y=y, join=L)
    L["cut"].append(arch(x, 30, h * 0.72, y))
    return L


def pennant(ic, x, y, pole=44, fly=34, drop=22, way=1, join=None):
    """A black flag on a pole, its foot at (x, y), flying right (1) or left (-1)."""
    L = _layer(ic, join)
    L["add"].append(box(x - 4, y, x + 4, y + pole))
    L["add"].append([(x, y + pole), (x + way * fly, y + pole - drop / 2), (x, y + pole - drop)])
    return L


def crown(points=5, w=150, band=30, rise=58, balls=True, cx=0.0, y=0.0):
    """A crown's outline: a band, and points rising from it (the middle ones tallest). Returns outlines to add."""
    out = [box(cx - w / 2, y, cx + w / 2, y + band)]
    xs = np.linspace(cx - w / 2, cx + w / 2, points * 2 + 1)
    tops = []
    line = [(cx - w / 2, y + band - 2)]
    for i in range(points):
        mid = abs(i - (points - 1) / 2.0) / max((points - 1) / 2.0, 1.0)
        top = y + band + rise * (1.0 - 0.28 * mid)
        line += [(xs[2 * i + 1], top)]
        if i < points - 1:
            line += [(xs[2 * i + 2], y + band + rise * 0.22)]
        tops.append((xs[2 * i + 1], top))
    line += [(cx + w / 2, y + band - 2)]
    out.append(line)
    if balls:
        for tx, ty in tops:
            out.append(oval(tx, ty + 3, 9, 9))
    return out
