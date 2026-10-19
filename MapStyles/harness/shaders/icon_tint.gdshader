// A settlement's icon (a Destination's drawing) in another colour: the
// picture's own colour mixed toward [tint] by tint's alpha, its shape kept. The
// icons are black ink, which a modulate cannot lighten; this can, for a dark
// map or a greyed one. For real, an icon_tint on Destination.
shader_type canvas_item;

uniform vec4 tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);

void fragment() {
	COLOR.rgb = mix(COLOR.rgb, tint.rgb, tint.a);
}
