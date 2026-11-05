"""Colours of the new_1 cottage: its Base palette, the minimal-colour groups of the
TwoColor treatments, and the mapping into the pinned crate palette (as the poke_u
buildings' palettes.py).

Every voxel the sculptor makes carries a material label, never a colour, and
each treatment turns labels into palette indices here, so the same geometry can
be painted every way and the semantic groups survive recolouring.

- Base and Cartoon share one palette (BASE_PALETTE) holding every colour at fixed
  indices: the medians of each material's pixels in new_1.jpg, clustered so the
  JPEG's noise and the outlines drop out; the invented interior (its plank floor,
  the roof's underside) and the buried foundation are noted.
- TwoColor, as the user redefined it on 2026-10-28 (not exactly two colours;
  glass is an exception; as few colours as possible, similar ones merged into
  large flat regions), paints each label with its group's one colour; a group may
  be folded into another (GROUPS' "=name").
- CratePalette copies the pinned crate palette byte for byte and maps each colour
  to its nearest entry among the indices allowed for its material class. Glass is
  crate index 253, which no opaque label may use, and only that index carries the
  Glass material.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = Path(r"C:/Users/tandm/Documents/Projects/VoxelRidgeInspiration")
CRATE = json.loads((WORK / "knowledge" / "palettes" / "crate-palette.json").read_text())
CRATE_RGBA = [tuple(c) for c in CRATE["rgba"]]

# label: (RGB, minimal-colour group, crate class). Order fixes the Base indices.
LABELS = {
    # Invented (the art shows no inside): the buried foundation, plank floors, the
    # roof's underside.
    "found": ((112, 106, 96), "stone", "grey"),
    "found_dark": ((92, 86, 78), "stone", "grey"),
    "floor": ((150, 112, 74), "wood", "wood"),
    "floor_dark": ((124, 90, 58), "wood", "wood"),
    "floor_gap": ((96, 68, 44), "wood", "wood"),
    "ceiling": ((126, 106, 76), "roof", "wood"),
    # The walls and the corner pillars: blue-grey stone in courses, the top of each
    # course lit, a few dark pits in each block, dark joints.
    "stone": ((147, 161, 186), "stone", "blue"),
    "stone_light": ((198, 206, 223), "stone", "blue"),
    "stone_pit": ((109, 123, 149), "stone", "blue"),
    "stone_dark": ((87, 100, 125), "stone", "blue"),
    "stone_joint": ((62, 68, 88), "stone", "blue"),
    # The beam under the roof, all round: dark red-brown, its top lit, its underside dark.
    "beam": ((91, 45, 42), "wood", "red"),
    "beam_light": ((145, 80, 60), "wood", "red"),
    "beam_dark": ((50, 25, 24), "wood", "red"),
    # The roof: tan stone, the parapet's blocks lit on top and dark at their joints,
    # its face over the beam; the recessed middle the same stone, cracked; the
    # chimney the same, its top lit, its flue dark.
    "rim": ((163, 138, 97), "roof", "light"),
    "rim_light": ((206, 174, 128), "roof", "light"),
    "rim_dark": ((97, 82, 57), "roof", "light"),
    "rim_joint": ((62, 52, 36), "roof", "light"),
    "crack": ((94, 80, 58), "roof", "light"),
    "chimney_light": ((215, 183, 124), "roof", "light"),
    "flue": ((20, 14, 10), "dark", "grey"),
    # The moss on the roof's left end: the trees' olive, yellow dots, darker edges.
    "moss": ((161, 163, 40), "leaf", "leaf"),
    "moss_dark": ((100, 109, 54), "leaf", "leaf"),
    "moss_dot": ((212, 204, 72), "leaf", "leaf"),
    # The door: red-brown boards, their joints dark, lit along its top; the arched
    # frame round it, lighter, its outer edge lit, its inner edge dark.
    "door": ((93, 45, 41), "wood", "red"),
    "door_dark": ((57, 31, 31), "wood", "red"),
    "door_light": ((135, 74, 58), "wood", "red"),
    "arch": ((136, 74, 57), "wood", "red"),
    "arch_light": ((175, 109, 86), "wood", "red"),
    "arch_dark": ((82, 46, 44), "wood", "red"),
    # The doorstep: a half round of slate-blue stone, its rim darker.
    "step": ((100, 115, 146), "stone", "blue"),
    "step_dark": ((75, 90, 118), "stone", "blue"),
    # The window bays: the dark of the house's inside, round the glass; the flower
    # boxes in front of them, orange wood, dark at the foot, soil in their tops.
    "recess": ((28, 16, 16), "dark", "grey"),
    "box": ((192, 117, 82), "wood", "red"),
    "box_dark": ((124, 75, 61), "wood", "red"),
    "soil": ((84, 52, 38), "wood", "wood"),
    # Plants: the flower boxes' jagged-leaved plants, the flowering plant on the
    # roof's leaves, its yellow star flowers and their orange hearts.
    "plant": ((98, 184, 102), "leaf", "leaf"),
    "plant_mid": ((59, 142, 74), "leaf", "leaf"),
    "plant_dark": ((44, 100, 58), "leaf", "leaf"),
    "petal": ((248, 220, 96), "leaf", "flower"),
    "petal_dark": ((243, 191, 46), "leaf", "flower"),
    "petal_heart": ((236, 140, 36), "leaf", "flower"),

    # Glass: the art's windows are the black of the unlit inside; the glass is that
    # dark, a little lighter, so what is behind shows dimly; its clarity is
    # GLASS_CLARITY.
    "glass_dark": ((44, 46, 58), "glass", "glass"),
}

GLASS_CLARITY = {"glass_dark": 0.7}

# The family's minimal-colour groups: the blue-grey stone (walls, pillars, the
# doorstep, the foundation), the tan roof (parapet, roof, chimney, the roof's
# underside), the wood (beam, door, frame, flower boxes, floors), the plants (moss,
# leaves, the roof's yellow flowers folded into them), the dark of the window bays,
# and glass.
GROUPS = {
    "Cottage": {"stone": (147, 161, 186), "roof": (163, 138, 97), "wood": (93, 45, 41), "leaf": (98, 184, 102),
                "dark": (28, 16, 16), "glass": (44, 46, 58)},
}
GROUP_CLARITY = 0.7

# Crate palette indices each material class may use. 253 is kept for glass.
CRATE_GLASS = 253
CRATE_CLASSES = {
    "grey": [177, 193, 194, 195, 201, 202, 203, 204, 205, 206, 240, 249, 250],
    # (246, a pale yellow-green, left out: it would turn the tan stone green.)
    "light": [193, 194, 195, 196, 230, 236, 237, 238, 248],
    "wood": [178, 179, 180, 225, 226, 227, 228, 229, 230, 233, 234, 235, 236, 237, 238],
    "red": [178, 179, 180, 219, 220, 221, 222, 234, 235],
    "blue": [193, 194, 205, 206, 249, 250, 251, 252, 254],
    "leaf": [241, 242, 243, 244, 245, 246],
    "flower": [211, 212, 213, 214, 220, 221, 222, 228, 229, 230, 251, 252],
    "glass": [CRATE_GLASS],
}
for _cls, _indices in CRATE_CLASSES.items():
    assert _cls == "glass" or CRATE_GLASS not in _indices
GROUP_CLASS = {"stone": "blue", "roof": "light", "wood": "red", "leaf": "leaf", "dark": "grey", "glass": "glass"}
GROUP_CLASS_OF = {}
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
