## Bakes the new map's navigation without the editor: the same bake as the
## Bake Navigation button on the Navigation node ([MapNavigation]) of
## Scenes/Map.tscn, from the scene as saved. Run from vcom/:
##
##   godot --headless --path . --script res://Scripts/WorldMap/BakeMapNavigation.gd
##   godot --headless --path . --script res://Scripts/WorldMap/BakeMapNavigation.gd -- --check
##   godot --headless --path . --script res://Scripts/WorldMap/BakeMapNavigation.gd -- <scene>
##
## It prints the bake's report and exits 0, or 1 after an error. With
## [code]--check[/code] it bakes nothing: it says whether the baked navigation
## matches the scene, and exits 1 when it does not. The scene defaults to
## res://Scenes/Map.tscn; its first [MapNavigation] node is the one baked.
##
## The scene is read as saved: in the editor, save it first, or use the button.
## A script error does not end a --script run (Godot sits idle after it), so
## give a scripted run a timeout.
extends SceneTree

const DEFAULT_SCENE := "res://Scenes/Map.tscn"


func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	var check := args.has("--check")
	var scene_path := DEFAULT_SCENE
	for arg in args:
		if not arg.begins_with("--"):
			scene_path = arg
	quit(_run(scene_path, check))


func _run(scene_path: String, check: bool) -> int:
	var packed := load(scene_path) as PackedScene
	if packed == null:
		push_error("BakeMapNavigation: cannot load '%s'." % scene_path)
		return 1
	var scene := packed.instantiate()
	var found := scene.find_children("*", "Node", true, false)
	found.push_front(scene)
	var navigation: MapNavigation = null
	for node in found:
		if node is MapNavigation:
			navigation = node
			break
	var code := 0
	if navigation == null:
		push_error("BakeMapNavigation: '%s' has no MapNavigation node." % scene_path)
		code = 1
	elif check:
		var reason := navigation.stale_reason()
		if reason.is_empty():
			print("BakeMapNavigation: %s matches %s." % [navigation.data_path, scene_path])
		else:
			print("BakeMapNavigation: stale: %s." % reason)
			code = 1
	elif navigation.bake() == null:
		code = 1
	scene.free()
	return code
