"""Deterministic 16-cubed source-inspired ground tiles, seven established styles.
No source-image extrusion: surfaces are reconstructed as periodic material motifs.
"""
from pathlib import Path
from collections import Counter
import json,hashlib,math
from PIL import Image,ImageDraw
from voxlib import read,write,components
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
CAT=json.loads((HERE/'catalogue.json').read_text());BY={r['name']:r for r in CAT}
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
CRATE=json.loads((ROOT/'knowledge/palettes/crate-palette.json').read_text())
WATER={'calm','waves','ripples','caustic','dapple'}
PAVING={'herringbone','brick','flagstone','cobble','broken'}
EARTH={'dirt','sand','soil','mud','furrows','cracked','gravel','rock','slate'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def noise(x,y,s=0):
 n=((x%16)*374761393+(y%16)*668265263+s*1442695041)&0xffffffff
 n=((n^(n>>13))*1274126177)&0xffffffff
 return (n^(n>>16))%101

def palette_source(r):
 im=Image.open(ROOT/r['source']).convert('RGB').crop(r['crop']);pix=list(im.getdata());k=r['kind']
 # Reject overlay colors by the material's hue; keep original RGB values.
 def allowed(c):
  R,G,B=c
  if k in ['grass','broadgrass']:return G>R*.95 and G>B*1.12 and G>95
  if k in WATER:return B>R*1.05 and G>R*1.03
  if k in ['dirt','sand','soil','mud','furrows','cracked']:return R>=G*.99 and G>B*1.08 and R>60
  if k in PAVING or k in ['rock','slate']:return max(c)-min(c)<70 and min(c)>65
  if 'planks' in k:return R>=G*.99 and G>B*1.1
  return True
 clean=[c for c in pix if allowed(c)] or pix
 # Quantization removes JPEG chroma noise; the most frequent remaining tone is representative.
 q=Image.new('RGB',(len(clean),1));q.putdata(clean);q=q.quantize(colors=4).convert('RGB')
 base=Counter(q.getdata()).most_common(1)[0][0]
 if r['name']=='PokeR_Ground_GardenSoil':base=(151,128,101)
 if r['name']=='PokeI_Ground_FurrowedSoil':base=(131,105,81)
 if r['name']=='PokeD_Ground_GrayRock':base=(133,128,112)
 if r['name']=='PokeL_Ground_TerraceEarth':base=(176,119,74)
 if r['name']=='PokeT_Ground_CaveRock':base=(167,121,82)
 r['representative_rgb']=list(base)
 return base
COL={r['name']:palette_source(r) for r in CAT if r['role']=='surface'}
def shift(c,d):return tuple(max(0,min(255,v+d)) for v in c)

def surface(r,x,y,cartoon):
 """Return material group, tonal tier, top level; all patterns wrap at 16."""
 x%=16;y%=16
 k=r['kind'];seed=sum(map(ord,r['name']))%97
 xx,yy=x,y
 if cartoon and k not in ['planks','diagonalplanks','herringbone','brick','flagstone','furrows']:
  x=min(x,15-x);y=min(y,15-y)
 n=noise(x,y,seed);tone=0;h=13 if k in WATER else 15;group='surface'
 if k in ['grass','broadgrass']:
  # Sparse pixel tufts, broad graphic patches for Pixelwood.
  if k=='broadgrass':
   if cartoon:tone=-1 if (x-3)**2+(y-3)**2<=2 else 0
   else:tone=-1 if any(min(abs(x-a),16-abs(x-a))**2+min(abs(y-b),16-abs(y-b))**2<=rad for a,b,rad in [(3,5,7),(12,12,4)]) else 0
  elif cartoon:tone=1 if (x in [3,4] and y in [3,4]) else -1 if x==y and x in [2,5] else 0
  else:
   for a,b in [(2,3),(10,5),(6,12)]:
    dx=(x-a)%16;dy=(y-b)%16
    if (dx,dy) in [(0,0),(2,0),(1,1)]:tone=-1
    if (dx,dy)==(1,2):tone=1
 elif k in ['dirt','sand','soil']:
  tone=(-1 if n<7 else 1 if n>95 else 0) if not cartoon else (1 if x in [3,4] and y in [3,4] else 0)
 elif k=='furrows':
  h=14 if x%4==0 else 15;tone=-1 if x%4==0 else 1 if x%4==3 else 0
 elif k in ['rock','mud','gravel','cracked','slate']:
  u=(x+(y//4)*2)%8;v=y%8
  seam=(u==0 or (v==0 and u<6)) if cartoon else ((x+y//3)%8==0 or ((y+x//5)%8==0))
  if k=='slate':seam=(y%8==3 and x%16<12) or (x%8==4 and y%8 in [4,5]);h=14 if seam else 15;tone=-1 if seam else 0
  elif k=='cracked':h=14 if seam else 15;tone=-1 if seam else (1 if n>83 else 0)
  elif k=='mud':tone=-1 if (x//3+y//3)%4==0 else 1 if n>94 else 0
  elif k=='gravel':tone=-1 if noise(x//2,y//2,seed)<23 else 1 if noise(x//2,y//2,seed)>78 else 0
  else:tone=1 if (x//3+y//4)%3==0 else -1 if seam else 0
 elif k in WATER:
  if k=='calm':tone=1 if y%8==3 and x%8 in [2,3,4] else 0
  elif k=='ripples':tone=1 if ((y%8==2 and x%8 in [2,3]) or (y%8==6 and x%8 in [5,6,7])) else 0
  elif k=='waves':tone=1 if (y+(x//3)%3)%8==0 else -1 if (y+(x//3)%3)%8==1 else 0
  elif k=='caustic':tone=1 if ((x+y)%8==0 or (x-y)%8==0) else -1 if (x+y)%8==4 else 0
  else:
   value=math.sin(x*math.tau/16)+.65*math.cos(y*math.tau/16)+.4*math.sin((x+y)*math.tau/8)
   tone=1 if value>.9 else -1 if value<-.9 else 0
  if cartoon:tone=1 if (x in [2,3,4] and y==3) else 0
 elif k in ['planks','diagonalplanks']:
  u=(x+y)%16 if k=='diagonalplanks' else x
  seam=u%4==0;group='wood';h=14 if seam else 15;tone=-1 if seam else (1 if u%4==3 else 0)
  if not cartoon and y%8==2 and u%4==2:tone=-1
 elif k in PAVING:
  if k=='herringbone':
   # Diagonal staircase arrangement of perpendicular 2x1 bricks.
   u=(x+y)%16;v=(x-y)%16;i=u//4;j=v//4;d=(i-j)%4
   seam=(v%4==0 or u%8==0) if d in [0,1] else (u%4==0 or v%8==0)
   if cartoon:seam=(u%4==0 or v%8==0)
   tone=(i+j)%3-1
  elif k=='brick':
   seam=y%4==0 or (x+4*(y//4))%8==0;tone=(x//8+y//4)%3-1
  elif k=='flagstone':
   seam=x%8==0 or (y+(x//8)*4)%8==0 or (x%8==4 and y%8<4);tone=(x//4+y//4)%3-1
   if cartoon:seam=x%8==0 or y%8==0;tone=0
  elif k=='broken':
   seam=x%8==0 or y%8==0 or (x+y)%13==0;group='moss' if seam else 'surface';tone=0
   if cartoon:seam=x%8==0 or y%8==0;group='moss' if seam else 'surface'
  else:
   if cartoon:seam=x%8 in [0,7] or y%8 in [0,7];tone=0
   else:
    sites=[(2,2),(9,1),(14,5),(6,7),(1,11),(10,13),(15,14)]
    ds=sorted((min(abs(x-a),16-abs(x-a))**2+min(abs(y-b),16-abs(y-b))**2,i) for i,(a,b) in enumerate(sites));seam=ds[1][0]-ds[0][0]<4;tone=ds[0][1]%3-1
  if seam:h=14;group='moss' if k=='broken' else 'mortar';tone=0
  elif cartoon:tone=0 if k!='herringbone' else tone
 return group,tone,h

def mat_rgb(r,group,tone):
 c=COL[r['name']]
 if group=='substrate':c=(116,80,52) if r['kind'] in ['grass','broadgrass'] else shift(c,-24)
 elif group=='mortar':c=shift(c,-32)
 elif group=='moss':c=(114,151,66)
 return shift(c,(-15,0,13)[tone+1])

def contour_a(r,x,y,cartoon):
 # Endpoint at 8 is identical for every contour. Small waviness stays inside boundary.
 bend=0 if cartoon else [0,0,-1,-1,0,1,1,0,0,0,1,1,0,-1,-1,0][y]
 if r['contour']=='Edge':return x<8+bend
 # Outer corner: A occupies the upper-left quadrant; inner: A all but lower-right.
 if r['contour']=='OuterCorner':return x<8 and y<8
 return x<8 or y<8

def model(r,cartoon):
 vox={};refs={}
 for x in range(16):
  for y in range(16):
   chosen=r
   if r['role']=='transition':chosen=BY[r['materials'][0 if contour_a(r,x,y,cartoon) else 1]]
   group,tone,h=surface(chosen,x,y,cartoon)
   for z in range(h+1):
    # Closed filled blocks: no hollow undersides. Turf cap 3 voxels; other cap 2.
    g=group if z>=h-1 else ('surface' if chosen['kind'] in WATER else 'substrate')
    t=tone if z==h else 0
    if chosen['kind'] in ['grass','broadgrass'] and z==13:g='surface'
    # Exposed earth strata have no per-cell dark border.
    if g=='substrate' and not cartoon and z in [3,8]:t=-1
    label=(chosen['name'],g,t);vox[x,y,z]=label;refs[label]=mat_rgb(chosen,g,t)
   if r.get('curb'):
    a=contour_a(r,x,y,cartoon)
    adjacent=any(contour_a(r,nx,ny,cartoon)!=a for nx,ny in [(max(0,x-1),y),(min(15,x+1),y),(x,max(0,y-1)),(x,min(15,y+1))])
    if adjacent and not a:
     label=(chosen['name'],'curb',0);refs[label]=shift(COL[chosen['name']],12);vox[x,y,15]=label
 return vox,refs

def paint(raw,refs,style):
 flat='TwoColor' in style;crate='CratePalette' in style
 palette=[tuple(c) for c in CRATE['rgba']] if crate else [(0,0,0,255)]*256
 keys={};mapping={};groups={}
 for key in sorted(refs):
  fam,g,t=key
  if flat:
   # Unlike substrate, mortar and moss remain distinct. Similar paving/curb merges.
   if g=='curb':g='surface'
   if g=='substrate' and BY[fam]['kind'] not in ['grass','broadgrass']:g='wood' if 'planks' in BY[fam]['kind'] else 'surface'
   rgb=mat_rgb(BY[fam],g,0);semantic=fam+':'+g
  else:rgb=refs[key];semantic=fam+':'+g
  unique=(semantic,rgb)
  if unique not in keys:
   if crate:
    kind=BY[fam]['kind']
    if g=='substrate':allowed=list(range(233,239))
    elif kind in WATER:allowed=list(range(249,255))
    elif g=='moss' or kind in ['grass','broadgrass']:allowed=list(range(241,247))
    elif kind in PAVING or kind=='slate' or 'GrayRock' in fam or 'CliffRock' in fam:allowed=[193,194,195,196,205,206]
    elif kind=='sand':allowed=[230,237,238]
    elif kind in ['planks','diagonalplanks']:allowed=[179,180,235,236,237,238]
    else:allowed=list(range(233,239))
    idx=min(allowed,key=lambda i:sum((palette[i-1][j]-rgb[j])**2 for j in range(3)))
   else:idx=len(keys)+1;palette[idx-1]=tuple(rgb)+(255,)
   keys[unique]=idx
  idx=keys[unique];mapping[key]=idx;groups.setdefault(semantic,set()).add(idx)
 return {p:mapping[v] for p,v in raw.items()},palette,{g:sorted(s) for g,s in groups.items()}

def main():
 old={r['file']:r['sha256'] for r in json.loads((HERE/'manifest.json').read_text())['models']} if (HERE/'manifest.json').exists() else {}
 result={'date':'2026-10-29','families':CAT,'models':[],'palette_sha256':CRATE['palette_sha256']}
 for r in CAT:
  folder=ROOT/'output'/Path(r['source']).stem;support=folder/'ground';support.mkdir(exist_ok=True)
  if r['role']=='surface':Image.open(ROOT/r['source']).convert('RGB').crop(r['crop']).resize((192,192),Image.Resampling.NEAREST).save(support/(r['name']+'_source.png'))
  for style in STYLES:
   raw,refs=model(r,'Cartoon' in style);v,palette,groups=paint(raw,refs,style)
   name=r['name']+('' if style=='Base' else '_'+style);path=folder/(name+'.vox');rel=path.relative_to(ROOT).as_posix()
   if path.exists():assert rel in old and sha(path)==old[rel],f'Preserving unrecognized or hand-edited model: {path}'
   write(path,(16,16,16),v,palette)
   row={'file':rel,'family':r['name'],'source':r['source'],'style':style,'canvas':[16,16,16],'voxels':len(v),'colors':len(set(v.values())),'groups':groups,'sha256':sha(path),'occupied_min':[min(p[i] for p in v) for i in range(3)],'occupied_max':[max(p[i] for p in v) for i in range(3)]}
   result['models'].append(row)
 (HERE/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
 print('Generated',len(result['models']),'VOX files from',len(CAT),'families')
if __name__=='__main__':main()
