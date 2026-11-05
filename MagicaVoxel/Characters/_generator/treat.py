"""The VoxelRidgeInspiration treatments (knowledge/VARIATIONS.md there), for characters.

Cartoon: bilaterally symmetric (the figure's left half mirrored onto its right, paint and
bones with it), each group's near shades merged into its commonest, colours a little
brighter: broader regions, fewer incidental patches.
TwoColor (as amended by the user on 2026-10-28): as few flat colours as possible, one for
each family of similar materials, glass and lights kept apart as exceptions. The families
are the hide (skin, fur, scales, feathers, bark, leaves, petals), the hard parts grown on it
(hair, horn, bone, shell, chitin), the face's marks (eyes, mouth, markings), soft goods
(cloth, leather) and hard goods (metal, gems).
CratePalette: the exact geometry, every colour the nearest of the game's crate palette
(MagicaVoxel/Blocks/BrightCrate1.vox, copied whole), glass and glowing colours each on a
place no opaque colour uses, so they keep their materials.
"""
import colorsys
import hashlib
import math
import os

import vox
from core import Model, shade, sat

FAMILIES = {
    'hide': ('skin', 'fur', 'scale', 'feather', 'bark', 'plant', 'petal'),
    'hard': ('hair', 'horn', 'bone', 'shell', 'chitin'),
    'marks': ('eye', 'mouth', 'detail'),
    'soft': ('cloth', 'leather'),
    'goods': ('metal', 'gem'),
}
CRATE = os.path.join(vox.HERE, '..', '..', 'Blocks', 'BrightCrate1.vox')
CRATE_PALETTE_SHA = 'b1a4e811c89d143b006c0a421443dd2e1b3b9da0b6588b176c4d072b67c279c2'


def family_of(group):
    for fam, groups in FAMILIES.items():
        if group in groups:
            return fam
    return group


def _dist(a, b):
    # a cheap perceptual weighting of RGB
    dr, dg, db = a[0] - b[0], a[1] - b[1], a[2] - b[2]
    rm = (a[0] + b[0]) / 2
    return math.sqrt((2 + rm / 256) * dr * dr + 4 * dg * dg + (2 + (255 - rm) / 256) * db * db)


def _special(v):
    return v.mat is not None


def cartoon(m, merge=70.0, boost=1.12):
    c = m.copy()
    c.mirror_from_left()
    by_group = {}
    for p, v in c.v.items():
        if _special(v):
            continue
        by_group.setdefault(v.group, {}).setdefault(v.color, 0)
        by_group[v.group][v.color] += 1
    remap = {}
    for group, counts in by_group.items():
        order = sorted(counts, key=lambda k: -counts[k])
        kept = []
        for col in order:
            near = [k for k in kept if _dist(k, col) < merge]
            if near:
                remap[(group, col)] = near[0]
            else:
                kept.append(col)
                remap[(group, col)] = col
    for p, v in c.v.items():
        if _special(v):
            continue
        col = remap[(v.group, v.color)]
        v.color = sat(col, boost)
    c.notes.append('Cartoon: mirrored from the figure\'s left; near shades merged within each group (distance < %d); saturation x%.2f' % (merge, boost))
    return c


def two_color(m):
    c = m.copy()
    counts = {}
    for p, v in c.v.items():
        if _special(v):
            continue
        fam = family_of(v.group)
        counts.setdefault(fam, {}).setdefault(v.color, 0)
        counts[fam][v.color] += 1
    pick = {fam: max(cs, key=lambda k: cs[k]) for fam, cs in counts.items()}
    # two families may have picked one colour: nudge the later apart so each stays a group
    used = {}
    for fam in sorted(pick, key=lambda f: -sum(counts[f].values())):
        col = pick[fam]
        while col in used.values():
            col = shade(col, 0.85) if sum(col) > 120 else shade(col, 1.25)
        used[fam] = col
    for p, v in c.v.items():
        if _special(v):
            continue
        v.color = used[family_of(v.group)]
    c.notes.append('TwoColor: one flat colour a family: ' + ', '.join('%s #%02x%02x%02x' % (f, *col) for f, col in sorted(used.items())))
    return c


_crate = None


def crate_palette():
    global _crate
    if _crate is None:
        size, voxels, palette, mats = vox.read(CRATE)
        flat = bytes(v for e in palette for v in e)
        sha = hashlib.sha256(flat).hexdigest()
        if sha != CRATE_PALETTE_SHA:
            raise ValueError('BrightCrate1.vox palette changed: %s' % sha)
        _crate = palette
    return _crate


def crate(m):
    """Returns (model recoloured to crate colours, the crate's 256 RGBA, places): the
    places map each voxel to a palette place, glass and glowing colours on places of their
    own so their materials do not reach opaque voxels."""
    pal = crate_palette()
    entries = [(i + 1, tuple(e[:3])) for i, e in enumerate(pal[:254])]
    distinct = {}
    for place, col in entries:
        distinct.setdefault(col, []).append(place)
    c = m.copy()
    place_of = {}
    opaque_places = set()
    special = []
    for p, v in c.v.items():
        if _special(v):
            special.append(p)
            continue
        col = min(distinct, key=lambda k: _dist(k, v.color))
        v.color = col
        place_of[p] = distinct[col][0]
        opaque_places.add(distinct[col][0])
    mat_place = {}
    for p in special:
        v = c.v[p]
        key = (v.color, v.mat)
        if key not in mat_place:
            ranked = sorted(distinct, key=lambda k: _dist(k, v.color))
            chosen = None
            for col in ranked:
                for place in distinct[col]:
                    if place not in opaque_places and place not in mat_place.values():
                        chosen = place
                        break
                if chosen:
                    break
            mat_place[key] = chosen
        place = mat_place[key]
        v.color = tuple(pal[place - 1][:3])
        place_of[p] = place
    mats = {}
    for (col, mat), place in mat_place.items():
        if mat[0] == 'glass':
            mats[place] = vox.glass_material(mat[1])
        elif mat[0] == 'emit':
            mats[place] = vox.emit_material(mat[1], mat[2] if len(mat) > 2 else 1)
    c.notes.append('CratePalette: nearest colours of BrightCrate1.vox (palette sha256 %s), its RGBA copied whole' % CRATE_PALETTE_SHA[:16])
    return c, pal, place_of, mats


def write_crate(m, path):
    from core import canvas
    c, pal, place_of, mats = crate(m)
    data = vox.write(path, canvas(c), place_of, pal, mats)
    return c, data


TREATMENTS = {'Cartoon': cartoon, 'TwoColor': two_color}
