"""How the source data's files are written: plain PNGs that any program reads exactly, and JSON
with one record to a line."""
import json
import os
import numpy as np
from PIL import Image

KM = 0.335
KM2 = KM * KM


def save_grey(path, values):
    """A map of whole numbers from 0 to 255 as an 8-bit grey PNG: a pixel's value is the number."""
    values = np.asarray(values)
    assert values.min() >= 0 and values.max() <= 255, (values.min(), values.max())
    Image.fromarray(values.astype(np.uint8), "L").save(path, optimize=True)
    print("wrote %s: %d x %d, values %d to %d, %d bytes" % (os.path.basename(path), values.shape[1], values.shape[0], values.min(), values.max(), os.path.getsize(path)))


def save_mask(path, mask):
    """Yes or no for every pixel: 255 where yes, 0 where no, as an 8-bit grey PNG."""
    Image.fromarray(np.where(mask, 255, 0).astype(np.uint8), "L").save(path, optimize=True)
    print("wrote %s: %d x %d, %d px set, %d bytes" % (os.path.basename(path), mask.shape[1], mask.shape[0], int(np.asarray(mask).sum()), os.path.getsize(path)))


def save_number(path, values):
    """A map of whole numbers from 0 to 65535 as an RGB PNG: the number is red + 256 x green; blue is 0."""
    values = np.asarray(values)
    assert values.min() >= 0 and values.max() <= 65535, (values.min(), values.max())
    rgb = np.zeros(values.shape + (3,), dtype=np.uint8)
    rgb[..., 0] = values % 256
    rgb[..., 1] = values // 256
    Image.fromarray(rgb, "RGB").save(path, optimize=True)
    print("wrote %s: %d x %d, values %d to %d, %d bytes" % (os.path.basename(path), values.shape[1], values.shape[0], values.min(), values.max(), os.path.getsize(path)))


def load_number(path):
    rgb = np.asarray(Image.open(path).convert("RGB")).astype(np.int32)
    return rgb[..., 0] + 256 * rgb[..., 1]


def kept(values):
    """Rounded to hundredths of a pixel without moving any value on to, or over, a half-pixel
    line: so a point falls in the same pixel however a drawing program rounds it to one, and a
    line drawn from the rounded points is the line drawn from the points."""
    values = np.asarray(values, dtype=np.float64)
    near = np.round(values, 2)
    on_line = (np.abs(2.0 * near - np.rint(2.0 * near)) < 1e-9) & (values != near)
    near = np.round(np.where(on_line, near + 0.01 * np.sign(values - near), near), 2)
    assert (np.floor(2.0 * near) == np.floor(2.0 * values)).all()
    return near


def _plain(value):
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(type(value))


def save_json(path, data):
    """JSON a person can scan: each top-level key on its own line, and each record of a top-level
    list on its own line, with nothing spread over several lines inside a record."""
    lines = ["{"]
    keys = list(data.keys())
    for i, key in enumerate(keys):
        value = data[key]
        comma = "," if i < len(keys) - 1 else ""
        if isinstance(value, list) and value and isinstance(value[0], (dict, list)):
            lines.append(" %s: [" % json.dumps(key))
            for j, item in enumerate(value):
                lines.append("  %s%s" % (json.dumps(item, separators=(",", ":"), default=_plain, ensure_ascii=False), "," if j < len(value) - 1 else ""))
            lines.append(" ]%s" % comma)
        else:
            lines.append(" %s: %s%s" % (json.dumps(key), json.dumps(value, separators=(", ", ": "), default=_plain, ensure_ascii=False), comma))
    lines.append("}")
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines) + "\n")
    with open(path, encoding="utf-8") as handle:
        json.load(handle)                                 # it reads back
    print("wrote %s: %d bytes" % (os.path.basename(path), os.path.getsize(path)))
