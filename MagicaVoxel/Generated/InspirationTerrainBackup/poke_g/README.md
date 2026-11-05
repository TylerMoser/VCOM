# poke_g tree collection

Created 2026-10-27: **21 complete VOX files**, three tree types with Base and all six established variations. No cell-by-cell files or brush packages.

[Overview](overview.png) | [Complete file index](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)

## Reference interpretation and scale

[poke_g.png](../../poke_g.png) is 560 x 768, consistent with 35 x 48 tiles at 16 pixels per tile. Use approximately one pixel per voxel and 16 voxels per game tile. Canvas width and height approximate the visible sprite; square depth and unseen branches are inferred. The top-down projection mixes height and crown depth, so dimensions are relative authoring estimates, not a unique physical reconstruction.

The image repeats three identifiable types: a broad dark olive crown, a brighter crown with distinct overlapping leaf tiers, and a slender layered sapling. Dark trees of apparently different heights were compared in enlarged contextual crops and treated as repeated placements/occlusion of the same broad-crown sprite. The models exclude ground shadows, flowers, shrubs, logs and adjacent trees. Names describe appearance, not botanical species.

| Base model | Canvas XYZ | Base occupied XYZ | Canvas tiles XYZ | Family comparison |
| --- | --- | --- | --- | --- |
| [BroadCrown](PokeG_BroadCrown.vox) | 32 x 32 x 40 | 31 x 31 x 40 | 2.0 x 2.0 x 2.5 | [Seven treatments](previews/PokeG_BroadCrown_family.png) |
| [TieredCrown](PokeG_TieredCrown.vox) | 32 x 32 x 36 | 31 x 31 x 36 | 2.0 x 2.0 x 2.25 | [Seven treatments](previews/PokeG_TieredCrown_family.png) |
| [Sapling](PokeG_Sapling.vox) | 12 x 12 x 28 | 11 x 11 x 28 | 0.75 x 0.75 x 1.75 | [Seven treatments](previews/PokeG_Sapling_family.png) |

Source-region boxes are contextual crops with top-left image XY and exclusive right/bottom edges; they are not exact masks. Canvas and occupied extents are separately recorded for every output in the manifest. Preview cards are individually framed across families. All models use Z-up, ground at z=0, horizontal canvas-centered pivot, no mandatory front, and scene translation `0 0 floor(height/2)`. Godot Mesh scale is 0.0625.

## Shape and palette decisions

BroadCrown has a full lower canopy and broad rounded shoulders, with muted dark olive foliage. TieredCrown is slightly shorter with more distinct leaf skirts and yellow-green highlights. Sapling has a narrow upright silhouette and several small leaf tiers above a short trunk. Base silhouettes have restrained asymmetry and clustered paint. Cartoon makes the crown and paint exactly quarter-turn symmetric, with cleaner color regions. Interiors are filled, with continuous hidden wood and grounded roots; these are volumetric reconstructions, not flat extrusions.

The palettes are artistic approximations of the source. Foliage and wood are explicit semantic groups, including internal voxels. Original leaf indices are 1-6 and wood indices 7-9; this is local generator bookkeeping, not a rule for external assets. There are no fruit/flower ornaments in this image.

## Variation families

Follow [the shared variation specification](../../knowledge/VARIATIONS.md). Each family has Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Color-only variants retain the exact coordinates, dimensions and placement of their Base or Cartoon authority. TwoColor uses one foliage color and one wood color, exactly two occupied palette indices with distinct RGBA values; lighting still shades the rendered faces.

CratePalette retains the entire pinned [crate RGBA snapshot](../../knowledge/palettes/crate-palette.json) byte-for-byte. Greens map to 241-246 and bark to crate browns 178-180. Exact mappings, representative colors, chosen game indices and source hashes are recorded in manifest.json. Both crate/two-color mixtures share their family selections. Reserved palette index 255 is unused.

## Validation and integration scope

[Structural audit](structural-audit.json): 21 files, zero errors and zero warnings. Generation rereads serialized files and checks dimensions, bounds, indices, connectivity, recolor occupancy, Cartoon symmetry, exact reference palette hashes and two-color counts. Every model is one six-connected component.

[Godot validation](godot-validation.json) records current VCOM whole-model Mesh import at scale 0.0625, retained voxel counts and grounded bounds. The importer is copied into QA with its license and [source hashes](qa/source-provenance.json). [Validation summary](validation-summary.json) records final hashes and visual review evidence. All styles have matched-camera previews, and Base/Cartoon have four azimuths for geometry review.

This checks the binary and whole-model importer/render path. It does not establish combat-map integration, movement, cover, destruction or MagicaVoxel GUI behavior. All models exceed the single-cell PieceKind 16-cubed contract in height. Their widths are below the loose-model limit of 62, but that separate runtime path is untested. VoxelXCOM remains unchanged; integrate separately when requested without automatically creating cell parts.

## Reproduce and continue

From the workspace root:

```powershell
python output/poke_g/generate.py
$pokeGFiles = (Get-ChildItem -LiteralPath output/poke_g -Filter *.vox -File).FullName
python tools/inspect_vox.py $pokeGFiles --output output/poke_g/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_g/qa --script res://preview.gd --rendering-method gl_compatibility
python output/poke_g/compose_previews.py
```

Automated rendering uses Start-Process with WindowStyle Hidden and captures `qa/render.log` and `qa/render-errors.log`. Generation requires standard Python; composition requires Pillow. `generate.py` owns family/palette/variation definitions and checks; `sculpt.py` owns profiles and geometry; `voxlib.py` is the local VOX helper. No runtime import of another source-image folder is required.

The generator checks existing VOX hashes against the preceding manifest and refuses unknown or hand-edited files unless `--replace-generated` is deliberately supplied. Preserve hand edits before using that override. It rewrites its named models and manifest; rendering/composition refresh their own outputs. After revisions, refresh validation evidence and review summary. Keep future poke_g assets directly in this folder with distinct filenames.


## Lights (2026-10-28)

[PokeG_RoundStreetlight](lights/README.md): seven complete variations with Emit materials, source notes, day/night previews and runtime validation.


## Rocks (2026-10-28)

[2 rock appearances, 14 complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.

## Buildings (2026-10-29)

- [Seven buildings, 49 complete models](buildings/README.md): `PokeG_GreenHouse` and `PokeG_GreenHouseMirrored` (the stepped green house, three copies in the art, one drawn mirrored), `PokeG_GreenWideHouse` (four copies), `PokeG_DomeCenter` (poke_f's domed centre drawn again in red-brown tiles, its Poke Ball as drawn), `PokeG_RedCenter` (its Poke Ball emblem as drawn), `PokeG_Mart` (its MART sign as drawn) and `PokeG_WoodLodge`, each in Base and all six variations, made on VCOM's tile grid at game scale (storeys, closed doors, MagicaVoxel Glass windows) as the poke_f buildings are, and tested in a copy of the game. [Overview](buildings/overview.png) | [File index](buildings/FILES.md).

- [Flowers, bushes and grass](vegetation/README.md): 4 new appearances, 28 complete models, and existing-family reuse links.


## Outdoor stairs — 2026-11-03

Added 2 families / 14 complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.

## Terrain (2026-11-04)

- [1 terrain style, 49 complete models](terrain/README.md): `PokeG_RockLedge_H2 (2 levels)`, modular kits of this image's ground shapes on VCOM's grid (the fill, straight faces, outer and inner corners, ridges, ridge ends, pillars and the extras drawn), each piece in Base and all six variations, heights as drawn in whole levels, tested in a copy of the game. [Previews](terrain/previews/) | [Collection](../terrain/README.md).
