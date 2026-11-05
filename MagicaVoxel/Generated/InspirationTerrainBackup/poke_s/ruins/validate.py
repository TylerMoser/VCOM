"""Independent disk checks; never rewrites VOX files."""
from pathlib import Path
import json,sys,hashlib
from voxlib import read,components
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from inspect_vox import inspect
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((HERE/'manifest.json').read_text());audits=[];checks=[]
for f in m['families']:
 rows=[r for r in m['models'] if r['family']==f['name']]
 assert len(rows)==7
 geometry={};groups={}
 for style in ('Base','Cartoon'):
  r=next(r for r in rows if r['style']==style);_,v,_=read(ROOT/r['file']);geometry[style]=set(v);groups[style]={p:m['semantic_groups'] for p in []}
  assert len(components(v))==1
  if f['name'].endswith('TempleCore'):
   assert (96,120,47) in v and (96,120,48) not in v
  if f['name'].endswith('GardenRotunda') or f['name'].endswith('RecessedRotunda'):
   assert (31,31,39) in v and (31,31,40) not in v
  if f['name'].endswith('SteppedSanctuary'):
   heights=[max(z for x,y,z in v if x==40 and y==yy) for yy in (2,22,42,50,70,86)]
   assert heights==sorted(heights) and len(set(heights))==6,heights
  groups[style]={p:1 if c<=4 else 5 if c<=7 else 8 for p,c in v.items()}
 assert geometry['Base']!=geometry['Cartoon'],f['name']
 for r in rows:
  path=ROOT/r['file'];assert sha(path)==r['sha256']
  a=inspect(path);assert not a['warnings'] and len(a['models'])==1
  assert a['models'][0]['bounds'][0][2]==0
  assert a['nodes'][2]['frames'][0]['_t']==f"0 0 {r['canvas'][2]//2}"
  size,v,pal=read(path);authority='Cartoon' if 'Cartoon' in r['style'] else 'Base'
  assert set(v)==geometry[authority] and len(v)==r['voxels']
  assert 0 not in v.values() and 255 not in v.values()
  if 'CratePalette' in r['style']:assert a['palette_sha256']==m['palette_sha256']
  if 'TwoColor' in r['style']:
   used={}
   for p,c in v.items():used.setdefault(groups[authority][p],set()).add(c)
   assert all(len(colors)==1 for colors in used.values())
   assert len(set(v.values()))==len(used)
  audits.append(a)
 checks.append({'family':f['name'],'variants':7,'connected':True,'recolors_exact':True,'cartoon_geometry_distinct':True,'flat_semantic_groups':True})
 print('Validated',f['name'],flush=True)
before=json.loads((HERE/'preserved-hashes.json').read_text());assert all(sha(ROOT/p)==h for p,h in before.items())
(HERE/'structural-audit.json').write_text(json.dumps(audits,indent=2))
(HERE/'validation-summary.json').write_text(json.dumps({'models':len(audits),'errors':0,'warnings':0,'preserved_existing_vox':len(before),'families':checks},indent=2))
print('PASS',len(audits))
