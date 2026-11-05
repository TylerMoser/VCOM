"""Another image's model, the same art in other colours: its Base and Cartoon
geometry exactly, each voxel's material read off its TwoColor file (one colour a
material), each shade carried over by its rank in lightness within its material to
the new sprite's own shades of that material (as many as the old model has)."""
import numpy as np

from sprites import hue_sat, interior, quantize
from voxlib import read


def _materials(two_path):
    """{voxel: material} of a TwoColor file: its two colours, the greener 'leaf'."""
    size, vox, pal, mats = read(two_path)
    idx = sorted(set(vox.values()))
    green = max(idx, key=lambda i: pal[i - 1][1] - pal[i - 1][0])
    return {p: ("leaf" if i == green else "wood") for p, i in vox.items()}


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def recolour(base_path, two_path, new_sprite, paint_sprite=None):
    """A build ({voxel: (material, rgb)}, size) of the old model in the new sprite's
    colours."""
    size, vox, pal, mats = read(base_path)
    mat = _materials(two_path)
    sp = paint_sprite or new_sprite
    rgb = sp.rgb.astype(int)
    m = interior(sp.mask)
    h, s, v = hue_sat(rgb)
    leaf_px = rgb[m & (h > 60) & (h < 175) & (s > 0.18)]
    wood_px = rgb[m & (((h < 55) | (h > 320)) & (s > 0.15))]
    out = {}
    for material, px in (("leaf", leaf_px), ("wood", wood_px)):
        old = sorted({pal[i - 1][:3] for p, i in vox.items() if mat[p] == material}, key=_lum)
        if not old:
            continue
        if len(px) < 3:
            new = old
        else:
            new = sorted([tuple(int(c) for c in q) for q in quantize(px, len(old)).tolist()], key=_lum)
            while len(new) < len(old):
                new.append(new[-1])
        table = {o: new[min(len(new) - 1, round(i * (len(new) - 1) / max(1, len(old) - 1)))] for i, o in enumerate(old)}
        for p, i in vox.items():
            if mat[p] == material:
                out[p] = (material, table[pal[i - 1][:3]])
    return out, tuple(size)
