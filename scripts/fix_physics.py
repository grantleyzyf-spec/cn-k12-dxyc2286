# -*- coding: utf-8 -*-
"""学科数据归一（模板）。用法: python3 fix.py <subject> [--write]
幂等；先 dry-run 看计数，再 --write。"""
import json, os, re, sys

S = sys.argv[1]
WRITE = "--write" in sys.argv
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
tp, qp = f"{D}/{S}/topics.json", f"{D}/{S}/questions.json"
topics = json.load(open(tp, encoding="utf-8"))
qs = json.load(open(qp, encoding="utf-8"))

DIFF = {"medium": "standard", "easy": "basic"}
PROC = re.compile(r"(计算|运算|口算|估算|竖式|解方程|解不等式|化简|求值|换算|笔算)")
REAS = re.compile(r"(证明|推理|说明理由)")

# 每题题干 <12 字的补写映射（按学科手工填，别自动加前缀）
PROMPT_FIX = {}

n_diff = n_prompt = n_choice = n_root = n_type = 0
for q in qs:
    if q.get("difficulty") in DIFF:
        q["difficulty"] = DIFF[q["difficulty"]]
        n_diff += 1
    if q["id"] in PROMPT_FIX and len(q.get("prompt", "")) < 12:
        q["prompt"] = q["question"] = PROMPT_FIX[q["id"]]
        n_prompt += 1
    if q.get("type") == "choice" and len(q.get("options") or []) != 4:
        q["type"] = "fill"
        q["options"] = []
        n_choice += 1

for t in topics:
    if not t.get("prerequisites") and not t.get("root_reason"):
        g = int(t.get("grade") or 0)
        band = "小学" if g <= 6 else ("初中" if g <= 9 else "高中")
        t["root_reason"] = f"起始知识点：{(t.get('chapter') or '')[:24]} 为{band}阶段起始内容，图谱内无更早前置（跨学段前置不单独连边）"
        n_root += 1
    if t.get("type") == "conceptual":
        nm = t.get("name", "")
        if PROC.search(nm):
            t["type"] = "procedural"; n_type += 1
        elif REAS.search(nm):
            t["type"] = "reasoning"; n_type += 1

print(f"难度归一 {n_diff} | 题干补全 {n_prompt} | 选项不合规改建 {n_choice} | 根节点补 reason {n_root} | 题型细分 {n_type}")
print("难度:", {k: sum(1 for q in qs if q.get("difficulty") == k) for k in ("basic", "standard", "hard")})
print("题型:", {k: sum(1 for t in topics if t.get("type") == k) for k in ("conceptual", "procedural", "reasoning", "modeling", "application")})
print("仍无 root_reason 的根节点:", sum(1 for t in topics if not t.get("prerequisites") and not t.get("root_reason")))

if WRITE:
    json.dump(qs, open(qp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(topics, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("written:", tp, qp)
