// Tints the land of the new map (Scenes/Map.tscn) by its biome, so the open
// land says what country it is. One material, Resources/MapGround.tres, is
// shared by every county and by the island in a lake, and holds each biome's
// colour and intensity, so a change there (its Shader Parameters, in the
// inspector) recolours that biome everywhere, in the editor too. The colours
// live only there: the defaults below are no tint at all.
//
// Which biome a county is in is set on the county itself: [biome], under
// Instance Shader Parameters in its inspector, a list of the nine. It is its
// kingdom's, a kingdom being a biome (Land/KingdomN is biome N). A county
// duplicated by hand keeps it; one moved to another kingdom needs it changed.
//
// A biome's colour is its land at intensity 1. Below that the county's own
// colour, the land's white, shows through: at 0.4 the land is 40% of the way
// from white to the colour. [overall_intensity] scales every biome's at once,
// 1 leaving each as set (an intensity never passes 1).
shader_type canvas_item;

// The county's biome: its kingdom's number, 1 to 9. None is the land's white.
instance uniform int biome : hint_enum("None", "Tundra Mountains", "Volcanic Mountains / Ruins",
		"Temperate Mountains", "Desert", "Grassland", "Evergreen Temperate Rainforest", "Swamp",
		"Deciduous Forest", "Tropical Rainforest") = 0;

uniform float overall_intensity : hint_range(0.0, 2.0, 0.01) = 1.0;

group_uniforms tundra_mountains;
uniform vec3 tundra_mountains_color : source_color = vec3(1.0);
uniform float tundra_mountains_intensity : hint_range(0.0, 1.0, 0.01) = 0.0;
group_uniforms volcanic_mountains;
uniform vec3 volcanic_mountains_color : source_color = vec3(1.0);
uniform float volcanic_mountains_intensity : hint_range(0.0, 1.0, 0.01) = 0.0;
group_uniforms temperate_mountains;
uniform vec3 temperate_mountains_color : source_color = vec3(1.0);
uniform float temperate_mountains_intensity : hint_range(0.0, 1.0, 0.01) = 0.0;
group_uniforms desert;
uniform vec3 desert_color : source_color = vec3(1.0);
uniform float desert_intensity : hint_range(0.0, 1.0, 0.01) = 0.0;
group_uniforms grassland;
uniform vec3 grassland_color : source_color = vec3(1.0);
uniform float grassland_intensity : hint_range(0.0, 1.0, 0.01) = 0.0;
group_uniforms evergreen_temperate_rainforest;
uniform vec3 evergreen_temperate_rainforest_color : source_color = vec3(1.0);
uniform float evergreen_temperate_rainforest_intensity : hint_range(0.0, 1.0, 0.01) = 0.0;
group_uniforms swamp;
uniform vec3 swamp_color : source_color = vec3(1.0);
uniform float swamp_intensity : hint_range(0.0, 1.0, 0.01) = 0.0;
group_uniforms deciduous_forest;
uniform vec3 deciduous_forest_color : source_color = vec3(1.0);
uniform float deciduous_forest_intensity : hint_range(0.0, 1.0, 0.01) = 0.0;
group_uniforms tropical_rainforest;
uniform vec3 tropical_rainforest_color : source_color = vec3(1.0);
uniform float tropical_rainforest_intensity : hint_range(0.0, 1.0, 0.01) = 0.0;
group_uniforms;

// The county's biome's colour, and in alpha how much of it shows. Picked once a
// vertex, the biome being the same all over a county: picked a pixel, it cost
// the map three times its GPU time.
varying flat vec4 tint;

void vertex() {
	vec3 color = vec3(1.0);
	float intensity = 0.0;
	switch (biome) {
		case 1: color = tundra_mountains_color; intensity = tundra_mountains_intensity; break;
		case 2: color = volcanic_mountains_color; intensity = volcanic_mountains_intensity; break;
		case 3: color = temperate_mountains_color; intensity = temperate_mountains_intensity; break;
		case 4: color = desert_color; intensity = desert_intensity; break;
		case 5: color = grassland_color; intensity = grassland_intensity; break;
		case 6: color = evergreen_temperate_rainforest_color; intensity = evergreen_temperate_rainforest_intensity; break;
		case 7: color = swamp_color; intensity = swamp_intensity; break;
		case 8: color = deciduous_forest_color; intensity = deciduous_forest_intensity; break;
		case 9: color = tropical_rainforest_color; intensity = tropical_rainforest_intensity; break;
	}
	tint = vec4(color, clamp(intensity * overall_intensity, 0.0, 1.0));
}

void fragment() {
	COLOR.rgb = mix(COLOR.rgb, tint.rgb, tint.a);
}
