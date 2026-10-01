// The ground blocks' material: what the MagicaVoxel importer gives them
// (vertex colours as sRGB albedo, roughness 1, Godot's standard lighting),
// plus the optional tile grid: a faint line along every block boundary, drawn
// while the global tile_grid is above 0. TileGrid.gd sets that global; the
// lines are style 19's grid (Styles/VISUAL_VARIANTS.md), without the rest of
// that style. With the grid off this draws exactly as the importer's material.
shader_type spatial;
// StandardMaterial3D's lighting. Named outright because a shader left to its
// own defaults in Godot 4.7 is not lit the same: tops came out about 3%
// darker, more at grazing angles.
render_mode diffuse_burley, specular_schlick_ggx;

global uniform float tile_grid;

// How much a line darkens the surface under it.
uniform float line_darken : hint_range(0.0, 1.0) = 0.18;
// A line's half-width, in metres.
uniform float line_width = 0.02;

// The vertex stage is StandardMaterial3D's (vertex_color_is_srgb) and nothing
// else; the fragment stage works out where a pixel is only while the grid is
// on, so the grid costs nothing while it is off.
void vertex() {
	if (!OUTPUT_IS_SRGB) {
		COLOR.rgb = mix(
				pow((COLOR.rgb + vec3(0.055)) * (1.0 / (1.0 + 0.055)), vec3(2.4)),
				COLOR.rgb * (1.0 / 12.92),
				lessThan(COLOR.rgb, vec3(0.04045)));
	}
}

void fragment() {
	vec3 albedo = COLOR.rgb;
	if (tile_grid > 0.0) {
		// Blocks are 1 m with their faces on whole metres, so a boundary is
		// wherever a coordinate is whole. A face's lines run along its own two
		// axes: x and z on a top, the vertical and one horizontal on a wall.
		vec3 world_pos = (INV_VIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
		vec3 n = normalize((INV_VIEW_MATRIX * vec4(NORMAL, 0.0)).xyz);
		vec3 d = abs(fract(world_pos + 0.5) - 0.5);
		vec3 fw = fwidth(world_pos);
		float dist;
		float aa;
		if (abs(n.y) > 0.5) {
			dist = min(d.x, d.z);
			aa = max(fw.x, fw.z);
		} else if (abs(n.x) > 0.5) {
			dist = min(d.y, d.z);
			aa = max(fw.y, fw.z);
		} else {
			dist = min(d.x, d.y);
			aa = max(fw.x, fw.y);
		}
		float line = 1.0 - smoothstep(line_width - aa, line_width + aa, dist);
		albedo *= 1.0 - line_darken * tile_grid * line;
	}
	ALBEDO = albedo;
	METALLIC = 0.0;
	SPECULAR = 0.5;
	ROUGHNESS = 1.0;
}
