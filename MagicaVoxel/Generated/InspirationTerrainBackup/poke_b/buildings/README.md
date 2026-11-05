# poke_b building collection

Created 2026-10-28. Six distinct building appearances, **42 complete VOX files**, each with Base and all six established variations. Final files are directly in output/poke_b; this supporting folder owns the building generators, manifests and previews. Existing tree assets remain separate.

[Overview](overview.png) | [Model index](FILES.md) | [Source catalogue](reference/catalogue.png) | [Manifest](manifest.json)

## Source identification and proportional scale

[poke_b.png](../../../poke_b.png) is a 656 x 960 pixel map on an apparent 16-pixel tile grid. Approximately one image pixel corresponds to one voxel, with 16 voxels per game tile. Six buildings are present: domed institutional lab, red-roof clinic, gray mansard house with stairs/door, gray mansard house with three front windows, cyan mansard house with stairs/door, and flower-box cottage with a right-hand timber annex. The two gray houses have different facades and therefore separate models. The cyan house is also retained as a source appearance rather than silently merging it with the gray entry house.

Building width follows the sprite footprint. Depth and height are inferred together from the oblique view, not by equating every vertical sprite pixel with world height. Canvases allow eaves, steps and roof fixtures; occupied bounds are recorded independently. Reconstruction is approximate, and hidden side/rear construction is intentionally simple. Trees, fences, mailbox/signposts, streets and neighboring garden patches are excluded.

| Building | Canvas XYZ | Base occupied XYZ | All styles | Four sides |
| --- | --- | --- | --- | --- |
| DomeLab | 120 x 104 x 112 | 116 x 94 x 111 | [Comparison](previews/PokeB_DomeLab_family.png) | [Geometry](previews/PokeB_DomeLab_geometry.png) |
| RedClinic | 104 x 96 x 64 | 98 x 88 x 57 | [Comparison](previews/PokeB_RedClinic_family.png) | [Geometry](previews/PokeB_RedClinic_geometry.png) |
| GrayEntryHouse | 80 x 80 x 80 | 76 x 72 x 80 | [Comparison](previews/PokeB_GrayEntryHouse_family.png) | [Geometry](previews/PokeB_GrayEntryHouse_geometry.png) |
| GrayWindowHouse | 80 x 80 x 80 | 76 x 57 x 80 | [Comparison](previews/PokeB_GrayWindowHouse_family.png) | [Geometry](previews/PokeB_GrayWindowHouse_geometry.png) |
| CyanEntryHouse | 80 x 80 x 80 | 76 x 72 x 80 | [Comparison](previews/PokeB_CyanEntryHouse_family.png) | [Geometry](previews/PokeB_CyanEntryHouse_geometry.png) |
| FlowerCottage | 104 x 88 x 72 | 97 x 74 x 64 | [Comparison](previews/PokeB_FlowerCottage_family.png) | [Geometry](previews/PokeB_FlowerCottage_geometry.png) |

All models are MagicaVoxel Z-up, local front -Y (Godot +Z), horizontal canvas-centered, grounded at z=0, with scene translation `0 0 floor(canvas height/2)` and Mesh scale 0.0625. No automatic single-cell splitting is performed.

## Building interpretations

- **DomeLab:** pale structural columns, paired front windows, central glazed door and wing-like plaque, low coral roof, blue glazed cylindrical drum and cream dome. The dome cap is filled for continuous support; the main building and drum space are hollow. The small emblem is a voxel interpretation, not exact text/vector recovery.
- **RedClinic:** rounded orange-red low roof, large blue skylight on the right, green facade, red entrance canopy, red/white circular emblem, central glazed entrance, right service door and small sign plate. Sign marks are simplified geometric marks.
- **GrayEntryHouse / CyanEntryHouse:** inset flat upper roof, sloping mansard sides, dormer-window band, three stepped roof projections, back-left roof vent, lower entry with paired windows, front stairs and pale rails. The two source roof colors are kept distinct.
- **GrayWindowHouse:** similar gray upper massing but three lower front windows and no invented front stairs or door. Unseen access is not modeled as a new source feature.
- **FlowerCottage:** terracotta pitched roof, left-slope rectangular fixtures, cream gable, paired blue windows and attached flower boxes, lower entry and projecting bay window with small red hoods, and a narrow timber annex/deck to the right. Rear/side construction and annex depth are inferred.

Ground-floor rooms are hollow above structural floors; doors are closed, glazing uses opaque blue materials, and walls/roof supports are face-connected. These are complete architectural assets, not functional door/window resources. No furniture, room program, gameplay navigation or destructible segmentation is invented.

## Treatments and material grouping

Each appearance includes Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. [Shared rules](../../../knowledge/VARIATIONS.md) apply. Cartoon uses a broader dome profile, more rounded clinic roof corners, broader mansard steps, and fewer raised cottage tile courses. It regularizes repeated architecture and broad paint regions while retaining source-specific asymmetric fixtures, doors, signs and annexes. These directional buildings do not claim full four-way rotational symmetry.

The two semantic groups are **primary body/structure** (indices 1-6: walls, floors, columns, trim and cream dome) and **roof/secondary accents** (7-19: roofing, blue glazing, secondary fixtures, colored signage and flower-box plants). TwoColor intentionally merges secondary materials into the family roof color: for example the lab windows become coral, clinic emblem accents red, and cottage flowers terracotta. It stores exactly two distinct used colors, not two plus glass/flowers. Every hidden voxel is classified by the same rules.

CratePalette copies the full pinned [crate palette](../../../knowledge/palettes/crate-palette.json) and chooses nearest RGB entries from indices 1-254 for each source shade. Exact maps and the two chosen game colors are recorded per family. Both crate/two-color mixtures reuse those representatives. Color-only treatments preserve the exact Base or Cartoon occupied set and placement; index 255 is never occupied. Lighting still shades flat TwoColor paint.

## Validation and game constraints

[Structural audit](structural-audit.json), [Godot report](godot-validation.json), and [final validation](validation-summary.json) cover the 42 building files only. They are separate from the older tree evidence. A fresh copy of current VCOM importer code is used in buildings/qa, with its license and [source hashes](importer-provenance.json). Whole Mesh imports run at 0.0625 and check retained voxel counts and grounded bounds. The family comparison sheets show all treatments; geometry sheets show four sides of Base and Cartoon under matched camera and lighting.

validate.py checks serialized dimensions, hashes, connectivity, exact recolor coordinates, semantic two-color assignment, palette identity, hollow ground-floor interiors, render evidence, previews and preservation of all 112 previous tree models. Structural inspection alone does not establish visual quality or gameplay compatibility.

All six buildings exceed the single-cell 16-cubed PieceKind contract, and their occupied widths exceed the separate loose-model 62-voxel X limit. The whole-model importer can preview these complete assets; battle-map integration, collision, cover, cutaway, doors, navigation and destruction are not tested. VoxelXCOM is unchanged. Preserve the requested size and design integration separately rather than shrinking or generating unsolicited cell files.

## Reproduction and continuation

```powershell
python output/poke_b/buildings/generate.py
$buildingFiles = (Get-Content output/poke_b/buildings/manifest.json -Raw | ConvertFrom-Json).models.file | ForEach-Object { Join-Path 'output/poke_b' $_ }
python tools/inspect_vox.py $buildingFiles --output output/poke_b/buildings/structural-audit.json
& "C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe" --path output/poke_b/buildings/qa --script res://preview.gd
python output/poke_b/buildings/compose_previews.py
python output/poke_b/buildings/validate.py
```

Automated rendering launches hidden with buildings/qa/render.log and buildings/qa/render-errors.log. Generator/sculptor use standard Python and local voxlib.py; preview composition uses Pillow. Inputs and geometry dependencies are hashed. Generator owns only these 42 filenames and its own manifest. Unknown/modified files require a deliberate `--replace-generated` override; preserve hand edits first. Refresh audits, renders and visual review after changes. Keep later building additions in this image folder without altering its existing tree generator/manifest.
