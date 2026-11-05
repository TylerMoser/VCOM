"""What a species adds to the body: tails, wings, shells, spines, fins, manes, whiskers,
antennae, claws, and the patterns of a hide. Each says which bone it rides on: a tail the
hips, a shell or a back's wings the chest, feathers or a membrane under an arm the arm's
bones (behind the body, y 18 and more, where a lowered arm folds them across the back),
whatever is on the head the head."""
import math

from core import shade, mix, MID
from outfits import arm_side_bone


def h(p, seed=0):
    """A deterministic hash of a position, 0..1."""
    x, y, z = p
    n = (x * 73856093) ^ (y * 19349663) ^ (z * 83492791) ^ (seed * 2654435761)
    n = (n ^ (n >> 13)) * 1274126177
    return ((n ^ (n >> 16)) & 0xffff) / 0xffff


def arm_room(p):
    """Whether [p] is where a lowered arm hangs and swings (x 12-13 and 19-20, y 14-18, z 9-16):
    nothing riding on the torso may be there."""
    return p[0] in (12, 13, 19, 20) and 14 <= p[1] <= 18 and 9 <= p[2] <= 16


# --- Sweeps --------------------------------------------------------------------------------

def sweep(m, path, color, group, bone, only_empty=True, step=0.2, sym=False):
    """Fills the union of ellipsoids along a path of control points (x, y, z, rx, ry, rz),
    interpolated; [color] is a colour or a function (t, p) -> colour, t from 0 at the path's
    start to 1 at its end."""
    segs = []
    total = 0.0
    for a, b in zip(path, path[1:]):
        d = math.dist(a[:3], b[:3])
        segs.append((a, b, d))
        total += d
    filled = {}
    walked = 0.0
    for a, b, d in segs:
        n = max(1, int(d / step))
        for i in range(n + 1):
            t = i / n
            q = [a[k] + (b[k] - a[k]) * t for k in range(6)]
            tt = (walked + d * t) / total if total else 0
            cx, cy, cz, rx, ry, rz = q
            for x in range(int(math.floor(cx - rx)) - 1, int(math.ceil(cx + rx)) + 2):
                for y in range(int(math.floor(cy - ry)) - 1, int(math.ceil(cy + ry)) + 2):
                    for z in range(int(math.floor(cz - rz)) - 1, int(math.ceil(cz + rz)) + 2):
                        dd = ((x + 0.5 - cx) / max(rx, 0.01)) ** 2 + ((y + 0.5 - cy) / max(ry, 0.01)) ** 2 + ((z + 0.5 - cz) / max(rz, 0.01)) ** 2
                        if dd <= 1.0:
                            p = (x, y, z)
                            if p not in filled or tt < filled[p]:
                                filled[p] = tt
        walked += d
    for p, tt in filled.items():
        if only_empty and m.has(p):
            continue
        if bone in ('Chest', 'Spine', 'Hips') and arm_room(p):
            continue  # a lowered arm hangs there
        c = color(tt, p) if callable(color) else color
        if c is None:
            continue
        m.set(p, c, group, bone)
        if sym and p[0] != 32 - p[0]:
            q = (32 - p[0], p[1], p[2])
            if not (only_empty and m.has(q)):
                from core import mirror_bone
                m.set(q, c, group, mirror_bone(bone))
    return filled


def tip_color(base, tip, at=0.8):
    return lambda t, p: tip if t >= at else base


def ringed(base, ring, period=3, tip=None, at=0.85):
    def f(t, p):
        if tip and t >= at:
            return tip
        return ring if int(t * 20) % period == 0 else base
    return f


# --- Tails (on the hips) -------------------------------------------------------------------

def tail(m, style, color, tip=None, group='fur', second=None):
    """Tails from the hips' back (y 18, z 9-11). Styles: thin (a rat's, a long curve near
    the ground), cat (thin, rising in an S), lizard (thick, tapering to the ground behind),
    croc (heavy, with a ridge of scutes), bushy (a squirrel's, up the back behind the head),
    fox (full, sweeping out and down), dog (short, up), curl (a husky's, over the back),
    stub (a rabbit's ball), beaver (a flat paddle), otter (thick, long, low), tuft (a cow's,
    thin with a tuft), monkey (long and curling up), ringed (a lemur's), fish (a short tail
    and fin), shark (a crescent fin), chameleon (a spiral), feathers (a fan), long_feathers
    (a roadrunner's, up), club (an ankylosaur's), spikes (a stegosaur's), snake (long, on the
    ground), devil (thin with a spade), seal (two flippers)."""
    tip = tip or shade(color, 0.85)
    second = second or shade(color, 1.2)
    B = 'Hips'
    if style == 'thin':
        sweep(m, [(16, 18, 9.5, .6, .6, .6), (16, 21, 7, .6, .6, .6), (16, 24, 4, .55, .55, .55), (16, 27, 2.5, .5, .5, .5), (17, 30, 3, .5, .5, .5)], tip_color(color, tip, 0.9), group, B)
    elif style == 'cat':
        sweep(m, [(16, 18, 9.5, .7, .7, .7), (16, 21, 9, .7, .7, .7), (16, 23, 12, .7, .7, .7), (16, 23, 16, .7, .7, .7), (16, 25, 19, .7, .7, .7), (16, 27, 20, .65, .65, .65)], tip_color(color, tip, 0.85), group, B)
    elif style == 'lizard':
        sweep(m, [(16, 18, 10, 1.9, 1.6, 1.7), (16, 21, 8, 1.6, 1.6, 1.5), (16, 24, 5, 1.1, 1.2, 1.1), (16, 27, 2.5, .8, .8, .8), (16, 30, 1, .55, .6, .55)], tip_color(color, tip, 0.85), group, B)
    elif style == 'croc':
        sweep(m, [(16, 18, 10, 2.2, 1.8, 1.9), (16, 21, 7.5, 1.9, 1.8, 1.6), (16, 25, 4, 1.4, 1.5, 1.2), (16, 29, 1.5, .9, 1.2, .8), (16, 31, .8, .55, .6, .55)], color, group, B)
        for y, z in ((19, 12), (21, 10), (23, 8), (25, 6), (27, 4), (29, 3)):
            m.set((15, y, z), tip, 'scale', B)
            m.set((17, y, z), tip, 'scale', B)
    elif style == 'bushy':
        f = lambda t, p: tip if (t > 0.92 or h(p, 3) > 0.86) else (second if h(p, 5) > 0.8 else color)
        sweep(m, [(16, 18.5, 9, 1.4, 1.4, 1.4), (16, 21, 9, 2.2, 2, 2.2), (16, 23, 12, 2.8, 2.6, 2.8), (16, 23.5, 17, 3, 2.6, 3), (16, 23, 22, 2.8, 2.6, 2.8), (16, 22, 26, 2.4, 2.3, 2.4), (16, 20.5, 28, 1.6, 1.6, 1.6)], f, group, B)
    elif style == 'fox':
        sweep(m, [(16, 18.5, 9.5, 1.2, 1.2, 1.2), (16, 21, 8, 2.1, 2, 2.1), (16, 24, 6, 2.5, 2.3, 2.4), (16, 27, 4, 2.2, 2, 2.0), (16, 29, 3, 1.3, 1.3, 1.3)], tip_color(color, tip, 0.78), group, B)
    elif style == 'dog':
        sweep(m, [(16, 18, 10, 1, 1, 1), (16, 20, 11.5, 1.1, 1.1, 1.1), (16, 21.5, 14, 1, 1, 1), (16, 22, 16, .8, .8, .8)], tip_color(color, tip, 0.85), group, B)
    elif style == 'curl':
        sweep(m, [(16, 18, 10, 1.3, 1.3, 1.3), (16, 20.5, 12, 1.6, 1.6, 1.6), (16, 21.5, 15, 1.6, 1.6, 1.6), (16, 20.5, 17, 1.4, 1.4, 1.4), (16, 19.5, 15.5, 1.1, 1.1, 1.1)], tip_color(color, tip, 0.8), group, B)
    elif style == 'stub':
        m.ellipsoid(16, 18.8, 10, 1.6, 1.4, 1.6, tip if tip else color, group, B, only_empty=True)
    elif style == 'beaver':
        sweep(m, [(16, 18, 9.5, 1, 1, 1), (16, 20, 8, 1, 1, .9)], color, group, B)
        for y in range(20, 28):
            w = 3 if 21 <= y <= 26 else 2
            for x in range(16 - w, 17 + w):
                z = max(1, 7 - (y - 20) // 2)
                c = shade(tip, 0.85) if (x + y) % 2 == 0 else tip
                m.set((x, y, z), c, 'scale', B)
    elif style == 'otter':
        sweep(m, [(16, 18, 9.5, 1.7, 1.5, 1.6), (16, 21, 7, 1.5, 1.5, 1.3), (16, 24, 4, 1.1, 1.2, .9), (16, 27, 2, .8, .8, .7), (16, 29, 1.2, .55, .6, .5)], tip_color(color, tip, 0.9), group, B)
    elif style == 'tuft':
        sweep(m, [(16, 18, 10, .6, .6, .6), (16, 20, 8, .6, .6, .6), (16, 21, 5, .6, .6, .6), (16, 21.5, 3.5, .6, .6, .6)], color, group, B)
        m.ellipsoid(16, 21.6, 2.4, 1.1, 1.1, 1.4, tip, 'hair', B, only_empty=True)
    elif style == 'monkey':
        pts = [(16, 18, 9.5), (16, 21, 8), (16, 24, 8), (16, 26, 10.5), (16, 26.5, 14), (16, 25, 16.5), (16, 23, 16.5), (16, 22.3, 14.6), (16, 23.5, 13.4)]
        sweep(m, [(x, y, z, .65, .65, .65) for x, y, z in pts], tip_color(color, tip, 0.9), group, B)
    elif style == 'ringed':
        f = lambda t, p: tip if t > 0.9 else (second if int(t * 14) % 2 else color)
        sweep(m, [(16, 18.5, 9.5, 1, 1, 1), (16, 21, 8.5, 1.4, 1.4, 1.4), (16, 23.5, 10, 1.5, 1.5, 1.5), (16, 25, 14, 1.5, 1.5, 1.5), (16, 25, 18, 1.4, 1.4, 1.4), (16, 24, 22, 1.2, 1.2, 1.2)], f, group, B)
    elif style == 'fish':
        sweep(m, [(16, 18, 9.5, 1, 1, 1.2), (16, 20, 8.5, .8, .8, 1), (16, 21.5, 8, .6, .6, .7)], color, group, B)
        for dz in range(-3, 4):
            for dy in range(0, 3 - abs(dz) // 2):
                m.set((16, 22 + dy, 8 + dz), tip if abs(dz) >= 2 or dy == 2 else color, group, B)
    elif style == 'shark':
        sweep(m, [(16, 18, 10, 1.4, 1.3, 1.5), (16, 21, 8.5, 1.1, 1.2, 1.2), (16, 24, 7.5, .7, .8, .8)], color, group, B)
        for k in range(6):
            m.set((16, 25 + k // 3, 8 + k), color if k < 5 else tip, group, B)
            if k < 4:
                m.set((16, 26 + k // 3, 8 + k), color, group, B)
        for k in range(4):
            m.set((16, 25 + k // 2, 7 - k), color if k < 3 else tip, group, B)
    elif style == 'chameleon':
        pts = [(16, 18, 9.5, 1.2, 1.2, 1.2), (16, 21, 8, 1.1, 1.1, 1.1), (16, 23.5, 6.5, 1, 1, 1), (16, 25.5, 5.5, .9, .9, .9),
               (16, 27, 3.8, .8, .8, .8), (16, 26.5, 2, .7, .7, .7), (16, 25, 1.6, .7, .7, .7), (16, 24.2, 2.8, .6, .6, .6), (16, 25, 3.5, .55, .55, .55)]
        sweep(m, pts, ringed(color, tip, 3), group, B)
    elif style == 'feathers':
        for x in range(13, 20):
            length = 4 + (2 - abs(x - 16)) // 1 if abs(x - 16) <= 2 else 3
            out = 1 if abs(x - 16) == 3 else 0  # the outer feathers start behind the lowered arms' room
            for k in range(length):
                c = tip if k >= length - 1 else (second if (x + k) % 3 == 0 else color)
                m.set((x, 18 + out + k // 2 + 1, 9 - k // 2 - (k > 2)), c, 'feather', B)
                m.set((x, 18 + out + (k + 1) // 2, 9 - k // 2), c, 'feather', B)
    elif style == 'long_feathers':
        for x in (15, 16, 17):
            n = 11 if x == 16 else 8
            for k in range(n):
                c = tip if k >= n - 2 else (second if k % 3 == 0 else color)
                m.set((x, 19 + k, 9 + k // 2), c, 'feather', B)
    elif style == 'club':
        sweep(m, [(16, 18, 10, 1.6, 1.4, 1.5), (16, 22, 8, 1.2, 1.2, 1.1), (16, 26, 6, .9, .9, .9)], color, group, B)
        m.ellipsoid(16, 28.5, 5.5, 2.6, 1.8, 1.6, tip, 'bone', B, only_empty=True)
    elif style == 'spikes':
        sweep(m, [(16, 18, 10, 1.7, 1.5, 1.6), (16, 21, 8, 1.4, 1.4, 1.3), (16, 25, 5.5, 1, 1, 1), (16, 29, 4, .65, .65, .65)], color, group, B)
        for (y, z) in ((25, 7), (27, 6)):
            for dx in (-1, 1):
                for k in range(1, 4):
                    m.set((16 + dx * (k + 1), y, z + k), tip if k == 3 else shade(tip, 0.85), 'bone', B)
    elif style == 'snake':
        sweep(m, [(16, 18, 9.5, 1.5, 1.4, 1.4), (16, 21, 6.5, 1.3, 1.3, 1.2), (16, 24, 3, 1.1, 1.1, 1), (16, 27, 1.2, 1, 1, .9), (18.5, 30, 1, .8, .9, .75), (21, 30.5, 1, .6, .6, .6)], ringed(color, tip, 4), group, B)
    elif style == 'devil':
        sweep(m, [(16, 18, 9.5, .6, .6, .6), (16, 21, 7, .6, .6, .6), (16, 23, 5.5, .6, .6, .6), (16, 25, 6.5, .6, .6, .6)], color, group, B)
        for (x, y, z) in ((16, 26, 7), (15, 26, 6), (17, 26, 6), (16, 26, 6), (16, 27, 6), (16, 26, 5)):
            m.set((x, y, z), tip, group, B)
    elif style == 'seal':
        for side in (-1, 1):
            for k in range(3):
                for dz in (0, 1):
                    m.set((16 + side * (1 + k // 2), 18 + k, 2 - dz + k // 2), color if k < 2 else tip, group, B)


# --- Wings ---------------------------------------------------------------------------------

def arm_wings(m, color, tip=None, depth=None, second=None, style='feathers', reach=0):
    """Feathers hanging from the arms, behind them (y 18): longest at the hand, as a wing's
    primaries are. [depth] the voxels hanging below the arm at the hand; [reach] feathers out
    past the hand. Each feather rides on the arm bone above it."""
    tip = tip or shade(color, 0.7)
    second = second or shade(color, 1.15)
    depth = depth or 5
    for side in ('r', 'l'):
        for i, x in enumerate(range(4 - reach, 14)):
            xx = x if side == 'r' else 32 - x
            bone = arm_side_bone(max(4, x) if side == 'r' else min(28, 32 - x))
            if x < 4:
                bone = 'RightHand' if side == 'r' else 'LeftHand'
            d = max(1, depth - (x - 4) * depth // 11)
            if style == 'scallop' and x % 3 == 2:
                d = max(1, d - 1)
            for z in range(18 - d, 19):
                c = tip if z == 18 - d else (second if z >= 17 else color)
                m.set((xx, 18, z), c, 'feather', bone)
            if x <= 8:
                m.set((xx, 19, 17), color, 'feather', bone)
                m.set((xx, 19, 18), second, 'feather', bone)


def bat_wings(m, membrane, frame=None, depth=7, reach=2):
    """Membranes behind the arms (y 18), from the arm down to a scalloped edge, the fingers'
    bones ribbing them; they ride on the arms' bones and fold across the back."""
    frame = frame or shade(membrane, 0.6)
    for side in ('r', 'l'):
        for x in range(4 - reach, 13):
            xx = x if side == 'r' else 32 - x
            if x < 4:
                bone = 'RightHand' if side == 'r' else 'LeftHand'
            else:
                bone = arm_side_bone(x if side == 'r' else 32 - x)
            base = depth if x >= 6 else depth - (6 - x)
            scallop = (x % 4 == 1)
            bottom = 18 - base + (2 if scallop else 0)
            for z in range(max(bottom, 9), 19):
                rib = (x % 4 == 3)
                c = frame if (rib or z >= 18) else membrane
                m.set((xx, 18, z), c, 'skin', bone)


def back_wings(m, color, tip=None, style='feathered', glass=None, span=8, second=None):
    """Wings on the back (on the chest), behind the arms: feathered (folded angel wings, up
    and out), moth (two broad pairs, an eye spot each), insect (two clear pairs: [glass] the
    clarity), butterfly (big rounded), dragon (a membrane on ribs), tiny (stubs)."""
    tip = tip or shade(color, 0.7)
    second = second or shade(color, 1.2)
    mat = ('glass', glass) if glass else None
    B = 'Chest'
    cells = []
    if style == 'feathered':
        for x in range(17, 17 + span):
            top = 26 - (x - 17) // 2
            bottom = 11 + (x - 17)
            for z in range(min(bottom, top - 2), top + 1):
                cells.append((x, 20 if x <= 19 else 21, z, tip if z <= bottom or x == 16 + span else (second if z >= top - 1 else color)))
            cells.append((x, (19 if x <= 19 else 20) + (1 if top - 2 >= 20 else 0), top - 2, color))
    elif style in ('moth', 'butterfly'):
        for x in range(17, 17 + span):
            for z in range(7, 29):
                dx = x - 16.5
                up = ((dx - span * 0.45) / (span * 0.6)) ** 2 + ((z - 22) / 6.5) ** 2 <= 1
                low = ((dx - span * 0.35) / (span * 0.45)) ** 2 + ((z - 12.5) / 4.5) ** 2 <= 1
                if up or low:
                    c = color
                    if style == 'moth' and ((dx - span * 0.5) ** 2 + (z - 22) ** 2) <= 2.2:
                        c = second
                    if style == 'butterfly':
                        edge_up = ((dx - span * 0.45) / (span * 0.6 - 1)) ** 2 + ((z - 22) / 5.5) ** 2 > 1
                        edge_low = ((dx - span * 0.35) / (span * 0.45 - 1)) ** 2 + ((z - 12.5) / 3.5) ** 2 > 1
                        if (up and edge_up) or (low and not up and edge_low):
                            c = tip
                        elif (x + z) % 5 == 0:
                            c = second
                    elif ((dx - span * 0.45) / (span * 0.6 - 1)) ** 2 + ((z - 22) / 5.5) ** 2 > 1 and up:
                        c = tip
                    cells.append((x, 20 if z >= 19 else 19, z, c))
    elif style == 'insect':
        for x in range(17, 17 + span):
            dx = x - 16.5
            for z in range(10, 28):
                up = ((dx - span * 0.5) / (span * 0.55)) ** 2 + ((z - 22.5) / 2.2) ** 2 <= 1
                low = ((dx - span * 0.42) / (span * 0.45)) ** 2 + ((z - 17) / 1.9) ** 2 <= 1
                if up or low:
                    vein = (x - 17) % 3 == 2 or abs(z - 22.5) < 0.5 or abs(z - 17) < 0.5
                    cells.append((x, 20 if z >= 19 else 19, z, tip if vein else color))
    elif style == 'dragon':
        for x in range(17, 17 + span):
            top = 24 + (x - 17) // 3
            bottom = 12 + (x - 17) // 2 + (2 if (x - 17) % 3 == 1 else 0)
            for z in range(bottom, top + 1):
                rib = (x - 17) % 3 == 0 or z == top
                cells.append((x, 20 if z >= 19 else 19, z, tip if rib else color))
    elif style == 'tiny':
        for x in range(17, 20):
            for z in range(16, 21 - (x - 17)):
                cells.append((x, 19 if z < 20 else 20, z, color if z > 16 else tip))
    for x, y, z, c in cells:
        if x == 16 + span and style == 'feathered':
            pass
        g = 'glass' if mat and c == color else ('feather' if style == 'feathered' else 'chitin')
        m.set((x, y, z), c, g, B, None, mat if g == 'glass' else None)
        m.set((32 - x, y, z), c, g, B, None, mat if g == 'glass' else None)
    if style in ('moth', 'butterfly', 'insect', 'dragon'):
        # the wings' root down the middle of the back, behind the head where it rises past it
        for z in range(12, 22):
            y = 18 if z < 19 else (19 if z == 19 else 20)
            if not m.has((16, y, z)):
                m.set((16, y, z), tip, 'chitin', B)
            if z >= 19 and not m.has((16, y + 1, z)):
                m.set((16, y + 1, z), tip, 'chitin', B)


# --- Shells, spines and fins (on the chest) ------------------------------------------------

def turtle_shell(m, color, rim=None, scute=None, depth=4, top=19, bottom=8, spikes=None):
    """A domed shell on the back: an ellipsoid's back half behind y 18, a rim round it, scutes
    marked by darker lines."""
    rim = rim or shade(color, 0.7)
    scute = scute or shade(color, 0.8)
    cz = (top + bottom) / 2
    rz = (top - bottom) / 2 + 0.5
    for x in range(10, 23):
        for y in range(18, 18 + depth + 1):
            for z in range(bottom, top + 1):
                d = ((x + 0.5 - 16.5) / 6.3) ** 2 + ((y + 0.5 - 17.6) / (depth + 0.4)) ** 2 + ((z + 0.5 - cz - 0.5) / rz) ** 2
                if y == 18 and not 14 <= x <= 18:
                    continue  # behind the lowered arms the shell starts a voxel further back
                if d <= 1.0:
                    edge = d > 0.72 and y <= 19
                    c = rim if edge else color
                    if not edge and ((x - 16) % 3 == 0 or (z - bottom) % 4 == 0):
                        c = scute
                    m.set((x, y, z), c, 'shell', 'Chest')
    if spikes:
        for (x, z) in ((16, 16), (16, 12), (13, 14), (19, 14)):
            yb = m.back_y(x, z)
            if yb:
                m.set((x, yb + 1, z), spikes, 'shell', 'Chest')


def plastron(m, color, line=None):
    line = line or shade(color, 0.8)
    for z in range(9, 18):
        for x in range(14, 19):
            if z == 17 and x in (14, 18):
                continue
            c = line if z in (11, 14) or x == 16 else color
            m.set((x, 14, z), c, 'shell', None)


def snail_shell(m, color, stripe=None, cy=24.0, cz=17.0, r=7.0, width=3, aperture=None):
    """A coiled shell on the back: a disc in the y-z plane, [width] voxels each side of the
    middle, a spiral stripe round it."""
    stripe = stripe or shade(color, 0.7)
    aperture = aperture or shade(color, 1.3)
    for x in range(16 - width, 17 + width):
        rr = r * math.sqrt(max(0.0, 1 - ((x - 16) / (width + 1.2)) ** 2))
        for y in range(18, 32):
            for z in range(0, 32):
                dy, dz = y + 0.5 - cy, z + 0.5 - cz
                d = math.hypot(dy, dz)
                if d > rr:
                    continue
                if z >= 20 and y < 20:
                    continue
                if arm_room((x, y, z)):
                    continue
                a = math.atan2(dz, dy)
                turn = (d / r * 2.6 - a / (2 * math.pi)) % 1.0
                c = stripe if turn < 0.22 else color
                if d < 1.3:
                    c = stripe
                m.set((x, y, z), c, 'shell', 'Chest')


def hermit_shell(m, color, stripe=None):
    """A conch on the back, its spire up and back."""
    stripe = stripe or shade(color, 0.75)
    pts = [(16, 21, 10, 3.6, 3, 3.6), (16, 22.5, 14, 3.2, 3, 3.2), (16, 23.5, 18, 2.6, 2.4, 2.6), (16, 24, 21.5, 1.9, 1.8, 1.9), (16, 24.3, 24.5, 1.2, 1.2, 1.2), (16, 24.4, 26.5, .6, .6, .6)]
    sweep(m, pts, lambda t, p: stripe if int(t * 16) % 3 == 0 else color, 'shell', 'Chest', only_empty=True)
    for p in list(m.v):
        if m.v[p].bone == 'Chest' and m.v[p].group == 'shell' and p[1] < 18:
            del m.v[p]
        elif m.v[p].bone == 'Chest' and m.v[p].group == 'shell' and p[2] >= 20 and p[1] < 20:
            del m.v[p]


def spines(m, color, tip=None, length=3, density=0.5, head=True, back=True, seed=1, tipped=0.35):
    """Quills: from the back (on the chest) out behind, and over the back of the head. A
    share [tipped] of them end in the light [tip], the rest darker, so a coat of quills reads
    as speckled rather than as a sheet of tips."""
    light = tip or shade(color, 1.5)
    dark = shade(color, 0.72)

    class _Tip:
        # each quill's end colour, chosen by where it starts
        def __call__(self, p):
            return light if h(p, seed + 77) < tipped else dark
    pick = _Tip()
    if back:
        # rooted behind the torso (x 14-18), splaying out only behind the lowered arms' room
        for z in range(9, 19):
            for x in range(14, 19):
                if h((x, 0, z), seed) > density:
                    continue
                n = length - (1 if abs(x - 16) == 2 else 0) + 1
                end = pick((x, 0, z))
                for k in range(n):
                    dx = ((x - 16) * k) // 3 if k else 0
                    m.set((x + dx, 18 + k, z - k // 2), end if k == n - 1 else color, 'hair', 'Chest')
    if head and m.head:
        hd = m.head
        # where the head's back and top are, before any quill is added, so quills grow out of
        # the head and never out of each other
        backs, tops = {}, {}
        for p, v in m.v.items():
            if v.part == 'head' and v.group != 'hair':
                backs[(p[0], p[2])] = max(backs.get((p[0], p[2]), -1), p[1])
                tops[(p[0], p[1])] = max(tops.get((p[0], p[1]), -1), p[2])
        for z in range(hd.z0 + 1, hd.z1 + 2):
            for x in range(hd.x0, hd.x1 + 1):
                if h((x, 1, z), seed) > density:
                    continue
                yb = backs.get((x, z))
                if yb is None:
                    continue
                n = length
                end = pick((x, 1, z))
                for k in range(1, n + 1):
                    dz = k // 2 if z > (hd.z0 + hd.z1) / 2 else 0
                    m.set((x, yb + k, z + dz), end if k == n else color, 'hair', 'Head', 'head')
        for x in range(hd.x0 + 1, hd.x1):
            for y in range(hd.y0 + 2, hd.y1 + 1):
                if h((x, y, 2), seed) > density * 0.8:
                    continue
                zt = tops.get((x, y))
                if zt is None:
                    continue
                end = pick((x, y, 2))
                for k in range(1, length):
                    m.set((x, y + k // 2, zt + k), end if k == length - 1 else color, 'hair', 'Head', 'head')


def armadillo_bands(m, color, band=None):
    band = band or shade(color, 0.75)
    for z in range(8, 20):
        for x in range(12, 21):
            for y in range(18, 22):
                d = ((x + 0.5 - 16.5) / 5.4) ** 2 + ((y + 0.5 - 17.5) / 4.3) ** 2 + ((z + 0.5 - 13.8) / 6.6) ** 2
                if d <= 1 and not arm_room((x, y, z)):
                    m.set((x, y, z), band if z % 2 == 0 else color, 'shell', 'Chest')


def dorsal_fin(m, color, tip=None, height=6, y0=18, z0=11):
    tip = tip or shade(color, 0.8)
    for k in range(height):
        for z in range(z0 + k, z0 + height + 2 - k):
            y = y0 + k
            if z >= 20 and y < 20:
                continue
            m.set((16, y, z), tip if k == height - 1 or z == z0 + height + 1 - k else color, 'skin', 'Chest')


def back_plates(m, color, edge=None, count=4):
    """A stegosaur's plates in a row down the back."""
    edge = edge or shade(color, 0.75)
    plates = [(19, 18, 4), (21, 15, 5), (22, 11, 4), (21, 8, 3)][:count]
    for y0, zc, size in plates:
        for dy in range(size):
            for dz in range(-size + dy + 1, size - dy):
                y = y0 + dy
                z = zc + dz
                if z >= 20 and y < 20:
                    continue
                c = edge if (dy == size - 1 or abs(dz) == size - dy - 1) else color
                m.set((16, y, z), c, 'bone', 'Chest')
                if dy < size - 2 and abs(dz) < size - dy - 2:
                    m.set((15, y, z), c, 'bone', 'Chest'); m.set((17, y, z), c, 'bone', 'Chest')


def scutes(m, color, rows=((16, 18, z) for z in range(9, 19, 2))):
    for (x, y, z) in rows:
        m.set((x - 1, y, z), color, 'scale', 'Chest')
        m.set((x + 1, y, z), color, 'scale', 'Chest')


def spider_legs(m, color, joint=None, pairs=2):
    """Static legs out of the back (on the chest), behind the arms: up, out and down."""
    joint = joint or shade(color, 0.75)
    for side in (-1, 1):
        for i in range(pairs):
            z0 = 15 - i * 3
            pts = [(16 + side * 1.5, 18.5 + i * 0.6, z0), (16 + side * 5, 20 + i, z0 + 4), (16 + side * 9, 21 + i, z0 + 2), (16 + side * 11.5, 21 + i, z0 - 4 - i)]
            sweep(m, [(x, y, z, .6, .6, .6) for x, y, z in pts], lambda t, p: joint if abs(t - 0.36) < 0.06 or abs(t - 0.7) < 0.05 else color, 'chitin', 'Chest')


def abdomen(m, color, pattern=None, style='spider', second=None):
    """A big hind body behind the hips (on the hips): spider (round, a mark on it), ant (a
    round gaster on a waist), wasp (striped, with a sting), bee (fuzzy and striped)."""
    second = second or shade(color, 0.7)
    B = 'Hips'
    if style == 'spider':
        m.ellipsoid(16, 22.5, 11, 4, 4.2, 4.4, color, 'chitin', B, only_empty=True, where=lambda p: p[1] >= 18)
        if pattern:
            for (y, z) in ((26, 12), (26, 11), (26, 10), (25, 13), (25, 9)):
                for x in (15, 16, 17):
                    if m.has((x, y + 1, z)) is False and m.has((x, y, z)):
                        m.set((x, y, z), pattern, 'chitin', B)
            for x in (15, 16, 17):
                yb = m.back_y(x, 11)
                if yb:
                    m.set((x, yb, 11), pattern, 'chitin', B); m.set((x, yb, 12), pattern, 'chitin', B)
                yb = m.back_y(16, 14)
            for z in (9, 10, 13, 14):
                yb = m.back_y(16, z)
                if yb:
                    m.set((16, yb, z), pattern, 'chitin', B)
    elif style == 'ant':
        sweep(m, [(16, 18, 10, .8, .8, .8), (16, 19.5, 9.5, .9, .9, .9)], color, 'chitin', B)
        m.ellipsoid(16, 23, 9, 3.2, 3.6, 3.4, color, 'chitin', B, only_empty=True)
        if pattern:
            for p in list(m.v):
                if m.v[p].bone == B and m.v[p].group == 'chitin' and p[1] >= 22 and (p[2] + p[1]) % 4 == 0:
                    m.v[p].color = pattern
    elif style in ('wasp', 'bee'):
        sweep(m, [(16, 18, 10, .8, .8, .8), (16, 19.5, 9.5, .9, .9, .9)], second, 'chitin', B)
        sweep(m, [(16, 21, 9.5, 2.4, 2.2, 2.4), (16, 23.5, 8.5, 2.9, 2.6, 2.8), (16, 26, 7, 2.3, 2.1, 2.2), (16, 28, 5.8, 1.2, 1.2, 1.2)],
              lambda t, p: second if int(t * 9) % 2 else color, 'chitin', B)
        if style == 'wasp':
            m.set((16, 29, 5), (40, 36, 30), 'chitin', B); m.set((16, 30, 4), (40, 36, 30), 'chitin', B)
        else:
            for p in list(m.v):
                v = m.v[p]
                if v.bone == B and v.group == 'chitin' and h(p, 9) > 0.8 and p[1] > 20:
                    v.color = shade(v.color, 1.15)


# --- Head features -------------------------------------------------------------------------

def whiskers(m, color, length=2, rows=(0, 1)):
    """Whiskers out of the muzzle's sides: [length] voxels each way at its rows [rows] (0 its
    lowest), one voxel behind its tip."""
    hd = m.head
    info = getattr(m, 'snout_info', None)
    if info:
        tip, half, z, hgt, ln = info
        y = min(tip + 1, hd.y0 - 1)
        base_half = half + 1
    else:
        y, z, base_half, hgt = hd.y0 - 1, hd.z0 + 1, 1, 2
    for r in rows:
        zz = z + min(r, hgt - 1)
        for side in (-1, 1):
            for k in range(length):
                m.set((16 + side * (base_half + k), y, zz), color, 'hair', 'Head', 'head')


def antennae(m, color, style='thin', tip=None, length=5):
    """thin (up and out, curling), clubbed (a butterfly's), feathery (a moth's), elbowed (an
    ant's), long (back over the head)."""
    tip = tip or color
    hd = m.head
    top = hd.z1
    for side in (-1, 1):
        x0 = 16 + side * 2
        if style == 'thin':
            pts = [(x0, hd.y0 + 1, top + 1), (x0 + side, hd.y0, top + 3), (x0 + side * 2, hd.y0, top + length)]
        elif style == 'elbowed':
            pts = [(x0, hd.y0 + 1, top + 1), (x0, hd.y0 + 1, top + 3), (x0 + side * 2, hd.y0 - 1, top + 3), (x0 + side * 3, hd.y0 - 2, top + 2)]
        elif style == 'long':
            pts = [(x0, hd.y0 + 1, top + 1), (x0 + side, hd.y0 + 3, top + 3), (x0 + side * 2, hd.y1, top + 4), (x0 + side * 3, hd.y1 + 3, top + 2)]
        else:
            pts = [(x0, hd.y0 + 1, top + 1), (x0 + side, hd.y0 + 1, top + 3), (x0 + side * 2, hd.y0 + 2, top + length)]
        sweep(m, [(x, y, z, .55, .55, .55) for x, y, z in pts], color, 'chitin', 'Head')
        end = pts[-1]
        if style == 'clubbed':
            m.ellipsoid(end[0], end[1], end[2], 1, 1, 1, tip, 'chitin', 'Head', only_empty=True)
        if style == 'feathery':
            for k in range(1, length):
                zz = top + k
                xx = x0 + side * (1 + k * 2 // length)
                for dy in (-1, 1):
                    m.set((xx + side, hd.y0 + 1 + dy, zz), tip, 'chitin', 'Head')
                    m.set((xx - side if k > 1 else xx, hd.y0 + 1 + dy, zz), tip, 'chitin', 'Head')
        else:
            m.set(tuple(int(round(v)) for v in end), tip, 'chitin', 'Head')


def eye_stalks(m, color, eye=(30, 28, 32), white=(240, 238, 230), height=3, spread=2):
    hd = m.head
    for side in (-1, 1):
        x = 16 + side * spread
        for k in range(1, height + 1):
            m.set((x, hd.y0 + 2, hd.z1 + k), color, 'skin', 'Head', 'head')
        m.ellipsoid(x, hd.y0 + 2, hd.z1 + height + 1, 1.2, 1.2, 1.2, white, 'eye', 'Head', 'head')
        m.set((x, hd.y0 + 1, hd.z1 + height + 1), eye, 'eye', 'Head', 'head')


def gills(m, color, z=None):
    hd = m.head
    z0 = z if z is not None else hd.z0 + 1
    for x in (hd.x0, hd.x1):
        for k in range(3):
            y = hd.y0 + 3 + k
            for zz in (z0, z0 + 1, z0 + 2):
                if k != 1 and m.has((x, y, zz)):
                    m.set((x, y, zz), color, 'detail', 'Head', 'head')


def mane(m, color, highlight=None, size=2, low=19):
    """A mane round the face: out from the head's sides and back, behind the face, down the
    back of the neck; over the arms it stops at z 19."""
    hl = highlight or shade(color, 1.15)
    hd = m.head
    cx, cy, cz = 16, (hd.y0 + hd.y1) / 2 + 1, (hd.z0 + hd.z1) / 2
    rx, ry, rz = hd.w / 2 + size, hd.d / 2 + size - 0.5, hd.h / 2 + size
    for x in range(hd.x0 - size - 1, hd.x1 + size + 2):
        for y in range(hd.y0 + 1, hd.y1 + size + 2):
            for z in range(low, hd.z1 + size + 1):
                d = ((x + 0.5 - cx - 0.5) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 + ((z + 0.5 - cz) / rz) ** 2
                if d > 1 or m.has((x, y, z)):
                    continue
                if z <= 19 and 14 <= y <= 18 and (x <= 13 or x >= 19):
                    continue
                if z <= 19 and 14 <= x <= 18 and 14 <= y <= 18:
                    continue
                m.set((x, y, z), hl if h((x, y, z), 7) > 0.75 else color, 'fur', 'Head', 'head')


def frill(m, color, edge=None, size=4, spikes=False):
    """A frill fanning out behind the head (a ceratopsian's, a frilled lizard's)."""
    edge = edge or shade(color, 0.7)
    hd = m.head
    yb = hd.y1 + 1
    cz = (hd.z0 + hd.z1) / 2 + 1
    for x in range(hd.x0 - size, hd.x1 + size + 1):
        for z in range(hd.z0 - 1, hd.z1 + size + 1):
            d = ((x + 0.5 - 16.5) / (hd.w / 2 + size)) ** 2 + ((z + 0.5 - cz) / (hd.h / 2 + size)) ** 2
            if d > 1:
                continue
            if z <= 19 and (x <= 13 or x >= 19):
                continue
            c = edge if d > 0.7 else color
            if spikes and d > 0.82 and (x + z) % 3 == 0:
                m.set((x, yb + 1, z), edge, 'bone', 'Head', 'head')
            m.set((x, yb, z), c, 'bone', 'Head', 'head')


def head_fins(m, color, tip=None):
    """A fish's fins: a crest along the head's top and one out of each cheek."""
    tip = tip or shade(color, 0.75)
    hd = m.head
    for y in range(hd.y0 + 1, hd.y1 + 2):
        hgt = 3 if hd.y0 + 2 <= y <= hd.y1 - 1 else 2
        for k in range(1, hgt + 1):
            m.set((16, y, hd.z1 + k), tip if k == hgt else color, 'skin', 'Head', 'head')
    for side in (-1, 1):
        x = (hd.x1 + 1) if side == 1 else (hd.x0 - 1)
        for k in range(3):
            for z in range(hd.z0 + 1, hd.z0 + 4 - k):
                m.set((x + side * k, hd.y0 + 3 + k, z), tip if k == 2 else color, 'skin', 'Head', 'head')


def arm_fins(m, color):
    for x in list(range(7, 12)) + list(range(21, 26)):
        hgt = 2 if x in (9, 10, 22, 23) else 1
        for k in range(hgt):
            m.set((x, 18 + k, 18 - k), color, 'skin', arm_side_bone(x))


# --- Hands and feet ------------------------------------------------------------------------

def claws(m, color, length=1):
    """Claws out past each hand's fingers."""
    for side, x0, step in (('r', 3, -1), ('l', 29, 1)):
        bone = 'RightHand' if side == 'r' else 'LeftHand'
        for y in (15, 17):
            for k in range(length):
                m.set((x0 + step * k, y, 18), color, 'bone', bone)


def big_claws(m, color, tip=None):
    """Big digging hands (a mole's): the hand broadened forward and back, claws out."""
    tip = tip or shade(color, 1.3)
    for side, xs, xc in (('r', (3, 4, 5), 2), ('l', (27, 28, 29), 30)):
        bone = 'RightHand' if side == 'r' else 'LeftHand'
        for x in xs:
            for y in (14, 15, 16, 17, 18):
                m.set((x, y, 18), color, 'skin', bone)
            m.set((x, 16, 17), color, 'skin', bone)
        for y in (14, 16, 18):
            m.set((xc, y, 18), tip, 'bone', bone)


def pincers(m, color, tip=None, size=1):
    """Crab claws in place of the hands: a fixed finger and a moving one, open."""
    tip = tip or shade(color, 0.7)
    for side in ('r', 'l'):
        bone = 'RightHand' if side == 'r' else 'LeftHand'
        sx = -1 if side == 'r' else 1
        base = 5 if side == 'r' else 27
        for x in ([4, 5] if side == 'r' else [27, 28]):
            for y in range(14, 19):
                for z in (17, 18, 19):
                    m.set((x, y, z), color, 'chitin', bone)
        tipx = base + sx * 2
        for k in range(1, 3 + size):
            x = tipx + sx * (k - 1)
            m.set((x, 15, 19 + (k > 2)), tip if k == 2 + size else color, 'chitin', bone)
            m.set((x, 16, 19 + (k > 2)), tip if k == 2 + size else color, 'chitin', bone)
            m.set((x, 15, 17), tip if k >= 1 + size else color, 'chitin', bone)
            m.set((x, 16, 17), tip if k >= 1 + size else color, 'chitin', bone)


def hooves(m, color):
    m.paint(color, 'horn', parts=('foot_r', 'foot_l'))
    m.paint(color, 'horn', parts=('lleg_r', 'lleg_l'), where=lambda p, v: p[2] == 1)


def paws(m, pad, parts=('hand_r', 'hand_l')):
    m.paint(pad, 'skin', parts=parts, where=lambda p, v: p[1] == 15)


def talons(m, color):
    for x in (14, 15, 17, 18):
        m.paint(color, 'horn', box=(x, x, 13, 15, 0, 0))
    for x in (14, 18):
        m.set((x, 12, 0), shade(color, 0.7), 'horn', 'RightFoot' if x < 16 else 'LeftFoot')
    for x in (15, 17):
        m.set((x, 18, 0), color, 'horn', 'RightFoot' if x < 16 else 'LeftFoot')


def webbed_feet(m, color):
    for x in (13, 16, 19):
        for y in (12, 13):
            if x == 16:
                continue
            m.set((x, y, 0), color, 'skin', 'RightFoot' if x < 16 else 'LeftFoot')
    for x in (14, 15, 17, 18):
        m.set((x, 12, 0), color, 'skin', 'RightFoot' if x < 16 else 'LeftFoot')


# --- Hides ---------------------------------------------------------------------------------

BODY = ('chest', 'spine', 'hips', 'uarm_r', 'larm_r', 'hand_r', 'uarm_l', 'larm_l', 'hand_l',
        'uleg_r', 'lleg_r', 'foot_r', 'uleg_l', 'lleg_l', 'foot_l', 'neck')


def belly(m, color, parts=('chest', 'spine', 'hips', 'neck'), head=False):
    """The front of the torso lighter (y 15, the middle three columns)."""
    m.paint(color, None, parts=parts, where=lambda p, v: p[1] == 15 and 15 <= p[0] <= 17 and v.group == m.skin_group)


def stripes(m, color, period=3, parts=BODY, head=True, axis='z', offset=0, width=1):
    """Bands round the body: across (z) on the torso and legs, along the arms by x."""
    def where(p, v):
        if v.group != m.skin_group:
            return False
        if v.part in ('uarm_r', 'larm_r', 'uarm_l', 'larm_l'):
            return (p[0] + offset) % period < width
        return (p[2] + offset) % period < width and p[1] != 15
    m.paint(color, None, parts=parts, where=where)
    if head and m.head:
        hd = m.head
        def hw(p, v):
            if v.group != m.skin_group or v.part != 'head':
                return False
            if p[1] <= hd.y0:
                return False
            return (p[1] + p[2] + offset) % period < width and (p[2] >= hd.z1 - 1 or p[1] >= hd.y1 - 1 or p[0] in (hd.x0, hd.x1))
        m.paint(color, None, where=hw)


def spots(m, color, density=0.22, seed=3, parts=BODY, head=True, size=1):
    def where(p, v):
        if v.group != m.skin_group:
            return False
        q = (p[0] // size, p[1] // size, p[2] // size)
        return h(q, seed) < density
    m.paint(color, None, parts=parts + (('head',) if head else ()), where=where)


def points(m, color, ears=True, face=True, limbs=True):
    """Darker extremities, a Siamese cat's: hands, feet, lower legs, ears and the muzzle."""
    if limbs:
        m.paint(color, None, parts=('hand_r', 'hand_l', 'foot_r', 'foot_l'), where=lambda p, v: v.group == m.skin_group)
        m.paint(color, None, parts=('larm_r', 'larm_l', 'lleg_r', 'lleg_l'), where=lambda p, v: v.group == m.skin_group)
    if ears and m.head:
        hd = m.head
        m.paint(color, None, where=lambda p, v: v.part == 'head' and v.group == m.skin_group and p[2] > hd.z1)


def countershade(m, back_color, parts=BODY + ('head',)):
    """A darker back: the back faces and the top of the head."""
    hd = m.head
    def where(p, v):
        if v.group != m.skin_group:
            return False
        if v.part == 'head':
            return p[2] >= hd.z1 or p[1] >= hd.y1
        return p[1] >= 17
    m.paint(back_color, None, parts=parts, where=where)


def mottle(m, colors, density=0.25, seed=11, groups=None):
    """Scatters [colors] over the hide's voxels (scales, warts)."""
    groups = groups or (m.skin_group,)
    for p, v in m.v.items():
        if v.group in groups and h(p, seed) < density:
            v.color = colors[int(h(p, seed + 1) * len(colors)) % len(colors)]


def scales(m, dark, seed=5, density=0.3):
    """A scale texture: a darker shade on a checker of the hide's voxels, broken up."""
    for p, v in m.v.items():
        if v.group == m.skin_group and (p[0] + p[1] + p[2]) % 2 == 0 and h(p, seed) < density + 0.4:
            v.color = dark if h(p, seed + 2) < 0.6 else shade(dark, 1.1)
