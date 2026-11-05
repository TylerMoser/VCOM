"""new_1's props, sculpted to measurements read off the image (see new1_sculpt's
notes): the woodpile beside the house and the chopping stump with its axe. Each
builder returns ({(x, y, z): (material, rgb)}, (sx, sy, sz)), standing on z 0;
+y is the back (up the image), -y the front.

Props have a front, so Cartoon is mirror-symmetric across x's middle (the axe in
that plane), not quarter-turn symmetric."""
import math

from new1_sculpt import LIGHT, _mirror1
from sculpt_tree import connected_main

WOOD = dict(top=(238, 201, 166), log=(228, 157, 110), log_shade=(184, 120, 85), groove=(110, 72, 51),
            ring_a=(227, 154, 108), ring_b=(184, 114, 86), heart=(150, 83, 59), board=(239, 202, 166),
            board_shade=(211, 157, 123), board_edge=(161, 103, 75))


def woodpile(cartoon=False):
    """The woodpile beside the house: three logs stripped of their bark lying side
    by side, their length running back from the viewer, their cut ends ringed, and
    two boards laid across them, the boards hanging over the pile's left side, as
    drawn. 26 x 20 x 9."""
    nx, ny = 26, 20
    Cx, Cy = nx / 2.0, ny / 2.0
    w = WOOD
    out = {}
    R, half = 3.45, 9.5
    for lx in (-7.0, 0.0, 7.0):
        for x in range(nx):
            for y in range(ny):
                dy = y + 0.5 - Cy
                if abs(dy) > half:
                    continue
                for z in range(9):
                    dx, dz = x + 0.5 - Cx - lx, z + 0.5 - R
                    d = math.hypot(dx, dz)
                    if d > R + 0.15:
                        continue
                    end = abs(dy) > half - 1.0
                    if end:
                        # its cut end: rings round a dark heart
                        if d < 0.9:
                            col = w["heart"]
                        elif d > R - 0.6:
                            col = w["groove"]
                        elif cartoon:
                            col = w["ring_a"]
                        else:
                            col = w["ring_a"] if int(d / 1.0) % 2 == 0 else w["ring_b"]
                    else:
                        nxl, nzl = dx / max(d, 1e-6), dz / max(d, 1e-6)
                        if cartoon:
                            col = w["log"] if nzl > -0.2 else w["log_shade"]
                        else:
                            lit = nxl * LIGHT[0] + nzl * LIGHT[2]
                            col = w["top"] if lit > 0.9 else (w["log"] if lit > -0.1 else w["log_shade"])
                            if d > R - 0.7 and nzl < -0.55:
                                col = w["groove"]
                    out[(x, y, z)] = ("wood", col)
    # the two boards across the logs
    for by in (3.5, -0.5):
        x_lo, x_hi = (-11.5, 11.5) if cartoon else (-12.6, 10.8)
        for x in range(nx):
            for y in range(ny):
                dx, dy = x + 0.5 - Cx, y + 0.5 - Cy - by
                if x_lo <= dx <= x_hi and abs(dy) <= 1.5:
                    for z in (7, 8):
                        if z == 8:
                            col = w["board"] if (cartoon or dy > -0.6) else w["board_shade"]
                        else:
                            col = w["board_edge"]
                        out[(x, y, z)] = ("wood", col)
    out = {p: v for p, v in out.items() if 0 <= p[0] < nx and 0 <= p[1] < ny}
    if cartoon:
        out = _mirror1(out, nx)
    return connected_main(out), (nx, ny, 9)


STUMP = dict(top=(224, 153, 110), ring=(200, 130, 90), heart=(173, 103, 70), crack=(120, 70, 50),
             bark=(107, 55, 47), bark_light=(150, 82, 60), bark_dark=(66, 47, 38), rim=(209, 134, 92))
AXE = dict(steel=(151, 163, 184), edge=(200, 205, 218), eye=(86, 92, 110), handle=(160, 95, 70),
           handle_dark=(110, 60, 45))


def stump_axe(cartoon=False):
    """The chopping stump beside the house: a broad cut stump, its top ringed with
    a crack across it and its sides cracked bark, flaring a little at its foot; an
    axe stuck in its top at the back-left, the blade buried, the handle leaning up
    and out to the back-left, as drawn. Cartoon: the axe stuck at the back in the
    stump's middle plane, its handle leaning straight back."""
    n = 24
    C = n / 2.0
    s = STUMP
    out = {}
    R, H = 9.8, 10
    for x in range(n):
        for y in range(n):
            dx, dy = x + 0.5 - C, y + 0.5 - C
            d = math.hypot(dx, dy)
            ang = math.atan2(dy, dx)
            for z in range(H):
                r = R + (0.9 if z == 0 else (0.45 if z == 1 else 0.0))
                if d > r + 0.2:
                    continue
                if z == H - 1:
                    if d < 1.1:
                        col = s["heart"]
                    elif d > R - 0.8:
                        col = s["rim"]
                    elif cartoon:
                        col = s["top"] if int(d / 2.5) % 2 == 0 else s["ring"]
                    else:
                        col = s["top"] if int(d / 1.5) % 2 == 0 else s["ring"]
                        # a crack from the heart to the rim, toward the front right
                        if abs(math.sin(ang - math.radians(-55))) * d < 0.6 and math.cos(ang - math.radians(-55)) > 0 \
                                and d > 1.5:
                            col = s["crack"]
                    out[(x, y, z)] = ("cut", col)
                elif d > r - 0.9:
                    if cartoon:
                        col = s["bark"]
                        cracks = [math.radians(a) for a in (-45, -135, 45, 135)]
                    else:
                        lit = (dx * LIGHT[0] + dy * LIGHT[1]) / max(d, 1e-6)
                        col = s["bark_light"] if lit > 0.45 else s["bark"]
                        cracks = [math.radians(a) for a in (-80, -30, 20, 75, 140, 200, 250)]
                    if any(abs(math.sin(ang - c)) * d < 0.55 and math.cos(ang - c) > 0 for c in cracks) and z < H - 2:
                        col = s["bark_dark"]
                    out[(x, y, z)] = ("wood", col)
                else:
                    out[(x, y, z)] = ("wood", s["bark"])
    # the axe: its handle direction, the blade below its eye, a wedge two voxels thick
    if cartoon:
        Hd = (0.0, 0.55, 0.835)
        E = (0.0, 2.5, H + 2.6)
    else:
        Hd = (-0.55, 0.30, 0.78)
        E = (-2.6, 2.6, H + 2.6)
    m = math.sqrt(sum(v * v for v in Hd))
    Hd = tuple(v / m for v in Hd)
    hh = math.hypot(Hd[0], Hd[1])
    Hh = (Hd[0] / hh, Hd[1] / hh)
    P = (Hd[2] * Hh[0], Hd[2] * Hh[1], -hh)              # down from the eye, in the handle's plane
    N = (-Hh[1], Hh[0], 0.0)                             # across the blade
    if cartoon:
        P = (0.0, -abs(P[1]) if False else P[1], P[2])
    for i in range(int(8 * 3) + 1):
        a = i / 3.0                                      # out along P, to the edge
        span = 3.6 - 0.2 * a                            # along the handle, narrowing a little
        j = -span
        while j <= span + 1e-6:
            for k in (-0.5, 0.5):
                thick_ok = a < 6.4 or abs(k) < 0.6
                if not thick_ok:
                    continue
                px = E[0] + P[0] * a + Hd[0] * j + N[0] * k
                py = E[1] + P[1] * a + Hd[1] * j + N[1] * k
                pz = E[2] + P[2] * a + Hd[2] * j
                q = (int(math.floor(C + px)), int(math.floor(C + py)), int(math.floor(pz)))
                if a < 1.2:
                    col = AXE["eye"]
                elif a > 6.5:
                    col = AXE["edge"]
                else:
                    col = AXE["steel"]
                out[q] = ("metal", col)
            j += 0.34
    for i in range(int(12 * 3) + 1):
        t = i / 3.0 - 1.0
        px, py, pz = E[0] + Hd[0] * t, E[1] + Hd[1] * t, E[2] + Hd[2] * t
        for (ox, oy) in ((0.0, 0.0), (0.5, 0.0), (0.0, 0.5), (0.5, 0.5)):
            q = (int(math.floor(C + px + ox - 0.25)), int(math.floor(C + py + oy - 0.25)), int(math.floor(pz)))
            if q not in out or out[q][0] != "metal":
                lit = (ox - 0.25) * LIGHT[0] + (oy - 0.25) * LIGHT[1] > 0
                out[q] = ("wood", AXE["handle"] if (cartoon or lit) else AXE["handle_dark"])
    out = {p: v for p, v in out.items() if 0 <= p[0] < n and 0 <= p[1] < n and p[2] >= 0}
    out = connected_main(out)
    if cartoon:
        out = _mirror1(out, n)
    return out, (n, n, max(z for (x, y, z) in out) + 1)
