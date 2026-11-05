"""Reading a sprite out of an inspiration image: its pixels (without the sheet's
white background or the grey drop shadow), scaled to voxels, and split into
materials by colour.

A sprite is read at the image's own voxel scale: new_2 is native pixel art of 16
pixels a tile (a pixel a voxel); new_1 is pixel art enlarged to 73.6 image pixels
a tile (4.6 a voxel), so it is sampled at each voxel's centre.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(r"C:/Users/tandm/Documents/Projects/VoxelRidgeInspiration")
SCALE = {"new_1.jpg": 73.6 / 16.0, "new_2.jpg": 1.0}
_cache = {}


def image(name):
    if name not in _cache:
        _cache[name] = np.asarray(Image.open(ROOT / name).convert("RGB")).astype(int)
    return _cache[name]


def is_background(rgb):
    """The sheet's white and the drop shadows' neutral grey."""
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mn = np.minimum(np.minimum(r, g), b)
    mx = np.maximum(np.maximum(r, g), b)
    mean = (r + g + b) / 3.0
    white = mn > 235
    grey = ((mx - mn) < 22) & (mean > 135) & (mean < 225)
    # JPEG halo round a sprite: pale, nearly unsaturated pixels
    halo = (mn > 196) & ((mx - mn) < 48)
    return white | grey | halo


class Sprite:
    """A sprite's pixels at voxel scale: rgb[row, col] (row 0 the top) and mask;
    [box] is (x0, y0, x1, y1) in the image's pixels, exclusive."""

    def __init__(self, image_name, box, mask_fn=None, keep_main=True):
        self.image_name, self.box = image_name, tuple(box)
        s = SCALE[image_name]
        im = image(image_name)
        x0, y0, x1, y1 = box
        if s == 1.0:
            rgb = im[y0:y1, x0:x1]
        else:
            w = int(round((x1 - x0) / s))
            h = int(round((y1 - y0) / s))
            xs = (x0 + (np.arange(w) + 0.5) * s).astype(int)
            ys = (y0 + (np.arange(h) + 0.5) * s).astype(int)
            rgb = im[ys][:, xs]
        self.rgb = rgb
        self.mask = ~is_background(rgb) if mask_fn is None else mask_fn(rgb)
        self.h, self.w = rgb.shape[:2]
        if keep_main:
            self.mask = main_body(self.mask)

    def rows(self, sel=None):
        """For each row (top first): (left, right) extent of [sel] (default the mask), or None."""
        m = self.mask if sel is None else sel
        out = []
        for r in range(self.h):
            cols = np.nonzero(m[r])[0]
            out.append((int(cols.min()), int(cols.max())) if len(cols) else None)
        return out

    def luminance(self):
        rgb = self.rgb.astype(float)
        return 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]


def hue_sat(rgb):
    """(hue in degrees, saturation 0..1, value 0..255) of an RGB array."""
    rgb = rgb.astype(float)
    mx = rgb.max(axis=-1)
    mn = rgb.min(axis=-1)
    d = mx - mn + 1e-6
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60.0
    s = np.where(mx > 0, (mx - mn) / (mx + 1e-6), 0)
    return h, s, mx


def is_foliage(rgb):
    h, s, v = hue_sat(rgb)
    return (h > 65) & (h < 175) & (s > 0.18)


def is_wood(rgb):
    """Browns and dark greys of trunks and roots."""
    h, s, v = hue_sat(rgb)
    brown = ((h < 50) | (h > 330)) & (s > 0.15) & (v < 190)
    return brown


def quantize(colors, k):
    """Up to [k] representative colours of an (n, 3) array (k-means, deterministic)."""
    colors = np.asarray(colors, float)
    if len(colors) == 0:
        return np.zeros((0, 3))
    uniq = np.unique(colors.round(), axis=0)
    if len(uniq) <= k:
        return uniq
    lum = colors @ np.array([0.299, 0.587, 0.114])
    order = np.argsort(lum)
    centres = np.array([colors[order[int((i + 0.5) * len(order) / k)]] for i in range(k)])
    for _ in range(12):
        d = ((colors[:, None, :] - centres[None]) ** 2).sum(-1)
        lab = d.argmin(1)
        for i in range(k):
            if (lab == i).any():
                centres[i] = colors[lab == i].mean(0)
    return np.unique(centres.round(), axis=0)


def nearest(rgb, centres):
    d = ((np.asarray(rgb, float)[..., None, :] - centres) ** 2).sum(-1)
    return centres[d.argmin(-1)]


def interior(mask):
    """The mask without its border pixels (where JPEG artefacts gather): colours are
    sampled there."""
    m = mask.copy()
    m[1:, :] &= mask[:-1, :]
    m[:-1, :] &= mask[1:, :]
    m[:, 1:] &= mask[:, :-1]
    m[:, :-1] &= mask[:, 1:]
    return m if m.sum() >= max(8, mask.sum() // 4) else mask


def is_water(rgb):
    """Blue and cyan water drawn round aquatic plants."""
    h, s, v = hue_sat(rgb)
    rgbf = rgb.astype(float)
    cyan = (h >= 165) & (h <= 260) & (s > 0.12)
    pale_cyan = (rgbf[..., 2] > rgbf[..., 0] + 25) & (rgbf[..., 2] >= rgbf[..., 1] - 25) & (v > 150)
    return cyan | pale_cyan


def main_body(mask, near=2):
    """The mask's largest eight-connected part and every part within [near] pixels
    of it (a sprite's box can catch scraps of its neighbours)."""
    H, W = mask.shape
    lab = np.zeros(mask.shape, int)
    sizes = [0]
    k = 0
    for r in range(H):
        for c in range(W):
            if mask[r, c] and not lab[r, c]:
                k += 1
                stack = [(r, c)]
                lab[r, c] = k
                n = 0
                while stack:
                    a, b = stack.pop()
                    n += 1
                    for da in (-1, 0, 1):
                        for db in (-1, 0, 1):
                            aa, bb = a + da, b + db
                            if 0 <= aa < H and 0 <= bb < W and mask[aa, bb] and not lab[aa, bb]:
                                lab[aa, bb] = k
                                stack.append((aa, bb))
                sizes.append(n)
    if k <= 1:
        return mask
    main = int(np.argmax(sizes))
    keep = lab == main
    grown = keep.copy()
    for _ in range(near):
        g = grown.copy()
        g[1:, :] |= grown[:-1, :]
        g[:-1, :] |= grown[1:, :]
        g[:, 1:] |= grown[:, :-1]
        g[:, :-1] |= grown[:, 1:]
        grown = g
    ids = set(np.unique(lab[grown & mask])) - {0}
    return np.isin(lab, list(ids))
