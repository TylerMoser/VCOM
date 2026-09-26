## Human notes per variant: what it is, what it costs, and what applying it
## permanently would change. Kept apart from the settings so the renderer
## never reads them.
extends RefCounted

## The styles the user kept after reviewing all 28. The others are still
## defined in VariantList.gd and can be re-rendered, but were rejected.
const KEPT := [0, 1, 4, 5, 7, 10, 11, 15, 19, 21, 22, 23, 27, 28]

const ENV := "CombatMap.tscn Environment/sky/sun"
const AA := "project.godot anti-aliasing"
const BLOCK := "new block shader + GridMap material hookup"
const OUTLINE := "new outline shader + full-screen quad node"
const LUT := "generated LUT resource"


static func notes() -> Dictionary:
	return {
		0: ["Dark void, the default grey procedural sky as ambient (0.45), and a sun only ~10° off the camera's own direction, so top and side faces barely differ and shadows hide behind objects. No AO, no anti-aliasing.", "—", "—"],
		1: ["The baseline upgrade: sun moved to the camera's left so tops, south faces and east faces read as three distinct tones and shadows fall where you can see them; bright blue sky for backdrop and ambient; light SSAO; MSAA for clean block edges. Most variants build on this.", "Low (SSAO, MSAA 4×)", ENV + "; " + AA],
		2: ["Classic stylised colour contrast: warm key light with blue-violet ambient, so lit faces go warm and shade goes cool. Indigo backdrop.", "Low", ENV + "; " + AA],
		3: ["Godot's newest tonemapper, AgX, with raised contrast and +30% saturation. AgX rolls off bright colours gracefully, so greens stay natural rather than neon. Trade-off: the translucent move-range overlay reads browner.", "Low", ENV + "; " + AA],
		4: ["Real-time global illumination (SDFGI) with sky light and bounce, soft PCSS sun shadows and AO on a studio-grey backdrop. The closest to MagicaVoxel's own path-traced renders.", "High (SDFGI is the most expensive option here)", ENV + "; " + AA],
		5: ["Screen-space indirect light: a cheaper bounce than SDFGI that lifts shadows with the colour of nearby surfaces, so shade near grass goes green.", "Medium (SSIL)", ENV + "; " + AA],
		6: ["Low orange sun (22°) with long shadows, peach-to-violet sky, soft bloom. Dramatic and warm; turns the grass olive.", "Low (glow)", ENV + "; " + AA],
		7: ["Pastel sky, wide soft shadows, strong AO, and block colours lightened and desaturated 22% by the block shader. Calm and Townscaper-like; the least saturated option.", "Low", ENV + "; " + AA + "; " + BLOCK],
		8: ["Dark navy void so the map pops, strong high sun with crisp shadows, heavy AO, ACES with extra contrast. ACES pushes bright greens toward yellow; exposure 0.85 keeps that in check.", "Low", ENV + "; " + AA],
		9: ["A generated 33³ grading LUT: vibrance lifts muted colours such as the sky while leaving strong ones alone, greens drop 25% saturation and shift slightly toward yellow, and shadows cool. Aimed at 'vibrant without over-saturated'.", "Free (LUT is part of tonemapping)", ENV + "; " + AA + "; " + LUT],
		10: ["Per-channel curves: teal-lifted shadows, warm mids and highlights. A muted, filmic grade; the sky goes teal-grey.", "Free", ENV + "; " + AA + "; " + LUT],
		11: ["Near and far depth-of-field blur plus +20% saturation fake a tabletop miniature. The focus band is wide enough that units stay sharp; in game the focus distance should follow the camera zoom.", "Medium (DOF)", ENV + "; " + AA + "; CameraRig.gd (focus follows zoom)"],
		12: ["Height fog below the playfield dissolves the map's dirt skirt into sky-coloured haze, plus light aerial perspective. Reads as an island floating in cloud. Subtle.", "Free", ENV + "; " + AA],
		13: ["Wide soft bloom, light volumetric haze with forward scattering, lavender sky. Soft and dreamy, at some cost to readability at the far edge.", "Medium (volumetric fog)", ENV + "; " + AA],
		14: ["Glossy clearcoat on blocks and units plus screen-space reflections: board-game plastic. Units get specular highlights; blocks pick up a sky sheen.", "Medium (SSR)", ENV + "; " + AA + "; block + unit materials"],
		15: ["Godot's built-in toon diffuse on blocks and units (hard terminator), toon specular and rim on units, blue-violet ambient. Two-tone faces and crisp shadows.", "Free", ENV + "; " + AA + "; block + unit materials"],
		16: ["Custom lighting that bands the sun into steps and adds violet straight into shaded areas. It is added rather than multiplied because green albedo has almost no blue to tint. Anime-style shadows.", "Free", ENV + "; " + AA + "; " + BLOCK + "; unit materials"],
		17: ["Voxel-art hand shading, which means shading with hue as well as brightness: tops brighter and warmer, south faces slightly cool, east faces darker and blue-shifted, plus fake contact AO at wall bases. Faces read clearly whatever the sun does.", "Free", ENV + "; " + AA + "; " + BLOCK],
		18: ["The block shader remaps green hues only: −28% saturation, +6% value, 10° toward yellow. Tackles 'sharp green blocks are too over-saturated' without touching the .vox art.", "Free", ENV + "; " + AA + "; " + BLOCK],
		19: ["World-space tile grid lines on blocks, contact AO at wall bases, raised ground a little brighter per metre, darker map skirt, slightly calmer greens. For reading tiles, elevation and cover at a glance.", "Free", ENV + "; " + AA + "; " + BLOCK],
		20: ["Flat and bright: Linear tonemap, high flat ambient, colour driven mostly by per-face tints, crisp blue-tinted shadows, cyan backdrop. 'Vector voxel' in the style of Crossy Road.", "Free", ENV + "; " + AA + "; " + BLOCK],
		21: ["Full-screen depth + normal outline pass: 1 px dark ink silhouettes. It also exposes height changes that match the floor colour, such as the long raised strip on the right. Uses SMAA, because MSAA breaks the edge tests.", "Low (one full-screen pass)", ENV + "; " + AA + "; " + OUTLINE],
		22: ["#15's toon shading with 2 px ink outlines, crease lines where walls meet the floor, and +15% saturation. Comic-book.", "Low", ENV + "; " + AA + "; " + OUTLINE + "; block + unit materials"],
		23: ["The outline pass used for definition rather than ink: silhouettes are a darker shade of the colour underneath, top edges of blocks get a light bevel line, floor/wall creases a soft dark line (t3ssel8r-style convex highlights). Subtle at full resolution; zoom in to see it.", "Low", ENV + "; " + AA + "; " + OUTLINE],
		24: ["Godot 4.7's new nearest-neighbour 3D scaling renders the world at 33% resolution while the HUD stays sharp, plus 1 px tinted outlines and bevel highlights (t3ssel8r-style). The camera needs pixel-snapping to avoid shimmer while panning.", "Lowest (a ninth of the pixels)", ENV + "; " + AA + " + 3D scaling; " + OUTLINE + "; camera snapping"],
		25: ["Two shadow-casting suns (orange key, pale-yellow second) give double shadows; warm desert sky; grass shifted to dry yellow. A Star Wars-style planet theme.", "Medium (second shadow map)", ENV + " + second light; " + AA + "; " + BLOCK],
		26: ["Magenta sun against teal ambient (complementary colours), violet-to-navy sky, ACES and glow. A stylised alien world.", "Low", ENV + "; " + AA],
		27: ["Camera FOV narrowed from 75° to 40° and pulled back to keep the framing. Much less perspective distortion, so the map reads like a tabletop and walls stay parallel. Changes the camera, not the art.", "Free", ENV + "; " + AA + "; Camera3D fov + CameraRig distances"],
		28: ["Claude's pick for the todo notes: #01's lighting with softer sun shadows; the block shader with calmer greens (green-only −18% saturation), light hand-shaded faces, contact AO at wall bases and a slight elevation gain; bevel outlines like #23; and a gentle vibrance LUT with cool shadows.", "Low", ENV + "; " + AA + "; " + BLOCK + "; " + OUTLINE + "; " + LUT],
	}
