#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""地理学层合并器：learn/_parts/<册>/*.json → learn/<册>.json（按 topics.json 的课时序）。"""
import json, os, glob, collections

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "geography")
PARTS = os.path.join(D, "learn", "_parts")
OUT = os.path.join(D, "learn")

topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
order = {t["id"]: i for i, t in enumerate(topics)}

by_book = collections.defaultdict(dict)
for f in sorted(glob.glob(os.path.join(PARTS, "*", "*.json"))):
    obj = json.load(open(f, encoding="utf-8"))
    book = obj.get("book") or os.path.basename(os.path.dirname(f))
    # 一片 4 篇时是 {book, lessons:[…]}；一篇一文件时直接是单篇对象
    batch = obj.get("lessons") if isinstance(obj, dict) and "lessons" in obj else [obj]
    for les in batch or []:
        tid = les.get("topicId")
        if not tid:
            continue
        les = dict(les)
        les["book"] = book
        by_book[book][tid] = les

total = 0
for book, lessons in sorted(by_book.items()):
    items = [lessons[k] for k in sorted(lessons, key=lambda x: order.get(x, 9999))]
    dst = os.path.join(OUT, f"{book}.json")
    json.dump({"book": book, "lessons": items}, open(dst, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    total += len(items)
    print(f"{book}: {len(items)} 篇 → {dst}")
print(f"合计 {total} 篇")
