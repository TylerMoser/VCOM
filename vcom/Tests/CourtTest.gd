## Run CourtTest.tscn to check every capital's authored court and its UI.
extends Node


func _ready() -> void:
	call_deferred("_run")


func _run() -> void:
	var map := load("res://Scenes/Map.tscn") as PackedScene
	var state := map.get_state()
	var counts := {"Count": 0, "Duke": 0, "King": 0}
	var seen: Array[Court] = []
	var settlement_locations: Array = []
	for node in state.get_node_count():
		var path := str(state.get_node_path(node)).trim_prefix("./")
		var title := ""
		if path.begins_with("Settlements/CountyCapitals/"):
			title = "Count"
		elif path.begins_with("Settlements/DuchyCapitals/"):
			title = "Duke"
		elif path.begins_with("Settlements/KingdomCapitals/"):
			title = "King"
		if title.is_empty():
			continue
		var locations: Array = []
		for property in state.get_node_property_count(node):
			if state.get_node_property_name(node, property) == &"locations":
				locations = state.get_node_property_value(node, property)
		assert(not locations.is_empty() and locations[0] is Court)
		var court := locations[0] as Court
		assert(court.display_name == "Court of " + title)
		assert(court.ruler_name == title and court.favor == Court.Favor.NEUTRAL)
		assert(court.gain_favor_by == ["none"] and court.lose_favor_by == ["none"])
		assert(not court.description.is_empty() and not seen.has(court))
		seen.append(court)
		counts[title] += 1
		if path.ends_with("County115Capital"):
			settlement_locations = locations
	assert(counts == {"Count": 176, "Duke": 35, "King": 9})
	assert(settlement_locations.size() == 4)
	assert(settlement_locations[1] is QuestBoard)
	var menu := TabbedMenu.new()
	get_tree().root.add_child(menu)
	for location: Location in settlement_locations:
		menu.tabs.add_child(location.make_tab())
	menu.open()
	var page := menu.tabs.get_current_tab_control() as CourtTab
	assert(page != null and menu.tabs.get_tab_title(0) == "Court of Count")
	assert(page._ruler.text == "Count")
	assert(page._favor.texture == CourtTab.FAVOR_ICONS[Court.Favor.NEUTRAL])
	assert(page._favor.tooltip_text == "Favor: Neutral")
	await get_tree().process_frame
	await get_tree().process_frame
	assert(page._favor.global_position.x > page._ruler.global_position.x + page._ruler.size.x)
	if DisplayServer.get_name() != "headless":
		await RenderingServer.frame_post_draw
		get_tree().root.get_texture().get_image().save_png(OS.get_environment("TEMP") + "/voxel-court.png")
	menu.close()
	for favor in 3:
		var court := Court.new()
		court.display_name = "Test Court"
		court.favor = favor
		court.description = "Long court information.\n".repeat(100)
		var long_page := court.make_tab() as CourtTab
		menu.tabs.add_child(long_page)
		menu.open()
		menu.tabs.current_tab = menu.tabs.get_tab_count() - 1
		await get_tree().process_frame
		await get_tree().process_frame
		assert(long_page._favor.texture == CourtTab.FAVOR_ICONS[favor])
		assert(long_page.get_v_scroll_bar().max_value > long_page.size.y)
		long_page.scroll_vertical = 200
		assert(long_page.scroll_vertical > 0)
		menu.close()
	print("COURT CHECKS PASSED: ", counts)
	get_tree().quit()

