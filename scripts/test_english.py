#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""英语学科数据不变量测试（可单独跑，也可接进 CI）
用法: python3 scripts/test_english.py
退出码 0 = 全绿；1 = 有失败项
课标原文 TXT 不存在时（CI 环境）自动跳过「quote 回表」一项，仍按 25 项计数。
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/4.《义务教育英语课程标准·日常修订版》(2022年版2025年修订).txt",
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/（4）普通高中英语课程标准日常修订版（2017年版2025年修订）.txt",
]

fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


topics = json.load(open(os.path.join(D, "english/topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, "english/dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(D, "english/questions.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}
ENTRY_IDS = {e["id"] for e in idx["subjects"]["english"]["entries"]}

# 1 规模与唯一性
ck("知识点 204 条", len(topics) == 204, len(topics))
ck("题目 204 道", len(qs) == 204, len(qs))
ck("先修边 209 条", len(deps) == 209, len(deps))
ck("id 唯一", len(T) == len(topics))
ck("全部 subject=english", all(t.get("subject") == "english" for t in topics))
ck("诊断题与知识点 1:1", len(qs) == len(topics), f"{len(qs)} vs {len(topics)}")

# 2 册次覆盖（英语：三年级起到高中选修，grade 3–12）
grades = {int(t["grade"]) for t in topics}
ck("年级覆盖 3–12", grades == set(range(3, 13)), sorted(grades))

# 3 课标
no_std = [t["id"] for t in topics if not t.get("standards")]
ck("全部知识点都挂课标", not no_std, no_std[:5])
bad_ref = [(t["id"], s.get("id")) for t in topics for s in t.get("standards", [])
           if s.get("id") not in ENTRY_IDS]
ck("课标条目都能在索引里找到", not bad_ref, bad_ref[:3])
no_quote = [t["id"] for t in topics for s in t.get("standards", []) if not s.get("quote")]
ck("每条课标引用都带 quote", not no_quote, no_quote[:3])
ck("confidence 只用三档",
   all(s.get("confidence") in ("exact", "partial", "inferred")
       for t in topics for s in t.get("standards", [])))

# 4 quote 回表（有原文才查，CI 里没有 TXT 则跳过）
if all(os.path.exists(p) for p in TXT):
    src = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT))
    miss = [(t["id"], s["quote"][:16]) for t in topics for s in t.get("standards", [])
            if s.get("quote") and norm(s["quote"]) not in src]
    ck("quote 逐字回表命中 100%", not miss, miss[:3])
else:
    checks.append(("quote 回表（缺课标 TXT，跳过）", True, ""))

# 5 先修边
pairs = [(e["from"], e["to"]) for e in deps]
ck("无自环且无重复边", all(a != b for a, b in pairs) and len(set(pairs)) == len(pairs))
ck("两端都存在", all(a in T and b in T for a, b in pairs),
   [(a, b) for a, b in pairs if a not in T or b not in T][:3])
ck("边类型只用 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps),
   sorted({e.get("type") for e in deps}))

parent = {}
for a, b in pairs:
    parent.setdefault(b, set()).add(a)
asym = [(a, b) for b, ps in parent.items() for a in ps if a not in T[b].get("prerequisites", [])]
ck("deps 与 topics.prerequisites 双向镜像", not asym, asym[:3])

color = {}


def dfs(u):
    color[u] = 1
    for b in (b for a, b in pairs if a == u):
        if color.get(b) == 1:
            return True
        if color.get(b, 0) == 0 and dfs(b):
            return True
    color[u] = 2
    return False


ck("先修图无环", not any(color.get(u, 0) == 0 and dfs(u) for u in T))

# 6 根节点
roots = [t for t in topics if not t.get("prerequisites")]
ck("根节点都有 root_reason", all(len(t.get("root_reason") or "") >= 10 for t in roots), len(roots))

# 7 题目可用性
by_topic = {}
for q in qs:
    by_topic.setdefault(q.get("topicId"), []).append(q)
ck("每个知识点都有题", all(t in by_topic for t in T), len(T) - len(by_topic))
diffs = {q.get("difficulty") for q in qs}
ck("难度只用 basic/standard/hard 且三档齐备", diffs == {"basic", "standard", "hard"}, sorted(map(str, diffs)))
bad_choice = []
for q in qs:
    if q.get("type") == "choice":
        labels = [o.get("label") for o in (q.get("options") or [])]
        if len(labels) != 4 or q.get("answer") not in labels:
            bad_choice.append(q["id"])
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
ck("题干 ≥ 8 字", all(len(q.get("prompt", "")) >= 8 for q in qs),
   [q["id"] for q in qs if len(q.get("prompt", "")) < 8][:5])
ck("每题都有解析（≥20 字）", all(len(q.get("explanation", "")) >= 20 for q in qs),
   [q["id"] for q in qs if len(q.get("explanation", "")) < 20][:5])

# 8 核心字段
need = ["name", "domain", "grade", "semester", "chapter", "type", "description", "mastery_criteria"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics),
   [t["id"] for t in topics if not all(t.get(k) for k in need)][:3])
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics),
   [t["id"] for t in topics if not 1 <= len(t.get("mastery_criteria") or []) <= 3][:3])

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print("ENGLISH DATA PASSED")
