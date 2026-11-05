# poke_i buildings: file index

[Overview](overview.png) | [Notes](README.md) | [Manifest](manifest.json) | [Validation](validation-summary.json) | [Source catalogue](reference/catalogue.png)

The 21 models are in `output/poke_i/`.

## PokeI_SmallHouse

Small house. Three copies of the small house: an orange gable roof with its ridge front to back, a light band along the ridge and a light batten across its left slope, a gable of dark boards, brown board walls, the red door and a window in a white frame.

[All seven treatments in the game](previews/PokeI_SmallHouse_family.png) | [Four sides, Base and Cartoon](previews/PokeI_SmallHouse_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeI_SmallHouse_ingame.png) | [Beside the art](previews/PokeI_SmallHouse_art.png) | [Source crop 1](reference/PokeI_SmallHouse_1.png) | [Source crop 2](reference/PokeI_SmallHouse_2.png) | [Source crop 3](reference/PokeI_SmallHouse_3.png)

- [Base](../PokeI_SmallHouse.vox)
- [Cartoon](../PokeI_SmallHouse_Cartoon.vox)
- [CratePalette](../PokeI_SmallHouse_CratePalette.vox)
- [TwoColor](../PokeI_SmallHouse_TwoColor.vox)
- [Cartoon_TwoColor](../PokeI_SmallHouse_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeI_SmallHouse_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeI_SmallHouse_Cartoon_CratePalette_TwoColor.vox)

## PokeI_ChimneyHouse

Chimney house. Two copies of the house with the chimney: a steep orange gable roof, a stone chimney on its right slope, a cream gable with two windows and dark boards under the ridge, brown board walls, a beam, the red door and a window in a cream panel.

[All seven treatments in the game](previews/PokeI_ChimneyHouse_family.png) | [Four sides, Base and Cartoon](previews/PokeI_ChimneyHouse_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeI_ChimneyHouse_ingame.png) | [Beside the art](previews/PokeI_ChimneyHouse_art.png) | [Source crop 1](reference/PokeI_ChimneyHouse_1.png) | [Source crop 2](reference/PokeI_ChimneyHouse_2.png)

- [Base](../PokeI_ChimneyHouse.vox)
- [Cartoon](../PokeI_ChimneyHouse_Cartoon.vox)
- [CratePalette](../PokeI_ChimneyHouse_CratePalette.vox)
- [TwoColor](../PokeI_ChimneyHouse_TwoColor.vox)
- [Cartoon_TwoColor](../PokeI_ChimneyHouse_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeI_ChimneyHouse_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeI_ChimneyHouse_Cartoon_CratePalette_TwoColor.vox)

## PokeI_DayCare

Day care. The large building at the top by its fenced yard: a hall whose middle rises in a clerestory with a flat top and two light rails, hipped roofs of orange tiles over its sides and over a wing on its right, cream walls between dark timber posts, the double door of dark glass under a tiled canopy, windows.

[All seven treatments in the game](previews/PokeI_DayCare_family.png) | [Four sides, Base and Cartoon](previews/PokeI_DayCare_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeI_DayCare_ingame.png) | [Beside the art](previews/PokeI_DayCare_art.png) | [Source crop](reference/PokeI_DayCare_1.png)

- [Base](../PokeI_DayCare.vox)
- [Cartoon](../PokeI_DayCare_Cartoon.vox)
- [CratePalette](../PokeI_DayCare_CratePalette.vox)
- [TwoColor](../PokeI_DayCare_TwoColor.vox)
- [Cartoon_TwoColor](../PokeI_DayCare_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeI_DayCare_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeI_DayCare_Cartoon_CratePalette_TwoColor.vox)

## Records

- [manifest.json](manifest.json): every file's hash, canvas, voxels, palette and glass; each family's footprint, doors, storeys, groups and crate picks.
- [validation-summary.json](validation-summary.json), [structural-audit.json](structural-audit.json), [qa/integration-report.json](qa/integration-report.json), [qa/whole-import.json](qa/whole-import.json), [preserved-hashes.json](preserved-hashes.json).
- [reference/regions.json](reference/regions.json): where the art draws each building.
- The scripts: [sculpt.py](sculpt.py), [palettes.py](palettes.py), [voxlib.py](voxlib.py), [generate.py](generate.py), [compare_art.py](compare_art.py), [compose_previews.py](compose_previews.py), [validate.py](validate.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/integration.py](qa/integration.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd), [qa/godot/whole_import.gd](qa/godot/whole_import.gd).
