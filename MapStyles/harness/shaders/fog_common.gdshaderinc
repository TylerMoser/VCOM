// What the fog of war knows of a point of the map. Shared by the fog itself (fog_veil.gdshader) and
// the lines it leaves known over it (map_line_fogged.gdshader), so both agree to the pixel on where
// the fog is. For the variants of proposal 20 in MapStyles/20-fog-of-war/.
//
// [mask] is a picture of the MapCreation sheet (10,385 by 13,400 units) that the party paints as it
// travels (StyleKit.fog_mask()): R how far explored (0 to 1, soft at the edge of its sight), G how
// recently (1 the newest), with mipmaps, which are the same picture blurred.

uniform vec2 sheet = vec2(10385.0, 13400.0);
uniform sampler2D mask : filter_linear_mipmap, repeat_disable;
// How hard the edge is: 1 keeps the mask's own soft edge, 0 cuts it sharp at its middle.
uniform float edge_soft : hint_range(0.0, 1.0) = 1.0;
// Moves the edge in and out by noise: how far, in the mask's 0 to 1, and how large the ragged
// shapes are, in map units.
uniform float ragged : hint_range(0.0, 1.0) = 0.0;
uniform float ragged_scale = 90.0;

varying vec2 world;

float fog_hash(vec2 p) {
	uvec2 q = uvec2(ivec2(floor(p)) + ivec2(65536));
	uint h = (q.x * 1597334677u) ^ (q.y * 3812015801u);
	h = h * 747796405u + 2891336453u;
	h = ((h >> ((h >> 28u) + 4u)) ^ h) * 277803737u;
	h = (h >> 22u) ^ h;
	return float(h) * (1.0 / 4294967295.0);
}

float fog_noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(fog_hash(i), fog_hash(i + vec2(1.0, 0.0)), u.x),
			mix(fog_hash(i + vec2(0.0, 1.0)), fog_hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

// How far explored the point is before the edge is shaped: the mask, made ragged. The noise works
// only where the mask is between its two ends, the soft edge of the party's sight, and most at its
// middle, so the fog is even deep in the unknown and the known land clear.
float fog_raw(vec2 at) {
	float e = texture(mask, at / sheet).r;
	if (ragged > 0.0) {
		float n = fog_noise(at / ragged_scale) * 0.65 + fog_noise(at / (ragged_scale * 0.31)) * 0.35;
		e += (n - 0.5) * 2.0 * ragged * clamp(4.0 * e * (1.0 - e), 0.0, 1.0);
	}
	return e;
}

// How far explored, 0 to 1, the edge shaped by edge_soft.
float fog_explored(float raw) {
	float w = 0.5 * edge_soft + 0.002;
	return smoothstep(0.5 - w, 0.5 + w, raw);
}
