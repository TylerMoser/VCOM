extends SceneTree
const Reader=preload("res://addons/MagicaVoxel_Importer_with_Extensions/VoxImporter/vox-importer-common.gd")
func _initialize():call_deferred("run")
func run():
 var args=OS.get_cmdline_user_args()
 var workspace: String=args[0]
 var base=workspace+"/output/codex_missed_vegetation/"
 var manifest=JSON.parse_string(FileAccess.get_file_as_string(base+"manifest.json"))
 root.size=Vector2i(560,420);root.msaa_3d=Viewport.MSAA_4X
 var scene=Node3D.new();root.add_child(scene)
 var floor_node=MeshInstance3D.new();var plane=PlaneMesh.new();plane.size=Vector2(100,100);floor_node.mesh=plane;floor_node.position.y=-.02
 var mat=StandardMaterial3D.new();mat.albedo_color=Color("899081");floor_node.material_override=mat;scene.add_child(floor_node)
 var world=WorldEnvironment.new();var env=Environment.new();env.background_mode=Environment.BG_COLOR;env.background_color=Color("d9dfd4");env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color.WHITE;env.ambient_light_energy=.18;world.environment=env;scene.add_child(world)
 var sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-48,-35,0);sun.shadow_enabled=true;sun.light_energy=.35;scene.add_child(sun)
 var camera=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;scene.add_child(camera)
 var report={}
 var signature=FileAccess.get_sha256(get_script().resource_path)
 if FileAccess.file_exists(base+"godot-validation.json"):report=JSON.parse_string(FileAccess.get_file_as_string(base+"godot-validation.json"))
 for row in manifest.models:
  if args.size()>1 and not row.family.contains(args[1]):continue
  var path=workspace+"/"+row.file
  if report.has(row.file) and report[row.file].sha256==row.sha256 and report[row.file].get("render_signature","")==signature:continue
  var reader=Reader.new();var data=reader.read_vox_data(path);assert(data.error==OK)
  assert(data.vox.models.size()==int(row.scene_models))
  var unified=reader.unify_voxels(data.vox,false);assert(unified.size()==1)
  var points=unified[unified.keys()[0]];assert(points.size()==int(row.voxels))
  if int(row.scene_models)>1:
   var expected=FileAccess.get_file_as_bytes(base+"qa/expected/"+row.file.get_file().trim_suffix(".vox")+".bin")
   var lx=int(row.canvas[0]);var dy=int(row.canvas[1]);var hz=int(row.canvas[2]);assert(expected.size()==lx*dy*hz)
   for p in points:
    var x=int(p.x)+lx/2;var y=int(p.y)+dy/2;var z=int(p.z)
    assert(x>=0 and x<lx and y>=0 and y<dy and z>=0 and z<hz)
    assert(expected[(x*dy+y)*hz+z]==int(points[p])+1)
  var meshes=Reader.new().import(path,"",{"Scale":.0625,"GreedyMeshGenerator":true,"SnapToGround":false,"FirstKeyframeOnly":true},[],[])
  assert(meshes is Array and meshes.size()==1)
  var mesh:Mesh=meshes[0];var bounds=mesh.get_aabb();assert(abs(bounds.position.y)<.001)
  var extent=Vector3(float(row.occupied_max[0])-float(row.occupied_min[0])+1,float(row.occupied_max[2])-float(row.occupied_min[2])+1,float(row.occupied_max[1])-float(row.occupied_min[1])+1)/16
  assert(bounds.size.distance_to(extent)<.001)
  var item=MeshInstance3D.new();item.mesh=mesh;scene.add_child(item)
  var height=float(row.canvas[2])/16;var length=float(row.canvas[0])/16
  camera.size=max(height*1.7,float(max(row.canvas[0],row.canvas[1]))/16*1.1)
  var target=Vector3(0,bounds.size.y*.45,0)
  camera.position=target+Vector3(0,10,16);camera.look_at(target)
  var folder=workspace+"/"+row.file.get_base_dir()+"/codex_missed_vegetation/previews/";DirAccess.make_dir_recursive_absolute(folder)
  var stem=row.file.get_file().trim_suffix(".vox")
  var angles=[25]
  if row.style in ["Base","Cartoon"]:angles=[25,0,90,180,270]
  for angle in angles:
   item.rotation.y=deg_to_rad(angle)
   for frame in 2:await process_frame
   await RenderingServer.frame_post_draw
   var suffix="" if angle==25 else "_view"+str(angle)
   assert(root.get_texture().get_image().save_png(folder+stem+suffix+".png")==OK)
  if row.style in ["Base","Cartoon"]:
   item.rotation.y=deg_to_rad(25);floor_node.visible=false;camera.position=target+Vector3(0,-7,13);camera.look_at(target)
   for frame in 2:await process_frame
   await RenderingServer.frame_post_draw
   assert(root.get_texture().get_image().save_png(folder+stem+"_underside.png")==OK)
   floor_node.visible=true;camera.position=target+Vector3(0,10,16);camera.look_at(target)
  report[row.file]={"sha256":row.sha256,"render_signature":signature,"voxels":points.size(),"scene_models":int(row.scene_models),"grounded":true,"dimensions_match":true,"mesh_bounds":str(bounds),"multi_model_coordinates_and_colors":"exact" if int(row.scene_models)>1 else "single model; count and bounds checked","whole_import":"pass","preview":"current VCOM imported Mesh","combat_integration":"not performed"}
  var file=FileAccess.open(base+"godot-validation.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
  item.queue_free();await process_frame
 print("MISSED_VEGETATION_IMPORT_QA_PASS ",report.size());quit()
