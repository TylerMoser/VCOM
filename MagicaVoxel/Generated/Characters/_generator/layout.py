"""Prints the GDScript layout a model needs in the game's VoxelRig.LAYOUTS to be baked with
Character_Bigger's skeleton and animations (README.md, "Baking one"):

    python layout.py ../Catfolk/Catfolk_04_Lion.vox [res://Characters/Catfolk_04_Lion.vox] [--shift]

The model's own regions come from its folder's layouts.json (written by build.py), put ahead
of Character_Bigger's; its joints are Character_Bigger's; "center" is the base body's middle,
which needs VoxelRig's "center" option (README.md) whenever the model's box is not the base
body's box, as a hat brim, a tail, a snout or wings make it. With --shift the layout has no
"center" and moves the joints instead, which works with VoxelRig as it is, but stands the body
off its tile's middle by as much."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import core
import vox


def gd_layout(regions, center, name='LAYOUT', shift=None):
    """The layout as GDScript. With [shift] (the model's box's middle, x and y) there is no
    "center": the joints move by as much as the box's middle is off the body's."""
    lines = ['const %s := {' % name, '\t"scale": 0.063,']
    dx = dz = 0.0
    if shift is None:
        lines.append("\t## The base body's middle (x, y in the model's voxels): VoxelRig centres the rig on it.")
        lines.append('\t"center": Vector2(%s, %s),' % (center[0], center[1]))
    else:
        dx, dz = center[0] - shift[0], shift[1] - center[1]
        lines.append("\t## Character_Bigger's joints moved (%+g, 0, %+g): the model's box is off its body's middle." % (dx, dz))
    lines.append('\t"joints": {')
    for bone in core.BONES:
        x, y, z = core.BASE_JOINTS[bone]
        lines.append('\t\t&"%s": Vector3(%s, %s, %s),' % (bone, x + dx, y, z + dz))
    lines.append('\t},')
    lines.append('\t"regions": [')
    for bone, lo, hi in regions:
        lines.append('\t\t[&"%s", Vector3i(%d, %d, %d), Vector3i(%d, %d, %d)],' % (bone, *lo, *hi))
    for bone, lo, hi in core.BASE_REGIONS:
        lines.append('\t\t[&"%s", Vector3i(%d, %d, %d), Vector3i(%d, %d, %d)],' % (bone, *lo, *hi))
    lines.append('\t],')
    lines.append('}')
    return '\n'.join(lines)


def layout_of(vox_path):
    folder = os.path.dirname(os.path.abspath(vox_path))
    data = json.load(open(os.path.join(folder, 'layouts.json'), encoding='utf-8'))
    return data[os.path.basename(vox_path)]


def box_middle(vox_path):
    size, voxels, palette, mats = vox.read(vox_path)
    xs = [p[0] for p in voxels]
    ys = [p[1] for p in voxels]
    return ((min(xs) + max(xs) + 1) / 2, (min(ys) + max(ys) + 1) / 2)


def main(args):
    shift = '--shift' in args
    args = [a for a in args if a != '--shift']
    if not args:
        print(__doc__)
        return 1
    path = args[0]
    entry = layout_of(path)
    stem = os.path.splitext(os.path.basename(path))[0]
    const = ''.join(c for c in stem.upper() if c.isalnum() or c == '_')
    print(gd_layout(entry['regions'], entry['center'], const, box_middle(path) if shift else None))
    res = args[1] if len(args) > 1 else 'res://Characters/%s.vox' % stem
    print()
    print('# in LAYOUTS:')
    print('\t"%s": %s,' % (res, const))
    if entry['needs_center'] and not shift:
        print('# This model needs VoxelRig\'s "center" option, or --shift (README.md, "Baking one").')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
