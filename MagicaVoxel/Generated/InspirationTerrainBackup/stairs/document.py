"""Persist source decisions, scale estimates and complete-model placement records."""
import json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
m=json.loads((HERE/'manifest.json').read_text());files=[];coverage=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):p.write_text(s,encoding='utf-8')
reuse={
 'mario.jpg':'Raised platforms are terrain forms, not a separate staircase. No stair export.',
 'pixelwood_a.jpg':'No independent stair flight; tent entry already belongs to tent.',
 'pixelwood_b.gif':'House threshold belongs to the existing house. Slate ledges are cliff geometry.',
 'pixelwood_c.jpg':'Chest pedestal, rock ledges and log bridge are not stair flights.',
 'poke_a.jpg':'Terrace edges and bridge approaches, no independently drawn tread flight.',
 'poke_e.png':'Shoreline ledges and hoop fencing, no independent stairs.',
 'poke_l.png':'Terrace sprite blocks, no tread staircase in the sheet.',
 'poke_o.png':'Building thresholds are part of building work; continuous coastal ledges are not stairs.',
 'poke_u.jpg':'Stepped-looking wood spans are the already completed island bridges; no separate terrain stairs.'
}
notes={
 'poke_b.png':'House entrance stairs and cottage annex stairs are already in the buildings. Two outdoor flights differ in tread count.',
 'poke_c.png':'Four terrain-flight sizes retained. Door thresholds remain in buildings; bridge deck is covered by prior collections.',
 'poke_d.png':'Includes complete lower eastern terrace and its side stair, plus northern rough stone flight. Long retaining walls and the barred drain remain separate future assets.',
 'poke_f.png':'Northern clipped stair uses the tall flight. Clinic entry is already included in its building. Pond slats belong to bridges.',
 'poke_g.png':'Front and side flights have different visible tread counts. Building entrance steps remain in buildings.',
 'poke_h.png':'Repeated front and oblique four-step field flights share one family with rotations. Farmhouse upper-floor stair is already part of its building.',
 'poke_i.jpg':'All visible terrain flights use the short farm family with rotations. Calibration follows newer buildings, not early tree records.',
 'poke_j.jpg':'Two repeated forest stair sprites share one family.',
 'poke_k.jpg':'Three matching flights share one family. Corrected calibration: 29.4 displayed pixels span a two-tile tree repeat, hence about 14.72 pixels per tile.',
 'poke_m.png':'One short flight and one stacked double flight with a middle landing. Building stairs are not recreated.',
 'poke_n.png':'Two broad outdoor treads on the upper path; gate and house thresholds already belong to buildings.',
 'poke_p.png':'Side-on gray stair beside the lower bridge gets its own flight. The bridge remains unchanged.',
 'poke_q.png':'Short summit and longer lower flights kept distinct, with tan wood treads and segmented green bamboo edging. Existing skull/chain/bamboo fence props excluded.',
 'poke_r.png':'Northern and commercial-garden three-step flights share one family. House thresholds remain building details.',
 'poke_s.jpg':'Repeated six-step terrain flights and short eastern three-step flight covered. Central temple steps and smaller sanctuary steps already belong to the ruins collection, especially PokeS_RuinsSteppedSanctuary.',
 'poke_t.png':'Repeated warm stone cave-bank flights use rotations of one family. Side-on depth is inferred from the shared tread/curb motif; no duplicate orientation exports.'
}
for src in sorted([p for p in ROOT.iterdir() if p.suffix.lower() in ['.png','.jpg','.gif']]):
 fs=[f for f in m['families'] if f['source']==src.name]
 coverage.append(dict(source=src.name,sha256=sha(src),families=[f['name'] for f in fs],decision=notes.get(src.name,reuse.get(src.name,'No separate outdoor flight found.'))))
 if not fs:continue
 folder=ROOT/'output'/src.stem/'stairs';rows=[r for r in m['models'] if r['source']==src.name]
 write(folder/'manifest.json',json.dumps(dict(source=src.name,families=fs,models=rows),indent=2)+'\n')
 lines=[f'# {src.stem}: outdoor stairs','',notes[src.name],'','All files live in the parent image output folder. Each family has Base and all six established variations. [Shared collection rules and QA](../../stairs/README.md).','']
 for f in fs:
  name=f['name'];lines += [f'## {name}','',f"{f['note']} Canvas: {' × '.join(map(str,f['size']))} voxels. Rise: {f['rise']} voxels; {f['steps']} visible treads. Source calibration: {f['tile_pixels']} displayed pixels/tile. Crop: {f['crop']}.",'',f'[Source crop](reference/{name}.png) · [Seven styles]({name}_variations.png) · [Cardinal and underside views]({name}_geometry.png)','']
  for r in rows:
   if r['family']==name:
    filename=Path(r['file']).name;lines.append(f"- [{r['style']}](../{filename})")
    files.append(f"- [{name} — {r['style']}](../{src.stem}/{filename})")
  lines+=['']
 write(folder/'README.md','\n'.join(lines)+'\n')
 local=folder.parent/'README.md';text=local.read_text(encoding='utf-8',errors='replace') if local.exists() else f'# {src.stem}\n'
 marker='## Outdoor stairs — 2026-11-03'
 if marker not in text:write(local,text+f'\n\n{marker}\n\nAdded {len(fs)} families / {len(rows)} complete VOX files with all seven styles. [Stair models, source notes and previews](stairs/README.md). No per-cell exports.\n')
write(HERE/'source-review.json',json.dumps(coverage,indent=2)+'\n')
write(HERE/'FILES.md','# Outdoor stair files\n\n'+'\n'.join(files)+'\n')
print('Documented',len(coverage),'sources;',len(m['families']),'families across',len(notes),'images')
