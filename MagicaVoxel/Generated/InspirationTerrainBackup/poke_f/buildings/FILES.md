# poke_f buildings: file index

[Overview](overview.png) | [Notes](README.md) | [Manifest](manifest.json) | [Validation](validation-summary.json) | [Source catalogue](reference/catalogue.png)

The 28 models are in `output/poke_f/`.

## PokeF_BlueHouse

Blue house. Six copies of the blue-roofed house, four of them in two pairs side by side, the right one a tile further back: a front gable of dark timber with two small windows, two chimneys, a blue door, a double window over flower boxes.

[All seven treatments in the game](previews/PokeF_BlueHouse_family.png) | [Four sides, Base and Cartoon](previews/PokeF_BlueHouse_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeF_BlueHouse_ingame.png) | [Beside the art](previews/PokeF_BlueHouse_art.png) | [Source crop](reference/PokeF_BlueHouse_1.png)

- [Base](../PokeF_BlueHouse.vox)
- [Cartoon](../PokeF_BlueHouse_Cartoon.vox)
- [CratePalette](../PokeF_BlueHouse_CratePalette.vox)
- [TwoColor](../PokeF_BlueHouse_TwoColor.vox)
- [Cartoon_TwoColor](../PokeF_BlueHouse_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeF_BlueHouse_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeF_BlueHouse_Cartoon_CratePalette_TwoColor.vox)

## PokeF_DomeCenter

Domed centre. The building in the middle: the red dome of a Poke Ball (its band and button, as drawn) on a blue-panelled building with white walls, purple-blue windows, a glass double door under a dark blue canopy, banded wooden pillars at its corners.

[All seven treatments in the game](previews/PokeF_DomeCenter_family.png) | [Four sides, Base and Cartoon](previews/PokeF_DomeCenter_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeF_DomeCenter_ingame.png) | [Beside the art](previews/PokeF_DomeCenter_art.png) | [Source crop](reference/PokeF_DomeCenter_1.png)

- [Base](../PokeF_DomeCenter.vox)
- [Cartoon](../PokeF_DomeCenter_Cartoon.vox)
- [CratePalette](../PokeF_DomeCenter_CratePalette.vox)
- [TwoColor](../PokeF_DomeCenter_TwoColor.vox)
- [Cartoon_TwoColor](../PokeF_DomeCenter_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeF_DomeCenter_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeF_DomeCenter_Cartoon_CratePalette_TwoColor.vox)

## PokeF_RoundShop

Round shop. The round-cornered building by the pond: a low salmon-tiled roof, white panels in grey frames, a red band between its two storeys, a glass door, windows over planters of pink flowers.

[All seven treatments in the game](previews/PokeF_RoundShop_family.png) | [Four sides, Base and Cartoon](previews/PokeF_RoundShop_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeF_RoundShop_ingame.png) | [Beside the art](previews/PokeF_RoundShop_art.png) | [Source crop](reference/PokeF_RoundShop_1.png)

- [Base](../PokeF_RoundShop.vox)
- [Cartoon](../PokeF_RoundShop_Cartoon.vox)
- [CratePalette](../PokeF_RoundShop_CratePalette.vox)
- [TwoColor](../PokeF_RoundShop_TwoColor.vox)
- [Cartoon_TwoColor](../PokeF_RoundShop_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeF_RoundShop_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeF_RoundShop_Cartoon_CratePalette_TwoColor.vox)

## PokeF_TealHall

Teal hall. The teal building at the bottom right, its left third in view (the rest off the image or behind trees): a hipped teal roof in a brown parapet with a beige top, a white strip of windows over a beige band, a teal ground storey, a lower teal wing. Completed mirrored.

[All seven treatments in the game](previews/PokeF_TealHall_family.png) | [Four sides, Base and Cartoon](previews/PokeF_TealHall_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeF_TealHall_ingame.png) | [Beside the art](previews/PokeF_TealHall_art.png) | [Source crop](reference/PokeF_TealHall_1.png)

- [Base](../PokeF_TealHall.vox)
- [Cartoon](../PokeF_TealHall_Cartoon.vox)
- [CratePalette](../PokeF_TealHall_CratePalette.vox)
- [TwoColor](../PokeF_TealHall_TwoColor.vox)
- [Cartoon_TwoColor](../PokeF_TealHall_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeF_TealHall_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeF_TealHall_Cartoon_CratePalette_TwoColor.vox)

## Supporting files

- [generate.py](generate.py): writes and checks the 28 files and [manifest.json](manifest.json)
- [sculpt.py](sculpt.py): the geometry, on the game's grid; [palettes.py](palettes.py): colours, groups, crate mapping; [voxlib.py](voxlib.py): VOX I/O
- [validate.py](validate.py): re-checks everything from disk, writes [validation-summary.json](validation-summary.json)
- [compare_art.py](compare_art.py): each Base in the art's projection beside the source; [compose_previews.py](compose_previews.py): the preview sheets from the game's renders
- [qa/cut_pieces.py](qa/cut_pieces.py), [qa/integration.py](qa/integration.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd), [qa/godot/whole_import.gd](qa/godot/whole_import.gd): the test in a copy of the game; results in [qa/integration-report.json](qa/integration-report.json) and [qa/whole-import.json](qa/whole-import.json)
- [structural-audit.json](structural-audit.json): `tools/inspect_vox.py` on the 28 files
- [preserved-hashes.json](preserved-hashes.json): ChatGPT's poke_f streetlight files, by hash
- [reference/](reference/): the source crops, [regions.json](reference/regions.json) and the [catalogue](reference/catalogue.png)
