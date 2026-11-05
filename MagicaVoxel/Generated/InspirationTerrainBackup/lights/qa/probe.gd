extends SceneTree
const Reader=preload("res://addons/MagicaVoxel_Importer_with_Extensions/VoxImporter/vox-importer-common.gd")
func _initialize():call_deferred("run")
func run():
 var args=OS.get_cmdline_user_args()
 var workspace: String=args[0]
 var manifest=JSON.parse_string(FileAccess.get_file_as_string(workspace+"/output/lights/manifest.json"))
 root.size=Vector2i(360,440);root.msaa_3d=Viewport.MSAA_4X
 var scene=Node3D.new();root.add_child(scene)
 var floor_node=MeshInstance3D.new();var plane=PlaneMesh.new();plane.size=Vector2(100,100);floor_node.mesh=plane;floor_node.position.y=-.01
 var mat=StandardMaterial3D.new();mat.albedo_color=Color("899081");floor_node.material_override=mat;scene.add_child(floor_node)
 var world=WorldEnvironment.new();var env=Environment.new();env.background_mode=Environment.BG_COLOR;env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;world.environment=env;scene.add_child(world)
 var sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-48,-35,0);sun.shadow_enabled=true;scene.add_child(sun)
 var camera=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;scene.add_child(camera)
 var report={}
 for row in manifest.models:
  var path=workspace+"/"+row.file
  var meshes=Reader.new().import(path,"",{"Scale":.0625,"GreedyMeshGenerator":true,"SnapToGround":false,"FirstKeyframeOnly":true},[],[])
  assert(meshes is Array and meshes.size()==1)
  var mesh:Mesh=meshes[0];mesh.take_over_path(path)
  var shape=VoxelShape.read_mesh(mesh)
  assert(shape!=null and shape.count==int(row.voxels))
  var emit_count=0
  var indices={}
  for i in shape.voxels:
   if i!=0:indices[i]=true
   if VoxelShape.glows(shape.flags[i]):emit_count+=1
  assert(emit_count==int(row.emission_voxels))
  for i in indices:
   assert(VoxelShape.glows(shape.flags[i])==(i in PackedInt32Array(row.emission_indices)))
   if i in PackedInt32Array(row.emission_indices):
    assert(abs(shape.powers[i]-float(row.power))<.001)
    assert(abs(VoxelShape.glow_of(shape.flags[i])-23.0/31.0)<.001)
  assert(not VoxelShape.glows(shape.flags[255]))
  var bounds=mesh.get_aabb();assert(abs(bounds.position.y)<.001)
  var item=VoxelModel.new(shape).show_on();scene.add_child(item)
  # This harness supplies an omni to illustrate Power. Level registration is separate.
  var lamp=OmniLight3D.new();scene.add_child(lamp)
  var c=row.emitter_centroid
  lamp.position=Vector3((float(c[0])-float(row.canvas[0])/2)/16,float(c[2])/16,-(float(c[1])-float(row.canvas[1])/2)/16)
  var color=Color(0,0,0);var n=0
  for i in shape.voxels:
   if i!=0 and VoxelShape.glows(shape.flags[i]):color+=shape.colors[i];n+=1
  lamp.light_color=Color(color.r/n,color.g/n,color.b/n)
  lamp.omni_range=3.5*pow(2,float(row.power)-1);lamp.light_energy=pow(2,float(row.power));lamp.shadow_enabled=false
  var height=float(row.canvas[2])/16
  camera.size=max(height*1.3,float(row.canvas[0])/16*1.65)
  camera.position=Vector3(0,height*.44+4.5,9);camera.look_at(Vector3(0,height*.44,0))
  var output=workspace+"/"+row.file.get_base_dir()+"/lights/previews"
  DirAccess.make_dir_recursive_absolute(output)
  var stem=row.file.get_file().trim_suffix(".vox")
  var angles=[25]
  if row.style in ["Base","Cartoon"]:angles=[25,0,90,180,270]
  for angle in angles:
   item.rotation.y=deg_to_rad(angle)
   for night in [false,true] if angle==25 else [false]:
    RenderingServer.global_shader_parameter_set("voxel_glow",1.0 if night else 0.0)
    env.background_color=Color("131d2c") if night else Color("d9dfd4")
    env.ambient_light_color=Color("7182a0") if night else Color.WHITE
    env.ambient_light_energy=.25
    sun.light_energy=.18 if night else .45;sun.light_color=Color("9eb9ed") if night else Color.WHITE
    lamp.visible=night
    for f in 3:await process_frame
    await RenderingServer.frame_post_draw
    var suffix="_night" if night else ("" if angle==25 else "_view"+str(angle))
    assert(root.get_texture().get_image().save_png(output+"/"+stem+suffix+".png")==OK)
  report[row.file]={"voxels":shape.count,"emit_voxels":emit_count,"glow":23.0/31.0,"power":row.power,"mesh_bounds":str(bounds),"grounded":true,"runtime_VoxelShape":"pass","runtime_VoxelModel_shader":"rendered day/night","level_registration":"not performed","omni_preview":"harness light, no shadows"}
  item.queue_free();lamp.queue_free();await process_frame
 var file=FileAccess.open(workspace+"/output/lights/godot-validation.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
 print("LIGHTS_RUNTIME_QA_PASS ",report.size());quit()
