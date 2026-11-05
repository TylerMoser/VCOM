"""Builds new_2's families: build(spec) -> (Base build, Cartoon build), each
({(x, y, z): (material, rgb)}, size); copies are made by treatments.copy_family."""
import math

import numpy as np

import sculpt_clumps
import sculpt_hammock
import sculpt_hedge
import sculpt_palm
import sculpt_plants as P
from catalogue_new2 import BOXES
from recolour import recolour
from sculpt_tree import SpriteTree
from sprites import ROOT, Sprite

IMAGE = "new_2.jpg"
_sprites = {}
# sprites drawn as separate pieces: every part of them is kept
SCATTERED = {"FloatingLilyPads", "HammockPalms", "WindBlownBlades", "GrassTuft_A", "GrassTuft_B", "GrassTuft_A2",
             "FloweringTuft", "Hedge_Field3x3", "Hedge_Interior2x2"}


def sprite(name):
    if name not in _sprites:
        _sprites[name] = Sprite(IMAGE, BOXES[name], keep_main=name not in SCATTERED)
    return _sprites[name]


def build(spec):
    k = spec["kind"]
    if k == "tree":
        geo = sprite(spec["geo"])
        paint = sprite(spec["paint"]) if spec.get("paint") else None
        vs = sprite(spec["vines_sprite"]) if spec.get("vines_sprite") else None
        t = SpriteTree(geo, paint=paint, vines_sprite=vs)
        return t.base(), t.cartoon()
    if k == "recolour":
        sp = sprite(spec["sprite"])
        model = ROOT / "output" / spec["model"]
        base = recolour(str(model) + ".vox", str(model) + "_TwoColor.vox", sp)
        cart = recolour(str(model) + "_Cartoon.vox", str(model) + "_Cartoon_TwoColor.vox", sp)
        return base, cart
    if k == "palm":
        p = sculpt_palm.Palm(sprite(spec["sprite"]))
        return p.build(False), p.build(True)
    if k == "hammock":
        p = sculpt_palm.Palm(sprite(spec["sprite"]))
        left, right = sprite(spec["left"]), sprite(spec["right"])
        lp, rp = sculpt_palm.Palm(left), sculpt_palm.Palm(right)
        bl, br = BOXES[spec["left"]], BOXES[spec["right"]]
        spacing = int(round((br[0] + rp.cx) - (bl[0] + lp.cx)))
        # the net's colours, from the raw image between the palms (its cream is pale
        # enough that the sprite mask takes it for the sheet's white): cream, and the
        # grey-brown of its lattice
        from sprites import image as raw_image
        im = raw_image(IMAGE)
        bx = BOXES[spec["box"]]
        reg = im[bx[1]:bx[3], bx[0] + int(lp.cx + p.reach * 0.75):bx[0] + int(spacing + lp.cx - p.reach * 0.75)]
        reg = reg.reshape(-1, 3).astype(int)
        lum = reg @ np.array([0.299, 0.587, 0.114])
        spread = reg.max(axis=1) - reg.min(axis=1)
        cream = reg[(lum > 205) & (lum < 249) & (spread < 40)]
        lattice = reg[(lum > 115) & (lum < 185) & (spread < 40)]
        net = tuple(int(v) for v in (np.median(cream, axis=0) if len(cream) else (240, 232, 222)))
        mesh = tuple(int(v) for v in (np.median(lattice, axis=0) if len(lattice) else (150, 140, 130)))
        rope = (150, 112, 74)
        out = []
        for cartoon in (False, True):
            pv, ps = p.build(cartoon)
            # the net tied round the trunks just under their tops, where the fronds
            # leave them, as drawn
            hang = p.H - 1 - min(p.trunk) - 1
            out.append(sculpt_hammock.hammock(pv, ps, spacing, net, mesh, rope, cartoon=cartoon,
                                              hang=hang, sag=4, width=10))
        return out[0], out[1]
    if k == "blades":
        sp = sprite(spec["sprite"])
        return P.blades(sp, False, **spec["args"]), P.blades(sp, True, **spec["args"])
    if k == "lobes":
        sp = sprite(spec["sprite"])
        return P.lobes(sp, False, **spec["args"]), P.lobes(sp, True, **spec["args"])
    if k == "pads":
        sp = sprite(spec["sprite"])
        args = dict(spec["args"])
        if "exclude_box" in args:
            eb = BOXES[args.pop("exclude_box")]
            b = BOXES[spec["sprite"]]
            args["exclude"] = (eb[0] - b[0], eb[1] - b[1], eb[2] - b[0], eb[3] - b[1])
        return P.pads(sp, False, **args), P.pads(sp, True, **args)
    if k == "cactus":
        sp = sprite(spec["sprite"])
        return P.cactus(sp, False, **spec["args"]), P.cactus(sp, True, **spec["args"])
    if k == "stump":
        sp = sprite(spec["sprite"])
        return P.root_stump(sp, False), P.root_stump(sp, True)
    if k == "clumps":
        sp = sprite(spec["sprite"])
        return sculpt_clumps.clumps(sp, False, **spec["args"]), sculpt_clumps.clumps(sp, True, **spec["args"])
    if k == "fern":
        sp = sprite(spec["sprite"])
        return sculpt_clumps.fern(sp, False), sculpt_clumps.fern(sp, True)
    if k == "hedge":
        h = sculpt_hedge.Hedge(sprite(spec["sprite"]), sprite(spec["interior"]))
        return h.build(spec["piece"], False), h.build(spec["piece"], True)
    raise ValueError(k)
