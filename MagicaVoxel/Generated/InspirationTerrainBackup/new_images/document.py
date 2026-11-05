"""Writes the new images' notes from their records: output/new_images/README.md
and duplicates.json, output/new_1/elements/ and output/new_2/elements/ README.md
and FILES.md, output/new_1/buildings/README.md and FILES.md.

    python output/new_images/document.py [--root <folder holding new_1/, new_2/ and new_images/>]"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TREATMENTS = ["Base", "Cartoon", "CratePalette", "TwoColor", "Cartoon_TwoColor", "CratePalette_TwoColor",
              "Cartoon_CratePalette_TwoColor"]


def suffix(t):
    return "" if t == "Base" else "_" + t


def links(stem, up=""):
    return " | ".join("[%s](%s%s%s.vox)" % (t, up, stem, suffix(t)) for t in TREATMENTS)


def load(root):
    j = lambda p: json.loads((root / p).read_text(encoding="utf-8")) if (root / p).exists() else {}
    return (j("new_1/elements/manifest.json"), j("new_2/elements/manifest.json"), j("new_1/buildings/manifest.json"),
            j("new_images/validation-summary.json"), j("new_images/qa/whole-import.json"),
            j("new_images/structural-audit.json"), j("new_1/buildings/qa/integration-report.json"))


def size_of(manifest, stem):
    for r in manifest["files"]:
        if r["file"] == stem + ".vox":
            return r["size"], r["voxels"]
    return None, None


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("wrote", path)


# ---------------------------------------------------------------- the collection
COLLECTION = """# The new images: new_1 and new_2

Created 2026-11-04 (Claude). Every element of the two inspiration images the user
added, [new_1.jpg](../../new_1.jpg) and [new_2.jpg](../../new_2.jpg), as complete
voxel models: **{families} families, {files} complete VOX files**, each family in
Base and all six established treatments. The files are directly in
[output/new_1/](../new_1/) ({n1_families} families, {n1_files} files, the cottage
among them) and [output/new_2/](../new_2/) ({n2_families} families, {n2_files} files),
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

- [Validation](validation-summary.json), on the files on disk: {val_files} files in
  {val_families} families, **{val_problems} problems**: each file reads, inside its
  canvas, grounded, 255 unused, the crate palette exact and 253 only on glass, TwoColor
  one colour a material; each recolour's voxels exactly its Base's or Cartoon's;
  Cartoon's shape not Base's (but the ground tiles' and the copies', by their
  conventions); every Cartoon's symmetry found and the quarter-turn ones checked; one
  connected model but for the families drawn as a scatter or a patch of separate
  plants; nothing that was in output/new_1/ and output/new_2/ before changed, nor the
  shared files' old bytes.
- [Structural audit](structural-audit.json) ([tools/inspect_vox.py](../../tools/inspect_vox.py)):
  {audit_files} files, {audit_errors} errors, {audit_warnings} warnings.
- [Read whole through VCOM's own importer](qa/whole-import.json), in a scratch copy of
  the game verified identical to the real one first: {whole_ok} of {whole_n} files
  read, their voxel counts, a mesh at Scale 0.0625, grounded and as big as their voxels
  say; glass only in the cottage's seven files.
- The cottage, cut into the game's 16-cubed pieces and played by the game's rules in
  a scratch copy: {cot_scenes} scenes (its seven treatments), {cot_failed} failed checks
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
"""


def collection(root, M1, M2, MC, V, WI, AU, IR):
    n1f = len(M1["families"]) + 1
    n1 = len(M1["files"]) + len(MC.get("models", []))
    n2f, n2 = len(M2["families"]), len(M2["files"])
    keys = ("read", "voxels_match", "mesh", "grounded", "size_match", "glass_voxels_match")
    whole_ok = sum(1 for r in WI.values() if all(r.get(k) for k in keys))
    audit = AU if isinstance(AU, list) else []
    errs = sum(len(a.get("errors", [])) for a in audit)
    warns = sum(len(a.get("warnings", [])) for a in audit)
    failed = sum(1 for r in IR.values() for ok in r.get("checks", {}).values() if not ok)
    text = COLLECTION.format(families=n1f + n2f, files=n1 + n2, n1_families=n1f, n1_files=n1, n2_families=n2f,
                             n2_files=n2, val_files=V.get("summary", {}).get("files", "?"),
                             val_families=V.get("summary", {}).get("families", "?"),
                             val_problems=V.get("summary", {}).get("problems", "?"), audit_files=len(audit),
                             audit_errors=errs, audit_warnings=warns, whole_ok=whole_ok, whole_n=len(WI),
                             cot_scenes=len(IR), cot_failed=failed)
    write(root / "new_images" / "README.md", text)


# ---------------------------------------------------------------- new_1's elements
def new1_elements(root, M1, MC):
    rows = []
    for f in M1["families"]:
        if f.get("layer") == "Ground":
            continue
        stem = "New1_" + f["name"]
        size, vox = size_of(M1, stem)
        rows.append("| [`%s`](../%s.vox) | %s | %d | %s | %s |" % (
            stem, stem, f["what"], len(f["regions"]), "x".join(map(str, size)), f["builder"].split(".")[0]))
    ground = []
    for f in M1["families"]:
        if f.get("layer") != "Ground":
            continue
        r = f["row"]
        ground.append("| [`%s`](../%s.vox) | %s | %s |" % (
            r["name"], r["name"], r.get("contour") or r["kind"],
            " and ".join(n.replace("New1_Ground_", "") for n in r.get("materials", [])) or
            "its swatch, x %d-%d y %d-%d" % tuple(r["crop"])))
    text = """# new_1's elements

Every element of [new_1.jpg](../../../new_1.jpg) but its cottage (which is in
[../buildings/](../buildings/README.md)): **{n} families, {files} complete VOX files**
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
{rows}

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
{ground}

## Left out

The HUD (the user's call): the three hearts, the d-pad and its arrow icon, the item
bubble with its table and Y button, the corner logo. The fairy's sparkles (an effect)
and the shadows (the light's).
""".format(n=len(M1["families"]), files=len(M1["files"]), rows="\n".join(rows), ground="\n".join(ground))
    write(root / "new_1" / "elements" / "README.md", text)
    lines = ["# new_1's element files", "",
             "Every file of [new_1's elements](README.md), seven a family, directly in [output/new_1/](../); "
             "[review sheets](previews/).", ""]
    for f in M1["families"]:
        stem = f["row"]["name"] if f.get("layer") == "Ground" else "New1_" + f["name"]
        lines += ["## %s" % stem, "", links(stem, "../"), ""]
    write(root / "new_1" / "elements" / "FILES.md", "\n".join(lines))


# ---------------------------------------------------------------- new_2's elements
def new2_elements(root, M2):
    rows = []
    for f in M2["families"]:
        stem = "New2_" + f["name"]
        size, vox = size_of(M2, stem)
        how = f["kind"]
        if f["kind"] == "tree" and f.get("paint"):
            how = "tree (geometry %s, painted from %s)" % (f["geo"], f["paint"])
        elif f["kind"] == "tree" and f.get("geo") != f["name"]:
            how = "tree (geometry %s)" % f["geo"]
        elif f["kind"] in ("copy", "recolour"):
            how = "%s of output/%s" % (f["kind"], f["model"])
        rows.append("| [`%s`](../%s.vox) | %s | %s | %s |" % (stem, stem, f["what"], "x".join(map(str, size)), how))
    text = """# new_2's elements

Every sprite of [new_2.jpg](../../../new_2.jpg), the vegetation sheet: **{n}
families, {files} complete VOX files** directly in [output/new_2/](../), each in Base
and all six treatments ([all files](FILES.md)). Made 2026-11-04 by
[output/new_images/generate.py](../../new_images/generate.py), the reasons and rules in
[output/new_images/README.md](../../new_images/README.md). [Every sprite's box](reference/new_2_boxes.png)
and [review sheets](previews/) (the sprite, then Base, Cartoon, TwoColor and
CratePalette).

The sheet is native pixel art, 16 pixels a tile: a voxel is a pixel, a model as tall as
its sprite. Every non-background part of the sheet lies in one of its 88 boxes
(checked); the boxes are in [lib/boxes_new2.json](../../new_images/lib/boxes_new2.json).

## The families

| Family | What it is | Canvas | Made as |
| --- | --- | --- | --- |
{rows}

## Shared and reused

- **Colourways.** The sheet draws many trees twice, lighter and darker: each pair is
  one geometry (the lighter sprite's), each painted from its own sprite (`_Light`,
  `_Dark`); so are the bushy tree and its shaded copy, the two leaf-point trees, the two
  scraggly trees, and the vine trees (the giant tree's geometry, the vines from the vine
  tree's sprite).
- **Drawn twice alike.** The mirrored twin sapling, the second oval tree, the second
  broad-crown tree, both hammock palms: one family each.
- **The same art as an earlier image's model.** The fallen log and the small cut stump
  are poke_g's (copied whole, re-encoded under these names); the layered tree, the rounded
  tree and the sapling are poke_l's geometry in this sheet's colours. All recorded in
  [duplicates.json](../../new_images/duplicates.json).
- **The hedge** is a kit of eight tile pieces, from the sheet's 3 x 3 field and its 2 x 2
  interior: Fill, Straight, OuterCorner, InnerCorner, Ridge, RidgeEnd, Pillar,
  FillMarked; with them every hedge the sheet draws (the field, the pills two tiles long
  either way, the round single) is built.
- **Scatters.** The floating lily pads, the lily pads under the lotus, the grass tufts,
  the reeds and the wind-blown blades are drawn as separate pieces and stay so (their
  parts counted in the validation).
""".format(n=len(M2["families"]), files=len(M2["files"]), rows="\n".join(rows))
    write(root / "new_2" / "elements" / "README.md", text)
    lines = ["# new_2's element files", "",
             "Every file of [new_2's elements](README.md), seven a family, directly in [output/new_2/](../); "
             "[review sheets](previews/).", ""]
    for f in M2["families"]:
        stem = "New2_" + f["name"]
        lines += ["## %s" % stem, "", links(stem, "../"), ""]
    write(root / "new_2" / "elements" / "FILES.md", "\n".join(lines))


# ---------------------------------------------------------------- the cottage
COTTAGE = """# new_1 cottage

Created 2026-11-04 (Claude), the way the [poke_u buildings](../../poke_u/buildings/README.md)
were made. The building in [new_1.jpg](../../../new_1.jpg): **one family, 7 complete VOX
files**, `New1_Cottage` in Base and all six established treatments, directly in
`output/new_1/`; this folder holds its generator, records, previews and the test that
puts it into the game. [Views](previews/New1_Cottage_views.png) | [In the art's projection](previews/New1_Cottage_art.png)
| [Files](FILES.md) | [Manifest](manifest.json) | [In-game test](qa/integration-report.json)

It is **made to go into VCOM cleanly**: drawn on the game's tile grid at the game's scale,
with real glass, so it can be cut into the game's 16-cubed level pieces and play by the
game's rules. That was tested in a copy of the game: its seven treatments cut, imported
and checked, {scenes} scenes, {failed} failed checks.

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
{scenes} scenes, {failed} failed checks ([report](qa/integration-report.json)). The
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
"""


def cottage(root, MC, IR):
    failed = sum(1 for r in IR.values() for ok in r.get("checks", {}).values() if not ok)
    write(root / "new_1" / "buildings" / "README.md", COTTAGE.format(scenes=len(IR), failed=failed))
    lines = ["# new_1 cottage files", "", "The [cottage](README.md)'s seven files, directly in [output/new_1/](../).",
             "", "## New1_Cottage", "", links("New1_Cottage", "../"), "",
             "[Views](previews/New1_Cottage_views.png) | [In the art's projection](previews/New1_Cottage_art.png)", ""]
    write(root / "new_1" / "buildings" / "FILES.md", "\n".join(lines))


def duplicates(root, M1, M2):
    out = {"note": "Reuse in the new images' models: the same art as an earlier image's model, colourways sharing "
                   "one geometry, sprites drawn more than once, and models one family holds of another's.",
           "copied_from_earlier_images": [], "recoloured_from_earlier_images": [], "colourways": [],
           "drawn_more_than_once": {}, "held_by_other_models": []}
    for f in M2["families"]:
        if f["kind"] == "copy":
            out["copied_from_earlier_images"].append({"family": "New2_" + f["name"], "of": "output/" + f["model"],
                                                      "how": "the same voxels and palettes, re-encoded under this name"})
        elif f["kind"] == "recolour":
            out["recoloured_from_earlier_images"].append({"family": "New2_" + f["name"], "of": "output/" + f["model"],
                                                          "how": "the same voxels, painted from this sheet's sprite"})
        elif f["kind"] == "tree" and (f.get("paint") or f.get("geo") != f["name"]):
            out["colourways"].append({"family": "New2_" + f["name"], "geometry_of_sprite": f["geo"],
                                      "painted_from_sprite": f.get("paint") or f["geo"]})
    import sys
    sys.path.insert(0, str(HERE / "lib"))
    from catalogue_new2 import REPEATS
    out["drawn_more_than_once"]["new_2 (sprite: the family standing for it)"] = REPEATS
    out["drawn_more_than_once"]["new_1 (family: copies drawn)"] = {
        "New1_" + f["name"]: len(f["regions"]) for f in M1["families"] if f.get("regions") and len(f["regions"]) > 1}
    out["held_by_other_models"] = [
        {"model": "New1_Cottage", "holds": "New1_PlanterPlant (two, pressed front to back into its flower box)"},
        {"model": "New1_Cottage", "holds": "New1_RoofFlowerPlant (on its roof)"},
        {"model": "New1_Cottage", "holds": "New1_TinySprout (two, in the moss on its roof)"},
        {"model": "New2_HammockPalms", "holds": "the fan palm (New2_FanPalm's art) twice, the second turned half round"},
        {"model": "New1_BlueFlower", "holds": "New1_CoralFlower's geometry, in blue"}]
    write(root / "new_images" / "duplicates.json", json.dumps(out, indent=1) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=HERE.parent)
    args = ap.parse_args()
    M1, M2, MC, V, WI, AU, IR = load(args.root)
    duplicates(args.root, M1, M2)
    new1_elements(args.root, M1, MC)
    new2_elements(args.root, M2)
    cottage(args.root, MC, IR)
    collection(args.root, M1, M2, MC, V, WI, AU, IR)


if __name__ == "__main__":
    main()
