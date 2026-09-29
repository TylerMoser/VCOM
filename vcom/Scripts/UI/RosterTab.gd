## The pause menu's Roster tab: the roster's characters in a
## [CharacterBrowser], where their equipment can be changed.
class_name RosterTab
extends CharacterBrowser


func _init() -> void:
	super()
	name = "Roster"


## Shows [param roster]'s characters, in order, and selects the first, on the
## first page.
func show_roster(roster: Roster) -> void:
	show_characters(roster.characters)
