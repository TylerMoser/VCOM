"""Folk of the water: fishfolk, crabfolk, sharkfolk (hammerheads among them), frogfolk
(generic, poison, toad, regular) and snailfolk."""
from .common import Set, designs, beast, EYES
from .mammals import treat3
from . import concepts_extra as CX
from .lizards import side_eyes
from core import shade, mix, sat
import heads as H
import outfits as O
import extras as X
import freebody as F

WHITE = (240, 238, 232)
GLOW = ('emit', 0.95, 1)

# --- Fishfolk --------------------------------------------------------------------------------

def fish_eyes(m, hd, iris=(240, 200, 60), pupil=(28, 26, 30), big=True):
    """Round eyes on the head's sides, bulging a voxel, seen from the front too."""
    z = hd.z0 + 3
    for side in (-1, 1):
        x = (hd.x0 - 1) if side < 0 else (hd.x1 + 1)
        cells = [(x, hd.y0 + 1, z), (x, hd.y0 + 2, z), (x, hd.y0 + 1, z + 1), (x, hd.y0 + 2, z + 1)]
        if big:
            cells += [(x, hd.y0 + 1, z + 2), (x, hd.y0 + 2, z + 2), (x, hd.y0 + 3, z + 1)]
        for c in cells:
            m.set(c, iris, 'eye', 'Head', 'head')
        m.set((x + side, hd.y0 + 1, z + 1), pupil, 'eye', 'Head', 'head')
        m.set((x + side, hd.y0 + 2, z + 1), pupil, 'eye', 'Head', 'head')
        m.set((x, hd.y0, z + 1), pupil, 'eye', 'Head', 'head')


def fish_mouth(m, hd, color=(150, 60, 70), style='o', teeth=None):
    """o (a round open mouth), wide (a long line), under (a jutting lower jaw with teeth)."""
    y = m.front_y(16, hd.z0 + 1)
    if style == 'o':
        for (x, z) in ((15, hd.z0), (16, hd.z0), (17, hd.z0), (15, hd.z0 + 1), (17, hd.z0 + 1), (16, hd.z0 + 2), (15, hd.z0 + 2), (17, hd.z0 + 2)):
            m.set((x, hd.y0 - 1, z), shade(m.skin, 1.12), m.skin_group, 'Head', 'head')
        m.set((16, hd.y0 - 1, hd.z0 + 1), color, 'mouth', 'Head', 'head')
    elif style == 'wide':
        for x in range(hd.x0 + 1, hd.x1):
            yy = m.front_y(x, hd.z0 + 1)
            m.set((x, yy, hd.z0 + 1), color, 'mouth', 'Head', 'head')
    elif style == 'under':
        for x in range(hd.x0 + 1, hd.x1):
            m.set((x, hd.y0 - 1, hd.z0), shade(m.skin, 0.9), m.skin_group, 'Head', 'head')
            if teeth and x % 2 == 0:
                m.set((x, hd.y0 - 1, hd.z0 + 1), teeth, 'bone', 'Head', 'head')
            yy = m.front_y(x, hd.z0 + 1)
            if not (teeth and x % 2 == 0):
                m.set((x, yy, hd.z0 + 1), color, 'mouth', 'Head', 'head')


def dorsal(color, tip=None, spiky=False):
    def f(m):
        hd = m.head
        tip_c = tip or shade(color, 0.75)
        for i, y in enumerate(range(hd.y0 + 1, hd.y1 + 2)):
            hgt = 3 if 1 <= i <= 5 else 2
            for k in range(1, hgt + 1):
                c = tip_c if k == hgt else color
                if spiky and k == hgt and i % 2:
                    continue
                m.set((16, y, hd.z1 + k), c, 'skin', 'Head', 'head')
        for z in range(10, 19):
            hgt = 2 if 12 <= z <= 16 else 1
            for k in range(hgt):
                m.set((16, 18 + k, z), tip_c if k == hgt - 1 else color, 'skin', 'Chest')
    return f


def lure(m, color=(150, 255, 200)):
    hd = m.head
    pts = [(16, hd.y0 + 1, hd.z1 + 1), (16, hd.y0, hd.z1 + 3), (16, hd.y0 - 2, hd.z1 + 4), (16, hd.y0 - 4, hd.z1 + 3)]
    X.sweep(m, [(x, y, z, .55, .55, .55) for x, y, z in pts], shade(m.skin, 0.9), 'skin', 'Head')
    m.ellipsoid(16, hd.y0 - 4.5, hd.z1 + 2, 1.1, 1.1, 1.1, color, 'light', 'Head', 'head', mat=GLOW)


def barbels(m, color):
    hd = m.head
    for side in (-1, 1):
        for k in range(1, 5):
            m.set((16 + side * (2 + k // 2), hd.y0 - 1 - (k > 2), hd.z0 + 1 - k // 2), color, 'skin', 'Head', 'head')


def bill(m, color=(60, 70, 90)):
    hd = m.head
    for k in range(1, 8):
        m.set((16, hd.y0 - k, hd.z0 + 2), color, 'bone', 'Head', 'head')
        if k < 3:
            m.set((16, hd.y0 - k, hd.z0 + 3), color, 'bone', 'Head', 'head')


def bands_white(m, edge=(30, 30, 30)):
    for p, v in m.v.items():
        if v.group == m.skin_group:
            k = p[2] % 6 if v.part != 'head' else (p[1] - m.head.y0) % 5
            if k == 0:
                v.color = WHITE
            elif k == 1 and v.part != 'head':
                v.color = edge
    hd = m.head
    for p, v in m.v.items():
        if v.part == 'head' and v.group == m.skin_group and p[1] == hd.y0 + 3:
            v.color = WHITE


def puff(m):
    hd = m.head
    X.spines(m, shade(m.skin, 0.8), tip=(240, 230, 200), length=2, density=0.35, head=True, back=False, seed=19)


def lion_fins(m):
    for p, v in m.v.items():
        if v.group == m.skin_group and (p[2] + p[0]) % 3 == 0:
            v.color = WHITE
    X.spines(m, (200, 60, 50), tip=WHITE, length=3, density=0.35, head=True, back=True, seed=23)


def fish(skin=(220, 120, 50), belly=None, head=None, iris=(240, 200, 60), mouth='o', teeth=None, fin=None, fin_tip=None,
         tail='fish', tail_color=None, tail_tip=None, pattern=None, outfit=None, outfit_kw=None, hat=False, extras=None, arm_fin=True,
         head_color=None, spiky=False, big_eyes=True):
    head = head or dict(w=9, d=9, h=8, style='round')
    fin = fin or shade(skin, 0.85)
    def face(m, hd):
        m.head_skin = head_color or skin
        fish_eyes(m, hd, iris=iris, big=big_eyes)
        fish_mouth(m, hd, style=mouth, teeth=teeth)
        X.gills(m, shade(head_color or skin, 0.7))
    def pat(m):
        if pattern:
            pattern(m)
        dorsal(fin, fin_tip, spiky)(m)
    def after(m):
        if arm_fin:
            X.arm_fins(m, fin)
        if extras:
            extras(m)
    return beast(skin, skin_group='scale', head=head, eyes=None, face=face, pattern=pat, belly_color=belly, tail=tail,
                 tail_color=tail_color or skin, tail_tip=tail_tip or fin, outfit=outfit, outfit_kw=outfit_kw, hat=hat, extras=after,
                 head_color=head_color, feet='webbed', feet_color=fin, hands=True, hand_color=shade(skin, 0.9))


def koi(m):
    for p, v in m.v.items():
        if v.group == m.skin_group and X.h((p[0] // 3, p[1] // 3, p[2] // 3), 61) < 0.5:
            v.color = (230, 90, 40) if X.h((p[0] // 3, 1, p[2] // 3), 62) < 0.75 else (40, 36, 36)


FISH = [
    ('Koi', dict(skin=WHITE, pattern=koi, fin=(240, 150, 100), extras=lambda m: barbels(m, (230, 200, 180)), outfit='monk', hat=False,
                 outfit_kw=dict(main=(40, 60, 110), trim=(222, 184, 72)))),
    ('Goldfish', dict(skin=(240, 140, 40), belly=(250, 200, 120), fin=(250, 170, 80), outfit='bard', hat=True, iris=(250, 250, 250))),
    ('Clownfish', dict(skin=(240, 120, 30), pattern=bands_white, fin=(240, 120, 30), fin_tip=(30, 30, 30), outfit='peasant', hat=False)),
    ('Piranha', dict(skin=(140, 150, 160), belly=(220, 60, 50), mouth='under', teeth=WHITE, iris=(220, 40, 40), outfit='assault', hat=False)),
    ('Angler', dict(skin=(60, 56, 64), mouth='under', teeth=(230, 230, 220), extras=lure, iris=(200, 200, 220), outfit='necromancer', hat=False,
                    outfit_kw=dict(accent=(150, 255, 200)))),
    ('Puffer', dict(skin=(210, 190, 120), belly=(240, 236, 220), head=dict(w=11, d=9, h=9, style='round'), extras=puff,
                    pattern=lambda m: X.spots(m, (110, 90, 60), density=0.15), outfit='merchant', hat=False)),
    ('Lionfish', dict(skin=(210, 70, 50), pattern=lion_fins, fin=(220, 90, 70), outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Swordfish', dict(skin=(60, 90, 150), belly=(210, 220, 230), extras=bill, fin=(50, 70, 120), outfit='gladiator', hat=False)),
    ('Catfish', dict(skin=(110, 100, 80), belly=(200, 190, 160), head=dict(w=11, d=9, h=7, style='round'), mouth='wide', big_eyes=False,
                     extras=lambda m: barbels(m, (90, 80, 60)), outfit='smith', hat=False)),
    ('Salmon', dict(skin=(170, 176, 186), belly=(240, 160, 140), pattern=lambda m: X.spots(m, (60, 60, 70), density=0.1), fin=(140, 150, 160),
                    outfit='hunter', hat=False)),
    ('Betta', dict(skin=(60, 60, 200), fin=(150, 60, 200), fin_tip=(220, 80, 160), tail='fox', tail_color=(120, 60, 200), tail_tip=(220, 80, 160),
                   outfit='noble', hat=False, outfit_kw=dict(main=(60, 40, 120)))),
    ('Tuna', dict(skin=(40, 60, 100), belly=(200, 210, 220), fin=(240, 210, 60), outfit='sailor', hat=True)),
    ('Blobfish', dict(skin=(240, 180, 180), head=dict(w=11, d=9, h=8, style='round'), mouth='wide', big_eyes=False, arm_fin=False,
                      extras=lambda m: m.ellipsoid(16, m.head.y0 - 1, m.head.z0 + 2.5, 1.8, 1.2, 1.4, (230, 160, 160), 'scale', 'Head', 'head', only_empty=True),
                      outfit='scholar', hat=False)),
    ('Moray', dict(skin=(80, 120, 50), head=dict(w=7, d=10, h=7, style='soft'), mouth='under', teeth=WHITE, big_eyes=False,
                   pattern=lambda m: X.spots(m, (40, 60, 30), density=0.25), outfit='pirate', hat=True, tail='snake', tail_color=(80, 120, 50))),
    ('Tang', dict(skin=(40, 90, 200), fin=(240, 210, 40), tail_color=(240, 210, 40), pattern=lambda m: X.stripes(m, (20, 30, 80), period=5, head=False),
                  outfit='water_mage', hat=False)),
]

# --- Crabfolk --------------------------------------------------------------------------------

def carapace(color, rim=None, spikes=None):
    """The shell over the back (on the chest) and a plate in front, wider at the shoulders."""
    rim = rim or shade(color, 0.75)
    def f(m):
        for x in range(10, 23):
            for y in (18, 19, 20):
                for z in range(11, 20):
                    d = ((x + 0.5 - 16.5) / 6.6) ** 2 + ((z + 0.5 - 15.5) / 4.8) ** 2
                    if d > 1 or (y == 18 and not 14 <= x <= 18) or X.arm_room((x, y, z)):
                        continue
                    if y == 20 and d > 0.7:
                        continue
                    c = rim if d > 0.78 else color
                    m.set((x, y, z), c, 'chitin', 'Chest')
        for x in range(14, 19):
            for z in range(10, 18):
                m.set((x, 14, z), color if z not in (10, 13) else rim, 'chitin', None)
        if spikes:
            for (x, z) in ((12, 18), (20, 18), (14, 19), (18, 19), (16, 17)):
                yb = m.back_y(x, z)
                if yb:
                    m.set((x, yb + 1, z), spikes, 'chitin', 'Chest')
    return f


def crab_legs(color, joint=None, pairs=2):
    def f(m):
        X.spider_legs(m, color, joint=joint or shade(color, 0.75), pairs=pairs)
    return f


def big_claw(color, tip=None, side='l'):
    """One great claw, a fiddler crab's, in place of one hand."""
    tip = tip or shade(color, 0.7)
    def f(m):
        bone = 'LeftHand' if side == 'l' else 'RightHand'
        xs = range(27, 31) if side == 'l' else range(2, 6)
        for x in xs:
            for y in range(13, 20):
                for z in (17, 18, 19, 20):
                    if z == 17 and y in (13, 19):
                        continue
                    m.set((x, y, z), color, 'chitin', bone)
        out = 31 if side == 'l' else 1
        # the claw's two fingers: the fixed one below, the moving one above, opening outward
        for y in (13, 14, 15, 16):
            m.set((out, y, 21), tip if y == 13 else color, 'chitin', bone)
            m.set((out, y, 17), tip if y == 13 else color, 'chitin', bone)
        for y in (13, 14):
            m.set((out, y, 22), tip, 'chitin', bone)
    return f


def crab(shell=(200, 60, 40), skin=None, head=None, iris=(30, 28, 30), claw=None, claw_tip=None, pattern=None, outfit=None,
         outfit_kw=None, hat=False, extras=None, legs=True, spikes=None, antennae=None, fiddler=None, rim=None):
    skin = skin or shade(shell, 1.1)
    head = head or dict(w=9, d=7, h=6, style='soft')
    def face(m, hd):
        X.eye_stalks(m, shade(shell, 0.9), eye=iris, white=(30, 28, 30) if iris == (30, 28, 30) else WHITE, height=2, spread=2)
        for x in range(14, 19):
            m.set((x, hd.y0 - 1, hd.z0), shade(shell, 0.7), 'chitin', 'Head', 'head')
        m.set((15, hd.y0 - 1, hd.z0 + 1), shade(shell, 0.6), 'chitin', 'Head', 'head')
        m.set((17, hd.y0 - 1, hd.z0 + 1), shade(shell, 0.6), 'chitin', 'Head', 'head')
        if antennae:
            X.antennae(m, antennae, 'long', length=6)
    def pat(m):
        if pattern:
            pattern(m)
    def after(m):
        carapace(shell, rim=rim, spikes=spikes)(m)
        if fiddler:
            big_claw(claw or shell, claw_tip, side=fiddler)(m)
        else:
            X.pincers(m, claw or shell, tip=claw_tip)
        if legs:
            crab_legs(shade(shell, 0.9))(m)
        if extras:
            extras(m)
    return beast(skin, skin_group='chitin', head=head, head_color=shell, eyes=None, face=face, pattern=pat, outfit=outfit,
                 outfit_kw=outfit_kw, hat=hat, extras=after)


def lobster_tail(color):
    def f(m):
        for i in range(6):
            for x in range(15 - (i > 3), 18 + (i > 3)):
                m.set((x, 18 + i, 9 - i // 2), color if i % 2 else shade(color, 0.85), 'chitin', 'Hips')
        for x in range(13, 20):
            m.set((x, 24, 6), shade(color, 0.8), 'chitin', 'Hips')
            m.set((x, 25, 5), shade(color, 0.7), 'chitin', 'Hips')
    return f


def hermit(color, stripe):
    def f(m):
        X.hermit_shell(m, color, stripe)
    return f


CRABS = [
    ('RedRock', dict(shell=(200, 60, 40), outfit='warrior', hat=False)),
    ('BlueClaw', dict(shell=(80, 120, 170), claw=(90, 140, 200), claw_tip=(220, 70, 50), outfit='sailor', hat=True)),
    ('Shore', dict(shell=(80, 120, 60), outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('Fiddler', dict(shell=(70, 60, 80), claw=(240, 200, 60), fiddler='l', outfit='bard', hat=True)),
    ('Hermit', dict(shell=(220, 120, 70), legs=False, extras=hermit((230, 200, 160), (170, 110, 80)), outfit='monk', hat=False)),
    ('KingCrab', dict(shell=(180, 50, 40), spikes=(230, 200, 180), outfit='noble', hat=False, outfit_kw=dict(cape=False, main=(120, 30, 40)),
                      extras=lambda m: H.hat(m, m.head, 'crown', (222, 184, 72), extra=(60, 160, 220)))),
    ('Coconut', dict(shell=(80, 70, 140), claw=(110, 90, 170), outfit='heavy', hat=False)),
    ('Spider', dict(shell=(200, 150, 90), spikes=(220, 190, 140), outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Lobster', dict(shell=(160, 40, 30), antennae=(200, 60, 40), legs=True, extras=lobster_tail((170, 50, 36)), outfit='pirate', hat=True)),
    ('Crayfish', dict(shell=(110, 70, 50), antennae=(140, 90, 60), extras=lobster_tail((120, 80, 56)), outfit='hunter', hat=True)),
    ('Ghost', dict(shell=(230, 220, 200), iris=(30, 28, 30), outfit='white_mage', hat=False)),
    ('Sally', dict(shell=(220, 90, 40), pattern=lambda m: X.spots(m, (60, 120, 200), density=0.2), claw=(220, 90, 40), outfit='gunslinger', hat=True)),
    ('Armored', dict(shell=(110, 114, 122), rim=(80, 84, 90), outfit='guardian', hat=False, outfit_kw=dict(cape=False))),
]

# --- Sharkfolk -------------------------------------------------------------------------------

def shark_snout(m, hd, color, belly, length=3, teeth=WHITE, wide=7):
    for k in range(1, length + 1):
        half = max(1, wide // 2 - (k * 2) // max(1, length))
        for x in range(16 - half, 17 + half):
            for z in range(hd.z0 + 1, hd.z0 + 4 - (k > length - 1)):
                m.set((x, hd.y0 - k, z), color, 'skin', 'Head', 'head')
            m.set((x, hd.y0 - k, hd.z0), belly, 'skin', 'Head', 'head')
    # the mouth under the snout, a row of teeth along it
    for x in range(hd.x0 + 1, hd.x1):
        y = m.front_y(x, hd.z0 + 1)
        m.set((x, hd.y0, hd.z0 + 1) if y is None else (x, max(y, hd.y0 - 1), hd.z0 + 1), (60, 30, 40), 'mouth', 'Head', 'head')
        if teeth and x % 2 == 0:
            m.set((x, hd.y0 - 1, hd.z0 + 1), teeth, 'bone', 'Head', 'head')
    m.snout_info = (hd.y0 - length, 1, hd.z0, 3, length)


def shark(skin=(110, 120, 140), belly=WHITE, head=None, iris=(30, 28, 30), snout=3, hammer=None, fin_color=None, pattern=None,
          outfit=None, outfit_kw=None, hat=False, extras=None, tail='shark', fin_height=6, tip=None, teeth=WHITE):
    head = head or dict(w=9, d=9, h=7, style='soft')
    def face(m, hd):
        m.head_skin = skin
        if hammer:
            hammerhead(m, hd, skin, belly, iris, width=hammer)
        else:
            shark_snout(m, hd, skin, belly, snout, teeth=teeth)
            side_eyes(m, hd, iris, z=hd.z0 + 3, style='dot')
        X.gills(m, shade(skin, 0.6))
    def pat(m):
        m.paint(belly, None, parts=('chest', 'spine', 'hips', 'neck'), where=lambda p, v: p[1] == 15 and v.group == 'skin')
        hd = m.head
        m.paint(belly, None, where=lambda p, v: v.part == 'head' and v.group == 'skin' and p[2] == hd.z0)
        if pattern:
            pattern(m)
    def after(m):
        X.dorsal_fin(m, fin_color or shade(skin, 0.95), tip=tip or shade(skin, 0.75), height=fin_height)
        X.arm_fins(m, fin_color or shade(skin, 0.9))
        if extras:
            extras(m)
    return beast(skin, skin_group='skin', head=head, eyes=None, face=face, pattern=pat, tail=tail, tail_color=skin,
                 tail_tip=tip or shade(skin, 0.75), outfit=outfit, outfit_kw=outfit_kw, hat=hat, extras=after, feet='webbed',
                 feet_color=shade(skin, 0.85))


def hammerhead(m, hd, skin, belly, iris, width=5):
    """The hammer: a flat bar across the front of the head, an eye at each end."""
    z0 = hd.z0 + 2
    for x in range(16 - width - 3, 17 + width + 3):
        for y in range(hd.y0 - 2, hd.y0 + 2):
            for z in (z0, z0 + 1, z0 + 2):
                if z == z0 + 2 and abs(x - 16) > width + 1:
                    continue
                m.set((x, y, z), skin if z > z0 else belly, 'skin', 'Head', 'head')
    for side in (-1, 1):
        x = 16 + side * (width + 3)
        m.set((x, hd.y0 - 1, z0 + 1), iris, 'eye', 'Head', 'head')
        m.set((x, hd.y0, z0 + 1), iris, 'eye', 'Head', 'head')
        m.set((x, hd.y0 - 2, z0 + 1), (230, 220, 160), 'eye', 'Head', 'head')
    for x in range(hd.x0 + 1, hd.x1):
        m.set((x, hd.y0 - 1, hd.z0 + 1), (60, 30, 40), 'mouth', 'Head', 'head')
        if x % 2 == 0:
            m.set((x, hd.y0 - 1, hd.z0), WHITE, 'bone', 'Head', 'head')
    m.snout_info = (hd.y0 - 2, 1, hd.z0, 3, 2)


def tiger_stripes(m):
    for p, v in m.v.items():
        if v.group == 'skin' and p[1] >= 16 and (p[2] + p[0] // 2) % 4 == 0:
            v.color = shade(v.color, 0.7)


SHARKS = [
    ('GreatWhite', dict(outfit='barbarian', hat=False, outfit_kw=dict(paint=False))),
    ('Hammerhead', dict(skin=(120, 130, 140), hammer=5, outfit='tactician', hat=False)),
    ('Tiger', dict(skin=(120, 120, 110), pattern=tiger_stripes, outfit='warrior', hat=False)),
    ('Mako', dict(skin=(50, 80, 150), snout=4, outfit='sharpshooter', hat=False)),
    ('WhaleShark', dict(skin=(60, 70, 90), head=dict(w=11, d=9, h=7, style='soft'), snout=1, teeth=None,
                        pattern=lambda m: X.spots(m, WHITE, density=0.15), outfit='monk', hat=False, outfit_kw=dict(main=(60, 120, 160)))),
    ('Goblin', dict(skin=(230, 170, 170), snout=5, outfit='necromancer', hat=False, iris=(60, 60, 60))),
    ('Thresher', dict(skin=(100, 100, 140), extras=lambda m: X.tail(m, 'cat', (100, 100, 140), tip=(70, 70, 110), group='skin'), tail=None,
                      outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Bull', dict(skin=(110, 110, 110), head=dict(w=11, d=9, h=7, style='soft'), snout=2, outfit='heavy', hat=False)),
    ('Blacktip', dict(skin=(150, 150, 140), tip=(30, 30, 34), outfit='assault', hat=False)),
    ('Nurse', dict(skin=(150, 120, 80), snout=1, teeth=None, extras=lambda m: barbels(m, (120, 96, 64)), outfit='support', hat=False)),
    ('Bonnethead', dict(skin=(130, 140, 140), hammer=3, outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('GreatHammer', dict(skin=(100, 110, 120), hammer=6, fin_height=8, outfit='guardian', hat=False, outfit_kw=dict(cape=False))),
    ('Megalodon', dict(skin=(70, 74, 84), head=dict(w=11, d=10, h=8, style='soft'), snout=3, outfit='pirate', hat=True)),
    ('Lemon', dict(skin=(200, 190, 110), outfit='gunslinger', hat=True)),
]

# --- Frogfolk --------------------------------------------------------------------------------

def frog_eyes(m, hd, color, iris=(230, 200, 40), pupil=(28, 26, 30), size=1.8, slit=False):
    for side in (-1, 1):
        cx = 16 + side * 3.5 + 0.5
        m.ellipsoid(cx, hd.y0 + 2.5, hd.z1 + 0.6, size, size, size, color, m.skin_group, 'Head', 'head', only_empty=True)
        x = int(cx) if side > 0 else int(cx)
        for dx in (0, 1) if size > 1.5 else (0,):
            m.set((x - (1 if side < 0 else 0) + dx * (1 if side > 0 else 0), hd.y0 + 1, hd.z1 + 1), iris, 'eye', 'Head', 'head')
        m.set((x - (1 if side < 0 else 0) + (0 if side > 0 else 1), hd.y0 + 1, hd.z1 + 1), pupil if not slit else iris, 'eye', 'Head', 'head')
        m.set((x - (1 if side < 0 else 0) + (0 if side > 0 else 1), hd.y0 + 1, hd.z1 + 2), iris, 'eye', 'Head', 'head')
        if slit:
            m.set((x, hd.y0 + 1, hd.z1 + 1), pupil, 'eye', 'Head', 'head')


def frog(skin=(80, 170, 70), belly=(220, 230, 170), head=None, iris=(230, 200, 40), mouth=(40, 90, 40), pattern=None, outfit=None,
         outfit_kw=None, hat=False, extras=None, pads=None, throat=None, warts=None, glow=False, eye_size=1.8, slit=False):
    head = head or dict(w=11, d=8, h=6, style='soft')
    def face(m, hd):
        frog_eyes(m, hd, m.skin, iris=iris, size=eye_size, slit=slit)
        H.mouth(m, hd, 'line', color=mouth, z=hd.z0 + 1, width=7)
        for x in (hd.x0 + 1, hd.x1 - 1):
            y = m.front_y(x, hd.z0 + 2)
            if y is not None:
                m.set((x, y, hd.z0 + 2), mouth, 'mouth', 'Head', 'head')
        m.set((15, hd.y0, hd.z0 + 3), shade(m.skin, 0.6), 'detail', 'Head', 'head')
        m.set((17, hd.y0, hd.z0 + 3), shade(m.skin, 0.6), 'detail', 'Head', 'head')
        if throat:
            for x in (15, 16, 17):
                m.set((x, hd.y0 + 1, 19), throat, 'skin', 'Head', 'head')
                m.set((x, hd.y0, hd.z0), throat, 'skin', 'Head', 'head')
    def pat(m):
        if pattern:
            pattern(m)
        if warts:
            X.mottle(m, warts, density=0.3, seed=71)
    def after(m):
        if pads:
            for x in (3, 29):
                for y in (15, 17):
                    m.set((x, y, 18), pads, 'skin', 'RightHand' if x < 16 else 'LeftHand')
        if extras:
            extras(m)
    m = beast(skin, skin_group='skin', head=head, eyes=None, face=face, pattern=pat, belly_color=belly, outfit=outfit,
              outfit_kw=outfit_kw, hat=hat, extras=after, feet='webbed', feet_color=pads or shade(skin, 0.85))
    if glow:
        for p, v in m.v.items():
            if v.group == 'skin' and v.color == glow[0]:
                v.mat = GLOW
                v.group = 'light'
    return m


def dart(colors, size=2, seed=7):
    def f(m):
        for p, v in m.v.items():
            if v.group == m.skin_group:
                q = (p[0] // size, p[1] // size, p[2] // size)
                v.color = colors[int(X.h(q, seed) * len(colors)) % len(colors)] if X.h(q, seed + 9) < 0.45 else v.color
    return f


def bands(colors, period=2):
    def f(m):
        for p, v in m.v.items():
            if v.group == m.skin_group:
                v.color = colors[(p[2] // period + (p[1] // 4)) % len(colors)]
    return f


FROGS = [
    ('Pondkeeper', dict(outfit='monk', hat=False, outfit_kw=dict(main=(90, 130, 60), trim=(200, 160, 60)))),
    ('Bullfrog', dict(skin=(90, 110, 50), belly=(230, 220, 140), throat=(240, 220, 100), head=dict(w=11, d=9, h=7, style='soft'), outfit='heavy',
                      hat=False)),
    ('Treeclimber', dict(skin=(110, 200, 70), belly=(240, 240, 220), iris=(220, 40, 40), slit=True, pads=(240, 140, 40), outfit='scout', hat=False,
                         outfit_kw=dict(quiver=False))),
    ('Horned', dict(skin=(120, 160, 70), pattern=lambda m: X.spots(m, (150, 90, 50), density=0.25), head=dict(w=11, d=9, h=7, style='soft'),
                    extras=lambda m: H.horns(m, m.head, 'small', (110, 150, 60)), outfit='barbarian', hat=False, outfit_kw=dict(paint=False))),
    ('Glassfrog', dict(skin=(160, 220, 120), belly=(200, 230, 200), iris=(220, 220, 220), outfit='psychic', hat=False)),
    ('Tomato', dict(skin=(230, 80, 40), belly=(240, 160, 90), outfit='merchant', hat=True)),
    ('Goliath', dict(skin=(100, 110, 70), head=dict(w=13, d=9, h=7, style='soft'), outfit='warrior', hat=False)),
    ('Croaker', dict(skin=(120, 150, 70), throat=(230, 220, 150), outfit='bard', hat=True)),
    ('Marsh', dict(skin=(90, 120, 60), pattern=lambda m: X.spots(m, (60, 80, 40), density=0.3), outfit='nature_mage', hat=False)),
    ('Clawed', dict(skin=(150, 140, 120), belly=(230, 220, 200), iris=(60, 60, 60), outfit='sailor', hat=True)),
    ('Prince', dict(skin=(100, 180, 80), outfit='noble', hat=False, extras=lambda m: H.hat(m, m.head, 'crown', (222, 184, 72), extra=(220, 40, 60)))),
    ('Swampsniper', dict(skin=(80, 110, 70), outfit='sharpshooter', hat=False)),
]

POISON = [
    ('Strawberry', dict(skin=(220, 40, 40), belly=(220, 40, 40), extras=lambda m: m.paint((40, 80, 200), None, parts=('uleg_r', 'lleg_r', 'uleg_l', 'lleg_l', 'larm_r', 'larm_l', 'hand_r', 'hand_l', 'foot_r', 'foot_l'),
                    where=lambda p, v: v.group == 'skin'), outfit='apothecary', hat=False)),
    ('Azure', dict(skin=(40, 90, 210), belly=(40, 90, 210), pattern=lambda m: X.spots(m, (20, 20, 40), density=0.2), outfit='rogue', hat=False,
                   outfit_kw=dict(mask=False, main=(30, 30, 50)))),
    ('Golden', dict(skin=(250, 200, 40), belly=(250, 210, 80), iris=(30, 28, 30), outfit='cleric', hat=False, outfit_kw=dict(main=(40, 40, 40), trim=(250, 200, 40)))),
    ('Dyeing', dict(skin=(250, 220, 40), belly=(40, 90, 200), pattern=bands([(250, 220, 40), (30, 30, 30), (30, 30, 30)], 2), outfit='assault', hat=False)),
    ('Bumblebee', dict(skin=(250, 210, 30), pattern=bands([(250, 210, 30), (20, 20, 20)], 2), outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('Mimic', dict(skin=(30, 30, 30), pattern=lambda m: X.stripes(m, (240, 130, 30), period=3, head=True), outfit='bard', hat=True)),
    ('Glowtoxin', dict(skin=(40, 40, 50), pattern=lambda m: X.spots(m, (120, 255, 120), density=0.2), glow=((120, 255, 120),), outfit='necromancer',
                       hat=False, outfit_kw=dict(accent=(120, 255, 120)))),
    ('Phantasmal', dict(skin=(160, 60, 40), pattern=lambda m: X.stripes(m, WHITE, period=4, head=True), outfit='sharpshooter', hat=False)),
    ('Emerald', dict(skin=(40, 180, 90), pattern=lambda m: X.spots(m, (20, 30, 20), density=0.25, size=2), outfit='fire_mage', hat=False,
                     outfit_kw=dict(main=(40, 120, 60), trim=(150, 255, 120), accent=(150, 255, 120)))),
    ('Harlequin', dict(skin=(240, 120, 40), pattern=dart([(30, 30, 30), (240, 240, 230)], 2), outfit='noble', hat=False)),
    ('Lovely', dict(skin=(150, 50, 40), pattern=lambda m: X.spots(m, (240, 200, 60), density=0.25), outfit='gunslinger', hat=True)),
    ('Blackjewel', dict(skin=(30, 30, 36), pattern=lambda m: X.spots(m, (220, 40, 60), density=0.12), outfit='psychic', hat=False,
                     iris=(220, 40, 60))),
]

TOAD = dict(head=dict(w=11, d=9, h=6, style='soft'), eye_size=1.6, iris=(230, 140, 40), slit=True)


def toad(**kw):
    d = dict(TOAD)
    d.update(kw)
    skin = d.get('skin', (140, 120, 70))
    d.setdefault('warts', [shade(skin, 0.8), shade(skin, 1.15)])
    return frog(**d)


TOADS = [
    ('Cane', dict(skin=(140, 120, 70), belly=(220, 200, 150), outfit='merchant', hat=True)),
    ('Natterjack', dict(skin=(120, 130, 90), extras=lambda m: m.paint((240, 220, 80), None, parts=('chest', 'spine', 'hips'),
                        where=lambda p, v: p[0] == 16 and p[1] == 17), outfit='peasant', hat=True)),
    ('Firebelly', dict(skin=(60, 130, 60), belly=(240, 80, 30), outfit='fire_mage', hat=False)),
    ('Warlord', dict(skin=(110, 100, 60), outfit='warrior', hat=False, outfit_kw=dict(main=(90, 70, 40)))),
    ('Smith', dict(skin=(120, 100, 70), outfit='smith', hat=False)),
    ('Bog', dict(skin=(90, 90, 60), outfit='necromancer', hat=False, iris=(150, 255, 90))),
    ('Oriental', dict(skin=(150, 110, 60), belly=(240, 120, 40), outfit='monk', hat=False)),
    ('Surinam', dict(skin=(140, 130, 100), head=dict(w=13, d=9, h=5, style='soft'), outfit='scholar', hat=False)),
    ('Brute', dict(skin=(100, 90, 60), outfit='heavy', hat=False)),
    ('Bandit', dict(skin=(130, 110, 70), outfit='gunslinger', hat=True)),
    ('Hermit', dict(skin=(150, 140, 110), outfit='earth_mage', hat=False)),
    ('Gourd', dict(skin=(170, 120, 60), outfit='apothecary', hat=False)),
]

REGULAR = [
    ('Leopard', dict(skin=(120, 170, 80), pattern=lambda m: X.spots(m, (50, 80, 40), density=0.22, size=2), outfit='scout', hat=False,
                     outfit_kw=dict(quiver=False))),
    ('Wood', dict(skin=(170, 120, 80), extras=lambda m: [m.set((x, m.front_y(x, m.head.z0 + 2), m.head.z0 + 2), (60, 40, 30), 'detail', 'Head', 'head')
                                                         for x in (m.head.x0, m.head.x0 + 1, m.head.x1 - 1, m.head.x1) if m.front_y(x, m.head.z0 + 2) is not None],
                  outfit='hunter', hat=True)),
    ('RedEyed', dict(skin=(100, 200, 70), belly=(240, 240, 220), iris=(220, 30, 30), slit=True, pads=(240, 130, 40),
                     extras=lambda m: m.paint((40, 90, 200), None, parts=('chest', 'spine'), where=lambda p, v: v.group == 'skin' and p[0] in (14, 18)),
                     outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Whites', dict(skin=(120, 190, 150), head=dict(w=11, d=9, h=7, style='soft'), outfit='peasant', hat=True)),
    ('Green', dict(skin=(90, 150, 70), outfit='ranger', hat=False)),
    ('Pickerel', dict(skin=(150, 140, 100), pattern=lambda m: X.spots(m, (110, 70, 40), density=0.3, size=2), outfit='bard', hat=True)),
    ('River', dict(skin=(80, 120, 90), outfit='sailor', hat=True)),
    ('Reedpiper', dict(skin=(110, 170, 90), outfit='nature_mage', hat=False)),
    ('Chorus', dict(skin=(130, 140, 100), outfit='cleric', hat=False)),
    ('Lilypad', dict(skin=(90, 180, 90), outfit='white_mage', hat=False)),
    ('Tadpole', dict(skin=(70, 80, 60), belly=(130, 140, 110), outfit='apothecary', hat='goggles')),
    ('Leaper', dict(skin=(100, 160, 60), outfit='assault', hat=False)),
]

# --- Snailfolk -------------------------------------------------------------------------------

def snail(skin=(200, 180, 150), shell=(150, 100, 60), stripe=None, head=None, eye=(30, 28, 32), outfit=None, outfit_kw=None, hat=False,
          extras=None, shell_style='coil', shell_r=7.0, pattern=None, frills=None, glow=None):
    head = head or dict(w=9, d=8, h=6, style='round')
    def face(m, hd):
        X.eye_stalks(m, shade(skin, 0.95), eye=eye, white=shade(skin, 0.9), height=4, spread=2)
        for x in (13, 19):
            m.set((x, hd.y0, hd.z1 + 1), shade(skin, 0.95), 'skin', 'Head', 'head')
        H.mouth(m, hd, 'smile', color=shade(skin, 0.6), z=hd.z0 + 1, width=3)
        for x in (14, 18):
            y = m.front_y(x, hd.z0 + 3)
            if y is not None:
                m.set((x, y, hd.z0 + 3), eye, 'eye', 'Head', 'head')
    def pat(m):
        for p, v in m.v.items():
            if v.group == 'skin' and X.h(p, 81) < 0.12:
                v.color = shade(v.color, 1.12)
        if pattern:
            pattern(m)
    def after(m):
        if shell_style == 'coil':
            X.snail_shell(m, shell, stripe=stripe, r=shell_r)
        elif shell_style == 'cone':
            X.hermit_shell(m, shell, stripe)
        if frills:
            for z in range(9, 19, 2):
                for x in (15, 17):
                    m.set((x, 18, z), frills[0], 'skin', 'Chest')
                    m.set((x, 19, z + 1), frills[1], 'skin', 'Chest')
            hd = m.head
            for y in range(hd.y0 + 2, hd.y1 + 1, 2):
                m.set((16, y, hd.z1 + 1), frills[0], 'skin', 'Head', 'head')
                m.set((16, y, hd.z1 + 2), frills[1], 'skin', 'Head', 'head')
        if extras:
            extras(m)
    m = beast(skin, skin_group='skin', head=head, eyes=None, face=face, pattern=pat, outfit=outfit, outfit_kw=outfit_kw, hat=hat, extras=after)
    if glow:
        for p, v in m.v.items():
            if v.color == glow:
                v.mat = GLOW
                v.group = 'light'
    return m


SNAILS = [
    ('Garden', dict(outfit='peasant', hat=False)),
    ('Roman', dict(skin=(220, 200, 170), shell=(230, 210, 170), stripe=(180, 150, 110), outfit='scholar', hat=False)),
    ('Cone', dict(skin=(200, 170, 150), shell=(240, 220, 180), stripe=(150, 80, 50), shell_style='cone', outfit='apothecary', hat=False)),
    ('Conch', dict(skin=(230, 190, 170), shell=(250, 180, 160), stripe=(240, 140, 120), shell_style='cone', outfit='sailor', hat=True)),
    ('Nautilus', dict(skin=(230, 210, 190), shell=(246, 240, 230), stripe=(190, 100, 60), outfit='water_mage', hat=False, shell_r=8.0)),
    ('BananaSlug', dict(skin=(240, 210, 60), shell_style=None, pattern=lambda m: X.spots(m, (110, 90, 40), density=0.12), outfit='scout', hat=False,
                        outfit_kw=dict(quiver=False))),
    ('Nudibranch', dict(skin=(120, 60, 200), shell_style=None, frills=((250, 150, 40), (250, 240, 230)), outfit='psychic', hat=False)),
    ('Apple', dict(skin=(230, 190, 120), shell=(200, 160, 60), stripe=(120, 90, 40), outfit='merchant', hat=False)),
    ('Treesnail', dict(skin=(200, 220, 200), shell=(250, 230, 120), stripe=(220, 90, 140), outfit='bard', hat=True)),
    ('Ironshell', dict(skin=(170, 170, 170), shell=(150, 154, 162), stripe=(110, 114, 122), outfit='guardian', hat=False, outfit_kw=dict(cape=False))),
    ('Glowshell', dict(skin=(150, 170, 190), shell=(60, 60, 90), stripe=(120, 220, 255), glow=(120, 220, 255), outfit='necromancer', hat=False)),
    ('Moss', dict(skin=(170, 180, 130), shell=(110, 130, 70), stripe=(80, 100, 50), outfit='nature_mage', hat=False)),
    ('Racer', dict(skin=(200, 170, 140), shell=(200, 60, 40), stripe=(250, 250, 250), outfit='gunslinger', hat=True)),
]


def mer_concept(kind):
    """A figure's upper body on a fish's tail, lying curled on the ground."""
    skin = {'shark': (110, 120, 140), 'koi': (240, 238, 232), 'snail': (200, 180, 150)}[kind]
    m = F.body(skin, 'skin', leg=4, leg_w=2, leg_d=2, gap=1, torso_w=7, torso_d=4, torso_h=10, arm_len=8, arm_w=2, arm_d=2,
               arm_pose='a', head=dict(w=9, d=9, h=7, style='soft'), neck=1, foot_len=0)
    m.v = {p: v for p, v in m.v.items() if not (v.part or '').startswith(('uleg', 'lleg', 'foot'))}
    b = m.body
    hd = m.head
    m.head_skin = skin
    if kind == 'shark':
        shark_snout(m, hd, skin, WHITE, 3)
        side_eyes(m, hd, (30, 28, 30), z=hd.z0 + 3, style='dot')
        X.sweep(m, [(16, 16, b.hip, 3, 2.5, 2.5), (16, 18, 3, 2.8, 2.6, 2.4), (16, 23, 2, 2.2, 2.2, 2), (16, 28, 2, 1.4, 1.4, 1.3)], skin, 'skin', None)
        for k in range(6):
            m.set((16, 30 + k // 3, 2 + k), (80, 90, 110), 'skin')
            m.set((16, 30 + k // 3, 2 - k // 2), (80, 90, 110), 'skin')
        for z in range(b.hip + 2, b.top + 1):
            m.set((16, b.back + 1, z), shade(skin, 0.9), 'skin')
        F.dress(m, belt=(60, 40, 30), buckle=(222, 184, 72), sash=(150, 40, 40))
    elif kind == 'koi':
        fish_eyes(m, hd, iris=(240, 200, 60))
        fish_mouth(m, hd, style='o')
        X.sweep(m, [(16, 16, b.hip, 3, 2.5, 2.5), (16, 18, 3, 2.8, 2.6, 2.4), (20, 22, 2, 2.2, 2.2, 2), (22, 27, 2, 1.4, 1.4, 1.3)],
                lambda t, p: (230, 90, 40) if X.h((p[0] // 2, p[1] // 2, 0), 5) < 0.4 else (240, 238, 232), 'skin', None)
        for k in range(5):
            for d in (-1, 0, 1):
                m.set((22 + d, 29 + k // 2, 2 + k - 2), (240, 150, 100), 'skin')
        F.dress(m, sash=(40, 60, 110), belt=(222, 184, 72))
    else:
        X.eye_stalks(m, shade(skin, 0.95), height=4)
        H.mouth(m, hd, 'smile', color=shade(skin, 0.6), z=hd.z0 + 1, width=3)
        X.sweep(m, [(16, 15, b.hip, 3.2, 3, 2.4), (16, 13, 2.5, 3.2, 3.5, 2.2), (16, 9, 1.5, 2.5, 3, 1.6), (16, 6, 1, 1.5, 1.6, 1)], skin, 'skin', None)
        for x in range(13, 20):
            for y in range(b.back + 1, b.back + 12):
                for z in range(2, 20):
                    dy, dz = y + 0.5 - (b.back + 6), z + 0.5 - 11
                    d = (dy * dy + dz * dz) ** 0.5
                    if d <= 6.5 * (1 - ((x - 16) / 4.5) ** 2) ** 0.5:
                        m.set((x, y, z), (180, 110, 60) if int(d * 1.3 + (dy > 0) * 2) % 3 else (120, 70, 40), 'shell')
        F.dress(m, sash=(60, 110, 60))
    return m


SETS = [
    Set('Fishfolk', 'Fishfolk', designs(fish, FISH), treat3(1, 2, 3), concepts=[('Koi', lambda: mer_concept('koi'))]),
    Set('Crabfolk', 'Crabfolk', designs(crab, CRABS), treat3(1, 2, 4), concepts=[('Broadshell', CX.crab)]),
    Set('Sharkfolk', 'Sharkfolk', designs(shark, SHARKS), treat3(2, 1, 12), concepts=[('Merrow', lambda: mer_concept('shark'))]),
    Set('Frogfolk', 'Frogfolk', designs(frog, FROGS), treat3(1, 2, 3), concepts=[('Crouch', CX.frog)]),
    Set('Frogfolk/Poison', 'Frogfolk_Poison', designs(frog, POISON), treat3(1, 2, 3)),
    Set('Frogfolk/Toad', 'Frogfolk_Toad', designs(toad, TOADS), treat3(1, 2, 3)),
    Set('Frogfolk/Regular', 'Frogfolk_Regular', designs(frog, REGULAR), treat3(1, 3, 2)),
    Set('Snailfolk', 'Snailfolk', designs(snail, SNAILS), treat3(1, 2, 7), concepts=[('Slither', lambda: mer_concept('snail'))]),
]
