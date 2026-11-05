## Closes in on the squad, and shoots whoever it has the best odds on.
##
## Each action, the first of these that it can do:
##
## - Its magazine empty: reloads, as XCOM's aliens do.
## - Next to a squad member it can shoot: shoots them. Once it is there, every
##   action it has left goes on them.
## - Any action but its last: moves as close as it can to the nearest squad
##   member, up to [member Unit.move_range] tiles.
## - Its last action: shoots whoever it has the best odds on, or moves closer
##   if it cannot see anyone.
##
## When it cannot get any closer it shoots rather than waste the action; with
## nothing to shoot either it tops up a part-spent magazine, and failing that
## it ends its turn.
class_name AssaultAI
extends EnemyAI


func choose_action(tactics: Tactics) -> AIAction:
	var empty: Variant = tactics.reload(true)
	if empty != null:
		return empty

	var point_blank: Variant = tactics.best_shot(tactics.adjacent_foes())
	if point_blank != null:
		return point_blank

	var easiest: Variant = tactics.best_shot(tactics.foes)
	if tactics.unit.actions_remaining <= 1 and easiest != null:
		return easiest
	var advance: Variant = tactics.advance(tactics.unit.move_range)
	if advance != null:
		return advance
	if easiest != null:
		return easiest
	var top_up: Variant = tactics.reload()
	return top_up if top_up != null else AIAction.end_turn()
