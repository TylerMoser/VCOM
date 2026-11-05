extends SceneTree
const Reader=preload("res://addons/MagicaVoxel_Importer_with_Extensions/VoxImporter/vox-importer-common.gd")
func _initialize(): call_deferred("run")
func run():
 var base=OS.get_cmdline_user_args()[0]+"/"
 var rows=JSON.parse_string(FileAccess.get_file_as_string(base+"manifest.json"))
 root.size=Vector2i(320,320);root.msaa_3d=Viewport.MSAA_4X
 var scene=Node3D.new();root.add_child(scene)
 var world=WorldEnvironment.new();var env=Environment.new();env.background_mode=Environment.BG_COLOR;env.background_color=Color("233440");env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color.WHITE;env.ambient_light_energy=.65;world.environment=env;scene.add_child(world)
 var sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-40,-30,0);sun.light_energy=1.0;scene.add_child(sun)
 var camera=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=.9;scene.add_child(camera)
 var report=[]
 DirAccess.make_dir_recursive_absolute(base+"previews")
 for row in rows:
  var reader=Reader.new();var data=reader.read_vox_data(row.path);assert(data.error==OK)
  var unified=reader.unify_voxels(data.vox,false);assert(unified.size()==1)
  var points=unified[unified.keys()[0]];assert(points.size()==int(row.voxels))
  var meshes=reader.import(row.path,"",{"Scale":.0625,"GreedyMeshGenerator":true,"SnapToGround":false,"FirstKeyframeOnly":true},[],[])
  assert(meshes is Array and meshes.size()==1)
  var mesh:Mesh=meshes[0];var bounds=mesh.get_aabb();assert(abs(bounds.position.y)<.001)
  var extent=Vector3(row.canvas[0],row.canvas[2],row.canvas[1])/16.0
  assert(bounds.size.distance_to(extent)<.001)
  var transparent=0;var opaque=0
  for index in mesh.get_surface_count():
   var material=mesh.surface_get_material(index)
   if material.transparency==BaseMaterial3D.TRANSPARENCY_ALPHA: transparent+=1
   else: opaque+=1
  assert(opaque>=1 and (transparent>=1 if row.glass_voxels>0 else transparent==0))
  var item=MeshInstance3D.new();item.mesh=mesh;scene.add_child(item)
  camera.size=max(bounds.size.y*1.35,bounds.size.x*1.5)
  var target=bounds.get_center();camera.position=target+Vector3(.55,.35,2.0);camera.look_at(target)
  for frame in 3: await process_frame
  await RenderingServer.frame_post_draw
  assert(root.get_texture().get_image().save_png(base+"previews/"+row.name.trim_suffix(".vox")+".png")==OK)
  if true:
   camera.position=target+Vector3(-.8,.4,-2);camera.look_at(target)
   for frame in 3: await process_frame
   await RenderingServer.frame_post_draw
   root.get_texture().get_image().save_png(base+"previews/"+row.name.trim_suffix(".vox")+"_back.png")
  report.append({"name":row.name,"sha256":row.sha256,"voxel_count":points.size(),"grounded":true,"bounds_match":true,"transparent_surfaces":transparent,"opaque_surfaces":opaque})
  item.queue_free();await process_frame
 var file=FileAccess.open(base+"import-validation.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
 print("SHIELD_IMPORT_RENDER_PASS ",report.size());quit()
