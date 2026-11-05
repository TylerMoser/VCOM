"""Record completed human-facing visual review after checking final artifact hashes."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

manifest = json.loads((HERE / 'manifest.json').read_text())
imports = json.loads((HERE / 'godot-validation.json').read_text())
validation = json.loads((HERE / 'validation-summary.json').read_text())
assert validation['models'] == 119 and validation['errors'] == validation['warnings'] == 0
assert validation['preserved_prior_vox'] == 4970
signature = digest(HERE / 'qa/probe.gd')
for row in manifest['models']:
    result = imports[row['file']]
    assert digest(ROOT / row['file']) == row['sha256'] == result['sha256'], row['file']
    assert result['render_signature'] == signature
    assert result['whole_import'] == 'pass' and result['dimensions_match'] and result['grounded']
    assert result['voxels'] == row['voxels']
assert not (HERE / 'qa/render-errors.log').read_text().strip()
images = list(HERE.glob('*.png'))
for family in manifest['families']:
    directory = ROOT / 'output' / Path(family['source']).stem / 'bridges'
    images.extend(directory.glob(family['name'] + '_*.png'))
    images.extend((directory / 'previews').glob(family['name'] + '*.png'))
record = {
    'date': '2026-11-03',
    'families': len(manifest['families']),
    'files': len(manifest['models']),
    'review': 'Reviewed source crops, seven-style sheets, Base/Cartoon cardinal and underside views, and bank-placement diagnostics. Final overview and changed stone paving and bank anchors rechecked after refinement.',
    'refinements': [
        'Rounded, quieter cobblestone paint on poke_d road surfaces.',
        '24-voxel bank margins on poke_p spans seat all three posts; clear spans remain 96 and 80 voxels.'
    ],
    'limits': 'Hidden structure and clipped poke_h endpoint are documented reconstructions. Current VCOM Mesh importer tested in isolated project; combat navigation, destruction, cover and live-map integration not tested.',
    'models': {r['file']: r['sha256'] for r in manifest['models']},
    'preview_sha256': {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(set(images))},
    'validation_sha256': digest(HERE / 'validation-summary.json'),
    'godot_validation_sha256': digest(HERE / 'godot-validation.json'),
    'preserved_prior_vox': 4970,
}
(HERE / 'visual-review.json').write_text(json.dumps(record, indent=2) + '\n', encoding='utf-8')
print('Final review recorded: 119 matching model/import hashes; 4970 prior VOX preserved.')
