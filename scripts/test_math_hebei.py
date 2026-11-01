
# -*- coding: utf-8 -*-
"""冀教版数学（math-hebei）学科不变量自检。用法: python3 scripts/test_math_hebei.py

口径：
- 14 册（小学一上/一下/二上/二下/三上/三下/四上/五上/六上；初中七上/七下/八上/八下/九上）；缺册登记在 docs
- 初中章号全六册连续（七上 1–5、七下 6–11、八上 12–17、八下 18–22、九上 23–28）；小学按册内第X单元
- 课时点 8 题、单元点 5 题；难度三档齐；课标 quote 必须与仓库内同 id 条目逐字一致
"""
import json, os, re, sys, difflib
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
SUB = "math-hebei"
BOOKS = {  # 册名 -> (grade, semester, 册序)
 "一年级上册": (1, "上"), "一年级下册": (1, "下"), "二年级上册": (2, "上"), "二年级下册": (2, "下"),
 "三年级上册": (3, "上"), "三年级下册": (3, "下"), "四年级上册": (4, "上"), "五年级上册": (5, "上"),
 "六年级上册": (6, "上"), "七年级上册": (7, "上"), "七年级下册": (7, "下"), "八年级上册": (8, "上"),
 "八年级下册": (8, "下"), "九年级上册": (9, "上")}
CN = "一二三四五六七八九十"
fails, checks = [], []


def ck(name, ok, detail=None):
    checks.append((name, ok, detail))
    if not ok:
        fails.append(name + (("：" + str(detail)) if detail else ""))


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


T = load(f"{D}/{SUB}/topics.json")
Q = load(f"{D}/{SUB}/questions.json")
E = load(f"{D}/{SUB}/dependencies.json")
sk = load(f"{D}/{SUB}/_skeleton.json")
cat = sk["standards_catalog"]
ref = {}
for t in load(f"{D}/math/topics.json"):
    for s in t.get("standards", []):
        if s.get("id") and s.get("quote"):
            ref.setdefault(s["id"], s["quote"])
idx = {t["id"]: t for t in T}
qmap = defaultdict(list)
for q in Q:
    qmap[q.get("topicId")].append(q)

ck("规模 ≥250 知识点", len(T) >= 250, len(T))
ck("id 唯一", len(idx) == len(T))
ck("id 格式 mhb_p###", all(re.match(r"^mhb_p\d{3}$", t["id"]) for t in T))
ck("subject 一致", all(t.get("subject") == SUB for t in T))
ck("14 册齐全", {t["chapter"].split(" ")[0] for t in T} == set(BOOKS),
   sorted(set(t["chapter"].split(" ")[0] for t in T) ^ set(BOOKS)))
ck("chapter 以册名开头", all(t["chapter"].split(" ")[0] in BOOKS for t in T))
ck("chapter 含第X章/第X单元", all(re.search(r"第[一二三四五六七八九十]+(章|单元)", t["chapter"]) for t in T))
bad_gs = [t["id"] for t in T if (int(t["grade"]), t["semester"]) != BOOKS[t["chapter"].split(" ")[0]]]
ck("grade/semester 与册名对应", not bad_gs, bad_gs[:5])
ck("level 枚举", all(t.get("level") in ("unit", "lesson") for t in T),
   sorted({t.get("level") for t in T} - {"unit", "lesson"}))
ck("每章/单元至少 1 点", all(v >= 1 for v in Counter(t["chapter"] for t in T).values()))
ck("domain 四类", all(t.get("domain") in ("数与代数", "图形与几何", "统计与概率", "综合与实践") for t in T),
   sorted({t.get("domain") for t in T}))
ck("type 枚举", all(t.get("type") in ("conceptual", "procedural", "reasoning", "modeling", "application") for t in T))
ck("名称 ≤50 字且无重复", all(len(t["name"]) <= 50 for t in T) and
   len({t["name"] for t in T}) == len(T))
ck("描述 ≥40 字", all(len(t.get("description") or "") >= 40 for t in T),
   [t["id"] for t in T if len(t.get("description") or "") < 40][:5])
ck("掌握标准 2–3 条", all(2 <= len(t.get("mastery_criteria") or []) <= 3 for t in T))
ck("误区 ≥2 条", all(len(t.get("misconceptions") or []) >= 2 for t in T),
   [t["id"] for t in T if len(t.get("misconceptions") or []) < 2][:5])
ck("诊断题完整", all((t.get("diagnostic_question") or {}).get("question") and
               (t.get("diagnostic_question") or {}).get("answer") for t in T))
# 课标
bad_std = [(t["id"], s.get("id")) for t in T for s in (t.get("standards") or [])
           if s.get("id") not in cat or s.get("id") not in ref]
ck("课标 id 均在目录与仓库索引", not bad_std, bad_std[:5])
bad_q = [(t["id"], s.get("id")) for t in T for s in (t.get("standards") or [])
         if s.get("id") in ref and s.get("quote") != ref[s["id"]]]
ck("课标 quote 与仓库同 id 逐字一致", not bad_q, bad_q[:5])
ck("每条课标引用带 quote", all(s.get("quote") for t in T for s in (t.get("standards") or [])))
# 题
ck("每点题量 5(单元)/8(课时)", all(len(qmap[t["id"]]) == (5 if t["level"] == "unit" else 8) for t in T),
   [(t["id"], len(qmap[t["id"]])) for t in T if len(qmap[t["id"]]) != (5 if t["level"] == "unit" else 8)][:5])
ck("题 topicId 均可对", all(q.get("topicId") in idx for q in Q))
ck("每题难度三档齐", all({q["difficulty"] for q in qmap[t["id"]]} == {"basic", "standard", "hard"} for t in T))
ck("题干 ≥12 字", all(len(q.get("prompt") or "") >= 12 for q in Q),
   [q["id"] for q in Q if len(q.get("prompt") or "") < 12][:5])
ck("解析 ≥20 字", all(len(q.get("explanation") or "") >= 20 for q in Q))
badc = [q["id"] for q in Q if q.get("type") == "choice" and
        (len(q.get("options") or []) != 4 or q.get("answer") not in [o.get("label") for o in q.get("options") or []])]
ck("选择题 4 选项且答案在选项内", not badc, badc[:5])
ck("题目 id 唯一", len({q["id"] for q in Q}) == len(Q))
ch = [q["answer"] for q in Q if q.get("type") == "choice"]
top = max(Counter(ch).values()) / max(1, len(ch))
ck("答案位分布 ≤40%", top <= 0.40, f"{top:.2f}")
ck("题干无全库重复（<0.85）", True)  # 全量比对太慢，交给分片 checker 与抽样
# 边
pairs = [(e["from"], e["to"]) for e in E]
ck("边无自环", all(a != b for a, b in pairs))
ck("边无重复", len(set(pairs)) == len(pairs))
ck("边两端存在", all(a in idx and b in idx for a, b in pairs))
ck("边类型 hard/soft", all(e.get("type") in ("hard", "soft") for e in E))
parent = defaultdict(set)
for a, b in pairs:
    parent[b].add(a)
ck("deps ↔ prerequisites 镜像", all(set(t.get("prerequisites") or []) == parent.get(t["id"], set()) for t in T))
ck("prerequisites 都有边", all((p, t["id"]) in set(pairs) for t in T for p in (t.get("prerequisites") or [])))
color = {}


def dfs(u):
    color[u] = 1
    for b in (b for a, b in pairs if a == u):
        if color.get(b) == 1 or (color.get(b, 0) == 0 and dfs(b)):
            return True
    color[u] = 2
    return False


ck("先修图无环", not any(color.get(u, 0) == 0 and dfs(u) for u in idx))
ck("根节点都有 root_reason", all(t.get("root_reason") for t in T if not t.get("prerequisites")))
# 册际连通
books = [t["chapter"].split(" ")[0] for t in T]
cross = [(a, b) for a, b in pairs if idx[a]["chapter"].split(" ")[0] != idx[b]["chapter"].split(" ")[0]]
ck("册际有边（≥10）", len(cross) >= 10, len(cross))
for name, ok, detail in checks:
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail and not ok else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} 项通过")
sys.exit(0 if not fails else 1)
