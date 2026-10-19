## 12d · Lightness steps. Every biome differs from each of its neighbours in lightness as well as hue,
## so the biomes stay apart in greyscale, on a dim screen and to a red-green colour-blind eye. In 12's
## palette two neighbours (the Swamp and the Deciduous Forest) are 2.7 apart (CIEDE2000), and with
## deuteranopia the Temperate Mountains and the Evergreen Rainforest 1.3: one colour. Here no two
## neighbours are under 7.9 apart, or 5.7 with deuteranopia. The Temperate Mountains, which border
## seven biomes, are the lightest (L* 97); the rest sit on three steps (about 90, 84 and 77) so that
## no two neighbours share one.
extends RefCounted

const NAME := "Lightness steps"
const LABEL := "12d"
const Now := preload("res://_probe/styles/1200_ground_now.gd")


func apply(kit) -> void:
	Now.ground(kit, {}, Now.STEPS)
	Now.forests(kit, Now.FORESTS_12)


func panels(_kit) -> Array:
	return Now.VIEWS
