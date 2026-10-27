# -*- coding: utf-8 -*-
"""德语（german）学科不变量自检 —— 进 CI。

覆盖：规模／唯一性／册次（课程类型）／课标可解析与逐字回表／confidence 枚举／
先修边（无环、无重、无自环、双向镜像）／根节点依据／题库可用性（每题一点、
4 选项、答案在选项内、题干长度、解析、难度三档）／掌握标准／字段口径。

课标 TXT 不存在时自动跳过回表（CI 环境没有教材库），其余断言照跑。
用法：python3 scripts/test_german.py
"""
import json
import os
import re
import sys
from collections import Counter

SUBJECT = "german"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/"
    "（20）普通高中德语课程标准（2017年版2020年修订）.txt",
]

# 德语只有《普通高中德语课程标准（2017年版2020年修订）》一版；
# 义务教育阶段外语课标只有英语/日语/俄语，德语 7—9 年级无课标对应。
BOOKS = {"必修", "选择性必修", "选修"}

fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail is not None else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


topics = json.load(open(os.path.join(D, SUBJECT, "topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, SUBJECT, "dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(D, SUBJECT, "questions.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}
std_ids = {e["id"] for e in idx["subjects"][SUBJECT]["entries"]}
QbyTopic = {}
for q in qs:
    QbyTopic.setdefault(q.get("topicId"), []).append(q)

# ---------------------------------------------------------------- 结构与规模
ck("规模非空（知识点≥100）", len(topics) >= 100, len(topics))
ck("id 唯一", len(T) == len(topics))
ck("全部 subject 一致", all(t.get("subject") == SUBJECT for t in topics))
ck("grade 全在 10–12（德语只有高中课标）", all(10 <= int(t.get("grade") or 0) <= 12 for t in topics),
   sorted({t.get("grade") for t in topics}))
need = ["name", "domain", "grade", "semester", "chapter", "type", "description",
        "mastery_criteria", "diagnostic_question", "standards"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics))
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics),
   [t["id"] for t in topics if not 1 <= len(t.get("mastery_criteria") or []) <= 3][:3])
ck("tags 非空且 ≤3", all(1 <= len(t.get("tags") or []) <= 3 for t in topics))
ck("description ≥12 字", all(len(t.get("description") or "") >= 12 for t in topics),
   [t["id"] for t in topics if len(t.get("description") or "") < 12][:3])

# ---------------------------------------------------------------- 册次口径
ck("chapter 无「未分章」占位", not [t["id"] for t in topics if "未分章" in (t.get("chapter") or "")])
bad_book = [t["id"] for t in topics if (t.get("chapter") or "").split(" ")[0] not in BOOKS]
ck("册名取自课标课程类型（必修/选择性必修/选修）", not bad_book, bad_book[:3])
ck("三类课程都有知识点",
   {(t.get("chapter") or "").split(" ")[0] for t in topics} == BOOKS,
   sorted({(t.get("chapter") or "").split(" ")[0] for t in topics}))
ck("semester 仅 上/下", all(t.get("semester") in ("上", "下") for t in topics))
ck("知识点类型枚举合规",
   all(t.get("type") in ("conceptual", "procedural", "reasoning", "modeling", "application")
       for t in topics), Counter(t.get("type") for t in topics).most_common())

# ---------------------------------------------------------------- 课标
ck("课标 id 均可解析", not [1 for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids])
ck("课标 id 前缀为 dyu-2017", all(s["id"].startswith("dyu-2017:")
                               for t in topics for s in t.get("standards", [])))
ck("每条课标引用都带 quote", not [1 for t in topics for s in t.get("standards", []) if not s.get("quote")])
ck("quote 长度 12–40 字", all(12 <= len(norm(s.get("quote"))) <= 40
                             for t in topics for s in t.get("standards", [])),
   [(t["id"], len(norm(s.get("quote")))) for t in topics for s in t.get("standards", [])
    if not 12 <= len(norm(s.get("quote"))) <= 40][:3])
ck("confidence 三档",
   all(s.get("confidence") in ("exact", "partial", "inferred")
       for t in topics for s in t.get("standards", [])),
   Counter(s.get("confidence") for t in topics for s in t.get("standards", [])).most_common())
ck("sourceLine 为整数", all(isinstance(s.get("sourceLine"), int)
                           for t in topics for s in t.get("standards", []) if "sourceLine" in s))

if all(os.path.exists(p) for p in TXT):
    src = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT))
    miss = [(t["id"], s["quote"][:16]) for t in topics for s in t.get("standards", [])
            if s.get("quote") and norm(s["quote"]) not in src]
    ck("quote 逐字回表 100%", not miss, miss[:3])
else:
    checks.append(("quote 回表（缺课标 TXT，跳过）", True, None))

# ---------------------------------------------------------------- 先修边
pairs = [(e["from"], e["to"]) for e in deps]
ck("边无自环", all(a != b for a, b in pairs))
ck("边无重复", len(set(pairs)) == len(pairs))
ck("边两端存在", all(a in T and b in T for a, b in pairs))
ck("边类型 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps))
ck("边数与先修关系数一致（无孤立边）", len(deps) > 0)
parent = {}
for a, b in pairs:
    parent.setdefault(b, set()).add(a)
ck("deps 与 prerequisites 双向镜像",
   not [(b, a) for b, ps in parent.items() for a in ps if a not in T[b].get("prerequisites", [])])
ck("topics.prerequisites 无 deps 之外的悬空先修",
   not [(t["id"], p) for t in topics for p in t.get("prerequisites", [])
        if (p, t["id"]) not in set(pairs)])

color = {}


def dfs(u):
    color[u] = 1
    for b in (b for a, b in pairs if a == u):
        if color.get(b) == 1 or (color.get(b, 0) == 0 and dfs(b)):
            return True
    color[u] = 2
    return False


ck("先修图无环", not any(color.get(u, 0) == 0 and dfs(u) for u in T))
ck("根节点都有 root_reason",
   all(t.get("root_reason") for t in topics if not t.get("prerequisites")),
   [t["id"] for t in topics if not t.get("prerequisites") and not t.get("root_reason")][:3])
ck("非根节点不残留 root_reason",
   not [t["id"] for t in topics if t.get("prerequisites") and t.get("root_reason")])

# ---------------------------------------------------------------- 题库
ck("诊断题与知识点数量匹配", len(qs) >= len(topics), "%d vs %d" % (len(qs), len(topics)))
ck("每知识点都有题", all(tid in QbyTopic for tid in T))
ck("每知识点恰好 1 题", all(len(v) == 1 for v in QbyTopic.values()),
   [k for k, v in QbyTopic.items() if len(v) != 1][:3])
ck("题目 topicId 均可对", all(q.get("topicId") in T for q in qs))
ck("难度枚举合规", all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs),
   Counter(q.get("difficulty") for q in qs).most_common())
ck("难度三档都有", {q.get("difficulty") for q in qs} == {"basic", "standard", "hard"})
ck("题型枚举合规", all(q.get("type") in ("choice", "fill", "short-answer", "numeric") for q in qs),
   Counter(q.get("type") for q in qs).most_common())
bad_choice = [q["id"] for q in qs if q.get("type") == "choice"
              and (len(q.get("options") or []) != 4
                   or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
dup_opt = [q["id"] for q in qs if q.get("type") == "choice"
           and len({(o.get("text") or "").strip() for o in q["options"]}) != len(q["options"])]
ck("选项文本互不相同", not dup_opt, dup_opt[:3])
ck("题干 ≥12 字", all(len(q.get("prompt", "")) >= 12 for q in qs),
   [(q["id"], len(q["prompt"])) for q in qs if len(q.get("prompt", "")) < 12][:3])
ck("question 别名字段与 prompt 同值", all(q.get("question", q["prompt"]) == q["prompt"] for q in qs))
ck("全库题干无重复", len({q["prompt"] for q in qs}) == len(qs),
   [p for p, c in Counter(q["prompt"] for q in qs).items() if c > 1][:3])
ck("每题有解析（≥10 字）", all(len(q.get("explanation", "")) >= 10 for q in qs),
   [q["id"] for q in qs if len(q.get("explanation", "")) < 10][:3])
ck("numeric 有 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"))
ck("diagnostic_question 与题库同源",
   all(t.get("diagnostic_question", {}).get("question") == QbyTopic[t["id"]][0]["prompt"]
       for t in topics if t["id"] in QbyTopic),
   [t["id"] for t in topics if t["id"] in QbyTopic
    and t.get("diagnostic_question", {}).get("question") != QbyTopic[t["id"]][0]["prompt"]][:3])

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail is not None and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print(SUBJECT.upper() + " DATA PASSED")
