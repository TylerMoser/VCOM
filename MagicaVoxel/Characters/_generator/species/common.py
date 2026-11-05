"""What every species module shares: the Set a folder of models is, palettes of skin, hair
and eyes, and person(), the builder of a figure with a humanlike face."""
from core import base_body, shade, mix, sat, rgb
import heads as H
import outfits as O
import classes as C
import extras as X


class Set:
    """A folder of models: [path] under MagicaVoxel/Characters, [kind] the files' prefix,
    [designs] (descriptor, builder) pairs, rig-ready; [treatments] (design number, name);
    [concepts] (descriptor, builder) pairs, free proportions."""

    def __init__(self, path, kind, designs, treatments=(), concepts=(), title=None):
        self.path = path
        self.kind = kind
        self.designs = list(designs)
        self.treatments = list(treatments)
        self.concepts = list(concepts)
        self.title = title or path.replace('/', ' / ')


def designs(builder, specs):
    """(descriptor, builder) pairs from (descriptor, keywords) pairs."""
    return [(name, (lambda kw=kw: builder(**kw))) for name, kw in specs]


SKIN = {
    'porcelain': (246, 224, 208), 'fair': (238, 204, 178), 'light': (228, 186, 152),
    'peach': (240, 190, 160), 'tan': (206, 158, 118), 'olive': (190, 152, 108),
    'golden': (214, 164, 104), 'brown': (162, 112, 78), 'umber': (128, 84, 56),
    'deep': (92, 60, 44), 'ruddy': (224, 160, 130), 'ashen': (200, 196, 190),
}
HAIR = {
    'black': (34, 30, 34), 'raven': (40, 40, 60), 'darkbrown': (72, 46, 30), 'brown': (112, 74, 44),
    'chestnut': (136, 70, 40), 'auburn': (152, 62, 36), 'ginger': (204, 104, 50), 'copper': (186, 90, 44),
    'blonde': (228, 196, 116), 'sandy': (200, 170, 110), 'platinum': (238, 234, 214), 'grey': (168, 168, 170),
    'white': (236, 236, 236), 'silver': (200, 204, 214),
}
EYES = {
    'blue': (60, 112, 196), 'green': (66, 146, 80), 'brown': (112, 70, 40), 'hazel': (150, 116, 56),
    'grey': (130, 144, 160), 'amber': (214, 150, 40), 'violet': (140, 90, 200), 'teal': (40, 150, 150),
    'red': (200, 40, 40), 'gold': (230, 190, 60), 'black': (30, 28, 32), 'ice': (160, 220, 240),
}


def mouth_color(skin):
    return mix(skin, (96, 40, 44), 0.5)


def person(skin, hair=None, hair_style='short', eyes='template', iris='blue', brows='flat',
           brow_color=None, nose=None, mouth='line', mouth_z=None, mouth_w=3, beard=None,
           beard_color=None, ears=None, head=None, outfit=None, hat=True, extras=None,
           freckles=None, blush=None, eye_z=None, eye_gap=3, eye_w=2, eye_h=2, glow_eyes=False,
           fringe=True, body=None, skin_group='skin', outfit_kw=None, before_outfit=None,
           highlight=None):
    """A figure with a humanlike face. [skin], [hair], [iris] are colours or names in SKIN,
    HAIR, EYES; [head] the head's shape (make_head's keywords); [outfit] a class or folk name
    (classes.py) with [outfit_kw]; [extras] a function run last on the model."""
    skin = SKIN.get(skin, skin) if isinstance(skin, str) else skin
    hair = HAIR.get(hair, hair) if isinstance(hair, str) else hair
    iris = EYES.get(iris, iris) if isinstance(iris, str) else iris
    m = base_body(body or skin, skin_group)
    hd = H.make_head(m, skin, skin_group, **(head or {}))
    if eyes:
        H.eyes(m, hd, eyes, iris=iris, z=eye_z, gap=eye_gap, width=eye_w, height=eye_h, glow=glow_eyes)
    if brows and hair is not None or (brows and brow_color):
        bz = (eye_z if eye_z is not None else hd.z0 + 2) + eye_h + (1 if eyes == 'template' else 0)
        H.brows(m, hd, brow_color or shade(hair, 0.85), z=bz, style=brows, gap=eye_gap, width=eye_w)
    if nose:
        H.nose(m, hd, nose, z=(eye_z if eye_z is not None else hd.z0 + 2) - (0 if nose == 'button' else 1))
    if mouth:
        H.mouth(m, hd, mouth, color=mouth_color(skin), z=mouth_z if mouth_z is not None else hd.z0, width=mouth_w)
    if blush:
        H.cheeks(m, hd, blush, z=(eye_z if eye_z is not None else hd.z0 + 2) - 1, gap=eye_gap, width=eye_w)
    if freckles:
        for x in (13, 14, 18, 19):
            z = (eye_z if eye_z is not None else hd.z0 + 2) - 1
            if (x % 2) == 0:
                H.face_cell(m, hd, x, z, freckles, 'detail')
    if ears:
        H.ears(m, hd, ears, skin, inner=shade(skin, 0.85))
    if hair is not None and hair_style:
        H.hair(m, hd, hair, hair_style, fringe=fringe, highlight=highlight)
    if beard:
        H.beard(m, hd, beard_color or hair, beard)
    if before_outfit:
        before_outfit(m)
    if outfit:
        C.dress(m, outfit, hat=hat, **(outfit_kw or {}))
    if extras:
        extras(m)
    return m


def beast(fur, skin_group='fur', head=None, muzzle=None, ears=None, ear_color=None, ear_inner=None,
          eyes='pupil', iris='amber', eye_z=None, eye_gap=3, eye_w=2, eye_h=2, glow_eyes=False,
          brows=None, brow_color=None, mouth=None, mouth_color_=None, belly_color=None, face=None,
          pattern=None, tail=None, tail_color=None, tail_tip=None, tail_second=None, hands=None,
          hand_color=None, feet=None, feet_color=None, outfit=None, outfit_kw=None, hat=False,
          horns=None, horn_color=None, horn_tip=None, mane=None, mane_color=None, whiskers=None,
          hair=None, hair_style=None, extras=None, before_outfit=None, body=None, head_color=None,
          nose=None, nose_color=None, cheeks=None):
    """A figure with a beast's head and hide. [head] make_head's keywords; [muzzle] snout()'s
    (length, w, h, z, color, nose_color, taper, jaw, top, teeth); [face] a function painting
    the face; [pattern] a function painting the hide before the clothes go on."""
    fur = SKIN.get(fur, fur) if isinstance(fur, str) else fur
    iris = EYES.get(iris, iris) if isinstance(iris, str) else iris
    hc = head_color or fur
    m = base_body(body or fur, skin_group)
    hd = H.make_head(m, hc, skin_group, **(head or {}))
    top = hd.z0 - 1
    if muzzle:
        mz = dict(muzzle)
        mcol = mz.pop('color', shade(hc, 1.1))
        H.snout(m, hd, mcol, group=skin_group, **mz)
        top = mz.get('z', hd.z0) + mz.get('h', 3) - 1
    ez = eye_z if eye_z is not None else max(hd.z0 + 2, top + 1)
    if eyes:
        H.eyes(m, hd, eyes, iris=iris, z=ez, gap=eye_gap, width=eye_w, height=eye_h, glow=glow_eyes)
    if brows:
        H.brows(m, hd, brow_color or shade(hc, 0.6), z=ez + eye_h, style=brows, gap=eye_gap, width=eye_w)
    if nose:
        H.nose(m, hd, nose, color=nose_color, z=ez - 1)
    if mouth:
        H.mouth(m, hd, mouth, color=mouth_color_ or mix(hc, (60, 30, 30), 0.6), z=hd.z0, width=3)
    if cheeks:
        H.cheeks(m, hd, cheeks, z=ez - 1, gap=eye_gap, width=eye_w)
    if face:
        face(m, hd)
    if ears:
        H.ears(m, hd, ears, ear_color or hc, inner=ear_inner)
    if horns:
        H.horns(m, hd, horns, horn_color or (230, 220, 200), tip=horn_tip)
    if mane:
        X.mane(m, mane_color or shade(fur, 0.7), size=mane if isinstance(mane, int) else 2)
    if hair is not None and hair_style:
        H.hair(m, hd, hair, hair_style)
    if whiskers:
        X.whiskers(m, whiskers)
    if belly_color:
        X.belly(m, belly_color)
    if pattern:
        pattern(m)
    if hands == 'paws':
        X.paws(m, hand_color or shade(fur, 0.7))
    elif hands == 'claws':
        X.claws(m, hand_color or (230, 226, 210))
    elif hands == 'big_claws':
        X.big_claws(m, hand_color or shade(fur, 0.8))
    elif hands == 'pincers':
        X.pincers(m, hand_color or fur)
    elif hands and hand_color:
        m.paint(hand_color, None, parts=('hand_r', 'hand_l'))
    if feet == 'hooves':
        X.hooves(m, feet_color or (60, 50, 44))
    elif feet == 'talons':
        X.talons(m, feet_color or (220, 180, 60))
    elif feet == 'webbed':
        X.webbed_feet(m, feet_color or shade(fur, 0.85))
    elif feet and feet_color:
        m.paint(feet_color, None, parts=('foot_r', 'foot_l'))
    if before_outfit:
        before_outfit(m)
    if outfit:
        C.dress(m, outfit, hat=hat, **(outfit_kw or {}))
    if tail:
        X.tail(m, tail, tail_color or fur, tip=tail_tip, group=skin_group if skin_group != 'skin' else 'skin', second=tail_second)
    if extras:
        extras(m)
    return m
