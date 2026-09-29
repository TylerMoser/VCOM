## Ends the game once nobody is left on the roster: the world map stops,
## "Game Over" comes up in the battles' banner, and the game quits as the
## banner starts to fade.
##
## It watches the roster while the world map is in the tree, so it goes off
## when the map comes back from the battle that killed the last of them,
## after that battle's "Defeat", or as the map opens on an empty roster.
## Everything but this stops with the tree paused. This runs on through the
## pause and sits over the menus, so a menu opened meanwhile can neither hold
## it up nor cover it.
class_name GameOver
extends CanvasLayer

## Over the menus' layer ([constant TabbedMenu.LAYER]).
const LAYER := TabbedMenu.LAYER + 1

var _banner: TurnBanner
var _over := false


func _init() -> void:
	layer = LAYER
	process_mode = PROCESS_MODE_ALWAYS
	# Where the combat HUD has its banner: centred, 64 px from the top.
	_banner = TurnBanner.new()
	_banner.anchor_left = 0.5
	_banner.anchor_right = 0.5
	_banner.offset_top = 64.0
	_banner.offset_bottom = 64.0
	_banner.grow_horizontal = Control.GROW_DIRECTION_BOTH
	add_child(_banner)


func _process(_delta: float) -> void:
	if not _over and Campaign.roster.characters.is_empty():
		_end()


func _end() -> void:
	_over = true
	get_tree().paused = true
	_banner.announce("Game Over")
	await _banner.fading
	get_tree().quit()
