"""Colours of the poke_b game-ready buildings: one shared Base palette, the
minimal-colour groups of the TwoColor treatments, and the mapping into the
pinned crate palette.

Every voxel the sculptor makes carries a material label, never a colour, and
each treatment turns labels into palette indices here, so the same geometry can
be painted every way and the semantic groups survive recolouring.

- Base and Cartoon share one palette (BASE_PALETTE) holding every colour of all
  six buildings at fixed indices, sampled from poke_b.png (the invented
  interiors and the buried foundation are noted). A combat map using several of
  them adds these colours to its level palette once.
- TwoColor, as the user redefined it on 2026-10-28 (not exactly two colours;
  glass is an exception; as few colours as possible, similar ones merged into
  large flat regions), paints each label with its group's one colour. Groups
  are named by what they are (light, red, dark, stone, grey, wood, teal, leaf,
  flower, glass) and each family gives its own groups their colour, its most
  telling one from the art, so the clinic's red is the clinic's and the lab's
  the lab's. A family may fold a group into another (GROUPS' "=name"), when the
  two would be alike in it.
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
    "joist": ((120, 92, 66), "dark", "wood"),
    "outline": ((45, 45, 45), "dark", "grey"),

    # --- The domed lab. ---
    "lab_wall": ((223, 223, 223), "light", "light"),
    "lab_wall_shade": ((193, 193, 193), "light", "light"),
    "lab_wall_dark": ((165, 165, 165), "light", "light"),
    "lab_frame": ((176, 176, 178), "light", "light"),
    "lab_white": ((224, 224, 242), "light", "light"),
    "lab_cream_light": ((228, 217, 209), "light", "light"),
    "lab_cream": ((217, 199, 187), "light", "light"),
    "lab_cream_mid": ((206, 183, 168), "light", "light"),
    "lab_cream_dark": ((188, 157, 137), "light", "light"),
    "lab_tan": ((169, 130, 103), "dark", "wood"),
    "lab_brown": ((114, 84, 65), "dark", "wood"),
    "lab_black": ((40, 40, 40), "dark", "grey"),
    "lab_roof": ((231, 124, 109), "red", "red"),
    "lab_roof_dark": ((226, 102, 84), "red", "red"),
    "lab_ring": ((216, 60, 37), "red", "red"),
    "lab_dome": ((239, 233, 228), "light", "light"),
    "lab_dome_shade": ((223, 208, 198), "light", "light"),
    "lab_emblem": ((122, 138, 182), "dark", "blue"),
    "lab_emblem_light": ((228, 237, 255), "light", "light"),

    # --- The red clinic. ---
    "cl_red": ((219, 94, 57), "red", "red"),
    "cl_red_mid": ((220, 103, 69), "red", "red"),
    "cl_red_light": ((224, 117, 86), "red", "red"),
    "cl_red_dark": ((198, 72, 36), "red", "red"),
    "cl_red_deep": ((167, 62, 31), "red", "red"),
    "cl_red_shadow": ((141, 52, 27), "red", "red"),
    "cl_white": ((233, 237, 235), "light", "light"),
    "cl_wall": ((194, 205, 199), "light", "light"),
    "cl_wall_mid": ((181, 193, 186), "light", "light"),
    "cl_wall_shade": ((176, 191, 182), "light", "light"),
    "cl_wall_dark": ((139, 160, 147), "light", "light"),
    "cl_trim": ((204, 201, 220), "light", "light"),
    "cl_trim_dark": ((156, 155, 160), "light", "grey"),
    "cl_pillar": ((81, 89, 94), "dark", "grey"),
    "cl_pillar_mid": ((88, 98, 103), "dark", "grey"),
    "cl_pillar_dark": ((70, 77, 81), "dark", "grey"),
    "cl_frame": ((62, 56, 47), "dark", "grey"),
    "cl_frame_dark": ((51, 46, 38), "dark", "grey"),
    "cl_green_dark": ((98, 119, 106), "dark", "grey"),

    # --- The mansard houses (A, its cyan twin, B): stone, slate, boards. ---
    "m_light": ((206, 221, 227), "light", "light"),
    "m_pale": ((176, 176, 178), "light", "light"),
    "m_white": ((224, 224, 242), "light", "light"),
    "m_stone_light": ((141, 165, 184), "stone", "blue"),
    "m_stone": ((109, 137, 159), "stone", "blue"),
    "m_stone_mid": ((109, 124, 141), "stone", "blue"),
    "m_stone_dark": ((85, 102, 121), "stone", "blue"),
    "m_stone_deep": ((89, 102, 117), "stone", "blue"),
    "m_cheek": ((191, 211, 219), "light", "light"),
    "m_cheek_mid": ((173, 200, 209), "light", "light"),
    "m_cheek_dark": ((162, 189, 196), "light", "light"),
    "m_cap": ((52, 63, 73), "dark", "grey"),
    "m_tread": ((196, 196, 215), "light", "light"),
    "m_riser": ((147, 147, 149), "light", "light"),
    "m_riser_dark": ((112, 115, 137), "stone", "blue"),
    "m_roof": ((156, 152, 143), "grey", "grey"),
    "m_roof_mid": ((139, 133, 123), "grey", "grey"),
    "m_roof_shade": ((130, 124, 114), "grey", "grey"),
    "m_roof_dark": ((106, 102, 93), "grey", "grey"),
    "m_roof_black": ((88, 85, 78), "grey", "grey"),
    "m_roof_line": ((65, 63, 65), "dark", "grey"),
    "m_cheek_grey": ((112, 126, 131), "grey", "grey"),
    "m_flue_top": ((201, 199, 201), "light", "light"),
    "m_flue": ((113, 111, 113), "grey", "grey"),
    "m_flue_side": ((141, 148, 141), "grey", "grey"),
    "m_flue_shade": ((109, 116, 109), "grey", "grey"),
    "m_dormer_frame": ((56, 123, 175), "stone", "blue"),
    "m_black": ((11, 11, 11), "dark", "grey"),
    "m_handle": ((193, 173, 72), "wood", "flower"),
    "m_door": ((109, 137, 159), "stone", "blue"),
    "m_door_dark": ((89, 102, 117), "stone", "blue"),
    "m_door_light": ((141, 165, 184), "stone", "blue"),
    # House A's tan boards and every house's shutters.
    "a_board": ((204, 141, 92), "wood", "wood"),
    "a_board_light": ((222, 160, 111), "wood", "wood"),
    "a_board_shade": ((168, 118, 81), "wood", "wood"),
    "a_board_line": ((137, 98, 69), "wood", "wood"),
    "sh_light": ((152, 128, 88), "wood", "wood"),
    "sh_mid": ((144, 112, 72), "wood", "wood"),
    "sh": ((128, 96, 56), "wood", "wood"),
    "sh_dark": ((112, 80, 48), "wood", "wood"),
    "sh_edge": ((80, 56, 32), "wood", "wood"),
    # House B's and the cyan house's brown boards.
    "b_board": ((128, 96, 56), "wood", "wood"),
    "b_board_light": ((152, 128, 88), "wood", "wood"),
    "b_board_dark": ((112, 80, 48), "wood", "wood"),
    "b_board_line": ((80, 56, 32), "wood", "wood"),
    "cy_board": ((144, 112, 72), "wood", "wood"),
    # The cyan house's teal mansard and orange door.
    "cy_roof": ((132, 192, 196), "teal", "teal"),
    "cy_roof_mid": ((104, 179, 183), "teal", "teal"),
    "cy_roof_shade": ((87, 170, 174), "teal", "teal"),
    "cy_roof_dark": ((77, 157, 162), "teal", "teal"),
    "cy_roof_black": ((65, 134, 137), "teal", "teal"),
    "cy_door": ((162, 85, 34), "wood", "wood"),
    "cy_door_light": ((192, 102, 41), "wood", "wood"),
    "cy_door_dark": ((140, 74, 30), "wood", "wood"),

    # --- The flower cottage and its outside stair. ---
    "co_wall": ((230, 202, 140), "light", "light"),
    "co_wall_mid": ((202, 163, 129), "light", "light"),
    "co_wall_shade": ((190, 165, 118), "light", "light"),
    "co_wall_dark": ((192, 147, 105), "light", "light"),
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

    # Glass, as tints a little lighter than the art's, so that what is behind still
    # shows through; their clarity is GLASS_CLARITY.
    "glass_lab": ((158, 194, 226), "glass", "glass"),
    "glass_clinic": ((130, 192, 214), "glass", "glass"),
    "glass_teal": ((96, 150, 138), "glass", "glass"),
    "glass_sky": ((160, 196, 226), "glass", "glass"),
    "glass_house": ((132, 176, 220), "glass", "glass"),
    "glass_cottage": ((128, 172, 216), "glass", "glass"),
    "glass_dark": ((86, 92, 88), "glass", "glass"),
}

# MagicaVoxel Transparency of each glass label, as SimpleWindow1's 0.9 and the
# street lamp's 0.85 are set: how much of what is behind shows through. The
# clinic's teal window and the cottage's roof lights are darker glass, as drawn.
GLASS_CLARITY = {"glass_lab": 0.7, "glass_clinic": 0.7, "glass_teal": 0.5, "glass_sky": 0.7, "glass_house": 0.7,
                 "glass_cottage": 0.7, "glass_dark": 0.45}

# Each family's minimal-colour groups: its own colour for each, or "=other" to
# fold the group into another (that group's colour and index).
GROUPS = {
    "DomeLab": {"light": (228, 217, 209), "red": (231, 124, 109), "dark": (114, 84, 65), "wood": "=dark",
                "glass": (158, 194, 226)},
    "RedClinic": {"light": (194, 205, 199), "red": (219, 94, 57), "dark": (81, 89, 94), "wood": "=dark",
                  "glass": (130, 192, 214)},
    "GrayEntryHouse": {"light": (206, 221, 227), "stone": (109, 137, 159), "grey": (156, 152, 143),
                       "wood": (204, 141, 92), "dark": "=stone", "glass": (132, 176, 220)},
    "GrayWindowHouse": {"light": (206, 221, 227), "stone": (109, 137, 159), "grey": (156, 152, 143),
                        "wood": (128, 96, 56), "dark": "=stone", "glass": (132, 176, 220)},
    "CyanEntryHouse": {"light": (206, 221, 227), "stone": (109, 137, 159), "teal": (132, 192, 196),
                       "grey": "=teal", "wood": (144, 112, 72), "dark": "=stone", "glass": (132, 176, 220)},
    "FlowerCottage": {"light": (230, 202, 140), "red": (184, 84, 48), "dark": (87, 73, 45), "wood": "=dark",
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
    "teal": [193, 205, 206, 252, 254],
    "blue": [193, 194, 205, 206, 250, 251, 252, 254],
    "leaf": [241, 242, 243, 244, 245, 246],
    "flower": [211, 212, 213, 214, 220, 221, 222, 228, 229, 230, 251, 252],
    "glass": [CRATE_GLASS],
}
for _cls, _indices in CRATE_CLASSES.items():
    assert _cls == "glass" or CRATE_GLASS not in _indices
# The class a group's one colour is matched in, for the crate mixtures.
GROUP_CLASS = {"light": "light", "red": "red", "dark": "wood", "stone": "blue", "grey": "grey", "wood": "wood",
               "teal": "teal", "leaf": "leaf", "flower": "flower", "glass": "glass"}
GROUP_CLASS_OF = {"RedClinic": {"dark": "grey"}}


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


# Crate picks made by hand, where the nearest entries would lose the art's contrast:
# the mansard houses' blue-grey stone, slate and pale coping are all nearest the
# crate palette's three pale greys (193-195), so the stone takes its dark blue-grey
# (206) and the slate the palest of them (193), as the art has dark stone under
# mid slate under a light coping.
CRATE_GROUP_PICKS = {"GrayEntryHouse": {"stone": 206, "grey": 193}, "GrayWindowHouse": {"stone": 206, "grey": 193},
                     "CyanEntryHouse": {"stone": 206}}


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
