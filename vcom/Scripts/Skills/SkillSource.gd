## Anything that gives a character a [SkillTree]: their [Species], their
## [SubSpecies] and their classes ([CharacterClass]), each a column of the
## Roster's Skills page headed by its [member display_name].
##
## A new kind of tree is a subclass, a [Character] property holding one, and a
## row of [constant Character.TREES]. Data, like [Location]: one resource per
## species or class, shared by everyone who has it; what a character has
## learned of its tree is theirs ([member Character.learned]).
class_name SkillSource
extends Resource

## Heads its column on the Skills page.
@export var display_name := ""
@export var tree: SkillTree
