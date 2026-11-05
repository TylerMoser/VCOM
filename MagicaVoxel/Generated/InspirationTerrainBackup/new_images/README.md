# The new images: new_1 and new_2

Created 2026-11-04 (Claude). Every element of the two inspiration images the user
added, [new_1.jpg](../../new_1.jpg) and [new_2.jpg](../../new_2.jpg), as complete
voxel models: **111 families, 777 complete VOX files**, each family in
Base and all six established treatments. The files are directly in
[output/new_1/](../new_1/) (25 families, 175 files, the cottage
among them) and [output/new_2/](../new_2/) (86 families, 602 files),
named `New1_*` and `New2_*`; this folder holds the code that makes them, its
library, the checks and their results.

| | |
| --- | --- |
| new_1's elements | [notes](../new_1/elements/README.md), [all files](../new_1/elements/FILES.md), [where each is drawn](../new_1/elements/reference/new_1_regions.png), [review sheets](../new_1/elements/previews/) |
| new_1's cottage | [notes](../new_1/buildings/README.md), [files](../new_1/buildings/FILES.md), made and tested in the game as the earlier buildings were |
| new_2's elements | [notes](../new_2/elements/README.md), [all files](../new_2/elements/FILES.md), [every sprite's box](../new_2/elements/reference/new_2_boxes.png), [review sheets](../new_2/elements/previews/) |
| Checks | [validation](validation-summary.json), [structural audit](structural-audit.json), [read whole through the game's importer](qa/whole-import.json), [reuse](duplicates.json) |

## What was asked

The user's request (2026-11-04): *"I added 2 additional inspiration images to the
folder, new_1 and new_2. Fully generate vox files for all elements of these images,
following all previously rules/guidelines. Take your time with this step, and be
careful not to miss any sprites or components of the images."* Asked about two
things the earlier collections had no rule for, the user chose: **model new_1's
four figures** (the hooded hero, the floating fairy, the crested creature and the
crow) as static figures, with no rig or animation; and **leave the HUD out** (the
hearts, the d-pad and arrow icons, the item bubble with its table and Y button, the
corner logo).

new_1.jpg is a scene: pixel art enlarged 4.6 times (a tile 16 of its art pixels, 73.6
of the image's), a cottage in a meadow with trees, plants, props and four figures.
new_2.jpg is a sprite sheet of vegetation at its native size (16 pixels a tile).
Nothing was missed: every non-background part of new_2's sheet lies in one of its 88
sprite boxes (checked), and new_1's elements were inventoried from the image and its
rebuild at one pixel an art pixel, region by region ([new_1_regions.png](../new_1/elements/reference/new_1_regions.png)).

Another agent made its own models of the same two images at the same time:
`New1_Codex_*` and `New2_Codex_*` in the same folders, their `codex/` subfolders and
[output/codex_new_images/](../codex_new_images/). None of them was touched (their
hashes are in [preserved-hashes.json](preserved-hashes.json) and checked), and no name
here is one of theirs.

## The rules followed

As every collection here: complete models only (no cell files or brushes); seven
files a family in the [shared specification's](../../knowledge/VARIATIONS.md) names
and order; grounded at z 0, scene translation `0 0 floor(height / 2)`, imported as a
Mesh at Scale 0.0625, 16 voxels a tile; palette index 255 (the game's blood) never
used, 253 (the crate's glass) only for glass; the crate palette byte for byte in
CratePalette files; the TwoColor rule (the user's, 2026-10-28): *"Don't require
exactly 2 colors. Make exceptions for glass and lights. Also allow more than 2
colors, but minimizing the number of colors and combining all similar colors into
large chunks of single-color voxels."*: one flat colour a material. A sprite drawn
more than once is one family; the same art as an earlier image's model reuses that
model (recorded in [duplicates.json](duplicates.json)); a building is made on the
game's grid and tested in a copy of the game ([output/new_1/buildings/](../new_1/buildings/README.md)).

## How they are made

- **new_2** ([lib/build_new2.py](lib/build_new2.py), [lib/catalogue_new2.py](lib/catalogue_new2.py)):
  each sprite is read at a pixel a voxel ([lib/sprites.py](lib/sprites.py): the
  sheet's white and the drop shadows' light grey are background; a box keeps its
  main body), its height the model's, as the earlier tree collections size trees.
  Trees and bushes ([lib/sculpt_tree.py](lib/sculpt_tree.py)) are sliced row by row: a
  run of the sprite that reaches the axis a round slice centred where it is drawn
  (on the axis in Cartoon), a run of leaf off the axis a clump turned to the front and
  back (all four sides in Cartoon), wood off the trunk a branch, a stray clump joined
  to the trunk by a branch; the dark outline lines cut a voxel in; each surface voxel
  painted from the side it faces. Palms ([lib/sculpt_palm.py](lib/sculpt_palm.py)):
  a stout ringed trunk and rings of fronds. Grasses and reeds as blades, sprouts as
  leaf lobes on a stem, lily pads seen from above, the cactus as ribbed columns, the
  big stump with its roots ([lib/sculpt_plants.py](lib/sculpt_plants.py)); the cloud
  bush and the forked sapling as puffs on a trunk, the fern as fronds
  ([lib/sculpt_clumps.py](lib/sculpt_clumps.py)); the hedge as a kit of tile pieces
  ([lib/sculpt_hedge.py](lib/sculpt_hedge.py)); the hammock between two palms
  ([lib/sculpt_hammock.py](lib/sculpt_hammock.py)).
- **new_1** ([lib/catalogue_new1.py](lib/catalogue_new1.py)): its trees overlap one
  another and the HUD and its plants and figures stand on the meadow, so nothing can
  be cut out whole by colour; each element is built of its parts as the image draws
  them, every size measured on the image in its art pixels and every colour its
  median there ([lib/new1_sculpt.py](lib/new1_sculpt.py), [lib/new1_plants.py](lib/new1_plants.py),
  [lib/new1_props.py](lib/new1_props.py), [lib/new1_figures.py](lib/new1_figures.py)).
  Its ground tiles are made by the ground collection's own functions, taken unchanged
  from [output/ground/generate.py](../ground/generate.py) (its hash checked) and run
  over new_1's rows ([lib/new1_ground.py](lib/new1_ground.py)), so they follow
  [GROUND.md](../../knowledge/GROUND.md) exactly. The cottage is made by its own
  pipeline, the poke_u buildings' ([output/new_1/buildings/](../new_1/buildings/README.md)).
- **The treatments** ([lib/treatments.py](lib/treatments.py)): Base and Cartoon in
  their own colours; CratePalette each colour on the nearest crate entry of its
  material's class; TwoColor one flat colour a material: the mean of the material's
  colours as the game's camera sees them from above (an open top counts twice, an
  open side once, an underside not at all), snapped to the nearest of its own shades;
  the crate mixtures those flat colours on distinct crate entries. Cartoon changes the
  shape as well as the paint: exact quarter-turn symmetry for the trees, palms,
  bushes, cactus, stump and most plants, a mirror for the things with a front (the
  figures, the props, a flower), each simplified (bands of colour, regular
  details, plumper leaves).

## Regenerating

```text
python output/new_images/generate.py [new_1|new_2|all] [family ...]   # every model but the cottage
python output/new_1/buildings/generate.py                             # the cottage
python output/new_images/review.py            # review sheets, both images
python output/new_images/refsheets.py         # the regions and boxes over each image
python output/new_images/ground_layout.py     # new_1's ground tiles laid out together
python output/new_images/validate.py          # writes validation-summary.json
python output/new_images/qa/whole_import.py --game <copy of VoxelXCOM/vcom>
python output/new_1/buildings/qa/integration.py --game <copy of VoxelXCOM/vcom>
python output/new_images/document.py          # these notes
```

Each generator owns only the files its manifest names: a file already there is
overwritten only if it is still exactly what it wrote last (its hash), so a hand
edit, or another agent's file, stops the run unless `--replace-generated` is given.
Run again, they give the same files byte for byte. They read the image files, the
crate palette, poke_l's and poke_g's models (reused) and the ground collection's
generator, and change none of them.

## Checks

- [Validation](validation-summary.json), on the files on disk: 777 files in
  111 families, **0 problems**: each file reads, inside its
  canvas, grounded, 255 unused, the crate palette exact and 253 only on glass, TwoColor
  one colour a material; each recolour's voxels exactly its Base's or Cartoon's;
  Cartoon's shape not Base's (but the ground tiles' and the copies', by their
  conventions); every Cartoon's symmetry found and the quarter-turn ones checked; one
  connected model but for the families drawn as a scatter or a patch of separate
  plants; nothing that was in output/new_1/ and output/new_2/ before changed, nor the
  shared files' old bytes.
- [Structural audit](structural-audit.json) ([tools/inspect_vox.py](../../tools/inspect_vox.py)):
  777 files, 0 errors, 0 warnings.
- [Read whole through VCOM's own importer](qa/whole-import.json), in a scratch copy of
  the game verified identical to the real one first: 777 of 777 files
  read, their voxel counts, a mesh at Scale 0.0625, grounded and as big as their voxels
  say; glass only in the cottage's seven files.
- The cottage, cut into the game's 16-cubed pieces and played by the game's rules in
  a scratch copy: 7 scenes (its seven treatments), 0 failed checks
  ([its report](../new_1/buildings/qa/integration-report.json)).

## Decisions made without asking

- **Scale.** new_1: a voxel an art pixel across and in depth, as the house and the tree
  collections size things; the trees and plants as tall as drawn; the cottage's
  heights foreshortened to 0.6 (its door drawn 19.2 art pixels tall for its two
  levels); the four figures at 1.35 voxels an art pixel, the scale that makes the hero
  as tall as the game's units (27 voxels), the same for all four so they keep their
  sizes against each other. new_2: a voxel a pixel, a model as tall as its sprite.
- **Colourways** (new_2 draws many trees twice, lighter and darker): one geometry,
  each painted from its own sprite; the second scraggly tree and the second leaf-point
  tree, shaded a little differently, likewise. Copies drawn the same (the mirrored twin
  sapling, the second oval tree, the second broad-crown tree) are one family.
- **Puffs and fronds** where slicing could not read a sprite: the cloud bush's five
  puffs, the forked sapling's four clumps (the two drawn and two the side view shows),
  the leafy clump as a fern of lobed fronds; each puff placed by eye from the sprite.
- **Palms** sculpted anew from new_2's own sprites rather than reusing poke_o's palms:
  new_2 draws its own kind, squat, with broad fronds over a stout ringed trunk.
- **The hedge** as a kit of eight tile pieces (fill, straight edge, outer and inner
  corner, a ridge a tile wide and its end, the round single, the marked fill) that
  build every hedge the sheet draws.
- **Floating things** stand on a datum at z 0, as the vegetation collection's lily pads
  do: the pads on the water's surface, reeds rising from it, the fairy's lowest voxel
  (it floats about 6 voxels up in the image; lift it when placing it).
- **new_1's figures**: built of the round parts the image draws, lit from the upper
  left as drawn; their Cartoon mirrored across the figure's middle, the hero's staff
  held upright in front of him so it stays one staff. The fairy's sparkles are an
  effect, and shadows are the light's: neither is modelled.
- **The roof's plants** (the flowering plant, the moss's two sprouts) and the flower
  box's two plants are their own families and are also on the cottage, where drawn.
- **TwoColor's flat colour** is the snapped mean of what is seen, so a leaf's dark
  underside or a tuft's dark foot does not become the plant's one colour.

## Known gaps

- The trees are read from one front view: a crown's puffs drawn on one side stand on
  the sides the view shows (front, back and that side), not round the whole crown.
- new_1's ground meadow, light meadow and path are new_1's own colours on the ground
  collection's motifs; the light patches' leaf-sprig edges and the grass tufts along the
  path's edges are its wavy edge, not the drawn sprigs and tufts.
- No model has gameplay flags: decorative plants need `solid=false` at integration, as
  the vegetation collection notes; only the cottage was played in the game.
