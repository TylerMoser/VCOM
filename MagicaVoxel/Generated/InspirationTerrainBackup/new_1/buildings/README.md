# new_1 cottage

Created 2026-11-04 (Claude), the way the [poke_u buildings](../../poke_u/buildings/README.md)
were made. The building in [new_1.jpg](../../../new_1.jpg): **one family, 7 complete VOX
files**, `New1_Cottage` in Base and all six established treatments, directly in
`output/new_1/`; this folder holds its generator, records, previews and the test that
puts it into the game. [Views](previews/New1_Cottage_views.png) | [In the art's projection](previews/New1_Cottage_art.png)
| [Files](FILES.md) | [Manifest](manifest.json) | [In-game test](qa/integration-report.json)

It is **made to go into VCOM cleanly**: drawn on the game's tile grid at the game's scale,
with real glass, so it can be cut into the game's 16-cubed level pieces and play by the
game's rules. That was tested in a copy of the game: its seven treatments cut, imported
and checked, 7 scenes, 0 failed checks.

## The building in the art

new_1.jpg is pixel art enlarged 4.6 times: a tile is 16 of its art pixels, so a voxel is
one of them across and in depth. The cottage stands in the middle of the scene, drawn
once, whole: 80 art pixels wide (five tiles), its flat roof 36 deep. Not part of it:
the crow on its roof (a figure of its own), the woodpile, plants and stump round it
(families of their own in [../elements/](../elements/README.md)).

## Made for the game's grid

As the poke_u buildings: 16 voxels a tile, tile boundaries at x = 8 + 16i and y = 8 +
16j with half a tile of margin all round; levels z = 16k, level 0 its own floor, a stone
foundation standing in for the map's ground; walls two voxels thick across their
boundary; the door closed as drawn, one leaf in one doorway slot, the two levels a unit
fills; each window within its tile, its own window piece, its glass over a sill course a
level high; no upper floor (the art draws no way up; its flat roof is no floor); the
corner pillars where four tiles meet, decoration to the fight; every pattern repeating
every 16 voxels. Front local -Y, Z up, grounded at z 0, scene translation `0 0 floor(height
/ 2)`, Mesh at Scale 0.0625, index 255 unused. Five tiles by two, 96 x 48 x 96.

**Scale.** A tile 16 across and in depth; heights foreshortened to **0.6**: the door is
drawn 19.2 art pixels tall for its two levels. Measured in the art's projection from the
ground line under the door (row 93.5 of the art's 160), model against art:

| Feature | Model | Art |
| --- | --- | --- |
| The door's leaves (top, foot) | rows 74.3-93.5 | 74.3-93.5 |
| The door's leaves (x) | x 71-87 | 69-88.5 |
| The arch round the door (top; x) | row 68.5; x 65-93 | row 70; x 65-92 |
| The beam under the roof (a voxel proud) | rows 70.5-74.1 | 70-73 |
| The parapet's front face | rows 59.3-69.5 | 59-70 |
| The roof's back edge | row 25.3 | 23 |
| The chimney's top (front, back; x) | rows 30.7, 22.7; x 49-63 | rows 31, 24; x 48-63 |
| The window bays' dark | rows 73.1-84.5 | 73-81, its foot behind the box |
| The flower boxes (two proud) | rows 82.3-87.1 | 82.8-86.7 |
| The stone base course | rows 85.1-93.5 | 86.7-93.5 |
| The corner pillars (x) | x 37-46, 112-121 | 39-46, 111-118 |
| The crack across the roof (x) | x 78-106 | 80-105 |

Every feature is within two art pixels of where it is drawn but the roof's back edge,
drawn two rows deeper than the two tiles and the parapet give. [previews/New1_Cottage_art.png](previews/New1_Cottage_art.png)
draws the Base model in the art's projection beside the source crop.

**Where the grid moves things.** The door is drawn 19.5 art pixels wide (two leaves);
here it is one doorway slot, a tile, its two leaves drawn on it, the arch round it as
drawn. The window bays are drawn 19 pixels wide, from each pillar to the door's frame;
here each bay is dark as drawn, but only its part within one tile (tiles 1 and 3) is a
window with glass, the rest a dark recess, as a window keeps within its tile.

## Each part

What the art shows is followed; what it cannot show (sides, back, inside) is inferred in
the same style.

- **Walls**: blue-grey stone in courses eight voxels high, blocks eight long staggered,
  the top of each course lit, a few dark pits in each block, as the pillars are drawn; a
  square stone pillar at each corner, a voxel proud of both walls.
- **The front**: the stone base course (the sill) whole; over it the two dark window
  bays, their glass the black of the unlit inside (MagicaVoxel Glass, a little lighter so
  the inside shows dimly); in the foot of each bay a flower box of orange wood two voxels
  proud, the stone showing under it, the left box holding the two jagged-leaved plants
  (new_1's PlanterPlant) as drawn, the right one only soil; the door of two dark
  red-brown leaves in tile 2 under a round-headed arch of lighter wood; a half round
  doorstep of slate in front of it, in the margin, at the floor's height.
- **The beam**: dark red-brown, all round under the roof, a voxel proud, its top lit.
- **The roof**: a slab over the walls, tan stone; a parapet six voxels wide round its
  edge, its blocks a tile long, lit on top; the middle recessed four, cracked at the
  front as drawn; a tan chimney at the back left, its top lit and its flue dark; moss in
  the trees' olive over the back of its left end with four small yellow flowers and two
  tiny sprouts (new_1's TinySprout), and the flowering plant (new_1's RoofFlowerPlant) at
  its front left, as drawn.
- *Inferred*: the back (two dark windows over the base course, no boxes), a window in
  each side, the inside (a plank floor, the roof's underside), the foundation.

## Treatments

Seven files: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor,
Cartoon_CratePalette_TwoColor. Every voxel carries a material label ([palettes.py](palettes.py)),
so each treatment paints the same geometry.

- **Base**: one palette, the medians of each material's pixels in the art, clustered so
  the JPEG's noise and the outlines drop out; the invented inside and foundation noted.
- **Cartoon**: the same building on the same grid, its door, windows and slots unchanged:
  the stone in courses and blocks twice as big and without pits, the parapet plain, no
  crack, the moss one colour, the flower boxes a voxel deeper, the door's boards wider,
  the plants the Cartoon plants.
- **CratePalette**: the pinned crate palette byte for byte, each colour on its class's
  nearest entry (blues for the stone and the step, lights for the tan stone, reds for the
  wood, leaves for the plants, greys for the dark); glass on crate index 253 alone.
- **TwoColor**, by the user's rule: six groups, the stone, the tan roof, the wood, the
  plants (their yellow flowers folded in), the dark of the window bays, and glass.
- **The mixtures**: Cartoon_TwoColor the Cartoon geometry in those colours, the crate
  mixtures each group on its own crate entry.

## Validation

[qa/integration.py](qa/integration.py) cuts the cottage into the game's pieces
([qa/cut_pieces.py](qa/cut_pieces.py)) in a scratch copy of the game, verified identical
to the real one first, imports them and checks what the rules see
([qa/godot/building_probe.gd](qa/godot/building_probe.gd)): the storey's floor at its
level under the roof; round it, at the two levels a unit fills, every wall, sill and the
closed door shut and every window open; a line of sight through each window at the eye
and none through the walls; a vault in over each sill and no step in anywhere else; the
view cut away at the storey; the level the game stamps the model voxel for voxel.
7 scenes, 0 failed checks ([report](qa/integration-report.json)). The
files themselves are checked with the rest by [output/new_images/validate.py](../../new_images/validate.py).

## Regenerating

```text
python output/new_1/buildings/generate.py      # the 7 files and manifest.json
python output/new_1/buildings/previews.py      # previews/New1_Cottage_views.png
python output/new_1/buildings/compare_art.py   # previews/New1_Cottage_art.png
python output/new_1/buildings/qa/integration.py --game <copy of VoxelXCOM/vcom>
```

The generator owns only its seven files (it stops at anything else) and needs the plant
builders in [output/new_images/lib/](../../new_images/lib/).
