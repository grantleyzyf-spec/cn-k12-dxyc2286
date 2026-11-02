#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""鄂教版高中数学图谱 · 数据不变量（可单独跑，也可接 CI）
用法: python3 data/math-ejiao/_scripts/test_math_ejiao.py
退出码 0 = 全绿
"""
import json, os, re, sys
from collections import Counter

ROOT = "/Users/a627692/Desktop/cn-k12-dxyc2286"
OUT = os.path.join(ROOT, "data", "math-ejiao")
fails = []


def ck(name, ok, detail=None):
    print(("  ✅ " if ok else "  ❌ ") + name + (f"  [{detail}]" if detail is not None else ""))
    if not ok:
        fails.append(name)


topics = json.load(open(os.path.join(OUT, "topics.json"), encoding="utf-8"))
deps = json.load(open(os.path.join(OUT, "dependencies.json"), encoding="utf-8"))
qs = json.load(open(os.path.join(OUT, "questions.json"), encoding="utf-8"))
skel = json.load(open(os.path.join(OUT, "_skeleton.json"), encoding="utf-8"))
T = {t["id"]: t for t in topics}
Q = {q["id"]: q for q in qs}

n_unit = sum(1 for t in topics if "page" not in t)
n_lesson = len(topics) - n_unit
print("== 规模 ==")
ck("知识点 = 20 单元点 + 212 课时点", len(topics) == 232 and n_unit == 20 and n_lesson == 212,
   f"{len(topics)} 点（单元 {n_unit} / 课时 {n_lesson}）")
ck("id 唯一", len(T) == len(topics))
ck("题量 ≥ 点×5", len(qs) >= len(topics) * 5, f"{len(qs)} 题 / {len(topics)} 点")
ck("全部 subject=math-ejiao", all(t.get("subject") == "math-ejiao" for t in topics))
ck("topic id 前缀 mej_", all(t["id"].startswith("mej_") for t in topics))
ck("题 id 唯一", len(Q) == len(qs))

print("== 两层点口径 ==")
ck("单元点无 page", all("page" not in t for t in topics if t["id"] < "mej_h1000"))
ck("课时点都有 page", all(t.get("page") for t in topics if t["id"] > "mej_h1000"))
ck("课时点 misconceptions ≥2",
   all(len(t.get("misconceptions") or []) >= 2 for t in topics if t["id"] > "mej_h1000"))
ck("chapter 首段是鄂教版册名",
   all(t["chapter"].split(" ")[0].startswith("鄂教版") for t in topics),
   sorted({t["chapter"].split(" ")[0] for t in topics})[:3])
ck("grade 10–16", all(10 <= t.get("grade", 0) <= 16 for t in topics))

print("== 依赖 ==")
ids = set(T)
ck("无悬空边", all(d["from"] in ids and d["to"] in ids for d in deps), len(deps))
ck("边的 to 都有 prerequisites 回填",
   all(d["from"] in T[d["to"]].get("prerequisites", []) for d in deps))
roots = [t for t in topics if not t.get("prerequisites")]
ck("有根点且都写了 root_reason", all(t.get("root_reason") for t in roots), f"{len(roots)} 个根点")
# 无环
graph = {}
for d in deps:
    graph.setdefault(d["from"], []).append(d["to"])
seen, stack = {}, set()


def dfs(n):
    stack.add(n)
    for m in graph.get(n, []):
        if m in stack:
            return False
        if seen.get(m) is None:
            seen[m] = 1
            if not dfs(m):
                return False
    stack.discard(n)
    return True


ck("先修图无环", all(dfs(n) for n in list(graph)))

print("== 题目质量 ==")
bad_type = [q["id"] for q in qs if q.get("type") not in {"choice", "fill", "short-answer", "numeric"}]
ck("type 合法", not bad_type, bad_type[:3])
bad_diff = [q["id"] for q in qs if q.get("difficulty") not in {"basic", "standard", "hard"}]
ck("difficulty 仅三档", not bad_diff, bad_diff[:3])
bad_ans = [q["id"] for q in qs if q.get("type") == "choice"
           and q.get("answer") not in [o.get("label") for o in (q.get("options") or [])]]
ck("选择题答案在选项内", not bad_ans, bad_ans[:3])
bad_opt = [q["id"] for q in qs if q.get("type") == "choice"
           and [o.get("label") for o in (q.get("options") or [])] != ["A", "B", "C", "D"]]
ck("选择题 4 选项 A–D", not bad_opt, bad_opt[:3])
ck("题干汉字 ≥8", all(len(re.findall(r"[\u4e00-\u9fa5]", q.get("prompt") or "")) >= 8 for q in qs))
ck("解析汉字 ≥15", all(len(re.findall(r"[\u4e00-\u9fa5]", q.get("explanation") or "")) >= 15 for q in qs))
ck("无 Markdown 符号", not any(re.search(r"[*_`#\[\]|]", q.get("prompt") or "") for q in qs))
num_no_verify = [q["id"] for q in qs if q.get("type") == "numeric" and not q.get("verify")]
ck("numeric 都带 verify", not num_no_verify, num_no_verify[:3])
ck("topicId 都在 topics 里", all(q.get("topicId") in ids for q in qs))

print("== 逐点题量与答案位 ==")
by_topic = Counter(q.get("topicId") for q in qs)
lack_u = [t for t in topics if "page" not in t and by_topic.get(t["id"], 0) < 5]
lack_l = [t for t in topics if "page" in t and by_topic.get(t["id"], 0) < 8]
ck("单元点 ≥5 题", not lack_u, [t["id"] for t in lack_u][:3])
ck("课时点 ≥8 题", not lack_l, [t["id"] for t in lack_l][:3])
skew = []
for tid in {q["topicId"] for q in qs}:
    letters = Counter(q["answer"] for q in qs if q["topicId"] == tid and q.get("type") == "choice")
    tot = sum(letters.values())
    if tot >= 4 and letters.most_common(1)[0][1] / tot > 0.4:
        skew.append((tid, letters.most_common(1)[0]))
ck("单点答案字母 ≤40%", not skew, skew[:3])

print("== 诊断题（前端用）==")
bad_dq = [t["id"] for t in topics
          if not t.get("diagnostic_question") or not t["diagnostic_question"].get("question")]
ck("每点都有 diagnostic_question", not bad_dq, bad_dq[:3])

print("\n" + ("全部通过" if not fails else f"失败 {len(fails)} 项：" + "；".join(fails[:6])))
sys.exit(0 if not fails else 1)
