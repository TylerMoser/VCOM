"""Colours of the poke_n buildings: one shared Base palette, the minimal-colour
groups of the TwoColor treatments, and the mapping into the pinned crate palette
(as the poke_m buildings' palettes.py).

Every voxel the sculptor makes carries a material label, never a colour, and
each treatment turns labels into palette indices here, so the same geometry can
be painted every way and the semantic groups survive recolouring.

- Base and Cartoon share one palette (BASE_PALETTE) holding every colour of the
  three buildings at fixed indices. poke_n.png is native pixel art, so the colours
  are the art's own, read pixel by pixel (the invented interiors and the buried
  foundation noted; glass a little lighter so that what is behind still shows).
  Each roof is one material in one set of colours on both its slopes, as the game
  lights them itself; the art draws its left slopes darker.
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

    # --- The red house (the art's colours). ---
    "rh_roof": ((215, 80, 34), "roof", "red"),
    "rh_roof_light": ((225, 97, 53), "roof", "red"),
    "rh_roof_dark": ((162, 60, 26), "roof", "red"),
    "rh_roof_line": ((183, 68, 29), "roof", "red"),
    "rh_ridge": ((225, 97, 53), "roof", "red"),
    "rh_verge": ((139, 139, 139), "stone", "grey"),
    "rh_verge_dark": ((37, 37, 37), "dark", "grey"),
    "rh_wall": ((202, 163, 129), "light", "light"),
    "rh_wall_light": ((230, 202, 140), "light", "light"),
    "rh_wall_line": ((192, 147, 105), "light", "light"),
    "rh_gable": ((230, 202, 140), "light", "light"),
    "rh_gable_line": ((202, 163, 129), "light", "light"),
    "rh_stone": ((141, 121, 49), "stone", "wood"),
    "rh_stone_light": ((130, 106, 46), "stone", "wood"),
    "rh_stone_dark": ((104, 81, 41), "stone", "wood"),
    "rh_beam": ((104, 81, 41), "wood", "wood"),
    "rh_beam_dark": ((38, 34, 29), "wood", "wood"),
    "rh_timber": ((104, 81, 41), "wood", "wood"),
    "rh_timber_dark": ((100, 70, 40), "wood", "wood"),
    "rh_frame": ((238, 238, 247), "light", "light"),
    "rh_door": ((60, 86, 125), "door", "blue"),
    "rh_door_mid": ((38, 67, 104), "door", "blue"),
    "rh_door_line": ((32, 55, 96), "door", "blue"),
    "rh_door_dark": ((20, 39, 88), "door", "blue"),
    "rh_knob": ((152, 144, 136), "light", "grey"),
    "rh_box": ((112, 83, 48), "wood", "wood"),
    "rh_box_dark": ((56, 49, 42), "wood", "wood"),
    "rh_leaf": ((99, 163, 80), "flower", "leaf"),
    "rh_flower": ((206, 123, 181), "flower", "flower"),
    "rh_flower_orange": ((247, 115, 66), "flower", "flower"),
    "rh_dormer": ((184, 192, 168), "light", "light"),
    "rh_dormer_line": ((160, 168, 155), "light", "light"),
    "rh_chim": ((128, 72, 40), "stone", "wood"),
    "rh_chim_dark": ((104, 56, 16), "stone", "wood"),
    "rh_chim_cap": ((198, 179, 133), "light", "light"),
    "rh_chim_ring": ((168, 144, 104), "light", "light"),
    "rh_chim_top": ((144, 120, 88), "light", "wood"),
    "rh_chim_face": ((119, 111, 77), "light", "wood"),
    "rh_chim_face_dark": ((107, 99, 58), "light", "wood"),
    "rh_flue": ((24, 24, 56), "dark", "grey"),

    # --- The chalet (the art's colours). ---
    "ch_roof": ((187, 114, 64), "roof", "wood"),
    "ch_roof_light": ((194, 124, 78), "roof", "wood"),
    "ch_roof_line": ((185, 102, 46), "roof", "wood"),
    "ch_roof_dark": ((171, 85, 27), "roof", "wood"),
    "ch_verge": ((193, 193, 193), "light", "light"),
    "ch_verge_dark": ((99, 98, 98), "light", "grey"),
    "ch_wall": ((206, 179, 108), "light", "light"),
    "ch_wall_light": ((176, 148, 75), "light", "light"),
    "ch_wall_line": ((167, 148, 96), "light", "light"),
    "ch_gable": ((206, 179, 108), "light", "light"),
    "ch_gable_spot": ((176, 148, 75), "light", "light"),
    "ch_beam": ((126, 98, 70), "wood", "wood"),
    "ch_beam_dark": ((64, 55, 49), "wood", "wood"),
    "ch_brace": ((131, 101, 64), "wood", "wood"),
    "ch_post": ((164, 118, 80), "wood", "wood"),
    "ch_post_light": ((176, 128, 88), "wood", "wood"),
    "ch_post_dark": ((64, 55, 49), "wood", "wood"),
    "ch_frame": ((224, 224, 242), "light", "light"),
    "ch_door": ((171, 85, 27), "door", "red"),
    "ch_door_line": ((145, 72, 23), "door", "red"),
    "ch_door_dark": ((116, 58, 18), "door", "red"),
    "ch_lamp": ((116, 88, 48), "wood", "wood"),
    "ch_lamp_glass": ((214, 200, 150), "light", "light"),
    "ch_chim": ((177, 197, 207), "stone", "light"),
    "ch_chim_light": ((206, 221, 227), "stone", "light"),
    "ch_chim_dark": ((141, 165, 184), "stone", "grey"),
    "ch_vent": ((66, 70, 66), "dark", "grey"),

    # --- The roofed gate (the art's colours). ---
    "gt_plank": ((129, 83, 61), "roof", "wood"),
    "gt_plank_light": ((145, 93, 61), "roof", "wood"),
    "gt_plank_dark": ((93, 59, 42), "roof", "wood"),
    "gt_gap": ((49, 30, 22), "roof", "wood"),
    "gt_cap": ((49, 30, 22), "roof", "wood"),
    "gt_cap_light": ((81, 50, 38), "roof", "wood"),
    "gt_post": ((81, 55, 51), "wood", "wood"),
    "gt_post_light": ((105, 63, 46), "wood", "wood"),
    "gt_post_dark": ((57, 42, 42), "wood", "wood"),
    "gt_beam": ((105, 63, 46), "wood", "wood"),
    "gt_beam_dark": ((65, 40, 30), "wood", "wood"),

    # Glass: the art's blues a little lighter, so that what is behind still shows
    # through; their clarity is GLASS_CLARITY.
    "glass_rh": ((120, 170, 215), "glass", "glass"),
    "glass_ch": ((120, 175, 225), "glass", "glass"),
}

# MagicaVoxel Transparency of each glass label.
GLASS_CLARITY = {"glass_rh": 0.7, "glass_ch": 0.7}

# Each family's minimal-colour groups: its own colour for each, or "=other" to
# fold the group into another (that group's colour and index).
GROUPS = {
    "RedHouse": {"roof": (215, 80, 34), "light": (230, 202, 140), "wood": (104, 81, 41), "door": (60, 86, 125),
                 "stone": "=wood", "flower": "=roof", "dark": "=wood", "glass": (120, 170, 215)},
    "Chalet": {"roof": (187, 114, 64), "light": (206, 179, 108), "wood": (126, 98, 70), "door": "=roof",
               "stone": "=light", "dark": "=wood", "glass": (120, 175, 225)},
    "RoofedGate": {"roof": (105, 63, 46), "wood": (65, 45, 40), "light": "=wood", "dark": "=wood"},
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
GROUP_CLASS = {"light": "light", "roof": "wood", "wood": "wood", "door": "blue", "stone": "light",
               "flower": "flower", "dark": "grey", "glass": "glass"}
GROUP_CLASS_OF = {"RedHouse": {"roof": "red"}}
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
    if "glass" not in GROUPS[family]:
        return {}                                      # the gate has none
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
