"""Dinosaurs: raptors, tyrants, horned, plated, armoured, domed, crested and sailed folk, and a
pterosaur."""
from .common import Set, designs, beast, EYES
from .mammals import treat3
from .lizards import side_eyes, crest
from core import shade, mix
import heads as H
import outfits as O
import extras as X
import freebody as F

WHITE = (240, 238, 232)
TEETH = (240, 236, 220)


def dino(scale=(90, 140, 70), belly=(220, 210, 160), head=None, snout=None, iris=(230, 190, 50), tail='lizard', tail_tip=None,
         pattern=None, outfit=None, outfit_kw=None, hat=False, extras=None, feathers=None, feather_tip=None, eye_style='side',
         head_color=None, group='scale', teeth=TEETH, claws=True):
    iris = EYES.get(iris, iris) if isinstance(iris, str) else iris
    head = head or dict(w=9, d=8, h=7, style='soft')
    sn = dict(length=3, w=5, h=3, taper=1, color=shade(head_color or scale, 1.06), jaw=belly, mouth=(80, 40, 40))
    if teeth:
        sn['teeth'] = teeth
    sn.update(snout or {})
    def face(m, hd):
        m.head_skin = head_color or scale
        side_eyes(m, hd, iris, z=hd.z0 + 3, style='slit', bulge=eye_style == 'bulge')
    def pat(m):
        if pattern:
            for f in (pattern if isinstance(pattern, (list, tuple)) else [pattern]):
                f(m)
    def after(m):
        if feathers:
            X.arm_wings(m, feathers, tip=feather_tip, depth=3, reach=0)
            hd = m.head
            for y in range(hd.y0 + 2, hd.y1 + 2):
                m.set((16, y, hd.z1 + 1), feathers, 'feather', 'Head', 'head')
                if y % 2:
                    m.set((16, y + 1, hd.z1 + 2), feather_tip or shade(feathers, 0.8), 'feather', 'Head', 'head')
        if extras:
            for f in (extras if isinstance(extras, (list, tuple)) else [extras]):
                f(m)
    return beast(scale, skin_group=group, head=head, muzzle=sn, eyes=None, belly_color=belly, face=face, pattern=pat, tail=tail,
                 tail_tip=tail_tip, hands='claws' if claws else None, hand_color=(230, 224, 200), outfit=outfit, outfit_kw=outfit_kw,
                 hat=hat, extras=after, head_color=head_color)


def sickle(m, color=(230, 224, 200)):
    for x in (14, 18):
        m.set((x, 12, 1), color, 'bone', 'RightFoot' if x < 16 else 'LeftFoot')
        m.set((x, 12, 0), color, 'bone', 'RightFoot' if x < 16 else 'LeftFoot')


def three_horns(m, color=(232, 222, 196)):
    hd = m.head
    tip, half, z, hgt, ln = m.snout_info
    m.set((16, tip + 1, z + hgt), color, 'horn', 'Head', 'head')
    m.set((16, tip + 1, z + hgt + 1), shade(color, 1.1), 'horn', 'Head', 'head')
    for x in (hd.x0 + 1, hd.x1 - 1):
        for k in range(1, 5):
            m.set((x, hd.y0 + 1 - k // 2, hd.z1 + k), color if k < 4 else shade(color, 1.15), 'horn', 'Head', 'head')


def beak_tip(color=(80, 70, 60)):
    def f(m):
        tip, half, z, hgt, ln = m.snout_info
        for zz in range(z, z + hgt):
            m.set((16, tip - 1, zz), color, 'horn', 'Head', 'head')
        m.set((16, tip - 2, z), color, 'horn', 'Head', 'head')
    return f


def dome(color, knobs=None):
    def f(m):
        hd = m.head
        m.ellipsoid(16.5, (hd.y0 + hd.y1) / 2 + 0.5, hd.z1 - 0.5, hd.w / 2 + 0.3, hd.d / 2, 3.2, color, 'bone', 'Head', 'head', only_empty=True,
                    where=lambda p: p[2] > hd.z1 - 1)
        if knobs:
            for x in range(hd.x0, hd.x1 + 1, 2):
                m.set((x, hd.y1, hd.z1 - 1), knobs, 'bone', 'Head', 'head')
                m.set((x, hd.y0 + 1, hd.z1), knobs, 'bone', 'Head', 'head')
    return f


def tube_crest(color):
    def f(m):
        hd = m.head
        pts = [(16, hd.y0 + 3, hd.z1, 1.2, 1.2, 1.2), (16, hd.y1, hd.z1 + 3, 1.1, 1.1, 1.1), (16, hd.y1 + 4, hd.z1 + 4, 1, 1, 1),
               (16, hd.y1 + 7, hd.z1 + 3, .8, .8, .8)]
        X.sweep(m, pts, color, 'bone', 'Head')
    return f


def double_crest(color, edge=None):
    edge = edge or shade(color, 0.7)
    def f(m):
        hd = m.head
        for x in (15, 17):
            for i, y in enumerate(range(hd.y0 - 1, hd.y1)):
                hgt = min(3, 1 + i // 2) if i < 6 else 2
                for k in range(1, hgt + 1):
                    m.set((x, y, hd.z1 + k), edge if k == hgt else color, 'bone', 'Head', 'head')
    return f


def horns_above(color=(232, 222, 196)):
    def f(m):
        hd = m.head
        for x in (hd.x0, hd.x1):
            out = -1 if x < 16 else 1
            m.set((x + out, hd.y0 + 2, hd.z1), color, 'horn', 'Head', 'head')
            m.set((x + out * 2, hd.y0 + 2, hd.z1 + 1), shade(color, 1.1), 'horn', 'Head', 'head')
    return f


def thumb_spikes(color=(230, 224, 200)):
    def f(m):
        for x, bone in ((5, 'RightHand'), (27, 'LeftHand')):
            m.set((x, 14, 18), color, 'bone', bone)
            m.set((x, 13, 18), color, 'bone', bone)
    return f


def long_claws(color=(230, 224, 200)):
    def f(m):
        for side, x0, step, bone in (('r', 3, -1, 'RightHand'), ('l', 29, 1, 'LeftHand')):
            for y in (15, 16, 17):
                for k in range(3):
                    m.set((x0 + step * k, y, 18 - (k // 2)), color, 'bone', bone)
    return f


def anky_armour(color, stud=None):
    stud = stud or shade(color, 1.25)
    def f(m):
        X.turtle_shell(m, color, rim=shade(color, 0.8), scute=shade(color, 0.9), depth=3, top=19, bottom=8)
        for p, v in list(m.v.items()):
            if v.group == 'shell' and (p[0] + p[2]) % 3 == 0 and p[1] >= 20:
                q = (p[0], p[1] + 1, p[2])
                if not m.has(q):
                    m.set(q, stud, 'shell', 'Chest')
        hd = m.head
        for x in (hd.x0 - 1, hd.x1 + 1):
            m.set((x, hd.y1 - 1, hd.z0 + 3), stud, 'shell', 'Head', 'head')
            m.set((x, hd.y1, hd.z0 + 4), stud, 'shell', 'Head', 'head')
    return f


def sail(color, edge=None):
    edge = edge or shade(color, 0.7)
    def f(m):
        for z in range(9, 20):
            hgt = 2 + min(z - 9, 19 - z) // 2
            for k in range(hgt):
                y = 18 + k
                zz = z
                if zz >= 20 and y < 20:
                    continue
                m.set((16, y, zz), edge if k == hgt - 1 else color, 'skin', 'Chest')
        for k in range(4):
            for z in range(20, 23 - k // 2):
                m.set((16, 20 + k, z), edge if k == 3 else color, 'skin', 'Chest')
    return f


def ptero_crest(color):
    def f(m):
        hd = m.head
        for k in range(6):
            m.set((16, hd.y1 + 1 + k, hd.z1 - k // 3), color, 'bone', 'Head', 'head')
            if k < 4:
                m.set((16, hd.y1 + k, hd.z1 + 1 - k // 3), color, 'bone', 'Head', 'head')
    return f


def stripes_back(color):
    return lambda m: X.stripes(m, color, period=3, head=True)


DINOS = [
    ('Raptor', dict(scale=(150, 110, 70), belly=(230, 210, 170), feathers=(120, 80, 50), feather_tip=(220, 200, 160), snout=dict(length=4, taper=1),
                    extras=sickle, pattern=stripes_back((100, 70, 40)), outfit='scout', hat=False, outfit_kw=dict(quiver=False))),
    ('Tyrant', dict(scale=(90, 100, 70), belly=(200, 190, 150), head=dict(w=11, d=10, h=8, style='soft'), snout=dict(length=4, w=7, h=4, taper=1),
                    outfit='barbarian', hat=False, outfit_kw=dict(paint=False))),
    ('Triceratops', dict(scale=(120, 130, 90), belly=(210, 200, 160), head=dict(w=9, d=8, h=7, style='soft'), snout=dict(length=3, w=5, h=3, taper=2),
                         teeth=None, extras=[beak_tip(), three_horns, lambda m: X.frill(m, (170, 120, 70), edge=(110, 70, 40), size=4, spikes=True)],
                         outfit='guardian', hat=False, outfit_kw=dict(cape=False))),
    ('Stegosaur', dict(scale=(110, 130, 80), belly=(200, 200, 150), head=dict(w=7, d=8, h=6, style='soft'), teeth=None, tail='spikes',
                       tail_tip=(220, 210, 180), extras=lambda m: X.back_plates(m, (200, 110, 60), edge=(150, 70, 40)), outfit='warrior', hat=False)),
    ('Ankylosaur', dict(scale=(130, 110, 80), belly=(200, 180, 140), tail='club', tail_tip=(150, 130, 100), teeth=None,
                        extras=anky_armour((150, 130, 90)), outfit='heavy', hat=False)),
    ('Domehead', dict(scale=(170, 140, 90), belly=(230, 210, 170), teeth=None, extras=dome((210, 180, 130), (240, 220, 180)), outfit='monk', hat=False,
                      outfit_kw=dict(main=(160, 50, 40)))),
    ('Crestback', dict(scale=(90, 140, 120), belly=(220, 220, 180), teeth=None, extras=tube_crest((200, 90, 50)), outfit='bard', hat=False)),
    ('Spinosaur', dict(scale=(120, 110, 80), belly=(220, 200, 150), snout=dict(length=6, w=3, h=2, taper=0), extras=sail((200, 80, 50)),
                       outfit='pirate', hat=True, outfit_kw=dict(eyepatch=False))),
    ('Dilophosaur', dict(scale=(150, 170, 60), belly=(230, 230, 160), extras=[double_crest((220, 60, 40)),
                                                                             lambda m: X.frill(m, (240, 200, 60), edge=(200, 60, 40), size=3)],
                         outfit='psychic', hat=False)),
    ('Pteranodon', dict(scale=(160, 130, 100), belly=(230, 210, 180), snout=dict(length=5, w=3, h=2, taper=1, color=(220, 180, 90)), teeth=None,
                        extras=[ptero_crest((220, 120, 60)), lambda m: X.bat_wings(m, (140, 100, 70), frame=(90, 60, 40), depth=7, reach=2)],
                        tail='stub', outfit='sharpshooter', hat=False)),
    ('Carnotaur', dict(scale=(170, 60, 40), belly=(230, 180, 140), head=dict(w=9, d=8, h=7, style='soft'), snout=dict(length=3, taper=0),
                       extras=horns_above(), outfit='gladiator', hat=False)),
    ('Iguanodon', dict(scale=(110, 140, 90), belly=(210, 210, 170), teeth=None, extras=thumb_spikes(), outfit='peasant', hat=True)),
    ('Compy', dict(scale=(120, 170, 70), belly=(230, 230, 170), head=dict(w=9, d=8, h=7, style='round'), snout=dict(length=2, w=3, h=2, taper=0),
                   pattern=stripes_back((80, 120, 50)), outfit='rogue', hat=False, outfit_kw=dict(mask=False))),
    ('Clawreaper', dict(scale=(150, 140, 110), feathers=(170, 150, 110), feather_tip=(110, 90, 60), teeth=None, extras=long_claws(),
                        snout=dict(length=2, taper=1), outfit='smith', hat=False)),
    ('Utahraptor', dict(scale=(80, 90, 100), belly=(200, 200, 200), feathers=(60, 70, 90), feather_tip=(200, 60, 40), extras=sickle,
                        outfit='assault', hat=False)),
]


def rex_concept():
    """A tyrant as it stands: leaning forward over its legs, a great head, the arms small."""
    c = (90, 100, 70)
    m = F.body(c, 'scale', leg=11, leg_w=3, leg_d=4, gap=3, torso_w=9, torso_d=7, torso_h=10, arm_len=4, arm_w=1, arm_d=1,
               arm_pose='a', head=dict(w=11, d=12, h=9, style='soft'), neck=2, foot_len=4, head_forward=5)
    hd = m.head
    m.head_skin = c
    H.snout(m, hd, shade(c, 1.06), length=5, w=9, h=4, taper=1, jaw=(200, 190, 150), teeth=TEETH, mouth=(80, 40, 40))
    side_eyes(m, hd, (230, 170, 40), z=hd.z0 + 5)
    b = m.body
    X.sweep(m, [(16, b.back + 1, b.hip + 3, 3, 2.5, 3), (16, b.back + 7, b.hip + 1, 2.2, 2.2, 2), (16, b.back + 13, b.hip - 1, 1.3, 1.3, 1.2),
                (16, b.back + 18, b.hip - 2, .7, .7, .7)], c, 'scale', None)
    X.scales(m, shade(c, 0.82))
    m.paint((200, 190, 150), None, parts=('chest', 'spine', 'hips'), where=lambda p, v: p[1] == b.front)
    F.dress(m, belt=(70, 50, 36), buckle=(184, 128, 70))
    return m


def brachio_concept():
    """A long-necked giant: four legs under it, its head high."""
    c = (120, 140, 110)
    m = F.body(c, 'scale', leg=8, leg_w=3, leg_d=3, gap=3, torso_w=11, torso_d=10, torso_h=9, arm_len=8, arm_w=3, arm_d=3,
               arm_pose='down', head=dict(w=7, d=8, h=6, style='soft'), neck=1, foot_len=0, head_forward=0)
    # move the head and arms: the arms become front legs, the head rides up on a long neck
    b = m.body
    H.snout(m, m.head, shade(c, 1.06), length=2, w=5, h=2, taper=1, nostrils=True)
    H.eyes(m, m.head, 'dot', iris=(30, 28, 32), gap=5, z=m.head.z0 + 3)
    head_cells = {p: v for p, v in m.v.items() if v.part == 'head'}
    for p in head_cells:
        del m.v[p]
    for p, v in head_cells.items():
        m.v[(p[0], p[1] - 10, p[2] + 12)] = v
    X.sweep(m, [(16, b.front + 2, b.top, 3, 3, 3), (16, b.front - 3, b.top + 6, 2.2, 2.2, 2.2), (16, b.front - 7, b.top + 12, 1.8, 1.8, 1.8)], c, 'scale', None)
    for p, v in list(m.v.items()):
        if (v.part or '').startswith(('uarm', 'larm', 'hand')):
            del m.v[p]
    for x0 in (11, 19):
        for x in range(x0, x0 + 3):
            for y in range(b.front + 1, b.front + 4):
                for z in range(0, b.hip + 2):
                    m.set((x, y, z), c, 'scale', None, 'uleg_r')
    X.sweep(m, [(16, b.back + 1, b.hip + 4, 3, 2.5, 3), (16, b.back + 8, b.hip + 1, 2, 2, 2), (16, b.back + 14, 2, 1, 1, 1)], c, 'scale', None)
    X.scales(m, shade(c, 0.85))
    return m


SETS = [
    Set('Dinosaur', 'Dinosaur', designs(dino, DINOS), treat3(1, 3, 2),
        concepts=[('Tyrant', rex_concept), ('Longneck', brachio_concept)]),
]
