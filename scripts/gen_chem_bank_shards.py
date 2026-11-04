#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人教版化学：生成题库分片（按册切、单片 ≤ 约 100 题）。

用法：python3 scripts/gen_chem_bank_shards.py
产物：data/chemistry/_bank_shards/CHEM_B01.json …（每片带 topics 骨架 + slots 题槽 + 绝对路径）
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "chemistry")
PER_LESSON, PER_UNIT = 8, 5


def main():
    T = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
    sk = json.load(open(os.path.join(D, "_skeleton.json"), encoding="utf-8"))
    books = {}
    for t in T:
        books.setdefault(t["chapter"].split(" ")[0], []).append(t)
    outdir = os.path.join(D, "_bank_shards")
    os.makedirs(outdir, exist_ok=True)
    for f in os.listdir(outdir):
        if f.startswith("CHEM_B"):
            os.remove(os.path.join(outdir, f))
    qno = 0
    idx = 0
    meta = {}
    for b in sk["books"]:
        book = b["book"]
        pts = sorted(books[book], key=lambda t: (t["level"] != "unit", t["chapter"]))
        # 按单元聚合，两单元一片，避免单片过大
        units = []
        for u in (x for x in pts if x.get("level") == "unit"):
            units.append([u] + [t for t in pts if t.get("level") == "lesson"
                                and t["chapter"].startswith(u["chapter"] + " · ")])
        groups = [units[i:i + 2] for i in range(0, len(units), 2)]
        for g in groups:
            idx += 1
            sid = f"CHEM_B{idx:02d}"
            shard_pts = [p for grp in g for p in grp]
            slots = []
            for p in shard_pts:
                n = PER_LESSON if p.get("level") == "lesson" else PER_UNIT
                ids = []
                for _ in range(n):
                    qno += 1
                    ids.append(f"chem_q{qno:04d}")
                quota = ({"choice": 3, "fill": 2, "short-answer": 2, "numeric": 1} if n == 8
                         else {"choice": 3, "fill": 1, "short-answer": 1})
                slots.append({"topicId": p["id"], "level": p.get("level", "lesson"),
                              "count": n, "idRange": ids, "quota": quota})
            shard = {"shard": sid, "book": book, "stage": b["stage"], "grade": b["grade"],
                     "semester": b["semester"],
                     "txt": os.path.join(D, "_text", f"{book}.txt"),
                     "out": os.path.join(D, "_bank", f"{sid}_out.json"),
                     "topics": [{"id": p["id"], "name": p["name"], "level": p.get("level"),
                                 "chapter": p["chapter"], "domain": p["domain"],
                                 "grade": p["grade"], "semester": p["semester"],
                                 "type": p.get("type", "conceptual")} for p in shard_pts],
                     "slots": slots,
                     "total": sum(s["count"] for s in slots)}
            with open(os.path.join(outdir, f"{sid}.json"), "w", encoding="utf-8") as fh:
                json.dump(shard, fh, ensure_ascii=False, indent=1)
                fh.write("\n")
            meta[sid] = (book, len(shard_pts), shard["total"])
    print(f"分片 {idx} 个，题槽合计 {qno}")
    for k, v in meta.items():
        print(f"  {k} {v[0]:10} 点 {v[1]:>2} 题 {v[2]:>3}")


if __name__ == "__main__":
    main()
