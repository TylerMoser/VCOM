extends SceneTree
const Reader = preload("res://addons/MagicaVoxel_Importer_with_Extensions/VoxImporter/vox-importer-common.gd")
func model_files():
 return ["PokeA_ForestTree.vox","PokeA_Sapling.vox"]
func output_prefix():return "complete_trees"
func _initialize():call_deferred("run")
func run():
 root.size=Vector2i(1000,850)
 var scene=Node3D.new();root.add_child(scene)
 var group=Node3D.new();scene.add_child(group)
 var report={};var height=0.0;var span=0.0
 for filename in model_files():
  var path=ProjectSettings.globalize_path("res://../"+filename)
  var reader=Reader.new();var raw=reader.read_vox_data(path)
  assert(raw.error==OK and raw.vox.models.size()==1)
  var frames=reader.unify_voxels(raw.vox,false)
  var count=frames[frames.keys().min()].size()
  assert(count==raw.vox.models[0].voxels.size())
  var meshes=Reader.new().import(path,"",{"Scale":.0625,"GreedyMeshGenerator":true,"SnapToGround":false,"FirstKeyframeOnly":true},[],[])
  assert(meshes is Array and meshes.size()>0)
  var node=MeshInstance3D.new();node.mesh=meshes[0];group.add_child(node)
  var box=node.mesh.get_aabb();node.position.x=span+box.size.x/2
  span+=box.size.x+.6;height=max(height,box.size.y)
  report[filename]={"voxels":count,"canvas":str(raw.vox.models[0].size),"mesh_bounds":str(box),"validation":"whole-model importer; no per-cell files or VoxelModel mesher"}
 group.position.x=-(span-.6)/2
 var plane=MeshInstance3D.new();var plane_mesh=PlaneMesh.new();plane_mesh.size=Vector2(100,100);plane.mesh=plane_mesh;plane.position.y=-.01
 var mat=StandardMaterial3D.new();mat.albedo_color=Color("b4bfa7");plane.material_override=mat;scene.add_child(plane)
 var we=WorldEnvironment.new();var env=Environment.new();env.background_mode=Environment.BG_COLOR;env.background_color=Color("d9e0d0");env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color.WHITE;env.ambient_light_energy=.25;we.environment=env;scene.add_child(we)
 var sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-52,-35,0);sun.light_energy=.45;sun.shadow_enabled=true;scene.add_child(sun)
 var camera=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=max(height*1.55,span*1.1);scene.add_child(camera)
 camera.position=Vector3(0,height*.5+4,9);camera.look_at(Vector3(0,height*.5,0));root.msaa_3d=Viewport.MSAA_4X
 for i in 4:
  for node in group.get_children():node.rotation.y=deg_to_rad(25+i*90)
  for f in 4:await process_frame
  await RenderingServer.frame_post_draw
  root.get_texture().get_image().save_png("res://../previews/%s_%d.png"%[output_prefix(),i])
 var file=FileAccess.open("res://../%s-validation.json"%output_prefix(),FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
 print("WHOLE_MODEL_QA_PASS")
 quit()
