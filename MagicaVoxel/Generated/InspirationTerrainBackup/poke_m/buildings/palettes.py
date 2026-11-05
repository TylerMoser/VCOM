"""Colours of the poke_m buildings: one shared Base palette, the minimal-colour
groups of the TwoColor treatments, and the mapping into the pinned crate palette
(as the poke_j buildings' palettes.py).

Every voxel the sculptor makes carries a material label, never a colour, and
each treatment turns labels into palette indices here, so the same geometry can
be painted every way and the semantic groups survive recolouring.

- Base and Cartoon share one palette (BASE_PALETTE) holding every colour of the
  two buildings at fixed indices. poke_m.png is native pixel art, so the colours
  are the art's own, read pixel by pixel (the invented interiors and the buried
  foundation noted; glass a little lighter so that what is behind still shows).
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

    # --- The log cabin (the art's colours). ---
    "lc_slate_light": ((118, 114, 114), "roof", "grey"),
    "lc_slate": ((100, 96, 96), "roof", "grey"),
    "lc_slate_mid": ((85, 80, 80), "roof", "grey"),
    "lc_slate_dark": ((70, 66, 66), "roof", "grey"),
    "lc_outline": ((42, 41, 38), "dark", "grey"),
    "lc_log_light": ((188, 137, 85), "wood", "wood"),
    "lc_log": ((148, 106, 64), "wood", "wood"),
    "lc_log_shade": ((112, 82, 51), "wood", "wood"),
    "lc_log_dark": ((87, 61, 37), "wood", "wood"),
    "lc_end": ((211, 174, 135), "wood", "wood"),
    "lc_door_light": ((211, 174, 135), "wood", "wood"),
    "lc_gable": ((87, 61, 37), "wood", "wood"),
    "lc_frame": ((188, 137, 85), "wood", "wood"),
    "lc_handle": ((246, 240, 226), "light", "light"),

    # --- The lodge (the art's colours). ---
    "lg_roof_light": ((210, 150, 102), "roof", "wood"),
    "lg_roof": ((170, 108, 58), "roof", "wood"),
    "lg_roof_dark": ((120, 82, 52), "roof", "wood"),
    "lg_roof_line": ((80, 55, 34), "roof", "wood"),
    "lg_band": ((201, 185, 142), "light", "light"),
    "lg_band_line": ((150, 135, 95), "light", "light"),
    "lg_brick": ((251, 249, 187), "light", "light"),
    "lg_mortar": ((201, 185, 142), "light", "light"),
    "lg_plinth": ((105, 103, 93), "dark", "grey"),
    "lg_plinth_dark": ((96, 94, 83), "dark", "grey"),
    "lg_soffit": ((107, 96, 74), "wood", "wood"),
    "lg_soffit_dark": ((56, 50, 40), "wood", "wood"),
    "lg_post_light": ((198, 169, 108), "wood", "wood"),
    "lg_post": ((170, 131, 85), "wood", "wood"),
    "lg_post_shade": ((143, 93, 63), "wood", "wood"),
    "lg_post_line": ((90, 61, 44), "wood", "wood"),
    "lg_frame": ((107, 96, 74), "wood", "wood"),
    "lg_sill": ((56, 50, 40), "wood", "wood"),
    "lg_door": ((138, 125, 97), "wood", "wood"),
    "lg_door_line": ((107, 96, 74), "wood", "wood"),
    "lg_door_frame": ((56, 50, 40), "wood", "wood"),
    "lg_door_light": ((176, 162, 131), "wood", "wood"),
    "lg_transom": ((150, 135, 95), "wood", "wood"),
    "lg_handle": ((246, 240, 226), "light", "light"),

    # Glass: the art's pale blue a little lighter, so that what is behind still shows
    # through, and its white streaks; their clarity is GLASS_CLARITY.
    "glass_lc": ((160, 210, 216), "glass", "glass"),
    "glass_lc_light": ((236, 240, 236), "glass", "glass"),
    "glass_lg": ((160, 210, 216), "glass", "glass"),
    "glass_lg_light": ((236, 240, 236), "glass", "glass"),
}

# MagicaVoxel Transparency of each glass label: the panes 0.7, their streaks denser.
GLASS_CLARITY = {"glass_lc": 0.7, "glass_lc_light": 0.5, "glass_lg": 0.7, "glass_lg_light": 0.5}

# Each family's minimal-colour groups: its own colour for each, or "=other" to
# fold the group into another (that group's colour and index).
GROUPS = {
    "LogCabin": {"roof": (100, 96, 96), "wood": (148, 106, 64), "light": "=wood", "dark": "=roof",
                 "glass": (160, 210, 216)},
    "Lodge": {"roof": (170, 108, 58), "wood": (170, 131, 85), "light": (251, 249, 187), "dark": "=wood",
              "glass": (160, 210, 216)},
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
GROUP_CLASS = {"light": "light", "roof": "wood", "wood": "wood", "dark": "grey", "glass": "glass"}
GROUP_CLASS_OF = {"LogCabin": {"roof": "grey"}}
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
