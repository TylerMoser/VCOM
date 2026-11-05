"""Colours of the poke_i buildings: one shared Base palette, the minimal-colour
groups of the TwoColor treatments, and the mapping into the pinned crate palette
(as the poke_g buildings' palettes.py).

Every voxel the sculptor makes carries a material label, never a colour, and
each treatment turns labels into palette indices here, so the same geometry can
be painted every way and the semantic groups survive recolouring.

- Base and Cartoon share one palette (BASE_PALETTE) holding every colour of the
  three buildings at fixed indices, sampled from poke_i.jpg (the invented
  interiors and the buried foundation noted). The source is a scaled-down JPEG,
  so its colours were taken as the medians and clusters of whole regions (its
  blur darkens the small ones) and the small features' from their brightest
  pixels.
- TwoColor, as the user redefined it on 2026-10-28 (not exactly two colours;
  glass is an exception; as few colours as possible, similar ones merged into
  large flat regions), paints each label with its group's one colour, each family
  giving its groups its own most telling colour from the art; a family may fold a
  group into another (GROUPS' "=name").
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
    "floor": ((150, 112, 74), "wood", "wood"),
    "floor_dark": ((124, 90, 58), "wood", "wood"),
    "floor_gap": ((96, 68, 44), "wood", "wood"),
    "ceiling": ((214, 210, 200), "light", "light"),

    # --- The small house. ---
    "sh_roof_light": ((186, 126, 52), "roof", "wood"),
    "sh_roof": ((168, 108, 38), "roof", "wood"),
    "sh_roof_shade": ((146, 91, 27), "roof", "wood"),
    "sh_roof_line": ((132, 80, 23), "roof", "wood"),
    "sh_ridge": ((211, 151, 66), "roof", "wood"),
    "sh_roof_edge": ((80, 49, 24), "roof", "wood"),
    "sh_gable": ((97, 76, 55), "wood", "wood"),
    "sh_gable_board": ((125, 108, 78), "wood", "wood"),
    "sh_wall": ((104, 79, 53), "wood", "wood"),
    "sh_wall_light": ((116, 92, 64), "wood", "wood"),
    "sh_wall_line": ((80, 60, 40), "wood", "wood"),
    "sh_beam": ((127, 99, 72), "wood", "wood"),
    "sh_post": ((80, 49, 24), "wood", "wood"),
    "sh_door": ((140, 40, 46), "door", "red"),
    "sh_door_line": ((112, 36, 40), "door", "red"),
    "sh_door_dark": ((82, 32, 30), "door", "red"),
    "sh_jamb": ((188, 154, 138), "light", "light"),
    "sh_knob": ((210, 180, 90), "light", "flower"),
    "sh_frame": ((219, 214, 218), "light", "light"),

    # --- The chimney house. ---
    "ch_roof_light": ((201, 139, 58), "roof", "wood"),
    "ch_roof": ((168, 108, 39), "roof", "wood"),
    "ch_roof_shade": ((141, 87, 28), "roof", "wood"),
    "ch_roof_line": ((120, 74, 22), "roof", "wood"),
    "ch_ridge": ((212, 150, 62), "roof", "wood"),
    "ch_roof_edge": ((96, 56, 14), "roof", "wood"),
    "ch_wall": ((120, 101, 74), "wood", "wood"),
    "ch_wall_light": ((145, 128, 102), "wood", "wood"),
    "ch_wall_line": ((90, 74, 52), "wood", "wood"),
    "ch_post": ((76, 69, 47), "wood", "wood"),
    "ch_beam": ((137, 112, 87), "wood", "wood"),
    "ch_cream": ((201, 186, 182), "light", "light"),
    "ch_panel": ((222, 209, 211), "light", "light"),
    "ch_timber": ((108, 70, 46), "wood", "wood"),
    "ch_timber_board": ((140, 100, 70), "wood", "wood"),
    "ch_door": ((150, 44, 52), "door", "red"),
    "ch_door_line": ((120, 40, 46), "door", "red"),
    "ch_door_dark": ((90, 34, 36), "door", "red"),
    "ch_knob": ((210, 180, 90), "light", "flower"),
    "ch_frame": ((230, 226, 228), "light", "light"),
    "ch_stone": ((152, 144, 148), "stone", "grey"),
    "ch_stone_light": ((188, 175, 155), "stone", "light"),
    "ch_stone_shade": ((120, 112, 110), "stone", "grey"),
    "ch_flue": ((55, 53, 34), "dark", "grey"),

    # --- The day care. ---
    "day_roof_light": ((200, 124, 70), "roof", "wood"),
    "day_roof": ((177, 98, 50), "roof", "wood"),
    "day_roof_dark": ((153, 77, 38), "roof", "wood"),
    "day_roof_line": ((126, 67, 29), "roof", "wood"),
    "day_roof_edge": ((84, 49, 20), "roof", "wood"),
    "day_roof_top": ((207, 126, 65), "roof", "wood"),
    "day_rail": ((205, 187, 171), "light", "light"),
    "day_wall": ((214, 196, 172), "light", "light"),
    "day_frame": ((232, 222, 206), "light", "light"),
    "day_base": ((128, 98, 68), "wood", "wood"),
    "day_post": ((100, 74, 48), "wood", "wood"),
    "day_beam": ((128, 98, 68), "wood", "wood"),
    "day_canopy": ((157, 79, 36), "roof", "red"),
    "day_canopy_dark": ((120, 60, 28), "roof", "red"),

    # Glass, as tints a little lighter than the art's, so that what is behind still
    # shows through; their clarity is GLASS_CLARITY.
    "glass_sh": ((189, 193, 232), "glass", "glass"),
    "glass_ch": ((190, 195, 245), "glass", "glass"),
    "glass_day": ((160, 156, 210), "glass", "glass"),
    "glass_door": ((70, 92, 110), "glass", "glass"),
}

# MagicaVoxel Transparency of each glass label: the windows' 0.7, the day care's
# door darker glass, as drawn.
GLASS_CLARITY = {"glass_sh": 0.7, "glass_ch": 0.7, "glass_day": 0.7, "glass_door": 0.45}

# Each family's minimal-colour groups: its own colour for each, or "=other" to
# fold the group into another (that group's colour and index).
GROUPS = {
    "SmallHouse": {"roof": (168, 108, 38), "wood": (104, 79, 53), "light": (219, 214, 218), "door": "=roof",
                   "dark": "=wood", "glass": (189, 193, 232)},
    "ChimneyHouse": {"roof": (168, 108, 39), "wood": (120, 101, 74), "light": (201, 186, 182), "door": "=roof",
                     "stone": "=light", "dark": "=wood", "glass": (190, 195, 245)},
    "DayCare": {"roof": (177, 98, 50), "light": (214, 196, 172), "wood": (100, 74, 48), "dark": "=wood",
                "glass": (160, 156, 210)},
}
GROUP_CLARITY = 0.7

# Crate palette indices each material class may use. 253 is kept for glass.
CRATE_GLASS = 253
CRATE_CLASSES = {
    "grey": [177, 193, 194, 195, 201, 202, 203, 204, 205, 206, 240, 249, 250],
    "light": [193, 194, 195, 196, 230, 236, 237, 238, 246, 248],
    "wood": [178, 179, 180, 225, 226, 227, 228, 229, 230, 233, 234, 235, 236, 237, 238],
    "red": [178, 179, 180, 219, 220, 221, 222, 234, 235],
    "teal": [193, 205, 206, 243, 244, 252, 254],
    "blue": [193, 194, 205, 206, 249, 250, 251, 252, 254],
    "leaf": [241, 242, 243, 244, 245, 246],
    "flower": [211, 212, 213, 214, 220, 221, 222, 228, 229, 230, 251, 252],
    "glass": [CRATE_GLASS],
}
for _cls, _indices in CRATE_CLASSES.items():
    assert _cls == "glass" or CRATE_GLASS not in _indices
GROUP_CLASS = {"light": "light", "roof": "wood", "wood": "wood", "door": "red", "stone": "grey", "dark": "grey",
               "glass": "glass"}
GROUP_CLASS_OF = {}
# Crate picks made by hand where the nearest entry would lose the art's contrast.
CRATE_GROUP_PICKS = {}


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
