## 90 · Not a proposal: the map as it is, laid out as proposal 21 is, each view
## as everyone sees it and as someone with deuteranopia would, to set beside 21.
## With BEFORE=1, the map as it was before the look was applied, which 21 was
## made against.
extends RefCounted

const NAME := "Current look, colour-blind check"

const SAFE := preload("res://_probe/styles/21_colour_blind_safe.gd")


func panels(kit) -> Array:
	return SAFE.new().panels(kit)
