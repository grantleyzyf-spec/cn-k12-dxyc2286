#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""中图版（钟作慈）初中地理（geography-zhongtu-cz）数据不变量测试。

用法：python3 scripts/test_geo_ztu.py      # 退出码 0 = 全绿

规模断言（改规模先改这里）：4 册 / 18 个单元位（17 章 + 绪论）/ 137 课时点 = 155 点；每课时点 8 题、每单元点 5 题。
"""
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-zhongtu-cz")
TXT = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/6.《义务教育地理课程标准·日常修订版》(2022年版2025年修订).txt",
]
BOOKS = ["七年级上册", "七年级下册", "八年级上册", "八年级下册"]
# 义教地理四领域（中图版（钟作慈）只有初中，⛔ 不用高中四领域、⛔ 不用「地球与宇宙」「地图与地理工具」这类自造名）
DOMAINS = {"地球与地图", "世界地理", "中国地理", "乡土地理"}
N_TOPICS, N_UNITS, N_LESSONS = 155, 18, 137
BOOK_POINTS = {"七年级上册": 47, "七年级下册": 36, "八年级上册": 36, "八年级下册": 36}
fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
qs_path = os.path.join(D, "questions.json")
qs = json.load(open(qs_path, encoding="utf-8")) if os.path.exists(qs_path) else []
deps_path = os.path.join(D, "dependencies.json")
deps = json.load(open(deps_path, encoding="utf-8")) if os.path.exists(deps_path) else []
T = {t["id"]: t for t in topics}
units = [t for t in topics if t.get("level") == "unit"]
lessons = [t for t in topics if t.get("level") == "lesson"]

# 1 规模与唯一性
ck(f"知识点 {N_TOPICS} 条（单元 {N_UNITS} + 课时 {N_LESSONS}）",
   len(topics) == N_TOPICS and len(units) == N_UNITS and len(lessons) == N_LESSONS,
   f"{len(topics)}/{len(units)}/{len(lessons)}")
ck("id 唯一", len({t["id"] for t in topics}) == len(topics))
ck("subject 全为 geography-zhongtu-cz", all(t.get("subject") == "geography-zhongtu-cz" for t in topics))

# 2 册次与主题覆盖
books_in = Counter(t["chapter"].split(" ")[0] for t in topics)
ck("四册齐全且册级点数对表", set(books_in) == set(BOOKS) and all(books_in[b] == BOOK_POINTS[b] for b in BOOKS), dict(books_in))
per_unit = Counter(t.get("prereqUpper") or t["id"] for t in lessons)
ck("每个单元位课时数对表（17 章各 8 + 绪论 1）",
   len(per_unit) == N_UNITS and sum(per_unit.values()) == N_LESSONS and sorted(per_unit.values()).count(1) == 1
   and set(per_unit.values()) == {1, 8}, dict(per_unit))

# 3 字段与领域
ck("description 汉字 40–120",
   all(40 <= len(re.findall(r"[\u4e00-\u9fa5]", t.get("description") or "")) <= 120 for t in topics),
   [(t["id"], len(re.findall(r"[\u4e00-\u9fa5]", t.get("description") or ""))) for t in topics
    if not 40 <= len(re.findall(r"[\u4e00-\u9fa5]", t.get("description") or "")) <= 120][:5])
ck("mastery_criteria 2–3 条",
   all(2 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics),
   [t["id"] for t in topics if not 2 <= len(t.get("mastery_criteria") or []) <= 3][:5])
ck("domain 在义教地理四领域内", all(t.get("domain") in DOMAINS for t in topics),
   Counter(t.get("domain") for t in topics if t.get("domain") not in DOMAINS))
ck("tags 首项＝domain", all((t.get("tags") or [""])[0] == t.get("domain") for t in topics),
   [t["id"] for t in topics if (t.get("tags") or [""])[0] != t.get("domain")][:5])
ck("chapter 形如「<册> 第N章 <章名>」（绪论单独成位）",
   all(re.match(r"^\S+?(上|下)册 (第[一二三四五六七八九十\d]+章|绪论) \S", t["chapter"]) for t in topics),
   [t["id"] for t in topics
    if not re.match(r"^\S+?(上|下)册 (第[一二三四五六七八九十\d]+章|绪论) \S", t["chapter"])][:5])
ck("课时点 chapter 带「 · 第N课时」",
   all(" · 第" in t["chapter"] for t in lessons),
   [t["id"] for t in lessons if " · 第" not in t["chapter"]][:5])
ck("grade/semester 与册次一致",
   all((t["grade"] == (7 if t["chapter"].startswith("七年级") else 8))
       and (t["semester"] == ("上" if "上册" in t["chapter"].split(" ")[0] else "下")) for t in topics),
   [t["id"] for t in topics if t["grade"] not in (7, 8)][:5])

# 4 课标
ck("每个点都挂课标", all(t.get("standards") for t in topics),
   [t["id"] for t in topics if not t.get("standards")][:5])
ck("每条课标引用都带 quote", all(s.get("quote") for t in topics for s in t.get("standards") or []))
ck("confidence 三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                          for t in topics for s in t.get("standards") or []))
ck("curriculumRef 与首条课标一致",
   all((t.get("curriculumRef") or "") == (t.get("standards") or [{}])[0].get("id", "") for t in topics),
   [t["id"] for t in topics
    if (t.get("curriculumRef") or "") != (t.get("standards") or [{}])[0].get("id", "")][:5])

if all(os.path.exists(p) for p in TXT):
    src = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT))
    miss = [(t["id"], (t["standards"][0]["quote"] or "")[:14]) for t in topics
            if t.get("standards") and norm(t["standards"][0]["quote"]) not in src]
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
ck("课时点先修只挂课时点",
   all(all(T[p]["level"] == "lesson" for p in t.get("prerequisites") or []) for t in lessons),
   [t["id"] for t in lessons if any(T[p]["level"] == "unit" for p in t.get("prerequisites") or [])][:3])
ck("课时点都有 prereqUpper 且指向本主题单元点",
   all(t.get("prereqUpper") in T and T[t["prereqUpper"]]["level"] == "unit" for t in lessons),
   [t["id"] for t in lessons if t.get("prereqUpper") not in T][:3])

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

# 6 题库
if qs:
    per = Counter(q["topicId"] for q in qs)
    ck("每课时点恰好 8 题", all(per.get(t["id"], 0) == 8 for t in lessons),
       [(t["id"], per.get(t["id"], 0)) for t in lessons if per.get(t["id"], 0) != 8][:5])
    ck("每单元点恰好 5 题", all(per.get(t["id"], 0) == 5 for t in units),
       [(t["id"], per.get(t["id"], 0)) for t in units if per.get(t["id"], 0) != 5][:5])
    ck("题 id 唯一", len({q["id"] for q in qs}) == len(qs))
    ck("题目 topicId 都能对上", all(q["topicId"] in T for q in qs),
       [q["id"] for q in qs if q["topicId"] not in T][:3])
    ck("每点三档齐（点内 basic/standard/hard 都有）",
       all({q["difficulty"] for q in qs if q["topicId"] == t["id"]} >= {"basic", "standard", "hard"} for t in topics),
       [t["id"] for t in topics
        if {q["difficulty"] for q in qs if q["topicId"] == t["id"]} < {"basic", "standard", "hard"}][:5])
    ch = [q for q in qs if q.get("type") == "choice"]
    cnt = Counter(q["answer"] for q in ch)
    dist = {k: round(cnt.get(k, 0) / len(ch) * 100, 1) for k in "ABCD"}
    ck("选择题答案位各 ≥15%（只按 choice 统计）", all(v >= 15 for v in dist.values()), dist)
    types = Counter(q["type"] for q in qs)
    ratio = {k: round(types.get(k, 0) / len(qs) * 100, 1) for k in ("choice", "fill", "short-answer", "numeric")}
    ck("题型比例（choice 40–60 / fill ≥15 / short ≥10 / numeric ≥4）",
       ratio["choice"] >= 40 and ratio["fill"] >= 15 and ratio["short-answer"] >= 10 and ratio["numeric"] >= 4, ratio)
    ck("numeric 都带 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"),
       [q["id"] for q in qs if q.get("type") == "numeric" and not q.get("verify")][:3])
else:
    checks.append(("题库尚未合并（阶段 3 未开）", True, ""))

for name, ok, detail in checks:
    print(("✅" if ok else "❌"), name, ("" if ok else f"  [{detail}]"))
print(f"\n{sum(1 for _, ok, _ in checks if ok)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print("GEOGRAPHY-ZHONGTU DATA PASSED")
