"""Dwarves: big noses, bushy brows and beards down the chest (on the head's bone, so a long
one sways with the head and passes in front of a gun held at the chest), stout bellies."""
from .common import Set, designs, person, SKIN, HAIR
from core import shade, part_of
import heads as H
import outfits as O
import classes as C
import extras as X
import freebody as F


def stout(m, color=None):
    """A belly: a layer in front of the belly (y 14), taking the torso's clothes."""
    c = color or m.skin
    for z in range(10, 16):
        for x in range(14, 19):
            if z in (10, 15) and x in (14, 18):
                continue
            m.set((x, 14, z), c, m.skin_group, None, part_of((x, 16, z)))


def beads(color):
    def f(m):
        hd = m.head
        for p, v in list(m.v.items()):
            if v.group == 'hair' and p[2] < hd.z0 - 2 and p[1] <= hd.y0 - 1 and (p[2] % 3 == 0) and p[0] in (14, 15, 17, 18):
                v.color = color
                v.group = 'metal'
    return f


def dwarf(beard_color='auburn', beard='dwarf', hair=None, hair_style='short', skin='ruddy', iris='blue',
          outfit='smith', hat=True, belly=True, eyes='template', head=None, bead=None, outfit_kw=None,
          brows='bushy', extras=None, nose='big'):
    def before(m):
        if belly:
            stout(m)
    def after(m):
        if bead:
            beads(bead)(m)
        if extras:
            extras(m)
    hair = HAIR.get(hair, hair) if isinstance(hair, str) else hair
    bc = HAIR.get(beard_color, beard_color) if isinstance(beard_color, str) else beard_color
    return person(skin, hair=hair or bc, hair_style=hair_style, eyes=eyes, iris=iris, brows=brows,
                  nose=nose, mouth=None, beard=beard, beard_color=bc, head=head or dict(w=9, d=8, h=8),
                  outfit=outfit, hat=hat, before_outfit=before, extras=after, outfit_kw=outfit_kw)


SPECS = [
    ('Smith', dict(beard_color='auburn', beard='dwarf', outfit='smith', bead=(222, 184, 72))),
    ('Miner', dict(beard_color='black', beard='braided', outfit='miner', iris='brown', bead=(196, 200, 208))),
    ('Ironbeard', dict(beard_color='grey', beard='dwarf', outfit='heavy', skin='tan')),
    ('Hearthguard', dict(beard_color='ginger', beard='forked', outfit='guardian', outfit_kw=dict(emblem='diamond', second=(130, 40, 40)), bead=(222, 184, 72))),
    ('Berserker', dict(beard_color='copper', beard='full', hair_style='mohawk', hair='copper', outfit='barbarian', hat=False, eyes='angry', brows='angry')),
    ('Runepriest', dict(beard_color='white', beard='dwarf', outfit='cleric', skin='light', hat=True, bead=(120, 200, 255),
                        outfit_kw=dict(main=(70, 80, 120), trim=(200, 170, 70), accent=(120, 200, 255)))),
    ('Engineer', dict(beard_color='brown', beard='braided', outfit='apothecary', hat='goggles', bead=(184, 128, 70),
                      outfit_kw=dict(main=(120, 90, 60), second=(170, 150, 120)))),
    ('Thunderer', dict(beard_color='blonde', beard='full', outfit='sharpshooter', hat='helm', skin='peach',
                       outfit_kw=dict(main=(110, 60, 40), hat_color=(150, 154, 160)))),
    ('Captain', dict(beard_color='darkbrown', beard='forked', outfit='tactician', outfit_kw=dict(main=(110, 30, 40)), iris='green')),
    ('Brewer', dict(beard_color='ginger', beard='long', outfit='peasant', hat='beanie', outfit_kw=dict(main=(150, 110, 70), hat_color=(60, 100, 60)),
                    nose='pig', brows='flat')),
    ('Mountaineer', dict(beard_color='sandy', beard='full', outfit='hunter', iris='grey')),
    ('Longbeard', dict(beard_color='white', beard='dwarf', hair='white', hair_style='bald', outfit='scholar', skin='tan', bead=(222, 184, 72),
                       outfit_kw=dict(main=(70, 60, 90)))),
    ('Slayer', dict(beard_color='ginger', beard='braided', hair='ginger', hair_style='mohawk', outfit='warrior', hat=False, belly=False,
                    outfit_kw=dict(main=(90, 60, 40), trim=(184, 128, 70)), eyes='angry')),
    ('Merchant', dict(beard_color='black', beard='goatee', outfit='merchant', skin='olive', outfit_kw=dict(main=(110, 40, 90)))),
    ('Prospector', dict(beard_color='grey', beard='long', outfit='gunslinger', skin='ruddy', iris='hazel',
                        outfit_kw=dict(main=(140, 110, 70)))),
    ('Shieldmaiden', dict(beard_color='auburn', beard=None, hair='auburn', hair_style='braids', outfit='warrior', belly=False,
                          eyes='big', iris='green', brows='flat', nose='button', outfit_kw=dict(main=(110, 70, 50), trim=(196, 200, 208)))),
]

def concept(kind):
    """A dwarf as dwarves are drawn: short legs, a barrel of a body, long arms, big hands."""
    skin = SKIN['ruddy']
    m = F.body(skin, leg=5, leg_w=3, leg_d=4, gap=1, torso_w=11, torso_d=6, torso_h=10, arm_len=10, arm_w=3,
               arm_d=3, arm_pose='a', head=dict(w=11, d=9, h=8), neck=0, foot_len=2, hand=3)
    hd = m.head
    H.eyes(m, hd, 'template', iris=(60, 112, 196), gap=3)
    H.brows(m, hd, (150, 70, 40), z=hd.z0 + 5, style='bushy')
    H.nose(m, hd, 'big', z=hd.z0 + 2)
    if kind == 'smith':
        H.hair(m, hd, (176, 74, 40), 'bald')
        H.beard(m, hd, (176, 74, 40), 'dwarf', length=11)
        F.dress(m, trousers=(90, 70, 56), boots=(70, 50, 36), boot_h=2, apron=(120, 84, 52), gloves=(70, 50, 36),
                belt=(60, 40, 30), buckle=(222, 184, 72))
    elif kind == 'guardian':
        H.beard(m, hd, (200, 200, 200), 'forked', length=10)
        H.hat(m, hd, 'horned_helm', (150, 154, 162), trim=(110, 112, 120), extra=(235, 225, 200))
        F.dress(m, shirt=(120, 40, 40), trousers=(90, 60, 50), boots=(110, 114, 122), boot_h=3, plate=(170, 174, 182),
                pauldrons=(150, 154, 162), gloves=(110, 114, 122), belt=(60, 40, 30), buckle=(222, 184, 72),
                cape=(120, 40, 40))
    else:
        H.beard(m, hd, (40, 34, 36), 'braided', length=9)
        H.hat(m, hd, 'mining', (200, 170, 60), trim=(150, 126, 44))
        F.dress(m, shirt=(170, 140, 90), sleeves='short', trousers=(80, 90, 110), boots=(70, 50, 36), boot_h=3,
                gloves=(124, 86, 52), belt=(60, 40, 30), buckle=(196, 200, 208))
    return m


CONCEPTS = [
    ('Smith', lambda: concept('smith')),
    ('Warden', lambda: concept('guardian')),
    ('Miner', lambda: concept('miner')),
]

SETS = [Set('Dwarf', 'Dwarf', designs(dwarf, SPECS), treatments=[(1, 'Cartoon'), (4, 'TwoColor'), (2, 'CratePalette')],
            concepts=CONCEPTS)]
