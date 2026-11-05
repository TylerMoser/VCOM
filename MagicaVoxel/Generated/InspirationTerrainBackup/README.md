# Output organization

Established October 26, 2026. Every root-level reference image has a matching output folder named after its filename **without the extension**. All voxel files generated from that image belong directly in its folder. Each folder can contain many assets and variants across multiple prompts and sessions.

## Working rules

- Generate complete models only, one `.vox` per model/variant. Do not automatically generate cell-by-cell VOX files or brush packages, including for multi-tile models.

- Identify the source image before generating assets, then use its folder below.

- Use descriptive asset names such as `oak_tree_01.vox`, `stone_wall_straight.vox`, or `roof_corner_02.vox`; keep distinct objects and variants separately named.

- Keep generators, previews, audit reports, and asset notes within the same image folder. Supporting `generators/` or `previews/` subfolders are optional; final `.vox` files stay directly in the image folder.

- Record the exact source image filename, generated filenames, dimensions, palette, seed, placement, and validation in an asset note or a folder README as assets are created.

- Preserve earlier variants and hand edits. Update an existing asset when requested; use a new descriptive name for a distinct asset or variant.

- Leave original reference images at the workspace root. Shared research stays in `knowledge/` and reusable tools in `tools/`.

- When a new reference image is added, create `output/<image-stem>/` and add its mapping here. If two images share a stem, disambiguate their folder names using the extensions and document the mapping rather than mixing their outputs.

- For an asset deliberately based on several images, select its primary reference folder and list all references in its note; avoid separate competing copies.

- This structure supersedes the original proposal for top-level `models/`, `generators/`, and `previews/` folders. Game integration into VoxelXCOM is a separate step when requested.

## Style families

Use [the shared variation specification](../knowledge/VARIATIONS.md) for all source images and model types. The suffixes are `Cartoon`, `CratePalette`, `TwoColor`, `Cartoon_TwoColor`, `CratePalette_TwoColor`, and `Cartoon_CratePalette_TwoColor`. Put them after the complete base asset name, including any size identifier. All six plus Base give seven files per base; generate only the requested treatments. Final files remain directly in the image folder, not separate style folders.

Use [the family manifest template](../knowledge/templates/README.md) to record source geometry, semantic groups, symmetry, colors, palette hashes and validation. Local notes record asset-specific choices; shared definitions live in the specification.

## Example

```text

poke_b.png

output/

  poke_b/

    oak_tree_01.vox

    oak_tree_02.vox

    oak_tree_01.py

    oak_tree_01.png

    oak_tree_01-audit.json

    oak_tree_01.md

```

These example assets have not been generated.

## Image-to-folder mapping

| Source image (workspace root) | Output folder |
| --- | --- |
| `mario.jpg` | `output/mario/` |
| `pixelwood_a.jpg` | `output/pixelwood_a/` |
| `pixelwood_b.gif` | `output/pixelwood_b/` |
| `pixelwood_c.jpg` | `output/pixelwood_c/` |
| `poke_a.jpg` | `output/poke_a/` |
| `poke_b.png` | `output/poke_b/` |
| `poke_c.png` | `output/poke_c/` |
| `poke_d.png` | `output/poke_d/` |
| `poke_e.png` | `output/poke_e/` |
| `poke_f.png` | `output/poke_f/` |
| `poke_g.png` | `output/poke_g/` |
| `poke_h.png` | `output/poke_h/` |
| `poke_i.jpg` | `output/poke_i/` |
| `poke_j.jpg` | `output/poke_j/` |
| `poke_k.jpg` | `output/poke_k/` |
| `poke_l.png` | `output/poke_l/` |
| `poke_m.png` | `output/poke_m/` |
| `poke_n.png` | `output/poke_n/` |
| `poke_o.png` | `output/poke_o/` |
| `poke_p.png` | `output/poke_p/` |
| `poke_q.png` | `output/poke_q/` |
| `poke_r.png` | `output/poke_r/` |
| `poke_s.jpg` | `output/poke_s/` |
| `poke_t.png` | `output/poke_t/` |
| `poke_u.jpg` | `output/poke_u/` |

## New images (2026-11-04)

Two inspiration images added after the first 25, mapped the same way:

| Source image (workspace root) | Output folder |
| --- | --- |
| `new_1.jpg` | `output/new_1/` |
| `new_2.jpg` | `output/new_2/` |


## Independent new-image comparison set

`new_1.jpg` maps to `new_1/`; `new_2.jpg` maps to `new_2/`. The independent Codex set uses `New1_Codex_*` (154 files) and `New2_Codex_*` (630 files), with support in each image folder's `codex/` directory. [Shared collection and file index](codex_new_images/README.md). Preserve Claude's unprefixed files and support directories.
