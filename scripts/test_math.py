#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数学学科数据不变量测试（可单独跑，也可接进 CI）
用法: python3 scripts/test_math.py
退出码 0 = 全绿；1 = 有失败项
"""
import json, re, sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订).txt",
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/（3）普通高中数学课程标准日常修订版（2017年版2025年修订）.txt",
]

fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


topics = json.load(open(os.path.join(D, "math/topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, "math/dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(D, "math/questions.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}

# 1 规模与唯一性
ck("知识点 479 条", len(topics) == 479, len(topics))
ck("id 唯一", len(T) == len(topics))
ck("全部 subject=math", all(t.get("subject") == "math" for t in topics))
ck("诊断题 5 题/点（479×5=2395）", len(qs) == len(topics) * 5, f"{len(qs)} vs {len(topics)*5}")
ck("题 id 唯一", len({q["id"] for q in qs}) == len(qs))

# 2 册次覆盖 1..14
grades = {int(t["grade"]) for t in topics}
ck("年级覆盖 1–14", grades == set(range(1, 15)), sorted(grades))

# 3 课标
no_std = [t["id"] for t in topics if not t.get("standards")]
ck("带课标的比例 ≥ 99%", len(no_std) <= 3, no_std)
bad_ref = [(t["id"], s.get("id")) for t in topics for s in t.get("standards", [])
           if s.get("id") not in {e["id"] for e in idx["subjects"]["math"]["entries"]}]
ck("课标条目都能在索引里找到", not bad_ref, bad_ref[:3])
no_quote = [t["id"] for t in topics for s in t.get("standards", []) if not s.get("quote")]
ck("每条课标引用都带 quote", not no_quote, no_quote[:3])
ck("confidence 只用三档",
   all(s.get("confidence") in ("exact", "partial", "inferred")
       for t in topics for s in t.get("standards", [])))

# 4 quote 回表（有原文才查）
if all(os.path.exists(p) for p in TXT):
    src = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT))
    miss = [(t["id"], s["quote"][:16]) for t in topics for s in t.get("standards", [])
            if s.get("quote") and norm(s["quote"]) not in src]
    ck("quote 逐字回表命中 100%", not miss, miss[:3])
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
ck("deps 与 topics.prerequisites 双向镜像", not asym, asym[:3])

# 环检测
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
ck("根节点都有 root_reason", all(t.get("root_reason") for t in roots), len(roots))

# 7 题目可用性
by_topic = {}
by_topic_cnt = {}
for q in qs:
    by_topic.setdefault(q.get("topicId"), []).append(q)
    by_topic_cnt.setdefault(q.get("topicId"), []).append(q)
ck("每个知识点都有题", all(t in by_topic for t in T), len(T) - len(by_topic))
ck("难度只用 basic/standard/hard",
   all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs),
   sorted({q.get("difficulty") for q in qs}))
bad_choice = []
for q in qs:
    if q.get("type") == "choice":
        labels = [o.get("label") for o in (q.get("options") or [])]
        if len(labels) != 4 or q.get("answer") not in labels:
            bad_choice.append(q["id"])
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
ck("题干 ≥ 8 字", all(len(q.get("prompt", "")) >= 8 for q in qs),
   [q["id"] for q in qs if len(q.get("prompt", "")) < 8][:5])
ck("每题都有解析", all(len(q.get("explanation", "")) >= 4 for q in qs))
ck("numeric 题都有 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"))

# 7b 多题型与题库厚度
import collections, difflib

types_cnt = collections.Counter(q["type"] for q in qs)
ck("每点恰好 5 题", all(len(v) == 5 for v in by_topic_cnt.values()),
   [k for k, v in by_topic_cnt.items() if len(v) != 5][:5])
ck("题型四类齐备", set(types_cnt) == {"choice", "fill", "numeric", "short-answer"}, dict(types_cnt))
ck("每点至少 3 种题型", all(len({q["type"] for q in v}) >= 3 for v in by_topic_cnt.values()),
   [k for k, v in by_topic_cnt.items() if len({q["type"] for q in v}) < 3][:5])
ck("numeric 占比 ≥ 20%", types_cnt["numeric"] >= len(qs) * 0.2, f'{types_cnt["numeric"]}/{len(qs)}')
ck("fill 与 short-answer 各 ≥ 479", types_cnt["fill"] >= 479 and types_cnt["short-answer"] >= 479, dict(types_cnt))

bad_verify = []
for q in qs:
    if q.get("type") != "numeric":
        continue
    a, v = str(q.get("answer")), q.get("verify") or ""
    try:
        if abs(eval(v) - float(a)) > 1e-6:
            bad_verify.append(q["id"])
    except Exception:
        bad_verify.append(q["id"])
ck("numeric verify 可复算且等于 answer", not bad_verify, bad_verify[:5])

ck("选择题都带 choices 且与 options 同值",
   all(q.get("choices") == q.get("options") and len(q.get("choices") or []) == 4
       for q in qs if q.get("type") == "choice"),
   [q["id"] for q in qs if q.get("type") == "choice"
    and not (q.get("choices") == q.get("options") and len(q.get("choices") or []) == 4)][:5])
ck("非选择题 choices 为空数组", all((q.get("choices") or []) == [] for q in qs if q.get("type") != "choice"))
ck("难度字段三档内", all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs))
ck("选项文本互不相同", not [q["id"] for q in qs if q.get("type") == "choice"
                        and len({(o.get("text") or "").strip() for o in q.get("options") or []}) != 4])
ck("题干 ≥ 12 字", all(len(q.get("prompt", "")) >= 12 for q in qs),
   [q["id"] for q in qs if len(q.get("prompt", "")) < 12][:5])
ck("解析 ≥ 20 字", all(len(q.get("explanation", "")) >= 20 for q in qs),
   [q["id"] for q in qs if len(q.get("explanation", "")) < 20][:5])
ck("题干全域不重复", len({q.get("prompt") for q in qs}) == len(qs), len(qs) - len({q.get("prompt") for q in qs}))

near_dup = []


def _diff_chars(a, b):
    return sum(max(i2 - i1, j2 - j1)
               for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes() if tag != "equal")


for tid, v in by_topic_cnt.items():
    seen = []
    for q in v:
        p = re.sub(r"\s+", "", q.get("prompt") or "")
        for o in seen:
            r = difflib.SequenceMatcher(None, p, o).ratio()
            # 高相似且差异不足 6 字 ⇒ 同一道题换了个词；共用语境的题（如正方体背景）不算重复
            if r > 0.88 and _diff_chars(p, o) < 6:
                near_dup.append(f'{tid}:{q["id"]}')
        seen.append(p)
ck("同点题干不近似（高相似且差异<6字）", not near_dup, near_dup[:5])

ck("答案位置无偏置（choice 四 label 各 ≥15%）",
   all(v >= types_cnt["choice"] * 0.15 for v in
       collections.Counter(q["answer"] for q in qs if q.get("type") == "choice").values()),
   dict(collections.Counter(q["answer"] for q in qs if q.get("type") == "choice")))

# 8 核心字段
need = ["name", "domain", "grade", "semester", "chapter", "type", "description", "mastery_criteria"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics))
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print("MATH DATA PASSED")
