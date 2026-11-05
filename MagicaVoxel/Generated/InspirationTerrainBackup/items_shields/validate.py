import json,struct,sys,hashlib
from pathlib import Path
from collections import deque,Counter
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'tools'))
from inspect_vox import inspect
rows=json.loads((HERE/'manifest.json').read_text());report=[];geometries={}
for row in rows:
 p=Path(row['path']);b=p.read_bytes();a=inspect(p);assert not a['warnings']
 assert hashlib.sha256(b).hexdigest()==row['sha256']
 offset=20;v={}
 while offset<len(b):
  cid,n,m=struct.unpack_from('<4sii',b,offset)
  if cid==b'XYZI':v={tuple(q[:3]):q[3] for q in struct.iter_unpack('BBBB',b[offset+16:offset+12+n])}
  offset+=12+n+m
 assert len(v)==row['voxels'] and 255 not in v.values()
 assert a['models'][0]['size']==row['canvas']
 lo=[min(p[i] for p in v) for i in range(3)];hi=[max(p[i] for p in v) for i in range(3)]
 assert lo==[0,0,0] and [hi[i]+1 for i in range(3)]==row['canvas']
 seen={next(iter(v))};q=deque(seen)
 while q:
  p=q.popleft()
  for delta in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
   n=tuple(p[i]+delta[i] for i in range(3))
   if n in v and n not in seen:seen.add(n);q.append(n)
 assert len(seen)==len(v),row['name']+' disconnected'
 assert 6 in v.values(),'Missing grip'
 # Open space under the middle of the rear grip must remain available for the hand.
 for (x,y,z),k in v.items():
  if k==6 and y==hi[1] and z==row['canvas'][2]//2:
   assert (x,y-1,z) not in v
 assert sum(k==7 for k in v.values())==row['glass_voxels']
 if row['glass_voxels']:assert a['materials'][7]['_type']=='_glass'
 geometries.setdefault(row['kind'],set()).add(frozenset(v))
 report.append({'name':row['name'],'sha256':row['sha256'],'connected':True,'grip_clearance':True,'dimensions':True,'glass_voxels':row['glass_voxels']})
assert Counter(r['kind'] for r in rows)==dict.fromkeys(['Buckler','Wooden','Hide','Steel','Tower','Fortress','Round','Ballistic'],4)
assert all(len(g)==4 for g in geometries.values()),'Designs must differ geometrically'
(HERE/'validation.json').write_text(json.dumps(report,indent=2))
print('PASS: 32 shields, all eight types, four unique geometries each; connected; grip clearance; materials')
