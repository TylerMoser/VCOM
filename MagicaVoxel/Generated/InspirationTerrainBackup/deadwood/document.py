"""Write collection/source records without replacing previous category notes."""
from generate import *
notes={
'mario.jpg':'No discrete stump or fallen log identified. Carved pillars are stone; characters, signs, and background tree silhouettes are excluded.',
'pixelwood_a.jpg':'Fallen trunk with broken side branch. Existing PixelwoodA_Stump and all six variations are preserved and reused.',
'pixelwood_b.gif':'The fallen log and cut stumps repeat Pixelwood A artwork. Reuse its families; do not create duplicate models. Campfire remains in the lights collection.',
'pixelwood_c.jpg':'The very long, bark-covered natural log across the stream is a separate size family. Reuse the existing Pixelwood A cut stump.',
'poke_c.png':'Repeated small forked driftwood in the river becomes one reusable family. The masonry/wooden built bridge is architecture.',
'poke_g.png':'One fallen-log appearance and one small cut-stump appearance, repeated near houses.',
'poke_m.png':'Long and short fallen logs, broad rooted cut stumps, the taller stump beneath a character, and a tiny root stump. Repeated medium stumps reuse the broad family. Characters and tools are excluded from geometry.',
'poke_o.png':'Short fallen log, clean-cut stump, and an irregular tan/brown splintered wood remnant. The latter is interpreted as a low broken stump/root remnant, not a character; its obscured underside is inferred.',
'poke_p.png':'Three distinct sizes/profiles: broad large cut stump, tiny flared root stump and narrower sapling stump.',
'poke_j.png':'Pale-topped props checked against nearby trees and matching sprites: lamps/flowers, not confidently identifiable stumps.',
'poke_k.png':'Small pale and orange props beside shrubs resolve to flowers. No distinct stump/log identified.',
'poke_s.png':'Tiny brown ground accents are mushroom-like, not clearly exposed timber. No confident stump/log candidate.',
'poke_t.png':'Banded brown object is a barrel; dark cliff formations are rocks. Neither belongs in this collection.',
'poke_h.png':'Wheat, hay stacks, tools and manufactured fence/bridge timber are excluded; no discrete deadwood prop identified.'}
manifest=json.loads((HERE/'manifest.json').read_text());sources=json.loads((HERE/'source-inventory.json').read_text());coverage=[]
intro='''# Stumps and logs

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
'''
for src in sources:
 name=src['source'];families=[f for f in FAMILIES if f['source']==name];stem=Path(name).stem;support=ROOT/'output'/stem/'deadwood'
 note=notes.get(name,'No discrete stump or fallen log confidently identified. Living tree trunks, rocks, characters, fences, signs and constructed bridge timbers are outside this collection.')
 coverage.append({'source':name,'reviewed':True,'families':[f['name'] for f in families],'reuse':manifest['reuse'].get(name,[]),'notes':note})
 intro+=f'| [{name}](../{stem}/deadwood/README.md) | {len(families)} | {note} |\n'
 text=f'# {name}: stumps and logs\n\n{note}\n\n[Collection conventions and runtime limits](../../deadwood/README.md) | [Local manifest](manifest.json)\n\n'
 if manifest['reuse'].get(name):text+='Reuse: '+', '.join(manifest['reuse'][name])+'. All seven styles apply.\n\n'
 for f in families:
  text+=f"## {f['name']}\n\nCanvas {f['size'][0]} x {f['size'][1]} x {f['size'][2]} voxels (X width, Y length, Z height). Source crop: {f['crop']}; hidden surfaces and depth inferred.\n\n[Source]({f['name']}_source.png) | [Seven treatments]({f['name']}_variations.png) | [Four-direction geometry]({f['name']}_geometry.png)\n\n"
  for style in STYLES:
   filename=f['name']+('' if style=='Base' else '_'+style)+'.vox';text+=f'- [{style}](../{filename})\n'
  text+='\n'
 (support/'README.md').write_text(text)
intro+='\n## Rebuild and review\n\nRun `python output/deadwood/generate.py`, then the saved `qa/probe.gd` against its scratch game with the workspace absolute path as user argument. Run `python output/deadwood/previews.py` and `python output/deadwood/validate.py`. The generator refuses to overwrite a delivered file whose hash differs from its previous manifest (possible hand edit). The render probe caches unchanged hashes; invalidate report entries when changing render code. Review the final renders before marking completion.\n'
(HERE/'README.md').write_text(intro)
(HERE/'source-review.json').write_text(json.dumps(coverage,indent=2))
