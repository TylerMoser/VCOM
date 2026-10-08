"""Two things a duchy's counties must not do, and which of the duchies as solved do them:
two seats under MIN_GAP km apart, and the duchy's own seat with less than ROOM px of its own
county round it (unless it had less when the counties were first made).

Usage: n3_gates.py <old duchy out dir> <new duchy out dir> <tag>
"""
import pickle
import sys
import numpy as np
from scipy import ndimage

KM = 0.335
MIN_GAP = 13.0           # km: the closest two seats were when the counties were first made was 13.8
ROOM = 12.0              # px of its own county a duchy's seat should have on every side


def gap_of(seats):
    points = np.array(seats, dtype=np.float64)
    gap = np.hypot(points[:, None, 0] - points[None, :, 0], points[:, None, 1] - points[None, :, 1]) * KM
    np.fill_diagonal(gap, 1e9)
    return float(gap.min())


def room_of(owner, box, seat):
    """How far, in px, the duchy's seat is from the nearest land of another county of its duchy."""
    others = owner > 0
    if not others.any():
        return 1e9
    return float(ndimage.distance_transform_edt(~others)[seat[1] - box[0].start, seat[0] - box[1].start])


def passes(seats, owner, box, old_room):
    gap, room = gap_of(seats), room_of(owner, box, seats[0])
    return gap >= MIN_GAP and room >= min(ROOM, old_room - 1.0), gap, room


if __name__ == "__main__":
    OLD, NEW, TAG = sys.argv[1:4]
    with open(OLD + "/counties_%s.pickle" % TAG, "rb") as handle:
        old = pickle.load(handle)["results"]
    with open(NEW + "/counties_%s.pickle" % TAG, "rb") as handle:
        new = pickle.load(handle)["results"]
    failing = []
    for number in sorted(new):
        was, now = old[number], new[number]
        old_room = room_of(was["owner"], was["box"], was["seats"][0])
        good, gap, room = passes(now["seats"], now["owner"], now["box"], old_room)
        if not good:
            failing.append(number)
        if not good or room < 15 or gap < 16:
            print("duchy %2d (%s): closest seats %.1f km (were %.1f); the duchy seat's room %.1f px (was %.1f)%s" % (
                number, now["how"], gap, gap_of(was["seats"]), room, old_room, "" if good else "   <-- not good enough"))
    print("duchies not good enough: %s" % failing)
