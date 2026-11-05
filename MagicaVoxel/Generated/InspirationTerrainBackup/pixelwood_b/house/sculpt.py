"""Pixelwood cabin. Deliberate front asymmetry preserved in Cartoon."""
import math
from voxlib import components
def build(cartoon):
 v={};g={}
 def put(x,y,z,c):
  if 0<=x<80 and 0<=y<80 and 0<=z<80:v[x,y,z]=c;g[x,y,z]='wood' if c<=6 else 'accent'
 def box(x0,x1,y0,y1,z0,z1,c):
  for x in range(x0,x1+1):
   for y in range(y0,y1+1):
    for z in range(z0,z1+1):put(x,y,z,c)
 def roof(x):return round(34+35*(1-abs(x-39.5)/39.5))
 # Raised plank floor, solid perimeter sill and four low feet.
 box(4,75,10,69,3,5,3)
 for x in range(6,74):
  for y in range(12,68):put(x,y,5,4 if cartoon else 3+(x//4)%3)
 for x in (6,66):
  for y in (12,60):box(x,x+7,y,y+7,0,2,2)
 # Board walls: real interior void; horizontal relief on exterior courses.
 for z in range(6,35):
  for x in range(4,76):
   col=3 if z%5==0 else (4 if cartoon else 3+(z//5)%3)
   for y in (10,11,68,69):put(x,y,z,col)
  for y in range(12,68):
   col=3 if z%5==0 else (4 if cartoon else 3+(z//5)%3)
   for x in (4,5,74,75):put(x,y,z,col)
 # Vertical boards in the triangular gables.
 for x in range(4,76):
  for z in range(35,roof(x)):
   col=3 if x%4==0 else (4 if cartoon else 3+x%3)
   for y in (10,11,68,69):put(x,y,z,col)
 # Source-like vertical timber skirt beneath the horizontal wall boards.
 for x in range(4,76):
  for z in range(6,10):put(x,9,z,2 if x%3==0 else (3 if cartoon else 3+x%2))
 # Corner posts, heavy bottom sill and front crossbeam.
 for x in (4,72):
  for y in (9,68):box(x,x+3,y,y+2,5,34,3)
 box(4,75,8,11,3,5,4);box(4,75,8,10,32,34,4)
 for x in (5,72):
  for z in (15,24):box(x,x+2,7,9,z,z+2,5)
 # Arched door on the LEFT. Closed door panel is inset behind its surround.
 for x in range(16,36):
  for z in range(6,30):
   top=21+round(7*math.sqrt(max(0,1-((x-25.5)/10)**2)))
   if z>top:continue
   for y in (10,11):v.pop((x,y,z),None);g.pop((x,y,z),None)
   edge=x<=18 or x>=33 or z>=top-2
   if edge:box(x,x,7,11,z,z,5)
   else:box(x,x,12,12,z,z,2 if x%4==0 else (3 if cartoon else 3+(x//4)%2))
 box(19,32,10,12,10,11,4);box(19,32,10,12,17,18,4)
 box(30,31,9,11,14,15,6)
 # Broad front window on the RIGHT: dark recessed opaque panes and a cross frame.
 for x in range(46,67):
  for z in range(16,30):
   for y in (10,11):v.pop((x,y,z),None);g.pop((x,y,z),None)
   put(x,12,z,17)
 box(44,68,8,11,14,15,5);box(44,68,8,11,30,31,3)
 box(44,45,8,11,16,29,3);box(67,68,8,11,16,29,3)
 box(55,56,9,12,16,29,4);box(46,66,9,12,22,23,4)
 # Circular attic window centered in the gable.
 for x in range(32,48):
  for z in range(41,57):
   d=math.hypot(x-39.5,z-48.5)
   if d<=7:
    for y in (10,11):v.pop((x,y,z),None);g.pop((x,y,z),None)
    if d>=5.7:box(x,x,8,11,z,z,3)
    else:put(x,10,z,17)
 box(39,40,9,12,43,54,4);box(34,45,9,12,48,49,4)
 # Front entry steps; connected to floor with a source-like broad tread.
 box(16,35,1,9,0,1,3);box(16,35,4,9,2,3,4);box(16,35,7,10,4,5,5)
 # Ribbed green pitched roof. Two layers keep diagonal steps connected.
 for x in range(80):
  z=roof(x);mx=min(x,79-x)
  for y in range(8,74):
   rib=mx%(8 if cartoon else 6)==0
   col=(11 if rib else 9) if cartoon else ((11 if x<40 else 9) if rib else (10 if x<40 else 8))
   if not cartoon and y in (25,26,52) and mx%13==3:col=7
   for zz in (z-1,z):put(x,y,zz,col)
   if rib and y not in (8,73):put(x,y,z+1,col)
   if y in (8,73):put(x,y,z,7)
 # Ridge cap and thick dark fascia; no invented side windows.
 box(39,40,7,74,68,70,10)
 for x in range(80):
  for y in (7,8,73,74):
   for z in (roof(x)-2,roof(x)-1):put(x,y,z,7)
 # Masonry chimney left and toward the rear. Hollow flue in its upper section.
 for z in range(44,80):
  for x in range(14,25):
   for y in range(49,60):
    if z>=73 and 17<=x<=21 and 52<=y<=56:continue
    mortar=z%5==0 or ((x+(3 if z//5%2 else 0))%7==0 and y in (49,59))
    col=13 if mortar else (15 if cartoon else 14+(x//4+z//5)%2)
    put(x,y,z,col)
 # Ensure the flue remains open through the roof and chimney masonry.
 for x in range(17,22):
  for y in range(52,57):
   for z in range(73,80):v.pop((x,y,z),None);g.pop((x,y,z),None)
 assert len(components(v))==1,components(v)
 assert (40,40,20) not in v
 return v,g
