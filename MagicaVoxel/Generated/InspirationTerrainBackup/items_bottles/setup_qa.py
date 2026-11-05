from pathlib import Path
import shutil,json,hashlib
here=Path(__file__).resolve().parent
source=here.parents[1].parent/'VoxelXCOM/vcom/addons/MagicaVoxel_Importer_with_Extensions'
dest=here/'qa'; dest.mkdir(exist_ok=True)
shutil.copytree(source,dest/'addons/MagicaVoxel_Importer_with_Extensions',dirs_exist_ok=True)
(dest/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Potion bottle QA"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
(here/'importer-provenance.json').write_text(json.dumps({str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source.rglob('*') if p.is_file()},indent=2))
