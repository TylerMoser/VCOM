extends SceneTree
const Reader=preload("res://addons/MagicaVoxel_Importer_with_Extensions/VoxImporter/vox-importer-common.gd")
func _initialize():call_deferred("run")
func run():
 var workspace: String=OS.get_cmdline_user_args()[0]
 var assembly_only=OS.get_cmdline_user_args().has("assembly-only")
 var corners_only=OS.get_cmdline_user_args().has("corners-only")
 var base=workspace+"/output/poke_s/ruins/"
 var manifest=JSON.parse_string(FileAccess.get_file_as_string(base+"manifest.json"))
 root.size=Vector2i(480,480);root.msaa_3d=Viewport.MSAA_4X
 var scene=Node3D.new();root.add_child(scene)
 var floor_node=MeshInstance3D.new();var plane=PlaneMesh.new();plane.size=Vector2(100,100);floor_node.mesh=plane;floor_node.position.y=-.02
 var mat=StandardMaterial3D.new();mat.albedo_color=Color("899081");floor_node.material_override=mat;scene.add_child(floor_node)
 var world=WorldEnvironment.new();var env=Environment.new();env.background_mode=Environment.BG_COLOR;env.background_color=Color("d9dfd4");env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color.WHITE;env.ambient_light_energy=.18;world.environment=env;scene.add_child(world)
 var sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-48,-35,0);sun.shadow_enabled=true;sun.light_energy=.35;scene.add_child(sun)
 var camera=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;scene.add_child(camera)
 var report={}
 if corners_only:report=JSON.parse_string(FileAccess.get_file_as_string(base+"godot-validation.json"))
 DirAccess.make_dir_recursive_absolute(base+"previews")
 for row in manifest.models:
  if assembly_only:break
  if corners_only and not row.family.ends_with("TerraceCorner"):continue
  var path=workspace+"/"+row.file
  var reader=Reader.new()
  var data=reader.read_vox_data(path)
  assert(data.error==OK)
  var unified=reader.unify_voxels(data.vox,false)
  assert(unified.size()==1)
  var count=unified[unified.keys()[0]].size()
  assert(count==int(row.voxels))
  var meshes=Reader.new().import(path,"",{"Scale":.0625,"GreedyMeshGenerator":true,"SnapToGround":false,"FirstKeyframeOnly":true},[],[])
  assert(meshes is Array and meshes.size()==1)
  var mesh:Mesh=meshes[0]
  var bounds=mesh.get_aabb();assert(abs(bounds.position.y)<.001)
  var expected=Vector3(float(row.occupied_max[0])-float(row.occupied_min[0])+1,float(row.occupied_max[2])-float(row.occupied_min[2])+1,float(row.occupied_max[1])-float(row.occupied_min[1])+1)/16
  assert(bounds.size.distance_to(expected)<.001)
  var item=MeshInstance3D.new();item.mesh=mesh;scene.add_child(item)
  var height=float(row.canvas[2])/16
  camera.size=max(height*1.3,float(max(row.canvas[0],row.canvas[1]))/16*1.65)
  if row.family.ends_with("TerraceCorner"):camera.size*=1.3
  camera.position=Vector3(0,height*.4+12,18);camera.look_at(Vector3(0,height*.4,0))
  var stem=row.file.get_file().trim_suffix(".vox")
  var angles=[25]
  if row.style in ["Base","Cartoon"]:angles=[25,0,90,180,270]
  for angle in angles:
   item.rotation.y=deg_to_rad(angle)
   for f in 2:await process_frame
   await RenderingServer.frame_post_draw
   var suffix="" if angle==25 else "_view"+str(angle)
   assert(root.get_texture().get_image().save_png(base+"previews/"+stem+suffix+".png")==OK)
  report[row.file]={"sha256":FileAccess.get_sha256(path),"voxels":count,"mesh_bounds":str(bounds),"grounded":true,"dimensions_match":true,"whole_import":"pass","preview":"current VCOM imported Mesh","level_registration":"not performed"}
  item.queue_free();await process_frame
 if corners_only:
  var output=FileAccess.open(base+"godot-validation.json",FileAccess.WRITE);output.store_string(JSON.stringify(report,"\t"));output.close()
  print("RUINS_CORNER_PREVIEWS_PASS");quit();return
 # Whole architectural sections assembled at their documented voxel offsets.
 for placement in [["TempleCore",0],["TempleWing",-144],["TempleWing",144]]:
  var meshes=Reader.new().import(workspace+"/output/poke_s/PokeS_Ruins"+placement[0]+".vox","",{"Scale":.0625,"GreedyMeshGenerator":true,"SnapToGround":false,"FirstKeyframeOnly":true},[],[])
  var item=MeshInstance3D.new();item.mesh=meshes[0];item.position.x=float(placement[1])/16;scene.add_child(item)
  if int(placement[1])>0:item.scale.x=-1
 camera.size=31;camera.position=Vector3(15,23,32);camera.look_at(Vector3(0,3,0))
 for f in 3:await process_frame
 await RenderingServer.frame_post_draw
 assert(root.get_texture().get_image().save_png(base+"temple_assembly.png")==OK)
 if not assembly_only:
  var file=FileAccess.open(base+"godot-validation.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
 print("RUINS_IMPORT_QA_PASS ",report.size());quit()
