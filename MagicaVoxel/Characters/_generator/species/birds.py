"""Birdfolk, generic and the four kinds: crows, predators, songbirds and roadrunners. A beak,
feathers behind the arms (arm wings, which fold across the back with a lowered arm) or a
pair of wings on the back, a fan of tail feathers on the hips, talons."""
from .common import Set, designs, beast, EYES
from .mammals import treat3
from . import concepts_extra as CX
from core import shade, mix, sat
import heads as H
import outfits as O
import extras as X
import freebody as F

WHITE = (240, 238, 232)


def crest(m, color, style='tuft', tip=None):
    """tuft (a few feathers up at the back), tall (a jay's or cardinal's peak), tufts (an
    owl's ear tufts), comb (a rooster's), quills (a secretary bird's), plume (one long)."""
    tip = tip or shade(color, 0.8)
    hd = m.head
    if style == 'tuft':
        for k, (dy, dz) in enumerate(((3, 1), (4, 1), (5, 2), (5, 1), (6, 2), (7, 1))):
            m.set((16, hd.y0 + dy, hd.z1 + dz), color if k < 4 else tip, 'feather', 'Head', 'head')
    elif style == 'tall':
        for i in range(5):
            for k in range(1, 4 - i // 2 + 1):
                m.set((16, hd.y0 + 2 + i, hd.z1 + k + (i // 2)), tip if k == 4 - i // 2 else color, 'feather', 'Head', 'head')
            if i < 3:
                m.set((15, hd.y0 + 2 + i, hd.z1 + 1), color, 'feather', 'Head', 'head')
                m.set((17, hd.y0 + 2 + i, hd.z1 + 1), color, 'feather', 'Head', 'head')
    elif style == 'tufts':
        for x in (hd.x0 + 1, hd.x1 - 1):
            for k in range(1, 4):
                m.set((x + (k // 2) * (-1 if x < 16 else 1), hd.y0 + 2, hd.z1 + k), color if k < 3 else tip, 'feather', 'Head', 'head')
                m.set((x, hd.y0 + 3, hd.z1 + 1), color, 'feather', 'Head', 'head')
    elif style == 'comb':
        for i, hgt in enumerate((2, 3, 2, 3, 2)):
            for k in range(1, hgt + 1):
                m.set((16, hd.y0 + 1 + i, hd.z1 + k), color, 'skin', 'Head', 'head')
    elif style == 'quills':
        for i in range(6):
            m.set((15 + (i % 3), hd.y1 + 1 + i // 3, hd.z1 - i // 2 + 1), tip, 'feather', 'Head', 'head')
            m.set((15 + (i % 3), hd.y1 + 2 + i // 3, hd.z1 - i // 2 + 2), color, 'feather', 'Head', 'head')
    elif style == 'plume':
        for k in range(6):
            m.set((16, hd.y0 + 3 + k // 2, hd.z1 + 1 + k), color if k < 5 else tip, 'feather', 'Head', 'head')


def wattle(m, color=(220, 40, 40)):
    hd = m.head
    for z in (hd.z0, hd.z0 - 1):
        m.set((16, hd.y0 - 1, z), color, 'skin', 'Head', 'head')


def facial_disc(color, rim=None):
    def f(m, hd):
        rim_c = rim or shade(color, 0.8)
        for x in range(hd.x0, hd.x1 + 1):
            for z in range(hd.z0, hd.z1):
                y = m.front_y(x, z)
                if y is None:
                    continue
                d = abs(x - 16) / 4.5 + abs(z - (hd.z0 + 3.5)) / 4.0
                if d < 1.0:
                    m.set((x, y, z), color, 'feather', 'Head', 'head')
                elif d < 1.25:
                    m.set((x, y, z), rim_c, 'feather', 'Head', 'head')
    return f


def mask(color):
    """A dark band across the eyes (a cardinal's, a shrike's)."""
    def f(m, hd):
        for x in range(hd.x0, hd.x1 + 1):
            for z in (hd.z0 + 2, hd.z0 + 3):
                y = m.front_y(x, z)
                if y is not None and m.get((x, y, z)).group == 'feather':
                    m.set((x, y, z), color, 'feather', 'Head', 'head')
    return f


def cap(color, rows=2):
    def f(m, hd):
        for p, v in m.v.items():
            if v.part == 'head' and v.group == 'feather' and p[2] >= hd.z1 - rows + 1:
                v.color = color
    return f


def cheeks(color):
    def f(m, hd):
        for x in (hd.x0, hd.x0 + 1, hd.x1 - 1, hd.x1):
            for z in (hd.z0 + 1, hd.z0 + 2):
                y = m.front_y(x, z)
                if y is not None and m.get((x, y, z)).group == 'feather':
                    m.set((x, y, z), color, 'feather', 'Head', 'head')
    return f


def bird(plumage=(120, 100, 80), head_color=None, breast=None, beak='cone', beak_color=(230, 180, 60), beak_tip=None,
         eyes='bead', iris='black', eye_gap=5, eye_h=2, crest_style=None, crest_color=None, face=None, wings='arm',
         wing_color=None, wing_tip=None, wing_depth=5, tail='feathers', tail_color=None, tail_tip=None, talons=(220, 180, 60),
         outfit=None, outfit_kw=None, hat=False, extras=None, head=None, glow_eyes=False, wing_reach=1, eye_z=None,
         brows=None, brow_color=None):
    iris = EYES.get(iris, iris) if isinstance(iris, str) else iris
    head = head or dict(w=9, d=8, h=8, style='soft')
    hc = head_color or plumage
    def face_fn(m, hd):
        if face:
            for f in (face if isinstance(face, (list, tuple)) else [face]):
                f(m, hd)
        if beak:
            H.beak(m, hd, beak_color, beak, z=hd.z0 + 1, tip=beak_tip)
        if crest_style:
            crest(m, crest_color or shade(hc, 0.85), crest_style)
    def pat(m):
        if breast:
            m.paint(breast, None, parts=('chest', 'spine', 'neck'), where=lambda p, v: p[1] == 15 and v.group == 'feather')
    def after(m):
        if wings == 'arm':
            X.arm_wings(m, wing_color or plumage, tip=wing_tip, depth=wing_depth, reach=wing_reach)
        elif wings in ('feathered', 'tiny'):
            X.back_wings(m, wing_color or plumage, tip=wing_tip, style=wings, span=7)
        if tail:
            X.tail(m, tail, tail_color or plumage, tip=tail_tip or shade(tail_color or plumage, 0.7), group='feather')
        if talons:
            X.talons(m, talons)
        if extras:
            extras(m)
    m = beast(plumage, skin_group='feather', head=head, eyes=None, iris=iris, face=face_fn, pattern=pat, outfit=outfit,
              outfit_kw=outfit_kw, hat=hat, extras=after, head_color=head_color)
    # eyes go on after the face's marks, so a disc or a mask does not paint over them
    hd = m.head
    H.eyes(m, hd, eyes, iris=iris, z=eye_z if eye_z is not None else hd.z0 + 3, gap=eye_gap, width=2, height=eye_h, glow=glow_eyes)
    if brows:
        H.brows(m, hd, brow_color or shade(hc, 0.6), z=(eye_z or hd.z0 + 3) + eye_h, style=brows, gap=eye_gap)
    return m


# --- Generic ---------------------------------------------------------------------------------

def peacock_tail(m):
    for x in range(10, 23):
        for z in range(4, 22):
            d = ((x - 16) / 7.0) ** 2 + ((z - 12) / 9.5) ** 2
            if d <= 1 and not (14 <= x <= 18 and z <= 9):
                c = (40, 120, 90)
                if (x + z) % 4 == 0 and d > 0.25:
                    c = (40, 80, 180) if d > 0.5 else (230, 190, 50)
                m.set((x, 21 if d > 0.4 else 20, z), c, 'feather', 'Hips')
    for z in range(8, 12):
        m.set((16, 19, z), (40, 100, 80), 'feather', 'Hips')


def pouch(m):
    hd = m.head
    for y in range(hd.y0 - 5, hd.y0):
        for x in (15, 16, 17):
            m.set((x, y, hd.z0), (240, 180, 90), 'skin', 'Head', 'head')
            if hd.y0 - 4 <= y <= hd.y0 - 1:
                m.set((x, y, hd.z0 - 1), (240, 170, 80), 'skin', 'Head', 'head')
    for y in range(hd.y0 - 5, hd.y0):
        m.set((16, y, hd.z0 + 1), (240, 200, 120), 'horn', 'Head', 'head')


def toucan_beak(m):
    hd = m.head
    for k in range(1, 6):
        for x in (15, 16, 17):
            for z in range(hd.z0 + 1, hd.z0 + 4 - k // 3):
                c = (250, 150, 40) if k < 4 else (230, 60, 40)
                if z == hd.z0 + 1:
                    c = (60, 200, 90) if k < 3 else c
                m.set((x, hd.y0 - k, z), c, 'horn', 'Head', 'head')


GENERIC = [
    ('Macaw', dict(plumage=(220, 40, 40), wing_color=(40, 90, 210), wing_tip=(250, 210, 40), beak='hook', beak_color=(240, 236, 226),
                   beak_tip=(40, 40, 40), tail='long_feathers', tail_color=(220, 40, 40), tail_tip=(40, 90, 210), outfit='pirate', hat=True,
                   face=cheeks(WHITE), outfit_kw=dict(eyepatch=False))),
    ('Owl', dict(plumage=(140, 110, 80), face=facial_disc((220, 200, 170)), eyes='sclera', iris=(240, 150, 30), eye_gap=3, eye_h=2,
                 crest_style='tufts', beak='hook', beak_color=(90, 80, 70), outfit='scholar', hat=False)),
    ('Penguin', dict(plumage=(40, 40, 46), breast=WHITE, face=cheeks((250, 200, 60)), beak='cone', beak_color=(250, 150, 40), wings='tiny',
                     tail=None, talons=(250, 150, 40), outfit='tactician', hat=False, outfit_kw=dict(main=(30, 30, 36), trim=(250, 200, 60)))),
    ('Toucan', dict(plumage=(36, 34, 36), face=cheeks((250, 230, 120)), beak=None, extras=toucan_beak, outfit='merchant', hat=False)),
    ('Peacock', dict(plumage=(30, 90, 170), head_color=(30, 110, 180), crest_style='plume', crest_color=(40, 160, 140), tail=None,
                     extras=peacock_tail, outfit='noble', hat=False, wings=None, outfit_kw=dict(main=(30, 70, 120)))),
    ('Pelican', dict(plumage=(236, 232, 226), beak=None, extras=pouch, outfit='sailor', hat=True, crest_style='tuft', crest_color=(240, 220, 160))),
    ('Duck', dict(plumage=(130, 110, 80), head_color=(40, 130, 70), beak='duck', beak_color=(240, 200, 60), breast=(150, 80, 60), outfit='peasant',
                  hat=False, talons=(240, 150, 40))),
    ('Rooster', dict(plumage=(180, 90, 40), head_color=(220, 120, 50), crest_style='comb', crest_color=(220, 40, 40), extras=wattle,
                     tail='long_feathers', tail_color=(40, 80, 60), outfit='gladiator', hat=False)),
    ('Pigeon', dict(plumage=(150, 150, 160), head_color=(130, 130, 150), breast=(120, 150, 140), beak='cone', beak_color=(60, 60, 60),
                    iris=(230, 120, 40), eyes='dot', outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Kiwi', dict(plumage=(140, 100, 60), beak='long', beak_color=(220, 200, 170), wings=None, tail=None, outfit='scout', hat=False,
                  outfit_kw=dict(quiver=False))),
    ('Puffin', dict(plumage=(36, 34, 36), face=cheeks(WHITE), beak='heavy', beak_color=(240, 110, 40), beak_tip=(60, 90, 160), breast=WHITE,
                    outfit='sailor', hat=False)),
    ('Swan', dict(plumage=(246, 244, 240), beak='cone', beak_color=(240, 120, 40), beak_tip=(30, 30, 30), outfit='white_mage', hat=False)),
    ('Hummingbird', dict(plumage=(40, 170, 110), head_color=(50, 190, 120), breast=(200, 40, 90), beak='long', beak_color=(40, 40, 40),
                         wings='feathered', wing_color=(80, 200, 150), outfit='psychic', hat=False, iris=(30, 30, 30))),
    ('Kingfisher', dict(plumage=(40, 120, 200), breast=(240, 140, 50), beak='long', beak_color=(40, 40, 40), face=cheeks((240, 140, 50)),
                        outfit='water_mage', hat=False)),
]

# --- Crows -----------------------------------------------------------------------------------

def sheen(color):
    def f(m):
        for p, v in m.v.items():
            if v.group == 'feather' and X.h(p, 41) < 0.25:
                v.color = color
    return f


CROW = dict(plumage=(40, 40, 50), beak='heavy', beak_color=(56, 56, 62), beak_tip=(30, 30, 34), eyes='sclera', iris=(40, 40, 46),
            talons=(50, 50, 56), wing_tip=(30, 30, 36))


def crow(**kw):
    d = dict(CROW)
    ex = kw.pop('extras', None)
    d['extras'] = lambda m: (sheen((60, 60, 100))(m), ex(m) if ex else None)
    d.update(kw)
    return bird(**d)


def grey_nape(m, hd):
    for p, v in m.v.items():
        if v.part == 'head' and v.group == 'feather' and p[1] >= hd.y0 + 4:
            v.color = (140, 140, 150)


CROWS = [
    ('Carrion', dict(outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Raven', dict(plumage=(30, 30, 40), head=dict(w=9, d=8, h=8, style='soft'), outfit='necromancer', hat=False, iris=(120, 255, 140), eyes='glow')),
    ('Magpie', dict(plumage=(30, 30, 40), breast=WHITE, wing_tip=(40, 80, 180), tail='long_feathers', tail_color=(40, 60, 120), outfit='bard',
                    hat=True)),
    ('Jackdaw', dict(face=grey_nape, iris=(230, 230, 240), eyes='pupil', outfit='gunslinger', hat=True)),
    ('Rook', dict(face=lambda m, hd: [setattr(v, 'color', (200, 190, 190)) for p, v in m.v.items() if v.part == 'head' and v.group == 'horn'],
                  beak_color=(190, 180, 180), outfit='scholar', hat=False)),
    ('Chough', dict(beak='long', beak_color=(220, 40, 40), talons=(220, 40, 40), outfit='monk', hat=False, outfit_kw=dict(main=(40, 40, 50), trim=(220, 40, 40)))),
    ('Plaguecrow', dict(outfit='apothecary', hat=False, extras=lambda m: H.hat(m, m.head, 'wide', (30, 28, 30), trim=(20, 20, 20)))),
    ('Sharpbeak', dict(outfit='sharpshooter', hat=True)),
    ('Ravenlord', dict(plumage=(30, 30, 40), outfit='noble', hat=False, outfit_kw=dict(main=(40, 30, 60), cape=True),
                       extras=lambda m: H.hat(m, m.head, 'crown', (200, 200, 210), extra=(140, 40, 60)))),
    ('Scarecrow', dict(outfit='peasant', hat=True, outfit_kw=dict(main=(150, 120, 80)))),
    ('Stormcrow', dict(outfit='air_mage', hat=True, iris=(150, 220, 255), eyes='glow')),
    ('Blackwing', dict(outfit='assault', hat=False, wing_depth=7)),
    ('Watcher', dict(outfit='tactician', hat=True, outfit_kw=dict(main=(30, 30, 36), trim=(200, 200, 210)))),
]

# --- Predators -------------------------------------------------------------------------------

def moustache(color):
    """A falcon's dark stripe down from each eye."""
    def f(m, hd):
        for x in (hd.x0 + 1, hd.x1 - 1):
            for z in (hd.z0, hd.z0 + 1, hd.z0 + 2):
                y = m.front_y(x, z)
                if y is not None and m.get((x, y, z)).group == 'feather':
                    m.set((x, y, z), color, 'feather', 'Head', 'head')
    return f


def ruff(color):
    def f(m):
        O.collar_ruff(m, color, group='feather')
    return f


def bald(m, hd):
    for p, v in m.v.items():
        if v.part == 'head' and v.group == 'feather':
            v.color = (220, 140, 130)
            v.group = 'skin'


PREDATORS = [
    ('BaldEagle', dict(plumage=(90, 60, 40), head_color=WHITE, beak='hook', beak_color=(250, 200, 50), eyes='angry', iris=(240, 200, 60),
                       brows='angry', brow_color=(220, 220, 214), tail_color=WHITE, outfit='tactician', hat=False)),
    ('GoldenEagle', dict(plumage=(110, 76, 40), head_color=(190, 140, 60), beak='hook', beak_color=(80, 70, 60), beak_tip=(40, 40, 40),
                         eyes='angry', iris=(200, 130, 40), outfit='guardian', hat=False, outfit_kw=dict(cape=False, main=(222, 184, 72)))),
    ('Hawk', dict(plumage=(150, 100, 60), breast=(240, 226, 200), beak='hook', beak_color=(70, 70, 70), eyes='angry', iris=(220, 170, 60),
                  tail_color=(200, 90, 50), outfit='scout', hat=False, outfit_kw=dict(quiver=True))),
    ('Peregrine', dict(plumage=(90, 100, 120), breast=(230, 226, 220), face=moustache((40, 44, 56)), beak='hook', beak_color=(250, 200, 60),
                       beak_tip=(40, 40, 40), eyes='angry', iris=(40, 40, 40), outfit='sharpshooter', hat=False)),
    ('HornedOwl', dict(plumage=(110, 86, 60), face=facial_disc((200, 160, 110), (60, 44, 30)), crest_style='tufts', eyes='sclera',
                       iris=(240, 170, 30), eye_gap=3, beak='hook', beak_color=(60, 56, 50), outfit='psychic', hat=False)),
    ('BarnOwl', dict(plumage=(220, 180, 120), face=facial_disc((250, 246, 240), (200, 150, 90)), eyes='dot', iris='black', eye_gap=3,
                     beak='cone', beak_color=(230, 210, 190), outfit='white_mage', hat=False)),
    ('SnowyOwl', dict(plumage=(246, 244, 240), face=facial_disc((252, 252, 250)), eyes='sclera', iris=(240, 200, 40), eye_gap=3,
                      beak='hook', beak_color=(60, 60, 60), outfit='water_mage', hat=False,
                      extras=lambda m: X.spots(m, (60, 60, 60), density=0.08, head=False))),
    ('Vulture', dict(plumage=(50, 44, 40), face=bald, extras=ruff((240, 236, 226)), beak='hook', beak_color=(230, 220, 200), eyes='pupil',
                     iris=(200, 40, 40), outfit='necromancer', hat=False)),
    ('Osprey', dict(plumage=(90, 70, 50), head_color=WHITE, face=mask((70, 50, 40)), breast=WHITE, beak='hook', beak_color=(40, 40, 40),
                    eyes='angry', iris=(240, 200, 60), outfit='sailor', hat=False)),
    ('Harpy', dict(plumage=(70, 70, 80), head_color=(160, 160, 170), crest_style='tuft', crest_color=(60, 60, 70), beak='hook',
                   beak_color=(40, 40, 40), eyes='angry', iris=(230, 190, 60), outfit='barbarian', hat=False, outfit_kw=dict(paint=False))),
    ('Kestrel', dict(plumage=(200, 110, 60), head_color=(120, 130, 160), face=moustache((40, 40, 50)), beak='hook', beak_color=(250, 200, 60),
                     eyes='dot', iris='black', outfit='gunslinger', hat=False)),
    ('Secretary', dict(plumage=(200, 200, 206), face=mask((240, 120, 40)), crest_style='quills', crest_color=(40, 40, 46), beak='hook',
                       beak_color=(120, 120, 120), outfit='cleric', hat=False, tail='long_feathers', tail_color=(40, 40, 46))),
    ('Condor', dict(plumage=(36, 34, 36), face=bald, extras=ruff(WHITE), beak='hook', beak_color=(200, 190, 170), outfit='heavy', hat=False)),
]

# --- Songbirds -------------------------------------------------------------------------------

SONG = dict(head=dict(w=9, d=8, h=7, style='round'), beak='cone', beak_color=(60, 56, 50), eyes='bead', iris='black', eye_gap=5,
            talons=(150, 120, 100), wing_depth=4)


def song(**kw):
    d = dict(SONG)
    d.update(kw)
    return bird(**d)


SONGBIRDS = [
    ('Robin', dict(plumage=(110, 90, 70), breast=(230, 110, 50), face=cheeks((230, 110, 50)), outfit='scout', hat=False,
                   outfit_kw=dict(quiver=False))),
    ('BlueJay', dict(plumage=(60, 110, 200), breast=WHITE, crest_style='tall', crest_color=(60, 110, 200), face=mask((30, 30, 40)),
                     wing_tip=(30, 30, 40), outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Cardinal', dict(plumage=(210, 40, 40), crest_style='tall', crest_color=(210, 40, 40), face=mask((30, 26, 26)), beak_color=(240, 140, 60),
                      outfit='cleric', hat=False, outfit_kw=dict(main=(200, 30, 40), trim=(222, 184, 72)))),
    ('Canary', dict(plumage=(250, 220, 60), beak_color=(240, 160, 120), outfit='bard', hat=True)),
    ('Goldfinch', dict(plumage=(250, 210, 40), face=cap((30, 30, 30)), wing_color=(40, 40, 40), wing_tip=WHITE, beak_color=(240, 170, 120),
                       outfit='merchant', hat=False)),
    ('Sparrow', dict(plumage=(150, 110, 70), head_color=(120, 110, 100), breast=(200, 190, 170), face=cheeks((220, 210, 190)),
                     outfit='peasant', hat=True)),
    ('Bluebird', dict(plumage=(70, 130, 220), breast=(220, 130, 70), outfit='monk', hat=False, outfit_kw=dict(main=(70, 130, 220)))),
    ('Oriole', dict(plumage=(250, 140, 30), head_color=(30, 30, 30), wing_color=(30, 30, 30), wing_tip=WHITE, outfit='gunslinger', hat=True)),
    ('Wren', dict(plumage=(140, 100, 60), tail='long_feathers', tail_color=(120, 86, 50), face=cheeks((200, 170, 130)), outfit='apothecary',
                  hat=False)),
    ('Chickadee', dict(plumage=(160, 160, 160), face=[cap((30, 30, 30), 3), cheeks(WHITE)], breast=(240, 230, 210), outfit='tactician', hat=False)),
    ('Nightingale', dict(plumage=(150, 110, 80), breast=(220, 200, 180), outfit='psychic', hat=False, eyes='big', iris='black', eye_h=3)),
    ('Swallow', dict(plumage=(40, 50, 110), breast=(240, 220, 200), face=cheeks((200, 80, 50)), tail='long_feathers',
                     tail_color=(40, 50, 110), wing_depth=6, outfit='sharpshooter', hat=False)),
    ('Waxwing', dict(plumage=(190, 160, 130), crest_style='tall', crest_color=(190, 150, 120), face=mask((40, 30, 30)), wing_tip=(220, 40, 40),
                     outfit='noble', hat=False)),
]

# --- Roadrunners -----------------------------------------------------------------------------

def streaks(dark, light):
    """Streaked plumage: short dark and light dashes, fewer on the head."""
    def f(m):
        for p, v in m.v.items():
            if v.group == 'feather':
                r = X.h((p[0], p[1], p[2] // 2), 51)
                if v.part == 'head':
                    r = r * 1.8
                if r < 0.16:
                    v.color = dark
                elif r < 0.24:
                    v.color = light
    return f


def eye_patch(color):
    def f(m, hd):
        for x in (hd.x0, hd.x1):
            for y in (hd.y0 + 2, hd.y0 + 3):
                m.set((x, y, hd.z0 + 4), color, 'skin', 'Head', 'head')
                m.set((x, y + 1, hd.z0 + 4), (230, 60, 50), 'skin', 'Head', 'head')
    return f


RUN = dict(plumage=(130, 100, 70), beak='long', beak_color=(60, 56, 50), crest_style='tall', eyes='pupil', iris=(220, 170, 60),
           tail='long_feathers', talons=(110, 110, 120), wing_depth=4, face=eye_patch((80, 150, 220)))


def runner(**kw):
    d = dict(RUN)
    stre = kw.pop('streak', ((70, 50, 36), (220, 210, 190)))
    ex = kw.pop('extras', None)
    d['extras'] = lambda m: (streaks(*stre)(m) if stre else None, ex(m) if ex else None)
    d.update(kw)
    if 'crest_color' not in d:
        d['crest_color'] = shade(d['plumage'], 0.6)
    return bird(**d)


ROADRUNNERS = [
    ('Desert', dict(outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('Duster', dict(outfit='gunslinger', hat=True)),
    ('Dustrider', dict(plumage=(170, 130, 90), outfit='assault', hat=False)),
    ('Sandsniper', dict(plumage=(190, 160, 120), outfit='sharpshooter', hat=False)),
    ('Courier', dict(outfit='peasant', hat=False, extras=lambda m: O.satchel(m, (124, 86, 52)))),
    ('Mesa', dict(plumage=(150, 90, 60), outfit='monk', hat=False)),
    ('Lesser', dict(plumage=(150, 130, 100), outfit='bard', hat=True, streak=((90, 70, 50), (230, 220, 200)))),
    ('Dawnrunner', dict(plumage=(200, 120, 60), outfit='fire_mage', hat=False)),
    ('Mirage', dict(plumage=(160, 150, 190), streak=((90, 80, 130), (230, 220, 240)), outfit='psychic', hat=False)),
    ('Cactus', dict(plumage=(120, 130, 80), outfit='nature_mage', hat=False)),
    ('Trailboss', dict(outfit='tactician', hat=True, outfit_kw=dict(main=(110, 80, 50)))),
    ('Rattlebeak', dict(plumage=(140, 110, 80), outfit='rogue', hat=False, outfit_kw=dict(mask=True))),
    ('Prospector', dict(outfit='miner', hat=True)),
]


def bird_concept(kind):
    """A birdfolk with wings for arms and legs bent like a bird's."""
    plumage = {'eagle': (90, 60, 40), 'crow': (40, 40, 50), 'parrot': (220, 40, 40)}[kind]
    m = F.body(plumage, 'feather', leg=8, leg_w=2, leg_d=2, gap=3, torso_w=7, torso_d=6, torso_h=10, arm_len=6, arm_w=2, arm_d=2,
               arm_pose='a', head=dict(w=9, d=8, h=8, style='soft'), neck=1, foot_len=3, head_color=WHITE if kind == 'eagle' else None)
    hd = m.head
    H.beak(m, hd, (250, 200, 50) if kind != 'crow' else (56, 56, 62), 'hook' if kind != 'crow' else 'heavy', z=hd.z0 + 1)
    H.eyes(m, hd, 'angry' if kind == 'eagle' else 'sclera', iris=(240, 200, 60), z=hd.z0 + 3, gap=5)
    b = m.body
    wing = {'eagle': (90, 60, 40), 'crow': (40, 40, 50), 'parrot': (40, 90, 210)}[kind]
    tip = shade(wing, 0.7) if kind != 'parrot' else (250, 210, 40)
    for side, sgn in (('r', -1), ('l', 1)):
        for x in range(4, 18):
            xx = 16 + sgn * x
            top = b.top + 4 - x // 3
            bottom = b.top - 2 - x // 1 + (x // 4)
            for z in range(max(2, bottom), top + 1):
                m.set((xx, b.back + 1, z), tip if z <= bottom + 1 or x >= 16 else wing, 'feather')
    for x in range(13, 20):
        for k in range(6):
            m.set((x, b.back + 1 + k, b.hip - k // 2), tip if k >= 4 else plumage, 'feather')
    m.paint((220, 180, 60), 'horn', parts=('foot_r', 'foot_l', 'lleg_r', 'lleg_l'))
    F.dress(m, belt=(80, 60, 40), buckle=(222, 184, 72), sash=(40, 60, 120) if kind == 'eagle' else None)
    return m


SETS = [
    Set('Birdfolk', 'Birdfolk', designs(bird, GENERIC), treat3(1, 2, 3),
        concepts=[('Eagle', lambda: bird_concept('eagle')), ('Parrot', lambda: bird_concept('parrot'))]),
    Set('Birdfolk/Crow', 'Birdfolk_Crow', designs(crow, CROWS), treat3(3, 1, 2), concepts=[('Raven', lambda: bird_concept('crow'))]),
    Set('Birdfolk/Predator', 'Birdfolk_Predator', designs(bird, PREDATORS), treat3(1, 5, 4), concepts=[('Owl', CX.owl)]),
    Set('Birdfolk/Songbird', 'Birdfolk_Songbird', designs(song, SONGBIRDS), treat3(2, 3, 1)),
    Set('Birdfolk/Roadrunner', 'Birdfolk_Roadrunner', designs(runner, ROADRUNNERS), treat3(1, 2, 3)),
]
