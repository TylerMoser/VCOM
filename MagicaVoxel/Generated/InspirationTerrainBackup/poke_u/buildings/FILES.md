# poke_u buildings: file index

[Overview](overview.png) | [Notes](README.md) | [Manifest](manifest.json) | [Validation](validation-summary.json) | [Source catalogue](reference/catalogue.png)

The 14 models are in `output/poke_u/`.

## PokeU_Cottage

Cottage. Three copies of the cottage: a steep gable roof of red tiles with its ridge front to back; a timber frame at the front, posts standing out from the corners under a beam across it, the gable over it dark between a post under the ridge and two braces, two windows in it; cream walls; the red door with a window, two windows of two panes with flower boxes; two beige chimney stacks on the right slope.

[All seven treatments in the game](previews/PokeU_Cottage_family.png) | [Four sides, Base and Cartoon](previews/PokeU_Cottage_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeU_Cottage_ingame.png) | [Beside the art](previews/PokeU_Cottage_art.png) | [Source crop 1](reference/PokeU_Cottage_1.png) | [Source crop 2](reference/PokeU_Cottage_2.png) | [Source crop 3](reference/PokeU_Cottage_3.png)

- [Base](../PokeU_Cottage.vox)
- [Cartoon](../PokeU_Cottage_Cartoon.vox)
- [CratePalette](../PokeU_Cottage_CratePalette.vox)
- [TwoColor](../PokeU_Cottage_TwoColor.vox)
- [Cartoon_TwoColor](../PokeU_Cottage_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeU_Cottage_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeU_Cottage_Cartoon_CratePalette_TwoColor.vox)

## PokeU_WingHouse

Wing house. The big house at the right: a wing on the right a tile ahead of the rest under a gable roof of red tiles with its ridge front to back, its gable dark with a window of two panes over a beam on timber posts; the part to its left under a lean-to of red tiles, hipped at its left end, over a beam on a timber post, with the red door and a small window with a flower box; a window with a flower box in the wing (the rest of its front hidden by a tree); two beige chimney stacks on the wing's right slope.

[All seven treatments in the game](previews/PokeU_WingHouse_family.png) | [Four sides, Base and Cartoon](previews/PokeU_WingHouse_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeU_WingHouse_ingame.png) | [Beside the art](previews/PokeU_WingHouse_art.png) | [Source crop](reference/PokeU_WingHouse_1.png)

- [Base](../PokeU_WingHouse.vox)
- [Cartoon](../PokeU_WingHouse_Cartoon.vox)
- [CratePalette](../PokeU_WingHouse_CratePalette.vox)
- [TwoColor](../PokeU_WingHouse_TwoColor.vox)
- [Cartoon_TwoColor](../PokeU_WingHouse_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeU_WingHouse_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeU_WingHouse_Cartoon_CratePalette_TwoColor.vox)

## Records

- [manifest.json](manifest.json): every file's hash, canvas, voxels, palette and glass; each family's footprint, doors, storeys, groups and crate picks.
- [validation-summary.json](validation-summary.json), [structural-audit.json](structural-audit.json), [qa/integration-report.json](qa/integration-report.json), [qa/whole-import.json](qa/whole-import.json), [preserved-hashes.json](preserved-hashes.json).
- [reference/regions.json](reference/regions.json): where the art draws each building.
- The scripts: [sculpt.py](sculpt.py), [palettes.py](palettes.py), [voxlib.py](voxlib.py), [generate.py](generate.py), [compare_art.py](compare_art.py), [compose_previews.py](compose_previews.py), [validate.py](validate.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/integration.py](qa/integration.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd), [qa/godot/whole_import.gd](qa/godot/whole_import.gd).
