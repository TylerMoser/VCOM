"""Where the new borders run far from the old, and what they run along there, border by border.

Usage: kb3_where.py <duchy out dir> <kingdom fields dir> <network dir> <tag>
"""
import pickle
import sys
import numpy as np
from scipy import ndimage

OUT, KING, NET, TAG = sys.argv[1:5]
KM = 0.335
fields = np.load(OUT + "/fields1.npz")
more = np.load(KING + "/fields.npz")
away = np.load(NET + "/near.npz")["away"]
with open(KING + "/lines_%s.pickle" % TAG, "rb") as handle:
    lines = pickle.load(handle)
river, lake, divide = fields["river"], fields["lake"], fields["divide"]
ridge = fields["ridge"] | divide
names = (("river", ndimage.binary_dilation(river, iterations=2)), ("lake", ndimage.binary_dilation(lake, iterations=2)),
         ("watershed", ndimage.binary_dilation(divide, iterations=3)), ("ridge", ndimage.binary_dilation(ridge, iterations=3)),
         ("spur or brook", ndimage.binary_dilation(more["spur"] | more["brook"], iterations=2)))
for code, cells in zip(lines["codes"], lines["cells"]):
    far = away[cells[:, 0], cells[:, 1]]
    on = np.zeros(len(cells), dtype=np.int8)
    for i, (name, mask) in enumerate(names, start=1):
        on = np.where((on == 0) & mask[cells[:, 0], cells[:, 1]], i, on)
    share = [100.0 * (on == i).mean() for i in range(len(names) + 1)]
    worst = int(np.argmax(far))
    long_far = far > 24.0
    print("border %d|%d: %4.0f km long; from the old line %4.1f km on average, %4.1f at most at (%d, %d); beyond 24 km for %3.0f km; along river %2.0f%%, lake %2.0f%%, watershed %2.0f%%, ridge %2.0f%%, spur or brook %2.0f%%, open %2.0f%%" % (
        code // 10, code % 10, len(cells) * KM * 1.1, far.mean(), far.max(), cells[worst, 1], cells[worst, 0], long_far.sum() * KM * 1.1,
        share[1], share[2], share[3], share[4], share[5], share[0]))
print("meeting places now: %s" % [m[::-1] for m in lines["meet"]])
