"""Checks serialized models, including sealed cavities and material-only variants."""
import json,struct,sys,hashlib
from pathlib import Path
from collections import deque
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parents[1]/'tools'))
from inspect_vox import inspect
rows=json.loads((HERE/'manifest.json').read_text()); saved={}; report=[]
steps=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)]
def neighbors(p): return [tuple(p[a]+s[a] for a in range(3)) for s in steps]
for row in rows:
    p=Path(row['path']); b=p.read_bytes(); audit=inspect(p)
    assert not audit['warnings'] and len(audit['models'])==1
    assert hashlib.sha256(b).hexdigest()==row['sha256']
    offset=20; v={}
    while offset<len(b):
        cid,n,m=struct.unpack_from('<4sii',b,offset)
        if cid==b'XYZI': v={tuple(q[:3]):q[3] for q in struct.iter_unpack('BBBB',b[offset+16:offset+12+n])}
        offset+=12+n+m
    assert len(v)==row['voxels'] and 255 not in v.values()
    assert audit['models'][0]['size']==row['canvas']
    c=row['canvas'][0]//2
    assert {(2*c-x,y,z):k for (x,y,z),k in v.items()}==v
    assert {(y,x,z):k for (x,y,z),k in v.items()}==v
    seen={next(iter(v))}; q=deque(seen)
    while q:
        for p in neighbors(q.popleft()):
            if p in v and p not in seen: seen.add(p);q.append(p)
    assert len(seen)==len(v),'Disconnected geometry'
    # Flood exterior air with liquid removed: sealed shell must protect fill.
    shell={p for p,k in v.items() if k!=3}; seen={(-1,-1,-1)};q=deque(seen)
    while q:
        for p in neighbors(q.popleft()):
            if all(-1<=p[a]<=row['canvas'][a] for a in range(3)) and p not in shell and p not in seen:
                seen.add(p);q.append(p)
    assert not any(p in seen for p,k in v.items() if k==3),'Liquid leaks outside'
    assert audit['materials'][1]['_type']=='_glass' and float(audit['materials'][1]['_trans'])==.85
    if row['mode']=='Translucent': assert audit['materials'][3]['_type']=='_glass' and float(audit['materials'][3]['_trans'])==.5
    if row['mode']=='Opaque': assert audit['materials'][3]['_type']=='_diffuse' and '_trans' not in audit['materials'][3]
    saved[row['name']]=v
    report.append({'name':row['name'],'structure':'pass','connected':'pass','sealed_liquid':'pass','materials':'pass','symmetry':'pass'})
for row in rows:
    v=saved[row['name']]; empty=saved[f"PotionBottle_{row['size']}_Empty.vox"]
    assert {p:k for p,k in v.items() if k!=3}==empty
    if row['mode']=='Translucent': assert v==saved[row['name'].replace('Translucent','Opaque')]
assert len(rows)==45
(HERE/'validation.json').write_text(json.dumps(report,indent=2))
print('PASS: 45 files; materials, shells, symmetry, connectivity, sealed fill, exact variant geometry')
