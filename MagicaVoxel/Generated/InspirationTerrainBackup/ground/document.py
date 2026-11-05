"""Persist terrain collection navigation, source coverage and modeling decisions."""
from pathlib import Path
from collections import Counter
import json
P=Path(__file__).resolve().parent;ROOT=P.parents[1];m=json.loads((P/'manifest.json').read_text());fs=m['families'];models=m['models'];reuse=json.loads((P/'reuse.json').read_text())
intro='''# Ground texture collection

Reviewed all 25 inspiration images. This collection contains **101 surface families and 147 transition families, 248 families / 1,736 complete VOX files**, with Base and all six established variations. Final files live directly in `output/<image-stem>/`. Supporting source crops, unlit top/repeat previews and VCOM previews live in that image folder's `ground/` directory. These are intentionally authored terrain tiles, not fragments cut from larger models.

## Using the tiles

- Each canvas is **16 x 16 x 16**, one game cell across, Z-up, translation `0 0 8`. Land reaches z=15, except one-voxel recessed paving joints, cracks and plank grooves. Water fills z=0..13, leaving its surface two voxels below the top of adjoining land. Blocks are filled and connected, with a complete bottom plane.
- Import as MagicaVoxel Mesh, scale **0.0625**, GreedyMeshGenerator=true, SnapToGround=false, FirstKeyframeOnly=true. Standard PieceKind translation is `(0,-0.5,0)`. Repeat at 16 voxels / one game unit. These are whole intended ground blocks; no extra cell exports or brush packages are needed.
- Flat floor tops preserve the source-like proportions and the tile interface. Grass and dirt silhouettes are intentionally identical across styles. Cartoon changes their drawn motifs into broader balanced patches; it changes paving, furrow and crack geometry only where the surface remains usable. This terrain-specific exception avoids sculpting unwanted bumps into a floor solely to distinguish a style.
- Top/repeat previews show exact stored paint, without lighting; Godot previews show lit surfaces and real grooves. A flat-color tile can still have visible cracks or lighting on its geometry.
- Water is **static opaque diffuse voxel art**, not glass, an animated shader, a fluid, or a swimming rule. Pale wave colors are the same water material and merge in TwoColor. Land support generally needs solid=true; decorative water and mixed shores need an explicit gameplay decision when registered. Do not apply the props' solid=false default indiscriminately to floors. VCOM rules work at cell scale, not at the painted shoreline inside a mixed tile.
- No game assets, PieceLibrary, maps or gameplay rules were changed. The isolated current-VCOM QA imports, reads every tile through both the mesh and 16-cubed block readers, checks voxel counts, and renders every treatment. This is not combat-map placement or movement testing.

## Transitions and orientation

`Trail`, `Shore`, and `Paving` families combine named surface families in the manifest. They are construction helpers inferred from visible boundaries, not claims of 147 additional distinct source textures. The source image's particular road width is assembled from repeated tiles; it is not baked into a giant road model.

The unrotated **Edge** has material A at x<8 and B at x>=8. **OuterCorner** has A in the x<8,y<8 quarter; **InnerCorner** has A everywhere except the x>=8,y>=8 quarter. Rotate by quarter-turns as needed. Natural straight edges have a small one-voxel irregularity, returning to x=8 at both ends; Cartoon edges are clean. Endpoints and corner interfaces align. The same A/B surface motifs and palette mappings are used in the cores and edges. Paving borders have a flush two-column curb band; no raised sidewalk obstruction is added. Corners use clean square topology; a complete automatic 47-tile blob/road-junction system is outside this collection.

The 3x3 repetition views of transition tiles deliberately repeat that *same* mixed tile, making bands or a checkerboard. They are seam diagnostics, not the intended layout of a whole shoreline. Arrange cores and rotated edge/corner cases to build a continuous shape.

## Source interpretation and materials

Source swatches establish colors and recognizable motifs; this is **reconstructed voxel terrain, not a pixel-perfect extrusion**. Clean grass swatches were selected using proximity to a visually chosen source color. Material hue filters exclude nearby characters, flowers, foliage and shadows. Four-tone quantization limits JPEG noise. The generator records the resulting representative RGB per surface in the manifest. A few tiny or partly covered soil/rock swatches use explicit visually matched representatives; see `palette_source()`.

Herringbone/parquet, irregular cobbles, large flagstones, pale brick, broken mossy pavers, wood grain, cultivated furrows, sparse grass, coarse grass, grit, cracks, cave floor, sand, caustics, shallow-water patches and river ripples have separate deterministic motifs. Underground fill, layer depth and invisible cross-sections are inferred. Terrain from the same material but genuinely different source colors keeps a separate appearance family. Lighting shadows alone are not separate textures.

TwoColor follows the user's **2026-10-28 amendment**, minimizing flat material colors. Single-material earth, sand, rock, wood and water can use one paint color. Grass over earth keeps two; stone/mortar and moss remain meaningful groups. Paving curbs merge with paving in flat variants. Recolors preserve exact occupancy. CratePalette copies the pinned 1,024 RGBA bytes unchanged and restricts mappings to suitable palette ranges; no occupied palette index 255. No Glass or Emit materials are used.

Exclusions: roofs and walls; entire bridges/buildings; loose stones, flowers, reeds, wheat, bushes and props already in other collections; characters, objects reflected or drawn in water; vertical waterfall effects; black cave voids; white spritesheet backgrounds; clouds/sky around poke_s and poke_u. Pixelwood B's gray horizontal bands are slate ledge/cliff faces, **not roads**: SlateLedge is a reusable rock-material interpretation. CliffRock/TerraceEarth tiles likewise adapt exposed geological material to a ground block, rather than replicating a whole cliff. The Pixelwood C log bridge is already a deadwood model; its gray broken pavers are included here.

## Reproduction and evidence

Run from the workspace root:

```powershell
python output/ground/generate.py
python output/ground/validate.py --binary
# Run qa/probe.gd through Godot in qa/game, with the absolute workspace path as its user argument.
python output/ground/previews.py
python output/ground/validate.py
python output/ground/document.py
```

`generate.py` refuses to overwrite an unrecognized or manually changed VOX file. `preservation-baseline.json` pins previously delivered models. `manifest.json` records each output hash, canvas, counts and flat material groups. `source-inventory.json`, `source-review.json`, `structural-audit.json`, `godot-validation.json`, `validation-summary.json` and `visual-review.json` record the actual checks. `qa/source-provenance.json` pins copied game source; the scratch copy lives under this collection, never in VoxelXCOM. `surface_styles_*.png` and `transition_styles_*.png` compare all seven styles in repeated grids; `runtime_overview_*.png` show actual VCOM block renders.

## Browse by source

'''
review=[]
for source in sorted(set(f['source'] for f in fs)|set(reuse)):
 group=[f for f in fs if f['source']==source];stem=Path(source).stem;folder=ROOT/'output'/stem/'ground';folder.mkdir(exist_ok=True)
 lines=[f'# {source}: ground tiles','',f'{sum(f["role"]=="surface" for f in group)} new surface families; {sum(f["role"]=="transition" for f in group)} transition families. Seven VOX treatments per family.', '', '[Shared terrain contract, orientation and validation](../../ground/README.md)', '', '## Surface families','', '| Family | Pattern | Reference crop | Top/repeat | VCOM styles |','| --- | --- | --- | --- | --- |']
 for f in group:
  if f['role']!='surface':continue
  n=f['name'];lines.append(f'| [{n}](../{n}.vox) | {f["kind"]} | [{f["crop"]}]({n}_source.png) | [Preview]({n}_top_and_repeat.png) | [Preview]({n}_variations.png) |')
 lines+=['','## Transition families','','| Family | Material A / B | Previews |','| --- | --- | --- |']
 for f in group:
  if f['role']!='transition':continue
  n=f['name'];lines.append(f'| [{n}](../{n}.vox) | {" / ".join(f["materials"])} | [Top/repeat]({n}_top_and_repeat.png), [VCOM]({n}_variations.png) |')
 lines+=['','## Assembled tile layouts','']
 for f in group:
  if f['role']=='transition' and f['contour']=='Edge':
   prefix=f['name'][:-4];lines.append(f'- [{prefix}: all seven treatments]({prefix}_assembled.png)')
 links=[]
 if source in reuse:
  lines+=['','## Reuse from an earlier Pixelwood image','']
  for n in reuse[source]:
   owner=next(f for f in fs if f['name']==n);ownerstem=Path(owner['source']).stem
   lines.append(f'- [{n}](../../{ownerstem}/ground/{n}_variations.png): reuse all seven files in `output/{ownerstem}/`; no duplicate exports.')
   links += [dict(file=r['file'],sha256=r['sha256']) for r in models if r['family']==n]
 lines+=['','Final VOX files are in the parent image folder. Surface crops are color/motif references; hidden soil depth and transition masks are authored. See the collection README for flat-style, water and geology limitations.','']
 (folder/'README.md').write_text('\n'.join(lines))
 (folder/'manifest.json').write_text(json.dumps({'source':source,'families':group,'models':[r for r in models if r['source']==source],'reuse':links},indent=2)+'\n')
 review.append({'source':source,'reviewed':True,'new_surfaces':[f['name'] for f in group if f['role']=='surface'],'transition_helpers':[f['name'] for f in group if f['role']=='transition'],'reuse':links,'scope':'Ground materials and tile contours; exclusion rationale in collection README.'})
 intro+=f'- [{source}](../{stem}/ground/README.md): {len(group)} families / {len(group)*7} files'+('; Pixelwood meadow/dirt reuse' if links else '')+'.\n'
intro+='\n## Collection preview sheets\n\n'
for pattern,label in [('surface_styles_*.png','Surface styles and repeats'),('transition_styles_*.png','Transition styles and repeats'),('runtime_overview_*.png','VCOM rendered blocks')]:
 intro+=label+': '+', '.join(f'[{i+1}]({file.name})' for i,file in enumerate(sorted(P.glob(pattern))))+'.\n\n'
intro+='Completed 2026-10-30. Final visual review and validation records are stored alongside this document.\n'
(P/'README.md').write_text(intro)
(P/'source-review.json').write_text(json.dumps(review,indent=2)+'\n')
print('Documented',len(review),'source images')
