# poke_r buildings: file index

[Overview](overview.png) | [Notes](README.md) | [Manifest](manifest.json) | [Validation](validation-summary.json) | [Source catalogue](reference/catalogue.png)

The 14 models are in `output/poke_r/`.

## PokeR_RedHouse

Red house. Four copies of the red house: a steep red gable roof with its ridge front to back, darker lines down its slopes and a dark red verge; white siding, a white board across the front under the tall front gable with two windows and a louvred vent in it; the red door and a window of two panes on the ground floor, a blue strip along the foot, grey corner boards.

[All seven treatments in the game](previews/PokeR_RedHouse_family.png) | [Four sides, Base and Cartoon](previews/PokeR_RedHouse_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeR_RedHouse_ingame.png) | [Beside the art](previews/PokeR_RedHouse_art.png) | [Source crop 1](reference/PokeR_RedHouse_1.png) | [Source crop 2](reference/PokeR_RedHouse_2.png) | [Source crop 3](reference/PokeR_RedHouse_3.png) | [Source crop 4](reference/PokeR_RedHouse_4.png)

- [Base](../PokeR_RedHouse.vox)
- [Cartoon](../PokeR_RedHouse_Cartoon.vox)
- [CratePalette](../PokeR_RedHouse_CratePalette.vox)
- [TwoColor](../PokeR_RedHouse_TwoColor.vox)
- [Cartoon_TwoColor](../PokeR_RedHouse_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeR_RedHouse_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeR_RedHouse_Cartoon_CratePalette_TwoColor.vox)

## PokeR_Shop

Shop. The flat-roofed building at the right: cream walls with ochre bricks at the corners and an ochre band under the roof, three pairs of windows above and two below under red awnings, the green door with a round window between ochre pilasters; a flat roof of grey tiles inside a grey parapet, a tall red housing on it with a dark opening in its top.

[All seven treatments in the game](previews/PokeR_Shop_family.png) | [Four sides, Base and Cartoon](previews/PokeR_Shop_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeR_Shop_ingame.png) | [Beside the art](previews/PokeR_Shop_art.png) | [Source crop](reference/PokeR_Shop_1.png)

- [Base](../PokeR_Shop.vox)
- [Cartoon](../PokeR_Shop_Cartoon.vox)
- [CratePalette](../PokeR_Shop_CratePalette.vox)
- [TwoColor](../PokeR_Shop_TwoColor.vox)
- [Cartoon_TwoColor](../PokeR_Shop_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeR_Shop_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeR_Shop_Cartoon_CratePalette_TwoColor.vox)

## Records

- [manifest.json](manifest.json): every file's hash, canvas, voxels, palette and glass; each family's footprint, doors, storeys, groups and crate picks.
- [validation-summary.json](validation-summary.json), [structural-audit.json](structural-audit.json), [qa/integration-report.json](qa/integration-report.json), [qa/whole-import.json](qa/whole-import.json), [preserved-hashes.json](preserved-hashes.json).
- [reference/regions.json](reference/regions.json): where the art draws each building.
- The scripts: [sculpt.py](sculpt.py), [palettes.py](palettes.py), [voxlib.py](voxlib.py), [generate.py](generate.py), [compare_art.py](compare_art.py), [compose_previews.py](compose_previews.py), [validate.py](validate.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/integration.py](qa/integration.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd), [qa/godot/whole_import.gd](qa/godot/whole_import.gd).
