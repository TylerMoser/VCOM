## Builds the two labelled comparison sheets from LedgeProbe's frames, cropped
## to the ledges. Needs a window (not --headless); render.sh runs it:
## godot --path . --resolution 1620x1000 --script LedgeSheet.gd -- --dir=C:/.../out/ledges
extends SceneTree

var _dir := ""


func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--dir="):
			_dir = arg.get_slice("=", 1)
	_run.call_deferred()


func _run() -> void:
	# The project stretches the UI from 1280x720; draw the sheets pixel for pixel.
	root.content_scale_mode = Window.CONTENT_SCALE_MODE_DISABLED
	root.content_scale_factor = 1.0
	var r0 := Rect2i(440, 130, 520, 430)
	await _sheet("sheet-view0.png", 3, 1.0, [
		["05 as applied", "t0-view0.png", r0],
		["Height tint (grass only)", "t1-view0.png", r0],
		["Edge highlights (23)", "t2-view0.png", r0],
		["Ink outlines (21)", "t3-view0.png", r0],
		["Height haze (12)", "t4-view0.png", r0],
		["Height tint + edge highlights", "t5-view0.png", r0],
	])
	var r1 := Rect2i(690, 320, 520, 380)
	await _sheet("sheet-view1.png", 3, 1.0, [
		["05 as applied", "t0-view1.png", r1],
		["Height tint (grass only)", "t1-view1.png", r1],
		["Edge highlights (23)", "t2-view1.png", r1],
		["Ink outlines (21)", "t3-view1.png", r1],
		["Height haze (12)", "t4-view1.png", r1],
		["Height tint + edge highlights", "t5-view1.png", r1],
	])
	quit()


func _sheet(out_name: String, columns: int, scale: float, cells: Array) -> void:
	var panel := PanelContainer.new()
	var bg := StyleBoxFlat.new()
	bg.bg_color = Color(0.06, 0.07, 0.09)
	bg.set_content_margin_all(10)
	panel.add_theme_stylebox_override(&"panel", bg)
	var grid := GridContainer.new()
	grid.columns = columns
	grid.add_theme_constant_override(&"h_separation", 10)
	grid.add_theme_constant_override(&"v_separation", 10)
	panel.add_child(grid)
	for cell: Array in cells:
		var image := Image.load_from_file("%s/%s" % [_dir, cell[1]])
		var region: Rect2i = cell[2]
		image = image.get_region(region)
		image.resize(int(region.size.x * scale), int(region.size.y * scale), Image.INTERPOLATE_NEAREST)
		var box := VBoxContainer.new()
		var label := Label.new()
		label.text = cell[0]
		label.add_theme_font_size_override(&"font_size", 20)
		label.add_theme_color_override(&"font_color", Color(0.95, 0.95, 0.9))
		box.add_child(label)
		var picture := TextureRect.new()
		picture.texture = ImageTexture.create_from_image(image)
		box.add_child(picture)
		grid.add_child(box)
	root.add_child(panel)
	for i in 4:
		await process_frame
	await RenderingServer.frame_post_draw
	var size := Vector2i(panel.size)
	var shot := root.get_texture().get_image().get_region(Rect2i(Vector2i.ZERO, size))
	shot.save_png("%s/%s" % [_dir, out_name])
	print("Sheet: saved %s %s" % [out_name, size])
	panel.queue_free()
	await process_frame
