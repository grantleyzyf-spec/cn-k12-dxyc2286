#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 _skeleton.json 生成「按章派单」：_shards/<tag>c<unit_no>.json
每片 = 一章（1 个单元点 + N 个课时点），供 check_bank_hj.py 单章自检、
_bank/<tag>.part<NN>.json 由 merge_bank_hj.py 自动汇总。
"""
import json, os

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OUT = os.path.join(REPO, "data", "math-hujiao")
skel = json.load(open(os.path.join(OUT, "_skeleton.json"), encoding="utf-8"))
os.makedirs(os.path.join(OUT, "_shards"), exist_ok=True)

rows = []
for v in skel["volumes"]:
    for i, u in enumerate(v["units"], 1):
        tag = f"{v['tag']}c{i}"
        shard = {
            "tag": tag, "book": v["book"], "stage": v["stage"], "edition": "沪教版",
            "grade": v["grade"], "semester": v["semester"], "part_of": v["tag"],
            "units": [{
                "unit_id": u["unit_id"], "unit_name": u["unit_name"],
                "unit_chapter": u["unit_chapter"], "domain": u["domain"],
                "lessons": [{"id": l["id"], "name": l["sec_name"], "chapter": l["chapter"],
                             "page": l.get("page")} for l in u["lessons"]],
            }],
        }
        json.dump(shard, open(os.path.join(OUT, "_shards", f"{tag}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        rows.append((tag, v["book"], u["unit_name"], len(u["lessons"]), 5 + 8 * len(u["lessons"])))
for r in rows:
    print(f"{r[0]:<8} {r[1]:<14} {r[2]:<22} 节{r[3]:>2} 题{r[4]:>3}")
print(f"合计 {len(rows)} 章 / {sum(r[3] for r in rows)} 节 / {sum(r[4] for r in rows)} 题")
