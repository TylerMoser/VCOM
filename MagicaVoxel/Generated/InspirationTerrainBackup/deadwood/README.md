# Stumps and logs

112 new complete VOX files across 16 source appearance/size families, with all seven established treatments. All 25 inspiration images reviewed. The existing seven Pixelwood stump files are preserved; Pixelwood B reuses A's stump and fallen log.

[Overview](overview.png) | [Manifest](manifest.json) | [Validation](validation-summary.json) | [Source review](source-review.json)

Models live directly in `output/<image-stem>/`; source crops, seven-style comparison sheets and four-direction geometry sheets live in each image's `deadwood/` folder. This shared folder holds the reproducible generator, catalogue, review records and QA. No per-cell exports or brush packages were created.

Seven treatments: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Cartoon simplifies the outline and mirrors geometry and paint across X and Y. Color-only variations retain exact Base/Cartoon occupancy. TwoColor uses exactly two semantic colors here: bark and exposed cut wood. Grain rings are paint details and disappear in flat variants. CratePalette copies the reference RGBA bytes exactly, choosing brown swatches for bark and light wood. Materials are opaque diffuse; no emission or glass.

Sizing uses 16 voxels per game tile and the visible source sprite grid. Pixelwood's enlarged pixels are approximately three display pixels per source pixel (five in B); Pokemon screenshots are approximately native pixel scale. Width/length follow the sprite; depth, cut surfaces, back sides and stump height are inferred from the oblique view. These are authored 3D interpretations, not literal sprite extrusions. Long logs run along VOX Y; Z is up. Each model is one connected component touching z=0, with scene translation `0 0 floor(height/2)` and import Scale 0.0625.

## Runtime boundary

105 files pass the current VCOM reader, VoxelShape and VoxelModel rendering path in a scratch project copied from the current game. The seven Pixelwood C log files import correctly and pass VoxelShape extraction, but cannot use VoxelModel: its mesher limits the maximum occupied extent on ANY axis to 62. Pixelwood A has a 20 x 60 x 20 canvas and fits the runtime limit; Pixelwood C is 32 x 152 x 32. The oversized previews use the ordinary imported mesh and need a static-mesh integration path or later explicit game-side assembly. Rotating long models onto Y does not bypass VoxelModel's limit. Proportions have been preserved. No game files, combat maps, collision configuration or registrations were changed. Small decorative driftwood should use solid=false when integrated; large logs/stumps need deliberate gameplay collision configuration.

The QA probe checks counts, bounds, used colors, ground plane, opaque materials and hashes; validate.py additionally checks round-trip data, structural validity, seven-style geometry invariants, Cartoon paint symmetry, flat semantic colors, the pinned palette and preservation of all prior delivered models. Render comparisons were reviewed; see visual-review.json. This is standalone import/render validation, not a played combat-map test.

## Source coverage

| Source | New families | Notes |
| --- | ---: | --- |
| [mario.jpg](../mario/deadwood/README.md) | 0 | No discrete stump or fallen log identified. Carved pillars are stone; characters, signs, and background tree silhouettes are excluded. |
| [pixelwood_a.jpg](../pixelwood_a/deadwood/README.md) | 1 | Fallen trunk with broken side branch. Existing PixelwoodA_Stump and all six variations are preserved and reused. |
| [pixelwood_b.gif](../pixelwood_b/deadwood/README.md) | 0 | The fallen log and cut stumps repeat Pixelwood A artwork. Reuse its families; do not create duplicate models. Campfire remains in the lights collection. |
| [pixelwood_c.jpg](../pixelwood_c/deadwood/README.md) | 1 | The very long, bark-covered natural log across the stream is a separate size family. Reuse the existing Pixelwood A cut stump. |
| [poke_a.jpg](../poke_a/deadwood/README.md) | 0 | No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection. |
| [poke_b.png](../poke_b/deadwood/README.md) | 0 | No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection. |
| [poke_c.png](../poke_c/deadwood/README.md) | 1 | Repeated small forked driftwood in the river becomes one reusable family. The masonry/wooden built bridge is architecture. |
| [poke_d.png](../poke_d/deadwood/README.md) | 0 | No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection. |
| [poke_e.png](../poke_e/deadwood/README.md) | 0 | No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection. |
| [poke_f.png](../poke_f/deadwood/README.md) | 0 | No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection. |
| [poke_g.png](../poke_g/deadwood/README.md) | 2 | One fallen-log appearance and one small cut-stump appearance, repeated near houses. |
| [poke_h.png](../poke_h/deadwood/README.md) | 0 | Wheat, hay stacks, tools and manufactured fence/bridge timber are excluded; no discrete deadwood prop identified. |
| [poke_i.jpg](../poke_i/deadwood/README.md) | 0 | No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection. |
| [poke_j.jpg](../poke_j/deadwood/README.md) | 0 | No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection. |
| [poke_k.jpg](../poke_k/deadwood/README.md) | 0 | No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection. |
| [poke_l.png](../poke_l/deadwood/README.md) | 0 | No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection. |
| [poke_m.png](../poke_m/deadwood/README.md) | 5 | Long and short fallen logs, broad rooted cut stumps, the taller stump beneath a character, and a tiny root stump. Repeated medium stumps reuse the broad family. Characters and tools are excluded from geometry. |
| [poke_n.png](../poke_n/deadwood/README.md) | 0 | No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection. |
| [poke_o.png](../poke_o/deadwood/README.md) | 3 | Short fallen log, clean-cut stump, and an irregular tan/brown splintered wood remnant. The latter is interpreted as a low broken stump/root remnant, not a character; its obscured underside is inferred. |
| [poke_p.png](../poke_p/deadwood/README.md) | 3 | Three distinct sizes/profiles: broad large cut stump, tiny flared root stump and narrower sapling stump. |
| [poke_q.png](../poke_q/deadwood/README.md) | 0 | No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection. |
| [poke_r.png](../poke_r/deadwood/README.md) | 0 | No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection. |
| [poke_s.jpg](../poke_s/deadwood/README.md) | 0 | No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection. |
| [poke_t.png](../poke_t/deadwood/README.md) | 0 | Banded brown object is a barrel; dark cliff formations are rocks. Neither belongs in this collection. |
| [poke_u.jpg](../poke_u/deadwood/README.md) | 0 | No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection. |

## Rebuild and review

Run `python output/deadwood/generate.py`, then the saved `qa/probe.gd` against its scratch game with the workspace absolute path as user argument. Run `python output/deadwood/previews.py` and `python output/deadwood/validate.py`. The generator refuses to overwrite a delivered file whose hash differs from its previous manifest (possible hand edit). The render probe caches unchanged hashes; invalidate report entries when changing render code. Review the final renders before marking completion.
