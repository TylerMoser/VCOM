"""Draws map icons in the manner of the MWM icons: bold black shapes, inked by hand, with a white
edge round them, or white shapes with a black outline.

An icon is 666 x 666 like the pack's, its ground line at y = 453 and its middle at x = 333, where
the pack's own buildings stand. Shapes are given in the icon's own measure: x to the right of the
middle, y up from the ground, in the pack's pixels.

An Icon is a list of parts, drawn one over another:
- ink: one or more layers of black. Each layer is a set of outlines added together, with holes
  cut out of it (doors, windows). A layer in front keeps a thin white line between it and the
  layers behind, as the pack's Town does between its tower and its house. Round all the black of
  the part runs the white edge.
- paper: a white shape with a black outline, as the pack's flags and banners are.
- piece: one of the pack's own icons, placed whole, or its black alone taken into an ink part.

A shape drawn here is given the wavering edge and soft corners of a brush: its outline is pushed
about a little by a slow random field, then blurred and cut off at half strength.
"""
import os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

SIZE = 666
SS = 2                    # the icon is worked at this many times its size, then reduced
BIG = SIZE * SS
CX, GROUND = 333.0, 453.0
EDGE = 10.0               # px of white round the black
BETWEEN = 4.5             # px of white between a layer and those behind it
SOFT = 3.4                # px: how far corners are rounded
WAVER = 2.4               # px: how far an edge wanders
SWELL = 30.0              # px: over what length it wanders
LINE = 8.0                # px: the black outline of a white shape
PACK = None               # the folder of the pack's icons, set by whoever uses this


def to_big(points):
    """Points in the icon's own measure, as points of the big working picture."""
    return [((CX + x) * SS, (GROUND - y) * SS) for x, y in points]


class Icon:
    def __init__(self, seed=0):
        self.parts = []
        self.rng = np.random.default_rng(seed)
        field = [ndimage.gaussian_filter(self.rng.standard_normal((BIG // 4, BIG // 4)), SWELL * SS / 4.0) for _ in range(2)]
        self.drift = [ndimage.zoom(f / max(f.std(), 1e-9), 4, order=1) * WAVER * SS for f in field]

    # -- ink ----------------------------------------------------------------------------------------------
    def ink(self):
        """Starts a part of black layers with one white edge round them all."""
        part = {"kind": "ink", "layers": []}
        self.parts.append(part)
        return part

    def layer(self, part=None):
        """Starts a layer in an ink part (the last ink part, or a new one)."""
        if part is None:
            part = self.parts[-1] if self.parts and self.parts[-1]["kind"] == "ink" else self.ink()
        layer = {"add": [], "cut": [], "given": []}
        part["layers"].append(layer)
        return layer

    # -- paper --------------------------------------------------------------------------------------------
    def paper(self, line=LINE):
        """Starts a white shape with a black outline."""
        part = {"kind": "paper", "add": [], "cut": [], "marks": [], "line": line, "given": []}
        self.parts.append(part)
        return part

    # -- the pack's own ---------------------------------------------------------------------------------------
    def piece(self, name, x=0.0, y=0.0, scale=1.0, flip=False):
        """One of the pack's icons whole, its foot at (x, y)."""
        self.parts.append({"kind": "piece", "name": name, "x": x, "y": y, "scale": scale, "flip": flip})

    # -- drawing ----------------------------------------------------------------------------------------------
    def _brushed(self, add, cut):
        """Outlines as a mask with a brush's edge: 0..1."""
        image = Image.new("L", (BIG, BIG), 0)
        pen = ImageDraw.Draw(image)
        for points in add:
            pen.polygon(to_big(points), fill=255)
        for points in cut:
            pen.polygon(to_big(points), fill=0)
        mask = np.asarray(image, dtype=np.float32) / 255.0
        if not mask.any():
            return mask > 0.5
        yy, xx = np.mgrid[0:BIG, 0:BIG].astype(np.float32)
        mask = ndimage.map_coordinates(mask, [yy + self.drift[1], xx + self.drift[0]], order=1, mode="constant")
        return ndimage.gaussian_filter(mask, SOFT * SS) > 0.5

    def _black_of(self, part):
        black = np.zeros((BIG, BIG), dtype=bool)
        for layer in part["layers"]:
            mine = self._brushed(layer["add"], layer["cut"]) if layer["add"] else np.zeros((BIG, BIG), dtype=bool)
            for given in layer["given"]:
                mine |= given
            if black.any() and mine.any():
                black &= ndimage.distance_transform_edt(~mine) > BETWEEN * SS
            black |= mine
        return black

    def render(self):
        """The icon as an RGBA picture, 666 x 666."""
        colour = np.zeros((BIG, BIG, 3), dtype=np.float32)      # colour times cover
        cover = np.zeros((BIG, BIG), dtype=np.float32)

        def lay(rgb, alpha):
            nonlocal colour, cover
            colour = colour * (1.0 - alpha[..., None]) + np.asarray(rgb, dtype=np.float32) * alpha[..., None]
            cover = cover * (1.0 - alpha) + alpha

        def soft(distance_inside_minus_outside):
            return np.clip(distance_inside_minus_outside + 0.5, 0.0, 1.0)

        for part in self.parts:
            if part["kind"] == "ink":
                black = self._black_of(part)
                if not black.any():
                    continue
                away = ndimage.distance_transform_edt(~black)
                within = ndimage.distance_transform_edt(black)
                white = soft(EDGE * SS - away)
                white = np.maximum(white, ndimage.binary_fill_holes(away <= EDGE * SS).astype(np.float32))
                lay((1.0, 1.0, 1.0), white)
                lay((0.0, 0.0, 0.0), soft(within - away))
            elif part["kind"] == "paper":
                shape = self._brushed(part["add"], part["cut"])
                for given in part["given"]:
                    shape |= given
                away = ndimage.distance_transform_edt(~shape)
                within = ndimage.distance_transform_edt(shape)
                lay((0.0, 0.0, 0.0), soft(part["line"] * SS - away))
                lay((1.0, 1.0, 1.0), soft(within - away))
                if part["marks"]:
                    marks = self._brushed(part["marks"], []) & shape
                    lay((0.0, 0.0, 0.0), soft(ndimage.distance_transform_edt(marks) - ndimage.distance_transform_edt(~marks)))
            else:
                image = pack(part["name"])
                box = image.getbbox()
                cut = image.crop(box)
                if part["flip"]:
                    cut = cut.transpose(Image.FLIP_LEFT_RIGHT)
                w, h = max(1, round(cut.width * part["scale"] * SS)), max(1, round(cut.height * part["scale"] * SS))
                cut = np.asarray(cut.resize((w, h), Image.LANCZOS), dtype=np.float32) / 255.0
                left = round((CX + part["x"]) * SS - w / 2.0)
                top = round((GROUND - part["y"]) * SS - h)
                y0, y1, x0, x1 = max(top, 0), min(top + h, BIG), max(left, 0), min(left + w, BIG)
                alpha = np.zeros((BIG, BIG), dtype=np.float32)
                rgb = np.zeros((BIG, BIG, 3), dtype=np.float32)
                alpha[y0:y1, x0:x1] = cut[y0 - top: y1 - top, x0 - left: x1 - left, 3]
                rgb[y0:y1, x0:x1] = cut[y0 - top: y1 - top, x0 - left: x1 - left, :3]
                colour = colour * (1.0 - alpha[..., None]) + rgb * alpha[..., None]
                cover = cover * (1.0 - alpha) + alpha
        # Reduced to the icon's size, colour and cover apart, so that no dark creeps into the white's edge.
        small_cover = cover.reshape(SIZE, SS, SIZE, SS).mean(axis=(1, 3))
        small_colour = colour.reshape(SIZE, SS, SIZE, SS, 3).mean(axis=(1, 3))
        rgb = np.where(small_cover[..., None] > 1e-6, small_colour / np.maximum(small_cover[..., None], 1e-6), 1.0)
        out = np.concatenate([rgb, small_cover[..., None]], axis=2)
        return Image.fromarray(np.round(np.clip(out, 0.0, 1.0) * 255.0).astype(np.uint8), "RGBA")


_PACK = {}


def pack(name):
    """One of the pack's icons."""
    if name not in _PACK:
        _PACK[name] = Image.open(os.path.join(PACK, name + ".png")).convert("RGBA")
    return _PACK[name]


def pack_black(name, x=0.0, y=0.0, scale=1.0, flip=False):
    """The black of one of the pack's icons as a mask of the big working picture, its foot at (x, y):
    to be given to an ink layer, so that it joins the layers drawn here under one white edge."""
    image = pack(name)
    a = np.asarray(image, dtype=np.float32) / 255.0
    ink = ((a[..., :3].mean(axis=2) < 0.45) & (a[..., 3] > 0.5)).astype(np.float32)
    ys, xs = np.nonzero(ink)
    cut = Image.fromarray((ink[ys.min(): ys.max() + 1, xs.min(): xs.max() + 1] * 255).astype(np.uint8), "L")
    if flip:
        cut = cut.transpose(Image.FLIP_LEFT_RIGHT)
    w, h = max(1, round(cut.width * scale * SS)), max(1, round(cut.height * scale * SS))
    cut = np.asarray(cut.resize((w, h), Image.LANCZOS), dtype=np.float32) / 255.0 > 0.5
    left = round((CX + x) * SS - w / 2.0)
    top = round((GROUND - y) * SS - h)
    mask = np.zeros((BIG, BIG), dtype=bool)
    y0, y1, x0, x1 = max(top, 0), min(top + h, BIG), max(left, 0), min(left + w, BIG)
    mask[y0:y1, x0:x1] = cut[y0 - top: y1 - top, x0 - left: x1 - left]
    return mask


# -- outlines -------------------------------------------------------------------------------------------------
def box(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def oval(cx, cy, rx, ry, steps=40, start=0.0, end=360.0):
    angles = np.radians(np.linspace(start, end, steps, endpoint=False))
    return [(cx + rx * np.cos(a), cy + ry * np.sin(a)) for a in angles]


def arch(x, w, h, y=0.0):
    """A doorway: straight sides and a round head."""
    r = w / 2.0
    top = [(x + r * np.cos(a), y + h - r + r * np.sin(a)) for a in np.radians(np.linspace(0, 180, 12))]
    return [(x + r, y - 2.0)] + top + [(x - r, y - 2.0)]


def star(cx, cy, r, points=5, inner=0.45, turn=90.0):
    out = []
    for i in range(points * 2):
        a = np.radians(turn + i * 180.0 / points)
        rr = r if i % 2 == 0 else r * inner
        out.append((cx + rr * np.cos(a), cy + rr * np.sin(a)))
    return out
