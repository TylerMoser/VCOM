from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
for name,text in {
 'README.md':'\n\n## Outdoor stairs — 2026-11-03\n\nCompleted 26 families / 182 VOX files in the corresponding image folders. [Collection, source coverage and previews](output/stairs/README.md) · [Persistent authoring notes](knowledge/STAIRS.md). All seven styles; no per-cell files.\n',
 'knowledge/MODELING.md':'\n\n## Outdoor terrain staircases\n\nSee [STAIRS.md](STAIRS.md) for complete flights and landings, uphill-axis placement, image scale corrections, material groups, and the distinction between imported stair art and combat traversability.\n'
}.items():
 p=ROOT/name;s=p.read_text(encoding='utf-8');marker=text.strip().splitlines()[0]
 if marker not in s:p.write_text(s+text,encoding='utf-8')
p=ROOT/'knowledge/REMAINING_ASSETS.md';s=p.read_text(encoding='utf-8')
marker='**Outdoor stair completion update, 2026-11-03:**'
if marker not in s:
 s=s.replace('# Remaining inspiration assets','# Remaining inspiration assets\n\n'+marker+' [26 families / 182 files](../output/stairs/README.md) now cover the freestanding terrain staircases, including the poke_d lower eastern stair landing and poke_m double flight. All 25 images were reviewed; existing building and sanctuary stairs are reused. The per-image table below is historical for stairs as well as bridges; cliffs, retaining networks, waterfalls and other unrelated subjects remain outstanding. See source-review.json in the stair collection for current coverage.',1)
 s=s.replace('4. **Freestanding terrain staircases and their supports:** notably poke_b/c/d/f/g/h/i/j/k/m/n/p/q/r/s/t. Include landings, stringers and retaining sidewalls where drawn. Some buildings already contain their own entrance/upper-floor stairs; do not count those again.','4. **Outdoor terrain stairs and supports — completed 2026-11-03:** [26 families / 182 models](../output/stairs/README.md), including landings, stringers, stone/bamboo curbs and the lower eastern poke_d platform. Existing building and sanctuary stairs are preserved.')
 s=s.replace('2. Freestanding terrain stairs remain; complete bridges are now covered (2026-11-03).','2. Outdoor stairs and complete bridges — completed 2026-11-03; reuse the new collections.')
 p.write_text(s,encoding='utf-8')
print('Updated persistent stair coverage records')
