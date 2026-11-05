extends SceneTree
## Run by integration.py in a scratch copy of VCOM (never the game itself):
##   godot [--headless] --path <copy> --script res://_probe/building_probe.gd -- <jobs.json>
## For each job (a building cut into pieces by cut_pieces.py), builds a level of
## grass and the pieces, lit as TestMap is, asks the rules what integration.py
## expects of it, and with "render" saves frames by day, dusk and night from the
## game's own renderer. Writes report.json into "out". (poke_c's probe, for
## buildings of several storeys: climbs, closed-off storeys, a cut per storey.)

var jobs: Dictionary
var report := {}

func _initialize() -> void:
	jobs = JSON.parse_string(FileAccess.get_file_as_string(OS.get_cmdline_user_args()[0]))
	call_deferred("run")


func run() -> void:
	root.size = Vector2i(1280, 800)
	root.msaa_3d = Viewport.MSAA_4X
	var base_lib: PieceLibrary = load("res://Blocks/Pieces.tres")
	var grass := base_lib.find(&"BrightGrass1")
	var wall_wear: Destruction = load("res://Resources/Destruction/SimpleWall1.tres")
	for job in jobs.jobs:
		var periods: Array = [TimeOfDay.Period.DAY]
		if jobs.render:
			periods = [TimeOfDay.Period.DAY, TimeOfDay.Period.DUSK, TimeOfDay.Period.NIGHT]
		for period in periods:
			var built := build(job, grass, wall_wear, period)
			var scene: Node3D = built[0]
			var level: VoxelLevel = built[1]
			var grid: CombatGrid = built[2]
			for i in 3:
				await process_frame
			if period == TimeOfDay.Period.DAY:
				report[job.name] = check(job, level, grid)
			if jobs.render:
				await render(job, scene, level, period)
			scene.queue_free()
			await process_frame
	var file := FileAccess.open(jobs.out + "/report.json", FileAccess.WRITE)
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
	print("PROBE_DONE ", report.size(), " scenes")
	quit()


func build(job: Dictionary, grass: PieceKind, wear: Destruction, period: int) -> Array:
	var lib := PieceLibrary.new()
	lib.kinds.append(grass)
	var data := LevelData.new()
	var foot := {}
	for lay in job.layouts:
		for id in lay.kinds:
			if lib.find(StringName(id)) != null:
				continue
			var k: Dictionary = lay.kinds[id]
			var kind := PieceKind.new()
			kind.id = StringName(id)
			kind.model = load(k.file)
			kind.window = k.window
			kind.cutaway = k.cutaway
			kind.tile_grid = k.floor
			kind.edge_piece = k.edge
			kind.corner_piece = k.corner
			kind.destruction = grass.destruction if k.floor else wear
			lib.kinds.append(kind)
		for c in lay.footprint:
			foot[Vector2i(int(c[0]), int(c[1]))] = true
	var lo := Vector2i(1000, 1000)
	var hi := Vector2i(-1000, -1000)
	for c in foot:
		lo = Vector2i(mini(lo.x, c.x), mini(lo.y, c.y))
		hi = Vector2i(maxi(hi.x, c.x), maxi(hi.y, c.y))
	var margin := 16                   # wide enough that its edges are out of every view
	for x in range(lo.x - margin, hi.x + margin + 1):
		for z in range(lo.y - margin, hi.y + margin + 1):
			if not foot.has(Vector2i(x, z)):
				data.add(&"BrightGrass1", Vector3i(2 * x, 0, 2 * z), 0)
	for lay in job.layouts:
		for p in lay.pieces:
			data.add(StringName(p.kind), Vector3i(int(p.slot[0]), int(p.slot[1]), int(p.slot[2])), int(p.get("turn", 0)))

	var tm: Node = load("res://Scenes/TestMap.tscn").instantiate()
	var env_node: WorldEnvironment = tm.get_node("WorldEnvironment")
	var sun: DirectionalLight3D = tm.get_node("DirectionalLight3D")
	tm.remove_child(env_node)
	tm.remove_child(sun)
	tm.free()
	var scene := Node3D.new()
	scene.name = "Map"
	root.add_child(scene)
	env_node.name = "WorldEnvironment"
	sun.name = "DirectionalLight3D"
	scene.add_child(env_node)
	scene.add_child(sun)
	var level := VoxelLevel.new()
	level.name = "Level"
	level.library = lib
	level.data = data
	scene.add_child(level)
	var grid := CombatGrid.new()
	grid.name = "CombatGrid"
	scene.add_child(grid)
	TimeOfDay.forced = period
	var tod := TimeOfDay.new()
	tod.name = "TimeOfDay"
	scene.add_child(tod)
	var cam := Camera3D.new()
	cam.name = "Camera"
	scene.add_child(cam)
	cam.current = true
	var top := 0
	for lay in job.layouts:
		for p in lay.pieces:
			top = maxi(top, int(p.slot[1]) + 1)
	scene.set_meta("centre", Vector3((lo.x + hi.x + 1) * 0.5, 0.0, (lo.y + hi.y + 1) * 0.5))
	scene.set_meta("extent", maxf(float(maxi(hi.x - lo.x + 1, hi.y - lo.y + 1)), top * 0.75))
	scene.set_meta("top", float(top))
	if job.has("figure"):
		# A soldier for scale (the figure every unit wears, standing idle): two cells
		# tall, as a unit is to the rules. It sets its own height each frame (a hop),
		# so it stands under a node at the tile, as a unit carries it.
		var holder := Node3D.new()
		var at: Array = job.figure
		holder.position = Vector3(float(at[0]) + 0.5, float(at[1]), float(at[2]) + 0.5)
		holder.rotation.y = deg_to_rad(float(at[3]) if at.size() > 3 else 0.0)
		scene.add_child(holder)
		holder.add_child(load("res://Scenes/BaseCharacter.tscn").instantiate())
	return [scene, level, grid]


func v3(a) -> Vector3i:
	return Vector3i(int(a[0]), int(a[1]), int(a[2]))


func v2(a) -> Vector2i:
	return Vector2i(int(a[0]), int(a[1]))


func check(job: Dictionary, level: VoxelLevel, grid: CombatGrid) -> Dictionary:
	var checks := {}
	var notes := {}
	var e: Dictionary = job.expect
	var bad := []
	for t in e.floors:
		if not grid.is_tile(v3(t)):
			bad.append(t)
	checks["floors_are_tiles"] = bad.is_empty()
	notes["floors_not_tiles"] = bad
	bad = []
	for d in e.shut:
		if not grid.has_edge(v3(d[0]), v2(d[1])):
			bad.append(d)
	checks["walls_and_doors_shut"] = bad.is_empty()
	notes["open_where_shut"] = bad
	bad = []
	for d in e.open:
		if grid.has_edge(v3(d[0]), v2(d[1])):
			bad.append(d)
	checks["windows_open"] = bad.is_empty()
	notes["shut_where_open"] = bad
	bad = []
	for s in e.sight:
		var seen := grid.is_line_clear(v3(s[0]), v3(s[1]))
		if seen != bool(s[2]):
			bad.append(s)
	checks["sight"] = bad.is_empty()
	notes["sight_wrong"] = bad
	bad = []
	for s in e.vaults:
		var from := v3(s[0])
		var to := v3(s[1])
		if not grid.neighbours(from).has(to) or grid.vault_height(from, to) != 1:
			bad.append(s)
	checks["vaults"] = bad.is_empty()
	notes["no_vault"] = bad
	bad = []
	for s in e.climbs:
		var from := v3(s[0])
		var to := v3(s[1])
		if not grid.neighbours(from).has(to) or grid.vault_height(from, to) != 0:
			bad.append(s)
	checks["climbs"] = bad.is_empty()
	notes["no_climb"] = bad
	bad = []
	for s in e.blocked_steps:
		if grid.neighbours(v3(s[0])).has(v3(s[1])):
			bad.append(s)
	checks["blocked_steps"] = bad.is_empty()
	notes["stepped_through"] = bad
	var reach = grid.find_reachable(v3(e.reach[0]), 80)
	bad = []
	for t in e.reach[1]:
		if not reach.came_from.has(v3(t)) and v3(t) != v3(e.reach[0]):
			bad.append(t)
	checks["reachable"] = bad.is_empty()
	notes["unreached"] = bad
	bad = []
	for t in e.closed:
		if reach.came_from.has(v3(t)):
			bad.append(t)
	checks["closed_off"] = bad.is_empty()
	notes["reached_though_closed"] = bad
	bad = []
	for t in e.under:
		if not level.is_under_building(v3(t)):
			bad.append(t)
	checks["under_building"] = bad.is_empty()
	notes["not_under"] = bad
	var cut_counts := []
	var cuts_ok := true
	for h in e.cuts:
		level.cut_away(int(h))
		var cut := level.cutaway.pieces.size() if level.cutaway != null else 0
		level.cut_away(VoxelLevel.UNCUT)
		cut_counts.append(cut)
		cuts_ok = cuts_ok and cut > 0
	checks["cutaway"] = cuts_ok
	notes["cut_pieces"] = cut_counts
	if job.has("exact"):
		var ex: Dictionary = job.exact
		var b: Array = ex.box
		var ground := 0
		for i in level.data.count():
			if level.data.kind_id(i) == &"BrightGrass1":
				ground = i + 1
		var total := 0
		var count := 0
		var vol := level.volume
		for gx in range(int(b[0]), int(b[3])):
			for gy in range(int(b[1]), int(b[4])):
				for gz in range(int(b[2]), int(b[5])):
					var v := Vector3i(gx, gy, gz)
					if not vol.is_solid(v) or vol.owner_at(v) < ground:
						continue
					var c: Color = vol.palette[vol.color_at(v)]
					var h := ((gx + 4096) * 8192 + (gy + 4096)) * 8192 + (gz + 4096)
					var code := (c.r8 * 65536 + c.g8 * 256 + c.b8) * 2 + (1 if vol.is_glass(v) else 0)
					total = (total + (h % 17179869143) * 33554432 + code) % 2305843009213693951
					count += 1
		checks["stamped_exactly"] = count == int(ex.count) and str(total) == String(ex.sum)
		notes["stamped"] = [count, str(total), int(ex.count), String(ex.sum)]
	notes["tiles"] = grid.tiles().size()
	notes["pieces"] = level.data.count()
	notes["kinds"] = level.library.kinds.size()
	notes["windows"] = level.rules.window_slots().size()
	notes["triangles"] = level.renderer.triangles
	return {"checks": checks, "notes": notes}


func render(job: Dictionary, scene: Node3D, level: VoxelLevel, period: int) -> void:
	var cam: Camera3D = scene.get_node("Camera")
	var centre: Vector3 = scene.get_meta("centre")
	var extent: float = scene.get_meta("extent")
	var dir: String = jobs.out + "/" + job.name
	DirAccess.make_dir_recursive_absolute(dir)
	var names := ["day", "dusk", "night"]
	var views: Array = job.views if period == TimeOfDay.Period.DAY else [job.views[0]]
	var i := 0
	for v in views:
		cam.fov = float(v[4]) if v.size() > 4 else 30.0
		var yaw := deg_to_rad(float(v[0]))
		var pitch := deg_to_rad(float(v[1]))
		var dist := float(v[2]) * extent
		var target := centre + Vector3(0, float(v[3]) * float(scene.get_meta("top")), 0)
		cam.position = target + Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch)) * dist
		cam.look_at(target, Vector3.UP)
		var cut := int(v[5]) if v.size() > 5 else -1
		if cut >= 0:
			level.cut_away(cut)
		for n in 6:
			await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("%s/%s_%d.png" % [dir, names[period], i])
		if cut >= 0:
			level.cut_away(VoxelLevel.UNCUT)
		i += 1
