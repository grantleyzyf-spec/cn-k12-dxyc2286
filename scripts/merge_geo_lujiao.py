#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""merge_geo_lujiao.py —— 把 _parts/*.json 合并成 topics/questions/dependencies。

口径（与语文/地理兄弟桶一致）：
- 课时点先修＝同册上一节（跨单元成链）；每册首节为根（写 root_reason）。
- 单元点是一个「上位点」：prerequisites=[]，写 root_reason，不挂 unit→lesson 边（避免与双向镜像断言互斥）。
- 题量：课时点恰好 8、单元点恰好 5；id 唯一。
"""
import json, os, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-lujiao")
sk = json.load(open(os.path.join(D, "_skeleton.json"), encoding="utf-8"))

parts = {}
for f in sorted(os.listdir(os.path.join(D, "_parts"))):
    if not f.endswith(".json"):
        continue
    d = json.load(open(os.path.join(D, "_parts", f), encoding="utf-8"))
    parts[d["unitId"]] = d
print("分片 %d / 19" % len(parts))

units = sk["units"]
lessons = sk["lessons"]
need_unit = {u["id"] for u in units}
need_lesson = {l["id"] for l in lessons}
miss_u = need_unit - set(parts)
if miss_u:
    print("!! 缺分片:", sorted(miss_u)); sys.exit(1)

# ---- 合并点
topics = []
qall = []
for u in units:
    p = parts[u["id"]]
    uu = dict(u)
    uu.update({k: v for k, v in p.get("unit", {}).items()
               if k in ("description", "mastery_criteria", "type", "tags", "diagnostic_question")})
    uu["prerequisites"] = []
    uu["root_reason"] = "单元上位点，不设先修课时；本单元各课时以同册上一节为直接先修。"
    uu["curriculumRef"] = uu["standards"][0]["id"]
    uu.setdefault("external", False)
    uu["verified"] = False
    topics.append(uu)

for l in lessons:
    p = parts[l["unitId"]]
    lp = next((x for x in p.get("lessons", []) if x["id"] == l["id"]), None)
    if not lp:
        print("!! 分片缺课时点", l["id"]); sys.exit(1)
    ll = dict(l)
    ll.update({k: v for k, v in lp.items()
               if k in ("description", "mastery_criteria", "type", "tags", "diagnostic_question")})
    ll["curriculumRef"] = ll["standards"][0]["id"]
    ll.setdefault("external", False)
    ll["verified"] = False
    topics.append(ll)

# ---- 先修链（同册按 lessonNo 顺序）
by_book = {}
for l in lessons:
    by_book.setdefault(l["chapter"].split(" ")[0], []).append(l)
for book, ls in by_book.items():
    ls.sort(key=lambda x: (x["unitNo"], x["lessonNo"]))
    prev = None
    for i, l in enumerate(ls):
        t = next(x for x in topics if x["id"] == l["id"])
        if prev is None:
            t["prerequisites"] = []
            t["root_reason"] = "%s 的第一节，是本册学习的起点，不需要前置课时。" % book
        else:
            t["prerequisites"] = [prev]
        prev = l["id"]

deps = []
for t in topics:
    for pre in t.get("prerequisites") or []:
        deps.append({"from": pre, "to": t["id"], "type": "hard"})

# ---- 题
for uid, p in parts.items():
    for q in p.get("questions", []):
        q.setdefault("question", q.get("prompt", ""))
        q.setdefault("options", [])
        q.setdefault("choices", q.get("options") or [])
        qall.append(q)

# ---- 校验
T = {t["id"] for t in topics}
per = Counter(q["topicId"] for q in qall)
bad_amt = [(k, v) for k, v in per.items() if v != (5 if k in need_unit else 8)]
missing_q = [t for t in T if t not in per]
dup_q = [k for k, v in Counter(q["id"] for q in qall).items() if v > 1]
print("点 %d ｜ 题 %d ｜ 边 %d" % (len(topics), len(qall), len(deps)))
if bad_amt:
    print("!! 题量不符（单元应 5 / 课时应 8）:", bad_amt[:10])
if missing_q:
    print("!! 无题点:", missing_q[:10])
if dup_q:
    print("!! 题 id 重复:", dup_q[:10])
if bad_amt or missing_q or dup_q:
    sys.exit(1)

json.dump(topics, open(os.path.join(D, "topics.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(qall, open(os.path.join(D, "questions.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(deps, open(os.path.join(D, "dependencies.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("题型", dict(Counter(q["type"] for q in qall)))
print("难度", dict(Counter(q["difficulty"] for q in qall)))
print("答案位", dict(sorted(Counter(q["answer"] for q in qall if q["type"] == "choice").items())))
print("已写 topics/questions/dependencies")
