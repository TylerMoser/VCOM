## Renders one visual variant of CombatMap as a two-panel screenshot.
##
## Left panel: the game exactly as it starts (authored camera, HUD, move range).
## Right panel: a closer in-game angle with overlays and HUD hidden, so the
## terrain itself can be judged.
##
## Run: godot --path . --resolution 1280x720 --fixed-fps 60 res://_probe/VisualProbe.tscn -- --variant=N --out=C:/path/file.png
extends Node

const Variants := preload("res://_probe/Variants.gd")
const MAP_SCENE := "res://Scenes/CombatMap.tscn"

const SETTLE_FRAMES_A := 150
const SETTLE_FRAMES_B := 90

## Close view: pivot, yaw (deg), pitch (deg below horizontal), distance.
var cam_b_pivot := Vector3(9.0, 1.0, -8.0)
var cam_b_yaw := 38.0
var cam_b_pitch := 36.0
var cam_b_distance := 15.0

var _variant_id := 0
var _out := ""
var _out_dir := ""
var _only := ""


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--variant="):
			_variant_id = int(arg.get_slice("=", 1))
		elif arg.begins_with("--out="):
			_out = arg.get_slice("=", 1)
		elif arg.begins_with("--outdir="):
			_out_dir = arg.get_slice("=", 1)
		elif arg.begins_with("--only="):
			_only = arg.get_slice("=", 1)
		elif arg.begins_with("--camb="):
			var f := arg.get_slice("=", 1).split_floats(",")
			cam_b_pivot = Vector3(f[0], f[1], f[2])
			cam_b_yaw = f[3]
			cam_b_pitch = f[4]
			cam_b_distance = f[5]

	var variant: Dictionary = Variants.get_variant(_variant_id)
	if variant.is_empty():
		push_error("VisualProbe: no variant %d" % _variant_id)
		get_tree().quit(1)
		return
	if _out_dir != "":
		_out = "%s/%02d-%s.png" % [_out_dir, _variant_id, Variants.slug(variant.get("name", ""))]

	var map := (load(MAP_SCENE) as PackedScene).instantiate()
	add_child(map)

	# Keep a stray cursor over the window from edge-panning the camera.
	var rig := map.get_node(^"CameraRig")
	rig.set("edge_pan_enabled", false)
	rig.set_process_unhandled_input(false)

	Variants.apply(variant, map, get_viewport())
	print("VisualProbe: variant %d '%s' applied" % [_variant_id, variant.get("name", "")])

	var image_a: Image = null
	if _only != "b":
		image_a = await _capture(SETTLE_FRAMES_A)
	else:
		await _frames(30)

	var image_b: Image = null
	if _only != "a":
		(map.get_node(^"TileHighlights") as Node3D).visible = false
		(map.get_node(^"HUD") as CanvasLayer).visible = false
		var extra := map.get_node_or_null(^"ProbeCanvas") as CanvasLayer
		if extra != null:
			extra.visible = true
		var cam := Camera3D.new()
		var rig_cam := map.get_node(^"CameraRig/Camera3D") as Camera3D
		cam.fov = rig_cam.fov
		cam.attributes = rig_cam.attributes
		map.add_child(cam)
		Variants.apply_view_b(variant, map)
		if variant.has("fov"):
			# Keep the close view's framing when the lens changes.
			cam_b_distance *= tan(deg_to_rad(75.0) * 0.5) / tan(deg_to_rad(float(variant["fov"])) * 0.5)
			cam.far = 4000.0
		var yaw := deg_to_rad(cam_b_yaw)
		var pitch := deg_to_rad(cam_b_pitch)
		var offset := Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch)) * cam_b_distance
		cam.look_at_from_position(cam_b_pivot + offset, cam_b_pivot, Vector3.UP)
		cam.make_current()
		_add_caption("%02d  %s" % [_variant_id, variant.get("name", "")])
		image_b = await _capture(SETTLE_FRAMES_B)

	var out_image: Image
	if image_a != null and image_b != null:
		var w := image_a.get_width()
		var h := image_a.get_height()
		var gap := 6
		out_image = Image.create(w * 2 + gap, h, false, image_a.get_format())
		out_image.fill(Color(0.02, 0.02, 0.03))
		out_image.blit_rect(image_a, Rect2i(0, 0, w, h), Vector2i(0, 0))
		out_image.blit_rect(image_b, Rect2i(0, 0, w, h), Vector2i(w + gap, 0))
	else:
		out_image = image_a if image_a != null else image_b

	var err := out_image.save_png(_out)
	print("VisualProbe: saved %s (%dx%d) err=%d" % [_out, out_image.get_width(), out_image.get_height(), err])
	get_tree().quit()


func _frames(count: int) -> void:
	for i in count:
		await get_tree().process_frame


func _capture(settle: int) -> Image:
	await _frames(settle)
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	image.convert(Image.FORMAT_RGB8)
	return image


func _add_caption(text: String) -> void:
	var layer := CanvasLayer.new()
	layer.layer = 100
	add_child(layer)
	var panel := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.05, 0.06, 0.09, 0.78)
	style.content_margin_left = 14
	style.content_margin_right = 14
	style.content_margin_top = 6
	style.content_margin_bottom = 6
	style.corner_radius_bottom_right = 6
	panel.add_theme_stylebox_override(&"panel", style)
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override(&"font_size", 22)
	label.add_theme_color_override(&"font_color", Color(0.96, 0.96, 0.92))
	panel.add_child(label)
	layer.add_child(panel)
