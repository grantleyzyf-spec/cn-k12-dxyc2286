#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""粤教粤人版地理（geography-yuejiao）数据不变量测试。

用法：python3 scripts/test_geo_yuejiao.py   # 退出码 0 = 全绿
"""
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-yuejiao")
TXT = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/6.《义务教育地理课程标准·日常修订版》(2022年版2025年修订).txt",
]
BOOKS = ["七年级上册", "七年级下册", "八年级上册", "八年级下册"]
DOMAINS = {"地球与地图", "世界地理", "中国地理", "乡土地理"}
fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


def chap_book(t):
    return t["chapter"].split(" ")[0]


topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
qs_path = os.path.join(D, "questions.json")
qs = json.load(open(qs_path, encoding="utf-8")) if os.path.exists(qs_path) else []
deps_path = os.path.join(D, "dependencies.json")
deps = json.load(open(deps_path, encoding="utf-8")) if os.path.exists(deps_path) else []
T = {t["id"]: t for t in topics}
units = [t for t in topics if t.get("level") == "unit"]
lessons = [t for t in topics if t.get("level") == "lesson"]

# 1 规模与唯一性
ck("知识点 171 条（单元 19 + 课时 152）",
   len(topics) == 171 and len(units) == 19 and len(lessons) == 152,
   f"{len(topics)}/{len(units)}/{len(lessons)}")
ck("id 唯一", len({t["id"] for t in topics}) == len(topics))
ck("subject 全为 geography-yuejiao", all(t.get("subject") == "geography-yuejiao" for t in topics))

# 2 册次覆盖
books_in = Counter(chap_book(t) for t in topics)
ck("四册齐全", [b for b in BOOKS if not books_in.get(b)] == [] and len(books_in) == 4, dict(books_in))
ck("每单元恰好 1 个单元点 + 8 个课时点",
   all(sum(1 for t in topics if t["chapter"] == u["chapter"] or t["chapter"].startswith(u["chapter"] + " · ")) == 9
       for u in units),
   [(u["id"], sum(1 for t in topics if t["chapter"] == u["chapter"] or t["chapter"].startswith(u["chapter"] + " · ")))
    for u in units][:3])

# 3 字段与领域
ck("description 全部 ≥30 字", all(len(t.get("description") or "") >= 30 for t in topics),
   [t["id"] for t in topics if len(t.get("description") or "") < 30][:5])
ck("mastery_criteria 全部 ≥2 条", all(len(t.get("mastery_criteria") or []) >= 2 for t in topics),
   [t["id"] for t in topics if len(t.get("mastery_criteria") or []) < 2][:5])
ck("domain 在义教课标四领域内", all(t.get("domain") in DOMAINS for t in topics),
   Counter(t.get("domain") for t in topics if t.get("domain") not in DOMAINS))
ck("tags 首项＝domain", all((t.get("tags") or [""])[0] == t.get("domain") for t in topics),
   [t["id"] for t in topics if (t.get("tags") or [""])[0] != t.get("domain")][:5])
ck("chapter 含册名与「第X单元」", all(re.match(r"^.+ 第[一二三四五六七八九十]+单元", t["chapter"]) for t in topics),
   [t["id"] for t in topics if not re.match(r"^.+ 第[一二三四五六七八九十]+单元", t["chapter"])][:5])

# 4 课标
ck("每个点都挂课标", all(t.get("standards") for t in topics),
   [t["id"] for t in topics if not t.get("standards")][:5])
ck("每条课标引用都带 quote", all(s.get("quote") for t in topics for s in t.get("standards") or []))
ck("confidence 三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                          for t in topics for s in t.get("standards") or []))
ck("curriculumRef 与首条课标一致",
   all((t.get("curriculumRef") or "") == (t.get("standards") or [{}])[0].get("id", "") for t in topics),
   [t["id"] for t in topics if (t.get("curriculumRef") or "") != (t.get("standards") or [{}])[0].get("id", "")][:5])

if all(os.path.exists(p) for p in TXT):
    src = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT))
    miss = []
    for t in topics:
        for s in t.get("standards") or []:
            if s.get("quote") and norm(s["quote"]) not in src:
                miss.append((t["id"], s["quote"][:14]))
    ck("quote 逐字回表 100%", not miss, miss[:3])
else:
    checks.append(("quote 回表（缺课标 TXT，跳过）", True, ""))

# 5 先修边
pairs = [(e["from"], e["to"]) for e in deps]
ck("无自环", all(a != b for a, b in pairs))
ck("无重复边", len(set(pairs)) == len(pairs))
ck("两端都存在", all(a in T and b in T for a, b in pairs))
ck("边类型只用 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps))
parent = {}
for a, b in pairs:
    parent.setdefault(b, set()).add(a)
asym = [(a, b) for b, ps in parent.items() for a in ps if a not in T[b].get("prerequisites", [])]
ck("deps ↔ prerequisites 双向镜像", not asym, asym[:3])
ck("课时点不挂单元点当先修",
   all(all(T[p]["level"] == "lesson" for p in t.get("prerequisites") or []) for t in lessons),
   [t["id"] for t in lessons if any(T[p]["level"] == "unit" for p in t.get("prerequisites") or [])][:3])
ck("课时点都有 prereqUpper", all(t.get("prereqUpper") for t in lessons),
   [t["id"] for t in lessons if not t.get("prereqUpper")][:3])
seen, stack = set(), []


def dfs(n):
    if n in stack:
        return False
    if n in seen:
        return True
    stack.append(n)
    for p in T[n].get("prerequisites") or []:
        if not dfs(p):
            return False
    stack.pop()
    seen.add(n)
    return True


cyc = [t["id"] for t in topics if not dfs(t["id"])]
ck("先修图无环", not cyc, cyc[:3])
ck("根节点都有 root_reason",
   all((t.get("prerequisites") or []) or t.get("root_reason") for t in topics),
   [t["id"] for t in topics if not (t.get("prerequisites") or []) and not t.get("root_reason")][:3])

# 6 题库（未产出时只提示）
if qs:
    per = Counter(q["topicId"] for q in qs)
    ck("每课时点 ≥8 题", all(per.get(t["id"], 0) >= 8 for t in lessons),
       [(t["id"], per.get(t["id"], 0)) for t in lessons if per.get(t["id"], 0) < 8][:5])
    ck("每单元点 ≥5 题", all(per.get(t["id"], 0) >= 5 for t in units),
       [(t["id"], per.get(t["id"], 0)) for t in units if per.get(t["id"], 0) < 5][:5])
    ck("题 id 唯一", len({q["id"] for q in qs}) == len(qs))
    ck("题目 topicId 都能对上", all(q["topicId"] in T for q in qs),
       [q["id"] for q in qs if q["topicId"] not in T][:3])
    ck("选择题 4 选项且答案在选项内",
       all(len(q.get("options") or []) == 4 and q.get("answer") in [o["label"] for o in q.get("options") or []]
           for q in qs if q.get("type") == "choice"),
       [q["id"] for q in qs if q.get("type") == "choice" and len(q.get("options") or []) != 4][:3])
    ck("numeric 都带 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"),
       [q["id"] for q in qs if q.get("type") == "numeric" and not q.get("verify")][:3])
    ck("题型四类齐全", {q.get("type") for q in qs} >= {"choice", "fill", "numeric", "short-answer"},
       sorted({q.get("type") for q in qs}))
    ck("难度三档齐全", {q.get("difficulty") for q in qs} >= {"basic", "standard", "hard"},
       sorted({q.get("difficulty") for q in qs}))
else:
    checks.append(("题库尚未产出（阶段 3 未开）", True, ""))

for name, ok, detail in checks:
    print(("✅" if ok else "❌"), name, ("" if ok else f"  [{detail}]"))
print(f"\n{sum(1 for _, ok, _ in checks if ok)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print("GEOGRAPHY-YUEJIAO DATA PASSED")
