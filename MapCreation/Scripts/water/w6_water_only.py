"""Water.png: Rivers.png with the brown watershed lines taken off again, leaving the coast map
with its rivers and lakes. Every brown pixel goes back to what the coast map has there; the check
then confirms nothing but the blue differs from the coast map, and that the blue is the same.

Usage: w6_water_only.py <repo root>
"""
import sys
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
ROOT = sys.argv[1]
BLUE = (28, 112, 224, 255)
BROWN = (196, 118, 44, 255)

rivers = np.asarray(Image.open(ROOT + "/MapCreation/Rivers.png").convert("RGBA"))
plain = np.asarray(Image.open(ROOT + "/MapCreation/WorldMapV1.png").convert("RGBA"))
brown = (rivers == np.array(BROWN, dtype=np.uint8)).all(axis=2)
water = rivers.copy()
water[brown] = plain[brown]
Image.fromarray(water, "RGBA").save(ROOT + "/MapCreation/Water.png")

saved = np.asarray(Image.open(ROOT + "/MapCreation/Water.png").convert("RGBA"))
changed = (saved != plain).any(axis=2)
colours, counts = np.unique(saved[changed].reshape(-1, 4), axis=0, return_counts=True)
blue_before = (rivers == np.array(BLUE, dtype=np.uint8)).all(axis=2)
blue_after = (saved == np.array(BLUE, dtype=np.uint8)).all(axis=2)
print("Water.png: %d x %d, %s" % (saved.shape[1], saved.shape[0], Image.open(ROOT + "/MapCreation/Water.png").mode))
print("brown pixels taken off: %d; brown left: %d" % (brown.sum(), (saved == np.array(BROWN, dtype=np.uint8)).all(axis=2).sum()))
print("pixels differing from the coast map: %d, in colours %s" % (changed.sum(), {tuple(int(v) for v in c): int(n) for c, n in zip(colours, counts)}))
print("blue the same as in Rivers.png: %s (%d px)" % (bool((blue_before == blue_after).all()), blue_after.sum()))
print("differs from Rivers.png only where that was brown: %s" % bool(((saved != rivers).any(axis=2) == brown).all()))
