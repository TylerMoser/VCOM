"""Preview images: a small isometric voxel renderer (exposed faces, flat shading, painter's
order) and contact sheets. Only for looking at the models; MagicaVoxel and the game draw
them their own ways."""
import math

from PIL import Image, ImageDraw, ImageFont

VIEWS = {
    # the camera's direction from the model, across the ground, and its elevation
    'front_left': ((1, -1), 28),    # the front (-y) and the figure's left (+x)
    'front_right': ((-1, -1), 28),
    'back_right': ((-1, 1), 28),    # the back (+y) and the figure's right
    'back_left': ((1, 1), 28),
    'front': ((0, -1), 8),
    'side': ((1, 0), 8),
    'back': ((0, 1), 8),
}

FONT = None


def _font(size):
    try:
        return ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', size)
    except Exception:
        return ImageFont.load_default()


def render(colors, view='front_left', scale=9, bg=(58, 66, 80), outline=True, glass=None, glow=None):
    """[colors] {(x, y, z): (r, g, b)}; [glass] the set of positions drawn see-through."""
    glass = glass or set()
    glow = glow or set()
    (cx, cy), elev = VIEWS[view]
    hl = math.hypot(cx, cy)
    cx, cy = cx / hl, cy / hl
    e = math.radians(elev)
    rx, ry = cy, -cx
    ce, se = math.cos(e), math.sin(e)

    def proj(x, y, z):
        fwd = -(x * cx + y * cy)
        return x * rx + y * ry, z * ce + fwd * se, fwd * ce - z * se

    occ = set(colors)
    solid = occ - glass
    tvec = (cx * ce, cy * ce, se)
    faces = []
    dirs = [(0, 0, 1), (0, 0, -1), (1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0)]
    for p, col in colors.items():
        x, y, z = p
        is_glass = p in glass
        for nx, ny, nz in dirs:
            q = (x + nx, y + ny, z + nz)
            if q in solid or (is_glass and q in glass) or (not is_glass and q in occ and q not in glass):
                continue
            facing = nx * tvec[0] + ny * tvec[1] + nz * tvec[2]
            if facing <= 1e-6:
                continue
            if nz > 0:
                light = 1.0
            elif nz < 0:
                light = 0.5
            else:
                light = 0.74 + 0.14 * (nx * 0.6 - ny * 0.8)
            if p in glow:
                light = 1.15
            if nz:
                zz = z + (1 if nz > 0 else 0)
                corners = [(x, y, zz), (x + 1, y, zz), (x + 1, y + 1, zz), (x, y + 1, zz)]
            elif nx:
                xx = x + (1 if nx > 0 else 0)
                corners = [(xx, y, z), (xx, y + 1, z), (xx, y + 1, z + 1), (xx, y, z + 1)]
            else:
                yy = y + (1 if ny > 0 else 0)
                corners = [(x, yy, z), (x + 1, yy, z), (x + 1, yy, z + 1), (x, yy, z + 1)]
            pts = [proj(*c) for c in corners]
            depth = proj(x + 0.5 + nx * 0.5, y + 0.5 + ny * 0.5, z + 0.5 + nz * 0.5)[2]
            shaded = tuple(max(0, min(255, int(c * light))) for c in col)
            faces.append((depth, pts, shaded, is_glass))
    if not faces:
        return Image.new('RGB', (40, 40), bg)
    xs = [q[0] for f in faces for q in f[1]]
    ys = [q[1] for f in faces for q in f[1]]
    minx, maxx, miny, maxy = min(xs), max(xs), min(ys), max(ys)
    pad = 3
    w = int((maxx - minx) * scale) + pad * 2 + 1
    h = int((maxy - miny) * scale) + pad * 2 + 1
    img = Image.new('RGBA', (w, h), bg + (255,))
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(img)
    faces.sort(key=lambda f: -f[0])
    for depth, pts, col, is_glass in faces:
        poly = [((q[0] - minx) * scale + pad, (maxy - q[1]) * scale + pad) for q in pts]
        if is_glass:
            g = ImageDraw.Draw(layer)
            g.polygon(poly, fill=col + (110,), outline=col + (200,))
            img = Image.alpha_composite(img, layer)
            layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            dr = ImageDraw.Draw(img)
        else:
            dr.polygon(poly, fill=col, outline=tuple(int(c * 0.8) for c in col) if outline else None)
    return img.convert('RGB')


def model_colors(m):
    colors = {p: vx.color for p, vx in m.v.items()}
    glass = {p for p, vx in m.v.items() if vx.mat and vx.mat[0] == 'glass'}
    glow = {p for p, vx in m.v.items() if vx.mat and vx.mat[0] == 'emit'}
    return colors, glass, glow


def turnaround(m, scale=8, views=('front_left', 'back_right'), bg=(58, 66, 80)):
    colors, glass, glow = model_colors(m)
    ims = [render(colors, v, scale, bg, glass=glass, glow=glow) for v in views]
    w = sum(i.width for i in ims) + 6 * (len(ims) - 1)
    h = max(i.height for i in ims)
    out = Image.new('RGB', (w, h), bg)
    x = 0
    for i in ims:
        out.paste(i, (x, h - i.height))
        x += i.width + 6
    return out


def sheet(items, cols, cell=(330, 300), title=None, bg=(36, 41, 50), label_size=13):
    """[items]: (label, image) pairs, laid out [cols] across."""
    rows = max(1, (len(items) + cols - 1) // cols)
    top = 34 if title else 0
    W, H = cell
    out = Image.new('RGB', (W * cols, H * rows + top), bg)
    dr = ImageDraw.Draw(out)
    font = _font(label_size)
    if title:
        dr.text((8, 6), title, fill=(255, 255, 255), font=_font(20))
    for i, (label, im) in enumerate(items):
        r, c = divmod(i, cols)
        im2 = im.copy()
        im2.thumbnail((W - 8, H - 26))
        x0 = c * W + (W - im2.width) // 2
        y0 = top + r * H + 4 + (H - 26 - im2.height)
        out.paste(im2, (x0, y0))
        dr.text((c * W + 6, top + r * H + H - 21), label, fill=(225, 225, 225), font=font)
    return out
