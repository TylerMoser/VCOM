"""Refresh current runtime sources in the isolated QA project; never writes to VCOM."""
from voxlib import *
import shutil
source=GAME/'vcom';dest=HERE/'qa_runtime'
assert dest.resolve()!=source.resolve()
shutil.copytree(source,dest,ignore=shutil.ignore_patterns('.godot','.git'),dirs_exist_ok=True)
(HERE/'runtime-provenance.json').write_text(json.dumps({str(p.relative_to(source)):sha(p.read_bytes()) for p in source.rglob('*') if p.is_file() and '.godot' not in p.parts},indent=2))
print('Runtime QA source refreshed:',dest)
