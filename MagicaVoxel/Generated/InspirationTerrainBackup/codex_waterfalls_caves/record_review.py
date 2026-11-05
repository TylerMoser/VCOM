"""Run after visual review of all style and cardinal/underside sheets."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((HERE/'manifest.json').read_text());qa=json.loads((HERE/'godot-validation.json').read_text());v=json.loads((HERE/'validation-summary.json').read_text())
assert len(m['models'])==v['models']==154 and v['errors']==v['warnings']==0
signature=sha(HERE/'qa/probe.gd')
images=list(HERE.glob('*.png'))
for f in m['families']:
 assert sha(ROOT/f['source'])==f['source_sha256']
 folder=ROOT/'output'/Path(f['source']).stem/'codex_waterfalls_caves'
 images+=list(folder.glob(f['name']+'_*.png'))
 images+=list((folder/'previews').glob(f['name']+'*.png'))
for r in m['models']:
 q=qa[r['file']]
 assert sha(ROOT/r['file'])==r['sha256']==q['sha256']
 assert q['render_signature']==signature and q['whole_import']=='pass'
 assert q['grounded'] and q['dimensions_match'] and q['voxels']==r['voxels']
assert not (HERE/'qa/render-errors.log').read_text().strip()
baseline=json.loads((HERE/'prior-hashes.json').read_text());changed=[n for n,h in baseline.items() if not (ROOT/n).exists() or sha(ROOT/n)!=h]
record=dict(date='2026-11-03',author='Codex',families=22,models=154,review='Inspected target sources and enlarged crops, final overview, all six seven-style sheets and all six Base/Cartoon cardinal/underside sheets. Confirmed actual cave openings and water lips, connected sheets and foam silhouettes.',limits='Hidden structure/vertical scale are inferred. Current importer Mesh previews tested; live combat integration and fluid/cave gameplay not performed.',model_sha256={r['file']:r['sha256'] for r in m['models']},preview_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(images))},validation_sha256=sha(HERE/'validation-summary.json'),godot_validation_sha256=sha(HERE/'godot-validation.json'),prior_vox=len(baseline),prior_vox_unchanged=len(baseline)-len(changed),concurrent_external_changes=changed)
(HERE/'visual-review.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('Final hashes and importer evidence match for 154 files; prior unchanged',len(baseline)-len(changed),'external changes',len(changed))
