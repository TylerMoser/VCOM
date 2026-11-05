"""Heads and what goes on them: head shapes, eyes, brows, noses, mouths, ears, snouts,
beaks, horns, hair, beards and headgear. Everything here rides on the Head bone.

A head is a box x x0..x1 (odd width, centred on x 16), y y0 (its face) .. y1, z z0..z1;
the base head is 9 x 8 x 8 at x 12-20, y 12-19, z 20-27."""
from core import shade, mix

WHITE = (240, 238, 230)
BLACK = (28, 26, 30)
DARK = (48, 40, 40)


class Head:
    def __init__(self, x0, x1, y0, y1, z0, z1):
        self.x0, self.x1, self.y0, self.y1, self.z0, self.z1 = x0, x1, y0, y1, z0, z1

    @property
    def w(self):
        return self.x1 - self.x0 + 1

    @property
    def h(self):
        return self.z1 - self.z0 + 1

    @property
    def d(self):
        return self.y1 - self.y0 + 1


def make_head(m, color, group='skin', w=9, d=8, h=8, z0=20, y0=12, style='base', bone='Head'):
    """Replaces the base head with a new one. Styles: base (its eight corners off), box,
    soft (every edge off), round (a superellipsoid), dome (soft below, round above),
    jaw (narrower at the top), wedge (narrower at the bottom)."""
    m.v = {p: vx for p, vx in m.v.items() if vx.part != 'head'}
    x0, x1 = 16 - w // 2, 16 + w // 2
    y1, z1 = y0 + d - 1, z0 + h - 1
    cx, cy, cz = 16, (y0 + y1) / 2, (z0 + z1) / 2
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                ex = (x in (x0, x1)) + (y in (y0, y1)) + (z in (z0, z1))
                if style == 'base' and ex == 3:
                    continue
                if style == 'soft' and ex >= 2:
                    continue
                if style == 'round':
                    nx = (x - cx) / (w / 2); ny = (y - cy) / (d / 2); nz = (z - cz) / (h / 2)
                    if nx ** 4 + ny ** 4 + nz ** 4 > 1.05:
                        continue
                if style == 'dome':
                    if z <= cz and ex >= 3:
                        continue
                    if z > cz:
                        nx = (x - cx) / (w / 2); ny = (y - cy) / (d / 2); nz = (z - cz) / (h / 2)
                        if nx ** 4 + ny ** 4 + nz ** 2 > 1.08:
                            continue
                if style == 'jaw' and z >= z1 - 1 and x in (x0, x1):
                    continue
                if style == 'wedge' and z <= z0 + 1 and x in (x0, x1):
                    continue
                m.set((x, y, z), color, group, bone, 'head')
    m.head = Head(x0, x1, y0, y1, z0, z1)
    return m.head


def face_cell(m, hd, x, z, color, group, mat=None, depth=0):
    """Paints the frontmost voxel of column (x, z) of the head, or puts one [depth] in front
    of the face (negative: set into it)."""
    if depth == 0:
        y = m.front_y(x, z)
        if y is None:
            y = hd.y0
        m.set((x, y, z), color, group, 'Head', 'head', mat)
    elif depth > 0:
        y = (m.front_y(x, z) or hd.y0) - depth
        m.set((x, y, z), color, group, 'Head', 'head', mat)
    else:
        y = (m.front_y(x, z) or hd.y0)
        for k in range(-depth):
            m.remove((x, y + k, z))
        m.set((x, y - depth, z), color, group, 'Head', 'head', mat)


def eye_columns(gap=3, width=2):
    """The x columns of the right eye (low x) and the left, [gap] voxels apart about x 16."""
    inner = (gap + 1) // 2
    right = list(range(16 - inner - width + 1, 16 - inner + 1))
    left = [32 - x for x in reversed(right)]
    return right, left


def eyes(m, hd, style='template', iris=(70, 120, 200), z=None, gap=3, width=2, height=2,
         white=WHITE, dark=BLACK, glow=False, depth=0):
    """Eyes on the face. Styles: template (a dark lid row over white and iris), pupil (white
    with the iris inside and below), dot (solid dark), bead (one dark voxel), slit (iris with
    a dark inner column), glow (the iris glowing), sclera (an iris on white, a dark centre),
    closed (a single dark line), angry (template with the lids slanting in), big (three tall:
    dark lid, iris, white shine below)."""
    if z is None:
        z = hd.z0 + 2
    right, left = eye_columns(gap, width)
    mat = ('emit', 0.8) if glow or style == 'glow' else None
    for side, cols in (('r', right), ('l', left)):
        inner = cols[-1] if side == 'r' else cols[0]
        outer = cols[0] if side == 'r' else cols[-1]
        for x in cols:
            for k in range(height):
                zz = z + k
                top = k == height - 1
                if style == 'template':
                    c = dark if top else (iris if (x == inner or width == 1) else white)
                elif style == 'pupil':
                    c = iris if (x == inner and not top) else white
                    if x == inner and top and height > 2:
                        c = iris
                elif style == 'dot':
                    c = dark
                elif style == 'bead':
                    c = dark if (x == inner and k == 0) else None
                elif style == 'slit':
                    c = dark if x == inner else iris
                elif style == 'glow':
                    c = iris
                elif style == 'sclera':
                    c = dark if (x == inner and not top) else (iris if x == inner else white)
                elif style == 'closed':
                    c = dark if k == 0 else None
                elif style == 'angry':
                    # a glare: the lid slanting down to the inner corner, a dark pupil there
                    if top:
                        c = dark if x == inner else None
                    else:
                        c = dark if x == inner else white
                elif style == 'big':
                    c = dark if top else (iris if k == height - 2 else (white if x == outer else iris))
                else:
                    c = dark
                if c is None:
                    continue
                face_cell(m, hd, x, zz, c, 'eye', mat if c != white else None, depth)
    return right, left


def brows(m, hd, color, z=None, gap=3, width=2, style='flat', depth=0):
    """Brows over the eyes: flat, angry (high outside, low inside), worried, bushy (standing
    out a voxel), uni (one bar across)."""
    if z is None:
        z = hd.z0 + 4
    right, left = eye_columns(gap, width)
    if style == 'uni':
        for x in range(right[0], left[-1] + 1):
            face_cell(m, hd, x, z, color, 'hair', None, 1 if depth else 0)
        return
    for cols, inner in ((right, right[-1]), (left, left[0])):
        for x in cols:
            zz = z
            if style == 'angry' and x == inner:
                zz = z - 1
            if style == 'worried' and x != inner:
                zz = z - 1
            face_cell(m, hd, x, zz, color, 'hair', None, 1 if style == 'bushy' or depth else 0)


def nose(m, hd, style='button', color=None, z=None):
    """button (one voxel out), long (two out), big (three wide, two tall, out), pig (a
    snout with nostrils), hook (out and down), tip (one voxel, the face's colour)."""
    if z is None:
        z = hd.z0 + 1
    col = color or shade(m.get((16, hd.y0, z)).color if m.get((16, hd.y0, z)) else (200, 160, 130), 0.95)
    y = hd.y0 - 1
    if style == 'button':
        m.set((16, y, z), col, 'skin', 'Head', 'head')
    elif style == 'long':
        m.set((16, y, z), col, 'skin', 'Head', 'head'); m.set((16, y - 1, z), col, 'skin', 'Head', 'head')
    elif style == 'big':
        m.box(15, 17, y, y, z - 1, z, col, 'skin', 'Head', 'head'); m.set((16, y - 1, z - 1), col, 'skin', 'Head', 'head')
    elif style == 'pig':
        m.box(15, 17, y, y, z - 1, z, col, 'skin', 'Head', 'head')
        m.set((15, y, z - 1), shade(col, 0.55), 'mouth', 'Head', 'head'); m.set((17, y, z - 1), shade(col, 0.55), 'mouth', 'Head', 'head')
    elif style == 'hook':
        m.set((16, y, z), col, 'skin', 'Head', 'head'); m.set((16, y, z - 1), col, 'skin', 'Head', 'head'); m.set((16, y - 1, z), col, 'skin', 'Head', 'head')


def mouth(m, hd, style='line', color=DARK, z=None, width=3, tooth=WHITE):
    """line, smile (corners up), frown, open (two tall), grin (teeth showing), tusks (two
    lower tusks up past the lip), fangs (two upper fangs down), buck (two front teeth)."""
    if z is None:
        z = hd.z0
    half = width // 2
    xs = range(16 - half, 16 + half + 1)
    if style in ('line', 'smile', 'frown', 'open', 'grin'):
        for x in xs:
            face_cell(m, hd, x, z, color, 'mouth')
        if style == 'smile':
            face_cell(m, hd, 16 - half - 1, z + 1, color, 'mouth'); face_cell(m, hd, 16 + half + 1, z + 1, color, 'mouth')
        if style == 'frown':
            face_cell(m, hd, 16 - half - 1, z - 1, color, 'mouth'); face_cell(m, hd, 16 + half + 1, z - 1, color, 'mouth')
        if style == 'open':
            for x in xs:
                face_cell(m, hd, x, z - 1, color, 'mouth')
        if style == 'grin':
            for x in xs:
                face_cell(m, hd, x, z, tooth, 'bone')
            face_cell(m, hd, 16 - half - 1, z, color, 'mouth'); face_cell(m, hd, 16 + half + 1, z, color, 'mouth')
    if style == 'tusks':
        for x in (16 - half - 1, 16 + half + 1):
            m.set((x, hd.y0 - 1, z), tooth, 'bone', 'Head', 'head')
            m.set((x, hd.y0 - 1, z + 1), tooth, 'bone', 'Head', 'head')
        for x in xs:
            face_cell(m, hd, x, z, color, 'mouth')
    if style == 'fangs':
        for x in xs:
            face_cell(m, hd, x, z, color, 'mouth')
        for x in (16 - half, 16 + half):
            m.set((x, hd.y0 - 1, z), tooth, 'bone', 'Head', 'head')
    if style == 'buck':
        m.set((16, hd.y0 - 1, z), tooth, 'bone', 'Head', 'head')
        m.set((16, hd.y0 - 1, z - 1), tooth, 'bone', 'Head', 'head')


def cheeks(m, hd, color, z=None, gap=3, width=2):
    """Blush or cheek patches under the outer eye corners."""
    if z is None:
        z = hd.z0 + 1
    right, left = eye_columns(gap, width)
    face_cell(m, hd, right[0], z, color, 'skin'); face_cell(m, hd, left[-1], z, color, 'skin')


def snout(m, hd, color, length=3, w=5, h=3, z=None, nose_color=None, group='skin', taper=0, jaw=None,
          teeth=None, nostrils=True, top=None, nose_width=3, mouth=None):
    """A muzzle out of the face's lower half: [w] wide, [h] tall, [length] out, narrowing by
    [taper] voxels a side over its length. [jaw] paints its lower row; [top] its upper."""
    if z is None:
        z = hd.z0
    for k in range(1, length + 1):
        shrink = (taper * k) // max(1, length)
        half = max(0, w // 2 - shrink)
        hh = h
        for x in range(16 - half, 16 + half + 1):
            for dz in range(hh):
                c = color
                if jaw and dz == 0:
                    c = jaw
                if top and dz == hh - 1:
                    c = top
                m.set((x, hd.y0 - k, z + dz), c, group, 'Head', 'head')
        if teeth and k >= 1:
            for x in (16 - half, 16 + half):
                if k % 2 == 1:
                    m.set((x, hd.y0 - k, z), teeth, 'bone', 'Head', 'head')
    tip = hd.y0 - length
    half_tip = max(0, w // 2 - (taper * length) // max(1, length))
    if nose_color:
        nz = z + h - 1
        m.set((16, tip, nz), nose_color, 'detail', 'Head', 'head')
        if half_tip >= 1 and nose_width >= 3:
            m.set((15, tip, nz), nose_color, 'detail', 'Head', 'head'); m.set((17, tip, nz), nose_color, 'detail', 'Head', 'head')
    elif nostrils and half_tip >= 1:
        nz = z + h - 1
        m.set((15, tip, nz), shade(color, 0.6), 'detail', 'Head', 'head'); m.set((17, tip, nz), shade(color, 0.6), 'detail', 'Head', 'head')
    if mouth and h >= 2:
        # the mouth's line along the snout's sides, where its jaw meets its top
        for k in range(1, length + 1):
            shrink = (taper * k) // max(1, length)
            half = max(0, w // 2 - shrink)
            for x in (16 - half, 16 + half):
                m.set((x, hd.y0 - k, z), mouth, 'mouth', 'Head', 'head')
        if half_tip >= 1:
            for x in range(16 - half_tip, 16 + half_tip + 1):
                m.set((x, tip, z), mouth, 'mouth', 'Head', 'head')
        if teeth:
            for k in range(1, length + 1, 2):
                shrink = (taper * k) // max(1, length)
                half = max(0, w // 2 - shrink)
                for x in (16 - half, 16 + half):
                    m.set((x, hd.y0 - k, z), teeth, 'bone', 'Head', 'head')
    m.snout_info = (tip, half_tip, z, h, length)
    return tip


def beak(m, hd, color, style='cone', z=None, tip=None):
    """cone (short, tapering), hook (curved down, a raptor's), long (thin and far out, a
    roadrunner's), heavy (deep and thick, a crow's), duck (flat and wide)."""
    if z is None:
        z = hd.z0 + 1
    dark = tip or shade(color, 0.7)
    y = hd.y0 - 1
    if style == 'cone':
        m.box(15, 17, y, y, z, z + 1, color, 'horn', 'Head', 'head')
        m.box(16, 16, y - 1, y - 1, z, z + 1, color, 'horn', 'Head', 'head')
        m.set((16, y - 2, z), dark, 'horn', 'Head', 'head')
    elif style == 'hook':
        m.box(15, 17, y, y, z, z + 2, color, 'horn', 'Head', 'head')
        m.box(15, 17, y - 1, y - 1, z + 1, z + 2, color, 'horn', 'Head', 'head')
        m.box(16, 16, y - 2, y - 2, z + 1, z + 2, color, 'horn', 'Head', 'head')
        m.set((16, y - 2, z), dark, 'horn', 'Head', 'head')
        m.set((16, y - 3, z + 1), dark, 'horn', 'Head', 'head')
    elif style == 'long':
        m.box(15, 17, y, y, z, z + 1, color, 'horn', 'Head', 'head')
        for k in range(1, 6):
            m.set((16, y - k, z), color, 'horn', 'Head', 'head')
            if k < 4:
                m.set((16, y - k, z + 1), color, 'horn', 'Head', 'head')
        m.set((16, y - 6, z), dark, 'horn', 'Head', 'head')
    elif style == 'heavy':
        m.box(14, 18, y, y, z - 1, z + 2, color, 'horn', 'Head', 'head')
        m.box(15, 17, y - 1, y - 2, z - 1, z + 1, color, 'horn', 'Head', 'head')
        m.box(16, 16, y - 3, y - 3, z - 1, z, dark, 'horn', 'Head', 'head')
    elif style == 'duck':
        m.box(14, 18, y, y - 3, z, z, color, 'horn', 'Head', 'head')
        m.box(14, 18, y, y - 2, z + 1, z + 1, color, 'horn', 'Head', 'head')


def ears(m, hd, style, color, inner=None, z=None, size=1):
    """Ears for both sides. Styles: human, elf, elf_long, cat, fox, lynx, dog_pointed,
    dog_floppy, mouse, hamster, rabbit, rabbit_lop, bat, elephant, round (small, on top),
    bear, fin, frill."""
    inner = inner or shade(color, 0.8)
    top = hd.z1
    if z is None:
        z = hd.z0 + 3
    ym = (hd.y0 + hd.y1) // 2
    def both(x, y, zz, c, g='skin'):
        m.dot(x, y, zz, c, g, 'Head', 'head', sym=True)
    side = hd.x0 - 1  # the right side's outer column
    if style == 'human':
        for zz in (z - 1, z):
            both(side, ym, zz, color); both(side, ym + 1, zz, color)
    elif style in ('elf', 'elf_long'):
        n = 3 if style == 'elf' else 5
        for k in range(n):
            both(side - k, ym, z - 1 + k, color)
            both(side - k, ym + 1, z - 1 + k, color if k < n - 1 else color)
            if k < n - 1:
                both(side - k, ym, z + k, color)
        both(side, ym, z - 2, color)
    elif style in ('cat', 'fox', 'lynx', 'dog_pointed'):
        hgt = {'cat': 3, 'fox': 4, 'lynx': 4, 'dog_pointed': 3}[style]
        base = 3 if style != 'fox' else 4
        x_out = hd.x0
        for k in range(hgt):
            wdt = max(1, base - k)
            for x in range(x_out, x_out + wdt):
                for y in (ym - 1, ym):
                    both(x, y, top + 1 + k, color if (y == ym or x == x_out or k == hgt - 1) else inner)
        if style == 'lynx':
            both(x_out, ym, top + hgt + 1, shade(color, 0.4), 'fur')
    elif style == 'dog_floppy':
        for zz in range(z - 3, top):
            for y in range(ym - 1, ym + 2):
                both(side, y, zz, color if zz < top - 1 or y != ym - 1 else color)
        both(side, ym, top, color)
    elif style in ('mouse', 'hamster'):
        r = (1 + size) if style == 'mouse' else 2
        cxe = hd.x0 + (0 if style == 'mouse' else 1)
        cze = top + (1 if style == 'mouse' else 0)
        for x in range(cxe - r, cxe + r + 1):
            for zz in range(cze - r, cze + r + 1):
                if (x - cxe) ** 2 + (zz - cze) ** 2 <= r * r + 0.5 and zz > top - 1:
                    both(x, ym, zz, inner if (abs(x - cxe) < r - 0 and abs(zz - cze) < r - 0 and r > 2) else color)
                    both(x, ym + 1, zz, color)
    elif style == 'rabbit':
        for k in range(1, 6 * size + 1):
            for x in (hd.x0 + 1, hd.x0 + 2):
                both(x, ym, top + k, color)
                both(x, ym - 1, top + k, inner if (x == hd.x0 + 2 or True) and 1 < k < 6 * size else color)
    elif style == 'rabbit_lop':
        for zz in range(z - 4, top + 1):
            for y in range(ym - 1, ym + 1):
                both(side, y, zz, color)
                both(side - 1, y, zz, color if zz != top else color)
        for y in range(ym - 1, ym + 1):
            both(side, y, top + 1, color)
    elif style == 'bat':
        for k in range(5):
            wdt = max(1, 3 - k // 2)
            for x in range(hd.x0 - k // 2, hd.x0 - k // 2 + wdt):
                both(x, ym, top + 1 + k, color)
                if k < 4:
                    both(x, ym - 1, top + 1 + k, inner)
    elif style == 'elephant':
        # flat against the head's sides, out and back, above the arms (z 19 and up)
        for x in range(hd.x0 - 3 - size, hd.x0):
            for y in range(hd.y0 + 2, hd.y1 + 2):
                for zz in range(19, top + 2):
                    dx = (hd.x0 - x - 0.5) / (3.0 + size); dy = (y - (hd.y0 + hd.y1) / 2 - 1) / 4.2; dz = (zz - (top + 19) / 2) / 5.6
                    if dx * dx * 0.3 + dy * dy + dz * dz <= 1.0 and dx <= 1.0:
                        outer = x == hd.x0 - 3 - size or dy * dy + dz * dz > 0.7
                        both(x, y, zz, color if outer else inner)
    elif style == 'round':
        for x in (hd.x0, hd.x0 + 1):
            both(x, ym, top + 1, color)
        both(hd.x0, ym, top + 2, color) if size > 1 else None
    elif style == 'bear':
        for x in range(hd.x0 - 1, hd.x0 + 2):
            for zz in (top, top + 1):
                both(x, ym, zz, color if not (x == hd.x0 and zz == top + 1) else inner)
                both(x, ym + 1, zz, color)
    elif style == 'fin':
        for k in range(4):
            for zz in range(z - 1, z + 3 - k // 2):
                both(side - k, ym + k, zz, color if k < 3 else inner)
    elif style == 'frill':
        for k in range(1, 4):
            for zz in range(hd.z0, top + 1 - k):
                both(hd.x0 - k, ym + k, zz, color if zz % 2 else inner)


def horns(m, hd, style, color, tip=None, z=None):
    """bull (out and up), long_bull (wider), ram (curled), goat (back and up), small (two
    nubs), rhino (one, up the middle, a beetle's), unicorn, devil, antlers, stubs."""
    tip = tip or shade(color, 1.25)
    top = hd.z1
    ym = hd.y0 + 2
    if z is None:
        z = top - 1
    def both(x, y, zz, c):
        m.dot(x, y, zz, c, 'horn', 'Head', 'head', sym=True)
    if style in ('bull', 'long_bull'):
        n = 4 if style == 'bull' else 6
        pts = [(hd.x0 - 1 - k, z + (k * k) // 6) for k in range(n)]
        for i, (x, zz) in enumerate(pts):
            c = tip if i == n - 1 else color
            both(x, ym, zz, c); both(x, ym + 1, zz, c)
            if i < n - 2:
                both(x, ym, zz + 1, c); both(x, ym + 1, zz + 1, c)
        x, zz = pts[-1]
        both(x, ym, zz + 1, tip); both(x, ym, zz + 2, tip)
    elif style == 'ram':
        ring = [(0, 0), (-1, 0), (-2, 0), (-3, -1), (-3, -2), (-3, -3), (-2, -4), (-1, -4), (0, -3), (0, -2)]
        for i, (dx, dz) in enumerate(ring):
            for y in (ym + 1, ym + 2):
                both(hd.x0 + dx, y, top + dz, color if i < len(ring) - 2 else tip)
    elif style == 'goat':
        for k in range(5):
            both(hd.x0 + 2, ym + 1 + k, top + 1 + k // 2 + (1 if k > 2 else 0), color if k < 4 else tip)
            both(hd.x0 + 2, ym + 1 + k, top + 1 + k // 2, color if k < 4 else tip)
    elif style == 'small':
        both(hd.x0 + 1, ym + 1, top + 1, color); both(hd.x0 + 1, ym + 1, top + 2, tip)
    elif style == 'stubs':
        both(hd.x0 + 2, ym, top + 1, color)
    elif style == 'devil':
        both(hd.x0 + 1, ym + 1, top + 1, color); both(hd.x0, ym + 1, top + 2, color); both(hd.x0, ym + 1, top + 3, tip)
    elif style == 'rhino':
        for k in range(6):
            m.set((16, hd.y0 + 1 - k // 3, top + 1 + k), color if k < 5 else tip, 'horn', 'Head', 'head')
            if k < 3:
                m.set((15, hd.y0 + 1, top + 1 + k), color, 'horn', 'Head', 'head')
                m.set((17, hd.y0 + 1, top + 1 + k), color, 'horn', 'Head', 'head')
        m.set((15, hd.y0 - 1, top + 5), tip, 'horn', 'Head', 'head'); m.set((17, hd.y0 - 1, top + 5), tip, 'horn', 'Head', 'head')
    elif style == 'unicorn':
        for k in range(5):
            m.set((16, hd.y0 + 1 - k // 2, top + 1 + k), color if k < 4 else tip, 'horn', 'Head', 'head')
    elif style == 'antlers':
        for k in range(4):
            both(hd.x0 + 1 - k, ym + 2, top + 1 + k, color)
        both(hd.x0 - 1, ym + 2, top + 2 + 1, color); both(hd.x0 - 1, ym + 2, top + 2 + 2, tip)
        both(hd.x0 + 1, ym + 2, top + 3, color); both(hd.x0 + 1, ym + 2, top + 4, tip)
        both(hd.x0 - 2, ym + 2, top + 5, tip)


def hair(m, hd, color, style='short', fringe=True, highlight=None):
    """Hair on the head, recolouring its outside and adding volume: short, crop, bowl,
    long (to the shoulders), ponytail, bun, braids, mohawk, spiky, curly, swept, bob, bald
    (a ring round the back), topknot, afro, side (parted). Leaves the face."""
    hl = highlight or shade(color, 1.18)
    z0, z1, x0, x1, y0, y1 = hd.z0, hd.z1, hd.x0, hd.x1, hd.y0, hd.y1
    face_top = z0 + (4 if fringe else 5)
    def paint_top(depth_rows):
        for p, vx in list(m.v.items()):
            if vx.part != 'head' or vx.group in ('eye', 'mouth', 'bone', 'horn'):
                continue
            x, y, z = p
            if not (x0 <= x <= x1 and y0 <= y <= y1 and z0 <= z <= z1):
                continue  # ears, snouts and the rest stand outside the head itself
            if z >= z1 - depth_rows + 1 or (y >= y0 + 1 and z >= face_top - 1 and (x in (x0, x1) or y == y1)) or (y == y1 and z >= z0 + 2):
                if style == 'bald' and z >= z1 - 1:
                    continue
                vx.color = color; vx.group = 'hair'
    if style == 'bald':
        for p, vx in list(m.v.items()):
            if vx.part == 'head' and p[1] >= y1 - 1 and z0 + 2 <= p[2] <= z0 + 4:
                vx.color = color; vx.group = 'hair'
        return
    paint_top(2)
    # fringe across the face's top row
    if fringe and style not in ('mohawk', 'topknot'):
        for x in range(x0, x1 + 1):
            for z in (z1, z1 - 1):
                if style == 'swept' and z == z1 - 1 and x > 16:
                    continue
                y = m.front_y(x, z)
                if y is not None:
                    m.set((x, y, z), color, 'hair', 'Head', 'head')
        for x in (x0, x1):
            for z in range(face_top - 1, z1):
                y = m.front_y(x, z)
                if y is not None:
                    m.set((x, y, z), color, 'hair', 'Head', 'head')
    def add(x, y, z, c=None):
        if not m.has((x, y, z)):
            m.set((x, y, z), c or color, 'hair', 'Head', 'head')
    if style in ('short', 'side', 'swept', 'bowl', 'curly', 'spiky', 'afro', 'bob', 'long', 'ponytail', 'bun', 'braids', 'topknot'):
        # a layer of volume over the crown
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                if style in ('short', 'side', 'swept') and (x in (x0, x1) or y in (y0, y1)):
                    continue
                add(x, y, z1 + 1, hl if (x + y) % 5 == 0 else color)
    if style == 'bowl':
        for x in range(x0 - 1, x1 + 2):
            for z in range(z1 - 2, z1 + 1):
                add(x, y0 - 1, z) if z == z1 or x in (x0 - 1, x1 + 1) else None
        for y in range(y0, y1 + 2):
            for z in range(z1 - 3, z1 + 1):
                add(x0 - 1, y, z); add(x1 + 1, y, z)
    if style == 'spiky':
        for (x, y, h) in [(13, 14, 2), (16, 13, 3), (19, 14, 2), (14, 17, 2), (18, 17, 2), (16, 16, 2), (12, 16, 1), (20, 16, 1)]:
            for k in range(h):
                add(x, y, z1 + 2 + k, hl if k == h - 1 else color)
    if style == 'curly':
        for x in range(x0 - 1, x1 + 2):
            for y in range(y0, y1 + 2):
                for z in range(z1 - 1, z1 + 3):
                    edge = x in (x0 - 1, x1 + 1) or y == y1 + 1 or z == z1 + 2
                    if edge and (x * 3 + y * 5 + z * 7) % 4 != 0 and not (y <= y0 + 1 and z < z1 + 1):
                        add(x, y, z, hl if (x + z) % 3 == 0 else color)
    if style == 'afro':
        cx, cy, cz = 16, (y0 + y1) / 2 + 0.5, z1 - 0.5
        for x in range(x0 - 2, x1 + 3):
            for y in range(y0 - 1, y1 + 3):
                for z in range(z0 + 3, z1 + 5):
                    if ((x - cx) / 6.5) ** 2 + ((y - cy) / 6.0) ** 2 + ((z - cz) / 5.5) ** 2 <= 1 and not (y < y0 + 1 and z < z1 - 1):
                        add(x, y, z, hl if (x + y + z) % 4 == 0 else color)
    if style in ('long', 'braids', 'bob'):
        bottom = {'long': 15, 'braids': 13, 'bob': z0}[style]
        for x in range(x0, x1 + 1):
            for z in range(bottom, z0 + 2):
                if style == 'braids' and x not in (x0 + 1, x1 - 1, 16):
                    continue
                add(x, y1 + 1, z)
        for y in range(y0 + 1, y1 + 2):
            for z in range(max(bottom, z0 - 1 if style != 'bob' else z0), z1 + 1):
                if style == 'braids':
                    continue
                add(x0 - 1, y, z); add(x1 + 1, y, z)
        for x in range(x0, x1 + 1):
            for z in range(z0 + 2, z1 + 1):
                add(x, y1 + 1, z)
        if style == 'braids':
            for x in (x0, x1):
                for z in range(z0 - 4, z0 + 3):
                    add(x - (1 if x == x0 else -1), y0 + 2, z, hl if z % 2 else color)
    if style == 'ponytail':
        for z in range(z1 - 2, z1 + 1):
            add(16, y1 + 1, z); add(15, y1 + 1, z); add(17, y1 + 1, z)
        for k in range(1, 7):
            add(16, y1 + 1 + (1 if k < 4 else 0), z1 - 1 - k, hl if k % 3 == 0 else color)
            add(16, y1 + 2, z1 - k)
    if style == 'bun':
        m.ellipsoid(16, y1 - 1, z1 + 2.5, 2.2, 2.2, 1.8, color, 'hair', 'Head', 'head', only_empty=True)
    if style == 'topknot':
        m.box(15, 17, y0 + 3, y0 + 5, z1 + 1, z1 + 2, color, 'hair', 'Head', 'head', only_empty=True)
        m.box(16, 16, y0 + 4, y0 + 4, z1 + 3, z1 + 4, color, 'hair', 'Head', 'head', only_empty=True)
    if style == 'mohawk':
        for p, vx in list(m.v.items()):
            if vx.group == 'hair' and vx.part == 'head' and not (15 <= p[0] <= 17) and p[2] >= z1 - 1:
                vx.color = shade(m.get((16, y0, z0 + 1)).color, 1.0) if m.get((16, y0, z0 + 1)) else vx.color
                vx.group = 'skin'
        for y in range(y0, y1 + 2):
            for k in range(1, 4 if y0 + 1 < y < y1 else 3):
                add(16, y, z1 + k, hl if k == 3 else color)
                if k == 1:
                    add(15, y, z1 + k); add(17, y, z1 + k)
    if style == 'side':
        for z in range(z1 - 2, z1 + 1):
            add(x0 - 1, y0 + 1, z)
        for x in range(x0, 16):
            add(x, y0 - 1, z1)


def beard(m, hd, color, style='full', highlight=None, length=None):
    """full (jaw and chin, down over the chest), long, braided (a long beard in two braids),
    forked, goatee, stubble (the jaw's colour), moustache, mutton (sideburns), dwarf (huge,
    to the belt), mutton_chops."""
    hl = highlight or shade(color, 1.15)
    z0, y0, x0, x1 = hd.z0, hd.y0, hd.x0, hd.x1
    def put(x, y, z, c=None):
        m.set((x, y, z), c or color, 'hair', 'Head', 'head')
    if style in ('full', 'long', 'braided', 'forked', 'dwarf'):
        # sideburns and jaw
        for x in (x0, x1):
            for z in range(z0, z0 + 3):
                y = m.front_y(x, z)
                if y is not None:
                    put(x, y, z)
        for x in range(x0, x1 + 1):
            for z in (z0, ):
                y = m.front_y(x, z)
                if y is not None:
                    put(x, y, z)
        if style != 'full' or True:
            for x in range(x0 + 1, x1):
                put(x, y0 - 1, z0)
        depth = {'full': 2, 'long': 5, 'braided': 7, 'forked': 6, 'dwarf': 9}[style] if length is None else length
        for k in range(1, depth + 1):
            z = z0 - k
            if style == 'forked' and k > depth // 2:
                xs = [14, 15, 17, 18]
            elif style == 'braided' and k > 2:
                xs = [14, 15, 17, 18] if k % 2 else [14, 18]
            else:
                shrink = (k * 2) // max(1, depth) if style != 'dwarf' else (k // 4)
                xs = list(range(x0 + 1 + shrink, x1 - shrink))
            for x in xs:
                c = hl if (x + k) % 4 == 0 else color
                put(x, y0 - 1, z, c)
                if k <= 2 or style == 'dwarf':
                    put(x, y0, z, c)
        if style == 'dwarf':
            for x in range(x0 + 2, x1 - 1):
                put(x, y0 - 2, z0 - 2, hl)
    elif style == 'goatee':
        for z in (z0, z0 - 1):
            put(16, y0 - 1 if z < z0 else y0, z)
        put(15, y0, z0); put(17, y0, z0); put(16, y0 - 1, z0 - 2)
    elif style == 'stubble':
        for x in range(x0, x1 + 1):
            y = m.front_y(x, z0)
            if y is not None:
                put(x, y, z0, color)
        for x in (x0, x1):
            y = m.front_y(x, z0 + 1)
            put(x, y, z0 + 1, color)
    elif style in ('moustache', 'mutton'):
        if style == 'moustache':
            for x in range(14, 19):
                put(x, y0 - 1, z0 + 1)
            put(13, y0 - 1, z0); put(19, y0 - 1, z0)
        else:
            for x in (x0, x1):
                for z in range(z0, z0 + 4):
                    y = m.front_y(x, z)
                    put(x, y, z)
            for x in range(14, 19):
                put(x, y0 - 1, z0 + 1)


def hat(m, hd, style, color, trim=None, extra=None):
    """Headgear: hood, cowl (hood up over a mask), helm (open-faced), great_helm (closed,
    a slit), horned_helm, cap (flat), beanie, bandana, wide (a wide-brimmed hat), cowboy,
    tricorne, wizard (a cone), top (a top hat), crown, circlet, headband, mining (a helmet
    with a lamp), goggles (glass on the brow), turban, beret, straw (a farmer's), fez,
    skullcap, laurel."""
    trim = trim or shade(color, 0.75)
    x0, x1, y0, y1, z0, z1 = hd.x0, hd.x1, hd.y0, hd.y1, hd.z0, hd.z1
    def put(x, y, z, c=None, g='cloth', mat=None):
        m.set((x, y, z), c or color, g, 'Head', 'head', mat)
    def shell(bottom, front_bottom, g='cloth', c=None, open_face=True):
        for x in range(x0 - 1, x1 + 2):
            for y in range(y0 - 1, y1 + 2):
                for z in range(bottom, z1 + 2):
                    inside = x0 <= x <= x1 and y0 <= y <= y1 and z <= z1
                    if inside:
                        continue
                    if open_face and y == y0 - 1 and z < front_bottom:
                        continue
                    corner = (x in (x0 - 1, x1 + 1)) + (y in (y0 - 1, y1 + 1)) + (z == z1 + 1)
                    if corner >= 3 or (corner == 2 and z == z1 + 1):
                        continue
                    put(x, y, z, c, g)
    if style in ('hood', 'cowl'):
        shell(z0 - 1 if style == 'hood' else z0, z1 - 1, 'cloth')
        for x in range(x0 + 1, x1):
            put(x, y0 - 1, z1, trim)
        if style == 'cowl':
            for x in range(x0, x1 + 1):
                for z in (z0, z0 + 1):
                    put(x, y0 - 1, z, trim)
        for x in range(x0 - 1, x1 + 2):
            put(x, y1 + 1, z0 - 1); put(x, y1 + 2, z0)
    elif style in ('helm', 'horned_helm', 'mining', 'great_helm', 'skullcap'):
        g = 'metal' if style != 'skullcap' else 'cloth'
        bottom = z1 - 2 if style == 'skullcap' else z0 + 3
        shell(bottom, z0 + 5 if style != 'great_helm' else z0, g, open_face=style != 'great_helm')
        if style == 'great_helm':
            for x in range(x0, x1 + 1):
                for z in range(z0, z1 + 1):
                    put(x, y0 - 1, z, color, 'metal')
            for x in list(range(x0 + 1, 16)) + list(range(17, x1)):
                put(x, y0 - 1, z0 + 3, BLACK, 'detail')
            for z in range(z0, z0 + 3):
                put(16, y0 - 1, z, trim, 'metal')
        else:
            for x in range(x0 - 1, x1 + 2):
                put(x, y0 - 1, z0 + 5 if style != 'skullcap' else z1 - 1, trim, g)
            put(16, y0 - 1, z0 + 4, trim, g) if style == 'helm' else None
        if style == 'horned_helm':
            horns(m, hd, 'bull', extra or (235, 225, 200), z=z0 + 6)
        if style == 'mining':
            put(16, y0 - 2, z0 + 6, (255, 240, 170), 'light', ('emit', 0.9, 1))
            put(15, y0 - 2, z0 + 6, trim, 'metal'); put(17, y0 - 2, z0 + 6, trim, 'metal')
            put(16, y0 - 2, z0 + 7, trim, 'metal'); put(16, y0 - 2, z0 + 5, trim, 'metal')
    elif style == 'cap':
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                put(x, y, z1 + 1)
        for x in range(x0 + 1, x1):
            for y in (y0 - 1, y0 - 2):
                put(x, y, z1, trim)
    elif style == 'beanie':
        shell(z1 - 1, z1 - 1, 'cloth')
        for x in range(x0 - 1, x1 + 2):
            put(x, y0 - 1, z1 - 1, trim)
        put(16, (y0 + y1) // 2, z1 + 2, trim)
    elif style == 'bandana':
        for x in range(x0 - 1, x1 + 2):
            put(x, y0 - 1, z1 - 1); put(x, y0 - 1, z1 - 2)
        for y in range(y0, y1 + 2):
            put(x0 - 1, y, z1 - 1); put(x1 + 1, y, z1 - 1); put(x0 - 1, y, z1 - 2); put(x1 + 1, y, z1 - 2)
        for x in range(x0, x1 + 1):
            put(x, y1 + 1, z1 - 1); put(x, y1 + 1, z1 - 2)
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                put(x, y, z1 + 1)
        put(15, y1 + 2, z1 - 2, trim); put(17, y1 + 2, z1 - 2, trim); put(15, y1 + 3, z1 - 3, trim); put(17, y1 + 3, z1 - 4, trim)
    elif style in ('wide', 'cowboy', 'straw'):
        brim = 2 if style != 'cowboy' else 2
        for x in range(x0 - brim, x1 + brim + 1):
            for y in range(y0 - brim, y1 + brim + 1):
                if (x in (x0 - brim, x1 + brim)) and (y in (y0 - brim, y1 + brim)):
                    continue
                zb = z1 + 1
                if style == 'cowboy' and x in (x0 - brim, x1 + brim):
                    zb = z1 + 2
                put(x, y, zb, color if style != 'straw' or (x + y) % 3 else shade(color, 0.85))
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z1 + 2, z1 + 4 + (1 if style == 'cowboy' else 0)):
                    if style == 'cowboy' and z == z1 + 4 and x == 16:
                        continue
                    if x in (x0, x1) and y in (y0, y1):
                        continue
                    put(x, y, z, trim if z == z1 + 2 else color)
    elif style == 'tricorne':
        for x in range(x0 - 2, x1 + 3):
            for y in range(y0 - 2, y1 + 2):
                d = max(abs(x - 16) - 2, 0) + max(y0 - y, 0) + max(y - y1, 0)
                if d <= 3:
                    put(x, y, z1 + 1, color)
        for x in range(x0 - 2, x1 + 3):
            put(x, y0 - 2, z1 + 2, trim) if abs(x - 16) < 5 else None
        for y in range(y0, y1 + 2):
            put(x0 - 2, y, z1 + 2, trim); put(x1 + 2, y, z1 + 2, trim)
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                if not (x in (x0, x1) and y in (y0, y1)):
                    put(x, y, z1 + 2, color)
        for x in range(x0 + 1, x1):
            for y in range(y0 + 1, y1):
                put(x, y, z1 + 3, color)
    elif style == 'wizard':
        for x in range(x0 - 2, x1 + 3):
            for y in range(y0 - 2, y1 + 3):
                if ((x - 16) / 6.5) ** 2 + ((y - (y0 + y1) / 2) / 6.0) ** 2 <= 1:
                    put(x, y, z1 + 1, trim)
        cy = (y0 + y1) / 2
        for k in range(8):
            r = 4.2 - k * 0.55
            for x in range(x0, x1 + 1):
                for y in range(y0, y1 + 2):
                    if ((x - 16) ** 2 + (y - cy - k * 0.35) ** 2) <= r * r:
                        put(x, y, z1 + 2 + k, color)
        put(16, int(cy + 3), z1 + 10, extra or (240, 210, 80), 'metal')
    elif style == 'top':
        for x in range(x0 - 1, x1 + 2):
            for y in range(y0 - 1, y1 + 2):
                if not (x in (x0 - 1, x1 + 1) and y in (y0 - 1, y1 + 1)):
                    put(x, y, z1 + 1)
        for x in range(x0 + 1, x1):
            for y in range(y0 + 1, y1):
                for z in range(z1 + 2, z1 + 7):
                    put(x, y, z, trim if z == z1 + 2 else color)
    elif style in ('crown', 'circlet'):
        gold = color
        for x in range(x0, x1 + 1):
            for y in (y0, y1):
                put(x, y if y == y1 else y - 0, z1 if style == 'crown' else z1 - 2, gold, 'metal') if style == 'circlet' else None
        if style == 'crown':
            for x in range(x0, x1 + 1):
                for y in range(y0, y1 + 1):
                    if x in (x0, x1) or y in (y0, y1):
                        put(x, y, z1 + 1, gold, 'metal')
                        if (x - x0) % 2 == 0 and (y in (y0, y1)) or (y - y0) % 2 == 0 and x in (x0, x1):
                            put(x, y, z1 + 2, gold, 'metal')
            put(16, y0, z1 + 1, extra or (200, 40, 60), 'gem')
        else:
            for x in range(x0 - 1, x1 + 2):
                put(x, y0 - 1, z1 - 1, gold, 'metal')
            for y in range(y0, y1 + 2):
                put(x0 - 1, y, z1 - 1, gold, 'metal'); put(x1 + 1, y, z1 - 1, gold, 'metal')
            for x in range(x0, x1 + 1):
                put(x, y1 + 1, z1 - 1, gold, 'metal')
            put(16, y0 - 1, z1 - 1, extra or (80, 170, 230), 'gem')
    elif style == 'headband':
        for x in range(x0 - 1, x1 + 2):
            put(x, y0 - 1, z0 + 5)
        for y in range(y0, y1 + 2):
            put(x0 - 1, y, z0 + 5); put(x1 + 1, y, z0 + 5)
        for x in range(x0, x1 + 1):
            put(x, y1 + 1, z0 + 5)
        put(16, y1 + 2, z0 + 5, trim); put(16, y1 + 3, z0 + 4, trim); put(17, y1 + 3, z0 + 3, trim)
    elif style == 'goggles':
        for x in range(x0 - 1, x1 + 2):
            put(x, y0 - 1, z0 + 5, trim, 'leather')
        for y in range(y0, y1 + 2):
            put(x0 - 1, y, z0 + 5, trim, 'leather'); put(x1 + 1, y, z0 + 5, trim, 'leather')
        for x in range(x0, x1 + 1):
            put(x, y1 + 1, z0 + 5, trim, 'leather')
        for xs in ((13, 14), (18, 19)):
            for x in xs:
                put(x, y0 - 2, z0 + 5, extra or (150, 210, 230), 'glass', ('glass', 0.55))
            put(xs[0] - 1, y0 - 2, z0 + 5, color, 'metal'); put(xs[1] + 1, y0 - 2, z0 + 5, color, 'metal')
    elif style == 'turban':
        for x in range(x0 - 1, x1 + 2):
            for y in range(y0 - 1, y1 + 2):
                for z in range(z1 - 2, z1 + 3):
                    inside = x0 <= x <= x1 and y0 <= y <= y1 and z <= z1
                    if inside or (x in (x0 - 1, x1 + 1) and y in (y0 - 1, y1 + 1)):
                        continue
                    if z == z1 + 2 and (x in (x0 - 1, x1 + 1) or y in (y0 - 1, y1 + 1)):
                        continue
                    put(x, y, z, trim if (z + x) % 3 == 0 else color)
        put(16, y0 - 2, z1, extra or (60, 160, 90), 'gem')
    elif style == 'beret':
        for x in range(x0 - 1, x1 + 2):
            for y in range(y0, y1 + 2):
                if ((x - 15.5) / 6) ** 2 + ((y - (y0 + y1) / 2 - 0.5) / 5.5) ** 2 <= 1:
                    put(x, y, z1 + 1)
        for x in range(x0 + 1, x1):
            for y in range(y0 + 1, y1):
                put(x, y, z1 + 2)
        put(16, (y0 + y1) // 2, z1 + 3, trim)
    elif style == 'fez':
        for x in range(14, 19):
            for y in range(y0 + 2, y0 + 7):
                for z in range(z1 + 1, z1 + 4):
                    put(x, y, z)
        put(18, y0 + 6, z1 + 3, trim); put(19, y0 + 6, z1 + 2, trim); put(19, y0 + 6, z1 + 1, trim)
    elif style == 'laurel':
        for x in range(x0 - 1, x1 + 2):
            if abs(x - 16) > 1:
                put(x, y0 - 1 if abs(x - 16) < 4 else y0, z1 - 1, color, 'plant')
        for y in range(y0, y1 + 1):
            put(x0 - 1, y, z1 - 1, color, 'plant'); put(x1 + 1, y, z1 - 1, color, 'plant')
