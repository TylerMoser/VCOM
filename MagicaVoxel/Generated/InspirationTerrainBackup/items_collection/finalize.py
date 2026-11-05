"""Final hashes bind model delivery, all automated evidence and source provenance."""
from voxlib import *
import catalog
rows=json.loads((HERE/'manifest.json').read_text());wanted={r['file']:r['sha256'] for r in rows}
old=json.loads((HERE/'preserved-originals.json').read_text())
for rel,h in {**old,**wanted}.items():assert sha((DEST/rel).read_bytes())==h,rel
assert len(list(DEST.rglob('*.vox')))==len(wanted)+len(old)==3726
imports=json.loads((HERE/'import-validation.json').read_text())
runtime=json.loads((HERE/'runtime-validation.json').read_text())
rig=json.loads((HERE/'rig-validation.json').read_text())
validation=json.loads((HERE/'validation.json').read_text())
audit=json.loads((HERE/'structural-audit.json').read_text())
assert wanted=={k:r['sha256'] for k,r in imports.items()}
assert wanted=={r['file']:r['sha256'] for r in runtime}
assert wanted=={r['file']:r['sha256'] for r in validation['results']}
assert all(wanted[r['file']]==r['sha256'] for r in rig) and len(rig)==456
assert sum(r['rendered_poses'] for r in rig)==228
assert {r['animations'] for r in rig if r['rendered_poses']}=={56}
assert len(audit)==3726 and all(not r.get('warnings') and not r.get('error') for r in audit)
assert {str(Path(r['path']).resolve()):r['sha256'] for r in audit}=={str((DEST/k).resolve()):h for k,h in {**old,**wanted}.items()}
for log in ('render-errors.log','runtime-errors.log'):
 text=(HERE/log).read_text(errors='replace');assert 'SCRIPT ERROR' not in text and '\nERROR:' not in text,log
for r in json.loads((HERE/'render-list.json').read_text()):
 assert (HERE/'previews'/(r['preview_id']+'.png')).exists()
 if r['style']=='Base':assert (HERE/'previews'/(r['preview_id']+'_back.png')).exists()
for spec in catalog.CATALOG:assert (HERE/'sheets'/spec['category']/(spec['name']+'.png')).exists()
for spec in catalog.CATALOG:
 if spec['family'] in catalog.WEARABLE:assert (HERE/'pose_sheets'/(spec['category']+'_'+spec['name']+'.png')).exists()
source={}
for p in (GAME/'vcom').rglob('*'):
 if p.is_file() and '.godot' not in p.parts and p.suffix in ('.gd','.gdshader','.glsl'):
  rel=p.relative_to(GAME/'vcom');copied=HERE/'qa_runtime'/rel
  assert copied.exists() and sha(copied.read_bytes())==sha(p.read_bytes()),'Runtime sources changed: '+str(rel)
  source[str(rel)]=sha(p.read_bytes())
(HERE/'runtime-provenance.json').write_text(json.dumps(source,indent=2))
reference={str(p.resolve()):sha(p.read_bytes()) for p in [GAME/'Brainstorming/Items.txt',GAME/'MagicaVoxel/Characters/Character_Bigger.vox',ROOT/'knowledge/palettes/crate-palette.json',GAME/'MagicaVoxel/Blocks/BrightCrate1.vox']}
(HERE/'source-provenance.json').write_text(json.dumps(reference,indent=2))
summary=dict(new_files=3639,preserved_originals=87,total_files=3726,expanded_types=387,designs_per_type=4,
 standalone_files=3096,fitted_files=456,existing_palette_counterparts=87,palette_sha256=PIN['palette_sha256'],
 imported_and_runtime_checked=3639,rig_checked=456,animated_designs=228,animations_per_design=56,
 sampled_poses=['stand_unarmed','run_unarmed','crouch_unarmed','strike_sword'],
 source_scripts_unchanged=len(source),manual_visual_review='Representative comparison and pose sheets; all files rendered and automatically checked',
 manifest_sha256=sha((HERE/'manifest.json').read_bytes()),layouts_sha256=sha((HERE/'layouts.json').read_bytes()),
 outputs='VoxelXCOM/MagicaVoxel/Items',gameplay_integration=False)
(HERE/'final-verification.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
