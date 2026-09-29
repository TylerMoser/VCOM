## One of the Roster tab's sub-tabs (Details, Equipment, Skills): a view of
## the character selected in the strip above it. The Roster hands every page
## the new character whenever the selection changes, whichever page is open,
## so switching sub-tab never shows a page left on someone else.
##
## A page for real content extends this and overrides [method _refresh].
class_name CharacterPage
extends Control

## Who the page is showing. Null when the roster is empty.
var character: Character


func _init(title: String) -> void:
	name = title


func show_character(who: Character) -> void:
	character = who
	_refresh()


## Redraws the page for [member character]. Empty until the page has content.
func _refresh() -> void:
	pass
