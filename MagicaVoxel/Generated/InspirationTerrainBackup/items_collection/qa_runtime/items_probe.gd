extends SceneTree
const Rig=preload("res://Scripts/Characters/VoxelRig.gd")
const Animations=preload("res://Scripts/Characters/HumanoidAnimations.gd")
func _initialize():call_deferred("run")
func run():
 var base=OS.get_cmdline_user_args()[0]+"/"
 var rows=JSON.parse_string(FileAccess.get_file_as_string(base+"render-list.json"))
 var layouts=JSON.parse_string(FileAccess.get_file_as_string(base+"layouts.json"))
 var report=[];var rig_report=[];var seen={}
 root.size=Vector2i(256,320);root.msaa_3d=Viewport.MSAA_4X
 var scene=Node3D.new();root.add_child(scene)
 var environment=WorldEnvironment.new();var env=Environment.new();env.background_mode=Environment.BG_COLOR;env.background_color=Color("26343e");env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color.WHITE;env.ambient_light_energy=.65;environment.environment=env;scene.add_child(environment)
 var sun=DirectionalLight3D.new();sun.rotation_degrees=Vector3(-45,-25,0);sun.light_energy=.8;scene.add_child(sun)
 var camera=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=2.7;scene.add_child(camera)
 camera.position=Vector3(1.7,1.8,4);camera.look_at(Vector3(0,.9,0))
 RenderingServer.global_shader_parameter_set("voxel_glow",.3)
 DirAccess.make_dir_recursive_absolute(base+"rig_previews")
 for row in rows:
  var shape=VoxelShape.read_model(row.path,0);assert(shape!=null,row.file)
  assert(shape.count==int(row.voxels),row.file)
  assert(shape.glass_count==int(row.glass_voxels),row.file)
  var model=VoxelModel.new(shape);var shown=model.show_on();assert(shown.mesh!=null,row.file)
  report.append({"file":row.file,"sha256":row.sha256,"count":shape.count,"glass_count":shape.glass_count,"runtime_mesh":true})
  shown.free()
  if row.form=="Fitted":
   var entry=layouts[row.file];var layout=Rig.CHARACTER_BIGGER.duplicate(true)
   var regions=[]
   for region in entry.regions:
    regions.append([StringName(region[0]),Vector3i(region[1][0],region[1][1],region[1][2]),Vector3i(region[2][0],region[2][1],region[2][2])])
   regions.append_array(layout.regions);layout.regions=regions
   var data=Rig.VoxImporter.new().read_vox_data(row.render_path)
   var lo=Vector3i(999,999,999);var hi=-lo
   for p in data.vox.models[0].voxels:lo=lo.min(Vector3i(p));hi=hi.max(Vector3i(p))
   var shift=Vector3(16.5-(lo.x+hi.x+1)*.5,0,(lo.y+hi.y+1)*.5-16.0)
   for b in layout.joints:layout.joints[b]+=shift
   var rig=Rig.new();assert(rig.load_vox(row.render_path,layout),row.file)
   var total=0
   for b in rig.cells:total+=rig.cells[b].size()
   assert(total==int(row.composite_voxels),row.file)
   for region in entry.regions:
    for x in range(int(region[1][0]),int(region[2][0])+1):
     assert(rig.cells[StringName(region[0])].has(Vector3i(x,region[1][2],-region[1][1])),row.file)
   var unit=Node3D.new();scene.add_child(unit)
   var skel=rig.make_skeleton();unit.add_child(skel)
   var body=MeshInstance3D.new();body.mesh=rig.make_mesh(skel);skel.add_child(body);body.skeleton=NodePath("..");body.skin=skel.create_skin_from_rest_transforms()
   assert(body.mesh.get_surface_count()>0,row.file)
   VoxelModel.new(rig.make_shape()).show_on(body,true)
   var animation_count=0;var rendered=false
   # Palette counterparts share geometry; animate all 228 distinct wearable designs.
   if row.style=="Base" and not seen.has(row.category+row.item+row.design):
    seen[row.category+row.item+row.design]=true
    var library=Animations.new(rig).make_library();animation_count=library.get_animation_list().size();assert(animation_count>=50)
    var player=AnimationPlayer.new();unit.add_child(player);player.add_animation_library("",library)
    for pose in ["stand_unarmed","run_unarmed","crouch_unarmed","strike_sword"]:
     player.play(pose);player.seek(.3,true);player.pause()
     for frame in 3:await process_frame
     await RenderingServer.frame_post_draw
     assert(root.get_texture().get_image().save_png(base+"rig_previews/"+row.category+"_"+row.item+"_"+row.design+"_"+pose+".png")==OK)
    rendered=true
   rig_report.append({"file":row.file,"sha256":row.sha256,"equipment_voxels_assigned":row.voxels,"composite_voxels":total,"skinned_mesh":true,"joint_shift":str(shift),"animations":animation_count,"rendered_poses":rendered})
   unit.queue_free();await process_frame
  if report.size()%100==0:print("RUNTIME_PROGRESS ",report.size(),"/",rows.size())
 var f=FileAccess.open(base+"runtime-validation.json",FileAccess.WRITE);f.store_string(JSON.stringify(report));f.close()
 f=FileAccess.open(base+"rig-validation.json",FileAccess.WRITE);f.store_string(JSON.stringify(rig_report));f.close()
 print("ITEM_RUNTIME_PASS ",report.size()," RIG_PASS ",rig_report.size()," ANIMATED_DESIGNS ",seen.size());quit()
