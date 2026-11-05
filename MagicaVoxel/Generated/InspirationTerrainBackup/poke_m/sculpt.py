"""Source-specific dispatcher and budding sapling construction for poke_m."""
import math
from voxlib import components
from profiles import build as profile_build
from leaves import build as leaf_build

def build(kind,n,h,cartoon,decor):
 if kind in ('cluster','droop'):
  return leaf_build('layered' if kind=='cluster' else 'droop',n,h,cartoon,None)
 if kind!='bud':
  v,g=profile_build({'round':'ball','pointed':'broad','pine':'conifer','small':'sapling','smallpine':'smallpine'}[kind],n,h,cartoon,None)
  return v,g
 c=(n-1)/2;v={};g={}
 def ball(cx,cy,cz,rx,ry,rz,col,group):
  for x in range(max(0,int(cx-rx)),min(n,int(cx+rx)+2)):
   for y in range(max(0,int(cy-ry)),min(n,int(cy+ry)+2)):
    for z in range(max(0,int(cz-rz)),min(h,int(cz+rz)+2)):
     if ((x-cx)/rx)**2+((y-cy)/ry)**2+((z-cz)/rz)**2<=1:v[x,y,z]=col;g[x,y,z]=group
 for z in range(15):ball(c,c,z,1.5,1.5,1,8,'wood')
 ball(c,c,0,2.5,2.5,1,8,'wood')
 for j in range(4 if cartoon else 3):
  a=j*math.tau/(4 if cartoon else 3);co=math.cos(a);si=math.sin(a)
  tipz=19 if cartoon else [19,17,20][j]
  for step in range(21):
   q=step/20;ball(c+co*4.2*q,c+si*4.2*q,10+(tipz-10)*q,1,1,1,8 if cartoon else 7+j,'wood')
  ball(c+co*4.2,c+si*4.2,tipz,2.7,2.7,2.4,4,'foliage')
  ball(c+co*4.2,c+si*4.2,tipz+1,1.9,1.9,1.6,5,'foliage')
  ball(c+co*4.2,c+si*4.2,tipz+3,1.2,1.2,1.2,10,'foliage')
  ball(c+co*4.2,c+si*4.2,tipz+3.5,.9,.9,.9,11,'foliage')
 if cartoon:
  canonical={p:(v[p],g[p]) for p in v if p[0]>=n//2 and p[1]>=n//2};v={};g={}
  for (x,y,z),(col,group) in canonical.items():
   for q in [(x,y,z),(n-1-y,x,z),(n-1-x,n-1-y,z),(y,n-1-x,z)]:v[q]=col;g[q]=group
 assert len(components(v))==1,(kind,cartoon,components(v))
 return v,g
