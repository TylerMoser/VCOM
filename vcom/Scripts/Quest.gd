## Journal content for the pause menu. Quest progression is managed separately.
class_name Quest
extends Resource

enum Category { MAIN, MAJOR, MINOR }

@export var title: String = ""
@export var category: Category = Category.MAIN
@export_multiline var description: String = ""
@export_multiline var objectives: String = ""
@export_enum("Active", "Completed", "Failed") var status: String = "Active"
@export var quest_giver: String = ""
@export var location: String = ""
@export_multiline var rewards: String = ""
