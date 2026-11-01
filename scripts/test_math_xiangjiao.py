#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数学（湘教版, math-xiangjiao）学科不变量自检。用法：python3 scripts/test_math_xiangjiao.py

覆盖：册次与规模、章名口径、id 命名、题量、题型难度、选项、边与根节点、课标逐字回表。
课标 TXT 在 CI 环境通常不存在，自动跳过回表项。
"""
import json, os, re, sys
from collections import Counter

SUBJECT = "math-xiangjiao"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
    "3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订)（docx转换）.txt",
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
    "3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订).txt",
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/"
    "（3）普通高中数学课程标准日常修订版（2017年版2025年修订）.txt",
]
MD_BAD = re.compile(r"\*\*|##|`|\\$|\\frac|\|")
BOOKS = ["湘教版七年级上册", "湘教版七年级下册", "湘教版八年级上册",
         "湘教版八年级下册", "湘教版九年级上册", "湘教版必修第一册",
         "湘教版必修第二册", "湘教版选择性必修第一册"]

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
by_topic = Counter(q["topicId"] for q in qs)

ck("id 唯一", len(T) == len(topics))
ck("全部 subject=math-xiangjiao", all(t.get("subject") == SUBJECT for t in topics))
ck("规模 = 198 点", len(topics) == 198, len(topics))
ck("id 命名 mxj_[ph]NNN(N)", all(re.fullmatch(r"mxj_[ph]\d{3,4}", t["id"]) for t in topics),
   [t["id"] for t in topics if not re.fullmatch(r"mxj_[ph]\d{3,4}", t["id"])][:3])
ck("年级 7–11", {t.get("grade") for t in topics} == {7, 8, 9, 10, 11},
   sorted({t.get("grade") for t in topics}))
ck("学期 上/下", all(t.get("semester") in ("上", "下") for t in topics))
def book_of(t):
    m = re.match(r"^(湘教版[^ ]+)", t.get("chapter", ""))
    return m.group(1) if m else ""


ck("8 册齐全", {book_of(t) for t in topics} == set(BOOKS),
   sorted({book_of(t) for t in topics} - set(BOOKS)))
ck("章名「湘教版… 第N章 名」",
   all(re.match(r"^湘教版[^ ]+ 第\d+章 .+", t["chapter"]) for t in topics),
   [t["chapter"] for t in topics if not re.match(r"^湘教版[^ ]+ 第\d+章 .+", t["chapter"])][:3])
ck("无「十X年级」字样", not [t["id"] for t in topics if re.search(r"十[一二三四五六]年级", t["chapter"])])
ck("unit/lesson 计数 37/161",
   (sum(1 for t in topics if re.match(r"mxj_[ph]\d{3}$", t["id"])),
    sum(1 for t in topics if re.match(r"mxj_[ph]\d{4}$", t["id"]))) == (37, 161),
   (sum(1 for t in topics if re.match(r"mxj_[ph]\d{3}$", t["id"])),
    sum(1 for t in topics if re.match(r"mxj_[ph]\d{4}$", t["id"]))))
ck("description ≥12 字", all(len(t.get("description", "")) >= 12 for t in topics),
   [t["id"] for t in topics if len(t.get("description", "")) < 12][:3])
ck("mastery_criteria 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))
ck("诊断入口题有问有答",
   all((t.get("diagnostic_question") or {}).get("question") and
       (t.get("diagnostic_question") or {}).get("answer") for t in topics))
ck("每点有题", all(by_topic[t["id"]] >= 5 for t in topics),
   [(t["id"], by_topic[t["id"]]) for t in topics if by_topic[t["id"]] < 5][:3])
ck("题量 1473", len(qs) == 1473, len(qs))
ck("题目 subject 一致", all(q.get("subject") == SUBJECT for q in qs))
ck("题型枚举", {q.get("type") for q in qs} <= {"choice", "fill", "short-answer", "numeric"},
   sorted({q.get("type") for q in qs}))
ck("难度三档", {q.get("difficulty") for q in qs} <= {"basic", "standard", "hard"},
   sorted({q.get("difficulty") for q in qs}))
ck("每点难度三档齐备",
   all({q.get("difficulty") for q in qs if q["topicId"] == t["id"]} >= {"basic", "standard", "hard"}
       for t in topics),
   [t["id"] for t in topics
    if {q.get("difficulty") for q in qs if q["topicId"] == t["id"]} < {"basic", "standard", "hard"}][:3])
bad_choice = [q["id"] for q in qs if q.get("type") == "choice"
              and (len(q.get("options") or []) != 4
                   or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:3])
ck("题干 ≥8 字", all(len(q.get("prompt", "")) >= 8 for q in qs),
   [q["id"] for q in qs if len(q.get("prompt", "")) < 8][:3])
ck("解析 ≥15 字", all(len(q.get("explanation", "")) >= 15 for q in qs),
   [q["id"] for q in qs if len(q.get("explanation", "")) < 15][:3])
ck("numeric 带 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"))
ck("答案位不集中于单一字母",
   all(max(Counter(q["answer"] for q in qs
                   if q["topicId"] == t["id"] and q.get("type") == "choice").values() or [0]) <= 3
       for t in topics))

pairs = [(e["from"], e["to"]) for e in deps]
parent = {}
for a, b in pairs:
    parent.setdefault(b, set()).add(a)
ck("边无自环", all(a != b for a, b in pairs))
ck("边无重复", len(set(pairs)) == len(pairs))
ck("边两端存在", all(a in T and b in T for a, b in pairs))
ck("边类型 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps))
ck("软边存在（册际衔接）", sum(1 for e in deps if e.get("type") == "soft") >= 7,
   sum(1 for e in deps if e.get("type") == "soft"))
ck("deps 与 prerequisites 双向镜像",
   not [(a, b) for b, ps in parent.items() for a in ps if a not in T[b].get("prerequisites", [])])
color = {}


def dfs(u):
    color[u] = 1
    for b in (y for x, y in pairs if x == u):
        if color.get(b) == 1 or (color.get(b, 0) == 0 and dfs(b)):
            return True
    color[u] = 2
    return False


ck("先修图无环", not any(color.get(u, 0) == 0 and dfs(u) for u in T))
ck("根节点都有 root_reason",
   all(t.get("root_reason") for t in topics if not t.get("prerequisites")))
ck("课标 id 均可解析", not [1 for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids])
ck("每条课标引用带 quote", not [1 for t in topics for s in t.get("standards", []) if not s.get("quote")])
ck("课标引用密度 ≥95%", sum(1 for t in topics if t.get("standards")) >= int(0.95 * len(topics)),
   sum(1 for t in topics if t.get("standards")))

present = [p for p in TXT if os.path.isfile(p)]
if present:
    src = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in present))
    miss = [(t["id"], s["quote"][:16]) for t in topics for s in t.get("standards", [])
            if s.get("quote") and norm(s["quote"]) not in src]
    ck("课标 quote 逐字回表 100%", not miss, miss[:3])
else:
    checks.append(("课标 quote 回表（缺 TXT，跳过）", True, None))

ck("正文无 Markdown 符号", not [q["id"] for q in qs if MD_BAD.search(q.get("prompt", "") + q.get("explanation", ""))],
   [q["id"] for q in qs if MD_BAD.search(q.get("prompt", "") + q.get("explanation", ""))][:3])

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print("MATH-XIANGJIAO DATA PASSED")
