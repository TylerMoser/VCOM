"""Original potion items, no image source. Refuses to replace hand-edited exports."""
from pathlib import Path
import struct, json, hashlib, shutil, sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEST = ROOT.parent / 'VoxelXCOM/MagicaVoxel/Items/Bottles'
COLORS = {'Red': (224,42,64), 'Blue': (42,92,230), 'Pink': (248,109,181),
          'Cyan': (34,218,229), 'Purple': (153,65,219), 'Green': (66,197,73), 'Yellow': (247,211,44)}
# radius at each glass layer; final layer is a cork stopper above the rim.
SIZES = {'Small': (3,[1,1.45,1.45,1],1),
         'Medium': (5,[1.5,2.3,2.3,2.3,1.45,1.45],2),
         'Large': (7,[2.4,3.2,3.2,3.2,3.2,3.2,2.4,1.45,1.45],4)}
def i(*values): return struct.pack('<'+'i'*len(values),*values)
def s(value):
    b=value.encode(); return i(len(b))+b
def d(values): return i(len(values))+b''.join(s(k)+s(str(v)) for k,v in values.items())
def chunk(name,body=b'',children=b''): return name.encode()+i(len(body),len(children))+body+children
def digest(data): return hashlib.sha256(data).hexdigest()
def geometry(size):
    n,radii,fill=SIZES[size]; c=n//2; v={}; inside=set()
    for z,r in enumerate(radii):
        for x in range(n):
            for y in range(n):
                distance=((x-c)**2+(y-c)**2)**.5
                if distance > r: continue
                if z>0 and distance<=max(0,r-1): inside.add((x,y,z))
                else: v[x,y,z]=1
    # The narrow mouth remains hollow under a removable, one-voxel cork.
    v[c,c,len(radii)-1]=2
    inside.discard((c,c,len(radii)-1))
    v[c,c,len(radii)]=2
    return (n,n,len(radii)+1),v,inside,{p for p in inside if p[2]<=fill}
def encode(canvas,v,color,mode):
    palette=[(210,237,242,255),(167,112,65,255),(*color,255)]+[(0,0,0,255)]*253
    mats={1:{'_type':'_glass','_trans':'.85','_rough':'.08','_ior':'.5','_ri':'1.5','_d':'.05'},
          2:{'_type':'_diffuse','_rough':'.85'}}
    if mode!='Empty':
        mats[3]=({'_type':'_glass','_trans':'.5','_rough':'.1','_ior':'.33','_ri':'1.33','_d':'.15'}
                 if mode=='Translucent' else {'_type':'_diffuse','_rough':'.2'})
    body=chunk('SIZE',i(*canvas))+chunk('XYZI',i(len(v))+b''.join(bytes((*p,k)) for p,k in sorted(v.items())))
    body+=chunk('nTRN',i(0)+d({})+i(1,-1,-1,1)+d({}))
    body+=chunk('nGRP',i(1)+d({})+i(1,2))
    body+=chunk('nTRN',i(2)+d({'_name':'Potion bottle'})+i(3,-1,0,1)+d({'_t':f'0 0 {canvas[2]//2}'}))
    body+=chunk('nSHP',i(3)+d({})+i(1,0)+d({}))
    body+=chunk('LAYR',i(0)+d({'_name':'Bottle'})+i(-1))
    body+=chunk('RGBA',b''.join(bytes(c) for c in palette))
    body+=b''.join(chunk('MATL',i(k)+d(m)) for k,m in mats.items())
    return b'VOX '+i(200)+chunk('MAIN',children=body)
def main():
    DEST.mkdir(parents=True,exist_ok=True)
    old=json.loads((HERE/'manifest.json').read_text()) if (HERE/'manifest.json').exists() else []
    owned={r['name']:r['sha256'] for r in old}; rows=[]; pending=[]
    for size in SIZES:
        canvas,shell,inside,liquid=geometry(size)
        for name,color,mode in [('Empty',(0,0,0),'Empty')]+[(c,rgb,m) for c,rgb in COLORS.items() for m in ['Translucent','Opaque']]:
            v=dict(shell)
            if mode!='Empty': v.update({p:3 for p in liquid})
            filename=f'PotionBottle_{size}_{name}'+('' if mode=='Empty' else '_'+mode)+'.vox'
            data=encode(canvas,v,color,mode); path=DEST/filename
            if path.exists() and digest(path.read_bytes()) not in [owned.get(filename),digest(data)]:
                raise RuntimeError('Preserving modified/unowned file: '+str(path))
            pending.append((path,data))
            rows.append(dict(name=filename,path=str(path),size=size,canvas=canvas,mode=mode,color=name,
                sha256=digest(data),voxels=len(v),glass_voxels=sum(k==1 for k in v.values()),
                liquid_voxels=len(liquid) if mode!='Empty' else 0,air_voxels=len(inside)-(len(liquid) if mode!='Empty' else 0)))
    for path,data in pending: path.write_bytes(data)
    (HERE/'manifest.json').write_text(json.dumps(rows,indent=2))
    print(f'Wrote {len(rows)} complete bottles to {DEST}')
if __name__=='__main__': main()
