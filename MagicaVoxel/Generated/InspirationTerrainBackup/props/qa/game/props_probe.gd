extends SceneTree
const Reader=preload("res://addons/MagicaVoxel_Importer_with_Extensions/VoxImporter/vox-importer-common.gd")
func _initialize():call_deferred("run")
func run():
 var workspace: String=OS.get_cmdline_user_args()[0]
 var manifest=JSON.parse_string(FileAccess.get_file_as_string(workspace+"/output/props/manifest.json"))
 root.size=Vector2i(360,360);root.msaa_3d=Viewport.MSAA_4X
 var scene=Node3D.new();root.add_child(scene)
 var floor_node=MeshInstance3D.new();var plane=PlaneMesh.new();plane.size=Vector2(100,100);floor_node.mesh=plane;floor_node.position.y=-.01
 var mat=StandardMaterial3D.new();mat.albedo_color=Color("899081");floor_node.material_override=mat;scene.add_child(floor_node)
 var world=WorldEnvironment.new();var env=Environment.new();env.background_mode=Environment.BG_COLOR;env.background_color=Color("d9dfd4");env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color.WHITE;env.ambient_light_energy=.25;world.environment=env;scene.add_child(world)
 var sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-48,-35,0);sun.shadow_enabled=true;sun.light_energy=.45;scene.add_child(sun)
 var camera=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;scene.add_child(camera)
 RenderingServer.global_shader_parameter_set("voxel_glow",0.0)
 var report={}
 var previous={}
 var report_path=workspace+"/output/props/godot-validation.json"
 if FileAccess.file_exists(report_path):previous=JSON.parse_string(FileAccess.get_file_as_string(report_path))
 for row in manifest.models:
  var path=workspace+"/"+row.file
  if previous.has(row.file) and previous[row.file].sha256==FileAccess.get_sha256(path):
   report[row.file]=previous[row.file];continue
  var meshes=Reader.new().import(path,"",{"Scale":.0625,"GreedyMeshGenerator":true,"SnapToGround":false,"FirstKeyframeOnly":true},[],[])
  assert(meshes is Array and meshes.size()==1)
  var mesh:Mesh=meshes[0];mesh.take_over_path(path)
  var shape=VoxelShape.read_mesh(mesh)
  assert(shape!=null and shape.count==int(row.voxels))
  assert(not shape.has_glow() and not shape.has_glass())
  var indices={}
  for i in shape.voxels:
   if i!=0:indices[i]=true
  assert(indices.size()==int(row.colors) and not indices.has(255))
  var bounds=mesh.get_aabb();assert(abs(bounds.position.y)<.001)
  var expected=Vector3(float(row.occupied_max[0])-float(row.occupied_min[0])+1,float(row.occupied_max[2])-float(row.occupied_min[2])+1,float(row.occupied_max[1])-float(row.occupied_min[1])+1)/16
  assert(bounds.size.distance_to(expected)<.001)
  var oversize=max(shape.size.x,max(shape.size.y,shape.size.z))>VoxelShape.WIDEST
  var item: Node3D
  if oversize:
   item=MeshInstance3D.new();item.mesh=mesh
  else:item=VoxelModel.new(shape).show_on()
  scene.add_child(item)
  var height=float(row.canvas[2])/16
  camera.size=max(height*1.3,float(max(row.canvas[0],row.canvas[1]))/16*1.55)
  camera.position=Vector3(0,height*.4+5.5,9);camera.look_at(Vector3(0,height*.4,0))
  if row.family in ["Mario_QuestionBlock","PokeH_HayBale"]:camera.size*=1.2
  var output=workspace+"/"+row.file.get_base_dir()+"/props/previews"
  DirAccess.make_dir_recursive_absolute(output)
  var stem=row.file.get_file().trim_suffix(".vox")
  var angles=[25]
  if row.style in ["Base","Cartoon"]:angles=[25,0,90,180,270]
  for angle in angles:
   item.rotation.y=deg_to_rad(angle)
   for f in 2:await process_frame
   await RenderingServer.frame_post_draw
   var suffix="" if angle==25 else "_view"+str(angle)
   assert(root.get_texture().get_image().save_png(output+"/"+stem+suffix+".png")==OK)
  report[row.file]={"sha256":FileAccess.get_sha256(path),"voxels":shape.count,"colors":indices.size(),"mesh_bounds":str(bounds),"grounded":true,"dimensions_match":true,"runtime_VoxelShape":"pass","runtime_VoxelModel_shader":"unsupported: occupied extent exceeds 62" if oversize else "rendered","preview_path":"imported mesh" if oversize else "VoxelModel shader","materials":"opaque diffuse","level_registration":"not performed"}
  item.queue_free();await process_frame
 var file=FileAccess.open(workspace+"/output/props/godot-validation.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
 print("PROPS_RUNTIME_QA_PASS ",report.size());quit()
