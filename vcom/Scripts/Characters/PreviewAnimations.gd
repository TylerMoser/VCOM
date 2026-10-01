## Renders frames of the figure's animations to images, to look at a pose or
## a cycle without running the game: the way to check an animation after
## changing it and baking. Run from vcom/, in a window (a --headless run cannot
## render):
##
##   godot --path . --script res://Scripts/Characters/PreviewAnimations.gd --resolution 360x400 -- <clip> [<clip> ...]
##       [--frames 6] [--view three_quarter|side|front|back|top] [--out <folder>] [--scene <figure scene>]
##
## A clip that is a whole pose (a base pose, a run, an act, the hop and the
## fall) is shown exactly as baked, through the figure's [AnimationPlayer]. A
## reaction, which is a change added on to whatever the body is doing, is
## shown as the game plays it, through the figure's [AnimationTree], added on
## to a pose: the aim for [code]fire_rifle[/code], standing for the rest. The
## figure holds what the clip's stance holds: the rifle for a clip whose name
## has [code]rifle[/code] in it (and for the hop, the fall and the reactions),
## the sword for [code]melee[/code] and [code]sword[/code] ones, and a grenade
## in the left hand for throws.
##
## A clip's frames are spread evenly over it, the last on its end for a clip
## played once. They are saved as [code]<clip>_NN.png[/code] in the out folder
## (default [code]user://animation_preview[/code]; the run prints where that is),
## and all of them together as [code]sheet.png[/code], a row per clip in the
## order given. Ground lines are one cell apart, so a stride or a lunge can be
## read off them.
##
## A script error does not end a --script run: Godot sits idle after it, so
## give the run a timeout when scripting it.
extends SceneTree

const HumanoidAnimations := preload("res://Scripts/Characters/HumanoidAnimations.gd")
const RIFLE := preload("res://Resources/Rifle.tres")
const SWORD := preload("res://Resources/Items/Shortsword.tres")
const GRENADE := preload("res://Resources/Items/FragGrenade.tres")

const DEFAULT_SCENE := "res://Scenes/BaseCharacter.tscn"
const DEFAULT_OUT := "user://animation_preview"
## Seconds the tree is run in a pose before a clip's frames are taken, so the
## cross-fade into it is over.
const SETTLE := 0.6
## Where the camera looks from for each view, and at.
const VIEWS := {
	"three_quarter": Vector3(3.0, 1.9, 3.4),
	"side": Vector3(4.6, 0.95, 0.2),
	"front": Vector3(0.0, 1.0, 4.6),
	"back": Vector3(0.0, 1.4, -4.6),
	"top": Vector3(0.01, 5.0, 0.0),
}
const LOOK_AT := Vector3(0.0, 0.8, 0.0)

var _model: Node3D
var _tree: AnimationTree


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var clips: Array[String] = []
	var frames := 6
	var view := "three_quarter"
	var out := DEFAULT_OUT
	var scene_path := DEFAULT_SCENE
	var index := 0
	while index < args.size():
		match args[index]:
			"--frames":
				index += 1
				frames = maxi(int(args[index]), 1)
			"--view":
				index += 1
				view = args[index]
			"--out":
				index += 1
				out = args[index]
			"--scene":
				index += 1
				scene_path = args[index]
			_:
				clips.append(args[index])
		index += 1
	if clips.is_empty():
		push_error("PreviewAnimations: name at least one clip, e.g. -- stand_rifle run_rifle.")
		quit(1)
		return
	if not VIEWS.has(view):
		push_error("PreviewAnimations: no view '%s'; use one of %s." % [view, VIEWS.keys()])
		quit(1)
		return
	var folder := ProjectSettings.globalize_path(out)
	DirAccess.make_dir_recursive_absolute(folder)
	_build_stage(view)
	_model = (load(scene_path) as PackedScene).instantiate()
	root.add_child(_model)
	await process_frame
	_tree = _model.get_node(^"AnimationTree")
	_tree.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	# The figure's own script would drive the tree from its unit; there is none.
	_model.set_process(false)

	var rows: Array = []
	for clip in clips:
		var animation := _tree.get_animation(clip)
		if animation == null:
			push_error("PreviewAnimations: no clip '%s' in '%s'." % [clip, scene_path])
			continue
		_dress(clip)
		var shots: Array[Image] = []
		for time in _times(animation, frames):
			await _show(clip, time)
			var image := root.get_viewport().get_texture().get_image()
			image.save_png(folder.path_join("%s_%02d.png" % [clip, shots.size()]))
			shots.append(image)
		rows.append(shots)
		print("PreviewAnimations: %s, %.2f s, %d frames" % [clip, animation.length, shots.size()])
	if not rows.is_empty():
		_sheet(rows).save_png(folder.path_join("sheet.png"))
		print("PreviewAnimations: frames and sheet.png in %s" % folder)
	quit()


## The times to take frames of [param animation] at: spread over a loop, and
## from start to end for a clip played once.
func _times(animation: Animation, frames: int) -> Array[float]:
	var times: Array[float] = []
	var once := animation.loop_mode == Animation.LOOP_NONE
	for frame in frames:
		var share := float(frame) / maxf(frames - 1, 1) if once else float(frame) / frames
		times.append(animation.length * share)
	return times


## Shows [param clip] [param time] seconds in and waits for the frame to be
## drawn: a reaction added on to a pose through the tree, anything else
## straight from the player.
func _show(clip: String, time: float) -> void:
	var player: AnimationPlayer = _model.get_node(^"AnimationPlayer")
	if clip in HumanoidAnimations.REACTS:
		player.stop()
		_tree.active = true
		for blend: StringName in [&"move", &"hop", &"air"]:
			_tree.set(StringName("parameters/%s/blend_amount" % blend), 0.0)
		_tree.set(&"parameters/stance/transition_request", "aim_rifle" if clip == "fire_rifle" else "stand_rifle")
		_tree.set(&"parameters/react/request", AnimationNodeOneShot.ONE_SHOT_REQUEST_ABORT)
		_tree.advance(SETTLE)
		_tree.set(&"parameters/react_pick/transition_request", clip)
		_tree.set(&"parameters/react/request", AnimationNodeOneShot.ONE_SHOT_REQUEST_FIRE)
		_tree.advance(0.0)
		_tree.advance(time)
	else:
		_tree.active = false
		player.play(clip)
		player.seek(time, true)
		player.pause()
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw


## Gives the figure what [param clip]'s stance holds.
func _dress(clip: String) -> void:
	var gun: Item = RIFLE if clip.contains("rifle") or clip in ["hop", "fall", "land", "hit_front", "hit_back", "dodge"] else null
	# The draw and stow show the sword throughout: a rifleman's gun only goes
	# on his back at the clip's swap, which the game does, not the clip.
	var melee: Item = SWORD if clip.contains("melee") or clip.contains("sword") else null
	var grenades: Array[Item] = []
	if clip.contains("throw"):
		grenades.append(GRENADE)
	_model.call(&"stand_easy")
	_model.call(&"equip", gun, melee, grenades)
	if clip.contains("throw"):
		_model.call(&"ready_throw")


## A floor, a light and a camera on [param view], the figure at the middle.
func _build_stage(view: String) -> void:
	var world := Node3D.new()
	root.add_child(world)
	var environment := WorldEnvironment.new()
	environment.environment = Environment.new()
	environment.environment.background_mode = Environment.BG_COLOR
	environment.environment.background_color = Color(0.45, 0.6, 0.75)
	environment.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.environment.ambient_light_color = Color.WHITE
	environment.environment.ambient_light_energy = 0.55
	world.add_child(environment)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55.0, -35.0, 0.0)
	sun.shadow_enabled = true
	world.add_child(sun)
	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(8.0, 8.0)
	ground.mesh = plane
	var grass := StandardMaterial3D.new()
	grass.albedo_color = Color(0.42, 0.62, 0.36)
	ground.material_override = grass
	world.add_child(ground)
	var line_color := StandardMaterial3D.new()
	line_color.albedo_color = Color(0.3, 0.45, 0.28)
	for offset in range(-3, 4):
		for across in 2:
			var line := MeshInstance3D.new()
			var box := BoxMesh.new()
			box.size = Vector3(8.0, 0.004, 0.01) if across == 0 else Vector3(0.01, 0.004, 8.0)
			line.mesh = box
			line.material_override = line_color
			line.position = Vector3(0.0, 0.002, offset + 0.5) if across == 0 else Vector3(offset + 0.5, 0.002, 0.0)
			world.add_child(line)
	var camera := Camera3D.new()
	camera.fov = 32.0
	world.add_child(camera)
	camera.transform = Transform3D(Basis.IDENTITY, VIEWS[view]).looking_at(LOOK_AT if view != "top" else Vector3(0.0, 0.7, 0.0))


## Every frame in [param rows], a row of images per clip, in one image.
func _sheet(rows: Array) -> Image:
	var size: Vector2i = (rows[0][0] as Image).get_size()
	var columns := 0
	for row: Array in rows:
		columns = maxi(columns, row.size())
	var sheet := Image.create(size.x * columns, size.y * rows.size(), false, Image.FORMAT_RGBA8)
	sheet.fill(Color(0.12, 0.12, 0.12))
	for row_index in rows.size():
		var row: Array = rows[row_index]
		for column in row.size():
			var image: Image = row[column]
			image.convert(Image.FORMAT_RGBA8)
			sheet.blit_rect(image, Rect2i(Vector2i.ZERO, size), Vector2i(column * size.x, row_index * size.y))
	return sheet
