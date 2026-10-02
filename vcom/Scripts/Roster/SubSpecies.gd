## A kind of one [Species], such as a Human's Minor Noble: a [SkillTree] of its
## own, beside the species'.
class_name SubSpecies
extends SkillSource

## The species this is a kind of, and the only one: a character's
## [member Character.sub_species] is one of their
## [member Character.species]'s kinds.
@export var species: Species
