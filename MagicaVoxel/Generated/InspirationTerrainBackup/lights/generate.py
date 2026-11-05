"""Reproduce the 2026-10-28 lighting collection; never writes to VoxelXCOM.
Run from any directory. Complete models only, no per-cell files.
"""
from pathlib import Path
import sys,json,hashlib,struct,math
from PIL import Image
from sculpt import build
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'output/poke_b/buildings'))
from voxlib import chunk,dictionary,components,read
STYLES=['Base','Cartoon','CratePalette','TwoColor','Cartoon_TwoColor','CratePalette_TwoColor','Cartoon_CratePalette_TwoColor']
FAMILIES=[
 dict(source='pixelwood_a.jpg',name='PixelwoodA_PostLantern',shape='pixelwood',size=[16,16,40],crop=[99,207,154,340],scale=1/3,metal=[81,85,98],light=[255,205,115],power=1.5,note='Square amber lantern, dark corner mullions, broad hipped cap and squared foot. Three source pixels per voxel.'),
 dict(source='pixelwood_b.gif',name='PixelwoodB_Campfire',shape='fire',size=[24,24,28],crop=[540,820,680,975],scale=.2,metal=[81,85,98],light=[244,154,62],power=1.5,note='Five GIF frames reviewed. Static flame inspired by frame 0; eight-sided rock ring and charred logs; no animation or detached sparks.'),
 dict(source='poke_b.png',name='PokeB_SilverStreetLantern',shape='cap',size=[12,12,40],crop=[414,182,435,227],scale=1,metal=[100,113,104],light=[211,246,247],power=2,note='Tapered pale-blue diffuser, faceted silver cap and finial, narrow stem, square-reading stepped pedestal.'),
 dict(source='poke_c.png',name='PokeC_SilverStreetLantern',shape='cap',size=[12,12,40],crop=[63,254,85,305],scale=1,metal=[100,113,104],light=[211,246,247],power=2,note='Same silver lantern artwork as poke_b. Reuses its complete geometry and palette under this image folder; not an additional design.'),
 dict(source='poke_d.png',name='PokeD_StoneLantern',shape='stone',size=[16,16,20],crop=[458,198,486,229],scale=1,metal=[172,171,151],light=[255,205,128],power=1,note='Small stone garden lantern: broad rounded cap and finial, open chamber, short feet. Source unlit dark chamber; small warm burner inferred for usable night lighting.'),
 dict(source='poke_f.png',name='PokeF_TwinGlobeStreetlight',shape='twin',size=[32,12,48],crop=[207,235,242,291],scale=1,metal=[142,137,128],light=[222,245,243],power=2,note='Paired low-domed lamps on rising Y arms and one ringed pedestal. Two heads in one complete file.'),
 dict(source='poke_g.png',name='PokeG_RoundStreetlight',shape='drum',size=[16,16,48],crop=[397,155,420,211],scale=1,metal=[140,134,126],light=[220,246,241],power=2,note='Wide low-domed gray head, short pale diffuser band, slender stem and tiered round base.'),
 dict(source='poke_j.jpg',name='PokeJ_DarkStreetLantern',shape='cap',size=[10,10,28],crop=[190,130,215,174],scale=2/3,metal=[54,66,68],light=[227,236,220],power=1.5,note='Small dark lantern left of north house. JPEG obscures detail; inferred faceted cap and small luminous chamber. Existing scale estimate: 24 displayed pixels per tile.'),
 dict(source='poke_m.png',name='PokeM_BronzePostLantern',shape='hood',size=[16,16,48],crop=[25,844,55,880],scale=1,metal=[122,112,80],light=[243,243,211],power=2,note='Visible at lower image edge: bronze pointed hood, broad cream chamber and thin pole. Base and lower stem are cropped away; inferred matching stepped pedestal, total height 48.'),
 dict(source='poke_n.png',name='PokeN_TealStreetlight',shape='drum',size=[16,16,40],crop=[266,414,290,465],scale=1,metal=[63,86,88],light=[166,193,193],power=2,note='Dark teal disc cap, recessed gray-blue diffuser band and flared pedestal. Luminescence inferred from identifiable lamp fixture in daytime source.'),
 dict(source='poke_s.jpg',name='PokeS_IvoryScrollLantern',shape='crook',size=[24,16,56],crop=[630,59,658,104],scale=1.6,metal=[219,218,190],light=[255,238,180],power=2,note='Ivory curved shepherd-hook fixture repeated beside waterfalls. Small compressed image: scroll and hanging lantern reconstructed; approx. 10 displayed pixels per tile. Bilateral depth symmetry, intentional offset lantern preserved.'),
]
NO_LIGHT={
 'mario.jpg':'Question blocks, HUD and signs are not light fixtures.',
 'pixelwood_c.jpg':'Orange water plants are cattails with green leaves, not torches; chest is not a lamp.',
 'poke_a.jpg':'Woodland paths, fences and flowers; no identifiable lighting prop.',
 'poke_e.png':'Trees, flowers, fences and water; no identifiable lighting prop.',
 'poke_h.png':'Farm tools, scarecrows, hay and crops; no identifiable lighting prop.',
 'poke_i.jpg':'Red posts by doors are mailboxes; no identifiable lighting prop.',
 'poke_k.jpg':'Forest paths and signs; no identifiable lighting prop.',
 'poke_l.png':'Tree/terrain tilesheet; no lighting prop.',
 'poke_o.png':'Mailboxes, signs, benches, parasols and floral decorations; no identifiable lighting prop.',
 'poke_p.png':'Flowers, paths and building; no identifiable lighting prop.',
 'poke_q.png':'Paired sculpted creature statues at shrine and gate are not lamps; crystal rocks are not evidenced as lights.',
 'poke_r.png':'Blue objects beside doors are mailboxes; no identifiable lighting prop.',
 'poke_t.png':'Cave rocks, crystals, plants and signs; no identifiable torch or installed light.',
 'poke_u.jpg':'Signs, characters and pale sculpted trees; no identifiable lighting prop.',
}
def rgba(rgb):return tuple(rgb)+(255,)
def shifted(c,n):return [max(0,min(255,x+n)) for x in c]
def labels(f):
 metal=f['metal'];light=f['light']
 return {'metal':(metal,'structure'),'metalDark':(shifted(metal,-27),'structure'),'metalLight':(shifted(metal,28),'structure'),
 'frame':(shifted(metal,-27),'frame'),'stone':([164,164,149] if f['shape']=='stone' else [103,107,119],'stone'),
 'stoneDark':([117,119,104],'stone'),'stoneLight':([190,188,168] if f['shape']=='stone' else [146,149,157],'stone'),
 'wood':([105,67,41],'wood'),'woodDark':([63,43,33],'wood'),
 'light':(light,'emitter'),'flame':(light,'emitter'),'flameLight':([255,211,110],'emitter')}
def paint(f,m,style):
 info=labels(f);flat='TwoColor' in style;crate='CratePalette' in style
 palette=[rgba(f['metal'])]*256 if not crate else [tuple(c) for c in json.loads((ROOT/'knowledge/palettes/crate-palette.json').read_text())['rgba']]
 reps={'structure':f['metal'],'frame':shifted(f['metal'],-27),'stone':info['stone'][0],'wood':info['wood'][0],'emitter':f['light']}
 used=sorted(set(m.v.values()));mapping={};assigned={};material={};groups={}
 for label in used:
  rgb,group=info[label];rgb=reps[group] if flat else rgb
  key=(group,tuple(rgb))
  if key not in assigned:
   if crate:
    # A palette index cannot be both structural and emissive (or shadowless frame).
    allowed=list(range(1,255))
    if group in ('structure','frame','stone'):
     allowed=[185,186,187,193,194,195,196,201,202,203,204,205,206,248]
     if f['shape']=='hood':allowed=[185,225,226,227,228,229,230,233,234,235,236,237,238]
     if f['shape']=='crook':allowed=[193,194,195,196,237,238,248]
    if group=='wood':allowed=[178,179,180,225,226,227,228,233,234,235]
    if group=='emitter':allowed=[196,222,228,229,230,237,238,248,253,254]
    candidates=[i for i in allowed if i not in material or groups[i]==group]
    idx=min(candidates,key=lambda i:sum((palette[i-1][j]-rgb[j])**2 for j in range(3)))
   else:
    idx=len(assigned)+1;palette[idx-1]=rgba(rgb)
   assigned[key]=idx;groups[idx]=group
   material[idx]={'_type':'_emit','_emit':'.75','_flux':str(f['power']),'_ldr':'0'} if group=='emitter' else {'_type':'_diffuse','_rough':'1'}
  mapping[label]=assigned[key]
 vox={p:mapping[label] for p,label in m.v.items()}
 return vox,palette,material,{str(i):g for i,g in groups.items()}
def write(path,size,v,pal,mats):
 graph=chunk('nTRN',struct.pack('<i',0)+dictionary({})+struct.pack('<iiii',1,-1,-1,1)+dictionary({}))
 graph+=chunk('nGRP',struct.pack('<i',1)+dictionary({})+struct.pack('<ii',1,2))
 graph+=chunk('nTRN',struct.pack('<i',2)+dictionary({'_name':path.stem})+struct.pack('<iiii',3,-1,0,1)+dictionary({'_t':f'0 0 {size[2]//2}'}))
 graph+=chunk('nSHP',struct.pack('<i',3)+dictionary({})+struct.pack('<ii',1,0)+dictionary({}))
 body=chunk('SIZE',struct.pack('<iii',*size))+chunk('XYZI',struct.pack('<i',len(v))+b''.join(bytes((*p,c)) for p,c in sorted(v.items())))+graph
 body+=chunk('LAYR',struct.pack('<i',0)+dictionary({'_name':'Complete light'})+struct.pack('<i',-1))
 body+=chunk('RGBA',b''.join(bytes(c) for c in pal))
 for i,props in sorted(mats.items()):body+=chunk('MATL',struct.pack('<i',i)+dictionary(props))
 path.write_bytes(b'VOX '+struct.pack('<i',200)+chunk('MAIN',children=body))
def main():
 manifest={'date':'2026-10-28','emission':.75,'power_contract':'Energy=2^Power; reach=3.5*2^(Power-1) cells for registered level pieces.','models':[],'families':FAMILIES}
 inventory=json.loads((HERE/'source-inventory.json').read_text())
 for f in FAMILIES:
  stem=Path(f['source']).stem;dest=ROOT/'output'/stem;support=dest/'lights';support.mkdir(parents=True,exist_ok=True)
  crop=Image.open(ROOT/f['source']).convert('RGB').crop(f['crop']);crop.resize((crop.width*4,crop.height*4),Image.Resampling.NEAREST).save(support/(f['name']+'_source.png'))
  models={False:build(f),True:build(f,True)}
  assert set(models[False].v)!=set(models[True].v),(f['name'],'Cartoon must change shape')
  for style in STYLES:
   m=models['Cartoon' in style];v,pal,mats,groups=paint(f,m,style)
   filename=f['name']+('' if style=='Base' else '_'+style)+'.vox';path=dest/filename
   write(path,m.size,v,pal,mats)
   reread=read(path);assert reread==(m.size,v,pal)
   emission=[i for i,p in mats.items() if p['_type']=='_emit'];ep=[p for p,i in v.items() if i in emission]
   bounds=[[min(p[k] for p in v) for k in range(3)],[max(p[k] for p in v) for k in range(3)]]
   row=dict(file=str(path.relative_to(ROOT)).replace('\\','/'),family=f['name'],style=style,canvas=m.size,voxels=len(v),occupied_min=bounds[0],occupied_max=bounds[1],components=components(v),
    emission_indices=emission,emission_voxels=len(ep),emission=.75,power=f['power'],shadowless_colors=[int(i) for i,g in groups.items() if g=='frame'],groups=groups,
    colors=len(set(v.values())),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),palette_sha256=hashlib.sha256(b''.join(bytes(c) for c in pal)).hexdigest(),
    emitter_centroid=[sum(p[k]+.5 for p in ep)/len(ep) for k in range(3)])
   assert row['components']==[len(v)],(filename,row['components'])
   assert 255 not in v.values() and ep
   if 'CratePalette' in style:assert row['palette_sha256']=='b1a4e811c89d143b006c0a421443dd2e1b3b9da0b6588b176c4d072b67c279c2'
   if 'TwoColor' in style:
    for g in set(groups.values()):assert len({i for i in v.values() if groups[str(i)]==g})==1
   manifest['models'].append(row)
  (support/'manifest.json').write_text(json.dumps({'family':f,'models':[r for r in manifest['models'] if r['family']==f['name']]},indent=2))
 for item in inventory:
  item['assessment']=NO_LIGHT.get(item['source'],'Identifiable lighting modeled; see families.')
  item['families']=[f['name'] for f in FAMILIES if f['source']==item['source']]
  assert item['families'] or item['source'] in NO_LIGHT
 (HERE/'catalogue.json').write_text(json.dumps({'sources':inventory,'families':FAMILIES},indent=2))
 (HERE/'manifest.json').write_text(json.dumps(manifest,indent=2))
 print('Generated',len(manifest['models']),'complete models across',len(FAMILIES),'source appearances')
if __name__=='__main__':main()
