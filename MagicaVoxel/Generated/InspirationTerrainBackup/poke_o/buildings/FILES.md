# poke_o buildings: file index

[Overview](overview.png) | [Notes](README.md) | [Manifest](manifest.json) | [Validation](validation-summary.json) | [Source catalogue](reference/catalogue.png)

The 21 models are in `output/poke_o/`.

## PokeO_GableHouse

Gabled house. Three copies of the gabled house: a pink front gable roof with its ridge front to back in stripes under a light band, a dormer with a triangular window on its left slope, a khaki gable with a small window over a light board, cream walls, the red door and a window, a teal strip along the foot.

[All seven treatments in the game](previews/PokeO_GableHouse_family.png) | [Four sides, Base and Cartoon](previews/PokeO_GableHouse_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeO_GableHouse_ingame.png) | [Beside the art](previews/PokeO_GableHouse_art.png) | [Source crop 1](reference/PokeO_GableHouse_1.png) | [Source crop 2](reference/PokeO_GableHouse_2.png) | [Source crop 3](reference/PokeO_GableHouse_3.png)

- [Base](../PokeO_GableHouse.vox)
- [Cartoon](../PokeO_GableHouse_Cartoon.vox)
- [CratePalette](../PokeO_GableHouse_CratePalette.vox)
- [TwoColor](../PokeO_GableHouse_TwoColor.vox)
- [Cartoon_TwoColor](../PokeO_GableHouse_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeO_GableHouse_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeO_GableHouse_Cartoon_CratePalette_TwoColor.vox)

## PokeO_SkylightHouse

Skylight house. Two copies of the skylight house: a pink split roof, flat on the right with a skylight in it and on the left a facet in courses sloping down to its eave; a band of wall with a small high window under its front edge, a light board, cream walls, the red door and a window, a teal strip along the foot.

[All seven treatments in the game](previews/PokeO_SkylightHouse_family.png) | [Four sides, Base and Cartoon](previews/PokeO_SkylightHouse_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeO_SkylightHouse_ingame.png) | [Beside the art](previews/PokeO_SkylightHouse_art.png) | [Source crop 1](reference/PokeO_SkylightHouse_1.png) | [Source crop 2](reference/PokeO_SkylightHouse_2.png)

- [Base](../PokeO_SkylightHouse.vox)
- [Cartoon](../PokeO_SkylightHouse_Cartoon.vox)
- [CratePalette](../PokeO_SkylightHouse_CratePalette.vox)
- [TwoColor](../PokeO_SkylightHouse_TwoColor.vox)
- [Cartoon_TwoColor](../PokeO_SkylightHouse_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeO_SkylightHouse_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeO_SkylightHouse_Cartoon_CratePalette_TwoColor.vox)

## PokeO_WideHouse

Wide house. The wide house at the top right: the skylight house's split roof six tiles wide with two grey rooftop units on its flat part; in front of its middle a wing under a lower split roof, the red door in it, a mailbox and a small tree before it; two high windows over a window on the main block's front, cream walls, a teal strip along the foot.

[All seven treatments in the game](previews/PokeO_WideHouse_family.png) | [Four sides, Base and Cartoon](previews/PokeO_WideHouse_geometry.png) | [Game camera, cut away, dusk, night](previews/PokeO_WideHouse_ingame.png) | [Beside the art](previews/PokeO_WideHouse_art.png) | [Source crop](reference/PokeO_WideHouse_1.png)

- [Base](../PokeO_WideHouse.vox)
- [Cartoon](../PokeO_WideHouse_Cartoon.vox)
- [CratePalette](../PokeO_WideHouse_CratePalette.vox)
- [TwoColor](../PokeO_WideHouse_TwoColor.vox)
- [Cartoon_TwoColor](../PokeO_WideHouse_Cartoon_TwoColor.vox)
- [CratePalette_TwoColor](../PokeO_WideHouse_CratePalette_TwoColor.vox)
- [Cartoon_CratePalette_TwoColor](../PokeO_WideHouse_Cartoon_CratePalette_TwoColor.vox)

## Records

- [manifest.json](manifest.json): every file's hash, canvas, voxels, palette and glass; each family's footprint, doors, storeys, groups and crate picks.
- [validation-summary.json](validation-summary.json), [structural-audit.json](structural-audit.json), [qa/integration-report.json](qa/integration-report.json), [qa/whole-import.json](qa/whole-import.json), [preserved-hashes.json](preserved-hashes.json).
- [reference/regions.json](reference/regions.json): where the art draws each building.
- The scripts: [sculpt.py](sculpt.py), [palettes.py](palettes.py), [voxlib.py](voxlib.py), [generate.py](generate.py), [compare_art.py](compare_art.py), [compose_previews.py](compose_previews.py), [validate.py](validate.py), [qa/cut_pieces.py](qa/cut_pieces.py), [qa/integration.py](qa/integration.py), [qa/godot/building_probe.gd](qa/godot/building_probe.gd), [qa/godot/whole_import.gd](qa/godot/whole_import.gd).
