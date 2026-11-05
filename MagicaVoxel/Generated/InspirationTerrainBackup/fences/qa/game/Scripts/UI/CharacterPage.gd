## One of a [CharacterBrowser]'s sub-tabs (Details, Equipment, Skills): a view
## of the character selected in the strip above it. The browser hands every page
## the new character whenever the selection changes, whichever page is open,
## so switching sub-tab never shows a page left on someone else.
##
## A page for real content extends this and overrides [method _refresh].
class_name CharacterPage
extends Control

## Who the page is showing. Null when the roster is empty.
var character: Character
## Whether the page only shows the character, without the means to change
## them: for someone not on the roster, such as a character for hire. Set
## before the first character is shown.
var read_only := false


func _init(title: String) -> void:
	name = title


func show_character(who: Character) -> void:
	character = who
	_refresh()


## Moves the keyboard into the page, coming down from the sub-tabs. False
## when the page has nothing to focus, and the tabs keep it.
func focus_selection() -> bool:
	return false


## Redraws the page for [member character]. Empty until the page has content.
func _refresh() -> void:
	pass
