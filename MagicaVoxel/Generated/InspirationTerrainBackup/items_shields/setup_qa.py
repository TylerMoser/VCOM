from pathlib import Path
import shutil,json,hashlib
here=Path(__file__).resolve().parent
source=here.parents[1].parent/'VoxelXCOM/vcom/addons/MagicaVoxel_Importer_with_Extensions'
dest=here/'qa';dest.mkdir(exist_ok=True)
shutil.copytree(source,dest/'addons/MagicaVoxel_Importer_with_Extensions',dirs_exist_ok=True)
(dest/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Shield QA"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
(here/'importer-provenance.json').write_text(json.dumps({str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()},indent=2))
# Adapt the proven standalone import/render probe. Camera fits each shield separately.
probe=(here.parent/'items_bottles/qa/probe.gd').read_text()
probe=probe.replace('assert(transparent>=1 and opaque>=1)','assert(opaque>=1 and (transparent>=1 if row.glass_voxels>0 else transparent==0))')
probe=probe.replace('var target=bounds.get_center();camera.position=target+Vector3(1,0.8,1.5);camera.look_at(target)',
 'camera.size=max(bounds.size.y*1.35,bounds.size.x*1.5)\n  var target=bounds.get_center();camera.position=target+Vector3(.55,.35,2.0);camera.look_at(target)')
probe=probe.replace('if row.mode=="Empty":','if true:').replace('Vector3(-1,-.8,-1.5)','Vector3(-.8,.4,-2)').replace('_bottom.png','_back.png').replace('BOTTLE_IMPORT_RENDER_PASS','SHIELD_IMPORT_RENDER_PASS')
(dest/'probe.gd').write_text(probe)
