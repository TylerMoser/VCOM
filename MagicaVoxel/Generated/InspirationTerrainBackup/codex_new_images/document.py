from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];m=json.loads((HERE/'manifest.json').read_text())
intro='''# Codex — new_1 and new_2 environment collection

Independent second set, 2026-11-04. **112 families / 784 complete VOX files**, each with Base and all six established treatments. 22 families / 154 files from new_1; 90 families / 630 files from new_2. Every deliverable is directly in `output/new_1/` or `output/new_2/`, named `New1_Codex_*` or `New2_Codex_*`. Other authors' files are not inputs to the sculpture and are not overwritten. At initial inspection, Claude's exports were not present in this checkout; the overwrite guard still protects any unowned or manually edited output.

The user explicitly chose **environment assets only**. Excluded from new_1: player, yellow companion, crow, green creature, hearts, button hints, arrows and interface overlays. New_2's white background and gray cast shadows are not modeled. No water terrain is inferred around the floating plants just because some source sprites have cyan outlines. Repeated source placements reuse the corresponding family.

## Source coverage and interpretation

new_1: complete flat-roof cottage, olive cone tree, two sizes of broad rosette, tall grass, tiny sprout, yellow roof-flower cluster, white flower, coral flower, blue flower, woodpile, chopping block with embedded axe, and nine repeatable meadow/path surface and transition tiles. The cottage includes its roof moss, roof flowers and front planter. A standalone flower cluster is also supplied for reuse. The woodpile is separate, matching the source's left-hand placement.

new_2: large/small stumps, fallen log, seedlings and forked/column/lollipop saplings, low bushes, floating leaf/lily/bud appearances, square and oblong hedges plus a notched corner, grasses and bush patches, three palm sizes and a complete palm hammock, cactus, rooted/pointed/round/lobed shrubs, drooping and clustered trees, conifers, scalloped and round broadleaf forms, and giant branch trees with and without hanging vines. Light/dark pairs are retained as distinct source paint appearances. The detailed table and numbered source maps show the crop assigned to every family. Some tiny sprite distinctions are necessarily interpreted from a compressed JPEG; no botanical species identity is asserted.

## Scale and placement

One game tile is 16 voxels. new_1 appears enlarged about 3x (approximately 48 displayed pixels/tile); new_2 is treated as native 16-pixel tiles. Canopy widths follow source sprite widths, with inferred horizontal depth. Pixel-art vertical projection is not a unique physical height measurement. Tree heights and concealed branches are volumetric interpretations; shadows are excluded. Very small plant dimensions remain below 16 where the sprite warrants it. All dimensions and occupied bounds are in the manifest.

MagicaVoxel Z-up, centered XY, ground at z=0, scene translation `0 0 floor(H/2)`. Floating pads use z=0 as water-surface datum. Mesh import Scale 0.0625, greedy mesh on, SnapToGround off. Trees are solid volumetric forms. Grass clumps and separate plants may have multiple components, but every component must touch its placement plane; tiny detached leaf-tip fragments are removed deterministically. Palm hammock is one complete assembly. Whole models only: no authoring cell files or brush packages.

The cottage follows the existing VCOM building convention: footprint 8x6 tiles; boundary grid 8+16i; foundation/floor at level 0; hollow interior above z=16; walls three courses high; closed double door in two tile slots; windows within eye-level course z=32..47, with MagicaVoxel Glass at transparency 0.7; roof at z=64 and parapet above. Foundation is intended to replace/bury into ground. Front is -Y. Back and sides, interior and roof depth are inferred. No light is invented for the dark chimney/window openings. Roof access is not provided by appearance alone.

## Variations

Canonical suffixes: Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. Cartoon broadens/regularizes leaf volumes, simplifies conifer skirts, thickens stems and balances silhouettes. Radial plants use exact C4; directional objects retain their direction and functional openings; rectangular objects use bilateral balance where appropriate. Ground tile geometry stays full 16-cubed to preserve tile interfaces; its Cartoon treatment simplifies the surface pattern. Any other shared-geometry tiny motif is explicitly listed in validation-summary.json.

CratePalette preserves all 1,024 pinned RGBA bytes, with material-aware mapping to existing slots. Index 255 is unused. TwoColor is the amended flat-material treatment: one paint per semantic group, including hidden geometry. Leaves, wood, cut ends, stone, ochre roof, steel, petals, centers, glass, sand, grass, cloth and dark chimney interior are recorded source groups; cut ends merge with wood in flat treatments. Only groups actually present are used. Glass stays separate. Recolors preserve the exact Base or Cartoon coordinate set. Leaf shading is coherent clustered paint, not a baked cast shadow. Source colors are approximate interpretations of JPEG artwork. No Emit material is needed for the selected environment assets.

## Validation and reproducibility

`generate.py` uses catalogue.py and sculpt.py; it refuses to overwrite edited or unowned outputs. `validate.py` rereads every saved VOX and checks bounds, palette, symmetry, semantic reductions, geometry inheritance, grounding and glass masks. `structural-audit.json` records the separate binary inspector. `qa/probe.gd` uses a copied current VCOM importer and checks voxel counts, mesh dimensions and grounding while rendering all seven styles plus Base/Cartoon front/back/side/underside views. `sheets.py` produces the review sheets; final hashes and visual review are in visual-review.json.

The cottage additionally uses the established building test harness in an isolated copy of VCOM: QA-only cell cuts, voxel/color/glass-exact reconstruction, floors, walls, closed doors, window sight/vault behavior, reachability and cutaway checks. See qa/house-validation.json and qa/house-results/report.json. Those scratch cells are test artifacts, not delivered models. The actual sibling game project is untouched. Other models have whole-import validation, not combat registration; single-cell PieceKind and 62-voxel loose-model limits still require a suitable integration path for larger complete objects. Decorative plants normally need solid=false.

[All files](FILES.md) · [Source coverage](COVERAGE.md) · [Overview](overview.png)

'''
(HERE/'README.md').write_text(intro)
files=['# All complete Codex models',''];coverage=['# Source coverage','', '| ID | Family | Canvas XYZ | Source crop | Notes |','| --- | --- | --- | --- | --- |']
for j,f in enumerate(m['families'],1):
 rows=[r for r in m['models'] if r['family']==f['name']];folder=ROOT/'output'/Path(f['source']).stem/'codex'
 files+=['## '+f['name'],'']+['- ['+r['style']+'](../../'+r['file']+')' for r in rows]+['']
 coverage.append(f"| {j} | {f['name']} | {f['size']} | {f['crop']} | {f.get('note','Distinct source silhouette, size or paint appearance; hidden depth inferred.')} |")
 (folder/(f['name']+'.md')).write_text('# '+f['name']+'\n\n'+f.get('note','See collection coverage for source interpretation.')+'\n\nCanvas '+str(f['size'])+'; source crop '+str(f['crop'])+'.\n\n[Collection](../../codex_new_images/README.md)\n')
(HERE/'FILES.md').write_text('\n'.join(files));(HERE/'COVERAGE.md').write_text('\n'.join(coverage))
for source in ['new_1.jpg','new_2.jpg']:
 im=Image.open(ROOT/source).convert('RGB').resize(tuple(n*2 for n in Image.open(ROOT/source).size));d=ImageDraw.Draw(im)
 fs=[(j,f) for j,f in enumerate(m['families'],1) if f['source']==source]
 for j,f in fs:
  a,b,c,e=[n*2 for n in f['crop']];d.rectangle((a,b,c,e),outline='magenta',width=2);d.rectangle((a,b,a+24,b+12),fill='white');d.text((a,b),str(j),fill='black')
 im.save(HERE/'reference'/(Path(source).stem+'_coverage.png'))
 folder=ROOT/'output'/Path(source).stem/'codex'
 (folder/'README.md').write_text('# '+source+' — Codex set\n\n'+str(len(fs))+' families / '+str(len(fs)*7)+' complete files.\n\n[Collection and validation](../../codex_new_images/README.md) · [File list](../../codex_new_images/FILES.md) · [Coverage](../../codex_new_images/COVERAGE.md)\n')
print('Documented',len(m['families']),'families')
