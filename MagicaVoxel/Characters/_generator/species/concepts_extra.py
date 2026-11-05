"""More concept models, free proportions, for the kinds whose bodies suggest them: a crab's
breadth, a frog's crouch, the beast stance of the cat and dog folk, a hare's legs, a wasp's
and a moth's bodies, an owl's roundness, a walking flytrap. Each set's module lists them."""
from core import shade, mix
import heads as H
import extras as X
import freebody as F

WHITE = (240, 238, 232)


def crab():
    shell = (200, 60, 40)
    m = F.body(shell, 'chitin', leg=5, leg_w=2, leg_d=2, gap=5, torso_w=13, torso_d=6, torso_h=6, arm_len=8, arm_w=2, arm_d=2,
               arm_pose='t', head=dict(w=9, d=6, h=5, style='soft'), neck=0, foot_len=0, head_forward=2)
    b = m.body
    X.eye_stalks(m, shade(shell, 0.9), height=3, spread=3)
    # the carapace: wide and flat over the body
    for x in range(4, 29):
        for y in range(b.front - 2, b.back + 4):
            for z in range(b.hip, b.top + 3):
                d = ((x + 0.5 - 16.5) / 12.5) ** 2 + ((y + 0.5 - 16) / 6) ** 2 + ((z + 0.5 - (b.hip + 2)) / 4.2) ** 2
                if d <= 1:
                    m.set((x, y, z), shell if d < 0.8 else shade(shell, 0.75), 'chitin')
    # eight walking legs, four each side
    for side in (-1, 1):
        for i in range(4):
            y0 = 13 + i * 2.2
            pts = [(16 + side * 11, y0, b.hip + 2), (16 + side * 15, y0, b.hip + 4), (16 + side * 18, y0 + 0.5, 0.5)]
            X.sweep(m, [(x, y, z, .7, .7, .7) for x, y, z in pts], shade(shell, 0.9), 'chitin', None)
    # the great claws at the ends of the arms
    for side in (-1, 1):
        xc = 16 + side * 16
        m.ellipsoid(xc, b.cy - 3, b.top + 1, 2.6, 3.4, 2.2, shell, 'chitin')
        for k in range(4):
            m.set((xc + side * (k // 2), b.cy - 6 - k, b.top + 2), shade(shell, 0.7), 'chitin')
            m.set((xc + side * (k // 2), b.cy - 6 - k, b.top - 1), shade(shell, 0.7), 'chitin')
    return m


def frog():
    skin = (80, 170, 70)
    m = F.body(skin, 'skin', leg=4, leg_w=3, leg_d=5, gap=5, torso_w=11, torso_d=8, torso_h=7, arm_len=7, arm_w=2, arm_d=2,
               arm_pose='a', head=dict(w=13, d=10, h=7, style='soft'), neck=0, foot_len=4, head_forward=2)
    hd = m.head
    for side in (-1, 1):
        cx = 16 + side * 4.5 + 0.5
        m.ellipsoid(cx, hd.y0 + 3, hd.z1 + 0.5, 2.2, 2.2, 2.2, skin, 'skin')
        m.set((int(cx), hd.y0 + 1, hd.z1 + 1), (230, 200, 40), 'eye')
        m.set((int(cx), hd.y0 + 1, hd.z1 + 2), (230, 200, 40), 'eye')
        m.set((int(cx) - side, hd.y0 + 1, hd.z1 + 1), (28, 26, 30), 'eye')
    H.mouth(m, hd, 'line', color=(40, 90, 40), z=hd.z0 + 1, width=9)
    b = m.body
    # the folded hind legs, big thighs beside the body
    for side in (-1, 1):
        m.ellipsoid(16 + side * 7, b.cy + 2, 4, 2.6, 4.2, 3.2, skin, 'skin')
        for k in range(6):
            m.set((16 + side * 8, b.cy - 3 - k // 2, 0), shade(skin, 0.85), 'skin')
    m.paint((220, 230, 170), None, parts=('chest', 'spine', 'hips'), where=lambda p, v: p[1] == m.body.front)
    F.dress(m, belt=(110, 80, 50), buckle=(184, 128, 70))
    return m


def beast_stance(kind):
    """A werebeast: legs bent back, a long torso leaning forward, long arms, a muzzle."""
    fur = (120, 120, 130) if kind == 'wolf' else (230, 130, 40)
    m = F.body(fur, 'fur', leg=9, leg_w=3, leg_d=3, gap=1, torso_w=11, torso_d=6, torso_h=11, arm_len=14, arm_w=3, arm_d=3,
               arm_pose='a', head=dict(w=9, d=9, h=8, style='base'), neck=1, foot_len=3, waist=2, head_forward=3)
    hd = m.head
    if kind == 'wolf':
        H.snout(m, hd, (200, 200, 205), length=4, w=5, h=3, taper=2, nose_color=(30, 30, 30), nose_width=1, mouth=(60, 40, 40), teeth=WHITE)
        H.eyes(m, hd, 'angry', iris=(230, 190, 60), z=hd.z0 + 3)
        H.ears(m, hd, 'dog_pointed', fur, inner=(200, 160, 160))
        X.mane(m, shade(fur, 0.8), size=2, low=hd.z0 - 2)
    else:
        H.snout(m, hd, WHITE, length=2, w=5, h=2, taper=0, nose_color=(230, 130, 150), nose_width=1)
        H.eyes(m, hd, 'slit', iris=(230, 190, 50), z=hd.z0 + 2)
        H.ears(m, hd, 'cat', fur, inner=(240, 170, 170))
        X.stripes(m, (30, 26, 26), period=3, head=True)
    b = m.body
    tail = [(16, b.back + 1, b.hip + 2), (16, b.back + 5, b.hip), (16, b.back + 9, b.hip + 2), (16, b.back + 12, b.hip + 6)]
    r = 1.4 if kind == 'wolf' else 0.8
    X.sweep(m, [(x, y, z, r, r, r) for x, y, z in tail], fur, 'fur', None)
    for side, cells in b.arms.items():
        last = max(k for _, k in cells)
        for (x, y, z), k in cells:
            if k == last:
                m.set((x, y - 1, z - 1), (230, 224, 200), 'bone')
    F.dress(m, trousers=(80, 60, 50), belt=(60, 40, 30), buckle=(184, 128, 70))
    return m


def hare():
    fur = (170, 140, 100)
    m = F.body(fur, 'fur', leg=11, leg_w=2, leg_d=3, gap=1, torso_w=7, torso_d=5, torso_h=9, arm_len=8, arm_w=2, arm_d=2,
               arm_pose='a', head=dict(w=9, d=8, h=7, style='round'), neck=1, foot_len=5)
    hd = m.head
    H.snout(m, hd, WHITE, length=1, w=3, h=2, nose_color=(230, 130, 150), nose_width=1)
    H.eyes(m, hd, 'big', iris=(110, 70, 40), height=3)
    for side in (-1, 1):
        for k in range(1, 10):
            for x in (16 + side * 2, 16 + side * 3):
                m.set((x, hd.y0 + 4 + k // 4, hd.z1 + k), fur if x == 16 + side * 3 or k > 8 else (236, 160, 170), 'fur')
    b = m.body
    m.ellipsoid(16, b.back + 1.5, b.hip + 1, 1.8, 1.6, 1.8, WHITE, 'fur', only_empty=True)
    F.dress(m, shirt=(60, 100, 60), sleeves='short', belt=(110, 80, 50), buckle=(184, 128, 70))
    return m


def wasp():
    c = (240, 200, 40)
    m = F.body(c, 'chitin', leg=9, leg_w=1, leg_d=1, gap=5, torso_w=5, torso_d=4, torso_h=8, arm_len=9, arm_w=1, arm_d=1,
               arm_pose='a', head=dict(w=9, d=8, h=7, style='round'), neck=2, foot_len=1)
    hd = m.head
    for side in (-1, 1):
        x0 = hd.x0 if side < 0 else hd.x1 - 2
        for x in range(x0, x0 + 3):
            for z in range(hd.z0 + 1, hd.z0 + 5):
                y = m.front_y(x, z)
                if y is not None:
                    m.set((x, y, z), (40, 36, 30), 'eye')
    X.antennae(m, (40, 36, 30), 'elbowed')
    b = m.body
    for side in (-1, 1):
        pts = [(16 + side * 2, b.cy, b.hip + 1), (16 + side * 6, b.cy + 1, b.hip + 3), (16 + side * 8, b.cy + 2, 0.5)]
        X.sweep(m, [(x, y, z, .55, .55, .55) for x, y, z in pts], (40, 36, 30), 'chitin', None)
    X.sweep(m, [(16, b.back, b.hip, .8, .8, .8), (16, b.back + 4, b.hip - 1, 2.6, 3, 2.6), (16, b.back + 8, b.hip - 2, 2.8, 3, 2.6),
                (16, b.back + 12, b.hip - 4, 1.6, 1.8, 1.6), (16, b.back + 14, b.hip - 5, .5, .5, .5)],
            lambda t, p: (40, 36, 30) if int(t * 9) % 2 else c, 'chitin', None)
    for side in (-1, 1):
        for x in range(1, 11):
            for z in range(b.top - 1, b.top + 4 - x // 4):
                m.set((16 + side * (2 + x), b.back + 1, z), (210, 220, 230), 'glass', None, None, ('glass', 0.6))
    return m


def moth():
    c = (200, 90, 50)
    m = F.body(c, 'chitin', leg=8, leg_w=2, leg_d=2, gap=1, torso_w=7, torso_d=5, torso_h=9, arm_len=9, arm_w=2, arm_d=2,
               arm_pose='a', head=dict(w=9, d=8, h=7, style='round'), neck=1, foot_len=2)
    hd = m.head
    H.eyes(m, hd, 'dot', iris=(30, 28, 32), gap=3, width=2, height=2)
    X.antennae(m, shade(c, 0.8), 'feathery')
    b = m.body
    for side in (-1, 1):
        for x in range(1, 17):
            for z in range(2, b.top + 12):
                up = ((x - 8) / 8.5) ** 2 + ((z - (b.top + 3)) / 8) ** 2 <= 1
                low = ((x - 6) / 6.5) ** 2 + ((z - (b.top - 7)) / 6) ** 2 <= 1
                if up or low:
                    edge = up and ((x - 8) / 7.5) ** 2 + ((z - (b.top + 3)) / 7) ** 2 > 1
                    spot = (x - 9) ** 2 + (z - (b.top + 3)) ** 2 <= 4
                    col = (240, 220, 200) if edge else ((60, 90, 160) if spot else c)
                    m.set((16 + side * (x + 1), b.back + 2, z), col, 'chitin')
    fur = shade(c, 1.2)
    for x in range(13, 20):
        for y in range(b.front - 1, b.back + 2):
            m.set((x, y, b.top + 1), fur, 'fur')
    return m


def owl():
    c = (140, 110, 80)
    m = F.body(c, 'feather', leg=4, leg_w=2, leg_d=2, gap=3, torso_w=11, torso_d=9, torso_h=11, arm_len=9, arm_w=2, arm_d=4,
               arm_pose='down', head=dict(w=11, d=10, h=9, style='round'), neck=0, foot_len=2)
    hd = m.head
    for x in range(hd.x0, hd.x1 + 1):
        for z in range(hd.z0, hd.z1):
            y = m.front_y(x, z)
            if y is not None and abs(x - 16) / 5.5 + abs(z - hd.z0 - 4) / 4.5 < 1:
                m.set((x, y, z), (220, 200, 170), 'feather')
    H.eyes(m, hd, 'sclera', iris=(240, 150, 30), gap=3, width=2, height=2, z=hd.z0 + 4)
    H.beak(m, hd, (90, 80, 70), 'hook', z=hd.z0 + 2)
    for x in (hd.x0 + 1, hd.x1 - 1):
        for k in range(1, 4):
            m.set((x, hd.y0 + 2, hd.z1 + k), c, 'feather')
    X.mottle(m, [(110, 86, 60), (170, 140, 110)], density=0.3, groups=('feather',))
    m.paint((220, 180, 60), 'horn', parts=('foot_r', 'foot_l', 'lleg_r', 'lleg_l'))
    return m


def walking_flytrap():
    green = (110, 170, 60)
    m = F.body((120, 90, 60), 'bark', leg=7, leg_w=2, leg_d=2, gap=3, torso_w=5, torso_d=4, torso_h=12, arm_len=10, arm_w=2, arm_d=2,
               arm_pose='a', head=dict(w=13, d=12, h=4, style='soft'), neck=1, foot_len=3, head_color=green)
    hd = m.head
    # the jaws: the head is the lower lobe; an upper lobe opens above it, red inside, teeth round both
    for x in range(hd.x0, hd.x1 + 1):
        for y in range(hd.y0, hd.y1 + 1):
            edge = x in (hd.x0, hd.x1) or y in (hd.y0, hd.y1)
            m.set((x, y, hd.z1), (220, 60, 60) if not edge else green, 'plant')
            m.set((x, y + 3, hd.z1 + 5 + (y - hd.y0) // 3), green if edge else (200, 50, 50), 'plant')
    for x in range(hd.x0, hd.x1 + 1, 2):
        m.set((x, hd.y0 - 1, hd.z1 + 1), (220, 240, 160), 'horn')
        m.set((x, hd.y0 + 2, hd.z1 + 4), (220, 240, 160), 'horn')
    for side in (-1, 1):
        m.set((16 + side * 3, hd.y1 + 3, hd.z1 + 10), (250, 240, 200), 'eye')
    for p, v in m.v.items():
        if v.part in ('chest', 'spine', 'hips', 'uarm_r', 'uarm_l', 'larm_r', 'larm_l') and X.h(p, 171) < 0.3:
            v.color = (80, 140, 50)
            v.group = 'plant'
    return m
