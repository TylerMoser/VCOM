# poke_n buildings: file index

[Overview](overview.png) | [Notes](README.md) | [Manifest](manifest.json) | [Validation](validation-summary.json) | [Source catalogue](reference/catalogue.png)

The 21 models are in `output/poke_n/`.

## PokeN_RedHouse

Red house. Two copies of the red house: a steep red gable roof with its ridge front to back under a light band, grey verges, a shed dormer on its right slope and a brick chimney at its back, the upper floor's two wide windows over flower boxes between dark timbers, a dark beam, the ground floor's cream walls between stone quoins, a bay window under a red awning and the blue double door.

[All seven treatments in the game](previews/PokeN_RedHouse_family.png) | [Four sides, Base and Cartoon](previews/PokeN_RedHouse_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeN_RedHouse_ingame.png) | [Beside the art](previews/PokeN_RedHouse_art.png) | [Source crop 1](reference/PokeN_RedHouse_1.png) | [Source crop 2](reference/PokeN_RedHouse_2.png)

- [Base](../PokeN_RedHouse.vox)
- [Cartoon](../PokeN_RedHouse_Cartoon.vox)
- [CratePalette](../PokeN_RedHouse_CratePalette.vox)
- [TwoColor](../PokeN_RedHouse_TwoColor.vox)
- [Cartoon_TwoColor](../PokeN_RedHouse_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeN_RedHouse_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeN_RedHouse_Cartoon_CratePalette_TwoColor.vox)

## PokeN_Chalet

Chalet. The house at the top: a wing on the left under a steep hipped roof with a white fascia, its door with a pane and a lamp beside it; an A-frame block a tile forward on the right under a very steep gable with a flat top, its cream gable with dark braces and three windows under a white verge, two windows below between timber posts; a tall pale chimney down its right slope.

[All seven treatments in the game](previews/PokeN_Chalet_family.png) | [Four sides, Base and Cartoon](previews/PokeN_Chalet_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeN_Chalet_ingame.png) | [Beside the art](previews/PokeN_Chalet_art.png) | [Source crop](reference/PokeN_Chalet_1.png)

- [Base](../PokeN_Chalet.vox)
- [Cartoon](../PokeN_Chalet_Cartoon.vox)
- [CratePalette](../PokeN_Chalet_CratePalette.vox)
- [TwoColor](../PokeN_Chalet_TwoColor.vox)
- [Cartoon_TwoColor](../PokeN_Chalet_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeN_Chalet_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeN_Chalet_Cartoon_CratePalette_TwoColor.vox)

## PokeN_RoofedGate

Roofed gate. The gate over the path at the bottom: a low roof of brown planks under a dark cap on two dark posts, its shadow across the path; no walls.

[All seven treatments in the game](previews/PokeN_RoofedGate_family.png) | [Four sides, Base and Cartoon](previews/PokeN_RoofedGate_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeN_RoofedGate_ingame.png) | [Beside the art](previews/PokeN_RoofedGate_art.png) | [Source crop](reference/PokeN_RoofedGate_1.png)

- [Base](../PokeN_RoofedGate.vox)
- [Cartoon](../PokeN_RoofedGate_Cartoon.vox)
- [CratePalette](../PokeN_RoofedGate_CratePalette.vox)
- [TwoColor](../PokeN_RoofedGate_TwoColor.vox)
- [Cartoon_TwoColor](../PokeN_RoofedGate_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeN_RoofedGate_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeN_RoofedGate_Cartoon_CratePalette_TwoColor.vox)

## Records

- [manifest.json](manifest.json): every file's hash, canvas, voxels, palette and glass; each family's footprint, doors, storeys, groups and crate picks.
- [validation-summary.json](validation-summary.json), [structural-audit.json](structural-audit.json), [qa/integration-report.json](qa/integration-report.json), [qa/whole-import.json](qa/whole-import.json), [preserved-hashes.json](preserved-hashes.json).
- [reference/regions.json](reference/regions.json): where the art draws each building.
- The scripts: [sculpt.py](sculpt.py), [palettes.py](palettes.py), [voxlib.py](voxlib.py), [generate.py](generate.py), [compare_art.py](compare_art.py), [compose_previews.py](compose_previews.py), [validate.py](validate.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/integration.py](qa/integration.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd), [qa/godot/whole_import.gd](qa/godot/whole_import.gd).
