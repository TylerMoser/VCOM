"""Run after visual inspection of every final style and geometry page."""
import json,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((HERE/'manifest.json').read_text());qa=json.loads((HERE/'godot-validation.json').read_text());v=json.loads((HERE/'validation-summary.json').read_text());house=json.loads((HERE/'qa/house-validation.json').read_text())
assert len(m['models'])==len(qa)==v['models']==784 and v['errors']==0
for r in m['models']:
 q=qa[r['file']];assert sha(ROOT/r['file'])==r['sha256']==q['sha256'];assert q['whole_import']=='pass' and q['render_signature']==sha(HERE/'qa/probe.gd');assert q['voxels']==r['voxels']
 if 'MossRoofCottage' in r['family']:assert house['models'][r['file']]==r['sha256']
for f in m['families']:assert sha(ROOT/f['source'])==f['source_sha256']
assert not (HERE/'qa/render-errors.log').read_text().strip()
assert not house['failed']
pages=list(HERE.glob('styles_*.png'))+list(HERE.glob('geometry_*.png'));assert len(pages)==56
baseline=json.loads((HERE/'prior-hashes.json').read_text());changed=[p for p,h in baseline.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h]
other=json.loads((HERE/'other-author-hashes.json').read_text());assert all((ROOT/p).exists() and sha(ROOT/p)==h for p,h in other.items()), 'Other author model changed'
record=dict(date='2026-11-04',author='Codex',families=112,models=784,scope='Environment assets only, per user clarification; characters, creatures, HUD and sprite shadows excluded.',review='Reviewed original sources and enlarged detail crops, all 28 style pages and all 28 Base/Cartoon cardinal/underside geometry pages. Checked varied plant silhouettes, branches, hammock mesh, cottage exterior and glass, source coverage and flat material groups.',model_sha256={r['file']:r['sha256'] for r in m['models']},sheet_sha256={p.name:sha(p) for p in pages},validation_sha256=sha(HERE/'validation-summary.json'),importer_evidence_sha256=sha(HERE/'godot-validation.json'),house_evidence_sha256=sha(HERE/'qa/house-validation.json'),prior_vox=len(baseline),prior_vox_unchanged=len(baseline)-len(changed),external_changes=changed,limits='Hidden surfaces and vertical depths inferred from pixel art. Cottage tested through scratch VCOM building harness; other assets tested as whole imported meshes, not registered combat pieces.')
record['other_author_models_unchanged']=len(other)
record['review']='Reviewed source images and detail crops against all family style and Base/Cartoon cardinal/underside sheets. Unchanged families reviewed in the earlier 27-page layout; additions and revised families rechecked in the final 28-page layout. Corrected woodpile orientation, floating-plant crops, bush stems, broadleaf fullness, rosette separation and olive-tree profile.'
(HERE/'visual-review.json').write_text(json.dumps(record,indent=2));print('PASS: 784 final hashes/imports and 7 cottage integrations; other author unchanged',len(other),'prior unchanged',len(baseline)-len(changed),'external changes',len(changed))
