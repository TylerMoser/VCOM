## Pick an enemy to fire at, for one action point. Only a unit carrying a gun
## has it, and it fires [member Unit.weapon], spending one of its rounds: with
## the magazine empty it is dimmed until a reload ([ReloadAction]).
##
## The targets on offer are whatever [LineOfSight] says the unit can see, so a
## unit behind high cover leans out around it to find its shot. The tile it
## leans out to is marked on the map, and the sight line, reticle and target
## panel all follow the target. A target it can only see where that target
## leans out of its own cover is seen leaning out there for as long as it is
## lined up, and through the shot.
##
##   Cycle targets - Tab, or Shift+Tab to go back; or click another target.
##   Fire          - Enter or Space, click the target lined up (either
##                   button), or click the tick beside its odds.
##   Show the sum  - hold Ctrl to open the breakdown behind the hit chance.
##
## A click on a target other than the one lined up lines it up rather than
## firing at it, so a shot is never taken at odds the player has not seen. The
## cursor turns to a hand over any target.
##
## With the gamepad LB / RB cycle the targets, A fires, and holding LT opens
## the breakdown. The tile cursor goes to the target lined up, taking the
## camera with it, and moving the cursor on to another target lines that one
## up.
##
## A shot that needs a step out plays it: the unit leans out to the tile it
## found the shot from, fires, and settles back into its cover. Whether the
## shot lands is [HitChance]'s business, and where the round goes is
## [Ballistics]'s. While a target is lined up the unit turns to it with its
## gun raised, and keeps facing it as it steps out and back.
class_name ShootAction
extends UnitAction

## Action points a shot costs.
const COST := 1
## Marker on the tile the shooter leans out to, when the shot needs one.
const STEP_OUT_LAYER := &"shoot_step_out"
const STEP_OUT_COLOR := Color(1.0, 0.45, 0.35)

## Seconds the unit takes to lean out of cover, and to settle back in.
@export var step_out_seconds := 0.15
@export var enemy_group := &"enemies"
@export var overlay_path: NodePath = ^"../../HUD/ShotOverlay"

var _unit: Unit
var _shots: Array[LineOfSight.Shot] = []
## Index into [member _shots] of the target currently lined up.
var _index := 0
## The odds of the shot lined up, worked out once when it is lined up so the
## number the player is shown is the number that gets rolled.
var _estimate: HitChance.Estimate
var _overlay: ShotOverlay
## The target lined up, while the shot sees it only where it leans out of its
## cover, and so has its figure leaning out; null for one seen where it stands.
var _leaning: Unit


func _init() -> void:
	display_name = "Shoot"
	required_tag = Item.GUN


func _ready() -> void:
	set_process(false)
	_overlay = get_node_or_null(overlay_path) as ShotOverlay
	if _overlay == null:
		push_error("ShootAction: no ShotOverlay at '%s'." % overlay_path)
	else:
		_overlay.confirmed.connect(_on_confirmed)


# Follow the mouse every frame, not only when it moves, as the camera pans and
# turns under a still cursor.
func _process(_delta: float) -> void:
	point_at_target(not controller.busy and _index_of(hovered_unit()) >= 0)


func is_available(unit: Unit) -> bool:
	return unit.actions_remaining >= COST and unit.can_fire() and not _find_shots(unit).is_empty()


func begin(unit: Unit) -> void:
	_unit = unit
	_shots = _find_shots(unit)
	_index = 0
	_show_shot()
	set_process(true)


func end() -> void:
	set_process(false)
	point_at_target(false)
	if _unit != null:
		_unit.stand_easy()
	_lean_back()
	_unit = null
	_shots.clear()
	_index = 0
	_estimate = null
	_clear_aim()


func handle_input(event: InputEvent) -> bool:
	# Tab belongs to the targets for as long as the action is up, so it never
	# cycles the squad out from under the player mid-aim.
	if _shots.is_empty():
		return false
	# Shift+Tab also matches the plain Tab action, so check it first.
	if event.is_action_pressed(&"previous_target"):
		_cycle(-1)
	elif event.is_action_pressed(&"next_target"):
		_cycle(1)
	elif event.is_action_pressed(&"confirm_action"):
		_fire()
	else:
		return _click(clicked_unit(event))
	return true


## The shot lined up right now, or null while the unit has no targets.
func current_shot() -> Variant:
	return _shots[_index] if not _shots.is_empty() else null


## Takes the shot that is lined up: leans out if it needs to, rolls against
## the odds the player was shown, calls the result once the round lands, and
## comes back to cover. The action is spent either way.
func _fire() -> void:
	var shot: Variant = current_shot()
	if shot == null:
		return
	var aimed := shot as LineOfSight.Shot
	var estimate := _estimate
	var unit := _unit
	var cover := unit.global_position
	# Read where to call the result now: a target that dies is gone by then.
	var mark := _eye_of(aimed)

	unit.spend_actions(COST)
	# Drop the aim before anything moves: the target may be about to leave
	# the map, and the sight line is drawn from where the unit was.
	_clear_aim()
	controller.busy = true

	if aimed.stepped_out:
		await unit.walk([controller.grid.tile_position(aimed.from)], step_out_seconds, true)

	var show_rounds := _overlay.show_rounds if _overlay != null else Callable()
	var outcome: Ballistics.Outcome = await unit.shoot_at(
		aimed, estimate.chance, controller.grid, show_rounds
	)
	if _overlay != null:
		_overlay.flash_result(mark, "%d" % outcome.damage if outcome.hit else "MISS", outcome.hit)

	if aimed.stepped_out:
		await unit.walk([cover], step_out_seconds, true)
	completed.emit()


func _cycle(step: int) -> void:
	_index = posmod(_index + step, _shots.size())
	_show_shot()


## Fires on [param clicked] if it is the target lined up, lines it up if it is
## another target, and leaves anything else alone, returning false.
func _click(clicked: Unit) -> bool:
	var at := _index_of(clicked)
	if at < 0:
		return false
	if at == _index:
		_fire()
	else:
		_index = at
		_show_shot()
	return true


func confirm_hint() -> String:
	return "Fire"


func cycles_targets() -> bool:
	return true


## The cursor moved on to [param tile]: a target standing there is lined up.
func cursor_moved(tile: Vector3i) -> void:
	for at in _shots.size():
		if at != _index and controller.grid.tile_at(_shots[at].target.global_position) == tile:
			_index = at
			_show_shot()
			return


## Where [param target] is among the targets on offer, or -1.
func _index_of(target: Unit) -> int:
	if target == null:
		return -1
	for at in _shots.size():
		if _shots[at].target == target:
			return at
	return -1


## The tick on the target panel: fire, if this is what is lined up.
func _on_confirmed() -> void:
	if controller.active == self and not controller.busy and current_shot() != null:
		_fire()


func _find_shots(unit: Unit) -> Array[LineOfSight.Shot]:
	var enemies: Array[Unit] = []
	for node in get_tree().get_nodes_in_group(enemy_group):
		var enemy := node as Unit
		if enemy != null:
			enemies.append(enemy)
	return LineOfSight.new(controller.grid).find_shots(unit, enemies)


func _show_shot() -> void:
	var shot: Variant = current_shot()
	if shot == null:
		return
	var aimed := shot as LineOfSight.Shot
	_estimate = HitChance.for_shot(_unit, aimed)

	if aimed.stepped_out:
		controller.highlights.set_layer(STEP_OUT_LAYER, {aimed.from: STEP_OUT_COLOR})
	else:
		controller.highlights.clear_layer(STEP_OUT_LAYER)

	var eye := controller.grid.cell_center(LineOfSight.eye_cell(aimed.from))
	# Whoever was lined up before draws back, and this one leans out if that is
	# where the shot sees it: before the aim, which is taken at where it leans.
	if _leaning != aimed.target or not aimed.leaning:
		_lean_back()
	if aimed.leaning:
		_leaning = aimed.target
		aimed.target.lean_out(aimed.seen_at, eye, controller.grid)
	_unit.aim_at(_unit.aim_point(aimed.target, controller.grid))
	if InputDevice.gamepad and controller.cursor != null:
		controller.cursor.snap_to(aimed.target_tile)
	if _overlay != null:
		_overlay.show_shot(eye, _eye_of(aimed), aimed, _estimate, true)


## Where [param shot]'s target's eye is for the sight line, the reticle and the
## result called over it: over its tile, or as far out of it as its figure leans
## while the shot has it leaning out.
func _eye_of(shot: LineOfSight.Shot) -> Vector3:
	return controller.grid.cell_center(LineOfSight.eye_cell(shot.target_tile)) + shot.target.lean()


## Has the target that was leaning out for the shot lined up draw back behind
## its cover, if it is still there to.
func _lean_back() -> void:
	if is_instance_valid(_leaning):
		_leaning.lean_back()
	_leaning = null


func _clear_aim() -> void:
	controller.highlights.clear_layer(STEP_OUT_LAYER)
	if _overlay != null:
		_overlay.clear()
