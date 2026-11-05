"""Write source-specific bridge records and reusable collection index."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];m=json.loads((HERE/'manifest.json').read_text())
special={
 'pixelwood_c.jpg':('Reuse the existing complete natural log bridge; no duplicate.', ['PixelwoodC_LogBridge']),
 'poke_c.png':('New downstream uncovered bridge; preserve/reuse the existing covered-bridge pavilion and span.', ['PokeC_BridgePavilion','PokeC_BridgeSpan']),
 'poke_n.png':('Correction: the apparent crossing is the roofed gate, already converted in the newer building collection. No bridge generated.', ['PokeN_RoofedGate']),
 'poke_d.png':('Three true spans: long four-arch river bridge, short southern river bridge, eastern road overpass. Lower eastern stair platform is terrain, excluded.',[]),
 'poke_p.png':('Two identical east-west crossings reuse the longer model; north-south shorter crossing uses the shorter model, rotated. Gray diagonal ramp is terrain stairs.',[]),
 'poke_s.jpg':('Eastern river bridge included; western pale walkway/edging is garden masonry already covered by ruins/fences.',[]),
 'poke_t.png':('One bridge type reused at all four placements, with quarter-turn rotations for the vertical views.',[]),
 'poke_h.png':('Far end is cropped; complete ten-tile model is an explicitly inferred extension of the visible span.',[]),
 'poke_i.jpg':('Three distinct crossings: bowed railed, shorter flat railed, and narrow unrailed. Uses newer building scale calibration of 9.5 displayed pixels/tile.',[])}
sources=[];files=['# Complete bridge model index','','Each family has seven complete files. Previews are framed independently; thumbnail size is not game scale.','']
for image in sorted(p for p in ROOT.iterdir() if p.suffix.lower() in ('.png','.jpg','.gif')):
 fs=[f for f in m['families'] if f['source']==image.name];rows=[r for r in m['models'] if r['source']==image.name]
 decision,reuse=special.get(image.name,('New complete crossings authored from the visible source.' if fs else 'No missing independent bridge identified; terrain steps, ledges, building porches, shoreline and scenery borders excluded.',[]))
 record={'source':image.name,'sha256':hashlib.sha256(image.read_bytes()).hexdigest(),'reviewed':True,'decision':decision,'new_families':[f['name'] for f in fs],'reuse':[f'output/{image.stem}/{name}.vox' for name in reuse]};sources.append(record)
 folder=ROOT/'output'/image.stem/'bridges';folder.mkdir(exist_ok=True)
 (folder/'manifest.json').write_text(json.dumps({'source_review':record,'families':fs,'models':rows},indent=2))
 lines=[f'# {image.name}: complete bridges','',decision,'','[Collection rules and validation](../../bridges/README.md)','']
 for old in reuse:lines.append(f'- Existing family: [{old}](../{old}.vox), with its existing six style alternatives.')
 for f in fs:
  name=f['name'];lines += ['',f'## {name}','',f['note'],'',f"Canvas XYZ: {' × '.join(map(str,f['size']))}; bank deck elevation: {f['deck']} voxels. Source tile estimate: {f['tile_pixels']} displayed pixels. Source crop: {f['crop']}.",'',f'[Source](reference/{name}.png) · [Seven styles]({name}_variations.png) · [Cardinal and underside views]({name}_geometry.png) · [Bank placement](previews/{name}_banks.png)','']
  files += [f'## {name}','',f"Source: {f['source']}; canvas {f['size']}; {f['note']}",'',f"[Seven styles](../{image.stem}/bridges/{name}_variations.png) · [Geometry](../{image.stem}/bridges/{name}_geometry.png)",'']
  for r in rows:
   if r['family']==name:
    file=Path(r['file']).name;lines.append(f"- [{r['style']}](../{file})");files.append(f"- [{r['style']}](../{image.stem}/{file})")
 (folder/'README.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
(HERE/'source-review.json').write_text(json.dumps(sources,indent=2),encoding='utf-8');(HERE/'FILES.md').write_text('\n'.join(files)+'\n',encoding='utf-8')
print('Documented',len(sources),'sources;',len(m['families']),'families')
