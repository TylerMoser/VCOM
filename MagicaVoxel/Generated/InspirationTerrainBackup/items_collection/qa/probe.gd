extends SceneTree
const Reader=preload("res://addons/MagicaVoxel_Importer_with_Extensions/VoxImporter/vox-importer-common.gd")
func _initialize():call_deferred("run")
func run():
 var args=OS.get_cmdline_user_args();var base=args[0]+"/"
 var rows=JSON.parse_string(FileAccess.get_file_as_string(base+"render-list.json"))
 root.size=Vector2i(192,192);root.msaa_3d=Viewport.MSAA_4X
 var scene=Node3D.new();root.add_child(scene)
 var world=WorldEnvironment.new();var env=Environment.new();env.background_mode=Environment.BG_COLOR;env.background_color=Color("26343e");env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color.WHITE;env.ambient_light_energy=.55;world.environment=env;scene.add_child(world)
 var sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-40,-30,0);sun.light_energy=.8;scene.add_child(sun)
 var fill=DirectionalLight3D.new();fill.rotation_degrees=Vector3(-30,150,0);fill.light_energy=.3;scene.add_child(fill)
 var camera=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;scene.add_child(camera)
 var report={};var sig=FileAccess.get_sha256(get_script().resource_path)
 if FileAccess.file_exists(base+"import-validation.json"):report=JSON.parse_string(FileAccess.get_file_as_string(base+"import-validation.json"))
 DirAccess.make_dir_recursive_absolute(base+"previews")
 var count=0
 for row in rows:
  if args.size()>1 and row.category!=args[1]:continue
  if report.has(row.file) and report[row.file].sha256==row.sha256 and report[row.file].get("signature","")==sig:continue
  var reader=Reader.new();var data=reader.read_vox_data(row.path);assert(data.error==OK,row.file)
  var unified=reader.unify_voxels(data.vox,false);assert(unified.size()==1,row.file)
  var points=unified[unified.keys()[0]];assert(points.size()==int(row.voxels),row.file)
  var options={"Scale":.0625,"GreedyMeshGenerator":true,"SnapToGround":false,"FirstKeyframeOnly":true}
  var meshes=reader.import(row.path,"",options,[],[]);assert(meshes is Array and meshes.size()==1,row.file)
  var mesh:Mesh=meshes[0];var bounds=mesh.get_aabb()
  var lo=row.occupied_min;var hi=row.occupied_max
  var extent=Vector3(hi[0]-lo[0]+1,hi[2]-lo[2]+1,hi[1]-lo[1]+1)/16.0
  assert(bounds.size.distance_to(extent)<.001,row.file)
  if row.form=="Standalone":assert(abs(bounds.position.y)<.001,row.file)
  var transparency=0
  for j in mesh.get_surface_count():
   if mesh.surface_get_material(j).transparency==BaseMaterial3D.TRANSPARENCY_ALPHA:transparency+=1
  assert((transparency>0)==(row.glass_voxels>0),row.file)
  if row.form=="Fitted":
   meshes=Reader.new().import(row.render_path,"",options,[],[]);mesh=meshes[0];bounds=mesh.get_aabb()
  var item=MeshInstance3D.new();item.mesh=mesh;scene.add_child(item)
  var target=bounds.get_center();camera.size=max(max(bounds.size.y*1.4,bounds.size.x*1.4),bounds.size.z*1.4)
  camera.position=target+Vector3(.8,.65,2);camera.look_at(target)
  for frame in 2:await process_frame
  await RenderingServer.frame_post_draw
  assert(root.get_texture().get_image().save_png(base+"previews/"+row.preview_id+".png")==OK)
  if row.style=="Base":
   camera.position=target+Vector3(-.9,.5,-2);camera.look_at(target)
   for frame in 2:await process_frame
   await RenderingServer.frame_post_draw
   assert(root.get_texture().get_image().save_png(base+"previews/"+row.preview_id+"_back.png")==OK)
  report[row.file]={"sha256":row.sha256,"signature":sig,"voxels":points.size(),"bounds_match":true,"transparent_surfaces":transparency,"preview_id":row.preview_id,"fitted_on_mannequin":row.form=="Fitted"}
  item.queue_free();await process_frame;count+=1
  if count%40==0:
   var f=FileAccess.open(base+"import-validation.json",FileAccess.WRITE);f.store_string(JSON.stringify(report));f.close()
   print("ITEM_RENDER_PROGRESS ",report.size(),"/",rows.size())
 var file=FileAccess.open(base+"import-validation.json",FileAccess.WRITE);file.store_string(JSON.stringify(report));file.close()
 print("ITEM_IMPORT_RENDER_PASS ",report.size());quit()
