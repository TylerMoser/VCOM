"""Splices the forests into the map's scene as it is, without making the scene afresh: the scene is
changed by hand, and only the forests are to change here.

What is spliced in is the scene m2_scene.gd makes with "forests" (from f2_shapes.py's shapes):
- the group Forests, with everything under it, put right after the land (the last block under
  Land), so that the forests are drawn over the land and under everything else;
- the scenes the pieces are instances of, ConiferForest.tscn, BroadleafForest.tscn,
  TropicalForest.tscn and SwampForest.tscn.
Nothing else in the scene changes, a byte. A node's unique_id or a resource's id that the scene
already uses is given a new one.

With --replace, what was spliced in before is taken out first: the Forests group and everything
under it, and the four scenes' resources. Anything changed in those by hand is lost, so it is
refused without it.

Usage: f3_splice.py <the scene> <the forests alone> [--replace]
"""
import random
import re
import sys

SCENE, ALONE = sys.argv[1], sys.argv[2]
REPLACE = "--replace" in sys.argv[3:]
NODE = re.compile(r'^\[node name="([^"]+)"(?: type="([^"]+)")?(?: parent="([^"]+)")?')
EXT = re.compile(r'^\[ext_resource type="([^"]+)"(?: uid="[^"]+")? path="([^"]+)" id="([^"]+)"\]')
UID = re.compile(r"unique_id=(\d+)")
USES = re.compile(r'ExtResource\("([^"]+)"\)')
OURS = ("res://Scenes/ConiferForest.tscn", "res://Scenes/BroadleafForest.tscn", "res://Scenes/TropicalForest.tscn",
        "res://Scenes/SwampForest.tscn")
GROUP = "Forests"


def blocks_of(text):
    """The file's blocks, each from its [heading] to the next: the first holds the file's own heading."""
    return re.split(r"\n(?=\[)", text)


def path(block):
    m = NODE.match(block)
    if not m:
        return None
    name, parent = m.group(1), m.group(3)
    return name if parent in (None, ".") else parent + "/" + name


def under(p, group):
    return p is not None and (p == group or p.startswith(group + "/"))


def spliced(block):
    """Whether a block of the scene is one this puts there."""
    p = path(block)
    if p is not None:
        return under(p, GROUP)
    m = EXT.match(block)
    return bool(m) and m.group(2) in OURS


with open(SCENE, encoding="utf-8", newline="") as handle:
    scene_text = handle.read()
with open(ALONE, encoding="utf-8", newline="") as handle:
    alone_text = handle.read()
assert "\r\n" not in scene_text, "the scene has two-byte line ends; this keeps one-byte ones"
scene = blocks_of(scene_text)
alone = blocks_of(alone_text)

# -- what is in the scene already ------------------------------------------------------------------
had = [i for i, b in enumerate(scene) if spliced(b)]
if had and not REPLACE:
    sys.exit("the scene has forests already (%d blocks): give --replace to take them out first" % len(had))
if had:
    gone = set(had)
    scene = [b for i, b in enumerate(scene) if i not in gone]
    print("took out %d blocks spliced in before" % len(gone))

taken_uids = set(int(u) for b in scene for u in UID.findall(b.split("\n", 1)[0]))
taken_ids = set(EXT.match(b).group(3) for b in scene if EXT.match(b))

# -- what comes in ---------------------------------------------------------------------------------
rng = random.Random(20261018)
rename = {}
exts = []
for b in alone[1:]:
    m = EXT.match(b)
    if not m:
        continue
    kind, where, rid = m.groups()
    assert where in OURS, "not expected among the forests' resources: %s" % where
    wanted = "%d_%s" % (len(taken_ids) + 1, where.rsplit("/", 1)[1].split(".")[0].lower())
    while wanted in taken_ids:
        wanted = "%s_%s" % (wanted, "".join(rng.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(3)))
    rename[rid] = wanted
    taken_ids.add(wanted)
    exts.append(b.replace('id="%s"]' % rid, 'id="%s"]' % wanted, 1))
moved_uids = 0


def fixed(block):
    """A node's block with its scene renamed if need be, and a unique_id the scene does not use."""
    global moved_uids
    block = USES.sub(lambda m: 'ExtResource("%s")' % rename.get(m.group(1), m.group(1)), block)
    head, newline, rest = block.partition("\n")
    m = UID.search(head)
    if m:
        uid = int(m.group(1))
        if uid in taken_uids:
            while uid in taken_uids:
                uid = rng.randrange(1, 2 ** 31)
            head = UID.sub("unique_id=%d" % uid, head, count=1)
            moved_uids += 1
        taken_uids.add(uid)
    return head + newline + rest


coming = []
for b in alone[1:]:
    p = path(b)
    if p is None or p == "Map":
        continue                      # resources, and the scene's own root
    if not under(p, GROUP):
        sys.exit("not expected among the forests: %s" % p)
    coming.append(fixed(b))

# -- where it goes -----------------------------------------------------------------------------------
last_ext = max(i for i, b in enumerate(scene) if EXT.match(b))
after_land = max(i for i, b in enumerate(scene) if under(path(b), "Land"))
for after, new_blocks in sorted([(last_ext, exts), (after_land, coming)], key=lambda x: -x[0]):
    if not new_blocks:
        continue
    # Every block ends with the blank line before the next; the file's last block need not.
    new_blocks = [nb if nb.endswith("\n") else nb + "\n" for nb in new_blocks]
    if not scene[after].endswith("\n"):
        scene[after] += "\n"
    scene[after + 1: after + 1] = new_blocks

text = "\n".join(scene)
with open(SCENE, "w", encoding="utf-8", newline="") as handle:
    handle.write(text)
pieces = sum(1 for b in coming if 'instance=ExtResource(' in b.split("\n", 1)[0])
print("spliced into %s: %d resources, %d blocks under %s (%d pieces of forest); %d unique_ids changed; %d bytes" % (
    SCENE, len(exts), len(coming), GROUP, pieces, moved_uids, len(text.encode("utf-8"))))
