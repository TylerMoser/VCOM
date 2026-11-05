"""Clothing, armour and gear on the base body, and outfits for the game's classes.

Where a piece may go, so the game's animations do not drive a limb through it:
- the torso stays x 14-18: a lowered arm hangs flush beside it in x 12-13 and 19-20, from the
  shoulder (z 18) down to the hand (z 9), so nothing is added at x 13 or 19 above z 8;
- nothing hangs under an arm (z 16 or lower beside it): a lowered arm turns that side onto
  the torso; what hangs from an arm goes behind the body (y 18 or more) or in front (y 14);
- below the hips (z 8 and lower) a piece goes with the leg it is on (x 16 and less the right,
  17 and more the left), but for the middle column x 16, which goes with the hips: it is
  between the legs, where no leg swings;
- the head is x 12-20, y 12-19 from z 20 up: what is on the back above z 19 starts at y 20.
"""
from core import shade, mix

TORSO = ('chest', 'spine', 'hips')
UPPER = ('chest', 'spine')
ARMS = ('uarm_r', 'larm_r', 'hand_r', 'uarm_l', 'larm_l', 'hand_l')
SLEEVES = ('uarm_r', 'larm_r', 'uarm_l', 'larm_l')
HANDS = ('hand_r', 'hand_l')
LEGS = ('uleg_r', 'lleg_r', 'uleg_l', 'lleg_l')
FEET = ('foot_r', 'foot_l')
LEG_X = {'r': (14, 15), 'l': (17, 18)}
FRONT, BACK = 14, 18


def hem_bone(x, z):
    """The bone of an added voxel below the hips: the middle column goes with the hips."""
    if z <= 8 and x == 16:
        return 'Hips'
    return None


def put(m, x, y, z, color, group, bone=None, mat=None):
    if bone is None:
        bone = hem_bone(x, z)
    m.set((x, y, z), color, group, bone, None, mat)


def arm_side_bone(x):
    if x <= 5: return 'RightHand'
    if x <= 8: return 'RightLowerArm'
    if x <= 13: return 'RightUpperArm'
    if x >= 27: return 'LeftHand'
    if x >= 24: return 'LeftLowerArm'
    if x >= 19: return 'LeftUpperArm'
    return 'Chest'


# --- Plain clothes -------------------------------------------------------------------------

def shirt(m, color, sleeves='long', neckline='v', group='cloth', hips=False):
    """Recolours the torso (and the hips with [hips]) and the sleeves. Necklines: v (skin in a
    V at the top front), round (one voxel), none."""
    m.paint(color, group, parts=TORSO if hips else UPPER)
    if sleeves == 'long':
        m.paint(color, group, parts=SLEEVES)
    elif sleeves == 'short':
        m.paint(color, group, parts=SLEEVES, where=lambda p, v: 11 <= p[0] <= 21)
    elif sleeves == 'elbow':
        m.paint(color, group, parts=('uarm_r', 'uarm_l'))
    skin = getattr(m, 'skin', None)
    if skin is not None and neckline in ('v', 'round', 'deep'):
        cells = [(16, 15, 18)]
        if neckline == 'v':
            cells += [(15, 15, 18), (17, 15, 18), (16, 15, 17)]
        if neckline == 'deep':
            cells += [(15, 15, 18), (17, 15, 18), (16, 15, 17), (16, 15, 16)]
        for p in cells:
            if m.has(p):
                m.paint(skin, m.skin_group, box=(p[0], p[0], p[1], p[1], p[2], p[2]))


def trousers(m, color, length='long', group='cloth'):
    """long, knee (to the knee), shorts (the thigh's top half)."""
    m.paint(color, group, parts=('hips',))
    if length == 'long':
        m.paint(color, group, parts=LEGS)
    elif length == 'knee':
        m.paint(color, group, parts=('uleg_r', 'uleg_l'))
    elif length == 'shorts':
        m.paint(color, group, parts=('uleg_r', 'uleg_l'), where=lambda p, v: p[2] >= 6)


def boots(m, color, height=3, cuff=None, group='leather', toe=None):
    """Recolours the feet and the legs up to [height]; [cuff] folds a band over the top."""
    m.paint(color, group, parts=FEET)
    m.paint(color, group, parts=LEGS, where=lambda p, v: p[2] <= height)
    if toe:
        for x in (14, 15, 17, 18):
            m.paint(toe, group, box=(x, x, 13, 13, 0, 0))
    if cuff:
        for side in 'rl':
            xs = LEG_X[side]
            for x in xs:
                put(m, x, FRONT, height, cuff, group)
                put(m, x, BACK, height, cuff, group)
            out = 13 if side == 'r' else 19
            for y in range(15, 18):
                put(m, out, y, height, cuff, group)


def shoes(m, color, group='leather'):
    m.paint(color, group, parts=FEET)


def gloves(m, color, cuff=False, group='leather'):
    m.paint(color, group, parts=HANDS)
    if cuff:
        m.paint(color, group, parts=('larm_r', 'larm_l'), where=lambda p, v: p[0] in (6, 26))


def wraps(m, color, group='cloth'):
    """Hand wraps: the hands and the forearms' ends banded."""
    m.paint(color, group, parts=HANDS)
    m.paint(color, group, parts=('larm_r', 'larm_l'), where=lambda p, v: p[0] in (6, 7, 25, 26))


def belt(m, color, buckle=None, z=9, group='leather'):
    m.paint(color, group, box=(14, 18, 15, 17, z, z))
    if buckle:
        put(m, 16, FRONT, z, buckle, 'metal')


def sash(m, color, z=10, tail=True, group='cloth'):
    m.paint(color, group, box=(14, 18, 15, 17, z, z + 1))
    if tail:
        put(m, 18, FRONT, z, color, group)
        put(m, 18, FRONT, z - 1, color, group)
        put(m, 18, FRONT, z - 2, shade(color, 0.85), group)


def cross_sash(m, color, group='cloth', side='r'):
    """A sash from one shoulder across to the other hip, front and back."""
    for k in range(9):
        x = 14 + k // 2 if side == 'r' else 18 - k // 2
        z = 18 - k
        m.paint(color, group, box=(x, x, 15, 15, z, z))
        m.paint(color, group, box=(x, x, 17, 17, z, z))


def vest(m, color, open_front=True, group='cloth', trim=None):
    def where(p, v):
        if open_front and p[1] == 15 and p[0] == 16:
            return False
        return True
    m.paint(color, group, parts=UPPER, where=where)
    if trim:
        m.paint(trim, group, parts=UPPER, where=lambda p, v: p[1] == 15 and p[0] in (15, 17))


# --- Coats and robes -----------------------------------------------------------------------

def coat(m, color, trim=None, length='knee', open_front=True, collar=True, cuffs=True,
         sleeves=True, lining=None, group='cloth'):
    """A coat: the torso to the hips, sleeves, and below the hips its skirts, flaring round
    each leg (back, outer side, the front corners): knee (to z 5), long (to z 2), hip (none)."""
    trim = trim or shade(color, 0.7)
    lining = lining or shade(color, 0.8)
    def where(p, v):
        return not (open_front and p[1] == 15 and p[0] == 16 and p[2] >= 9)
    m.paint(color, group, parts=TORSO, where=where)
    if open_front:
        m.paint(trim, group, parts=TORSO, where=lambda p, v: p[1] == 15 and p[0] in (15, 17))
    if sleeves:
        m.paint(color, group, parts=SLEEVES)
        if cuffs:
            m.paint(trim, group, parts=SLEEVES, where=lambda p, v: p[0] in (6, 26))
    if collar:
        for y in range(15, 18):
            put(m, 15, y, 19, trim, group, 'Chest')
            put(m, 17, y, 19, trim, group, 'Chest')
        put(m, 16, 17, 19, trim, group, 'Chest')
    bottom = {'hip': 9, 'knee': 5, 'long': 2, 'ankle': 1}[length]
    for z in range(bottom, 9):
        edge = z == bottom
        for x in range(14, 19):
            put(m, x, BACK, z, trim if edge else color, group)
        for y in range(15, 18):
            put(m, 13, y, z, trim if edge else color, group)
            put(m, 19, y, z, trim if edge else color, group)
        for x in (13, 14, 18, 19):
            c = trim if (edge or x in (14, 18)) else color
            put(m, x, FRONT, z, c, group)
        put(m, 13, BACK, z, trim if edge else color, group)
        put(m, 19, BACK, z, trim if edge else color, group)
    if not open_front and bottom < 9:
        for z in range(bottom, 9):
            for x in (15, 17):
                put(m, x, FRONT, z, color, group)


def robe(m, color, trim=None, hem=None, sleeves='bell', flare=True, front=None, group='cloth'):
    """A robe to the ankles: the torso, the legs and the gap between them filled, a layer in
    front and behind, flaring at the hem; bell sleeves (wide at the wrist) or plain."""
    trim = trim or shade(color, 0.75)
    hem = hem or trim
    m.paint(color, group, parts=TORSO + LEGS)
    m.paint(color, group, parts=SLEEVES)
    for z in range(1, 9):
        for y in range(15, 18):
            put(m, 16, y, z, color, group)
        for x in range(14, 19):
            put(m, x, FRONT, z, hem if z == 1 else color, group)
            put(m, x, BACK, z, hem if z == 1 else color, group)
    if flare:
        for z in range(1, 5):
            for y in range(14, 19):
                put(m, 13, y, z, hem if z == 1 else color, group)
                put(m, 19, y, z, hem if z == 1 else color, group)
    if front:
        for z in range(1, 19):
            if m.has((16, FRONT, z)):
                m.set((16, FRONT, z), front, group, hem_bone(16, z))
            else:
                m.paint(front, group, box=(16, 16, 15, 15, z, z))
    if sleeves == 'bell':
        for x in (6, 7, 25, 26):
            for z in (17, 18):
                put(m, x, FRONT, z, trim if x in (6, 26) else color, group, arm_side_bone(x))
                put(m, x, BACK, z, trim if x in (6, 26) else color, group, arm_side_bone(x))
            for y in range(15, 18):
                put(m, x, y, 19, trim if x in (6, 26) else color, group, arm_side_bone(x))
        m.paint(trim, group, parts=SLEEVES, where=lambda p, v: p[0] in (6, 26))


def tunic(m, color, belt_color=None, trim=None, group='cloth', skirt=True):
    """A belted tunic with a short skirt round the thighs."""
    trim = trim or shade(color, 0.75)
    m.paint(color, group, parts=TORSO)
    m.paint(color, group, parts=SLEEVES, where=lambda p, v: 10 <= p[0] <= 22)
    if skirt:
        for z in (7, 8):
            for x in range(14, 19):
                put(m, x, FRONT, z, trim if z == 7 else color, group)
                put(m, x, BACK, z, trim if z == 7 else color, group)
            for y in range(15, 18):
                put(m, 13, y, z, trim if z == 7 else color, group)
                put(m, 19, y, z, trim if z == 7 else color, group)
    if belt_color:
        belt(m, belt_color)


def cape(m, color, inner=None, bottom=6, collar=None, group='cloth', wide=True, emblem=None):
    """A cape down the back from the shoulders, all on the chest. Long ones pass through the
    legs in a stride (README, the rig)."""
    inner = inner or shade(color, 0.75)
    x0, x1 = (13, 19) if wide else (14, 18)
    for z in range(bottom, 19):
        # over the shoulders it is as wide as asked; below them it keeps behind the torso,
        # out of the way of a lowered arm's swing
        lo, hi = (x0, x1) if z >= 17 else (14, 18)
        for x in range(lo, hi + 1):
            if z == bottom and x in (lo, hi):
                continue
            put(m, x, BACK, z, inner if x in (lo, hi) else color, group, 'Chest')
            if z <= 16 and lo < x < hi:
                put(m, x, BACK + 1, z, color, group, 'Chest')
    for x in range(x0, x1 + 1):
        put(m, x, BACK, 19, collar or color, group, 'Chest')
        put(m, x, 17, 19, collar or color, group, 'Chest') if x != 16 else None
    put(m, 16, 17, 19, collar or color, group, 'Chest')
    if emblem:
        for (dx, dz) in ((0, 0), (-1, 0), (1, 0), (0, 1), (0, -1)):
            put(m, 16 + dx, BACK + 1, 13 + dz, emblem, group, 'Chest')


def cloak_hood_down(m, color, group='cloth'):
    """A hood lying on the back of the shoulders."""
    for x in range(14, 19):
        put(m, x, BACK, 18, color, group, 'Chest')
        put(m, x, BACK, 19, color, group, 'Chest')
        put(m, x, BACK + 1, 17, color, group, 'Chest')
        put(m, x, BACK + 1, 18, shade(color, 0.85), group, 'Chest')


def mantle(m, color, highlight=None, group='fur'):
    """A fur (or feathered) mantle round the shoulders: round the neck at z 19, over the
    shoulders, and a band at z 18 in front and behind."""
    hl = highlight or shade(color, 1.2)
    for x in range(11, 22):
        for y in range(14, 19):
            if x == 16 and y in (15, 16):
                continue
            if x in (11, 21) and y in (14, 18):
                continue
            bone = 'RightUpperArm' if x <= 13 else ('LeftUpperArm' if x >= 19 else 'Chest')
            put(m, x, y, 19, hl if (x * 7 + y * 3) % 5 == 0 else color, group, bone)
    for x in range(13, 20):
        bone = 'RightUpperArm' if x <= 13 else ('LeftUpperArm' if x >= 19 else 'Chest')
        put(m, x, FRONT, 18, color, group, bone)
        put(m, x, BACK, 18, color, group, bone)
        if 14 <= x <= 18:
            put(m, x, BACK, 17, hl if x % 2 else color, group, 'Chest')
            put(m, x, FRONT, 17, color if x % 2 else hl, group, 'Chest')


def collar_ruff(m, color, group='cloth'):
    for x in range(14, 19):
        for y in range(14, 19):
            if x == 16 and y in (15, 16):
                continue
            put(m, x, y, 19, color if (x + y) % 2 else shade(color, 0.85), group, 'Chest')


def scarf(m, color, tail=True, mask=False, group='cloth', stripe=None):
    """A scarf round the neck, its end down the front; [mask] pulls it up over the mouth
    (onto the face, so it moves with the head)."""
    c2 = stripe or shade(color, 0.85)
    for x in range(15, 18):
        for y in range(14, 18):
            if x == 16 and y in (15, 16):
                continue
            put(m, x, y, 19, color, group, 'Chest')
    put(m, 14, 15, 19, color, group, 'Chest'); put(m, 18, 15, 19, color, group, 'Chest')
    put(m, 14, 16, 19, c2, group, 'Chest'); put(m, 18, 16, 19, c2, group, 'Chest')
    if tail:
        for z in range(13, 19):
            put(m, 17, FRONT, z, color if z % 3 else c2, group, 'Chest')
        put(m, 18, FRONT, 13, c2, group, 'Chest')
    if mask:
        hd = getattr(m, 'head', None)
        if hd:
            for x in range(hd.x0, hd.x1 + 1):
                for z in (hd.z0, hd.z0 + 1):
                    y = m.front_y(x, z)
                    if y is not None:
                        m.set((x, y - 1 if x in range(hd.x0 + 1, hd.x1) else y, z), color, group, 'Head', 'head')


def bandana_mask(m, color, group='cloth'):
    hd = m.head
    for x in range(hd.x0, hd.x1 + 1):
        for z in (hd.z0, hd.z0 + 1):
            y = m.front_y(x, z)
            if y is not None:
                m.set((x, y, z), color, group, 'Head', 'head')
    m.set((16, hd.y0 - 1, hd.z0), color, group, 'Head', 'head')


# --- Armour --------------------------------------------------------------------------------

def breastplate(m, color, trim=None, back=True, group='metal', ridge=True, low=12):
    """A plate over the chest and belly (the front at y 14), and a back plate."""
    trim = trim or shade(color, 0.75)
    m.paint(color, group, parts=UPPER)
    for z in range(low, 19):
        for x in range(14, 19):
            if z == 18 and x in (14, 18):
                continue
            c = color
            if ridge and x == 16:
                c = shade(color, 1.15)
            if z == low:
                c = trim
            put(m, x, FRONT, z, c, group)
            if back:
                put(m, x, BACK, z, trim if z == low else color, group)


def mail(m, color, group='metal'):
    """Chain mail: the torso and sleeves in two close shades."""
    dark = shade(color, 0.82)
    m.paint(color, group, parts=TORSO + ('uarm_r', 'uarm_l'), where=lambda p, v: (p[0] + p[2]) % 2 == 0)
    m.paint(dark, group, parts=TORSO + ('uarm_r', 'uarm_l'), where=lambda p, v: (p[0] + p[2]) % 2 == 1)


def pauldrons(m, color, trim=None, size=1, spikes=None, group='metal', sides='both', fur=None):
    """Shoulder plates on the upper arms: on top of the shoulder (z 19), lipping over its
    front and back; size 2 is broader and raised at the outer edge."""
    trim = trim or shade(color, 0.75)
    for side in ('r', 'l'):
        if sides != 'both' and sides != side:
            continue
        bone = 'RightUpperArm' if side == 'r' else 'LeftUpperArm'
        xs = list(range(11, 14)) if size == 1 else list(range(10, 14))
        if side == 'l':
            xs = [32 - x for x in xs]
        outer = xs[0] if side == 'r' else xs[0]
        y0, y1 = (14, 18) if size == 1 else (13, 19)
        for x in xs:
            for y in range(y0, y1 + 1):
                c = trim if (x == outer or y in (y0, y1)) else color
                put(m, x, y, 19, c, group, bone)
            put(m, x, y0 if size == 1 else 14, 18, trim, group, bone)
            put(m, x, y1 if size == 1 else 18, 18, trim, group, bone)
        if size >= 2:
            for x in xs[:2]:
                for y in range(y0 + 1, y1):
                    put(m, x, y, 20, color if x != outer else trim, group, bone)
        if fur:
            for x in xs:
                put(m, x, 16, 20 if size == 1 else 21, fur, 'fur', bone) if x == xs[1] else None
        if spikes:
            x = xs[0] if size >= 2 else xs[1]
            top = 21 if size >= 2 else 20
            put(m, x, 16, top, spikes, group, bone)
            put(m, x, 16, top + 1, shade(spikes, 1.2), group, bone)


def epaulettes(m, color, fringe=None, group='metal'):
    fringe = fringe or shade(color, 0.85)
    for side in 'rl':
        bone = 'RightUpperArm' if side == 'r' else 'LeftUpperArm'
        xs = (11, 12, 13) if side == 'r' else (19, 20, 21)
        for x in xs:
            for y in (15, 16, 17):
                put(m, x, y, 19, color, group, bone)
        x = 11 if side == 'r' else 21
        for y in (15, 16, 17):
            put(m, x - (1 if side == 'r' else -1), y, 19, fringe, group, bone)


def gauntlets(m, color, group='metal', trim=None):
    m.paint(color, group, parts=HANDS + ('larm_r', 'larm_l'))
    if trim:
        m.paint(trim, group, parts=('larm_r', 'larm_l'), where=lambda p, v: p[0] in (8, 24))
        for x in (8, 24):
            for z in (17, 18):
                put(m, x, FRONT, z, trim, group, arm_side_bone(x))
                put(m, x, BACK, z, trim, group, arm_side_bone(x))
            for y in range(15, 18):
                put(m, x, y, 19, trim, group, arm_side_bone(x))


def bracers(m, color, group='leather', studs=None):
    m.paint(color, group, parts=('larm_r', 'larm_l'))
    if studs:
        for x in (7, 25):
            put(m, x, 16, 19, studs, 'metal', arm_side_bone(x))


def greaves(m, color, group='metal', knee=True):
    m.paint(color, group, parts=('lleg_r', 'lleg_l'))
    for x in (14, 15, 17, 18):
        for z in (2, 3, 4):
            put(m, x, FRONT, z, color if z != 4 else shade(color, 1.1), group)
        if knee:
            put(m, x, FRONT, 5, shade(color, 0.85), group)


def tabard(m, color, trim=None, emblem=None, emblem_color=None, back=True, bottom=5, group='cloth'):
    """A tabard: a panel in front (and behind) from the shoulders to [bottom], three wide."""
    trim = trim or shade(color, 0.75)
    for z in range(bottom, 19):
        for x in (15, 16, 17):
            c = trim if (z == bottom or (x != 16 and z == 18)) else color
            put(m, x, FRONT, z, c, group)
            if back:
                put(m, x, BACK, z, c, group)
    if emblem and emblem_color:
        for dx, dz in EMBLEMS[emblem]:
            put(m, 16 + dx, FRONT, 14 + dz, emblem_color, group)
    belt(m, shade(trim, 0.8), z=10)


EMBLEMS = {
    'cross': [(0, 0), (0, 1), (0, -1), (-1, 0), (1, 0), (0, 2)],
    'dot': [(0, 0)],
    'bar': [(0, 1), (0, 0), (0, -1)],
    'chevron': [(-1, 1), (0, 0), (1, 1)],
    'diamond': [(0, 1), (-1, 0), (1, 0), (0, -1)],
    'tower': [(-1, -1), (0, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
}


def kilt(m, color, stripe=None, top=8, bottom=5, group='cloth'):
    m.paint(color, group, parts=('hips',))
    for z in range(bottom, top + 1):
        for x in range(14, 19):
            c = stripe if (stripe and (x + z) % 3 == 0) else color
            put(m, x, FRONT, z, c, group)
            put(m, x, BACK, z, c, group)
        for y in range(14, 19):
            c = stripe if (stripe and (y + z) % 3 == 0) else color
            put(m, 13, y, z, c, group)
            put(m, 19, y, z, c, group)


def loincloth(m, color, back=True, belt_color=None, group='cloth'):
    for z in range(4, 10):
        put(m, 16, FRONT, z, color if z > 4 else shade(color, 0.8), group, 'Hips')
        if back:
            put(m, 16, BACK, z, color if z > 4 else shade(color, 0.8), group, 'Hips')
    for x in (15, 17):
        put(m, x, FRONT, 9, color, group)
        if back:
            put(m, x, BACK, 9, color, group)
    if belt_color:
        belt(m, belt_color)


def apron(m, color, strap=None, bottom=3, group='cloth', pocket=None):
    strap = strap or shade(color, 0.7)
    for z in range(bottom, 16):
        for x in range(14, 19):
            if z >= 13 and x in (14, 18):
                continue
            put(m, x, FRONT, z, color if z > bottom else shade(color, 0.85), group)
    for z in (16, 17, 18):
        put(m, 15, FRONT, z, strap, group); put(m, 17, FRONT, z, strap, group)
    put(m, 16, 17, 19, strap, group, 'Chest')
    put(m, 15, 17, 19, strap, group, 'Chest'); put(m, 17, 17, 19, strap, group, 'Chest')
    m.paint(strap, group, box=(14, 18, 15, 17, 10, 10))
    if pocket:
        put(m, 15, FRONT - 1, 7, pocket, group); put(m, 16, FRONT - 1, 7, pocket, group, 'Hips'); put(m, 17, FRONT - 1, 7, pocket, group)


# --- Gear ----------------------------------------------------------------------------------

def backpack(m, color, flap=None, roll=None, group='leather'):
    flap = flap or shade(color, 0.8)
    for x in range(14, 19):
        for y in (18, 19, 20):
            for z in range(10, 18):
                if (x in (14, 18)) and (z in (10, 17)) and y == 20:
                    continue
                c = flap if (y == 20 and z >= 14) else color
                put(m, x, y, z, c, group, 'Chest')
    put(m, 16, 21, 13, shade(color, 0.7), 'metal', 'Chest')
    if roll:
        for x in range(13, 20):
            for y in (18, 19, 20):
                put(m, x, y, 18, roll if x not in (13, 19) else shade(roll, 0.8), 'cloth', 'Chest')
    for z in range(10, 19):
        for x in (15, 17):
            if z >= 16:
                put(m, x, FRONT, z, shade(color, 0.7), group)


def bandolier(m, color, items=None, side='r', back=True, group='leather'):
    """A strap from one shoulder to the other hip, front and back; [items] on every other
    voxel of the front: cartridges, vials (a glass colour) or pouches."""
    cells = []
    for k in range(9):
        x = 18 - k // 2 if side == 'r' else 14 + k // 2
        cells.append((x, 18 - k))
    for i, (x, z) in enumerate(cells):
        put(m, x, FRONT, z, color, group)
        if back:
            put(m, x, BACK, z, color, group)
        if items and i % 2 == 1:
            mat = None
            c = items
            if isinstance(items, tuple) and len(items) == 2 and isinstance(items[1], tuple):
                c, mat = items
            put(m, x, FRONT - 1, z, c, 'glass' if mat else 'metal', None, mat)


def pouches(m, color, group='leather', front=True, back=True):
    if front:
        put(m, 14, FRONT, 9, color, group); put(m, 14, FRONT, 10, color, group)
        put(m, 18, FRONT, 9, color, group); put(m, 18, FRONT, 10, color, group)
    if back:
        for x in (15, 16, 17):
            put(m, x, BACK, 9, shade(color, 0.85), group, 'Hips'); put(m, x, BACK, 10, color, group, 'Hips')


def holster(m, color, side='r', group='leather'):
    x = 13 if side == 'r' else 19
    for z in (5, 6, 7, 8):
        for y in (15, 16):
            put(m, x, y, z, color, group)
    put(m, x, 17, 8, shade(color, 0.7), group)


def satchel(m, color, strap=None, group='leather', side='l'):
    strap = strap or shade(color, 0.75)
    x0, x1 = (17, 18) if side == 'l' else (14, 15)
    for x in range(x0, x1 + 1):
        for z in range(8, 12):
            put(m, x, BACK, z, color, group, 'Hips')
            put(m, x, BACK + 1, z, color if z < 11 else shade(color, 0.8), group, 'Hips')
    for k in range(8):
        x = 14 + k // 2 if side == 'l' else 18 - k // 2
        put(m, x, FRONT, 18 - k, strap, group)


def powder_horn(m, color=(220, 205, 170), tip=(150, 120, 60)):
    for (x, y, z) in ((14, 18, 11), (14, 19, 10), (15, 19, 10), (15, 19, 9), (16, 19, 9)):
        put(m, x, y, z, color, 'horn', 'Hips')
    put(m, 17, 19, 9, tip, 'metal', 'Hips')
    put(m, 14, 18, 12, (110, 80, 50), 'leather', 'Spine')


def quiver(m, color, fletch=(230, 230, 230), group='leather'):
    """A quiver across the back, the arrows' flights over the left shoulder, behind the head."""
    for k in range(9):
        x = 14 + k // 2
        z = 10 + k
        put(m, x, BACK + 1, z, color, group, 'Chest')
        put(m, x, BACK + 2, z, color, group, 'Chest')
    for (x, z) in ((18, 19), (19, 19), (18, 20), (19, 20), (19, 21), (20, 21)):
        put(m, x, BACK + 2, z, fletch, 'cloth', 'Chest')
    for k in range(9):
        put(m, 14 + k // 2, BACK, 10 + k, shade(color, 0.8), group, 'Chest') if k % 3 == 0 else None


def scroll_case(m, color, cap=(200, 170, 70)):
    for z in range(11, 21):
        put(m, 17, BACK + 2, z, color if z < 20 else cap, 'leather' if z < 20 else 'metal', 'Chest')
        put(m, 17, BACK + 3, z, color if z < 20 else cap, 'leather' if z < 20 else 'metal', 'Chest')
    put(m, 17, BACK, 14, shade(color, 0.7), 'leather', 'Chest')
    put(m, 17, BACK + 1, 14, shade(color, 0.7), 'leather', 'Chest')


def necklace(m, color, pendant=None, group='metal', mat=None):
    for (x, z) in ((15, 18), (17, 18), (16, 17)):
        put(m, x, FRONT, z, color, group, 'Chest')
    if pendant:
        put(m, 16, FRONT, 16, pendant, 'gem', 'Chest', mat)


def bone_necklace(m, color=(235, 228, 205), cord=(90, 60, 40)):
    for (x, z) in ((14, 18), (15, 17), (16, 17), (17, 17), (18, 18)):
        put(m, x, FRONT, z, cord, 'leather', 'Chest')
    for x in (15, 16, 17):
        put(m, x, FRONT, 16, color, 'bone', 'Chest')
    put(m, 16, FRONT, 15, color, 'bone', 'Chest')


def armband(m, color, emblem=None, side='l'):
    x = 21 if side == 'l' else 11
    m.paint(color, 'cloth', box=(x, x, 15, 17, 17, 18))
    if emblem:
        put(m, x, FRONT, 18, emblem, 'cloth', arm_side_bone(x))


def goggles_on_head(m, frame=(120, 90, 60), lens=(150, 210, 230)):
    from heads import hat
    hat(m, m.head, 'goggles', frame, trim=(70, 50, 35), extra=lens)


def vials(m, colors):
    """Little glass vials on the belt's front."""
    xs = [14, 15, 17, 18]
    for x, c in zip(xs, colors):
        put(m, x, FRONT, 9, c, 'glass', None, ('glass', 0.45))
        put(m, x, FRONT, 10, (200, 190, 170), 'cloth')


def warpaint(m, color, style='stripes'):
    hd = m.head
    if style == 'stripes':
        for x in (13, 14, 18, 19):
            for z in (hd.z0 + 1,):
                y = m.front_y(x, z)
                m.set((x, y, z), color, 'detail', 'Head', 'head')
    elif style == 'band':
        for x in range(hd.x0, hd.x1 + 1):
            z = hd.z0 + 3
            y = m.front_y(x, z)
            vx = m.get((x, y, z))
            if vx and vx.group not in ('eye',):
                m.set((x, y, z), color, 'detail', 'Head', 'head')
    elif style == 'chin':
        for x in range(15, 18):
            y = m.front_y(x, hd.z0)
            m.set((x, y, hd.z0), color, 'detail', 'Head', 'head')
    m.paint(color, 'detail', parts=('chest',), where=lambda p, v: p[1] == 15 and p[2] in (15, 16) and p[0] in (14, 15, 17, 18))


def plume(m, color, z_top=None):
    hd = m.head
    top = z_top or hd.z1 + 1
    for k in range(4):
        m.set((16, hd.y0 + 3 + k, top + 3 - abs(k - 1)), color, 'cloth', 'Head', 'head')
        m.set((16, hd.y0 + 3 + k, top + 2 - abs(k - 1)), shade(color, 0.85), 'cloth', 'Head', 'head')
    m.set((16, hd.y0 + 7, top + 1), color, 'cloth', 'Head', 'head')


def feather_in_hat(m, color, x=20, z=None):
    hd = m.head
    z = z or hd.z1 + 2
    for k in range(4):
        m.set((x + (1 if k > 1 else 0), hd.y0 + 4 + k, z + k), color if k < 3 else shade(color, 1.2), 'cloth', 'Head', 'head')
