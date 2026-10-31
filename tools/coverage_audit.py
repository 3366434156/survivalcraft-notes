# -*- coding: utf-8 -*-
"""覆盖对账：源码每个 .cs 反查笔记库提名，零提名的即遗漏。零依赖。"""
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
SRC_ROOT = Path(r"E:\SurvivalcraftAPIProject")
LIB_ROOT = Path(r"E:\数据\生存战争系列\SC完全学习笔记")
EXCLUDE_DIRS = {"obj", "bin", ".vs", ".git", "packages", "TestResults"}

def iter_cs(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for f in filenames:
            if f.endswith(".cs"):
                yield Path(dirpath) / f

def lib_text():
    texts = []
    for p in LIB_ROOT.rglob("*.md"):
        if "docs" in p.parts:
            continue
        try:
            texts.append(p.read_text(encoding="utf-8", errors="replace"))
        except OSError:
            pass
    return "\n".join(texts)

def main():
    text = lib_text()
    by_dir = {}
    total = missed = 0
    for cs in iter_cs(SRC_ROOT):
        total += 1
        name = cs.name
        if name not in text:
            missed += 1
            rel = cs.relative_to(SRC_ROOT)
            by_dir.setdefault(str(rel.parent), []).append(name)
    print("TOTAL_CS=%d  UNMENTIONED=%d" % (total, missed))
    for d in sorted(by_dir):
        print("[%s] %d" % (d, len(by_dir[d])))
        for n in by_dir[d]:
            print("   ", n)

if __name__ == "__main__":
    main()
