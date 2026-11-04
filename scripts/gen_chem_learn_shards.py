#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""人教版化学学层分片：每片 4 篇（同册不跨片），只覆盖 level=lesson 的点。"""
import json, os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(REPO, "data", "chemistry")
SD = os.path.join(D, "_learn_shards")
os.makedirs(SD, exist_ok=True)
T = json.load(open(os.path.join(D, "topics.json"), encoding="utf-8"))
lessons = [t for t in T if t["level"] == "lesson"]
by_book = {}
for t in lessons:
    by_book.setdefault(t["chapter"].split(" ")[0], []).append(t)

idx, n = [], 0
for book, pts in by_book.items():
    for i in range(0, len(pts), 4):
        grp = pts[i:i+4]
        n += 1
        tag = f"CHEM_L{n:02d}"
        payload = {"shard": tag, "subject": "chemistry", "book": book,
                   "text_file": f"data/chemistry/_text/{book}.txt",
                   "out": f"data/chemistry/learn/_parts/{book}/",
                   "lessons": [{"topicId": t["id"], "title": t["name"], "chapter": t["chapter"],
                                "description": t.get("description", ""),
                                "mastery_criteria": t.get("mastery_criteria", []),
                                "standards": [s.get("quote") for s in (t.get("standards") or [])]}
                               for t in grp]}
        json.dump(payload, open(os.path.join(SD, f"{tag}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        idx.append({"shard": tag, "book": book, "n": len(grp), "topics": [t["id"] for t in grp]})
json.dump(idx, open(os.path.join(SD, "_INDEX.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"学层分片 {len(idx)} / 篇 {sum(x['n'] for x in idx)}")
