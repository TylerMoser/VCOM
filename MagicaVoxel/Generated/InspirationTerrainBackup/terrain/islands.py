"""Whole small floating islands: an island rim style's pieces laid out as one
island (layout.place, as the level editor would), its rock hanging below in a
mass that tapers to a point, all as one complete model on the game's grid.

The underside hangs [depth] whole levels below the rim's own foot, so the model's
cells stay on the 16-voxel grid: the rim's tiles keep their levels, the underside
adds [depth] levels beneath them. How deep each column hangs grows with its
distance in from the island's edge (in plan, at the rim's foot), so the mass is
deepest under the middle and comes to a point; a fixed hash roughens it.
"""
import math

import kit
import layout
from families import hashf

# Each image's small islands: (name, rows as in layout.parse, levels of underside).
ISLANDS = {
    "poke_s": [("SmallIsland", [".##.", "####", "####", ".##."], 2),
               ("Islet", ["##", "##"], 2)],
    "poke_u": [("SmallIsland", [".###", "####", "###."], 2),
               ("Islet", ["##.", "###"], 2)],
}


def raw(style, rows, depth, cartoon):
    """The island's voxels as build() gives a piece's: (x, y, z) -> ref."""
    mask, tiles, extra = layout.parse(rows)
    H = len(rows)
    world = {}
    for (tx, ty) in sorted(mask):
        piece, q = layout.place(mask, extra, tx, ty)
        v = layout.turn_voxels(kit.build(style, piece, cartoon), q)
        for (x, y, z), ref in v.items():
            world[(16 * tx + x, 16 * ty + y, z)] = ref
    D = 16 * depth
    foot = {(x, y) for (x, y, z) in world if z == 0}
    # Distance in from the edge of the rim's foot, in plan (4-neighbour steps).
    dist = {p: 0 for p in foot if any((p[0] + dx, p[1] + dy) not in foot
                                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))}
    frontier = list(dist)
    while frontier:
        nxt = []
        for (x, y) in frontier:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                n = (x + dx, y + dy)
                if n in foot and n not in dist:
                    dist[n] = dist[(x, y)] + 1
                    nxt.append(n)
        frontier = nxt
    reach = max(dist.values()) if dist else 1
    out = {(x, y, z + D): ref for (x, y, z), ref in world.items()}
    for (x, y), d in dist.items():
        t = d / float(reach)
        rough = 0 if cartoon else int(hashf(x // 3, y // 3, 17) * 3)
        hang = min(D, int(round(D * math.pow(t, 0.75))) + rough)
        for k in range(hang):
            z = D - 1 - k
            share = k / float(max(1, hang))
            if cartoon:
                label = "rock_dark" if share > 0.6 else "rock"
            elif share > 0.85:
                label = "rock_line"
            elif share > 0.55:
                label = "rock_dark"
            else:
                label = "rock"
            out[(x, y, z)] = ("lab", label)
    W = max(len(r) for r in rows)
    size = (16 * W, 16 * H, 16 * (style.levels + 1) + D)
    return out, size
