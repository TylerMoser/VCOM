extends SceneTree
const Reader=preload("res://addons/MagicaVoxel_Importer_with_Extensions/VoxImporter/vox-importer-common.gd")
func _initialize():call_deferred("run")
func run():
 root.size=Vector2i(480,560);root.msaa_3d=Viewport.MSAA_4X
 var scene=Node3D.new();root.add_child(scene)
 var tree=MeshInstance3D.new();scene.add_child(tree)
 var floor_node=MeshInstance3D.new();var plane=PlaneMesh.new();plane.size=Vector2(100,100);floor_node.mesh=plane;floor_node.position.y=-.01
 var mat=StandardMaterial3D.new();mat.albedo_color=Color("b4bfa7");floor_node.material_override=mat;scene.add_child(floor_node)
 var world=WorldEnvironment.new();var env=Environment.new();env.background_mode=Environment.BG_COLOR;env.background_color=Color("d9e0d0");env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color.WHITE;env.ambient_light_energy=.25;world.environment=env;scene.add_child(world)
 var sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-52,-35,0);sun.light_energy=.45;sun.shadow_enabled=true;scene.add_child(sun)
 var camera=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;scene.add_child(camera)
 var manifest=JSON.parse_string(FileAccess.get_file_as_string("res://../tent/manifest.json"))
 var report={}
 for row in manifest.models:
  var filename=row.file;var path=ProjectSettings.globalize_path("res://../"+filename)
  var reader=Reader.new();var raw=reader.read_vox_data(path);assert(raw.error==OK)
  var frames=reader.unify_voxels(raw.vox,false);var count=frames[frames.keys().min()].size()
  assert(count==int(row.voxels));assert(count==raw.vox.models[0].voxels.size())
  var meshes=Reader.new().import(path,"",{"Scale":.0625,"GreedyMeshGenerator":true,"SnapToGround":false,"FirstKeyframeOnly":true},[],[])
  assert(meshes is Array and meshes.size()==1);tree.mesh=meshes[0]
  var height=float(row.canvas[2])/16.0
  camera.size=max(height*1.35,float(row.canvas[0])/16.0*1.5)
  camera.position=Vector3(0,height*.35+9,9);camera.look_at(Vector3(0,height*.35,0))
  var bounds=tree.mesh.get_aabb();assert(abs(bounds.position.y)<.001)
  var indices={}
  for p in raw.vox.models[0].voxels:indices[raw.vox.models[0].voxels[p]]=true
  if "TwoColor" in filename:assert(indices.size()==2)
  report[filename]={"voxels":count,"palette_indices_used":indices.size(),"mesh_bounds":str(bounds),"surfaces":tree.mesh.get_surface_count(),"grounded":true,"reader_import":"pass","gameplay":"not_run"}
  var angles=[25]
  if row.style in ["Base","Cartoon"]:angles=[25,0,90,180,270]
  for angle in angles:
   tree.rotation.y=deg_to_rad(angle)
   for f in 3:await process_frame
   await RenderingServer.frame_post_draw
   var suffix="" if angle==25 else "_view"+str(angle)
   assert(root.get_texture().get_image().save_png("res://../tent/previews/"+filename.trim_suffix(".vox")+suffix+".png")==OK)
 var file=FileAccess.open("res://../tent/godot-validation.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
 print("PIXELWOOD_TENT_QA_PASS: ",report.size()," complete models imported and rendered")
 quit()
