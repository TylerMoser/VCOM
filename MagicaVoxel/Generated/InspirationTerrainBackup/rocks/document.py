"""Refresh documentation without replacing existing source-folder records."""
from pathlib import Path
import json,hashlib
from generate import ROOT,HERE,read
m=json.loads((HERE/'manifest.json').read_text());catalogue=json.loads((HERE/'catalogue.json').read_text())
canonical={};duplicates=[]
for f in m['families']:
 row=next(r for r in m['models'] if r['family']==f['name'] and r['style']=='Base')
 size,v,p=read(ROOT/row['file']);signature=hashlib.sha256(repr((size,sorted(v.items()),p)).encode()).hexdigest()
 if signature in canonical:duplicates.append({'family':f['name'],'same_base_content_as':canonical[signature],'reason':'Matching reference artwork; named files retained in both source image folders.'})
 else:canonical[signature]=f['name']
(HERE/'duplicates.json').write_text(json.dumps(duplicates,indent=2))
lines=['# Rocks across the inspiration images','', '**462 complete VOX files**: seven treatments for **66 source appearances**, across 18 image folders. All 25 originals were reviewed. Repeated artwork is available in each corresponding source folder; [exact Base duplicates](duplicates.json) are recorded. No cell-by-cell exports.','', '[Overview](overview.png) · [Source catalogue](catalogue.json) · [Rock authoring instructions](../../knowledge/ROCKS.md)','', '## Models','', 'Final models sit directly under `output/<source-image-stem>/`; the links below open source-specific model lists, reference crops and previews. Sizes are canvas X/Y/Z; exact occupied bounds and inferred scale are in the manifests.','', '| Source | Appearances | Models |','| --- | --- | --- |']
for source in catalogue['sources']:
 if source['families']:
  stem=Path(source['source']).stem;n=len(source['families']);lines.append(f"| [{source['source']}](../{stem}/rocks/README.md) | {n} | {n*7} |")
lines+=['','## Variations and materials','', 'Every family has Base, Cartoon, CratePalette, TwoColor, Cartoon_TwoColor, CratePalette_TwoColor and Cartoon_CratePalette_TwoColor. The saved October 28 amendment applies: TwoColor is one flat color per meaningful material group. Plain rocks therefore use one color, mossy rocks two, and the red-crystal outcrop two. No shading colors are retained inside those groups. Natural render shading remains.','', 'Crate variants retain the full pinned crate palette unchanged. All rocks and crystals are opaque diffuse; none is assigned unrequested emission or glass. Cartoon changes geometry and balances corresponding sides; it preserves the front of carved stacks and the crystal chamber.','', '## Review sheets','']
for i in range(1,12):lines.append(f'- Page {i}: [all seven treatments](variations_{i:02}.png) · [Base/Cartoon from four directions](geometry_{i:02}.png)')
lines+=['','## Coverage and interpretation','', 'Modeled discrete stones, boulders, gravel, standing stones, layered rock piles, cave spires, carved stone stacks and crystal-bearing rock. Continuous cliff terrain, entire floating islands, paving and architecture are outside this prop set. Water references have complete inferred undersides but no water, foam or shadow geometry. Source projection and resized/compressed images make depth/height approximate.','']
for s in catalogue['sources']:
 if not s['families']:lines.append(f"- **{s['source']}**: {s['assessment']}")
lines+=['', 'The cyan angular forms in poke_s are trees and were excluded after enlarged review. Its modeled stones are in the rivers. Cave shells, creatures, loose items and mushrooms are not rocks. The existing Pixelwood fire remains intact; its rock ring is also supplied as an empty ring.','', '## Validation and continuation','', 'The structural auditor checks all 462 files. Generation and validation check connected geometry, palette hashes, geometry inheritance, flat semantic colors, bilateral Cartoon geometry/paint and reserved index 255. The current VCOM importer and actual VoxelShape/VoxelModel renderer check voxel counts, dimensions, ground alignment and diffuse materials. The runtime report is tied to each delivered file by SHA-256. All seven treatments are rendered; Base/Cartoon also have four cardinal views.','', 'This is whole-model validation in an isolated game copy, not combat-map registration or cover/destruction testing. Larger rocks are not drop-in single-cell PieceKinds. Existing images/models are preserved; the live game was not modified.','', '- [Manifest](manifest.json), [source coverage](catalogue.json), [structural audit](structural-audit.json), [runtime report](godot-validation.json), [validation summary](validation-summary.json), [visual review](visual-review.json).', '- `python output/rocks/generate.py` reproduces generated models (save future hand edits first).', '- `qa/probe.gd` runs in `qa/game`; pass the absolute workspace path after `--`. The successful run ends with `ROCKS_RUNTIME_QA_PASS 462`.', '- `python output/rocks/validate.py` checks final files against the runtime report.', '- `python output/rocks/previews.py` and `python output/rocks/document.py` rebuild supporting sheets/records.', '- [Runtime source provenance](qa/source-provenance.json).','']
(HERE/'README.md').write_text('\n'.join(lines),encoding='utf-8')
for s in catalogue['sources']:
 stem=Path(s['source']).stem;dest=ROOT/'output'/stem;support=dest/'rocks';support.mkdir(exist_ok=True)
 families=[f for f in m['families'] if f['source']==s['source']]
 text=['# Rocks from '+s['source'],'',s['assessment'],'']
 for f in families:
  text+=['## '+f['name'],'',f['note'],'',f"Canvas: {' × '.join(map(str,f['size']))} voxels. Source conversion estimate: {f['scale']:.4g} voxels per displayed pixel. Depth and physical height inferred from sprite perspective. Actual occupied bounds are in the manifest.",'',f"[Source crop]({f['name']}_source.png) · [Seven variations]({f['name']}_variations.png) · [Four-direction geometry]({f['name']}_geometry.png)",'', '| Style | VOX | Voxels | Used colors |','| --- | --- | --- | --- |']
  for r in [r for r in m['models'] if r['family']==f['name']]:text.append(f"| {r['style']} | [{Path(r['file']).name}](../{Path(r['file']).name}) | {r['voxels']} | {r['colors']} |")
  match=next((d for d in duplicates if d['family']==f['name']),None)
  if match:text+=['','Base content matches '+match['same_base_content_as']+'; files are retained here for source-folder organization.']
  text+=['']
 text+=['Whole models, Z-up, translation `0 0 floor(canvas height/2)`, Mesh scale .0625, grounded and opaque diffuse. Minimal-color variants use one flat color for plain stone, two for moss/stone or crystal/stone. No water planes, foam, emission or automatic gameplay behavior.','', '[Collection evidence and reproduction](../../rocks/README.md) · [Authoring knowledge](../../../knowledge/ROCKS.md)','']
 (support/'README.md').write_text('\n'.join(text),encoding='utf-8')
 if families:
  rows=[r for r in m['models'] if r['family'] in s['families']]
  appendix='\n\n## Rocks (2026-10-28)\n\n'+f"[{len(families)} rock appearances, {len(rows)} complete models](rocks/README.md), including all seven treatments, source crops, previews and runtime validation.\n"
  p=dest/'README.md';old=p.read_text(encoding='utf-8') if p.exists() else '# '+stem+'\n'
  if '## Rocks (2026-10-28)' not in old:p.write_text(old+appendix,encoding='utf-8')
  p=dest/'FILES.md';old=p.read_text(encoding='utf-8') if p.exists() else '# Files\n'
  if '## Rock models (2026-10-28)' not in old:p.write_text(old+'\n\n## Rock models (2026-10-28)\n\n'+'\n'.join('- ['+Path(r['file']).name+']('+Path(r['file']).name+')' for r in rows)+'\n\n[Notes and previews](rocks/README.md).\n',encoding='utf-8')
for name,line in [('README.md','\n- [Rock collection](output/rocks/README.md): all 25 images reviewed; 66 source appearances, 462 complete models with all seven treatments, source-scale notes, previews and runtime validation (2026-10-28).\n'),('knowledge/MODELING.md','\n## Rock assets (2026-10-28)\n\nRead [ROCKS.md](ROCKS.md) for source coverage, faceted solid geometry, material grouping and validation. Under the current minimal-color amendment, plain stone uses one flat color; moss and crystal remain separate groups. Deliver complete models without cell files.\n')]:
 p=ROOT/name;s=p.read_text(encoding='utf-8')
 if line.strip() not in s:p.write_text(s+line,encoding='utf-8')
print('Documented',len(m['models']),'models;',len(duplicates),'duplicate Base appearances')
