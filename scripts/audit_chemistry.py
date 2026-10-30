# -*- coding: utf-8 -*-
"""学科体检（模板）。用法: python3 audit.py <subject>
输出：字段缺失、课标/quote 覆盖、边对称、根节点、题目可用性、册次分布。"""
import json, os, sys
from collections import Counter

S = sys.argv[1]
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
t = json.load(open(f"{D}/{S}/topics.json", encoding="utf-8"))
d = json.load(open(f"{D}/{S}/dependencies.json", encoding="utf-8"))
q = json.load(open(f"{D}/{S}/questions.json", encoding="utf-8"))
std = json.load(open(f"{D}/cn-curriculum-standards.json", encoding="utf-8"))
idx = {e["id"] for e in std["subjects"][S]["entries"]}
T = {x["id"]: x for x in t}
Q = {x.get("topicId"): x for x in q}

print("=== 规模 ===", len(t), "知识点 /", len(d), "边 /", len(q), "题")
for f in ["id", "name", "subject", "domain", "grade", "semester", "chapter", "type", "description",
          "mastery_criteria", "diagnostic_question", "standards", "prerequisites", "curriculumRef", "tags", "verified"]:
    miss = [x["id"] for x in t if f not in x or x[f] in (None, "", [], {})]
    print(f"  {f:20s} 缺 {len(miss):3d}", miss[:3])
print("  semester:", Counter(x.get("semester") for x in t))
print("  type:", Counter(x.get("type") for x in t))
print("  grade:", dict(sorted(Counter(x.get("grade") for x in t).items())))

print("\n=== 课标 ===")
print("  无 standards:", [x["id"] for x in t if not x.get("standards")])
print("  引用不在索引:", [(x["id"], s.get("id")) for x in t for s in x.get("standards", []) if s.get("id") not in idx][:5])
print("  缺 quote:", sum(1 for x in t for s in x.get("standards", []) if not s.get("quote")))
print("  confidence:", Counter(s.get("confidence") for x in t for s in x.get("standards", [])))

print("\n=== 先修边 ===")
pairs = {(e["from"], e["to"]): e.get("type") for e in d}
asym = [(p, x["id"]) for x in t for p in x.get("prerequisites", []) if (p, x["id"]) not in pairs]
rev = [(a, b) for (a, b) in pairs if b in T and a not in T[b].get("prerequisites", [])]
print("  topics 有/deps 缺:", len(asym), asym[:3])
print("  deps 有/topics 缺:", len(rev), rev[:3])
print("  类型:", Counter(e.get("type") for e in d), "| 悬空:", sum(1 for e in d if e["from"] not in T or e["to"] not in T))
print("  根节点:", sum(1 for x in t if not x.get("prerequisites")), "| 无 root_reason:",
      sum(1 for x in t if not x.get("prerequisites") and not x.get("root_reason")))
print("  自环:", sum(1 for e in d if e["from"] == e["to"]), "| 重复边:", len(d) - len(pairs))

print("\n=== 题目 ===")
print("  无题知识点:", len([x for x in t if x["id"] not in Q]))
print("  type:", Counter(x.get("type") for x in q), "| difficulty:", Counter(x.get("difficulty") for x in q))
bad = [(x["id"], len(x.get("options") or []), x.get("answer")) for x in q
       if x.get("type") == "choice" and (len(x.get("options") or []) != 4 or x.get("answer") not in [o.get("label") for o in x.get("options") or []])]
print("  choice 不合规:", bad[:5])
print("  题干 <8 字:", [x["id"] for x in q if len(x.get("prompt", "")) < 8][:5])
print("  缺解析:", [x["id"] for x in q if len(x.get("explanation", "")) < 4][:3])
print("  numeric 缺 verify:", [x["id"] for x in q if x.get("type") == "numeric" and not x.get("verify")][:5])

print("\n=== 册次 ===")
print("  grade-semester:", Counter((x.get("grade"), x.get("semester")) for x in t).most_common())
print("  chapter 前缀种类:", len({(x.get("chapter") or "")[:12] for x in t}))
