// The land's polygons (every county, and the islands in lakes) coloured as ground: by biome, and by
// what the land and its people make of it. For the variants of proposal 12 in
// MapStyles/12-biome-ground-colours/. Every part is off at its default, so a variant turns on only
// what it shows; StyleKit.style_ground() fills in the pictures.
//
// The pictures are read in the map's own space, the MapCreation sheet being 10,385 by 13,400 units:
//   region_map  the biome (1 to 9) of every pixel: SourceData/KingdomMap.png (the kingdoms, each a
//               biome) or TerrainMap.png (the country as the land was shaped, its own edges)
//   elevation   harness/data/elevation.png: the square root of the height's share of 3,352 m
//   wetness, farmland, coast  harness/data/ (make_data.py): near a river, near people, near the sea
//   edge        harness/data/kingdom_edge.png: how far from a kingdom's border
shader_type canvas_item;

uniform vec2 sheet = vec2(10385.0, 13400.0);

// -- where the colour comes from --------------------------------------------------------------------
// 0: the polygon's own colour, which a style sets county by county; 1: [palette] by the biome of
// [region_map] at the pixel.
uniform int source = 1;
uniform sampler2D region_map : filter_nearest, repeat_disable;
uniform vec4 palette[10] : source_color;
// How far from [base], the land's white, toward the biome's colour.
uniform float strength : hint_range(0.0, 1.0) = 1.0;
uniform vec4 base : source_color = vec4(1.0);
// The biomes blended over this many map units where they meet (taps over a disc): an ecotone.
uniform float soft_units = 0.0;
// Pigment pooled darker where one biome's colour gives way to another's, as in a watercolour wash
// (with soft_units over 0).
uniform float wash = 0.0;

// -- by the zoom -------------------------------------------------------------------------------------
// With both heights over 0, [strength] is also times strength_far at fade_far_miles and over,
// strength_near at fade_near_miles and under, by the logarithm of the view's height between.
uniform float fade_far_miles = 0.0;
uniform float fade_near_miles = 0.0;
uniform float strength_far = 1.0;
uniform float strength_near = 1.0;

// -- the height -----------------------------------------------------------------------------------------
uniform sampler2D elevation : filter_linear_mipmap, repeat_disable;
// Uplands darker and cooler: toward [height_tint] by the height.
uniform float height_shade = 0.0;
uniform vec4 height_tint : source_color = vec4(0.72, 0.74, 0.8, 1.0);
// Lowlands warmer: toward [low_tint] near sea level.
uniform float low_shade = 0.0;
uniform vec4 low_tint : source_color = vec4(1.0, 0.97, 0.9, 1.0);
// Bare rock over rock_from and snow over snow_from (elevation.png's 0 to 1; over 1 is none), the
// snowline [snow_north] lower at the sheet's top than at its bottom, softened and made ragged.
uniform float rock_from = 2.0;
uniform vec4 rock : source_color = vec4(0.8, 0.78, 0.76, 1.0);
uniform float snow_from = 2.0;
uniform vec4 snow : source_color = vec4(0.97, 0.98, 1.0, 1.0);
uniform float snow_north = 0.0;
uniform float line_soft = 0.025;
uniform float line_ragged = 0.03;

// -- water, people and the sea -----------------------------------------------------------------------
uniform sampler2D wetness : filter_linear_mipmap, repeat_disable;
// Green valleys: toward [wet_color] by the nearness of a river, in each biome by its [dry] share.
uniform float wet_strength = 0.0;
uniform vec4 wet_color : source_color = vec4(0.78, 0.88, 0.66, 1.0);
uniform float dry[10];
uniform sampler2D farmland : filter_linear_mipmap, repeat_disable;
// Fields round the settlements: cells of [farm_cell] map units, each a field in one of three colours
// where the nearness of people says (far out, where a cell is under a few pixels, an even tint).
uniform float farm_strength = 0.0;
uniform float farm_cell = 22.0;
uniform vec4 farm_a : source_color = vec4(0.93, 0.87, 0.66, 1.0);
uniform vec4 farm_b : source_color = vec4(0.86, 0.9, 0.7, 1.0);
uniform vec4 farm_c : source_color = vec4(0.9, 0.82, 0.68, 1.0);
uniform sampler2D coast : filter_linear_mipmap, repeat_disable;
// A strand along the sea: toward [coast_color] where the sea is near.
uniform float coast_strength = 0.0;
uniform vec4 coast_color : source_color = vec4(0.97, 0.93, 0.8, 1.0);
// The wind from the west: the land tinted toward [wet_west] in the west and [dry_east] in the east.
uniform float moisture = 0.0;
uniform vec4 wet_west : source_color = vec4(0.9, 1.0, 0.92, 1.0);
uniform vec4 dry_east : source_color = vec4(1.0, 0.93, 0.82, 1.0);

// -- along the kingdoms' borders ---------------------------------------------------------------------
// The biome's colour only in a band [band_px] screen pixels wide inside each kingdom's border.
uniform sampler2D edge : filter_linear_mipmap, repeat_disable;
uniform float edge_reach = 160.0;
uniform float band_px = 0.0;

// -- marks ------------------------------------------------------------------------------------------------
// A small mark by biome, [pattern_px] screen pixels apart (0 none; 1 stipple; 2 grass tufts; 3 marsh;
// 4 rock strokes; 5 ice crosses; 6 cinders; 7 dune arcs; 8 leaves; 9 rings).
uniform int pattern[10];
uniform vec4 pattern_color : source_color = vec4(0.25, 0.2, 0.15, 0.35);
uniform float pattern_px = 14.0;
uniform float pattern_size = 0.5;
uniform float pattern_density = 0.8;
// A larger picture by biome, sparser (0 none; 1 snowflake; 2 volcano; 3 peaks; 4 cactus; 5 grass;
// 6 conifer; 7 reeds; 8 round tree; 9 palm).
uniform int icon[10];
uniform vec4 icon_color : source_color = vec4(0.3, 0.27, 0.22, 0.55);
uniform float icon_px = 56.0;
uniform float icon_density = 0.3;

// -- paper ---------------------------------------------------------------------------------------------
// A broad mottle and a fine grain, keeping their size on the screen, darkening toward [paper_dark].
uniform float paper = 0.0;
uniform vec4 paper_dark : source_color = vec4(0.55, 0.42, 0.25, 1.0);

varying vec2 world;
varying float px_per_unit;

void vertex() {
	world = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
	px_per_unit = length((CANVAS_MATRIX * MODEL_MATRIX)[0].xy);
}

// A hash of a lattice point, 0 to 1, on integers so it holds at the map's large coordinates;
// [seed] gives each point further numbers of its own.
float hash(vec2 p, uint seed) {
	uvec2 q = uvec2(ivec2(floor(p)) + ivec2(65536));
	uint h = (q.x * 1597334677u) ^ (q.y * 3812015801u) ^ (seed * 2246822519u);
	h = h * 747796405u + 2891336453u;
	h = ((h >> ((h >> 28u) + 4u)) ^ h) * 277803737u;
	h = (h >> 22u) ^ h;
	return float(h) * (1.0 / 4294967295.0);
}

float value_noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i, 0u), hash(i + vec2(1.0, 0.0), 0u), u.x),
			mix(hash(i + vec2(0.0, 1.0), 0u), hash(i + vec2(1.0, 1.0), 0u), u.x), u.y);
}

float fbm(vec2 p) {
	mat2 turn = mat2(vec2(0.8, 0.6), vec2(-0.6, 0.8));
	float sum = value_noise(p) * 0.55;
	p = turn * p * 2.03 + 13.7;
	sum += value_noise(p) * 0.3;
	p = turn * p * 2.01 + 7.1;
	sum += value_noise(p) * 0.15;
	return sum;
}

// Noise whose features keep near [px] screen pixels at any zoom.
float zoom_noise(vec2 p, float px) {
	float level = log2(px / max(px_per_unit, 1e-6));
	float l0 = floor(level);
	return mix(fbm(p / exp2(l0) + 17.0 * l0), fbm(p / exp2(l0 + 1.0) + 17.0 * (l0 + 1.0)), level - l0);
}

int biome_at(vec2 uv) {
	return clamp(int(round(texture(region_map, uv).r * 255.0)), 0, 9);
}

vec3 biome_colour(int id) {
	return id == 0 ? base.rgb : palette[id].rgb;
}

// The biomes' colours averaged over a disc of [soft_units] round uv: 1 + 16 taps on a golden-angle
// spiral, the sea left out.
vec3 soft_colour(vec2 uv, vec3 own) {
	vec3 sum = own;
	float n = 1.0;
	vec2 r = vec2(soft_units) / sheet;
	for (int i = 0; i < 16; i++) {
		float a = float(i) * 2.39996;
		float d = sqrt((float(i) + 0.5) / 16.0);
		int id = biome_at(uv + vec2(cos(a), sin(a)) * d * r);
		if (id > 0) {
			sum += biome_colour(id);
			n += 1.0;
		}
	}
	return sum / n;
}

// -- the marks' shapes: signed distances, in a cell's units ---------------------------------------------

float sd_segment(vec2 p, vec2 a, vec2 b) {
	vec2 pa = p - a;
	vec2 ba = b - a;
	return length(pa - ba * clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0));
}

float sd_triangle(vec2 p, vec2 q) {
	p.x = abs(p.x);
	vec2 a = p - q * clamp(dot(p, q) / dot(q, q), 0.0, 1.0);
	vec2 b = p - q * vec2(clamp(p.x / q.x, 0.0, 1.0), 1.0);
	float s = -sign(q.y);
	vec2 d = min(vec2(dot(a, a), s * (p.x * q.y - p.y * q.x)), vec2(dot(b, b), s * (p.y - q.y)));
	return -sqrt(d.x) * sign(d.y);
}

// A small mark (pattern), its size s, centred at the origin; y runs down.
float pattern_shape(int kind, vec2 p, float s) {
	float w = 0.045 * s;
	if (kind == 1) {
		return length(p) - 0.09 * s;
	} else if (kind == 2) {
		float d = sd_segment(p, vec2(0.0, 0.2) * s, vec2(0.0, -0.18) * s);
		d = min(d, sd_segment(p, vec2(-0.03, 0.2) * s, vec2(-0.2, -0.08) * s));
		d = min(d, sd_segment(p, vec2(0.03, 0.2) * s, vec2(0.2, -0.08) * s));
		return d - w;
	} else if (kind == 3) {
		float d = sd_segment(p, vec2(-0.32, 0.12) * s, vec2(0.32, 0.12) * s);
		d = min(d, sd_segment(p, vec2(0.0, 0.12) * s, vec2(0.0, -0.12) * s));
		d = min(d, sd_segment(p, vec2(-0.15, 0.12) * s, vec2(-0.2, -0.04) * s));
		d = min(d, sd_segment(p, vec2(0.15, 0.12) * s, vec2(0.2, -0.04) * s));
		return d - w;
	} else if (kind == 4) {
		float d = sd_segment(p, vec2(-0.22, 0.14) * s, vec2(0.0, -0.16) * s);
		d = min(d, sd_segment(p, vec2(0.0, -0.16) * s, vec2(0.22, 0.14) * s));
		return d - w;
	} else if (kind == 5) {
		float d = sd_segment(p, vec2(-0.16, 0.0) * s, vec2(0.16, 0.0) * s);
		d = min(d, sd_segment(p, vec2(0.0, -0.16) * s, vec2(0.0, 0.16) * s));
		return d - w;
	} else if (kind == 6) {
		float d = length(p - vec2(-0.12, 0.05) * s) - 0.07 * s;
		return min(d, length(p - vec2(0.12, -0.06) * s) - 0.05 * s);
	} else if (kind == 7) {
		// An arc: the top of a ring.
		float ring = abs(length(p - vec2(0.0, 0.22) * s) - 0.3 * s) - w;
		return max(ring, p.y - 0.08 * s);
	} else if (kind == 8) {
		vec2 q = vec2(p.x * 0.8 - p.y * 0.6, p.x * 0.6 + p.y * 0.8);
		return length(q / vec2(1.0, 0.45)) * 0.45 - 0.09 * s;
	} else if (kind == 9) {
		return abs(length(p) - 0.12 * s) - w;
	}
	return 1e3;
}

// A larger picture (icon), its size s.
float icon_shape(int kind, vec2 p, float s) {
	float w = 0.035 * s;
	if (kind == 1) {
		float d = 1e3;
		for (int k = 0; k < 3; k++) {
			float a = float(k) * 1.0472;
			vec2 v = vec2(cos(a), sin(a)) * 0.3 * s;
			d = min(d, sd_segment(p, -v, v));
		}
		return d - w;
	} else if (kind == 2) {
		float cone = sd_triangle(p - vec2(0.0, -0.18) * s, vec2(0.34, 0.46) * s);
		cone = max(cone, -(p.y + 0.1 * s));
		float plume = min(length(p - vec2(0.02, -0.26) * s) - 0.05 * s, length(p - vec2(0.08, -0.36) * s) - 0.06 * s);
		return min(cone, plume);
	} else if (kind == 3) {
		float a = sd_triangle(p - vec2(-0.1, -0.22) * s, vec2(0.24, 0.44) * s);
		float b = sd_triangle(p - vec2(0.14, -0.1) * s, vec2(0.18, 0.32) * s);
		return min(a, b);
	} else if (kind == 4) {
		float d = sd_segment(p, vec2(0.0, 0.28) * s, vec2(0.0, -0.28) * s);
		d = min(d, sd_segment(p, vec2(0.0, 0.06) * s, vec2(-0.16, 0.06) * s));
		d = min(d, sd_segment(p, vec2(-0.16, 0.06) * s, vec2(-0.16, -0.12) * s));
		d = min(d, sd_segment(p, vec2(0.0, -0.02) * s, vec2(0.15, -0.02) * s));
		d = min(d, sd_segment(p, vec2(0.15, -0.02) * s, vec2(0.15, -0.18) * s));
		return d - 0.06 * s;
	} else if (kind == 5) {
		float d = sd_segment(p, vec2(0.0, 0.24) * s, vec2(0.0, -0.22) * s);
		d = min(d, sd_segment(p, vec2(-0.05, 0.24) * s, vec2(-0.26, -0.1) * s));
		d = min(d, sd_segment(p, vec2(0.05, 0.24) * s, vec2(0.26, -0.1) * s));
		d = min(d, sd_segment(p, vec2(-0.02, 0.24) * s, vec2(-0.14, -0.2) * s));
		d = min(d, sd_segment(p, vec2(0.02, 0.24) * s, vec2(0.14, -0.2) * s));
		return d - w;
	} else if (kind == 6) {
		float crown = sd_triangle(p - vec2(0.0, -0.34) * s, vec2(0.2, 0.52) * s);
		float stem = sd_segment(p, vec2(0.0, 0.16) * s, vec2(0.0, 0.3) * s) - 0.05 * s;
		return min(crown, stem);
	} else if (kind == 7) {
		float d = 1e3;
		for (int k = -1; k <= 1; k++) {
			float x = float(k) * 0.12 * s;
			d = min(d, sd_segment(p, vec2(x, 0.26) * vec2(1.0, s), vec2(x * 1.3, -0.16 * s)) - w);
			d = min(d, length((p - vec2(x * 1.3, -0.2 * s)) / vec2(0.6, 1.0)) - 0.05 * s);
		}
		return d;
	} else if (kind == 8) {
		float crown = length(p - vec2(0.0, -0.1) * s) - 0.22 * s;
		float stem = sd_segment(p, vec2(0.0, 0.08) * s, vec2(0.0, 0.3) * s) - 0.05 * s;
		return min(crown, stem);
	} else if (kind == 9) {
		float d = sd_segment(p, vec2(0.02, 0.3) * s, vec2(-0.02, -0.16) * s) - 0.04 * s;
		d = min(d, sd_segment(p, vec2(-0.02, -0.16) * s, vec2(-0.26, -0.04) * s) - w);
		d = min(d, sd_segment(p, vec2(-0.02, -0.16) * s, vec2(0.24, -0.06) * s) - w);
		d = min(d, sd_segment(p, vec2(-0.02, -0.16) * s, vec2(-0.12, -0.32) * s) - w);
		d = min(d, sd_segment(p, vec2(-0.02, -0.16) * s, vec2(0.14, -0.3) * s) - w);
		return d;
	}
	return 1e3;
}

// The coverage of marks of the biome at the pixel, on a grid of [cell] map units; each mark is
// drawn by the biome under its own cell's middle, so it never spills a biome's mark into another.
float marks(float cell, bool icons, float size, float density, uint seed) {
	vec2 g = world / cell;
	float aa = max(fwidth(g.x), 1e-5) * 0.75;
	float best = 0.0;
	vec2 base_cell = floor(g);
	for (int y = -1; y <= 1; y++) {
		for (int x = -1; x <= 1; x++) {
			vec2 c = base_cell + vec2(float(x), float(y));
			if (hash(c, seed) > density) {
				continue;
			}
			vec2 offset = (vec2(hash(c, seed + 1u), hash(c, seed + 2u)) - 0.5) * 0.44;
			vec2 centre = c + 0.5 + offset;
			int id = biome_at(centre * cell / sheet);
			int kind = icons ? icon[id] : pattern[id];
			if (id == 0 || kind == 0) {
				continue;
			}
			vec2 p = g - centre;
			float d = icons ? icon_shape(kind, p, size) : pattern_shape(kind, p, size);
			best = max(best, 1.0 - smoothstep(-aa, aa, d));
		}
	}
	return best;
}

// Marks keeping about [px] screen pixels apart: two spacings a power of two apart, faded across.
float zoom_marks(float px, bool icons, float size, float density, uint seed) {
	float level = log2(px / max(px_per_unit, 1e-6));
	float l0 = floor(level);
	return mix(marks(exp2(l0), icons, size, density, seed), marks(exp2(l0 + 1.0), icons, size, density, seed),
			level - l0);
}

void fragment() {
	vec2 uv = world / sheet;
	int id = biome_at(uv);
	vec3 own = source == 1 ? biome_colour(id) : COLOR.rgb;
	vec3 col = own;
	float pool = 0.0;
	if (soft_units > 0.0) {
		col = soft_colour(uv, own);
		pool = clamp(length(col - own) * 9.0, 0.0, 1.0);
	}
	if (moisture > 0.0) {
		float east = smoothstep(0.12, 0.9, uv.x + (uv.y - 0.5) * 0.15);
		col = mix(col, col * mix(wet_west.rgb, dry_east.rgb, east), moisture);
	}

	float s = strength;
	if (fade_far_miles > 0.0 && fade_near_miles > 0.0) {
		float miles = 1.0 / (SCREEN_PIXEL_SIZE.y * px_per_unit * 16.09344);
		float t = clamp(log(fade_far_miles / miles) / log(fade_far_miles / fade_near_miles), 0.0, 1.0);
		s *= mix(strength_far, strength_near, t);
	}
	if (band_px > 0.0) {
		float stored = texture(edge, uv).r;
		float px = stored * stored * edge_reach * 3.35 * px_per_unit;
		float band = 1.0 - smoothstep(0.0, band_px, px);
		s *= band * band;
	}
	col = mix(base.rgb, col, s);

	if (height_shade > 0.0 || low_shade > 0.0 || rock_from <= 1.0 || snow_from <= 1.0) {
		float h = texture(elevation, uv).r;
		col = mix(col, col * height_tint.rgb, height_shade * smoothstep(0.12, 0.85, h));
		col = mix(col, col * low_tint.rgb, low_shade * (1.0 - smoothstep(0.0, 0.3, h)));
		float n = (fbm(world / 60.0) - 0.5) * line_ragged * 2.0;
		if (rock_from <= 1.0) {
			col = mix(col, rock.rgb, smoothstep(rock_from - line_soft, rock_from + line_soft, h + n));
		}
		if (snow_from <= 1.0) {
			float line = snow_from - snow_north * (1.0 - uv.y);
			col = mix(col, snow.rgb, smoothstep(line - line_soft, line + line_soft, h + n));
		}
	}
	if (wet_strength > 0.0) {
		float w = texture(wetness, uv).r * dry[id] * wet_strength;
		col = mix(col, wet_color.rgb, clamp(w, 0.0, 1.0));
	}
	if (farm_strength > 0.0) {
		float near = texture(farmland, uv).r;
		vec2 turned = vec2(world.x * 0.866 - world.y * 0.5, world.x * 0.5 + world.y * 0.866);
		vec2 cell = floor(turned / farm_cell);
		float pick = hash(cell, 7u);
		vec3 field = pick < 0.34 ? farm_a.rgb : (pick < 0.67 ? farm_b.rgb : farm_c.rgb);
		vec3 even = (farm_a.rgb + farm_b.rgb + farm_c.rgb) / 3.0;
		float cell_px = farm_cell * px_per_unit;
		vec3 fields = mix(even, field, smoothstep(2.0, 5.0, cell_px));
		float here = smoothstep(0.0, 0.25, near * farm_strength - hash(cell, 9u) * 0.6);
		float tint = mix(clamp(near * farm_strength * 1.5, 0.0, 1.0), here, smoothstep(2.0, 5.0, cell_px));
		col = mix(col, fields, tint);
	}
	if (coast_strength > 0.0) {
		float c = texture(coast, uv).r + (fbm(world / 40.0) - 0.5) * 0.25;
		col = mix(col, coast_color.rgb, smoothstep(0.35, 0.55, c) * coast_strength);
	}
	if (wash > 0.0 && soft_units > 0.0) {
		float mottle = zoom_noise(world + 91.0, 120.0);
		col *= 1.0 - wash * (pool * 0.6 + (mottle - 0.5) * 0.25);
	}
	if (paper > 0.0) {
		float mottle = zoom_noise(world, 260.0);
		float grain = zoom_noise(world + 311.0, 9.0);
		float dark = smoothstep(0.42, 0.8, mottle) * 0.85 + (grain - 0.5) * 0.3;
		col = mix(col, col * paper_dark.rgb * 1.25, paper * clamp(dark, 0.0, 1.0));
	}
	if (pattern_color.a > 0.0 && pattern[id] > 0) {
		float m = zoom_marks(pattern_px, false, pattern_size, pattern_density, 11u) * pattern_color.a;
		col = mix(col, pattern_color.rgb, m);
	}
	if (icon_color.a > 0.0 && icon[id] > 0) {
		float m = zoom_marks(icon_px, true, 0.62, icon_density, 23u) * icon_color.a;
		col = mix(col, icon_color.rgb, m);
	}
	COLOR = vec4(col, COLOR.a);
}
