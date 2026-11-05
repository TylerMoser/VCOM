"""Colours of the poke_g buildings: one shared Base palette, the minimal-colour
groups of the TwoColor treatments, and the mapping into the pinned crate palette
(as the poke_f buildings' palettes.py).

Every voxel the sculptor makes carries a material label, never a colour, and
each treatment turns labels into palette indices here, so the same geometry can
be painted every way and the semantic groups survive recolouring.

- Base and Cartoon share one palette (BASE_PALETTE) holding every colour of the
  seven buildings at fixed indices, sampled from poke_g.png (the invented
  interiors and the buried foundation noted); the domed centre's are poke_f's,
  its panels recoloured as poke_g.png draws them.
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
    # floor, plank and tiled floors, the ceilings.
    "found": ((112, 106, 96), "dark", "grey"),
    "found_dark": ((92, 86, 78), "dark", "grey"),
    "floor": ((150, 112, 74), "wood", "wood"),
    "floor_dark": ((124, 90, 58), "wood", "wood"),
    "floor_gap": ((96, 68, 44), "wood", "wood"),
    "tiles": ((206, 202, 192), "light", "light"),
    "tiles_line": ((168, 164, 156), "light", "light"),
    "ceiling": ((214, 210, 200), "light", "light"),

    # --- The green houses (the stepped house, its mirror image, the wide house). ---
    "gh_roof_light": ((147, 202, 117), "green", "leaf"),
    "gh_roof": ((133, 188, 103), "green", "leaf"),
    "gh_roof_mid": ((112, 167, 82), "green", "leaf"),
    "gh_roof_seam": ((91, 146, 61), "green", "leaf"),
    "gh_roof_edge": ((69, 124, 39), "green", "leaf"),
    "gh_roof_outline": ((0, 94, 0), "green", "leaf"),
    "gh_plinth": ((69, 124, 39), "green", "leaf"),
    "gh_panel_light": ((140, 115, 82), "wood", "wood"),
    "gh_panel": ((125, 91, 66), "wood", "wood"),
    "gh_panel_low": ((109, 79, 53), "wood", "wood"),
    "gh_panel_low_dark": ((92, 68, 46), "wood", "wood"),
    "gh_beam": ((137, 101, 74), "wood", "wood"),
    "gh_beam_dark": ((97, 69, 53), "wood", "wood"),
    "gh_timber": ((73, 59, 51), "wood", "wood"),
    "gh_sash": ((126, 102, 71), "wood", "wood"),
    "gh_sash_dark": ((101, 81, 56), "wood", "wood"),
    "gh_frame_light": ((231, 214, 173), "light", "light"),
    "gh_frame": ((201, 188, 135), "light", "light"),
    "gh_frame_shade": ((164, 153, 108), "light", "light"),
    "gh_door_light": ((128, 78, 65), "door", "red"),
    "gh_door": ((110, 64, 48), "door", "red"),
    "gh_door_dark": ((91, 55, 36), "door", "red"),
    "gh_door_edge": ((73, 43, 29), "door", "red"),
    "gh_brass": ((184, 153, 67), "light", "flower"),

    # --- The domed centre: poke_f's drawing, its blue panels red-brown tiles here. ---
    "dc_white": ((206, 221, 227), "light", "light"),
    "dc_white_shade": ((176, 191, 198), "light", "light"),
    "dc_frame": ((193, 207, 214), "light", "light"),
    "dc_panel_light": ((176, 84, 65), "brown", "red"),
    "dc_panel": ((158, 75, 58), "brown", "red"),
    "dc_panel_mid": ((142, 67, 52), "brown", "red"),
    "dc_panel_dark": ((118, 56, 43), "brown", "red"),
    "dc_band": ((106, 47, 35), "brown", "red"),
    "dc_band_dark": ((83, 37, 28), "brown", "red"),
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

    # --- The red centre. ---
    "rc_wall": ((177, 197, 207), "light", "light"),
    "rc_wall_shade": ((141, 165, 184), "light", "light"),
    "rc_white": ((231, 236, 236), "light", "light"),
    "rc_line": ((77, 88, 101), "grey", "grey"),
    "rc_foot": ((126, 126, 126), "grey", "grey"),
    "rc_foot_dark": ((66, 75, 86), "grey", "grey"),
    "rc_pillar": ((126, 126, 126), "grey", "grey"),
    "rc_pillar_mid": ((105, 105, 107), "grey", "grey"),
    "rc_pillar_dark": ((72, 72, 72), "grey", "grey"),
    "rc_pillar_edge": ((55, 55, 55), "grey", "grey"),
    "rc_frame": ((66, 75, 86), "grey", "grey"),
    "rc_knob": ((74, 74, 74), "grey", "grey"),
    "rc_red_hi": ((223, 125, 125), "red", "red"),
    "rc_red_light": ((218, 103, 103), "red", "red"),
    "rc_red": ((213, 82, 82), "red", "red"),
    "rc_red_mid": ((207, 57, 57), "red", "red"),
    "rc_red_shade": ((182, 45, 45), "red", "red"),
    "rc_red_dark": ((164, 40, 40), "red", "red"),
    "rc_red_deep": ((140, 34, 34), "red", "red"),
    "rc_red_edge": ((89, 22, 22), "red", "red"),
    "rc_ball_rim": ((123, 132, 165), "grey", "grey"),
    "rc_ball_rim_dark": ((89, 102, 117), "grey", "grey"),
    "rc_ball_dark": ((107, 115, 140), "grey", "grey"),
    "rc_ball_light": ((224, 240, 248), "light", "light"),
    "rc_ball_blue": ((184, 216, 240), "light", "light"),
    "rc_ball_white": ((249, 249, 249), "light", "light"),

    # --- The Mart. ---
    "mt_wall": ((177, 197, 207), "light", "light"),
    "mt_wall_shade": ((141, 165, 184), "light", "light"),
    "mt_white": ((231, 236, 236), "light", "light"),
    "mt_line": ((77, 88, 101), "grey", "grey"),
    "mt_col_light": ((131, 131, 133), "grey", "grey"),
    "mt_col": ((105, 105, 107), "grey", "grey"),
    "mt_col_dark": ((72, 72, 72), "grey", "grey"),
    "mt_col_edge": ((55, 55, 55), "grey", "grey"),
    "mt_frame": ((176, 176, 178), "light", "light"),
    "mt_bar": ((224, 240, 242), "light", "light"),
    "mt_frame_dark": ((66, 75, 86), "grey", "grey"),
    "mt_knob": ((74, 74, 74), "grey", "grey"),
    "mt_roof_dot": ((122, 167, 199), "blue", "blue"),
    "mt_roof": ((82, 140, 182), "blue", "blue"),
    "mt_roof_mid": ((71, 127, 168), "blue", "blue"),
    "mt_roof_shade": ((64, 114, 151), "blue", "blue"),
    "mt_roof_dark": ((52, 93, 123), "blue", "blue"),
    "mt_roof_deep": ((46, 83, 109), "blue", "blue"),
    "mt_roof_edge": ((33, 59, 78), "blue", "blue"),
    "mt_stripe": ((221, 221, 221), "light", "light"),
    "mt_sign_top": ((249, 249, 249), "light", "light"),
    "mt_sign": ((199, 199, 199), "light", "light"),
    "mt_sign_low": ((168, 168, 168), "light", "light"),
    "mt_sign_edge": ((131, 131, 131), "grey", "grey"),
    "mt_sign_dark": ((91, 91, 91), "grey", "grey"),
    "mt_letter": ((105, 105, 231), "letter", "blue"),

    # --- The wooden lodge. ---
    "wl_deck": ((187, 148, 115), "wood", "wood"),
    "wl_deck_mid": ((168, 133, 103), "wood", "wood"),
    "wl_deck_line": ((150, 118, 92), "wood", "wood"),
    "wl_rim": ((198, 174, 121), "wood", "light"),
    "wl_fascia": ((145, 118, 92), "wood", "wood"),
    "wl_fascia_dark": ((109, 88, 69), "dark", "wood"),
    "wl_fascia_line": ((88, 63, 41), "dark", "wood"),
    "wl_beam": ((131, 101, 64), "dark", "wood"),
    "wl_panel": ((184, 136, 112), "wood", "wood"),
    "wl_panel_dark": ((140, 99, 81), "wood", "wood"),
    "wl_post": ((164, 127, 97), "wood", "wood"),
    "wl_post_mid": ((136, 108, 80), "wood", "wood"),
    "wl_post_dark": ((125, 92, 52), "wood", "wood"),
    "wl_timber": ((83, 57, 33), "dark", "wood"),
    "wl_frame": ((176, 176, 178), "light", "light"),
    "wl_bar": ((224, 224, 242), "light", "light"),
    "wl_door": ((109, 88, 69), "dark", "wood"),
    "wl_door_line": ((88, 63, 41), "dark", "wood"),
    "wl_path": ((146, 137, 111), "path", "grey"),
    "wl_path_mid": ((141, 130, 96), "path", "grey"),
    "wl_path_dark": ((126, 111, 76), "path", "grey"),

    # Glass, as tints a little lighter than the art's, so that what is behind still
    # shows through; their clarity is GLASS_CLARITY.
    "glass_house": ((130, 200, 228), "glass", "glass"),
    "glass_center": ((152, 168, 246), "glass", "glass"),
    "glass_red": ((150, 175, 250), "glass", "glass"),
    "glass_mart": ((150, 150, 250), "glass", "glass"),
    "glass_lodge": ((150, 150, 248), "glass", "glass"),
}

GLASS_CLARITY = {"glass_house": 0.7, "glass_center": 0.7, "glass_red": 0.7, "glass_mart": 0.7, "glass_lodge": 0.7}

# Each family's minimal-colour groups: its own colour for each, or "=other" to
# fold the group into another (that group's colour and index).
_GREEN = {"green": (133, 188, 103), "wood": (125, 91, 66), "light": (201, 188, 135), "door": "=wood", "dark": "=wood",
          "glass": (130, 200, 228)}
GROUPS = {
    "GreenHouse": dict(_GREEN),
    "GreenHouseMirrored": dict(_GREEN),
    "GreenWideHouse": dict(_GREEN),
    "DomeCenter": {"light": (206, 221, 227), "brown": (158, 75, 58), "red": (191, 42, 41), "dark": (74, 83, 98),
                   "wood": (119, 88, 63), "glass": (152, 168, 246)},
    "RedCenter": {"light": (177, 197, 207), "red": (213, 82, 82), "grey": (105, 105, 107), "dark": "=grey",
                  "wood": "=grey", "glass": (150, 175, 250)},
    "Mart": {"light": (177, 197, 207), "blue": (82, 140, 182), "grey": (105, 105, 107), "letter": "=blue",
             "dark": "=grey", "wood": "=grey", "glass": (150, 150, 250)},
    "WoodLodge": {"wood": (187, 148, 115), "dark": (109, 88, 69), "light": (176, 176, 178), "path": "=dark",
                  "glass": (150, 150, 248)},
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
               "green": "leaf", "brown": "red", "door": "red", "letter": "blue", "path": "grey", "glass": "glass"}
GROUP_CLASS_OF = {"WoodLodge": {"dark": "wood"}}
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
