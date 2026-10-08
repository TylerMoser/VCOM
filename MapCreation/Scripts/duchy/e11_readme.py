"""The source data's README.md: the written part, with every file's size put in.

Usage: e11_readme.py <template> <the source data's folder>
"""
import os
import re
import sys

TEMPLATE, TO = sys.argv[1:3]
text = open(TEMPLATE, encoding="utf-8").read()
names = sorted(n for n in os.listdir(TO) if n != "README.md")
for name in names:
    marker = "{{%s}}" % name
    assert text.count(marker) == 1, "the template has %d places for %s" % (text.count(marker), name)
    size = os.path.getsize(TO + "/" + name)
    text = text.replace(marker, "%.1f MB" % (size / 1e6) if size >= 1e6 else "%d KB" % max(round(size / 1e3), 1))
left = re.findall(r"\{\{[^}]*\}\}", text)
assert not left, "the template names files that are not in the folder: %s" % left
with open(TO + "/README.md", "w", encoding="utf-8", newline="\n") as handle:
    handle.write(text)
longest = max(len(line) for line in text.split("\n") if not line.startswith("|") and not line.startswith("var ") and "import" not in line)
print("wrote README.md: %d files told of, %d lines, %d bytes; the longest line of prose is %d characters" % (len(names), text.count("\n"), os.path.getsize(TO + "/README.md"), longest))
