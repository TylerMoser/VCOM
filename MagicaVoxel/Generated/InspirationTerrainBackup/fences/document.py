"""Persist source decisions, model index, repeat conventions and validation scope."""
from generate import *
m=json.loads((HERE/'manifest.json').read_text());coverage=json.loads((HERE/'source-review.json').read_text())
text='''# Fences and railings

133 complete VOX files: 19 fence/post appearance families, each with Base and all six established variations. All 25 inspiration images reviewed. Existing delivered models and source images are preserved.

[Overview](overview.png) | [Manifest](manifest.json) | [Source review](source-review.json) | [Validation](validation-summary.json) | [Visual review](visual-review.json)

## Organization and reuse

Final files are directly in `output/<source-image-stem>/`. Each image's `fences/` folder holds source crops, seven-treatment comparisons, cardinal views, repeat previews and local records. This collection folder contains the generator, catalogue, sculpture, validation and isolated Godot QA. No cell-by-cell exports or brushes were generated. Repeated copies of a fence within a source use one family; horizontal/vertical placements are rotations. Source-specific shades and cap profiles remain separate named appearances.

## Scale and placement

One game tile equals 16 voxels. Fence sections use a 40 x 8 canvas horizontally, with a **32-voxel (two-tile) repeat pitch along X**. The extra width accommodates the shared terminal uprights/caps: place the next section 32 voxels along X, not 40. Three-section previews demonstrate the overlap. These are complete reusable two-tile sections, not every arbitrarily long fence run baked into a single asset. The skull shrine/gate post is a separate complete 16 x 12 x 32 model and has no repeat requirement.

Height and upright spacing follow the native pixel-art scale approximately; hidden rear faces and rail thickness are inferred. poke_i is a reduced JPEG with an approximately 9.5-display-pixel tile, restored to the 16-voxel scale. Cartoon uses broader balanced members and deliberate cap shapes. All ordinary Cartoon sections mirror geometry and paint across X and Y. The skull post mirrors X only, retaining its distinct front. Rotations and a shared post can form fence corners, but these deliveries do not include dedicated corner/gate hinge models or an installed map brush. The repeat checks cover straight runs, not gameplay or arbitrary corner combinations.

## Seven treatments

Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. Color-only treatments preserve exact occupancy and semantic material masks. The current minimal-material TwoColor rule applies: one flat color for an all-wood, all-metal or stone fence; separate wood and metal colors for a chain fence; separate timber and bone for the skull post. No painted highlights remain in flat styles; renderer lighting still shades surfaces. CratePalette retains the exact pinned crate RGBA bytes. All materials are opaque diffuse, with no emission or glass and no occupied palette index 255.

The rustic poke_p uprights are intentionally separate grounded components, because no connecting rails are visible in the source. Other members must connect to ground through their structure. The skull's real recessed eye/nose openings reveal dark timber backing; these openings and material masks survive recoloring.

## Validation and integration boundary

All 133 files pass binary audit, round-trip checks, bounds/grounding checks, semantic flat-color checks, Cartoon symmetry and palette invariants, and current VCOM standalone VoxelShape/VoxelModel import/render checks in a scratch project copied from the game. The largest axis is 40, below the 62-voxel VoxelModel limit. Base and Cartoon have four-direction previews plus three-section repeat previews (except the standalone skull post). All earlier delivered model hashes are checked against the preservation baseline.

No game files or combat maps were changed. These multi-tile sections are authored assets, not registered PieceKinds. The current level stamp path requires a deliberate integration approach; do not assume loose-model rendering proves terrain placement. Configure decorative fences as solid=false if they should not affect combat. For barriers, cover/climbing are determined by logical piece configuration, not the visible gaps alone.

## Source coverage

| Source | New families | Decision |
| --- | ---: | --- |
'''
for row in coverage:
 src=row['source'];stem=Path(src).stem;fs=[f for f in FAMILIES if f['source']==src]
 text+=f"| [{src}](../{stem}/fences/README.md) | {len(fs)} | {row['notes']} |\n"
 local=f"# {src}: fences\n\n{row['notes']}\n\n[Collection conventions](../../fences/README.md) | [Local manifest](manifest.json)\n\n"
 for f in fs:
  local+=f"## {f['name']}\n\nCanvas: {' x '.join(map(str,f['size']))} voxels. Source crop: {f['crop']}. "+('Standalone post; front faces negative VOX Y.' if f['kind']=='skull' else 'Repeat at 32 voxels along X, overlapping the end uprights.')+'\n\n'
  local+=f"[Source]({f['name']}_source.png) | [Seven styles]({f['name']}_variations.png) | [Cardinal geometry]({f['name']}_geometry.png)\n\n"
  if f['kind']!='skull':local+=f"[Base repeat](previews/{f['name']}_joined.png) | [Cartoon repeat](previews/{f['name']}_Cartoon_joined.png)\n\n"
  for style in STYLES:
   fn=f['name']+('' if style=='Base' else '_'+style)+'.vox';local+=f'- [{style}](../{fn})\n'
  local+='\n'
 (ROOT/'output'/stem/'fences'/'README.md').write_text(local)
text+='\n## Reproduce\n\nRun `python output/fences/generate.py`; run `qa/probe.gd` through the saved scratch Godot project with the absolute workspace as its user argument; then run `python output/fences/previews.py` and `python output/fences/validate.py`. Inspect the rendered comparisons. The generator refuses to overwrite a file changed since the previous manifest. The render probe caches model hashes: invalidate matching report entries if you change rendering code. `qa/source-provenance.json` pins the copied game sources.\n'
(HERE/'README.md').write_text(text)
