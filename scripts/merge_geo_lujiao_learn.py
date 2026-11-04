#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""merge_geo_lujiao_learn.py —— _learn_parts/*.json → learn/<册>.json（按骨架课时顺序）。
护栏：目标册已存在且现有篇数 > 本次合并篇数 → 拒绝写入（防缩水）。
"""
import json, os, glob
from collections import defaultdict
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D=os.path.join(ROOT,"data","geography-lujiao")
sk=json.load(open(os.path.join(D,"_skeleton.json"),encoding="utf-8"))
order=[l["id"] for l in sk["lessons"]]
byid={l["id"]:l for l in sk["lessons"]}
parts=defaultdict(list)
for f in sorted(glob.glob(os.path.join(D,"_learn_parts","*_out.json"))):
    d=json.load(open(f,encoding="utf-8"))
    for les in d.get("lessons",[]):
        if not (les.get("markdown") or "").strip():
            continue
        parts[les.get("book") or byid[les["topicId"]]["chapter"].split(" ")[0]].append(les)
ok=True
for book,lessons in parts.items():
    lessons.sort(key=lambda x: order.index(x["topicId"]) if x["topicId"] in order else 999)
    p=os.path.join(D,"learn",book+".json")
    old=json.load(open(p,encoding="utf-8")) if os.path.exists(p) else None
    if old and len(old.get("lessons",[]))>len(lessons):
        print("!! 拒绝写 %s：现有 %d 篇 > 本次 %d 篇"%(book,len(old["lessons"]),len(lessons))); ok=False; continue
    os.makedirs(os.path.dirname(p),exist_ok=True)
    json.dump({"book":book,"lessons":lessons},open(p,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
    print("  %-8s %d 篇"%(book,len(lessons)))
print("ALL_OK" if ok else "HAS_FAIL")
