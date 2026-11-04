#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并 data/history/learn/_parts/*.json → data/history/learn/<册>.json

用法：
    python3 scripts/merge_history_learn.py            # 只显示将要合并的结果
    python3 scripts/merge_history_learn.py --write    # 落盘（拒绝缩水：现有篇数更多时跳过该册）
"""
import argparse
import collections
import glob
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = os.path.join(REPO, "data", "history", "learn", "_parts")
OUT = os.path.join(REPO, "data", "history", "learn")
BOOK_ORDER = ["七年级上册", "七年级下册", "八年级上册", "八年级下册", "九年级上册", "九年级下册",
              "中外历史纲要（上）", "中外历史纲要（下）", "选择性必修1", "选择性必修2", "选择性必修3"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    by = collections.defaultdict(dict)
    for f in sorted(glob.glob(os.path.join(PARTS, "*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            print(f"⚠️ 跳过坏文件 {f}: {e}")
            continue
        for les in d.get("lessons", []):
            by[les.get("book") or d.get("book") or "?"][les["topicId"]] = les
    total = 0
    for b in BOOK_ORDER + [k for k in by if k not in BOOK_ORDER]:
        ls = by.get(b)
        if not ls:
            continue
        arr = sorted(ls.values(), key=lambda x: x["topicId"])
        total += len(arr)
        print(f"{b:<20} {len(arr):>3} 篇")
        if a.write:
            os.makedirs(OUT, exist_ok=True)
            dst = os.path.join(OUT, b + ".json")
            if os.path.exists(dst):
                old = json.load(open(dst, encoding="utf-8")).get("lessons", [])
                if len(old) > len(arr):
                    print(f"  拒绝缩水：现有 {len(old)} > 本次 {len(arr)}")
                    continue
            json.dump({"book": b, "lessons": arr}, open(dst, "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)
    print(f"合计 {total} 篇" + ("（已落盘）" if a.write else "（dry-run，加 --write 落盘）"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
