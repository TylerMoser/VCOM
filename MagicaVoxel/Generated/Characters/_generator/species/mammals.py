"""Small furred folk: rodents (generic, rat, hamster, beaver, rabbit, squirrel, mole), batfolk,
hedgehogs, armadillos, otters and badgers."""
from .common import Set, designs, beast, EYES
from core import shade, mix
import heads as H
import outfits as O
import extras as X
import freebody as F
from . import concepts_extra as CX

WHITE = (240, 238, 230)
PINK = (236, 160, 170)
NOSE_PINK = (230, 130, 150)
BLACK_NOSE = (36, 30, 32)


def treat3(a, b, c):
    return [(a, 'Cartoon'), (b, 'TwoColor'), (c, 'CratePalette')]


def buck_teeth(m, color=WHITE, wide=False):
    tip, half, z, hgt, ln = m.snout_info
    for x in ((15, 16) if wide else (16,)):
        m.set((x, tip, z - 1), color, 'bone', 'Head', 'head')
        m.set((x, tip + 1, z - 1), color, 'bone', 'Head', 'head')


def face_patch(m, color, rows=2):
    """A paler face round the muzzle: the face's lower rows."""
    hd = m.head
    for x in range(hd.x0 + 1, hd.x1):
        for z in range(hd.z0, hd.z0 + rows):
            y = m.front_y(x, z)
            v = m.get((x, y, z))
            if v and v.group == m.skin_group:
                v.color = color


def furry(fur, muzzle=None, ears=None, eyes='pupil', iris='black', tail=None, tail_color=None, tail_tip=None,
          belly=None, face=None, nose=None, whiskers=None, teeth=None, outfit=None, outfit_kw=None, hat=False,
          head=None, pattern=None, extras=None, hands=None, hand_color=None, feet=None, feet_color=None,
          ear_color=None, ear_inner=None, eye_gap=3, eye_z=None, eye_h=2, glow_eyes=False, brows=None,
          head_color=None, mouth=None, cheeks=None, ear_size=1, group='fur', tail_second=None):
    """A furred figure: [muzzle] snout()'s keywords; [face] a paler muzzle-and-cheeks colour;
    [teeth] 'buck' or 'fangs'."""
    iris = EYES.get(iris, iris) if isinstance(iris, str) else iris
    head = head or dict(w=9, d=8, h=8, style='base')
    def face_fn(m, hd):
        if face:
            face_patch(m, face)
        if teeth == 'buck':
            buck_teeth(m)
        elif teeth == 'buck2':
            buck_teeth(m, wide=True)
        elif teeth == 'orange':
            buck_teeth(m, (230, 140, 40), wide=True)
        elif teeth == 'fangs':
            tip, half, z, hgt, ln = m.snout_info
            for x in (15, 17):
                m.set((x, tip, z - 1), WHITE, 'bone', 'Head', 'head')
    def after(m):
        if extras:
            extras(m)
    sn = None
    if muzzle:
        sn = dict(length=2, w=3, h=2, taper=0, nose_width=1)
        sn.update(muzzle)
        if 'color' not in sn:
            sn['color'] = face or shade(head_color or fur, 1.1)
    m = beast(fur, skin_group=group, head=head, muzzle=sn, ears=None, eyes=eyes, iris=iris, eye_gap=eye_gap, eye_z=eye_z,
              eye_h=eye_h, glow_eyes=glow_eyes, brows=brows, belly_color=belly, face=face_fn, pattern=pattern, tail=tail,
              tail_color=tail_color, tail_tip=tail_tip, tail_second=tail_second, hands=hands, hand_color=hand_color, feet=feet, feet_color=feet_color,
              outfit=None, extras=None, head_color=head_color, cheeks=cheeks, whiskers=whiskers)
    if ears:
        H.ears(m, m.head, ears, ear_color or head_color or fur, inner=ear_inner, size=ear_size)
    if outfit:
        from classes import dress
        dress(m, outfit, hat=hat, **(outfit_kw or {}))
        if tail:
            X.tail(m, tail, tail_color or fur, tip=tail_tip, group=group, second=tail_second)
    after(m)
    return m


# --- Rodents ---------------------------------------------------------------------------------

def plague_mask(m, color=(230, 220, 190), lens=(60, 60, 60)):
    """A plague doctor's beaked mask over the face and snout."""
    hd = m.head
    for x in range(hd.x0, hd.x1 + 1):
        for z in range(hd.z0, hd.z0 + 5):
            y = m.front_y(x, z)
            if y is not None and y >= hd.y0 - 1:
                m.set((x, y, z), color, 'leather', 'Head', 'head')
    for k in range(1, 6):
        for x in range(16 - max(0, 2 - k // 2), 17 + max(0, 2 - k // 2)):
            for z in range(hd.z0, hd.z0 + max(1, 3 - k // 2)):
                m.set((x, hd.y0 - k, z), color if k < 5 else shade(color, 0.8), 'leather', 'Head', 'head')
    for x in (13, 14, 18, 19):
        m.set((x, hd.y0 - 1, hd.z0 + 3), lens, 'glass', 'Head', 'head', ('glass', 0.4))
    H.hat(m, hd, 'wide', (40, 36, 40), trim=(30, 28, 30))


def crown_small(m):
    H.hat(m, m.head, 'crown', (222, 184, 72), extra=(60, 160, 220))


def mouse(fur, **kw):
    d = dict(muzzle=dict(length=2, w=3, h=2, taper=1, nose_color=NOSE_PINK, nose_width=1), ears='mouse', ear_inner=PINK,
             eyes='dot', tail='thin', tail_color=PINK, whiskers=(230, 230, 230), teeth='buck', head=dict(w=9, d=8, h=7, style='base'),
             ear_size=2)
    d.update(kw)
    return furry(fur, **d)


RODENT = [
    ('FieldMouse', dict(fur=(170, 120, 80), belly=(230, 210, 180), face=(230, 210, 180), outfit='scout', outfit_kw=dict(quiver=True))),
    ('HouseMouse', dict(fur=(150, 150, 154), belly=(220, 220, 220), outfit='peasant', hat=True)),
    ('WhiteMouse', dict(fur=(244, 240, 236), iris='red', eyes='bead', outfit='white_mage', hat=False)),
    ('Dormouse', dict(fur=(210, 150, 80), belly=(240, 220, 180), face=(240, 220, 180), tail='bushy', tail_color=(200, 140, 70),
                      outfit='monk', hat=False, eyes='big', iris='black', eye_h=3)),
    ('Gerbil', dict(fur=(220, 170, 110), belly=(245, 235, 210), tail='tuft', tail_color=(220, 170, 110), tail_tip=(150, 100, 60),
                    outfit='merchant', hat=True)),
    ('Vole', dict(fur=(110, 86, 60), belly=(170, 150, 120), ears='round', muzzle=dict(length=1, w=3, h=2, nose_color=BLACK_NOSE, nose_width=1),
                  outfit='miner', hat=True, tail='thin', tail_color=(110, 86, 60))),
    ('Jerboa', dict(fur=(230, 200, 150), belly=(250, 240, 220), ears='rabbit', ear_inner=PINK, tail='tuft', tail_color=(230, 200, 150),
                    tail_tip=(250, 250, 250), outfit='sharpshooter', hat=False, eyes='big', eye_h=3)),
    ('Pika', dict(fur=(160, 130, 100), ears='round', muzzle=dict(length=1, w=3, h=2, nose_color=BLACK_NOSE, nose_width=1), tail=None,
                  outfit='bard', hat=True)),
    ('Chinchilla', dict(fur=(170, 174, 180), belly=(230, 230, 230), ears='mouse', ear_size=2, tail='bushy', tail_color=(150, 154, 160),
                        outfit='noble', hat=False)),
    ('Shrew', dict(fur=(80, 70, 70), muzzle=dict(length=3, w=3, h=2, taper=1, nose_color=NOSE_PINK, nose_width=1),
                                    ears='round', outfit='rogue', hat=True, eyes='bead')),
    ('Piebald', dict(fur=(240, 236, 230), pattern=lambda m: X.spots(m, (60, 50, 50), density=0.18, size=2), outfit='gunslinger', hat=True)),
    ('Tinker', dict(fur=(130, 100, 80), belly=(200, 180, 150), outfit='apothecary', hat='goggles')),
    ('Brigadier', dict(fur=(120, 110, 100), belly=(200, 190, 170), outfit='tactician', hat=True)),
]


def rat(fur, **kw):
    d = dict(muzzle=dict(length=3, w=3, h=2, taper=1, nose_color=NOSE_PINK, nose_width=1), ears='mouse', ear_inner=PINK, ear_size=1,
             eyes='dot', tail='thin', tail_color=(220, 170, 170), whiskers=(220, 220, 220), teeth='buck2',
             head=dict(w=9, d=8, h=7, style='base'))
    d.update(kw)
    return furry(fur, **d)


RAT = [
    ('Sewer', dict(fur=(110, 100, 90), belly=(160, 150, 140), outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('PlagueDoctor', dict(fur=(80, 74, 70), outfit='apothecary', hat=False, extras=plague_mask,
                          outfit_kw=dict(main=(50, 46, 50), second=(40, 36, 40)))),
    ('Bilge', dict(fur=(140, 120, 100), outfit='pirate', hat=True)),
    ('Cutpurse', dict(fur=(70, 66, 70), belly=(130, 120, 120), outfit='rogue', hat=True)),
    ('Ratcatcher', dict(fur=(150, 130, 110), outfit='hunter', hat=True)),
    ('Gutter', dict(fur=(90, 90, 96), outfit='assault', hat=True, eyes='angry', iris='red')),
    ('Snowfur', dict(fur=(240, 236, 232), iris='red', eyes='pupil', outfit='psychic', hat=False)),
    ('Scavenger', dict(fur=(120, 100, 76), outfit='miner', hat=False, outfit_kw=dict(pack=True))),
    ('Plaguecaller', dict(fur=(90, 96, 80), outfit='necromancer', hat=True, iris=(150, 255, 90), eyes='glow')),
    ('RatKing', dict(fur=(110, 100, 96), outfit='noble', hat=False, extras=crown_small, outfit_kw=dict(cape=True, main=(90, 30, 60)))),
    ('Smuggler', dict(fur=(60, 56, 60), outfit='gunslinger', hat=True)),
    ('Sapper', dict(fur=(130, 110, 90), outfit='smith', hat=False, extras=lambda m: H.hat(m, m.head, 'goggles', (120, 90, 60), trim=(70, 50, 35),
                                                                                         extra=(220, 170, 90)))),
    ('Dockhand', dict(fur=(150, 140, 130), outfit='sailor', hat=True)),
]


def cheek_pouches(color):
    def f(m):
        hd = m.head
        for side in (-1, 1):
            x = hd.x0 - 1 if side < 0 else hd.x1 + 1
            for y in range(hd.y0 + 1, hd.y0 + 5):
                for z in range(hd.z0, hd.z0 + 3):
                    m.set((x, y, z), color, 'fur', 'Head', 'head')
        for x in range(hd.x0, hd.x1 + 1):
            for z in range(hd.z0, hd.z0 + 2):
                y = m.front_y(x, z)
                if y is not None and m.get((x, y, z)).group == 'fur':
                    m.set((x, y, z), color, 'fur', 'Head', 'head')
    return f


def hamster(fur, cheek=(245, 235, 220), **kw):
    d = dict(muzzle=dict(length=1, w=3, h=2, nose_color=NOSE_PINK, nose_width=1, color=cheek), ears='hamster', ear_inner=PINK, eyes='dot',
             tail='stub', tail_color=cheek, teeth='buck', head=dict(w=9, d=8, h=7, style='round'), belly=cheek, cheeks=None)
    d.update(kw)
    m = furry(fur, **d)
    return m


def with_cheeks(builder, cheek):
    def f(**kw):
        ex = kw.pop('extras', None)
        def extras(m):
            cheek_pouches(cheek)(m)
            if ex:
                ex(m)
        kw['extras'] = extras
        return builder(**kw)
    return f


def hamster_cheeked(fur, cheek=(245, 235, 220), **kw):
    ex = kw.pop('extras', None)
    def extras(m):
        cheek_pouches(cheek)(m)
        if ex:
            ex(m)
    return hamster(fur, cheek=cheek, extras=extras, **kw)


def back_stripe(color):
    def f(m):
        m.paint(color, None, parts=('chest', 'spine', 'hips'), where=lambda p, v: p[1] == 17 and p[0] == 16 and v.group == m.skin_group)
        hd = m.head
        m.paint(color, None, where=lambda p, v: v.part == 'head' and p[0] == 16 and p[2] >= hd.z1 and v.group == m.skin_group)
    return f


HAMSTER = [
    ('Golden', dict(fur=(220, 150, 70), outfit='peasant', hat=True)),
    ('Teddy', dict(fur=(200, 140, 80), cheek=(240, 220, 190), outfit='monk', hat=False, eyes='big', eye_h=3)),
    ('Winter', dict(fur=(210, 214, 220), cheek=(250, 250, 250), pattern=back_stripe((90, 96, 110)), outfit='hunter', hat=True)),
    ('Panda', dict(fur=(245, 242, 236), pattern=lambda m: X.spots(m, (40, 36, 36), density=0.22, size=3), outfit='bard', hat=True)),
    ('Roborovski', dict(fur=(200, 170, 120), cheek=(250, 246, 236), outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('Banded', dict(fur=(110, 80, 60), pattern=lambda m: m.paint((240, 230, 210), None, parts=('chest', 'spine'),
                                                                   where=lambda p, v: v.group == m.skin_group), outfit='merchant', hat=True)),
    ('Campbell', dict(fur=(170, 150, 120), pattern=back_stripe((80, 70, 60)), outfit='miner', hat=True)),
    ('Blackbear', dict(fur=(50, 46, 46), cheek=(80, 76, 76), outfit='heavy', hat=False)),
    ('Cinnamon', dict(fur=(200, 110, 60), cheek=(240, 200, 170), outfit='apothecary', hat='goggles', iris='red', eyes='pupil')),
    ('Cream', dict(fur=(240, 220, 180), outfit='cleric', hat=True)),
    ('Wheelwright', dict(fur=(180, 130, 80), outfit='smith', hat=False)),
    ('Captain', dict(fur=(210, 160, 90), outfit='tactician', hat=True)),
    ('Gourmand', dict(fur=(230, 180, 110), outfit='merchant', hat=False, extras=lambda m: H.hat(m, m.head, 'top', (60, 40, 50), trim=(150, 40, 60)))),
]


def beaver(fur, **kw):
    d = dict(muzzle=dict(length=2, w=5, h=2, taper=1, nose_color=BLACK_NOSE, nose_width=3, color=shade(fur, 1.2)), ears='round',
             eyes='dot', tail='beaver', tail_color=fur, tail_tip=(60, 56, 56), teeth='orange', head=dict(w=9, d=8, h=7, style='round'),
             whiskers=(60, 50, 40), feet='webbed', feet_color=(70, 60, 56), belly=shade(fur, 1.15))
    d.update(kw)
    return furry(fur, **d)


def plaid(base, line):
    def f(m):
        m.paint(line, 'cloth', parts=('chest', 'spine', 'uarm_r', 'uarm_l', 'larm_r', 'larm_l'),
                where=lambda p, v: v.group == 'cloth' and ((p[0] % 3 == 0) or (p[2] % 3 == 0)))
    return f


BEAVER = [
    ('Lumberjack', dict(fur=(120, 80, 50), outfit='peasant', hat='beanie', outfit_kw=dict(main=(180, 40, 40), hat_color=(180, 40, 40)),
                        extras=plaid((180, 40, 40), (40, 30, 30)))),
    ('Dambuilder', dict(fur=(110, 74, 46), outfit='smith', hat=False)),
    ('Engineer', dict(fur=(130, 90, 60), outfit='apothecary', hat='goggles', outfit_kw=dict(main=(150, 120, 80)))),
    ('Riverwarden', dict(fur=(100, 70, 44), outfit='guardian', hat=False, outfit_kw=dict(cape=False, emblem='bar'))),
    ('Foreman', dict(fur=(140, 100, 60), outfit='miner', hat=True, outfit_kw=dict(hat_color=(230, 200, 60)))),
    ('Boatman', dict(fur=(120, 84, 56), outfit='sailor', hat=True)),
    ('Gnawer', dict(fur=(90, 60, 40), outfit='barbarian', hat=False, outfit_kw=dict(paint=False))),
    ('Surveyor', dict(fur=(150, 110, 70), outfit='scholar', hat=True)),
    ('Trapper', dict(fur=(110, 80, 56), outfit='hunter', hat=True)),
    ('Sergeant', dict(fur=(126, 86, 52), outfit='tactician', hat=True, outfit_kw=dict(main=(60, 80, 50)))),
    ('Carpenter', dict(fur=(140, 96, 60), outfit='peasant', hat=False, extras=lambda m: O.apron(m, (190, 170, 130), bottom=4))),
    ('Rifleman', dict(fur=(100, 70, 50), outfit='sharpshooter', hat=True)),
]


def rabbit(fur, **kw):
    d = dict(muzzle=dict(length=1, w=3, h=2, nose_color=NOSE_PINK, nose_width=1, color=WHITE), ears='rabbit', ear_inner=PINK, eyes='big',
             eye_h=3, iris='brown', tail='stub', tail_color=WHITE, teeth='buck', head=dict(w=9, d=8, h=7, style='round'))
    d.update(kw)
    return furry(fur, **d)


RABBIT = [
    ('Snowshoe', dict(fur=(244, 242, 238), muzzle=dict(length=1, w=3, h=2, nose_color=NOSE_PINK, nose_width=1, color=(250, 250, 250)),
                      outfit='scout', hat=False, iris='blue')),
    ('Cottontail', dict(fur=(160, 130, 100), belly=(230, 220, 200), outfit='ranger', hat=False)),
    ('Lop', dict(fur=(200, 170, 130), ears='rabbit_lop', outfit='bard', hat=True)),
    ('Jackrabbit', dict(fur=(170, 140, 100), ears='rabbit', ear_size=1, outfit='gunslinger', hat=False, iris='amber')),
    ('Harlequin', dict(fur=(230, 160, 70), pattern=lambda m: X.spots(m, (50, 40, 40), density=0.25, size=2), outfit='noble', hat=False)),
    ('Dutch', dict(fur=(60, 56, 60), pattern=lambda m: m.paint((245, 242, 236), None, parts=('chest', 'spine', 'uarm_r', 'uarm_l'),
                                                               where=lambda p, v: v.group == m.skin_group), outfit='monk', hat=False)),
    ('Moonhare', dict(fur=(200, 206, 230), outfit='psychic', hat=False, iris='violet', eyes='glow')),
    ('Warren', dict(fur=(140, 110, 80), outfit='guardian', hat=False, outfit_kw=dict(emblem='cross', second=(60, 100, 60)))),
    ('Thumper', dict(fur=(120, 120, 126), outfit='assault', hat=True, eyes='angry')),
    ('Angora', dict(fur=(250, 240, 236), pattern=lambda m: X.mottle(m, [(240, 230, 226), (255, 250, 248)], density=0.5), outfit='white_mage',
                    hat=False)),
    ('Rex', dict(fur=(110, 70, 50), outfit='tactician', hat=True)),
    ('Marsh', dict(fur=(90, 76, 60), ears='rabbit_lop', outfit='nature_mage', hat=False)),
    ('Sniper', dict(fur=(150, 150, 140), outfit='sharpshooter', hat=False)),
]


def squirrel(fur, **kw):
    d = dict(muzzle=dict(length=1, w=3, h=2, nose_color=BLACK_NOSE, nose_width=1, color=shade(fur, 1.2)), ears='lynx', ear_inner=shade(fur, 0.8),
             eyes='big', eye_h=3, iris='black', tail='bushy', tail_color=fur, teeth='buck', head=dict(w=9, d=8, h=7, style='base'),
             belly=(240, 226, 200))
    d.update(kw)
    return furry(fur, **d)


def chipmunk(m):
    for p, v in m.v.items():
        if v.group == m.skin_group and v.part in ('chest', 'spine', 'hips') and p[1] == 17:
            if p[0] in (15, 17):
                v.color = (60, 40, 30)
            elif p[0] in (14, 18):
                v.color = (240, 226, 200)
    hd = m.head
    for x in (14, 18):
        for z in (hd.z0 + 2,):
            y = m.front_y(x, z)
            m.set((x, y, z), (240, 226, 200), 'fur', 'Head', 'head')


def gliding(color):
    def f(m):
        X.bat_wings(m, color, frame=shade(color, 0.8), depth=6, reach=0)
    return f


SQUIRREL = [
    ('Red', dict(fur=(200, 90, 40), outfit='scout', hat=False, outfit_kw=dict(quiver=True))),
    ('Grey', dict(fur=(140, 140, 146), outfit='ranger', hat=False)),
    ('Black', dict(fur=(50, 46, 46), belly=(80, 76, 76), outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Chipmunk', dict(fur=(190, 130, 80), pattern=chipmunk, outfit='bard', hat=True, tail='fox', tail_color=(150, 100, 60))),
    ('Flying', dict(fur=(150, 120, 90), outfit=None, extras=gliding((170, 140, 110)), eyes='big', eye_h=3)),
    ('Fox', dict(fur=(190, 120, 70), belly=(220, 170, 110), outfit='gunslinger', hat=True)),
    ('Albino', dict(fur=(245, 242, 236), iris='red', eyes='pupil', outfit='white_mage', hat=False)),
    ('Tassel', dict(fur=(110, 100, 96), ears='lynx', outfit='hunter', hat=False)),
    ('Nutcracker', dict(fur=(170, 100, 60), outfit='tactician', hat=True, outfit_kw=dict(main=(160, 40, 40)))),
    ('Prairie', dict(fur=(200, 160, 110), ears='round', tail='dog', outfit='sharpshooter', hat=False)),
    ('Acorn', dict(fur=(180, 110, 60), outfit='nature_mage', hat=False)),
    ('Treetop', dict(fur=(160, 80, 40), outfit='assault', hat=True)),
]


def mole(fur=(54, 50, 56), **kw):
    d = dict(muzzle=dict(length=3, w=3, h=2, taper=1, nose_color=(240, 150, 170), nose_width=3, color=(230, 160, 170)), ears=None,
             eyes='bead', iris=(20, 20, 20), tail='thin', tail_color=(230, 160, 170), hands='big_claws', hand_color=(236, 170, 176),
             head=dict(w=9, d=8, h=7, style='round'), whiskers=(200, 190, 190))
    d.update(kw)
    return furry(fur, **d)


def star_nose(m):
    tip, half, z, hgt, ln = m.snout_info
    for (dx, dz) in ((-2, 0), (-2, 1), (2, 0), (2, 1), (-1, 2), (1, 2), (0, 2), (-1, -1), (1, -1), (0, -1)):
        m.set((16 + dx, tip - 1 if abs(dx) < 2 else tip, z + dz), (240, 120, 150), 'skin', 'Head', 'head')


MOLE = [
    ('Digger', dict(outfit='miner', hat=True)),
    ('StarNose', dict(fur=(60, 50, 46), extras=star_nose, outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('Sapper', dict(outfit='assault', hat=False, extras=lambda m: H.hat(m, m.head, 'goggles', (120, 90, 60), trim=(70, 50, 35), extra=(230, 180, 90)))),
    ('Archivist', dict(fur=(80, 70, 66), outfit='scholar', hat=False)),
    ('Tunnelsmith', dict(outfit='smith', hat=False)),
    ('Golden', dict(fur=(200, 160, 90), outfit='merchant', hat=False, eyes=None)),
    ('Undermarshal', dict(outfit='tactician', hat=True)),
    ('Burrowguard', dict(outfit='guardian', hat=True, outfit_kw=dict(cape=False))),
    ('Mudcaller', dict(fur=(90, 70, 50), outfit='earth_mage', hat=False)),
    ('Grub', dict(fur=(110, 100, 110), outfit='peasant', hat=True)),
    ('Blindseer', dict(fur=(40, 36, 46), outfit='psychic', hat=False, eyes=None)),
    ('Prospector', dict(outfit='gunslinger', hat=True)),
]

# --- Batfolk ---------------------------------------------------------------------------------

def bat(fur, membrane=None, **kw):
    membrane = membrane or shade(fur, 0.7)
    ex = kw.pop('extras', None)
    def extras(m):
        X.bat_wings(m, membrane, frame=shade(membrane, 0.65), depth=kw.pop('_depth', 7), reach=2)
        if ex:
            ex(m)
    d = dict(muzzle=dict(length=1, w=3, h=2, nose_color=shade(fur, 0.6), nose_width=3), ears='bat', ear_inner=shade(fur, 1.3),
             eyes='dot', teeth='fangs', head=dict(w=9, d=8, h=7, style='round'), extras=extras, iris='black')
    d.update(kw)
    return furry(fur, **d)


def leaf_nose(m):
    tip, half, z, hgt, ln = m.snout_info
    for dz in (2, 3):
        m.set((16, tip, z + dz), shade(m.skin, 0.75), 'skin', 'Head', 'head')
    m.set((15, tip, z + 2), shade(m.skin, 0.75), 'skin', 'Head', 'head'); m.set((17, tip, z + 2), shade(m.skin, 0.75), 'skin', 'Head', 'head')


def fox_face(m):
    tip, half, z, hgt, ln = m.snout_info


BAT = [
    ('Vampire', dict(fur=(80, 70, 70), membrane=(60, 40, 50), outfit='necromancer', hat=False, iris='red', eyes='glow')),
    ('FlyingFox', dict(fur=(150, 100, 50), membrane=(70, 50, 40), head_color=(200, 140, 70), muzzle=dict(length=3, w=3, h=2, taper=1,
                       nose_color=(40, 30, 30), nose_width=1), ears='cat', outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('Leafnose', dict(fur=(110, 90, 80), extras=leaf_nose, outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Ghost', dict(fur=(230, 226, 224), membrane=(200, 190, 196), outfit='white_mage', hat=False, eyes='pupil', iris='red')),
    ('Hoary', dict(fur=(170, 150, 130), membrane=(110, 90, 80), outfit='hunter', hat=False)),
    ('Duskwing', dict(fur=(60, 56, 80), membrane=(90, 60, 110), outfit='psychic', hat=False, iris='violet', eyes='glow')),
    ('Nightscout', dict(fur=(50, 46, 46), membrane=(40, 36, 40), outfit='sharpshooter', hat=False)),
    ('Fruitbat', dict(fur=(130, 90, 60), membrane=(90, 60, 40), head_color=(220, 170, 90), muzzle=dict(length=2, w=3, h=2, taper=0,
                      nose_color=(40, 30, 30), nose_width=1), ears='round', outfit='peasant', hat=True, eyes='big', eye_h=3)),
    ('Longear', dict(fur=(140, 110, 90), membrane=(100, 76, 60), ears='rabbit', ear_inner=(200, 150, 140), outfit='bard', hat=False)),
    ('Echo', dict(fur=(90, 80, 76), outfit='apothecary', hat='goggles')),
    ('Belfry', dict(fur=(70, 64, 60), membrane=(50, 44, 46), outfit='cleric', hat=False)),
    ('Wingblade', dict(fur=(110, 50, 50), membrane=(70, 30, 30), outfit='assault', hat=False, eyes='angry', iris='amber')),
]

# --- Hedgehog, armadillo, otter, badger -----------------------------------------------------

def hedgehog(spine=(120, 90, 60), face=(230, 210, 180), **kw):
    ex = kw.pop('extras', None)
    tip = kw.pop('tip', (240, 230, 210))
    density = kw.pop('density', 0.55)
    def extras(m):
        X.spines(m, spine, tip=tip, length=3, density=density, head=True, back=True, seed=kw.pop('_seed', 2))
        if ex:
            ex(m)
    d = dict(muzzle=dict(length=2, w=3, h=2, taper=1, nose_color=BLACK_NOSE, nose_width=1, color=face), ears='round', ear_color=face,
             eyes='dot', head=dict(w=9, d=8, h=7, style='round'), head_color=face, belly=face, extras=extras, hands=True, hand_color=(200, 170, 150))
    d.update(kw)
    return furry(face, **d)


HEDGEHOG = [
    ('Quillback', dict(outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('Albino', dict(spine=(236, 230, 220), tip=(255, 255, 250), face=(250, 236, 230), iris='red', eyes='pupil', outfit='white_mage', hat=False)),
    ('Desert', dict(spine=(170, 130, 80), face=(240, 220, 190), ears='mouse', ear_inner=PINK, outfit='merchant', hat=False)),
    ('Brambleguard', dict(spine=(90, 70, 50), outfit='guardian', hat=False, outfit_kw=dict(cape=False, emblem='diamond'))),
    ('Pricklemonk', dict(spine=(130, 100, 70), outfit='monk', hat=False)),
    ('Thornbrute', dict(spine=(70, 60, 50), tip=(200, 190, 170), outfit='barbarian', hat=False, eyes='angry', outfit_kw=dict(paint=False))),
    ('Hedgemage', dict(spine=(100, 80, 60), outfit='nature_mage', hat=False)),
    ('Tinker', dict(spine=(140, 110, 80), outfit='apothecary', hat='goggles')),
    ('Duelist', dict(spine=(80, 60, 50), outfit='bard', hat=True)),
    ('Pincushion', dict(spine=(160, 120, 90), density=0.75, outfit='peasant', hat=False)),
    ('Gunner', dict(spine=(110, 90, 70), outfit='sharpshooter', hat=False)),
    ('Commodore', dict(spine=(120, 96, 70), outfit='tactician', hat=True)),
]


def armadillo(skin=(190, 160, 150), band=None, **kw):
    ex = kw.pop('extras', None)
    shell = kw.pop('shell', shade(skin, 0.85))
    band = band or shade(shell, 0.78)
    def extras(m):
        X.armadillo_bands(m, shell, band=band)
        hd = m.head
        for x in range(hd.x0 + 1, hd.x1):
            for y in range(hd.y0 + 1, hd.y1):
                m.set((x, y, hd.z1 + 1), shell if (x + y) % 2 else band, 'shell', 'Head', 'head')
        if ex:
            ex(m)
    d = dict(muzzle=dict(length=3, w=3, h=2, taper=1, nose_color=shade(skin, 0.6), nose_width=1), ears='dog_pointed', ear_inner=shade(skin, 0.8),
             eyes='bead', tail='ringed', tail_color=shell, tail_tip=band, tail_second=band, head=dict(w=9, d=8, h=7, style='soft'),
             extras=extras, group='skin', hands='claws', hand_color=(230, 220, 200))
    d.update(kw)
    return furry(skin, **d)


ARMADILLO = [
    ('ThreeBand', dict(outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('PinkFairy', dict(skin=(250, 236, 230), shell=(240, 170, 180), outfit='white_mage', hat=False)),
    ('Giant', dict(skin=(150, 130, 110), shell=(120, 100, 80), outfit='heavy', hat=False)),
    ('Nine', dict(skin=(180, 160, 140), outfit='gunslinger', hat=True)),
    ('Rollguard', dict(skin=(170, 150, 130), outfit='guardian', hat=False, outfit_kw=dict(cape=False))),
    ('Hairy', dict(skin=(170, 140, 110), pattern=lambda m: X.mottle(m, [(140, 110, 80), (200, 180, 150)], density=0.4), outfit='hunter', hat=True)),
    ('Dunerunner', dict(skin=(210, 180, 140), outfit='merchant', hat=False)),
    ('Plated', dict(skin=(160, 150, 140), shell=(150, 154, 160), outfit='assault', hat=False)),
    ('Burrowmonk', dict(skin=(190, 170, 150), outfit='monk', hat=False)),
    ('Shellsage', dict(skin=(180, 160, 140), outfit='scholar', hat=False)),
    ('Tunneler', dict(skin=(170, 150, 130), outfit='miner', hat=True)),
    ('Earthshaker', dict(skin=(150, 120, 90), outfit='earth_mage', hat=False)),
]


def otter(fur=(110, 76, 50), face=(220, 200, 170), **kw):
    d = dict(muzzle=dict(length=2, w=5, h=2, taper=1, nose_color=BLACK_NOSE, nose_width=1, color=face), ears='round', eyes='dot',
             tail='otter', head=dict(w=9, d=8, h=7, style='round'), belly=face, whiskers=(230, 220, 210), feet='webbed', feet_color=shade(fur, 0.8))
    d.update(kw)
    return furry(fur, **d)


OTTER = [
    ('River', dict(outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('Sea', dict(fur=(90, 70, 56), face=(230, 220, 200), head_color=(200, 190, 170), outfit='sailor', hat=True)),
    ('Giant', dict(fur=(80, 56, 40), face=(200, 180, 150), outfit='warrior', hat=False)),
    ('Corsair', dict(fur=(120, 84, 56), outfit='pirate', hat=True)),
    ('Brookmonk', dict(fur=(130, 96, 66), outfit='monk', hat=False)),
    ('Tidecaller', dict(fur=(100, 80, 60), outfit='water_mage', hat=False)),
    ('Smooth', dict(fur=(150, 110, 70), outfit='bard', hat=True)),
    ('Clawless', dict(fur=(110, 90, 70), face=(240, 230, 210), outfit='merchant', hat=True)),
    ('Netcaster', dict(fur=(100, 76, 56), outfit='hunter', hat=True)),
    ('Riverguard', dict(fur=(90, 70, 50), outfit='guardian', hat=False, outfit_kw=dict(cape=False, emblem='chevron', second=(40, 90, 120)))),
    ('Skipper', dict(fur=(130, 90, 60), outfit='tactician', hat=True, outfit_kw=dict(main=(40, 60, 100)))),
    ('Diver', dict(fur=(80, 64, 50), outfit='rogue', hat=False, extras=lambda m: H.hat(m, m.head, 'goggles', (100, 80, 60), trim=(60, 50, 40),
                                                                                         extra=(150, 220, 230)))),
]


def badger_face(m):
    """A badger's white stripe down the middle of a black face, white cheeks."""
    hd = m.head
    for p, v in m.v.items():
        if v.part != 'head' or v.group not in ('fur',):
            continue
        x, y, z = p
        if x in (15, 16, 17) and (y <= hd.y0 + 1 or z >= hd.z1 - 1):
            v.color = (240, 238, 232)
        elif x in (13, 14, 18, 19) and y <= hd.y0 + 6 and z >= hd.z0 + 2:
            v.color = (36, 34, 36)
        elif z < hd.z0 + 2 and y <= hd.y0 + 2:
            v.color = (240, 238, 232)


def badger(fur=(130, 128, 130), **kw):
    ex = kw.pop('extras', None)
    face_fn = kw.pop('face_fn', badger_face)
    def extras(m):
        if ex:
            ex(m)
    d = dict(muzzle=dict(length=2, w=3, h=2, taper=0, nose_color=BLACK_NOSE, nose_width=3, color=(240, 238, 232)), ears='round',
             ear_color=(36, 34, 36), eyes='dot', iris='black', head=dict(w=9, d=8, h=7, style='base'), tail='stub', tail_color=fur,
             hands='claws', hand_color=(220, 210, 190), pattern=lambda m: (face_fn(m), m.paint((40, 38, 40), None, parts=('uleg_r', 'lleg_r', 'uleg_l', 'lleg_l', 'larm_r', 'larm_l', 'hand_r', 'hand_l'),
                                                                                              where=lambda p, v: v.group == m.skin_group)),
             extras=extras)
    d.update(kw)
    return furry(fur, **d)


def honey_face(m):
    hd = m.head
    for p, v in m.v.items():
        if v.part == 'head' and v.group == 'fur':
            v.color = (240, 238, 232) if p[2] >= hd.z0 + 5 or p[1] >= hd.y1 - 1 else (36, 34, 36)


BADGER = [
    ('Brock', dict(outfit='warrior', hat=False)),
    ('Honey', dict(fur=(40, 38, 40), face_fn=honey_face, pattern=None, outfit='barbarian', hat=False, eyes='angry', outfit_kw=dict(paint=False),
                   extras=lambda m: (honey_face(m), m.paint((220, 220, 214), None, parts=('chest', 'spine', 'hips', 'uarm_r', 'uarm_l'),
                                                            where=lambda p, v: p[1] >= 17 and v.group == m.skin_group)))),
    ('Settwarden', dict(outfit='guardian', hat=False, outfit_kw=dict(cape=False, emblem='tower'))),
    ('American', dict(fur=(170, 150, 120), outfit='gunslinger', hat=True)),
    ('Delver', dict(outfit='miner', hat=True)),
    ('Smith', dict(outfit='smith', hat=False)),
    ('Hog', dict(fur=(150, 140, 130), muzzle=dict(length=3, w=3, h=2, taper=0, nose_color=(230, 150, 160), nose_width=3, color=(240, 238, 232)),
                 outfit='peasant', hat=True)),
    ('Stinkstripe', dict(fur=(40, 38, 40), outfit='rogue', hat=False, tail='fox', tail_color=(40, 38, 40), tail_tip=(240, 238, 232))),
    ('Burrowlord', dict(outfit='noble', hat=False, extras=lambda m: H.hat(m, m.head, 'crown', (222, 184, 72), extra=(150, 40, 60)))),
    ('Ironclaw', dict(outfit='heavy', hat=False)),
    ('Colonel', dict(outfit='tactician', hat=True)),
    ('Earthwarden', dict(outfit='earth_mage', hat=False)),
]


def bat_concept(kind):
    fur = (80, 70, 70) if kind != 'fox' else (150, 100, 50)
    m = F.body(fur, 'fur', leg=7, leg_w=2, leg_d=2, gap=1, torso_w=7, torso_d=4, torso_h=8, arm_len=12, arm_w=2, arm_d=2, arm_pose='t',
               head=dict(w=9, d=8, h=7, style='round'), neck=1)
    hd = m.head
    H.snout(m, hd, shade(fur, 1.1) if kind != 'fox' else (200, 140, 70), length=1 if kind != 'fox' else 3, w=3, h=2, taper=0,
            nose_color=(40, 30, 30), nose_width=1)
    H.eyes(m, hd, 'dot', iris=(30, 30, 30))
    H.ears(m, hd, 'bat' if kind != 'fox' else 'cat', fur, inner=shade(fur, 1.3))
    b = m.body
    membrane = (60, 40, 50) if kind != 'fox' else (70, 50, 40)
    # wings: from each arm's length down to the legs, fingers spread past the hands
    for side, sgn in (('r', -1), ('l', 1)):
        cells = b.arms[side]
        xs = sorted({p[0] for p, k in cells}, key=lambda x: sgn * x)
        tip = xs[-1]
        for x in range(16 + sgn * 4, tip + sgn * 6, sgn):
            reach = abs(x - 16)
            top = b.top - 1
            bottom = max(2, b.top - 14 + reach // 2 + (3 if reach % 4 == 1 else 0))
            for z in range(bottom, top + 1):
                rib = (reach % 4 == 3)
                m.set((x, b.cy, z), shade(membrane, 0.65) if rib else membrane, 'skin')
        for k in range(1, 6):
            m.set((tip + sgn * k, b.cy, b.top - 1 + (k // 3)), shade(membrane, 0.6), 'skin')
    F.dress(m, belt=(60, 40, 30), buckle=(200, 200, 210), trousers=(50, 40, 50) if kind != 'fox' else None)
    return m


SETS = [
    Set('Rodent', 'Rodent', designs(mouse, RODENT), treat3(1, 2, 11)),
    Set('Rodent/Rat', 'Rodent_Rat', designs(rat, RAT), treat3(1, 4, 3)),
    Set('Rodent/Hamster', 'Rodent_Hamster', designs(hamster_cheeked, HAMSTER), treat3(1, 2, 3)),
    Set('Rodent/Beaver', 'Rodent_Beaver', designs(beaver, BEAVER), treat3(1, 2, 5)),
    Set('Rodent/Rabbit', 'Rodent_Rabbit', designs(rabbit, RABBIT), treat3(2, 1, 5), concepts=[('Hare', lambda: CX.hare())]),
    Set('Rodent/Squirrel', 'Rodent_Squirrel', designs(squirrel, SQUIRREL), treat3(1, 2, 4)),
    Set('Rodent/Mole', 'Rodent_Mole', designs(mole, MOLE), treat3(1, 2, 3)),
    Set('Batfolk', 'Batfolk', designs(bat, BAT), treat3(1, 2, 3),
        concepts=[('Nightwing', lambda: bat_concept('bat')), ('FlyingFox', lambda: bat_concept('fox'))]),
    Set('Hedgehog', 'Hedgehog', designs(hedgehog, HEDGEHOG), treat3(1, 2, 4)),
    Set('Armadillo', 'Armadillo', designs(armadillo, ARMADILLO), treat3(1, 2, 3)),
    Set('Otter', 'Otter', designs(otter, OTTER), treat3(1, 2, 4)),
    Set('Badger', 'Badger', designs(badger, BADGER), treat3(1, 2, 4)),
]
