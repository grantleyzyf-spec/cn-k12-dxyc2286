#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数学（北师大版, math-bsd）学科不变量自检。用法：python3 scripts/test_math_bsd.py

课标回表用 docx 转换的干净原文（不是 OCR 版）；CI 环境缺 TXT 时该项自动跳过。
"""
import json, os, re, sys
from collections import Counter

SUBJECT = "math-bsd"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
    "3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订)（docx转换）.txt",
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/"
    "（3）普通高中数学课程标准日常修订版（2017年版2025年修订）.txt",
]
FOUR = {"数与代数", "图形与几何", "统计与概率", "综合与实践"}
MD_BAD = re.compile(r"\*\*|##|`|\$|\\frac")
ABS_OK = re.compile(r"\|[^|\n]{1,14}\|")   # 绝对值 |x|、|a + b| 放行（与 check_bsd_bank.py 同口径）


def has_md(s):
    rest = ABS_OK.sub("", s)
    return bool(MD_BAD.search(rest)) or "|" in rest

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
ck("全部 subject=math-bsd", all(t.get("subject") == SUBJECT for t in topics))
ck("规模非空（≥31 知识点）", len(topics) >= 31, len(topics))
ck("id 命名 mbs_[pjuh]NNN（h＝高中）", all(re.fullmatch(r"mbs_[pjuh]\d{3}", t["id"]) for t in topics))
ck("领域只用课标四领域", {t.get("domain") for t in topics} <= FOUR,
   sorted({t.get("domain") for t in topics}))
ck("四领域都有点", {t.get("domain") for t in topics} == FOUR,
   sorted({t.get("domain") for t in topics}))
ck("tags 首位＝领域", all((t.get("tags") or [None])[0] == t.get("domain") for t in topics))
ck("年级 1–15", all(isinstance(t.get("grade"), int) and 1 <= t["grade"] <= 15 for t in topics))
ck("学期 上/下", all(t.get("semester") in ("上", "下") for t in topics))
ck("章名含册次", all(re.match(r"^(?:[一二三四五六]年级[上下]册|[七八九]年级[上下]册|必修第[一二三四五]册|选择性必修第[一二三四五]册) 第[一二三四五六七八九十\d]+(?:单元|章)", t["chapter"])
                 for t in topics))
ck("含「十X年级」字样", not [t["id"] for t in topics if re.search(r"十[一二三四]年级", t["chapter"])])
ck("description 40–120 字", all(40 <= len(t.get("description", "")) <= 120 for t in topics),
   [t["id"] for t in topics if not 40 <= len(t.get("description", "")) <= 120][:3])
ck("掌握标准 2–3 条", all(2 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))
ck("诊断入口题有问有答",
   all((t.get("diagnostic_question") or {}).get("question") and (t.get("diagnostic_question") or {}).get("answer")
       for t in topics))

# ---- 课标 ----
ck("每点都挂课标", all(t.get("standards") for t in topics),
   [t["id"] for t in topics if not t.get("standards")][:3])
ck("课标 id 都能在索引里解析",
   not [1 for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids],
   [s.get("id") for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids][:3])
ck("每条课标都带 quote", not [1 for t in topics for s in t.get("standards", []) if not s.get("quote")])
ck("confidence 三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                           for t in topics for s in t.get("standards", [])))
ck("quote 长度 12–120 字",
   all(12 <= len(s["quote"]) <= 120 for t in topics for s in t.get("standards", [])))
if all(os.path.exists(p) for p in TXT):
    src = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT))
    miss = [(t["id"], s["quote"][:14]) for t in topics for s in t.get("standards", [])
            if s.get("quote") and norm(s["quote"]) not in src]
    ck("quote 逐字回表 100%", not miss, miss[:3])
else:
    checks.append(("quote 回表（缺 TXT，跳过）", True, None))

# ---- 边 ----
pairs = [(e["from"], e["to"]) for e in deps]
ck("边无自环", all(a != b for a, b in pairs))
ck("边无重复", len(set(pairs)) == len(pairs))
ck("边两端都存在", all(a in T and b in T for a, b in pairs))
ck("边类型 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps))
parent = {}
for a, b in pairs:
    parent.setdefault(b, set()).add(a)
ck("deps ↔ prerequisites 双向镜像",
   not [(a, b) for b, ps in parent.items() for a in ps if a not in T[b].get("prerequisites", [])]
   and not [(p, t["id"]) for t in topics for p in t.get("prerequisites", []) if (p, t["id"]) not in set(pairs)])

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

# ---- 题库 ----
UNIT_TIDS = {t["id"] for t in topics if t.get("level") == "unit"}
ck("诊断题 ≥8 题/课时点、≥5 题/单元点",
   all(by_topic.get(tid, 0) >= (5 if tid in UNIT_TIDS else 8) for tid in T),
   {k: v for k, v in by_topic.items() if v < (5 if k in UNIT_TIDS else 8)})
ck("题 id 唯一", len({q["id"] for q in qs}) == len(qs))
ck("题 id 命名 mbs_qNNNNNN", all(re.fullmatch(r"mbs_q\d{6}", q["id"]) for q in qs))
ck("题目 topicId 均可对", all(q["topicId"] in T for q in qs))
types = Counter(q["type"] for q in qs)
ck("题型四类齐备", set(types) == {"choice", "fill", "numeric", "short-answer"}, dict(types))
ck("numeric ≥20%", types["numeric"] >= len(qs) * 0.2, f"{types['numeric']}/{len(qs)}")
ck("fill ≥18%", types["fill"] >= len(qs) * 0.18, f"{types['fill']}/{len(qs)}")
ck("short-answer ≥18%", types["short-answer"] >= len(qs) * 0.18, f"{types['short-answer']}/{len(qs)}")
ck("每点 ≥3 种题型",
   all(len({q["type"] for q in qs if q["topicId"] == tid}) >= 3 for tid in T))
ck("难度三档齐备", {q["difficulty"] for q in qs} == {"basic", "standard", "hard"},
   dict(Counter(q["difficulty"] for q in qs)))
ck("题干 ≥12 字", all(len(q.get("prompt", "")) >= 12 for q in qs),
   [q["id"] for q in qs if len(q.get("prompt", "")) < 12][:3])
ck("题干全域不重复", len({q["prompt"] for q in qs}) == len(qs))
ck("解析 ≥20 字", all(len(q.get("explanation", "")) >= 20 for q in qs),
   [q["id"] for q in qs if len(q.get("explanation", "")) < 20][:3])
ck("无 Markdown 符号", not [q["id"] for q in qs
                          if has_md(q.get("prompt", "") + q.get("explanation", ""))])
bad_choice = [q["id"] for q in qs if q["type"] == "choice"
              and (len(q.get("options") or []) != 4
                   or q.get("answer") not in [o["label"] for o in q["options"]]
                   or len({o["text"] for o in q["options"]}) != 4)]
ck("选择题 4 选项/答案在选项内/文本互异", not bad_choice, bad_choice[:3])
ck("选择题 choices 与 options 同值",
   all(q.get("choices") == q.get("options") for q in qs if q["type"] == "choice"))
ck("非选择题 choices 为空", all((q.get("choices") or []) == [] for q in qs if q["type"] != "choice"))
bad_num = []
for q in qs:
    if q["type"] != "numeric":
        continue
    try:
        if abs(float(eval(q["verify"], {"__builtins__": {}}, {})) - float(q["answer"])) > 1e-6:
            bad_num.append(q["id"])
    except Exception:                                   # noqa: BLE001
        bad_num.append(q["id"])
ck("numeric verify 可复算且等于 answer", not bad_num, bad_num[:3])
ck("简答都带 keypoints≥2", all(len(q.get("keypoints") or []) >= 2
                             for q in qs if q["type"] == "short-answer"))
ch = Counter(q["answer"] for q in qs if q["type"] == "choice")
tot = sum(ch.values()) or 1
ck("答案位均衡（各 ≥15%）", all(ch[k] / tot >= 0.15 for k in "ABCD"), dict(ch))
g1 = [q for q in qs if T[q["topicId"]]["grade"] == 1]
# 一年级上册只到 20 以内；下册到 100 以内 ⇒ 按册设上限（用 topic 的 chapter 判册，不看 grade）
LIMIT = 20
bad_g1 = []
for q in g1:
    ch = T[q["topicId"]]["chapter"]
    lim = 100 if "一年级下册" in ch else 20
    over = [n for n in re.findall(r"(?<![\d.])(\d{1,3})(?![\d.])", q["prompt"]) if int(n) > lim]
    if over:
        bad_g1.append((q["id"], ch.split(" ")[0], over[:3]))
ck("一年级不超纲（上册 ≤20 / 下册 ≤100）", not bad_g1, bad_g1[:3])

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print(SUBJECT.upper() + " DATA PASSED")
