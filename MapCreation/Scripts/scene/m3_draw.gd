extends SceneTree
## Looks at the map's scene as Godot draws it: how long it takes to load and to draw, the whole map
## at one pixel of the screen to a pixel of the pictures (to set beside AllSimple.png), and close views.
## Run from vcom/, in a window (headless cannot draw):
##   godot --path . --script m3_draw.gd -- <scene .tscn> <folder to write to> [x,y,w,h,scale,msaa,name ...]
## A view is a part of the pictures in their own pixels, drawn [scale] screen pixels to the pixel.

const UNITS := 3.35


func _initialize() -> void:
	_run()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var scene_path: String = args[0]
	var dir: String = args[1]
	await process_frame
	var start := Time.get_ticks_usec()
	var packed: PackedScene = ResourceLoader.load(scene_path, "", ResourceLoader.CACHE_MODE_IGNORE)
	var loaded := (Time.get_ticks_usec() - start) / 1000.0
	start = Time.get_ticks_usec()
	var map := packed.instantiate()
	var made := (Time.get_ticks_usec() - start) / 1000.0
	var view := SubViewport.new()
	view.size = Vector2i(3100, 4000)
	view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	view.disable_3d = true
	root.add_child(view)
	var camera := Camera2D.new()
	camera.position = Vector2(3100, 4000) * UNITS * 0.5
	camera.zoom = Vector2.ONE / UNITS
	start = Time.get_ticks_usec()
	view.add_child(map)
	view.add_child(camera)
	camera.make_current()
	await process_frame
	await RenderingServer.frame_post_draw
	var first := (Time.get_ticks_usec() - start) / 1000.0
	var later := 0.0
	for i in 20:
		start = Time.get_ticks_usec()
		await process_frame
		await RenderingServer.frame_post_draw
		later += (Time.get_ticks_usec() - start) / 1000.0 / 20.0
	print("loaded in ", snappedf(loaded, 0.1), " ms; made into nodes in ", snappedf(made, 0.1), " ms; first frame ", snappedf(first, 0.1), " ms; a frame after that ", snappedf(later, 0.01), " ms (the whole map on a 3100 x 4000 view)")
	print("nodes in the scene: ", _count(map))
	view.get_texture().get_image().save_png(dir + "/render_full.png")
	print("wrote render_full.png")
	for i in range(2, args.size()):
		var parts := args[i].split(",")
		var x := float(parts[0]); var y := float(parts[1]); var w := float(parts[2]); var h := float(parts[3])
		var scale := float(parts[4])
		view.size = Vector2i(int(w * scale), int(h * scale))
		view.msaa_2d = Viewport.MSAA_4X if parts[5] == "1" else Viewport.MSAA_DISABLED
		camera.position = Vector2(x + w * 0.5, y + h * 0.5) * UNITS
		camera.zoom = Vector2.ONE * scale / UNITS
		for j in 3:
			await process_frame
		await RenderingServer.frame_post_draw
		view.get_texture().get_image().save_png(dir + "/" + parts[6] + ".png")
		print("wrote ", parts[6], ".png ", view.size)
	quit()


func _count(node: Node) -> int:
	var count := 1
	for child in node.get_children():
		count += _count(child)
	return count
