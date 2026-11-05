"""Colours of the poke_h building: one Base palette, the minimal-colour groups of
the TwoColor treatments, and the mapping into the pinned crate palette (as the
poke_g buildings' palettes.py).

Every voxel the sculptor makes carries a material label, never a colour, and
each treatment turns labels into palette indices here, so the same geometry can
be painted every way and the semantic groups survive recolouring.

- Base and Cartoon share one palette (BASE_PALETTE) holding every colour of the
  farmhouse at fixed indices: poke_b's flower cottage's (poke_h.png draws the
  same house, pixel for pixel above its porch), the porch's and the vines'
  sampled from poke_h.png (the invented interiors and the buried foundation
  noted).
- TwoColor, as the user redefined it on 2026-10-28 (not exactly two colours;
  glass is an exception; as few colours as possible, similar ones merged into
  large flat regions), paints each label with its group's one colour, the
  family giving its groups its own most telling colour from the art; a family
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
    # floor, plank floors, the ceilings under the upper floor.
    "found": ((112, 106, 96), "dark", "grey"),
    "found_dark": ((92, 86, 78), "dark", "grey"),
    "floor": ((150, 112, 74), "wood", "wood"),
    "floor_dark": ((124, 90, 58), "wood", "wood"),
    "floor_gap": ((96, 68, 44), "wood", "wood"),
    "ceiling": ((214, 210, 200), "light", "light"),

    # --- The farmhouse: poke_b's flower cottage's colours, and its outside stair. ---
    "co_wall": ((230, 202, 140), "light", "light"),
    "co_wall_mid": ((202, 163, 129), "light", "light"),
    "co_band": ((184, 155, 103), "light", "light"),
    "co_band_dark": ((132, 107, 62), "dark", "wood"),
    "co_timber": ((87, 73, 45), "dark", "wood"),
    "co_timber_dark": ((55, 49, 43), "dark", "wood"),
    "co_white": ((238, 238, 247), "light", "light"),
    "co_frame": ((182, 182, 184), "light", "light"),
    "co_frame_dark": ((148, 148, 152), "light", "light"),
    "co_roof": ((184, 84, 48), "red", "red"),
    "co_roof_dark": ((145, 65, 38), "red", "red"),
    "co_roof_mid": ((159, 72, 42), "red", "red"),
    "co_roof_light": ((216, 105, 65), "red", "red"),
    "co_roof_hi": ((203, 96, 59), "red", "red"),
    "co_roof_edge": ((112, 50, 29), "red", "red"),
    "co_roof_black": ((67, 31, 18), "dark", "wood"),
    "co_sky_frame": ((146, 164, 144), "dark", "grey"),
    "co_sky_frame_dark": ((118, 130, 112), "dark", "grey"),
    "co_door": ((74, 137, 126), "teal", "teal"),
    "co_door_mid": ((63, 116, 106), "teal", "teal"),
    "co_door_dark": ((48, 80, 73), "teal", "teal"),
    "co_brass": ((223, 188, 106), "light", "flower"),
    "co_box": ((112, 83, 48), "wood", "wood"),
    "co_box_dark": ((55, 49, 43), "dark", "wood"),
    "co_leaf": ((49, 156, 107), "leaf", "leaf"),
    "co_leaf_dark": ((41, 132, 90), "leaf", "leaf"),
    "co_flower_pink": ((173, 74, 156), "flower", "flower"),
    "co_flower_orange": ((247, 115, 66), "flower", "flower"),
    "co_flower_yellow": ((255, 156, 49), "flower", "flower"),
    "co_tread": ((203, 180, 130), "light", "light"),
    "co_tread_mid": ((179, 149, 120), "light", "wood"),
    "co_riser": ((151, 125, 99), "light", "wood"),
    "co_riser_dark": ((128, 104, 81), "dark", "wood"),
    "co_stringer": ((203, 96, 59), "red", "red"),
    "co_stringer_dark": ((168, 75, 45), "red", "red"),
    "co_stringer_black": ((72, 33, 19), "dark", "wood"),
    "co_landing": ((152, 152, 154), "light", "light"),
    "co_landing_dark": ((120, 120, 122), "dark", "grey"),

    # --- The porch's posts and the vines, sampled from poke_h.png. ---
    "fh_post": ((156, 115, 66), "wood", "wood"),
    "fh_post_mid": ((112, 83, 48), "wood", "wood"),
    "fh_post_dark": ((74, 66, 57), "dark", "wood"),
    "fh_flower_rose": ((214, 82, 132), "flower", "flower"),

    # Glass, as tints a little lighter than the art's, so that what is behind still
    # shows through; their clarity is GLASS_CLARITY.
    "glass_cottage": ((128, 172, 216), "glass", "glass"),
    "glass_dark": ((86, 92, 88), "glass", "glass"),
}

# MagicaVoxel Transparency of each glass label: the windows' 0.7, the roof lights
# darker glass, as drawn (poke_b's).
GLASS_CLARITY = {"glass_cottage": 0.7, "glass_dark": 0.45}

# The family's minimal-colour groups: its own colour for each, or "=other" to fold
# the group into another (that group's colour and index). poke_b's cottage's.
GROUPS = {
    "Farmhouse": {"light": (230, 202, 140), "red": (184, 84, 48), "dark": (87, 73, 45), "wood": "=dark",
                  "teal": (74, 137, 126), "leaf": (49, 156, 107), "flower": (247, 115, 66),
                  "glass": (128, 172, 216)},
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
GROUP_CLASS = {"light": "light", "red": "red", "dark": "wood", "grey": "grey", "wood": "wood", "teal": "teal",
               "leaf": "leaf", "flower": "flower", "glass": "glass"}
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
