# -*- coding: utf-8 -*-
"""历史（history）学科收口自检：30 项不变量。用法：python3 scripts/test_history.py

课标回表：本机课标 TXT 存在时逐字回表；CI 环境缺 TXT 自动跳过（不假红）。
口径与数学、语文、生物一致（见 docs/math.md、docs/chinese.md、docs/biology.md）。
"""
import json, os, re, sys
from collections import Counter

SUBJECT = "history"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/5.《义务教育历史课程标准·日常修订版》(2022年版2025年修订).txt",
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/（6）普通高中历史课程标准日常修订版（2017年版2025年修订）.txt",
]
VOLUMES = ["七年级上册", "七年级下册", "八年级上册", "八年级下册", "九年级上册", "九年级下册",
           "中外历史纲要（上）", "中外历史纲要（下）", "选择性必修1", "选择性必修2", "选择性必修3"]

fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


def volume_of(ch):
    m = re.match(r"((?:七|八|九)年级[上下]册|中外历史纲要（[上下]）|选择性必修[123])", ch or "")
    return m.group(1) if m else (ch or "").split(" ")[0]


topics = json.load(open(os.path.join(D, SUBJECT, "topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, SUBJECT, "dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(D, SUBJECT, "questions.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}
std_ids = {e["id"] for e in idx["subjects"][SUBJECT]["entries"]}

ck("id 唯一", len(T) == len(topics))
ck("全部 subject 一致", all(t.get("subject") == SUBJECT for t in topics))
ck("规模非空（≥140 知识点）", len(topics) >= 140, len(topics))
ck("诊断题与知识点数量匹配", len(qs) >= len(topics), f"{len(qs)} vs {len(topics)}")
ck("年级取值 7–12", all(isinstance(t.get("grade"), int) and 7 <= t["grade"] <= 12 for t in topics),
   sorted({t.get("grade") for t in topics}))
ck("学期取值 上/下", all(t.get("semester") in ("上", "下") for t in topics))
ck("章节非空且含册次", all(volume_of(t.get("chapter")) for t in topics))
ck("11 个册次全部有知识点", all(volume_of(t.get("chapter")) in VOLUMES for t in topics)
   and len({volume_of(t.get("chapter")) for t in topics}) == len(VOLUMES),
   sorted(Counter(volume_of(t.get("chapter")) for t in topics).items()))
ck("类型枚举合规", all(t.get("type") in ("conceptual", "procedural", "reasoning", "modeling", "application")
                      for t in topics), sorted({t.get("type") for t in topics}))
ck("领域（课标学习板块）≥6 种且无空值",
   len({t.get("domain") for t in topics}) >= 6 and all(t.get("domain") for t in topics),
   sorted(Counter(t.get("domain") for t in topics).items()))
ck("课标 id 均可解析", not [1 for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids])
ck("每条课标引用都带 quote", not [1 for t in topics for s in t.get("standards", []) if not s.get("quote")])
ck("confidence 三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                          for t in topics for s in t.get("standards", [])))
ck("每个知识点都有课标引用", all(t.get("standards") for t in topics),
   [t["id"] for t in topics if not t.get("standards")][:3])
ck("curriculumRef 与首条课标一致",
   all(t.get("curriculumRef") == (t.get("standards") or [{}])[0].get("id") for t in topics),
   [t["id"] for t in topics if t.get("curriculumRef") != (t.get("standards") or [{}])[0].get("id")][:3])

if all(os.path.exists(p) for p in TXT):
    src = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT))
    miss = [(t["id"], s["quote"][:16]) for t in topics for s in t.get("standards", [])
            if s.get("quote") and norm(s["quote"]) not in src]
    ck("quote 逐字回表 100%", not miss, miss[:3])
else:
    checks.append(("quote 回表（缺 TXT，跳过）", True, None))

pairs = [(e["from"], e["to"]) for e in deps]
ck("边无自环", all(a != b for a, b in pairs))
ck("边无重复", len(set(pairs)) == len(pairs), len(pairs) - len(set(pairs)))
ck("边两端存在", all(a in T and b in T for a, b in pairs))
ck("边类型 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps))
parent = {}
for a, b in pairs:
    parent.setdefault(b, set()).add(a)
ck("deps 与 prerequisites 双向镜像",
   not [(a, b) for b, ps in parent.items() for a in ps if a not in T[b].get("prerequisites", [])])
ck("topics.prerequisites 均有对应边",
   not [(p, t["id"]) for t in topics for p in t.get("prerequisites", []) if (p, t["id"]) not in set(pairs)])

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
ck("非根节点 root_reason 不冲突",
   all(not t.get("root_reason") for t in topics if t.get("prerequisites")))
ck("每知识点都有题", all(any(q.get("topicId") == tid for q in qs) for tid in T))
ck("题目 topicId 均可解析", all(q.get("topicId") in T for q in qs))
ck("难度三档枚举合规", all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs),
   sorted({q.get("difficulty") for q in qs}))
bad_choice = [q["id"] for q in qs if q.get("type") == "choice"
              and (len(q.get("options") or []) != 4
                   or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
ans_dist = Counter(q.get("answer") for q in qs)
ck("答案分布均衡（最多–最少 ≤ 8）",
   bool(ans_dist) and max(ans_dist.values()) - min(ans_dist.values()) <= 8, dict(ans_dist))
ck("题干 ≥8 字", all(len(q.get("prompt", "")) >= 8 for q in qs))
ck("每题有解析", all(len(q.get("explanation", "")) >= 4 for q in qs))
ck("numeric 有 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"))
need = ["name", "domain", "grade", "semester", "chapter", "type", "description", "mastery_criteria"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics))
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print(SUBJECT.upper() + " DATA PASSED")
