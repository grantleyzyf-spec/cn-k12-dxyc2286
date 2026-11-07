#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人教版物理学层合并器：learn/_parts/<册>/*.json → learn/<册>.json（按 topics.json 的课时序）。

用法：python3 scripts/merge_geo_learn.py [--bucket physics]（默认 geography，人教）
"""
import json, os, glob, collections, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUCKET = sys.argv[sys.argv.index("--bucket") + 1] if "--bucket" in sys.argv else "physics"
D = os.path.join(REPO, "data", BUCKET)
PARTS = os.path.join(D, "learn", "_parts")
OUT = os.path.join(D, "learn")

topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
order = {t["id"]: i for i, t in enumerate(topics)}
topic_name = {t["id"]: t.get("name", "") for t in topics}

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
        # 篇名统一从 topics.json 取：docx 渲染按 title 派生文件名，缺 title 会渲染成 _<topicId>.docx
        if not les.get("title"):
            les["title"] = topic_name.get(tid, "")
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
