# Pixelwood A ridge tent

Created 2026-10-28: **seven complete tent VOX files**, Base and all six established variations. Models are directly in output/pixelwood_a; this supporting folder holds the tent-only generator, manifest, previews and checks. Existing tree assets remain unchanged.

[Style comparison](comparison.png) | [Four-side geometry](geometry.png) | [Source crop](../reference/tent-source-enlarged.png) | [Manifest](manifest.json)

## Source interpretation and proportional size

Reference: [pixelwood_a.jpg](../../../pixelwood_a.jpg), tent near image center, approximately x=210-395 and y=180-390. The image enlarges underlying pixels roughly threefold: a displayed 48-pixel tile corresponds to 16 voxels. The tent spans approximately 60 original pixels across, including supports. The model canvas is **64 x 64 x 32**, or **4 x 4 x 2 tiles**. Its occupied bounds are x=2..61, y=2..61, z=0..31: **60 x 60 x 32** voxels. The cloth spans 56 voxels across and along its ridge, with an apex around z=29 and exposed wooden caps at z=31.

The sprite shows two canvas slopes, a long highlighted ridge, a triangular front wall and entrance, narrow openings on both slopes with folded flaps, small corner supports, and warm cream/tan canvas. Model depth and height are inferred together from an oblique view: at about 45 degrees, a 56-voxel ridge projects about 40 pixels vertically, while the front triangle projects about 20. This approximates the sprite's ratio of roof length to front-wall height. These are authoring estimates, not recovered original 3D dimensions.

Front is local **-Y**, corresponding to Godot **+Z**. MagicaVoxel is Z-up. Ground is z=0; scene translation is `0 0 16`; Mesh import scale is 0.0625. The front and rear are deliberately different.

## Construction and inferred details

The tent is a hollow, connected shell, not a solid wedge. Two-voxel cloth thickness keeps sloping steps face-connected. The entrance is an actual triangular opening; both roof-side vents are holes through the fabric, with narrow raised flaps at their edges. No black polygons fill the openings. Broad folds, a stitched ridge, short corner stakes, an internal ridge beam and a rear upright complete the structure.

The source cannot establish the rear, interior framing or floor. The rear is inferred closed, the ridge supported internally, and a one-voxel dark fabric groundsheet makes the interior read as the dark space visible in the source. It remains a surface over a hollow room. Its dark color represents shaded interior cloth in the source-inspired treatments; it is not a third material. The source ground shadow is not included in the voxel geometry. Stake positions are attached to the low eaves for connectivity; no unsupported guy ropes are invented.

## Variations and semantic groups

Cartoon regularizes fold placement and left/right paint, using exact bilateral reflection **(x,y,z) -> (63-x,y,z)**. Four-way rotational symmetry would confuse the entrance and rear, so it is intentionally not used. Cartoon preserves the footprint, doorway, vents, ground plane, apex and building orientation.

The two material groups are **canvas** (all panels, hems, vent flaps, ridge seam and groundsheet, source indices 1-6) and **wood** (stakes, upright, ridge beam and caps, indices 7-9). Every TwoColor file stores one cream color for all canvas and one brown for all wood, including interior surfaces. This removes the dark painted groundsheet, so openings have less contrast in lit TwoColor previews; they remain geometrically open. Do not add black as a third color to compensate.

CratePalette copies the full pinned [crate palette](../../../knowledge/palettes/crate-palette.json) byte-for-byte and chooses nearest RGB entries from indices 1-254 for this warm fabric/wood palette. Exact mappings and two-color representatives are saved in the manifest. Index 255 is unused. Both crate/two-color mixtures reuse the same two colors. All color-only variants preserve every occupied coordinate of their designated Base or Cartoon geometry source. See the [shared variation specification](../../../knowledge/VARIATIONS.md).

## Files

- [Base](../PixelwoodA_Tent.vox)
- [Cartoon](../PixelwoodA_Tent_Cartoon.vox)
- [CratePalette](../PixelwoodA_Tent_CratePalette.vox)
- [TwoColor](../PixelwoodA_Tent_TwoColor.vox)
- [Cartoon_TwoColor](../PixelwoodA_Tent_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PixelwoodA_Tent_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PixelwoodA_Tent_Cartoon_CratePalette_TwoColor.vox)

## Validation and game integration

[Binary audit](structural-audit.json) reports seven files with zero errors or warnings. [Godot report](godot-validation.json) records imports through the current VCOM whole-model Mesh importer at 0.0625, retained voxel counts, and grounded bounds. [Final validation](validation-summary.json) records hashes and visual review. The existing local importer and license in ../qa are reused; its source hashes are in ../qa/source-provenance.json.

validate.py checks serialized recolor geometry, exact bilateral occupancy and paint, two-color material assignments, crate palette identity, connectivity, open doorway, hollow room, side vents, floor/rear positions and preservation of all 28 pre-existing tree files. All seven treatments and four cardinal views of Base/Cartoon were reviewed under matched camera and lighting. The source comparison is perspective guidance rather than a pixel-perfect projection reconstruction.

Gameplay, collision, navigation, cover, cutaway and destruction are **not tested or integrated**. The model exceeds the single-cell 16-cubed PieceKind contract. Occupied X width is 60, below the separate loose-model 62-voxel limit, but that runtime path was not exercised. An open voxel doorway does not automatically make a walkable game entrance, and its clearance must be evaluated against game units. VoxelXCOM was not changed. Do not generate per-cell files automatically.

## Reproduction and future edits

```powershell
python output/pixelwood_a/tent/generate.py
$tentFiles = (Get-ChildItem -LiteralPath output/pixelwood_a -Filter 'PixelwoodA_Tent*.vox' -File).FullName
python tools/inspect_vox.py $tentFiles --output output/pixelwood_a/tent/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/pixelwood_a/qa --script res://tent_preview.gd
python output/pixelwood_a/tent/compose_previews.py
python output/pixelwood_a/tent/validate.py
```

Automated rendering launches hidden, logging to qa/tent-render.log and qa/tent-render-errors.log. Generation uses standard Python, local ../voxlib.py, the original image and pinned palette; composition uses Pillow. Generator owns only seven PixelwoodA_Tent filenames plus its own manifest. It refuses unknown/edited models unless `--replace-generated` is deliberately supplied. Preserve hand edits first, then rebuild dependent variants and refresh all audits, renders and review records. The tree generator and manifest remain independent.
