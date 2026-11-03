#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""粤教粤人版地理：把 _bank/GYJ_B*.json 合并进 questions.json，并把点位正文回写 topics.json。

幂等：题按 id 跳过；topics 仅在分片提供了 description/mastery_criteria 时覆盖。
"""
import collections
import glob
import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "geography-yuejiao")
QP = os.path.join(D, "questions.json")
TP = os.path.join(D, "topics.json")
RANK = {"basic": 0, "standard": 1, "hard": 2}

qs = json.load(open(QP, encoding="utf-8")) if os.path.exists(QP) else []
have = {q["id"] for q in qs}
added = 0
topics = json.load(open(TP, encoding="utf-8"))
TMAP = {t["id"]: t for t in topics}
touched = 0
for f in sorted(glob.glob(os.path.join(D, "_bank", "GYJ_B*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    for q in d.get("questions") or []:
        if q["id"] in have:
            continue
        q.setdefault("question", q["prompt"])
        q.setdefault("choices", q.get("options", []))
        qs.append(q)
        have.add(q["id"])
        added += 1
    for it in d.get("items") or []:
        t = TMAP.get(it.get("topicId"))
        if not t:
            continue
        if it.get("description"):
            t["description"] = it["description"]
        if it.get("mastery_criteria"):
            t["mastery_criteria"] = it["mastery_criteria"]
        if (it.get("diagnostic_question") or {}).get("question"):
            t["diagnostic_question"] = it["diagnostic_question"]
        touched += 1

by = collections.defaultdict(list)
for q in qs:
    by[q["topicId"]].append(q)
for tid in by:
    by[tid].sort(key=lambda x: (RANK.get(x.get("difficulty"), 9), x["id"]))
qs = [q for tid in sorted(by) for q in by[tid]]
json.dump(qs, open(QP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(topics, open(TP, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"新增 {added} 题 → 总 {len(qs)}；点 {len(by)}；每点题数 "
      f"{dict(collections.Counter(collections.Counter(q['topicId'] for q in qs).values()))}；回写点位 {touched}")
