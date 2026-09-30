## Throw a grenade the unit carries. Only a unit with a grenade equipped has
## it.
##
## A placeholder so far: it can be made active, but throwing is not written
## yet, so it spends nothing and does nothing. How far a throw reaches, the
## blast, its damage to units and terrain, and using the grenade up belong
## here and on [BattleItem].
class_name ThrowGrenadeAction
extends UnitAction


func _init() -> void:
	display_name = "Throw Grenade"
	required_tag = Item.GRENADE


func is_available(unit: Unit) -> bool:
	return unit.actions_remaining > 0
