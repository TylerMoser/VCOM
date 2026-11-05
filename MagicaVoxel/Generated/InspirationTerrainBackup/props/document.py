"""Source-specific prop notes, coverage and reusable authoring records."""
from generate import *
m=json.loads((HERE/'manifest.json').read_text());coverage=json.loads((HERE/'source-review.json').read_text());reuse=json.loads((HERE/'reuse.json').read_text())
m['reuse']={r['source']:r['reuse'] for r in coverage if r['reuse']};(HERE/'manifest.json').write_text(json.dumps(m,indent=2))
text='''# Signs, benches and remaining decorative props

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
'''
for r in coverage:
 src=r['source'];stem=Path(src).stem;fs=[f for f in FAMILIES if f['source']==src];dest=ROOT/'output'/stem/'props'
 text+=f"| [{src}](../{stem}/props/README.md) | {len(fs)} | {r['notes']} |\n"
 local=f"# {src}: signs, benches and decorations\n\n{r['notes']}\n\n[Collection rules and validation](../../props/README.md) | [Local manifest](manifest.json)\n\n"
 if r['reuse']:
  local+='Reuse these existing families, including all seven styles:\n\n'
  for b in r['reuse']:
   path=Path(b);local+=f'- [{path.stem}](../../{path.parent.name}/{path.name})\n'
  local+='\n'
 for f in fs:
  local+=f"## {f['name']}\n\nCanvas: {' x '.join(map(str,f['size']))} voxels. Original source crop: {f['crop']}. Hidden surfaces and depth are inferred; no gameplay behavior is attached.\n\n[Source]({f['name']}_source.png) | [All seven styles]({f['name']}_variations.png) | [Cardinal views]({f['name']}_geometry.png)\n\n"
  for st in STYLES:
   fn=f['name']+('' if st=='Base' else '_'+st)+'.vox';local+=f'- [{st}](../{fn})\n'
  local+='\n'
 (dest/'README.md').write_text(local)
 (dest/'manifest.json').write_text(json.dumps({'source':src,'review':r,'families':fs,'models':[row for row in m['models'] if row['file'].split('/')[1]==stem],'reuse':[row for row in reuse if row['source']==src]},indent=2))
text+='\n## Rebuild\n\nRun `python output/props/generate.py`; run `qa/probe.gd` through the saved scratch Godot project with this workspace absolute path as the user argument; then run `python output/props/previews.py`, `python output/props/validate.py` and `python output/props/document.py`. Review renders before marking completion. The generator checks previous manifest hashes and refuses to overwrite hand edits. The render probe caches model hashes; invalidate report entries when changing render code. Current copied game sources are pinned in `qa/source-provenance.json`.\n'
(HERE/'README.md').write_text(text)
# Rebuild the candidate sheets using the final, corrected classifications and crop coordinates.
for page in range(math.ceil(len(FAMILIES)/12)):
 sheet=Image.new('RGB',(1200,900),'#dfdfd5');d=ImageDraw.Draw(sheet)
 for j,f in enumerate(FAMILIES[page*12:page*12+12]):
  im=Image.open(ROOT/f['source']).crop(f['crop']).convert('RGB');scale=min(285/im.width,240/im.height);im=im.resize((int(im.width*scale),int(im.height*scale)),Image.Resampling.NEAREST);x=j%4*300;y=j//4*300;sheet.paste(im,(x,y+35));d.text((x+3,y+5),f['name'],fill='black')
 sheet.save(HERE/'reference'/f'candidates_{page+1}.png')
