"""Colours of the poke_f buildings: one shared Base palette, the minimal-colour
groups of the TwoColor treatments, and the mapping into the pinned crate palette
(as the poke_b game-ready buildings' palettes.py).

Every voxel the sculptor makes carries a material label, never a colour, and
each treatment turns labels into palette indices here, so the same geometry can
be painted every way and the semantic groups survive recolouring.

- Base and Cartoon share one palette (BASE_PALETTE) holding every colour of the
  four buildings at fixed indices, sampled from poke_f.png (the invented
  interiors, the buried foundation and the teal hall's hidden parts noted).
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
    # floor, plank and tiled floors, the ceilings under the upper floors.
    "found": ((112, 106, 96), "dark", "grey"),
    "found_dark": ((92, 86, 78), "dark", "grey"),
    "floor": ((150, 112, 74), "wood", "wood"),
    "floor_dark": ((124, 90, 58), "wood", "wood"),
    "floor_gap": ((96, 68, 44), "wood", "wood"),
    "tiles": ((206, 202, 192), "light", "light"),
    "tiles_line": ((168, 164, 156), "light", "light"),
    "ceiling": ((214, 210, 200), "light", "light"),

    # --- The blue house. ---
    "bh_wall": ((193, 191, 181), "light", "light"),
    "bh_wall_light": ((224, 216, 200), "light", "light"),
    "bh_frame": ((176, 176, 178), "light", "light"),
    "bh_timber": ((145, 118, 92), "wood", "wood"),
    "bh_timber_mid": ((122, 92, 55), "wood", "wood"),
    "bh_timber_dark": ((88, 63, 41), "wood", "wood"),
    "bh_timber_light": ((198, 174, 121), "wood", "light"),
    "bh_gable_dark": ((77, 72, 63), "wood", "grey"),
    "bh_roof_light": ((135, 171, 211), "blue", "blue"),
    "bh_roof": ((122, 162, 207), "blue", "blue"),
    "bh_roof_mid": ((88, 138, 194), "blue", "blue"),
    "bh_roof_shade": ((69, 125, 188), "blue", "blue"),
    "bh_roof_dark": ((53, 96, 144), "blue", "blue"),
    "bh_roof_black": ((34, 62, 93), "blue", "blue"),
    "bh_door": ((88, 138, 194), "blue", "blue"),
    "bh_door_dark": ((59, 108, 162), "blue", "blue"),
    "bh_brass": ((213, 190, 104), "light", "flower"),
    "bh_box": ((59, 108, 162), "blue", "blue"),
    "bh_leaf": ((65, 91, 68), "leaf", "leaf"),
    "bh_leaf_light": ((88, 140, 82), "leaf", "leaf"),
    "bh_flower_yellow": ((232, 204, 88), "flower", "flower"),
    "bh_flower_red": ((206, 86, 64), "flower", "flower"),
    "bh_chim": ((186, 167, 141), "light", "light"),
    "bh_chim_light": ((202, 187, 167), "light", "light"),
    "bh_chim_shade": ((167, 143, 109), "light", "light"),
    "bh_flue": ((81, 68, 49), "wood", "wood"),

    # --- The domed centre. ---
    "dc_white": ((206, 221, 227), "light", "light"),
    "dc_white_shade": ((176, 191, 198), "light", "light"),
    "dc_frame": ((193, 207, 214), "light", "light"),
    "dc_panel_light": ((135, 171, 211), "blue", "blue"),
    "dc_panel": ((122, 162, 207), "blue", "blue"),
    "dc_panel_mid": ((88, 138, 194), "blue", "blue"),
    "dc_panel_dark": ((69, 125, 188), "blue", "blue"),
    "dc_band": ((53, 96, 144), "blue", "blue"),
    "dc_band_dark": ((34, 62, 93), "blue", "blue"),
    "dc_red_light": ((203, 89, 88), "red", "red"),
    "dc_red_hi": ((199, 69, 68), "red", "red"),
    "dc_red": ((191, 42, 41), "red", "red"),
    "dc_red_shade": ((165, 37, 36), "red", "red"),
    "dc_red_dark": ((137, 32, 32), "red", "red"),
    "dc_ball_band": ((74, 83, 98), "dark", "grey"),
    "dc_ball_band_dark": ((64, 71, 85), "dark", "grey"),
    "dc_button": ((193, 207, 214), "light", "light"),
    "dc_button_mid": ((159, 186, 207), "light", "light"),
    "dc_button_ring": ((106, 114, 142), "dark", "grey"),
    "dc_button_dark": ((92, 99, 121), "dark", "grey"),
    "dc_pillar_light": ((176, 137, 105), "wood", "wood"),
    "dc_pillar": ((119, 88, 63), "wood", "wood"),
    "dc_pillar_mid": ((98, 73, 52), "wood", "wood"),
    "dc_pillar_dark": ((84, 63, 45), "wood", "wood"),
    "dc_cap": ((186, 167, 141), "light", "light"),
    "dc_step": ((186, 167, 141), "light", "light"),
    "dc_step_dark": ((143, 129, 97), "light", "light"),

    # --- The round shop. ---
    "rs_roof_light": ((226, 143, 107), "red", "red"),
    "rs_roof": ((213, 111, 80), "red", "red"),
    "rs_roof_dark": ((180, 85, 59), "red", "red"),
    "rs_roof_edge": ((112, 56, 41), "red", "red"),
    "rs_band": ((197, 97, 70), "red", "red"),
    "rs_white": ((237, 237, 237), "light", "light"),
    "rs_white_shade": ((211, 220, 215), "light", "light"),
    "rs_white_dark": ((149, 172, 158), "light", "light"),
    "rs_grey_light": ((140, 140, 141), "grey", "grey"),
    "rs_grey": ((114, 114, 115), "grey", "grey"),
    "rs_grey_mid": ((79, 79, 79), "grey", "grey"),
    "rs_grey_dark": ((59, 59, 59), "grey", "grey"),
    "rs_box": ((80, 71, 61), "wood", "wood"),
    "rs_box_dark": ((50, 42, 37), "wood", "wood"),
    "rs_leaf": ((40, 152, 110), "leaf", "leaf"),
    "rs_flower_pink": ((230, 130, 190), "flower", "flower"),
    "rs_flower_orange": ((240, 150, 60), "flower", "flower"),

    # --- The teal hall. ---
    "th_roof_lighter": ((66, 189, 189), "teal", "teal"),
    "th_roof_light": ((57, 173, 165), "teal", "teal"),
    "th_roof": ((41, 156, 148), "teal", "teal"),
    "th_roof_shade": ((33, 140, 123), "teal", "teal"),
    "th_roof_dark": ((24, 82, 66), "teal", "teal"),
    "th_wall": ((66, 189, 189), "teal", "teal"),
    "th_wall_shade": ((41, 156, 148), "teal", "teal"),
    "th_wall_dark": ((24, 123, 99), "teal", "teal"),
    "th_wall_deep": ((16, 107, 82), "teal", "teal"),
    "th_beige_light": ((239, 214, 181), "light", "light"),
    "th_beige": ((206, 181, 156), "light", "light"),
    "th_beige_mid": ((173, 140, 115), "light", "light"),
    "th_beige_dark": ((156, 123, 99), "light", "wood"),
    "th_band": ((189, 181, 140), "light", "light"),
    "th_band_dark": ((165, 156, 123), "light", "light"),
    "th_brown": ((107, 82, 57), "dark", "wood"),
    "th_brown_dark": ((88, 70, 46), "dark", "wood"),
    "th_white": ((242, 242, 242), "light", "light"),

    # Glass, as tints a little lighter than the art's, so that what is behind still
    # shows through; their clarity is GLASS_CLARITY.
    "glass_house": ((140, 140, 236), "glass", "glass"),
    "glass_center": ((152, 168, 246), "glass", "glass"),
    "glass_shop": ((122, 192, 232), "glass", "glass"),
    "glass_hall": ((132, 212, 236), "glass", "glass"),
}

GLASS_CLARITY = {"glass_house": 0.7, "glass_center": 0.7, "glass_shop": 0.7, "glass_hall": 0.7}

# Each family's minimal-colour groups: its own colour for each, or "=other" to
# fold the group into another (that group's colour and index).
GROUPS = {
    "BlueHouse": {"light": (193, 191, 181), "blue": (122, 162, 207), "wood": (145, 118, 92), "dark": "=wood",
                  "leaf": (65, 91, 68), "flower": (232, 204, 88), "glass": (140, 140, 236)},
    "DomeCenter": {"light": (206, 221, 227), "blue": (122, 162, 207), "red": (191, 42, 41), "dark": (74, 83, 98),
                   "wood": (119, 88, 63), "glass": (152, 168, 246)},
    "RoundShop": {"light": (237, 237, 237), "red": (213, 111, 80), "grey": (114, 114, 115), "wood": "=grey",
                  "dark": "=grey", "leaf": (40, 152, 110), "flower": (230, 130, 190), "glass": (122, 192, 232)},
    "TealHall": {"teal": (41, 156, 148), "light": (206, 181, 156), "dark": (107, 82, 57), "wood": "=dark",
                 "glass": (132, 212, 236)},
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
GROUP_CLASS = {"light": "light", "red": "red", "dark": "grey", "blue": "blue", "grey": "grey", "wood": "wood",
               "teal": "teal", "leaf": "leaf", "flower": "flower", "glass": "glass"}
GROUP_CLASS_OF = {"TealHall": {"dark": "wood"}}
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
