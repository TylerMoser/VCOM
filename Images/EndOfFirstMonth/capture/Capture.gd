extends Node

const OUT = "C:/Users/tandm/Documents/Projects/VoxelXCOM/Images/EndOfFirstMonth/"
var scene: Node
var count := 0

func _ready():
	process_mode = Node.PROCESS_MODE_ALWAYS
	_run.call_deferred()

func frames(n = 20):
	for i in n:
		await get_tree().process_frame

func shot(label: String):
	await frames(8)
	await RenderingServer.frame_post_draw
	var error = get_viewport().get_texture().get_image().save_png(OUT + label + ".png")
	assert(error == OK)
	count += 1
	print("CAPTURE ", label)

func slug(s: String) -> String:
	return s.to_lower().replace(" ", "-").replace("/", "-")

func tabshots(tabs: TabContainer, prefix: String):
	for i in tabs.get_tab_count():
		tabs.current_tab = i
		await frames(3)
		var label = prefix + "-" + slug(tabs.get_tab_title(i))
		var nested = visible_tabs(tabs.get_tab_control(i))
		if nested.is_empty():
			await shot(label)
		else:
			for child in nested:
				await tabshots(child, label)

func visible_tabs(node: Node) -> Array:
	if node is TabContainer:
		return [node]
	var result = []
	for child in node.get_children():
		if child is Control and child.visible:
			result.append_array(visible_tabs(child))
	return result

func load_scene(path: String):
	get_tree().paused = false
	if scene != null:
		scene.queue_free()
		await frames(3)
	scene = load(path).instantiate()
	add_child(scene)
	await frames(75)

func map_camera(at: Vector2, zoom_value: float):
	var camera = scene.get_node("Camera")
	camera._target_position = at
	camera._current_position = at
	camera._target_zoom = zoom_value
	camera._current_zoom = zoom_value
	camera._apply()
	await frames(20)

func _run():
	seed(112026)
	if "details" in OS.get_cmdline_user_args() or "tooltip" in OS.get_cmdline_user_args():
		await details()
		get_tree().quit()
		return
	if "extras" in OS.get_cmdline_user_args():
		await extras()
		get_tree().quit()
		return
	if "combat" in OS.get_cmdline_user_args():
		await combat()
		get_tree().quit()
		return
	await load_scene("res://Scenes/Map.tscn")
	await shot("worldmap-01-overview")
	var camera = scene.get_node("Camera")
	var party = scene.get_node("Party")
	var capital = scene.get_node("Settlements/CountyCapitals/County115Capital")
	await map_camera(capital.global_position, camera._max_zoom())
	await shot("worldmap-02-capital-and-roads")
	var destinations = get_tree().get_nodes_in_group(Destination.GROUP)
	destinations.sort_custom(func(a,b): return a.global_position.distance_squared_to(capital.global_position) < b.global_position.distance_squared_to(capital.global_position))
	party.global_position = capital.global_position
	for destination in destinations:
		if destination.global_position.distance_to(capital.global_position) > 220:
			party._send_to(destination.global_position)
			await frames(25)
			if not party._route.is_empty():
				print("ROUTE ", destination.name, " ", party._route.size(), " legs")
				await shot("worldmap-03-navigation-route")
				await frames(90)
				await shot("worldmap-04-travelling")
				break
	party._route.clear()
	party.global_position = capital.global_position
	var village = scene.get_node("VillageMenu")
	village.open_village(capital)
	await tabshots(village.tabs, "menu-settlement")
	village.close()
	for location in capital.locations:
		if location is QuestBoard:
			var offers = Campaign.quests_on(location)
			if not offers.is_empty():
				Campaign.accept_quest(location, offers[0])
	PauseMenu.open()
	await tabshots(PauseMenu.tabs, "menu-pause")
	PauseMenu.close()
	var squad_menu = scene.get_node("SquadMenu")
	squad_menu.choose_squad(load("res://Scenes/BoundaryMap.tscn"))
	await tabshots(squad_menu.tabs, "menu-squad-selection")
	squad_menu.close()
	for period in 3:
		TimeOfDay.forced = period
		await load_scene("res://Scenes/BoundaryMap.tscn")
		print("LAMPS ", scene.get_node("Lamps").count())
		await shot("combat-fresh-" + ["day", "dusk", "night"][period])
	print("CAPTURE COMPLETE ", count)
	get_tree().quit()

func frame3(at: Vector3, distance: float, yaw: float = 45.0, pitch: float = 40.0):
	var rig = scene.get_node("CameraRig")
	rig.set_process(false)
	rig.position = at
	rig.rotation_degrees = Vector3(-pitch, yaw, 0)
	rig.get_node("Camera3D").position = Vector3(0, 0, distance)
	await frames(10)

func combat():
	Campaign.equip(Campaign.roster.characters[0], &"item_1", load("res://Resources/Items/FragGrenade.tres"))
	Campaign.equip(Campaign.roster.characters[1], &"item_1", load("res://Resources/Items/FragGrenade.tres"))
	for period in 3:
		TimeOfDay.forced = period
		await load_scene("res://Scenes/TestMap.tscn")
		var lamps = scene.get_node("Lamps")
		print("LIGHTING LAMPS ", lamps.count())
		var level = scene.get_node("Level")
		var light_center = Vector3.ZERO
		var total = 0
		for i in level.data.count():
			if "StreetLamp1Top" in String(level.data.kind_id(i)):
				var slot = level.data.slot_at(i)
				light_center += Vector3(float(slot.x) / 2 + 0.5, slot.y, float(slot.z) / 2 + 0.5)
				total += 1
		if total > 0:
			light_center /= total
		print("LAMP CENTER ", light_center)
		scene.get_node("ActionController").deactivate()
		await frame3(light_center + Vector3(0, 1, -2), 19)
		await shot("lighting-" + ["day", "dusk", "night"][period] + "-house-and-lamps")
		await frame3(light_center + Vector3(0, 1, -2), 12, 15, 25)
		await shot("lighting-" + ["day", "dusk", "night"][period] + "-closeup")
	TimeOfDay.forced = 0
	await load_scene("res://Scenes/BoundaryMap.tscn")
	await frames(100)
	var ctrl = scene.get_node("ActionController")
	var squad = scene.get_node("PlayerSquad")
	var grid = scene.get_node("CombatGrid")
	var unit = squad.members[0]
	ctrl.deactivate()
	await frame3(Vector3(15, 1, -22), 35, 45, 55)
	await shot("combat-fresh-01-battlefield-overview")
	var enemy = scene.get_node("Units/Enemy1")
	var candidates = grid.tiles()
	candidates.sort_custom(func(a,b): return grid.tile_position(a).distance_squared_to(enemy.position) < grid.tile_position(b).distance_squared_to(enemy.position))
	for tile in candidates:
		var p = grid.tile_position(tile)
		if p.distance_to(enemy.position) > 5 and p.distance_to(enemy.position) < 9:
			unit.position = p
			if not ctrl.get_node("Shoot")._find_shots(unit).is_empty():
				break
	squad.select(unit)
	ctrl.activate(ctrl.get_node("Move"))
	await frame3((unit.position + enemy.position) / 2, 13, 45, 50)
	await shot("combat-fresh-02-movement-and-cover")
	ctrl.activate(ctrl.get_node("Overwatch"))
	await shot("combat-fresh-03-overwatch")
	ctrl.activate(ctrl.get_node("Shoot"))
	await shot("combat-fresh-04-shot-lined-up")
	await ctrl.get_node("Shoot")._fire()
	await shot("combat-busy-01-first-shot")
	await frames(160)
	unit.start_turn()
	ctrl.activate(ctrl.get_node("ThrowGrenade"))
	var action = ctrl.get_node("ThrowGrenade")
	action.set_process(false)
	var target = grid.tile_at(enemy.position)
	action._aim(target)
	await shot("combat-fresh-05-grenade-preview")
	if action._throw != null and action._throw.is_clear():
		action._throw_lined_up()
		await frames(35)
		await shot("combat-busy-02-grenade-in-flight")
		await frames(60)
		await shot("combat-busy-03-blast-aftermath")
		await frames(100)
	ctrl.deactivate()
	# More blasts use the actual grenade rules and destructible map.
	var throwing = Throwing.new(grid)
	for center in [Vector3i(8,1,-18), Vector3i(10,1,-15), Vector3i(12,1,-20), Vector3i(9,1,-12)]:
		grid.blast(grid.tile_position(center), throwing.blast_tiles(center, 4), 12, 2.0)
		Explosion.go_off(scene.get_node("TerrainDestruction"), grid.tile_position(center), 4)
		await frames(12)
	await shot("combat-busy-04-destruction-in-progress")
	await frames(120)
	await frame3(Vector3(11, 1, -17), 14, 45, 55)
	await shot("combat-busy-05-wreckage-closeup")
	await frame3(Vector3(15, 1, -22), 32, 45, 55)
	await shot("combat-busy-06-battlefield-wide")
	print("COMBAT COMPLETE")

func extras():
	await load_scene("res://Scenes/Map.tscn")
	var capital = scene.get_node("Settlements/CountyCapitals/County115Capital")
	var camera = scene.get_node("Camera")
	var party = scene.get_node("Party")
	var destination = scene.get_node("Settlements/Hamlets/County115Hamlet5") if scene.has_node("Settlements/Hamlets/County115Hamlet5") else null
	for candidate in get_tree().get_nodes_in_group(Destination.GROUP):
		if candidate.name == "County115Hamlet5":
			destination = candidate
	assert(destination != null)
	party.global_position = capital.global_position
	party._send_to(destination.global_position)
	await frames(20)
	var box = Rect2(capital.global_position, Vector2.ONE)
	for point in party._route:
		box = box.expand(point)
	var zoom_fit = minf(1000.0 / maxf(box.size.x, 100), 480.0 / maxf(box.size.y, 100))
	await map_camera(box.get_center(), minf(zoom_fit, camera._max_zoom()))
	await shot("worldmap-03-navigation-route")
	await frames(200)
	await shot("worldmap-04-travelling")
	InputDevice.use_gamepad(true)
	await shot("worldmap-05-controller-navigation")
	party._route.clear()
	var switch = scene.find_child("BorderSwitch", true, false)
	if switch != null:
		switch.shown = false
	await map_camera(capital.global_position, camera._max_zoom() / 3)
	await shot("worldmap-06-regional-geography")
	var menu = scene.get_node("VillageMenu")
	for rank in ["DuchyCapitals", "KingdomCapitals"]:
		var settlement = scene.get_node("Settlements/" + rank).get_child(0)
		party.position = settlement.position
		menu.open_village(settlement)
		menu.tabs.current_tab = 1
		await shot("menu-settlement-" + slug(menu.tabs.get_tab_title(1)))
		menu.close()
	PauseMenu.open()
	PauseMenu.tabs.current_tab = 2
	PauseMenu._roster._pages.current_tab = 2
	await shot("menu-roster-skills-controller-prompts")
	PauseMenu.close()
	InputDevice.use_gamepad(false)
	TimeOfDay.forced = 2
	await load_scene("res://Scenes/TestMap.tscn")
	scene.get_node("ActionController").deactivate()
	await frame3(Vector3(25,3,-21), 14, 45, 55)
	scene.get_node("Level").cut_away(5)
	await shot("lighting-night-building-upper-floor-cutaway")
	scene.get_node("Level").cut_away(2)
	await shot("lighting-night-building-ground-floor-cutaway")
	PauseMenu.open()
	PauseMenu.tabs.current_tab = 4
	await shot("menu-pause-system-in-combat")
	PauseMenu.close()
	TimeOfDay.forced = 0
	await load_scene("res://Scenes/BoundaryMap.tscn")
	await frames(150)
	var ctrl = scene.get_node("ActionController")
	var squad = scene.get_node("PlayerSquad")
	var grid = scene.get_node("CombatGrid")
	var enemy = scene.get_node("Units/Enemy1")
	var unit = squad.members[0]
	var candidates = grid.tiles()
	candidates.sort_custom(func(a,b): return grid.tile_position(a).distance_squared_to(enemy.position) < grid.tile_position(b).distance_squared_to(enemy.position))
	for tile in candidates:
		var p = grid.tile_position(tile)
		if p.distance_to(enemy.position) > 5 and p.distance_to(enemy.position) < 8:
			unit.position = p
			if not ctrl.get_node("Shoot")._find_shots(unit).is_empty():
				break
	squad.select(unit)
	ctrl.deactivate()
	await frame3((unit.position + enemy.position) / 2, 13, 45, 50)
	unit.overwatching = true
	var points: Array[Vector3] = []
	for tile in grid.neighbours(grid.tile_at(enemy.position)):
		points.append(grid.tile_position(tile))
		break
	var reactions = scene.get_node("Reactions")
	reactions.walk(enemy, points, 4.0)
	await frames(12)
	await shot("combat-fresh-06-reaction-window")
	await frames(300)
	InputDevice.use_gamepad(true)
	ctrl.activate(ctrl.get_node("Move"))
	await shot("combat-controller-prompts")
	InputDevice.use_gamepad(false)
	ctrl.deactivate()
	for i in 4:
		enemy.take_damage(1, unit.position)
		unit.take_damage(1, enemy.position)
		await frames(35)
	var throwing = Throwing.new(grid)
	for center in [Vector3i(7,1,-17),Vector3i(9,1,-16),Vector3i(11,1,-18),Vector3i(10,1,-14)]:
		grid.blast(grid.tile_position(center), throwing.blast_tiles(center, 5), 20, 2.0)
		await frames(25)
	enemy.take_damage(100, unit.position)
	await frames(100)
	await frame3(Vector3(10,1,-16), 13,45,55)
	await shot("combat-blood-01-wreckage-and-casualty")
	await frame3(Vector3(10,1,-16), 19,45,55)
	await shot("combat-blood-02-busy-battlefield")
	var banner = scene.get_node("HUD/TurnBanner")
	banner.announce("Victory")
	await shot("combat-ui-victory-banner")
	await frames(180)
	banner.announce("Defeat")
	await shot("combat-ui-defeat-banner")
	print("EXTRAS COMPLETE")

func details():
	await load_scene("res://Scenes/Map.tscn")
	PauseMenu.open()
	PauseMenu.tabs.current_tab = 2
	PauseMenu._roster._pages.current_tab = 2
	var skills = PauseMenu._roster._pages.get_tab_control(2)
	skills._by_keyboard = true
	skills.focus_selection()
	await frames(5)
	skills._show_tooltip()
	await shot("menu-roster-skill-description")
	PauseMenu.close()
	if "tooltip" in OS.get_cmdline_user_args():
		return
	Campaign.roster.characters[0].item_1 = load("res://Resources/Items/Medkit.tres")
	Campaign.roster.characters[0].weapon_2 = load("res://Resources/Items/Shortsword.tres")
	TimeOfDay.forced = 0
	await load_scene("res://Scenes/TestMap.tscn")
	await frames(150)
	var ctrl = scene.get_node("ActionController")
	ctrl.deactivate()
	await frame3(Vector3(25,2,-21), 13,45,55)
	scene.get_node("HUD/FloorSelector").choose(1)
	await shot("combat-building-floor-selector-and-interior")
	var unit = scene.get_node("PlayerSquad").members[0]
	unit.take_damage(3, unit.position + Vector3(0,0,-4))
	await frame3(unit.position, 8,45,50)
	ctrl.activate(ctrl.get_node("UseMedkit"))
	await shot("combat-ui-medkit-target")
	ctrl.deactivate()
	var enemy = scene.get_node("Units/Enemy1")
	enemy.position = unit.position + Vector3(1,0,0)
	ctrl.activate(ctrl.get_node("Strike"))
	await shot("combat-ui-melee-target")
	ctrl.deactivate()
	TimeOfDay.forced = 0
	await load_scene("res://Scenes/BoundaryMap.tscn")
	await frames(150)
	scene.get_node("ActionController").deactivate()
	var level = scene.get_node("Level")
	var terrain = scene.get_node("TerrainDestruction")
	var grid = scene.get_node("CombatGrid")
	var throwing = Throwing.new(grid)
	var center = Vector3(12,1,-15)
	for i in level.data.count():
		if "Crate" in String(level.data.kind_id(i)):
			var p = LevelData.box_center(level.data.slot_at(i))
			if p.distance_to(center) < 13:
				terrain.break_piece(i)
	for p in [Vector3(7,1,-16),Vector3(12,1,-11),Vector3(16,1,-18),Vector3(10,1,-8)]:
		var tile = grid.tile_at(p)
		grid.blast(p, throwing.blast_tiles(tile, 7), 30, 3.0)
		await frames(20)
	await frames(120)
	await frame3(center, 17,45,55)
	await shot("combat-clean-01-heavy-destruction")
	await frame3(center, 12,45,55)
	await shot("combat-clean-02-debris-closeup")
	for victim in get_tree().get_nodes_in_group("enemies"):
		if victim.position.distance_to(center) < 18:
			victim.take_damage(100, center)
	await frames(180)
	await shot("combat-blood-03-heavy-destruction-closeup")
	await frame3(center, 17,45,55)
	await shot("combat-blood-04-heavy-destruction-wide")
	print("DETAILS COMPLETE")
