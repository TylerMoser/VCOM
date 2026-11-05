"""Colours of the poke_u buildings: one shared Base palette, the minimal-colour
groups of the TwoColor treatments, and the mapping into the pinned crate palette
(as the poke_r buildings' palettes.py).

Every voxel the sculptor makes carries a material label, never a colour, and
each treatment turns labels into palette indices here, so the same geometry can
be painted every way and the semantic groups survive recolouring.

- Base and Cartoon share one palette (BASE_PALETTE) holding every colour of the
  two buildings at fixed indices. poke_u.jpg is a JPEG of native pixel art, so
  the colours are the medians of each material's pixels (the cottage's of its
  three copies laid over each other), which takes out the compression's noise;
  the invented interiors and the buried foundation are noted, and glass is a
  little lighter so that what is behind still shows. Each roof is one material
  in one set of colours on all its faces, as the game lights them itself: the
  colour the art gives the faces turned neither left nor right (it draws the
  left slopes lit and the right ones shaded).
- TwoColor, as the user redefined it on 2026-10-28 (not exactly two colours;
  glass is an exception; as few colours as possible, similar ones merged into
  large flat regions), paints each label with its group's one colour; a family
  may fold a group into another (GROUPS' "=name").
- CratePalette copies the pinned crate palette byte for byte and maps each
  colour to its nearest entry among the indices allowed for its material class.
  Glass is painted with crate index 253, which no opaque label may use, and only
  that index carries the Glass material.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parent.parent.parent
CRATE = json.loads((WORK / "knowledge" / "palettes" / "crate-palette.json").read_text())
CRATE_RGBA = [tuple(c) for c in CRATE["rgba"]]

# label: (RGB, minimal-colour group, crate class). Order fixes the Base indices.
LABELS = {
    # Shared, invented (the art shows no inside): the buried foundation under each
    # floor, plank floors, the ceilings under the roofs.
    "found": ((112, 106, 96), "dark", "grey"),
    "found_dark": ((92, 86, 78), "dark", "grey"),
    "floor": ((150, 112, 74), "dark", "wood"),
    "floor_dark": ((124, 90, 58), "dark", "wood"),
    "floor_gap": ((96, 68, 44), "dark", "wood"),
    "ceiling": ((214, 210, 200), "light", "light"),

    # The roofs (both houses alike): red tiles, a few lighter, dark lines between
    # their courses and tiles, a darker ridge, the verges' and eaves' edge darker
    # still, the underside darkest.
    "roof": ((189, 86, 47), "roof", "red"),
    "roof_light": ((206, 104, 70), "roof", "red"),
    "roof_line": ((166, 70, 33), "roof", "red"),
    "roof_ridge": ((161, 61, 26), "roof", "red"),
    "roof_edge": ((147, 57, 14), "roof", "red"),
    "roof_under": ((96, 34, 10), "roof", "red"),
    # The timber frame: posts, beams and braces, light brown, their tops lit and
    # their feet and edges dark; the gables' dark infill between them.
    "timber": ((144, 118, 91), "dark", "wood"),
    "timber_light": ((194, 168, 137), "dark", "wood"),
    "timber_dark": ((86, 63, 40), "dark", "wood"),
    "gable": ((93, 80, 60), "gable", "wood"),
    # The walls: cream.
    "wall": ((196, 190, 176), "light", "light"),
    # The windows: white frames, a dark sill under the glass.
    "frame": ((225, 225, 245), "light", "light"),
    "frame_dark": ((70, 78, 95), "dark", "grey"),
    # The door: red boards, lit and shaded strips of its panels, brown jambs, a
    # cream knob.
    "door": ((190, 60, 45), "door", "red"),
    "door_light": ((205, 80, 65), "door", "red"),
    "door_dark": ((160, 45, 30), "door", "red"),
    "door_frame": ((150, 85, 60), "door", "red"),
    "knob": ((220, 180, 140), "light", "light"),
    # The flower boxes under the windows: dark red, cream flowers and their
    # grey-green leaves along the top.
    "box": ((125, 58, 36), "box", "red"),
    "box_dark": ((80, 24, 6), "box", "red"),
    "flower": ((215, 190, 150), "light", "light"),
    "leaf": ((140, 150, 110), "dark", "leaf"),
    # The chimneys: beige stacks, their caps' tops lit and their sides and the
    # stacks under them shaded, a dark flue.
    "chimney": ((185, 167, 136), "light", "light"),
    "chimney_light": ((200, 187, 159), "light", "light"),
    "chimney_band": ((165, 142, 114), "light", "light"),
    "flue": ((81, 63, 43), "dark", "wood"),

    # Glass: the art's periwinkle a little lighter, so that what is behind still
    # shows through; its clarity is GLASS_CLARITY.
    "glass_house": ((140, 150, 245), "glass", "glass"),
}

# MagicaVoxel Transparency of each glass label.
GLASS_CLARITY = {"glass_house": 0.7}

# Each family's minimal-colour groups: its own colour for each, or "=other" to
# fold the group into another (that group's colour and index). The door and the
# flower boxes are folded into the roof's red, the gables' infill into the
# timber's brown, as in both houses they are the same colours, near enough.
GROUPS = {
    "Cottage": {"roof": (189, 86, 47), "light": (196, 190, 176), "dark": (144, 118, 91), "gable": "=dark",
                "door": "=roof", "box": "=roof", "glass": (140, 150, 245)},
    "WingHouse": {"roof": (189, 86, 47), "light": (196, 190, 176), "dark": (144, 118, 91), "gable": "=dark",
                  "door": "=roof", "box": "=roof", "glass": (140, 150, 245)},
}
GROUP_CLARITY = 0.7

# Crate palette indices each material class may use. 253 is kept for glass.
CRATE_GLASS = 253
CRATE_CLASSES = {
    "grey": [177, 193, 194, 195, 201, 202, 203, 204, 205, 206, 240, 249, 250],
    # (246, a pale yellow-green, left out: it would turn creams green.)
    "light": [193, 194, 195, 196, 230, 236, 237, 238, 248],
    "wood": [178, 179, 180, 225, 226, 227, 228, 229, 230, 233, 234, 235, 236, 237, 238],
    "red": [178, 179, 180, 219, 220, 221, 222, 234, 235],
    "teal": [193, 205, 206, 243, 244, 252, 254],
    "blue": [193, 194, 205, 206, 249, 250, 251, 252, 254],
    "leaf": [241, 242, 243, 244, 245, 246],
    "flower": [211, 212, 213, 214, 220, 221, 222, 228, 229, 230, 251, 252],
    "pink": [213, 214, 219, 220],
    "glass": [CRATE_GLASS],
}
for _cls, _indices in CRATE_CLASSES.items():
    assert _cls == "glass" or CRATE_GLASS not in _indices
GROUP_CLASS = {"light": "light", "roof": "red", "dark": "wood", "gable": "wood", "door": "red", "box": "red",
               "glass": "glass"}
GROUP_CLASS_OF = {}
# Crate picks made by hand where the nearest entry would lose the art's contrast.
# The light group (the cream walls, frames and chimneys) on 195: its nearest, 194, is a mid grey
# that would take a third of the walls' contrast with the timber's 235 away.
CRATE_GROUP_PICKS = {"Cottage": {"light": 195}, "WingHouse": {"light": 195}}


def _distance(a, b):
    return sum((a[i] - b[i]) ** 2 for i in range(3))


def _nearest(rgb, indices):
    return min(indices, key=lambda i: (_distance(rgb, CRATE_RGBA[i - 1]), i))


# Base palette: each distinct colour once, by first appearance in LABELS; a glass
# colour is keyed apart from an opaque one of the same RGB, as its material differs.
_base_keys = []
BASE_INDEX = {}
for _label, (_rgb, _group, _cls) in LABELS.items():
    _key = (_rgb, _label in GLASS_CLARITY)
    if _key not in _base_keys:
        _base_keys.append(_key)
    BASE_INDEX[_label] = _base_keys.index(_key) + 1
assert len(_base_keys) <= 254
BASE_PALETTE = [(*k[0], 255) for k in _base_keys] + [(*_base_keys[0][0], 255)] * (256 - len(_base_keys))
BASE_GLASS = {BASE_INDEX[g]: t for g, t in GLASS_CLARITY.items()}
assert all((LABELS[l][1] == "glass") == (l in GLASS_CLARITY) for l in LABELS)


def resolve_group(family, group):
    """The group [group] is painted as in [family]: itself, or the one it folds into."""
    g = GROUPS[family][group]
    return g[1:] if isinstance(g, str) else group


def family_groups(family):
    """[family]'s own groups (those not folded into another), in GROUPS' order."""
    return [g for g, c in GROUPS[family].items() if not isinstance(c, str)]


def group_index(family, group):
    return family_groups(family).index(resolve_group(family, group)) + 1


def group_palette(family):
    cols = [GROUPS[family][g] for g in family_groups(family)]
    return [(*c, 255) for c in cols] + [(*cols[0], 255)] * (256 - len(cols))


def group_glass(family):
    if "glass" not in GROUPS[family]:
        return {}
    return {group_index(family, "glass"): GROUP_CLARITY}


def _class_of(family, group):
    return GROUP_CLASS_OF.get(family, {}).get(group, GROUP_CLASS[group])


def _crate_groups(family):
    """Each of [family]'s groups' crate index: a hand pick (CRATE_GROUP_PICKS), else
    its nearest in its class, in GROUPS' order, passing over an index an earlier
    group of the family took, so every group keeps a colour of its own."""
    taken = dict(CRATE_GROUP_PICKS.get(family, {}))
    for g in family_groups(family):
        if g in taken:
            continue
        rgb = GROUPS[family][g]
        free = [i for i in CRATE_CLASSES[_class_of(family, g)] if i not in taken.values()]
        taken[g] = _nearest(rgb, free)
    return taken


CRATE_GROUPS = {}


def crate_group_index(family, group):
    if family not in CRATE_GROUPS:
        CRATE_GROUPS[family] = _crate_groups(family)
    return CRATE_GROUPS[family][resolve_group(family, group)]


# Crate mappings: each label's colour to its class's nearest crate entry.
CRATE_INDEX = {label: _nearest(rgb, CRATE_CLASSES[cls]) for label, (rgb, group, cls) in LABELS.items()}
CRATE_GLASS_CLARITY = {CRATE_GLASS: 0.7}
for _label, _i in CRATE_INDEX.items():
    assert (_i == CRATE_GLASS) == (LABELS[_label][1] == "glass"), _label
for _family in GROUPS:
    for _g in family_groups(_family):
        assert (crate_group_index(_family, _g) == CRATE_GLASS) == (_g == "glass"), (_family, _g)
    _seen = [crate_group_index(_family, _g) for _g in family_groups(_family)]
    assert len(set(_seen)) == len(_seen), (_family, "two groups on one crate colour", _seen)


def paint(treatment, label, family):
    """The palette index [label] takes under [treatment] in [family]'s files."""
    two = "TwoColor" in treatment
    crate = "CratePalette" in treatment
    group = LABELS[label][1]
    if two and crate:
        return crate_group_index(family, group)
    if two:
        return group_index(family, group)
    if crate:
        return CRATE_INDEX[label]
    return BASE_INDEX[label]


def palette_of(treatment, family):
    """(palette, glass indices -> Transparency) of [family]'s [treatment] files."""
    if "CratePalette" in treatment:
        return CRATE_RGBA, CRATE_GLASS_CLARITY
    if "TwoColor" in treatment:
        return group_palette(family), group_glass(family)
    return BASE_PALETTE, BASE_GLASS


def groups_used(labels, family):
    """The groups [family]'s files paint [labels] with (folded groups resolved)."""
    return {resolve_group(family, LABELS[l][1]) for l in labels}
