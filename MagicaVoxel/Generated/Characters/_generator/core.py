"""The model every design is drawn on, the base body it starts from, colours, and the rig
layout each model needs to be baked with the game's skeleton.

Coordinates are MagicaVoxel's: x across (the figure's left is +x, its middle column x 16,
mirror x -> 32 - x), y front to back (the face looks toward -y), z up (feet on z 0). The
base body is Character_Bigger.vox voxel for voxel: legs x 14-15 and 17-18, y 15-17, z 1-8,
feet z 0 (y 13-17); hips z 9-11, spine 12-14, chest 15-18, all x 14-18, y 15-17; arms along
z 17-18 (x 6-13 and 19-26; hands x 4-5 and 27-28 at z 18); the neck x 16, y 15-16, z 19;
the head x 12-20, y 12-19, z 20-27, its front face at y 12.
"""
import colorsys
import hashlib
import json
import os

import vox

SIZE = (32, 32, 32)
WORK = (32, 32, 48)       # the canvas a model is drawn on; written as tall as it needs
MID = 16                  # the figure's middle column
FACE_Y = 12               # the base head's front face

# --- Colours -------------------------------------------------------------------------------

def rgb(hexstr):
    hexstr = hexstr.lstrip('#')
    return tuple(int(hexstr[i:i + 2], 16) for i in (0, 2, 4))


def shade(c, f):
    """Darker (f < 1) or lighter (f > 1) by scaling value, keeping hue."""
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
    if f < 1:
        l = l * f
    else:
        l = l + (1 - l) * (f - 1)
    r, g, b = colorsys.hls_to_rgb(h, max(0, min(1, l)), s)
    return (round(r * 255), round(g * 255), round(b * 255))


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def sat(c, f):
    h, l, s = colorsys.rgb_to_hls(*(v / 255 for v in c))
    r, g, b = colorsys.hls_to_rgb(h, l, max(0, min(1, s * f)))
    return (round(r * 255), round(g * 255), round(b * 255))


# --- Bones ---------------------------------------------------------------------------------

BONES = ['Root', 'Hips', 'Spine', 'Chest', 'Neck', 'Head',
         'LeftUpperArm', 'LeftLowerArm', 'LeftHand', 'RightUpperArm', 'RightLowerArm', 'RightHand',
         'LeftUpperLeg', 'LeftLowerLeg', 'LeftFoot', 'RightUpperLeg', 'RightLowerLeg', 'RightFoot']

# CHARACTER_BIGGER's regions, in order: [bone, low corner, high corner], inclusive.
BASE_REGIONS = [
    ('Head', (0, 0, 20), (255, 255, 255)),
    ('Neck', (0, 0, 19), (255, 255, 19)),
    ('RightHand', (0, 0, 17), (5, 255, 18)),
    ('RightLowerArm', (6, 0, 17), (8, 255, 18)),
    ('RightUpperArm', (9, 0, 17), (13, 255, 18)),
    ('LeftHand', (27, 0, 17), (255, 255, 18)),
    ('LeftLowerArm', (24, 0, 17), (26, 255, 18)),
    ('LeftUpperArm', (19, 0, 17), (23, 255, 18)),
    ('Chest', (0, 0, 15), (255, 255, 18)),
    ('Spine', (0, 0, 12), (255, 255, 14)),
    ('Hips', (0, 0, 9), (255, 255, 11)),
    ('RightUpperLeg', (0, 0, 5), (16, 255, 8)),
    ('LeftUpperLeg', (17, 0, 5), (255, 255, 8)),
    ('RightLowerLeg', (0, 0, 1), (16, 255, 4)),
    ('LeftLowerLeg', (17, 0, 1), (255, 255, 4)),
    ('RightFoot', (0, 0, 0), (16, 255, 0)),
    ('LeftFoot', (17, 0, 0), (255, 255, 0)),
]

# CHARACTER_BIGGER's joints, in rig voxels (Godot axes: x the figure's left, y up, z forward).
BASE_JOINTS = {
    'Root': (0, 0, 0), 'Hips': (0, 9, -0.5), 'Spine': (0, 12, -0.5), 'Chest': (0, 15, -0.5),
    'Neck': (0, 19, -0.5), 'Head': (0, 20, -0.5),
    'LeftUpperArm': (3.5, 18, -0.5), 'LeftLowerArm': (7.5, 18, -0.5), 'LeftHand': (10.5, 18, -0.5),
    'RightUpperArm': (-3.5, 18, -0.5), 'RightLowerArm': (-7.5, 18, -0.5), 'RightHand': (-10.5, 18, -0.5),
    'LeftUpperLeg': (1.5, 9, -0.5), 'LeftLowerLeg': (1.5, 5, -0.5), 'LeftFoot': (1.5, 1, -0.5),
    'RightUpperLeg': (-1.5, 9, -0.5), 'RightLowerLeg': (-1.5, 5, -0.5), 'RightFoot': (-1.5, 1, -0.5),
}

# The middle of the base figure's voxels, which VoxelRig centres the rig on: x 4..28, y 12..19.
BASE_CENTER = (16.5, 16.0)


def region_bone(p, regions=BASE_REGIONS):
    x, y, z = p
    for bone, lo, hi in regions:
        if lo[0] <= x <= hi[0] and lo[1] <= y <= hi[1] and lo[2] <= z <= hi[2]:
            return bone
    return None


def part_of(p):
    """The base body part a position falls in, by the base layout's bands."""
    x, y, z = p
    if z >= 20:
        return 'head'
    if z == 19:
        return 'neck'
    if z >= 17:
        if x <= 5: return 'hand_r'
        if x <= 8: return 'larm_r'
        if x <= 13: return 'uarm_r'
        if x >= 27: return 'hand_l'
        if x >= 24: return 'larm_l'
        if x >= 19: return 'uarm_l'
        return 'chest'
    if z >= 15: return 'chest'
    if z >= 12: return 'spine'
    if z >= 9: return 'hips'
    side = 'r' if x <= 16 else 'l'
    if z >= 5: return 'uleg_' + side
    if z >= 1: return 'lleg_' + side
    return 'foot_' + side


PART_BONE = {
    'head': 'Head', 'neck': 'Neck', 'chest': 'Chest', 'spine': 'Spine', 'hips': 'Hips',
    'uarm_r': 'RightUpperArm', 'larm_r': 'RightLowerArm', 'hand_r': 'RightHand',
    'uarm_l': 'LeftUpperArm', 'larm_l': 'LeftLowerArm', 'hand_l': 'LeftHand',
    'uleg_r': 'RightUpperLeg', 'lleg_r': 'RightLowerLeg', 'foot_r': 'RightFoot',
    'uleg_l': 'LeftUpperLeg', 'lleg_l': 'LeftLowerLeg', 'foot_l': 'LeftFoot',
}

ARM_PARTS = ('uarm_r', 'larm_r', 'hand_r', 'uarm_l', 'larm_l', 'hand_l')
LEG_PARTS = ('uleg_r', 'lleg_r', 'foot_r', 'uleg_l', 'lleg_l', 'foot_l')
TORSO_PARTS = ('chest', 'spine', 'hips')


def arm_bone(x, z=18):
    """The arm bone a voxel at [x] along the arm rows rides on."""
    return PART_BONE[part_of((x, 16, 18))] if x <= 13 or x >= 19 else 'Chest'


def leg_bone(x, z):
    return PART_BONE[part_of((x, 16, max(0, min(8, z))))]


# --- The model -----------------------------------------------------------------------------

class Vox:
    __slots__ = ('color', 'group', 'bone', 'part', 'mat')

    def __init__(self, color, group, bone=None, part=None, mat=None):
        self.color = tuple(color)
        self.group = group
        self.bone = bone
        self.part = part
        self.mat = mat

    def copy(self):
        return Vox(self.color, self.group, self.bone, self.part, self.mat)


class Model:
    """Voxels {(x, y, z): Vox}. Every voxel has a colour, a semantic group (skin, fur, hair,
    cloth, leather, metal, eye, ...), the base part it belongs to (for painting) and the bone
    it moves with: explicit for add-ons, else the base layout's band."""

    def __init__(self, size=WORK):
        self.v = {}
        self.size = size
        self.notes = []
        self.clipped = 0

    # basic access
    def set(self, p, color, group, bone=None, part=None, mat=None):
        if None in p:
            raise ValueError('no position: %s' % (p,))
        if self.size is not None and not all(0 <= p[i] < self.size[i] for i in range(3)):
            self.clipped += 1
            return
        self.v[tuple(p)] = Vox(color, group, bone, part, mat)

    def has(self, p):
        return tuple(p) in self.v

    def get(self, p):
        return self.v.get(tuple(p))

    def remove(self, p):
        self.v.pop(tuple(p), None)

    def box(self, x0, x1, y0, y1, z0, z1, color, group, bone=None, part=None, mat=None, only_empty=False, sym=False):
        for x in range(min(x0, x1), max(x0, x1) + 1):
            for y in range(min(y0, y1), max(y0, y1) + 1):
                for z in range(min(z0, z1), max(z0, z1) + 1):
                    if only_empty and self.has((x, y, z)):
                        continue
                    self.set((x, y, z), color, group, bone, part, mat)
        if sym:
            self.box(32 - x0, 32 - x1, y0, y1, z0, z1, color, group, mirror_bone(bone), part and mirror_part(part), mat, only_empty)

    def dot(self, x, y, z, color, group, bone=None, part=None, mat=None, sym=False, only_empty=False):
        if not (only_empty and self.has((x, y, z))):
            self.set((x, y, z), color, group, bone, part, mat)
        if sym and x != 32 - x:
            if not (only_empty and self.has((32 - x, y, z))):
                self.set((32 - x, y, z), color, group, mirror_bone(bone), part and mirror_part(part), mat)

    def clear_box(self, x0, x1, y0, y1, z0, z1):
        for p in list(self.v):
            if x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and z0 <= p[2] <= z1:
                del self.v[p]

    def paint(self, color, group=None, where=None, parts=None, box=None, mat=None, keep_mat=False):
        """Recolours existing voxels: those of [parts], in [box] (x0, x1, y0, y1, z0, z1),
        and passing [where](p, vox)."""
        for p, vx in self.v.items():
            if parts is not None and vx.part not in parts:
                continue
            if box is not None:
                x0, x1, y0, y1, z0, z1 = box
                if not (x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and z0 <= p[2] <= z1):
                    continue
            if where is not None and not where(p, vx):
                continue
            vx.color = tuple(color)
            if group:
                vx.group = group
            if not keep_mat:
                vx.mat = mat

    def ellipsoid(self, cx, cy, cz, rx, ry, rz, color, group, bone=None, part=None, mat=None, only_empty=False, where=None,
                  clear_arms=True):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
                for z in range(int(cz - rz) - 1, int(cz + rz) + 2):
                    d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2
                    if d <= 1.0:
                        if only_empty and self.has((x, y, z)):
                            continue
                        if clear_arms and bone in ('Chest', 'Spine', 'Hips') and x in (12, 13, 19, 20) and 14 <= y <= 18 and 9 <= z <= 16:
                            continue  # a lowered arm hangs there
                        if where is not None and not where((x, y, z)):
                            continue
                        self.set((x, y, z), color, group, bone, part, mat)

    def surface(self, p, direction):
        """Whether the voxel at [p] shows a face toward [direction]."""
        return self.has(p) and not self.has((p[0] + direction[0], p[1] + direction[1], p[2] + direction[2]))

    def front_y(self, x, z):
        """The frontmost voxel's y in column (x, z), or None."""
        ys = [p[1] for p in self.v if p[0] == x and p[2] == z]
        return min(ys) if ys else None

    def back_y(self, x, z):
        ys = [p[1] for p in self.v if p[0] == x and p[2] == z]
        return max(ys) if ys else None

    def top_z(self, x, y):
        zs = [p[2] for p in self.v if p[0] == x and p[1] == y]
        return max(zs) if zs else None

    def bounds(self):
        xs = [p[0] for p in self.v]; ys = [p[1] for p in self.v]; zs = [p[2] for p in self.v]
        return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))

    def bone_of(self, p):
        vx = self.v[p]
        if vx.bone:
            return vx.bone
        if vx.part in PART_BONE:
            return PART_BONE[vx.part]
        return region_bone(p)

    def copy(self):
        m = Model(self.size)
        m.v = {p: vx.copy() for p, vx in self.v.items()}
        m.notes = list(self.notes)
        for k in ('skin', 'skin_group', 'head'):
            if hasattr(self, k):
                setattr(m, k, getattr(self, k))
        return m

    def mirror_from_left(self):
        """Makes the model bilaterally symmetric by copying its left half (x > 16) onto its
        right, colours, groups and mirrored bones included."""
        keep = {p: vx for p, vx in self.v.items() if p[0] >= MID}
        out = dict(keep)
        for p, vx in keep.items():
            if p[0] > MID:
                q = (32 - p[0], p[1], p[2])
                c = vx.copy()
                c.bone = mirror_bone(vx.bone)
                c.part = mirror_part(vx.part) if vx.part else None
                out[q] = c
        self.v = out


def mirror_bone(bone):
    if not bone:
        return bone
    if bone.startswith('Left'):
        return 'Right' + bone[4:]
    if bone.startswith('Right'):
        return 'Left' + bone[5:]
    return bone


def mirror_part(part):
    if part.endswith('_r'):
        return part[:-2] + '_l'
    if part.endswith('_l'):
        return part[:-2] + '_r'
    return part


def base_body(skin=(200, 170, 140), group='skin'):
    """Character_Bigger.vox's voxels, each tagged with its base part, in [skin]."""
    size, voxels, palette, _ = vox.read(vox.TEMPLATE)
    m = Model(WORK)
    for p in voxels:
        m.set(p, skin, group, None, part_of(p))
    m.skin = tuple(skin)
    m.skin_group = group
    m.head = None
    return m


# --- Rig layout ----------------------------------------------------------------------------

def merge_boxes(cells):
    """Covers a set of cells with few axis-aligned boxes (greedy, exact)."""
    left = set(cells)
    boxes = []
    for c in sorted(cells, key=lambda p: (p[2], p[1], p[0])):
        if c not in left:
            continue
        x0, y0, z0 = c
        x1 = x0
        while (x1 + 1, y0, z0) in left:
            x1 += 1
        y1 = y0
        while all((x, y1 + 1, z0) in left for x in range(x0, x1 + 1)):
            y1 += 1
        z1 = z0
        while all((x, y, z1 + 1) in left for x in range(x0, x1 + 1) for y in range(y0, y1 + 1)):
            z1 += 1
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    left.discard((x, y, z))
        boxes.append(((x0, y0, z0), (x1, y1, z1)))
    return boxes


def rig_layout(m):
    """The layout the game's VoxelRig needs to rig [m] with Character_Bigger's skeleton:
    its regions, every voxel whose base-band bone is not the one it was drawn for covered by a
    box of its own, put first; the base joints; and the centre to rig it about (the base
    body's middle, which a model with a tail or a snout no longer has as its bounds' middle).
    Returns (layout dict, problems)."""
    wrong = {}
    for p in m.v:
        want = m.bone_of(p)
        if region_bone(p) != want:
            wrong.setdefault(want, set()).add(p)
    extra = []
    for bone in BONES:
        if bone in wrong:
            for lo, hi in merge_boxes(wrong[bone]):
                extra.append((bone, lo, hi))
    # Overriding boxes can capture voxels meant for other bones: check and split until exact.
    regions = extra + BASE_REGIONS
    problems = []
    for _ in range(4):
        bad = [p for p in m.v if region_bone(p, regions) != m.bone_of(p)]
        if not bad:
            break
        cells = {}
        for p in bad:
            cells.setdefault(m.bone_of(p), set()).add(p)
        fix = []
        for bone, ps in cells.items():
            fix += [(bone, p, p) for p in sorted(ps)]
        regions = fix + regions
    bad = [p for p in m.v if region_bone(p, regions) != m.bone_of(p)]
    if bad:
        problems.append('%d voxels still on the wrong bone' % len(bad))
    (x0, x1), (y0, y1), (z0, z1) = m.bounds()
    centre = ((x0 + x1 + 1) / 2, (y0 + y1 + 1) / 2)
    layout = {
        'scale': 0.063,
        'center': list(BASE_CENTER),
        'bounds_center': [centre[0], centre[1]],
        'needs_center': centre != BASE_CENTER or z0 != 0,
        'joints': BASE_JOINTS,
        'extra_regions': [[b, list(lo), list(hi)] for b, lo, hi in regions[:len(regions) - len(BASE_REGIONS)]],
    }
    if z0 != 0:
        problems.append('lowest voxel at z %d, not 0' % z0)
    return layout, problems


# --- Palette and writing -------------------------------------------------------------------

GROUP_ORDER = ['skin', 'fur', 'scale', 'feather', 'chitin', 'bark', 'plant', 'petal', 'shell', 'horn', 'hair',
               'eye', 'mouth', 'cloth', 'leather', 'metal', 'gem', 'bone', 'detail', 'glass', 'light']


def palette_of(m):
    """Distinct (colour, material) pairs, ordered by group, then hue."""
    seen = {}
    for vx in m.v.values():
        key = (vx.color, vx.mat)
        if key not in seen:
            seen[key] = vx.group
    def order(item):
        (color, mat), group = item
        g = GROUP_ORDER.index(group) if group in GROUP_ORDER else len(GROUP_ORDER)
        h, l, s = colorsys.rgb_to_hls(*(c / 255 for c in color))
        return (g, round(h, 2), l)
    entries = sorted(seen.items(), key=order)
    if len(entries) > 254:
        raise ValueError('too many colours: %d' % len(entries))
    return [key for key, _ in entries]


def canvas(m):
    """The canvas [m] is written on: its working width and depth, as tall as its voxels need
    (32, 40 or 48), or its own size for a model drawn on a canvas of its own (a concept)."""
    if m.size is None:
        (x0, x1), (y0, y1), (z0, z1) = m.bounds()
        return (x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1)
    if m.size != WORK:
        return m.size
    top = max(p[2] for p in m.v)
    return (WORK[0], WORK[1], 32 if top < 32 else (40 if top < 40 else 48))


def write_model(m, path, palette_override=None):
    """Writes [m] as a .vox; returns the bytes. [palette_override] (a full 256-entry RGBA list)
    keeps a given palette, every colour of [m] having to be in it (CratePalette)."""
    mats = {}
    if palette_override is not None:
        rgba = palette_override
        index = {}
        for i, e in enumerate(rgba[:254]):
            index.setdefault(tuple(e[:3]), i + 1)
        voxels = {}
        for p, vx in m.v.items():
            voxels[p] = index[vx.color]
        return vox.write(path, canvas(m), voxels, rgba, mats)
    if m.size is None:
        # a model drawn on no canvas (a concept) is moved onto one just big enough
        (x0, x1), (y0, y1), (z0, z1) = m.bounds()
        moved = Model(None)
        moved.v = {(p[0] - x0, p[1] - y0, p[2] - z0): v for p, v in m.v.items()}
        moved.size = canvas(m)
        m = moved
    keys = palette_of(m)
    place = {k: i + 1 for i, k in enumerate(keys)}
    rgba = [(c[0], c[1], c[2], 255) for c, mat in keys]
    for (c, mat), i in place.items():
        if mat and mat[0] == 'glass':
            mats[i] = vox.glass_material(mat[1])
        elif mat and mat[0] == 'emit':
            mats[i] = vox.emit_material(mat[1], mat[2] if len(mat) > 2 else 1)
    voxels = {p: place[(vx.color, vx.mat)] for p, vx in m.v.items()}
    return vox.write(path, canvas(m), voxels, rgba, mats)


def sha256(data):
    return hashlib.sha256(data).hexdigest()
