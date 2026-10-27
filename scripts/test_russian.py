# -*- coding: utf-8 -*-
"""俄语（russian）学科不变量测试：python3 scripts/test_russian.py

34 项不变量。课标 TXT 不存在时（CI 环境）自动跳过回表两项，不影响其余检查。
课标源为本仓库 OCR 重建的扫描件文本（原件无文字层），见
scripts/ocr_russian_standard.py 与 docs/russian.md「课标回表」。
"""
import json
import os
import re
import sys

SUBJECT = "russian"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
    "《义务教育俄语课程标准》(2022年版) 扫描件OCR.txt",
]
PUNCT = "，。；：、！？（）()“”\"'‘’《》〈〉…—－-.,;:!?·"

fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


def loose(s):
    return "".join(ch for ch in norm(s) if ch not in PUNCT)


topics = json.load(open(os.path.join(D, SUBJECT, "topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, SUBJECT, "dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(D, SUBJECT, "questions.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}
std_ids = {e["id"] for e in idx["subjects"][SUBJECT]["entries"]}

# ---- 基础契约（与数学/语文同口径）----
ck("id 唯一", len(T) == len(topics))
ck("全部 subject 一致", all(t.get("subject") == SUBJECT for t in topics))
ck("诊断题与知识点数量匹配", len(qs) >= len(topics), f"{len(qs)} vs {len(topics)}")
ck("课标 id 均可解析", not [1 for t in topics for s in t.get("standards", [])
                            if s.get("id") not in std_ids])
ck("每条课标引用都带 quote", not [1 for t in topics for s in t.get("standards", [])
                                  if not s.get("quote")])
ck("confidence 三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                          for t in topics for s in t.get("standards", [])))

# ---- 课标回表（去标点宽松必红；严格仅作报告）----
if all(os.path.exists(p) for p in TXT):
    src_raw = "".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT)
    src_loose = loose(src_raw)
    src_strict = norm(src_raw)
    refs = [(t["id"], s["id"], s["quote"]) for t in topics for s in t.get("standards", [])
            if s.get("quote")]
    miss_loose = [(tid, sid, q[:18]) for tid, sid, q in refs if loose(q) not in src_loose]
    ck("quote 逐字回表 100%（去标点强校验）", not miss_loose, miss_loose[:3])
    strict_hit = sum(1 for _, _, q in refs if norm(q) in src_strict)
    checks.append((f"quote 严格回表（仅去空白）{strict_hit}/{len(refs)}"
                   " — 差额为扫描件 OCR 标点噪声，已逐条去标点复核", True, None))
    nlines = src_raw.count("\n") + 1
    ck("sourceLine 落在课标文本行范围内",
       all(isinstance(s.get("sourceLine"), int) and 1 <= s["sourceLine"] <= nlines
           for t in topics for s in t.get("standards", [])))
    line_of = {}
    bad_line = []
    for t in topics:
        for s in t.get("standards", []):
            k = norm(s.get("quote"))
            if k in line_of and line_of[k] != s.get("sourceLine"):
                bad_line.append((t["id"], s.get("sourceLine"), line_of[k]))
            line_of[k] = s.get("sourceLine")
    ck("同一引文指向同一行号", not bad_line, bad_line[:3])
else:
    checks.append(("quote 回表（缺课标 TXT，跳过）", True, None))
    checks.append(("sourceLine 范围（缺课标 TXT，跳过）", True, None))
    checks.append(("同一引文同一行号（缺课标 TXT，跳过）", True, None))

# ---- 先修图 ----
pairs = [(e["from"], e["to"]) for e in deps]
ck("边无自环", all(a != b for a, b in pairs))
ck("边无重复", len(set(pairs)) == len(pairs))
ck("边两端存在", all(a in T and b in T for a, b in pairs))
ck("边类型 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps))
parent = {}
for a, b in pairs:
    parent.setdefault(b, set()).add(a)
ck("deps 与 prerequisites 双向镜像",
   not [(a, b) for b, ps in parent.items() for a in ps
        if a not in T[b].get("prerequisites", [])])
ck("prerequisites 指向存在节点",
   not [p for t in topics for p in t.get("prerequisites", []) if p not in T])

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
   all(t.get("root_reason") for t in topics if not t.get("prerequisites")))
ck("根节点说明指向课内起点",
   all(re.search(r"起始|入门|起点|零起点|无.*先修", t["root_reason"])
       for t in topics if not t.get("prerequisites")),
   [t["id"] for t in topics if not t.get("prerequisites")
    and not re.search(r"起始|入门|起点|零起点|无.*先修", t["root_reason"])])

# ---- 题库 ----
ck("每知识点都有题", all(any(q.get("topicId") == tid for q in qs) for tid in T))
ck("题目 topicId 均可解析", all(q.get("topicId") in T for q in qs))
ck("难度枚举合规", all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs),
   sorted({q.get("difficulty") for q in qs}))
ck("三档难度均出现", {q.get("difficulty") for q in qs} == {"basic", "standard", "hard"},
   sorted({q.get("difficulty") for q in qs}))
bad_choice = [q["id"] for q in qs if q.get("type") == "choice"
              and (len(q.get("options") or []) != 4
                   or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
ans_dist = {}
for q in qs:
    if q.get("type") == "choice":
        ans_dist[q["answer"]] = ans_dist.get(q["answer"], 0) + 1
n_choice = sum(ans_dist.values()) or 1
ck("选择题答案分布均衡（单字母占比 ≤35%）",
   all(v / n_choice <= 0.35 for v in ans_dist.values()), ans_dist)
ck("选项文本非空", all(all((o.get("text") or "").strip() for o in (q.get("options") or []))
                  for q in qs if q.get("type") == "choice"))
ck("判断题/填空题答案非空", all((q.get("answer") or "").strip() for q in qs))
ck("题干 ≥12 字", all(len(q.get("prompt", "")) >= 12 for q in qs),
   [q["id"] for q in qs if len(q.get("prompt", "")) < 12][:5])
ck("每题有解析", all(len(q.get("explanation", "")) >= 4 for q in qs))
ck("numeric 有 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"))

# ---- 节点质量 ----
need = ["name", "domain", "grade", "semester", "chapter", "type", "description",
        "mastery_criteria"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics))
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))
ck("规模下限 90 知识点", len(topics) >= 90, len(topics))
ck("grade 取值 7–9", all(isinstance(t.get("grade"), int) and 7 <= t["grade"] <= 9
                         for t in topics),
   sorted({t.get("grade") for t in topics}))
ck("semester 仅 上/下", all(t.get("semester") in ("上", "下") for t in topics))
ck("chapter 含册名（年级册）", all(re.search(r"[七八九]年级[上下]册", t.get("chapter", ""))
                                   for t in topics),
   [t["id"] for t in topics if not re.search(r"[七八九]年级[上下]册", t.get("chapter", ""))][:3])
ck("domain 属俄语课标领域", all(t.get("domain") in ("语音", "词汇", "语法", "语篇", "语用")
                                 for t in topics),
   sorted({t.get("domain") for t in topics}))
ck("tags 非空", all(t.get("tags") for t in topics))
ck("verified 字段为布尔", all(isinstance(t.get("verified"), bool) for t in topics))
ck("诊断题问题与答案均非空",
   all((t.get("diagnostic_question") or {}).get("question", "").strip()
       and (t.get("diagnostic_question") or {}).get("answer", "").strip() for t in topics),
   [t["id"] for t in topics
    if not ((t.get("diagnostic_question") or {}).get("question", "").strip()
            and (t.get("diagnostic_question") or {}).get("answer", "").strip())][:5])

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print(SUBJECT.upper() + " DATA PASSED")
