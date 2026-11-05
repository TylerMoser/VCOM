# new_1's elements

Every element of [new_1.jpg](../../../new_1.jpg) but its cottage (which is in
[../buildings/](../buildings/README.md)): **24 families, 168 complete VOX files**
directly in [output/new_1/](../), each in Base and all six treatments
([all files](FILES.md)). Made 2026-11-04 by
[output/new_images/generate.py](../../new_images/generate.py), the reasons and rules in
[output/new_images/README.md](../../new_images/README.md). [Where each is drawn](reference/new_1_regions.png)
(every copy outlined, the HUD left out in red) and [review sheets](previews/) (the
image's crop, then Base, Cartoon, TwoColor and CratePalette).

new_1 is a scene, not a sheet: its trees overlap one another and the HUD, and its plants
and figures stand on the meadow. Each element is built of its parts as drawn, its sizes
measured in the image's art pixels (16 a tile; a voxel each) and its colours the medians
of its pixels; Base keeps the image's light (lit from the left, shaded on the right).

## The elements

| Family | What it is | Copies drawn | Canvas | Builder |
| --- | --- | --- | --- | --- |
| [`New1_OliveConeTree`](../New1_OliveConeTree.vox) | the olive cone tree: a straight cone, lit on its left, dark leaf-marks on it and a pale cap at its tip, over a skirt of two tiers of round scalloped leaves, a short red-brown trunk and spreading roots (drawn eight times, every one cut off by the image's edge or overlapped by a neighbour or the HUD; the second from the left at the top the clearest) | 8 | 28x28x35 | new1_sculpt |
| [`New1_TallGrass`](../New1_TallGrass.vox) | a tile of the tall leafy grass (the strip at the top, the patch at the left: one tile of it, repeated) | 2 | 16x16x14 | new1_plants |
| [`New1_SmallYellowFlower`](../New1_SmallYellowFlower.vox) | the small yellow flower in front of the tall grass: five petals round a cream heart | 1 | 8x8x6 | new1_plants |
| [`New1_TinySprout`](../New1_TinySprout.vox) | the tiny two-leaved sprout (drawn three times: in the grass, and twice in the moss on the roof, which the cottage holds) | 3 | 10x10x4 | new1_sculpt |
| [`New1_BroadLeafPlant`](../New1_BroadLeafPlant.vox) | the broad-leaved plant: five broad oval leaves round a dark heart (drawn three times, beside the house) | 3 | 24x24x8 | new1_sculpt |
| [`New1_PlanterPlant`](../New1_PlanterPlant.vox) | the small jagged-leaved plant in the house's flower box (drawn twice; the cottage holds both) | 2 | 10x10x9 | new1_sculpt |
| [`New1_RoofFlowerPlant`](../New1_RoofFlowerPlant.vox) | the low flowering plant on the roof: round leaves and three yellow star flowers (the cottage holds it too) | 1 | 22x22x7 | new1_plants |
| [`New1_CoralFlower`](../New1_CoralFlower.vox) | the six-petalled coral-red flower (drawn twice in the grass) | 2 | 14x14x6 | new1_plants |
| [`New1_BlueFlower`](../New1_BlueFlower.vox) | the six-petalled blue flower: the coral flower's shape in blue (drawn three times in the grass) | 3 | 14x14x6 | new1_plants |
| [`New1_Woodpile`](../New1_Woodpile.vox) | the woodpile beside the house: three stripped logs side by side, ringed ends, two boards across them | 1 | 26x20x9 | new1_props |
| [`New1_ChoppingStump`](../New1_ChoppingStump.vox) | the chopping stump with an axe stuck in its top | 1 | 24x24x22 | new1_props |
| [`New1_Hero`](../New1_Hero.vox) | the hooded hero on the path, a golden staff in his hand (a static figure) | 1 | 20x16x27 | new1_figures |
| [`New1_Fairy`](../New1_Fairy.vox) | the yellow fairy floating beside the hero (a static figure; it floats about 6 voxels up, lift it when placing it) | 1 | 18x14x15 | new1_figures |
| [`New1_CrestedCreature`](../New1_CrestedCreature.vox) | the green crested creature by the flowers: an orange crest, yellow and blue feathers, a cape and scarf (a static figure) | 1 | 28x20x40 | new1_figures |
| [`New1_Crow`](../New1_Crow.vox) | the crow perched on the roof, facing right (a static figure) | 1 | 22x14x17 | new1_figures |

How each was read:

- **OliveConeTree**: no copy is whole (each is overlapped or cut off), so the tree is
  built to measurements taken across them: 35 tall from its cap to its trunk's foot;
  the cone from a 5-pixel cap to 19 wide, lit on its left; the skirt of two tiers of
  scallops 24 wide; the trunk 6 wide, its roots spread low round it (drawn 26 across, here
  within the 28-voxel canvas). Cartoon: quarter-turn
  symmetric, the cone in two bands.
- **TallGrass**: the two patches are one tile of grass repeated; its blades wrap at
  16 voxels, so tiles placed side by side join.
- **BroadLeafPlant**: five leaves as drawn (two behind, two big at the sides, one in
  front); Cartoon eight, evenly set.
- **CoralFlower / BlueFlower**: one shape in two colours; Cartoon mirrored both ways
  (six petals allow no quarter turn).
- **Woodpile**: three stripped logs lying side by side, their ringed ends to the front,
  two boards across them as drawn.
- **ChoppingStump**: the stump and its axe, the head buried at the back left, the handle
  leaning out; Cartoon the axe on the stump's middle plane.
- **Hero, Fairy, CrestedCreature, Crow**: static figures (the user's call), at the scale
  that makes the hero as tall as the game's units (27 voxels); built of the parts the
  image draws. The fairy floats about 6 voxels up in the image: lift it when placing it.

## The ground tiles

Made by the ground collection's own code ([output/ground/](../../ground/README.md),
[GROUND.md](../../../knowledge/GROUND.md)): 16 x 16 x 16, land's top at z 15, motifs
repeating every 16; a core tile each for the meadow, the light patches of meadow and the
sandy path, and for each pair that meets an edge (A, the meadow, on local x < 8), an
outer corner and an inner corner, turned to fit. [Laid out together](previews/ground_layout_Base.png)
([Cartoon](previews/ground_layout_Cartoon.png), [TwoColor](previews/ground_layout_TwoColor.png)).

| Family | Kind | From |
| --- | --- | --- |
| [`New1_Ground_LightMeadow`](../New1_Ground_LightMeadow.vox) | grass | its swatch, x 150-545 y 200-575 |
| [`New1_Ground_LightPatchEdge`](../New1_Ground_LightPatchEdge.vox) | Edge | Meadow and LightMeadow |
| [`New1_Ground_LightPatchInnerCorner`](../New1_Ground_LightPatchInnerCorner.vox) | InnerCorner | Meadow and LightMeadow |
| [`New1_Ground_LightPatchOuterCorner`](../New1_Ground_LightPatchOuterCorner.vox) | OuterCorner | Meadow and LightMeadow |
| [`New1_Ground_Meadow`](../New1_Ground_Meadow.vox) | grass | its swatch, x 672-556 y 728-580 |
| [`New1_Ground_PathEdge`](../New1_Ground_PathEdge.vox) | Edge | Meadow and SandPath |
| [`New1_Ground_PathInnerCorner`](../New1_Ground_PathInnerCorner.vox) | InnerCorner | Meadow and SandPath |
| [`New1_Ground_PathOuterCorner`](../New1_Ground_PathOuterCorner.vox) | OuterCorner | Meadow and SandPath |
| [`New1_Ground_SandPath`](../New1_Ground_SandPath.vox) | sand | its swatch, x 335-650 y 385-720 |

## Left out

The HUD (the user's call): the three hearts, the d-pad and its arrow icon, the item
bubble with its table and Y button, the corner logo. The fairy's sparkles (an effect)
and the shadows (the light's).
