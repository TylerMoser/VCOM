from voxlib import *
import shutil
import wearables
qa=HERE/'qa';qa.mkdir(exist_ok=True)
source=GAME/'vcom/addons/MagicaVoxel_Importer_with_Extensions'
shutil.copytree(source,qa/'addons/MagicaVoxel_Importer_with_Extensions',dirs_exist_ok=True)
(qa/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Item collection QA"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
(HERE/'importer-provenance.json').write_text(json.dumps({str(p.relative_to(source)):sha(p.read_bytes()) for p in source.rglob('*') if p.is_file()},indent=2))
rows=json.loads((HERE/'manifest.json').read_text());preview_rows=[]
composites=qa/'composites';composites.mkdir(exist_ok=True)
for index,row in enumerate(rows):
 row=dict(row);row['preview_id']=f'{index:04d}';row['render_path']=row['path']
 size,v,pal,mats=read(row['path']);row['glass_voxels']=sum(mats.get(c,{}).get('_type')=='_glass' for c in v.values())
 if row['form']=='Fitted':
  # Mannequin voxels in a neutral palette entry, leaving every gear color/material untouched.
  free=next(k for k in range(1,255) if k not in set(v.values()))
  pal[free-1]=(105,115,125,255);mats[free]={'_type':'_diffuse'}
  combined={p:free for p in wearables.BODY};combined.update(v)
  path=composites/(row['preview_id']+'.vox');path.write_bytes(writebytes(size,combined,pal,mats))
  row['render_path']=str(path);row['composite_voxels']=len(combined)
 preview_rows.append(row)
(HERE/'render-list.json').write_text(json.dumps(preview_rows,indent=2))
print('Prepared',len(preview_rows),'renders;',len(list(composites.glob('*.vox'))),'mannequin composites')
