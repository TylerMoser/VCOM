"""How MapCreation/WorldMapV1.png maps on to the in-game art: fit and check."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage, optimize

Image.MAX_IMAGE_PIXELS = None
ROOT = sys.argv[1]
creation = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
art_mask = np.asarray(Image.open(ROOT + "/vcom/WorldMap/WorldMapV1LandMask.png").convert("L")) > 127
c_land = (creation[..., 0] >= 250) & (creation[..., 1] >= 250) & (creation[..., 2] >= 250)
ch, cw = c_land.shape
ah, aw = art_mask.shape

def moments(mask):
    ys, xs = np.nonzero(mask)
    cx, cy = xs.mean(), ys.mean()
    dx, dy = xs - cx, ys - cy
    return cx, cy, (dx * dx).mean(), (dy * dy).mean(), (dx * dy).mean(), mask.sum()

mc = moments(c_land)
ma = moments(art_mask)
print("creation land: centroid (%.2f, %.2f) var x %.1f var y %.1f cov %.1f area %d" % mc)
print("art land:      centroid (%.2f, %.2f) var x %.1f var y %.1f cov %.1f area %d" % ma)
sx0 = np.sqrt(mc[2] / ma[2]); sy0 = np.sqrt(mc[3] / ma[3])
print("scale from spread: x %.5f  y %.5f; area ratio %.5f vs product %.5f" % (sx0, sy0, mc[5] / ma[5], sx0 * sy0))
print("correlation: creation %.4f  art %.4f" % (mc[4] / np.sqrt(mc[2] * mc[3]), ma[4] / np.sqrt(ma[2] * ma[3])))

# Resample the art mask into the creation frame under an affine and score the overlap.
yy, xx = np.mgrid[0:ch, 0:cw]
def iou(params, full=False):
    sx, sy, tx, ty, shear_x, shear_y = params
    # creation (x, y) -> art (u, v)
    u = (xx - tx) / sx + shear_x * (yy - ty) / sy
    v = (yy - ty) / sy + shear_y * (xx - tx) / sx
    ui = np.clip(np.rint(u).astype(np.int64), 0, aw - 1)
    vi = np.clip(np.rint(v).astype(np.int64), 0, ah - 1)
    inside = (u >= 0) & (u < aw) & (v >= 0) & (v < ah)
    sampled = art_mask[vi, ui] & inside
    inter = (sampled & c_land).sum()
    union = (sampled | c_land).sum()
    return inter / union

tx0 = mc[0] - ma[0] * sx0
ty0 = mc[1] - ma[1] * sy0
start = np.array([sx0, sy0, tx0, ty0, 0.0, 0.0])
print("start: scale (%.5f, %.5f) offset (%.2f, %.2f)  IoU %.5f" % (sx0, sy0, tx0, ty0, iou(start)))
result = optimize.minimize(lambda p: -iou(p), start, method="Powell",
                           options={"xtol": 1e-5, "ftol": 1e-7, "maxfev": 400})
best = result.x
print("fitted: scale x %.5f y %.5f  offset (%.2f, %.2f)  shear %.5f %.5f  IoU %.5f" % (*best, -result.fun))
# With no shear at all, for comparison.
plain = optimize.minimize(lambda p: -iou(np.array([p[0], p[1], p[2], p[3], 0.0, 0.0])), start[:4], method="Powell",
                          options={"xtol": 1e-5, "ftol": 1e-7, "maxfev": 300})
print("no shear: scale x %.5f y %.5f  offset (%.2f, %.2f)  IoU %.5f" % (*plain.x, -plain.fun))
uniform = optimize.minimize(lambda p: -iou(np.array([p[0], p[0], p[1], p[2], 0.0, 0.0])),
                            np.array([np.sqrt(sx0 * sy0), tx0, ty0]), method="Powell",
                            options={"xtol": 1e-5, "ftol": 1e-7, "maxfev": 300})
print("uniform scale only: scale %.5f offset (%.2f, %.2f)  IoU %.5f" % (*uniform.x, -uniform.fun))
print("ratio of x scale to y scale: %.4f" % (plain.x[0] / plain.x[1]))
print("art px per creation px: x %.4f  y %.4f" % (1 / plain.x[0], 1 / plain.x[1]))
