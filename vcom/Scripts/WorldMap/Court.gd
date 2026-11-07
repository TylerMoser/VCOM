## A capital's court, authored separately for each ruler.
class_name Court
extends Location

enum Favor { NOT_FAVORED, NEUTRAL, FAVORED }

@export var ruler_name := "Count"
@export var favor: Favor = Favor.NEUTRAL
@export var gain_favor_by: Array[String] = ["none"]
@export var lose_favor_by: Array[String] = ["none"]


func make_tab() -> Control:
	return CourtTab.new(self)
