## How a computer-controlled unit spends its turn, one action at a time.
##
## Each kind of enemy gets a subclass, and each enemy is handed one through
## [member Unit.ai], the way it is handed a [Weapon]. On the enemies' turn the
## [TurnManager] asks the unit's AI for an action, carries it out, and asks
## again until the unit is out of actions or the AI ends its turn.
##
## An AI only decides. It looks at the fight through the [Tactics] it is given
## and answers with an [AIAction]. Walking, shooting, the squad's reactions
## and the camera all belong to the turn manager, so every kind of enemy moves
## and fires by the same rules. One AI resource is shared by every unit that
## uses it, so, like a weapon, it must not keep anything between calls.
class_name EnemyAI
extends Resource


## What [member Tactics.unit] does with its next action. The unit's
## [member Unit.actions_remaining] still counts that action, so 1 means it is
## the last. The base AI does nothing and ends the unit's turn.
func choose_action(_tactics: Tactics) -> AIAction:
	return AIAction.end_turn()
