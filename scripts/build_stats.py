#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 data/ 现算统计，写 data/stats.json，并打印可直接贴进 README 的 Markdown 表。
用法: python3 scripts/build_stats.py [--write]
"""
import json, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")

topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
questions = json.load(open(os.path.join(D, "questions.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, "dependencies.json"), encoding="utf-8"))
std = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
subs_meta = json.load(open(os.path.join(D, "subjects.json"), encoding="utf-8"))

NAME = {s["id"]: s["name"] for s in subs_meta.get("subjects", [])}
SUBJ = {t["id"]: t.get("subject") for t in topics}

def stage(g):
    g = str(g)
    if g.isdigit():
        n = int(g)
        return "小学" if n <= 6 else ("初中" if n <= 9 else "高中")
    return "其他"

by_sub = Counter(t.get("subject") for t in topics)
q_by_sub = Counter(SUBJ.get(q.get("topicId")) for q in questions)
dep_by_sub = Counter(SUBJ.get(e.get("from")) for e in deps)
dep_type = Counter(e.get("type") for e in deps)
stage_cnt = Counter(stage(t.get("grade")) for t in topics)

std_by_sub, quote_by_sub = Counter(), Counter()
for t in topics:
    ss = t.get("standards") or []
    if ss:
        std_by_sub[t.get("subject")] += 1
        if any(s.get("quote") for s in ss):
            quote_by_sub[t.get("subject")] += 1

subs_std = std.get("subjects", {})
std_total = sum(v.get("entryCount", 0) for v in subs_std.values()) if subs_std else 0
grades = sorted({str(t.get("grade")) for t in topics}, key=lambda x: (len(x), x))
quote_total = sum(quote_by_sub.values())
std_any = sum(1 for t in topics if t.get("standards"))

rows = [{
    "id": sid, "name": NAME.get(sid, sid), "topics": n,
    "deps": dep_by_sub.get(sid, 0), "questions": q_by_sub.get(sid, 0),
    "with_standards": std_by_sub.get(sid, 0), "with_quote": quote_by_sub.get(sid, 0),
} for sid, n in by_sub.most_common()]

stats = {
    "generated_by": "scripts/build_stats.py",
    "subjects": len(by_sub), "topics": len(topics), "questions": len(questions),
    "dependencies": len(deps), "dep_hard": dep_type.get("hard", 0), "dep_soft": dep_type.get("soft", 0),
    "grades": grades, "stages": dict(stage_cnt), "standards_entries": std_total,
    "topics_with_standards": std_any, "topics_with_quote": quote_total, "per_subject": rows,
}
if "--write" in sys.argv:
    json.dump(stats, open(os.path.join(D, "stats.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote data/stats.json")

print("\n| 学科 | 知识点 | 先修边 | 诊断题 | 已挂课标 | 其中带原文引文 |")
print("| --- | ---: | ---: | ---: | ---: | ---: |")
for r in rows:
    print(f"| {r['name']}（`{r['id']}`） | {r['topics']} | {r['deps']} | {r['questions']} | {r['with_standards']} | {r['with_quote']} |")
print(f"| **合计** | **{len(topics)}** | **{len(deps)}** | **{len(questions)}** | **{std_any}** | **{quote_total}** |")
print("\n学段分布:", dict(stage_cnt), "| 年级:", grades)
print("课标条目:", std_total, "| hard/soft:", dep_type.get("hard", 0), "/", dep_type.get("soft", 0))
