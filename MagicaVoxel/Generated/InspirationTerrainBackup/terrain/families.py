"""The families of terrain the images draw, each a Style: how its face stands out
(relief) and is coloured (texture), in an image's own colours and sizes.

relief(u, z, cartoon, face, piece) is how far the surface stands out of the
nominal face (outward, in voxels; it may be negative), u running along the face
and z up; texture(u, z, depth, cartoon, side, piece) names the label of a body
voxel [depth] inside the surface it shows. Every pattern repeats every 16 voxels
along a face, so that pieces join, and rounds to whole voxels the same way on
every piece. A style may add pieces of its own (extra): a waterfall, a cave mouth,
a drain, each on a base piece's plan (plans) with its own ground tiles (tops,
bottoms), finished by decorate().
"""
import math

import kit

PIECES = kit.PIECES


def jag(u, table):
    """A 16-periodic table lookup: the jagged edges the art draws."""
    return table[u % 16]


def hashf(*a):
    """A fixed hash in [0, 1) of integers, for scattering specks and stones."""
    n = 0x9E3779B1
    for v in a:
        n = ((n ^ (v & 0xFFFFFFFF)) * 0x85EBCA6B) & 0xFFFFFFFF
        n ^= n >> 13
    n = (n * 0xC2B2AE35) & 0xFFFFFFFF
    n ^= n >> 16
    return n / 4294967296.0


def segment(u, widths):
    """(index, position, width) of u in a 16-periodic run of segments [widths]."""
    assert sum(widths) == 16, widths
    k, acc = u % 16, 0
    for i, w in enumerate(widths):
        if k < acc + w:
            return i, k - acc, w
        acc += w


def bump(pos, w, height):
    """A rounded profile across a segment: [height] at its middle, 0 at its edges."""
    half = w / 2.0
    t = (pos + 0.5 - half) / max(half, 0.5)
    return max(0.0, height * (1 - t * t))


class Style:
    """A family's look in one image: its labels ({label: (RGB, group, crate class)}),
    the ground tiles on top of it and under it (output/ground's family names, or
    None), its height in levels and the face's set-back (inset), corner radius
    (radius) and concave fillet (r_in); extra pieces and their plans and tiles."""
    family = "Style"
    defaults = {}

    def __init__(self, source, name, levels, labels, top, bottom, inset=4, radius=4.0, r_in=1.5,
                 body_group="earth", flat=None, note="", extra=(), plans=None, tops=None, bottoms=None, **params):
        for k, v in self.defaults.items():
            params.setdefault(k, v)
        self.source, self.name, self.levels = source, name, levels
        self.labels, self.top, self.bottom = labels, top, bottom
        self.inset, self.radius, self.r_in = inset, radius, r_in
        self.body_group = body_group
        self.flat = flat or {}
        self.note = note
        self.extra = tuple(extra)
        self.plans = dict(plans or {})
        self.tops = dict(tops or {})
        self.bottoms = dict(bottoms or {})
        self.params = params
        for k, v in params.items():
            setattr(self, k, v)
        if top:
            surface = self.ground_group("surface", top)
            self.labels = {k: (rgb, surface if g == "surface" else g, c) for k, (rgb, g, c) in labels.items()}

    @property
    def pieces(self):
        return tuple(PIECES) + self.extra

    @property
    def ztop(self):
        return kit.TILE * (self.levels + 1) - 1

    @property
    def zface(self):
        """The lowest z of the face: over the lower ground, or the bottom of a body
        hanging free."""
        return kit.TILE if self.bottom else 0

    def plan_of(self, piece):
        return self.plans.get(piece, piece)

    def top_for(self, piece):
        return self.tops.get(piece, self.top)

    def bottom_for(self, piece):
        return self.bottoms.get(piece, self.bottom)

    def relief(self, u, z, cartoon, face, piece):
        return 0.0

    def fill_relief(self, x, y, z, cartoon, piece):
        return 0.0

    def texture(self, u, z, depth, cartoon, side, piece):
        return "fill"

    def decorate(self, piece, v, cartoon):
        pass

    def top_texture(self, x, y, z, cartoon, piece):
        """The label of a top the body makes itself (no ground tile on it)."""
        return "rim_light" if "rim_light" in self.labels else "fill"

    def ground_group(self, g, family):
        """The group a copied ground voxel belongs to here: a grass or water tile's
        surface is grass or water (which a rim's grass or a fall's water shares);
        any other group is its own tile's ("substrate:Meadow", "surface:Sand")."""
        kind = GROUND_KIND.get(family, "surface")
        if g == "surface":
            if kind in ("grass", "broadgrass"):
                return "grass"
            if kind in kit.WATER_KINDS:
                return "water"
        return "%s:%s" % (g, family.split("_Ground_")[-1])

    def _ground_flat(self, group, treatment, crate):
        """A ground tile's own flat colour for [group] (its grass, water or other
        surface), so that a rim or a fall merges with the tile it belongs to. The
        body's colour is never a tile's: a tile's substrate takes the body's."""
        if group == self.body_group:
            return None
        fams = [f for f in [self.top, self.bottom] + list(self.tops.values()) + list(self.bottoms.values()) if f]
        for family in fams:
            for p, (i, rgb, g) in kit.ground(family, treatment).items():
                if self.ground_group(g, family) == group:
                    return i if crate else rgb
        return None

    def flat_colour(self, group, treatment):
        """TwoColor: the one colour of [group]: a ground group's is its tile's own
        flat colour, the body's the style's (remembered: asked for every voxel)."""
        cache = self.__dict__.setdefault("_flat_cache", {})
        key = ("rgb", group, treatment)
        if key not in cache:
            cache[key] = self._flat_colour(group, treatment)
        return cache[key]

    def _flat_colour(self, group, treatment):
        got = self._ground_flat(group, treatment, False)
        if got is not None:
            return got
        if group in self.flat:
            return tuple(self.flat[group])
        return next(rgb for rgb, g, c in self.labels.values() if g == group)

    def flat_crate(self, group, treatment):
        cache = self.__dict__.setdefault("_flat_cache", {})
        key = ("crate", group, treatment)
        if key not in cache:
            cache[key] = self._flat_crate(group, treatment)
        return cache[key]

    def _flat_crate(self, group, treatment):
        got = self._ground_flat(group, treatment, True)
        if got is not None:
            return got
        rgb = self.flat_colour(group, treatment)
        cls = next(c for r, g, c in self.labels.values() if g == group)
        return min(kit.CRATE_CLASSES[cls], key=lambda i: (sum((kit.CRATE_RGBA[i - 1][j] - rgb[j]) ** 2
                                                             for j in range(3)), i))


GROUND_KIND = {r["name"]: r["kind"] for r in kit.GROUND["families"]}


class StripedCliff(Style):
    """The earth cliff most of the Pokémon maps draw: a face of rounded columns
    ([widths] across a tile, summing to 16, a dark crease after each), each bulging
    up to [bulge] voxels out, its top rounded [round_top] voxels down at its sides,
    lit at the top of the face ([light] of its height), shaded toward the foot
    ([dark] of it), a dark line under the rim if [under_line]; over it the grass of
    the top hangs out [rim] voxels, its jagged edge ([teeth], 16 entries) hanging
    down the face; the foot spreads [foot] voxels, its lowest [foot_h] voxels the
    foot's colour (poke_r's gray stone base). Cartoon: [cartoon_widths] columns,
    an even edge."""
    family = "StripedCliff"
    TEETH = [1, 2, 2, 1, 0, 1, 3, 2, 1, 1, 2, 0, 1, 2, 3, 1]
    defaults = dict(widths=(5, 4, 4, 3), cartoon_widths=(8, 8), bulge=1.0, round_top=1, light=0.35, dark=0.3,
                    under_line=True, rim=3, foot=2, teeth=None, cartoon_teeth=(1, 2), foot_h=1)

    def _teeth(self, u, cartoon):
        if cartoon:
            a, b = self.cartoon_teeth
            return a + (b - a) * ((u // 4) % 2)
        return jag(u, self.teeth or self.TEETH)

    def _shape(self, u, z, cartoon):
        ztop = self.ztop
        if z >= ztop - 2 - self._teeth(u, cartoon):
            return "rim", 0, 0
        i, pos, w = segment(u, self.cartoon_widths if cartoon else self.widths)
        if pos == w - 1:
            return "crease", pos, w
        side = min(pos, w - 2 - pos)
        drop = max(0, self.round_top - side) if not cartoon else (1 if side == 0 and self.round_top else 0)
        if z > ztop - 3 - drop:
            return "gap", pos, w
        return "column", pos, w

    def relief(self, u, z, cartoon, face, piece):
        zone, pos, w = self._shape(u, z, cartoon)
        if zone == "rim":
            return float(self.rim + (1 if cartoon else 0))
        r = 0.5 + bump(pos, w - 1, self.bulge) if zone == "column" else 0.0
        if z < self.zface + self.foot:
            r += 1.0
        return r

    def texture(self, u, z, depth, cartoon, side, piece):
        if depth > 1.6:
            return "fill"
        zone, pos, w = self._shape(u, z, cartoon)
        if zone == "rim":
            return "grass_edge"
        if z < self.zface + self.foot_h:
            return "face_foot"
        if zone in ("crease", "gap"):
            return "face_line"
        ztop = self.ztop
        t = (z - self.zface) / max(1, ztop - 3 - self.zface)
        if self.under_line and z == ztop - 3:
            return "face_line"
        centre = abs(pos + 0.5 - (w - 1) / 2.0) <= max(1.0, (w - 1) / 4.0)
        if t > 1 - self.light:
            return "face_light" if centre else "face"
        if t < self.dark:
            return "face_dark"
        return "face" if centre or cartoon else "face_dark"


class LumpyWall(Style):
    """A wall of rock in rounded lumps (caves, mountainsides, rock terraces, gully
    walls): [bumps] across a tile (summing to 16), each bulging [bulge] voxels out
    of a V-shaped crevice [crevice] deep, in [tiers] stacked courses (each its own
    row of lumps, a ledge of [ledge] voxels at its top), lit at the top of each
    course and shaded under it; its top a rounded rim of the rock itself, [rim_h]
    voxels and [rim] out ("rock"), or the grass of the top hanging over it
    ("grass"). Each course's lumps are offset [stagger] voxels from the one below;
    a course may have a lit top line (face_top) and a dark gap under it
    (course_gap) when the style has those labels. Cartoon: [cartoon_bumps] lumps,
    one shade fewer."""
    family = "LumpyWall"
    defaults = dict(bumps=(6, 5, 5), cartoon_bumps=(8, 8), bulge=1.5, crevice=0.5, tiers=1, ledge=1,
                    rim_kind="rock", rim_h=3, rim=2, foot=1, teeth=None, light=0.35, stagger=5)

    def _tier(self, z):
        """(tier index, height within it 0..1) of z on the face."""
        span = (self.ztop - 2 - self.rim_h) - self.zface
        n = max(1, self.tiers)
        k = min(n - 1, int((z - self.zface) * n / max(1, span)))
        lo = self.zface + k * span / n
        return k, (z - lo) / max(1.0, span / n)

    def _rim_zone(self, u, z, cartoon):
        if self.rim_kind == "grass":
            t = 1 + (0 if cartoon else jag(u, self.teeth or StripedCliff.TEETH) // 2)
            return z >= self.ztop - 2 - t
        return z >= self.ztop - 2 - self.rim_h

    def relief(self, u, z, cartoon, face, piece):
        if self._rim_zone(u, z, cartoon):
            return float(self.rim + (1 if cartoon else 0))
        k, t = self._tier(z)
        i, pos, w = segment(u + self.stagger * k, self.cartoon_bumps if cartoon else self.bumps)
        r = bump(pos, w, self.bulge) - self.crevice * (1 - min(1.0, bump(pos, w, 1.0) * 2))
        if self.tiers > 1 and t > 0.8:
            r += self.ledge
        if z < self.zface + self.foot:
            r += 1.0
        return r + 0.5

    def top_texture(self, x, y, z, cartoon, piece):
        """A top of the rock itself (poke_m's mountains): rounded lumps on the 16
        grid, lit in their middles, dark in the cracks between."""
        widths = self.cartoon_bumps if cartoon else self.bumps
        j, py, wy = segment(y + 3, widths)
        i, px, wx = segment(x + 5 * (j % 2), widths)
        shape = bump(px, wx, 1.0) * bump(py, wy, 1.0)
        return "rim_light" if shape > 0.3 else "rim"

    def decorate(self, piece, v, cartoon):
        super().decorate(piece, v, cartoon)
        band = getattr(self, "top_band", 0)
        if not band or not self.top:
            return
        # The rock's own top in a band round the edge of the grass (poke_l): the
        # grass's edge ragged, two voxels in and out.
        base = self.plan_of(piece)
        for (x, y, z), ref in list(v.items()):
            if z < self.ztop - 2 or ref[0] != "gnd":
                continue
            d, face = kit.plan(base, x, y, self.inset, self.radius, self.r_in)
            if face is None:
                continue
            u = kit.FACE_U[face](x, y)
            edge = band + (0 if cartoon else (jag(u, StripedCliff.TEETH) - 1.5) * 0.8)
            if d < edge:
                v[(x, y, z)] = ("lab", self.top_texture(x, y, z, cartoon, piece) if z == self.ztop else "rim")

    def texture(self, u, z, depth, cartoon, side, piece):
        if depth > 1.6:
            return "fill"
        if self._rim_zone(u, z, cartoon):
            if self.rim_kind == "grass":
                return "grass_edge"
            return "rim_light" if z >= self.ztop - 3 else "rim"
        if z < self.zface + 1:
            return "foot"
        k, t = self._tier(z)
        i, pos, w = segment(u + self.stagger * k, self.cartoon_bumps if cartoon else self.bumps)
        shape = bump(pos, w, 1.0)
        span = max(1.0, ((self.ztop - 2 - self.rim_h) - self.zface) / max(1, self.tiers))
        if self.tiers > 1 and "course_gap" in self.labels and t * span < 1.5:
            return "course_gap"
        if shape < 0.25:
            return "crevice"
        if "face_top" in self.labels and (1 - t) * span < 1.0 and shape > 0.3:
            return "face_top"
        if t > 1 - self.light:
            return "face_light" if shape > 0.6 else "face"
        if t < 0.3 and not cartoon:
            return "face_dark"
        return "face"


class StrataCliff(Style):
    """A cliff in horizontal beds ([bands], their heights in voxels from the foot up;
    whatever is left goes to the top bed): each bed's top edge stands a voxel out
    and is lit, its foot tucked in and dark, vertical joints every [joint] voxels
    staggered bed to bed; the grass of the top hanging over it ([rim] out).
    Cartoon: joints twice as far apart, only the top bed's edge lit."""
    family = "StrataCliff"
    defaults = dict(bands=(16, 16), joint=8, rim=3, foot=1)

    def _band(self, z):
        lo = self.zface
        top = self.ztop - 3
        for i, h in enumerate(self.bands):
            last = i == len(self.bands) - 1
            if z < lo + h or last:
                hi = top if last else min(lo + h, top)
                return i, z - lo, max(1, hi - lo)
            lo += h

    def _rim(self, u, z, cartoon):
        return z >= self.ztop - 2 - (0 if cartoon else jag(u, StripedCliff.TEETH) // 2)

    def relief(self, u, z, cartoon, face, piece):
        if self._rim(u, z, cartoon):
            return float(self.rim + (1 if cartoon else 0))
        i, h, H = self._band(z)
        r = 0.5
        if h >= H - 2:
            r += 1.0
        elif h <= 1:
            r -= 0.5
        if z < self.zface + self.foot:
            r += 1.0
        return r

    def texture(self, u, z, depth, cartoon, side, piece):
        if depth > 1.6:
            return "fill"
        if self._rim(u, z, cartoon):
            return "grass_edge"
        i, h, H = self._band(z)
        jw = min(16, self.joint * (2 if cartoon else 1))
        if (u + (jw // 2) * (i % 2)) % jw == 0 and 1 < h < H - 1:
            return "joint"
        if h >= H - 1 and (not cartoon or i == len(self.bands) - 1):
            return "band_light"
        if h <= 1:
            return "band_dark"
        return "band" if (i % 2 == 0 or cartoon) else "band_alt"


class EarthBank(Style):
    """The Pixelwood earth bank: a near-flat brown wall with darker blotches (on a
    fixed hash, [blotch] of it), a jagged dark band at its foot ([foot_teeth] tall)
    and a light band under the rim; the grass of the top hanging over it in round
    scallops [scallop] voxels wide ([rim] out). Cartoon: no blotches, an even foot."""
    family = "EarthBank"
    defaults = dict(blotch=0.18, foot_teeth=3, scallop=4, rim=3, light_h=1)

    def _dip(self, u, cartoon):
        s = self.scallop * (2 if cartoon else 1)
        k = (u % s) / s
        return 1 if not cartoon and abs(k - 0.5) > 0.35 else 0

    def relief(self, u, z, cartoon, face, piece):
        if z >= self.ztop - 3 - (1 - self._dip(u, cartoon)):
            return float(self.rim + (1 if cartoon else 0))
        return 0.5 + (0.5 if z < self.zface + 2 else 0.0)

    def texture(self, u, z, depth, cartoon, side, piece):
        if depth > 1.6:
            return "fill"
        if z >= self.ztop - 3 - (1 - self._dip(u, cartoon)):
            return "grass_edge"
        if self.ztop - 3 - self.light_h <= z <= self.ztop - 4:
            return "bank_light"
        if z == self.zface and "bank_line" in self.labels:
            return "bank_line"
        teeth = self.foot_teeth if cartoon else self.foot_teeth - 1 + (2 if (u // 2) % 3 == 0 else 0)
        if z < self.zface + teeth:
            return "bank_foot"
        if not cartoon and hashf((u % 16) // 4, (self.ztop - z) // 4, 7) < self.blotch:
            return "bank_dark"
        return "bank"


class IslandRim(Style):
    """The rim of a floating island: the grass of the top over a body of rock that
    hangs free below it in rows of pointed crags (each row [row_h] voxels, its crags
    [crags] across a tile, pointing down), each row tucked [tuck] voxels further in
    than the one above, each crag bulging [crag_bulge] voxels and lit in its top
    [lit] voxels, tapering to its point; no lower ground. A Fill tile of the island
    hangs as deep, flat beneath. Cartoon: [cartoon_crags] crags."""
    family = "IslandRim"
    defaults = dict(rows=2, row_h=16, crags=(6, 5, 5), cartoon_crags=(8, 8), tuck=2.0, rim=3, point=6,
                    crag_bulge=1.0, lit=3)

    def _row(self, z):
        below = (self.ztop - 3) - z
        return int(below // self.row_h), below % self.row_h

    def _rim(self, u, z, cartoon):
        return z >= self.ztop - 2 - (0 if cartoon else jag(u, StripedCliff.TEETH) // 2)

    def relief(self, u, z, cartoon, face, piece):
        if self._rim(u, z, cartoon):
            return float(self.rim + (1 if cartoon else 0))
        k, h = self._row(z)
        i, pos, w = segment(u + 4 * k, self.cartoon_crags if cartoon else self.crags)
        shape = bump(pos, w, 1.0)
        r = 1.0 - self.tuck * k + shape * self.crag_bulge
        tip = h - (self.row_h - self.point)
        if tip > 0:
            r -= tip * (1.2 - shape) * 0.8 * max(1.0, self.crag_bulge * 0.6)
        return max(r, -3.0)

    def texture(self, u, z, depth, cartoon, side, piece):
        if depth > 1.6:
            return "fill"
        if self._rim(u, z, cartoon):
            return "grass_edge"
        k, h = self._row(z)
        i, pos, w = segment(u + 4 * k, self.cartoon_crags if cartoon else self.crags)
        shape = bump(pos, w, 1.0)
        if shape < 0.2:
            return "rock_line"
        if h < self.lit:
            return "rock_light" if shape > 0.4 else "rock"
        if h > self.row_h - self.point:
            return "rock_dark"
        return "rock"


class MarioPlatform(Style):
    """Paper Mario's raised ground: a flat grass top with a pale rim line round its
    edge, a fringe of grass tongues ([tongue] across, [tongue_h] long, their tips
    dark) hanging over the soil face, a dark shadow under the fringe, the soil warm
    brown with small crosses every [cross] voxels, a darker band at its foot.
    Cartoon: tongues and crosses twice as far apart."""
    family = "MarioPlatform"
    defaults = dict(tongue=4, tongue_h=3, cross=8, rim=2)

    def _tongue(self, u, cartoon):
        t = self.tongue * (2 if cartoon else 1)
        k = u % t
        return self.tongue_h if 0 < k < t - 1 else self.tongue_h - 1

    def relief(self, u, z, cartoon, face, piece):
        if z >= self.ztop - 2 - self._tongue(u, cartoon):
            return float(self.rim + (1 if cartoon else 0))
        return 0.5

    def texture(self, u, z, depth, cartoon, side, piece):
        if depth > 1.6:
            return "fill"
        n = self._tongue(u, cartoon)
        if z >= self.ztop - 2 - n:
            return "fringe_dark" if z == self.ztop - 2 - n else "fringe"
        if z >= self.ztop - 4 - n:
            return "soil_shadow"
        if z < self.zface + 2:
            return "soil_dark"
        c = self.cross * (2 if cartoon else 1)
        cu, cz = u % c, (z - self.zface) % c
        if (cu == c // 2 and abs(cz - c // 2) <= 1) or (cz == c // 2 and abs(cu - c // 2) <= 1):
            return "soil_mark"
        return "soil"

    def decorate(self, piece, v, cartoon):
        super().decorate(piece, v, cartoon)
        # The pale rim line along the top's edge: top voxels with open air beside them
        # inside the tile.
        zt = self.ztop
        for (x, y, z) in [p for p in v if p[2] == zt]:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < 16 and 0 <= ny < 16 and (nx, ny, zt) not in v:
                    v[(x, y, z)] = ("lab", "rim_light")
                    break


class ZigzagTrim(Style):
    """Paper Mario's trimmed edge: a band [trim_h] voxels tall, light orange with dark
    red triangles ([zig] across) rising into it from its foot, under a light line; a dark line under
    it, then a dark teal wall with darker crosses every [cross] voxels down to the
    foot. Cartoon: triangles twice as wide."""
    family = "ZigzagTrim"
    defaults = dict(trim_h=10, zig=8, cross=8)

    def relief(self, u, z, cartoon, face, piece):
        if z >= self.ztop - 3 - self.trim_h:
            return 2.0 if cartoon else 1.0
        return 0.5

    def texture(self, u, z, depth, cartoon, side, piece):
        if depth > 1.6:
            return "fill"
        top = self.ztop - 3
        if z > top - 1:
            return "trim_light"
        if z >= top - self.trim_h:
            zz = self.zig * (2 if cartoon else 1)
            k = abs((u % zz) + 0.5 - zz / 2.0) * 2 / zz          # 1 at a triangle's foot corners
            h = (z - (top - self.trim_h)) / float(self.trim_h)     # 0 at the band's foot
            return "trim_dark" if h < 1 - k * 0.9 else "trim"
        if z == top - self.trim_h - 1:
            return "trim_line"
        c = self.cross * (2 if cartoon else 1)
        cu, cz = u % c, (z - self.zface) % c
        if (cu == c // 2 and abs(cz - c // 2) <= 1) or (cz == c // 2 and abs(cu - c // 2) <= 1):
            return "teal_dark"
        return "teal"


class FacetedCliff(Style):
    """A face of angular rock blocks (poke_c's gorge, poke_q's terraces): rows of
    blocks from the top of the face down ([rows], voxels tall, cycling), each row's
    blocks [blocks] wide (16-periodic, cycling row by row), each block standing
    out its own amount (up to [depth], a fixed hash), lit along its top [top_h]
    voxels and its left edge, shaded in its lowest [low_h], a dark crease along its
    bottom and right; the grass of the top hanging over it ([rim] out). Cartoon:
    rows twice as tall, two blocks a tile."""
    family = "FacetedCliff"
    defaults = dict(rows=(8, 10, 7), blocks=((7, 9), (5, 6, 5), (10, 6)), depth=1.6, top_h=1, low_h=3, rim=3,
                    foot=1, left_light=True)

    def _rim(self, u, z, cartoon):
        return z >= self.ztop - 2 - (0 if cartoon else jag(u, StripedCliff.TEETH) // 2)

    def _block(self, u, z, cartoon):
        dz = (self.ztop - 3) - z
        rows = tuple(2 * r for r in self.rows) if cartoon else self.rows
        k, acc = 0, 0
        while dz >= acc + rows[k % len(rows)]:
            acc += rows[k % len(rows)]
            k += 1
        h = rows[k % len(rows)]
        widths = (8, 8) if cartoon else self.blocks[k % len(self.blocks)]
        i, pos, w = segment(u + (4 * k if cartoon else 0), widths)
        return k, i, dz - acc, h, pos, w

    def relief(self, u, z, cartoon, face, piece):
        if self._rim(u, z, cartoon):
            return float(self.rim + (1 if cartoon else 0))
        k, i, pz, h, pos, w = self._block(u, z, cartoon)
        out = 0.0 if (pos == w - 1 or pz == h - 1) else self.depth * (0.35 + 0.65 * hashf(k % 6, i, 11))
        r = 0.5 + out
        if z < self.zface + self.foot:
            r += 1.0
        return r

    def top_texture(self, x, y, z, cartoon, piece):
        """A top of the rock itself (poke_o's outcrop): smooth and lit, as the art
        draws the tops of its slabs."""
        return "block_light" if "block_light" in self.labels else "block"

    def texture(self, u, z, depth, cartoon, side, piece):
        if depth > 1.6:
            return "fill"
        if self._rim(u, z, cartoon):
            return "grass_edge" if self.top else "block_top"
        if z < self.zface + 1:
            return "foot"
        k, i, pz, h, pos, w = self._block(u, z, cartoon)
        if pos == w - 1 or pz == h - 1:
            return "crease"
        if pz < self.top_h:
            return "block_top"
        if pz >= h - 1 - self.low_h and not cartoon:
            return "block_low"
        if pos == 0 and self.left_light and not cartoon:
            return "block_light"
        return "block"


class Masonry(Style):
    """A built stone face (retaining walls, raised beds): courses [course] voxels
    tall of blocks [block] long, staggered half a block, a recessed joint round
    each (staggered [stagger] voxels course to course, half a block unless given),
    every [light_every]th block a shade lighter, a few of another stone (stone_alt,
    stone_tan) where the style has them; a coping [coping] voxels tall standing
    [lip] out along the top, lit, unless the top's own ground is to show over it
    ([coping] 0). Cartoon: blocks and courses twice as big, one stone colour."""
    family = "Masonry"
    defaults = dict(course=4, block=8, coping=2, lip=1, stagger=None, light_every=3)

    def _coping(self, z):
        return self.coping and z >= self.ztop - 2 - self.coping

    def relief(self, u, z, cartoon, face, piece):
        if self._coping(z):
            return 0.5 + self.lip
        ch = self.course * (2 if cartoon else 1)
        bl = self.block * (2 if cartoon else 1)
        row = (z - self.zface) // ch
        joint = (z - self.zface) % ch == 0 or (u + self._shift(bl) * (row % 2)) % bl == 0
        return 0.0 if joint else 0.5

    def _shift(self, bl):
        return bl // 2 if self.stagger is None else self.stagger

    def texture(self, u, z, depth, cartoon, side, piece):
        if depth > 1.6:
            return "fill"
        if self._coping(z):
            return "coping"
        ch = self.course * (2 if cartoon else 1)
        bl = self.block * (2 if cartoon else 1)
        row = (z - self.zface) // ch
        joint = (z - self.zface) % ch == 0 or (u + self._shift(bl) * (row % 2)) % bl == 0
        if joint:
            return "joint"
        blk = (u + self._shift(bl) * (row % 2)) // bl
        if cartoon:
            return "stone"
        if "stone_alt" in self.labels and hashf(blk % (16 // bl or 1), row, 5) < 0.1:
            return "stone_alt"
        if "stone_tan" in self.labels and hashf(blk % (16 // bl or 1), row, 9) < 0.08:
            return "stone_tan"
        return "stone_light" if (blk + row) % self.light_every == 1 else "stone"


class StonyBank(Style):
    """A bank faced with rounded stones of several sizes: cells on the face (round
    [sites], 16-periodic), each bulging [bulge] out of a dark seam, lit at its top;
    the grass of the top over it ([rim] out), a dark band [foot_h] voxels tall at
    its foot when the style has a foot label. Cartoon: [cartoon_sites]."""
    family = "StonyBank"
    defaults = dict(sites=((3, 4), (10, 2), (14, 9), (6, 11), (1, 14), (11, 15), (8, 7)),
                    cartoon_sites=((4, 4), (12, 4), (4, 12), (12, 12)), bulge=1.2, rim=3, foot_h=3)

    def _cell(self, u, z, cartoon):
        sites = self.cartoon_sites if cartoon else self.sites
        zz = (z - self.zface) % 16
        ds = sorted((math.sqrt(min(abs(u % 16 - a), 16 - abs(u % 16 - a)) ** 2 + min(abs(zz - b), 16 - abs(zz - b)) ** 2), i)
                    for i, (a, b) in enumerate(sites))
        return ds[0][1], ds[0][0], ds[1][0] - ds[0][0]

    def _rim(self, u, z, cartoon):
        return z >= self.ztop - 2 - (0 if cartoon else jag(u, StripedCliff.TEETH) // 2)

    def relief(self, u, z, cartoon, face, piece):
        if self._rim(u, z, cartoon):
            return float(self.rim + (1 if cartoon else 0))
        i, d0, gap = self._cell(u, z, cartoon)
        if gap < 1.0:
            return 0.0
        return 0.5 + self.bulge * max(0.0, 1 - d0 / 5.0)

    def texture(self, u, z, depth, cartoon, side, piece):
        if depth > 1.6:
            return "fill"
        if self._rim(u, z, cartoon):
            return "grass_edge"
        if "foot" in self.labels and z < self.zface + self.foot_h:
            return "foot"
        i, d0, gap = self._cell(u, z, cartoon)
        if gap < 1.0:
            return "seam"
        sites = self.cartoon_sites if cartoon else self.sites
        return "stone_light" if (z - self.zface) % 16 > sites[i][1] + 1 else "stone"


class DrainMixin:
    """Gives a style a Drain piece: its straight face with a round-headed opening
    [drain_w] voxels wide and [drain_h] tall at its foot, framed by a ring of dressed
    stone ([ring] voxels, label arch) standing a voxel proud, barred (bars every
    third voxel and across the spring of the arch) and dark behind (drain_dark,
    [drain_d] voxels in)."""

    def decorate(self, piece, v, cartoon):
        super().decorate(piece, v, cartoon)
        if piece != "Drain":
            return
        F = self.inset
        w, h = getattr(self, "drain_w", 10), getattr(self, "drain_h", 12)
        ring, deep = getattr(self, "ring", 2), getattr(self, "drain_d", 8)
        r = w / 2.0
        z0 = self.zface
        head = z0 + h - r

        def inside(dx, z, grow):
            rr = r + grow
            return dx <= rr and (z <= head or dx * dx + (z - head) ** 2 <= rr * rr)

        for x in range(16):
            dx = abs(x + 0.5 - 8)
            for z in range(z0, z0 + h + ring + 2):
                if inside(dx, z, 0):
                    for y in range(0, F + deep):
                        if (x, y, z) in v and v[(x, y, z)][0] == "lab":
                            del v[(x, y, z)]
                    v[(x, F + deep, z)] = ("lab", "drain_dark")
                    if (x % 3 == 1 or abs(z - round(head)) == 0) and z < z0 + h:
                        v[(x, F + 1, z)] = ("lab", "bars")
                elif inside(dx, z, ring):
                    for y in range(F - 1, F + 2):
                        v[(x, y, z)] = ("lab", "arch")


class NotchMixin:
    """Gives a style a Notch piece (poke_l's gully notch): its straight face with a
    V-shaped cleft cut down it from the top to the foot, [notch_w] voxels wide at
    the face narrowing to nothing [notch_d] voxels back, its walls dark (crevice),
    the lower ground showing at its floor."""

    def decorate(self, piece, v, cartoon):
        super().decorate(piece, v, cartoon)
        if piece != "Notch":
            return
        F = self.inset
        w, deep = getattr(self, "notch_w", 10), getattr(self, "notch_d", 10)

        def half(y):
            return (w / 2.0) * min(1.0, max(0.0, 1 - (y + 0.5 - F) / deep))

        for (x, y, z) in list(v):
            if z >= self.zface and abs(x + 0.5 - 8) < half(y):
                del v[(x, y, z)]
        for (x, y, z), ref in list(v.items()):
            if z < self.zface or ref[0] != "lab":
                continue
            for dx in (-1, 1):
                if abs(x + dx + 0.5 - 8) < half(y) and (x + dx, y, z) not in v:
                    v[(x, y, z)] = ("lab", "crevice")
                    break


class WaterfallMixin:
    """Gives a style a Fall piece: its straight face with the river at its top
    (tops["Fall"], a water tile) pouring over the rim in a sheet [sheet] voxels
    thick down the face into the pool below (bottoms["Fall"]), streaked lighter
    down it (or in bands across it, [bands] "across"; white lines with drips, as
    poke_c's cascades, with [foam_lines]), foaming white over a lip [lip] voxels
    deep and where it lands, spreading foam on the pool. A NarrowFall piece is a
    spring: the style's own top, with a stream [fall_w] voxels wide rising a few
    voxels back from the edge and falling down the middle of the face into its
    pool (bottoms["NarrowFall"])."""

    def decorate(self, piece, v, cartoon):
        super().decorate(piece, v, cartoon)
        if piece not in ("Fall", "NarrowFall"):
            return
        F = self.inset
        surface = self.ztop - 2
        # The pool is the lower tile's surface: the foam lies on it. Off a floating
        # rim (no ground below) the water falls to the piece's foot and ends in mist
        # there: no pool.
        has_pool = bool(self.bottom_for(piece))
        pool = kit.under_top(self, piece, 0, 0, cartoon) + 1 if has_pool else 0
        sheet = getattr(self, "sheet", 2)
        lip = getattr(self, "lip", 0)
        front = F - sheet - 1
        if piece == "Fall":
            xs, back = range(16), F + 4
        else:
            w = getattr(self, "fall_w", 6)
            xs, back = range(8 - w // 2, 8 - w // 2 + w), F + 6
        every = getattr(self, "band_every", 12)
        for x in xs:
            for y in range(front, back):
                for z in range(surface - 1, surface + 1):
                    v[(x, y, z)] = ("lab", "water")
                if piece == "NarrowFall":
                    # the stream sits a voxel down in its bed
                    v.pop((x, y, surface + 2), None)
                    v.pop((x, y, surface + 1), None)
            hang = lip + (0 if cartoon else (1 if x % 4 in (1, 2) else 0)) if lip else 0
            for z in range(pool, surface - 1):
                if getattr(self, "bands", None) == "across":
                    streak = (surface - z) % every < (3 if not cartoon else 4)
                else:
                    streak = (x % 3 == 0) if not cartoon else (x % 8 == 3)
                label = "foam" if z < pool + 3 or z >= surface - 1 - hang else ("water_light" if streak else "water")
                if getattr(self, "foam_lines", False) and getattr(self, "bands", None) == "across":
                    k = (surface - z) % every
                    if k == 0 or (k == 1 and (x % 2 == 0 or cartoon)):
                        label = "foam"
                for y in range(front, F - 1):
                    v[(x, y, z)] = ("lab", label)
            for y in range(0, front):
                if has_pool and (cartoon or hashf(x, y, 3) < (0.85 if y > 0 else 0.45)):
                    v[(x, y, pool)] = ("lab", "foam")
        if piece == "NarrowFall" and has_pool:
            # foam spreading on the pool either side of the stream's foot
            lo, hi = xs[0], xs[-1]
            for x in (lo - 2, lo - 1, hi + 1, hi + 2):
                if 0 <= x < 16:
                    for y in range(0, front):
                        if cartoon or hashf(x, y, 4) < 0.5:
                            v[(x, y, pool)] = ("lab", "foam")


class CaveMouthMixin:
    """Gives a style a CaveMouth piece (or, in masonry, an Archway): its straight face
    with a round-headed opening [mouth_w] voxels wide and [mouth_h] tall at its
    foot, going [mouth_d] voxels back into the rock to a dark end (cave_dark), the
    lower ground carried in as its floor."""

    def decorate(self, piece, v, cartoon):
        super().decorate(piece, v, cartoon)
        if piece not in ("CaveMouth", "Archway"):
            return
        F = self.inset
        r = self.mouth_w / 2.0
        z0 = self.zface
        head = z0 + self.mouth_h - r
        for x in range(16):
            dx = abs(x + 0.5 - 8)
            for z in range(z0, z0 + self.mouth_h + 1):
                if not (dx <= r and (z <= head or dx * dx + (z - head) ** 2 <= r * r)):
                    continue
                for y in range(0, F + self.mouth_d):
                    if (x, y, z) in v and v[(x, y, z)][0] == "lab":
                        del v[(x, y, z)]
                v[(x, F + self.mouth_d, z)] = ("lab", "cave_dark")
            for y in range(F, F + self.mouth_d + 1):
                for z in range(z0, z0 + self.mouth_h + 2):
                    if dx <= r + 1 and (x, y, z) in v and v[(x, y, z)][0] == "lab":
                        v[(x, y, z)] = ("lab", "cave_dark")


def with_extras(cls, *mixins):
    """A family class with extra pieces' mixins (waterfall, cave mouth)."""
    name = cls.__name__ + "".join(m.__name__.replace("Mixin", "") for m in mixins)
    return type(name, tuple(mixins) + (cls,), {"family": cls.family})
