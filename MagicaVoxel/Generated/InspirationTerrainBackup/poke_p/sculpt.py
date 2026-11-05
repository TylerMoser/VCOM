"""Layered teal tree and sapling matching poke_p; local geometry dependencies."""
from profiles import build as profile_build
from leaves import build as leaf_build

def build(kind,n,h,cartoon,decor):
 if kind=='layered':return leaf_build('droop',n,h,cartoon,None)
 return profile_build('column',n,h,cartoon,None)
