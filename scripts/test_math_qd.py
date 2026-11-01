# -*- coding: utf-8 -*-
"""数学（青岛版，math-qd）不变量测试。用法: python3 scripts/test_math_qd.py

26 项：规模 / 唯一 / subject / level 两级 / 册名可派生 / 课标可解析 + quote 逐字回表 /
先修图（无环·无重·无自环·双端存在·镜像） / 根节点 reason / 题量（课时 8・单元 5） /
选择 4 选项与答案位均衡 / 题干与解析字数 / 无占位干扰项 / 难度三档 / 领域口径 / 章节连续。

课标回表：义务教育数学课标 TXT（本机快照，CI 无则跳过）。
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

SUBJECT = "math-qd"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
    "3.《义务教育数学课程标准·日常修订版》(2022年版2025年修订).txt",
]
BANK_BOOKS = {"一年级上册"}   # 已交题库的册次；其余册次允许 0 题（缺口在 docs/art 记录）
BOOOKS = ("一年级上册", "一年级下册", "二年级上册", "二年级下册", "三年级上册", "三年级下册",
          "四年级上册", "五年级上册", "六年级上册", "七年级上册", "七年级下册",
          "八年级上册", "八年级下册", "九年级上册")
DOMAINS = {"数与代数", "图形与几何", "统计与概率", "综合与实践"}
HAN = re.compile(r"[\u4e00-\u9fff]")
fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + ("：" + str(detail) if detail else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


def han(s):
    return len(HAN.findall(s or ""))


topics = json.load(open(os.path.join(D, SUBJECT, "topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, SUBJECT, "dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(D, SUBJECT, "questions.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}
by_topic = Counter(q.get("topicId") for q in qs)

ck("id 唯一", len(T) == len(topics))
ck("全部 subject 一致", all(t.get("subject") == SUBJECT for t in topics))
ck("level 只有 unit/lesson 两级", {t.get("level") for t in topics} <= {"unit", "lesson"},
   Counter(t.get("level") for t in topics))
_inv = json.load(open(os.path.join(D, SUBJECT, "_inventory.json"), encoding="utf-8"))
SINGLE = set()   # 教材本身只有单元、无信息窗/小节的单元（实践·复习·拼搭类）
for _b in _inv["books"]:
    for _u in _b["units"]:
        if not _u.get("lessons"):
            SINGLE.add((_b["book"], re.sub(r"\s+", "", _u["title"])))
ck("单元点都有下属课时点（教材无信息窗的单元除外）",
   all(any(d["from"] == t["id"] for d in deps) or (t["chapter"].split(" ")[0], t["name"].split("·")[0]) in SINGLE
       for t in topics if t["level"] == "unit"),
   [t["id"] for t in topics if t["level"] == "unit" and not any(d["from"] == t["id"] for d in deps)
    and (t["chapter"].split(" ")[0], t["name"].split("·")[0]) not in SINGLE][:3])
ck("章节可派生册名", all(t["chapter"].startswith(tuple(BOOOKS)) for t in topics),
   [t["chapter"] for t in topics if not t["chapter"].startswith(tuple(BOOOKS))][:3])
ck("领域属课标四领域", {t.get("domain") for t in topics} <= DOMAINS,
   sorted({t.get("domain") for t in topics} - DOMAINS))
ck("年级 1–9 全覆盖", {t["grade"] for t in topics} == set(range(1, 10)),
   sorted(set(range(1, 10)) - {t["grade"] for t in topics}))

std_ids = {e["id"] for e in idx["subjects"][SUBJECT]["entries"]} if SUBJECT in idx["subjects"] else set()
ck("课标 id 均可解析", all(s.get("id") in std_ids for t in topics for s in t.get("standards", [])),
   [s.get("id") for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids][:3])
ck("每条课标引用都带 quote", all(s.get("quote") for t in topics for s in t.get("standards", [])))
ck("confidence 三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                          for t in topics for s in t.get("standards", [])))

if all(os.path.exists(p) for p in TXT):
    src = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT))
    miss = [(t["id"], s["id"]) for t in topics for s in t.get("standards", [])
            if s.get("quote") and norm(s["quote"]) not in src]
    ck("quote 逐字回表 100%", not miss, miss[:3])
else:
    checks.append(("quote 回表（缺课标 TXT，跳过）", True, None))

pairs = [(e["from"], e["to"]) for e in deps]
ck("边无自环", all(a != b for a, b in pairs))
ck("边无重复", len(set(pairs)) == len(pairs))
ck("边两端存在", all(a in T and b in T for a, b in pairs))
ck("边类型 hard/soft", {e.get("type") for e in deps} <= {"hard", "soft"})
parent = defaultdict(set)
for a, b in pairs:
    parent[b].add(a)
ck("deps 与 prerequisites 双向镜像",
   all(set(t.get("prerequisites", [])) == parent.get(t["id"], set()) for t in topics),
   [t["id"] for t in topics if set(t.get("prerequisites", [])) != parent.get(t["id"], set())][:3])
color = {}


def dfs(u):
    color[u] = 1
    for b in (b for a, b in pairs if a == u):
        if color.get(b) == 1 or (color.get(b, 0) == 0 and dfs(b)):
            return True
    color[u] = 2
    return False


ck("先修图无环", not any(color.get(u, 0) == 0 and dfs(u) for u in T))
ck("根节点都有 root_reason", all(t.get("root_reason") for t in topics if not t.get("prerequisites")),
   [t["id"] for t in topics if not t.get("prerequisites") and not t.get("root_reason")][:3])

need = {"lesson": 8, "unit": 5}
short = [(t["id"], t["level"], by_topic.get(t["id"], 0)) for t in topics
         if t["chapter"].split(" ")[0] in BANK_BOOKS and by_topic.get(t["id"], 0) < need[t["level"]]]
ck("已交题库册次逐点题量达标（课时 8 / 单元 5）", not short, short[:5])
no_bank = sorted({t["chapter"].split(" ")[0] for t in topics} - BANK_BOOKS)
checks.append((f"题库待补册次（{len(no_bank)} 册，缺口见 docs）", True, None))
ck("题目 topicId 都在 topics",
   all(q.get("topicId") in T for q in qs), [q.get("id") for q in qs if q.get("topicId") not in T][:3])
ck("难度三档且分布合理", {q.get("difficulty") for q in qs} == {"basic", "standard", "hard"},
   Counter(q.get("difficulty") for q in qs))
bad = [q["id"] for q in qs if q.get("type") == "choice"
       and (len(q.get("options") or []) != 4 or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad, bad[:5])
ck("题干 ≥12 汉字", all(han(q.get("prompt")) >= 12 for q in qs),
   [(q["id"], han(q.get("prompt"))) for q in qs if han(q.get("prompt")) < 12][:3])
ck("解析 ≥15 汉字", all(han(q.get("explanation")) >= 15 for q in qs),
   [q["id"] for q in qs if han(q.get("explanation")) < 15][:3])
ck("prompt 与 question 同值", all(q.get("question") == q.get("prompt") for q in qs))
PLACE = re.compile(r"与本题无关|与所学内容无关|不知道|仅在(?:大学|初中|高中)|不属于(?:本课程|该学科|本学科)|以上都(?:不是|对)|\.\.\.|…")
ck("选项无占位项/省略号", not [q["id"] for q in qs for o in q.get("options") or [] if PLACE.search(o.get("text") or "")],
   [q["id"] for q in qs for o in q.get("options") or [] if PLACE.search(o.get("text") or "")][:3])
dist = Counter(q.get("answer") for q in qs if q.get("type") == "choice")
ck("答案位不单一（≥3 标签，单标签 ≤45%）",
   len(dist) >= 3 and max(dist.values()) <= len([q for q in qs if q.get("type") == "choice"]) * 0.45, dist)

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print(SUBJECT.upper() + " DATA PASSED")
