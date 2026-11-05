# poke_n olive woodland trees and shrub

Created 2026-10-27: **28 complete VOX files**, four appearances with Base and all six established variations. Complete models only; no cell files or brush packages.

[Overview](overview.png) | [All models](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)

## Source and scale

[poke_n.png](../../poke_n.png) is 638 x 766 pixel artwork. The terrain and object grid is consistent with 16-pixel tiles, with major trees approximately 32 pixels wide. We use approximately one source pixel per voxel and 16 voxels per tile. This is a source-scale interpretation, not a recovery of physical height: top-down sprite projection mixes height and canopy depth. Square depth and unseen structure are inferred.

Four appearances are included: rounded olive tree, dark pointed tree, golden-olive tree and small dark round shrub beside paths. The rounded tree has broad horizontal foliage bands; the darker tree has a pointed crown and clustered foliage; the golden tree has a fuller upper crown. The shrub is a distinct small woody form, not a miniature copy of a tall tree. Repeated and occluded placements are not additional types. Flowers, reeds, rocks, terrain and source ground shadows are excluded. No separate sapling type was identified.

The rounded tree uses 32 x 32 x 36 voxels, the dark and golden trees 32 x 32 x 40, and the shrub 16 cubed. Source regions use top-left XY with exclusive right/bottom edges and retain contextual neighbors. They are not segmentation masks. All models are Z-up, grounded at z=0, horizontally canvas-centered, with scene translation `0 0 floor(height/2)` and no required facing direction.

| Base model | Canvas XYZ | Base occupied XYZ | Comparison |
| --- | --- | --- | --- |
| [PokeN_RoundedOliveTree](PokeN_RoundedOliveTree.vox) | 32 x 32 x 36 | 32 x 32 x 36 | [All styles](previews/PokeN_RoundedOliveTree_family.png) |
| [PokeN_DarkPointedTree](PokeN_DarkPointedTree.vox) | 32 x 32 x 40 | 32 x 32 x 40 | [All styles](previews/PokeN_DarkPointedTree_family.png) |
| [PokeN_GoldenOliveTree](PokeN_GoldenOliveTree.vox) | 32 x 32 x 40 | 32 x 32 x 40 | [All styles](previews/PokeN_GoldenOliveTree_family.png) |
| [PokeN_RoundShrub](PokeN_RoundShrub.vox) | 16 x 16 x 16 | 16 x 16 x 16 | [All styles](previews/PokeN_RoundShrub_family.png) |

## Geometry and variation choices

The local sculptor adapts established solid crown construction with new oliveball and goldcrown profiles. RoundedOliveTree has broad shoulders and coherent horizontal paint bands. DarkPointedTree has a higher pointed silhouette and clustered greens. GoldenOliveTree has a fuller upper profile and subdued golden-olive paint. RoundShrub is a low rounded form with a small woody base and internal stem. These woody regions are inferred where hidden by foliage/shadow in the sprite, keeping the two material groups meaningful. Interior geometry is solid and every output is connected.

Base uses restrained irregular outlines and clustered paint; Cartoon balances outline and color under exact horizontal quarter turns. Cartoon changes geometry while preserving identity, footprint and height target. The local code has no runtime dependency on another image folder. Source black outlines and ground shadows are not copied as shells or floor geometry.

The [shared specification](../../knowledge/VARIATIONS.md) defines all six treatments: Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Every recolor preserves the exact occupied set and scene placement of its designated Base or Cartoon authority.

Explicit semantic assignments separate foliage from roots, trunks and hidden wood. TwoColor uses one flat foliage color and one flat wood color, exactly two occupied indices with two distinct RGBA colors. Preview lighting still shades their faces.

CratePalette copies the entire pinned [crate palette](../../knowledge/palettes/crate-palette.json). Green foliage maps to 241-246, gold foliage to the saved warm range 225-230, and wood to crate browns 178-180. The palette has no close golden-olive ramp; the golden tree therefore becomes warmer in CratePalette, using only existing colors. For its two-color crate mixtures, foliage explicitly uses existing ochre index 228 (190,119,43), while wood uses its separately selected crate brown. Naive nearest-color mapping selected the same brown for both groups, so this documented choice preserves the required distinction. Both crate/two-color mixtures share that choice. Index 255 is unused. All exact mappings, palette hashes and geometry-source hashes are in the manifest.

## Validation and integration scope

[Structural audit](structural-audit.json) covers all 28 delivered models. Generation rereads serialized data and checks dimensions, bounds, connectivity, exact recolor coordinates, C4 occupancy and paint, reference palette identity and two-color counts. [Godot report](godot-validation.json) records whole Mesh import at scale 0.0625 with retained voxel counts and grounded bounds. QA uses the current VCOM importer with its license and [source hashes](qa/source-provenance.json). [Validation summary](validation-summary.json) records final checks and visual review.

[Contact sheet](previews/contact_01.png) covers every treatment. [Geometry sheet](previews/geometry_01.png) shows Base and Cartoon at four azimuths. Camera and lighting match within each family; different families are framed independently, so card size is not world scale.

This checks structural integrity and the whole-model import/render path, not gameplay, collision, cover, destruction or MagicaVoxel GUI behavior. Trees exceed the 16-cubed PieceKind contract; the shrub fits that canvas but still needs explicit game registration/settings. All widths are below the loose-model limit of 62; that separate runtime path remains untested. VoxelXCOM is unchanged. Integration is separate and must not automatically generate cell files.

## Reproduction

From the workspace root:

```powershell
python output/poke_n/generate.py
$pokeNFiles = (Get-ChildItem -LiteralPath output/poke_n -Filter *.vox -File).FullName
python tools/inspect_vox.py $pokeNFiles --output output/poke_n/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_n/qa --script res://preview.gd --rendering-method gl_compatibility
python output/poke_n/compose_previews.py
python output/poke_n/validate.py
```

Automated renders launch hidden and capture qa/render.log and qa/render-errors.log. Generation uses standard Python; composition uses Pillow. Local generate.py, sculpt.py and voxlib.py, source regions, original image and pinned palette are the authoring dependencies. The generator owns only its 28 named outputs and manifest and refuses unknown or edited existing models unless `--replace-generated` is deliberately supplied. Preserve hand edits before overriding. After revisions, refresh audits, renders, comparisons and visual-review records. Keep future poke_n files directly in this folder with distinct filenames.


## Lights (2026-10-28)

[PokeN_TealStreetlight](lights/README.md): seven complete variations with Emit materials, source notes, day/night previews and runtime validation.


## Rocks (2026-10-28)

[2 rock appearances, 14 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.

- [Flowers, bushes and grass](vegetation/README.md): 6 new appearances, 42 complete models, and existing-family reuse links.

## Buildings (2026-11-03)

- [Three buildings, 21 complete models](buildings/README.md): `PokeN_RedHouse` (the red house, two copies), `PokeN_Chalet` (the house at the top, an L with an A-frame block) and `PokeN_RoofedGate` (the roofed gate over the path, modelled at the user's choice), each in Base and all six variations, made on VCOM's tile grid at game scale (closed doors, MagicaVoxel Glass windows) as the poke_m buildings are, and tested in a copy of the game. [Overview](buildings/overview.png) | [File index](buildings/FILES.md).


## Outdoor stairs — 2026-11-03

Added 1 families / 7 complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.

## Terrain (2026-11-04)

- [2 terrain styles, 98 complete models](terrain/README.md): `PokeN_EarthCliff_H2 (2 levels)`, `PokeN_RedRockCliff_H9 (9 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
