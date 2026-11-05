extends SceneTree
## Run by terrain_test.py in a scratch copy of VCOM (never the game itself):
##   godot [--headless] --path <copy> --script res://_probe/terrain_probe.gd -- <jobs.json>
## For each job (a terrain style's pieces cut into the game's 16-cubed cells, laid
## out as a test plateau on its image's own ground tiles), builds the level, lit as
## TestMap is, asks the rules what terrain_test.py expects of it, and with "render"
## saves frames by day, dusk and night from the game's own renderer. Writes
## report.json into "out".

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
	for job in jobs.jobs:
		var periods: Array = [TimeOfDay.Period.DAY]
		if jobs.render:
			periods = [TimeOfDay.Period.DAY, TimeOfDay.Period.DUSK, TimeOfDay.Period.NIGHT]
		for period in periods:
			var built := build(job, grass, period)
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


func build(job: Dictionary, grass: PieceKind, period: int) -> Array:
	var lib := PieceLibrary.new()
	for id in job.kinds:
		var k: Dictionary = job.kinds[id]
		var kind := PieceKind.new()
		kind.id = StringName(id)
		kind.model = load(k.file)
		kind.tile_grid = bool(k.floor)
		kind.destruction = grass.destruction
		lib.kinds.append(kind)
	var data := LevelData.new()
	for p in job.pieces:
		data.add(StringName(p.kind), Vector3i(int(p.slot[0]), int(p.slot[1]), int(p.slot[2])), int(p.turn))
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
	scene.set_meta("centre", Vector3(float(job.centre[0]), 0.0, float(job.centre[1])))
	scene.set_meta("extent", float(job.extent))
	scene.set_meta("top", float(job.top))
	if job.has("figure"):
		# A soldier for scale: two cells tall, as a unit is to the rules.
		var holder := Node3D.new()
		var at: Array = job.figure
		holder.position = Vector3(float(at[0]) + 0.5, float(at[1]), float(at[2]) + 0.5)
		holder.rotation.y = deg_to_rad(float(at[3]))
		scene.add_child(holder)
		holder.add_child(load("res://Scenes/BaseCharacter.tscn").instantiate())
	return [scene, level, grid]


func v3(a) -> Vector3i:
	return Vector3i(int(a[0]), int(a[1]), int(a[2]))


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
	for t in e.not_floors:
		if grid.is_tile(v3(t)):
			bad.append(t)
	checks["nothing_else_stood_on"] = bad.is_empty()
	notes["stood_where_solid"] = bad
	bad = []
	for s in e.climbs:
		if not grid.neighbours(v3(s[0])).has(v3(s[1])):
			bad.append(s)
	checks["climbs"] = bad.is_empty()
	notes["no_climb"] = bad
	bad = []
	for s in e.blocked_steps:
		if grid.neighbours(v3(s[0])).has(v3(s[1])):
			bad.append(s)
	checks["blocked_steps"] = bad.is_empty()
	notes["stepped_up"] = bad
	var reach = grid.find_reachable(v3(e.reach[0]), 200)
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
	var ex: Dictionary = job.exact
	var b: Array = ex.box
	var total := 0
	var count := 0
	var vol := level.volume
	for gx in range(int(b[0]), int(b[3])):
		for gy in range(int(b[1]), int(b[4])):
			for gz in range(int(b[2]), int(b[5])):
				var v := Vector3i(gx, gy, gz)
				if not vol.is_solid(v):
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
		for n in 6:
			await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("%s/%s_%d.png" % [dir, names[period], i])
		i += 1
