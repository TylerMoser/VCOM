# poke_h buildings: file index

[Overview](overview.png) | [Notes](README.md) | [Manifest](manifest.json) | [Validation](validation-summary.json) | [Source catalogue](reference/catalogue.png)

The 7 models are in `output/poke_h/`.

## PokeH_Farmhouse

Farmhouse. The farmhouse in the middle of the fields: poke_b's flower cottage drawn again with a porch across its front, a shingled roof on two posts wrapped in flowering vines, vines up its outside stair; the red bell-cast roof with two roof lights, cream walls, flower boxes under the upper windows, the teal door and the bay window under the porch.

[All seven treatments in the game](previews/PokeH_Farmhouse_family.png) | [Four sides, Base and Cartoon](previews/PokeH_Farmhouse_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeH_Farmhouse_ingame.png) | [Beside the art](previews/PokeH_Farmhouse_art.png) | [Source crop](reference/PokeH_Farmhouse_1.png)

- [Base](../PokeH_Farmhouse.vox)
- [Cartoon](../PokeH_Farmhouse_Cartoon.vox)
- [CratePalette](../PokeH_Farmhouse_CratePalette.vox)
- [TwoColor](../PokeH_Farmhouse_TwoColor.vox)
- [Cartoon_TwoColor](../PokeH_Farmhouse_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeH_Farmhouse_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeH_Farmhouse_Cartoon_CratePalette_TwoColor.vox)

## Records

- [manifest.json](manifest.json): every file's hash, canvas, voxels, palette and glass; each family's footprint, doors, storeys, groups and crate picks.
- [validation-summary.json](validation-summary.json), [structural-audit.json](structural-audit.json), [qa/integration-report.json](qa/integration-report.json), [qa/whole-import.json](qa/whole-import.json), [preserved-hashes.json](preserved-hashes.json).
- [reference/regions.json](reference/regions.json): where the art draws each building.
- The scripts: [sculpt.py](sculpt.py), [palettes.py](palettes.py), [voxlib.py](voxlib.py), [generate.py](generate.py), [compare_art.py](compare_art.py), [compose_previews.py](compose_previews.py), [validate.py](validate.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/integration.py](qa/integration.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd), [qa/godot/whole_import.gd](qa/godot/whole_import.gd).
