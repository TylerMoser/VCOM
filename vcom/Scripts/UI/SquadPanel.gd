## Bottom-left row of cards, one per player-controlled unit.
extends HBoxContainer

## Group whose units get a card, in scene-tree order.
@export var unit_group := &"players"


func _ready() -> void:
	for node in get_tree().get_nodes_in_group(unit_group):
		var unit := node as Unit
		if unit == null:
			push_warning("SquadPanel: '%s' is in '%s' but is not a Unit." % [node.name, unit_group])
			continue
		var card := UnitCard.new()
		add_child(card)
		card.bind(unit)
