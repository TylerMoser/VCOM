## A village's hiring board: characters the party can take on, each for their
## [member Character.hire_cost] in gold. Every board works and looks the same
## ([HiringBoardTab]); who is on it differs, so each village has its own.
##
## [member characters] is who is on it when the campaign starts, and is never
## changed. Who still is, once some have been hired, is
## [method Campaign.for_hire].
class_name HiringBoard
extends Location

## In the order the board shows them. A character belongs on one board only.
@export var characters: Array[Character] = []


func make_tab() -> Control:
	return HiringBoardTab.new(self)
