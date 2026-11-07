## A settlement's initial quest offers. Campaign owns the remaining offers.
class_name QuestBoard
extends Location

@export var quests: Array[Quest] = []


func make_tab() -> Control:
	return QuestBoardTab.new(self)
