## The odds a shot lands, worked out from the shooter, the target and the
## ground between them:
##
##   Aim - Evasion - Cover + Flanking + Height - Distance
##
## Every term is whole percentage points, and the total is held between 0 and
## 100. The terms are kept so the HUD can show its working rather than a bare
## number the player has to take on faith.
##
## Everything about the shot is measured from where it is actually taken:
## a unit leaning out of cover shoots from the tile it leans out to.
class_name HitChance
extends RefCounted

## Aim the target's cover takes off the shot.
const HALF_COVER := 20
const FULL_COVER := 40
## Aim gained for catching a target whose cover faces the wrong way.
const FLANKING := 20
## Tiles between each step of the distance penalty.
const DISTANCE_STEP := 4


## One named part of the sum.
class Term:
	var label: String
	var value: int

	func _init(term_label: String, term_value: int) -> void:
		label = term_label
		value = term_value


## A worked-out chance to hit, and how it was arrived at.
class Estimate:
	## The parts that went into it, in the order they apply. Parts worth
	## nothing are left out, so the breakdown only lists what mattered.
	var terms: Array[Term] = []
	## The terms added up, before being held to 0..100.
	var raw := 0
	## The chance the shot lands, as a percentage.
	var chance := 0

	## Adds [param value] percentage points under [param label].
	func add(label: String, value: int) -> void:
		raw += value
		chance = clampi(raw, 0, 100)
		if value != 0:
			terms.append(Term.new(label, value))


## The chance [param shooter] lands [param shot].
static func for_shot(shooter: Unit, shot: LineOfSight.Shot) -> Estimate:
	var estimate := Estimate.new()
	estimate.add("Aim", shooter.aim)
	estimate.add("Evasion", -shot.target.evasion)
	estimate.add("Cover", -cover_penalty(shot.cover))
	estimate.add("Flanking", FLANKING if shot.flanked else 0)
	# Height tells both ways: shooting uphill costs as much as shooting down
	# gains.
	estimate.add("Height", (shot.from.y - shot.target_tile.y) * shooter.height_bonus)
	# Only whole steps count, so the number holds still while the player
	# shuffles about within a step.
	estimate.add("Distance", -floori(shot.distance / DISTANCE_STEP) * shooter.distance_penalty)
	return estimate


## The aim [param cover] takes off a shot.
static func cover_penalty(cover: LineOfSight.Cover) -> int:
	match cover:
		LineOfSight.Cover.HIGH:
			return FULL_COVER
		LineOfSight.Cover.LOW:
			return HALF_COVER
		_:
			return 0


## Whether a shot with [param chance] of landing does.
static func roll(chance: int) -> bool:
	return randi_range(1, 100) <= chance
