extends SceneTree
## The README's Godot lines, run as they are written there, with the folder where the README says
## it is. Run headless from vcom/:  godot --headless --path . --script g6_readme_snippet.gd


func _initialize() -> void:
	var x := 981
	var y := 1011
	var folder := ProjectSettings.globalize_path("res://").path_join("../MapCreation/SourceData")
	print("folder: ", folder, "; there: ", DirAccess.dir_exists_absolute(folder))
	var counties := Image.load_from_file(folder.path_join("CountyMap.png"))    # FORMAT_L8
	var bytes := counties.get_data()                                            # one byte a pixel
	var county := bytes[y * counties.get_width() + x]
	var lake_map := Image.load_from_file(folder.path_join("LakeMap.png"))      # FORMAT_RGB8
	var lake_bytes := lake_map.get_data()                                       # three bytes a pixel
	var at := 3 * (y * lake_map.get_width() + x)
	var lake := lake_bytes[at] + 256 * lake_bytes[at + 1]
	var rivers: Array = JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("Rivers.json")))["rivers"]
	print("formats: ", counties.get_format(), " (L8 is ", Image.FORMAT_L8, "), ", lake_map.get_format(), " (RGB8 is ", Image.FORMAT_RGB8, "); bytes ", bytes.size(), ", ", lake_bytes.size())
	print("at (", x, ", ", y, "): county ", county, ", lake ", lake, "; rivers ", rivers.size())

	# Every settlement by the bytes, and every lake's inside point.
	var settlements: Array = JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("Settlements.json")))["settlements"]
	var wrong := 0
	for s: Dictionary in settlements:
		if bytes[int(s["y"]) * counties.get_width() + int(s["x"])] != int(s["county"]):
			wrong += 1
	var lakes: Array = JSON.parse_string(FileAccess.get_file_as_string(folder.path_join("Lakes.json")))["lakes"]
	var wrong_lakes := 0
	for l: Dictionary in lakes:
		var i := 3 * (int(l["point_inside"][1]) * lake_map.get_width() + int(l["point_inside"][0]))
		if lake_bytes[i] + 256 * lake_bytes[i + 1] != int(l["id"]):
			wrong_lakes += 1
	print("settlements not on their county by the bytes: ", wrong, " of ", settlements.size(), "; lakes whose inside point is not theirs by the bytes: ", wrong_lakes, " of ", lakes.size())
	print("a number out of the JSON is of type ", typeof(settlements[0]["county"]), " (float is ", TYPE_FLOAT, ", int is ", TYPE_INT, "): ", settlements[0]["county"])
	var by_county := {}
	for s: Dictionary in settlements:
		by_county[int(s["county"])] = s
	print("looked up by int: ", by_county.has(13), "; by the number as the JSON gives it: ", by_county.has(settlements[12]["county"]))
	quit()
