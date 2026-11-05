"""Six source-directed architectural reconstructions, Z-up and front -Y.
Indices 1..6 body/structure, 7+ roof and secondary accents.
"""
import math
from voxlib import components
def build(kind,size,cartoon):
 W,D,H=size;v={};g={}
 def put(x,y,z,c):
  if 0<=x<W and 0<=y<D and 0<=z<H:v[x,y,z]=c;g[x,y,z]='body' if c<=6 else 'accent'
 def box(x0,x1,y0,y1,z0,z1,c):
  for x in range(max(0,x0),min(W,x1+1)):
   for y in range(max(0,y0),min(D,y1+1)):
    for z in range(max(0,z0),min(H,z1+1)):put(x,y,z,c)
 def shell(x0,x1,y0,y1,floor,top):
  box(x0,x1,y0,y1,0,floor,2)
  for z in range(floor+1,top+1):
   col=4 if cartoon else (3 if z%5==0 else 4+(z//5)%2)
   box(x0,x1,y0,y0+1,z,z,col);box(x0,x1,y1-1,y1,z,z,col)
   box(x0,x0+1,y0,y1,z,z,col);box(x1-1,x1,y0,y1,z,z,col)
 def window(x0,x1,z0,z1,y,frame=6):
  # Recessed opaque blue glazing, with a raised frame and narrow mullions.
  box(x0,x1,y-1,y+2,z0,z1,frame)
  box(x0+2,x1-2,y-2,y-2,z0+2,z1-2,14)
  for x in range(x0+2,x1-1):
   for z in range(z0+2,z1-1):
    if not cartoon and (x+z)%11<2:put(x,y-2,z,15)
  mid=(x0+x1)//2
  box(mid,mid,y-3,y-2,z0+2,z1-2,frame)
  box(x0+2,x1-2,y-3,y-2,(z0+z1)//2,(z0+z1)//2,frame)
 def door(x0,x1,z0,z1,y,c=3):
  box(x0,x1,y-2,y,z0,z1,2);box(x0+2,x1-2,y-3,y-3,z0+1,z1-2,c)
  box(x1-4,x1-3,y-4,y-3,z0+(z1-z0)//2,z0+(z1-z0)//2+1,16)
 def steps(x0,x1,ystart,yend,height):
  for y in range(ystart,yend+1):
   z=min(height,1+((y-ystart)//3)*2)
   box(x0,x1,y,y,0,z,5 if cartoon else 3+(y//3)%3)
 def sphere(cx,cy,cz,rx,ry,rz,col):
  for x in range(max(0,int(cx-rx)),min(W,int(cx+rx)+2)):
   for y in range(max(0,int(cy-ry)),min(D,int(cy+ry)+2)):
    for z in range(max(0,int(cz-rz)),min(H,int(cz+rz)+2)):
     if ((x-cx)/rx)**2+((y-cy)/ry)**2+((z-cz)/rz)**2<=1:put(x,y,z,col)
 if kind=='DomeLab':
  shell(6,113,12,91,3,49)
  # Pale columns and decorative header, matching the tall institutional facade.
  for x in (7,43,74,108):box(x,x+4,9,13,3,49,5)
  box(6,113,8,13,1,4,4);box(4,115,9,94,48,51,5)
  for x0 in (20,84):
   window(x0,x0+17,10,25,10);window(x0,x0+17,31,46,10)
  window(51,69,35,47,10);door(52,68,4,23,10,14)
  # Low red roof with parallel courses under the rooftop rotunda.
  box(3,116,10,95,51,54,7)
  for y in range(12,94):box(5,114,y,y,55,55,9 if cartoon else (8 if y%5==0 else 10))
  for x in (2,115):box(x,x+2,9,96,51,57,5)
  for y in (9,94):box(2,117,y,y+2,51,57,5)
  cx=59.5;cy=54.5;radius=35
  # Cylindrical glazed drum; domed shell over a hollow upper room.
  for x in range(24,96):
   for y in range(19,91):
    rr=math.hypot(x-cx,y-cy)
    if 32<=rr<=35:
     for z in range(56,73):
      a=math.atan2(y-cy,x-cx);mullion=abs(math.sin(a*8))<.16
      put(x,y,z,5 if z in (56,57,71,72) or mullion else (14 if cartoon or (x+z)%13>2 else 15))
    if rr<=35:
     dome=73+int(38*max(0,1-(rr/35)**2)**(.42 if cartoon else .5))
     for z in range(73,dome+1):put(x,y,z,6 if cartoon or z>96 else (4 if z<81 else 5))
  # Central plaque with a raised stylized diagonal feather/wing relief.
  box(48,72,6,10,25,34,2);box(49,71,5,6,26,33,6)
  for i in range(17):
   x=51+i;z=27+i//3
   box(x,x,3,5,z,z+1,14)
   if i%3==0:box(x,x+2,3,5,z+1,z+3,15)
 elif kind=='RedClinic':
  shell(7,96,16,85,2,29)
  box(4,99,13,89,28,32,6)
  # Rounded low hip roof, with a broad top and darker perimeter.
  for z in range(32,53):
   inset=max(0,(z-42)//3)
   x0=3+inset;x1=100-inset;y0=13+inset;y1=89-inset
   if z<=35:box(x0,x1,y0,y1,z,z,7);continue
   for x in range(x0,x1+1):
    for y in range(y0,y1+1):
     corner=min(x-x0,x1-x)<(4 if cartoon else 2) and min(y-y0,y1-y)<(4 if cartoon else 2)
     if corner:continue
     if z>=50 or x<=x0+2 or x>=x1-2 or y<=y0+2 or y>=y1-2:
      col=10 if cartoon else (11 if (x//4+y//4)%2==0 else 10)
      put(x,y,z,col)
  # Right-side blue roof light with pale raised border.
  box(58,83,44,76,52,55,5);box(61,80,47,73,55,56,14)
  for y in range(48,73):
   for x in range(62,80):
    if (x+y)%16<3:put(x,y,56,15)
  door(32,53,3,23,15,14)
  window(14,26,7,21,15);door(77,90,3,23,15,3)
  # Red entrance canopy, circular red/white medical emblem, small sign plate.
  box(11,75,6,17,24,28,8);box(14,72,5,7,25,27,10)
  sphere(43,6,30,7,3,7,6)
  for p in list(v):
   x,y,z=p
   if (x-43)**2+(z-30)**2<=49 and 3<=y<=7:
    put(x,y,z,9 if z>30 else (17 if z==30 else 6))
  sphere(43,3,30,2,1,2,6)
  box(61,71,10,15,5,16,6)
  for z in (8,12):box(63,69,9,10,z,z,9)
  box(63,63,9,10,8,13,9)
  for x in (8,94):box(x,x+2,12,15,2,29,3)
  # Four small roof air vents on rear rim keep the silhouette source-guided.
 elif kind in ('GrayEntryHouse','GrayWindowHouse','CyanEntryHouse'):
  entry=kind!='GrayWindowHouse';floor=9 if entry else 3
  shell(5,74,24,70,floor,38)
  box(4,75,22,72,36,39,13)
  # Mansard roof: broad flat inset top and sloping lower sides.
  for z in range(40,73):
   k=min(10,(z-40)//(4 if cartoon else 3));x0=2+k;x1=77-k;y0=21+k;y1=73-k
   if z==72:box(x0,x1,y0,y1,z,z,9);continue
   box(x0,x0+1,y0,y1,z,z,8);box(x1-1,x1,y0,y1,z,z,8)
   box(x0,x1,y0,y0+1,z,z,8);box(x0,x1,y1-1,y1,z,z,8)
  # Raised perimeter rim and inset flat roof surface.
  box(11,68,30,64,72,74,7);box(14,65,33,61,74,74,10)
  for x in (11,67):box(x,x+1,30,64,74,76,13)
  for y in (30,63):box(11,68,y,y+1,74,76,13)
  # Upper facade dormer band, flanked by three stepped roof buttresses.
  box(16,63,20,27,42,54,6)
  for x in (21,48):window(x,x+10,43,53,20)
  for x in (6,35,64):
   for y in range(19,30):box(x,x+8,y,y,39,44+(y-19)*2,8 if cartoon else 7+(y//3)%3)
  box(4,75,18,24,38,41,13)
  # A small stacked vent on the back-left roof corner.
  box(14,20,51,62,75,79,13);box(15,19,53,56,79,79,17);box(15,19,59,61,79,79,14)
  if entry:
   door(29,47,10,31,23,3);window(12,24,17,31,23);window(57,68,14,28,23)
   steps(28,48,2,24,9)
   for x in (25,49):
    for y in range(3,24):box(x,x+3,y,y,0,5+(y//3),6)
   box(49,54,18,23,25,30,13);box(50,52,17,18,26,29,6)
  else:
   for x in (13,33,53):window(x,x+13,12,28,23)
   box(5,74,21,24,4,7,13)
 elif kind=='FlowerCottage':
  # Main cream cottage plus narrow timber side annex/deck.
  shell(7,77,18,73,3,29);shell(78,99,20,71,2,25)
  for y in range(20,72):box(78,99,y,y,26,27,3 if y%5==0 else 5)
  for x in (78,98):box(x,x+1,19,73,26,30,3)
  # Main gabled tiled roof with ridge extending into the map.
  for x in range(3,82):
   z=30+round(31*(1-abs(x-42)/39))
   for y in range(15,77):
    col=10 if cartoon else (9 if y%4==0 or (x+(y//4%2)*3)%7==0 else 10+(x<42))
    for zz in (z-1,z):put(x,y,zz,col)
    if y in (15,76):put(x,y,z,7)
    elif y%(12 if cartoon else 8)==0:put(x,y,z+1,col)
  box(40,44,14,77,60,63,9)
  # Gable face and central tiny attic vent.
  for x in range(7,78):
   top=30+round(31*(1-abs(x-42)/39))
   box(x,x,18,19,30,top-2,5 if cartoon else 4+(x//4)%2)
   box(x,x,72,73,30,top-2,4)
  window(38,46,43,49,17)
  # Two small rectangular roof fixtures on the left slope.
  for y in (46,65):
   for x in range(12,19):
    z=30+round(31*(1-abs(x-42)/39))
    box(x,x,y,y+7,z,z+2,3)
    if 13<=x<=17:box(x,x,y+1,y+6,z+2,z+3,17)
  # Upper blue windows with attached flower boxes.
  for x in (15,55):
   window(x,x+18,25,38,16)
   box(x-1,x+19,9,17,22,25,3)
   for j in range(5):
    xx=x+2+j*3
    box(xx,xx+1,8,12,25,28,18)
    sphere(xx,9,29+(j%2),1.7,1.7,1.7,19 if j%2==0 else 16)
  # Lower door and projecting bay window with terracotta hoods.
  door(19,34,3,20,17,14);window(50,69,7,20,12)
  box(48,71,12,18,3,23,5);window(51,68,7,20,11)
  for y in range(7,18):
   box(14,38,y,y,20+(y-7)//3,22+(y-7)//3,9)
   box(46,73,y,y,21+(y-7)//3,23+(y-7)//3,9)
  steps(18,35,4,18,3)
 else:raise ValueError(kind)
 assert len(components(v))==1,(kind,cartoon,components(v))
 return v,g
