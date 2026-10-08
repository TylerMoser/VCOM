import sys
import numpy as np
from PIL import Image
from scipy import ndimage
Image.MAX_IMAGE_PIXELS = None
ROOT, OUT = sys.argv[1], sys.argv[2]
picture = np.asarray(Image.open(ROOT + "/MapCreation/Duchies.png").convert("RGBA"))
coast = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
fields = np.load(OUT + "/fields1.npz")
mainland = fields["king"] > 0
grey = (picture[..., 0] == picture[..., 1]) & (picture[..., 1] == picture[..., 2])
solid = grey & (picture[..., 3] == 255)
levels = np.bincount(picture[..., 0][solid], minlength=256)
print("solid grey pixels by level, 100 to 160:", {v: int(levels[v]) for v in range(100, 161)})
print("solid grey levels never used:", [v for v in range(256) if levels[v] == 0])
mid = grey & (picture[..., 0] > 40) & (picture[..., 0] < 215)
print("mid greys (41..214): %d in all; on the mainland mask: %d; within 3 px of it: %d; further out: %d" % (
    mid.sum(), (mid & mainland).sum(), (mid & ndimage.binary_dilation(mainland, iterations=3) & ~mainland).sum(),
    (mid & ~ndimage.binary_dilation(mainland, iterations=3)).sum()))
white = (picture[..., :3] >= 250).all(axis=2)
print("mainland: %d px; white %d; pink %d; purple %d; other %d" % (
    mainland.sum(), (white & mainland).sum(),
    ((picture[..., 0] == 233) & (picture[..., 1] == 0) & (picture[..., 2] == 255) & mainland).sum(),
    ((picture[..., 0] == 110) & (picture[..., 1] == 30) & (picture[..., 2] == 180) & mainland).sum(),
    (mainland & ~white & ~((picture[..., 0] == 233) & (picture[..., 1] == 0)) & ~((picture[..., 0] == 110) & (picture[..., 1] == 30))).sum()))
other = mainland & ~white & ~((picture[..., 0] == 233) & (picture[..., 1] == 0)) & ~((picture[..., 0] == 110) & (picture[..., 1] == 30))
vals, counts = np.unique(picture[other].reshape(-1, 4), axis=0, return_counts=True)
order = np.argsort(-counts)[:12]
print("commonest other colours on the mainland mask:", [(tuple(int(v) for v in vals[i]), int(counts[i])) for i in order])
print("coast picture equals Duchies.png off the pink and purple:", bool((coast == picture).all(axis=2)[~(((picture[..., 0] == 233) & (picture[..., 1] == 0)) | ((picture[..., 0] == 110) & (picture[..., 1] == 30)))].all()))
