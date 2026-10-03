## Which the player is using, a gamepad or the keyboard and mouse: whichever
## they touched last. The game plays with either, and whatever shows a control
## (the button prompts, the tile cursor, the world map's reticle) asks this
## which to show.
##
## An autoload ([code]InputDevices[/code]) watches every input event, even
## while the game is paused behind a menu, and flips [member gamepad] on a
## button pressed or a stick pushed past [constant STICK_THRESHOLD], and back
## on a key, a mouse button, or the mouse moved further than
## [constant MOUSE_THRESHOLD]: the game moves the pointer itself now and then
## (changing its shape sends a motion of its own), which must not count. The
## mouse pointer is hidden while the gamepad is in use, since nothing follows
## it then.
##
## Everything is static, so a script reads [member gamepad] by the class's name
## and never names the autoload: a probe can then still name it (see Gotchas in
## CLAUDE.md). [member instance] is the autoload, for its [signal changed].
class_name InputDevice
extends Node

## The gamepad was picked up, or put down for the keyboard and mouse.
signal changed(gamepad: bool)

## How far a stick or trigger must go to count as the gamepad being used.
const STICK_THRESHOLD := 0.5
## How far, in pixels, the mouse must move in one event to count as used.
const MOUSE_THRESHOLD := 3.0

## Whether the gamepad was used last.
static var gamepad := false
## The autoload, once it is in the tree.
static var instance: InputDevice


func _init() -> void:
	# The menus pause the game; the gamepad is still picked up behind them.
	process_mode = PROCESS_MODE_ALWAYS


func _enter_tree() -> void:
	instance = self


func _exit_tree() -> void:
	if instance == self:
		instance = null


func _input(event: InputEvent) -> void:
	if event is InputEventJoypadButton:
		if event.is_pressed():
			use_gamepad(true)
	elif event is InputEventJoypadMotion:
		if absf((event as InputEventJoypadMotion).axis_value) >= STICK_THRESHOLD:
			use_gamepad(true)
	elif event is InputEventKey or event is InputEventMouseButton:
		if event.is_pressed():
			use_gamepad(false)
	elif event is InputEventMouseMotion:
		if (event as InputEventMouseMotion).relative.length() >= MOUSE_THRESHOLD:
			use_gamepad(false)


## Switches to the gamepad, or back to the keyboard and mouse, as using one
## does. A probe can call it to stand in for picking the gamepad up.
static func use_gamepad(on: bool) -> void:
	if gamepad == on:
		return
	gamepad = on
	Input.mouse_mode = Input.MOUSE_MODE_HIDDEN if on else Input.MOUSE_MODE_VISIBLE
	if instance != null:
		instance.changed.emit(on)


## Connects [param callable] to [signal changed], if the autoload is there.
static func watch(callable: Callable) -> void:
	if instance != null and not instance.changed.is_connected(callable):
		instance.changed.connect(callable)


## Where the player is pointing on [param viewport]'s screen: the mouse, or
## with the gamepad the middle of the screen, where a reticle is drawn.
static func pointer_position(viewport: Viewport) -> Vector2:
	if gamepad:
		return viewport.get_visible_rect().size * 0.5
	return viewport.get_mouse_position()


## Where the player is pointing in [param item]'s canvas, as
## [method CanvasItem.get_global_mouse_position] gives the mouse: the world
## map's own coordinates, for anything on it.
static func pointer_on_canvas(item: CanvasItem) -> Vector2:
	return item.get_canvas_transform().affine_inverse() * pointer_position(item.get_viewport())
