#!/usr/bin/env python3
"""Safe anchored edits for the single-file game (sanctum-of-ash.html).

The game file is ~27MB so the Edit tool is impractical; instead we apply edits by
locating a UNIQUE verbatim anchor substring and inserting/replacing around it.
Every operation asserts the anchor occurs exactly once, so a bad anchor fails loudly
instead of silently corrupting the file.

Usage (from a small driver script):
    from apply_patch import Patcher
    p = Patcher("sanctum-of-ash.html")
    p.after("const enemies = [], corpses = [];", "\n/* new code */\n...")
    p.before("function setZone(", "/* hook */\n")
    p.replace("const CACHE = 'x'", "const CACHE = 'y'")
    p.save()   # writes only if every op applied; prints a summary
"""
import sys


class Patcher:
    def __init__(self, path):
        self.path = path
        with open(path, "r", encoding="utf-8") as f:
            self.s = f.read()
        self.ops = []

    def _count(self, anchor):
        return self.s.count(anchor)

    def _require_unique(self, anchor, what):
        n = self._count(anchor)
        if n == 0:
            raise SystemExit(f"[FAIL] {what}: anchor NOT FOUND:\n  {anchor!r}")
        if n > 1:
            raise SystemExit(f"[FAIL] {what}: anchor not unique ({n}x):\n  {anchor!r}")

    def after(self, anchor, code):
        self._require_unique(anchor, "after")
        self.s = self.s.replace(anchor, anchor + code, 1)
        self.ops.append(("after", anchor[:60]))
        return self

    def before(self, anchor, code):
        self._require_unique(anchor, "before")
        self.s = self.s.replace(anchor, code + anchor, 1)
        self.ops.append(("before", anchor[:60]))
        return self

    def replace(self, anchor, new):
        self._require_unique(anchor, "replace")
        self.s = self.s.replace(anchor, new, 1)
        self.ops.append(("replace", anchor[:60]))
        return self

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(self.s)
        print(f"[OK] {len(self.ops)} ops applied to {self.path}")
        for kind, a in self.ops:
            print(f"     {kind:8} @ {a!r}")


if __name__ == "__main__":
    print(__doc__)
