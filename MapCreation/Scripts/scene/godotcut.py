"""Godot 4's own cutter of a polygon into triangles, done here the same way, so that a polygon can be
known to draw before it is put in the scene.

It is core/math/triangulate.cpp, which Geometry2D.triangulate_polygon() and Polygon2D both use: an ear
cutter that wants a simple outline and fails ("probable bad polygon") when it goes twice round without
finding an ear, first strictly and then allowing flat triangles. Points are float32 in Godot, as here.
Checked against Godot 4.7 on the forests' 1,961 pieces of 2026-10-17: the same 14 failed in both.
"""
import numpy as np

F = np.float32
CMP_EPSILON = F(0.00001)


def triangulate(points):
    """The triangles' corners, three indices of [points] a triangle, or None where Godot fails."""
    p = np.asarray(points, dtype=np.float32)
    n = len(p)
    if n < 3:
        return None
    x, y = p[:, 0], p[:, 1]
    area = F(0.0)
    for i in range(n):
        j = (i + 1) % n
        area = F(area + F(F(x[i] * y[j]) - F(y[i] * x[j])))
    corners = list(range(n)) if area > 0 else list(range(n - 1, -1, -1))
    result = []
    relaxed = False
    left = n
    count = 2 * left
    v = left - 1
    while left > 2:
        count -= 1
        if count < 0:
            if relaxed:
                return None
            count = 2 * left
            relaxed = True
        u = v if v < left else 0
        v = u + 1 if u + 1 < left else 0
        w = v + 1 if v + 1 < left else 0
        if _snip(x, y, u, v, w, left, corners, relaxed):
            result.extend((corners[u], corners[v], corners[w]))
            del corners[v]
            left -= 1
            count = 2 * left
    return result


def _snip(x, y, u, v, w, n, corners, relaxed):
    """Whether corner v can be cut off as an ear: turned the right way (flat allowed once relaxed), and
    no other corner inside it (strictly inside, once relaxed)."""
    ax, ay = x[corners[u]], y[corners[u]]
    bx, by = x[corners[v]], y[corners[v]]
    cx, cy = x[corners[w]], y[corners[w]]
    threshold = -CMP_EPSILON if relaxed else CMP_EPSILON
    if threshold > F(F(F(bx - ax) * F(cy - ay)) - F(F(by - ay) * F(cx - ax))):
        return False
    others = np.asarray(corners[:n])
    keep = np.ones(n, dtype=bool)
    keep[[u, v, w]] = False
    px, py = x[others[keep]], y[others[keep]]
    a_cross_bp = F(cx - bx) * (py - by) - F(cy - by) * (px - bx)
    c_cross_ap = F(bx - ax) * (py - ay) - F(by - ay) * (px - ax)
    b_cross_cp = F(ax - cx) * (py - cy) - F(ay - cy) * (px - cx)
    if relaxed:
        inside = (a_cross_bp > 0) & (b_cross_cp > 0) & (c_cross_ap > 0)
    else:
        inside = (a_cross_bp >= 0) & (b_cross_cp >= 0) & (c_cross_ap >= 0)
    return not inside.any()
