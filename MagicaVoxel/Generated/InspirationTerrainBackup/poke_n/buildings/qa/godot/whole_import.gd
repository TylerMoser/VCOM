extends SceneTree
## Run in a scratch copy of VCOM (integration.py --whole does it):
##   godot --headless --path <copy> --script res://_probe/whole_import.gd -- <manifest.json> <models dir> <out.json>
## Reads every delivered building whole through the game's own MagicaVoxel importer,
## as Godot would on opening it: its voxel count, its glass as the game's VoxelShape
## reads it (a Glass material, its clarity), and a mesh at the blocks' Scale 0.0625,
## grounded at y 0 and as big as its canvas says.

const Reader = preload("res://addons/MagicaVoxel_Importer_with_Extensions/VoxImporter/vox-importer-common.gd")

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var args := OS.get_cmdline_user_args()
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(args[0]))
	var report := {}
	for row in manifest.models:
		var path: String = args[1] + "/" + row.file
		var reader = Reader.new()
		var raw: Dictionary = reader.read_vox_data(path)
		var r := {"read": raw.error == OK}
		if raw.error != OK:
			report[row.file] = r
			continue
		var frames: Dictionary = reader.unify_voxels(raw.vox, false)
		var voxels: Dictionary = frames[frames.keys().min()]
		r["voxels"] = voxels.size()
		r["voxels_match"] = voxels.size() == int(row.voxels)
		var glass := {}
		for place in raw.vox.materials:
			var m = raw.vox.materials[place]
			if m.is_glass():
				glass[str(place + 1)] = m.transparency
		r["glass"] = glass
		var glass_voxels := 0
		for v in voxels:
			if glass.has(str(int(voxels[v]) + 1)):
				glass_voxels += 1
		r["glass_voxels_match"] = glass_voxels == int(row.glass_voxels)
		var meshes = Reader.new().import(path, "", {"Scale": 0.0625, "GreedyMeshGenerator": true, "SnapToGround": false,
			"FirstKeyframeOnly": true}, [], [])
		var ok: bool = meshes is Array and meshes.size() == 1
		r["mesh"] = ok
		if ok:
			var mesh: Mesh = meshes[0]
			var aabb := mesh.get_aabb()
			r["aabb"] = str(aabb)
			r["grounded"] = absf(aabb.position.y) < 0.001
			r["surfaces"] = mesh.get_surface_count()
			var size := aabb.size * 16.0
			var occ_min: Array = row.occupied_min
			var occ_max: Array = row.occupied_max
			r["size_match"] = absf(size.x - (occ_max[0] - occ_min[0] + 1)) < 0.01 and \
				absf(size.y - (occ_max[2] - occ_min[2] + 1)) < 0.01 and absf(size.z - (occ_max[1] - occ_min[1] + 1)) < 0.01
		report[row.file] = r
	var f := FileAccess.open(args[2], FileAccess.WRITE)
	f.store_string(JSON.stringify(report, "\t"))
	f.close()
	print("WHOLE_IMPORT_DONE ", report.size())
	quit()
