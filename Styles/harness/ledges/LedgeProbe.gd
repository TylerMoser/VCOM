## Renders BoundaryMap, as the game currently looks, with one ledge-readability
## treatment on top, from the game's own camera facing both ways. See
## Styles/LEDGES.md. Run through Styles/harness/ledges/render.sh, which copies
## this into vcom/_probe/:
## godot --path . --resolution 1280x720 --fixed-fps 60 res://_probe/LedgeProbe.tscn -- --treatment=N --outdir=C:/x
##
## Treatments: 0 the game as it is, 1 height tint (grass only), 2 edge
## highlights (style 23's outline pass), 3 ink outlines (style 21's), 4 height
## haze (style 12's fog), 5 height tint + edge highlights.
extends Node

const Variants := preload("res://_probe/Variants.gd")

var _treatment := 0
var _out_dir := ""


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--treatment="):
			_treatment = int(arg.get_slice("=", 1))
		elif arg.begins_with("--outdir="):
			_out_dir = arg.get_slice("=", 1)

	var map := (load("res://Scenes/BoundaryMap.tscn") as PackedScene).instantiate()
	add_child(map)
	var rig := map.get_node(^"CameraRig")
	rig.set("edge_pan_enabled", false)
	rig.set_process_unhandled_input(false)
	(map.get_node(^"HUD") as CanvasLayer).visible = false
	(map.get_node(^"TileHighlights") as Node3D).visible = false

	var bevel := {"line_tint_mix": 1.0, "line_darken": 0.5, "line_opacity": 0.7, "crease_width": 2.0,
			"highlight_opacity": 0.7, "highlight_min_up": 0.5, "crease_opacity": 0.4}
	var ink := {"line_color": Color(0.10, 0.07, 0.14), "line_opacity": 0.9, "line_width": 1.0}
	var smaa := {"msaa_3d": Viewport.MSAA_DISABLED, "screen_space_aa": Viewport.SCREEN_SPACE_AA_SMAA}
	var name := ""
	match _treatment:
		0:
			name = "05 as applied"
		1:
			name = "Height tint (grass only)"
			_tint_grass(map)
		2:
			name = "Edge highlights (23)"
			Variants.apply({"viewport": smaa, "outline": bevel}, map, get_viewport())
		3:
			name = "Ink outlines (21)"
			Variants.apply({"viewport": smaa, "outline": ink}, map, get_viewport())
		4:
			name = "Height haze (12)"
			Variants.apply({"env": {"fog_enabled": true, "fog_mode": Environment.FOG_MODE_EXPONENTIAL,
					"fog_light_color": Color(0.64, 0.74, 0.87), "fog_density": 0.004, "fog_height": 1.0,
					"fog_height_density": 2.5, "fog_sky_affect": 0.0, "fog_aerial_perspective": 0.3,
					"fog_sun_scatter": 0.2}}, map, get_viewport())
		5:
			name = "Height tint + edge highlights"
			_tint_grass(map)
			Variants.apply({"viewport": smaa, "outline": bevel}, map, get_viewport())
	print("LedgeProbe: %d %s" % [_treatment, name])

	var views := [[Vector3(10.0, 1.0, -10.0), 45.0], [Vector3(14.0, 1.0, -16.0), 225.0]]
	for i in views.size():
		var view: Array = views[i]
		rig.set("_pivot", view[0])
		rig.set("_current_pivot", view[0])
		rig.set("_yaw", view[1])
		rig.set("_current_yaw", view[1])
		await _frames(150 if i == 0 else 90)
		await RenderingServer.frame_post_draw
		var image := get_viewport().get_texture().get_image()
		image.convert(Image.FORMAT_RGB8)
		image.save_png("%s/t%d-view%d.png" % [_out_dir, _treatment, i])
	get_tree().quit()


## Gives the grass block's mesh the height-tint shader.
func _tint_grass(map: Node) -> void:
	var lib := (map.get_node(^"GridMap") as GridMap).mesh_library
	var mat := ShaderMaterial.new()
	mat.shader = load("res://_probe/shaders/grass_height.gdshader")
	for id in lib.get_item_list():
		if lib.get_item_name(id) == "BrightGrass1":
			var mesh := lib.get_item_mesh(id)
			for s in mesh.get_surface_count():
				mesh.surface_set_material(s, mat)


func _frames(count: int) -> void:
	for i in count:
		await get_tree().process_frame
