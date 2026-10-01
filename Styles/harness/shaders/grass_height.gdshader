// Grass blocks tinted by how high they stand: every level above the floor is
// a little brighter and warmer, so two levels of grass read apart. Only the
// green parts change (the top and its fringe); the dirt stays as it is.
// Lighting is Godot's standard, as on the importer's material.
shader_type spatial;

uniform float floor_y = 1.0;
// Per level above the floor: brightness gain, and hue shift in degrees
// (negative is toward yellow).
uniform float value_per_level = 0.12;
uniform float hue_per_level = -6.0;
uniform float saturation_per_level = 0.0;

varying vec3 world_pos;

vec3 rgb2hsv(vec3 c) {
	vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
	vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
	vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
	float d = q.x - min(q.w, q.y);
	float e = 1.0e-10;
	return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsv2rgb(vec3 c) {
	vec3 p = abs(fract(c.xxx + vec3(0.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0);
	return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);
}

vec3 srgb_to_linear(vec3 c) {
	return mix(pow((c + 0.055) / 1.055, vec3(2.4)), c / 12.92, lessThan(c, vec3(0.04045)));
}

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec3 hsv = rgb2hsv(COLOR.rgb);
	// The level of the block this face belongs to: its top's height above the floor.
	float level = max(ceil(world_pos.y - 0.001) - floor_y, 0.0);
	float green = 1.0 - smoothstep(0.0, 45.0, abs(mod(hsv.x * 360.0 - 100.0 + 180.0, 360.0) - 180.0));
	float k = level * green;
	hsv.x = fract(hsv.x + hue_per_level / 360.0 * k + 1.0);
	hsv.y = clamp(hsv.y * (1.0 + saturation_per_level * k), 0.0, 1.0);
	hsv.z = clamp(hsv.z * (1.0 + value_per_level * k), 0.0, 1.0);
	ALBEDO = srgb_to_linear(hsv2rgb(hsv));
	ROUGHNESS = 1.0;
}
