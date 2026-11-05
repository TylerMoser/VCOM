"""new_2's hammock slung between two palms, as the sheet draws it, one model: the
fan palm (the same art as the sheet's single palm) on the left and the same palm
turned half round on the right (the sheet draws it mirrored), their trunks as far
apart as drawn, a cream net hanging between them from ropes tied round the trunks,
sagging to its middle, its mesh drawn in a darker diamond pattern. Cartoon: the
Cartoon palms, the net's sag and mesh exactly balanced end to end."""
import math


def hammock(palm_vox, palm_size, spacing, rgb_net, rgb_mesh, rgb_rope, cartoon=False, hang=None, sag=5, width=10):
    n, _, H = palm_size
    W = spacing + n
    out = {}
    # the left palm as made, the right turned half round about its own axis
    for (x, y, z), v in palm_vox.items():
        out[(x, y, z)] = v
        out[(spacing + (n - 1 - x), n - 1 - y, z)] = v
    C = n / 2.0
    x1, x2 = int(C) + 2, spacing + int(C) - 2
    hang = hang if hang is not None else max(6, int(H * 0.28))
    Cy = n / 2.0
    L = x2 - x1
    xm = (x1 + x2) / 2.0
    def sagged(x):
        t = (x - xm) / (L / 2.0)
        return int(round(hang - sag * (1 - t * t)))

    for x in range(x1, x2 + 1):
        t = (x - xm) / (L / 2.0)
        z = sagged(x)
        # where the net steps to the next column's height it is two voxels there, so
        # it is one piece face to face
        zs = sorted({z, sagged(x + 1) if x < x2 else z})
        # the net widens from the ends to its body
        w = width / 2.0 * min(1.0, (1 - abs(t)) * 3.0)
        for y in range(int(math.floor(Cy - w)), int(math.ceil(Cy + w))):
            if not (0 <= y < n):
                continue
            # a thin diamond lattice over the cream net, a cord along each edge
            k = (x - x1) + (y - int(Cy))
            mesh = (k % 6 == 0) or ((x - x1) - (y - int(Cy))) % 6 == 0
            edge = w >= 2.0 and abs(y + 0.5 - Cy) > w - 0.6
            for zz in zs:
                out[(x, y, zz)] = ("cloth", rgb_mesh if (mesh or edge) else rgb_net)
    # ropes from the net's ends round the trunks
    for xr in (x1, x2):
        for z in range(hang - 1, hang + 2):
            for y in (int(Cy) - 1, int(Cy)):
                out[(xr, y, z)] = ("rope", rgb_rope)
    if cartoon:
        full = {}
        for (x, y, z), v in out.items():
            if x <= (W - 1) / 2.0:
                full[(x, y, z)] = v
                full[(W - 1 - x, n - 1 - y, z)] = v
        out = full
    return out, (W, n, H)
