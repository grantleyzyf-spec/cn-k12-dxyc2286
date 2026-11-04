#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""湘教版地理：把 _bank/GXJ_B*.json 合并进 questions.json（幂等，按 id 跳过）。"""
import json, os, glob, collections

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "geography-xiangjiao")
QP = os.path.join(D, "questions.json")
RANK = {"basic": 0, "standard": 1, "hard": 2}

qs = json.load(open(QP, encoding="utf-8")) if os.path.exists(QP) else []
have = {q["id"] for q in qs}
added = 0
for f in sorted(glob.glob(os.path.join(D, "_bank", "GXJ_B*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    for q in d.get("questions") or []:
        if q["id"] in have:
            continue
        q.setdefault("question", q["prompt"])
        q.setdefault("choices", q.get("options", []))
        qs.append(q); have.add(q["id"]); added += 1
by = collections.defaultdict(list)
for q in qs:
    by[q["topicId"]].append(q)
for tid in by:
    by[tid].sort(key=lambda x: (RANK.get(x.get("difficulty"), 9), x["id"]))
qs = [q for tid in sorted(by) for q in by[tid]]
json.dump(qs, open(QP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"新增 {added} 题 → 总 {len(qs)}；点 {len(by)}；每点题数 {dict(collections.Counter(collections.Counter(q['topicId'] for q in qs).values()))}")
