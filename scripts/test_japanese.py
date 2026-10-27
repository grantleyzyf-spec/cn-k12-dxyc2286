# -*- coding: utf-8 -*-
"""日语学科不变量自检（28 项）。用法: python3 scripts/test_japanese.py

课标 TXT 不存在时自动跳过「quote 逐字回表」（GitHub Actions 里没有本机课标快照）。
"""
import bisect
import json
import os
import re
import sys

SUBJECT = "japanese"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/（17）普通高中日语课程标准（2017年版2020年修订）.txt",
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
agg_t = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}
std_ids = {e["id"] for e in idx["subjects"][SUBJECT]["entries"]}

DOMAINS = {"语音", "词汇", "语法", "听力", "阅读", "写作", "文化"}
Q_TYPES = {"choice", "fill", "short-answer", "numeric"}
T_TYPES = {"conceptual", "procedural", "reasoning", "modeling", "application"}

# ---------- 结构 ----------
ck("id 唯一", len(T) == len(topics), f"{len(T)} vs {len(topics)}")
ck("全部 subject 一致", all(t.get("subject") == SUBJECT for t in topics))
ck("id 前缀统一 jpn_", all(re.match(r"^jpn_[hp]\d{3}$", t["id"]) for t in topics))
ck("诊断题与知识点数量匹配", len(qs) >= len(topics), f"{len(qs)} vs {len(topics)}")
ck("每题 topicId 可对", all(q.get("topicId") in T for q in qs),
   [q["id"] for q in qs if q.get("topicId") not in T][:5])
ck("题目 id 唯一", len({q["id"] for q in qs}) == len(qs))
ck("领域在 7 类内", all(t.get("domain") in DOMAINS for t in topics),
   sorted({t.get("domain") for t in topics} - DOMAINS))
ck("领域七类都有点", {t.get("domain") for t in topics} == DOMAINS,
   sorted(DOMAINS - {t.get("domain") for t in topics}))
ck("知识点类型合法", all(t.get("type") in T_TYPES for t in topics),
   sorted({t.get("type") for t in topics} - T_TYPES))

# ---------- 册次 ----------
ck("册次覆盖 10/11/12", {t.get("grade") for t in topics} == {10, 11, 12},
   sorted({t.get("grade") for t in topics}))
ck("semester 只用 上/下", all(t.get("semester") in ("上", "下") for t in topics),
   sorted({t.get("semester") for t in topics}))
ck("chapter 均非空且带册名", all(t.get("chapter") and ("必修" in t["chapter"] or "选修" in t["chapter"])
                              for t in topics))
ck("汇总文件含本学科全部点",
   {t["id"] for t in topics} <= {x["id"] for x in agg_t if x.get("subject") == SUBJECT})

# ---------- 课标 ----------
ck("课标 id 均可解析", not [1 for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids])
ck("每条课标引用都带 quote", not [1 for t in topics for s in t.get("standards", []) if not s.get("quote")])
ck("confidence 三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                          for t in topics for s in t.get("standards", [])))
ck("sourceLine 全为整数", all(isinstance(s.get("sourceLine"), int)
                          for t in topics for s in t.get("standards", [])))
ck("每个知识点至少 1 条课标", all(t.get("standards") for t in topics),
   [t["id"] for t in topics if not t.get("standards")][:5])

if all(os.path.exists(p) for p in TXT):
    raw = open(TXT[0], encoding="utf-8").read().split("\n")
    starts, acc = [], 0
    for i, line in enumerate(raw, 1):
        starts.append((acc, i))
        acc += len(norm(line))
    full = "".join(norm(line) for line in raw)
    offs = [s[0] for s in starts]

    def line_of(ch):
        return starts[max(bisect.bisect_right(offs, ch) - 1, 0)][1]

    miss, bad_line = [], []
    for t in topics:
        for s in t.get("standards", []):
            pos = full.find(norm(s.get("quote")))
            if pos < 0:
                miss.append((t["id"], s["id"], (s.get("quote") or "")[:16]))
            elif line_of(pos) != s.get("sourceLine"):
                bad_line.append((t["id"], s.get("sourceLine"), line_of(pos)))
    ck("quote 逐字回表 100%", not miss, miss[:3])
    ck("sourceLine 与课标首现行号一致", not bad_line, bad_line[:3])
else:
    checks.append(("quote 回表（缺课标 TXT，跳过）", True, None))
    checks.append(("sourceLine 校验（缺课标 TXT，跳过）", True, None))

# ---------- 先修图 ----------
pairs = [(e["from"], e["to"]) for e in deps]
ck("边无自环", all(a != b for a, b in pairs))
ck("边无重复", len(set(pairs)) == len(pairs))
ck("边两端存在", all(a in T and b in T for a, b in pairs))
ck("边类型 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps),
   sorted({e.get("type") for e in deps} - {"hard", "soft"}))
ck("prerequisites 全部有对应边", not [(p, t["id"]) for t in topics for p in t.get("prerequisites", [])
                                if (p, t["id"]) not in set(pairs)])
ck("deps 与 prerequisites 双向镜像",
   not [(a, b) for a, b in pairs if a not in T[b].get("prerequisites", [])])
ck("prerequisites 无自指/悬空", not [p for t in topics for p in t.get("prerequisites", [])
                                if p not in T or p == t["id"]])

color = {}


def dfs(u):
    color[u] = 1
    for b in (b for a, b in pairs if a == u):
        if color.get(b) == 1 or (color.get(b, 0) == 0 and dfs(b)):
            return True
    color[u] = 2
    return False


sys.setrecursionlimit(10000)
ck("先修图无环", not any(color.get(u, 0) == 0 and dfs(u) for u in T))
ck("根节点都有 root_reason", all(t.get("root_reason") for t in topics if not t.get("prerequisites")),
   [t["id"] for t in topics if not t.get("prerequisites") and not t.get("root_reason")])

# ---------- 题库 ----------
ck("每知识点都有题", all(any(q.get("topicId") == tid for q in qs) for tid in T))
ck("题型合法", all(q.get("type") in Q_TYPES for q in qs), sorted({q.get("type") for q in qs} - Q_TYPES))
ck("难度三档齐备", {q.get("difficulty") for q in qs} == {"basic", "standard", "hard"},
   sorted({q.get("difficulty") for q in qs}))
bad_choice = [q["id"] for q in qs if q.get("type") == "choice"
              and (len(q.get("options") or []) != 4
                   or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
dup_opt = [q["id"] for q in qs if len({o.get("text") for o in q.get("options") or []}) != len(q.get("options") or [])]
ck("选项文本互不相同（无重复干扰项）", not dup_opt, dup_opt[:5])
ck("题干 ≥12 字", all(len(q.get("prompt", "")) >= 12 for q in qs),
   [q["id"] for q in qs if len(q.get("prompt", "")) < 12][:5])
ck("prompt 与 question 同值", all(q.get("prompt") == q.get("question") for q in qs),
   [q["id"] for q in qs if q.get("prompt") != q.get("question")][:5])
ck("每题有解析", all(len(q.get("explanation", "")) >= 10 for q in qs),
   [q["id"] for q in qs if len(q.get("explanation", "")) < 10][:5])
ck("题干互不重复", len({q.get("prompt") for q in qs}) == len(qs))
ck("numeric 有 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"))

# ---------- 字段 ----------
need = ["name", "domain", "grade", "semester", "chapter", "type", "description", "mastery_criteria"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics),
   [t["id"] for t in topics if not all(t.get(k) for k in need)][:5])
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))
ck("课标引用条目数 ≥ 知识点数", sum(len(t.get("standards", [])) for t in topics) >= len(topics))

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print(SUBJECT.upper() + " DATA PASSED")
