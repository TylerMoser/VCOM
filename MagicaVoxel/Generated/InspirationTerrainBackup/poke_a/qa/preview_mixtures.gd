extends SceneTree
const Reader=preload("res://addons/MagicaVoxel_Importer_with_Extensions/VoxImporter/vox-importer-common.gd")
func _initialize():call_deferred("run")
func run():
 root.size=Vector2i(600,700);root.msaa_3d=Viewport.MSAA_4X
 var scene=Node3D.new();root.add_child(scene)
 var tree=MeshInstance3D.new();scene.add_child(tree);tree.rotation.y=deg_to_rad(25)
 var floor_node=MeshInstance3D.new();var plane=PlaneMesh.new();plane.size=Vector2(100,100);floor_node.mesh=plane;floor_node.position.y=-.01
 var mat=StandardMaterial3D.new();mat.albedo_color=Color("b4bfa7");floor_node.material_override=mat;scene.add_child(floor_node)
 var world=WorldEnvironment.new();var env=Environment.new();env.background_mode=Environment.BG_COLOR;env.background_color=Color("d9e0d0");env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color.WHITE;env.ambient_light_energy=.25;world.environment=env;scene.add_child(world)
 var sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-52,-35,0);sun.light_energy=.45;sun.shadow_enabled=true;scene.add_child(sun)
 var camera=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;scene.add_child(camera)
 var report={}
 for base in ["PokeA_ForestTree_Large","PokeA_ForestTree","PokeA_Sapling"]:
  var height=4.0 if base.ends_with("Large") else (1.75 if base.ends_with("ForestTree") else .9375)
  camera.size=height*1.35;camera.position=Vector3(0,height*.48+4,9);camera.look_at(Vector3(0,height*.48,0))
  for suffix in ["_Cartoon_TwoColor","_CratePalette_TwoColor","_Cartoon_CratePalette_TwoColor"]:
   var filename=base+suffix+".vox";var path=ProjectSettings.globalize_path("res://../"+filename)
   var reader=Reader.new();var raw=reader.read_vox_data(path);assert(raw.error==OK)
   var frames=reader.unify_voxels(raw.vox,false);var count=frames[frames.keys().min()].size()
   assert(count==raw.vox.models[0].voxels.size())
   var meshes=Reader.new().import(path,"",{"Scale":.0625,"GreedyMeshGenerator":true,"SnapToGround":false,"FirstKeyframeOnly":true},[],[])
   assert(meshes is Array and meshes.size()==1);tree.mesh=meshes[0]
   var indices={}
   for p in raw.vox.models[0].voxels:indices[raw.vox.models[0].voxels[p]]=true
   assert(indices.size()==2)
   report[filename]={"voxels":count,"palette_indices_used":indices.size(),"mesh_bounds":str(tree.mesh.get_aabb()),"surfaces":tree.mesh.get_surface_count()}
   for f in 4:await process_frame
   await RenderingServer.frame_post_draw
   assert(root.get_texture().get_image().save_png("res://../previews/"+base+suffix+".png")==OK)
 var file=FileAccess.open("res://../mixtures-godot-validation.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
 print("MIXTURES_QA_PASS: nine complete two-color models")
 quit()
