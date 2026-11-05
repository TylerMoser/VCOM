"""Catfolk, dogfolk, minotaurs, loxodons (elephant folk), sealfolk and the monkeyfolk goblins."""
from .common import Set, designs, beast, EYES
from .mammals import furry, face_patch, buck_teeth, treat3, WHITE, PINK, NOSE_PINK, BLACK_NOSE
from . import concepts_extra as CX
from core import shade, mix
import heads as H
import outfits as O
import extras as X
import freebody as F

GOLD = (222, 184, 72)

# --- Catfolk ---------------------------------------------------------------------------------

def cat(fur, **kw):
    d = dict(muzzle=dict(length=1, w=3, h=2, nose_color=NOSE_PINK, nose_width=1), ears='cat', ear_inner=PINK, eyes='slit',
             iris=(150, 200, 70), tail='cat', whiskers=(236, 236, 230), head=dict(w=9, d=8, h=7, style='base'))
    d.update(kw)
    if 'face' not in d:
        d['face'] = shade(fur, 1.25)
    return furry(fur, **d)


def tabby(color):
    return lambda m: X.stripes(m, color, period=3, head=True)


def tiger_face(m):
    hd = m.head
    for x in (hd.x0, hd.x0 + 1, hd.x1 - 1, hd.x1):
        z = hd.z0 + 3
        y = m.front_y(x, z)
        if y is not None:
            m.set((x, y, z), (30, 26, 26), 'fur', 'Head', 'head')
    for x in (15, 17):
        y = m.front_y(x, hd.z1)
        if y is not None:
            m.set((x, y, hd.z1), (30, 26, 26), 'fur', 'Head', 'head')


def tears(color=(30, 26, 26)):
    def f(m):
        hd = m.head
        for x in (15, 17):
            for z in (hd.z0 + 1, hd.z0 + 2):
                y = m.front_y(x, z)
                if y is not None and m.get((x, y, z)).group == 'fur':
                    m.set((x, y, z), color, 'fur', 'Head', 'head')
    return f


def patches(colors, seed=3):
    def f(m):
        for p, v in m.v.items():
            if v.group == m.skin_group and X.h((p[0] // 3, p[1] // 3, p[2] // 3), seed) < 0.45:
                v.color = colors[int(X.h((p[0] // 3, 0, p[2] // 3), seed + 1) * len(colors)) % len(colors)]
    return f


def tux(m):
    m.paint(WHITE, None, parts=('chest', 'spine', 'hand_r', 'hand_l', 'foot_r', 'foot_l'),
            where=lambda p, v: v.group == m.skin_group and (p[1] == 15 or v.part in ('hand_r', 'hand_l', 'foot_r', 'foot_l')))


def rosettes(dark, mid):
    def f(m):
        for p, v in m.v.items():
            if v.group != m.skin_group:
                continue
            q = (p[0] // 2, p[1] // 2, p[2] // 2)
            r = X.h(q, 12)
            if r < 0.16:
                v.color = dark
            elif r < 0.24:
                v.color = mid
    return f


CATS = [
    ('Tabby', dict(fur=(220, 140, 60), pattern=tabby((170, 90, 40)), outfit='scout', outfit_kw=dict(quiver=False))),
    ('Tuxedo', dict(fur=(40, 38, 42), face=WHITE, pattern=tux, outfit='gunslinger', hat=True, iris=(230, 200, 60))),
    ('Siamese', dict(fur=(236, 222, 196), pattern=lambda m: X.points(m, (90, 70, 60)), face=(120, 96, 80), outfit='psychic', iris=(80, 140, 230))),
    ('Lion', dict(fur=(214, 170, 90), face=(236, 210, 150), extras=lambda m: X.mane(m, (150, 90, 40), size=2), tail='tuft',
                  tail_tip=(140, 80, 40), ears='round', outfit='guardian', iris=(200, 150, 50), outfit_kw=dict(cape=True, main=GOLD, second=(140, 30, 40)))),
    ('Tiger', dict(fur=(230, 130, 40), face=WHITE, pattern=lambda m: (X.stripes(m, (30, 26, 26), period=3, head=True), tiger_face(m)),
                   outfit='monk', iris=(230, 190, 50), outfit_kw=dict(main=(40, 40, 46), trim=(230, 190, 50), second=(230, 226, 210)))),
    ('SnowLeopard', dict(fur=(210, 210, 206), face=(240, 240, 236), pattern=rosettes((80, 80, 86), (150, 150, 150)), tail='fox',
                         tail_color=(200, 200, 196), outfit='hunter', hat=False, iris=(160, 210, 200))),
    ('Cheetah', dict(fur=(230, 190, 100), face=(245, 230, 200), pattern=lambda m: (X.spots(m, (40, 34, 30), density=0.18), tears()(m)),
                     outfit='sharpshooter', hat=False, iris=(230, 180, 50))),
    ('Panther', dict(fur=(40, 38, 44), face=(54, 52, 58), outfit='rogue', iris=(240, 210, 60), outfit_kw=dict(mask=False))),
    ('Lynx', dict(fur=(190, 150, 110), ears='lynx', tail='stub', tail_color=(190, 150, 110), tail_tip=(40, 34, 30),
                  pattern=lambda m: X.spots(m, (130, 100, 70), density=0.12), outfit='ranger', hat=False)),
    ('Calico', dict(fur=WHITE, pattern=patches([(220, 140, 60), (50, 44, 44)]), outfit='bard', hat=True, iris=(90, 170, 90))),
    ('Sphynx', dict(fur=(220, 180, 170), group='skin', face=(230, 190, 180), ears='bat', ear_inner=(240, 170, 170), whiskers=None,
                    outfit='necromancer', hat=False, iris=(120, 220, 120), eyes='glow')),
    ('Persian', dict(fur=(244, 242, 238), muzzle=None, nose=None, head=dict(w=9, d=8, h=7, style='round'), face=(250, 250, 248),
                     extras=lambda m: X.mane(m, (236, 234, 230), size=1), outfit='noble', hat=False, iris=(80, 150, 230), tail='fox',
                     tail_color=(240, 238, 234))),
    ('Serval', dict(fur=(230, 180, 90), ears='fox', pattern=lambda m: X.spots(m, (40, 34, 30), density=0.22), outfit='assault', hat=False)),
    ('MaineCoon', dict(fur=(130, 100, 70), pattern=tabby((80, 60, 40)), ears='lynx', tail='fox', outfit='heavy', hat=False)),
    ('Caracal', dict(fur=(200, 140, 80), ears='lynx', face=(240, 220, 190), tail='dog', outfit='tactician', hat=False)),
    ('Jaguar', dict(fur=(220, 160, 60), face=(240, 210, 150), pattern=rosettes((40, 30, 26), (180, 110, 40)), outfit='warrior', hat=False)),
]

# --- Dogfolk ---------------------------------------------------------------------------------

def dog(fur, **kw):
    d = dict(muzzle=dict(length=3, w=3, h=3, nose_color=BLACK_NOSE, nose_width=1, mouth=(60, 40, 40)), ears='dog_floppy', eyes='pupil',
             iris=(110, 70, 40), tail='dog', head=dict(w=9, d=8, h=8, style='base'))
    d.update(kw)
    return furry(fur, **d)


def saddle(color):
    def f(m):
        m.paint(color, None, parts=('chest', 'spine', 'hips'), where=lambda p, v: p[1] >= 16 and v.group == m.skin_group)
        hd = m.head
        m.paint(color, None, where=lambda p, v: v.part == 'head' and v.group == 'fur' and p[2] >= hd.z1 - 1 and p[1] >= hd.y0 + 2)
    return f


def husky_mask(m):
    hd = m.head
    for p, v in m.v.items():
        if v.part == 'head' and v.group == 'fur':
            if p[1] <= hd.y0 and p[2] <= hd.z0 + 3:
                v.color = WHITE
            elif p[1] <= hd.y0 and 15 <= p[0] <= 17:
                v.color = WHITE


def pompoms(color):
    def f(m):
        hd = m.head
        m.ellipsoid(16, hd.y0 + 4, hd.z1 + 1.5, 3, 3, 2.2, color, 'fur', 'Head', 'head', only_empty=True)
        for x in (5, 27):
            m.ellipsoid(x + (0.5 if x > 16 else 0.5), 16.5, 18.5, 1.3, 1.6, 1.3, color, 'fur', 'RightHand' if x < 16 else 'LeftHand', only_empty=True)
    return f


def underbite(m):
    tip, half, z, hgt, ln = m.snout_info
    for x in (15, 17):
        m.set((x, tip - 1, z), WHITE, 'bone', 'Head', 'head')
        m.set((x, tip - 1, z + 1), WHITE, 'bone', 'Head', 'head')
    for x in range(16 - half, 17 + half):
        if x not in (15, 17):
            m.set((x, tip - 1, z), shade(m.skin, 0.85), 'fur', 'Head', 'head')


def cask(m):
    for (x, y, z) in ((15, 13, 16), (16, 13, 16), (17, 13, 16), (15, 13, 17), (16, 13, 17), (17, 13, 17)):
        m.set((x, y, z), (150, 100, 50), 'leather', 'Chest')
    m.set((16, 13, 15), (150, 100, 50), 'leather', 'Chest')
    for x in (15, 17):
        m.set((x, 14, 18), (60, 40, 30), 'leather', 'Chest')


def jackal_face(m):
    hd = m.head
    for p, v in m.v.items():
        if v.part == 'head' and v.group == 'eye':
            pass
    H.hat(m, hd, 'circlet', GOLD, extra=(60, 160, 200))


DOGS = [
    ('Shepherd', dict(fur=(190, 140, 80), ears='dog_pointed', ear_inner=(150, 110, 80), pattern=saddle((50, 40, 36)), outfit='tactician',
                      hat=False, tail='fox', tail_color=(120, 90, 60))),
    ('Husky', dict(fur=(130, 130, 140), ears='dog_pointed', ear_inner=(220, 220, 220), extras=husky_mask, iris=(110, 180, 240), tail='curl',
                   outfit='hunter', hat=False, belly=WHITE)),
    ('Bulldog', dict(fur=(220, 200, 170), muzzle=dict(length=1, w=7, h=3, nose_color=BLACK_NOSE, nose_width=3, mouth=(60, 40, 40)),
                     ears='round', extras=underbite, head=dict(w=11, d=8, h=7, style='base'), outfit='heavy', hat=False, tail='stub')),
    ('Dalmatian', dict(fur=WHITE, pattern=lambda m: X.spots(m, (36, 34, 36), density=0.18), outfit='assault', hat=False, ear_color=(40, 38, 40))),
    ('Beagle', dict(fur=(220, 160, 80), pattern=saddle((50, 40, 36)), face=WHITE, ear_color=(170, 110, 50), outfit='scout', hat=False,
                    outfit_kw=dict(quiver=False), tail='dog', tail_tip=WHITE)),
    ('Poodle', dict(fur=(240, 236, 240), extras=pompoms((246, 242, 246)), outfit='noble', hat=False, muzzle=dict(length=3, w=3, h=2,
                    nose_color=BLACK_NOSE, nose_width=1), tail='tuft', tail_tip=(246, 242, 246))),
    ('Wolf', dict(fur=(120, 120, 130), muzzle=dict(length=3, w=5, h=3, taper=2, nose_color=BLACK_NOSE, nose_width=1, color=(200, 200, 205),
                  mouth=(60, 40, 40)), ears='dog_pointed', ear_inner=(200, 160, 160), eyes='angry', iris=(230, 190, 60), tail='fox',
                  outfit='barbarian', hat=False, outfit_kw=dict(paint=False))),
    ('Jackal', dict(fur=(40, 38, 44), ears='fox', ear_inner=GOLD, iris=(230, 190, 60), eyes='glow', outfit='cleric', hat=False,
                    extras=jackal_face, outfit_kw=dict(main=(40, 38, 44), trim=GOLD, accent=(60, 160, 200)), tail='fox')),
    ('Corgi', dict(fur=(220, 140, 60), face=WHITE, ears='fox', ear_inner=(240, 200, 180), belly=WHITE, outfit='peasant', hat=False,
                   tail='stub', eyes='big', eye_h=3)),
    ('Doberman', dict(fur=(40, 36, 36), ears='dog_pointed', face=(170, 90, 40), outfit='rogue', hat=False, outfit_kw=dict(mask=False),
                      tail='stub')),
    ('Retriever', dict(fur=(220, 170, 90), outfit='support', hat=False, tail='fox', mouth='smile')),
    ('StBernard', dict(fur=WHITE, pattern=saddle((160, 80, 40)), ear_color=(160, 80, 40), extras=cask, outfit='apothecary', hat=False,
                       head=dict(w=11, d=8, h=8, style='base'), muzzle=dict(length=2, w=5, h=3, nose_color=BLACK_NOSE, nose_width=3, mouth=(60, 40, 40)))),
    ('Basset', dict(fur=(200, 140, 80), face=WHITE, ear_color=(140, 90, 50), outfit='scholar', hat=False, eyes='closed')),
    ('Shiba', dict(fur=(220, 130, 60), face=(250, 240, 220), ears='fox', ear_inner=(250, 220, 200), tail='curl', tail_tip=(250, 240, 220),
                   outfit='monk', hat=False, eyes='closed', mouth='smile')),
    ('Fox', dict(fur=(220, 110, 40), face=WHITE, ears='fox', ear_inner=(40, 34, 30), muzzle=dict(length=3, w=3, h=2, taper=1,
                 nose_color=BLACK_NOSE, nose_width=1), tail='fox', tail_tip=WHITE, eyes='slit', iris=(230, 180, 50), outfit='bard', hat=True)),
    ('Greyhound', dict(fur=(150, 146, 150), muzzle=dict(length=4, w=3, h=2, taper=1, nose_color=BLACK_NOSE, nose_width=1), ears='round',
                       outfit='sharpshooter', hat=False, tail='thin', tail_color=(150, 146, 150))),
]

# --- Minotaur --------------------------------------------------------------------------------

def bull(fur, **kw):
    ex = kw.pop('extras', None)
    horns = kw.pop('horns', 'bull')
    horn_color = kw.pop('horn_color', (232, 220, 190))
    ring = kw.pop('ring', GOLD)
    def extras(m):
        hd = m.head
        H.horns(m, hd, horns, horn_color, tip=shade(horn_color, 0.7))
        H.ears(m, hd, 'human', m.skin, inner=shade(m.skin, 0.8))
        if ring:
            tip, half, z, hgt, ln = m.snout_info
            m.set((16, tip - 1, z), ring, 'metal', 'Head', 'head')
            m.set((15, tip - 1, z + 1), ring, 'metal', 'Head', 'head')
            m.set((17, tip - 1, z + 1), ring, 'metal', 'Head', 'head')
        if ex:
            ex(m)
    d = dict(muzzle=dict(length=2, w=7, h=3, taper=1, nose_color=None, color=shade(fur, 1.25), nostrils=True), ears=None, eyes='angry',
             iris=(200, 40, 40), tail='tuft', tail_tip=(40, 34, 30), head=dict(w=9, d=8, h=8, style='base'), feet='hooves',
             extras=extras, brows='angry')
    d.update(kw)
    return furry(fur, **d)


MINOTAUR = [
    ('Labyrinth', dict(fur=(110, 70, 40), outfit='barbarian', hat=False, outfit_kw=dict(paint=False))),
    ('Gladiator', dict(fur=(60, 50, 46), outfit='gladiator', hat=False)),
    ('Ironhorn', dict(fur=(140, 90, 50), horns='long_bull', outfit='heavy', hat=False)),
    ('Whitebull', dict(fur=(236, 230, 220), horns='long_bull', horn_color=(80, 70, 60), outfit='guardian', hat=False, iris=(60, 60, 60),
                       outfit_kw=dict(second=(60, 70, 140), cape=True))),
    ('Smith', dict(fur=(100, 60, 36), outfit='smith', hat=False)),
    ('Highland', dict(fur=(200, 110, 50), horns='long_bull', extras=lambda m: H.hair(m, m.head, (210, 120, 60), 'bowl'), outfit='hunter',
                      hat=False)),
    ('Spotted', dict(fur=WHITE, pattern=patches([(40, 36, 36)], seed=5), outfit='peasant', hat=False, ring=None, eyes='template',
                     iris=(80, 60, 40), brows=None)),
    ('Warlord', dict(fur=(40, 36, 36), horn_color=(200, 190, 160), outfit='warrior', hat=False, outfit_kw=dict(main=(60, 50, 50), trim=(150, 40, 40)))),
    ('Earthsage', dict(fur=(130, 100, 70), horns='ram', outfit='earth_mage', hat=False, eyes='closed', brows=None)),
    ('Bison', dict(fur=(90, 60, 40), extras=lambda m: X.mane(m, (60, 40, 28), size=2), horns='small', outfit='tribal', hat=False)),
    ('Yak', dict(fur=(60, 54, 50), extras=lambda m: H.hair(m, m.head, (80, 70, 64), 'long'), horns='bull', outfit='monk', hat=False,
                 outfit_kw=dict(main=(150, 40, 40), trim=GOLD))),
    ('Commander', dict(fur=(120, 80, 50), outfit='tactician', hat=False, outfit_kw=dict(main=(120, 30, 30)))),
]


def minotaur_concept(kind):
    fur = (110, 70, 40) if kind == 'brute' else (236, 230, 220)
    m = F.body(fur, 'fur', leg=10, leg_w=3, leg_d=3, gap=1, torso_w=11, torso_d=6, torso_h=12, arm_len=13, arm_w=3, arm_d=3,
               arm_pose='a', head=dict(w=9, d=9, h=9, style='base'), neck=1, foot_len=2, waist=1, hips_w=9)
    hd = m.head
    H.snout(m, hd, shade(fur, 1.25), length=3, w=7, h=3, taper=1)
    H.eyes(m, hd, 'angry', iris=(200, 40, 40), z=hd.z0 + 4)
    H.horns(m, hd, 'long_bull', (232, 220, 190), tip=(150, 140, 120))
    H.ears(m, hd, 'human', fur)
    m.paint((60, 50, 44), 'horn', parts=('foot_r', 'foot_l'))
    b = m.body
    X.sweep(m, [(16, b.back + 1, b.hip + 2, .7, .7, .7), (16, b.back + 4, b.hip - 2, .7, .7, .7), (16, b.back + 5, 4, .6, .6, .6)], fur, 'fur', None)
    m.ellipsoid(16, b.back + 5.4, 3, 1.2, 1.2, 1.6, (40, 34, 30), 'hair', None, only_empty=True)
    if kind == 'brute':
        F.dress(m, trousers=(90, 60, 40), belt=(60, 40, 30), buckle=(184, 128, 70), pauldrons=(110, 114, 122))
    else:
        F.dress(m, plate=(196, 200, 208), plate_trim=GOLD, belt=(60, 40, 30), buckle=GOLD, cape=(60, 70, 140), trousers=(60, 70, 140))
    return m

# --- Loxodon ---------------------------------------------------------------------------------

def trunk(m, color, length='long', tip=None):
    hd = m.head
    tip = tip or shade(color, 0.9)
    y = hd.y0 - 0.5
    if length == 'long':
        pts = [(16, y, hd.z0 + 3.5, 1.5, 1.2, 1.5), (16, y - 1.5, hd.z0 + 1, 1.3, 1.2, 1.3), (16, y - 2, hd.z0 - 2.5, 1.1, 1.1, 1.1),
               (16, y - 2.4, hd.z0 - 5, .9, .9, .9), (16, y - 3.4, hd.z0 - 6.5, .8, .8, .8), (16, y - 4.4, hd.z0 - 5.5, .7, .7, .7)]
    elif length == 'curl':
        pts = [(16, y, hd.z0 + 3.5, 1.5, 1.2, 1.5), (16, y - 1.5, hd.z0 + 1, 1.3, 1.2, 1.3), (16, y - 2.5, hd.z0 - 1.5, 1.1, 1.1, 1.1),
               (16, y - 4, hd.z0 - 2, .9, .9, .9), (16, y - 5, hd.z0 - 0.5, .8, .8, .8), (16, y - 4.6, hd.z0 + 1, .7, .7, .7)]
    else:
        pts = [(16, y, hd.z0 + 3.5, 1.5, 1.2, 1.5), (16, y - 1.5, hd.z0 + 1, 1.3, 1.2, 1.3), (16, y - 2, hd.z0 - 1, 1.1, 1.1, 1.1)]
    X.sweep(m, pts, lambda t, p: tip if t > 0.92 else (shade(color, 0.88) if p[2] % 2 == 0 else color), m.skin_group, 'Head')
    for p in list(m.v):
        v = m.v[p]
        if v.bone == 'Head' and v.part is None and p[2] < 20:
            v.part = 'head'


def tusks(m, color=(240, 232, 210), size=2):
    hd = m.head
    for x in (14, 18):
        pts = [(x, hd.y0, hd.z0), (x, hd.y0 - 1, hd.z0 - 1), (x, hd.y0 - 2, hd.z0 - 1)]
        if size >= 2:
            pts += [(x, hd.y0 - 3, hd.z0), (x, hd.y0 - 4, hd.z0 + 1)]
        if size >= 3:
            pts += [(x + (1 if x > 16 else -1), hd.y0 - 4, hd.z0 + 2), (x + (1 if x > 16 else -1), hd.y0 - 4, hd.z0 + 3)]
        for p in pts:
            m.set(p, color, 'bone', 'Head', 'head')


def wrinkles(m):
    for p, v in m.v.items():
        if v.group == m.skin_group and (p[2] % 3 == 0) and X.h(p, 31) < 0.5:
            v.color = shade(v.color, 0.9)


def loxodon(skin=(150, 150, 156), **kw):
    ex = kw.pop('extras', None)
    trunk_len = kw.pop('trunk', 'long')
    tusk_size = kw.pop('tusks', 2)
    ear_size = kw.pop('ear_size', 1)
    hair = kw.pop('woolly', None)
    def extras(m):
        trunk(m, m.skin, trunk_len)
        if tusk_size:
            tusks(m, size=tusk_size)
        H.ears(m, m.head, 'elephant', m.skin, inner=shade(m.skin, 1.12), size=ear_size)
        wrinkles(m)
        if hair:
            H.hair(m, m.head, hair, 'curly')
        if ex:
            ex(m)
    d = dict(muzzle=None, eyes='dot', iris=(30, 28, 32), head=dict(w=9, d=8, h=8, style='round'), group='skin', extras=extras,
             tail='tuft', tail_color=skin, tail_tip=(60, 56, 56), eye_gap=5, eye_z=24)
    d.update(kw)
    return furry(skin, **d)


LOXODON = [
    ('Monk', dict(outfit='monk', hat=False, outfit_kw=dict(main=(200, 120, 40)))),
    ('Templar', dict(skin=(160, 156, 160), outfit='cleric', hat=False, tusks=3)),
    ('Bulwark', dict(skin=(130, 130, 136), outfit='heavy', hat=False, trunk='curl')),
    ('Shieldwall', dict(outfit='guardian', hat=False, outfit_kw=dict(cape=True, second=(140, 40, 40)), trunk='curl')),
    ('Mammoth', dict(skin=(120, 80, 50), group='fur', woolly=(110, 70, 44), tusks=3, outfit='barbarian', hat=False, outfit_kw=dict(paint=False))),
    ('Sage', dict(skin=(170, 166, 170), outfit='scholar', hat=False, eyes='closed')),
    ('Druid', dict(skin=(140, 140, 130), outfit='nature_mage', hat=False, trunk='curl')),
    ('Merchant', dict(skin=(160, 150, 150), outfit='merchant', hat=True, tusks=1)),
    ('Forgemaster', dict(skin=(130, 126, 130), outfit='smith', hat=False, trunk='short')),
    ('Lightbearer', dict(skin=(200, 196, 200), outfit='white_mage', hat=False, tusks=1)),
    ('Earthcaller', dict(skin=(150, 130, 110), outfit='earth_mage', hat=False, trunk='curl')),
    ('Pygmy', dict(skin=(120, 120, 126), outfit='scout', hat=False, ear_size=0, tusks=0, outfit_kw=dict(quiver=False), trunk='short')),
    ('Warden', dict(skin=(140, 136, 140), outfit='warrior', hat=False, tusks=2)),
]


def loxodon_concept(kind):
    skin = (150, 150, 156) if kind != 'mammoth' else (120, 80, 50)
    m = F.body(skin, 'skin', leg=9, leg_w=4, leg_d=4, gap=1, torso_w=13, torso_d=7, torso_h=12, arm_len=12, arm_w=3, arm_d=3,
               arm_pose='a', head=dict(w=11, d=9, h=10, style='round'), neck=0, foot_len=1, head_forward=3)
    hd = m.head
    H.eyes(m, hd, 'dot', iris=(30, 28, 32), gap=5, z=hd.z0 + 5)
    pts = [(16, hd.y0 - 0.5, hd.z0 + 5, 2, 1.5, 2), (16, hd.y0 - 2, hd.z0 + 1, 1.6, 1.5, 1.6), (16, hd.y0 - 3, hd.z0 - 4, 1.3, 1.3, 1.3),
           (16, hd.y0 - 3.5, hd.z0 - 9, 1, 1, 1), (16, hd.y0 - 5, hd.z0 - 11, .8, .8, .8)]
    X.sweep(m, pts, skin, 'skin', None)
    for x in (13, 19):
        for k, (dy, dz) in enumerate(((0, 0), (-1, -1), (-2, -1), (-3, 0), (-4, 1), (-5, 2), (-5, 3))):
            m.set((x, hd.y0 + dy, hd.z0 + 1 + dz), (240, 232, 210), 'bone')
    for side in (-1, 1):
        for x in range(1, 6):
            for y in range(hd.y0 + 2, hd.y1 + 1):
                for z in range(hd.z0 - 3, hd.z1):
                    xx = (hd.x0 - x) if side < 0 else (hd.x1 + x)
                    dy = (y - (hd.y0 + hd.y1) / 2) / 3.6
                    dz = (z - (hd.z0 + hd.z1) / 2 + 1) / 6.5
                    if dy * dy + dz * dz + (x / 6) ** 2 <= 1:
                        m.set((xx, y, z), skin if x > 1 else shade(skin, 1.1), 'skin')
    if kind == 'mammoth':
        X.mottle(m, [(100, 64, 40), (140, 96, 60)], density=0.4, groups=('skin',))
        F.dress(m, belt=(60, 40, 30), buckle=(184, 128, 70), pauldrons=(110, 114, 122))
    else:
        F.dress(m, robe=(200, 120, 40), robe_trim=GOLD, sash=(150, 40, 40))
    return m

# --- Sealfolk --------------------------------------------------------------------------------

def flippers(color):
    def f(m):
        for side, xs in (('r', (2, 3)), ('l', (29, 30))):
            bone = 'RightHand' if side == 'r' else 'LeftHand'
            for x in xs:
                for y in (14, 15, 16, 17, 18):
                    m.set((x, y, 18), color, 'skin', bone)
        m.paint(color, None, parts=('hand_r', 'hand_l'))
    return f


def seal(fur=(120, 120, 126), **kw):
    ex = kw.pop('extras', None)
    flip = kw.pop('flipper', shade(fur, 0.75))
    def extras(m):
        flippers(flip)(m)
        hd = m.head
        # a shine in each big dark eye
        for x in (14, 18):
            y = m.front_y(x, hd.z0 + 3)
            if y is not None and m.get((x, y, hd.z0 + 3)).group == 'eye':
                m.set((x, y, hd.z0 + 3), (250, 250, 250), 'eye', 'Head', 'head')
        if ex:
            ex(m)
    d = dict(muzzle=dict(length=2, w=5, h=2, taper=1, nose_color=(40, 36, 36), nose_width=1, color=shade(fur, 1.15)), ears=None,
             eyes='dot', iris='black', head=dict(w=9, d=8, h=7, style='round'), whiskers=(220, 214, 200), tail='seal', feet='webbed',
             feet_color=flip, extras=extras, group='fur', belly=shade(fur, 1.15))
    d.update(kw)
    return furry(fur, **d)


def walrus(m):
    tip, half, z, hgt, ln = m.snout_info
    for x in (15, 17):
        for k in range(1, 6):
            m.set((x, tip + 1, z - k), (240, 232, 210), 'bone', 'Head', 'head')
    for x in range(14, 19):
        m.set((x, tip, z), (180, 150, 120), 'hair', 'Head', 'head')
        m.set((x, tip + 1, z - 1), (180, 150, 120), 'hair', 'Head', 'head') if x not in (15, 17) else None


def big_nose(m):
    tip, half, z, hgt, ln = m.snout_info
    m.ellipsoid(16, tip + 0.3, z + 1.5, 1.6, 1.3, 1.8, shade(m.skin, 0.9), m.skin_group, 'Head', 'head', only_empty=True)
    m.set((16, tip - 1, z), shade(m.skin, 0.8), m.skin_group, 'Head', 'head')


SEALS = [
    ('Harbor', dict(fur=(130, 130, 136), pattern=lambda m: X.spots(m, (90, 90, 96), density=0.15), outfit='sailor', hat=True)),
    ('Walrus', dict(fur=(170, 120, 90), extras=walrus, head=dict(w=11, d=8, h=7, style='round'), outfit='pirate', hat=True,
                    outfit_kw=dict(eyepatch=False))),
    ('SeaLion', dict(fur=(140, 100, 60), ears='round', outfit='gunslinger', hat=False)),
    ('Leopard', dict(fur=(150, 150, 156), pattern=lambda m: X.spots(m, (60, 60, 66), density=0.2), outfit='assault', hat=False,
                     teeth='fangs', eyes='angry')),
    ('Elephant', dict(fur=(130, 110, 90), extras=big_nose, outfit='heavy', hat=False, head=dict(w=11, d=8, h=7, style='round'))),
    ('Harp', dict(fur=(246, 244, 240), outfit='white_mage', hat=False, eyes='big', eye_h=3, iris='black', flipper=(200, 200, 200))),
    ('Fur', dict(fur=(90, 70, 56), ears='round', outfit='hunter', hat=True)),
    ('Monk', dict(fur=(110, 110, 116), outfit='monk', hat=False, outfit_kw=dict(main=(60, 100, 150)))),
    ('Hooded', dict(fur=(160, 160, 170), pattern=lambda m: X.spots(m, (50, 50, 56), density=0.2, size=2), outfit='rogue', hat=False)),
    ('Selkie', dict(fur=(90, 96, 110), outfit='water_mage', hat=False)),
    ('Bearded', dict(fur=(150, 120, 100), extras=lambda m: H.beard(m, m.head, (200, 190, 170), 'goatee'), outfit='scholar', hat=False)),
    ('Ringed', dict(fur=(110, 110, 120), pattern=lambda m: X.spots(m, (200, 200, 206), density=0.15), outfit='scout', hat=False,
                    outfit_kw=dict(quiver=False))),
]


def seal_concept(kind):
    fur = (130, 130, 136) if kind != 'walrus' else (170, 120, 90)
    m = F.body(fur, 'fur', leg=3, leg_w=3, leg_d=3, gap=1, torso_w=11, torso_d=8, torso_h=12, arm_len=8, arm_w=2, arm_d=4,
               arm_pose='a', head=dict(w=9, d=8, h=8, style='round'), neck=1, foot_len=3)
    hd = m.head
    H.snout(m, hd, shade(fur, 1.15), length=2, w=5, h=2, taper=1, nose_color=(40, 36, 36), nose_width=1)
    H.eyes(m, hd, 'dot', iris=(30, 28, 32), z=hd.z0 + 3)
    X.whiskers(m, (220, 214, 200))
    if kind == 'walrus':
        walrus(m)
        F.dress(m, belt=(60, 40, 30), buckle=GOLD, sash=(40, 60, 110))
    else:
        F.dress(m, shirt=(40, 60, 110), sleeves='short', belt=(60, 40, 30))
    return m

# --- Monkeyfolk goblins ----------------------------------------------------------------------

def face_disc(color, rows=6, top=None):
    """The bare face of a monkey: a rounded patch over the front of the head."""
    def f(m):
        hd = m.head
        cz = hd.z0 + (rows - 1) / 2
        for x in range(hd.x0, hd.x1 + 1):
            for z in range(hd.z0, hd.z0 + rows):
                dx = (x - 16) / (hd.w / 2 - 0.3)
                dz = (z - cz) / (rows / 2)
                if dx * dx + dz * dz > 1.05:
                    continue
                y = m.front_y(x, z)
                if y is not None and m.get((x, y, z)).group in ('fur',):
                    m.set((x, y, z), color, 'skin', 'Head', 'head')
    return f


def goblin_monkey(fur=(110, 80, 50), skin=(220, 180, 150), **kw):
    ex = kw.pop('extras', None)
    rows = kw.pop('face_rows', 6)
    ears = kw.pop('gob_ears', 'elf')
    grin = kw.pop('grin', True)
    def extras(m):
        if ex:
            ex(m)
    def pat(m):
        face_disc(skin, rows)(m)
        hd = m.head
        H.eyes(m, hd, kw_eyes, iris=kw_iris, z=hd.z0 + 3, gap=3, height=kw_eye_h)
        H.brows(m, hd, shade(fur, 0.7), z=hd.z0 + 5, style='angry')
        if grin:
            H.mouth(m, hd, 'grin', color=(60, 30, 30), z=hd.z0, width=3)
        H.ears(m, hd, ears, skin, inner=shade(skin, 0.85))
    kw_eyes = kw.pop('eyes', 'template')
    kw_eye_h = kw.pop('eye_h', 2)
    kw_iris = kw.pop('iris', (230, 180, 40))
    kw_iris = EYES.get(kw_iris, kw_iris) if isinstance(kw_iris, str) else kw_iris
    d = dict(muzzle=dict(length=1, w=5, h=2, taper=0, nose_color=shade(skin, 0.7), nose_width=3, color=skin), ears=None, eyes=None,
             head=dict(w=9, d=8, h=8, style='base'), tail='monkey', pattern=pat, extras=extras, hands=True, hand_color=skin,
             feet=True, feet_color=skin)
    d.update(kw)
    return furry(fur, **d)


def mandrill(m):
    tip, half, z, hgt, ln = m.snout_info
    for k in range(ln + 1):
        m.set((16, m.head.y0 - k, z + hgt - 1), (220, 40, 40), 'skin', 'Head', 'head')
    for x in (14, 18):
        y = m.front_y(x, z + 1)
        if y is not None:
            m.set((x, y, z + 1), (80, 120, 220), 'skin', 'Head', 'head')
            m.set((x, y, z), (80, 120, 220), 'skin', 'Head', 'head')


def silverback(m):
    m.paint((170, 170, 176), None, parts=('chest', 'spine', 'hips'), where=lambda p, v: p[1] == 17 and v.group == 'fur')


def flanges(m):
    hd = m.head
    for side in (-1, 1):
        x = hd.x0 - 1 if side < 0 else hd.x1 + 1
        for z in range(hd.z0, hd.z1):
            for y in (hd.y0, hd.y0 + 1):
                m.set((x, y, z), (170, 110, 80), 'skin', 'Head', 'head')


def proboscis(m):
    tip, half, z, hgt, ln = m.snout_info
    m.ellipsoid(16, tip - 0.2, z + 1, 1.4, 1.3, 1.8, (230, 150, 120), 'skin', 'Head', 'head', only_empty=True)


MONKEYS = [
    ('Chimp', dict(fur=(60, 50, 44), skin=(200, 170, 140), outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Macaque', dict(fur=(170, 140, 110), skin=(220, 120, 110), outfit='scout', hat=False, outfit_kw=dict(quiver=False), tail='stub')),
    ('Mandrill', dict(fur=(90, 80, 60), skin=(60, 50, 50), extras=mandrill, muzzle=dict(length=3, w=5, h=2, taper=1, nose_color=(220, 40, 40),
                      nose_width=3, color=(60, 50, 50)), outfit='tribal', hat=True, tail='stub')),
    ('Baboon', dict(fur=(150, 130, 90), skin=(80, 70, 70), muzzle=dict(length=3, w=5, h=3, taper=1, nose_color=(40, 34, 34), nose_width=3,
                    color=(80, 70, 70)), extras=lambda m: X.mane(m, (130, 110, 80), size=1), outfit='barbarian', hat=False, outfit_kw=dict(paint=False))),
    ('Capuchin', dict(fur=(60, 46, 36), skin=(240, 220, 190), face_rows=7, outfit='bard', hat=False)),
    ('Howler', dict(fur=(40, 30, 26), skin=(60, 50, 44), extras=lambda m: H.beard(m, m.head, (40, 30, 26), 'full'), outfit='fire_mage', hat=False)),
    ('Orangutan', dict(fur=(190, 90, 40), skin=(150, 100, 80), extras=flanges, outfit='scholar', hat=False)),
    ('Gorilla', dict(fur=(50, 46, 46), skin=(70, 66, 66), extras=silverback, outfit='heavy', hat=False, tail=None,
                     head=dict(w=11, d=8, h=8, style='base'))),
    ('Lemur', dict(fur=(150, 150, 156), skin=(250, 250, 250), face_rows=4, gob_ears='cat', muzzle=dict(length=2, w=3, h=2, taper=0,
                   nose_color=(30, 30, 30), nose_width=1, color=(40, 40, 40)), eyes='glow', iris=(240, 160, 40), tail='ringed',
                   tail_color=(250, 250, 250), tail_second=(40, 40, 40), outfit='psychic', hat=False, grin=False)),
    ('Proboscis', dict(fur=(200, 140, 90), skin=(230, 170, 140), extras=proboscis, outfit='merchant', hat=True)),
    ('Tarsier', dict(fur=(170, 140, 110), skin=(190, 160, 130), eyes='big', iris=(220, 170, 60), eye_h=3, gob_ears='bat', outfit='apothecary',
                     hat='goggles', grin=False, tail='thin')),
    ('Snubnose', dict(fur=(220, 160, 60), skin=(120, 170, 220), outfit='monk', hat=False, outfit_kw=dict(main=(150, 40, 40)))),
    ('Spider', dict(fur=(40, 36, 34), skin=(220, 180, 150), outfit='sharpshooter', hat=False)),
    ('Scrapper', dict(fur=(90, 110, 60), skin=(150, 190, 110), outfit='assault', hat=True, iris=(220, 40, 40))),
    ('Grimgrin', dict(fur=(80, 100, 60), skin=(170, 200, 120), outfit='gunslinger', hat=True, iris=(240, 220, 60))),
    ('Boss', dict(fur=(110, 120, 70), skin=(170, 190, 120), outfit='tactician', hat=True, iris=(220, 40, 40))),
]


def goblin_concept(kind):
    fur = (90, 110, 60) if kind == 'goblin' else (60, 50, 44)
    skin = (170, 200, 120) if kind == 'goblin' else (200, 170, 140)
    m = F.body(fur, 'fur', leg=5, leg_w=2, leg_d=2, gap=1, torso_w=7, torso_d=4, torso_h=8, arm_len=14, arm_w=2, arm_d=2,
               arm_pose='a', head=dict(w=9, d=8, h=8, style='base'), neck=0, foot_len=2, head_forward=2)
    hd = m.head
    H.snout(m, hd, skin, length=1, w=5, h=2, taper=0, nose_color=shade(skin, 0.7), nose_width=3)
    face_disc(skin, 6)(m)
    H.eyes(m, hd, 'template', iris=(230, 180, 40), z=hd.z0 + 3)
    H.brows(m, hd, shade(fur, 0.7), z=hd.z0 + 5, style='angry')
    H.mouth(m, hd, 'grin', color=(60, 30, 30), z=hd.z0, width=3)
    H.ears(m, hd, 'elf_long', skin, inner=shade(skin, 0.85))
    b = m.body
    pts = [(16, b.back + 1, b.hip + 1), (16, b.back + 4, b.hip - 1), (16, b.back + 7, b.hip + 1), (16, b.back + 8, b.hip + 5), (16, b.back + 6, b.hip + 7), (16, b.back + 5, b.hip + 5)]
    X.sweep(m, [(x, y, z, .65, .65, .65) for x, y, z in pts], fur, 'fur', None)
    m.paint(skin, None, parts=('hand_r', 'hand_l', 'foot_r', 'foot_l'))
    F.dress(m, belt=(80, 60, 40), buckle=(184, 128, 70), trousers=(120, 90, 60), sash=(150, 40, 40) if kind == 'goblin' else None)
    return m


SETS = [
    Set('Catfolk', 'Catfolk', designs(cat, CATS), treat3(1, 2, 5), concepts=[('Weretiger', lambda: CX.beast_stance('tiger'))]),
    Set('Dogfolk', 'Dogfolk', designs(dog, DOGS), treat3(2, 1, 7), concepts=[('Werewolf', lambda: CX.beast_stance('wolf'))]),
    Set('Minotaur', 'Minotaur', designs(bull, MINOTAUR), treat3(1, 2, 4),
        concepts=[('Brute', lambda: minotaur_concept('brute')), ('Paladin', lambda: minotaur_concept('paladin'))]),
    Set('Loxodon', 'Loxodon', designs(loxodon, LOXODON), treat3(1, 2, 5),
        concepts=[('Pilgrim', lambda: loxodon_concept('pilgrim')), ('Mammoth', lambda: loxodon_concept('mammoth'))]),
    Set('Sealfolk', 'Sealfolk', designs(seal, SEALS), treat3(1, 2, 6),
        concepts=[('Selkie', lambda: seal_concept('seal')), ('Walrus', lambda: seal_concept('walrus'))]),
    Set('MonkeyfolkGoblins', 'MonkeyfolkGoblin', designs(goblin_monkey, MONKEYS), treat3(1, 3, 14), title='Monkeyfolk goblins',
        concepts=[('Goblin', lambda: goblin_concept('goblin')), ('Chimp', lambda: goblin_concept('chimp'))]),
]
