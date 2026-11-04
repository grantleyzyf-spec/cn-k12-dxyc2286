#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""merge_geo_lujiao_exams.py —— 收 _exam_parts/E*_out.json 到 data/geography-lujiao/exams/<册>/<卷名>.json"""
import json, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "geography-lujiao")
P = os.path.join(D, "_exam_parts")
cards = sorted(glob.glob(os.path.join(P, "E[0-9][0-9].json")))
ok = miss = 0
for c in cards:
    card = json.load(open(c, encoding="utf-8"))
    out = os.path.join(P, card["eid"] + "_out.json")
    if not os.path.exists(out):
        print("!! 缺产物", card["eid"], card["paper"]); miss += 1; continue
    d = json.load(open(out, encoding="utf-8"))
    for k in ("book", "kind", "term", "grade", "paper", "examId", "scope"):
        d[k] = card[k]
    d["stage"] = "高中"
    d["fullScore"], d["duration"] = 150, 150
    tdir = os.path.join(D, "exams", card["book"])
    os.makedirs(tdir, exist_ok=True)
    json.dump(d, open(os.path.join(tdir, card["paper"] + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    ok += 1
print("合并 %d 卷 ｜ 缺 %d" % (ok, miss))
