#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""merge_phys_hkjy_lectures.py —— _lecture_parts/X*_out.json → exam_lectures/<册>/<卷名>.json"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "physics-hkjy")
P = os.path.join(D, "_lecture_parts")
ok = miss = 0
for c in sorted(glob.glob(os.path.join(P, "X[0-9][0-9].json"))):
    card = json.load(open(c, encoding="utf-8"))
    out = card["out"]
    if not os.path.exists(out):
        print("!! 缺产物", card["xid"], card["paper"])
        miss += 1
        continue
    d = json.load(open(out, encoding="utf-8"))
    d["examId"], d["book"], d["paper"], d["kind"] = card["examId"], card["book"], card["paper"], card["kind"]
    tdir = os.path.join(D, "exam_lectures", card["book"])
    os.makedirs(tdir, exist_ok=True)
    json.dump(d, open(os.path.join(tdir, card["paper"] + ".json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    ok += 1
print("讲解合并 %d 份 ｜ 缺 %d" % (ok, miss))
