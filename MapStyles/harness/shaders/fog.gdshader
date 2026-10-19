// Fog over the land the party has not seen: one polygon over the whole map,
// drawn over the land, forests, borders, water, roads and bridges and under the
// settlements and the party. Clear within [clear_radius] of [centre] (the
// map's units), with a ragged edge [edge] deep, and a veil of [fog] beyond,
// with a faint grain so it reads as paper, not as a grey wash. For real, the
// clear ground is a mask of everywhere the party has been (a texture painted
// as it travels), not a circle.
shader_type canvas_item;

uniform vec2 centre = vec2(0.0);
uniform float clear_radius = 500.0;
uniform float edge = 120.0;
uniform vec4 fog : source_color = vec4(0.93, 0.9, 0.83, 1.0);
uniform float opacity : hint_range(0.0, 1.0) = 0.9;

varying vec2 world;

void vertex() {
	world = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

// A hash of a lattice point, 0 to 1, on integers so it holds at the map's
// large coordinates.
float hash(vec2 p) {
	uvec2 q = uvec2(ivec2(floor(p)) + ivec2(65536));
	uint h = (q.x * 1597334677u) ^ (q.y * 3812015801u);
	h = h * 747796405u + 2891336453u;
	h = ((h >> ((h >> 28u) + 4u)) ^ h) * 277803737u;
	h = (h >> 22u) ^ h;
	return float(h) * (1.0 / 4294967295.0);
}

float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

void fragment() {
	float ragged = (noise(world / 90.0) * 0.6 + noise(world / 31.0) * 0.4 - 0.5) * edge * 1.2;
	float d = distance(world, centre) + ragged;
	float a = smoothstep(clear_radius, clear_radius + edge, d) * opacity;
	float grain = noise(world / 23.0) * 0.5 + noise(world / 211.0) * 0.5;
	COLOR = vec4(fog.rgb * (0.96 + grain * 0.07), a);
}
