## Plays out a shot the player is not lining up on the action bar: an enemy's
## fire, or a squad member's reaction. The shooter leans out of cover if the
## shot needs it, the sight line hangs long enough to be seen, the round flies
## to wherever [Ballistics] sends it, the result is called over the target as
## it lands, and the shooter settles back into cover.
##
## The shot itself is [method Unit.shoot_at], so a shot played out here means
## the same as one taken from the action bar.
class_name ShotPlayback
extends RefCounted

## Seconds the shooter takes to lean out of cover, and to settle back in.
var step_out_seconds := 0.2
## How long the sight line hangs before the shot goes off.
var aim_seconds := 0.45
## True for the squad's own fire. It is drawn as the player's aim, reticle and
## odds, rather than as the paler line of fire coming in.
var player_fire := false

var _grid: CombatGrid
## Null in a scene without one: the shot still happens, it just is not drawn.
var _overlay: ShotOverlay


func _init(grid: CombatGrid, overlay: ShotOverlay) -> void:
	_grid = grid
	_overlay = overlay


## [param shooter] takes [param shot], rolling against [param estimate]: the
## odds already worked out for it, which are the odds the player was shown.
## Await it to wait until the shooter is back in cover. Returns whether the
## shot hit.
func play(shooter: Unit, shot: LineOfSight.Shot, estimate: HitChance.Estimate) -> bool:
	var cover := shooter.global_position
	# Read where to call the result now: a target that dies is gone by then.
	var mark := _grid.cell_center(LineOfSight.eye_cell(shot.target_tile))

	if shot.stepped_out:
		await shooter.walk([_grid.tile_position(shot.from)], step_out_seconds)
	var show_rounds := Callable()
	if _overlay != null:
		var eye := _grid.cell_center(LineOfSight.eye_cell(shot.from))
		if player_fire:
			_overlay.show_shot(eye, mark, shot, estimate)
		else:
			_overlay.show_incoming(eye, mark)
		await _grid.get_tree().create_timer(aim_seconds).timeout
		# The round takes over from the sight line once it is fired.
		_overlay.clear()
		show_rounds = _overlay.show_rounds

	var outcome: Ballistics.Outcome = await shooter.shoot_at(shot, estimate.chance, _grid, show_rounds)
	if _overlay != null:
		# Under the target when the odds panel holds the space over it.
		var text := "%d" % shooter.weapon.damage if outcome.hit else "MISS"
		_overlay.flash_result(mark, text, outcome.hit, player_fire)

	if shot.stepped_out:
		await shooter.walk([cover], step_out_seconds)
	return outcome.hit
