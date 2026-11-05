"""Equipment at Character_Bigger's original T-pose coordinates, no rescaling."""
from voxlib import Model,read,GAME
BODY_SIZE,BODY,_,_=read(GAME/'MagicaVoxel/Characters/Character_Bigger.vox')
def bone(p,family):
 x,y,z=p
 if family=='helmet' or (family=='wearable' and z>=20):return 'Head'
 if family=='boots':return ('Right' if x<=16 else 'Left')+('Foot' if z==0 else 'LowerLeg' if z<=4 else 'UpperLeg')
 if z>=20:return 'Head'
 if z>=17:
  if x<=5:return 'RightHand'
  if x<=8:return 'RightLowerArm'
  if x<=13:return 'RightUpperArm'
  if x>=27:return 'LeftHand'
  if x>=24:return 'LeftLowerArm'
  if x>=19:return 'LeftUpperArm'
 if z==19:return 'Neck'
 if z>=15:return 'Chest'
 if z>=12:return 'Spine'
 if z>=9:return 'Hips'
 return ('Right' if x<=16 else 'Left')+('Foot' if z==0 else 'LowerLeg' if z<=4 else 'UpperLeg')
def helmet(name,v):
 m=Model();cap=name in ('Kepi','FieldCap','Tanker','Aviator');brim=name in ('Brodie','Pith','KettleHat','Morion','FieldCap','Kepi')
 low=25 if cap else (23 if name in ('Stahlhelm','Adrian','Pickelhaube','Miner') else 21)
 # Square-voxel envelope follows the base's broad block head and remains open at face.
 for x in range(11,22):
  for y in range(11,21):
   for z in range(low,29):
    if z<27 and 12<=x<=20 and 12<=y<=19:continue
    if y<=12 and z<25 and name not in ('GreatHelm','BoneHelm'):continue
    if z==28 and (x in (11,21) or y in (11,20)):continue
    m.put(x,y,z,6 if cap else 1)
 if brim:
  m.box(10,22,10,21,25 if cap else 26,25 if cap else 26,6 if cap else 2)
  # Keep the head cavity open through the brim's interior.
  for x in range(12,21):
   for y in range(12,20):m.v.pop((x,y,25 if cap else 26),None)
 if name in ('Pickelhaube','Pith','Bascinet'):
  for z in range(29,33):m.box(16-max(0,2-(z-29)),16+max(0,2-(z-29)),15-max(0,2-(z-29)),15+max(0,2-(z-29)),z,z,5 if name=='Pickelhaube' else 1)
 if name in ('Adrian','Morion','PlumedHelm') or v==2:
  m.box(16,16,12,19,29,30+(name=='PlumedHelm')*2,7 if name=='PlumedHelm' else 5)
 if name in ('HornedHelm','BoneHelm'):
  for x,side in ((11,-1),(21,1)):
   m.line((x,15,27),(x+side*3,15,29),10);m.line((x+side*3,15,29),(x+side*3,15,31+v%2),10)
 if name in ('NasalHelm','Spangenhelm','Barbute'):m.box(16,16,10,11,22,26,5)
 if name in ('GreatHelm','Sallet','Bascinet') or v==1:
  m.box(12,20,10,10,23,24,2)
  for x in (11,21):m.box(x,x,10,11,23,26,2)
  for x in range(13,20):m.v.pop((x,10,24),None)
 if name in ('Aviator','Tanker'):
  for x in (13,18):m.box(x,x+2,10,10,24,25,8)
  m.box(15,17,10,10,25,25,4)
 if name=='Miner':m.box(15,17,9,10,25,27,2);m.box(16,16,8,8,26,26,9)
 if v==3 or name=='RuneHelm':
  m.box(15,17,10,10,26,27,9)
  m.box(11,11,13,18,24,24,5);m.box(21,21,13,18,24,24,5)
 if v==0:m.box(13,19,11,11,26,26,2)
 if v==1:m.box(12,12,10,10,23,27,2);m.box(20,20,10,10,23,27,2)
 if v==2:m.box(15,17,14,16,29,31,5)
 if v==3:m.box(15,17,9,10,26,28,9)
 return m
def boots(name,v):
 m=Model();h=3
 if name in ('Cavalry','Wader','Greave','Trench','Officer','RuneBoot'):h=8
 elif name in ('Marching','FurLined','Mountain','Miner','Sabaton','SpikedBoot'):h=5
 if name in ('Sandal','Moccasin'):h=1
 h=min(8,h+v%2)
 for x0 in (14,17):
  for z in range(h+1):
   m.box(x0,x0+1,12 if z==0 else 14,18,z,z,1 if name in ('Sabaton','Greave') else 4)
  if name=='Sandal':
   m.box(x0,x0+1,14,14,1,1,3);m.box(x0,x0+1,17,17,1,1,3)
  else:
   for z in range(1,h+1):m.box(x0,x0+1,13,13,z,z,5 if z%2==0 else 4)
  m.box(x0,x0+1,12,18,0,0,2)
  if name in ('FurLined','Jungle','Desert','WrapBoot'):m.box(x0,x0+1,13,18,h,h,10 if name=='FurLined' else 6)
  if name in ('WingedBoot','SpikedBoot'):
   side=-1 if x0==14 else 1;xx=x0 if side==-1 else x0+1
   m.line((xx,17,2),(xx+side*(2+v%2),18,4),10 if name=='WingedBoot' else 1)
  if name in ('Officer','Cavalry'):m.box(x0,x0+1,12,13,h-2,h-1,5)
  if name in ('Trench','WrapBoot'):
   for z in range(2,h+1,2):m.box(x0,x0+1,13,18,z,z,6)
  if name in ('Mountain','Miner','Sabaton'):m.box(x0,x0+1,11,12,0,1,1)
  if name in ('Scout','Moccasin'):m.box(x0,x0+1,11,12,0,0,4)
  if name=='Alchemist':m.box(x0,x0+1,18,19,1,3,7)
  if name=='Wader':m.box(x0,x0+1,13,19,7,8,2)
  if name=='Sailor':m.box(x0,x0+1,12,13,1,2,6)
  if v==1:m.box(x0,x0+1,17,19,0,1,2)
  if v==2:m.box(x0,x0+1,11,12,1,2,1)
  if v==3:m.box(x0,x0+1,12,13,max(1,h-1),h,9)
 return m
def armor(name,v):
 m=Model();metal=name in ('Chainmail','Scalemail','HalfPlate','FullPlate','RingMail','Splint','BulletproofVest')
 base=1 if metal else 6 if name in ('Padded','ReinforcedVest') else 4
 zlow=9 if name in ('Padded','Chainmail','FullPlate','Scalemail') else 11
 for z in range(zlow,19):
  m.box(14,18,14,14,z,z,base);m.box(14,18,18,18,z,z,base)
  m.box(14,14,15,17,z,z,base);m.box(18,18,15,17,z,z,base)
  for x in range(14,19):
   if name in ('Chainmail','RingMail') and (x+z)%2==0:m.put(x,14,z,2)
   if name=='Scalemail' and z%2==0:m.put(x,13,z,5 if (x+z)%3==0 else 1)
   if name=='Splint' and x%2==0:m.put(x,13,z,1)
   if name=='Studded' and x%2==0 and z%3==0:m.put(x,13,z,1)
 # Shoulder straps keep the front/back joined at the top without blocking the neck.
 for x in (14,18):m.box(x,x,14,18,18,18,5 if metal else 4)
 if name in ('FullPlate','HalfPlate','Chainmail','Scalemail','Hide'):
  for x0,x1 in ((9,13),(19,23)):
   m.box(x0,x1,14,18,17,17,base);m.box(x0,x1,14,18,18,18,base)
   if v in (1,2):m.box(x0,x1,15,17,19,19,base)
 if name=='FullPlate':
  for x0 in (14,17):
   m.box(x0,x0+1,14,18,1,8,1)
   m.box(x0,x0+1,13,18,0,0,2)
 if name=='Hide':m.box(14,18,14,14,15,18,10)
 if name=='BulletproofVest':m.box(15,17,13,13,12,17,2)
 if v==0:m.box(14,18,13,13,11,11,4)
 elif v==1:
  for x in (14,17):m.box(x,x+1,12,13,11,13,4)
 elif v==2:m.box(16,16,13,13,zlow,18,5);m.box(14,18,13,13,16,16,5)
 else:m.box(15,17,13,13,15,17,5);m.put(16,12,16,9)
 return m
def gasmask(name,v):
 m=Model();m.box(13,19,10,11,21,25,4)
 for x in (13,18):m.box(x,x+1,9,9,24,25,8)
 for x in (11,21):m.box(x,x,12,20,24,24,4);m.box(min(x,13),max(x,19),11,12,24,24,4)
 m.box(11,21,20,20,24,24,4)
 if v in (0,2):m.box(15,17,8,9,21,23,2);m.box(15,17,7,7,21,21,1)
 else:
  m.box(12,13,8,9,21,23,2);m.box(19,20,8,9,21,23,2)
 if v==2:m.box(15,17,9,10,26,26,1)
 if v==3:m.box(15,17,9,9,24,24,9)
 return m
def build(spec,v):
 family,name=spec['family'],spec['name']
 m=helmet(name,v) if family=='helmet' else boots(name,v) if family=='boots' else gasmask(name,v) if name=='GasMask' else armor(name,v)
 # Equipment voxels may replace exposed body voxels when dressed; the body itself is preserved in QA composites.
 assert all(0<=p[0]<32 and 0<=p[1]<32 and 0<=p[2]<40 for p in m.v)
 assignments={p:bone(p,family) for p in m.v}
 return m,assignments
