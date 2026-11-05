"""Record this delivered collection without changing earlier model files."""
from pathlib import Path
import json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read_text(p):
 # A prior audit update inserted a Windows-1252 dash into otherwise UTF-8 text.
 # Preserve valid UTF-8 and repair only undecodable individual Windows bytes.
 text=p.read_bytes().decode('utf-8',errors='surrogateescape')
 return ''.join(bytes([ord(c)-0xdc00]).decode('cp1252') if 0xdc80<=ord(c)<=0xdcff else c for c in text).replace('\r\n','\n')
def append(p,text,marker):
 old=read_text(p) if p.exists() else ''
 if marker not in old:p.write_text(old.rstrip()+'\n\n'+text+'\n',encoding='utf-8')
append(ROOT/'README.md','- [Complete bridges](output/bridges/README.md): 17 new families / 119 complete files across 11 source images, all seven styles; preserved bridge reuse, corrected gate/terrain classifications, source-relative spans, current-importer validation and bank-placement previews (2026-11-03).','[Complete bridges](output/bridges/README.md)')
append(ROOT/'knowledge/MODELING.md','## Complete bridges (2026-11-03)\n\nSee [BRIDGES.md](BRIDGES.md) for whole crossings, bank/deck alignment, genuine open arches, intentional plank seams and the two-internal-model VOX scene used for a 320-voxel span. Complete files remain the deliverable; no per-cell exports or game integration are implied.','## Complete bridges (2026-11-03)')
m=json.loads((HERE/'manifest.json').read_text())
for source in sorted({f['source'] for f in m['families']}):
 fs=[f for f in m['families'] if f['source']==source];stem=Path(source).stem
 append(ROOT/'output'/stem/'README.md',f'## Complete bridges (2026-11-03)\n\n[Bridge collection for this image](bridges/README.md): {len(fs)} new families, {len(fs)*7} complete VOX files with all seven treatments, source crops, cardinal/underside views and bank-placement previews. Existing assets are preserved. Shared validation and generation: [complete bridges](../bridges/README.md).','## Complete bridges (2026-11-03)')
p=ROOT/'knowledge/REMAINING_ASSETS.md';text=read_text(p)
notice='**Bridge completion update, 2026-11-03:** [17 new families / 119 files](../output/bridges/README.md) now cover the missing complete crossings. Existing Pixelwood C log and poke_c covered bridges are reused. poke_n is a roofed gate already covered by its newer buildings, not a bridge; some poke_s walkways and the lower poke_d platform are terrain/garden masonry. See the collection source review for all 25 image decisions.\n\n'
if '**Bridge completion update' not in text:text=text.replace('# Remaining inspiration assets\n\n','# Remaining inspiration assets\n\n'+notice,1)
text=text.replace('Free river bridges, unrelated terrain stairs, floating-island/cliff bodies, waterfalls and creatures remain outstanding','Unrelated terrain stairs, floating-island/cliff bodies, waterfalls and creatures remain outstanding')
lines=text.splitlines()
newrows={
 'poke_a.jpg':'Cliff/terrace network and waterfalls remain. Complete picket bridge is now covered by the bridge collection.',
 'poke_c.png':'Outdoor stairs/landings, cliff banks, waterfall cascades and characters/river creatures remain. Houses, covered bridge and now the downstream uncovered bridge are covered.',
 'poke_d.png':'Retaining walls, terrain stairways/landings, lower eastern stair platform, arched barred riverbank drain, cliff walls, waterfalls and red spotted mushroom clumps remain. Four-arch river bridge, southern single arch, eastern overpass and their parapets are covered.',
 'poke_f.png':'Autumn tree appearances (no source tree exports/reuse record), terrain stairs, cliff banks and human/creature sprites remain. Pond slat crossing is now covered alongside buildings, statue, lamps and fence.',
 'poke_h.png':'Outdoor terrain stairways, cliff banks, people and creatures remain. Complete farm bridge is covered with an explicitly inferred far end beyond the image crop; wheat, hay, pitchfork, farmhouse and rails already exist.',
 'poke_i.jpg':'Terrain stairways and cliff terraces remain. All three crossing forms now have complete models; houses/day care, rails and crops already exist.',
 'poke_m.png':'Outdoor stairs, cliff/gully network, waterfall sections and people/creatures remain. Diagonal-board river bridge is now covered alongside cabins/lodge, logs, stumps and vegetation.',
 'poke_n.png':'Terrain steps and continuous cliffs remain. The newer building collection covers houses and the roofed gate; the gate was incorrectly labeled a bridge in the old audit. Trees, bench, fence, sign, lamps and water plants are covered.',
 'poke_p.png':'Blue-roof house, cave entrance, rocky gully/cliff system and adjacent gray diagonal terrain stair/ramp remain. Both plank-span lengths and their corner posts are now covered; reuse rotations for differently oriented copies.',
 'poke_s.jpg':'Terrain stairs outside the authored sanctuaries, floating-island/cliff bodies, waterfalls and creatures remain. The eastern river bridge is now covered alongside ruins/temple courts, garden walls, fountain, statue, balustrade, lamps and trees.',
 'poke_t.png':'Cave wall/ledge system and entrances, terrain stairs/sidewalls, creatures and unresolved pale sprites remain. Complete tubular-rail bridges are covered and reused with rotations; other existing cave props remain covered.',
 'poke_u.jpg':'Red-roof houses, floating cliffs/island undersides, narrow waterfalls and people/creatures remain. Both island plank-crossing lengths are now covered alongside trees, plants, notices and ground/water tiles.'}
for i,line in enumerate(lines):
 if line.startswith('3. **Complete bridges and crossings:'):
  lines[i]='3. **Complete bridges and crossings - completed 2026-11-03:** [17 new families / 119 files](../output/bridges/README.md), plus preserved reuse of the existing covered bridge and log bridge. The poke_n candidate is an already-modeled roofed gate, not a bridge.'
 if line.startswith('1. **Buildings without'):
  lines[i]=line.replace('poke_n houses (upper yellow/orange gabled house and lower timber houses); ','')
  if 'The poke_n houses and roofed gate are now covered' not in lines[i]:lines[i]+=' The poke_n houses and roofed gate are now covered by the newer building collection.'
 if line.startswith('8. **Remaining masonry details:'):lines[i]=line.replace('poke_d bridge parapets, retaining walls','poke_d retaining walls')
 if line.startswith('2. Bridges and freestanding stairs,'):lines[i]='2. Freestanding terrain stairs remain; complete bridges are now covered (2026-11-03).'
 if line.startswith('1. Complete remaining buildings in poke_n/o/p/r/u'):lines[i]=line.replace('poke_n/o/p/r/u','poke_o/p/r/u')
 if 'Separate river bridges and natural island supports remain outside this batch.' in line:lines[i]=lines[i].replace('Separate river bridges and natural island supports remain outside this batch.','River bridges are covered by the subsequent bridge collection; natural island supports remain outstanding.')
 for src,note in newrows.items():
  if line.startswith('| '+src+' |'):lines[i]=f'| {src} | {note} |'
p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Updated collection links and remaining-asset records.')
