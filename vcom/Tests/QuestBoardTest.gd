## Run the QuestBoardTest.tscn scene with Godot to validate the quest board.
extends Node


func _ready() -> void:
	call_deferred("_run")


func _run() -> void:
	var campaign := get_tree().root.get_node("Campaign")
	var board := QuestBoard.new()
	board.display_name = "Quest Board"
	for category in 3:
		var quest := Quest.new()
		quest.title = "Quest %s" % category
		quest.category = category
		quest.description = "Help the settlement."
		quest.objectives = "Speak to the captain."
		quest.quest_giver = "Captain"
		quest.location = "Settlement"
		quest.rewards = "100 gold"
		board.quests.append(quest)
	var offers: Array[Quest] = campaign.quests_on(board)
	assert(offers.size() == 3)
	assert(offers[0] != board.quests[0])
	offers.clear()
	assert(campaign.quests_on(board).size() == 3)
	var menu := TabbedMenu.new()
	get_tree().root.add_child(menu)
	var tab := board.make_tab() as QuestBoardTab
	menu.tabs.add_child(tab)
	menu.open()
	assert(tab._quests._list.get_child_count() == 4)
	tab._quests._list.get_child(2).grab_focus()
	await get_tree().process_frame
	await get_tree().process_frame
	var accepted := tab._quests.selected
	assert(accepted.category == Quest.Category.MAJOR)
	assert(tab._quests._details.text.contains("Type: Major Quest"))
	assert(not tab._accept.disabled)
	campaign.in_mission = true
	assert(not campaign.accept_quest(board, accepted))
	campaign.in_mission = false
	assert(not campaign.accept_quest(QuestBoard.new(), accepted))
	assert(not campaign.accept_quest(board, Quest.new()))
	assert(not campaign.accept_quest(board, null))
	tab._accept.pressed.emit()
	assert(campaign.quests.size() == 1 and campaign.quests[0] == accepted)
	assert(campaign.quests_on(board).size() == 2)
	assert(not campaign.accept_quest(board, accepted))
	assert(tab._quests.selected != accepted and not tab._accept.disabled)
	assert(tab._quests._list.get_child_count() == 3)
	assert(board.quests.size() == 3)
	accepted.status = "Completed"
	assert(board.quests[1].status == "Active")
	menu.close()
	menu.tabs.remove_child(tab)
	tab.queue_free()
	tab = board.make_tab()
	menu.tabs.add_child(tab)
	menu.open()
	assert(tab._quests.selected.category == Quest.Category.MAIN)
	assert(tab._quests._list.get_child_count() == 3)
	assert(menu._sub_tabs() == null)
	# Optional visual fixture, kept out of authored campaign content.
	if DisplayServer.get_name() != "headless":
		await get_tree().process_frame
		await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_tree().root.get_texture().get_image().save_png(OS.get_environment("TEMP") + "/voxel-quest-board.png")
	menu.close()
	# Accept the remaining types and verify the empty-board focus and action.
	menu.open()
	tab._accept.pressed.emit()
	assert(tab._quests.selected.category == Quest.Category.MINOR)
	assert(tab._quests._details.text.contains("Type: Minor Quest"))
	tab._accept.pressed.emit()
	assert(tab._quests.selected == null and tab._accept.disabled)
	assert(menu.tabs.get_tab_bar().has_focus())
	menu.close()
	var pause_menu := get_tree().root.get_node("PauseMenu")
	pause_menu.open()
	var journal := pause_menu.tabs.get_tab_control(1) as QuestsTab
	assert(journal.get_tab_count() == 3 and journal.current_tab == 0)
	for category in 3:
		var browser := journal.get_tab_control(category) as QuestBrowser
		assert(browser._list.get_child_count() == 2)
		assert(browser.selected.category == category)
	journal.current_tab = Quest.Category.MAJOR
	assert(journal.selected_quest() == accepted)
	pause_menu.tabs.current_tab = 1
	assert(pause_menu._sub_tabs() == journal)
	assert(journal.get_current_tab_control()._details.text.contains("Type: Major Quest"))
	if DisplayServer.get_name() != "headless":
		await get_tree().process_frame
		await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_tree().root.get_texture().get_image().save_png(OS.get_environment("TEMP") + "/voxel-quest-journal.png")
	pause_menu.close()
	var authored := load("res://Resources/Locations/County115QuestBoard.tres") as QuestBoard
	assert(authored != null and authored.quests.is_empty())
	var map := load("res://Scenes/Map.tscn") as PackedScene
	var state := map.get_state()
	var boards := 0
	for node in state.get_node_count():
		for property in state.get_node_property_count(node):
			if state.get_node_property_name(node, property) == &"locations":
				var locations: Array = state.get_node_property_value(node, property)
				if locations.has(authored):
					assert(locations.size() == 4)
					assert(locations[0] is Court)
					assert(locations[1] == authored)
					assert(locations[2] is HiringBoard and locations[3] is Market)
					boards += 1
	assert(boards == 1)
	print("QUEST BOARD CHECKS PASSED")
	get_tree().quit()


