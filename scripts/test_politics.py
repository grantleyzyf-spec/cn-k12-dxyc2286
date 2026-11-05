# -*- coding: utf-8 -*-
"""politics 学科不变量自检（25+ 项）。

用法：
  python3 scripts/test_politics.py            # 全量（题库为空会红）
  python3 scripts/test_politics.py --no-bank  # 题库未落时只查结构与课标

课标快照不在时跳过逐字回表（CI 无快照也能跑）。
"""
import json
import os
import re
import sys
from collections import Counter

SUBJECT = "politics"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
SUB = os.path.join(D, SUBJECT)
SNAP = [os.path.join(SUB, "_standards_src", "ddfz-2022-content.txt"),
        os.path.join(SUB, "_standards_src", "zz-2017-content.txt")]
ENTRIES = os.path.join(D, "politics-standards-entries.json")
NO_BANK = "--no-bank" in sys.argv

fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


topics = json.load(open(os.path.join(SUB, "topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(SUB, "dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(SUB, "questions.json"), encoding="utf-8"))
entries = json.load(open(ENTRIES, encoding="utf-8"))
T = {t["id"]: t for t in topics}
E = {e["id"]: e for e in entries}

# ---------------- 结构级
ck("知识点 id 唯一", len(T) == len(topics), f"{len(topics)} 条 / {len(T)} 唯一")
ck("全部 subject 一致", all(t.get("subject") == SUBJECT for t in topics))
ck("级别只有 unit/lesson", {t.get("level") for t in topics} <= {"unit", "lesson"},
   {t.get("level") for t in topics})
lv = Counter(t["level"] for t in topics)
ck("两级规模（unit 115 / lesson 319）", lv["unit"] == 115 and lv["lesson"] == 319, dict(lv))
ck("册次 21 册齐全", len({t["chapter"].split(" ")[0] for t in topics}) == 21,
   len({t["chapter"].split(" ")[0] for t in topics}))
ck("无「目录」点", not [t["id"] for t in topics if t["name"].strip() in ("目录", "目 录")])
ck("domain 属五板块", {t["domain"] for t in topics} <=
   {"道德教育", "政治认同", "法治教育", "经济发展", "哲学思维"}, {t["domain"] for t in topics})
ck("高中每册 domain ≤2 个板块",
   all(len({t["domain"] for t in topics if t["chapter"].split(" ")[0] == b}) <= 2
       for b in {t["chapter"].split(" ")[0] for t in topics if t["grade"] >= 10}))

# 高中框号：同课内 1..N 连续
box_bad = []
for t in topics:
    m = re.search(r"第([0-9一二三四五六七八九十]+)框", t["chapter"])
    if m and t["level"] == "lesson" and t["grade"] >= 10:
        unit = t["chapter"][:m.start()]
        nums = sorted(int(x.group(1)) if x.group(1).isdigit() else 0
                      for x in [re.search(r"第(\d+)框", u["chapter"]) for u in topics
                                if u["chapter"].startswith(unit) and u["level"] == "lesson"]
                      if x)
        if nums != list(range(1, len(nums) + 1)):
            box_bad.append(unit)
ck("高中框号连续", not box_bad, sorted(set(box_bad))[:3])

# ---------------- 课标级
ck("每条课标 id 可解析", not [1 for t in topics for s in t["standards"] if s.get("id") not in E])
ck("每条课标引用都带 quote", not [1 for t in topics for s in t["standards"] if not s.get("quote")])
ck("confidence 三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                        for t in topics for s in t["standards"]))
ck("sourceLine 是整数", all(isinstance(s.get("sourceLine"), int)
                        for t in topics for s in t["standards"]))
ck("每个点至少 1 条引文", all(t["standards"] for t in topics),
   [t["id"] for t in topics if not t["standards"]][:3])
ck("curriculumRef 与 standards[0] 一致",
   all(t.get("curriculumRef") == (t["standards"][0]["id"] if t["standards"] else "") for t in topics))

if all(os.path.exists(p) for p in SNAP):
    lines = {p: open(p, encoding="utf-8").read().split("\n") for p in SNAP}
    miss = []
    for t in topics:
        for s in t["standards"]:
            src = lines[SNAP[0] if s["id"].startswith("ddf") else SNAP[1]]
            ln = s["sourceLine"]
            if not (1 <= ln <= len(src)) or norm(s["quote"]) not in norm(src[ln - 1]):
                miss.append((t["id"], s["id"]))
    ck("quote 逐行回表 100%", not miss, miss[:3])
else:
    checks.append(("quote 回表（缺快照，跳过）", True, None))

# ---------------- 先修图
pairs = [(e["from"], e["to"]) for e in deps]
ck("边无自环", all(a != b for a, b in pairs))
ck("边无重复", len(set(pairs)) == len(pairs), len(pairs) - len(set(pairs)))
ck("边两端存在", all(a in T and b in T for a, b in pairs))
ck("边类型 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps))
# 口径：hard 边必须镜像进 prerequisites；soft 边（册内单元衔接）只做提示，不进 prerequisites
parent = {}
for e in deps:
    if e["type"] == "hard":
        parent.setdefault(e["to"], set()).add(e["from"])
parent_all = {}
for e in deps:
    parent_all.setdefault(e["to"], set()).add(e["from"])
ck("hard 边都写进 prerequisites",
   not [(a, b) for b, ps in parent.items() for a in ps
        if a not in T[b].get("prerequisites", [])])
ck("prerequisites 都有对应边（hard/soft）",
   not [(t["id"], q) for t in topics for q in t.get("prerequisites", [])
        if q not in parent_all.get(t["id"], set())])
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
ck("高中课时点首前置是本课",
   all(T[t["prerequisites"][0]]["level"] == "unit"
       for t in topics if t["grade"] >= 10 and t["level"] == "lesson" and t["prerequisites"]))

# ---------------- 字段级
need = ["name", "domain", "grade", "semester", "chapter", "type", "description", "mastery_criteria"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics))
def han(x):
    return len(re.findall(r"[\u4e00-\u9fff]", x or ""))


ck("掌握标准 2–3 条且每条 15–50 字",
   all(2 <= len(t.get("mastery_criteria") or []) <= 3
       and all(15 <= han(m) <= 50 for m in t["mastery_criteria"]) for t in topics),
   [t["id"] for t in topics if not (2 <= len(t.get("mastery_criteria") or []) <= 3)
    or any(not (15 <= han(m) <= 50) for m in t.get("mastery_criteria") or [])][:3])
ck("description 40–90 字且非占位",
   all(40 <= han(t.get("description")) <= 90 and t["description"] != t["name"]
       and "核心观点并联系生活实例说明" not in t["description"] for t in topics),
   [t["id"] for t in topics if han(t.get("description")) < 40 or t["description"] == t["name"]][:3])
ck("掌握标准以行为动词开头",
   all(any(m.startswith(v) for v in ("能", "会", "懂得", "知道", "理解", "辨别", "举例",
                                    "说明", "运用", "说出", "区分", "认识", "体会", "感受",
                                    "认同", "掌握", "分析", "判断", "解释", "列举", "做到"))
       for t in topics for m in t.get("mastery_criteria") or []),
   [t["id"] for t in topics for m in t.get("mastery_criteria") or []
    if not any(m.startswith(v) for v in ("能", "会", "懂得", "知道", "理解", "辨别"))][:3])

# ---------------- 题库级
if NO_BANK or not qs:
    checks.append(("题库检查（questions.json 为空，跳过）", True, None))
else:
    ck("题 id 唯一", len({q["id"] for q in qs}) == len(qs))
    ck("topicId 均可解析", all(q["topicId"] in T for q in qs))
    by = Counter(q["topicId"] for q in qs)
    need_n = {"unit": 5, "lesson": 8}
    short = [(t, by.get(t, 0)) for t, v in T.items() if v["level"] in need_n
             and by.get(t, 0) < need_n[v["level"]]]
    ck("题量 8/5 达标", not short, short[:5])
    ck("难度三档枚举", all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs))
    ck("三档都有", {q.get("difficulty") for q in qs} == {"basic", "standard", "hard"},
       {q.get("difficulty") for q in qs})
    bad = [q["id"] for q in qs if q.get("type") == "choice"
           and (len(q.get("options") or []) != 4
                or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
    ck("选择题 4 选项且答案在选项内", not bad, bad[:5])
    ck("题干 ≥12 字", all(len(q.get("prompt", "")) >= 12 for q in qs),
       [q["id"] for q in qs if len(q.get("prompt", "")) < 12][:3])
    ck("解析 ≥15 字", all(len(q.get("explanation", "")) >= 15 for q in qs),
       [q["id"] for q in qs if len(q.get("explanation", "")) < 15][:3])
    # 题型构成：课时点 6 choice + 1 fill + 1 short；单元/课点 5 choice
    mix_bad = []
    for t in topics:
        ts = Counter(x["type"] for x in qs if x["topicId"] == t["id"])
        if t["level"] == "lesson":
            if ts != Counter({"choice": 6, "fill": 1, "short-answer": 1}):
                mix_bad.append((t["id"], dict(ts)))
        elif ts != Counter({"choice": 5}):
            mix_bad.append((t["id"], dict(ts)))
    ck("题型构成 6/1/1 与 5/0/0", not mix_bad, mix_bad[:3])
    fill_bad = [q["id"] for q in qs if q.get("type") == "fill"
                and ((q.get("options") or []) != [] or not isinstance(q.get("answer"), str))]
    ck("填空题无选项且答案非空", not fill_bad, fill_bad[:3])
    short_bad = [q["id"] for q in qs if q.get("type") == "short-answer"
                 and not (2 <= len(q.get("keypoints") or []) <= 4)]
    ck("简答题 keypoints 2–4 条", not short_bad, short_bad[:3])
    kp_bad = [q["id"] for q in qs if q.get("type") == "short-answer"
              for k in q.get("keypoints") or [] if han(k) < 4]
    ck("简答要点每条 ≥4 字", not kp_bad, kp_bad[:3])
    ch = [q for q in qs if q.get("type") == "choice"]
    dist = Counter(q["answer"] for q in ch)
    ck("答案位 ≥3 档且单档 ≤50%", len(dist) >= 3 and max(dist.values()) <= 0.5 * len(ch), dict(dist))
    PLACE = ("以上都不是", "以上都对", "与本题无关", "不知道", "仅在大学", "不属于本课程", "无法判断")
    def is_placeholder(t):
        t = re.sub(r"[\s，。；、！？（）()]", "", t or "")
        return any(t == p or (t.startswith(p) and len(t) <= len(p) + 3) for p in PLACE)
    ck("无占位选项", not [q["id"] for q in qs for o in (q.get("options") or [])
                      if is_placeholder(o.get("text", ""))])
    ck("无模板题干", not [q["id"] for q in qs
                     if re.match(r"^关于「.*」，下列说法正确的是", q.get("prompt", ""))])
    ck("选项文本互不相同", not [q["id"] for q in qs if q.get("type") == "choice"
                         and len({o["text"] for o in q["options"]}) != len(q["options"])])

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print(SUBJECT.upper() + " DATA PASSED")
