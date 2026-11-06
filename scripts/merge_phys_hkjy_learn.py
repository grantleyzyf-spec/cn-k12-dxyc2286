#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""merge_phys_hkjy_learn.py —— _learn_parts/L*_out.json → learn/<册>.json（按骨架课时顺序）。
护栏：目标册已存在且现有篇数 > 本次合并篇数 → 拒绝写入（防缩水）。
"""
import glob
import json
import os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-hkjy")
sk = json.load(open(os.path.join(D, "_skeleton.json"), encoding="utf-8"))
rows = sk if isinstance(sk, list) else sk["lessons"]
rows = [l for l in rows if l.get("level") == "lesson"]
order = [l["id"] for l in rows]
byid = {l["id"]: l for l in rows}
parts = defaultdict(list)
for f in sorted(glob.glob(os.path.join(D, "_learn_parts", "*_out.json"))):
    d = json.load(open(f, encoding="utf-8"))
    for les in d.get("lessons", []):
        if not (les.get("markdown") or "").strip():
            continue
        book = les.get("book") or byid[les["topicId"]]["chapter"].split(" ")[0]
        les["book"] = book
        les["title"] = byid[les["topicId"]]["name"]
        parts[book].append(les)
ok = True
total = 0
for book, lessons in parts.items():
    lessons.sort(key=lambda x: order.index(x["topicId"]) if x["topicId"] in order else 999)
    p = os.path.join(D, "learn", book + ".json")
    old = json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None
    if old and len(old.get("lessons", [])) > len(lessons):
        print("!! 拒绝写 %s：现有 %d 篇 > 本次 %d 篇" % (book, len(old["lessons"]), len(lessons)))
        ok = False
        continue
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump({"book": book, "lessons": lessons}, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    total += len(lessons)
    print("  %-12s %d 篇" % (book, len(lessons)))
print("合计 %d 篇 / 应 %d 篇" % (total, len(order)))
print("ALL_OK" if ok and total == len(order) else "HAS_FAIL")
