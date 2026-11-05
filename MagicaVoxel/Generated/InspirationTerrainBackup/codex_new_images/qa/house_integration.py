"""Validate complete cottage via existing building harness in an isolated VCOM copy.
QA-only cells are never exported as authoring deliverables.
"""
from pathlib import Path
import sys,json,shutil,importlib.util,types,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];COL=HERE.parent
sys.path.insert(0,str(COL))
import voxlib as newvox
sys.path.insert(0,str(ROOT/'output/poke_c/buildings'))
sys.path.insert(0,str(ROOT/'output/poke_c/buildings/qa'))
# Load the established harness without executing its generation/main routines.
import integration as harness
import cut_pieces as cutter
GAME=HERE/'vcom_scratch';real=ROOT.parent/'VoxelXCOM/vcom'
assert GAME.resolve()!=real.resolve()
if not (GAME/'project.godot').exists():
 shutil.copytree(real,GAME,ignore=shutil.ignore_patterns('.godot','.git'),dirs_exist_ok=True)
(GAME/'_probe').mkdir(exist_ok=True)
shutil.copy(ROOT/'output/poke_c/buildings/qa/godot/building_probe.gd',GAME/'_probe/building_probe.gd')
m=json.loads((COL/'manifest.json').read_text());jobs=[]
for j,row in enumerate(r for r in m['models'] if 'MossRoofCottage' in r['family']):
 size,vox,pal,n=newvox.read(ROOT/row['file']);glass=set(row['glass_indices'])
 labels={c:(pal[c-1][:3],'glass' if c in glass else 'body') for c in set(vox.values())}
 adapter=types.SimpleNamespace(LABELS=labels,palette_of=lambda style,pal=pal,glass=glass:(pal,glass),paint=lambda style,label:label)
 cutter.palettes=adapter;harness.palettes=adapter
 def writer(path,size,v,palette,glass,name=None):
  newvox.write(path,size,v,palette,{c:{'_type':'_glass','_trans':'.7'} for c in glass})
 cutter.write=writer
 footprint={(i,j) for i in range(8) for j in range(6)};roles={}
 for x,y,z in vox:
  role='roof' if z>=64 else 'mid' if z<16 else 'edge'
  if z>=16 and z<64:
   role='ex' if x<=11 or x>=133 else 'ey' if y<=11 or y>=101 else 'mid'
  roles[x,y,z]=role
 model=types.SimpleNamespace(name='New1_Codex_MossRoofCottage',v=vox,role=roles,footprint=footprint,doors={('ey',i,0,k) for i in [3,4] for k in [1,2]})
 short='C'+str(j);lay=cutter.cut(model,row['style'],GAME/'Blocks/CodexQA'/short,cx=0,r=0,family=short,res_prefix='Blocks/CodexQA')
 expect=harness.expect_house(model,lay)
 # The exterior is tested at the grid contract, including window vaults and sealed doors.
 jobs.append(dict(name=row['style'],source_file=row['file'],source_sha256=row['sha256'],kind='Cottage',style=row['style'],house=True,layouts=[lay],expect=expect,views=harness.HOUSE_VIEWS,exact=harness.exact(harness.placed_voxels(model,row['style'],0,0))))
out=HERE/'house-results';out.mkdir(exist_ok=True)
(GAME/'_probe/jobs.json').write_text(json.dumps(dict(jobs=jobs,out=out.as_posix(),render=False)))
exe='C:/Program Files/Godot/Godot_v4.7-stable_win64_console.exe'
for label,args in [('import',['--headless','--path',str(GAME),'--import']),('probe',['--headless','--path',str(GAME),'--script','res://_probe/building_probe.gd','--',str(GAME/'_probe/jobs.json')])]:
 with (HERE/f'house-{label}.log').open('w') as log:
  proc=subprocess.run([exe]+args,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
 print(label,proc.returncode,flush=True)
report=json.loads((out/'report.json').read_text());bad=[(n,k) for n,r in report.items() for k,v in r['checks'].items() if not v]
print('HOUSE INTEGRATION',len(report),'variants; failed:',bad,flush=True)
assert not bad
(HERE/'house-validation.json').write_text(json.dumps(dict(models={j['source_file']:j['source_sha256'] for j in jobs},checks=report,failed=bad),indent=2))
