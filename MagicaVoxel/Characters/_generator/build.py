"""Builds the species' character models: every set in species/, or those whose folder starts
with one of the arguments.

    python build.py                 # everything
    python build.py Catfolk Rodent/Rat

Each set's folder (under MagicaVoxel/Characters/) gets its rig-ready models, their treatment
variants, Preview.png, layouts.json (each model's rig layout: README.md, "Baking one"), and
Concepts/ with its free-proportion models and their own Preview.png. manifest.json at the
top lists every model; a partial build updates only its own sets' entries."""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import core
import render as R
import treat
import vox
from species import ALL_SETS

ROOT = os.path.normpath(os.path.join(HERE, '..'))
MANIFEST = os.path.join(ROOT, 'manifest.json')

_base = None


def base_positions():
    global _base
    if _base is None:
        size, voxels, palette, _ = vox.read(vox.TEMPLATE)
        _base = set(voxels)
    return _base


ARM_BONES = {'RightUpperArm', 'RightLowerArm', 'RightHand', 'LeftUpperArm', 'LeftLowerArm', 'LeftHand'}


def check_rig(m):
    """What would keep [m] from moving well on the base skeleton (README.md, "The rig")."""
    problems = []
    for p in base_positions():
        if p[2] >= 19:
            continue
        if p not in m.v:
            problems.append('base voxel %s missing' % (p,))
        elif m.bone_of(p) != core.region_bone(p):
            problems.append('base voxel %s on %s, not %s' % (p, m.bone_of(p), core.region_bone(p)))
    for p, v in m.v.items():
        bone = m.bone_of(p)
        x, y, z = p
        if bone not in ARM_BONES and x in (12, 13, 19, 20) and 14 <= y <= 18 and 9 <= z <= 16:
            problems.append('%s on %s in a lowered arm\'s room' % (p, bone))
        if bone in ARM_BONES and 15 <= y <= 17 and z <= 16:
            problems.append('%s on %s under the arm: it folds into the body' % (p, bone))
        if bone == 'Chest' and z >= 20 and y <= 19 and 11 <= x <= 21:
            problems.append('%s on the chest inside the head\'s room' % (p,))
    if min(p[2] for p in m.v) != 0:
        problems.append('nothing on z 0')
    if m.clipped:
        problems.append('%d voxels fell off the canvas' % m.clipped)
    return problems


def summarise(problems, limit=6):
    if len(problems) <= limit:
        return problems
    return problems[:limit] + ['... %d more' % (len(problems) - limit)]


def entry(m, path, data, kind, role, treatment=None, source=None, layout=None):
    (x0, x1), (y0, y1), (z0, z1) = m.bounds()
    colors = {(v.color, v.mat) for v in m.v.values()}
    e = {
        'file': os.path.relpath(path, ROOT).replace('\\', '/'),
        'set': kind,
        'role': role,
        'canvas': list(core.canvas(m)),
        'bounds': [[x0, y0, z0], [x1, y1, z1]],
        'voxels': len(m.v),
        'colors': len(colors),
        'glass': sum(1 for v in m.v.values() if v.mat and v.mat[0] == 'glass'),
        'glow': sum(1 for v in m.v.values() if v.mat and v.mat[0] == 'emit'),
        'sha256': core.sha256(data),
    }
    if treatment:
        e['treatment'] = treatment
        e['source'] = source
    if layout is not None:
        e['needs_center'] = layout['needs_center']
        e['extra_regions'] = len(layout['extra_regions'])
    return e


def build_set(s, log):
    folder = os.path.join(ROOT, *s.path.split('/'))
    os.makedirs(folder, exist_ok=True)
    entries, layouts, tiles = [], {}, []
    made = {}
    for i, (desc, fn) in enumerate(s.designs, 1):
        name = '%s_%02d_%s' % (s.kind, i, desc)
        m = fn()
        problems = check_rig(m)
        layout, lp = core.rig_layout(m)
        problems += lp
        path = os.path.join(folder, name + '.vox')
        data = core.write_model(m, path)
        layouts[name + '.vox'] = {'center': layout['center'], 'needs_center': layout['needs_center'],
                                  'regions': layout['extra_regions']}
        e = entry(m, path, data, s.path, 'rig-ready', layout=layout)
        if problems:
            e['problems'] = summarise(problems)
            log.append('%s: %s' % (name, '; '.join(summarise(problems, 3))))
        entries.append(e)
        made[i] = (name, m)
        tiles.append(('%02d %s' % (i, desc), R.turnaround(m, 7)))
    for index, how in s.treatments:
        name, m = made[index]
        tname = name + '_' + how
        path = os.path.join(folder, tname + '.vox')
        if how == 'CratePalette':
            c, pal, places, mats = treat.crate(m)
            data = vox.write(path, core.canvas(c), places, pal, mats)
        else:
            c = treat.TREATMENTS[how](m)
            data = core.write_model(c, path)
        layout, lp = core.rig_layout(c)
        layouts[tname + '.vox'] = {'center': layout['center'], 'needs_center': layout['needs_center'],
                                   'regions': layout['extra_regions']}
        problems = check_rig(c) + lp
        e = entry(c, path, data, s.path, 'rig-ready', how, name + '.vox', layout)
        if problems:
            e['problems'] = summarise(problems)
            log.append('%s: %s' % (tname, '; '.join(summarise(problems, 3))))
        entries.append(e)
        tiles.append(('%02d %s' % (index, how), R.turnaround(c, 7)))
    with open(os.path.join(folder, 'layouts.json'), 'w', encoding='utf-8', newline='\n') as f:
        json.dump(layouts, f, separators=(',', ':'))
    title = '%s: %d rig-ready designs, %d treatment variants' % (s.title, len(s.designs), len(s.treatments))
    R.sheet(tiles, 4, cell=(420, 330), title=title).save(os.path.join(folder, 'Preview.png'))
    if s.concepts:
        cfolder = os.path.join(folder, 'Concepts')
        os.makedirs(cfolder, exist_ok=True)
        ctiles = []
        for i, (desc, fn) in enumerate(s.concepts, 1):
            name = '%s_Concept_%02d_%s' % (s.kind, i, desc)
            m = fn()
            path = os.path.join(cfolder, name + '.vox')
            data = core.write_model(m, path)
            entries.append(entry(m, path, data, s.path, 'concept'))
            ctiles.append(('C%02d %s' % (i, desc), R.turnaround(m, 6)))
        R.sheet(ctiles, 3, cell=(520, 420), title='%s concepts (free proportions, not rig-ready)' % s.title).save(os.path.join(cfolder, 'Preview.png'))
    return entries, made


README = os.path.join(ROOT, 'README.md')
INDEX_START, INDEX_END = '<!-- index: written by _generator/build.py -->', '<!-- /index -->'


def write_index(models):
    """Rewrites README.md's index of sets, between its markers, after a full build."""
    if not os.path.exists(README):
        return
    text = open(README, 'rb').read().decode('utf-8')
    if INDEX_START not in text or INDEX_END not in text:
        return
    rows = ['| Set | Designs | Treatments | Concepts | The designs |', '| --- | ---: | ---: | ---: | --- |']
    for s in ALL_SETS:
        mine = [e for e in models if e['set'] == s.path]
        designs = [e for e in mine if e['role'] == 'rig-ready' and not e.get('treatment')]
        treated = [e for e in mine if e.get('treatment')]
        concepts = [e for e in mine if e['role'] == 'concept']
        names = ', '.join(d for d, _ in s.designs)
        link = '[%s](%s/Preview.png)' % (s.path, s.path)
        rows.append('| %s | %d | %d | %d | %s |' % (link, len(designs), len(treated), len(concepts), names))
    total_d = sum(1 for e in models if e['role'] == 'rig-ready' and not e.get('treatment'))
    total_t = sum(1 for e in models if e.get('treatment'))
    total_c = sum(1 for e in models if e['role'] == 'concept')
    rows.append('| **All %d sets** | **%d** | **%d** | **%d** | %d files |' % (len(ALL_SETS), total_d, total_t, total_c, len(models)))
    nl = '\r\n' if '\r\n' in text else '\n'
    a = text.index(INDEX_START) + len(INDEX_START)
    b = text.index(INDEX_END)
    text = text[:a] + nl + nl.join(rows) + nl + text[b:]
    open(README, 'wb').write(text.encode('utf-8'))


def main(args):
    sets = [s for s in ALL_SETS if not args or any(s.path == a or s.path.startswith(a + '/') or s.path == a.rstrip('/') for a in args)]
    if args and not sets:
        print('no set matches', args)
        return 1
    manifest = {}
    if os.path.exists(MANIFEST):
        manifest = json.load(open(MANIFEST, encoding='utf-8'))
    models = {e['file']: e for e in manifest.get('models', [])}
    built = {s.path for s in sets}
    models = {k: e for k, e in models.items() if e['set'] not in built}
    log = []
    firsts = {}
    t0 = time.time()
    for s in sets:
        entries, made = build_set(s, log)
        for e in entries:
            models[e['file']] = e
        firsts[s.path] = made.get(1)
        n_r = sum(1 for e in entries if e['role'] == 'rig-ready')
        n_c = sum(1 for e in entries if e['role'] == 'concept')
        print('%-28s %3d rig-ready %3d concepts' % (s.path, n_r, n_c))
    out = {
        'about': 'Character models for VCOM, drawn on Character_Bigger.vox by _generator/build.py. See README.md.',
        'base': 'Character_Bigger.vox',
        'models': sorted(models.values(), key=lambda e: e['file']),
    }
    with open(MANIFEST, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(out, f, indent=1)
    if not args:
        write_index(out['models'])
        tiles = []
        for s in ALL_SETS:
            if firsts.get(s.path):
                name, m = firsts[s.path]
                colors, glass, glow = R.model_colors(m)
                tiles.append((s.path, R.render(colors, 'front_left', 6, glass=glass, glow=glow)))
        R.sheet(tiles, 9, cell=(230, 250), title='One of each: %d sets' % len(tiles), label_size=12).save(os.path.join(ROOT, 'Overview.png'))
    print('%d problems; %.1f s' % (len(log), time.time() - t0))
    for line in log[:80]:
        print('  ' + line)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
