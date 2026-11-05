"""Write only Codex-owned collection records; coexist with other active authors."""
import json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
m=json.loads((HERE/'manifest.json').read_text());index=[];coverage=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,s):p.write_text(s,encoding='utf-8')
decisions={
 'pixelwood_c.jpg':'One broad curtain. Standing stone, chest, log bridge and earth banks excluded; existing assets remain reusable.',
 'poke_a.jpg':'Short western and bridge-adjacent terrace waterfalls share one family. White outlines on level ponds are shoreline foam, not extra falls.',
 'poke_c.png':'Two different sizes: the upper five-band cascade and lower three-band cascade. Shallow shelves between bands are an inferred reconstruction.',
 'poke_d.png':'Northern upper fall, central wide low spillway and southwest narrower fall retained separately. The barred drain is masonry, not a cave mouth or a waterfall.',
 'poke_m.png':'Repeated low foamy lips at approximately (330,470), (411,608), (420,834) share one family. Reeds, pale shoreline corners and water texture alone do not form waterfalls.',
 'poke_s.jpg':'Nine waterfall lengths/widths cover bounded garden drops and longer island drops. Repeated appearances reuse families. Visible vertical extents guide lengths; obscured terminations are inferred. Cloud gaps and temple recesses are not cave mouths.',
 'poke_u.jpg':'Two narrow visible falling-water ribbons: upper behind the northern house and lower through an island notch. Other blue gaps are atmospheric background; no arbitrary curtains added there.',
 'poke_p.png':'Upper pointed rock mouth with a real passage. The model includes a compact rock surround, not the whole gully.',
 'poke_t.png':'Eastern small rounded mouth and larger irregular southern recess. Tiny dark marks by the western boulder and upper cliff are rock/shadow details and are excluded. Source black void beyond the southern recess is not modeled as black solid voxels.'
}
for src in sorted(p for p in ROOT.iterdir() if p.suffix.lower() in ['.jpg','.png','.gif']):
 fs=[f for f in m['families'] if f['source']==src.name]
 coverage.append(dict(source=src.name,sha256=sha(src),reinspected_for_this_batch=bool(fs),families=[f['name'] for f in fs],decision=decisions.get(src.name,'No target in the previous waterfall/cave-mouth audit; no model generated in this scoped batch.')))
 if not fs:continue
 folder=ROOT/'output'/src.stem/'codex_waterfalls_caves';rows=[r for r in m['models'] if r['source']==src.name]
 save(folder/'manifest.json',json.dumps(dict(author='Codex',source=src.name,families=fs,models=rows),indent=2)+'\n')
 lines=[f'# {src.stem}: Codex waterfalls and cave entrances','',decisions[src.name],'','[Shared collection rules, placement and validation](../../codex_waterfalls_caves/README.md). Complete VOX files are in the parent image folder. `Codex` in the family name distinguishes this batch from other authors.','']
 for f in fs:
  name=f['name'];lines += [f'## {name}','',f['note'],'',f"Canvas: {' × '.join(map(str,f['size']))} voxels; {f['tile_pixels']} displayed pixels/tile. Source crop: {f['crop']}.",'',f'[Source](reference/{name}.png) · [All styles]({name}_variations.png) · [Cardinal and underside views]({name}_geometry.png)','']
  if f['kind']=='waterfall':lines += [f"Water width: {f['width']} voxels; interpreted vertical drop: {f['drop']}; tiers: {f['tiers']}; free island fall: {f['free']}.",'']
  else:lines += [f"Nominal mouth width/height: {f['opening']} voxels. Through-passage depth: {f['size'][1]}. Floor top: z=2. Hidden depth is inferred.",'']
  for r in rows:
   if r['family']==name:
    fn=Path(r['file']).name;lines.append(f"- [{r['style']}](../{fn})");index.append(f"- [{name} — {r['style']}](../{src.stem}/{fn})")
  lines+=['']
 save(folder/'README.md','\n'.join(lines)+'\n')
save(HERE/'FILES.md','# Codex waterfall and cave models\n\n'+'\n'.join(index)+'\n')
save(HERE/'source-review.json',json.dumps(coverage,indent=2)+'\n')
print('Documented',len(m['families']),'families from',len(decisions),'reinspected sources')
