"""Cut views out of a picture. Usage: crops2.py <picture> <out dir> <prefix> name=x0,y0,x1,y1[,scale] ..."""
import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
image = Image.open(sys.argv[1]).convert("RGB")
for spec in sys.argv[4:]:
    name, numbers = spec.split("=")
    values = [float(v) for v in numbers.split(",")]
    box = tuple(int(v) for v in values[:4])
    view = image.crop(box)
    if len(values) > 4:
        view = view.resize((int(view.width * values[4]), int(view.height * values[4])), Image.LANCZOS if values[4] < 1 else Image.NEAREST)
    view.save("%s/%s_%s.png" % (sys.argv[2], sys.argv[3], name))
print("done")
