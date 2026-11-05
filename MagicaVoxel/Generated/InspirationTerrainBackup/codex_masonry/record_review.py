"""Run only after reviewing the final style and geometry sheets."""
from generate import HERE,ROOT,sha
import json
m=json.loads((HERE/'manifest.json').read_text());qa=json.loads((HERE/'godot-validation.json').read_text());v=json.loads((HERE/'validation-summary.json').read_text())
assert len(m['models'])==len(qa)==v['models']==28 and v['errors']==0
for r in m['models']:
 q=qa[r['file']];assert sha(ROOT/r['file'])==r['sha256']==q['sha256'];assert q['whole_import']=='pass' and q['render_signature']==sha(HERE/'qa/probe.gd')
assert not (HERE/'qa/render-errors.log').read_text().strip()
record=dict(date='2026-11-04',models=28,families=4,review='Reviewed source images and enlarged source crop, final seven-style sheet and Base/Cartoon cardinal/underside geometry sheet. Drain gaps, connected stone construction and recessed pedestal seat verified.',limits='Whole-model importer tested; combat placement, traversal and cover not tested.',model_sha256={r['file']:r['sha256'] for r in m['models']},sheet_sha256={p.name:sha(p) for p in HERE.glob('*.png')},import_evidence_sha256=sha(HERE/'godot-validation.json'),validation_sha256=sha(HERE/'validation-summary.json'))
(HERE/'visual-review.json').write_text(json.dumps(record,indent=2));print('Final evidence matches 28 reviewed models')
