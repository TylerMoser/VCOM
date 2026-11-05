"""Plantfolk, generic and the four kinds: cactus, flower, carnivorous and poison. Bark, stems
and leaves for a hide; leaves, petals, caps, jaws and pitchers for a head."""
from .common import Set, designs, beast, EYES
from .mammals import treat3
from . import concepts_extra as CX
from core import shade, mix, sat
import heads as H
import outfits as O
import extras as X
import freebody as F

WHITE = (240, 238, 232)
GLOW = ('emit', 0.9, 1)
DEW = ('glass', 0.35)


def plant_face(m, hd, eye=(30, 40, 20), style='dot', mouth=None, z=None):
    z = z if z is not None else hd.z0 + 2
    H.eyes(m, hd, style, iris=eye, z=z, gap=3)
    if mouth:
        H.mouth(m, hd, 'smile', color=mouth, z=hd.z0 + 1 if z > hd.z0 + 2 else hd.z0, width=3)


def leaf(m, base, tip_dir, length, color, vein=None, bone='Head', width=1.6):
    """A leaf from [base] along [tip_dir] (a unit-ish vector), widest a third of the way."""
    vein = vein or shade(color, 0.8)
    bx, by, bz = base
    dx, dy, dz = tip_dir
    pts = []
    for k in range(length + 1):
        t = k / max(1, length)
        wdt = width * (1 - abs(t - 0.35) / 0.65) + 0.45
        pts.append((bx + dx * k, by + dy * k, bz + dz * k, wdt, 0.55 if abs(dy) < 0.5 else wdt, 0.55 if abs(dz) > 0.5 else wdt))
    X.sweep(m, pts, lambda t, p: vein if abs(t - 0.5) < 0.05 else color, 'plant', bone)


def sprout(color, size=5):
    def f(m):
        hd = m.head
        for k in range(1, 3):
            m.set((16, hd.y0 + 4, hd.z1 + k), shade(color, 0.8), 'plant', 'Head', 'head')
        leaf(m, (16, hd.y0 + 4, hd.z1 + 2), (-0.8, 0, 0.45), size, color)
        leaf(m, (16, hd.y0 + 4, hd.z1 + 2), (0.8, 0, 0.45), size, color)
    return f


def leaf_crown(colors, size=1):
    """A crown of leaves over the head: the hair's shape in leaf colours."""
    def f(m):
        hd = m.head
        H.hair(m, hd, colors[0], 'curly' if size == 1 else 'afro', fringe=True, highlight=colors[1] if len(colors) > 1 else None)
        for p, v in m.v.items():
            if v.group == 'hair' and v.part == 'head':
                v.group = 'plant'
                if X.h(p, 111) < 0.25 and len(colors) > 2:
                    v.color = colors[2]
    return f


def bark(color, dark=None):
    dark = dark or shade(color, 0.75)
    def f(m):
        for p, v in m.v.items():
            if v.group == 'bark' and ((p[0] + p[1]) % 3 == 0 or X.h(p, 113) < 0.2):
                v.color = dark
    return f


def moss_patches(color):
    def f(m):
        for p, v in m.v.items():
            if v.group in ('bark', 'plant') and X.h((p[0] // 2, p[1] // 2, p[2] // 2), 115) < 0.25:
                v.color = color
    return f


def cap(m, color, spots=None, under=(230, 220, 200), r=6.5, height=4, y_off=0, stem=None):
    """A mushroom's cap over the head, its gills underneath."""
    hd = m.head
    cy = (hd.y0 + hd.y1) / 2 + y_off
    for x in range(hd.x0 - 3, hd.x1 + 4):
        for y in range(hd.y0 - 3, hd.y1 + 4):
            for z in range(hd.z1 - 1, hd.z1 + height + 1):
                d = ((x + 0.5 - 16.5) / r) ** 2 + ((y + 0.5 - cy - 0.5) / r) ** 2 + ((z - (hd.z1 - 1)) / (height + 0.5)) ** 2
                if d > 1:
                    continue
                if z <= 19:
                    continue
                c = color
                if z == hd.z1 - 1 or (z == hd.z1 and d > 0.75):
                    c = under
                elif spots and X.h((x // 2, y // 2, z // 2), 117) < 0.22:
                    c = spots
                m.set((x, y, z), c, 'plant', 'Head', 'head')


def pumpkin_head(color=(230, 120, 30), stem=(90, 110, 40), glow=None):
    def f(m, hd):
        for p, v in m.v.items():
            if v.part == 'head' and v.group in ('plant', 'bark', 'skin'):
                v.color = shade(color, 0.85) if p[0] % 3 == 1 else color
                v.group = 'plant'
        for k in range(1, 3):
            m.set((16, hd.y0 + 4, hd.z1 + k), stem, 'plant', 'Head', 'head')
        m.set((17, hd.y0 + 4, hd.z1 + 2), stem, 'plant', 'Head', 'head')
        face = glow or (40, 30, 20)
        mat = GLOW if glow else None
        for (x, z) in ((13, hd.z0 + 4), (14, hd.z0 + 4), (14, hd.z0 + 5), (18, hd.z0 + 4), (19, hd.z0 + 4), (18, hd.z0 + 5),
                       (16, hd.z0 + 3), (13, hd.z0 + 1), (14, hd.z0 + 1), (15, hd.z0 + 1), (16, hd.z0 + 1), (17, hd.z0 + 1), (18, hd.z0 + 1),
                       (19, hd.z0 + 1), (14, hd.z0 + 2), (16, hd.z0 + 2), (18, hd.z0 + 2)):
            y = m.front_y(x, z)
            if y is not None:
                m.set((x, y, z), face, 'light' if glow else 'detail', 'Head', 'head', mat)
    return f


def vines(color):
    def f(m):
        for p, v in m.v.items():
            if v.part in ('uarm_r', 'larm_r', 'uarm_l', 'larm_l', 'uleg_r', 'lleg_r', 'uleg_l', 'lleg_l', 'chest', 'spine') and v.group in ('bark', 'plant'):
                k = (p[0] + p[2] * 2 + p[1]) % 5 if v.part.startswith(('uarm', 'larm')) else (p[2] + p[0] + p[1]) % 5
                if k == 0:
                    v.color = color
    return f


def plant(skin=(110, 160, 70), group='plant', head=None, head_color=None, eye=(30, 40, 20), eyes='dot', mouth=None, crown=None,
          pattern=None, outfit=None, outfit_kw=None, hat=False, extras=None, face=None, belly=None, eye_z=None):
    head = head or dict(w=9, d=8, h=8, style='round')
    def face_fn(m, hd):
        if face:
            face(m, hd)
        if eyes:
            plant_face(m, hd, eye, eyes, mouth, z=eye_z)
    def pat(m):
        if pattern:
            for f in (pattern if isinstance(pattern, (list, tuple)) else [pattern]):
                f(m)
    def after(m):
        if crown:
            crown(m)
        if extras:
            for f in (extras if isinstance(extras, (list, tuple)) else [extras]):
                f(m)
    return beast(skin, skin_group=group, head=head, head_color=head_color, eyes=None, face=face_fn, pattern=pat, belly_color=belly,
                 outfit=outfit, outfit_kw=outfit_kw, hat=hat, extras=after)


GREEN = (110, 160, 70)
BARK = (120, 86, 56)

GENERIC = [
    ('Sproutling', dict(skin=(150, 200, 90), crown=sprout((90, 180, 60)), mouth=(60, 90, 40), outfit='peasant', hat=False)),
    ('Treant', dict(skin=BARK, group='bark', pattern=bark(BARK), crown=leaf_crown([(70, 130, 50), (100, 160, 60), (60, 110, 40)]),
                    eye=(230, 200, 80), eyes='glow', outfit='nature_mage', hat=False)),
    ('Mossling', dict(skin=(90, 130, 60), pattern=moss_patches((60, 100, 40)), extras=lambda m: cap(m, (170, 120, 70), r=4.5, height=3),
                      outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('Porcini', dict(skin=(230, 220, 190), extras=lambda m: cap(m, (150, 90, 50), under=(230, 210, 150)), mouth=(120, 100, 70), outfit='monk',
                     hat=False, outfit_kw=dict(main=(150, 110, 60)))),
    ('Vinewalker', dict(skin=(80, 130, 60), pattern=vines((50, 90, 40)), crown=sprout((90, 160, 60), 4), outfit='ranger', hat=False)),
    ('Gourdhead', dict(skin=(90, 120, 50), face=pumpkin_head(glow=(255, 200, 80)), eyes=None, outfit='necromancer', hat=False,
                       outfit_kw=dict(main=(50, 40, 40), trim=(230, 120, 30)))),
    ('Willow', dict(skin=(170, 150, 110), group='bark', pattern=bark((170, 150, 110)),
                    crown=lambda m: (H.hair(m, m.head, (140, 180, 90), 'long', highlight=(170, 200, 110)),
                                     [setattr(v, 'group', 'plant') for p, v in m.v.items() if v.group == 'hair']),
                    outfit='white_mage', hat=False, eyes='closed', eye=(70, 60, 40))),
    ('Birch', dict(skin=(236, 232, 220), group='bark', pattern=lambda m: X.spots(m, (40, 40, 40), density=0.12),
                   crown=leaf_crown([(200, 210, 80), (230, 220, 100)]), outfit='bard', hat=False)),
    ('Acorn', dict(skin=(200, 150, 90), extras=lambda m: cap(m, (110, 80, 50), under=(140, 100, 60), r=5.2, height=2,
                                                            spots=(130, 96, 60)), outfit='warrior', hat=False)),
    ('Bamboo', dict(skin=(150, 190, 80), pattern=lambda m: m.paint((110, 150, 60), None, where=lambda p, v: v.group == 'plant' and p[2] % 4 == 0),
                    crown=sprout((120, 180, 70), 4), outfit='monk', hat=False, outfit_kw=dict(main=(220, 200, 150)))),
    ('Lichen', dict(skin=(150, 160, 140), pattern=moss_patches((190, 200, 120)), outfit='scholar', hat=False)),
    ('Autumn', dict(skin=BARK, group='bark', pattern=bark(BARK), crown=leaf_crown([(210, 90, 40), (240, 160, 50), (170, 50, 40)]),
                    outfit='hunter', hat=False)),
    ('Cabbage', dict(skin=(160, 200, 120), head=dict(w=11, d=9, h=8, style='round'),
                     extras=lambda m: [m.set(p, (130, 180, 100) if (p[0] + p[2]) % 3 else (190, 220, 150), 'plant', 'Head', 'head')
                                       for p in [(x, y, z) for x in range(m.head.x0 - 1, m.head.x1 + 2) for y in range(m.head.y0 + 2, m.head.y1 + 2)
                                                 for z in range(20, m.head.z1 + 2) if not m.has((x, y, z)) and (x in (m.head.x0 - 1, m.head.x1 + 1) or y == m.head.y1 + 1 or z == m.head.z1 + 1)]],
                     outfit='merchant', hat=False)),
    ('Bonsai', dict(skin=(120, 110, 90), group='bark',
                    extras=lambda m: (X.sweep(m, [(16, m.head.y0 + 4, m.head.z1 + 1, .7, .7, .7), (14, m.head.y0 + 4, m.head.z1 + 3, .6, .6, .6)], (100, 80, 60), 'bark', 'Head'),
                                      m.ellipsoid(13, m.head.y0 + 4, m.head.z1 + 4.5, 2.5, 2, 1.4, (60, 120, 60), 'plant', 'Head', 'head', only_empty=True),
                                      m.ellipsoid(18, m.head.y0 + 4, m.head.z1 + 3.5, 2, 1.8, 1.2, (70, 130, 60), 'plant', 'Head', 'head', only_empty=True)),
                    outfit='tactician', hat=False)),
]

# --- Cactus ----------------------------------------------------------------------------------

def ribs(color):
    def f(m):
        for p, v in m.v.items():
            if v.group == 'plant' and (p[0] % 2 == 0 if v.part not in ('uarm_r', 'larm_r', 'uarm_l', 'larm_l') else p[2] % 2 == 0):
                v.color = color
    return f


def prickles(color=(240, 236, 210), density=0.12):
    def f(m):
        surface = [p for p, v in m.v.items() if v.group == 'plant']
        for p in surface:
            if X.h(p, 121) > density:
                continue
            v = m.v[p]
            for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1)):
                q = (p[0] + d[0], p[1] + d[1], p[2] + d[2])
                if not m.has(q):
                    bone = v.bone or m.bone_of(p)
                    if bone in ('Chest', 'Spine', 'Hips') and X.arm_room(q):
                        break
                    if bone in ('RightUpperArm', 'RightLowerArm', 'RightHand', 'LeftUpperArm', 'LeftLowerArm', 'LeftHand') and 15 <= q[1] <= 17 and q[2] <= 16:
                        break
                    if bone == 'Chest' and q[2] >= 20 and q[1] <= 19 and 11 <= q[0] <= 21:
                        break
                    m.set(q, color, 'horn', bone, None)
                    break
    return f


def bloom(color, centre=(250, 220, 60), size=1):
    def f(m):
        hd = m.head
        z = hd.z1 + 1
        for (dx, dy) in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)) + (((-1, -1), (1, 1), (-1, 1), (1, -1)) if size > 1 else ()):
            m.set((16 + dx, hd.y0 + 4 + dy, z), color, 'petal', 'Head', 'head')
        for (dx, dy) in ((-2, 0), (2, 0), (0, -2), (0, 2)) if size > 1 else ():
            m.set((16 + dx, hd.y0 + 4 + dy, z), color, 'petal', 'Head', 'head')
        m.set((16, hd.y0 + 4, z + 1), centre, 'petal', 'Head', 'head')
    return f


def pads(color, fruit=None, bunny=False):
    """A prickly pear's pads standing up from the head (two, as ears, on a bunny cactus)."""
    def f(m):
        hd = m.head
        for side in (-1, 1):
            cx = 16 + side * (3 if bunny else 4)
            for x in range(cx - 2, cx + 3):
                for z in range(hd.z1, hd.z1 + 7):
                    if ((x - cx) / 2.4) ** 2 + ((z - hd.z1 - 3) / 3.6) ** 2 <= 1:
                        m.set((x, hd.y0 + 4, z), color, 'plant', 'Head', 'head')
            if fruit:
                m.set((cx, hd.y0 + 4, hd.z1 + 7), fruit, 'petal', 'Head', 'head')
    return f


def cactus(**kw):
    d = dict(skin=(90, 150, 70), head=dict(w=9, d=8, h=8, style='soft'), eyes='dot', eye=(30, 40, 20), mouth=(50, 90, 40))
    rib = kw.pop('rib', None)
    spines = kw.pop('spines', (240, 236, 210))
    flower = kw.pop('flower', None)
    ex = kw.pop('extras', None)
    d.update(kw)
    def extras(m):
        ribs(rib or shade(m.skin, 0.85))(m)
        if flower:
            bloom(*flower)(m)
        if ex:
            ex(m)
        if spines:
            prickles(spines)(m)
    d['extras'] = extras
    return plant(**d)


CACTI = [
    ('Saguaro', dict(flower=((250, 250, 240), (250, 220, 80), 2), outfit='gunslinger', hat=True)),
    ('Barrel', dict(skin=(80, 140, 70), head=dict(w=11, d=9, h=8, style='round'), spines=(250, 210, 60), flower=((230, 50, 60), (250, 220, 80), 1),
                    outfit='merchant', hat=False)),
    ('PricklyPear', dict(skin=(120, 170, 80), extras=pads((120, 170, 80), (200, 40, 90)), outfit='peasant', hat=False)),
    ('BunnyEars', dict(skin=(140, 180, 90), extras=pads((140, 180, 90), bunny=True), spines=(250, 240, 200), outfit='bard', hat=False)),
    ('MoonGraft', dict(skin=(80, 140, 70), head_color=(240, 70, 60), outfit='psychic', hat=False)),
    ('OldMan', dict(skin=(120, 160, 90), extras=lambda m: (H.hair(m, m.head, (246, 244, 240), 'long'), H.beard(m, m.head, (246, 244, 240), 'long')),
                    spines=None, outfit='scholar', hat=False)),
    ('Christmas', dict(skin=(70, 140, 60), flower=((240, 80, 140), (250, 200, 220), 2), outfit='cleric', hat=False)),
    ('Cholla', dict(skin=(150, 170, 90), spines=(250, 220, 120), outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('GoldenBarrel', dict(skin=(70, 130, 60), spines=(250, 200, 40), head=dict(w=11, d=9, h=8, style='round'), outfit='warrior', hat=False)),
    ('Star', dict(skin=(110, 130, 80), rib=(160, 170, 130), flower=((250, 220, 60), (240, 120, 40), 1), spines=None, outfit='monk', hat=False)),
    ('Rosette', dict(skin=(130, 170, 150), spines=None, extras=lambda m: [leaf(m, (16, m.head.y0 + 4, m.head.z1), (dx, dy, 0.6), 3, (140, 190, 160), width=1.1)
                                                                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0.7, 0.7), (-0.7, 0.7))],
                     outfit='white_mage', hat=False)),
    ('Desperado', dict(skin=(90, 140, 70), flower=((250, 120, 40), (250, 220, 80), 1), outfit='sharpshooter', hat=False)),
    ('Thornwarden', dict(skin=(80, 130, 60), spines=(220, 220, 200), outfit='guardian', hat=False, outfit_kw=dict(cape=False))),
]

# --- Flower ----------------------------------------------------------------------------------

def petal_ring(colors, size=3, layers=1, shape='round'):
    """Petals in a ring round the face, behind it, out past the head's sides and top; over the
    arms they stop at z 19. [shape] round, pointed (a daisy's narrow rays) or cup (a tulip's)."""
    def f(m):
        hd = m.head
        y = hd.y0 + 2
        cx, cz = 16.5, (hd.z0 + hd.z1) / 2 + 0.5
        rx, rz = hd.w / 2, hd.h / 2
        for layer in range(layers):
            yy = y + layer
            grow = size - layer
            for x in range(hd.x0 - grow - 1, hd.x1 + grow + 2):
                for z in range(19, hd.z1 + grow + 2):
                    held = m.get((x, yy, z))
                    if held is not None and held.part != 'head':
                        continue  # never over the body (the neck, the shoulders)
                    nx = (x + 0.5 - cx) / (rx + grow)
                    nz = (z + 0.5 - cz) / (rz + grow)
                    d = nx * nx + nz * nz
                    inner = ((x + 0.5 - cx) / rx) ** 2 + ((z + 0.5 - cz) / rz) ** 2 <= 1.0
                    if d > 1 or inner:
                        continue
                    if z <= 19 and (x <= 13 or x >= 19) and 14 <= yy <= 18:
                        continue
                    if shape == 'pointed':
                        import math
                        a = math.atan2(nz, nx)
                        if math.cos(a * 12) < -0.2 and d > 0.55:
                            continue
                    if shape == 'cup' and z < cz - 1:
                        continue
                    c = colors[layer % len(colors)]
                    if d > 0.85 and len(colors) > layers:
                        c = colors[-1]
                    m.set((x, yy, z), c, 'petal', 'Head', 'head')
    return f


def leaf_sleeves(color):
    """Leaves hanging behind the arms (y 18), on the arms' bones."""
    def f(m):
        X.arm_wings(m, color, tip=shade(color, 0.8), depth=3, second=shade(color, 1.1))
        for p, v in m.v.items():
            if v.group == 'feather':
                v.group = 'plant'
    return f


def flower(**kw):
    d = dict(skin=(90, 160, 70), head=dict(w=9, d=7, h=8, style='round'), eyes='dot', eye=(40, 30, 20), mouth=(90, 60, 30))
    petals = kw.pop('petals', None)
    sleeves = kw.pop('sleeves', (90, 160, 70))
    ex = kw.pop('extras', None)
    d.update(kw)
    def extras(m):
        if petals:
            petal_ring(*petals)(m) if isinstance(petals, tuple) else petals(m)
        if sleeves:
            leaf_sleeves(sleeves)(m)
        if ex:
            ex(m)
    d['extras'] = extras
    return plant(**d)


def bells(color, count=3):
    def f(m):
        hd = m.head
        for i in range(count):
            y = hd.y0 + 2 + i * 2
            z = hd.z1 + 1 + i
            m.set((16, y, z + 1), (80, 140, 60), 'plant', 'Head', 'head')
            for (dx, dz) in ((0, 0), (-1, 0), (1, 0), (0, -1), (-1, -1), (1, -1)):
                m.set((16 + dx, y - 1, z + dz), color, 'petal', 'Head', 'head')
    return f


def seed_puff(m):
    hd = m.head
    m.ellipsoid(16.5, (hd.y0 + hd.y1) / 2 + 0.5, (hd.z0 + hd.z1) / 2 + 0.5, hd.w / 2 + 2.2, hd.d / 2 + 2, hd.h / 2 + 2, (246, 246, 240), 'petal',
                'Head', 'head', only_empty=True, where=lambda p: p[2] >= 20 and (X.h(p, 131) < 0.55))


FLOWERS = [
    ('Sunflower', dict(head_color=(120, 80, 40), petals=([(250, 200, 40), (240, 170, 30)], 3, 2), eye=(30, 20, 10), outfit='peasant', hat=False)),
    ('Daisy', dict(head_color=(250, 210, 60), petals=([(250, 250, 246)], 3, 1, 'pointed'), outfit='white_mage', hat=False)),
    ('Rose', dict(head_color=(220, 40, 50), petals=([(200, 30, 40), (240, 60, 70)], 2, 2, 'cup'), eye=(40, 10, 10), mouth=(120, 20, 30),
                  extras=prickles((60, 90, 40), 0.06), outfit='noble', hat=False)),
    ('Tulip', dict(head_color=(230, 80, 140), petals=([(230, 80, 140), (250, 140, 180)], 2, 1, 'cup'), outfit='bard', hat=False)),
    ('Lily', dict(head_color=(250, 246, 236), petals=([(250, 246, 236), (240, 170, 80)], 3, 1, 'pointed'), eye=(150, 90, 40), outfit='cleric', hat=False)),
    ('Lotus', dict(head_color=(250, 200, 210), petals=([(240, 150, 180), (250, 200, 210)], 3, 2), outfit='monk', hat=False,
                   outfit_kw=dict(main=(240, 150, 180), trim=(250, 220, 120)))),
    ('Poppy', dict(head_color=(30, 30, 30), petals=([(230, 40, 30), (200, 30, 26)], 3, 1), eye=(230, 220, 180), eyes='pupil', outfit='psychic', hat=False)),
    ('Dandelion', dict(head_color=(240, 220, 120), extras=seed_puff, petals=None, eye=(80, 70, 40), outfit='scout', hat=False,
                       outfit_kw=dict(quiver=False))),
    ('Orchid', dict(head_color=(250, 240, 250), petals=([(190, 90, 200), (240, 200, 245)], 3, 1), extras=lambda m: X.spots(m, (150, 50, 160), density=0.05, head=False),
                    outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Bluebell', dict(head_color=(160, 190, 120), extras=bells((90, 110, 220), 3), petals=None, outfit='water_mage', hat=False)),
    ('Hibiscus', dict(head_color=(250, 200, 100), petals=([(230, 50, 90), (250, 120, 150)], 3, 1), outfit='sailor', hat=False)),
    ('Marigold', dict(head_color=(240, 140, 30), petals=([(240, 140, 30), (250, 180, 50), (220, 100, 20)], 2, 3), outfit='fire_mage', hat=False)),
]

# --- Carnivorous -----------------------------------------------------------------------------

def flytrap(color=(120, 180, 60), inside=(210, 60, 60), teeth=(220, 240, 160), big=False):
    """The head as a flytrap's jaws: an upper and a lower lobe, red inside, cilia along both."""
    def f(m, hd):
        for p, v in list(m.v.items()):
            if v.part == 'head':
                del m.v[p]
        w = 11 if big else 9
        x0, x1 = 16 - w // 2, 16 + w // 2
        y0, y1 = 11, 19
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                ex = (x in (x0, x1)) + (y in (y0, y1))
                # lower lobe
                for z in (20, 21):
                    if ex >= 2 and z == 20:
                        continue
                    m.set((x, y, z), color if z == 20 or ex else inside, 'plant', 'Head', 'head')
                # upper lobe, open, leaning back
                for z in (24, 25, 26):
                    yy = y + (z - 24)
                    if ex >= 2 and z == 26:
                        continue
                    m.set((x, yy, z), inside if z == 24 and not ex else color, 'plant', 'Head', 'head')
        for x in range(x0, x1 + 1):
            m.set((x, y0 - 1, 22 if x % 2 else 21), teeth, 'horn', 'Head', 'head')
            m.set((x, y0 - 1, 23 if x % 2 == 0 else 24), teeth, 'horn', 'Head', 'head')
        for z in (22, 23):
            for y in range(y0 + 4, y1 + 2):
                m.set((16, y, z), shade(color, 0.85), 'plant', 'Head', 'head')
        for side in (-1, 1):
            m.set((16 + side * 2, y0 + 3, 27), (250, 240, 200), 'eye', 'Head', 'head')
            m.set((16 + side * 2, y0 + 2, 27), (30, 30, 20), 'eye', 'Head', 'head')
        hd.x0, hd.x1, hd.y0, hd.y1, hd.z0, hd.z1 = x0, x1, y0, y1 + 2, 20, 26
    return f


def pitcher(color=(120, 160, 60), rim=(180, 40, 50), veins=(170, 60, 70), lid=True):
    def f(m, hd):
        for p, v in m.v.items():
            if v.part == 'head':
                v.color = veins if (p[2] + p[0]) % 4 == 0 else color
        for x in range(hd.x0, hd.x1 + 1):
            for y in range(hd.y0, hd.y1 + 1):
                if x in (hd.x0, hd.x1) or y in (hd.y0, hd.y1):
                    m.set((x, y, hd.z1 + 1), rim, 'plant', 'Head', 'head')
        if lid:
            for x in range(hd.x0 + 1, hd.x1):
                for y in range(hd.y0 + 2, hd.y1 + 2):
                    m.set((x, y + (1 if y > hd.y1 - 2 else 0), hd.z1 + 3 + (y - hd.y0) // 3), color, 'plant', 'Head', 'head')
    return f


def sundew(color=(200, 60, 60), dew=(230, 250, 220)):
    def f(m):
        hd = m.head
        for x in range(hd.x0, hd.x1 + 1, 2):
            for y in range(hd.y0 + 1, hd.y1 + 1, 2):
                for k in (1, 2):
                    m.set((x, y, hd.z1 + k), color, 'plant', 'Head', 'head')
                m.set((x, y, hd.z1 + 3), dew, 'glass', 'Head', 'head', DEW)
    return f


def cobra_lily(color=(150, 170, 80), hood=(200, 120, 90)):
    def f(m):
        from .reptiles import hood as snake_hood
        snake_hood(m, color, mark=hood)
        hd = m.head
        for k in range(3):
            m.set((15 + k % 2 * 2, hd.y0 - 1, hd.z0 - k), hood, 'petal', 'Head', 'head')
    return f


CARNIVOROUS = [
    ('Flytrap', dict(face=flytrap(), eyes=None, outfit='barbarian', hat=False, outfit_kw=dict(paint=False))),
    ('Gnasher', dict(face=flytrap((90, 140, 50), (180, 30, 50), big=True), eyes=None, outfit='heavy', hat=False)),
    ('Duskjaw', dict(skin=(90, 60, 110), face=flytrap((110, 70, 130), (230, 60, 90)), eyes=None, outfit='necromancer', hat=False)),
    ('Snapper', dict(face=flytrap((140, 190, 70), (240, 120, 60)), eyes=None, outfit='assault', hat=False)),
    ('Pitcher', dict(face=pitcher(), outfit='apothecary', hat=False)),
    ('MonkeyCup', dict(skin=(100, 140, 60), face=pitcher((200, 60, 60), (240, 200, 80), (160, 40, 40)), outfit='merchant', hat=False)),
    ('Trumpet', dict(skin=(150, 170, 80), face=pitcher((200, 210, 110), (200, 60, 50), (180, 80, 70)), head=dict(w=9, d=8, h=10, style='round'),
                     outfit='bard', hat=False)),
    ('Sundew', dict(skin=(160, 190, 90), extras=sundew(), outfit='psychic', hat=False)),
    ('Dewdrop', dict(skin=(190, 70, 70), extras=sundew((220, 90, 90)), outfit='white_mage', hat=False)),
    ('CobraLily', dict(skin=(150, 170, 80), extras=cobra_lily(), outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Butterwort', dict(skin=(190, 220, 110), extras=lambda m: [leaf(m, (16, m.head.y0 + 4, m.head.z1), (dx, dy, 0.3), 4, (200, 230, 120), width=1.4)
                                                              for dx, dy in ((1, 0), (-1, 0), (0, 1), (0.7, -0.7), (-0.7, -0.7))], outfit='scholar', hat=False)),
    ('Corpsebloom', dict(skin=(120, 60, 50), extras=petal_ring([(170, 50, 40), (230, 200, 190)], 4, 1),
                         outfit='necromancer', hat=False, mouth=(60, 20, 20))),
]

# --- Poison ----------------------------------------------------------------------------------

def triple_leaves(color, red=None):
    def f(m):
        hd = m.head
        for (bx, d1, d2, d3) in ((15, (-0.9, 0, 0.4), (0, 0, 1), (0.9, 0, 0.4)),):
            base = (16, hd.y0 + 4, hd.z1 + 1)
            for i, d in enumerate((d1, d2, d3)):
                leaf(m, base, d, 4, red if (red and i == 1) else color, width=1.5)
        for x, side in ((12, -1), (20, 1)):
            for i, d in enumerate(((side * 0.6, 0, 0.8), (side * 0.9, 0.2, 0.1))):
                leaf(m, (x, 16, 19), d, 3, color, bone='RightUpperArm' if side < 0 else 'LeftUpperArm', width=1.0)
    return f


def berries(color, count=5):
    def f(m):
        hd = m.head
        spots = [(13, hd.z1 + 1), (15, hd.z1 + 2), (17, hd.z1 + 1), (19, hd.z1 + 2), (16, hd.z1 + 3)][:count]
        for (x, z) in spots:
            m.set((x, hd.y0 + 3, z), color, 'petal', 'Head', 'head')
            m.set((x, hd.y0 + 4, z - 1), (60, 90, 40), 'plant', 'Head', 'head')
    return f


def spores(color):
    def f(m):
        hd = m.head
        for i in range(10):
            x = 11 + int(X.h((i, 0, 0), 141) * 11)
            y = hd.y0 + int(X.h((i, 1, 0), 141) * 8)
            z = hd.z1 + 2 + int(X.h((i, 2, 0), 141) * 5)
            m.set((x, y, z), color, 'light', 'Head', 'head', GLOW)
    return f


def mandrake(m):
    for p, v in m.v.items():
        if v.group in ('plant', 'bark') and v.part in ('chest', 'spine', 'hips', 'uleg_r', 'uleg_l', 'lleg_r', 'lleg_l'):
            if X.h(p, 151) < 0.2:
                v.color = shade(v.color, 0.8)


POISON = [
    ('PoisonIvy', dict(skin=(100, 150, 60), extras=triple_leaves((80, 150, 50), (200, 50, 40)), outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Nightshade', dict(skin=(80, 100, 60), extras=[berries((30, 20, 40)), lambda m: bloom((140, 60, 200), (250, 220, 60), 1)(m)], outfit='necromancer',
                        hat=False)),
    ('Foxglove', dict(skin=(90, 140, 60), extras=bells((190, 90, 200), 4), outfit='apothecary', hat=False)),
    ('Hemlock', dict(skin=(150, 180, 110), pattern=lambda m: X.spots(m, (130, 50, 80), density=0.12), extras=lambda m: bloom((250, 250, 240), (240, 240, 220), 2)(m),
                     outfit='scholar', hat=False)),
    ('DeathCap', dict(skin=(230, 226, 200), extras=lambda m: cap(m, (200, 210, 160), under=(240, 240, 230), r=6), outfit='psychic', hat=False,
                      eye=(60, 80, 40))),
    ('FlyAgaric', dict(skin=(240, 236, 220), extras=lambda m: cap(m, (220, 40, 30), spots=(250, 250, 246), under=(246, 240, 220)), outfit='bard', hat=False)),
    ('Oleander', dict(skin=(90, 140, 70), extras=lambda m: bloom((240, 130, 170), (250, 230, 200), 2)(m), outfit='noble', hat=False)),
    ('Belladonna', dict(skin=(70, 90, 50), extras=berries((40, 20, 50), 5), outfit='white_mage', hat=False, outfit_kw=dict(main=(60, 40, 70), trim=(150, 100, 170)))),
    ('Wolfsbane', dict(skin=(80, 120, 60), extras=bells((80, 70, 200), 3), outfit='hunter', hat=False)),
    ('Mandrake', dict(skin=(190, 160, 110), group='bark', pattern=mandrake, crown=leaf_crown([(80, 140, 60), (110, 170, 70)]), mouth=(60, 30, 20),
                      eyes='angry', outfit='tribal', hat=False)),
    ('Sporecaller', dict(skin=(170, 160, 140), extras=[lambda m: cap(m, (150, 130, 90), under=(220, 210, 180), r=5, height=3), spores((150, 255, 120))],
                         outfit='earth_mage', hat=False)),
    ('Thornvine', dict(skin=(50, 40, 50), pattern=vines((120, 60, 160)), extras=prickles((150, 80, 180), 0.08), eye=(200, 120, 255), eyes='glow',
                       outfit='rogue', hat=False, outfit_kw=dict(main=(40, 34, 44)))),
]


def treant_concept(kind):
    """A tree walking: a trunk of a body, branching arms, roots for feet, a canopy."""
    barkc = (120, 86, 56) if kind != 'birch' else (230, 226, 214)
    m = F.body(barkc, 'bark', leg=9, leg_w=3, leg_d=3, gap=1, torso_w=9, torso_d=6, torso_h=16, arm_len=14, arm_w=2, arm_d=2,
               arm_pose='a', head=dict(w=9, d=8, h=8, style='soft'), neck=0, foot_len=2)
    hd = m.head
    H.eyes(m, hd, 'glow', iris=(230, 200, 80), z=hd.z0 + 3)
    bark(barkc)(m) if kind != 'birch' else X.spots(m, (40, 40, 40), density=0.12)
    m.ellipsoid(16.5, 16, hd.z1 + 4, 9, 7.5, 6, (70, 130, 50) if kind != 'autumn' else (210, 100, 40), 'plant', only_empty=True,
                where=lambda p: X.h(p, 161) < 0.85)
    for p, v in m.v.items():
        if v.group == 'plant' and X.h(p, 162) < 0.3:
            v.color = (100, 160, 60) if kind != 'autumn' else (240, 160, 50)
    b = m.body
    for side in (-1, 1):
        for k in range(4):
            m.set((16 + side * (3 + k), b.cy - 3 - k // 2, 0), barkc, 'bark')
            m.set((16 + side * (3 + k), b.cy + 2 + k // 2, 0), barkc, 'bark')
    return m


SETS = [
    Set('Plantfolk', 'Plantfolk', designs(plant, GENERIC), treat3(1, 2, 3),
        concepts=[('Treant', lambda: treant_concept('oak')), ('AutumnTreant', lambda: treant_concept('autumn'))]),
    Set('Plantfolk/Cactus', 'Plantfolk_Cactus', designs(cactus, CACTI), treat3(1, 2, 3)),
    Set('Plantfolk/Flower', 'Plantfolk_Flower', designs(flower, FLOWERS), treat3(1, 2, 3)),
    Set('Plantfolk/Carnivorous', 'Plantfolk_Carnivorous', designs(plant, CARNIVOROUS), treat3(1, 2, 5), concepts=[('Walker', CX.walking_flytrap)]),
    Set('Plantfolk/Poison', 'Plantfolk_Poison', designs(plant, POISON), treat3(6, 1, 2)),
]
