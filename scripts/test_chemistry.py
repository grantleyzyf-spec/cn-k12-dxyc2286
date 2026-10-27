# -*- coding: utf-8 -*-
"""学科不变量测试（模板）。用法: python3 scripts/test_<subject>.py
复制本文件，把 SUBJECT 改成目标学科；课标 TXT 不存在时自动跳过回表（CI 用）。"""
import json, os, re, sys

SUBJECT = "chemistry"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = [
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /义务教育/8.《义务教育化学课程标准·日常修订版》(2022年版2025年修订).txt",
    "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/（9）普通高中化学课程标准日常修订版（2017年版2025年修订）.txt",
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

ck("id 唯一", len(T) == len(topics))
ck("全部 subject 一致", all(t.get("subject") == SUBJECT for t in topics))
ck("诊断题与知识点数量匹配", len(qs) >= len(topics), f"{len(qs)} vs {len(topics)}")
ck("课标 id 均可解析", not [1 for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids])
ck("每条课标引用都带 quote", not [1 for t in topics for s in t.get("standards", []) if not s.get("quote")])
ck("confidence 三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                          for t in topics for s in t.get("standards", [])))

if all(os.path.exists(p) for p in TXT):
    src = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT))
    miss = [(t["id"], s["quote"][:16]) for t in topics for s in t.get("standards", [])
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
ck("每知识点都有题", all(any(q.get("topicId") == tid for q in qs) for tid in T))
ck("难度枚举合规", all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs),
   sorted({q.get("difficulty") for q in qs}))
bad_choice = [q["id"] for q in qs if q.get("type") == "choice"
              and (len(q.get("options") or []) != 4
                   or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
ck("题干 ≥8 字", all(len(q.get("prompt", "")) >= 8 for q in qs))
ck("每题有解析", all(len(q.get("explanation", "")) >= 4 for q in qs))
ck("numeric 有 verify", all(q.get("verify") for q in qs if q.get("type") == "numeric"))
need = ["name", "domain", "grade", "semester", "chapter", "type", "description", "mastery_criteria"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics))
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))
ck("题目 id 唯一", len({q.get("id") for q in qs}) == len(qs),
   sorted({q.get("id") for q in qs if [x.get("id") for x in qs].count(q.get("id")) > 1})[:3])
def _num_ok(q):
    try:
        return abs(float(eval(q["verify"], {"__builtins__": {}})) - float(q["answer"])) <= max(1e-6, abs(float(q["answer"])) * 1e-3)
    except Exception:
        return False


ck("numeric 的 answer 与 verify 复算一致", all(_num_ok(q) for q in qs if q.get("type") == "numeric"),
   [q["id"] for q in qs if q.get("type") == "numeric" and not _num_ok(q)][:3])
_stage = lambda g: 1 if g <= 6 else (2 if g <= 9 else 3)
_dup_stage = [n for n in {t["name"] for t in topics}
              if len({_stage(x["grade"]) for x in topics if x["name"] == n}) <
                 [x["name"] for x in topics].count(n)]
ck("同学段内知识点名不重复（跨学段同名允许，如九年级/高中「金属材料」）", not _dup_stage, _dup_stage[:3])
ck("高中册名可派生（章节以「必修/选择性必修…册」开头）",
   all(re.match(r"^(必修第[一二三四五]册|选择性必修第[一二三]册) ", t["chapter"]) for t in topics if t["grade"] >= 10),
   [t["chapter"] for t in topics if t["grade"] >= 10 and not re.match(r"^(必修第[一二三四五]册|选择性必修第[一二三]册) ", t["chapter"])][:3])

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails)); sys.exit(1)
print(SUBJECT.upper() + " DATA PASSED")
