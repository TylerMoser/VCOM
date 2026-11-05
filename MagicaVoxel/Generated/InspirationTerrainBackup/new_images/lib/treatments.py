"""The seven treatments of a family, from its Base and Cartoon builds, as the
workspace's variation specification has them (knowledge/VARIATIONS.md, with the
TwoColor amendment of 2026-10-28):

- Base: the build's own colours, each distinct colour one palette index.
- Cartoon: the Cartoon build, its own colours.
- CratePalette: Base's voxels exactly, the pinned crate palette byte for byte,
  each colour on the nearest entry of its material's range (index 253, the
  crate's glass, and 255, the game's blood, never used).
- TwoColor: Base's voxels, one flat colour a material: the mean of the material's
  colours on Base's surface as seen from above (an open top counts twice, an open
  side once, an underside not at all), snapped to the nearest of its own shades.
- Cartoon_TwoColor: the Cartoon voxels, the same flat colours.
- CratePalette_TwoColor and Cartoon_CratePalette_TwoColor: Base's and Cartoon's
  voxels, each material's flat colour on its nearest crate entry (distinct entries
  for distinct materials), the crate palette byte for byte.

A build is ({(x, y, z): (material, rgb)}, (sx, sy, sz)). Both builds share one
canvas: the larger of the two, each centred on it horizontally, both on z 0.
"""
import hashlib
import json
from pathlib import Path

from voxlib import encode

ROOT = Path(r"C:/Users/tandm/Documents/Projects/VoxelRidgeInspiration")
CRATE = json.loads((ROOT / "knowledge" / "palettes" / "crate-palette.json").read_text())
CRATE_RGBA = [tuple(c) for c in CRATE["rgba"]]
TREATMENTS = ["Base", "Cartoon", "CratePalette", "TwoColor", "Cartoon_TwoColor", "CratePalette_TwoColor",
              "Cartoon_CratePalette_TwoColor"]
# Crate entries each material may use.
CLASSES = {
    "leaf": [241, 242, 243, 244, 245, 246],
    "wood": [178, 179, 180, 225, 226, 227, 228, 229, 233, 234, 235, 236, 237],
    "cut": [229, 230, 235, 236, 237, 238],
    "earth": [178, 179, 180, 225, 226, 227, 228, 229, 233, 234, 235, 236, 237, 238],
    "flower": [212, 213, 214, 219, 220, 221],
    "red": [219, 220, 221, 178, 222],
    "blue": [250, 251, 252, 254],
    "bloom": [196, 238, 246, 248, 230, 229],
    "yellow": [228, 229, 230, 222],
    "cloth": [236, 237, 238, 196, 195],
    "rope": [235, 236, 179, 180, 234],
    "stone": [193, 194, 195, 205, 206],
    "metal": [193, 194, 195, 196, 205, 206],
    "black": [177, 201, 202, 203, 204, 217, 225],
    "white": [196, 248, 238, 195],
    "skin": [235, 236, 237, 238, 180, 214],
    "purple": [210, 211, 212, 213],
    "orange": [221, 222, 228, 229],
    "water": [250, 251, 252, 254],
    "moss": [243, 244, 245, 246, 230],
    # new_1's figures
    "hood": [205, 206, 193, 194, 204],
    "gold": [228, 229, 230, 222],
    "tunic": [211, 212, 213, 214],
    "boot": [178, 179, 180, 226, 227, 234, 235],
    "scale": [241, 242, 243, 244, 245, 246],
}


def suffix(t):
    return "" if t == "Base" else "_" + t


def _lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def _nearest_crate(rgb, allowed, taken=()):
    cands = [i for i in allowed if i not in taken] or list(allowed)
    return min(cands, key=lambda i: (sum((CRATE_RGBA[i - 1][j] - rgb[j]) ** 2 for j in range(3)), i))


def _pad(build, size):
    vox, (sx, sy, sz) = build
    ox, oy = (size[0] - sx) // 2, (size[1] - sy) // 2
    assert (size[0] - sx) % 2 == 0 and (size[1] - sy) % 2 == 0, ("canvas parity", size, (sx, sy))
    return {(x + ox, y + oy, z): v for (x, y, z), v in vox.items()}


def _own_palette(vox):
    """Each distinct colour one index, ordered by material then lightness."""
    cols = sorted({(m, c) for (m, c) in vox.values()}, key=lambda mc: (mc[0], _lum(mc[1]), mc[1]))
    rgbs = []
    for m, c in cols:
        if c not in rgbs:
            rgbs.append(c)
    assert len(rgbs) <= 254, "too many colours"
    index = {c: i + 1 for i, c in enumerate(rgbs)}
    palette = [tuple(c) + (255,) for c in rgbs] + [(0, 0, 0, 255)] * (256 - len(rgbs))
    return index, palette


def _flat(counts):
    """A material's one flat colour: the mean of its colours as seen (weighted by
    how much of each the camera sees), snapped to the nearest of its own shades, so
    it is a colour the model already has that stands for its overall look."""
    total = sum(counts.values())
    if total == 0:
        return max(counts)
    mean = [sum(c[i] * n for c, n in counts.items()) / float(total) for i in range(3)]
    return min(counts, key=lambda c: (sum((c[i] - mean[i]) ** 2 for i in range(3)), c))


def ground(build):
    """A build moved down to stand on z 0 (a sprite's box can end in shadow rows),
    its canvas as tall as it is."""
    vox, (sx, sy, sz) = build
    z0 = min(z for (x, y, z) in vox)
    vox = {(x, y, z - z0): v for (x, y, z), v in vox.items()}
    return vox, (sx, sy, max(z for (x, y, z) in vox) + 1)


def family(prefix, name, base, cartoon, layer="Model", canvas=None):
    """[(file name, bytes, record)] of a family's seven files."""
    base, cartoon = ground(base), ground(cartoon)
    sx = max(base[1][0], cartoon[1][0])
    sy = max(base[1][1], cartoon[1][1])
    sz = max(base[1][2], cartoon[1][2])
    if canvas:
        sx, sy, sz = max(sx, canvas[0]), max(sy, canvas[1]), max(sz, canvas[2])
    size = (sx, sy, sz)
    B = _pad(base, size)
    K = _pad(cartoon, size)
    for v in (B, K):
        assert min(z for (x, y, z) in v) == 0, (name, "not grounded")
    # each material's flat colour: its most common colour on Base's surface as the
    # game's camera sees it from above: a voxel's open top counts twice, each open
    # side once, its underside not at all (a leaf's dark underside is not its colour)
    counts = {}
    for (x, y, z), (m, c) in B.items():
        counts.setdefault(m, {}).setdefault(c, 0)
        counts[m][c] += 2 * ((x, y, z + 1) not in B) + sum(
            q not in B for q in ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z)))
    for (m, c) in K.values():
        counts.setdefault(m, {}).setdefault(c, 0)
    flat = {m: _flat(cs) for m, cs in counts.items()}
    mats = sorted(flat)
    taken = []
    flat_crate = {}
    for m in mats:
        idx = _nearest_crate(flat[m], CLASSES.get(m, CLASSES["leaf"]), taken)
        taken.append(idx)
        flat_crate[m] = idx
    out = []
    geometry = {"Base": B, "Cartoon": K}
    for t in TREATMENTS:
        cart = "Cartoon" in t
        src = K if cart else B
        if "TwoColor" in t:
            if "CratePalette" in t:
                vox = {p: flat_crate[m] for p, (m, c) in src.items()}
                pal = CRATE_RGBA
            else:
                order = {m: i + 1 for i, m in enumerate(mats)}
                vox = {p: order[m] for p, (m, c) in src.items()}
                pal = [tuple(flat[m]) + (255,) for m in mats] + [(0, 0, 0, 255)] * (256 - len(mats))
        elif "CratePalette" in t:
            memo = {}
            vox = {}
            for p, (m, c) in src.items():
                if (m, c) not in memo:
                    memo[(m, c)] = _nearest_crate(c, CLASSES.get(m, CLASSES["leaf"]))
                vox[p] = memo[(m, c)]
            pal = CRATE_RGBA
        else:
            index, pal = _own_palette(src)
            vox = {p: index[c] for p, (m, c) in src.items()}
        assert 255 not in vox.values() and 253 not in vox.values() if "CratePalette" in t else 255 not in vox.values()
        stem = "%s_%s%s" % (prefix, name, suffix(t))
        b = encode(size, vox, pal, name=stem, layer=layer)
        groups = {}
        for p, (m, c) in src.items():
            groups.setdefault(m, set()).add(vox[p])
        xs = [p[0] for p in vox]
        ys = [p[1] for p in vox]
        zs = [p[2] for p in vox]
        rec = {"file": stem + ".vox", "family": "%s_%s" % (prefix, name), "treatment": t, "size": list(size),
               "voxels": len(vox), "colours": len(set(vox.values())),
               "groups": {m: len(ix) for m, ix in sorted(groups.items())},
               "occupied_min": [min(xs), min(ys), min(zs)], "occupied_max": [max(xs), max(ys), max(zs)],
               "geometry": "%s_%s%s.vox" % (prefix, name, "_Cartoon" if cart else ""),
               "sha256": hashlib.sha256(b).hexdigest()}
        out.append((stem + ".vox", b, rec))
    return out, {"flat": {m: list(c) for m, c in flat.items()}, "flat_crate": flat_crate, "canvas": list(size)}


def copy_family(prefix, name, source_files, layer="Model"):
    """A family that is another image's model exactly (the same art): its seven
    files' voxels and palettes, re-encoded under this family's names."""
    from voxlib import read
    out = []
    for t, path in zip(TREATMENTS, source_files):
        size, vox, pal, mats = read(path)
        stem = "%s_%s%s" % (prefix, name, suffix(t))
        b = encode(tuple(size), vox, [tuple(c) for c in pal], name=stem, layer=layer)
        xs = [p[0] for p in vox]
        ys = [p[1] for p in vox]
        zs = [p[2] for p in vox]
        rec = {"file": stem + ".vox", "family": "%s_%s" % (prefix, name), "treatment": t, "size": list(size),
               "voxels": len(vox), "colours": len(set(vox.values())), "groups": {},
               "occupied_min": [min(xs), min(ys), min(zs)], "occupied_max": [max(xs), max(ys), max(zs)],
               "geometry": "%s_%s%s.vox" % (prefix, name, "_Cartoon" if "Cartoon" in t else ""),
               "copied_from": str(Path(path).relative_to(ROOT)).replace("\\", "/"),
               "sha256": hashlib.sha256(b).hexdigest()}
        out.append((stem + ".vox", b, rec))
    return out
