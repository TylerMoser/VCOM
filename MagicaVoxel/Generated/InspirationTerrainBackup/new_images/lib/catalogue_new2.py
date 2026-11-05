"""Every element of new_2.jpg, the vegetation sprite sheet, as a family: what it
is, the sprite it is read from (boxes in boxes_new2.json, the sheet's pixels), the
sculptor that makes it, and what it shares with others (the sheet draws many trees
twice, a lighter and a darker colourway of one drawing: those share one geometry,
each painted from its own sprite).

Repeated sprites are one family: the mirrored twin sapling, the second dark oval
tree, the second broad-crown tree, the second scraggly tree. Same art as an earlier
image's model: the fallen log and the small stump are poke_g's (copied whole, the
same colours), the layered tree, the rounded tree and the sapling poke_l's
(their geometry, in this sheet's colours)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOXES = json.loads((HERE / "boxes_new2.json").read_text())

F = []


def fam(name, kind, what, **kw):
    F.append(dict(name=name, kind=kind, what=what, **kw))


# trees and bushes sculpted from their sprites (geometry from geo; paint from paint)
for name, what in [
    ("DomeBushSmall", "a low round bush"),
    ("ColumnTree", "a slender column-crowned tree on a short trunk"),
    ("TwinSapling", "a small sapling with a parted crown on a short trunk (drawn twice, once mirrored)"),
    ("LollipopTree", "a round crown on a long thin grey trunk"),
    ("NarrowConeTree", "a narrow conifer of rounded tiers"),
    ("TieredConeTree", "a narrow pointed conifer of layered tiers"),
    ("DomeBushLarge_A", "a large dome bush"),
    ("DomeBushLarge_B", "a large round bush raised on its roots"),
    ("EggBush", "a small upright egg-shaped bush"),
    ("DarkDomeBush", "a small dark dome bush"),
    ("PointedDomeTree", "a round tree with a pointed top"),
    ("CloudBush", "a broad bush of flat-topped cloud-like clumps"),
    ("LeafyRoundBush", "a round leafy bush"),
    ("SpeckledRoundBush", "a round bush with pale specks"),
    ("RootedRoundTree", "a small round tree on spreading roots"),
    ("ConeDomeTree", "a cone-topped dome tree"),
    ("MushroomCrownTree", "a wide dome crown on a short thick trunk"),
    ("TallLayeredTree", "a tall pointed tree of layered leaves"),
    ("ScragglyTree", "a ragged round tree with its branches showing"),
    ("DarkOvalTree", "a dark pointed oval tree (drawn twice)"),
    ("BroadCrownTree", "a dark pointed broad-crowned tree (drawn twice)"),
    ("LeafyFernClump", "a small upright leafy clump"),
]:
    fam(name, "tree", what, geo=name)


def _recast(name, kind, what, **kw):
    """Gives a family above another sculptor, keeping its place in the list."""
    f = next(f for f in F if f["name"] == name)
    f.clear()
    f.update(dict(name=name, kind=kind, what=what, **kw))


# Plants of a few big round parts, read off the sprite by eye: (across, depth,
# height, radius across, radius up) in voxels from the trunk's foot; the Cartoon's
# evenly placed. The cloud bush: four puffs in a ring (the left, right and front
# ones drawn, the back one hidden behind the top one) and one over the middle; the
# sapling: the two clumps drawn left and right on a forked trunk, and two the
# side view shows, front and back.
_recast("CloudBush", "clumps", "a broad bush of five flat-topped cloud-like puffs on a short trunk",
        sprite="CloudBush", args=dict(
            puffs=[(-11.5, 0, 17, 13.5, 9.5), (12, 0, 16, 12, 9), (0, -11.5, 15.5, 13.5, 9.5),
                   (0, 11.5, 18, 13, 9.5), (-3, 2, 27, 14, 9.5)],
            cartoon_puffs=[(-11.5, 0, 16.5, 13.5, 9.5), (11.5, 0, 16.5, 13.5, 9.5), (0, -11.5, 16.5, 13.5, 9.5),
                           (0, 11.5, 16.5, 13.5, 9.5), (0, 0, 27, 14, 9.5)],
            trunk_top=9, trunk_r=3.5, flare=1.5, strokes=True))
_recast("TwinSapling", "clumps", "a small sapling forking into round leaf clumps (drawn twice, once mirrored)",
        sprite="TwinSapling", args=dict(
            puffs=[(-3.6, 0, 14.2, 4.1, 3.9), (3.6, 0, 11.8, 4.0, 3.7), (0, -3.6, 12.6, 3.9, 3.7),
                   (0, 3.6, 13.4, 4.0, 3.8)],
            cartoon_puffs=[(-3.6, 0, 13, 4.0, 3.8), (3.6, 0, 13, 4.0, 3.8), (0, -3.6, 13, 4.0, 3.8),
                           (0, 3.6, 13, 4.0, 3.8)],
            trunk_top=9, trunk_r=2.0, flare=2.0, strokes=False))
_recast("LeafyFernClump", "fern", "a small upright fern of broad lobed fronds", sprite="LeafyFernClump")

for base, what in [
    ("BranchedOak", "a spreading oak of big clumps on a branched trunk"),
    ("Spruce", "a layered spruce"),
    ("SmallFir", "a small round fir"),
    ("NarrowSpruce", "a narrow spruce"),
    ("RoundTree", "a round bushy tree"),
    ("BigRoundTree", "a big round tree"),
    ("PointedRoundTree", "a round tree with a pointed top"),
    ("TrunkCrownTree", "a big round crown on a thick bare trunk"),
    ("GiantTree", "a giant jungle tree, its clumps up a tall trunk"),
]:
    fam(base + "_Light", "tree", what + ", lighter colourway", geo=base + "_Light")
    fam(base + "_Dark", "tree", what + ", darker colourway (the lighter one's geometry)", geo=base + "_Light",
        paint=base + "_Dark")
fam("BushyTree_Light", "tree", "a bushy tree with a broad flat-topped crown", geo="BushyTree_Light")
fam("BushyTree_Hollow", "tree", "the bushy tree in a darker colourway with a shadowed hollow in its crown",
    geo="BushyTree_Light", paint="BushyTree_Hollow")
fam("LeafPointTree_Dark", "tree", "a pointed tree of spiky leaves, darker colourway", geo="LeafPointTree_A")
fam("LeafPointTree_Light", "tree", "the pointed leaf tree with a lighter top (its geometry)", geo="LeafPointTree_A",
    paint="LeafPointTree_B")
fam("ScragglyTree_EvenShade", "tree", "the second scraggly tree: the same drawing, its shading more even (the "
    "first one's geometry)", geo="ScragglyTree_A", paint="ScragglyTree_B")
fam("VineTree_Light", "tree", "the giant jungle tree hung with vines (the giant tree's art: its geometry, the "
    "vines from this sprite), lighter colourway", geo="GiantTree_Light", paint="VineTree_Light",
    vines_sprite="VineTree_Light")
fam("VineTree_Dark", "tree", "the vine-hung giant tree, darker colourway", geo="GiantTree_Light",
    paint="VineTree_Dark", vines_sprite="VineTree_Light")

# the same art as earlier images' models
fam("LayeredTree_Light", "recolour", "a tree of scale-like layered leaves: poke_l's layered tree, the same art",
    model="poke_l/PokeL_LayeredTree", sprite="LayeredTree_Light")
fam("LayeredTree_Dark", "recolour", "the layered tree, darker colourway", model="poke_l/PokeL_LayeredTree",
    sprite="LayeredTree_Dark")
fam("RoundedTree_Light", "recolour", "a rounded tree of layered leaves: poke_l's rounded tree, the same art",
    model="poke_l/PokeL_RoundedTree", sprite="RoundedTree_Light")
fam("RoundedTree_Dark", "recolour", "the rounded tree, darker colourway", model="poke_l/PokeL_RoundedTree",
    sprite="RoundedTree_Dark")
fam("Sapling_Light", "recolour", "a narrow young conifer: poke_l's sapling, the same art", model="poke_l/PokeL_Sapling",
    sprite="Sapling_Light")
fam("Sapling_Dark", "recolour", "the sapling, darker colourway", model="poke_l/PokeL_Sapling", sprite="Sapling_Dark")
fam("FallenLog", "copy", "a fallen log: poke_g's, the same art and colours", model="poke_g/PokeG_FallenLog",
    sprite="FallenLog")
fam("CutStump", "copy", "a small cut stump: poke_g's, the same art and colours", model="poke_g/PokeG_CutStump",
    sprite="CutStump")

# palms
fam("FanPalm", "palm", "a squat palm, its broad fronds in a star over a stout trunk", sprite="FanPalm")
fam("BroadPalm", "palm", "a big squat palm of broad fronds", sprite="BroadPalm")
fam("HammockPalms", "hammock", "a cream net hammock slung between two fan palms (the same art as the single palm, "
    "the right one mirrored), as drawn", sprite="FanPalm", box="HammockPalms", left="HammockPalm_Left",
    right="HammockPalm_Right")

# grasses, reeds and tufts
fam("SpikyGrassClump", "blades", "a tall flame-shaped clump of pale green blades", sprite="SpikyGrassClump",
    args=dict(lean=0.32))
fam("TallGrassClump", "blades", "a clump of tall grass", sprite="TallGrassClump", args=dict(lean=0.4))
fam("WaterReeds_A", "blades", "reeds standing in water (z 0 the water's surface)", sprite="WaterReeds_A",
    args=dict(lean=0.35))
fam("WaterReeds_B", "blades", "a smaller clump of reeds in water (z 0 the water's surface)", sprite="WaterReeds_B",
    args=dict(lean=0.35))
fam("GrassTuft_A", "blades", "a tile of short leafy grass", sprite="GrassTuft_A", args=dict(footprint="tile", lean=0.3))
fam("GrassTuft_B", "blades", "a tile of short grass, rounder and brighter", sprite="GrassTuft_B",
    args=dict(footprint="tile", lean=0.25, seed=2))
fam("GrassTuft_A2", "blades", "a tile of short upright grass", sprite="GrassTuft_A2",
    args=dict(footprint="tile", lean=0.15, seed=3))
fam("FloweringTuft", "blades", "a tile of short grass with small white flowers", sprite="FloweringTuft",
    args=dict(footprint="tile", lean=0.3, blooms=(236, 242, 228), seed=4))
fam("WindBlownBlades", "blades", "a few pale blades swept over by the wind", sprite="WindBlownBlades",
    args=dict(footprint="tile", curl=0.6, count=6, lean=0.0, mat="row"))

# sprouts and seedlings
fam("TwoLeafSapling", "lobes", "a seedling of two round leaves on a dark stem in a patch of soil",
    sprite="TwoLeafSapling", args=dict(mound=(70, 52, 38)))
fam("VSprout", "lobes", "a sprout of two leaves in a V", sprite="VSprout", args=dict())
fam("LowSeedling", "lobes", "a low seedling of two broad leaves", sprite="LowSeedling", args=dict(tilt=0.25))
fam("MoundSprout", "lobes", "a sprout in a mound of earth", sprite="MoundSprout", args=dict(mound=(176, 146, 100)))
fam("TinySprout_A", "lobes", "a tiny sprout", sprite="TinySprout_A", args=dict())
fam("TinySprout_B", "lobes", "another tiny sprout", sprite="TinySprout_B", args=dict())

# floating leaves (z 0 the water's surface)
fam("LilyPadTrio", "pads", "three overlapping lily pads", sprite="LilyPadTrio", args=dict())
fam("LotusLilyPads", "pads", "lily pads with a pink lotus flower", sprite="LotusLilyPads",
    args=dict(flower=(236, 150, 178)))
fam("FloatingLilyPads", "pads", "a scatter of small floating pads, as drawn (eight pads, separate)",
    sprite="FloatingLilyPads", args=dict(exclude_box="LotusLilyPads"))

# the rest
# the cactus's columns as drawn: (azimuth, distance out, height, radius), the
# middle one tallest, a pair drawn high behind it, one at each side, a pair low in front
fam("ColumnCactus", "cactus", "a clump of upright ribbed columns round a tall middle one", sprite="ColumnCactus",
    args=dict(columns=[(0, 0, 41, 4.0), (35, 9.5, 36, 3.7), (145, 9.5, 36, 3.7), (200, 11.5, 30, 3.1),
                       (340, 11.5, 30, 3.1), (240, 9.0, 28, 3.4), (300, 9.5, 28, 3.4)],
              cartoon_columns=[(0, 0, 40, 4.0)] + [(45 + 90 * k, 9.5, 32, 3.6) for k in range(4)]))
fam("RootStump", "stump", "a big cut stump with spreading roots", sprite="RootStump")
for piece in ("Fill", "Straight", "OuterCorner", "InnerCorner", "Ridge", "RidgeEnd", "Pillar", "FillMarked"):
    fam("Hedge_" + piece, "hedge", "the leafy hedge's %s piece" % piece, piece=piece, sprite="Hedge_Field3x3",
        interior="Hedge_Interior2x2")

# repeated sprites: the families above stand for these too
REPEATS = {"TwinSapling_Mirrored": "TwinSapling", "DarkOvalTree_Copy": "DarkOvalTree",
           "BroadCrownTree_Copy": "BroadCrownTree", "ScragglyTree_B": "ScragglyTree_EvenShade",
           "HammockPalm_Left": "HammockPalms", "HammockPalm_Right": "HammockPalms",
           "ScragglyTree_A": "ScragglyTree", "LeafPointTree_A": "LeafPointTree_Dark",
           "LeafPointTree_B": "LeafPointTree_Light", "Hedge_Field3x3": "Hedge_*", "Hedge_Interior2x2": "Hedge_*",
           "Hedge_Pill2x1": "Hedge_*", "Hedge_Round1x1": "Hedge_*", "Hedge_Pill1x2": "Hedge_*"}
