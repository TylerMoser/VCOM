"""Build collection and source-specific documentation without replacing older asset notes."""
from pathlib import Path
import json,hashlib,math
from generate import HERE,ROOT,STYLES
from voxlib import read
manifest=json.loads((HERE/'manifest.json').read_text());families=manifest['families'];models=manifest['models'];reuse=manifest['reuse']
sources=json.loads((HERE/'source-inventory.json').read_text())
def append_once(path,text):
 old=path.read_text(encoding='utf-8') if path.exists() else ''
 if text.strip() not in old:path.write_text(old+'\n'+text+'\n',encoding='utf-8')
seen={};duplicates=[]
for row in models:
 if row['style']!='Base':continue
 size,v,pal=read(ROOT/row['file']);digest=hashlib.sha256(repr((size,sorted(v.items()),pal)).encode()).hexdigest()
 if digest in seen:duplicates.append({'file':row['file'],'same_geometry_and_paint_as':seen[digest]})
 else:seen[digest]=row['file']
(HERE/'duplicates.json').write_text(json.dumps(duplicates,indent=2))
intro='''All models are complete, single-model, Z-up VOX files with explicit palettes and scene translation `0 0 floor(height/2)`. One voxel is 1/16 of a game tile. Dimensions follow the visible sprite scale; depth and hidden stems are inferred. ShortGrassPatch is a reusable tile of low grass accents interpreted from the source lawn, not a literal extraction of a complete terrain tile. There are no soil slabs, water volumes, cell exports or brush packages.

Cartoon changes geometry and balances both horizontal mirror planes, including paint. Other treatments inherit exact Base or Cartoon coordinates. CratePalette retains the pinned crate RGBA bytes. TwoColor follows the current minimal-material amendment: one flat foliage color, plus petal and flower-center colors where needed. Plain grass uses one color; a daisy normally uses three. Lighting still produces shading. Older reused shrubs retain their original two-color contract.

Separate plants in a patch are intentional components, each touching z=0. Lily pads use the water surface as their placement datum; submerged foliage uses the bed. They contain opaque diffuse materials, without glass or emission. Configure decorative grass and flowers with `solid=false` when integrating. These files have been checked in the VCOM standalone voxel reader/renderer at scale 0.0625; no combat-map registration or gameplay testing was performed.
'''
lines=['# Flowers, bushes and grass','',f'**{len(models)} new complete VOX models**: seven treatments for **{len(families)} source appearances**. All {len(sources)} originals reviewed. Existing bush families are linked and preserved; Pixelwood duplicates retain their first owner.','', '[Overview](overview.png) | [Manifest](manifest.json) | [Validation](validation-summary.json) | [Visual review](visual-review.json) | [Duplicate contents](duplicates.json)','',intro,'## Source coverage','','| Image | New appearances | New files | Reused families |','| --- | ---: | ---: | ---: |']
for source in sources:
 src=source['source'];stem=Path(src).stem;fs=[f for f in families if f['source']==src];rs=[r for r in models if r['file'].split('/')[1]==stem]
 lines.append(f'| [{src}](../{stem}/vegetation/README.md) | {len(fs)} | {len(rs)} | {len(reuse.get(src,[]))} |')
 local=['# '+src+' — flowers, bushes and grass','',f'{len(fs)} new appearances; {len(rs)} complete VOX files. [Collection index](../../vegetation/README.md).','',intro,'## New models','']
 for f in fs:
  local.extend(['### '+f['name'],'',f'Canvas XYZ: **{" x ".join(map(str,f["size"]))}**. Approximate source scale: {f["scale"]:.3g} voxel(s) per displayed pixel. Crop XYXY: `{f["crop"]}`. '+f['note'],'',f'[Source crop]({f["name"]}_source.png) | [Seven treatments]({f["name"]}_variations.png) | [Four directions]({f["name"]}_geometry.png)',''])
  for r in rs:
   if r['family']==f['name']:local.append(f'- [{r["style"]}](../{Path(r["file"]).name}) — {r["voxels"]} voxels; {r["colors"]} paint colors; {len(r["components"])} rooted component(s).')
  local.append('')
 local.extend(['## Reused models',''])
 for base in reuse.get(src,[]):
  owner=Path(base).parts[1];asset=Path(base).stem
  local.append(f'- **{asset}**: '+', '.join(f'[{s}](../../{owner}/{asset+("" if s=="Base" else "_"+s)}.vox)' for s in STYLES)+'.')
 if not reuse.get(src):local.append('No previously authored bush family is required for this source.')
 local.extend(['','## Scope and continuation','','Repeated placements of one appearance are represented once. Trees and their attached fruit remain in their existing collections. Creatures, mushrooms, stones, terrain banks, loose fallen leaves, harvested hay bales, fences and buildings are outside this collection. Small compressed details use appearance names rather than botanical species claims.','', 'Generator: `output/vegetation/generate.py`; geometry: `sculpt.py`; source decisions: `catalogue.py`. Run from the workspace root. Regeneration replaces only the named new families; preserve manual edits separately. [Local manifest](manifest.json) records hashes, semantic groups, occupied bounds, connectivity and palette identity.'])
 dest=ROOT/'output'/stem/'vegetation';dest.mkdir(exist_ok=True)
 (dest/'README.md').write_text('\n'.join(local)+'\n',encoding='utf-8')
 append_once(dest.parent/'README.md',f'- [Flowers, bushes and grass](vegetation/README.md): {len(fs)} new appearances, {len(rs)} complete models, and existing-family reuse links.')
 append_once(dest.parent/'FILES.md',f'\n## Flowers, bushes and grass\n\n[Full model and variation index](vegetation/README.md)\n\n'+'\n'.join('- ['+Path(r['file']).name+']('+Path(r['file']).name+')' for r in rs))
lines.extend(['','## Comparison sheets','','Each family uses a matched camera and lighting across seven treatments; families are framed independently.'])
for i in range(1,math.ceil(len(families)/6)+1):lines.append(f'- Page {i}: [Variations](variations_{i:02}.png) | [Cardinal geometry views](geometry_{i:02}.png)')
lines.extend(['','## Reproduction','','Run from the workspace root:','','```powershell','python output/vegetation/generate.py','# Run qa/probe.gd with Godot against qa/game, passing the absolute workspace path after --.','python output/vegetation/validate.py','python output/vegetation/previews.py','python output/vegetation/document.py','```','','The isolated QA project contains a snapshot of the current game scripts/addons, with source hashes in `qa/source-provenance.json`. `godot-validation.json` pins every rendered model hash. Original images and all pre-existing top-level delivered VOX files are verified against the preservation baseline.','', 'Inspection is of geometry and rendering, not botanical identification or gameplay behavior. Source projections do not uniquely determine hidden depth or height; recorded sizes are authoring estimates.'])
(HERE/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
append_once(ROOT/'README.md',f'- [Flowers, bushes and grass](output/vegetation/README.md): all 25 images reviewed; {len(families)} new appearances, {len(models)} complete models with seven treatments, plus preserved bush-family reuse links.')
append_once(ROOT/'knowledge/MODELING.md','## Low vegetation authoring\n\nRead [VEGETATION.md](VEGETATION.md) for flowers, bushes, grasses and aquatic plants, including rooted clumps, reuse and current minimal-color semantics.')
print('Documented',len(models),'new models;',len(duplicates),'duplicate Base contents recorded')
