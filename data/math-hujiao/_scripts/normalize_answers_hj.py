#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""沪教版 · 题目字段归一（幂等）：answer 一律字符串（schema 要求 string）"""
import json, os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
p = os.path.join(REPO, "data", "math-hujiao", "questions.json")
qs = json.load(open(p, encoding="utf-8"))
n = 0
for q in qs:
    a = q.get("answer")
    if a is not None and not isinstance(a, str):
        q["answer"] = str(a)
        n += 1
json.dump(qs, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
open(p, "a", encoding="utf-8").write("\n")
print(f"answer 转字符串 {n} 条（共 {len(qs)} 题）")
