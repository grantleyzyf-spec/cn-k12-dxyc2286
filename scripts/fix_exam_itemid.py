#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给某版本桶的卷面题补 itemId（整卷测试作答依赖它；缺了同一份卷所有题的 data-item 都是 undefined、互相覆盖）。

用法：python3 scripts/fix_exam_itemid.py math-hebei [--write]
规则：itemId = f"{examId}_q{no:02d}"（与数学人教卷、冀教已有 16 卷一致）。
幂等：已有 itemId 的题不动；复跑应报「改动 0 卷」。
"""
import argparse
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bucket")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    base = os.path.join(ROOT, "data", a.bucket, "exams")
    files = [p for p in glob.glob(os.path.join(base, "**", "*.json"), recursive=True)
             if not any(s.startswith("_") for s in os.path.relpath(p, base).split(os.sep))]
    fixed = touched = items_fixed = 0
    for p in sorted(files):
        d = json.load(open(p, encoding="utf-8"))
        eid = d.get("examId")
        if not eid:
            continue
        changed = False
        for sec in d.get("sections") or []:
            for it in sec.get("items") or []:
                if not it.get("itemId"):
                    it["itemId"] = f"{eid}_q{int(it.get('no', 0)):02d}"
                    items_fixed += 1
                    changed = True
        if changed:
            touched += 1
            if a.write:
                json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
                open(p, "a", encoding="utf-8").write("\n")
    print(f"{a.bucket}: 扫 {len(files)} 卷 · 需补 {touched} 卷 / {items_fixed} 题"
          f"{' · 已写入' if a.write else ' · 干跑（加 --write 落盘）'}")
    return touched


if __name__ == "__main__":
    main()
