"""Fast previews of voxel worlds ((x, y, z) -> RGB): exposed faces sampled and
splatted into a depth buffer with numpy. view3d is an orthographic view lit from
the upper left; oblique is an image's own projection (x across, y and z up the
image, z foreshortened by K, only front and top faces), for comparing with the art."""
import math

import numpy as np
from PIL import Image

DIRS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]


def _dense(world):
    pts = np.array(list(world.keys()), dtype=np.int32)
    cols = np.array(list(world.values()), dtype=np.int32)
    lo = pts.min(0)
    shape = pts.max(0) - lo + 1
    occ = np.zeros(shape + 2, dtype=bool)
    rgb = np.zeros(tuple(shape + 2) + (3,), dtype=np.int32)
    q = pts - lo + 1
    occ[q[:, 0], q[:, 1], q[:, 2]] = True
    rgb[q[:, 0], q[:, 1], q[:, 2]] = cols
    return occ, rgb, lo - 1


def _faces(world, dirs):
    """For each direction in [dirs]: (voxel positions, colours) of the faces exposed that way."""
    occ, rgb, off = _dense(world)
    out = []
    for d in dirs:
        nb = np.roll(occ, shift=(-d[0], -d[1], -d[2]), axis=(0, 1, 2))
        exp = occ & ~nb
        idx = np.argwhere(exp)
        out.append((d, idx + off, rgb[exp]))
    return out


def _splat(samples_xy, depth, colour, scale, bg, pad=10):
    xs, ys = samples_xy
    x0, y0 = xs.min(), ys.min()
    ix = ((xs - x0) * scale).astype(np.int64) + pad
    iy = ((ys - y0) * scale).astype(np.int64) + pad
    W, H = ix.max() + pad + 1, iy.max() + pad + 1
    order = np.lexsort((depth,))
    key = iy[order] * W + ix[order]
    first = np.unique(key, return_index=True)[1]
    img = np.empty((H * W, 3), dtype=np.uint8)
    img[:] = bg
    img[key[first]] = colour[order][first]
    return Image.fromarray(img.reshape(H, W, 3))


def _quad(d):
    """A face's corner and its two edge vectors, for a voxel at the origin facing d."""
    x, y, z = d
    if x:
        return ((1 if x > 0 else 0, 0, 0), (0, 1, 0), (0, 0, 1))
    if y:
        return ((0, 1 if y > 0 else 0, 0), (1, 0, 0), (0, 0, 1))
    return ((0, 0, 1 if z > 0 else 0), (1, 0, 0), (0, 1, 0))


def view3d(world, yaw=-25, pitch=38, scale=3.0, bg=(214, 222, 205)):
    yr, pr = math.radians(yaw), math.radians(pitch)
    fwd = np.array([math.sin(yr) * math.cos(pr), math.cos(yr) * math.cos(pr), -math.sin(pr)])
    right = np.array([math.cos(yr), -math.sin(yr), 0.0])
    up = np.cross(right, fwd)
    light = np.array([-0.55, -0.45, 0.70])
    light /= np.linalg.norm(light)
    n = max(2, int(math.ceil(scale * 1.5)))
    grid = (np.arange(n) + 0.5) / n
    ga, gb = np.meshgrid(grid, grid)
    ga, gb = ga.ravel(), gb.ravel()
    XY, D, C = [], [], []
    for d, pos, col in _faces(world, DIRS):
        nv = np.array(d, float)
        if nv @ fwd >= 0 or len(pos) == 0:
            continue
        o, e1, e2 = (np.array(v, float) for v in _quad(d))
        shade = 0.55 + 0.45 * max(0.0, nv @ light)
        p = pos[:, None, :] + o + ga[None, :, None] * e1 + gb[None, :, None] * e2
        p = p.reshape(-1, 3)
        XY.append((p @ right, -(p @ up)))
        D.append(p @ fwd)
        C.append(np.repeat(np.clip(col * shade, 0, 255).astype(np.uint8), len(ga), axis=0))
    xs = np.concatenate([a for a, b in XY])
    ys = np.concatenate([b for a, b in XY])
    return _splat((xs, ys), np.concatenate(D), np.concatenate(C), scale, bg)


def oblique(world, K, scale=4.0, ground_z=16, bg=(128, 158, 112)):
    n = max(2, int(math.ceil(scale * 1.5)))
    grid = (np.arange(n) + 0.5) / n
    ga, gb = np.meshgrid(grid, grid)
    ga, gb = ga.ravel(), gb.ravel()
    XY, D, C = [], [], []
    for d, pos, col in _faces(world, [(0, -1, 0), (0, 0, 1)]):
        if len(pos) == 0:
            continue
        o, e1, e2 = (np.array(v, float) for v in _quad(d))
        shade = 1.0 if d[2] else 0.86
        p = (pos[:, None, :] + o + ga[None, :, None] * e1 + gb[None, :, None] * e2).reshape(-1, 3)
        XY.append((p[:, 0], -(p[:, 1] + K * (p[:, 2] - ground_z))))
        D.append(p[:, 1] - p[:, 2] / K)
        C.append(np.repeat(np.clip(col * shade, 0, 255).astype(np.uint8), len(ga), axis=0))
    xs = np.concatenate([a for a, b in XY])
    ys = np.concatenate([b for a, b in XY])
    return _splat((xs, ys), np.concatenate(D), np.concatenate(C), scale, bg, pad=1)
