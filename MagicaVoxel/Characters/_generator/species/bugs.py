"""Spiderfolk and insectfolk: generic, moth, ant, mantis, wasp and the horned beetles listed
as Heracross (rhinoceros, Hercules and atlas beetles and their kin: horned beetle folk in
general, not a copy of any one design)."""
from .common import Set, designs, beast, EYES
from .mammals import treat3
from . import concepts_extra as CX
from core import shade, mix, sat
import heads as H
import outfits as O
import extras as X
import freebody as F

WHITE = (240, 238, 232)
GLOW = ('emit', 0.95, 1)
GLASS = 0.55


def compound_eyes(m, hd, color=(40, 36, 44), shine=(200, 200, 220), size=2):
    """Big eyes on the head's front corners, a highlight in each."""
    for side in (-1, 1):
        x0 = hd.x0 if side < 0 else hd.x1 - size + 1
        for x in range(x0, x0 + size):
            for z in range(hd.z0 + 2, hd.z0 + 2 + size + 1):
                y = m.front_y(x, z)
                if y is not None:
                    m.set((x, y, z), color, 'eye', 'Head', 'head')
        xs = hd.x0 if side < 0 else hd.x1
        for y in range(hd.y0 + 1, hd.y0 + 1 + size):
            for z in range(hd.z0 + 2, hd.z0 + 2 + size + 1):
                m.set((xs, y, z), color, 'eye', 'Head', 'head')
        hx = x0 + (0 if side < 0 else size - 1)
        y = m.front_y(hx, hd.z0 + 2 + size)
        if y is not None:
            m.set((hx, y, hd.z0 + 2 + size), shine, 'eye', 'Head', 'head')


def mandibles(m, hd, color, size=1):
    for side in (-1, 1):
        x = 16 + side * 2
        m.set((x, hd.y0 - 1, hd.z0), color, 'chitin', 'Head', 'head')
        m.set((x - side, hd.y0 - 2, hd.z0), color, 'chitin', 'Head', 'head')
        if size >= 2:
            m.set((x, hd.y0 - 2, hd.z0), color, 'chitin', 'Head', 'head')
            m.set((x - side, hd.y0 - 3, hd.z0), shade(color, 0.8), 'chitin', 'Head', 'head')
            m.set((x - side * 2, hd.y0 - 3, hd.z0), shade(color, 0.8), 'chitin', 'Head', 'head')


def segments(color):
    def f(m):
        m.paint(color, None, parts=('chest', 'spine', 'hips', 'uarm_r', 'uarm_l', 'larm_r', 'larm_l', 'uleg_r', 'uleg_l', 'lleg_r', 'lleg_l'),
                where=lambda p, v: v.group == m.skin_group and (p[2] in (12, 15, 5, 2) if v.part in ('chest', 'spine', 'hips', 'uleg_r', 'uleg_l', 'lleg_r', 'lleg_l') else p[0] in (8, 24, 11, 21)))
    return f


def elytra(color, line=None, spots=None, sheen=None, depth=3):
    """A beetle's wing cases: a dome on the back (on the chest), parted down the middle."""
    line = line or shade(color, 0.55)
    def f(m):
        for x in range(11, 22):
            for y in range(18, 18 + depth + 1):
                for z in range(7, 20):
                    d = ((x + 0.5 - 16.5) / 5.6) ** 2 + ((y + 0.5 - 17.4) / (depth + 0.5)) ** 2 + ((z + 0.5 - 13.5) / 6.6) ** 2
                    if d > 1 or (y == 18 and not 14 <= x <= 18) or X.arm_room((x, y, z)):
                        continue
                    c = color
                    if x == 16:
                        c = line
                    elif spots and X.h((x // 2, 0, z // 2), 91) < 0.3 and d < 0.8:
                        c = spots
                    elif sheen and (x + z) % 4 == 0:
                        c = sheen
                    m.set((x, y, z), c, 'chitin', 'Chest')
    return f


def bug(chitin=(60, 120, 60), head=None, head_color=None, eye_color=(40, 36, 44), eye_size=2, antenna=None, antenna_style='thin',
        antenna_tip=None, mandible=None, mandible_size=1, abdomen=None, abdomen_color=None, abdomen_pattern=None, abdomen_second=None,
        wings=None, wing_color=None, wing_tip=None, wing_glass=None, wing_second=None, wing_span=8, belly=None, pattern=None,
        outfit=None, outfit_kw=None, hat=False, extras=None, seg=True, back=None, glow_abdomen=False, horn=None, horn_color=None):
    head = head or dict(w=9, d=8, h=7, style='round')
    hc = head_color or chitin
    def face(m, hd):
        compound_eyes(m, hd, eye_color, size=eye_size)
        if mandible:
            mandibles(m, hd, mandible, mandible_size)
        if antenna:
            X.antennae(m, antenna, antenna_style, tip=antenna_tip)
        if horn:
            beetle_horn(m, hd, horn, horn_color or shade(hc, 0.9))
    def pat(m):
        if seg:
            segments(shade(chitin, 0.75))(m)
        if pattern:
            pattern(m)
    def after(m):
        if back:
            back(m)
        if wings:
            X.back_wings(m, wing_color or (220, 230, 240), tip=wing_tip, style=wings, glass=wing_glass, span=wing_span, second=wing_second)
        if abdomen:
            X.abdomen(m, abdomen_color or chitin, pattern=abdomen_pattern, style=abdomen, second=abdomen_second)
            if glow_abdomen:
                for p, v in m.v.items():
                    if v.bone == 'Hips' and v.group == 'chitin' and p[1] >= 22:
                        v.mat = GLOW
                        v.group = 'light'
                        v.color = glow_abdomen
        if extras:
            extras(m)
    return beast(chitin, skin_group='chitin', head=head, head_color=head_color, eyes=None, face=face, pattern=pat, belly_color=belly,
                 outfit=outfit, outfit_kw=outfit_kw, hat=hat, extras=after)


def beetle_horn(m, hd, style, color):
    """rhino (one great horn from the face, up past the head and curving back), hercules (a
    long horn forward and a second down from above to meet it), atlas (the great horn and a
    shorter one each side), goliath (a forked horn), stag (two mandibles). Each is lighter
    than the shell, so it reads against the head."""
    top = hd.z1
    light = shade(color, 1.3)
    if style in ('rhino', 'atlas'):
        pts = [(16, hd.y0 - 1, hd.z0 + 2, 1.5, 1.2, 1.5), (16, hd.y0 - 2.5, hd.z0 + 5, 1.3, 1.1, 1.3), (16, hd.y0 - 3, top, 1.1, 1, 1.1),
               (16, hd.y0 - 2.5, top + 3, .9, .9, .9), (16, hd.y0 - 0.5, top + 5, .7, .7, .7), (16, hd.y0 + 1.5, top + 5.5, .55, .55, .55)]
        X.sweep(m, pts, lambda t, p: light if t > 0.8 else color, 'horn', 'Head')
        if style == 'atlas':
            for side in (-1, 1):
                pts3 = [(16 + side * 3, hd.y0 + 1, top, .8, .8, .8), (16 + side * 4.5, hd.y0 - 1, top + 2, .7, .7, .7), (16 + side * 4.5, hd.y0 - 3, top + 2.5, .55, .55, .55)]
                X.sweep(m, pts3, lambda t, p: light if t > 0.7 else color, 'horn', 'Head')
    elif style == 'hercules':
        pts = [(16, hd.y0 - 1, hd.z0 + 2, 1.3, 1.1, 1.3), (16, hd.y0 - 3.5, hd.z0 + 3, 1.0, 1, 1.0), (16, hd.y0 - 6, hd.z0 + 4, .8, .8, .8),
               (16, hd.y0 - 8, hd.z0 + 6, .6, .6, .6)]
        X.sweep(m, pts, lambda t, p: light if t > 0.75 else color, 'horn', 'Head')
        pts2 = [(16, hd.y0 + 3, top + 1, 1.2, 1.2, 1.2), (16, hd.y0, top + 3, 1, 1, 1), (16, hd.y0 - 3.5, top + 2, .8, .8, .8),
                (16, hd.y0 - 6.5, top - 1.5, .6, .6, .6)]
        X.sweep(m, pts2, lambda t, p: light if t > 0.75 else shade(color, 0.9), 'horn', 'Head')
        for y in range(hd.y0 - 5, hd.y0 - 1):
            m.set((16, y, top - 1), (240, 220, 160), 'horn', 'Head', 'head') if (y % 2 == 0) else None
    elif style == 'goliath':
        pts = [(16, hd.y0 + 1, top + 1, 1, 1, 1), (16, hd.y0, top + 3, .9, .9, .9)]
        X.sweep(m, pts, color, 'horn', 'Head')
        for side in (-1, 1):
            m.set((16 + side, hd.y0, top + 4), color, 'horn', 'Head', 'head')
            m.set((16 + side * 2, hd.y0, top + 5), light, 'horn', 'Head', 'head')
    elif style == 'stag':
        for side in (-1, 1):
            pts = [(16 + side * 2, hd.y0 - 1, hd.z0 + 1, .8, .8, .8), (16 + side * 3, hd.y0 - 3, hd.z0 + 1, .7, .7, .7),
                   (16 + side * 3, hd.y0 - 5, hd.z0 + 2, .6, .6, .6), (16 + side * 1.5, hd.y0 - 6.5, hd.z0 + 2, .55, .55, .55)]
            X.sweep(m, pts, lambda t, p: light if t > 0.8 else color, 'horn', 'Head')
            m.set((16 + side * 3, hd.y0 - 4, hd.z0 + 3), light, 'horn', 'Head', 'head')


# --- Spiderfolk ------------------------------------------------------------------------------

def spider_eyes(m, hd, color=(30, 26, 34), shine=(220, 60, 60), jumping=False):
    """Eight eyes: two big ones low in front (bigger still on a jumping spider), two small ones
    beside them, four in a row above."""
    big = [(14, 15), (18, 17)] if not jumping else [(13, 15), (17, 19)]
    for (xa, xb) in big:
        for x in range(xa, xb + 1):
            for z in range(hd.z0 + 2, hd.z0 + 4 + (1 if jumping else 0)):
                y = m.front_y(x, z)
                if y is not None:
                    m.set((x, y, z), color, 'eye', 'Head', 'head')
        y = m.front_y(xa, hd.z0 + 3 + (1 if jumping else 0))
        if y is not None:
            m.set((xa, y, hd.z0 + 3 + (1 if jumping else 0)), shine, 'eye', 'Head', 'head')
    for x in (hd.x0 + 1, hd.x1 - 1):
        y = m.front_y(x, hd.z0 + 3)
        if y is not None:
            m.set((x, y, hd.z0 + 3), color, 'eye', 'Head', 'head')
    for x in (13, 15, 17, 19):
        y = m.front_y(x, hd.z0 + 5 + (1 if jumping else 0))
        if y is not None:
            m.set((x, y, hd.z0 + 5 + (1 if jumping else 0)), color, 'eye', 'Head', 'head')


def chelicerae(m, hd, color, fang=(240, 236, 220)):
    for x in (15, 17):
        m.set((x, hd.y0 - 1, hd.z0), color, 'chitin', 'Head', 'head')
        m.set((x, hd.y0 - 1, hd.z0 + 1), color, 'chitin', 'Head', 'head')
        m.set((x, hd.y0 - 1, hd.z0 - 1), fang, 'bone', 'Head', 'head')


def hairy(colors):
    def f(m):
        X.mottle(m, colors, density=0.35, seed=93, groups=('chitin',))
    return f


def spider(chitin=(50, 44, 40), head=None, eye_color=(30, 26, 34), shine=(220, 60, 60), mark=None, abdomen_color=None, legs=True,
           leg_color=None, pattern=None, outfit=None, outfit_kw=None, hat=False, extras=None, jumping=False, fuzz=None, pairs=2):
    head = head or dict(w=9, d=8, h=7, style='round')
    def face(m, hd):
        spider_eyes(m, hd, eye_color, shine, jumping)
        chelicerae(m, hd, shade(chitin, 0.8))
    def pat(m):
        if fuzz:
            hairy(fuzz)(m)
        if pattern:
            pattern(m)
    def after(m):
        X.abdomen(m, abdomen_color or chitin, pattern=mark, style='spider')
        if fuzz:
            X.mottle(m, fuzz, density=0.3, seed=95, groups=('chitin',))
        if legs:
            X.spider_legs(m, leg_color or chitin, joint=shade(leg_color or chitin, 0.7), pairs=pairs)
        if extras:
            extras(m)
    return beast(chitin, skin_group='chitin', head=head, eyes=None, face=face, pattern=pat, outfit=outfit, outfit_kw=outfit_kw, hat=hat,
                 extras=after)


def peacock_fan(m):
    for x in range(12, 21):
        for z in range(8, 15):
            d = ((x - 16) / 4.5) ** 2 + ((z - 9) / 5.5) ** 2
            if d <= 1 and z >= 9:
                c = (220, 90, 40) if d > 0.6 else ((60, 140, 220) if d > 0.3 else (240, 210, 60))
                m.set((x, 27, z), c, 'chitin', 'Hips')


SPIDERS = [
    ('Widow', dict(chitin=(30, 28, 34), mark=(210, 30, 40), outfit='rogue', hat=False, outfit_kw=dict(mask=False, main=(30, 28, 34)))),
    ('Tarantula', dict(chitin=(80, 60, 44), fuzz=[(100, 76, 54), (60, 46, 34), (180, 110, 60)], outfit='barbarian', hat=False,
                       outfit_kw=dict(paint=False))),
    ('Jumper', dict(chitin=(50, 50, 56), jumping=True, shine=(120, 220, 120), fuzz=[(70, 70, 76), (230, 230, 230)], mark=WHITE, outfit='scout',
                    hat=False, outfit_kw=dict(quiver=False))),
    ('Wolf', dict(chitin=(110, 96, 80), fuzz=[(90, 76, 60), (140, 124, 100)], outfit='hunter', hat=True)),
    ('Orbweaver', dict(chitin=(40, 36, 30), abdomen_color=(240, 200, 50), mark=(40, 36, 30), outfit='bard', hat=False)),
    ('Peacock', dict(chitin=(60, 50, 50), extras=peacock_fan, jumping=True, outfit='noble', hat=False)),
    ('Crab', dict(chitin=(240, 236, 200), abdomen_color=(250, 240, 180), mark=(220, 100, 110), outfit='white_mage', hat=False)),
    ('Trapdoor', dict(chitin=(60, 46, 40), outfit='miner', hat=True)),
    ('Huntsman', dict(chitin=(130, 110, 90), pairs=2, outfit='sharpshooter', hat=False)),
    ('Recluse', dict(chitin=(150, 120, 90), mark=(80, 60, 40), outfit='apothecary', hat=False)),
    ('Weaver', dict(chitin=(90, 70, 110), abdomen_color=(120, 90, 150), mark=(230, 220, 240), outfit='psychic', hat=False)),
    ('Matriarch', dict(chitin=(40, 34, 40), mark=(160, 60, 200), outfit='necromancer', hat=False, shine=(160, 60, 200),
                       extras=lambda m: H.hat(m, m.head, 'circlet', (200, 200, 210), extra=(160, 60, 200)))),
    ('Cellar', dict(chitin=(170, 150, 120), outfit='peasant', hat=True)),
]


def drider(kind):
    """A spider's body below, a figure's torso rising from its front."""
    chitin = (30, 28, 34) if kind == 'widow' else (80, 60, 44)
    m = F.body(chitin, 'chitin', leg=8, leg_w=2, leg_d=2, gap=1, torso_w=7, torso_d=4, torso_h=9, arm_len=8, arm_w=2, arm_d=2,
               arm_pose='a', head=dict(w=9, d=8, h=7, style='round'), neck=1, foot_len=0)
    m.v = {p: v for p, v in m.v.items() if not (v.part or '').startswith(('uleg', 'lleg', 'foot'))}
    b = m.body
    hd = m.head
    spider_eyes(m, hd)
    chelicerae(m, hd, shade(chitin, 0.8))
    m.ellipsoid(16, 18, 6.5, 4, 3.5, 2.5, chitin, 'chitin')
    m.ellipsoid(16, 25, 9, 5.5, 6, 5, chitin, 'chitin')
    if kind == 'widow':
        for (y, z) in ((31, 9), (31, 10), (31, 8), (30, 11), (30, 7)):
            m.set((16, y, z), (210, 30, 40), 'chitin')
    else:
        X.mottle(m, [(100, 76, 54), (60, 46, 34), (180, 110, 60)], density=0.35, groups=('chitin',))
    for side in (-1, 1):
        for i in range(4):
            y0 = 16 + i * 2.4
            pts = [(16 + side * 3, y0, 6.5), (16 + side * 8, y0 - 1 + i * 0.8, 11), (16 + side * 12, y0 - 2 + i * 1.6, 7), (16 + side * 14, y0 - 3 + i * 2.2, 0.5)]
            X.sweep(m, [(x, y, z, .7, .7, .7) for x, y, z in pts], lambda t, p: shade(chitin, 0.7) if abs(t - 0.4) < 0.06 else chitin, 'chitin', None)
    F.dress(m, plate=(110, 114, 122) if kind != 'widow' else None, belt=(60, 40, 30), buckle=(222, 184, 72), sash=(120, 30, 40) if kind == 'widow' else None)
    return m

# --- Insectfolk ------------------------------------------------------------------------------

def ladybug(m):
    elytra((210, 30, 30), line=(30, 30, 30), spots=(30, 30, 30))(m)


def scarab(m):
    elytra((40, 140, 90), line=(20, 70, 50), sheen=(200, 180, 60))(m)


GENERIC = [
    ('Ladybug', dict(chitin=(30, 30, 34), head=dict(w=9, d=8, h=7, style='round'), antenna=(30, 30, 34), back=ladybug, outfit='bard', hat=False)),
    ('Firefly', dict(chitin=(50, 46, 40), head_color=(220, 90, 60), antenna=(50, 46, 40), abdomen='ant', abdomen_color=(240, 230, 120),
                     glow_abdomen=(250, 240, 140), wings='insect', wing_color=(200, 210, 220), wing_glass=GLASS, wing_tip=(90, 80, 70), wing_span=6,
                     outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('Scarab', dict(chitin=(30, 90, 70), back=scarab, antenna=(30, 90, 70), antenna_style='clubbed', outfit='cleric', hat=False,
                    outfit_kw=dict(main=(30, 40, 60), trim=(222, 184, 72)))),
    ('Dragonfly', dict(chitin=(40, 120, 180), eye_color=(40, 160, 120), eye_size=3, wings='insect', wing_color=(190, 220, 240), wing_glass=0.65,
                       wing_tip=(60, 90, 110), wing_span=11, extras=lambda m: X.tail(m, 'snake', (40, 120, 180), tip=(20, 60, 100), group='chitin'),
                       outfit='air_mage', hat=False)),
    ('Grasshopper', dict(chitin=(110, 170, 60), eye_color=(150, 120, 60), antenna=(110, 170, 60), antenna_style='long', mandible=(80, 120, 40),
                         outfit='peasant', hat=True)),
    ('Cicada', dict(chitin=(80, 100, 60), eye_color=(200, 40, 40), wings='insect', wing_color=(220, 230, 220), wing_glass=0.6,
                    wing_tip=(90, 110, 70), outfit='bard', hat=False)),
    ('Stag', dict(chitin=(70, 40, 30), horn='stag', horn_color=(90, 50, 34), back=elytra((80, 46, 32)), outfit='warrior', hat=False)),
    ('Roach', dict(chitin=(110, 60, 30), antenna=(110, 60, 30), antenna_style='long', back=elytra((130, 70, 36), line=(70, 36, 20)), outfit='rogue',
                   hat=False, outfit_kw=dict(mask=False))),
    ('Weevil', dict(chitin=(90, 80, 70), extras=lambda m: [m.set((16, m.head.y0 - k, m.head.z0 + 2), (90, 80, 70), 'chitin', 'Head', 'head') for k in range(1, 5)],
                    antenna=(90, 80, 70), antenna_style='elbowed', back=elytra((100, 90, 80)), outfit='scholar', hat=False)),
    ('Jewel', dict(chitin=(40, 160, 120), back=elytra((40, 170, 130), sheen=(160, 60, 200)), antenna=(40, 160, 120), outfit='noble', hat=False)),
    ('Stick', dict(chitin=(130, 110, 70), head=dict(w=7, d=8, h=7, style='soft'), antenna=(130, 110, 70), antenna_style='long', outfit='nature_mage',
                   hat=False)),
    ('Shieldbug', dict(chitin=(80, 130, 50), back=elytra((90, 150, 60), line=(60, 100, 40)), outfit='guardian', hat=False, outfit_kw=dict(cape=False))),
    ('Locust', dict(chitin=(170, 140, 70), antenna=(170, 140, 70), mandible=(120, 100, 50), wings='insect', wing_color=(220, 210, 170),
                    wing_glass=0.5, wing_tip=(140, 110, 60), outfit='assault', hat=False)),
]

# --- Moth ------------------------------------------------------------------------------------

def fuzz_collar(color):
    def f(m):
        O.mantle(m, color, highlight=shade(color, 1.15), group='fur')
    return f


MOTH = dict(head=dict(w=9, d=8, h=7, style='round'), antenna_style='feathery', wings='moth', seg=False, wing_span=9)


def moth(**kw):
    d = dict(MOTH)
    ex = kw.pop('extras', None)
    fur = kw.pop('fur', None)
    def extras(m):
        X.mottle(m, [shade(m.skin, 1.1), shade(m.skin, 0.9)], density=0.4, seed=99, groups=('chitin',))
        if fur:
            fuzz_collar(fur)(m)
        if ex:
            ex(m)
    d['extras'] = extras
    d.update(kw)
    d.setdefault('antenna', shade(d.get('chitin', (150, 130, 110)), 0.8))
    return bug(**d)


def deaths_head(m):
    for (x, z) in ((15, 15), (16, 15), (17, 15), (15, 14), (17, 14), (16, 13)):
        m.set((x, 14, z), (240, 220, 160), 'chitin', None)


MOTHS = [
    ('Luna', dict(chitin=(200, 230, 180), wing_color=(170, 230, 170), wing_tip=(140, 120, 90), wing_second=(240, 210, 120), fur=(240, 246, 236),
                  outfit='white_mage', hat=False)),
    ('Atlas', dict(chitin=(160, 70, 40), wing_color=(200, 90, 50), wing_tip=(240, 220, 200), wing_second=(240, 240, 230), wing_span=11,
                   fur=(200, 110, 70), outfit='noble', hat=False)),
    ('RosyMaple', dict(chitin=(240, 160, 180), wing_color=(250, 200, 80), wing_tip=(240, 120, 160), wing_second=(240, 140, 170),
                       fur=(250, 220, 120), outfit='bard', hat=False)),
    ('DeathsHead', dict(chitin=(60, 50, 44), wing_color=(80, 70, 60), wing_tip=(40, 36, 30), wing_second=(200, 170, 60), extras=deaths_head,
                        fur=(90, 80, 70), outfit='necromancer', hat=False)),
    ('Polyphemus', dict(chitin=(170, 130, 90), wing_color=(190, 150, 100), wing_tip=(120, 90, 60), wing_second=(60, 90, 160), fur=(200, 170, 130),
                        outfit='psychic', hat=False)),
    ('Tiger', dict(chitin=(240, 236, 220), wing_color=(240, 236, 220), wing_tip=(30, 30, 30), wing_second=(30, 30, 30), fur=(240, 150, 60),
                   outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('Silk', dict(chitin=(246, 244, 238), wing_color=(246, 244, 238), wing_tip=(220, 216, 206), wing_second=(230, 226, 216), fur=(252, 250, 246),
                  outfit='cleric', hat=False)),
    ('Hawk', dict(chitin=(110, 100, 80), wings='insect', wing_color=(150, 140, 110), wing_tip=(80, 70, 50), wing_span=10, fur=(130, 120, 100),
                  outfit='sharpshooter', hat=False)),
    ('Comet', dict(chitin=(250, 210, 80), wing_color=(250, 200, 60), wing_tip=(200, 80, 60), wing_second=(200, 120, 60), fur=(250, 230, 160),
                   outfit='fire_mage', hat=False)),
    ('Dusk', dict(chitin=(130, 120, 110), wing_color=(140, 130, 120), wing_tip=(90, 80, 70), wing_second=(180, 170, 160),
                                           fur=(150, 140, 130), outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Lantern', dict(chitin=(120, 110, 140), wing_color=(130, 120, 160), wing_tip=(70, 60, 90), wing_second=(240, 230, 150), fur=(170, 160, 190),
                     outfit='apothecary', hat=False, extras=lambda m: m.set((16, 13, 9), (250, 230, 140), 'light', 'Hips', None, GLOW))),
    ('Peppered', dict(chitin=(200, 196, 190), wing_color=(210, 206, 200), wing_tip=(40, 40, 40), wing_second=(60, 60, 60), fur=(220, 216, 210),
                      outfit='scholar', hat=False)),
]

# --- Ant -------------------------------------------------------------------------------------

ANT = dict(head=dict(w=9, d=8, h=7, style='round'), antenna_style='elbowed', abdomen='ant', mandible_size=1)


def ant(**kw):
    d = dict(ANT)
    d.update(kw)
    d.setdefault('antenna', d.get('chitin', (40, 36, 34)))
    d.setdefault('mandible', shade(d.get('chitin', (40, 36, 34)), 0.85))
    return bug(**d)


def carried_leaf(m, color=(90, 160, 60), vein=(60, 120, 40)):
    """A leaf carried on the back (on the chest), rising behind the head."""
    for x in range(11, 22):
        for z in range(12, 30):
            d = ((x - 16) / 5.2) ** 2 + ((z - 21) / 8.5) ** 2
            if d <= 1:
                y = 21 if z >= 19 else 20
                m.set((x, y, z), vein if x == 16 else color, 'plant', 'Chest')
    for z in range(14, 19):
        m.set((16, 19, z), vein, 'plant', 'Chest')
        m.set((16, 18, z), vein, 'plant', 'Chest')


def ant_crown(m):
    H.hat(m, m.head, 'crown', (222, 184, 72), extra=(220, 40, 60))


ANTS = [
    ('Worker', dict(chitin=(40, 36, 34), outfit='miner', hat=True)),
    ('Fire', dict(chitin=(190, 70, 40), abdomen_color=(60, 40, 30), outfit='fire_mage', hat=False)),
    ('Carpenter', dict(chitin=(60, 40, 34), outfit='smith', hat=False)),
    ('Bullet', dict(chitin=(40, 30, 26), mandible_size=2, outfit='assault', hat=False)),
    ('Leafcutter', dict(chitin=(150, 80, 40), outfit='nature_mage', hat=False, extras=lambda m: carried_leaf(m))),
    ('Soldier', dict(chitin=(120, 50, 30), head=dict(w=11, d=9, h=8, style='round'), mandible_size=2, outfit='heavy', hat=False)),
    ('Honeypot', dict(chitin=(150, 100, 40), abdomen_color=(240, 180, 40), outfit='merchant', hat=False)),
    ('Weaver', dict(chitin=(170, 150, 50), abdomen_color=(140, 170, 60), outfit='bard', hat=False)),
    ('Army', dict(chitin=(90, 60, 40), mandible_size=2, outfit='tactician', hat=True, outfit_kw=dict(main=(70, 40, 30)))),
    ('Queen', dict(chitin=(60, 30, 40), extras=ant_crown, wings='insect', wing_color=(220, 210, 220), wing_glass=GLASS, wing_tip=(120, 90, 110),
                   wing_span=8, outfit='noble', hat=False, outfit_kw=dict(cape=True, main=(90, 30, 60)))),
    ('Scout', dict(chitin=(70, 50, 36), outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('Velvet', dict(chitin=(30, 30, 30), abdomen_color=(220, 40, 40), abdomen_pattern=(30, 30, 30), outfit='rogue', hat=False,
                    outfit_kw=dict(mask=False))),
    ('Guard', dict(chitin=(50, 40, 40), outfit='guardian', hat=False, outfit_kw=dict(cape=False))),
]

# --- Mantis ----------------------------------------------------------------------------------

def mantis_head(m, hd, color, eye=(150, 200, 90), pupil=(30, 30, 30)):
    """A mantis's head: wide at the eyes, narrowing to the jaw, the eyes bulging at its top
    corners, a pupil in each."""
    for side in (-1, 1):
        x = hd.x0 - 1 if side < 0 else hd.x1 + 1
        for y in range(hd.y0, hd.y0 + 3):
            for z in range(hd.z1 - 2, hd.z1 + 1):
                m.set((x, y, z), eye, 'eye', 'Head', 'head')
        m.set((x + side, hd.y0 + 1, hd.z1 - 1), eye, 'eye', 'Head', 'head')
        m.set((x, hd.y0 - 1, hd.z1 - 1), pupil, 'eye', 'Head', 'head')
        m.set((x - side, hd.y0 - 1, hd.z1 - 1), eye, 'eye', 'Head', 'head')
    for x in (15, 16, 17):
        m.set((x, hd.y0 - 1, hd.z0), shade(color, 0.8), 'chitin', 'Head', 'head')


def blades(color, spike=None):
    """Raptorial forearms: a serrated blade along the front of each forearm, and spikes on top."""
    spike = spike or shade(color, 1.25)
    def f(m):
        for x in (6, 7, 8, 9, 23, 24, 25, 26):
            bone = 'RightLowerArm' if x < 16 else 'LeftLowerArm'
            if x in (9, 23):
                bone = 'RightUpperArm' if x < 16 else 'LeftUpperArm'
            m.set((x, 14, 18), color, 'chitin', bone)
            m.set((x, 14, 17), color, 'chitin', bone)
            if x % 2 == 0:
                m.set((x, 13, 17), spike, 'horn', bone)
            m.set((x, 16, 19), spike if x % 2 else color, 'horn', bone)
    return f


def mantis(chitin=(110, 180, 70), eye=(150, 200, 90), wing_color=(150, 200, 110), outfit=None, outfit_kw=None, hat=False, extras=None,
           pattern=None, wings=True, antenna=None, flowers=None):
    def face(m, hd):
        mantis_head(m, hd, chitin, eye)
        X.antennae(m, antenna or chitin, 'thin', length=6)
    def after(m):
        blades(chitin)(m)
        if wings:
            for z in range(8, 19):
                for x in (14, 15, 16, 17, 18):
                    m.set((x, 19, z), wing_color if x != 16 else shade(wing_color, 0.8), 'chitin', 'Chest')
            for x in (15, 16, 17):
                m.set((x, 20, 9), shade(wing_color, 0.8), 'chitin', 'Chest')
        if flowers:
            for (x, z) in ((13, 18), (19, 18)):
                m.set((x, 19, z), flowers, 'petal', 'RightUpperArm' if x < 16 else 'LeftUpperArm')
        if extras:
            extras(m)
    return beast(chitin, skin_group='chitin', head=dict(w=9, d=7, h=7, style='wedge'), eyes=None, face=face, pattern=pattern,
                 outfit=outfit, outfit_kw=outfit_kw, hat=hat, extras=after)


MANTISES = [
    ('Praying', dict(outfit='monk', hat=False, outfit_kw=dict(main=(60, 100, 50), trim=(200, 170, 70)))),
    ('Orchid', dict(chitin=(246, 210, 226), eye=(240, 170, 200), wing_color=(250, 220, 236), flowers=(240, 140, 190), outfit='psychic', hat=False)),
    ('Ghost', dict(chitin=(120, 100, 70), eye=(140, 120, 80), wing_color=(130, 110, 80), outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('DevilsFlower', dict(chitin=(220, 220, 200), eye=(120, 160, 90), wing_color=(80, 120, 200), outfit='noble', hat=False)),
    ('Bladeking', dict(chitin=(80, 140, 60), outfit='gladiator', hat=False)),
    ('DeadLeaf', dict(chitin=(160, 110, 60), eye=(170, 130, 80), wing_color=(170, 120, 70), outfit='hunter', hat=False)),
    ('Jade', dict(chitin=(60, 170, 110), eye=(220, 220, 120), outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('Duelist', dict(chitin=(100, 160, 80), outfit='bard', hat=True)),
    ('Sentinel', dict(chitin=(140, 170, 90), outfit='guardian', hat=False, outfit_kw=dict(cape=False))),
    ('Shadow', dict(chitin=(50, 60, 50), eye=(200, 40, 40), wing_color=(60, 70, 60), outfit='assault', hat=False)),
    ('Sage', dict(chitin=(150, 170, 120), outfit='scholar', hat=False)),
    ('Reaper', dict(chitin=(60, 56, 64), eye=(120, 255, 140), wing_color=(70, 66, 74), outfit='necromancer', hat=False)),
]


def mantis_concept():
    """A mantis upright on two thin legs, two arms hanging and its raptorial pair folded."""
    c = (110, 180, 70)
    m = F.body(c, 'chitin', leg=11, leg_w=1, leg_d=1, gap=5, torso_w=5, torso_d=3, torso_h=12, arm_len=9, arm_w=2, arm_d=2,
               arm_pose='a', head=dict(w=9, d=7, h=7, style='wedge'), neck=3, foot_len=1)
    hd = m.head
    mantis_head(m, hd, c)
    X.antennae(m, c, 'thin', length=6)
    b = m.body
    for side in (-1, 1):
        pts = [(16 + side * 3, b.cy - 1, b.top - 1), (16 + side * 4, b.cy - 6, b.top - 1), (16 + side * 4, b.cy - 6, b.top + 4), (16 + side * 4, b.cy - 4, b.top + 5)]
        X.sweep(m, [(x, y, z, .8, .8, .8) for x, y, z in pts], c, 'chitin', None)
        for k in range(4):
            m.set((16 + side * 4, b.cy - 7, b.top + k), (170, 220, 120), 'horn')
    for z in range(b.hip - 2, b.top - 1):
        for x in range(14, 19):
            m.set((x, b.back + 1, z), (150, 200, 110), 'chitin')
    X.sweep(m, [(16, b.back, b.hip, 2, 2, 2), (16, b.back + 4, b.hip - 2, 2.4, 2.8, 2.4), (16, b.back + 8, b.hip - 1, 1.6, 2, 1.6)], c, 'chitin', None)
    return m

# --- Wasp ------------------------------------------------------------------------------------

WASP = dict(head=dict(w=9, d=8, h=7, style='round'), eye_color=(40, 36, 30), antenna_style='elbowed', abdomen='wasp', wings='insect',
            wing_color=(210, 220, 230), wing_glass=0.6, wing_tip=(90, 90, 80), wing_span=7)


def wasp(**kw):
    d = dict(WASP)
    d.update(kw)
    d.setdefault('antenna', (40, 36, 30))
    d.setdefault('abdomen_color', d.get('chitin', (240, 200, 40)))
    d.setdefault('abdomen_second', (40, 36, 30))
    d.setdefault('mandible', (60, 50, 30))
    return bug(**d)


def fuzzy(m):
    X.mottle(m, [shade(m.skin, 1.12), shade(m.skin, 0.88)], density=0.45, seed=101, groups=('chitin',))
    O.mantle(m, shade(m.skin, 1.05), highlight=shade(m.skin, 1.2), group='fur')


WASPS = [
    ('Yellowjacket', dict(chitin=(240, 200, 40), outfit='assault', hat=False)),
    ('Hornet', dict(chitin=(160, 90, 40), head_color=(220, 170, 60), abdomen_color=(220, 170, 50), abdomen_second=(90, 50, 30),
                    head=dict(w=11, d=8, h=8, style='round'), outfit='heavy', hat=False)),
    ('Paper', dict(chitin=(200, 120, 40), abdomen_color=(220, 140, 40), outfit='scholar', hat=False)),
    ('MudDauber', dict(chitin=(30, 40, 80), abdomen_color=(40, 60, 120), abdomen_second=(20, 30, 50), wing_color=(80, 100, 160), outfit='smith',
                       hat=False)),
    ('TarantulaHawk', dict(chitin=(30, 40, 70), abdomen_color=(30, 40, 80), abdomen_second=(20, 26, 50), wing_color=(240, 140, 40), wing_glass=None,
                           wing_tip=(200, 100, 30), outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Honeybee', dict(chitin=(200, 150, 50), abdomen='bee', abdomen_color=(220, 170, 50), extras=fuzzy, outfit='peasant', hat=False)),
    ('Bumblebee', dict(chitin=(40, 36, 30), abdomen='bee', abdomen_color=(250, 210, 40), abdomen_second=(40, 36, 30), wing_span=5, extras=fuzzy,
                       outfit='bard', hat=True)),
    ('Carpenter', dict(chitin=(30, 30, 34), abdomen='bee', abdomen_color=(40, 40, 44), abdomen_second=(30, 30, 34), extras=fuzzy, outfit='miner',
                       hat=True)),
    ('Orchid', dict(chitin=(40, 170, 110), abdomen='bee', abdomen_color=(60, 190, 120), abdomen_second=(30, 120, 90), outfit='nature_mage',
                    hat=False)),
    ('Warden', dict(chitin=(240, 200, 40), outfit='guardian', hat=False, outfit_kw=dict(cape=False, emblem='chevron', second=(40, 36, 30)))),
    ('Queen', dict(chitin=(230, 180, 40), outfit='noble', hat=False, extras=lambda m: H.hat(m, m.head, 'crown', (222, 184, 72), extra=(40, 36, 30)))),
    ('Stinger', dict(chitin=(250, 210, 60), outfit='sharpshooter', hat=False)),
    ('Swarmcaller', dict(chitin=(200, 160, 40), outfit='psychic', hat=False)),
]

# --- Heracross: horned beetles ---------------------------------------------------------------

def beetle(**kw):
    d = dict(head=dict(w=9, d=8, h=7, style='round'), seg=True)
    shell = kw.pop('shell', None)
    sheen = kw.pop('sheen', None)
    d.update(kw)
    chitin = d.get('chitin', (40, 70, 150))
    d['back'] = elytra(shell or chitin, sheen=sheen)
    d.setdefault('horn', 'rhino')
    d.setdefault('horn_color', shade(chitin, 1.12))
    return bug(**d)


BEETLES = [
    ('Bluehorn', dict(chitin=(50, 90, 170), eye_color=(240, 200, 60), horn='rhino', outfit='barbarian', hat=False, outfit_kw=dict(paint=False))),
    ('Hercules', dict(chitin=(40, 36, 34), shell=(170, 150, 80), horn='hercules', horn_color=(40, 36, 34), outfit='heavy', hat=False)),
    ('Atlas', dict(chitin=(50, 60, 40), horn='atlas', sheen=(90, 110, 70), outfit='guardian', hat=False, outfit_kw=dict(cape=False))),
    ('Goliath', dict(chitin=(40, 36, 34), shell=(230, 220, 200), horn='goliath', horn_color=(40, 36, 34), outfit='warrior', hat=False)),
    ('Rhino', dict(chitin=(90, 60, 40), horn='rhino', outfit='smith', hat=False)),
    ('Cobalt', dict(chitin=(30, 60, 160), shell=(40, 80, 190), sheen=(120, 170, 240), horn='hercules', horn_color=(30, 50, 130), outfit='assault',
                    hat=False)),
    ('Ironhorn', dict(chitin=(110, 114, 122), shell=(140, 144, 152), horn='rhino', horn_color=(90, 94, 100), outfit='knight', hat=False)),
    ('Emerald', dict(chitin=(40, 130, 70), sheen=(200, 190, 70), horn='rhino', outfit='nature_mage', hat=False)),
    ('Sunhorn', dict(chitin=(200, 120, 40), shell=(220, 150, 50), horn='atlas', horn_color=(160, 90, 30), outfit='fire_mage', hat=False)),
    ('Brawler', dict(chitin=(70, 50, 110), horn='rhino', outfit='gladiator', hat=False)),
    ('Stagknight', dict(chitin=(60, 30, 24), horn='stag', horn_color=(90, 50, 30), outfit='tactician', hat=False)),
    ('Thunderhorn', dict(chitin=(40, 40, 60), sheen=(240, 220, 80), horn='hercules', horn_color=(40, 40, 60), outfit='air_mage', hat=False)),
    ('Gunner', dict(chitin=(80, 90, 60), horn='rhino', outfit='sharpshooter', hat=False)),
]


def ant_concept():
    """An ant upright on two legs and a second pair from the hips, two arms free."""
    c = (40, 36, 34)
    m = F.body(c, 'chitin', leg=9, leg_w=1, leg_d=1, gap=5, torso_w=5, torso_d=3, torso_h=8, arm_len=9, arm_w=1, arm_d=1,
               arm_pose='a', head=dict(w=9, d=8, h=7, style='round'), neck=2, foot_len=1)
    hd = m.head
    compound_eyes(m, hd, (30, 28, 30))
    mandibles(m, hd, shade(c, 0.8), 2)
    X.antennae(m, c, 'elbowed')
    b = m.body
    for side in (-1, 1):
        pts = [(16 + side * 2, b.cy, b.hip + 1), (16 + side * 6, b.cy + 1, b.hip + 3), (16 + side * 9, b.cy + 1, 0.5)]
        X.sweep(m, [(x, y, z, .6, .6, .6) for x, y, z in pts], c, 'chitin', None)
    X.sweep(m, [(16, b.back, b.hip, 1, 1, 1), (16, b.back + 2, b.hip - 1, 1.1, 1.1, 1.1)], c, 'chitin', None)
    m.ellipsoid(16, b.back + 6, b.hip - 1, 3.4, 4, 3.6, c, 'chitin', only_empty=True)
    return m


SETS = [
    Set('Spiderfolk', 'Spiderfolk', designs(spider, SPIDERS), treat3(1, 2, 3),
        concepts=[('WidowDrider', lambda: drider('widow')), ('TarantulaDrider', lambda: drider('tarantula'))]),
    Set('Insectfolk', 'Insectfolk', designs(bug, GENERIC), treat3(1, 3, 2)),
    Set('Insectfolk/Moth', 'Insectfolk_Moth', designs(moth, MOTHS), treat3(1, 2, 3), concepts=[('Spread', CX.moth)]),
    Set('Insectfolk/Ant', 'Insectfolk_Ant', designs(ant, ANTS), treat3(1, 2, 3), concepts=[('Sixlegs', ant_concept)]),
    Set('Insectfolk/Mantis', 'Insectfolk_Mantis', designs(mantis, MANTISES), treat3(1, 2, 3), concepts=[('Stalker', mantis_concept)]),
    Set('Insectfolk/Wasp', 'Insectfolk_Wasp', designs(wasp, WASPS), treat3(1, 2, 6), concepts=[('Hornet', CX.wasp)]),
    Set('Insectfolk/Heracross', 'Insectfolk_Heracross', designs(beetle, BEETLES), treat3(1, 2, 3),
        title='Insectfolk / Heracross (horned beetles)'),
]
