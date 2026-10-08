extends SceneTree
## Does Godot read the source data's files exactly? Run headless:
##   godot --headless --path vcom --script g5_read_source.gd -- <SourceData dir> <MapCreation dir>


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var dir: String = args[0]
	var maps: String = args[1]

	var county := Image.load_from_file(dir + "/CountyMap.png")
	print("CountyMap.png: %d x %d, format %d (L8 is %d)" % [county.get_width(), county.get_height(), county.get_format(), Image.FORMAT_L8])
	var settlements: Array = JSON.parse_string(FileAccess.get_file_as_string(dir + "/Settlements.json"))["settlements"]
	var wrong := 0
	for s: Dictionary in settlements:
		if _grey(county, int(s["x"]), int(s["y"])) != int(s["county"]):
			wrong += 1
	print("settlements: %d; standing on a pixel of CountyMap.png that is not their county: %d" % [settlements.size(), wrong])

	var regions: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(dir + "/Regions.json"))
	var duchy := Image.load_from_file(dir + "/DuchyMap.png")
	var kingdom := Image.load_from_file(dir + "/KingdomMap.png")
	wrong = 0
	for c: Dictionary in regions["counties"]:
		var at: Array = c["point_inside"]
		if _grey(county, int(at[0]), int(at[1])) != int(c["number"]) or _grey(duchy, int(at[0]), int(at[1])) != int(c["duchy"]) or _grey(kingdom, int(at[0]), int(at[1])) != int(c["kingdom"]):
			wrong += 1
	print("counties: %d; whose point inside is not in that county, duchy and kingdom on the three maps: %d" % [(regions["counties"] as Array).size(), wrong])

	var lake_map := Image.load_from_file(dir + "/LakeMap.png")
	var lakes: Array = JSON.parse_string(FileAccess.get_file_as_string(dir + "/Lakes.json"))["lakes"]
	wrong = 0
	for l: Dictionary in lakes:
		var at: Array = l["point_inside"]
		if _number(lake_map, int(at[0]), int(at[1])) != int(l["id"]):
			wrong += 1
	print("LakeMap.png: format %d (RGB8 is %d); lakes: %d; whose point inside is not that lake on the map: %d" % [lake_map.get_format(), Image.FORMAT_RGB8, lakes.size(), wrong])

	var rivers: Array = JSON.parse_string(FileAccess.get_file_as_string(dir + "/Rivers.json"))["rivers"]
	var points := 0
	var most := 0.0
	for r: Dictionary in rivers:
		points += (r["points"] as Array).size()
		most = maxf(most, float(r["flow_at_end_m3s"]))
	print("rivers: %d, %d points, the largest carrying %.1f m3/s; the first point of river 1: %s" % [rivers.size(), points, most, str(rivers[0]["points"][0])])

	var roads: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(dir + "/Roads.json"))
	print("roads: %d places, %d stretches, %d roads, %d bridges" % [(roads["places"] as Array).size(), (roads["stretches"] as Array).size(), (roads["roads"] as Array).size(), (roads["bridges"] as Array).size()])
	var borders: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(dir + "/KingdomBorders.json"))
	print("kingdom borders: %d lines, %d meeting places" % [(borders["borders"] as Array).size(), (borders["meeting_places"] as Array).size()])

	var flow := Image.load_from_file(dir + "/DrainageFlow.png")
	var direction := Image.load_from_file(dir + "/DrainageDirection.png")
	var drainage: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(dir + "/Drainage.json"))
	var sink: Array = drainage["salt_lake_sink"]
	var column := int((float(sink[0]) - 0.5) / 2.0)
	var row := int((float(sink[1]) - 0.5) / 2.0)
	print("DrainageFlow.png: %d x %d; at the salt lake's lowest point, cell (%d, %d): direction %d, flow %.2f m3/s" % [
		flow.get_width(), flow.get_height(), column, row, _grey(direction, column, row), _number(flow, column, row) / 32.0])
	var biggest := 0
	for y in flow.get_height():
		for x in range(0, flow.get_width(), 1):
			biggest = maxi(biggest, _number(flow, x, y))
	print("   the largest flow on it: %.2f m3/s" % (biggest / 32.0))

	var elevation := Image.load_from_file(maps + "/Elevation.png")
	print("Elevation.png as Godot reads it: format %d; at the island's highest point (1947, 2157), which is 3,352.1 m: %.1f m" % [
		elevation.get_format(), elevation.get_pixel(1947, 2157).r * 6553.5])
	quit()


## A grey map's number at a pixel.
func _grey(image: Image, x: int, y: int) -> int:
	return int(round(image.get_pixel(x, y).r * 255.0))


## A number map's number at a pixel: red + 256 x green.
func _number(image: Image, x: int, y: int) -> int:
	var colour := image.get_pixel(x, y)
	return int(round(colour.r * 255.0)) + 256 * int(round(colour.g * 255.0))
