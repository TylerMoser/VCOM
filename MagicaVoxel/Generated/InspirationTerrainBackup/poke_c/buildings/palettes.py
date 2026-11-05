"""Colours of the poke_c buildings: one shared Base palette, the minimal-colour
groups of the TwoColor treatments, and the mapping into the pinned crate palette.

Every voxel the sculptor makes carries a material label, never a colour. Each
treatment turns labels into palette indices here, so the same geometry can be
painted every way and the semantic groups survive recolouring.

- Base and Cartoon share one palette (BASE_PALETTE) holding every colour of all
  five buildings at fixed indices, sampled from poke_c.png (the invented interior
  floor and buried foundation are noted). A combat map using several buildings
  adds these colours to its level palette once.
- TwoColor (as the user redefined it on 2026-10-28: not exactly two colours;
  glass is an exception; as few colours as possible, similar ones merged into
  large flat regions) paints each label with its group's one colour.
- CratePalette copies the pinned crate palette byte for byte and maps each colour
  to its nearest entry among the indices allowed for its material class. Glass
  is painted with crate index 253, which no opaque label may use, and only that
  index carries the Glass material.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parent.parent.parent
CRATE = json.loads((WORK / "knowledge" / "palettes" / "crate-palette.json").read_text())
CRATE_RGBA = [tuple(c) for c in CRATE["rgba"]]

# label: (RGB, minimal-colour group, crate class). Order fixes the Base indices.
LABELS = {
    # Slate roofs, hoods and the bay roof.
    "slate_black": ((27, 27, 33), "slate", "grey"),
    "slate_edge": ((40, 40, 48), "slate", "grey"),
    "slate_dark": ((47, 47, 53), "slate", "grey"),
    "slate_gap": ((56, 56, 64), "slate", "grey"),
    "slate_blue": ((56, 64, 72), "slate", "grey"),
    "slate_mid": ((65, 74, 84), "slate", "grey"),
    "slate": ((88, 88, 96), "slate", "grey"),
    "slate_light": ((104, 104, 112), "slate", "grey"),
    # The bridge's dark masonry: the same greys as the slates, stone to the groups.
    "masonry_black": ((27, 27, 27), "slate", "grey"),
    "masonry_dark": ((40, 40, 48), "slate", "grey"),
    "masonry": ((56, 56, 64), "slate", "grey"),
    "masonry_light": ((88, 88, 96), "slate", "grey"),
    # The cottages' tan chimneys.
    "tan_light": ((202, 187, 167), "light", "light"),
    "tan": ((186, 167, 141), "light", "light"),
    "tan_shade": ((167, 143, 109), "light", "light"),
    "tan_dark": ((132, 110, 80), "light", "wood"),
    "flue": ((81, 68, 49), "slate", "grey"),
    # The manor's blue-grey stone chimney.
    "cstone_light": ((153, 174, 196), "slate", "grey"),
    "cstone_hi": ((119, 136, 153), "slate", "grey"),
    "cstone": ((104, 104, 112), "slate", "grey"),
    "cstone_mid": ((89, 102, 114), "slate", "grey"),
    "cstone_dark": ((79, 90, 102), "slate", "grey"),
    "cflue": ((56, 56, 56), "slate", "grey"),
    # Cottage woodwork: the door and its panelling, the dark timbers, the eave beam.
    "door_wood": ((145, 118, 92), "wood", "wood"),
    "door_wood_mid": ((137, 101, 74), "wood", "wood"),
    "door_wood_dark": ((116, 85, 63), "wood", "wood"),
    "timber": ((88, 63, 41), "wood", "wood"),
    "timber_dark": ((80, 60, 48), "wood", "wood"),
    "timber_mid": ((97, 69, 53), "wood", "wood"),
    "timber_black": ((66, 54, 47), "wood", "wood"),
    "beam": ((122, 92, 55), "wood", "wood"),
    "beam_mid": ((131, 101, 64), "wood", "wood"),
    "beam_hi": ((198, 174, 121), "wood", "light"),
    "gable_dark": ((77, 72, 63), "slate", "wood"),
    "gable_mid": ((95, 89, 78), "slate", "wood"),
    # Manor half-timbering and frames.
    "mtimber": ((104, 75, 57), "wood", "wood"),
    "mtimber_light": ((117, 84, 65), "wood", "wood"),
    "mtimber_dark": ((87, 64, 49), "wood", "wood"),
    "mtimber_hi": ((137, 102, 74), "wood", "wood"),
    # Red-brown wood: the manor's doors, the bridge's rails, posts and beams.
    "redwood": ((110, 64, 48), "wood", "wood"),
    "redwood_light": ((128, 78, 65), "wood", "wood"),
    "redwood_dark": ((91, 55, 36), "wood", "wood"),
    "door_black": ((38, 32, 27), "wood", "wood"),
    # The pavilions' plank substructure.
    "plank": ((153, 111, 65), "wood", "wood"),
    "plank_mid": ((138, 91, 56), "wood", "wood"),
    "plank_dark": ((121, 71, 47), "wood", "wood"),
    "plank_line": ((97, 59, 43), "wood", "wood"),
    # Interior floorboards: invented (the art shows no interiors), a warm plank.
    "floor": ((150, 112, 74), "wood", "wood"),
    "floor_dark": ((124, 90, 58), "wood", "wood"),
    "floor_gap": ((96, 68, 44), "wood", "wood"),
    # Plaster, frames and paving.
    "plaster": ((216, 216, 197), "light", "light"),
    "plaster_mid": ((201, 201, 191), "light", "light"),
    "plaster_shade": ((170, 170, 153), "light", "light"),
    "plaster_dark": ((136, 128, 112), "light", "light"),
    "frame": ((176, 176, 178), "light", "light"),
    "frame_light": ((194, 192, 200), "light", "light"),
    "frame_hi": ((216, 208, 224), "light", "light"),
    "paving": ((192, 184, 160), "light", "light"),
    "paving_mid": ((160, 160, 128), "light", "light"),
    "paving_dark": ((136, 128, 104), "light", "light"),
    "paving_hi": ((224, 224, 192), "light", "light"),
    "brass": ((206, 183, 119), "light", "light"),
    "brass_dark": ((45, 45, 45), "slate", "grey"),
    # The pavilions' sage-green gables.
    "sage": ((138, 157, 131), "sage", "sage"),
    "sage_dark": ((121, 140, 116), "sage", "sage"),
    # The buried foundation under each floor: invented, grey stone.
    "found": ((112, 106, 96), "slate", "grey"),
    "found_dark": ((92, 86, 78), "slate", "grey"),
    # Flower boxes.
    "box_edge": ((27, 27, 27), "wood", "wood"),
    "leaf_dark": ((65, 91, 68), "leaf", "leaf"),
    "leaf": ((78, 126, 78), "leaf", "leaf"),
    "leaf_light": ((105, 152, 90), "leaf", "leaf"),
    "flower_yellow": ((255, 214, 8), "flower", "flower"),
    "flower_blue": ((73, 138, 164), "flower", "flower"),
    "flower_blue_light": ((122, 175, 196), "flower", "flower"),
    "flower_orange": ((192, 102, 41), "flower", "flower"),
    "flower_orange_light": ((206, 133, 83), "flower", "flower"),
    # Glass, as tints: the cottages' periwinkle and the manor's sky blue, lightened a
    # little from the art's (122, 122, 248) and (94, 153, 202) so that what is behind
    # still shows through; their clarity is GLASS_CLARITY.
    "glass_cottage": ((150, 152, 236), "glass", "glass"),
    "glass_manor": ((130, 178, 222), "glass", "glass"),
}

# MagicaVoxel Transparency of each glass label, as SimpleWindow1's 0.9 and the
# street lamp's 0.85 are set: how much of what is behind shows through.
GLASS_CLARITY = {"glass_cottage": 0.7, "glass_manor": 0.7}

# The minimal-colour groups' one colour each (the TwoColor treatments). Similar
# colours share a group; a colour like no other keeps its own (the pavilions' sage
# gables), and the cottages' dark gable infill, nearer the slates than the wood,
# goes with the slates so the timbers still show on it.
GROUPS = {
    "slate": (70, 74, 84),
    "wood": (124, 88, 60),
    "light": (214, 210, 192),
    "glass": (160, 186, 232),
    "leaf": (78, 126, 78),
    "flower": (230, 170, 40),
    "sage": (138, 157, 131),
}
GROUP_CLARITY = {"glass": 0.7}

# Crate palette indices each material class may use. 253 is kept for glass.
CRATE_GLASS = 253
CRATE_CLASSES = {
    "grey": [177, 182, 193, 194, 195, 196, 201, 202, 203, 204, 205, 206, 240, 249, 250],
    "wood": [178, 179, 180, 217, 218, 219, 225, 226, 227, 228, 229, 230, 233, 234, 235, 236, 237, 238],
    "light": [193, 194, 195, 196, 229, 230, 236, 237, 238, 246, 248],
    "sage": [193, 194, 244, 245, 246],
    "leaf": [241, 242, 243, 244, 245, 246],
    "flower": [211, 212, 213, 214, 220, 221, 222, 228, 229, 230, 251, 252],
    "glass": [CRATE_GLASS],
}
for _cls, _indices in CRATE_CLASSES.items():
    assert _cls == "glass" or CRATE_GLASS not in _indices


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

# Minimal-colour palette: one index a group, in GROUPS' order.
GROUP_INDEX = {g: i + 1 for i, g in enumerate(GROUPS)}
GROUP_PALETTE = [(*c, 255) for c in GROUPS.values()] + [(*GROUPS["slate"], 255)] * (256 - len(GROUPS))
GROUP_GLASS = {GROUP_INDEX[g]: t for g, t in GROUP_CLARITY.items()}

# Crate mappings: each label's colour, and each group's colour, to its class's
# nearest crate entry (group colours take the class of the group's labels).
CRATE_INDEX = {label: _nearest(rgb, CRATE_CLASSES[cls]) for label, (rgb, group, cls) in LABELS.items()}
_GROUP_CLASS = {"slate": "grey", "wood": "wood", "light": "light", "glass": "glass", "leaf": "leaf", "flower": "flower",
                "sage": "sage"}
CRATE_GROUP_INDEX = {g: _nearest(rgb, CRATE_CLASSES[_GROUP_CLASS[g]]) for g, rgb in GROUPS.items()}
CRATE_GLASS_CLARITY = {CRATE_GLASS: 0.7}
for _label, _i in CRATE_INDEX.items():
    assert (_i == CRATE_GLASS) == (LABELS[_label][1] == "glass"), _label


def paint(treatment, label):
    """The palette index [label] takes under [treatment]."""
    two = "TwoColor" in treatment
    crate = "CratePalette" in treatment
    group = LABELS[label][1]
    if two and crate:
        return CRATE_GROUP_INDEX[group]
    if two:
        return GROUP_INDEX[group]
    if crate:
        return CRATE_INDEX[label]
    return BASE_INDEX[label]


def palette_of(treatment):
    """(palette, glass indices -> Transparency) of [treatment]'s files."""
    if "CratePalette" in treatment:
        return CRATE_RGBA, CRATE_GLASS_CLARITY
    if "TwoColor" in treatment:
        return GROUP_PALETTE, GROUP_GLASS
    return BASE_PALETTE, BASE_GLASS
