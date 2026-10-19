"""Splices the villages and hamlets into the map's scene as it is, without making the scene afresh:
the scene is changed by hand, and only the villages and what goes with them are to change here.

What is spliced in is the scene m2_scene.gd makes with "villages" (from v2_shapes.py's shapes):
- the hamlets and the villages, each under its group (Settlements/Hamlets, Settlements/Villages),
  whose descriptions, and the Settlements group's, are taken from it as well;
- the lanes, a group Roads/Lanes put first under Roads, so that the roads are drawn over them;
- the bridges on the lanes, a group Bridges/Lanes put last under Bridges;
- the channels, a group Channels put after the rivers, just before BordersOverLakes;
- the two scenes the places are instances of, Village.tscn and Hamlet.tscn, and the two materials
  the lanes and the bridges on them are drawn with, Lane.tres and LaneBridge.tres (the map's look,
  Docs/MAP.md "Its look", which m2_scene.gd draws them in).
Nothing else in the scene changes, a byte. A node's unique_id or a resource's id that the scene
already uses is given a new one.

With --replace, what was spliced in before is taken out first: every node under the hamlets' and
the villages' groups, the Lanes groups under Roads and Bridges and the Channels group with
everything under them, and the four resources. Anything changed in those by hand is lost, so it is
refused without it.

Usage: v3_splice.py <the scene> <the villages alone> [--replace]
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
OURS = ("res://Scenes/Village.tscn", "res://Scenes/Hamlet.tscn", "res://Resources/MapLines/Lane.tres",
        "res://Resources/MapLines/LaneBridge.tres")
GROUPS = ("Settlements", "Settlements/Hamlets", "Settlements/Villages")


def blocks_of(text):
    """The file's blocks, each from its [heading] to the next: the first holds the file's own heading."""
    return re.split(r"\n(?=\[)", text)


def node_of(block):
    m = NODE.match(block)
    return (m.group(1), m.group(3)) if m else None


def path_of(name, parent):
    return name if parent in (None, ".") else parent + "/" + name


def path(block):
    n = node_of(block)
    return path_of(*n) if n else None


def under(p, group):
    return p is not None and (p == group or p.startswith(group + "/"))


def spliced(block):
    """Whether a block of the scene is one this puts there."""
    p = path(block)
    if p is not None:
        return (p.startswith("Settlements/Hamlets/") or p.startswith("Settlements/Villages/") or under(p, "Roads/Lanes")
                or under(p, "Bridges/Lanes") or under(p, "Channels"))
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
    sys.exit("the scene has villages already (%d blocks): give --replace to take them out first" % len(had))
if had:
    gone = set(had)
    scene = [b for i, b in enumerate(scene) if i not in gone]
    print("took out %d blocks spliced in before" % len(gone))

taken_uids = set(int(u) for b in scene for u in UID.findall(b.split("\n", 1)[0]))
taken_ids = set(EXT.match(b).group(3) for b in scene if EXT.match(b))

# -- what comes in ---------------------------------------------------------------------------------
rng = random.Random(20261017)
rename = {}
exts = []
for b in alone[1:]:
    m = EXT.match(b)
    if not m:
        continue
    kind, where, rid = m.groups()
    assert where in OURS, "not expected among the villages' resources: %s" % where
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


def description_of(block):
    m = re.search(r'^editor_description = ".*"$', block, flags=re.M)
    return m.group(0) if m else None


coming = {"Settlements/Hamlets": [], "Settlements/Villages": [], "Roads/Lanes": [], "Bridges/Lanes": [], "Channels": []}
descriptions = {}
for b in alone[1:]:
    p = path(b)
    if p is None or p == "Map" or node_of(b)[1] is None:
        continue                      # resources, and the scene's own root
    if p in GROUPS:
        descriptions[p] = description_of(b)
        continue
    if p in ("Roads", "Bridges"):
        continue                      # groups the scene has already
    for group in coming:
        if under(p, group):
            coming[group].append(fixed(b))
            break
    else:
        sys.exit("not expected among the villages: %s" % p)

# -- where it goes -----------------------------------------------------------------------------------
# The groups the scene already has take the descriptions the villages come with.
for i, b in enumerate(scene):
    p = path(b)
    if p in descriptions and descriptions[p] is not None:
        old = description_of(b)
        scene[i] = b.replace(old, descriptions[p], 1) if old else b.replace("\n", "\n" + descriptions[p] + "\n", 1)


def place_of(p):
    return next(i for i, b in enumerate(scene) if path(b) == p)


def last_under(group):
    return max(i for i, b in enumerate(scene) if under(path(b), group))


inserts = []                          # (after which block, the blocks)
last_ext = max(i for i, b in enumerate(scene) if EXT.match(b))
inserts.append((last_ext, exts))
inserts.append((place_of("Settlements/Hamlets"), coming["Settlements/Hamlets"]))
inserts.append((place_of("Settlements/Villages"), coming["Settlements/Villages"]))
inserts.append((place_of("Roads"), coming["Roads/Lanes"]))
inserts.append((last_under("Bridges"), coming["Bridges/Lanes"]))
inserts.append((place_of("BordersOverLakes") - 1, coming["Channels"]))
for after, new_blocks in sorted(inserts, key=lambda x: -x[0]):
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
print("spliced into %s: %d resources, %s; %d unique_ids changed; %d bytes" % (
    SCENE, len(exts), ", ".join("%d under %s" % (len(v), k) for k, v in coming.items()), moved_uids, len(text.encode("utf-8"))))
