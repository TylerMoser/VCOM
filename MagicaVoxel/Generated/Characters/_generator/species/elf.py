"""Elves: long pointed ears, fine features, wood, high, dark, snow, sea and sun elves."""
from .common import Set, designs, person, SKIN, HAIR
from core import shade
import heads as H
import outfits as O
import extras as X
import freebody as F

DARK_ELF = (126, 112, 150)
SNOW_ELF = (214, 228, 244)
SEA_ELF = (120, 182, 172)
SUN_ELF = (226, 172, 100)


def elf(skin='fair', hair='blonde', hair_style='long', ears='elf_long', **kw):
    kw.setdefault('eyes', 'big')
    kw.setdefault('eye_h', 3 if kw['eyes'] == 'big' else 2)
    kw.setdefault('brows', 'flat')
    return person(skin, hair=hair, hair_style=hair_style, ears=ears, **kw)


def antler_crown(color=(120, 90, 60)):
    def f(m):
        H.horns(m, m.head, 'antlers', color, tip=shade(color, 1.3))
    return f


SPECS = [
    ('WoodRanger', dict(skin='tan', hair='chestnut', hair_style='ponytail', iris='green', outfit='ranger')),
    ('HighMage', dict(skin='porcelain', hair='platinum', iris='blue', outfit='white_mage', hat='circlet',
                      outfit_kw=dict(hat_color=(222, 184, 72)))),
    ('Nightblade', dict(skin=DARK_ELF, hair='white', hair_style='swept', iris='red', eyes='angry', outfit='rogue')),
    ('Marksman', dict(skin='golden', hair='blonde', hair_style='braids', iris='teal', outfit='sharpshooter', hat=False)),
    ('Druid', dict(skin='olive', hair='darkbrown', hair_style='long', iris='amber', outfit='nature_mage', hat=False,
                   extras=antler_crown())),
    ('Seer', dict(skin='porcelain', hair='silver', hair_style='bob', iris='violet', eyes='glow', outfit='psychic')),
    ('Bladedancer', dict(skin='light', hair='auburn', hair_style='topknot', iris='green', outfit='monk', hat=False,
                         outfit_kw=dict(main=(60, 120, 90), trim=(200, 170, 70), second=(230, 226, 210)))),
    ('Prince', dict(skin='fair', hair='platinum', hair_style='long', iris='blue', outfit='noble', hat='circlet',
                    outfit_kw=dict(main=(40, 90, 70), trim=(222, 184, 72), hat_color=(222, 184, 72), cape=True))),
    ('Frostcaller', dict(skin=SNOW_ELF, hair='white', hair_style='long', iris='ice', eyes='glow', outfit='water_mage',
                         outfit_kw=dict(main=(150, 200, 230), trim=(230, 245, 255), second=(80, 130, 180)))),
    ('Tidecorsair', dict(skin=SEA_ELF, hair=(40, 90, 110), hair_style='ponytail', iris='gold', outfit='pirate',
                         outfit_kw=dict(main=(30, 70, 90), eyepatch=False))),
    ('Sentinel', dict(skin='light', hair='blonde', hair_style='long', iris='green', outfit='guardian',
                      outfit_kw=dict(main=(210, 200, 150), trim=(80, 140, 90), second=(60, 110, 70), emblem='chevron'))),
    ('Minstrel', dict(skin='peach', hair='ginger', hair_style='curly', iris='hazel', mouth='smile', outfit='bard',
                      outfit_kw=dict(main=(110, 60, 150), second=(220, 200, 90)))),
    ('Commander', dict(skin='fair', hair='raven', hair_style='side', iris='grey', eyes='template', outfit='tactician',
                       outfit_kw=dict(main=(40, 70, 50), trim=(200, 200, 210)))),
    ('Deathweaver', dict(skin=DARK_ELF, hair='raven', hair_style='long', iris=(120, 255, 140), eyes='glow', outfit='necromancer')),
    ('Pathfinder', dict(skin='tan', hair='sandy', hair_style='crop', iris='brown', outfit='scout',
                        outfit_kw=dict(main=(90, 110, 60)))),
    ('Sunsinger', dict(skin=SUN_ELF, hair='copper', hair_style='bun', iris='amber', outfit='fire_mage', hat=False, ears='elf')),
]


def concept(kind):
    """An elf as elves are often drawn: tall, slender, long-legged."""
    skin = SKIN['fair'] if kind != 'dark' else DARK_ELF
    m = F.body(skin, leg=13, leg_w=2, leg_d=2, gap=1, torso_w=5, torso_d=3, torso_h=10, arm_len=12, arm_w=2,
               arm_d=2, arm_pose='a', head=dict(w=7, d=7, h=8, style='soft'), neck=2, foot_len=2, hand=2, waist=0)
    hd = m.head
    H.eyes(m, hd, 'big', iris=(66, 146, 80) if kind != 'dark' else (200, 40, 40), height=3, gap=3, width=1)
    H.ears(m, hd, 'elf_long', skin, inner=shade(skin, 0.85))
    if kind == 'dark':
        H.hair(m, hd, (236, 236, 236), 'long')
        F.dress(m, shirt=(50, 46, 60), trousers=(40, 36, 50), boots=(30, 28, 34), boot_h=5, gloves=(30, 28, 34),
                belt=(90, 40, 50), buckle=(200, 200, 210), cape=(60, 30, 50))
    elif kind == 'mage':
        H.hair(m, hd, (238, 234, 214), 'long')
        H.hat(m, hd, 'circlet', (222, 184, 72), extra=(120, 170, 240))
        F.dress(m, robe=(236, 234, 226), robe_trim=(222, 184, 72), sash=(120, 170, 240))
    else:
        H.hair(m, hd, (136, 70, 40), 'ponytail')
        F.dress(m, shirt=(64, 104, 60), trousers=(96, 80, 60), boots=(124, 86, 52), boot_h=6, gloves=(124, 86, 52),
                belt=(78, 54, 36), cape=(46, 74, 44))
    return m


SETS = [Set('Elf', 'Elf', designs(elf, SPECS), treatments=[(2, 'Cartoon'), (1, 'TwoColor'), (3, 'CratePalette')],
            concepts=[('Ranger', lambda: concept('ranger')), ('HighMage', lambda: concept('mage')), ('DarkElf', lambda: concept('dark'))])]
