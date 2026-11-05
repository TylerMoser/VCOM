# Pixelwood B timber house

Created 2026-10-28: **seven complete house models**, Base and all six established variations. Final VOX files are directly in output/pixelwood_b. This house support folder contains independent generators, records and previews; existing trees are unchanged.

[Source and all styles](comparison.png) | [Four-side geometry](geometry.png) | [Source crop](source.png) | [Manifest](manifest.json)

## Source and size

The house in [pixelwood_b.gif](../../../pixelwood_b.gif) has green ribbed roof planes, a gray masonry chimney on the left, orange-brown horizontal timber walls, vertical gable planks, a round attic window, an arched door left of center, a large rectangular window to its right, and front steps. The lower facade includes a narrow vertical timber band. These intentional asymmetries remain in every treatment.

The GIF is 1210 x 1210 and enlarges its underlying pixel art fivefold. A displayed 80-pixel tile corresponds to 16 voxels. Roof width is about 400 displayed pixels, giving an 80-voxel width. Canvas is **80 x 80 x 80** (5 x 5 x 5 tiles); actual occupied extent is **80 x 74 x 80**, minimum [0, 1, 0], maximum [79, 74, 79]. Wall footprint is approximately 72 x 60 voxels, with projecting eaves and entry steps. Wall top is around z=34, roof ridge z=70 and chimney z=79. Projected roof depth and building height are inferred together from the oblique sprite, rather than interpreting its entire image height as vertical height.

The broad crop has two versions because frame 4 changes a small ground/fire-context patch below the house (x630..639, y790..799). The isolated house and entry-step regions are unchanged across all five frames ([animation record](animation-review.json)); frame 0 is the modeling reference. No separate animated house variant is required. Cropping coordinates are x=404..830, y=300..800 with exclusive upper edges. Nearby foliage, pavement and ground shadows are excluded.

Front is local **-Y**, Godot **+Z**. Models are Z-up, grounded at z=0, horizontally canvas-centered, scene translation `0 0 40`, recommended Mesh scale 0.0625. Height, unseen depth and hidden construction are approximations from 2D art, not measurements of an original 3D model.

## Construction and deliberate assumptions

The house has a hollow room above a plank floor, two-voxel walls, filled structural posts, stepped roof panels and raised standing ribs. The roof includes a dark fascia and ridge cap. The chimney has alternating masonry courses and an open upper flue. The door is **closed** and inset within its arched frame. Both front windows have dark, opaque recessed panes and timber crossbars; no unsupported game transparency is assumed. Front steps connect to the raised floor, and short foundation feet connect to the ground.

Side and rear walls are inferred closed timber walls. No extra side windows, back door, furnishings, fireplace or functional chimney system are invented. The rear gable is plain. Hidden floor, room and supports are reconstruction choices. The chimney is a connected architectural shell with a short open top, not a tested smoke/fire simulation.

## Variations

Cartoon uses fewer regular roof ribs, balanced roof paint, simpler timber tones and orderly masonry. It preserves the left chimney, left door and right window. Full bilateral or four-way symmetry would erase the source facade, so no full-model symmetry is claimed. The roof is checked for bilateral geometry/paint away from the chimney; asymmetric features are documented exceptions.

TwoColor uses exactly two semantic groups:

- **Timber structure:** wall boards, gables, door, frames, floor, supports and steps; source indices 1-6; warm brown representative.
- **Roof and secondary accents:** roof, fascia, chimney masonry and dark recessed glazing; indices 7-17; green representative.

This is a deliberate two-region reduction of a multi-material building: chimney and panes become green in TwoColor, while the Base/Cartoon treatments retain gray masonry and dark glazing. There is no third gray or black color in a TwoColor file. All material regions, including hidden interior surfaces, are assigned explicitly.

CratePalette copies the full pinned [reference RGBA palette](../../../knowledge/palettes/crate-palette.json) and maps each source shade to the nearest existing RGB entry in slots 1-254. Exact mapping and representative indices are in the manifest. No custom colors are introduced in those variants and index 255 remains unused. The two crate/two-color mixtures share identical representative selections. Every recolor preserves the exact occupied coordinates and placement of its Base or Cartoon authority. See [shared variation rules](../../../knowledge/VARIATIONS.md).

## Files

- [Base](../PixelwoodB_House.vox)
- [Cartoon](../PixelwoodB_House_Cartoon.vox)
- [CratePalette](../PixelwoodB_House_CratePalette.vox)
- [TwoColor](../PixelwoodB_House_TwoColor.vox)
- [Cartoon_TwoColor](../PixelwoodB_House_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PixelwoodB_House_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PixelwoodB_House_Cartoon_CratePalette_TwoColor.vox)

## Validation and integration

[Structural audit](structural-audit.json): seven files, zero errors and warnings. [Godot report](godot-validation.json): all seven imported/rendered with the current VCOM whole-model Mesh importer at 0.0625, voxel counts preserved and bounds grounded. The existing local importer copy, license and provenance at ../qa are reused. [Final record](validation-summary.json) pins final hashes and reviewed sheets.

validate.py checks serialized geometry and palette identity, connectedness, exact recolor coordinates, two-color group assignments, hollow room/floor, closed door, window panes, open flue, Cartoon roof balance, import counts and preservation of all 28 pre-existing tree files. All seven treatments and four sides of Base/Cartoon were visually reviewed under matched lighting and camera.

**Gameplay integration is not tested.** Occupied width is 80, exceeding both the single-cell 16-cubed PieceKind contract and the separate loose-model 62-voxel X limit. The complete art is valid for the whole-model importer; use a separately designed integration path rather than shrinking it and assuming runtime compatibility. Door interaction, navigation, cutaway, cover, destructibility and collision need game work. VoxelXCOM is unchanged. Do not automatically split the model into cell files.

## Reproduction and continuation

```powershell
python output/pixelwood_b/house/generate.py
$houseFiles = (Get-ChildItem -LiteralPath output/pixelwood_b -Filter 'PixelwoodB_House*.vox' -File).FullName
python tools/inspect_vox.py $houseFiles --output output/pixelwood_b/house/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/pixelwood_b/qa --script res://house_preview.gd
python output/pixelwood_b/house/compose_previews.py
python output/pixelwood_b/house/validate.py
```

Automated render runs launch hidden and record qa/house-render.log and qa/house-render-errors.log. Generator/sculptor use standard Python and ../voxlib.py; composition uses Pillow. Geometry, original image and palette dependencies are hashed. Only the seven house filenames and house manifest are owned by this generator. Unknown/modified models are protected unless `--replace-generated` is deliberately passed; preserve hand edits before overriding. Refresh audits, renders and visual review after a revision. Tree generation and its manifest remain independent.
