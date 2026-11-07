## The pause menu journal, separated into the three quest categories.
class_name QuestsTab
extends SubTabs


func _init() -> void:
	super()
	name = "Quests"
	for title in ["Main Quests", "Major Quests", "Minor Quests"]:
		add_child(QuestBrowser.new(title))
	get_tab_bar().gui_input.connect(_on_tab_bar_input)


func show_quests(quests: Array[Quest]) -> void:
	current_tab = 0
	for category in get_tab_count():
		var entries: Array[Quest] = []
		for quest in quests:
			if quest != null and quest.category == category:
				entries.append(quest)
		(get_tab_control(category) as QuestBrowser).show_quests(entries)


func selected_quest() -> Quest:
	return (get_current_tab_control() as QuestBrowser).selected


func focus_selection() -> bool:
	get_tab_bar().grab_focus()
	return true


func _on_tab_bar_input(event: InputEvent) -> void:
	if event.is_action_pressed(&"ui_down") and (get_current_tab_control() as QuestBrowser).focus_selection():
		get_tab_bar().accept_event()
