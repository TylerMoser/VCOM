from voxlib import *
from collections import defaultdict,Counter
from PIL import Image,ImageDraw,ImageFont
import catalog,shutil
rows=json.loads((HERE/'render-list.json').read_text());layouts=json.loads((HERE/'layouts.json').read_text())
bycat=defaultdict(list)
for r in rows:bycat[r['category']].append(r)
master=['# Item model catalog — 2026-11-05','',
 'Fantasy / World War I-era equipment. **3,639 new complete VOX files**, plus **87 preserved originals**: **3,726 files** in Items.',
 '', 'The expanded catalog contains **387 item types**, each with four geometrically distinct designs and four exact-geometry `_CratePalette` counterparts. The 57 wearable types also have fitted copies: **228 wearable designs / 456 fitted files**. Existing bottles, shields and original equipment each have a new palette counterpart.',
 '', '| Category | Expanded item types | New files | Browse |','| --- | ---: | ---: | --- |']
for cat,rs in bycat.items():
 types=[s['name'] for s in catalog.CATALOG if s['category']==cat]
 master.append(f'| {cat} | {len(types) if types else "Existing collection"} | {len(rs)} | [Catalog]({cat}/Catalog.md) |')
 lines=[f'# {cat}','',f'{len(rs)} new files. Original files are preserved.','',
  'All Base designs have a geometry-identical `_CratePalette` counterpart. Models are complete items, not individual voxel-cell packages.','']
 pages=sorted((DEST/cat).glob('Preview_*.png'))
 if pages:lines.append(' · '.join(f'[Overview {j+1}]({p.name})' for j,p in enumerate(pages)));lines.append('')
 lines+=['| Item | Base designs | Crate-palette designs | Comparison |','| --- | --- | --- | --- |']
 for item in types:
  group=[r for r in rs if r['item']==item and r['form']=='Standalone']
  base=[r for r in group if r['style']=='Base'];cp=[r for r in group if r['style']=='CratePalette']
  links=lambda a:' · '.join(f"[{r['design']}]({Path(r['path']).name})" for r in a)
  preview=(HERE/'sheets'/cat/(item+'.png')).as_posix()
  lines.append(f'| {item} | {links(base)} | {links(cp)} | [Front / palette / rear]({preview}) |')
 legacy=[r for r in rs if r['form']=='PreservedCounterpart']
 if legacy:
  lines+=['','## Existing models — new palette counterparts','']
  for r in legacy:lines.append(f"- [{Path(r['path']).name}]({Path(r['path']).name}) — source [{r['source']}]({(DEST/r['source']).as_posix()})")
 fits=[r for r in rs if r['form']=='Fitted']
 if fits:
  lines+=['','## Fitted equipment','', 'The [Fitted](Fitted/) folder contains equipment-only models at Character_Bigger’s original coordinates, both palettes. [Fitting instructions](Fitted/FITTING.md). No body voxels are included in these delivered overlays; the preview mannequin is QA only.','']
  dest=DEST/cat/'Fitted';local={Path(r['path']).name:layouts[r['file']] for r in fits}
  (dest/'layouts.json').write_text(json.dumps(local,indent=2))
  (dest/'FITTING.md').write_text('''# Fitted equipment

These are complete equipment overlays at Character_Bigger's original T-pose coordinates (32×32×32, or 32×32×40 for tall helmets). X across, negative Y front, Z up. The original body remains at its existing coordinates. Overlay the gear on the body, letting gear colors replace exposed body voxels where they overlap; do not center or ground the gear independently. Paired boots are deliberately two components in one file.

`layouts.json` gives exact equipment bone regions, one contiguous X run per row. Put these regions BEFORE the base CHARACTER_BIGGER regions. Arm-top armor at z=19 is assigned to the upper arms, not the neck. Every gear voxel was checked against its assigned bone and every fitted file made a skinned mesh in the current VCOM rig.

Current VoxelRig centers each model on its occupied bounding box. On the combined body-and-gear model, compute `cx=(minX+maxX+1)/2`, `cy=(minY+maxY+1)/2`. Add `(16.5-cx, 0, cy-16.0)` to every original CHARACTER_BIGGER joint (Godot axes), preserving the original scale .063. The test harness uses this existing supported layout approach; no game source changes were made. Do not use the equipment-only bounds to calculate this shift. The alternative requires an explicitly supported fixed-body center in a future rig version.

Standalone counterparts are the same voxels translated into a tight grounded canvas; their `original_offset` is recorded in the master manifest. The fitted version is the geometry authority for placement, and exact translation equality was tested.

All 228 distinct wearable designs were baked in the isolated QA process with 56 animations and captured standing, running, crouching, and striking. Palette twins share geometry and bone assignments. These captures and geometric checks are not an exhaustive collision test across all character species, combined equipment, weapons or animation frames. Add an actual equipment resource, attachment/dressing logic and stats separately when integrating. The original VCOM project was not changed.
''')
  for r in fits:
   if r['style']=='Base':
    lines.append(f"- [{r['item']} / {r['design']} — fitted](Fitted/{Path(r['path']).name}) · [palette](Fitted/{Path(r['path']).stem}_CratePalette.vox)")
 (DEST/cat/'Catalog.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
master+=['','## Conventions and limitations','',
 'Scale 0.0625 for source props; Z up. Standalone files are tightly bounded and grounded. Weapons and gear retain visible functional ends; attachment transforms are a separate integration step. Fitted equipment uses the character’s authored coordinate frame rather than a tight canvas.',
 '', 'CratePalette uses the exact original BrightCrate1 palette, including unused entries, with material-aware nearest-color remapping. Index 255 remains reserved for blood. Glass and emission are preserved on separate material indices. The palette source is the approved pinned snapshot; no new colors are introduced into that variation.',
 '', 'Effects, buffs, healing, ammunition types, armor protection and magic are visual item concepts. No stats, inventory entries, combat behavior or equipment system changes are included. “Chainmail / Chain Mail” is one type and “Shortword” is interpreted as Shortsword. All named entries of Items.txt are covered; open categories are explicitly expanded in their catalogs.',
 '', 'The current greedy importer merges touching glass materials into one surface: translucent liquids can appear faint and lose their internal interfaces. Independent VOX glass/liquid settings are retained. The separate runtime VoxelModel checks also passed, but this is not a claim of physically correct glass/liquid refraction.',
 '', f'[Authoring sources, evidence and reproduction]({(HERE/"README.md").as_posix()})',
 '']
(DEST/'CATALOG.md').write_text('\n'.join(master),encoding='utf-8')
(HERE/'CATALOG.md').write_text('# Catalog\n\n[Open the delivered category index]('+ (DEST/'CATALOG.md').as_posix()+')\n')
# Per-type animation comparison pages, all four designs and four sampled poses.
folder=HERE/'pose_sheets';folder.mkdir(exist_ok=True)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
for spec in [s for s in catalog.CATALOG if s['family'] in catalog.WEARABLE]:
 cat,item=spec['category'],spec['name'];sheet=Image.new('RGB',(1024,1400),'#192832');dr=ImageDraw.Draw(sheet)
 dr.text((12,12),cat+' / '+item+' — fitted, current VCOM rig',font=font,fill='white')
 for y,label in enumerate(catalog.VARIANTS):
  for x,pose in enumerate(['stand_unarmed','run_unarmed','crouch_unarmed','strike_sword']):
   path=HERE/'rig_previews'/f'{cat}_{item}_{label}_{pose}.png'
   if path.exists():sheet.paste(Image.open(path),(256*x,50+335*y))
   dr.text((256*x+5,365+335*y),label+' / '+pose.split('_')[0],font=font,fill='white')
 sheet.save(folder/f'{cat}_{item}.png')
print('Wrote delivered category catalogs, fitted metadata, and 57 pose comparison sheets')
