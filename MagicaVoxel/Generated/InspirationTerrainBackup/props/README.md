# Signs, benches and remaining decorative props

**322 complete VOX files across 46 new families**, each with Base and all six established variations. All 25 inspiration images reviewed against earlier collections. Existing props and source images were preserved; repeated props have reuse links.

[Overview](overview.png) | [Manifest](manifest.json) | [Source review](source-review.json) | [Reuse](reuse.json) | [Validation](validation-summary.json) | [Visual review](visual-review.json)

## Scope and organization

This collection covers signs and noticeboards, benches, mailboxes, a utility stand, item block/ball, mushrooms, treasure chest, stacked timber, hay bales/mound, pitchfork, flower planter, parked scooter, parasol, lounger, sandcastle, fountain, monuments and barrel. Characters, animals, HUD, terrain, whole bridges and buildings are not reclassified as decorations. Earlier trees, vegetation, rocks, lights, deadwood and fences remain authoritative. Tiny ambiguous source marks are explicitly recorded rather than assigned invented identities.

Each final `.vox` lives directly in `output/<image-stem>/`. Source crops, style sheets, cardinal views, local manifest and notes live in that image's `props/`. This shared folder contains the catalogue, deterministic sculptor, generator, palette mapping, validator and scratch Godot QA. No per-cell files or automatic brushes were created. Repeated placements in an image use the same family; Pixelwood mushroom and item-ball reuse spans images.

## Modeling and styles

One game tile corresponds to 16 voxels. Dimensions follow approximate sprite scale, with multi-tile width retained for benches, beach furniture and the fountain. Pixelwood is enlarged pixel art; poke_i is reduced, with a native tile approximately 9.5 displayed pixels. Depth, backs, undersides and occluded surfaces are inferred. Source crops are in the catalogue and beside the models. These are authored volumetric interpretations, not literal sprite extrusions. Small monuments and the utility stand have documented interpretive uncertainty.

The seven styles are Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Cartoon changes geometry, using broader supports, rounded/chamfered forms or cleaner massing. It balances left/right geometry and paint where appropriate, preserving a directional arrow, question glyph and scooter front/rear. Round mushrooms, ball, barrel, hay and fountain also balance both horizontal axes. Other recolors preserve every occupied voxel coordinate of Base or Cartoon.

TwoColor follows the current minimal-material rule: one flat color per material group, combining similar timber sign frame/face colors and mushroom spots/stem. Distinct lettering, colored panels, metal, bone-like pale mushroom stems, tires, soil, greenery, petals and cloth remain meaningful groups where needed. The parasol's orange/white sectors merge to one cloth color in flat styles. The question block retains its mark but merges its golden rim into its body. Lighting still shades flat stored colors. CratePalette copies the exact pinned reference RGBA bytes. Occupied palette index 255 is never used.

All files use one model, a rooted scene graph, explicit palette, MagicaVoxel Z-up and translation `0 0 floor(height/2)`. Use Mesh import Scale 0.0625. All components reach z=0 through connected geometry. Hollow space is retained under benches, loungers, signs and the parasol; chest/barrel are closed solid props. Lettering is represented by source-like short strokes rather than invented readable words. The question glyph remains recognizable. Surface materials are opaque diffuse; the fountain water is static opaque decorative geometry, not glass or simulated liquid. These assets introduce no emission.

## Validation and limitations

All 322 models pass binary inspection, serialized round-trip, geometry inheritance, flat semantic-color checks, exact crate palette, reserved-index checks, grounding, Cartoon symmetry and current VCOM standalone importer/VoxelShape/VoxelModel checks in a scratch copy of the game. Source hashes and 2,814 earlier delivered models match the preservation baseline. Base and Cartoon have four cardinal render views; all seven styles have matched overview views. Final models and validation are linked by SHA-256.

No game project, combat map, PieceKind library or collision configuration was changed. Loose-model rendering does not establish 16-cubed terrain stamping, pathfinding, cover, seating, mailbox interaction, item rewards, sign text, moving vehicles or fountain animation. Use solid=false for purely cosmetic decoration when integrating, and choose collision/cover deliberately for other props. The largest canvas axis is 48, within the current 62-voxel loose-model renderer limit.

## Source coverage

| Source | New families | Decisions |
| --- | ---: | --- |
| [mario.jpg](../mario/props/README.md) | 2 | Notice sign and question block. Existing carved stone stacks are reused from rocks. Characters, backdrop faces and HUD are excluded. The block is a static prop, not an implemented pickup. |
| [pixelwood_a.jpg](../pixelwood_a/props/README.md) | 2 | Two-arrow direction sign and spotted red mushroom. Lantern, tent, trees, flowers, rocks and deadwood already exist. |
| [pixelwood_b.gif](../pixelwood_b/props/README.md) | 0 | No new unique small props. Reuse the Pixelwood A mushroom. House, campfire, vegetation and stones already exist. |
| [pixelwood_c.jpg](../pixelwood_c/props/README.md) | 1 | Metal-banded treasure chest. Reuse Pixelwood A mushrooms. Stone plinth/terrain and water crossing remain with prior collections or architecture. |
| [poke_a.jpg](../poke_a/props/README.md) | 1 | Small trail sign. Trees, plants, boulders and bridge railing already covered; whole bridges and terrain are architecture. |
| [poke_b.png](../poke_b/props/README.md) | 2 | Blue/red-emblem gray information plaque and mailbox. Existing building signs/trim remain part of buildings. Lamps, fences and plants already covered. Loose item-ball sprites can reuse poke_g. |
| [poke_c.png](../poke_c/props/README.md) | 2 | Two freestanding noticeboard appearances: warm timber and pale framed green board. Characters and building-mounted signs are excluded. |
| [poke_d.png](../poke_d/props/README.md) | 0 | No new discrete signs, benches or clearly identifiable small props beyond existing stone lanterns, rocks, vegetation and architecture. |
| [poke_e.png](../poke_e/props/README.md) | 0 | No new discrete small props beyond existing plants, trees, rocks and fences. |
| [poke_f.png](../poke_f/props/README.md) | 2 | Antler-like monument on a pedestal and dark-framed garden noticeboard. The monument is a stylized interpretation of a small sprite, not a character replica. |
| [poke_g.png](../poke_g/props/README.md) | 5 | Park bench, timber sign, ground-standing pale notice, arched utility stand and item ball. Utility function is uncertain, so its visible arch, face and three red marks are modeled without assigning gameplay behavior. |
| [poke_h.png](../poke_h/props/README.md) | 4 | Single tied bale, three-bale stack, hay mound and pitchfork. Wheat is in vegetation. Characters, animals and held tools are excluded. Reuse the item ball from poke_g. |
| [poke_i.jpg](../poke_i/props/README.md) | 2 | Timber sign and red mailbox. Source is reduced; approximately 9.5 displayed pixels represent a native 16-pixel tile. Buildings and fences already covered. |
| [poke_j.jpg](../poke_j/props/README.md) | 1 | Low stacked timber decoration near the modern building, interpreted as round log ends. Previously overlooked by deadwood/fence passes. Other props are already-covered lamps, plants and building trim. |
| [poke_k.jpg](../poke_k/props/README.md) | 0 | No new discrete small props beyond existing vegetation, rocks and terrain/stair architecture. |
| [poke_l.png](../poke_l/props/README.md) | 0 | Tilesheet contains vegetation, rocks, cliffs and hoop edging, all already covered; no new small prop identified. |
| [poke_m.png](../poke_m/props/README.md) | 1 | One-way arrow sign. Red/white round pickup is recorded as reuse of the poke_g item ball, not a second mushroom. Characters, buildings and cut logs/stumps remain outside this new set. |
| [poke_n.png](../poke_n/props/README.md) | 2 | Slatted bench and timber notice sign. Source lettering is represented by short strokes; no invented readable wording. |
| [poke_o.png](../poke_o/props/README.md) | 8 | Timber sign, red mailbox, metal-framed blue plaque, planted flower box, parked scooter, open beach parasol, white lounger and four-turret sandcastle. Enlarged crops corrected initial thumbnail guesses of a vending machine, bicycle and volleyball net. Characters and swimmers are excluded. |
| [poke_p.png](../poke_p/props/README.md) | 1 | Small timber board by the bridge. Existing stumps, bridge uprights, plants and rocks are reused. |
| [poke_q.png](../poke_q/props/README.md) | 1 | Timber trail sign. Skull posts, chain fence and bamboo already exist in fences. Shrine, stairs and terrain are architectural; creatures are excluded. |
| [poke_r.png](../poke_r/props/README.md) | 2 | Blue mailbox and low pale information panel. Other small outlined markers are treated as the same information-sign family. Houses, fences and vegetation already covered. |
| [poke_s.jpg](../poke_s/props/README.md) | 2 | Tiered fountain and slender courtyard monument. Small reduced-image details and backs are inferred. Tiny brown marks remain ambiguous; they are not confidently classified as separate props. Larger arches, columns, terraces and ruins are architecture; lamps, vegetation and balustrades already covered. |
| [poke_t.png](../poke_t/props/README.md) | 3 | Barrel, cave trail sign and tiny red mushroom. Cave walls, bridges and stairs are architecture; rocks and tubular railings already covered. |
| [poke_u.jpg](../poke_u/props/README.md) | 2 | Small and wide pale-trimmed green noticeboards. Characters, green creatures and building-mounted signs are excluded. |

## Rebuild

Run `python output/props/generate.py`; run `qa/probe.gd` through the saved scratch Godot project with this workspace absolute path as the user argument; then run `python output/props/previews.py`, `python output/props/validate.py` and `python output/props/document.py`. Review renders before marking completion. The generator checks previous manifest hashes and refuses to overwrite hand edits. The render probe caches model hashes; invalidate report entries when changing render code. Current copied game sources are pinned in `qa/source-provenance.json`.
