from generate import HERE,ROOT
from pathlib import Path
import json
m=json.loads((HERE/'manifest.json').read_text())
text='''# Codex missed trees and mushrooms

Completed 2026-11-04: three poke_f tree appearances and one poke_d mushroom clump, all seven styles, **28 complete VOX files**. `_Codex_` filenames coexist with other authors' assets. Models are directly in their source-image output folders, with reference crops, previews and family notes in `codex_missed_vegetation/` beneath each image folder. No cell files or game modifications.

## Source coverage and comparison

The poke_f autumn woods repeat a broad layered tree silhouette with three paint arrangements: red crown/red lower whorl and orange sides; gold crown/gold lower whorl and orange sides; green crown/green lower whorl and gold sides. Orange is a side-lobe color here, not a fourth unique all-orange tree. Occluded repeats and edge crops do not create further families. The existing poke_d autumn trees have overlapping tapered leaf scales and different silhouettes; these broad lobed crowns and exposed fork are newly sculpted rather than renamed copies.

The poke_d riverbank mushroom sprite has two unequal coral caps with cream spots and pale stems. Reuse this clump at repeated source placements. Existing PixelwoodA_SpottedMushroom and PokeT_CaveMushroom have different shapes/palettes and do not cover this appearance. Source silhouettes are interpreted as full rounded volumes, not extruded sprite sheets. Unseen crown depth and cap backs are inferred.

## Scale and placement

16 source pixels approximately equal one tile; 16 voxels equal one game tile. Trees use 48x48x48 canvases, with 42x42x44 occupied extents (about 2.6 tiles wide); the mushroom clump uses a 16-cubed canvas. Tree geometry has a trunk, roots, forked branches, broad lower whorl, contrasting side lobes and upper crown. Each tree is connected to z=0. Mushrooms have two intentional disconnected components, each independently rooted at z=0; no invisible connecting soil slab. Cartoon balances their two different sizes along one axis.

Z-up; horizontally centered; scene translation `0 0 floor(H/2)`. Import whole Mesh at 0.0625. Decorative placement normally requires `solid=false` configured in the game; the VOX cannot encode it. Current PieceKind block import is cell-sized: full trees need a separate integration decision. No gameplay testing is claimed.

## Seven treatments

Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor, Cartoon_CratePalette_TwoColor. Cartoon trees have exact fourfold geometry/paint symmetry; mushrooms have X reflection symmetry. Recolors retain exact geometry. Flat tree treatments combine ALL foliage hues into the main crown color, plus brown wood. Mushroom flat treatments combine all cap spots and stems into cream, plus coral cap color. Both use exactly two flat paint groups, with no texture noise. CratePalette preserves the pinned palette byte-for-byte and selects existing nearest-RGB colors among slots 1..254; mappings are saved in manifest.json. Index 255 is unused. Materials are opaque diffuse.

## Evidence and reproduction

Run `generate.py` to regenerate unchanged owned models; it refuses to overwrite modified/unowned files. `validate.py` independently rereads all outputs and checks geometry inheritance, palette, flat groups, symmetry, bounds, connectivity and grounded components. `setup_qa.py` copies the current game importer into a scratch project. `qa/probe.gd` verifies imported voxel counts, mesh bounds and grounding, and renders all styles plus Base/Cartoon cardinal/underside views. `sheets.py` builds the comparison sheets. `visual-review.json` binds the final reviewed files and importer evidence. Import validation is distinct from combat-map testing.

[All model files](FILES.md) · [Style comparison](styles_1.png) · [Geometry and references](geometry_1.png)

'''
(HERE/'README.md').write_text(text)
files=['# Complete model files','']
for f in m['families']:
 rows=[r for r in m['models'] if r['family']==f['name']];support=ROOT/'output'/Path(f['source']).stem/'codex_missed_vegetation'
 files+=['## '+f['name'],'']+['- ['+r['style']+'](../../'+r['file']+')' for r in rows]+['']
 (support/(f['name']+'.md')).write_text('# '+f['name']+'\n\n'+f['note']+'\n\n[Collection](../../codex_missed_vegetation/README.md)\n')
(HERE/'FILES.md').write_text('\n'.join(files))
