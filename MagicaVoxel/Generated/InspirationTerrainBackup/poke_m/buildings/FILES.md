# poke_m buildings: file index

[Overview](overview.png) | [Notes](README.md) | [Manifest](manifest.json) | [Validation](validation-summary.json) | [Source catalogue](reference/catalogue.png)

The 14 models are in `output/poke_m/`.

## PokeM_LogCabin

Log cabin. The log cabin by the marsh: a steep gable roof of grey slates with its ridge front to back under a raised ridge cap, log walls whose side logs run out past the corners in round ends, a gable of dark boards over a light beam with a king post and rafters, the plank door and a window of two panes.

[All seven treatments in the game](previews/PokeM_LogCabin_family.png) | [Four sides, Base and Cartoon](previews/PokeM_LogCabin_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeM_LogCabin_ingame.png) | [Beside the art](previews/PokeM_LogCabin_art.png) | [Source crop](reference/PokeM_LogCabin_1.png)

- [Base](../PokeM_LogCabin.vox)
- [Cartoon](../PokeM_LogCabin_Cartoon.vox)
- [CratePalette](../PokeM_LogCabin_CratePalette.vox)
- [TwoColor](../PokeM_LogCabin_TwoColor.vox)
- [Cartoon_TwoColor](../PokeM_LogCabin_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeM_LogCabin_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeM_LogCabin_Cartoon_CratePalette_TwoColor.vox)

## PokeM_Lodge

Lodge. Two copies, each cut off by the image's edge: at the bottom left the front but for its left end, at the bottom only the roof, whole across. A skirt roof of brown boards over a dark fascia round cream brick walls between big timber corner posts, an upper part of light boards under a low gable roof with a light ridge board, a window and the door between two posts under a porch beam.

[All seven treatments in the game](previews/PokeM_Lodge_family.png) | [Four sides, Base and Cartoon](previews/PokeM_Lodge_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeM_Lodge_ingame.png) | [Beside the art](previews/PokeM_Lodge_art.png) | [Source crop 1](reference/PokeM_Lodge_1.png) | [Source crop 2](reference/PokeM_Lodge_2.png)

- [Base](../PokeM_Lodge.vox)
- [Cartoon](../PokeM_Lodge_Cartoon.vox)
- [CratePalette](../PokeM_Lodge_CratePalette.vox)
- [TwoColor](../PokeM_Lodge_TwoColor.vox)
- [Cartoon_TwoColor](../PokeM_Lodge_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeM_Lodge_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeM_Lodge_Cartoon_CratePalette_TwoColor.vox)

## Records

- [manifest.json](manifest.json): every file's hash, canvas, voxels, palette and glass; each family's footprint, doors, storeys, groups and crate picks.
- [validation-summary.json](validation-summary.json), [structural-audit.json](structural-audit.json), [qa/integration-report.json](qa/integration-report.json), [qa/whole-import.json](qa/whole-import.json), [preserved-hashes.json](preserved-hashes.json).
- [reference/regions.json](reference/regions.json): where the art draws each building.
- The scripts: [sculpt.py](sculpt.py), [palettes.py](palettes.py), [voxlib.py](voxlib.py), [generate.py](generate.py), [compare_art.py](compare_art.py), [compose_previews.py](compose_previews.py), [validate.py](validate.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/integration.py](qa/integration.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd), [qa/godot/whole_import.gd](qa/godot/whole_import.gd).
