## Bottom-left row of cards, one per squad member. Clicking a card selects that
## unit, and the selected unit's card is highlighted.
extends HBoxContainer

@export var squad_path: NodePath = ^"../../PlayerSquad"

var _squad: PlayerSquad


func _ready() -> void:
	_squad = get_node_or_null(squad_path) as PlayerSquad
	if _squad == null:
		push_error("SquadPanel: no PlayerSquad at '%s'." % squad_path)
		return
	if not _squad.is_node_ready():
		await _squad.ready

	for unit in _squad.members:
		var card := UnitCard.new()
		add_child(card)
		card.bind(unit)
		card.pressed.connect(_squad.select.bind(unit))

	_squad.selection_changed.connect(_on_selection_changed)
	_on_selection_changed(_squad.selected)


func _on_selection_changed(unit: Unit) -> void:
	for card: UnitCard in get_children():
		card.selected = card.unit == unit
