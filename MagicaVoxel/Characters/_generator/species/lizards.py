"""Lizardfolk, generic and the four kinds: desert, chameleonic, water and crocodile. A long
head and snout, eyes high and wide, a tail on the hips, crests, frills, horns and gills on the
head, spines down the back."""
from .common import Set, designs, beast, EYES
from core import shade, mix, sat
import heads as H
import outfits as O
import extras as X
import freebody as F

BONE = (232, 224, 200)


def side_eyes(m, hd, iris, z=None, style='slit', dark=(28, 26, 30), bulge=False, ring=None):
    """An eye at each front corner of the head, seen from the front and the side."""
    z = z if z is not None else hd.z0 + 3
    for x, out in ((hd.x0, -1), (hd.x1, 1)):
        if bulge:
            for dz in (-1, 0, 1, 2):
                for dy in (0, 1, 2):
                    if abs(dz - 0.5) + abs(dy - 1) <= 2:
                        m.set((x + out, hd.y0 + 1 + dy, z + dz), ring or m.head_skin, m.skin_group, 'Head', 'head')
            x = x + out
        cells = [(x, hd.y0 + 1, z), (x, hd.y0 + 1, z + 1), (x, hd.y0 + 2, z), (x, hd.y0 + 2, z + 1)]
        for (cx, cy, cz) in cells:
            c = iris
            if style == 'slit' and cy == hd.y0 + 1:
                c = dark if cz == z else iris
            if style == 'dot' and (cy, cz) == (hd.y0 + 1, z):
                c = dark
            m.set((cx, cy, cz), c, 'eye', 'Head', 'head')
        # from the front, the eye shows at the corner
        fx = x - out if bulge else x - out
        if not bulge:
            m.set((x - out * 0, hd.y0 + 1, z + 1), iris, 'eye', 'Head', 'head')
            m.set((x - out, hd.y0, z), dark, 'eye', 'Head', 'head')
            m.set((x - out, hd.y0, z + 1), iris, 'eye', 'Head', 'head')


def crest(m, style, color, tip=None, back=True):
    """spines (a row along the head and down the back), sail (a fin along the head), horns (a
    horned lizard's crown), casque (a chameleon's helmet), crown (spikes all round), ridge."""
    tip = tip or shade(color, 1.25)
    hd = m.head
    if style == 'spines':
        for i, y in enumerate(range(hd.y0 + 1, hd.y1 + 1)):
            hgt = 2 if i % 2 == 0 else 1
            for k in range(1, hgt + 1):
                m.set((16, y, hd.z1 + k), tip if k == hgt else color, 'horn', 'Head', 'head')
        for z in range(hd.z1, hd.z0 + 1, -2):
            m.set((16, hd.y1 + 1, z), color, 'horn', 'Head', 'head')
        if back:
            for z in range(10, 19, 2):
                m.set((16, 18, z), color, 'horn', 'Chest')
                m.set((16, 19, z + 1), tip, 'horn', 'Chest')
    elif style == 'sail':
        for i, y in enumerate(range(hd.y0 + 2, hd.y1 + 2)):
            hgt = min(i + 1, 4) if i < 6 else 2
            for k in range(1, hgt + 1):
                m.set((16, y, hd.z1 + k), tip if k == hgt else color, 'skin', 'Head', 'head')
        if back:
            for z in range(9, 19):
                hgt = 3 if 12 <= z <= 16 else 2
                for k in range(hgt):
                    m.set((16, 18 + k, z), tip if k == hgt - 1 else color, 'skin', 'Chest')
    elif style == 'horns':
        for x in range(hd.x0, hd.x1 + 1, 2):
            m.set((x, hd.y1 + 1, hd.z1), color, 'horn', 'Head', 'head')
            m.set((x, hd.y1 + 2, hd.z1 + (1 if abs(x - 16) < 3 else 0)), tip, 'horn', 'Head', 'head')
        for x in (hd.x0 + 1, hd.x1 - 1):
            m.set((x, hd.y1, hd.z1 + 1), color, 'horn', 'Head', 'head')
            m.set((x, hd.y1 + 1, hd.z1 + 2), tip, 'horn', 'Head', 'head')
        for x in (hd.x0 - 1, hd.x1 + 1):
            m.set((x, hd.y1 - 1, hd.z1 - 1), tip, 'horn', 'Head', 'head')
    elif style == 'casque':
        for i, y in enumerate(range(hd.y0 + 2, hd.y1 + 2)):
            hgt = 1 + i // 2
            for x in (15, 16, 17):
                for k in range(1, hgt + 1):
                    if x != 16 and k == hgt:
                        continue
                    m.set((x, y, hd.z1 + k), tip if (k == hgt or y == hd.y1 + 1) else color, m.skin_group, 'Head', 'head')
    elif style == 'crown':
        for x in range(hd.x0, hd.x1 + 1, 2):
            for y in (hd.y0 + 1, hd.y1):
                m.set((x, y, hd.z1 + 1), tip, 'horn', 'Head', 'head')
        for y in range(hd.y0 + 1, hd.y1 + 1, 2):
            m.set((hd.x0 - 1, y, hd.z1 - 1), tip, 'horn', 'Head', 'head')
            m.set((hd.x1 + 1, y, hd.z1 - 1), tip, 'horn', 'Head', 'head')
    elif style == 'ridge':
        for x in (hd.x0 + 1, hd.x1 - 1):
            for y in range(hd.y0, hd.y0 + 4):
                m.set((x, y, hd.z1), tip, 'horn', 'Head', 'head')


def gills(m, color, tip=None):
    """An axolotl's three feathery gill stalks each side of the head."""
    tip = tip or shade(color, 0.8)
    hd = m.head
    for side in (-1, 1):
        xb = hd.x0 - 1 if side < 0 else hd.x1 + 1
        for i, (dz, reach) in enumerate(((5, 3), (3, 3), (1, 2))):
            z = hd.z0 + dz
            for k in range(reach):
                x = xb + side * k
                c = tip if k == reach - 1 else color
                m.set((x, hd.y0 + 5, z + (k + 1) // 2), c, 'skin', 'Head', 'head')
                if k >= 1:
                    m.set((x, hd.y0 + 4, z + (k + 1) // 2 + 1), color, 'skin', 'Head', 'head')


def turret_eyes(m, color, iris=(240, 200, 60), pupil=(28, 26, 30)):
    """A chameleon's eyes: cones out of the head's sides, the pupil at their tips."""
    hd = m.head
    z = hd.z0 + 3
    for side in (-1, 1):
        xb = hd.x0 if side < 0 else hd.x1
        m.ellipsoid(xb + side * 0.6 + (0.5 if side > 0 else 0.5), hd.y0 + 2.5, z + 0.5, 1.6, 1.6, 1.6, color, m.skin_group, 'Head', 'head', only_empty=False,
                    where=lambda p, s=side, xb=xb: (p[0] - xb) * s >= 0)
        m.set((xb + side * 2, hd.y0 + 2, z), iris, 'eye', 'Head', 'head')
        m.set((xb + side * 2, hd.y0 + 2, z + 1), iris, 'eye', 'Head', 'head')
        m.set((xb + side * 2, hd.y0 + 1, z), pupil, 'eye', 'Head', 'head')
        m.set((xb + side * 1, hd.y0 + 1, z + 1), iris, 'eye', 'Head', 'head')


def throat_beard(m, color, tip=None):
    """A bearded dragon's spiny beard under the jaw."""
    tip = tip or shade(color, 1.3)
    hd = m.head
    for x in range(hd.x0 + 1, hd.x1):
        for y in range(hd.y0 - 2, hd.y0 + 2):
            m.set((x, y, 19), color, 'scale', 'Head', 'head')
        if x % 2 == 0:
            m.set((x, hd.y0 - 3, 19), tip, 'horn', 'Head', 'head')
            m.set((x, hd.y0 - 2, 18), tip, 'horn', 'Head', 'head')
    for x in (hd.x0, hd.x1):
        m.set((x, hd.y0, 19), tip, 'horn', 'Head', 'head')


def nose_horns(m, color, count=1):
    """A Jackson's chameleon's horns: one over the snout, two over the eyes."""
    hd = m.head
    m.set((16, hd.y0 - 1, hd.z1 - 1), color, 'horn', 'Head', 'head')
    m.set((16, hd.y0 - 2, hd.z1 - 1), color, 'horn', 'Head', 'head')
    m.set((16, hd.y0 - 3, hd.z1), shade(color, 1.2), 'horn', 'Head', 'head')
    if count >= 3:
        for x in (13, 19):
            m.set((x, hd.y0 - 1, hd.z1), color, 'horn', 'Head', 'head')
            m.set((x, hd.y0 - 2, hd.z1 + 1), shade(color, 1.2), 'horn', 'Head', 'head')


def gila(m, dark=(40, 30, 30), bright=(230, 120, 60)):
    X.mottle(m, [dark, bright, dark], density=0.75, seed=17)


def collar_band(m, color=(30, 28, 30)):
    m.paint(color, None, parts=('chest', 'neck'), where=lambda p, v: p[2] in (17, 18, 19) and v.group == m.skin_group)


def lizard(scale=(90, 150, 70), belly=(220, 210, 150), head=None, snout=None, eyes='slit', iris='gold',
           eye_style='front', crest_style=None, crest_color=None, tail='lizard', tail_tip=None, pattern=None,
           pattern_color=None, outfit=None, outfit_kw=None, hat=False, claws=True, extras=None, frill=None,
           frill_color=None, group='scale', head_color=None, teeth=None, mouth=None):
    iris = EYES.get(iris, iris) if isinstance(iris, str) else iris
    head = head or dict(w=9, d=8, h=7, style='soft')
    sn = dict(length=3, w=5, h=3, taper=1, color=shade(head_color or scale, 1.08), jaw=belly)
    sn.update(snout or {})
    if teeth:
        sn['teeth'] = teeth
    if mouth:
        sn['mouth'] = mouth
    def face(m, hd):
        m.head_skin = head_color or scale
        if eye_style == 'side':
            side_eyes(m, hd, iris, z=hd.z0 + 3, style='slit')
        elif eye_style == 'bulge':
            side_eyes(m, hd, iris, z=hd.z0 + 3, style='slit', bulge=True)
        elif eye_style == 'turret':
            turret_eyes(m, head_color or scale, iris)
    def pat(m):
        if pattern == 'scales':
            X.scales(m, pattern_color or shade(scale, 0.82))
        elif pattern == 'bands':
            X.stripes(m, pattern_color or shade(scale, 0.7), period=3)
        elif pattern == 'spots':
            X.spots(m, pattern_color or shade(scale, 0.7), density=0.2)
        elif pattern == 'gila':
            gila(m, pattern_color or (40, 30, 30))
        elif pattern == 'collar':
            collar_band(m, pattern_color or (30, 28, 30))
        elif callable(pattern):
            pattern(m)
        if crest_style:
            crest(m, crest_style, crest_color or shade(scale, 0.75))
        if frill:
            X.frill(m, frill_color or shade(scale, 1.1), edge=shade(frill_color or scale, 0.7), size=frill)
    def after(m):
        if extras:
            extras(m)
    m = beast(scale, skin_group=group, head=head, muzzle=sn, eyes=eyes if eye_style == 'front' else None,
              iris=iris, eye_gap=5, eye_w=2, belly_color=belly, face=face, pattern=pat, tail=tail,
              tail_tip=tail_tip, hands='claws' if claws else None, hand_color=BONE, outfit=outfit,
              outfit_kw=outfit_kw, hat=hat, extras=after, head_color=head_color)
    return m


# --- Generic ---------------------------------------------------------------------------------

GENERIC = [
    ('Warrior', dict(scale=(80, 140, 64), crest_style='spines', pattern='scales', outfit='warrior')),
    ('Shaman', dict(scale=(60, 140, 130), belly=(200, 220, 180), frill=3, frill_color=(220, 120, 60), outfit='nature_mage',
                    outfit_kw=dict(main=(110, 80, 50), second=(140, 170, 80)))),
    ('Hunter', dict(scale=(150, 110, 70), belly=(230, 200, 150), crest_style='ridge', pattern='bands', outfit='tribal',
                    outfit_kw=dict(trim=(200, 200, 190)))),
    ('Sharpshooter', dict(scale=(50, 90, 50), crest_style='spines', outfit='sharpshooter', iris='amber')),
    ('Gladiator', dict(scale=(170, 50, 40), belly=(240, 200, 120), crest_style='spines', crest_color=(240, 200, 80), outfit='gladiator', hat=False)),
    ('Scout', dict(scale=(120, 130, 60), pattern='bands', pattern_color=(80, 90, 40), outfit='scout', hat=False)),
    ('Monk', dict(scale=(60, 100, 170), belly=(170, 210, 230), outfit='monk', iris='ice', eye_style='side')),
    ('Officer', dict(scale=(100, 130, 100), outfit='tactician', hat=True, pattern='scales')),
    ('Alchemist', dict(scale=(120, 80, 140), belly=(210, 190, 220), outfit='apothecary', hat='goggles', iris='green')),
    ('Berserker', dict(scale=(40, 40, 46), belly=(160, 50, 40), crest_style='spines', crest_color=(180, 40, 30), pattern='scales',
                       pattern_color=(60, 30, 30), outfit='barbarian', outfit_kw=dict(paint=False))),
    ('Warden', dict(scale=(150, 160, 60), crest_style='crown', crest_color=(230, 220, 160), outfit='guardian', hat=False,
                    outfit_kw=dict(second=(60, 90, 50), emblem='chevron', cape=False))),
    ('Oracle', dict(scale=(236, 230, 226), belly=(250, 236, 236), iris='red', outfit='psychic', crest_style='ridge', crest_color=(240, 200, 210))),
    ('Bonecaller', dict(scale=(110, 116, 100), belly=(170, 170, 150), outfit='necromancer', hat=False, crest_style='horns', crest_color=BONE,
                        iris=(120, 255, 140))),
    ('Raider', dict(scale=(220, 120, 40), belly=(250, 220, 150), pattern='spots', pattern_color=(120, 60, 30), outfit='assault', hat=False)),
    ('Elder', dict(scale=(120, 140, 110), belly=(200, 200, 170), outfit='scholar', crest_style='ridge', hat=False)),
]

# --- Desert ----------------------------------------------------------------------------------

def thorny(m):
    X.spines(m, (200, 140, 80), tip=(240, 210, 160), length=2, density=0.45, seed=4)
    X.mottle(m, [(170, 110, 60), (220, 170, 110), (150, 90, 50)], density=0.5, seed=8)


def desert_wrap(m):
    hd = m.head
    for x in range(hd.x0 - 1, hd.x1 + 2):
        for y in range(hd.y0 + 3, hd.y1 + 2):
            m.set((x, y, hd.z1 + 1), (230, 214, 180), 'cloth', 'Head', 'head')
    for x in range(hd.x0, hd.x1 + 1):
        m.set((x, hd.y1 + 1, hd.z1), (230, 214, 180), 'cloth', 'Head', 'head')
        m.set((x, hd.y1 + 2, hd.z1 - 1), (200, 180, 150), 'cloth', 'Head', 'head')


DESERT = [
    ('ThornyDevil', dict(scale=(190, 130, 70), belly=(230, 200, 150), pattern=thorny, outfit='tribal', tail_tip=(140, 80, 40),
                         outfit_kw=dict(main=(150, 90, 50), trim=(230, 220, 200)))),
    ('Hornback', dict(scale=(210, 170, 110), belly=(240, 220, 180), crest_style='horns', crest_color=(160, 120, 80), pattern='spots',
                      pattern_color=(170, 120, 80), outfit='scout', outfit_kw=dict(main=(200, 170, 120), trim=(150, 110, 70)))),
    ('GilaBrute', dict(scale=(60, 40, 40), belly=(220, 120, 70), pattern='gila', outfit='warrior', iris='black',
                       outfit_kw=dict(main=(90, 60, 40)))),
    ('Beardscale', dict(scale=(200, 160, 100), belly=(240, 220, 170), outfit='gunslinger', hat=True, eye_style='side',
                        extras=lambda m: throat_beard(m, (180, 130, 80)))),
    ('Spinytail', dict(scale=(230, 170, 50), belly=(250, 220, 120), tail='spikes', tail_tip=(140, 100, 40), outfit='merchant', hat=False,
                       head_color=(120, 110, 90))),
    ('Collarneck', dict(scale=(60, 180, 170), belly=(230, 230, 120), pattern='collar', outfit='rogue', hat=False,
                        outfit_kw=dict(main=(120, 90, 60), mask=False))),
    ('FrillNomad', dict(scale=(170, 140, 100), frill=4, frill_color=(230, 120, 60), outfit='merchant', hat=False,
                        outfit_kw=dict(main=(220, 200, 160), second=(150, 60, 40)))),
    ('DuneStalker', dict(scale=(222, 196, 150), belly=(240, 230, 200), outfit='sharpshooter', hat=False, eye_style='side',
                         extras=desert_wrap, outfit_kw=dict(main=(200, 170, 120), trim=(150, 120, 80)))),
    ('Savannah', dict(scale=(140, 120, 90), belly=(200, 190, 150), head=dict(w=9, d=9, h=7, style='soft'), snout=dict(length=4),
                      pattern='spots', pattern_color=(110, 90, 60), outfit='tactician', hat=True, outfit_kw=dict(main=(150, 120, 70)))),
    ('GoldSkink', dict(scale=(210, 170, 60), belly=(240, 220, 160), pattern='bands', pattern_color=(120, 70, 30), outfit='assault', hat=False,
                       snout=dict(length=2, w=5, h=3, taper=1))),
    ('DuneShaman', dict(scale=(180, 150, 110), crest_style='crown', crest_color=(240, 230, 200), outfit='earth_mage', hat=False)),
    ('Sunscale', dict(scale=(220, 90, 40), belly=(250, 200, 90), crest_style='sail', crest_color=(250, 170, 40), outfit='fire_mage', hat=False)),
]

# --- Chameleonic -----------------------------------------------------------------------------

def bands(colors, period=2):
    def f(m):
        for p, v in m.v.items():
            if v.group == m.skin_group and v.part in ('chest', 'spine', 'hips', 'uleg_r', 'uleg_l', 'uarm_r', 'uarm_l'):
                k = (p[2] // period) % len(colors) if v.part not in ('uarm_r', 'uarm_l') else (p[0] // period) % len(colors)
                v.color = colors[k]
    return f


def shimmer(colors):
    def f(m):
        for p, v in m.v.items():
            if v.group == m.skin_group:
                t = (p[2] + p[0] * 0.3) / 30
                v.color = colors[min(len(colors) - 1, int(t * len(colors)))]
    return f


CHAM = dict(eye_style='turret', tail='chameleon', snout=dict(length=2, w=5, h=3, taper=1), head=dict(w=9, d=8, h=7, style='soft'))


def cham(**kw):
    d = dict(CHAM)
    d.update(kw)
    return d


CHAMELEONIC = [
    ('Veiled', cham(scale=(90, 170, 70), belly=(200, 220, 120), crest_style='casque', pattern=bands([(90, 170, 70), (220, 200, 70)], 3),
                    outfit='rogue', outfit_kw=dict(main=(60, 70, 50), mask=False))),
    ('Panther', cham(scale=(40, 150, 170), belly=(220, 220, 160), pattern=bands([(40, 150, 170), (230, 100, 60), (40, 150, 170)], 2),
                     crest_style='ridge', crest_color=(230, 100, 60), outfit='bard', hat=False)),
    ('Triceros', cham(scale=(70, 150, 80), belly=(170, 200, 120), extras=lambda m: nose_horns(m, (210, 200, 160), 3), outfit='guardian',
                      hat=False, outfit_kw=dict(cape=False))),
    ('Leafling', cham(scale=(140, 100, 60), belly=(180, 150, 100), pattern='spots', pattern_color=(100, 70, 40), outfit='scout',
                      outfit_kw=dict(main=(100, 80, 50)))),
    ('Carpet', cham(scale=(200, 120, 60), belly=(240, 200, 140), pattern='spots', pattern_color=(240, 230, 210), crest_style='ridge',
                    outfit='psychic', hat=False)),
    ('Parson', cham(scale=(110, 140, 110), belly=(190, 200, 170), head=dict(w=11, d=8, h=7, style='soft'), outfit='scholar', hat=False)),
    ('Twinhorn', cham(scale=(80, 160, 120), extras=lambda m: nose_horns(m, (90, 120, 90), 1), outfit='apothecary', hat=False)),
    ('Illusionist', cham(scale=(120, 80, 200), pattern=shimmer([(200, 80, 160), (150, 80, 200), (80, 120, 220), (60, 190, 200), (90, 210, 130)]),
                         crest_style='casque', outfit='psychic', hat=False, outfit_kw=dict(main=(40, 40, 70)))),
    ('Shadowskin', cham(scale=(50, 60, 60), belly=(80, 90, 90), crest_style='casque', crest_color=(80, 90, 90), outfit='rogue',
                        outfit_kw=dict(main=(30, 34, 40)))),
    ('Mossranger', cham(scale=(80, 120, 50), belly=(150, 170, 90), pattern='spots', pattern_color=(110, 90, 50), outfit='ranger', hat=False)),
    ('Dawnweaver', cham(scale=(240, 200, 170), belly=(250, 240, 220), pattern=bands([(240, 200, 170), (240, 150, 150)], 3), outfit='white_mage',
                        hat=False)),
    ('Marksman', cham(scale=(60, 130, 60), crest_style='casque', outfit='sharpshooter', hat=False)),
]

# --- Water -----------------------------------------------------------------------------------

AXO = dict(head=dict(w=11, d=8, h=7, style='soft'), snout=dict(length=1, w=7, h=2, taper=0), eyes='bead', iris='black', eye_style='front', tail='otter', claws=False)


def axo(**kw):
    d = dict(AXO)
    d.update(kw)
    return d


def fins_back(color):
    def f(m):
        X.arm_fins(m, color)
        for z in range(9, 19):
            hgt = 2 if 11 <= z <= 16 else 1
            for k in range(hgt):
                m.set((16, 18 + k, z), color, 'skin', 'Chest')
    return f


def gilled(color, tip=None, more=None):
    def f(m):
        gills(m, color, tip)
        if more:
            more(m)
    return f


def salt(m):
    X.spines(m, (70, 70, 76), tip=(220, 220, 214), length=2, density=0.22, head=True, back=False, seed=6)


WATER = [
    ('Axolotl', axo(scale=(240, 170, 190), belly=(250, 210, 220), group='skin', extras=gilled((230, 90, 120)), outfit='scout', hat=False,
                    outfit_kw=dict(main=(80, 130, 150), quiver=False), mouth=(160, 80, 100))),
    ('MarineIguana', dict(scale=(60, 62, 66), belly=(100, 90, 80), head_color=(200, 196, 186), crest_style='spines', crest_color=(90, 90, 96),
                          pattern=salt, outfit='sailor', hat=False, tail='lizard')),
    ('WaterDragon', dict(scale=(70, 160, 90), belly=(160, 210, 220), crest_style='sail', crest_color=(50, 110, 70), outfit='monk',
                         outfit_kw=dict(main=(60, 110, 160), trim=(220, 200, 80)))),
    ('FireNewt', dict(scale=(60, 50, 40), belly=(240, 120, 40), pattern='spots', pattern_color=(240, 120, 40), outfit='apothecary', hat=False,
                      snout=dict(length=2, w=5, h=2, taper=1), eyes='bead', iris='black')),
    ('Basilisk', dict(scale=(60, 150, 70), belly=(200, 220, 140), crest_style='sail', crest_color=(80, 180, 90), outfit='scout', hat=False,
                      iris='gold', tail='lizard')),
    ('Sea Drake'.replace(' ', ''), dict(scale=(30, 70, 120), belly=(150, 200, 220), crest_style='spines', crest_color=(90, 200, 220),
                                       extras=fins_back((90, 200, 220)), outfit='pirate', hat=True, outfit_kw=dict(eyepatch=False))),
    ('CaveOlm', axo(scale=(240, 226, 214), belly=(250, 240, 236), group='skin', eyes=None, extras=gilled((240, 140, 150)), outfit='psychic', hat=False,
                    outfit_kw=dict(main=(60, 60, 90)))),
    ('Reefscale', dict(scale=(40, 150, 160), belly=(220, 230, 180), extras=lambda m: (X.head_fins(m, (240, 150, 60)), X.arm_fins(m, (240, 150, 60))),
                       outfit='water_mage', hat=False, tail='fish', tail_tip=(240, 150, 60))),
    ('Tidewarden', dict(scale=(50, 110, 100), belly=(180, 210, 190), crest_style='sail', crest_color=(70, 160, 170), outfit='guardian', hat=False,
                        outfit_kw=dict(main=(150, 190, 200), second=(40, 80, 110), emblem='diamond', cape=False))),
    ('Leopard', axo(scale=(230, 210, 120), belly=(250, 240, 200), group='skin', pattern='spots', pattern_color=(90, 70, 40),
                    extras=gilled((150, 90, 60)), outfit='hunter', hat=False, mouth=(120, 90, 60))),
    ('Hellbender', dict(scale=(110, 90, 60), belly=(140, 120, 90), head=dict(w=11, d=8, h=6, style='soft'), snout=dict(length=1, w=7, h=2, taper=0),
                        pattern='spots', pattern_color=(80, 64, 44), eyes='bead', iris='black', tail='otter', claws=False, group='skin',
                        outfit='smith', hat=False, mouth=(70, 50, 40))),
    ('Rivermarksman', dict(scale=(60, 120, 120), belly=(200, 220, 200), crest_style='ridge', outfit='sharpshooter', hat=False,
                           extras=lambda m: X.arm_fins(m, (40, 90, 100)))),
]

# --- Crocodile -------------------------------------------------------------------------------

CROC = dict(head=dict(w=9, d=8, h=6, style='soft'), snout=dict(length=6, w=5, h=2, taper=0), teeth=(240, 236, 220), tail='croc',
            eye_style='bulge', mouth=(80, 50, 40))


def croc(**kw):
    d = dict(CROC)
    for k, v in kw.items():
        if k == 'snout':
            sn = dict(d['snout']); sn.update(v); d['snout'] = sn
        else:
            d[k] = v
    return d


def osteoderms(color):
    def f(m):
        X.scales(m, shade(m.skin, 0.8))
        for z in range(10, 19, 2):
            for x in (15, 17):
                m.set((x, 18, z), color, 'scale', 'Chest')
        hd = m.head
        for y in range(hd.y0 + 2, hd.y1 + 1, 2):
            for x in (hd.x0 + 2, hd.x1 - 2):
                m.set((x, y, hd.z1 + 1), color, 'scale', 'Head', 'head')
    return f


def gharial_knob(m):
    hd = m.head
    tip, half, z, hgt, ln = m.snout_info
    m.ellipsoid(16, tip + 0.5, z + 1.5, 1.6, 1.4, 1.4, shade(m.skin, 0.85), m.skin_group, 'Head', 'head', only_empty=True)


CROCODILE = [
    ('Niletooth', croc(scale=(110, 120, 60), belly=(210, 200, 140), pattern=osteoderms((80, 90, 50)), outfit='heavy', hat=False)),
    ('Alligator', croc(scale=(50, 60, 48), belly=(180, 170, 130), snout=dict(w=7, length=5), pattern=osteoderms((40, 48, 36)),
                       outfit='barbarian', outfit_kw=dict(paint=False))),
    ('Gharial', croc(scale=(120, 130, 100), belly=(220, 210, 180), snout=dict(length=8, w=3, h=2), extras=gharial_knob, outfit='sailor',
                     pattern=osteoderms((100, 110, 80)))),
    ('Caiman', croc(scale=(150, 140, 80), belly=(220, 210, 150), crest_style='ridge', crest_color=(120, 110, 60), outfit='scout', hat=False)),
    ('Saltjaw', croc(scale=(90, 96, 70), belly=(230, 220, 170), head=dict(w=11, d=9, h=6, style='soft'), snout=dict(w=7, length=6, h=3),
                     pattern=osteoderms((70, 76, 56)), outfit='pirate', hat=True)),
    ('Albino', croc(scale=(236, 230, 220), belly=(250, 240, 236), iris='red', outfit='psychic', hat=False)),
    ('Swampcaller', croc(scale=(80, 100, 70), belly=(170, 180, 130), pattern=osteoderms((60, 80, 50)), outfit='necromancer', hat=False,
                         iris=(120, 255, 140), outfit_kw=dict(main=(60, 70, 50), trim=(120, 140, 80)))),
    ('Mugger', croc(scale=(100, 90, 70), belly=(200, 180, 140), snout=dict(w=7, length=5), outfit='warrior', pattern=osteoderms((80, 70, 50)))),
    ('Dwarfcroc', croc(scale=(40, 40, 36), belly=(200, 170, 110), snout=dict(length=4), outfit='assault', hat=False)),
    ('Marshal', croc(scale=(100, 120, 80), belly=(220, 210, 160), outfit='tactician', hat=True, outfit_kw=dict(main=(90, 40, 40)))),
    ('Ironjaw', croc(scale=(90, 100, 70), belly=(200, 190, 150), outfit='smith', pattern=osteoderms((70, 80, 50)))),
    ('Bulwark', croc(scale=(80, 110, 80), belly=(210, 200, 160), outfit='guardian', hat=False, outfit_kw=dict(cape=False, emblem='tower',
                     second=(60, 90, 60)))),
]


def lizard_concept(kind):
    """A lizardfolk as a beast stands: legs bent, leaning forward on a long tail."""
    if kind == 'croc':
        skin = (90, 100, 64)
    elif kind == 'desert':
        skin = (200, 150, 90)
    else:
        skin = (80, 140, 64)
    m = F.body(skin, 'scale', leg=8, leg_w=3, leg_d=3, gap=1, torso_w=9 if kind == 'croc' else 7, torso_d=5, torso_h=11,
               arm_len=11, arm_w=2, arm_d=2, arm_pose='a', head=dict(w=9, d=9, h=7, style='soft'), neck=2, foot_len=3)
    hd = m.head
    H.snout(m, hd, shade(skin, 1.08), length=7 if kind == 'croc' else 4, w=5, h=3, taper=0 if kind == 'croc' else 1,
            jaw=(220, 210, 150), teeth=(240, 236, 220) if kind == 'croc' else None)
    m.head_skin = skin
    side_eyes(m, hd, (230, 190, 50), z=hd.z0 + 4, bulge=kind == 'croc')
    b = m.body
    X.sweep(m, [(16, b.back + 1, b.hip + 2, 2.4, 2, 2.4), (16, b.back + 6, b.hip - 1, 1.8, 1.8, 1.6), (16, b.back + 12, 2, 1.1, 1.2, 1),
                (16, b.back + 17, 0.6, .6, .7, .6)], skin, 'scale', None)
    X.scales(m, shade(skin, 0.82))
    m.paint((220, 210, 150), None, parts=('chest', 'spine', 'hips'), where=lambda p, v: p[1] == b.front and abs(p[0] - 16) <= 2)
    if kind == 'desert':
        X.spines(m, (230, 190, 120), tip=(250, 230, 190), length=2, density=0.5, head=True, back=False)
        F.dress(m, belt=(120, 80, 50), buckle=(222, 184, 72), sash=(230, 214, 180))
    elif kind == 'croc':
        F.dress(m, plate=(110, 114, 122), pauldrons=(110, 114, 122), belt=(70, 50, 36), buckle=(222, 184, 72))
    else:
        crest(m, 'spines', (60, 100, 50), back=False)
        F.dress(m, belt=(120, 80, 50), buckle=(184, 128, 70), cape=(150, 60, 40))
    return m


def treat3(a, b, c):
    return [(a, 'Cartoon'), (b, 'TwoColor'), (c, 'CratePalette')]


SETS = [
    Set('Lizardfolk', 'Lizardfolk', designs(lizard, GENERIC), treat3(1, 2, 3),
        concepts=[('Stalker', lambda: lizard_concept('generic')), ('Thornback', lambda: lizard_concept('desert'))]),
    Set('Lizardfolk/Desert', 'Lizardfolk_Desert', designs(lizard, DESERT), treat3(1, 3, 4)),
    Set('Lizardfolk/Chameleonic', 'Lizardfolk_Chameleonic', designs(lizard, CHAMELEONIC), treat3(2, 1, 8)),
    Set('Lizardfolk/Water', 'Lizardfolk_Water', designs(lizard, WATER), treat3(1, 3, 8)),
    Set('Lizardfolk/Crocodile', 'Lizardfolk_Crocodile', designs(lizard, CROCODILE), treat3(1, 2, 5),
        concepts=[('Brute', lambda: lizard_concept('croc'))]),
]
