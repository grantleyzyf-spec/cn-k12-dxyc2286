#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""鲁教版高中地理 data/geography-lujiao 数据不变量测试。
用法: /usr/bin/python3 scripts/test_geo_lujiao.py
退出码 0 = 全绿；1 = 有失败项。口径对齐 scripts/test_geography.py（同族断言），
差异：本桶是高中 5 册（grade 10/11/12），领域用高中地理四领域。
"""
import json, os, re, sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-lujiao")
TXT = "/Users/a627692/Desktop/中小学教材/2025修订课程标准TXT /高中教育/（7）普通高中地理课程标准日常修订版（2017年版2025年修订）.txt"

fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def norm(s):
    return re.sub(r"\s+", "", s or "")


topics = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(D, "dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(D, "questions.json"), encoding="utf-8"))
sk = json.load(open(os.path.join(D, "_skeleton.json"), encoding="utf-8"))
STD = json.load(open(os.path.join(D, "_text", "std_items.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}
UNITS = [t for t in topics if t.get("level") == "unit"]
LESSONS = [t for t in topics if t.get("level") == "lesson"]

# 1 规模
ck("知识点 75 条（19 单元 + 56 课时）", len(topics) == 75, len(topics))
ck("单元点 19 / 课时点 56", (len(UNITS), len(LESSONS)) == (19, 56), (len(UNITS), len(LESSONS)))
ck("id 唯一", len(T) == len(topics))
ck("全部 subject=geography-lujiao", all(t.get("subject") == "geography-lujiao" for t in topics))
per = Counter(q["topicId"] for q in qs)
ck("课时点恰好 8 题 / 单元点恰好 5 题",
   all(per.get(t["id"]) == (5 if t["level"] == "unit" else 8) for t in topics),
   [(t["id"], per.get(t["id"])) for t in topics if per.get(t["id"]) != (5 if t["level"] == "unit" else 8)][:5])
ck("题 id 唯一", len({q["id"] for q in qs}) == len(qs))
ck("题干无重复（全库）", len({q["prompt"] for q in qs}) == len(qs),
   len(qs) - len({q["prompt"] for q in qs}))

# 2 册次
grades = {int(t["grade"]) for t in topics}
ck("年级覆盖 10、11、12", grades == {10, 11, 12}, sorted(grades))
books = Counter(t["chapter"].split(" ")[0] for t in topics)
ck("五册齐全", set(books) == {"必修第一册", "必修第二册", "选择性必修1", "选择性必修2", "选择性必修3"},
   dict(books))
ck("册名与「第X单元」之间留空格", all(re.match(r"^\S+ 第[一二三四五六七八九十]+单元", t["chapter"]) for t in topics),
   [t["chapter"][:28] for t in topics if not re.match(r"^\S+ 第[一二三四五六七八九十]+单元", t["chapter"])][:3])
ck("单元号用中文数字", not [t["id"] for t in topics if re.search(r"第\d+单元", t["chapter"])])
ck("章名不含「十X年级」错写", not [t["id"] for t in topics if re.search(r"十[一二三四]年级", t["chapter"])])
sk_units = {u["chapter"] for u in sk["units"]}
ck("19 个单元章名与骨架逐字一致", {u["chapter"] for u in UNITS} == sk_units,
   sorted(sk_units - {u["chapter"] for u in UNITS})[:3])

# 3 领域（高中地理四领域）
DOMAINS = {"自然地理", "人文地理", "区域发展", "资源环境与国家安全"}
bad_dom = [(t["id"], t.get("domain")) for t in topics if t.get("domain") not in DOMAINS]
ck("领域取值都在高中地理四领域内", not bad_dom, bad_dom[:3])
BOOK_DOM = {"必修第一册": "自然地理", "必修第二册": "人文地理", "选择性必修1": "自然地理",
            "选择性必修2": "区域发展", "选择性必修3": "资源环境与国家安全"}
mis = [(t["id"], t["domain"]) for t in topics
       if t["domain"] != BOOK_DOM.get(t["chapter"].split(" ")[0])]
ck("领域与册次对应（必修一自然/必修二人文/选必1自然/选必2区域/选必3资源环境安全）", not mis, mis[:3])
ck("tags 首位＝领域", all((t.get("tags") or [""])[0] == t["domain"] for t in topics),
   [t["id"] for t in topics if (t.get("tags") or [""])[0] != t["domain"]][:3])

# 4 课标
ck("全部挂课标", all(t.get("standards") for t in topics))
bad_ref = [(t["id"], s.get("id")) for t in topics for s in t.get("standards", [])
           if s.get("id", "").replace("geo-2017:", "") not in STD]
ck("课标条目都在 49 条条目池内", not bad_ref, bad_ref[:3])
ck("每条课标引用都带 quote", all(s.get("quote") for t in topics for s in t.get("standards", [])))
ck("confidence 只用三档", all(s.get("confidence") in ("exact", "partial", "inferred")
                              for t in topics for s in t.get("standards", [])))
ck("curriculumRef 与首条课标一致",
   all(t.get("curriculumRef") == (t["standards"][0]["id"] if t.get("standards") else None) for t in topics),
   [t["id"] for t in topics if t.get("standards") and t.get("curriculumRef") != t["standards"][0]["id"]][:3])

# 5 quote 逐字回表
if os.path.exists(TXT):
    src = norm(open(TXT, encoding="utf-8", errors="ignore").read())
    miss = [(t["id"], s["quote"][:16]) for t in topics for s in t.get("standards", [])
            if s.get("quote") and norm(s["quote"]) not in src]
    ck("quote 逐字回表命中 100%", not miss, miss[:3])
else:
    checks.append(("quote 回表（缺课标 TXT，跳过）", True, ""))

# 6 先修边
pairs = [(e["from"], e["to"]) for e in deps]
ck("无自环", all(a != b for a, b in pairs))
ck("无重复边", len(set(pairs)) == len(pairs))
ck("两端都存在", all(a in T and b in T for a, b in pairs))
ck("边类型只用 hard/soft", all(e.get("type") in ("hard", "soft") for e in deps))
parent = {}
for a, b in pairs:
    parent.setdefault(b, set()).add(a)
asym = [(a, b) for b, ps in parent.items() for a in ps if a not in T[b].get("prerequisites", [])]
ck("deps 与 topics.prerequisites 双向镜像", not asym, asym[:3])
color = {}


def dfs(u):
    color[u] = 1
    for b in (b for a, b in pairs if a == u):
        if color.get(b) == 1:
            return True
        if color.get(b, 0) == 0 and dfs(b):
            return True
    color[u] = 2
    return False


ck("先修图无环", not any(color.get(u, 0) == 0 and dfs(u) for u in T))
ck("课时点先修链完整（5 册各 1 根 + 其余 51 节各 1 条先修）",
   len([l for l in LESSONS if len(T[l["id"]]["prerequisites"]) == 1]) == len(LESSONS) - 5
   and len(deps) == len(LESSONS) - 5,
   (len(deps), len(LESSONS)))

# 7 根节点
roots = [t for t in topics if not t.get("prerequisites")]
ck("根节点都有 root_reason", all(t.get("root_reason") for t in roots), len(roots))

# 8 题
ck("难度只用 basic/standard/hard", all(q.get("difficulty") in ("basic", "standard", "hard") for q in qs))
ck("难度三档齐全", {q.get("difficulty") for q in qs} == {"basic", "standard", "hard"})
ck("每点三档齐", all(len({q["difficulty"] for q in qs if q["topicId"] == t["id"]}) == 3 for t in topics),
   [t["id"] for t in topics if len({q["difficulty"] for q in qs if q["topicId"] == t["id"]}) != 3][:5])
ck("题型枚举合法", all(q.get("type") in ("choice", "fill", "short-answer", "numeric") for q in qs),
   sorted({q.get("type") for q in qs}))
ck("题型四类齐全", {q.get("type") for q in qs} == {"choice", "fill", "short-answer", "numeric"})
bad_choice = [q["id"] for q in qs if q.get("type") == "choice" and
              (len(q.get("options") or []) != 4 or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not bad_choice, bad_choice[:5])
ck("选择题选项文本互异", all(len({o["text"] for o in q["options"]}) == 4 for q in qs if q.get("type") == "choice"))
ck("填空题题干含 ____", all("____" in q["prompt"] for q in qs if q.get("type") == "fill"))
ck("题干 ≥ 12 字", all(len(q.get("prompt", "")) >= 12 for q in qs),
   [q["id"] for q in qs if len(q.get("prompt", "")) < 12][:5])
ck("解析 ≥ 20 汉字", all(len(re.findall(r"[\u4e00-\u9fa5]", q.get("explanation", ""))) >= 20 for q in qs),
   [q["id"] for q in qs if len(re.findall(r"[\u4e00-\u9fa5]", q.get("explanation", ""))) < 20][:5])
ck("numeric 题都有 verify 且复算等于答案",
   all(q.get("verify") and abs(eval(q["verify"], {"__builtins__": {}}, {}) - float(q["answer"])) < 1e-6
       for q in qs if q.get("type") == "numeric"),
   [q["id"] for q in qs if q.get("type") == "numeric"
    and (not q.get("verify") or abs(eval(q["verify"], {"__builtins__": {}}, {}) - float(q["answer"])) >= 1e-6)][:5])
ck("topicId 都能对上知识点", all(q.get("topicId") in T for q in qs))
_ans = Counter(q["answer"] for q in qs if q["type"] == "choice")
ck("答案位 A/B/C/D 各 ≥15%", len(_ans) == 4 and min(_ans.values()) / sum(_ans.values()) >= 0.15,
   {k: "%.1f%%" % (v * 100 / sum(_ans.values())) for k, v in sorted(_ans.items())})

# 9 字段
need = ["name", "domain", "grade", "semester", "chapter", "type", "description", "mastery_criteria"]
ck("核心字段齐全", all(all(t.get(k) for k in need) for t in topics))
ck("description 40–200 汉字", all(40 <= len(re.findall(r"[\u4e00-\u9fa5]", t.get("description", ""))) <= 200 for t in topics),
   [(t["id"], len(re.findall(r"[\u4e00-\u9fa5]", t.get("description", "")))) for t in topics
    if not 40 <= len(re.findall(r"[\u4e00-\u9fa5]", t.get("description", ""))) <= 200][:5])
ck("掌握标准 1–3 条", all(1 <= len(t.get("mastery_criteria") or []) <= 3 for t in topics))
ck("诊断题与答案齐全", all(t.get("diagnostic_question", {}).get("question") and
                            t["diagnostic_question"].get("answer") for t in topics))

for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
if fails:
    print("FAILED:", len(fails))
    sys.exit(1)
print("GEOGRAPHY-LUJIAO DATA PASSED")
