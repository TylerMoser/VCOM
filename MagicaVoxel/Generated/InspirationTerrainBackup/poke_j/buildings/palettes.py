"""Colours of the poke_j buildings: one shared Base palette, the minimal-colour
groups of the TwoColor treatments, and the mapping into the pinned crate palette
(as the poke_i buildings' palettes.py).

Every voxel the sculptor makes carries a material label, never a colour, and
each treatment turns labels into palette indices here, so the same geometry can
be painted every way and the semantic groups survive recolouring.

- Base and Cartoon share one palette (BASE_PALETTE) holding every colour of the
  two buildings at fixed indices, sampled from poke_j.jpg (the invented
  interiors and the buried foundation noted). The source is a scaled-down JPEG,
  so its colours were taken as the medians of whole regions (the red house's
  from the three copies averaged), the small features' from their brightest
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
    # floor, the red house's plank floor, the grey house's floor tiles, the ceilings
    # under the roofs.
    "found": ((112, 106, 96), "dark", "grey"),
    "found_dark": ((92, 86, 78), "dark", "grey"),
    "floor": ((150, 112, 74), "wood", "wood"),
    "floor_dark": ((124, 90, 58), "wood", "wood"),
    "floor_gap": ((96, 68, 44), "wood", "wood"),
    "tiles": ((206, 204, 196), "light", "light"),
    "tiles_line": ((174, 172, 164), "light", "light"),
    "ceiling": ((214, 210, 200), "light", "light"),

    # --- The red house (the three copies averaged). ---
    "rh_roof_light": ((186, 76, 38), "roof", "red"),
    "rh_roof": ((173, 64, 29), "roof", "red"),
    "rh_roof_shade": ((158, 55, 21), "roof", "red"),
    "rh_roof_line": ((140, 47, 18), "roof", "red"),
    "rh_roof_edge": ((98, 40, 21), "roof", "red"),
    "rh_stone": ((190, 168, 132), "light", "light"),
    "rh_stone_light": ((200, 180, 146), "light", "light"),
    "rh_stone_line": ((168, 146, 110), "light", "light"),
    "rh_bar": ((206, 200, 186), "light", "light"),
    "rh_post": ((126, 98, 74), "wood", "wood"),
    "rh_beam": ((121, 93, 72), "wood", "wood"),
    "rh_timber": ((104, 80, 62), "wood", "wood"),
    "rh_frame": ((112, 72, 54), "wood", "wood"),
    "rh_door": ((168, 63, 30), "door", "red"),
    "rh_door_line": ((142, 51, 24), "door", "red"),
    "rh_door_dark": ((112, 42, 22), "door", "red"),
    "rh_chim": ((186, 162, 124), "stone", "light"),
    "rh_chim_line": ((158, 134, 100), "stone", "light"),
    "rh_chim_shade": ((150, 128, 96), "stone", "light"),
    "rh_chim_top": ((146, 120, 90), "wood", "wood"),
    "rh_chim_cap": ((194, 179, 148), "stone", "light"),
    "rh_flue": ((55, 44, 23), "dark", "grey"),

    # --- The grey house. ---
    "gh_roof": ((170, 179, 184), "roof", "grey"),
    "gh_roof_light": ((182, 191, 196), "roof", "grey"),
    "gh_seam": ((144, 153, 158), "roof", "grey"),
    "gh_roof_edge": ((82, 91, 96), "roof", "grey"),
    "gh_fascia_light": ((118, 127, 128), "roof", "grey"),
    "gh_fascia": ((100, 104, 108), "roof", "grey"),
    "gh_fascia_dark": ((62, 66, 74), "roof", "grey"),
    "gh_vent_body": ((176, 179, 181), "roof", "grey"),
    "gh_stone": ((192, 192, 172), "light", "light"),
    "gh_stone_light": ((210, 211, 192), "light", "light"),
    "gh_stone_line": ((164, 166, 146), "light", "light"),
    "gh_plinth": ((152, 154, 136), "light", "light"),
    "gh_post": ((240, 241, 239), "light", "light"),
    "gh_frame": ((232, 236, 232), "light", "light"),
    "gh_apron": ((212, 218, 204), "light", "light"),
    "gh_vent": ((240, 242, 243), "light", "light"),
    "gh_vent_shade": ((206, 209, 212), "light", "light"),
    "gh_sky_frame": ((236, 246, 248), "light", "light"),
    "gh_well": ((200, 204, 206), "light", "light"),
    "gh_door": ((132, 99, 72), "wood", "wood"),
    "gh_door_light": ((158, 122, 92), "wood", "wood"),
    "gh_door_dark": ((94, 76, 52), "wood", "wood"),
    "gh_box": ((116, 84, 66), "wood", "wood"),
    "gh_box_dark": ((90, 66, 50), "wood", "wood"),
    "gh_flower": ((228, 146, 150), "flower", "flower"),
    "gh_flower_dark": ((196, 108, 116), "flower", "flower"),
    "gh_leaf": ((92, 138, 78), "flower", "leaf"),
    "gh_vent_slot": ((42, 42, 46), "dark", "grey"),

    # Glass, as tints a little lighter than the art's, so that what is behind still
    # shows through; their clarity is GLASS_CLARITY.
    "glass_rh": ((150, 192, 232), "glass", "glass"),
    "glass_fan": ((150, 198, 238), "glass", "glass"),
    "glass_gh": ((156, 192, 224), "glass", "glass"),
    "glass_gh_door": ((150, 172, 186), "glass", "glass"),
    "glass_sky": ((130, 182, 230), "glass", "glass"),
    "glass_sky_light": ((214, 234, 248), "glass", "glass"),
}

# MagicaVoxel Transparency of each glass label: the windows' 0.7, the skylight a
# little denser, its streaks and the grey house's door pane denser still.
GLASS_CLARITY = {"glass_rh": 0.7, "glass_fan": 0.7, "glass_gh": 0.7, "glass_gh_door": 0.5, "glass_sky": 0.6,
                 "glass_sky_light": 0.5}

# Each family's minimal-colour groups: its own colour for each, or "=other" to
# fold the group into another (that group's colour and index).
GROUPS = {
    "RedHouse": {"roof": (173, 64, 29), "light": (190, 168, 132), "wood": (124, 96, 72), "door": "=roof",
                 "stone": "=light", "dark": "=wood", "glass": (150, 192, 232)},
    "GreyHouse": {"roof": (140, 148, 154), "light": (206, 207, 192), "wood": (126, 94, 70), "flower": (228, 146, 150),
                  "dark": "=roof", "glass": (150, 190, 228)},
}
# The grey house's roof group is a mid grey, between its light seamed tops and
# their dark edges: its tops' own grey drew it near white beside its light walls.
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
GROUP_CLASS = {"light": "light", "roof": "red", "wood": "wood", "door": "red", "stone": "light", "dark": "grey",
               "flower": "flower", "glass": "glass"}
GROUP_CLASS_OF = {"GreyHouse": {"roof": "grey"}}
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
