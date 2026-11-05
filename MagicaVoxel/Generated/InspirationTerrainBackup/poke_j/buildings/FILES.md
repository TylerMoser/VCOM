# poke_j buildings: file index

[Overview](overview.png) | [Notes](README.md) | [Manifest](manifest.json) | [Validation](validation-summary.json) | [Source catalogue](reference/catalogue.png)

The 14 models are in `output/poke_j/`.

## PokeJ_RedHouse

Red house. Three copies of the red house: a steep red gable roof with its ridge front to back and wide eaves, a stone chimney at the back of its left slope, a half-timbered cream gable over a fan window, cream stone walls between dark posts, a beam, the red door in a dark frame and a window of four panes.

[All seven treatments in the game](previews/PokeJ_RedHouse_family.png) | [Four sides, Base and Cartoon](previews/PokeJ_RedHouse_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeJ_RedHouse_ingame.png) | [Beside the art](previews/PokeJ_RedHouse_art.png) | [Source crop 1](reference/PokeJ_RedHouse_1.png) | [Source crop 2](reference/PokeJ_RedHouse_2.png) | [Source crop 3](reference/PokeJ_RedHouse_3.png)

- [Base](../PokeJ_RedHouse.vox)
- [Cartoon](../PokeJ_RedHouse_Cartoon.vox)
- [CratePalette](../PokeJ_RedHouse_CratePalette.vox)
- [TwoColor](../PokeJ_RedHouse_TwoColor.vox)
- [Cartoon_TwoColor](../PokeJ_RedHouse_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeJ_RedHouse_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeJ_RedHouse_Cartoon_CratePalette_TwoColor.vox)

## PokeJ_GreyHouse

Grey house. The grey-roofed building at the top: three parts stepped front to back under flat grey roofs with standing seams and dark edges, the left part lower, a skylight and three white vents on the roofs, cream stone walls with white corner posts, the door under a long window, windows over flower boxes.

[All seven treatments in the game](previews/PokeJ_GreyHouse_family.png) | [Four sides, Base and Cartoon](previews/PokeJ_GreyHouse_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeJ_GreyHouse_ingame.png) | [Beside the art](previews/PokeJ_GreyHouse_art.png) | [Source crop](reference/PokeJ_GreyHouse_1.png)

- [Base](../PokeJ_GreyHouse.vox)
- [Cartoon](../PokeJ_GreyHouse_Cartoon.vox)
- [CratePalette](../PokeJ_GreyHouse_CratePalette.vox)
- [TwoColor](../PokeJ_GreyHouse_TwoColor.vox)
- [Cartoon_TwoColor](../PokeJ_GreyHouse_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeJ_GreyHouse_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeJ_GreyHouse_Cartoon_CratePalette_TwoColor.vox)

## Records

- [manifest.json](manifest.json): every file's hash, canvas, voxels, palette and glass; each family's footprint, doors, storeys, groups and crate picks.
- [validation-summary.json](validation-summary.json), [structural-audit.json](structural-audit.json), [qa/integration-report.json](qa/integration-report.json), [qa/whole-import.json](qa/whole-import.json), [preserved-hashes.json](preserved-hashes.json).
- [reference/regions.json](reference/regions.json): where the art draws each building.
- The scripts: [sculpt.py](sculpt.py), [palettes.py](palettes.py), [voxlib.py](voxlib.py), [generate.py](generate.py), [compare_art.py](compare_art.py), [compose_previews.py](compose_previews.py), [validate.py](validate.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/integration.py](qa/integration.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd), [qa/godot/whole_import.gd](qa/godot/whole_import.gd).
