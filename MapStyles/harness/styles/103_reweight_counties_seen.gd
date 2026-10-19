## 10c · County borders you can see. Measured, a county border weighs a tenth of any other line
## at every zoom: dots a little over a pixel across at the Duchy tier, half see-through, and 2.3
## widths apart. (02's README and Docs/MAP.md give the gap as 1.15 widths, but where a pattern
## is dots alone the shader puts its gap on either side of each dot, so as pictured and applied
## they are twice that apart.) Here the dots are 1.15 widths apart, as those describe them, the
## line 7 units wide (from 6) and 0.65 opaque (from 0.5: under the duchies' 0.7, so a county's
## dots stay lighter than a duchy's dashes); its bands along rivers and roads, and their pattern,
## with it. Kingdoms and duchies are as they are.
extends RefCounted

const NAME := "County borders you can see"
const LABEL := "10c"


func apply(kit) -> void:
	kit.as_revisited()
	var dots := kit.border_material("Counties") as ShaderMaterial
	dots.set_shader_parameter(&"gap", 0.575)
	kit.reweight_rank("Counties", 7.0)
	kit.set_alpha("Borders/Counties", 0.65)
	kit.set_alpha("BordersOverLakes/Counties", 0.65)
