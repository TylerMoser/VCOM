## Renders the new map (Scenes/Map.tscn) with one map style applied, at the
## standard views, and saves them side by side as one picture (NN-slug.png).
##
## Run it through MapStyles/harness/render.sh, which copies this folder into
## vcom/_probe/ for the run and deletes it afterwards. It needs a window:
## --headless cannot draw.
##
##   godot --path . --resolution 1280x720 --fixed-fps 60 res://_probe/MapStyleProbe.tscn \
##       -- --style=7 --outdir=C:/.../MapStyles [--data=C:/.../harness/data] [--filter=deutan]
##       [--views=B,C] [--panels] [--tag=suffix] [--timing=120] [--map=res://_probe/before/Map.tscn]
##
## --map renders another copy of the map than the scene's own: render.sh's BEFORE=1 gives it the
## scene, and the MapDetail, as they were before 02, 04, 05 and 10 were applied, which the
## proposals were written for.
##
## A style is a script in styles/ whose file name starts with its number (1NN_ for the variants
## of proposal NN revisited on 2026-10-19, which start from the scene as it was then, and 200 for
## the three of them chosen; StyleKit.as_revisited() puts it back so). It is
## applied to the map before the map enters the tree, as an edit to the scene
## would be, so the map's own nodes (MapDetail, BorderSwitch) read it in their
## _ready. A style may also:
##   ready(kit)            - add runtime nodes once the map is in the tree
##   panels(kit) -> Array  - render other views than the standard four: each an
##                           Array [letter, caption, centre or null, miles]
##   route(kit) -> PackedVector2Array - where the party is going, in place of ROUTE_TO
##   before_panel(kit, i, view) - change something just before panel i (its view
##                           as above) is captured, once the view is in place
extends Node

const MAP := "res://Scenes/Map.tscn"
const STYLES := "res://_probe/styles"
const Kit := preload("res://_probe/StyleKit.gd")

## The standard views, each [letter, caption, centre in the map's units or null
## for the land's middle, the view's height in miles or 0 for all the way out].
const VIEWS := [
	["A", "Realm: all the way out", null, 0.0],
	["B", "Duchy tier: 180 miles tall", Vector2(7302, 7381), 180.0],
	["C", "County tier: 80 miles tall", Vector2(6150, 8500), 80.0],
	["D", "Closest: 30 miles tall", Vector2(7302, 7381), 30.0],
]
## The party's route in every view: it is sent from its start towards the
## capital of kingdom 5, so the dashed line and its cross show.
const ROUTE_TO := Vector2(8100.0, 7520.0)
const GAP := 8
const BACKGROUND := Color(0.06, 0.06, 0.08)
const WATCHDOG_SECONDS := 180

var _style_id := 0
var _out_dir := ""
var _data_dir := ""
var _filter := ""
var _only := ""
var _tag := ""
var _keep_panels := false
var _timing := 20
var _map_path := MAP

var _map: Node2D
var _kit: RefCounted
var _style: Object
var _caption: Label
var _filter_layer: CanvasLayer


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		var value := arg.get_slice("=", 1)
		if arg.begins_with("--style="):
			_style_id = int(value)
		elif arg.begins_with("--outdir="):
			_out_dir = value
		elif arg.begins_with("--data="):
			_data_dir = value
		elif arg.begins_with("--filter="):
			_filter = value
		elif arg.begins_with("--views="):
			_only = value
		elif arg.begins_with("--tag="):
			_tag = value
		elif arg.begins_with("--timing="):
			_timing = maxi(int(value), 3)
		elif arg.begins_with("--map="):
			_map_path = value
		elif arg == "--panels":
			_keep_panels = true
	get_tree().root.gui_disable_input = true
	# A style that fails stops this coroutine, and Godot would then sit idle
	# for good: give up after a while instead.
	get_tree().create_timer(WATCHDOG_SECONDS, true, false, true).timeout.connect(func() -> void:
		push_error("MapStyleProbe: gave up after %d s" % WATCHDOG_SECONDS)
		get_tree().quit(2))

	var script := _find_style(_style_id)
	if script == null or not script.can_instantiate():
		push_error("MapStyleProbe: no style %d in %s, or it does not compile" % [_style_id, STYLES])
		get_tree().quit(1)
		return
	_style = script.new()
	# A variant names itself in its caption by its LABEL ("14a"), a proposal by its number.
	var label: Variant = _style.get("LABEL")
	var title := "%s  %s" % ["%02d" % _style_id if label == null else str(label), _style.get("NAME")]
	print("MapStyleProbe: style %s" % title)

	var started := Time.get_ticks_usec()
	_map = (load(_map_path) as PackedScene).instantiate()
	_kit = Kit.new(_map, self, _data_dir)
	var loaded := Time.get_ticks_usec()
	if _style.has_method("apply"):
		_style.apply(_kit)
	if _map_path != MAP:
		_as_before(_map.get_node_or_null(^"Detail"))
	var styled := Time.get_ticks_usec()
	print("MapStyleProbe: map loaded in %d ms; the style applied in %.1f ms" % [
		(loaded - started) / 1000, (styled - loaded) / 1000.0])

	_quiet(_map)
	var entered := Time.get_ticks_usec()
	add_child(_map)
	print("MapStyleProbe: map readied (MapDetail and the rest) in %d ms" % ((Time.get_ticks_usec() - entered) / 1000))
	_add_caption()
	await _frames(5)
	if _style.has_method("ready"):
		var readying := Time.get_ticks_usec()
		await _style.ready(_kit)
		print("MapStyleProbe: the style's runtime part readied in %.1f ms" % ((Time.get_ticks_usec() - readying) / 1000.0))
	_send_party()

	var views: Array = VIEWS
	if _style.has_method("panels"):
		views = _style.panels(_kit)
	var images: Array[Image] = []
	for i in views.size():
		var view: Array = views[i]
		if not _only.is_empty() and not _only.split(",").has(str(view[0])):
			continue
		images.append(await _render(view, i, title))
	if images.is_empty():
		get_tree().quit(1)
		return

	var slug := _slug(str(_style.get("NAME")))
	var stem := "%s/%02d-%s%s" % [_out_dir, _style_id, slug, _tag]
	if _keep_panels:
		for i in images.size():
			images[i].save_png("%s-%d.png" % [stem, i])
	var sheet := _sheet(images)
	var err := sheet.save_png(stem + ".png")
	print("MapStyleProbe: saved %s.png (%dx%d) err=%d" % [stem, sheet.get_width(), sheet.get_height(), err])
	get_tree().quit()


## The style whose file name in styles/ starts with [param id], as two digits.
func _find_style(id: int) -> GDScript:
	var prefix := "%02d_" % id
	for file in DirAccess.get_files_at(STYLES):
		if file.begins_with(prefix) and file.ends_with(".gd"):
			return load(STYLES.path_join(file))
	return null


## On a copy of the map as it was (render.sh's BEFORE=1), MapDetail as it was too. The copy has
## MapDetail's file as it was then, but a style that gives the Detail node a script of its own
## built on MapDetail (19's and 28's ProgressiveDetail) has today's under it: what came since is
## set off here, the borders' own width and fading by the zoom (14b, applied on 2026-10-19). On the
## file as it was, which has none of them, setting them does nothing.
func _as_before(detail: Node) -> void:
	if detail == null:
		return
	detail.set("border_growth", 0.0)
	detail.set("kingdom_border_faintest", 1.0)
	detail.set("duchy_border_faintest", 1.0)


## Keeps the player's real mouse and keys out of the map: nothing pans, zooms,
## sends the party or opens a menu while the views are taken.
func _quiet(map: Node) -> void:
	var camera := map.get_node(^"Camera")
	camera.set("edge_pan_enabled", false)
	camera.set_process_unhandled_input(false)
	for path: NodePath in [^"Party", ^"BorderSwitch", ^"VillageMenu", ^"SquadMenu"]:
		var node := map.get_node_or_null(path)
		if node != null:
			node.set_process_unhandled_input(false)
			node.set_process_input(false)


## Gives the party a route, so its dashed line shows, and stops it there: towards ROUTE_TO, or along
## the style's own route(kit) when it has one.
func _send_party() -> void:
	var party := _map.get_node(^"Party") as Node2D
	var route := PackedVector2Array([ROUTE_TO])
	if _style.has_method("route"):
		route = _style.route(_kit)
	party.set("_route", route)
	party.set_process(false)
	party.queue_redraw()


## Moves the camera to [param view], waits for the map's level of detail to
## settle, and captures the frame.
func _render(view: Array, index: int, title: String) -> Image:
	var camera := _map.get_node(^"Camera") as Camera2D
	var miles: float = view[3]
	var zoom: float
	if miles <= 0.0:
		zoom = camera.call("_min_zoom")
	else:
		zoom = get_viewport().get_visible_rect().size.y / (miles * Kit.UNITS_A_MILE)
	var centre: Vector2 = view[2] if view[2] != null else (camera.call("_map_rect") as Rect2).get_center()
	camera.set("_target_zoom", zoom)
	camera.set("_current_zoom", zoom)
	camera.set("_target_position", centre)
	camera.set("_current_position", centre)
	camera.call("_apply")
	_caption.text = "%s   ·   %s  %s" % [title, view[0], view[1]]
	# A fifth entry is a filter for this panel alone ("" for none); else
	# --filter's, for every panel.
	_set_filter(str(view[4]) if view.size() > 4 else _filter)

	await _settle()
	if _style.has_method("before_panel"):
		await _style.before_panel(_kit, index, view)
		await _settle()
	# The settlements follow the real pointer for their tooltips: stop them,
	# and draw each for this zoom.
	for place in get_tree().get_nodes_in_group(&"destinations"):
		place.set_process(false)
		place.set("hovered", false)
		place.queue_redraw()
	(_map.get_node(^"Party") as Node2D).queue_redraw()
	await _frames(3)
	var times := await _time_frames(_timing)
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	image.convert(Image.FORMAT_RGB8)
	print("MapStyleProbe: view %s  zoom %.4f  cpu %.2f ms  gpu %.2f ms  draw calls %d" % [
		view[0], zoom, times[0], times[1], times[2]])
	return image


## Waits until MapDetail has given every line in view its width and nothing is
## fading in or out.
func _settle() -> void:
	var detail := _map.get_node_or_null(^"Detail")
	for frame in 900:
		await get_tree().process_frame
		if frame < 8 or detail == null:
			continue
		if detail.get("_stale"):
			continue
		var still := true
		var shown: Array = detail.get("_shown")
		var waits: Array = detail.get("_waits")
		for tier in shown.size():
			if (shown[tier] > 0.0 and shown[tier] < 1.0) or waits[tier] >= 0.0:
				still = false
		if still:
			return


## The renderer's own measure of a frame over [param count] frames: the median
## CPU and GPU milliseconds (single frames jump with the GPU's clocks), and
## draw calls.
func _time_frames(count: int) -> Array:
	var rid := get_viewport().get_viewport_rid()
	RenderingServer.viewport_set_measure_render_time(rid, true)
	var cpu: Array[float] = []
	var gpu: Array[float] = []
	var calls := 0
	for i in count:
		await RenderingServer.frame_post_draw
		cpu.append(RenderingServer.viewport_get_measured_render_time_cpu(rid))
		gpu.append(RenderingServer.viewport_get_measured_render_time_gpu(rid))
		calls = maxi(calls, int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)))
	cpu.sort()
	gpu.sort()
	return [cpu[count / 2], gpu[count / 2], calls]


func _frames(count: int) -> void:
	for i in count:
		await get_tree().process_frame


## The panels two to a row.
func _sheet(images: Array[Image]) -> Image:
	var w := images[0].get_width()
	var h := images[0].get_height()
	var columns := 1 if images.size() == 1 else 2
	var rows := ceili(images.size() / float(columns))
	var sheet := Image.create(w * columns + GAP * (columns - 1), h * rows + GAP * (rows - 1), false, Image.FORMAT_RGB8)
	sheet.fill(BACKGROUND)
	for i in images.size():
		var at := Vector2i((i % columns) * (w + GAP), (i / columns) * (h + GAP))
		sheet.blit_rect(images[i], Rect2i(Vector2i.ZERO, Vector2i(w, h)), at)
	return sheet


## A caption in the bottom left corner naming the style and the view.
func _add_caption() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 120
	add_child(layer)
	var panel := PanelContainer.new()
	var box := StyleBoxFlat.new()
	box.bg_color = Color(0.05, 0.06, 0.09, 0.82)
	box.content_margin_left = 12
	box.content_margin_right = 12
	box.content_margin_top = 5
	box.content_margin_bottom = 5
	box.corner_radius_top_right = 6
	panel.add_theme_stylebox_override(&"panel", box)
	panel.anchor_top = 1.0
	panel.anchor_bottom = 1.0
	panel.grow_vertical = Control.GROW_DIRECTION_BEGIN
	_caption = Label.new()
	_caption.add_theme_font_size_override(&"font_size", 17)
	_caption.add_theme_color_override(&"font_color", Color(0.95, 0.95, 0.92))
	panel.add_child(_caption)
	layer.add_child(panel)


## A full-screen filter over the map, under the caption: "deutan", "protan" or
## "tritan" shows the frame as someone with that colour blindness would see it.
func _add_filter(kind: String) -> void:
	_filter_layer = CanvasLayer.new()
	_filter_layer.layer = 110
	add_child(_filter_layer)
	var rect := ColorRect.new()
	rect.set_anchors_preset(Control.PRESET_FULL_RECT)
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var material := ShaderMaterial.new()
	material.shader = load("res://_probe/shaders/cvd_filter.gdshader")
	material.set_shader_parameter(&"kind", ["deutan", "protan", "tritan", "grey"].find(kind))
	rect.material = material
	_filter_layer.add_child(rect)


## The filter for one panel: made, changed or hidden.
func _set_filter(kind: String) -> void:
	if kind.is_empty():
		if _filter_layer != null:
			_filter_layer.visible = false
		return
	if _filter_layer == null:
		_add_filter(kind)
	_filter_layer.visible = true
	var rect := _filter_layer.get_child(0) as ColorRect
	(rect.material as ShaderMaterial).set_shader_parameter(&"kind", ["deutan", "protan", "tritan", "grey"].find(kind))
	_caption.text += "   ·   %s" % {"deutan": "as seen with deuteranopia", "protan": "as seen with protanopia", "tritan": "as seen with tritanopia", "grey": "in greyscale (lightness alone)"}[kind]


static func _slug(text: String) -> String:
	var out := ""
	for c in text.to_lower():
		out += c if (c >= "a" and c <= "z") or (c >= "0" and c <= "9") else "-"
	while out.contains("--"):
		out = out.replace("--", "-")
	return out.trim_prefix("-").trim_suffix("-")
