"""Splices the streams into the map's scene as it is, without making the scene afresh: the scene is
changed by hand, and only the streams and what goes with them are to change here.

What is spliced in is the scene m2_scene.gd makes with "streams" (from t2_shapes.py's shapes): the
Streams group, which goes in just before the Rivers, so the streams are drawn over the lakes and
under the rivers; the lines of a border's colour laid under a stream where it runs on a border
(...AlongStream...), each at the end of its rank's group under Borders; and the width curves they
use. Nothing else in the scene changes, a byte. A node's unique_id or a curve's id that the scene
already uses is given a new one.

With --replace, streams spliced in before are taken out first: the Streams group and everything
under it, every ...AlongStream... line, and the curves only they used. Anything changed in them by
hand is lost, so it is refused without it.

Usage: t3_splice.py <the scene> <the streams alone> [--replace]
"""
import random
import re
import sys

SCENE, ALONE = sys.argv[1], sys.argv[2]
REPLACE = "--replace" in sys.argv[3:]
NODE = re.compile(r'^\[node name="([^"]+)"(?: type="([^"]+)")?(?: parent="([^"]+)")?')
SUB = re.compile(r'^\[sub_resource type="([^"]+)" id="([^"]+)"\]')
UID = re.compile(r"unique_id=(\d+)")
USES = re.compile(r'SubResource\("([^"]+)"\)')


def blocks_of(text):
    """The file's blocks, each from its [heading] to the next: the first holds the file's own heading."""
    return re.split(r"\n(?=\[)", text)


def node_of(block):
    m = NODE.match(block)
    return (m.group(1), m.group(3)) if m else None


def path_of(name, parent):
    return name if parent in (None, ".") else parent + "/" + name


with open(SCENE, encoding="utf-8", newline="") as handle:
    scene_text = handle.read()
with open(ALONE, encoding="utf-8", newline="") as handle:
    alone_text = handle.read()
assert "\r\n" not in scene_text, "the scene has two-byte line ends; this keeps one-byte ones"
scene = blocks_of(scene_text)
alone = blocks_of(alone_text)

# -- what is in the scene already ------------------------------------------------------------------
had = [i for i, b in enumerate(scene) if node_of(b) and (path_of(*node_of(b)) == "Streams" or (node_of(b)[1] or "").startswith("Streams")
                                                          or "AlongStream" in node_of(b)[0])]
if had and not REPLACE:
    sys.exit("the scene has streams already (%d nodes): give --replace to take them out first" % len(had))
if had:
    gone = set(had)
    used_by_gone = set(u for i in gone for u in USES.findall(scene[i]))
    used_by_rest = set(u for i, b in enumerate(scene) if i not in gone for u in USES.findall(b))
    for i, b in enumerate(scene):
        m = SUB.match(b)
        if m and m.group(2) in used_by_gone and m.group(2) not in used_by_rest:
            gone.add(i)
    scene = [b for i, b in enumerate(scene) if i not in gone]
    print("took out %d blocks of streams spliced in before" % len(gone))

taken_uids = set(int(u) for b in scene for u in UID.findall(b.split("\n", 1)[0]))
taken_subs = set(SUB.match(b).group(2) for b in scene if SUB.match(b))

# -- what comes in ---------------------------------------------------------------------------------
subs, nodes = [], []
for b in alone[1:]:
    if SUB.match(b):
        subs.append(b)
    elif node_of(b):
        nodes.append(b)
rename = {}
rng = random.Random(20261017)
for i, b in enumerate(subs):
    kind, sid = SUB.match(b).groups()
    if sid in taken_subs:
        new = sid
        while new in taken_subs:
            new = "%s_%s" % (kind, "".join(rng.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(5)))
        rename[sid] = new
        subs[i] = b.replace('id="%s"]' % sid, 'id="%s"]' % new, 1)
    taken_subs.add(rename.get(sid, sid))
moved_uids = 0


def fixed(block):
    """A node's block with its curve renamed if need be, and a unique_id the scene does not use."""
    global moved_uids
    block = USES.sub(lambda m: 'SubResource("%s")' % rename.get(m.group(1), m.group(1)), block)
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


stream_nodes, banks = [], {}
for b in nodes:
    name, parent = node_of(b)
    path = path_of(name, parent)
    if parent is None or path in ("Borders", "Borders/Counties", "Borders/Duchies", "Borders/Kingdoms"):
        continue                      # the scene's own root and groups, which the scene has already
    if path == "Streams" or parent.startswith("Streams"):
        stream_nodes.append(fixed(b))
    elif parent.startswith("Borders/"):
        banks.setdefault(parent, []).append(fixed(b))
    else:
        sys.exit("not expected in the streams alone: %s" % path)

# -- where it goes -----------------------------------------------------------------------------------
def last_in(group):
    """The place of the last block under a group (the group's own, if it has nothing under it)."""
    last = None
    for i, b in enumerate(scene):
        n = node_of(b)
        if n and (path_of(*n) == group or (n[1] or "") == group or (n[1] or "").startswith(group + "/")):
            last = i
    if last is None:
        sys.exit("no %s in the scene" % group)
    return last


inserts = []                          # (after which block, the blocks)
first_node = next(i for i, b in enumerate(scene) if node_of(b))
inserts.append((first_node - 1, subs))
for group, bank_blocks in banks.items():
    inserts.append((last_in(group), bank_blocks))
rivers = next(i for i, b in enumerate(scene) if node_of(b) == ("Rivers", "."))
inserts.append((rivers - 1, stream_nodes))
for after, new_blocks in sorted(inserts, key=lambda x: -x[0]):
    # Every block ends with the blank line before the next; the file's last block need not.
    new_blocks = [nb if nb.endswith("\n") else nb + "\n" for nb in new_blocks]
    if not scene[after].endswith("\n"):
        scene[after] += "\n"
    scene[after + 1: after + 1] = new_blocks

text = "\n".join(scene)
with open(SCENE, "w", encoding="utf-8", newline="") as handle:
    handle.write(text)
print("spliced into %s: %d curves (%d renamed), %d stream nodes, %s; %d unique_ids changed; %d bytes" % (
    SCENE, len(subs), len(rename), len(stream_nodes), ", ".join("%d under %s" % (len(v), k) for k, v in sorted(banks.items())),
    moved_uids, len(text.encode("utf-8"))))
