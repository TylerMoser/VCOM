## Use a medkit on a wounded ally standing next to the unit, or on the unit
## itself, for one action, giving back the medkit's [member Medkit.heal] in
## health, never above the most. It can be taken only while the unit has a use
## to draw on ([method supplier]) and someone to treat: the unit itself wounded,
## or a wounded ally next to it, next to as [method Tactics.is_next_to] has it,
## as a strike's reach is.
##
## A use is drawn from the unit's own medkits first ([member Unit.medkits]: one
## a battle for each medkit it carries), and once those are spent, or if it
## carries none, from a squad member next to it whose medkits have a use left
## ([method _lenders]): the use is theirs, so it is gone for them too. A unit
## carrying a medkit always has the action, dimmed with nothing to draw on; one
## carrying none has it only while such a squad member stands next to it
## ([method is_granted]).
##
## Lined up as a strike is: on offer are the wounded allies next to the unit,
## nearest first, then the unit itself if it is wounded, and the line, reticle
## and panel follow the one lined up, in green (no line to the unit itself), the
## panel showing the health they would gain rather than a chance, since nothing
## is rolled.
##
##   Cycle allies - Tab, or Shift+Tab to go back; or click another.
##   Heal         - Enter or Space, click the ally lined up (either button),
##                  or click the tick beside what they would gain.
##
## As with a strike, a click on another ally lines them up rather than healing
## them, and the cursor turns to a hand over any of them. A left click on one of
## them is the action's, not a change of selection ([method takes_click_on]);
## on any other squad member it selects them, as ever. With the gamepad, as
## a strike is lined up: LB / RB, A, and the tile cursor on the ally.
##
## While an ally is lined up the unit turns to them, and lined up on itself it
## looks down at its own middle; the panel names whose medkit it would be, when
## not the unit's own. Using it, the unit takes the medkit off its belt (a
## borrowed one appears in its hand) and holds it out, or presses it to itself,
## the one treated mends as it does ([method Unit.use_medkit]), with what they
## gained called over them, and the action is done once the medkit is back on
## the belt. The medkit is kept: it is spent only for the rest of the battle.
class_name UseMedkitAction
extends UnitAction

## Action points using a medkit costs: what a strike does.
const COST := 1

## The unit's own side, whose wounded it can treat.
@export var ally_group := &"players"
@export var overlay_path: NodePath = ^"../../HUD/ShotOverlay"

var _unit: Unit
var _targets: Array[Unit] = []
## Index into [member _targets] of the ally currently lined up.
var _index := 0
var _overlay: ShotOverlay


func _init() -> void:
	display_name = "Use Medkit"
	required_tag = Item.MEDKIT


func _ready() -> void:
	set_process(false)
	_overlay = get_node_or_null(overlay_path) as ShotOverlay
	if _overlay == null:
		push_error("UseMedkitAction: no ShotOverlay at '%s'." % overlay_path)
	else:
		_overlay.confirmed.connect(_on_confirmed)


# Every frame, as the camera moves under a still cursor (see ShootAction).
func _process(_delta: float) -> void:
	point_at_target(not controller.busy and _targets.has(hovered_unit()))


## A unit carrying a medkit has it, as the tag says, and so does one standing
## next to a squad member with a medkit use left to lend, for as long as it
## stands there.
func is_granted(unit: Unit) -> bool:
	return super(unit) or not _lenders(unit).is_empty()


func is_available(unit: Unit) -> bool:
	return supplier(unit) != null and unit.actions_remaining >= COST and not _patients(unit).is_empty()


## The medkit uses [param unit] can draw on where it stands, for the count on
## the action's button: its own, and those of every squad member next to it
## with any left.
func uses_left(unit: Unit) -> int:
	var uses := unit.medkits.size()
	for lender in _lenders(unit):
		uses += lender.medkits.size()
	return uses


## Whose medkit [param unit] would use now: its own while it has a use left,
## else the first squad member next to it with one, in the squad's order
## ([method _lenders]); null with none.
func supplier(unit: Unit) -> Unit:
	if not unit.medkits.is_empty():
		return unit
	var lenders := _lenders(unit)
	return lenders[0] if not lenders.is_empty() else null


func begin(unit: Unit) -> void:
	_unit = unit
	_targets = _patients(unit)
	_index = 0
	_show_target()
	set_process(true)


func end() -> void:
	set_process(false)
	point_at_target(false)
	if _unit != null:
		_unit.stand_easy()
	_unit = null
	_targets.clear()
	_index = 0
	if _overlay != null:
		_overlay.clear()


func handle_input(event: InputEvent) -> bool:
	# Tab belongs to the allies for as long as the action is up, as it does to
	# the targets while a strike is lined up.
	if _targets.is_empty():
		return false
	# Shift+Tab also matches the plain Tab action, so check it first.
	if event.is_action_pressed(&"previous_target"):
		_cycle(-1)
	elif event.is_action_pressed(&"next_target"):
		_cycle(1)
	elif event.is_action_pressed(&"confirm_action"):
		_heal()
	else:
		return _click(clicked_unit(event))
	return true


## The ally lined up right now (the unit itself, if that is who is lined up),
## or null while the unit has none to treat.
func current_target() -> Variant:
	return _targets[_index] if not _targets.is_empty() else null


func confirm_hint() -> String:
	return "Heal"


func cycles_targets() -> bool:
	return true


## Nothing is rolled, so LT has no sum to open.
func shows_odds() -> bool:
	return false


## A left click on an ally on offer lines them up or heals them, rather than
## selecting them; on any other squad member it still selects. The unit itself
## is selected already, so a click on it, while it is on offer, is the
## action's too.
func takes_click_on(unit: Unit) -> bool:
	return _targets.has(unit)


## The cursor moved on to [param tile]: a wounded ally beside the unit there, or
## the unit itself if wounded and the tile is its own, is lined up.
func cursor_moved(tile: Vector3i) -> void:
	for at in _targets.size():
		if at != _index and controller.grid.tile_at(_targets[at].global_position) == tile:
			_index = at
			_show_target()
			return


## Uses a medkit on the ally lined up, and calls what they gained over them as
## they mend. Nothing is rolled: it always works.
func _heal() -> void:
	var lined_up: Variant = current_target()
	if lined_up == null:
		return
	var target := lined_up as Unit
	var unit := _unit
	var from := supplier(unit)
	if from == null:
		return
	var grid := controller.grid
	var mark := grid.cell_center(LineOfSight.eye_cell(grid.tile_at(target.global_position)))

	unit.spend_actions(COST)
	if _overlay != null:
		_overlay.clear()
	# Busy while the medkit is out, as a strike is while the swing plays.
	controller.busy = true
	var gained: int = await unit.use_medkit(target, from)
	if _overlay != null:
		_overlay.flash_heal(mark, "+%d HP" % gained)
	await unit.recover()
	completed.emit()


func _cycle(step: int) -> void:
	_index = posmod(_index + step, _targets.size())
	_show_target()


## Heals [param clicked] if it is the ally lined up, lines it up if it is
## another of them, and leaves anything else alone, returning false.
func _click(clicked: Unit) -> bool:
	var at := _targets.find(clicked) if clicked != null else -1
	if at < 0:
		return false
	if at == _index:
		_heal()
	else:
		_index = at
		_show_target()
	return true


## The tick on the target panel: heal, if this is what is lined up.
func _on_confirmed() -> void:
	if controller.active == self and not controller.busy and current_target() != null:
		_heal()


## Whom [param unit] can treat: the living, wounded allies standing next to it,
## its own side, nearest first, then itself if it is wounded. Last, so the ally
## beside it comes up first, as a strike's nearest target does.
func _patients(unit: Unit) -> Array[Unit]:
	var grid := controller.grid
	var tile := grid.tile_at(unit.global_position)
	var adjacent: Array[Unit] = []
	for node in get_tree().get_nodes_in_group(ally_group):
		var ally := node as Unit
		if ally == null or ally == unit or not ally.is_wounded():
			continue
		if Tactics.is_next_to(tile, grid.tile_at(ally.global_position)):
			adjacent.append(ally)
	var from := unit.global_position
	adjacent.sort_custom(func(a: Unit, b: Unit) -> bool:
		return from.distance_squared_to(a.global_position) < from.distance_squared_to(b.global_position))
	if unit.is_wounded():
		adjacent.append(unit)
	return adjacent


## The living squad members standing next to [param unit], itself left out,
## with a medkit use left that it can draw on, in the squad's order.
func _lenders(unit: Unit) -> Array[Unit]:
	var lenders: Array[Unit] = []
	var grid := controller.grid
	var tile := grid.tile_at(unit.global_position)
	for node in get_tree().get_nodes_in_group(ally_group):
		var ally := node as Unit
		if ally == null or ally == unit or ally.medkits.is_empty():
			continue
		if Tactics.is_next_to(tile, grid.tile_at(ally.global_position)):
			lenders.append(ally)
	return lenders


## The health [param target] would gain from the next medkit the unit uses
## ([method supplier]): its [member Medkit.heal], or what it is missing if that
## is less.
func _gain(target: Unit) -> int:
	var from := supplier(_unit)
	if from == null:
		return 0
	return mini(from.medkits[0].heal, target.max_health - target.health)


## What the panel calls the medkit the unit would use: plainly a Medkit when it
## is its own, else whose it is.
func _kit_name() -> String:
	var from := supplier(_unit)
	return "Medkit" if from == null or from == _unit else "%s's Medkit" % from.display_name


func _show_target() -> void:
	var lined_up: Variant = current_target()
	if lined_up == null:
		return
	var target := lined_up as Unit
	_unit.attend(target)
	if InputDevice.gamepad and controller.cursor != null:
		controller.cursor.snap_to(controller.grid.tile_at(target.global_position))
	if _overlay != null:
		var grid := controller.grid
		_overlay.show_heal(
			grid.cell_center(LineOfSight.eye_cell(grid.tile_at(_unit.global_position))),
			grid.cell_center(LineOfSight.eye_cell(grid.tile_at(target.global_position))),
			target,
			_gain(target),
			true,
			_kit_name(),
		)
