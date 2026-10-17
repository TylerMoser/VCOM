"""The map's scene as the streams need it: its rivers, lakes, borders, roads and coast, read
straight out of vcom/Scenes/Map.tscn, in pixels of the pictures measured from their top left
corner (the middle of pixel (x, y) is (x + 0.5, y + 0.5): the measure m1_shapes.py works in).

The scene is read, not the source data, because the scene is the map: a stream has to end on a
river's line as the scene draws it, and the scene is changed by hand from now on.
"""
import re

import numpy as np

UNITS = 3.35            # the scene's units to a pixel of the pictures

_NODE = re.compile(r'^\[node name="([^"]+)" type="([^"]+)" parent="([^"]+)"')
_CURVE = re.compile(r'^\[sub_resource type="Curve" id="([^"]+)"\]')
_VECTOR = re.compile(r"Vector2\(([-0-9.e]+), ([-0-9.e]+)\)")


def _packed(value):
    inner = value[value.index("(") + 1: value.rindex(")")]
    if not inner.strip():
        return np.zeros((0, 2))
    return np.array([float(v) for v in inner.split(",")], dtype=np.float64).reshape(-1, 2) / UNITS


class Line:
    def __init__(self, name, parent, points, width, curve):
        self.name, self.parent, self.points, self.width, self.curve = name, parent, points, width, curve

    def widths(self):
        """The line's width at each of its points, in pixels of the pictures."""
        base = np.full(len(self.points), self.width / UNITS)
        if self.curve is None or len(self.points) < 2:
            return base
        along = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(self.points, axis=0).T))])
        t = along / max(along[-1], 1e-9)
        return base * np.interp(t, self.curve[:, 0], self.curve[:, 1])


class Polygon:
    def __init__(self, name, parent, points):
        self.name, self.parent, self.points = name, parent, points


def read(path):
    """(lines, polygons) of the scene: every Line2D and Polygon2D with where it sits in the tree."""
    curves, lines, polygons = {}, [], []
    kind, current, props = None, None, {}

    def finish():
        if kind == "curve" and "_data" in props:
            pairs = _VECTOR.findall(props["_data"])
            curves[current] = np.array([[float(a), float(b)] for a, b in pairs])
        elif kind == "Line2D" and "points" in props:
            lines.append((current, props.get("points"), float(props.get("width", "10")), props.get("width_curve")))
        elif kind == "Polygon2D" and "polygon" in props:
            polygons.append((current, props.get("polygon")))

    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            if line.startswith("["):
                finish()
                kind, current, props = None, None, {}
                m = _NODE.match(line)
                if m:
                    kind = m.group(2)
                    parent = m.group(3)
                    current = (m.group(1), parent)
                    continue
                m = _CURVE.match(line)
                if m:
                    kind, current = "curve", m.group(1)
                continue
            if kind is None or " = " not in line:
                continue
            key, value = line.split(" = ", 1)
            props[key] = value
        finish()

    out_lines = []
    for (name, parent), points, width, curve in lines:
        cid = None
        if curve:
            m = re.search(r'SubResource\("([^"]+)"\)', curve)
            cid = m.group(1) if m else None
        out_lines.append(Line(name, parent, _packed(points), width, curves.get(cid)))
    out_polygons = [Polygon(name, parent, _packed(points)) for (name, parent), points in polygons]
    return out_lines, out_polygons
