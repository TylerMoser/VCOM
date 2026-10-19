## Simple map symbols for the settlements, drawn into textures at run time, for
## the styles that show a settlement as a symbol rather than its picture: a
## kingdom's capital a ringed dot, a duchy's a square, a town a dot, a village a
## ring, a hamlet a small dot. Each is drawn at 64 pixels with smooth edges and
## shrunk by the settlement's icon_height, as the pictures are.
extends RefCounted

const SIZE := 64

## The symbol for each group under Settlements: shape and the height in
## screen pixels it is drawn at.
const FOR_GROUP := {
	"KingdomCapitals": ["capital", 15.0],
	"DuchyCapitals": ["square", 11.0],
	"CountyCapitals": ["dot", 8.0],
	"Villages": ["ring", 6.5],
	"Hamlets": ["small", 4.0],
}


## A symbol's texture: [param shape] is "capital", "square", "dot", "ring" or
## "small", in [param ink] with a [param halo] round it.
static func texture(shape: String, ink: Color, halo: Color, paper := Color.WHITE) -> ImageTexture:
	var image := Image.create(SIZE, SIZE, false, Image.FORMAT_RGBA8)
	var samples := 4
	for y in SIZE:
		for x in SIZE:
			var sum := Color(0, 0, 0, 0)
			for sy in samples:
				for sx in samples:
					var p := Vector2(x + (sx + 0.5) / samples, y + (sy + 0.5) / samples) / SIZE * 2.0 - Vector2.ONE
					sum += _shade(shape, p, ink, halo, paper)
			sum /= samples * samples
			# Store as straight alpha.
			if sum.a > 0.0:
				image.set_pixel(x, y, Color(sum.r / sum.a, sum.g / sum.a, sum.b / sum.a, sum.a))
	return ImageTexture.create_from_image(image)


## The colour at p (-1 to 1 across), as premultiplied alpha.
static func _shade(shape: String, p: Vector2, ink: Color, halo: Color, paper: Color) -> Color:
	var r := p.length()
	var square := maxf(absf(p.x), absf(p.y))
	var c := Color(0, 0, 0, 0)
	match shape:
		"capital":
			if r <= 1.0:
				c = halo
			if r <= 0.86:
				c = ink
			if r <= 0.62:
				c = paper
			if r <= 0.36:
				c = ink
		"square":
			if square <= 0.95:
				c = halo
			if square <= 0.72:
				c = ink
		"dot":
			if r <= 1.0:
				c = halo
			if r <= 0.72:
				c = ink
		"ring":
			if r <= 1.0:
				c = halo
			if r <= 0.8:
				c = ink
			if r <= 0.5:
				c = paper
		"small":
			if r <= 1.0:
				c = halo
			if r <= 0.65:
				c = ink
	return Color(c.r * c.a, c.g * c.a, c.b * c.a, c.a)
