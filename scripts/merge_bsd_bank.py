#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并 _bank/*.json → data/math-bsd/{topics,questions}.json（白名单字段重建）。

用法: python3 scripts/merge_bsd_bank.py [--root data/math-bsd] [--require-books 一年级上册 …]
- topics 只保留 schema 允许的字段；content 由分片提供（description/mastery_criteria/type/diagnostic_question）
- questions 按 topicId 排序后整体写盘
- 打印「缺内容点 / 无题点 / 题量分布」，分片齐不齐一眼可见
"""
import argparse, glob, json, os
from collections import Counter

TOPIC_FIELDS = ["id", "name", "subject", "domain", "grade", "semester", "chapter", "level",
                "type", "description", "mastery_criteria", "diagnostic_question", "external",
                "standards", "tags", "prerequisites", "root_reason", "verified"]
Q_FIELDS = ["id", "topicId", "prompt", "question", "options", "choices", "answer", "type",
            "difficulty", "explanation", "verify", "keypoints"]

ap = argparse.ArgumentParser()
ap.add_argument("--root", default="data/math-bsd")
ap.add_argument("--require-books", nargs="*", default=None)
a = ap.parse_args()

topics = json.load(open(f"{a.root}/topics.json", encoding="utf-8"))
T = {t["id"]: t for t in topics}
banks = sorted(glob.glob(f"{a.root}/_bank/*.json"))
questions, missing, unused = [], [], []
for bp in banks:
    b = json.load(open(bp, encoding="utf-8"))
    for t in b.get("topics", []):
        if t["id"] not in T:
            unused.append((os.path.basename(bp), t["id"]))
            continue
        for k in ("description", "mastery_criteria", "type", "diagnostic_question"):
            if t.get(k):
                T[t["id"]][k] = t[k]
    questions.extend(b.get("questions", []))

by_t = Counter(q["topicId"] for q in questions)
for tid, t in T.items():
    if not t.get("description"):
        missing.append(tid)
noq = [tid for tid in T if by_t.get(tid, 0) == 0]
short = [tid for tid in T if 0 < by_t.get(tid, 0) < 8]

# 白名单重建 + 补默认值
out_t = []
for t in topics:
    d = {k: t[k] for k in TOPIC_FIELDS if k in t}
    d.setdefault("tags", [d.get("domain")])
    if not d.get("tags") or d["tags"][0] != d.get("domain"):
        d["tags"] = [d.get("domain")] + [x for x in (d.get("tags") or []) if x != d.get("domain")]
    d.setdefault("type", "procedural")
    out_t.append(d)

out_q = []
for q in sorted(questions, key=lambda x: (x["topicId"], x["id"])):
    d = {k: q[k] for k in Q_FIELDS if k in q}
    if d.get("type") == "choice":
        d["choices"] = d.get("options", [])          # 与 options 同值（schema 要求 object 数组）
    else:
        d["choices"] = []
    out_q.append(d)

json.dump(out_t, open(f"{a.root}/topics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(f"{a.root}/topics.json", "a", encoding="utf-8").write("\n")
json.dump(out_q, open(f"{a.root}/questions.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(f"{a.root}/questions.json", "a", encoding="utf-8").write("\n")

# 汇总统计回写 subjects.json / stats.json 由 build_stats 负责；这里只报数
print(f"分片 {len(banks)} 个 | 知识点 {len(out_t)} | 诊断题 {len(out_q)}")
print("题型:", dict(Counter(q["type"] for q in out_q)))
print("难度:", dict(Counter(q["difficulty"] for q in out_q)))
print(f"缺内容点 {len(missing)}: {missing[:5]}")
print(f"无题点 {len(noq)}: {noq[:5]}")
print(f"题量不足 8 的点 {len(short)}: {short[:5]}")
if unused:
    print("⚠️ bank 里有不属于本切片的 topicId:", unused[:5])
