"""Outfits for the game's classes (Brainstorming/Classes.txt) and for everyday folk, each a
function dressing a model in the pieces of outfits.py, its colours overridable.

dress(m, name, hat=..., **colours): [hat] True puts on the outfit's own headgear, False none,
or names another (heads.hat's styles). Weapons are not drawn: the game hangs them in the
figure's hands as props."""
from core import shade, mix
import outfits as O
import heads as H

GOLD = (222, 184, 72)
SILVER = (196, 200, 208)
STEEL = (160, 166, 176)
IRON = (110, 114, 122)
BRONZE = (184, 128, 70)
LEATHER = (124, 86, 52)
DARK_LEATHER = (78, 54, 36)
BLACK = (40, 38, 44)
WHITE = (236, 234, 226)
CREAM = (226, 214, 184)
LINEN = (210, 198, 168)

DEFAULTS = {
    'tactician': dict(main=(44, 66, 120), trim=GOLD, second=WHITE, boots=BLACK, accent=(170, 40, 50)),
    'sharpshooter': dict(main=(70, 86, 58), trim=(52, 60, 44), second=(150, 130, 96), boots=DARK_LEATHER, accent=(120, 100, 70)),
    'gunslinger': dict(main=(168, 132, 86), trim=(110, 80, 50), second=(150, 60, 50), boots=DARK_LEATHER, accent=(60, 50, 44)),
    'assault': dict(main=(150, 44, 44), trim=STEEL, second=(70, 66, 60), boots=DARK_LEATHER, accent=STEEL),
    'scout': dict(main=(64, 104, 60), trim=(46, 74, 44), second=(130, 96, 62), boots=LEATHER, accent=DARK_LEATHER),
    'monk': dict(main=(222, 140, 50), trim=(150, 60, 40), second=CREAM, boots=LINEN, accent=(70, 50, 40)),
    'heavy': dict(main=STEEL, trim=IRON, second=(90, 60, 50), boots=IRON, accent=(150, 40, 40)),
    'barbarian': dict(main=(120, 86, 56), trim=(90, 60, 40), second=(200, 180, 150), boots=(110, 80, 56), accent=(170, 50, 40)),
    'guardian': dict(main=SILVER, trim=GOLD, second=(40, 70, 140), boots=STEEL, accent=WHITE),
    'support': dict(main=CREAM, trim=(170, 50, 50), second=(80, 100, 120), boots=LEATHER, accent=(170, 50, 50)),
    'psychic': dict(main=(96, 60, 150), trim=(190, 150, 230), second=(50, 30, 80), boots=(60, 40, 80), accent=(120, 230, 255)),
    'white_mage': dict(main=WHITE, trim=GOLD, second=(200, 190, 230), boots=(200, 190, 170), accent=(120, 170, 240)),
    'nature_mage': dict(main=(80, 120, 60), trim=(150, 110, 60), second=(170, 200, 100), boots=(110, 80, 50), accent=(230, 90, 120)),
    'fire_mage': dict(main=(180, 50, 30), trim=(250, 170, 50), second=(80, 30, 20), boots=(60, 30, 20), accent=(255, 140, 40)),
    'water_mage': dict(main=(40, 100, 170), trim=(150, 220, 240), second=(30, 60, 110), boots=(40, 60, 90), accent=(110, 210, 255)),
    'air_mage': dict(main=(200, 220, 230), trim=(110, 170, 210), second=(150, 170, 190), boots=(140, 150, 160), accent=(230, 250, 255)),
    'earth_mage': dict(main=(120, 90, 50), trim=(80, 130, 60), second=(90, 70, 40), boots=(70, 55, 35), accent=(220, 170, 60)),
    'necromancer': dict(main=(40, 36, 48), trim=(110, 70, 140), second=(230, 224, 200), boots=(30, 28, 34), accent=(120, 255, 140)),
    'apothecary': dict(main=(200, 186, 150), trim=(110, 80, 50), second=(90, 130, 100), boots=DARK_LEATHER, accent=(120, 230, 120)),
    'peasant': dict(main=(170, 150, 110), trim=(120, 96, 66), second=(110, 90, 60), boots=(100, 76, 52), accent=(200, 180, 110)),
    'noble': dict(main=(120, 30, 60), trim=GOLD, second=WHITE, boots=BLACK, accent=(240, 240, 240)),
    'sailor': dict(main=(40, 60, 110), trim=WHITE, second=(170, 40, 40), boots=BLACK, accent=(230, 230, 220)),
    'pirate': dict(main=(140, 30, 30), trim=GOLD, second=(40, 36, 40), boots=BLACK, accent=WHITE),
    'merchant': dict(main=(60, 120, 120), trim=GOLD, second=(200, 180, 120), boots=LEATHER, accent=(180, 60, 60)),
    'smith': dict(main=(110, 80, 50), trim=(70, 50, 35), second=(150, 150, 140), boots=DARK_LEATHER, accent=IRON),
    'bard': dict(main=(60, 140, 90), trim=(230, 190, 70), second=(200, 70, 90), boots=LEATHER, accent=(250, 250, 250)),
    'cleric': dict(main=(230, 226, 210), trim=(180, 40, 40), second=(150, 120, 70), boots=LEATHER, accent=GOLD),
    'knight': dict(main=SILVER, trim=(120, 30, 40), second=(120, 30, 40), boots=STEEL, accent=GOLD),
    'miner': dict(main=(90, 100, 120), trim=(70, 70, 70), second=(170, 140, 90), boots=DARK_LEATHER, accent=(255, 230, 150)),
    'scholar': dict(main=(90, 70, 60), trim=(200, 170, 90), second=(220, 210, 180), boots=DARK_LEATHER, accent=(170, 210, 230)),
    'hunter': dict(main=(110, 80, 50), trim=(220, 210, 190), second=(80, 100, 60), boots=LEATHER, accent=(200, 190, 170)),
    'rogue': dict(main=(50, 46, 56), trim=(90, 40, 50), second=(80, 70, 60), boots=BLACK, accent=(140, 140, 150)),
    'tribal': dict(main=(150, 100, 60), trim=(200, 60, 40), second=(230, 220, 200), boots=(150, 100, 60), accent=(60, 140, 180)),
    'warrior': dict(main=(120, 90, 60), trim=BRONZE, second=(140, 40, 40), boots=LEATHER, accent=BRONZE),
    'gladiator': dict(main=BRONZE, trim=(150, 40, 40), second=(200, 180, 150), boots=LEATHER, accent=(150, 40, 40)),
    'ranger': dict(main=(56, 90, 70), trim=(120, 90, 60), second=(160, 140, 100), boots=LEATHER, accent=(200, 200, 180)),
}


def _c(name, kw):
    c = dict(DEFAULTS[name])
    c.update({k: v for k, v in kw.items() if v is not None})
    return c


def _hat(m, hat, default, c, **kw):
    if hat is False or m.head is None:
        return
    style = default if hat is True else hat
    if style:
        H.hat(m, m.head, style, kw.get('hat_color', c.get('hat', c['main'])), kw.get('hat_trim', c['trim']), kw.get('hat_extra'))


def dress(m, name, hat=True, **kw):
    """Dresses [m] as [name]. Colour keywords (main, trim, second, boots, accent, hat,
    hat_color, hat_trim) override the outfit's own."""
    c = _c(name if name in DEFAULTS else 'peasant', kw)
    FN[name](m, c, hat, kw)
    return m


# --- The game's classes --------------------------------------------------------------------

def tactician(m, c, hat, kw):
    O.shirt(m, c['second'], neckline=None)
    O.trousers(m, c.get('trousers', c['second']))
    O.boots(m, c['boots'], 4, cuff=shade(c['boots'], 1.3))
    O.coat(m, c['main'], trim=c['trim'], length='knee', open_front=True)
    O.epaulettes(m, c['trim'])
    O.cross_sash(m, c['accent'])
    O.belt(m, DARK_LEATHER, buckle=c['trim'])
    _hat(m, hat, 'tricorne', c, hat_color=c.get('hat', BLACK), hat_trim=c['trim'])


def sharpshooter(m, c, hat, kw):
    O.shirt(m, c['second'])
    O.trousers(m, c.get('trousers', shade(c['second'], 0.7)))
    O.boots(m, c['boots'], 4)
    O.coat(m, c['main'], trim=c['trim'], length='long', collar=True)
    O.bandolier(m, DARK_LEATHER, items=(200, 170, 90))
    O.gloves(m, DARK_LEATHER)
    O.scarf(m, c['accent'], tail=False)
    _hat(m, hat, 'wide', c, hat_color=c.get('hat', shade(c['main'], 0.8)), hat_trim=DARK_LEATHER)


def gunslinger(m, c, hat, kw):
    O.shirt(m, c.get('shirt', LINEN))
    O.trousers(m, c.get('trousers', (90, 80, 70)))
    O.boots(m, c['boots'], 3, toe=shade(c['boots'], 0.7))
    O.vest(m, c['accent'])
    O.coat(m, c['main'], trim=c['trim'], length='long', collar=False)
    O.holster(m, DARK_LEATHER, 'r'); O.holster(m, DARK_LEATHER, 'l')
    O.belt(m, DARK_LEATHER, buckle=SILVER)
    O.scarf(m, c['second'], tail=True)
    _hat(m, hat, 'cowboy', c, hat_color=c.get('hat', (110, 80, 50)), hat_trim=(60, 40, 30))


def assault(m, c, hat, kw):
    O.shirt(m, c['main'], sleeves='short')
    O.trousers(m, c['second'])
    O.boots(m, c['boots'], 4)
    O.breastplate(m, c['trim'], trim=shade(c['trim'], 0.75), low=13)
    O.pauldrons(m, c['trim'], size=1, sides='r')
    O.gloves(m, DARK_LEATHER, cuff=True)
    O.belt(m, DARK_LEATHER, buckle=c['trim'])
    O.pouches(m, LEATHER)
    _hat(m, hat, 'bandana', c, hat_color=c['main'], hat_trim=shade(c['main'], 0.7))


def scout(m, c, hat, kw):
    O.shirt(m, c['second'], sleeves='long')
    O.trousers(m, c.get('trousers', (90, 74, 56)))
    O.boots(m, c['boots'], 4, cuff=shade(c['boots'], 1.2))
    O.vest(m, c['accent'], open_front=False)
    O.cape(m, c['main'], inner=c['trim'], bottom=9)
    O.bracers(m, c['accent'])
    O.belt(m, DARK_LEATHER)
    O.quiver(m, LEATHER) if kw.get('quiver', True) else None
    _hat(m, hat, 'hood', c, hat_color=c['main'], hat_trim=c['trim'])


def monk(m, c, hat, kw):
    O.shirt(m, c['main'], sleeves='short', neckline='deep')
    O.trousers(m, c['second'])
    O.sash(m, c['trim'], z=10)
    O.wraps(m, c['second'])
    m.paint(c['second'], 'cloth', parts=O.LEGS, where=lambda p, v: p[2] <= 2)
    O.necklace(m, (120, 80, 50), pendant=(150, 100, 60), group='bone') if kw.get('beads', True) else None
    _hat(m, hat, 'headband', c, hat_color=c['trim'], hat_trim=shade(c['trim'], 0.8))


def heavy(m, c, hat, kw):
    O.mail(m, shade(c['main'], 0.8))
    O.trousers(m, c['second'])
    O.breastplate(m, c['main'], trim=c['trim'])
    O.pauldrons(m, c['main'], trim=c['trim'], size=2)
    O.gauntlets(m, c['main'], trim=c['trim'])
    O.greaves(m, c['main'])
    O.boots(m, c['boots'], 1)
    O.belt(m, DARK_LEATHER, buckle=c['trim'])
    _hat(m, hat, 'great_helm', c, hat_color=c['main'], hat_trim=c['trim'])


def barbarian(m, c, hat, kw):
    O.trousers(m, c['main'], 'long')
    O.mantle(m, c['second'], group='fur')
    O.kilt(m, c['trim'], top=8, bottom=5)
    O.belt(m, DARK_LEATHER, buckle=BRONZE)
    O.bracers(m, c['main'], studs=BRONZE)
    O.boots(m, c['boots'], 3, cuff=c['second'], group='fur')
    O.cross_sash(m, DARK_LEATHER, group='leather')
    if kw.get('paint', True):
        O.warpaint(m, c['accent'], kw.get('paint_style', 'stripes'))
    _hat(m, hat, 'horned_helm', c, hat_color=IRON, hat_trim=shade(IRON, 0.8), hat_extra=(235, 225, 200))


def guardian(m, c, hat, kw):
    O.mail(m, shade(c['main'], 0.85))
    O.trousers(m, shade(c['second'], 0.8))
    O.breastplate(m, c['main'], trim=c['trim'], low=14)
    O.tabard(m, c['second'], trim=c['trim'], emblem=kw.get('emblem', 'tower'), emblem_color=c['accent'])
    O.pauldrons(m, c['main'], trim=c['trim'], size=1)
    O.gauntlets(m, c['main'])
    O.greaves(m, c['main'], knee=False)
    O.boots(m, c['boots'], 1)
    O.cape(m, c['second'], inner=shade(c['second'], 0.7), bottom=8) if kw.get('cape', True) else None
    _hat(m, hat, 'helm', c, hat_color=c['main'], hat_trim=c['trim'])


def support(m, c, hat, kw):
    O.shirt(m, c['second'])
    O.trousers(m, shade(c['second'], 0.75))
    O.boots(m, c['boots'], 3)
    O.coat(m, c['main'], trim=shade(c['main'], 0.8), length='knee', collar=True)
    O.armband(m, WHITE, emblem=c['accent'], side='l')
    O.satchel(m, LEATHER, side='l')
    O.gloves(m, (230, 230, 230))
    O.belt(m, DARK_LEATHER)
    _hat(m, hat, 'cap', c, hat_color=c['main'], hat_trim=c['accent'])


def psychic(m, c, hat, kw):
    O.robe(m, c['main'], trim=c['trim'], sleeves='bell')
    O.sash(m, c['second'], z=10, tail=True)
    O.necklace(m, c['trim'], pendant=c['accent'], mat=('emit', 0.9, 1))
    if hat is not False and m.head is not None and hat in (True, 'circlet'):
        H.hat(m, m.head, 'circlet', GOLD, extra=c['accent'])
        hd = m.head
        m.set((16, hd.y0 - 1, hd.z1 - 1), c['accent'], 'gem', 'Head', 'head', ('emit', 0.9, 1))
    elif hat:
        _hat(m, hat, None, c)


def white_mage(m, c, hat, kw):
    O.robe(m, c['main'], trim=c['trim'], hem=c['trim'], sleeves='bell', front=c['trim'])
    O.sash(m, c['second'], z=10, tail=False)
    O.collar_ruff(m, c['second'])
    _hat(m, hat, 'hood', c, hat_color=c['main'], hat_trim=c['trim'])


def nature_mage(m, c, hat, kw):
    O.robe(m, c['main'], trim=c['trim'], sleeves='bell')
    O.sash(m, c['trim'], z=10)
    O.mantle(m, c['second'], highlight=shade(c['second'], 1.25), group='plant')
    m.paint(shade(c['trim'], 0.9), 'leather', parts=O.FEET)
    if hat is True and m.head is not None:
        H.hat(m, m.head, 'laurel', c['second'])
        hd = m.head
        for x in (14, 18):
            m.set((x, hd.y0 - 1, hd.z1 - 1), c['accent'], 'petal', 'Head', 'head')
    elif hat:
        _hat(m, hat, None, c)


def elementalist(m, c, hat, kw):
    O.robe(m, c['main'], trim=c['trim'], sleeves='bell', front=c['second'])
    O.sash(m, c['second'], z=10)
    glow = ('emit', 0.85, 1)
    for p in ((15, 14, 10), (17, 14, 10)):
        m.set(p, c['accent'], 'light', None, None, glow)
    for x in (6, 26):
        m.set((x, 16, 19), c['accent'], 'light', 'RightLowerArm' if x < 16 else 'LeftLowerArm', None, glow)
    _hat(m, hat, 'wizard', c, hat_color=c['main'], hat_trim=c['trim'], hat_extra=c['accent'])


def fire_mage(m, c, hat, kw):
    elementalist(m, c, hat, kw)


water_mage = air_mage = earth_mage = fire_mage


def necromancer(m, c, hat, kw):
    O.robe(m, c['main'], trim=c['trim'], sleeves='bell')
    O.sash(m, c['trim'], z=10)
    O.pauldrons(m, c['second'], trim=shade(c['second'], 0.8), size=1, group='bone')
    O.bone_necklace(m, c['second'])
    glow = ('emit', 0.9, 1)
    m.set((16, 13, 16), c['accent'], 'light', 'Chest', None, glow)
    _hat(m, hat, 'hood', c, hat_color=shade(c['main'], 0.9), hat_trim=c['trim'])


def apothecary(m, c, hat, kw):
    O.shirt(m, c['second'], sleeves='long')
    O.trousers(m, (90, 80, 70))
    O.boots(m, c['boots'], 3)
    O.apron(m, c['main'], strap=c['trim'], bottom=4, pocket=shade(c['main'], 0.85))
    O.gloves(m, (60, 90, 70), cuff=True)
    O.bandolier(m, c['trim'], items=((120, 230, 120), ('glass', 0.5)), side='l', back=False)
    O.vials(m, [(230, 80, 80), (90, 160, 240), (240, 220, 90), (190, 110, 230)])
    if hat is not False and m.head is not None and hat in (True, 'goggles'):
        H.hat(m, m.head, 'goggles', (150, 110, 60), trim=(80, 60, 40), extra=(150, 220, 210))
    elif hat:
        _hat(m, hat, None, c)


# --- Everyday folk -------------------------------------------------------------------------

def peasant(m, c, hat, kw):
    O.tunic(m, c['main'], belt_color=None, trim=c['trim'])
    O.trousers(m, c['second'])
    O.tunic(m, c['main'], trim=c['trim'])
    O.belt(m, (150, 120, 80), z=10, group='cloth')
    O.shoes(m, c['boots'])
    _hat(m, hat, 'straw', c, hat_color=c.get('hat', (220, 196, 120)), hat_trim=(170, 70, 50))


def noble(m, c, hat, kw):
    O.shirt(m, c['second'])
    O.trousers(m, c.get('trousers', (230, 226, 210)), 'knee')
    m.paint((240, 240, 236), 'cloth', parts=O.LEGS, where=lambda p, v: p[2] <= 4)
    O.shoes(m, c['boots'])
    O.coat(m, c['main'], trim=c['trim'], length='knee')
    O.collar_ruff(m, c['accent'])
    O.cross_sash(m, c['trim'])
    O.cape(m, shade(c['main'], 0.8), inner=c['trim'], bottom=7) if kw.get('cape', False) else None
    _hat(m, hat, 'crown' if kw.get('royal') else 'beret', c, hat_color=GOLD if kw.get('royal') else shade(c['main'], 0.8), hat_trim=c['trim'], hat_extra=(200, 40, 70))
    if hat is True and not kw.get('royal'):
        O.feather_in_hat(m, c['accent'])


def sailor(m, c, hat, kw):
    O.shirt(m, c['trim'], sleeves='long')
    m.paint(c['main'], 'cloth', parts=O.UPPER + O.SLEEVES, where=lambda p, v: p[2] % 2 == 0)
    O.trousers(m, c.get('trousers', (230, 226, 210)))
    O.sash(m, c['second'], z=10)
    O.boots(m, c['boots'], 2)
    O.scarf(m, c['second'], tail=True)
    _hat(m, hat, 'beanie', c, hat_color=c['main'], hat_trim=shade(c['main'], 0.75))


def pirate(m, c, hat, kw):
    O.shirt(m, c['accent'], neckline='deep')
    O.trousers(m, c['second'])
    O.boots(m, c['boots'], 4, cuff=shade(c['boots'], 1.3))
    O.vest(m, c['main'], trim=c['trim'])
    O.sash(m, c['main'], z=10)
    O.belt(m, DARK_LEATHER, buckle=c['trim'], z=9)
    O.holster(m, DARK_LEATHER, 'l')
    _hat(m, hat, 'tricorne', c, hat_color=BLACK, hat_trim=c['trim'])
    if kw.get('eyepatch', True) and m.head is not None:
        hd = m.head
        for x in range(hd.x0, hd.x1 + 1):
            z = hd.z0 + 4 if x < 16 else hd.z0 + 5
            y = m.front_y(x, z)
            if y is not None:
                m.set((x, y, z), BLACK, 'leather', 'Head', 'head')
        for z in (hd.z0 + 2, hd.z0 + 3):
            for x in (13, 14):
                y = m.front_y(x, z)
                m.set((x, y, z), BLACK, 'leather', 'Head', 'head')


def merchant(m, c, hat, kw):
    O.shirt(m, c['second'])
    O.trousers(m, (110, 90, 70))
    O.shoes(m, c['boots'])
    O.robe(m, c['main'], trim=c['trim'], sleeves='plain', flare=False)
    O.sash(m, c['accent'], z=10)
    O.pouches(m, LEATHER, back=False)
    _hat(m, hat, 'turban', c, hat_color=c['second'], hat_trim=shade(c['second'], 0.8), hat_extra=c['accent'])


def smith(m, c, hat, kw):
    O.trousers(m, (80, 70, 60))
    O.shirt(m, c['second'], sleeves='none', neckline=None) if kw.get('shirt', False) else None
    O.apron(m, c['main'], strap=c['trim'], bottom=3)
    O.gloves(m, DARK_LEATHER, cuff=True)
    O.boots(m, c['boots'], 3)
    _hat(m, hat, 'bandana', c, hat_color=(120, 60, 40), hat_trim=(90, 40, 30))


def bard(m, c, hat, kw):
    O.shirt(m, c['accent'], sleeves='long')
    O.trousers(m, c['second'])
    O.boots(m, c['boots'], 4, cuff=c['trim'])
    O.vest(m, c['main'], trim=c['trim'])
    O.cape(m, c['second'], inner=c['main'], bottom=11, wide=False)
    O.belt(m, DARK_LEATHER, buckle=c['trim'])
    _hat(m, hat, 'beret', c, hat_color=c['main'], hat_trim=c['trim'])
    if hat is True:
        O.feather_in_hat(m, c['second'])


def cleric(m, c, hat, kw):
    O.robe(m, c['main'], trim=c['trim'], sleeves='plain')
    O.tabard(m, c['trim'], trim=c['accent'], emblem='cross', emblem_color=c['accent'], bottom=3, back=False)
    O.necklace(m, c['accent'], pendant=c['accent'])
    _hat(m, hat, 'skullcap', c, hat_color=c['trim'], hat_trim=c['accent'])


def knight(m, c, hat, kw):
    O.mail(m, shade(c['main'], 0.8))
    O.trousers(m, shade(c['main'], 0.8))
    O.breastplate(m, c['main'], trim=shade(c['main'], 0.8))
    O.pauldrons(m, c['main'], trim=c['accent'], size=2)
    O.gauntlets(m, c['main'])
    O.greaves(m, c['main'])
    O.boots(m, c['boots'], 1)
    O.cape(m, c['second'], inner=shade(c['second'], 0.7), bottom=7)
    O.belt(m, DARK_LEATHER, buckle=c['accent'])
    _hat(m, hat, 'great_helm', c, hat_color=c['main'], hat_trim=shade(c['main'], 0.8))
    if hat is True:
        O.plume(m, c['second'], z_top=m.head.z1 + 2)


def miner(m, c, hat, kw):
    O.shirt(m, c['second'], sleeves='elbow')
    O.trousers(m, c['main'])
    m.paint(c['main'], 'cloth', parts=O.UPPER, where=lambda p, v: p[2] <= 15 or p[0] in (15, 17))
    O.boots(m, c['boots'], 4)
    O.gloves(m, LEATHER, cuff=True)
    O.belt(m, DARK_LEATHER, buckle=SILVER)
    O.backpack(m, LEATHER, roll=(150, 60, 50)) if kw.get('pack', False) else None
    _hat(m, hat, 'mining', c, hat_color=c.get('hat', (200, 170, 60)), hat_trim=shade((200, 170, 60), 0.75))


def scholar(m, c, hat, kw):
    O.robe(m, c['main'], trim=c['trim'], sleeves='plain', front=c['second'])
    O.belt(m, DARK_LEATHER, buckle=c['trim'], z=10)
    O.scroll_case(m, LEATHER)
    if m.head is not None and kw.get('spectacles', True):
        spectacles(m, (180, 150, 80), c['accent'])
    _hat(m, hat, 'beret' if hat is True else hat, c, hat_color=shade(c['main'], 0.8), hat_trim=c['trim'])


def spectacles(m, frame, lens):
    hd = m.head
    z = hd.z0 + 2
    from heads import eye_columns
    right, left = eye_columns(3, 2)
    for cols in (right, left):
        for x in cols:
            y = m.front_y(x, z)
            m.set((x, y - 1, z), lens, 'glass', 'Head', 'head', ('glass', 0.6))
            m.set((x, y - 1, z + 1), frame, 'metal', 'Head', 'head')
    m.set((16, hd.y0 - 1, z + 1), frame, 'metal', 'Head', 'head')
    m.set((15, hd.y0 - 1, z + 1), frame, 'metal', 'Head', 'head')
    m.set((17, hd.y0 - 1, z + 1), frame, 'metal', 'Head', 'head')


def hunter(m, c, hat, kw):
    O.shirt(m, c['second'])
    O.trousers(m, (100, 80, 60))
    O.boots(m, c['boots'], 4, cuff=c['trim'], group='fur')
    O.coat(m, c['main'], trim=c['trim'], length='knee', collar=False)
    O.mantle(m, c['trim'], group='fur')
    O.belt(m, DARK_LEATHER)
    O.powder_horn(m)
    _hat(m, hat, 'beanie', c, hat_color=c['trim'], hat_trim=shade(c['trim'], 0.85))


def rogue(m, c, hat, kw):
    O.shirt(m, c['main'])
    O.trousers(m, c['main'])
    O.vest(m, c['second'], open_front=False)
    O.boots(m, c['boots'], 4)
    O.gloves(m, c['boots'], cuff=True)
    O.belt(m, DARK_LEATHER, buckle=c['accent'])
    O.pouches(m, (70, 56, 46))
    O.bandolier(m, DARK_LEATHER, items=c['accent'], side='l')
    O.cape(m, shade(c['main'], 0.9), inner=c['trim'], bottom=10, wide=False)
    if m.head is not None and kw.get('mask', True):
        O.bandana_mask(m, c['trim'])
    _hat(m, hat, 'hood', c, hat_color=c['main'], hat_trim=c['trim'])


def tribal(m, c, hat, kw):
    O.loincloth(m, c['main'], belt_color=(110, 80, 50))
    O.bone_necklace(m, c['second'])
    O.bracers(m, c['main'])
    O.warpaint(m, c['trim'], kw.get('paint_style', 'stripes')) if kw.get('paint', True) else None
    if hat is True and m.head is not None:
        hd = m.head
        H.hat(m, hd, 'headband', c['trim'], trim=c['main'])
        for k, col in enumerate((c['accent'], c['trim'], c['accent'])):
            m.set((19 + (k == 1), hd.y0 + 5, hd.z1 - 1 + k), col, 'feather', 'Head', 'head')
            m.set((19 + (k == 1), hd.y0 + 6, hd.z1 + k), col, 'feather', 'Head', 'head')
    elif hat:
        _hat(m, hat, None, c)


def warrior(m, c, hat, kw):
    O.shirt(m, c['second'], sleeves='short')
    O.trousers(m, shade(c['main'], 0.8))
    O.breastplate(m, c['main'], trim=c['trim'], group='leather', ridge=False, low=12)
    O.pauldrons(m, c['trim'], size=1, sides='l', trim=shade(c['trim'], 0.8))
    O.kilt(m, c['main'], top=8, bottom=6, group='leather')
    O.bracers(m, c['main'], studs=c['trim'])
    O.boots(m, c['boots'], 3)
    O.belt(m, DARK_LEATHER, buckle=c['trim'])
    _hat(m, hat, 'helm', c, hat_color=c['trim'], hat_trim=shade(c['trim'], 0.75))


def gladiator(m, c, hat, kw):
    O.trousers(m, c['second'], 'shorts')
    O.loincloth(m, c['trim'])
    O.belt(m, DARK_LEATHER, buckle=c['main'], z=10)
    O.pauldrons(m, c['main'], size=2, sides='r', trim=shade(c['main'], 0.75))
    O.cross_sash(m, DARK_LEATHER, group='leather', side='r')
    O.bracers(m, c['main'], group='metal')
    O.boots(m, LEATHER, 4)
    O.greaves(m, c['main'], knee=False)
    _hat(m, hat, 'helm', c, hat_color=c['main'], hat_trim=shade(c['main'], 0.75))
    if hat is True:
        O.plume(m, c['trim'], z_top=m.head.z1 + 2)


def ranger(m, c, hat, kw):
    O.shirt(m, c['second'])
    O.trousers(m, (96, 80, 60))
    O.boots(m, c['boots'], 4)
    O.coat(m, c['main'], trim=c['trim'], length='knee', collar=True)
    O.belt(m, DARK_LEATHER)
    O.bracers(m, c['trim'])
    O.quiver(m, LEATHER, fletch=c['accent'])
    _hat(m, hat, 'hood', c, hat_color=c['main'], hat_trim=c['trim'])


def bare(m, c, hat, kw):
    """No clothes at all (a beast's own hide), or only [kw] belt."""
    if kw.get('belt'):
        O.belt(m, kw['belt'], buckle=kw.get('buckle'))


FN = {name: globals()[name] for name in list(DEFAULTS) + ['bare']}
DEFAULTS['bare'] = dict(main=LEATHER, trim=LEATHER, second=LEATHER, boots=LEATHER, accent=LEATHER)

CLASSES = ['tactician', 'sharpshooter', 'gunslinger', 'assault', 'scout', 'monk', 'heavy', 'barbarian',
           'guardian', 'support', 'psychic', 'white_mage', 'nature_mage', 'fire_mage', 'water_mage',
           'air_mage', 'earth_mage', 'necromancer', 'apothecary']
FOLK = ['peasant', 'noble', 'sailor', 'pirate', 'merchant', 'smith', 'bard', 'cleric', 'knight', 'miner',
        'scholar', 'hunter', 'rogue', 'tribal', 'warrior', 'gladiator', 'ranger']
