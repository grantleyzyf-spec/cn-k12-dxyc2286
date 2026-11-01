# -*- coding: utf-8 -*-
"""合并学层分片 → data/math-bj/learn/<册>.json（words 现算）。

用法: python3 merge_learn.py [--write]
"""
import json
import os
import re
import sys
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PARTS = os.path.join(ROOT, "learn", "_parts")
LEARN = os.path.join(ROOT, "learn")
BOOKS = ["一上", "一下", "二上", "二下", "三上", "三下", "四上", "五上", "六上",
         "七上", "七下", "八上", "八下", "九上"]


def hanzi(s):
    return len(re.findall(r"[\u4e00-\u9fa5]", s or ""))


def main():
    write = "--write" in sys.argv
    topics = json.load(open(os.path.join(ROOT, "topics.json"), encoding="utf-8"))
    need = OrderedDict()
    for t in topics:
        if t["level"] != "lesson":
            continue
        m = re.match(r"([一二三四五六七八九])年级([上下])册", t["chapter"])
        if m:
            need.setdefault(f"{m.group(1)}年级{m.group(2)}册", []).append(t["id"])

    got = OrderedDict((b, OrderedDict()) for b in need)
    dup, unknown = [], []
    if os.path.isdir(PARTS):
        for f in sorted(os.listdir(PARTS)):
            if not f.endswith(".json"):
                continue
            d = json.load(open(os.path.join(PARTS, f), encoding="utf-8"))
            book = d.get("book")
            if book not in got:
                unknown.append((f, book))
                continue
            for L in d.get("lessons") or []:
                tid = L.get("topicId")
                if tid in got[book]:
                    dup.append((book, tid, f))
                    continue
                n = hanzi(L.get("markdown"))
                got[book][tid] = dict(topicId=tid, title=L.get("title") or tid,
                                      markdown=L.get("markdown") or "", words=n)

    total = 0
    for book, lessons in got.items():
        miss = [t for t in need[book] if t not in lessons]
        total += len(lessons)
        print(f"  {book:8s} 已写 {len(lessons):3d}/{len(need[book]):3d}"
              + (f"  缺 {len(miss)}" if miss else "  ✓"))
        if write and lessons:
            dst = os.path.join(LEARN, f"{book}.json")
            json.dump(dict(book=book, lessons=list(lessons.values())),
                      open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("合计已写", total, "/", sum(len(v) for v in need.values()),
          "| 重复 topicId:", len(dup), dup[:3], "| 未知册:", unknown[:3])
    if write:
        print("已写 learn/<册>.json")


if __name__ == "__main__":
    main()
