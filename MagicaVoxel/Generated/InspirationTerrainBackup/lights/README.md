# Inspiration lights collection

Reviewed all 25 original inspiration images. Created **77 complete VOX files**: seven treatments for 11 source appearances (10 distinct designs; poke_b and poke_c share their silver-lantern artwork). No per-cell exports. Existing models and source images are preserved.

[Night overview](overview-night.png) · [Variation sheet 1](variations_1.png) · [Variation sheet 2](variations_2.png) · [Geometry 1](geometry_1.png) · [Geometry 2](geometry_2.png)

## Models and source scale

Each final VOX is directly in its source image folder. Dimensions below are canvas X/Y/Z; exact occupied bounds are in the manifests. One original tile is 16 voxels. Depth, hidden surfaces, and physical height are inferred from the top-down sprites rather than recovered exactly.

| Source | Family | Canvas | Power |
| --- | --- | --- | --- |
| pixelwood_a.jpg | [PixelwoodA_PostLantern](../pixelwood_a/lights/README.md) | 16 × 16 × 40 | 1.5 |
| pixelwood_b.gif | [PixelwoodB_Campfire](../pixelwood_b/lights/README.md) | 24 × 24 × 28 | 1.5 |
| poke_b.png | [PokeB_SilverStreetLantern](../poke_b/lights/README.md) | 12 × 12 × 40 | 2 |
| poke_c.png | [PokeC_SilverStreetLantern](../poke_c/lights/README.md) | 12 × 12 × 40 | 2 |
| poke_d.png | [PokeD_StoneLantern](../poke_d/lights/README.md) | 16 × 16 × 20 | 1 |
| poke_f.png | [PokeF_TwinGlobeStreetlight](../poke_f/lights/README.md) | 32 × 12 × 48 | 2 |
| poke_g.png | [PokeG_RoundStreetlight](../poke_g/lights/README.md) | 16 × 16 × 48 | 2 |
| poke_j.jpg | [PokeJ_DarkStreetLantern](../poke_j/lights/README.md) | 10 × 10 × 28 | 1.5 |
| poke_m.png | [PokeM_BronzePostLantern](../poke_m/lights/README.md) | 16 × 16 × 48 | 2 |
| poke_n.png | [PokeN_TealStreetlight](../poke_n/lights/README.md) | 16 × 16 × 40 | 2 |
| poke_s.jpg | [PokeS_IvoryScrollLantern](../poke_s/lights/README.md) | 24 × 16 × 56 | 2 |

## Materials and variations

All seven treatments preserve working Emit voxels: Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. The saved October 28 minimal-color amendment applies: flat colors per semantic group, with dedicated emission. Lamps use 75% Emission; Power is recorded above. Crate variants preserve the pinned reference RGBA exactly, with material-safe remapping. Read [lighting instructions](../../knowledge/LIGHTS.md).

Cartoon fixtures are more balanced and deliberately sculpted, with checked paint/geometry symmetry. Radial fixtures and fire use C4; twin heads use bilateral X/Y; the directional ivory scroll lamp keeps its offset head and uses depth symmetry. Base/Cartoon silhouettes differ in every family.

## Coverage and exclusions

The catalogue records every original, its hash and the review decision. Repeated placements within an image receive one model family, rather than one file per placement. The b/c silver lantern is intentionally available in both corresponding folders. Existing building windows are not separately exported as lamps or retroactively changed.

- **mario.jpg**: Question blocks, HUD and signs are not light fixtures.
- **pixelwood_c.jpg**: Orange water plants are cattails with green leaves, not torches; chest is not a lamp.
- **poke_a.jpg**: Woodland paths, fences and flowers; no identifiable lighting prop.
- **poke_e.png**: Trees, flowers, fences and water; no identifiable lighting prop.
- **poke_h.png**: Farm tools, scarecrows, hay and crops; no identifiable lighting prop.
- **poke_i.jpg**: Red posts by doors are mailboxes; no identifiable lighting prop.
- **poke_k.jpg**: Forest paths and signs; no identifiable lighting prop.
- **poke_l.png**: Tree/terrain tilesheet; no lighting prop.
- **poke_o.png**: Mailboxes, signs, benches, parasols and floral decorations; no identifiable lighting prop.
- **poke_p.png**: Flowers, paths and building; no identifiable lighting prop.
- **poke_q.png**: Paired sculpted creature statues at shrine and gate are not lamps; crystal rocks are not evidenced as lights.
- **poke_r.png**: Blue objects beside doors are mailboxes; no identifiable lighting prop.
- **poke_t.png**: Cave rocks, crystals, plants and signs; no identifiable torch or installed light.
- **poke_u.jpg**: Signs, characters and pale sculpted trees; no identifiable lighting prop.

## Validation and limits

All 77 files passed the binary auditor and were read through the current game importer at .0625. The real VoxelShape reader verified voxel counts, emitting regions, 23/31 quantized glow, Power, grounded mesh bounds and the blood reservation. The actual VoxelModel shader rendered all treatments in day/night views; Base and Cartoon also have four cardinal views. Serialized geometry, material dictionaries, emitter masks, palette hashes, connectivity and symmetry are checked independently.

Previews use a harness omni with the documented energy/reach formula and shadows disabled to show spill. The voxel surface glow is the real game shader. These are not registered battle pieces: level placement, final lamp shadows and destruction have not been tested. No game files were modified.

The stone lantern source shows an unlit dark chamber; a small warm source was inferred. The bronze lamp is cropped at the image bottom, so its foot/lower pole are inferred. The dark lantern and ivory scroll lamp have compressed source detail. These uncertainties are documented per family. The fire is a static model, not GIF animation.

## Reproduce / continue

- `python output/lights/generate.py` rebuilds this collection only. Preserve any later hand edits before rerunning.
- `python output/lights/validate.py` audits outputs and compares the saved runtime report.
- `qa/probe.gd` runs in the saved isolated `qa/game` copy of VCOM; pass the absolute workspace root after `--`. It reads the delivered models without importing them into the live game.
- `python output/lights/previews.py` recomposes sheets after rendering.
- [Manifest](manifest.json), [catalogue](catalogue.json), [structural audit](structural-audit.json), [runtime report](godot-validation.json), [validation summary](validation-summary.json), [source provenance](qa/source-provenance.json).

The shared `output/lights/` folder holds collection tooling and evidence only; generated final models remain under their source image folders.

Final [visual review](visual-review.json) covers all daytime/nighttime treatments and cardinal geometry views. Bright Emit regions can clip to white in the compatibility-renderer night preview; stored source colors remain intact.
