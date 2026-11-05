"""Bodies of free proportions for the concept models, which are not rig-ready: legs, torso,
arms and head of any size, the arms hanging (or out), on no fixed canvas (the model is
moved onto one just big enough as it is written). Centred on x 16 like every model here, so
heads.py's faces fit them; z 0 is the ground."""
from core import Model, shade, mix
import heads as H


class Body:
    pass


def body(skin, group='skin', leg=8, leg_w=3, leg_d=3, gap=1, torso_w=7, torso_d=4, torso_h=9,
         arm_len=9, arm_w=2, arm_d=2, arm_pose='down', head=None, neck=1, foot_len=2, hand=2,
         shoulder=0, head_color=None, head_forward=1, waist=0, hips_w=None):
    """A standing figure. [arm_pose] down (hanging beside the body), a (out at the hands) or
    t (straight out). [waist] narrows the torso's middle; [hips_w] widens its bottom."""
    m = Model(None)
    b = Body()
    m.skin, m.skin_group, m.head = tuple(skin), group, None
    cy = 16
    b.front = cy - torso_d // 2
    b.back = b.front + torso_d - 1
    b.leg_top = leg
    b.hip = leg + 1
    b.top = leg + torso_h
    half = torso_w // 2
    b.x0, b.x1 = 16 - half, 16 + half
    # legs and feet
    lx = gap // 2 + 1
    b.legs = {'r': (16 - lx - leg_w + 1, 16 - lx), 'l': (16 + lx, 16 + lx + leg_w - 1)}
    ly0 = cy - leg_d // 2
    for side, (x0, x1) in b.legs.items():
        for x in range(x0, x1 + 1):
            for y in range(ly0, ly0 + leg_d):
                for z in range(1, leg + 1):
                    part = ('uleg_' if z > leg // 2 else 'lleg_') + side
                    m.set((x, y, z), skin, group, None, part)
            for y in range(ly0 - foot_len, ly0 + leg_d):
                m.set((x, y, 0), skin, group, None, 'foot_' + side)
    # the gap between the legs at the top, the crotch
    for x in range(b.legs['r'][1] + 1, b.legs['l'][0]):
        for y in range(ly0, ly0 + leg_d):
            m.set((x, y, leg), skin, group, None, 'hips')
    # torso
    hw = (hips_w or torso_w) // 2
    for z in range(b.hip, b.top + 1):
        t = (z - b.hip) / max(1, torso_h - 1)
        w = half
        if hips_w and z < b.hip + 3:
            w = hw
        if waist and 0.3 < t < 0.7:
            w = half - waist
        for x in range(16 - w, 16 + w + 1):
            for y in range(b.front, b.back + 1):
                part = 'hips' if z < b.hip + 3 else ('spine' if t < 0.6 else 'chest')
                m.set((x, y, z), skin, group, None, part)
    # arms
    b.arms = {}
    ay0 = cy - arm_d // 2 - (0 if arm_d % 2 else 0)
    for side, sgn in (('r', -1), ('l', 1)):
        start = 16 + sgn * (half + 1 + shoulder)
        cells = []
        for k in range(arm_len):
            if arm_pose == 't':
                x = start + sgn * k
                for w in range(arm_w):
                    for y in range(ay0, ay0 + arm_d):
                        cells.append(((x, y, b.top - w), k))
            else:
                z = b.top - k
                out = (k // 3) if arm_pose == 'a' else 0
                for w in range(arm_w):
                    x = start + sgn * (w + out)
                    for y in range(ay0, ay0 + arm_d):
                        cells.append(((x, y, z), k))
        for p, k in cells:
            part = ('uarm_' if k < arm_len * 0.5 else ('larm_' if k < arm_len - hand else 'hand_')) + side
            m.set(p, skin, group, None, part)
        b.arms[side] = cells
    # neck and head
    for z in range(b.top + 1, b.top + neck + 1):
        for x in (15, 16, 17) if torso_w >= 7 else (16,):
            for y in (cy - 1, cy):
                m.set((x, y, z), skin, group, None, 'neck')
    hk = dict(w=9, d=8, h=8)
    hk.update(head or {})
    hk.setdefault('z0', b.top + neck + 1)
    hk.setdefault('y0', cy - hk['d'] // 2 - head_forward)
    H.make_head(m, head_color or skin, group, **hk)
    b.cy = cy
    m.body = b
    return m


def paint_band(m, color, group, parts=None, z0=None, z1=None, where=None):
    def ok(p, v):
        if z0 is not None and p[2] < z0:
            return False
        if z1 is not None and p[2] > z1:
            return False
        return where(p, v) if where else True
    m.paint(color, group, parts=parts, where=ok)


TORSO = ('chest', 'spine', 'hips')
ARMS = ('uarm_r', 'larm_r', 'uarm_l', 'larm_l')
HANDS = ('hand_r', 'hand_l')
LEGS = ('uleg_r', 'lleg_r', 'uleg_l', 'lleg_l')
FEET = ('foot_r', 'foot_l')


def dress(m, shirt=None, sleeves='long', trousers=None, boots=None, boot_h=2, belt=None, buckle=None,
          gloves=None, robe=None, robe_trim=None, cape=None, cape_inner=None, plate=None, plate_trim=None,
          pauldrons=None, apron=None, sash=None, beard_room=True):
    """Clothes on a free body, painted by its parts and bands."""
    b = m.body
    if shirt:
        m.paint(shirt, 'cloth', parts=TORSO)
        if sleeves == 'long':
            m.paint(shirt, 'cloth', parts=ARMS)
        elif sleeves == 'short':
            m.paint(shirt, 'cloth', parts=('uarm_r', 'uarm_l'))
    if trousers:
        m.paint(trousers, 'cloth', parts=LEGS + ('hips',))
    if robe:
        m.paint(robe, 'cloth', parts=TORSO + LEGS + ARMS)
        xs = range(b.legs['r'][0] - 1, b.legs['l'][1] + 2)
        for z in range(1, b.hip):
            for x in xs:
                for y in range(b.front - 1, b.back + 2):
                    if not m.has((x, y, z)):
                        m.set((x, y, z), robe_trim if (robe_trim and z == 1) else robe, 'cloth', None, 'robe')
    if boots:
        m.paint(boots, 'leather', parts=FEET)
        m.paint(boots, 'leather', parts=LEGS, where=lambda p, v: p[2] <= boot_h)
    if gloves:
        m.paint(gloves, 'leather', parts=HANDS)
    if belt:
        m.paint(belt, 'leather', parts=TORSO, where=lambda p, v: p[2] == b.hip + 1)
        if buckle:
            m.set((16, b.front - 1, b.hip + 1), buckle, 'metal')
    if sash:
        m.paint(sash, 'cloth', parts=TORSO, where=lambda p, v: p[2] in (b.hip + 1, b.hip + 2))
    if plate:
        trim = plate_trim or shade(plate, 0.75)
        for z in range(b.hip + 2, b.top + 1):
            for x in range(b.x0, b.x1 + 1):
                if z == b.top and x in (b.x0, b.x1):
                    continue
                m.set((x, b.front - 1, z), trim if z == b.hip + 2 else (shade(plate, 1.12) if x == 16 else plate), 'metal')
        m.paint(plate, 'metal', parts=('chest', 'spine'))
    if pauldrons:
        for side, cells in b.arms.items():
            xs = sorted({p[0] for p, k in cells if k < 3})
            for x in xs + [xs[-1] + (1 if side == 'l' else -1)]:
                for y in range(b.front - 1, b.back + 2):
                    m.set((x, y, b.top + 1), pauldrons, 'metal')
                    m.set((x, y, b.top), pauldrons, 'metal') if y in (b.front - 1, b.back + 1) else None
    if apron:
        for z in range(2, b.top - 1):
            for x in range(b.x0 + 1, b.x1):
                m.set((x, b.front - 1, z), apron, 'cloth')
    if cape:
        inner = cape_inner or shade(cape, 0.75)
        for z in range(max(2, b.leg_top // 2), b.top + 1):
            for x in range(b.x0, b.x1 + 1):
                m.set((x, b.back + 1, z), inner if x in (b.x0, b.x1) else cape, 'cloth')
                if b.x0 < x < b.x1:
                    m.set((x, b.back + 2, z), cape, 'cloth')
