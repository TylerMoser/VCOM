# Rocks across the inspiration images

**462 complete VOX files**: seven treatments for **66 source appearances**, across 18 image folders. All 25 originals were reviewed. Repeated artwork is available in each corresponding source folder; [exact Base duplicates](duplicates.json) are recorded. No cell-by-cell exports.

[Overview](overview.png) · [Source catalogue](catalogue.json) · [Rock authoring instructions](../../knowledge/ROCKS.md)

## Models

Final models sit directly under `output/<source-image-stem>/`; the links below open source-specific model lists, reference crops and previews. Sizes are canvas X/Y/Z; exact occupied bounds and inferred scale are in the manifests.

| Source | Appearances | Models |
| --- | --- | --- |
| [mario.jpg](../mario/rocks/README.md) | 2 | 14 |
| [pixelwood_a.jpg](../pixelwood_a/rocks/README.md) | 4 | 28 |
| [pixelwood_b.gif](../pixelwood_b/rocks/README.md) | 4 | 28 |
| [pixelwood_c.jpg](../pixelwood_c/rocks/README.md) | 3 | 21 |
| [poke_a.jpg](../poke_a/rocks/README.md) | 1 | 7 |
| [poke_c.png](../poke_c/rocks/README.md) | 2 | 14 |
| [poke_d.png](../poke_d/rocks/README.md) | 4 | 28 |
| [poke_g.png](../poke_g/rocks/README.md) | 2 | 14 |
| [poke_h.png](../poke_h/rocks/README.md) | 2 | 14 |
| [poke_i.jpg](../poke_i/rocks/README.md) | 3 | 21 |
| [poke_l.png](../poke_l/rocks/README.md) | 6 | 42 |
| [poke_m.png](../poke_m/rocks/README.md) | 7 | 49 |
| [poke_n.png](../poke_n/rocks/README.md) | 2 | 14 |
| [poke_o.png](../poke_o/rocks/README.md) | 3 | 21 |
| [poke_p.png](../poke_p/rocks/README.md) | 4 | 28 |
| [poke_q.png](../poke_q/rocks/README.md) | 5 | 35 |
| [poke_s.jpg](../poke_s/rocks/README.md) | 4 | 28 |
| [poke_t.png](../poke_t/rocks/README.md) | 8 | 56 |

## Variations and materials

Every family has Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. The saved October 28 amendment applies: TwoColor is one flat color per meaningful material group. Plain rocks therefore use one color, mossy rocks two, and the red-crystal outcrop two. No shading colors are retained inside those groups. Natural render shading remains.

Crate variants retain the full pinned crate palette unchanged. All rocks and crystals are opaque diffuse; none is assigned unrequested emission or glass. Cartoon changes geometry and balances corresponding sides; it preserves the front of carved stacks and the crystal chamber.

## Review sheets

- Page 1: [all seven treatments](variations_01.png) · [Base/Cartoon from four directions](geometry_01.png)
- Page 2: [all seven treatments](variations_02.png) · [Base/Cartoon from four directions](geometry_02.png)
- Page 3: [all seven treatments](variations_03.png) · [Base/Cartoon from four directions](geometry_03.png)
- Page 4: [all seven treatments](variations_04.png) · [Base/Cartoon from four directions](geometry_04.png)
- Page 5: [all seven treatments](variations_05.png) · [Base/Cartoon from four directions](geometry_05.png)
- Page 6: [all seven treatments](variations_06.png) · [Base/Cartoon from four directions](geometry_06.png)
- Page 7: [all seven treatments](variations_07.png) · [Base/Cartoon from four directions](geometry_07.png)
- Page 8: [all seven treatments](variations_08.png) · [Base/Cartoon from four directions](geometry_08.png)
- Page 9: [all seven treatments](variations_09.png) · [Base/Cartoon from four directions](geometry_09.png)
- Page 10: [all seven treatments](variations_10.png) · [Base/Cartoon from four directions](geometry_10.png)
- Page 11: [all seven treatments](variations_11.png) · [Base/Cartoon from four directions](geometry_11.png)

## Coverage and interpretation

Modeled discrete stones, boulders, gravel, standing stones, layered rock piles, cave spires, carved stone stacks and crystal-bearing rock. Continuous cliff terrain, entire floating islands, paving and architecture are outside this prop set. Water references have complete inferred undersides but no water, foam or shadow geometry. Source projection and resized/compressed images make depth/height approximate.

- **poke_b.png**: No discrete loose rocks found; stone paving, continuous cliffs and house masonry excluded.
- **poke_e.png**: No discrete rocks found; shoreline is continuous terrain.
- **poke_f.png**: No discrete rocks found; central sculpted creature statue is not a natural rock.
- **poke_j.jpg**: No discrete rocks found; cliffs, buildings and garden edging are terrain/architecture.
- **poke_k.jpg**: No discrete rocks found; repeated cliff banks are continuous terrain.
- **poke_r.png**: No discrete rocks found; stairs, paving and continuous cliff edges excluded.
- **poke_u.jpg**: Rock-sided floating islands are whole terrain masses; no discrete loose rock prop identified.

The cyan angular forms in poke_s are trees and were excluded after enlarged review. Its modeled stones are in the rivers. Cave shells, creatures, loose items and mushrooms are not rocks. The existing Pixelwood fire remains intact; its rock ring is also supplied as an empty ring.

## Validation and continuation

The structural auditor checks all 462 files. Generation and validation check connected geometry, palette hashes, geometry inheritance, flat semantic colors, bilateral Cartoon geometry/paint and reserved index 255. The current VCOM importer and actual VoxelShape/VoxelModel renderer check voxel counts, dimensions, ground alignment and diffuse materials. The runtime report is tied to each delivered file by SHA-256. All seven treatments are rendered; Base/Cartoon also have four cardinal views.

This is whole-model validation in an isolated game copy, not combat-map registration or cover/destruction testing. Larger rocks are not drop-in single-cell PieceKinds. Existing images/models are preserved; the live game was not modified.

- [Manifest](manifest.json), [source coverage](catalogue.json), [structural audit](structural-audit.json), [runtime report](godot-validation.json), [validation summary](validation-summary.json), [visual review](visual-review.json).
- `python output/rocks/generate.py` reproduces generated models (save future hand edits first).
- `qa/probe.gd` runs in `qa/game`; pass the absolute workspace path after `--`. The successful run ends with `ROCKS_RUNTIME_QA_PASS 462`.
- `python output/rocks/validate.py` checks final files against the runtime report.
- `python output/rocks/previews.py` and `python output/rocks/document.py` rebuild supporting sheets/records.
- [Runtime source provenance](qa/source-provenance.json).
