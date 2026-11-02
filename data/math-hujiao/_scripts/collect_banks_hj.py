#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把按章 _bank/<tag>c<N>.json 汇总成按册 _bank/<vol>.json（merge_bank_hj.py 的输入）"""
import json, os, glob, re
from collections import Counter

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(REPO, "data", "math-hujiao")

skel = json.load(open(os.path.join(OUT, "_skeleton.json"), encoding="utf-8"))
total_u = total_l = total_q = 0
for v in skel["volumes"]:
    tag = v["tag"]
    files = sorted(glob.glob(os.path.join(OUT, "_bank", f"{tag}c*.json")),
                   key=lambda p: int(re.search(r"c(\d+)\.json$", p).group(1)))
    if not files:
        print(f"{tag}: 无分章产物（建模册或未开工）")
        continue
    bank = {"tag": tag, "book": v["book"], "unit_points": [], "lesson_points": []}
    for fp in files:
        b = json.load(open(fp, encoding="utf-8"))
        bank["unit_points"] += b.get("unit_points", [])
        bank["lesson_points"] += b.get("lesson_points", [])
    dst = os.path.join(OUT, "_bank", f"{tag}.json")
    json.dump(bank, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    nq = sum(len(p.get("questions") or []) for p in bank["unit_points"] + bank["lesson_points"])
    print(f"{tag}: 章文件 {len(files)} → 单元点 {len(bank['unit_points'])} / 课时点 {len(bank['lesson_points'])} / 题 {nq}")
    total_u += len(bank["unit_points"]); total_l += len(bank["lesson_points"]); total_q += nq
print(f"合计：单元点 {total_u} / 课时点 {total_l} / 题 {total_q}")
