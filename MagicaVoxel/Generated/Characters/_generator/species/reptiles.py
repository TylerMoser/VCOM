"""Snakefolk (hooded, banded, rattling, horned) and Turtlefolk (shelled, beaked)."""
from .common import Set, designs, beast, EYES
from .lizards import side_eyes
from core import shade, mix
import heads as H
import outfits as O
import extras as X
import freebody as F

# --- Snakefolk -------------------------------------------------------------------------------

def tongue(m, color=(200, 40, 60)):
    hd = m.head
    tip, half, z, hgt, ln = m.snout_info
    m.set((16, tip - 1, z), color, 'mouth', 'Head', 'head')
    m.set((15, tip - 2, z), color, 'mouth', 'Head', 'head')
    m.set((17, tip - 2, z), color, 'mouth', 'Head', 'head')


def hood(m, color, mark=None, inner=None, size=3):
    """A cobra's hood: spread behind and beside the head, its front a paler scale."""
    hd = m.head
    inner = inner or shade(color, 1.15)
    cy = hd.y1 - 1
    for x in range(hd.x0 - size, hd.x1 + size + 1):
        for z in range(19, hd.z1 + 2):
            dx = (x + 0.5 - 16.5) / (hd.w / 2 + size)
            dz = (z + 0.5 - (hd.z0 + hd.z1) / 2) / (hd.h / 2 + 2.2)
            if dx * dx + dz * dz > 1:
                continue
            inside = hd.x0 <= x <= hd.x1 and z >= hd.z0
            for y in (cy, cy + 1):
                if inside and y <= hd.y1:
                    continue
                c = color if y == cy + 1 else inner
                m.set((x, y, z), c, 'scale', 'Head', 'head')
    if mark:
        for (x, z) in ((14, hd.z0 + 3), (18, hd.z0 + 3), (14, hd.z0 + 2), (18, hd.z0 + 2), (15, hd.z0 + 1), (17, hd.z0 + 1), (16, hd.z0 + 1)):
            m.set((x, cy + 2, z), mark, 'scale', 'Head', 'head')


def rattle(m, color=(210, 190, 150)):
    for p, v in list(m.v.items()):
        if v.bone == 'Hips' and v.group == 'scale' and p[1] >= 28:
            v.color = color if (p[0] + p[1]) % 2 else shade(color, 0.8)


def eye_horns(m, color):
    hd = m.head
    for x in (hd.x0 + 1, hd.x1 - 1):
        m.set((x, hd.y0 + 1, hd.z1 + 1), color, 'horn', 'Head', 'head')
        m.set((x, hd.y0 + 1, hd.z1 + 2), shade(color, 1.2), 'horn', 'Head', 'head')


def diamonds(color, edge=None):
    edge = edge or shade(color, 0.6)
    def f(m):
        for p, v in m.v.items():
            if v.group != m.skin_group or v.part not in ('chest', 'spine', 'hips', 'uleg_r', 'uleg_l', 'lleg_r', 'lleg_l', 'uarm_r', 'uarm_l', 'larm_r', 'larm_l'):
                continue
            a = (p[2] + p[0]) % 4
            b = (p[2] - p[0]) % 4
            if a == 0 or b == 0:
                v.color = edge
            elif a == 2 and b == 2:
                v.color = color
    return f


def band_colors(colors, period=2):
    def f(m):
        for p, v in m.v.items():
            if v.group != m.skin_group or v.part == 'head':
                continue
            k = p[2] if v.part not in ('uarm_r', 'uarm_l', 'larm_r', 'larm_l', 'hand_r', 'hand_l') else p[0]
            v.color = colors[(k // period) % len(colors)]
    return f


def snake(scale=(150, 130, 70), belly=(230, 220, 160), head=None, snout=None, iris='gold', hood_color=None,
          hood_mark=None, pattern=None, tail='snake', tail_tip=None, outfit=None, outfit_kw=None, hat=False,
          horns=None, rattler=False, extras=None, head_color=None, tongue_color=(200, 40, 60)):
    iris = EYES.get(iris, iris) if isinstance(iris, str) else iris
    head = head or dict(w=9, d=9, h=6, style='soft')
    sn = dict(length=2, w=7, h=3, taper=2, color=shade(head_color or scale, 1.06), jaw=belly, nostrils=True, mouth=shade(scale, 0.55))
    sn.update(snout or {})
    def face(m, hd):
        m.head_skin = head_color or scale
        side_eyes(m, hd, iris, z=hd.z0 + 3, style='slit')
        if tongue_color:
            tongue(m, tongue_color)
        if horns:
            eye_horns(m, horns)
    def pat(m):
        if pattern:
            pattern(m)
        if hood_color:
            hood(m, hood_color, mark=hood_mark)
    def after(m):
        if rattler:
            rattle(m)
        if extras:
            extras(m)
    return beast(scale, skin_group='scale', head=head, muzzle=sn, eyes=None, belly_color=belly, face=face, pattern=pat,
                 tail=tail, tail_tip=tail_tip, outfit=outfit, outfit_kw=outfit_kw, hat=hat, extras=after,
                 head_color=head_color, hands='claws', hand_color=(230, 224, 200))


SNAKES = [
    ('Cobra', dict(scale=(170, 140, 80), hood_color=(150, 120, 60), hood_mark=(40, 34, 30), pattern=lambda m: X.scales(m, (140, 110, 60)),
                   outfit='monk', outfit_kw=dict(main=(160, 40, 40), trim=(222, 184, 72), second=(230, 220, 190)))),
    ('KingCobra', dict(scale=(90, 90, 50), belly=(220, 200, 110), hood_color=(110, 100, 50), pattern=band_colors([(90, 90, 50), (90, 90, 50), (210, 190, 100)], 1),
                       outfit='tactician', hat=False, outfit_kw=dict(main=(40, 40, 50), trim=(222, 184, 72)))),
    ('Rattler', dict(scale=(170, 140, 100), pattern=diamonds((120, 90, 60)), rattler=True, outfit='gunslinger', hat=True, iris='amber')),
    ('GreenMamba', dict(scale=(90, 190, 70), belly=(200, 240, 140), head=dict(w=9, d=10, h=6, style='soft'), snout=dict(length=3, taper=2),
                        outfit='rogue', hat=False, outfit_kw=dict(main=(40, 60, 40), trim=(70, 120, 50), mask=False))),
    ('CoralSnake', dict(scale=(200, 40, 40), belly=(230, 200, 60), pattern=band_colors([(200, 40, 40), (200, 40, 40), (240, 210, 60), (30, 30, 30), (30, 30, 30), (240, 210, 60)], 1),
                        head_color=(30, 30, 30), outfit='apothecary', hat=False, tongue_color=(240, 210, 60))),
    ('TreePython', dict(scale=(60, 170, 70), belly=(220, 230, 120), pattern=lambda m: X.spots(m, (240, 240, 230), density=0.12, head=False),
                        outfit='scout', hat=False, iris='gold')),
    ('Constrictor', dict(scale=(150, 120, 90), belly=(220, 210, 180), head=dict(w=11, d=9, h=7, style='soft'), pattern=diamonds((100, 70, 50), (70, 50, 40)),
                         outfit='heavy', hat=False)),
    ('SeaKrait', dict(scale=(80, 130, 190), belly=(170, 200, 230), pattern=band_colors([(80, 130, 190), (80, 130, 190), (30, 30, 40)], 1),
                      outfit='sailor', hat=True, tail='fish', tail_tip=(30, 30, 40))),
    ('HornedViper', dict(scale=(210, 180, 130), belly=(240, 230, 200), horns=(180, 150, 110), head=dict(w=9, d=9, h=6, style='wedge'),
                         pattern=lambda m: X.spots(m, (160, 130, 90), density=0.25), outfit='merchant', hat=False)),
    ('Albino', dict(scale=(245, 238, 210), belly=(250, 250, 240), pattern=diamonds((240, 210, 120)), iris='red', hood_color=(240, 230, 200),
                    outfit='white_mage', hat=False)),
    ('BlackMamba', dict(scale=(70, 70, 76), belly=(140, 140, 130), head=dict(w=9, d=10, h=6, style='wedge'), outfit='necromancer', hat=False,
                        iris=(120, 255, 140), tongue_color=(30, 30, 30))),
    ('Gaboon', dict(scale=(150, 110, 120), belly=(220, 200, 170), head=dict(w=11, d=9, h=6, style='wedge'),
                    pattern=diamonds((220, 200, 160), (90, 60, 70)), outfit='sharpshooter', hat=False, horns=(180, 140, 140))),
    ('Copperhead', dict(scale=(180, 110, 70), belly=(230, 190, 150), pattern=band_colors([(180, 110, 70), (130, 70, 40)], 2),
                        head_color=(200, 120, 60), outfit='assault', hat=False)),
    ('Spitter', dict(scale=(60, 60, 50), belly=(220, 220, 200), hood_color=(70, 70, 60), hood_mark=(230, 230, 220),
                     pattern=band_colors([(60, 60, 50), (60, 60, 50), (220, 220, 200)], 1), outfit='fire_mage', hat=False,
                     outfit_kw=dict(main=(40, 90, 50), trim=(150, 220, 90), accent=(150, 255, 90)))),
]


def naga(kind):
    """A naga: a figure's upper body on a serpent's coiled tail."""
    scale = {'cobra': (170, 140, 80), 'coral': (200, 40, 40), 'jade': (60, 170, 110)}[kind]
    m = F.body(scale, 'scale', leg=4, leg_w=2, leg_d=2, gap=1, torso_w=7, torso_d=4, torso_h=10, arm_len=7, arm_w=2,
               arm_d=2, arm_pose='a', head=dict(w=9, d=9, h=6, style='soft'), neck=2, foot_len=0)
    # nothing below the torso: drop the legs and feet the body made
    m.v = {p: v for p, v in m.v.items() if not (v.part or '').startswith(('uleg', 'lleg', 'foot'))}
    b = m.body
    hd = m.head
    H.snout(m, hd, shade(scale, 1.06), length=2, w=7, h=3, taper=2, jaw=(230, 220, 160), mouth=shade(scale, 0.55))
    m.head_skin = scale
    side_eyes(m, hd, (230, 190, 50), z=hd.z0 + 3)
    tongue(m)
    # the coil: from under the torso round in a ring on the ground, its end curling up behind
    pts = [(16, 16, b.hip, 3.2, 2.6, 2.4), (16, 13, 3.5, 3.4, 3.2, 2.6), (20, 14, 2.3, 3.2, 3.2, 2.3), (23, 19, 2.3, 3, 3, 2.3),
           (20, 24, 2.3, 2.8, 2.8, 2.2), (13, 24, 2.3, 2.6, 2.6, 2.1), (9, 20, 2.2, 2.3, 2.3, 2), (9, 15, 2, 2, 2, 1.8),
           (11, 10, 3, 1.5, 1.5, 1.5), (12, 8, 6, 1.0, 1.0, 1.0), (12, 9, 9, .6, .6, .6)]
    if kind == 'coral':
        colors = [(200, 40, 40), (200, 40, 40), (240, 210, 60), (30, 30, 30), (30, 30, 30), (240, 210, 60)]
        col = lambda t, p: colors[int(t * 40) % len(colors)]
    else:
        col = lambda t, p: shade(scale, 0.82) if (p[0] + p[1] + p[2]) % 3 == 0 else scale
    X.sweep(m, pts, col, 'scale', None)
    m.paint((230, 220, 160), None, parts=('chest', 'spine', 'hips'), where=lambda p, v: p[1] == b.front and abs(p[0] - 16) <= 1)
    if kind == 'cobra':
        hood(m, (150, 120, 60), mark=(40, 34, 30))
        F.dress(m, sash=(160, 40, 40), belt=(120, 80, 50), buckle=(222, 184, 72))
        H.hat(m, hd, 'circlet', (222, 184, 72), extra=(60, 200, 120))
    elif kind == 'jade':
        F.dress(m, shirt=(230, 214, 160), sleeves='short', sash=(40, 110, 80), belt=(120, 80, 50), buckle=(222, 184, 72))
    else:
        F.dress(m, belt=(60, 40, 30), buckle=(222, 184, 72), sash=(30, 30, 30))
    return m

# --- Turtlefolk -----------------------------------------------------------------------------

def turtle(skin=(110, 150, 80), shell=(120, 90, 50), rim=None, scute=None, plastron_color=(220, 200, 130), head=None,
           beak_color=None, beak='cone', iris='black', eyes='bead', pattern=None, outfit=None, outfit_kw=None, hat=False,
           spikes=None, shell_depth=4, shell_top=19, shell_bottom=8, extras=None, tail='stub', snout_len=0, flat=False):
    iris = EYES.get(iris, iris) if isinstance(iris, str) else iris
    head = head or dict(w=7, d=8, h=7, style='soft')
    def face(m, hd):
        if beak:
            H.beak(m, hd, beak_color or shade(skin, 0.7), beak, z=hd.z0 + 1)
        if snout_len:
            H.snout(m, hd, shade(skin, 1.05), length=snout_len, w=3, h=2, z=hd.z0 + 1, taper=1, nostrils=True)
    def pat(m):
        if pattern:
            pattern(m)
    def before(m):
        O.belt(m, (90, 70, 50))
    def after(m):
        X.turtle_shell(m, shell, rim=rim, scute=scute, depth=shell_depth, top=shell_top, bottom=shell_bottom, spikes=spikes)
        X.plastron(m, plastron_color)
        if extras:
            extras(m)
    return beast(skin, skin_group='skin', head=head, eyes=eyes, iris=iris, eye_gap=5 if head.get('w', 7) >= 9 else 3, face=face,
                 pattern=pat, tail=tail, tail_tip=shade(skin, 0.9), outfit=outfit, outfit_kw=outfit_kw, hat=hat, extras=after,
                 hands='claws', hand_color=(230, 220, 190))


def stripes_face(color):
    def f(m):
        hd = m.head
        for x in (hd.x0, hd.x1):
            for y in range(hd.y0 + 1, hd.y1 + 1):
                if (y + x) % 2 == 0 and m.has((x, y, hd.z0 + 2)):
                    m.set((x, y, hd.z0 + 2), color, 'skin', 'Head', 'head')
        X.stripes(m, color, period=3, head=False)
    return f


def moss(m):
    for p, v in m.v.items():
        if v.group == 'shell' and X.h(p, 21) < 0.45 and p[1] >= 20:
            v.color = (90, 140, 60) if X.h(p, 22) < 0.6 else (130, 170, 80)
            v.group = 'plant'
    for (x, z) in ((14, 20), (18, 20)):
        pass


def star(m):
    for p, v in m.v.items():
        if v.group == 'shell' and v.bone == 'Chest':
            cx = (p[0] - 16.5)
            cz = (p[2] - 13.5)
            if abs(cx) < 0.6 or abs(cz) < 0.6 or abs(abs(cx) - abs(cz)) < 0.6:
                v.color = (240, 210, 90)


TURTLES = [
    ('BoxMonk', dict(skin=(120, 110, 70), shell=(140, 100, 50), scute=(220, 180, 70), outfit='monk', hat=False,
                     outfit_kw=dict(main=(200, 120, 40), beads=False))),
    ('Snapper', dict(skin=(90, 96, 70), shell=(70, 70, 50), spikes=(110, 100, 70), beak='hook', beak_color=(60, 60, 50),
                     head=dict(w=9, d=8, h=7, style='soft'), outfit='warrior', hat=False, eyes='angry', iris='amber', tail='lizard')),
    ('SeaRover', dict(skin=(150, 170, 120), shell=(90, 120, 70), rim=(200, 190, 140), outfit='sailor', hat=True, shell_depth=3)),
    ('Tortoise', dict(skin=(160, 150, 120), shell=(150, 120, 70), scute=(90, 70, 40), shell_depth=5, shell_top=19, outfit='scholar', hat=False,
                      head=dict(w=7, d=8, h=7, style='soft'))),
    ('Softshell', dict(skin=(150, 150, 110), shell=(140, 140, 100), scute=(140, 140, 100), rim=(160, 160, 120), beak=None, snout_len=3,
                       outfit='scout', hat=False, shell_depth=2, eyes='pupil')),
    ('Ridgeback', dict(skin=(100, 100, 80), shell=(80, 76, 60), spikes=(60, 60, 50), beak='hook', beak_color=(80, 76, 60),
                       head=dict(w=9, d=8, h=7, style='soft'), outfit='guardian', hat=False, outfit_kw=dict(cape=False, main=(130, 130, 120)))),
    ('Painted', dict(skin=(50, 60, 50), shell=(50, 60, 50), rim=(200, 60, 40), scute=(70, 80, 60), pattern=stripes_face((220, 200, 60)),
                     outfit='bard', hat=True)),
    ('Leatherback', dict(skin=(60, 66, 70), shell=(40, 44, 48), scute=(80, 84, 90), outfit='pirate', hat=True, shell_depth=3)),
    ('Stargazer', dict(skin=(120, 110, 80), shell=(60, 50, 40), extras=star, outfit='psychic', hat=False)),
    ('Musk', dict(skin=(70, 66, 60), shell=(50, 46, 40), outfit='rogue', hat=False, outfit_kw=dict(mask=True))),
    ('Diamondback', dict(skin=(170, 170, 160), shell=(110, 100, 80), scute=(70, 64, 50), pattern=lambda m: X.spots(m, (60, 60, 60), density=0.2),
                         outfit='tactician', hat=True)),
    ('Mossback', dict(skin=(110, 130, 80), shell=(100, 80, 50), extras=moss, outfit='nature_mage', hat=False)),
    ('Ironshell', dict(skin=(120, 130, 100), shell=(150, 154, 160), rim=(110, 114, 120), scute=(120, 124, 130), outfit='heavy', hat=False)),
    ('Snapjaw', dict(skin=(110, 120, 80), shell=(90, 80, 50), beak='heavy', beak_color=(70, 70, 50), head=dict(w=9, d=8, h=7, style='soft'),
                     outfit='assault', hat=False, eyes='angry', iris='amber')),
]


def tortoise_concept(kind):
    skin = (150, 140, 110)
    m = F.body(skin, 'skin', leg=5, leg_w=4, leg_d=4, gap=3, torso_w=11, torso_d=7, torso_h=10, arm_len=9, arm_w=3, arm_d=3,
               arm_pose='a', head=dict(w=7, d=8, h=7, style='soft'), neck=3, foot_len=1, head_forward=4)
    hd = m.head
    H.eyes(m, hd, 'bead', iris=(30, 28, 32), gap=3)
    H.beak(m, hd, (100, 90, 70), 'cone' if kind != 'snap' else 'hook', z=hd.z0 + 1)
    b = m.body
    shell = (150, 110, 60) if kind != 'snap' else (80, 76, 60)
    for x in range(b.x0 - 3, b.x1 + 4):
        for y in range(b.front - 2, b.back + 9):
            for z in range(b.hip - 2, b.top + 6):
                d = ((x + 0.5 - 16.5) / 8.6) ** 2 + ((y + 0.5 - (b.back + 1)) / 7.5) ** 2 + ((z + 0.5 - (b.hip + b.top) / 2 - 1) / 8.6) ** 2
                if d <= 1 and y >= b.back - 1:
                    c = shell
                    if (x - 16) % 4 == 0 or (z - b.hip) % 5 == 0:
                        c = shade(shell, 0.72)
                    if d > 0.8 and y <= b.back + 2:
                        c = (220, 200, 140)
                    m.set((x, y, z), c, 'shell')
    if kind == 'snap':
        for z in range(b.hip + 1, b.top + 4, 3):
            for x in (12, 16, 20):
                yb = max((p[1] for p in m.v if p[0] == x and p[2] == z), default=None)
                if yb:
                    m.set((x, yb + 1, z), (60, 56, 44), 'shell')
    F.dress(m, belt=(100, 70, 50), buckle=(184, 128, 70), sash=(170, 60, 40) if kind != 'snap' else None)
    return m


SETS = [
    Set('Snakefolk', 'Snakefolk', designs(snake, SNAKES), [(1, 'Cartoon'), (5, 'TwoColor'), (3, 'CratePalette')],
        concepts=[('CobraNaga', lambda: naga('cobra')), ('CoralNaga', lambda: naga('coral')), ('JadeNaga', lambda: naga('jade'))]),
    Set('Turtlefolk', 'Turtlefolk', designs(turtle, TURTLES), [(1, 'Cartoon'), (4, 'TwoColor'), (2, 'CratePalette')],
        concepts=[('Elder', lambda: tortoise_concept('elder')), ('Snapper', lambda: tortoise_concept('snap'))]),
]
