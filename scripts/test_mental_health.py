# -*- coding: utf-8 -*-
"""心理健康（mental-health）学科不变量测试：python3 scripts/test_mental_health.py

课标 TXT 快照不在时（CI 环境）自动跳过回表两项。快照路径：
~/Desktop/中小学教材/2025修订课程标准TXT /义务教育/《中小学心理健康教育课程标准》(2026年).txt
"""
import json
import os
import re
import sys

SUBJECT = "mental-health"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
TXT = [os.path.expanduser(
    "~/Desktop/中小学教材/2025修订课程标准TXT /义务教育/"
    "《中小学心理健康教育课程标准》(2026年).txt")]
SUYANG = ("自我意识", "情绪管理", "人际交往", "学会学习", "生命与社会适应")
OTHER_SUYANG = ("唯物史观", "时空观念", "史料实证", "历史解释", "家国情怀",
                "语言能力", "文化意识", "思维品质", "学习能力",
                "科学观念", "科学思维", "探究实践", "态度责任",
                "技术意识", "工程思维", "创新设计", "图样表达", "物化能力",
                "信息意识", "计算思维", "数字化学习与创新", "信息社会责任",
                "审美感知", "艺术表现", "创意实践", "文化理解",
                "运动能力", "健康行为", "体育品德",
                "政治认同", "科学精神", "法治观念", "公共参与",
                "劳动观念", "劳动能力", "劳动习惯和品质", "劳动精神")

fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, bool(ok), detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail is not None else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


topics = json.load(open(os.path.join(D, SUBJECT, "topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, SUBJECT, "dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(D, SUBJECT, "questions.json"), encoding="utf-8"))
idx = json.load(open(os.path.join(D, "cn-curriculum-standards.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}
std_ids = {e["id"] for e in idx["subjects"].get(SUBJECT, {}).get("entries", [])}

ck("id 唯一", len(T) == len(topics))
ck("全部 subject 一致", all(t.get("subject") == SUBJECT for t in topics))
ck("规模下限 300 知识点", len(topics) >= 300, len(topics))
ck("两层俱全（单元级/课时级）",
   {t.get("level") for t in topics} == {"unit", "lesson"},
   sorted({t.get("level") for t in topics}))
ck("课标 id 均可解析", not [1 for t in topics for s in t.get("standards", [])
                            if s.get("id") not in std_ids],
   sorted({s.get("id") for t in topics for s in t.get("standards", []) if s.get("id") not in std_ids})[:3])
ck("每条课标引用都带 quote", not [1 for t in topics for s in t.get("standards", [])
                                  if not s.get("quote")])

if all(os.path.exists(p) for p in TXT):
    src = norm("".join(open(p, encoding="utf-8", errors="ignore").read() for p in TXT))
    miss = [(t["id"], s["quote"][:18]) for t in topics for s in t.get("standards", [])
            if s.get("quote") and norm(s["quote"]) not in src]
    ck("quote 逐字回表 100%", not miss, miss[:3])
    nlines = open(TXT[0], encoding="utf-8", errors="ignore").read().count("\n") + 1
    ck("sourceLine 落在课标快照行范围内",
       all(isinstance(s.get("sourceLine"), int) and 1 <= s["sourceLine"] <= nlines
           for t in topics for s in t.get("standards", [])))
else:
    checks.append(("quote 回表（缺课标快照，跳过）", True, None))
    checks.append(("sourceLine 范围（缺课标快照，跳过）", True, None))

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

per = {}
for q in qs:
    per[q.get("topicId")] = per.get(q.get("topicId"), 0) + 1
ck("课时点 ≥8 题", all(per.get(t["id"], 0) >= 8 for t in topics if t["level"] == "lesson"),
   [(t["id"], per.get(t["id"], 0)) for t in topics if t["level"] == "lesson" and per.get(t["id"], 0) < 8][:5])
ck("单元点 ≥5 题", all(per.get(t["id"], 0) >= 5 for t in topics if t["level"] == "unit"),
   [(t["id"], per.get(t["id"], 0)) for t in topics if t["level"] == "unit" and per.get(t["id"], 0) < 5][:5])
ck("题目 topicId 均可解析", all(q.get("topicId") in T for q in qs))
ck("难度枚举合规", all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs))
ck("三档难度均出现", {q.get("difficulty") for q in qs} == {"basic", "standard", "hard"})
bad_choice = [q["id"] for q in qs if q.get("type") == "choice"
              and (len(q.get("options") or []) != 4
                   or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
ans = {}
for q in qs:
    if q.get("type") == "choice":
        ans[q["answer"]] = ans.get(q["answer"], 0) + 1
n = sum(ans.values()) or 1
ck("答案位均衡（单字母 ≤40%）", all(v / n <= 0.40 for v in ans.values()), ans)
ck("题干 ≥12 字", all(len(q.get("prompt", "")) >= 12 for q in qs))
ck("每题有解析（≥15 字）", all(len(q.get("explanation", "")) >= 15 for q in qs))
ck("非选择题不带 options",
   all(not q.get("options") for q in qs if q.get("type") != "choice"))

need = ["name", "domain", "grade", "semester", "chapter", "type", "description",
        "mastery_criteria"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics))
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))
ck("domain 属心理健康五素养",
   all(t.get("domain") in SUYANG for t in topics),
   sorted({t.get("domain") for t in topics} - set(SUYANG)))
ck("无误入其他学科素养词",
   not [t["id"] for t in topics
        if any(w in (t.get("description") or "") + "".join(t.get("mastery_criteria") or [])
               for w in OTHER_SUYANG)])
ck("grade 取值 1–12", all(isinstance(t.get("grade"), int) and 1 <= t["grade"] <= 12 for t in topics))
ck("semester 仅 上/下", all(t.get("semester") in ("上", "下") for t in topics))
ck("chapter 含年级册名",
   all(re.search(r"[一二三四五六七八九]年级[上下]册|[七八九]年级全一册|高中[一二三]年级", t.get("chapter", ""))
       for t in topics),
   [t["id"] for t in topics
    if not re.search(r"[一二三四五六七八九]年级[上下]册|[七八九]年级全一册|高中[一二三]年级", t.get("chapter", ""))][:3])
ck("tags 非空", all(t.get("tags") for t in topics))
ck("诊断题问答齐全", all((t.get("diagnostic_question") or {}).get("question", "").strip()
                          and (t.get("diagnostic_question") or {}).get("answer", "").strip()
                          for t in topics))
ck("诊断题答案非裸字母",
   all((t.get("diagnostic_question") or {}).get("answer", "").strip() not in list("ABCD")
       for t in topics))

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print(SUBJECT.upper() + " DATA PASSED")
