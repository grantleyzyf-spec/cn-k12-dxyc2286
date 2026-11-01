#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""北京版数学（math-bj）不变量自检。用法: python3 scripts/test_math-bj.py

课标 TXT 不存在时（CI 环境）自动跳过回表。
"""
import json
import os
import re
import sys

SUBJECT = "math-bj"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = [
    os.path.expanduser(
        "~/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
        "3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订).txt"),
]

fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


topics = json.load(open(os.path.join(D, SUBJECT, "topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, SUBJECT, "dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(D, SUBJECT, "questions.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}
std_ids = {e["id"] for e in idx["subjects"][SUBJECT]["entries"]}
BOOKS = ["一上", "一下", "二上", "二下", "三上", "三下", "四上", "五上", "六上",
         "七上", "七下", "八上", "八下", "九上"]


def book_of(t):
    m = re.match(r"([一二三四五六七八九])年级([上下])册", t["chapter"])
    return f"{m.group(1)}{m.group(2)}" if m else None


ck("id 唯一", len(T) == len(topics))
ck("id 前缀合法", all(re.fullmatch(r"mbj_p\d{3}", t["id"]) for t in topics))
ck("subject 一致", all(t.get("subject") == SUBJECT for t in topics))
ck("层级字段只用 unit/lesson", all(t.get("level") in ("unit", "lesson") for t in topics))
ck("年级范围 1–9", all(1 <= t["grade"] <= 9 for t in topics))
ck("册次覆盖 14 册", {book_of(t) for t in topics} == set(BOOKS),
   sorted(set(BOOKS) - {book_of(t) for t in topics}))
ck("每册有点", all(sum(1 for t in topics if book_of(t) == b) >= 20 for b in BOOKS
                  if b not in ("八下", "九上", "七上", "七下")))
ck("单元点都有下辖课时点",
   all(any(e["from"] == t["id"] for e in deps) for t in topics if t["level"] == "unit"))
ck("题:点 ≥1", len(qs) >= len(topics), f"{len(qs)} vs {len(topics)}")
ck("每点都有题", all(any(q.get("topicId") == tid for q in qs) for tid in T))
ck("题量：单元 5 / 课时 8",
   all(sum(1 for q in qs if q.get("topicId") == tid) == (5 if t["level"] == "unit" else 8)
       for tid, t in T.items()),
   [(tid, sum(1 for q in qs if q.get("topicId") == tid)) for tid, t in T.items()
    if sum(1 for q in qs if q.get("topicId") == tid) != (5 if t["level"] == "unit" else 8)][:3])
ck("题 topicId 均可对", all(q.get("topicId") in T for q in qs))
ck("题目 id 唯一", len({q["id"] for q in qs}) == len(qs))
ck("题目 subject 一致", all(q.get("subject") == SUBJECT for q in qs))
ck("难度三档", all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs),
   sorted({q.get("difficulty") for q in qs}))
ck("每点三档齐",
   all(len({q.get("difficulty") for q in qs if q.get("topicId") == tid}) == 3 for tid in T))
ck("题干 ≥12 字", all(len(q.get("prompt") or "") >= 12 for q in qs))
ck("question 与 prompt 一致", all(q.get("question") == q.get("prompt") for q in qs))
ck("每题有解析 ≥20 字", all(len(q.get("explanation") or "") >= 20 for q in qs))
bad_choice = [q["id"] for q in qs if q.get("type") == "choice"
              and (len(q.get("options") or []) != 4
                   or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
bad_num = []
for q in qs:
    if q.get("type") == "numeric":
        v = q.get("verify")
        if not v:
            bad_num.append((q["id"], "no verify"))
            continue
        try:
            val = eval(v, {"__builtins__": {}}, {})
            if abs(float(val) - float(str(q["answer"]).strip())) > 1e-6:
                bad_num.append((q["id"], f"{v}->{val} != {q['answer']}"))
        except Exception as e:
            bad_num.append((q["id"], f"verify err {e}"))
ck("numeric verify 可复算且等于答案", not bad_num, bad_num[:5])
ck("课标 id 均可解析", not [1 for t in topics for s in t.get("standards") or []
                          if s.get("id") not in std_ids])
ck("每条课标引用都带 quote", not [1 for t in topics for s in t.get("standards") or []
                               if not s.get("quote")])
ck("confidence 三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                         for t in topics for s in t.get("standards") or []))

if all(os.path.exists(p) for p in TXT):
    src = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT))
    miss = [(t["id"], s["quote"][:16]) for t in topics for s in t.get("standards") or []
            if s.get("quote") and norm(s["quote"]) not in src]
    ck("quote 逐字回表 100%", not miss, miss[:3])
else:
    checks.append(("quote 回表（缺 TXT，跳过）", True, None))

pairs = [(e["from"], e["to"]) for e in deps]
ck("边无自环", all(a != b for a, b in pairs))
ck("边无重复", len(set(pairs)) == len(pairs))
ck("边两端存在", all(a in T and b in T for a, b in pairs))
ck("边类型 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps))
parent = {}
for a, b in pairs:
    parent.setdefault(b, set()).add(a)
ck("deps 与 prerequisites 双向镜像",
   not [(a, b) for b, ps in parent.items() for a in ps if a not in T[b].get("prerequisites", [])])


def _deps_by_from(frm):
    return [b for a, b in pairs if a == frm]


color = {}
sys.setrecursionlimit(10000)


def dfs(u):
    color[u] = 1
    for b in _deps_by_from(u):
        if color.get(b) == 1 or (color.get(b, 0) == 0 and dfs(b)):
            return True
    color[u] = 2
    return False


ck("先修图无环", not any(color.get(u, 0) == 0 and dfs(u) for u in T))
ck("根节点都有 root_reason",
   all(t.get("root_reason") for t in topics if not t.get("prerequisites")))
need = ["name", "domain", "grade", "semester", "chapter", "type", "description",
        "mastery_criteria", "diagnostic_question"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics))
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))
ck("掌握标准每条 ≤60 字",
   all(len(x) <= 60 for t in topics for x in t.get("mastery_criteria") or []))
ck("错因 2–3 条", all(2 <= len(t.get("misconceptions") or []) <= 3 for t in topics))
ck("课标挂标率 ≥60%",
   sum(1 for t in topics if t.get("standards")) / max(1, len(topics)) >= 0.6,
   f"{sum(1 for t in topics if t.get('standards'))}/{len(topics)}")

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print(SUBJECT.upper() + " DATA PASSED")
