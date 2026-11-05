"""Check all proposed geometry before writing files."""
import build,catalog,wearables
for spec in catalog.CATALOG:
 geometries=[]
 for variant in range(4):
  m=wearables.build(spec,variant)[0] if spec['family'] in catalog.WEARABLE else build.BUILDERS[spec['family']](spec['name'],variant)
  size,v,offset=m.normalize();geometries.append(frozenset(v))
  assert max(size)<=62
  assert len(build.component_sizes(v))==(2 if spec['family']=='boots' else 1),(spec,variant)
 assert len(set(geometries))==4,spec
print('All 387 types have four unique, correctly connected geometries.')
