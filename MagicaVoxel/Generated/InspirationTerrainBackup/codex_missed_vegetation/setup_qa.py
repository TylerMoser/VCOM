from pathlib import Path
import shutil,json,hashlib
here=Path(__file__).resolve().parent;root=here.parents[1];dest=here/'qa/game';dest.mkdir(parents=True,exist_ok=True)
src=root.parent/'VoxelXCOM/vcom/addons/MagicaVoxel_Importer_with_Extensions'
shutil.copytree(src,dest/'addons/MagicaVoxel_Importer_with_Extensions',dirs_exist_ok=True)
(dest/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Complete bridges QA"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
(dest.parent/'source-provenance.json').write_text(json.dumps({str(p.relative_to(src)):hashlib.sha256(p.read_bytes()).hexdigest() for p in src.rglob('*') if p.is_file()},indent=2))
